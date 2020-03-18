import osmnx as ox
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

query_str = '[out:json][timeout:180];(relation["network"="Singapore Rail"]["route"="monorail"](1.4011,103.8977,1.4154,103.9231);>;);out;'
response_json = overpass_request(data={'data': query_str}, timeout=180)


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


def create_graph(response_jsons, name='unnamed', retain_all=True, bidirectional=False):
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
    elements.extend(response_json['elements'])
    if len(elements) < 1:
        raise EmptyOverpassResponse('There are no data elements in the response JSON objects')

    # create the graph as a MultiDiGraph and set the original CRS to default_crs
    G = nx.MultiDiGraph(name=name, crs=settings.default_crs)

    # extract nodes and paths from the downloaded osm data
    nodes = {}
    paths = {}
    # for osm_data in response_jsons:
    nodes_temp, paths_temp = parse_osm_nodes_paths(response_jsons)
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


# finding which mrt station is closest to the start/end point
def lrt_nearnode(srctomrt):
    nearnode = []
    for k in mrtNodeList:
        if k.get("railway") == "station" or k.get("railway") == "stop":
            h = heuristic(latlon(srctomrt), latlon(k.get("osmid")))
            heapq.heappush(nearnode, (h, k.get("osmid")))
    return heapq.heappop(nearnode)


# retrieving lat/lon coordinates via OSMID
def latlon(osmid):
    for k in mrtNodeList:
        if k.get("osmid") == osmid:
            return k.get("x"), k.get("y")


# ASTAR ALGORITHM
def lrt_astar(start_point, end_point, edge_list):
    closepath = {}
    path = []
    routeq = []
    finalret = []
    stat = []

    # finding start station (working)
    for k in edge_list:
        h = heuristic(latlon(start_point), latlon(k[0][1]))
        if h > 5:
            heapq.heappush(stat, (h, k[0][1]))
    strt = heapq.heappop(stat)[1]

    # pushing start point into heapq queue (heuristic, length(dist), parent(key), current(value))
    heapq.heappush(routeq, (0, 0, None, strt))
    closepath[strt] = None

    while True:
        temp = heapq.heappop(routeq)

        # check if we reach end point node
        if temp[3] == end_point or heuristic(latlon(temp[3]), latlon(end_point)) < 20:
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
                        he = heuristic(latlon(i[0][1]), latlon(end_point))
                        cur_length = i[1].get('length')
                        heapq.heappush(routeq,
                                       ((he + temp[1] + cur_length), cur_length + temp[1], temp[3], i[0][1]))
                        # adding previous path to close path dict to prevent an infinite loop of short path
                        closepath[i[0][1]] = temp[3]


# ------------------- main code ------------------- #
G_lrt = create_graph(response_json)
mrtNodeList = list(G_lrt.nodes.values())
mrtEdgeList = list(G_lrt.edges.items())

startosmid = ox.get_nearest_node(G_lrt, (1.4014441, 103.8950046), method='euclidean', return_dist=True)
endosmid = ox.get_nearest_node(G_lrt, (1.399601, 103.9164448), method='euclidean', return_dist=True)

# testing algorithmn speed
start_time = time.time()
mrtfinal = lrt_astar(lrt_nearnode(startosmid[0])[1], lrt_nearnode(endosmid[0])[1], mrtEdgeList)
print("--- %s seconds ---" % round((time.time() - start_time), 2))

# calculating estimated time to reach the destination
totaldist = mrtfinal[1] + (startosmid[1] * 1000) + (endosmid[1] * 1000)
estwalk = totaldist / (45000 / 60)  # avg mrt speed 45km/hr - 750m per minute
print("Time: " + str(round(estwalk)) + " minutes" + "\nDistance: " + str(round((totaldist / 1000), 2)) + " km")

# plotting map to folium
m = ox.plot_route_folium(G_lrt, mrtfinal[0], route_color='#00008B', route_width=5, tiles="OpenStreetMap")
m.save('templates/astar_lrt.html')