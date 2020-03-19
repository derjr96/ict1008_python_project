import osmnx as ox
import heapq


def plotWalk(start, end):
    punggol = (1.4041070, 103.9025242)
    distance = 3000
    G = ox.graph_from_point(punggol, distance=distance, truncate_by_edge=True, network_type='walk')

    # storing all nodes into a list
    nodeList = list(G.nodes.values())
    edgeList = list(G.edges.items())

    # finding start and end point in the list and storing into variables
    start = (float(start[0]), float(start[1]))
    end = (float(end[0]), float(end[1]))

    startosmid = None
    endosmid = None

    for i in range(0, len(nodeList)):
        if (nodeList[i].get("x") == start[0]) and (nodeList[i].get("y") == start[1]):
            startosmid = nodeList[i].get("osmid")
        if (nodeList[i].get("x") == end[0]) and (nodeList[i].get("y") == end[1]):
            endosmid = nodeList[i].get("osmid")

    if startosmid is None:
        startosmid = ox.get_nearest_node(G, start)

    if endosmid is None:
        endosmid = ox.get_nearest_node(G, end)

    final = dijkstra(startosmid, endosmid, edgeList)

    return final


# DIJKSTRA
def dijkstra(start_point, end_point, edgeList):
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
