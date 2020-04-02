import json
import math
import pandas as pd
import folium
import osmnx as ox
import overpy
import time
import codes.findShortestBusRoute as findShortestBusRoute
import codes.PlotShortestBusRouteHelperBus as plotShortestBusRoute
import codes.PlotShortestWalkBusRouteHelperWalk as plotShortestWalkRoute


def convertRoute(coords):
    output = []
    for x in range(len(coords)):  # Parent Array
        for i in range(len(coords[x])):  # Inner Array
            output.append([coords[x][i][1], coords[x][i][0]])
    return output


    # Takes in Walk and Drive Digraph with start location and endlocation (Address)
def plotShortestWalkBus(W, D, startLocation, endLocation):
    startTime = time.time()

    # Converts address to coords
    startLocation = ox.geocode(startLocation)
    endLocation = ox.geocode(endLocation)

    #Convert coords to tuple of string lat and lon
    startLocation = (str(startLocation[0]), str(startLocation[1]))
    endLocation = (str(endLocation[0]), str(endLocation[1]))

    api = overpy.Overpass()

    punggol = (1.403948, 103.909048)
    distance = 2000

    startBusStopNode = None
    endBusStopNode = None
    radius = 100

    # Find busstop to walk to (starts from range 50m, increases till find a busstop) , retrieve its busstopCode, latlon
    # Uses overpass api
    # Complexity of O(n) Run n times until startBusStopNode is not none
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
    # Complexity of should be O(n)
    try:
        initialWalkToBusStop = plotShortestWalkRoute.plotWalk(W, startLocation, startBusStopLatLon)
    except:
        print("Cannot find walk route.")


    radius = 100

    # Find Dest busstop from final dest (starts from range 50m, increases till find a busstop) , retrieve its busstopCode, latlon
    # Uses overpass api
    # Complexity of O(n) Run n times until endBusStopNode is not none
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
            radius += 100

    # Find path of FINAL WALK from Dest BUS STOP to DESTINATION
    # Complexity of should be O(n)
    try:
        finalWalkFromBusStopToDestination = plotShortestWalkRoute.plotWalk(W, endBusStopLatLon, endLocation)
    except:
        print("Cannot find walk route.")

    # Find path of BUS ROUTE
    # Complexity of O(n^2)
    try:
        paths = findShortestBusRoute.findShortestBusRoute(int(startBusStopCode), int(endBusStopCode))
        busRouteToPlot = plotShortestBusRoute.findPath(D, paths)
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

    # Don't plot if no path
    if len(initialWalkToBusStop) > 0:
        folium.PolyLine(initialWalkToBusStop, color="blue", weight=4, opacity=1).add_to(m)

    folium.PolyLine(busRouteToPlot, color="purple", weight=4, opacity=1).add_to(m)

    # Don't plot if no path
    if len(finalWalkFromBusStopToDestination) > 0:
        folium.PolyLine(finalWalkFromBusStopToDestination, color="blue", weight=4, opacity=1).add_to(m)

    # For creating the Markers on the map with: BUS STOP DATA, BUS SERVICES TO TAKE AT THAT STOP, BUSSTOP NAME
    with open('data/all_bus_stops.json') as bus_stop:
        data = json.load(bus_stop)
        count = 0
        counter2 = 0
        tupleOfPairs = []
        tupleProcessed = []
        busServices = []

        # Complexity of O(n) n number of paths-1
        for i in range(len(paths) - 1):
            tupleOfPairs.append((paths[i], paths[i + 1]))

        df = pd.read_csv("data/Bus_Edge_Direction_1.csv", usecols=['BusStop A', 'BusStop B', 'Service(s)'])
        # Complexity of O(n) number of values in direction csv file
        for x in df.values:
            if math.isnan(x[0]):
                pass
            else:
                for i in tupleOfPairs:
                    if i[0] == x[0] and i[1] == x[1]:
                        tupleProcessed.append((x[0], x[1], x[2]))
                        break

        # To get bus services
        # Complexity of O(n^2) n number of paths, n number of values in tupleProcessed
        for i in paths:
            busServices.append([])
            for z in tupleProcessed:
                if i in z:
                    busServices[counter2].extend(z[2].split(','))
            counter2 = counter2 + 1

        # Complexity of O(n) n number of bus services
        for i in range(len(busServices)):
            busServices[i] = plotShortestBusRoute.removeDupes(busServices[i])

        # Create the marker nodes with the bus services to visualize on map
        # Complexity of O(n) number of paths
        for i in paths:
            for z in data['value']:
                if int(z['BusStopCode']) == paths[count]:
                    folium.Marker(location=[z['Latitude'], z['Longitude']], popup=folium.Popup
                    (("<div>" + z['Description'] + "</div>" + "Buses: " + str(busServices[count]).strip(
                        "[]").replace("'", '')), max_width=450),
                                  icon=folium.Icon(color='green', icon='bus', prefix='fa')).add_to(m)
            count = count + 1

        # Add Start and End Destination Markers
        folium.Marker(location=startLocation, icon=folium.Icon(color='red', icon='record')).add_to(m)
        folium.Marker(location=endLocation, icon=folium.Icon(color='red', icon='record')).add_to(m)

        # Save as html file
        m.save('templates/default.html')

        endTime = time.time()
        totalTime = ["Total calculation time: {first} seconds.".format(first=round(endTime - startTime, 2)), "Plotting of Map takes: {second}.".format(second=round(endTime - plotTime, 2)), "Time taken: {third}".format(third=round(endTime - startTime, 2))]
        totalTime.append("Click each node for bus information")
        return totalTime
