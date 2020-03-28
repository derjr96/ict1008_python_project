from flask import Flask, render_template
import osmnx as ox
import heapq
import time
import math


# retrieving lat/lon coordinates via OSMID
def latlon(osmid):
    for k in driveNodeList:
        if k.get("osmid") == osmid:
            return k.get("x"), k.get("y")


# calculating heuristic between two lat/lon points
def heuristic(start, end):
    lat1, lon1 = start[0], start[1]
    lat2, lon2 = end[0], end[1]
    radius = 6371.01  # km

    distlat = math.radians(lat2 - lat1)
    distlon = math.radians(lon2 - lon1)
    a = math.sin(distlat / 2) * math.sin(distlat / 2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(distlon / 2) * math.sin(distlon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    dist = radius * c * 1000
    return dist


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

        for i in driveEdgeList:
            if i[0][0] == temp[2]:
                if i[0][1] in closepath:
                    continue
                else:
                    heapq.heappush(routeQueue, (i[1].get('length') + temp[0], temp[2], i[0][1]))
                    # print("Parent: ", temp[2], "\nCurrent: ", edgeList[i][0][1])
                    closepath[i[0][1]] = temp[2]

# main code
punggol = (1.403948, 103.909048)
distance = 3000
G_drive = ox.graph_from_point(punggol, distance=distance, truncate_by_edge=True, network_type='drive', simplify=True)

# # Import to CSV for reference
n, e = ox.graph_to_gdfs(G_drive)
e.to_csv("data/edge.csv")
n.to_csv("data/node.csv")

# storing all nodes into a list
driveNodeList = list(G_drive.nodes.values())
driveEdgeList = list(G_drive.edges.items())
ox.plot_graph(G_drive)

# user input (GUI TEAM, user input in text area will be stored here)
src = "Edgedale Plains, Punggol, Singapore 828730"  # punggol will return punggol mrt coordinates
des = "Waterway Cascadia, 314A, Punggol Way, Punggol"  # random hdb
startpoint = ox.geocode(src)
endpoint = ox.geocode(des)
print(startpoint, endpoint)

startosmid = ox.get_nearest_node(G_drive, startpoint, method='euclidean', return_dist=True)
endosmid = ox.get_nearest_node(G_drive, endpoint, method='euclidean', return_dist=True)

print(startosmid, endosmid)
# testing algorithmn speed
start_time = time.time()
final = dijkstra(startosmid[0], endosmid[0])
print("--- %s seconds ---" % round((time.time() - start_time), 2))

# calculating estimated time to reach the destination taking avg human walking speed of 1.4m/s
totaldist = final[1] + (startosmid[1] * 1000) + (endosmid[1] * 1000)
estwalk = totaldist / (1.4 * 60)
print("Time: " + str(round(estwalk)) + " minutes" + "\nDistance: " + str(round((totaldist / 1000), 2)) + " km")

# plotting map to folium
print(final)
m = ox.plot_route_folium(G_drive, final, route_color='#00008B', route_width=5, tiles="OpenStreetMap")
m.save('templates/astar_driving.html')

'''
FLASK IS HERE FLASK IS HERE FLASK IS HERE FLASK IS HERE
'''
app = Flask(__name__)


@app.route("/")
def index():
    return render_template('index.html')
