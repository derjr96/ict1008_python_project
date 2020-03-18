import json
import math

import pandas as pd
import folium
import osmnx as ox
import networkx as nx
import time
import overpy
import scripts.findShortestBusRoute as findShortestBusRoute


def removeDupes(list):
    tempArray = []
    for i in list:
        if i not in tempArray:
            tempArray.append(i)
    return tempArray


def findPath(paths):
    api = overpy.Overpass()
    start_time = time.time()
    start = time.time()
    end = time.time()
    punggol = (1.4041070, 103.9025242)  # Punggol Interchange as mid point
    distance = 3000
    G = ox.graph_from_point(punggol, distance=distance, network_type='drive_service')

    tupleOfStartEnds = []
    tupleOfStartEndQueriesNodes = []  # Node IDs of BusStops in [(Start1, End2), (Start2, End3)] format
    route = []  # Routes to travel from [[Route Start1 to End 2], [Route Start2 to End3]] format

    for i in range(len(paths)):
        if i != len(paths) - 1:
            tupleOfStartEnds.append((paths[i], paths[i + 1]))

    # Retriving the long and lat of the nodes using busstop codes
    for i in range(len(tupleOfStartEnds)):
        resultStart = api.query("node['asset_ref'='" + str(tupleOfStartEnds[i][0]) + "'];out;")
        resultEnd = api.query("node['asset_ref'='" + str(tupleOfStartEnds[i][1]) + "'];out;")
        tupleOfStartEndQueriesNodes.append((resultStart.nodes[0], resultEnd.nodes[0]))

    # Retriving of all routes(edges) to plot route
    for i in range(len(tupleOfStartEndQueriesNodes)):
        route.extend(nx.shortest_path(G, (
            ox.get_nearest_edge(G, (tupleOfStartEndQueriesNodes[i][0].lat, tupleOfStartEndQueriesNodes[i][0].lon))[2]),
                                      (ox.get_nearest_edge(G, (tupleOfStartEndQueriesNodes[i][1].lat,
                                                               tupleOfStartEndQueriesNodes[i][1].lon)))[2]))

    route = removeDupes(route)

    # Get long and lat of all the individual busstops/nodes
    nodesLatLongs = []
    for i in range(len(paths)):
        tempNode = api.query("node['asset_ref'='" + str(paths[i]) + "'];out;").nodes[0]
        nodesLatLongs.append((tempNode.lat, tempNode.lon))

    # Plot the route on the map (does not include nodes)
    m = ox.plot_route_folium(G, route, route_color='#00008B', route_width=5)

    # For creating the Markers on the map with: BUS STOP DATA, BUS SERVICES TO TAKE AT THAT STOP, BUSSTOP NAME
    with open('../bus_data/all_bus_stops.json') as bus_stop:
        data = json.load(bus_stop)
        count = 0
        counter2 = 0
        tupleOfPairs = []
        tupleProcessed = []
        busServices = []

        for i in range(len(path) - 1):
            tupleOfPairs.append((path[i], path[i + 1]))

        df = pd.read_csv("../bus_data/Bus_Edge_Direction_1.csv", usecols=['BusStop A', 'BusStop B', 'Service(s)'])
        for x in df.values:
            if math.isnan(x[0]):
                pass
            else:
                for i in tupleOfPairs:
                    if i[0] == x[0] and i[1] == x[1]:
                        tupleProcessed.append((x[0], x[1], x[2]))
                        break

        # To get bus services
        for i in paths:
            busServices.append([])
            for z in tupleProcessed:
                if i in z:
                    busServices[counter2].extend(z[2].split(','))
            counter2 = counter2 + 1

        for i in range(len(busServices)):
            busServices[i] = removeDupes(busServices[i])

        # Create the node with the datas
        for i in nodesLatLongs:
            for z in data['value']:
                if int(z['BusStopCode']) == paths[count]:
                    folium.Marker(location=[i[0], i[1]], popup=folium.Popup(("<div>" + z[
                        'Description'] + "</div>" + "Buses: " + str(busServices[count]).strip("[]").replace("'", '')),
                                                                            max_width=450),
                                  icon=folium.Icon(color='red', icon='bus', prefix='fa')).add_to(m)
            count = count + 1

    m.save('../templates/dijkstra_bus.html')


# INSERT GUI VARIABLE THAT STORES START BUSSTOP CODE AND END BUSSTOP CODE HERE
# User input is to simulate that for now ^
startBusStopCode = input("Enter starting bus stop code:")
endBusStopCode = input("Enter destination bus  stop code:")
# Punggol Bus Interchange code is 65009

try:
    path = findShortestBusRoute.findShortestBusRoute(int(startBusStopCode), int(endBusStopCode))
    if len(path) == 0:
        pass
    else:
        findPath(path)
except:
    print("Bus Stop not found!\n")
