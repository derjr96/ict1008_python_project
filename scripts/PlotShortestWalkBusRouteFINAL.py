import json
import math
import pandas as pd
import folium
import osmnx as ox
import overpy
import time
import scripts.findShortestBusRouteFINAL as findShortestBusRoute
import scripts.PlotShortestBusRouteHelperBusFINAL as plotShortestBusRoute
import scripts.PlotShortestWalkBusRouteHelperWalkFINAL as plotShortestWalkRoute


def convertRoute(coords):
    output = []
    for x in range(len(coords)):  # Parent Array
        for i in range(len(coords[x])):  # Inner Array
            output.append([coords[x][i][1], coords[x][i][0]])
    return output


def plotShortestWalkBus(startLocation, endLocation):
    startTime = time.time()

    startLocation = ox.geocode(startLocation)
    endLocation = ox.geocode(endLocation)

    startLocation = (str(startLocation[0]), str(startLocation[1]))
    endLocation = (str(endLocation[0]), str(endLocation[1]))

    api = overpy.Overpass()
    punggol = (1.4041070, 103.9025242)
    distance = 3000
    W = ox.graph_from_point(punggol, distance=distance, network_type='walk')
    D = ox.graph_from_point(punggol, distance=distance, network_type='drive_service')

    startBusStopNode = None
    endBusStopNode = None
    radius = 100

    # Find busstop to walk to, retrieve its busstopCode, latlon

    while (startBusStopNode == None):
        startBusStopNode = api.query(
            "node(around:" + str(radius) + "," + startLocation[0] + "," + startLocation[
                1] + ")[highway=bus_stop];out;")

        if len(startBusStopNode.nodes) > 0:
            startBusStopNode = startBusStopNode.nodes[0]
            startBusStopLatLon = (startBusStopNode.lat, startBusStopNode.lon)
            startBusStopCode = startBusStopNode.tags['asset_ref']
        else:
            startBusStopNode = None
            radius += 50

    # Find path of INITIAL WALK to BUS STOP
    try:
        initialWalkToBusStop = plotShortestWalkRoute.plotWalk(startLocation, startBusStopLatLon)
    except:
        print("Cannot find walk route.")

    # Find destination busstop, retrieve its busStopCode, latlon
    while (endBusStopNode == None):
        endBusStopNode = api.query(
            "node(around:" + str(radius) + "," + endLocation[0] + "," + endLocation[
                1] + ")[highway=bus_stop];out;")

        if len(endBusStopNode.nodes) > 0:
            endBusStopNode = endBusStopNode.nodes[0]
            endBusStopLatLon = (endBusStopNode.lat, endBusStopNode.lon)
            endBusStopCode = endBusStopNode.tags['asset_ref']
        else:
            endBusStopNode = None
            radius += 50

    # Find path of FINAL WALK from BUS STOP to DESTINATION
    try:
        finalWalkFromBusStopToDestination = plotShortestWalkRoute.plotWalk(endBusStopLatLon, endLocation)
    except:
        print("Cannot find walk route.")

    # Find path of BUS ROUTE
    try:
        paths = findShortestBusRoute.findShortestBusRoute(int(startBusStopCode), int(endBusStopCode))
        busRouteToPlot = plotShortestBusRoute.findPath(paths)
        forPlotNode = busRouteToPlot[1]
        busRouteToPlot = busRouteToPlot[0]
    except:
        print("Cannot find bus route. Missing Map Data")

    # Convert Path(List of Nodes) to Path(List of coords) to draw PolyLines
    try:
        initialWalkToBusStop = convertRoute(ox.plot.node_list_to_coordinate_lines(W, initialWalkToBusStop))
        busRouteToPlot = convertRoute(ox.plot.node_list_to_coordinate_lines(D, busRouteToPlot))
        finalWalkFromBusStopToDestination = convertRoute(
            ox.plot.node_list_to_coordinate_lines(W, finalWalkFromBusStopToDestination))
    except:
        print("Unable to find route. Missing Map Data")

    plotTime = time.time()
    # Plot Final Graph
    m = folium.Map(location=punggol, distance=distance, zoom_start=15)
    if len(initialWalkToBusStop) > 0:
        folium.PolyLine(initialWalkToBusStop, color="green", weight=4, opacity=1).add_to(m)

    folium.PolyLine(busRouteToPlot, color="blue", weight=4, opacity=1).add_to(m)

    if len(finalWalkFromBusStopToDestination) > 0:
        folium.PolyLine(finalWalkFromBusStopToDestination, color="green", weight=4, opacity=1).add_to(m)

    # For creating the Markers on the map with: BUS STOP DATA, BUS SERVICES TO TAKE AT THAT STOP, BUSSTOP NAME
    with open('../bus_data/all_bus_stops.json') as bus_stop:
        data = json.load(bus_stop)
        count = 0
        counter2 = 0
        tupleOfPairs = []
        tupleProcessed = []
        busServices = []

        for i in range(len(paths) - 1):
            tupleOfPairs.append((paths[i], paths[i + 1]))

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
            busServices[i] = plotShortestBusRoute.removeDupes(busServices[i])

        # Get long and lat of all the individual busstops/nodes
        nodesLatLongs = []
        for i in range(len(forPlotNode)):
            nodesLatLongs.append((forPlotNode[i][0][0], forPlotNode[i][0][1]))
        nodesLatLongs.append((forPlotNode[-1][1][0], forPlotNode[-1][1][1]))

        # Create the node with the datas
        for i in nodesLatLongs:
            for z in data['value']:
                if int(z['BusStopCode']) == paths[count]:
                    folium.Marker(location=[i[0], i[1]], popup=folium.Popup
                    (("<div>" + z['Description'] + "</div>" + "Buses: " + str(busServices[count]).strip(
                        "[]").replace("'", '')), max_width=450),
                                  icon=folium.Icon(color='red', icon='bus', prefix='fa')).add_to(m)
            count = count + 1

        # Add Start and End Destination Markers
        folium.Marker(location=startLocation, icon=folium.Icon(color='green', icon='play', prefix='fa')).add_to(m)
        folium.Marker(location=endLocation, icon=folium.Icon(color='green', icon='stop', prefix='fa')).add_to(m)

    # Save as html file
    m.save('../templates/dijkstra_walk_bus.html')

    endTime = time.time()
    print("Plotting of Map takes: ", round(endTime - plotTime, 2))
    print("Time taken: ", round(endTime - startTime, 2))


# Test Cases (NOT ALL BUS STOPS ARE ON OSM OR ARE ACCURATE. MANUAL ADDITION OF MAP DATA ONLINE:
# 1. Punggol Green Primary - Punggol Bus Interchange ('1.4021', '103.89872') - ('1.40394', '103.90263') Checked
# 2. Punggol Point Park - Punggol Bus Interchange ('1.4208568','103.9103653') - ('1.40394', '103.90263') Checked
# 3. EdgeField Secondary - Oasis Terrace ('1.4005349','103.9016396') - ('1.40283','103.91279') Checked Best Result
# 4. Punggol BUs Interchange - Oasis Terrace ('1.4021', '103.89872') - ('1.40283','103.91279') Checked

# try:
plotShortestWalkBus('Punggol', 'Block 612, Punggol Drive, Punggol')
# except:
#     print("Please try again. Server load too high or too many request!\n")
# else:
#     print("Unable to find route!")
