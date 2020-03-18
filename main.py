from flask import Flask, render_template
import heapq
import time
import math

import pprint
import numpy as np
import osmnx as ox
import networkx as nx
import math
import matplotlib.pyplot as plt
import pandas as pd
import itertools as it
import geopandas as gpd

import io
import json
import hashlib
import math
import requests
import time
import re
import datetime as dt
import os
import logging as lg
from collections import OrderedDict
from dateutil import parser as date_parser
from osmnx.errors import *
from osmnx.utils import make_str, log

from osmnx import settings
from osmnx.downloader import get_from_cache, get_http_headers, get_pause_duration, save_to_cache

import geopandas as gpd
import logging as lg
import math
import networkx as nx
import numpy as np
import pandas as pd
import time

from itertools import groupby
from shapely.geometry import LineString
from shapely.geometry import MultiPolygon
from shapely.geometry import Point
from shapely.geometry import Polygon
from shapely.ops import unary_union

from osmnx import settings
from osmnx.projection import project_geometry
from osmnx.projection import project_gdf
from osmnx.simplify import simplify_graph
from osmnx.utils import make_str, log
from osmnx.geo_utils import get_largest_component
from osmnx.utils import great_circle_vec
from osmnx.geo_utils import get_nearest_node
from osmnx.geo_utils import geocode
from osmnx.geo_utils import count_streets_per_node
from osmnx.geo_utils import overpass_json_from_file
from osmnx.downloader import osm_polygon_download
from osmnx.downloader import get_osm_filter
from osmnx.downloader import overpass_request
from osmnx.errors import *
from osmnx.core import consolidate_subdivide_geometry, get_polygons_coordinates


def get_node(element):
    """
    Convert an OSM node element into the format for a networkx node.

    Parameters
    ----------
    element : dict
        an OSM node element

    Returns
    -------
    dict
    """
    useful_tags_node = ['ref', 'railway']
    node = {}
    node['y'] = element['lat']
    node['x'] = element['lon']
    node['osmid'] = element['id']

    if 'tags' in element:
        for useful_tag in useful_tags_node:
            if useful_tag in element['tags']:
                node[useful_tag] = element['tags'][useful_tag]
    return node


def parse_osm_nodes_paths(osm_data):
    """
    Construct dicts of nodes and paths with key=osmid and value=dict of
    attributes.
    Parameters
    ----------
    osm_data : dict
        JSON response from from the Overpass API
    Returns
    -------
    nodes, paths : tuple
    """

    nodes = {}
    paths = {}
    for element in osm_data['elements']:
        if element['type'] == 'node':
            key = element['id']
            nodes[key] = get_node(element)
        elif element['type'] == 'way':  # osm calls network paths 'ways'
            key = element['id']
            paths[key] = ox.get_path(element)

    return nodes, paths


def create_graph(mrt_response_json, name='unnamed', retain_all=True, bidirectional=False):
    """
    Create a networkx graph from Overpass API HTTP response objects.

    Parameters
    ----------
    response_jsons : list
        list of dicts of JSON responses from from the Overpass API
    name : string
        the name of the graph
    retain_all : bool
        if True, return the entire graph even if it is not connected
    bidirectional : bool
        if True, create bidirectional edges for one-way streets

    Returns
    -------
    networkx multidigraph
    """

    log('Creating networkx graph from downloaded OSM data...')
    start_time = time.time()

    # make sure we got data back from the server requests
    elements = []
    # for response_json in response_jsons:
    elements.extend(mrt_response_json['elements'])
    if len(elements) < 1:
        raise EmptyOverpassResponse('There are no data elements in the response JSON objects')

    # create the graph as a MultiDiGraph and set the original CRS to default_crs
    G = nx.MultiDiGraph(name=name, crs=settings.default_crs)

    # extract nodes and paths from the downloaded osm data
    nodes = {}
    paths = {}
    # for osm_data in response_jsons:
    nodes_temp, paths_temp = parse_osm_nodes_paths(mrt_response_json)
    for key, value in nodes_temp.items():
        nodes[key] = value
    for key, value in paths_temp.items():
        paths[key] = value

    # add each osm node to the graph
    for node, data in nodes.items():
        G.add_node(node, **data)

    # add each osm way (aka, path) to the graph
    G = ox.add_paths(G, paths, bidirectional=bidirectional)

    # retain only the largest connected component, if caller did not
    # set retain_all=True
    if not retain_all:
        G = get_largest_component(G)

    log('Created graph with {:,} nodes and {:,} edges in {:,.2f} seconds'.format(len(list(G.nodes())),
                                                                                 len(list(G.edges())),
                                                                                 time.time() - start_time))

    # add length (great circle distance between nodes) attribute to each edge to
    # use as weight
    if len(G.edges) > 0:
        G = ox.add_edge_lengths(G)

    return G


# finding which mrt station is closest to the start/end point
def mrt_nearnode(srctomrt, nodelist):
    nearnode = []
    for k in nodelist:
        if k.get("railway") == "station" or k.get("railway") == "stop":
            h = heuristic(latlon(srctomrt, nodelist), latlon(k.get("osmid"), nodelist))
            heapq.heappush(nearnode, (h, k.get("osmid")))
    return heapq.heappop(nearnode)


