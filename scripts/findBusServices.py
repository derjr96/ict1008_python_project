import math
import pandas as pd
import numpy as np


# [65009, 65359, 65489, 65469, 65619, 65629, 65639, 65689, 65139]

def findBusServices(path):
    tupleOfPairs = []

    for i in range(len(path) - 1):
        tupleOfPairs.append((path[i], path[i + 1]))

    tupleProcessed = []
    df = pd.read_csv("../bus_data/Bus_Edge_Direction_1.csv", usecols=['BusStop A', 'BusStop B', 'Service(s)'])
    for x in df.values:
        if math.isnan(x[0]):
            pass
        else:
            for i in tupleOfPairs:
                if i[0] == x[0] and i[1] == x[1]:
                    tupleProcessed.append((x[0], x[1], tuple(x[2].split(","))))
                    break
    #print(tupleProcessed)

    for i in range(len(tupleProcessed)):
        for z in range(len(tupleProcessed[i][2])):
            for x in range(len(tupleProcessed)):
                if tupleProcessed[i][2][z] in tupleProcessed[x][2]:
                    print(tupleProcessed[x])

findBusServices([65009, 65359, 65489, 65469, 65619, 65629, 65639, 65689, 65139])
