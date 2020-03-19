from flask import Flask, render_template
import heapq
import folium
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
def lrt_nearnode(srctomrt):
    nearnode = []
    for k in mrtNodeList:
        if k.get("railway") == "station" or k.get("railway") == "stop":
            h = heuristic(mrtn_latlon(srctomrt), mrtn_latlon(k.get("osmid")))
            heapq.heappush(nearnode, (h, k.get("osmid")))
    return heapq.heappop(nearnode)


# retrieving lat/lon coordinates for LRT via OSMID
def mrtn_latlon(osmid):
    for k in mrtNodeList:
        if k.get("osmid") == osmid:
            return k.get("y"), k.get("x")


# retrieving lat/lon coordinates for walk via OSMID
def walk_latlon(osmid):
    for k in walkNodeList:
        if k.get("osmid") == osmid:
            return k.get("x"), k.get("y")


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


# ASTAR ALGORITHM
def lrt_astar(start_point, end_point, use):
    closepath = {}
    path = []
    routeq = []
    finalret = []
    stat = []
    strt = 0

    # finding start station (working)
    if use == "no":
        for k in mrtEdgeList:
            h = heuristic(mrtn_latlon(start_point), mrtn_latlon(k[0][1]))
            if h > 30:
                heapq.heappush(stat, (h, k[0][1]))
        strt = heapq.heappop(stat)[1]
    elif use == "yes":
        strt = start_point

    # pushing start point into heapq queue (heuristic, length(dist), parent(key), current(value))
    heapq.heappush(routeq, (0, 0, None, strt))
    closepath[strt] = None

    while True:
        temp = heapq.heappop(routeq)

        # check if we reach end point node
        if heuristic(mrtn_latlon(temp[3]), mrtn_latlon(end_point)) < 60:
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
            for i in mrtEdgeList:
                if i[0][0] == temp[3]:
                    if i[0][1] in closepath:
                        continue
                    else:
                        he = heuristic(mrtn_latlon(i[0][1]), mrtn_latlon(end_point))
                        cur_length = i[1].get('length')
                        heapq.heappush(routeq,
                                       ((he + temp[1] + cur_length), cur_length + temp[1], temp[3], i[0][1]))
                        # adding previous path to close path dict to prevent an infinite loop of short path
                        closepath[i[0][1]] = temp[3]


# ASTAR ALGORITHM
def walk_astar(start_point, end_point):
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
            for i in walkEdgeList:
                if i[0][0] == temp[3]:
                    if i[0][1] in closepath:
                        continue
                    else:
                        h = heuristic(walk_latlon(i[0][1]), walk_latlon(end_point))
                        cur_length = i[1].get('length')
                        heapq.heappush(routeq, (h + cur_length + temp[1], cur_length + temp[1], temp[3], i[0][1]))
                        # adding previous path to close path dict to prevent an infinite loop of short path
                        closepath[i[0][1]] = temp[3]


# conversion of route to coords
def convertRoute(coords):
    output = []
    for x in range(len(coords)):  # Parent Array
        for i in range(len(coords[x])):  # Inner Array
            output.append([coords[x][i][1], coords[x][i][0]])
    return output


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

pe = []
pw = []
for k in mrtNodeList:  # check for nodes which are stations
    try:
        if "PE" in k.get('ref'):
            pe.append(k.get('osmid'))
        if "PW" in k.get('ref'):
            pw.append(k.get('osmid'))
    except:  # to catch and skip noneType iterations
        continue

# testing algorithmn speed
start_time = time.time()
# user input (GUI TEAM, user input in text area will be stored here)
src = "406B, Northshore Drive, Punggol"
# punggol will return punggol mrt coordinates 406B, Northshore Drive, Punggol - 220A Sumang Lane, Singapore 821220 - Blk 126A, Punggol Field, Punggol - Waterway Cascadia, 314A, Punggol Way, Punggol
des = "Blk 126D, Punggol Field, Punggol"  # random hdb 60 Punggol East, Singapore 828825
startpoint = ox.geocode(src)
endpoint = ox.geocode(des)

# finding nearest nodes required
strtpt = ox.get_nearest_node(G_walk, startpoint, method='euclidean', return_dist=True)
endpt = ox.get_nearest_node(G_walk, endpoint, method='euclidean', return_dist=True)

# locateStrtLrt and lcoateEndLrt is only used to locate the location of both mrt
locateStrtLrt = ox.get_nearest_node(G_lrt, startpoint, method='euclidean', return_dist=True)
lcoateEndLrt = ox.get_nearest_node(G_lrt, endpoint, method='euclidean', return_dist=True)
lrtstart = lrt_nearnode(locateStrtLrt[0])[1]
lrtend = lrt_nearnode(lcoateEndLrt[0])[1]

