from flask import Flask
import folium
from collections import deque, namedtuple
import pandas as pd
import osmnx as ox
import heapq
import time
import math

start_time = time.time()
starting = time.time()
ending = time.time()


# retrieving lat/lon coords via OSMID
def latlon(osmid):
    for i in range(0, len(nodeList)):
        if nodeList[i].get("osmid") == osmid:
            lat = nodeList[i].get("x")
            lon = nodeList[i].get("y")
    coord = (lat, lon)
    return coord


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


# # alternate heuristic calculation
# def distance(starting, ending):
#     lat1, lon1 = starting
#     lat2, lon2 = ending
#     radius = 6371  # km
#     a = radius * math.acos(math.sin(math.radians(lat1))) * math.sin(math.radians(lat2)) + math.cos(math.radians(lat1)) \
#         * math.cos(math.radians(lat2)) * math.cos(math.radians(lon1) - math.radians(lon2))
#     dist = 1000 * a
#     return dist


# DIJKSTRA
def astar(start_point, end_point):
    closepath = {}
    path = []
    routeQueue = []

    # pushing start point into heapq queue
    heapq.heappush(routeQueue, (0, 0, None, start_point))
    closepath[start_point] = None

    while True:
        temp = heapq.heappop(routeQueue)
        # print(temp[0], temp[1], temp[2])
        if temp[3] == end_point:
            path.append(temp[3])
            rear = temp[2]

            # path list to append all osmid by key in closepath with the first being the end node
            while rear is not None:
                path.append(rear)
                rear = closepath.get(rear)
            # reverse the path list into start to end
            path = path[::-1]
            return path

        for i in range(0, len(edgeList)):
            if edgeList[i][0][0] == temp[3]:
                if edgeList[i][0][1] in closepath:
                    continue
                else:
                    h = heuristic(latlon(edgeList[i][0][1]), latlon(end_point))
                    cur_length = edgeList[i][1].get('length')
                    if h < starting:
                        heapq.heappush(routeQueue,
                                       ((h + temp[1] + cur_length), cur_length + temp[1], temp[3], edgeList[i][0][1]))
                        closepath[edgeList[i][0][1]] = temp[3]


# main code
punggol = (1.403948, 103.909048)
distance = 1500
G = ox.graph_from_point(punggol, distance=distance, truncate_by_edge=True, network_type='walk')

# # Import to CSV for reference
n, e = ox.graph_to_gdfs(G)
e.to_csv("edge.csv")
n.to_csv("node.csv")

# storing all nodes into a list
nodeList = list(G.nodes.values())
edgeList = list(G.edges.items())

# finding start and end point in the list and storing into variables
start = (103.9073345, 1.4060506)
end = (103.9172982, 1.3956014)

for i in range(0, len(nodeList)):
    if (nodeList[i].get("x") == start[0]) and (nodeList[i].get("y") == start[1]):
        startosmid = nodeList[i].get("osmid")
    if (nodeList[i].get("x") == end[0]) and (nodeList[i].get("y") == end[1]):
        endosmid = nodeList[i].get("osmid")

final = astar(startosmid, endosmid)
print("--- %s seconds ---" % (time.time() - start_time))

# plotting map
ox.plot_graph_route(G, final, fig_height=10, fig_width=10)
