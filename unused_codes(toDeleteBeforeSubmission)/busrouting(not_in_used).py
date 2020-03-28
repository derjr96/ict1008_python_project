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

# bbox = (1.4220, 1.3857, 103.9259, 103.8873)
# potato = ox.osm_net_download(north=1.4220, south=1.3857, east=103.9259, west=103.8873,
#                      network_type='all_private', timeout=180, memory=None,
#                      max_query_area_size=50*1000*50*1000, infrastructure='way["highway"]',
#                      custom_filter=None)
query_str = '[out:json][timeout:180];(relation["type"="route"]["route"="bus"](1.385700,103.887300,1.422000,103.925900);>;);out;'
response_json = overpass_request(data={'data':query_str}, timeout=180)

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
    useful_tags_node = ['ref', 'highway', 'route_ref', 'type']
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
        elif element['type'] == 'way': #osm calls network paths 'ways'
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

    log('Created graph with {:,} nodes and {:,} edges in {:,.2f} seconds'.format(len(list(G.nodes())), len(list(G.edges())), time.time()-start_time))

    # add length (great circle distance between nodes) attribute to each edge to
    # use as weight
    if len(G.edges) > 0:
        G = ox.add_edge_lengths(G)

    return G
pp = pprint.PrettyPrinter(indent=4)
pp.pprint(response_json)

G = create_graph(response_json)
# n, e = ox.graph_to_gdfs(G)
# e.to_csv("bus_edge.csv")
# n.to_csv("bus_node.csv")
ox.plot_graph(G)