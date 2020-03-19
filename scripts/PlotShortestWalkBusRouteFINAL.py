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
    api = overpy.Overpass()
    punggol = (1.4041070, 103.9025242)
    distance = 3000
    W = ox.graph_from_point(punggol, distance=distance, truncate_by_edge=True, network_type='walk')
    D = ox.graph_from_point(punggol, distance=distance, truncate_by_edge=True, network_type='drive_service')

    # Find busstop to walk to, retrieve its busstopCode, latlon
    startBusStopNode = api.query(
        "node(around:100," + startLocation[0] + "," + startLocation[1] + ")[highway=bus_stop];out;").nodes[0]
    startBusStopLatLon = (startBusStopNode.lat, startBusStopNode.lon)
    startBusStopCode = startBusStopNode.tags['asset_ref']

    # Find path of INITIAL WALK to BUS STOP
    initialWalkToBusStop = plotShortestWalkRoute.plotWalk(startLocation, startBusStopLatLon)


    # Find destination busstop, retrieve its busStopCode, latlon
    time.sleep(60) #Try to prevent too many request
    print("Sleeping 60 seconds")

    endBusStopNode = api.query(
        "node(around:100," + endLocation[0] + "," + endLocation[1] + ")[highway=bus_stop];out;").nodes[0]
    endBusStopLatLon = (endBusStopNode.lat, endBusStopNode.lon)
    endBusStopCode = endBusStopNode.tags['asset_ref']


    # Find path of FINAL WALK from BUS STOP to DESTINATION
    finalWalkFromBusStopToDestination = plotShortestWalkRoute.plotWalk(endBusStopLatLon, endLocation)


    # Find path of BUS ROUTE
    paths = findShortestBusRoute.findShortestBusRoute(int(startBusStopCode), int(endBusStopCode))
    busRouteToPlot = plotShortestBusRoute.findPath(paths)


    # Convert Path(List of Nodes) to Path(List of coords) to draw PolyLines
    initialWalkToBusStop = convertRoute(ox.plot.node_list_to_coordinate_lines(W, initialWalkToBusStop))
    busRouteToPlot = convertRoute(ox.plot.node_list_to_coordinate_lines(D, busRouteToPlot))
    finalWalkFromBusStopToDestination = convertRoute(
        ox.plot.node_list_to_coordinate_lines(W, finalWalkFromBusStopToDestination))


    # Plot Final Graph
    m = folium.Map(location=punggol, distance=distance, zoom_start=15)
    if len(initialWalkToBusStop) > 0:
        folium.PolyLine(initialWalkToBusStop, color="green", weight=4, opacity=1).add_to(m)

    folium.PolyLine(busRouteToPlot, color="blue", weight=4, opacity=1).add_to(m)

    if len(finalWalkFromBusStopToDestination) > 0:
        folium.PolyLine(finalWalkFromBusStopToDestination, color="green", weight=4, opacity=1).add_to(m)

    time.sleep(60)  # Try to prevent too many request
    print("Sleeping 60 seconds")

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
        for i in range(len(paths)):
            tempNode = api.query("node['asset_ref'='" + str(paths[i]) + "'];out;").nodes[0]
            nodesLatLongs.append((tempNode.lat, tempNode.lon))

        # Create the node with the datas
        for i in nodesLatLongs:
            for z in data['value']:
                if int(z['BusStopCode']) == paths[count]:
                    folium.Marker(location=[i[0], i[1]], popup=folium.Popup(("<div>" + z[
                        'Description'] + "</div>" + "Buses: " + str(busServices[count]).strip("[]").replace("'", '')),
                                                                            max_width=450),
                                  icon=folium.Icon(color='red', icon='bus', prefix='fa')).add_to(m)
            count = count + 1

        # Add Start and End Destination Markers
        folium.Marker(location=startLocation, icon=folium.Icon(color='green', icon='play', prefix='fa')).add_to(m)
        folium.Marker(location=endLocation, icon=folium.Icon(color='green', icon='stop', prefix='fa')).add_to(m)

    # Save as html file
    m.save('../templates/dijkstra_walk_bus.html')


# startLocation = tuple(input("Enter starting coords:").split(','))  # PunggolGreenPrimarySch 1.4021,103.89872
# endLocation = tuple(input("Enter ending coords:").split(','))  # PunggolBusInterchange 1.40394,103.90263

startLocation = ('1.40394', '103.90263')
endLocation = ('1.42066', '103.91126')

# try:
plotShortestWalkBus(startLocation, endLocation)
# except overpy.exception:
#     print("Please try again. Server load too high or too many request!\n")
# else:
#     print("Unable to find route!")
