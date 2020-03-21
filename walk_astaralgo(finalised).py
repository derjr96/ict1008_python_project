from flask import Flask, render_template
import osmnx as ox
import heapq
import time
import math


# retrieving lat/lon coordinates via OSMID
def latlon(osmid):
    for k in walkNodeList:
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



# ASTAR ALGORITHM
def walk_astar(start_point, end_point):
    closepath = {}
    path = []
    routeq = []
    finalret = []

    main_h = heuristic(latlon(start_point), latlon(end_point))
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
                        h = heuristic(latlon(i[0][1]), latlon(end_point))
                        if h < main_h:
                            cur_length = i[1].get('length') + temp[1]
                            heur = h + cur_length
                            heapq.heappush(routeq, (heur, cur_length, temp[3], i[0][1]))
                            # adding previous path to close path dict to prevent an infinite loop of short path
                            closepath[i[0][1]] = temp[3]


# main code
punggol = (1.403948, 103.909048)
distance = 2000
G_walk = ox.graph_from_point(punggol, distance=distance, truncate_by_edge=True, network_type='walk')

# storing all nodes into a list
walkNodeList = list(G_walk.nodes.values())
walkEdgeList = list(G_walk.edges.items())

# user input (GUI TEAM, user input in text area will be stored here)
src = "Punggol"  # punggol will return punggol mrt coordinates
des = "Blk 612, Punggol Drive, Punggol"  # random hdb
startpoint = ox.geocode(src)
endpoint = ox.geocode(des)

startosmid = ox.get_nearest_node(G_walk, startpoint, method='euclidean', return_dist=True)
endosmid = ox.get_nearest_node(G_walk, endpoint, method='euclidean', return_dist=True)

# testing algorithmn speed
start_time = time.time()
final = walk_astar(startosmid[0], endosmid[0])
print("--- %s seconds ---" % round((time.time() - start_time), 2))

# calculating estimated time to reach the destination taking avg human walking speed of 1.4m/s
totaldist = final[1] + (startosmid[1] * 1000) + (endosmid[1] * 1000)
estwalk = totaldist / (1.4 * 60)
print("Time: " + str(round(estwalk)) + " minutes" + "\nDistance: " + str(round((totaldist / 1000), 2)) + " km")

# plotting map to folium
print(final[0])
m = ox.plot_route_folium(G_walk, final[0], route_color='#00008B', route_width=5, tiles="OpenStreetMap")
m.save('templates/astar_walking.html')

'''
FLASK IS HERE FLASK IS HERE FLASK IS HERE FLASK IS HERE
'''
app = Flask(__name__)


@app.route("/")
def index():
    return render_template('index.html')
