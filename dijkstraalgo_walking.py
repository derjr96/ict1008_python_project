from flask import Flask
import folium
from collections import deque, namedtuple
import pandas as pd
import osmnx as ox
import heapq
import time


punggol = (1.403948, 103.909048)
distance = 1500
G = ox.graph_from_point(punggol, distance=distance, truncate_by_edge=True, network_type='walk')

# # Import to CSV for reference
# n, e = ox.graph_to_gdfs(G)
# e.to_csv("edge.csv")
# n.to_csv("node.csv")

# storing all nodes into a list
nodeList = list(G.nodes.values())
edgeList = list(G.edges.items())


# DIJKSTRA
def dijkstra(start_point, end_point):
    closepath = {}
    path = []
    routeQueue = []

    # pushing start point into heapq queue
    heapq.heappush(routeQueue, (0, None, start_point))
    closepath[start_point] = None

    while True:
        temp = heapq.heappop(routeQueue)
        # print(temp[0], temp[1], temp[2])
        if temp[2] == end_point:
            path.append(temp[2])
            rear = temp[1]

            # path list to append all osmid by key in closepath with the first being the end node
            while rear is not None:
                path.append(rear)
                rear = closepath.get(rear)
            # reverse the path list into start to end
            path = path[::-1]
            return path

        for i in range(0, len(edgeList)):
            if edgeList[i][0][0] == temp[2]:
                if edgeList[i][0][1] in closepath:
                    continue
                else:
                    heapq.heappush(routeQueue, (edgeList[i][1].get('length') + temp[0], temp[2], edgeList[i][0][1]))
                    # print("Parent: ", temp[2], "\nCurrent: ", edgeList[i][0][1])
                    closepath[edgeList[i][0][1]] = temp[2]

# END OF DIJKSTRA

# finding start and end point in the list and storing into variables
start = (103.9073345, 1.4060506)
end = (103.9172982, 1.3956014)

for i in range(0, len(nodeList)):
    if (nodeList[i].get("x") == start[0]) and (nodeList[i].get("y") == start[1]):
        startosmid = nodeList[i].get("osmid")
    if (nodeList[i].get("x") == end[0]) and (nodeList[i].get("y") == end[1]):
        endosmid = nodeList[i].get("osmid")

# testing algorithmn speed
start_time = time.time()

final = dijkstra(6543124543, 5218598739)
print("--- %s seconds ---" % (time.time() - start_time))

# plotting map to folium
m = folium.Map(location=punggol)
ox.plot_route_folium(G, final, route_color='#00008B', route_width=5).add_child(m)
m.save('templates/dijkstra_walking.html')