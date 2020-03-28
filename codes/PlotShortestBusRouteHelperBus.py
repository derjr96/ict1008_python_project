import json
import math
import numpy as np
import osmnx as ox
import networkx as nx
import overpy
import time
import pandas as pd


def removeDupes(list):
    tempArray = []
    for i in list:
        if i not in tempArray:
            tempArray.append(i)
    return tempArray


def findPath(G, paths):
    startTime = time.time()

    listOfNodes = []  # Stored as [ (lat, lon, BusStopCode) ] format
    listOfTuplesStartEndLatLon = []  # Stored as [ ((Start1 lat, Start1 lon) , (End2 lat, End2 lon)) ] format
    route = []  # Routes to travel from [Route Start1 to End 2]format

    with open('bus_data/Punggol_Bus_Stops.json') as bus_stop:
        data = json.load(bus_stop)

        for i in paths:
            for x in data['punggolBusStops']:
                if i == int(x['BusStopCode']):
                    tempTuple = (x['Latitude'], x['Longitude'], x['BusStopCode'])
                    listOfNodes.append(tempTuple)
                    break

    # Retriving the long and lat of the nodes
    for i in range(len(listOfNodes)):
        if i != (len(listOfNodes) - 1):
            listOfTuplesStartEndLatLon.append(((float(listOfNodes[i][0]), float(listOfNodes[i][1])),
                                               (float(listOfNodes[i + 1][0]), float(listOfNodes[i + 1][1]))))

    # Retriving of all routes(edges) to plot route
    for i in range(len(listOfTuplesStartEndLatLon)):
        route.extend(nx.shortest_path(G, (
            ox.get_nearest_edge(G, (listOfTuplesStartEndLatLon[i][0][0], listOfTuplesStartEndLatLon[i][0][1])))[2], (
                                          ox.get_nearest_edge(G, (
                                              listOfTuplesStartEndLatLon[i][1][0],
                                              listOfTuplesStartEndLatLon[i][1][1])))[
                                          2]))

    route = removeDupes(route)

    endTime = time.time()

    print("Bus Route Retrieval Takes: ", round((endTime - startTime), 2))

    return route
