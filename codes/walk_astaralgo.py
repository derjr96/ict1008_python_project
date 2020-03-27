import osmnx as ox
import heapq
import time
import math


class AstarWalkAlgo:
    def __init__(self, s, d, G_walk, walkNodeList, walkEdgeList):
        self.G_walk = G_walk

        self.src = s
        self.des = d
        self.variable = 0
        self.variable1 = 0
        self.variable2 = 0
        self.walkNodeList = walkNodeList
        self.walkEdgeList = walkEdgeList

    # retrieving lat/lon coordinates via OSMID
    def latlon(self, osmid):
        for k in self.walkNodeList:
            if k.get("osmid") == osmid:
                return k.get("x"), k.get("y")

    # calculating heuristic between two lat/lon points
    def heuristic(self, start, end):
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
    def walk_astar(self, start_point, end_point):
        closepath = {}
        path = []
        routeq = []
        finalret = []

        main_h = self.heuristic(self.latlon(start_point), self.latlon(end_point))
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
                for i in self.walkEdgeList:
                    if i[0][0] == temp[3]:
                        if i[0][1] in closepath:
                            continue
                        else:
                            h = self.heuristic(self.latlon(i[0][1]), self.latlon(end_point))
                            if h < main_h:
                                cur_length = i[1].get('length') + temp[1]
                                heur = h + cur_length
                                heapq.heappush(routeq, (heur, cur_length, temp[3], i[0][1]))
                                # adding previous path to close path dict to prevent an infinite loop of short path
                                closepath[i[0][1]] = temp[3]

    def generate(self):
        # main code

        # storing all nodes into a list
        self.walkNodeList = list(self.G_walk.nodes.values())
        self.walkEdgeList = list(self.G_walk.edges.items())

        # user input (GUI TEAM, user input in text area will be stored here)
        # src = "Punggol"  # punggol will return punggol mrt coordinates
        # des = "Blk 612, Punggol Drive, Punggol"  # random hdb
        startpoint = ox.geocode(self.src)
        endpoint = ox.geocode(self.des)

        startosmid = ox.get_nearest_node(self.G_walk, startpoint, method='euclidean', return_dist=True)
        endosmid = ox.get_nearest_node(self.G_walk, endpoint, method='euclidean', return_dist=True)

        # testing algorithmn speed
        start_time = time.time()
        final = self.walk_astar(startosmid[0], endosmid[0])
        print("--- %s seconds ---" % round((time.time() - start_time), 2))

        # calculating estimated time to reach the destination taking avg human walking speed of 1.4m/s
        totaldist = final[1] + (startosmid[1] * 1000) + (endosmid[1] * 1000)
        estwalk = totaldist / (1.4 * 60)
        print("Time: " + str(round(estwalk)) + " minutes" + "\nDistance: " + str(round((totaldist / 1000), 2)) + " km")

        self.variable = str(round((time.time() - start_time), 2))
        self.variable1 = str(round(estwalk))
        self.variable2 = str(round((totaldist/1000), 2))

        # plotting map to folium
        m = ox.plot_route_folium(self.G_walk, final[0], route_color='#00008B', route_width=5, tiles="OpenStreetMap")
        #m.save("templates/astar_walking.html")
        m.save("templates/default.html")
        print("Successfully overwrite default.html!!!")

    def printout(self):
        return [self.variable, self.variable1, self.variable2]

# aswa = AstarWalkAlgo("Punggol", "Blk 612, Punggol Drive, Punggol")
# aswa.generate()
