import pandas as pd
import geopandas as gpd
import geopy
from geopy import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import osmnx as ox
import time
from osmnx import settings
from osmnx.utils import make_str, log
from osmnx.geo_utils import get_largest_component
from osmnx.downloader import overpass_request
from osmnx.errors import *
import networkx as nx


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

punggol = (1.403948, 103.909048)
distance = 2000

G_walk = ox.graph_from_point(punggol, distance=distance, truncate_by_edge=True, network_type='drive', simplify=True)
mrt_query_str = '[out:json][timeout:180];(relation["network"="Singapore Rail"]["route"="monorail"](1.4011,103.8977,1.4154,103.9231);>;);out;'
mrt_response_json = overpass_request(data={'data': mrt_query_str}, timeout=180)
G_lrt = create_graph(mrt_response_json)

# # Import to CSV for reference
n, e = ox.graph_to_gdfs(G_walk)
e.to_csv("data/edge.csv")
n.to_csv("data/node.csv")

# storing all nodes into a list
walkNodeList = list(G_walk.nodes.values())
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


locator = Nominatim(user_agent="myGeocoder", timeout=20)

building = {}
autofillList = []
# testing algorithmn speed
start_time = time.time()
for k in walkNodeList:
    coordinates = k.get('y'), k.get('x')
    location = locator.reverse(coordinates)
    k["address"] = location[0]
    if location[0] not in autofillList:
        print(location[0])
        autofillList.append(location[0])
    else:
        continue

for item in mrtNodeList:
    try:
        if "PE" in item.get('ref') or "PW" in item.get('ref'):
            coordinates = item.get('y'), item.get('x')
            location = locator.reverse(coordinates)
            print(location[0])
            autofillList.append(location[0])
    except:  # to catch and skip noneType iterations
        continue
autofillList.append('Punggol')

print("--- %s seconds to run all calculations ---" % round((time.time() - start_time), 2))

# print(walkNodeList)
print(autofillList)
df = pd.DataFrame(walkNodeList)
df.to_csv('data/rg_walk_node.csv', index=False)