if lrtstart == lrtend or (lrtstart == 6587709456 and lrtend == 6587709457) or \
        (lrtstart == 6587709457 and lrtend == 6587709456):
    final = walk_astar(strtpt[0], endpt[0])

    # plotting map to folium
    m = ox.plot_route_folium(G_walk, final[0], route_color='blue', route_width=5, tiles="OpenStreetMap")
    m.save('templates/astaralgo_walklrt.html')
else:
    reachLRT = ox.get_nearest_node(G_walk, mrtn_latlon(lrtstart), method='euclidean', return_dist=True)
    leaveLRT = ox.get_nearest_node(G_walk, mrtn_latlon(lrtend), method='euclidean', return_dist=True)

    eastlrt = 0
    westlrt = 0
    for i in mrtNodeList:
        if i.get('osmid') == lrtstart and lrtstart in pe:
            eastlrt += 1
            # print("scenario1")
        elif i.get('osmid') == lrtstart and lrtstart in pw:
            # print("scenario2")
            westlrt += 1
        elif i.get('osmid') == lrtend and lrtend in pe:
            # print("scenario3")
            eastlrt += 1
        elif i.get('osmid') == lrtend and lrtend in pw:
            # print("scenario4")
            westlrt += 1
        elif westlrt == 2 or eastlrt == 2:  # both lrt station in the same lrt loop
            break
        elif westlrt == 1 and eastlrt == 1:  # both lrt station in different lrt loop
            # print("break")
            break

    m = folium.Map(location=punggol, distance=distance, zoom_start=15)

    if westlrt == 1 and eastlrt == 1:  # if both stations are found on both loop (west loop and east loop)
        # algo testing walk and lrt
        walkToStation = walk_astar(strtpt[0], reachLRT[0])
        walkFromStation = walk_astar(leaveLRT[0], endpt[0])
        if lrtstart in pw:
            lrtfirst = lrt_astar(lrt_nearnode(lrtstart)[1], 6587709456, "no")
            lrtsecond = lrt_astar(6587709457, lrt_nearnode(lrtend)[1], "yes")
        elif lrtstart in pe:
            lrtfirst = lrt_astar(lrt_nearnode(lrtstart)[1], 6587709457, "no")
            lrtsecond = lrt_astar(6587709456, lrt_nearnode(lrtend)[1], "yes")

        # converting all osmnx nodes to coordinates
        walkToStation[0] = convertRoute(ox.plot.node_list_to_coordinate_lines(G_walk, walkToStation[0]))
        walkFromStation[0] = convertRoute(ox.plot.node_list_to_coordinate_lines(G_walk, walkFromStation[0]))
        lrtfirst[0] = convertRoute(ox.plot.node_list_to_coordinate_lines(G_lrt, lrtfirst[0]))
        lrtsecond[0] = convertRoute(ox.plot.node_list_to_coordinate_lines(G_lrt, lrtsecond[0]))

        folium.PolyLine(lrtfirst[0], color="red", weight=4, opacity=1).add_to(m)
        folium.PolyLine(lrtsecond[0], color="red", weight=4, opacity=1).add_to(m)
        folium.PolyLine(([lrtfirst[0][-1]] + [lrtsecond[0][0]]), color="blue", weight=4, opacity=1).add_to(m)
        folium.PolyLine((walkToStation[0] + [lrtfirst[0][0]]), color="blue", weight=4, opacity=1).add_to(m)
        folium.PolyLine(([lrtsecond[0][-1]] + walkFromStation[0]), color="blue", weight=4, opacity=1).add_to(m)
        m.save('templates/astaralgo_walklrt.html')

    else:  # if both stations are found on the same lrt loop
        # algo testing walk and lrt
        walkToStation = walk_astar(strtpt[0], reachLRT[0])
        walkFromStation = walk_astar(leaveLRT[0], endpt[0])
        mrtfinal = lrt_astar(lrt_nearnode(lrtstart)[1], lrt_nearnode(lrtend)[1], "no")

        # converting all osmnx nodes to coordinates
        walkToStation[0] = convertRoute(ox.plot.node_list_to_coordinate_lines(G_walk, walkToStation[0]))
        walkFromStation[0] = convertRoute(ox.plot.node_list_to_coordinate_lines(G_walk, walkFromStation[0]))
        mrtfinal[0] = convertRoute(ox.plot.node_list_to_coordinate_lines(G_lrt, mrtfinal[0]))

        # plotting map to folium
        folium.PolyLine(mrtfinal[0], color="red", weight=4, opacity=1).add_to(m)
        folium.PolyLine((walkToStation[0] + [mrtfinal[0][0]]), color="blue", weight=4, opacity=1).add_to(m)
        folium.PolyLine(([mrtfinal[0][-1]] + walkFromStation[0]), color="blue", weight=4, opacity=1).add_to(m)
        m.save('templates/astaralgo_walklrt.html')

print("--- %s seconds to run all calculations ---" % round((time.time() - start_time), 2))

'''
FLASK IS HERE FLASK IS HERE FLASK IS HERE FLASK IS HERE
'''
app = Flask(__name__)


@app.route("/")
def index():
    return render_template('index.html')
