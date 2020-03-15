import osmnx as ox
import heapq
import time
import math
import folium

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


# ASTAR ALGORITHM
def astar(start_point, end_point):
    closepath = {}
    path = []
    routeQueue = []
    finalret = []

    # pushing start point into heapq queue (heuristic, length(dist), parent(key), current(value))
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

            finalret.append(path)
            finalret.append(temp[1])
            return finalret

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
                        # adding previous path to close path dict to prevent an infinite loop of short path
                        closepath[edgeList[i][0][1]] = temp[3]


# main code
punggol = (1.403948, 103.909048)
distance = 2000
G_walk = ox.graph_from_point(punggol, distance=distance, truncate_by_edge=True, network_type='walk')

# storing all nodes into a list
nodeList = list(G_walk.nodes.values())
edgeList = list(G_walk.edges.items())

# user input (GUI TEAM, user input in text area will be stored here)
startstring = "32 Punggol East, Singapore 828824" # punggol will return punggol mrt coordinates
endstring = "94 punggol central, Singapore 828724"  #random hdb
startpoint = ox.geocode(startstring)
endpoint = ox.geocode(endstring)

startosmid = ox.get_nearest_node(G_walk, startpoint, method='euclidean', return_dist=True)
endosmid = ox.get_nearest_node(G_walk, endpoint, method='euclidean', return_dist=True)

final = astar(startosmid[0], endosmid[0])
print("--- %s seconds ---" % (time.time() - start_time))

# calculating estimated time to reach the destination taking avg human walking speed of 1.4m/s
totaldist = final[1] + (startosmid[1] * 1000) + (endosmid[1] * 1000)
estimatewalktime = totaldist / (1.4 * 60)
print("Time: " + str(round(estimatewalktime)) + " minutes" + "\nDistance: " + str(round((totaldist / 1000), 2)) + " km")

# plotting map to folium
# m = folium.Map(location=punggol)
m = ox.plot_route_folium(G_walk, final[0], route_color='#00008B', route_width=5, tiles="OpenStreetMap")

m.save('templates/astar_walking.html')
