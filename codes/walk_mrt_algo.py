import heapq
import folium
import math
import time
from datetime import datetime
import osmnx as ox


class AstarWalkMrtAlgo:
    def __init__(self, s, d, G_walk, G_lrt, walkNodeList, walkEdgeList, mrtNodeList, mrtEdgeList):
        self.G_lrt = G_lrt
        self.G_walk = G_walk

        self.walkNodeList = walkNodeList
        self.mrtNodeList = mrtNodeList
        self.walkEdgeList = walkEdgeList
        self.mrtEdgeList = mrtEdgeList

        # for walk and mrt output
        self.wlvariable = 0
        self.wlvariable1 = 0
        self.wlvariable2 = 0
        self.wlvariable3 = 0
        self.wlvariable4 = 0
        self.wlvariable5 = 0
        self.wlvariable6 = 0
        self.wlvariable7 = 0

        self.src = s
        self.des = d

    # LRT fare based on distance travelled
    def lrtFareCal(self, distance):
        if distance <= 3.2:
            print("Student Fare: $0.42")
            print("Adult Fare: $0.92")
            print("Senior Citizen Fare: $0.59")
            self.wlvariable1 = "Student Fare: $0.42"
            self.wlvariable2 = "Adult Fare: $0.92"
            self.wlvariable3 = "Senior Citizen Fare: $0.59"
        elif 4.2 >= distance > 3.2:
            print("Student Fare: $0.47")
            print("Adult Fare: $1.02")
            print("Senior Citizen Fare: $0.66")
            self.wlvariable1 = "Student Fare: $0.47"
            self.wlvariable2 = "Adult Fare: $1.02"
            self.wlvariable3 = "Senior Citizen Fare: $0.66"
        elif 5.2 >= distance > 4.2:
            print("Student Fare: $0.52")
            print("Adult Fare: $1.12")
            print("Senior Citizen Fare: $0.73")
            self.wlvariable1 = "Student Fare: $0.52"
            self.wlvariable2 = "Adult Fare: $1.12"
            self.wlvariable3 = "Senior Citizen Fare: $0.73"
        elif 6.2 >= distance > 5.2:
            print("Student Fare: $0.47")
            print("Adult Fare: $1.22")
            print("Senior Citizen Fare: $0.80")
            self.wlvariable1 = "Student Fare: $0.47"
            self.wlvariable2 = "Adult Fare: $1.22"
            self.wlvariable3 = "Senior Citizen Fare: $0.80"

    # finding which mrt station is closest to the start/end point
    def lrt_nearnode(self, srctomrt):
        nearnode = []
        for k in self.mrtNodeList:
            if k.get("railway") == "station" or k.get("railway") == "stop":
                h = self.heuristic(self.mrtn_latlon(srctomrt), self.mrtn_latlon(k.get("osmid")))
                heapq.heappush(nearnode, (h, k.get("osmid")))
        return heapq.heappop(nearnode)

    # retrieving lat/lon coordinates for LRT via OSMID
    def mrtn_latlon(self, osmid):
        for k in self.mrtNodeList:
            if k.get("osmid") == osmid:
                return k.get("y"), k.get("x")

    # retrieving lat/lon coordinates for walk via OSMID
    def walk_latlon(self, osmid):
        for k in self.walkNodeList:
            if k.get("osmid") == osmid:
                return k.get("x"), k.get("y")

    # calculating heuristic between two lat/lon points
    def heuristic(self, start, end):
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
    def lrt_astar(self, start_point, end_point, use):
        closepath = {}
        path = []
        routeq = []
        finalret = []
        stat = []
        strt = 0

        # finding start station (working)
        if use == "no":
            for k in self.mrtEdgeList:
                h = self.heuristic(self.mrtn_latlon(start_point), self.mrtn_latlon(k[0][1]))
                if h > 30:
                    heapq.heappush(stat, (h, k[0][1]))
            strt = heapq.heappop(stat)[1]
        elif use == "yes":
            strt = start_point

        # pushing start point into heapq queue (heuristic, length(dist), parent(key), current(value))
        heapq.heappush(routeq, (0, 0, None, strt))
        closepath[strt] = None

        while True:
            temp = heapq.heappop(routeq)

            # check if we reach end point node
            if self.heuristic(self.mrtn_latlon(temp[3]), self.mrtn_latlon(end_point)) < 60:
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
                for i in self.mrtEdgeList:
                    if i[0][0] == temp[3]:
                        if i[0][1] in closepath:
                            continue
                        else:
                            he = self.heuristic(self.mrtn_latlon(i[0][1]), self.mrtn_latlon(end_point))
                            cur_length = i[1].get('length')
                            heapq.heappush(routeq,
                                           ((he + temp[1] + cur_length), cur_length + temp[1], temp[3], i[0][1]))
                            # adding previous path to close path dict to prevent an infinite loop of short path
                            closepath[i[0][1]] = temp[3]

    # ASTAR ALGORITHM
    def walk_astar(self, start_point, end_point):
        closepath = {}
        path = []
        routeq = []
        finalret = []

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
                            h = self.heuristic(self.walk_latlon(i[0][1]), self.walk_latlon(end_point))
                            cur_length = i[1].get('length')
                            heapq.heappush(routeq, (h + cur_length + temp[1], cur_length + temp[1], temp[3], i[0][1]))
                            # adding previous path to close path dict to prevent an infinite loop of short path
                            closepath[i[0][1]] = temp[3]

    # conversion of route to coords
    def convertRoute(self, coords):
        output = []
        for x in range(len(coords)):  # Parent Array
            for i in range(len(coords[x])):  # Inner Array
                output.append([coords[x][i][1], coords[x][i][0]])
        return output

    def generate(self):
        # main code
        punggol = (1.403948, 103.909048)
        distance = 2000

        pe = []
        pw = []
        for k in self.mrtNodeList:  # check for nodes which are stations
            try:
                if "PE" in k.get('ref'):
                    pe.append(k.get('osmid'))
                if "PW" in k.get('ref'):
                    pw.append(k.get('osmid'))
            except:  # to catch and skip noneType iterations
                continue

        # testing algorithmn speed
        start_time = time.time()
        # user input (GUI TEAM, user input in text area will be stored here)
        # src = "Nibong, Punggol"     # 406B, Northshore Drive, Punggol
        # punggol will return punggol mrt coordinates 406B, Northshore Drive, Punggol - 220A Sumang Lane, Singapore 821220 - Blk 126A, Punggol Field, Punggol - Waterway Cascadia, 314A, Punggol Way, Punggol
        # des = "406B, Northshore Drive, Punggol"  # random hdb 60 Punggol East, Singapore 828825
        startpoint = ox.geocode(self.src)
        endpoint = ox.geocode(self.des)

        # finding nearest nodes required
        strtpt = ox.get_nearest_node(self.G_walk, startpoint, method='euclidean', return_dist=True)
        endpt = ox.get_nearest_node(self.G_walk, endpoint, method='euclidean', return_dist=True)

        # locateStrtLrt and lcoateEndLrt is only used to locate the location of both mrt
        locateStrtLrt = ox.get_nearest_node(self.G_lrt, startpoint, method='euclidean', return_dist=True)
        lcoateEndLrt = ox.get_nearest_node(self.G_lrt, endpoint, method='euclidean', return_dist=True)
        lrtstart = self.lrt_nearnode(locateStrtLrt[0])[1]
        lrtend = self.lrt_nearnode(lcoateEndLrt[0])[1]

        if lrtstart == lrtend or (lrtstart == 6587709456 and lrtend == 6587709457) or \
                (lrtstart == 6587709457 and lrtend == 6587709456):
            final = self.walk_astar(strtpt[0], endpt[0])

            # plotting map to folium
            m = ox.plot_route_folium(self.G_walk, final[0], route_color='blue', route_width=5, tiles="OpenStreetMap",
                                     popup_attribute="There is no LRT to bring you to your destination, please walk.")
            # m.save('templates/astaralgo_walklrt.html')
            m.save('templates/default.html')
        else:
            reachLRT = ox.get_nearest_node(self.G_walk, self.mrtn_latlon(lrtstart), method='euclidean', return_dist=True)
            leaveLRT = ox.get_nearest_node(self.G_walk, self.mrtn_latlon(lrtend), method='euclidean', return_dist=True)

            eastlrt = 0
            westlrt = 0
            for i in self.mrtNodeList:
                mrtid = i.get('osmid')
                if mrtid == lrtstart and lrtstart in pe:
                    eastlrt += 1
                    # print("scenario1")
                elif mrtid == lrtstart and lrtstart in pw:
                    # print("scenario2")
                    westlrt += 1
                elif mrtid == lrtend and lrtend in pe:
                    # print("scenario3")
                    eastlrt += 1
                elif mrtid == lrtend and lrtend in pw:
                    # print("scenario4")
                    westlrt += 1
                elif westlrt == 2 or eastlrt == 2:  # both lrt station in the same lrt loop
                    break
                elif westlrt == 1 and eastlrt == 1:  # both lrt station in different lrt loop
                    # print("break")
                    break

            m = folium.Map(location=punggol, distance=distance, zoom_start=15, tiles="OpenStreetMap")

            if westlrt == 1 and eastlrt == 1:  # if both stations are found on both loop (west loop and east loop)
                # algo testing walk and lrt
                walkToStation = self.walk_astar(strtpt[0], reachLRT[0])
                walkFromStation = self.walk_astar(leaveLRT[0], endpt[0])
                if lrtstart in pw:
                    lrtfirst = self.lrt_astar(self.lrt_nearnode(lrtstart)[1], 6587709456, "no")
                    lrtsecond = self.lrt_astar(6587709457, self.lrt_nearnode(lrtend)[1], "yes")
                elif lrtstart in pe:
                    lrtfirst = self.lrt_astar(self.lrt_nearnode(lrtstart)[1], 6587709457, "no")
                    lrtsecond = self.lrt_astar(6587709456, self.lrt_nearnode(lrtend)[1], "yes")

                # converting all osmnx nodes to coordinates
                walkToStation[0] = self.convertRoute(ox.plot.node_list_to_coordinate_lines(self.G_walk, walkToStation[0]))
                walkFromStation[0] = self.convertRoute(
                    ox.plot.node_list_to_coordinate_lines(self.G_walk, walkFromStation[0]))
                lrtfirst[0] = self.convertRoute(ox.plot.node_list_to_coordinate_lines(self.G_lrt, lrtfirst[0]))
                lrtsecond[0] = self.convertRoute(ox.plot.node_list_to_coordinate_lines(self.G_lrt, lrtsecond[0]))

                # calculating estimated time, cost, distance to reach the destination
                statDist = 10300 / 14
                totalDistLRT = (lrtfirst[1] + lrtsecond[1]) / 1000  # convert to meters to km
                now = datetime.now()
                timenow = now.strftime("%H")
                waitTime = 0
                if "10" > timenow > "6":
                    print("--- PEAK HOUR ---")
                    waitTime = 3
                    self.wlvariable = "--- PEAK HOUR ---"
                else:
                    print("--- NON-PEAK HOUR ---")
                    waitTime = 7
                    self.wlvariable = "--- NON-PEAK HOUR ---"
                self.lrtFareCal(totalDistLRT)  # call fare function
                numStation = math.floor(totalDistLRT / statDist + 2)
                totatTimeLRT = numStation + (
                            (totalDistLRT * 1000) / (45000 / 60)) + waitTime  # avg mrt speed 45km/hr - 750m per minute
                totalDistWalk = (walkToStation[1] + walkFromStation[1]) / 1000  # convert to meters to km
                estwalk = (totalDistWalk * 1000) / (5000 / 60)  # avg walking speed 1.4m/min - 5km/hr
                self.wlvariable4 = ("\nTime taken : " + str(round(totatTimeLRT + estwalk)) + " minutes\n")
                self.wlvariable5 = ("\nDistance travelled: " + str(round((totalDistWalk + totalDistLRT), 2)) + " km\n")
                self.wlvariable6 = ("Transfer: 1, Punggol Station")
                # plotting on folium map
                folium.PolyLine(lrtfirst[0], color="red", weight=2, opacity=1,
                                tooltip="Change LRT at Punggol Station.").add_to(m)
                folium.PolyLine(lrtsecond[0], color="red", weight=2, opacity=1,
                                tooltip="Continue here to your destination.").add_to(m)
                folium.PolyLine(([lrtfirst[0][-1]] + [lrtsecond[0][0]]), color="blue", weight=2, opacity=1,
                                tooltip="Transit LRT here!").add_to(m)
                folium.PolyLine(([startpoint] + walkToStation[0] + [lrtfirst[0][0]]), color="blue",
                                weight=2, opacity=1).add_to(m)
                folium.PolyLine(([lrtsecond[0][-1]] + walkFromStation[0] + [endpoint]), color="blue",
                                weight=2, opacity=1).add_to(m)
                # m.save('templates/astaralgo_walklrt.html')
                m.save('templates/default.html')

            else:  # if both stations are found on the same lrt loop
                # algo testing walk and lrt
                walkToStation = self.walk_astar(strtpt[0], reachLRT[0])
                walkFromStation = self.walk_astar(leaveLRT[0], endpt[0])
                lrtfinal = self.lrt_astar(self.lrt_nearnode(lrtstart)[1], self.lrt_nearnode(lrtend)[1], "no")

                # converting all osmnx nodes to coordinates
                walkToStation[0] = self.convertRoute(ox.plot.node_list_to_coordinate_lines(self.G_walk, walkToStation[0]))
                walkFromStation[0] = self.convertRoute(
                    ox.plot.node_list_to_coordinate_lines(self.G_walk, walkFromStation[0]))
                lrtfinal[0] = self.convertRoute(ox.plot.node_list_to_coordinate_lines(self.G_lrt, lrtfinal[0]))

                # calculating estimated time, cost, distance to reach the destination
                statDist = 10300 / 14
                totalDistLRT = (lrtfinal[1]) / 1000  # convert to meters to km
                now = datetime.now()
                timenow = now.strftime("%H")
                waitTime = 0
                if "10" > timenow > "6":
                    print("--- PEAK HOUR ---")
                    waitTime = 3
                    self.wlvariable = "--- PEAK HOUR ---"
                else:
                    print("--- NON-PEAK HOUR ---")
                    waitTime = 7
                    self.wlvariable = "--- NON-PEAK HOUR ---"
                self.lrtFareCal(totalDistLRT)  # call fare function
                numStation = math.floor(totalDistLRT / statDist + 2)
                totatTimeLRT = numStation + (
                        (totalDistLRT * 1000) / (45000 / 60)) + waitTime  # avg mrt speed 45km/hr - 750m per minute
                totalDistWalk = (walkToStation[1] + walkFromStation[1]) / 1000  # convert to meters to km
                estwalk = (totalDistWalk * 1000) / (5000 / 60)  # avg walking speed 1.4m/min - 5km/hr
                self.wlvariable4 = ("\nTime taken : " + str(round(totatTimeLRT + estwalk)) + " minutes")
                self.wlvariable5 = ("\nDistance travelled: " + str(round((totalDistWalk + totalDistLRT), 2)) + " km\n")
                self.wlvariable6 = ("Transfer: None.")

                # plotting map to folium
                folium.PolyLine(lrtfinal[0], color="red", weight=2, opacity=1).add_to(m)
                folium.PolyLine(([startpoint] + walkToStation[0] + [lrtfinal[0][0]]), color="blue",
                                weight=2, opacity=1).add_to(m)
                folium.PolyLine(([lrtfinal[0][-1]] + walkFromStation[0] + [endpoint]), color="blue",
                                weight=2, opacity=1).add_to(m)
                # m.save('templates/astaralgo_walklrt.html')
                m.save('templates/default.html')

        self.wlvariable7 = ("Seconds to run all calculations: %s seconds" % round((time.time() - start_time), 2))

    def printout2(self):
        return [self.wlvariable, self.wlvariable1, self.wlvariable2, self.wlvariable3, self.wlvariable4, self.wlvariable5, self.wlvariable6, self.wlvariable7]