import osmnx as ox
import heapq
import time


def plotWalk(G, start, end):
    startTime = time.time()

    # punggol = (1.4041070, 103.9025242)
    # distance = 3000
    # G = ox.graph_from_point(punggol, distance=distance, truncate_by_edge=True, network_type='walk')

    # storing all nodes into a list
    edgeList = list(G.edges.items())

    start = (float(start[0]), float(start[1]))
    end = (float(end[0]), float(end[1]))

    startosmid = ox.get_nearest_node(G, start)

    endosmid = ox.get_nearest_node(G, end)

    final = dijkstra(startosmid, endosmid, edgeList)

    print("Walk Route Retrieval Takes: ", round(time.time() - startTime, 2))
    return final


# DIJKSTRA
def dijkstra(start_point, end_point, edgeList):
    closepath = {}
    path = []
    routeQueue = []

    # pushing start point into heapq queue (heuristic, length(dist), parent(key), current(value))
    heapq.heappush(routeQueue, (0, None, start_point))
    closepath[start_point] = None

    # while loop will run for V amount on times which is how many vertex to reach the end point - Complexity: O(V)
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

        # with heapq, dijkstra, it will run based on the number of edges for Complexity of O(LogE)
        for i in range(0, len(edgeList)):
            if edgeList[i][0][0] == temp[2]:
                if edgeList[i][0][1] in closepath:
                    continue
                else:
                    heapq.heappush(routeQueue, (edgeList[i][1].get('length') + temp[0], temp[2], edgeList[i][0][1]))
                    # print("Parent: ", temp[2], "\nCurrent: ", edgeList[i][0][1])
                    closepath[edgeList[i][0][1]] = temp[2]
