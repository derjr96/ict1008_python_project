import osmnx as ox
import networkx as nx
import overpy
import time

def removeDupes(list):
    tempArray = []
    for i in list:
        if i not in tempArray:
            tempArray.append(i)
    return tempArray


def findPath(paths):
    api = overpy.Overpass()
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
        time.sleep(5) #For server load overload prevention
        resultEnd = api.query("node['asset_ref'='" + str(tupleOfStartEnds[i][1]) + "'];out;")
        tupleOfStartEndQueriesNodes.append((resultStart.nodes[0], resultEnd.nodes[0]))

    # Retriving of all routes(edges) to plot route
    for i in range(len(tupleOfStartEndQueriesNodes)):
        route.extend(nx.shortest_path(G, (
            ox.get_nearest_edge(G, (tupleOfStartEndQueriesNodes[i][0].lat, tupleOfStartEndQueriesNodes[i][0].lon))[2]),
                                      (ox.get_nearest_edge(G, (tupleOfStartEndQueriesNodes[i][1].lat,
                                                               tupleOfStartEndQueriesNodes[i][1].lon)))[2]))

    route = removeDupes(route)

    return route, tupleOfStartEndQueriesNodes