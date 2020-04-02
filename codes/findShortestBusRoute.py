import collections
import math
from collections import deque, namedtuple
import time
import numpy as np
import pandas as pd


def findShortestBusRoute(startBusStopCode, endBusStopCode):
    # we'll use infinity as a default distance to nodes.

    startTime = time.time()

    inf = float('inf')
    Edge = namedtuple('Edge', 'start, end, cost')

    def make_edge(start, end, cost=1):
        return Edge(start, end, cost)

    class Graph:
        def __init__(self, edges):
            # let's check that the data is right
            wrong_edges = [i for i in edges if len(i) not in [2, 3]]
            if wrong_edges:
                raise ValueError('Wrong edges data: {}'.format(wrong_edges))

            self.edges = [make_edge(*edge) for edge in edges]

        @property
        def vertices(self):
            return set(
                sum(
                    ([edge.start, edge.end] for edge in self.edges), []
                )
            )

        def get_node_pairs(self, n1, n2, both_ends=True):
            if both_ends:
                node_pairs = [[n1, n2], [n2, n1]]
            else:
                node_pairs = [[n1, n2]]
            return node_pairs

        def remove_edge(self, n1, n2, both_ends=True):
            node_pairs = self.get_node_pairs(n1, n2, both_ends)
            edges = self.edges[:]
            for edge in edges:
                if [edge.start, edge.end] in node_pairs:
                    self.edges.remove(edge)

        def add_edge(self, n1, n2, cost=1, both_ends=True):
            node_pairs = self.get_node_pairs(n1, n2, both_ends)
            for edge in self.edges:
                if [edge.start, edge.end] in node_pairs:
                    return ValueError('Edge {} {} already exists'.format(n1, n2))

            self.edges.append(Edge(start=n1, end=n2, cost=cost))
            if both_ends:
                self.edges.append(Edge(start=n2, end=n1, cost=cost))

        @property
        def neighbours(self):
            neighbours = {vertex: set() for vertex in self.vertices}
            for edge in self.edges:
                neighbours[edge.start].add((edge.end, edge.cost))

            return neighbours

        def dijkstra(self, source, dest):
            assert source in self.vertices, 'Such source node doesn\'t exist'
            distances = {vertex: inf for vertex in self.vertices}
            previous_vertices = {
                vertex: None for vertex in self.vertices
            }
            distances[source] = 0
            vertices = self.vertices.copy()

            while vertices:
                current_vertex = min(
                    vertices, key=lambda vertex: distances[vertex])
                vertices.remove(current_vertex)
                if distances[current_vertex] == inf:
                    break
                for neighbour, cost in self.neighbours[current_vertex]:
                    alternative_route = distances[current_vertex] + cost
                    if alternative_route < distances[neighbour]:
                        distances[neighbour] = alternative_route
                        previous_vertices[neighbour] = current_vertex

            path, current_vertex = deque(), dest
            while previous_vertices[current_vertex] is not None:
                path.appendleft(current_vertex)
                current_vertex = previous_vertices[current_vertex]
            if path:
                path.appendleft(current_vertex)
            return list(collections.deque(path))

    try:

        # To create edges on dijkstra graph, the tuple consists of ( SRC, DEST, Dist)
        tupleProcessed = []
        df = pd.read_csv("data/Bus_Edge_Direction_1.csv", usecols=['BusStop A', 'BusStop B', 'Distance'])

        # Complexity O(n) for number of rows in the csv
        for x in df.values:
            if math.isnan(x[0]):
                pass
            else:
                tempArray = [x[0].astype(np.int), x[1].astype(np.int), x[2]]
                tupleProcessed.append(tuple(tempArray))

        graph = Graph(tupleProcessed)

        print("Time for Dijkstra Bus Takes: ", round(time.time() - startTime, 2))

        result = graph.dijkstra(startBusStopCode, endBusStopCode)

        if len(result) == 0:
            print("Path not found!")
        else:
            # Return list of bus stop codes
            return result

    except:
        print("Path not found!")