# retrieving lat/lon coordinates via OSMID
def latlon(osmid, nodeList):
    for k in nodeList:
        if k[2] == osmid:
            return k[1], k[0]


# calculating heuristic between two lat/lon points
def heuristic(start, end):
    lat1, lon1 = start[0], start[1]
    lat2, lon2 = end[0], end[1]
    radius = 6371  # km

    distlat = math.radians(lat2 - lat1)
    distlon = math.radians(lon2 - lon1)
    a = math.sin(distlat / 2) * math.sin(distlat / 2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(distlon / 2) * math.sin(distlon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    dist = radius * c * 1000

    return dist


# getting walk to station
def walktoSt(edge_list, start):
    stat = []
    for k in edge_list:
        h = heuristic(latlon(start, edge_list), latlon(k[0][1], edge_list))
        if h > 5:
            heapq.heappush(stat, (h, k[0][1]))
    return heapq.heappop(stat)[1]


# ASTAR ALGORITHM
def astar(start_point, end_point, edge_list, node_list):
    closepath = {}
    path = []
    routeq = []
    finalret = []

    # pushing start point into heapq queue (heuristic, length(dist), parent(key), current(value))
    heapq.heappush(routeq, (0, 0, None, start_point))
    closepath[start_point] = None

    while True:
        temp = heapq.heappop(routeq)
        # check if we reach end point node
        if temp[3] == end_point:
            path.append(temp[3])
            rear = temp[2]

            # path list to append all osmid by key in closepath with the first being the end node
            while rear is not None:
                path.append(rear)
                rear = closepath.get(rear)

            # reverse the path list into start to end
            path = path[::-1]
            finalret.append(path)
            finalret.append(temp[1])
            return finalret
        else:
            for i in edge_list:
                if i[0][0] == temp[3]:
                    if i[0][1] in closepath:
                        continue
                    else:
                        h = heuristic(latlon(i[0][1], node_list), latlon(end_point, node_list))
                        cur_length = i[1].get('length')
                        heapq.heappush(routeq,
                                       ((h + temp[1] + cur_length), cur_length + temp[1], temp[3], i[0][1]))
                        # adding previous path to close path dict to prevent an infinite loop of short path
                        closepath[i[0][1]] = temp[3]


# main code
punggol = (1.403948, 103.909048)
distance = 2000

# data creation and storing
mrt_query_str = '[out:json][timeout:180];(relation["network"="Singapore Rail"]["route"="monorail"](1.4011,103.8977,1.4154,103.9231);>;);out;'
mrt_response_json = overpass_request(data={'data': mrt_query_str}, timeout=180)
G_lrt = create_graph(mrt_response_json)
G_walk = ox.graph_from_point(punggol, distance=distance, truncate_by_edge=True, network_type='walk')

# storing all nodes into a list
walkNodeList = list(G_walk.nodes.values())
walkEdgeList = list(G_walk.edges.items())
mrtNodeList = list(G_lrt.nodes.values())
mrtEdgeList = list(G_lrt.edges.items())

# user input (GUI TEAM, user input in text area will be stored here)
src = "220A Sumang Lane, Singapore 821220"  # punggol will return punggol mrt coordinates
des = "60 Punggol East, Singapore 828825"  # random hdb
startpoint = ox.geocode(src)
endpoint = ox.geocode(des)

startosmid = ox.get_nearest_node(G_walk, startpoint, method='euclidean', return_dist=True)
endosmid = ox.get_nearest_node(G_walk, endpoint, method='euclidean', return_dist=True)

# Walk-LRT connection start
strtlrt = ox.get_nearest_node(G_lrt, startpoint, method='euclidean', return_dist=True)

#################################################### Above correct ####################################################
mrtStart = walktoSt(mrtEdgeList, strtlrt[0])
mrtEnd = mrt_nearnode(endosmid[0], mrtNodeList)[1]

# testing WALK algorithmn
walkToStation = astar(startosmid[0], mrtStart, walkEdgeList, walkNodeList)
walkFromStation = astar(mrtEnd[1], endosmid[0], walkEdgeList, walkNodeList)

# testing LRT algorithmn
mrtfinal = astar(walktoSt(mrtEdgeList, mrtStart[1]), mrtEnd, mrtEdgeList, mrtNodeList)

# plotting map to folium
m = ox.plot_route_folium(G_walk, walkToStation[0], route_color='#00FFFF', route_width=5, tiles="OpenStreetMap")
ox.plot_route_folium(G_walk, walkFromStation[0], route_color='#00FFFF', route_width=5, tiles="OpenStreetMap").add_child(m)
ox.plot_route_folium(G_lrt, mrtfinal[0], route_color='#FF0000', route_width=5, tiles="OpenStreetMap").add_child(m)
m.save('templates/astaralgo_walklrt.html')

'''
FLASK IS HERE FLASK IS HERE FLASK IS HERE FLASK IS HERE
'''
app = Flask(__name__)


@app.route("/")
def index():
    return render_template('index.html')
