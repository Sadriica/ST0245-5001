# Imports
from collections import deque
from shapely import wkt
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import heapq
import time

# Creation of graph
graph_balanced = {}

# Read CSV and create Pandas Dataframe
data = pd.read_csv("calles_de_medellin_con_acoso.csv", sep=";")
dataframe = pd.DataFrame(data)

# Risk prom
prom_risk = dataframe['harassmentRisk'].mean()

# Fill Nan
dataframe = dataframe.fillna(prom_risk)

# Fill graph
for i in range(len(dataframe.harassmentRisk)):
    if not (dataframe.origin[i] in graph_balanced):
        graph_balanced[dataframe.origin[i]] = {}
        graph_balanced[dataframe.origin[i]][dataframe.destination[i]] = ((
                                                                             dataframe.harassmentRisk[i]),
                                                                         (dataframe.length[i]))
    else:
        graph_balanced[dataframe.origin[i]][dataframe.destination[i]] = ((
                                                                             dataframe.harassmentRisk[i]),
                                                                         (dataframe.length[i]))

    if not (dataframe.destination[i]
            in graph_balanced) and (dataframe.oneway[i] == True):
        graph_balanced[dataframe.destination[i]] = {}
        graph_balanced[dataframe.destination[i]][dataframe.origin[i]] = ((
                                                                             dataframe.harassmentRisk[i]),
                                                                         (dataframe.length[i]))


# Dijkstra algorithm was designed with help of Santiago Neusa. Thanks from him!!!

# Function Dijkstra with length priority
def dijkstra_length(graph, start, goal):
    risk = 0
    distances = {vertex: float('infinity') for vertex in graph}
    previous = {vertex: None for vertex in graph}

    distances[start] = 0
    previous[start] = None

    cola = [(distances[start], start)]

    while cola:
        distance, actual = heapq.heappop(cola)
        if actual == goal:
            break
        for hijos in graph[actual]:
            distance = distances[actual] + ((graph[actual][hijos][1] / 10) +
                                            (graph[actual][hijos][0] * 0.25))
            if distance < distances[hijos]:
                risk += graph[actual][hijos][0]
                distances[hijos] = distance
                previous[hijos] = actual
                heapq.heappush(cola, (distance, hijos))

    return previous, risk / len(previous)


# Function Dijkstra with risk priority
def dijkstra_risk(graph, start, goal):
    risk = 0
    distances = {vertex: float('infinity') for vertex in graph}
    previous = {vertex: None for vertex in graph}

    distances[start] = 0
    previous[start] = None

    cola = [(distances[start], start)]

    while cola:
        distance, actual = heapq.heappop(cola)
        if actual == goal:
            break
        for hijos in graph[actual]:
            distance = distances[actual] + (((graph[actual][hijos][1] / 10) * 0.25) +
                                            (graph[actual][hijos][0] * 2))
            if distance < distances[hijos]:
                risk += graph[actual][hijos][0]
                distances[hijos] = distance
                previous[hijos] = actual
                heapq.heappush(cola, (distance, hijos))

    return previous, risk / len(previous)


# Function Dijkstra with mixed priority
def dijkstra_mixed(graph, start, goal):
    risk = 0
    distances = {vertex: float('infinity') for vertex in graph}
    previous = {vertex: None for vertex in graph}

    distances[start] = 0
    previous[start] = None

    cola = [(distances[start], start)]

    while cola:
        distance, actual = heapq.heappop(cola)
        if actual == goal:
            break
        for hijos in graph[actual]:
            distance = distances[actual] + ((graph[actual][hijos][1]) /
                                            (graph[actual][hijos][0]))
            if distance < distances[hijos]:
                risk += graph[actual][hijos][0]
                distances[hijos] = distance
                previous[hijos] = actual
                heapq.heappush(cola, (distance, hijos))

    return previous, risk / len(previous)


# Function to track the path
def camino(previo, actual, ruta):
    if previo[actual] is None:
        ruta.append(actual)
        return ruta
    else:
        ruta.append(actual)
        return camino(previo, previo[actual], ruta)


# Dijkstra invoked for each graph

# Try to put some coordenates to test the code with each graph.

# Path with risk priority

print("Tiempo de camino que prioriza el riesgo")
inicio1 = time.time()
ruta1aux = dijkstra_risk(graph_balanced, "(-75.5778046, 6.2029412)",
                         "(-75.5762232, 6.266327)")
ruta1deque = deque()
ruta1c = camino(ruta1aux[0], "(-75.5762232, 6.266327)", ruta1deque)
final1 = time.time()
print(final1 - inicio1)
ruta1 = []
large1 = 0
while ruta1c:
    nodo = ruta1c.pop()
    ruta1.append(nodo)
    if ruta1c:
        siguiente1 = ruta1c.pop()
        large1 += graph_balanced[nodo][siguiente1][1]
        ruta1c.append(siguiente1)
print("El promedio de riesgo es:", ruta1aux[1])
print("El total recorrido es:", str(large1 / 1000) + "km")
print(" ")

# Path with length priority
print("Tiempo de camino que prioriza la distancia")
inicio2 = time.time()
ruta2aux = dijkstra_length(graph_balanced, "(-75.5778046, 6.2029412)",
                           "(-75.5762232, 6.266327)")
ruta2deque = deque()
ruta2c = camino(ruta2aux[0], "(-75.5762232, 6.266327)", ruta2deque)
final2 = time.time()
print(final2 - inicio2)
ruta2 = []
large2 = 0
while ruta2c:
    nodo2 = ruta2c.pop()
    ruta2.append(nodo2)
    if ruta2c:
        siguiente2 = ruta2c.pop()
        large2 += graph_balanced[nodo2][siguiente2][1]
        ruta2c.append(siguiente2)
print("El promedio de riesgo es:", ruta2aux[1])
print("El total recorrido es:", str(large2 / 1000) + "km")
print(" ")

# Path with mix priority
print("Tiempo de camino que balancea ambas variables")
inicio3 = time.time()
ruta3aux = dijkstra_mixed(graph_balanced, "(-75.5778046, 6.2029412)",
                          "(-75.5762232, 6.266327)")
ruta3deque = deque()
ruta3c = camino(ruta3aux[0], "(-75.5762232, 6.266327)", ruta3deque)
final3 = time.time()
print(final3 - inicio3)
ruta3 = []
large3 = 0
while ruta3c:
    nodo3 = ruta3c.pop()
    ruta3.append(nodo3)
    if ruta3c:
        siguiente3 = ruta3c.pop()
        large3 += graph_balanced[nodo3][siguiente3][1]
        ruta3c.append(siguiente3)
print("El promedio de riesgo es:", ruta3aux[1])
print("El total recorrido es:", str(large3 / 1000) + "km")
print(" ")
print(" ")
print(" ")
print(" ")
print(" ")
print("False warning from libraries. Ignore this!!!")

# Grafication. The next code has been taken from the github of MauricioToro
# and we take the idea of grafication and a little modifications from Stiven Ocampo

area = pd.read_csv('poligono_de_medellin.csv', sep=';')
area['geometry'] = area['geometry'].apply(wkt.loads)
area = gpd.GeoDataFrame(area)

# Load streets
edges1 = pd.read_csv('calles_de_medellin_con_acoso.csv', sep=';')
edges1['harassmentRisk'] = edges1['harassmentRisk'].fillna(
    edges1['harassmentRisk'].mean())
edges1.loc[edges1.harassmentRisk < 50, 'harassmentRisk'] = 0
for i in range(len(ruta1) - 2):
    edges1.loc[(edges1['origin'] == ruta1[i]) &
               (edges1['destination'] == ruta1[i + 1]), 'harassmentRisk'] = 100

edges1 = edges1.loc[edges1['harassmentRisk'] > 0]

edges1['geometry'] = edges1['geometry'].apply(wkt.loads)
edges1 = gpd.GeoDataFrame(edges1)

edges2 = pd.read_csv('calles_de_medellin_con_acoso.csv', sep=';')
edges2['harassmentRisk'] = edges2['harassmentRisk'].fillna(
    edges2['harassmentRisk'].mean())
edges2.loc[edges2.harassmentRisk < 50, 'harassmentRisk'] = 0
for i in range(len(ruta2) - 2):
    edges2.loc[(edges2['origin'] == ruta2[i]) &
               (edges2['destination'] == ruta2[i + 1]), 'harassmentRisk'] = 100

edges2 = edges2.loc[edges2['harassmentRisk'] > 0]

edges2['geometry'] = edges2['geometry'].apply(wkt.loads)
edges2 = gpd.GeoDataFrame(edges2)

edges3 = pd.read_csv('calles_de_medellin_con_acoso.csv', sep=';')
edges3['harassmentRisk'] = edges3['harassmentRisk'].fillna(
    edges3['harassmentRisk'].mean())
edges3.loc[edges3.harassmentRisk < 50, 'harassmentRisk'] = 0
for i in range(len(ruta3) - 2):
    edges3.loc[(edges3['origin'] == ruta3[i]) &
               (edges3['destination'] == ruta3[i + 1]), 'harassmentRisk'] = 100

edges3 = edges3.loc[edges3['harassmentRisk'] > 0]

edges3['geometry'] = edges3['geometry'].apply(wkt.loads)
edges3 = gpd.GeoDataFrame(edges3)

# Create plot
fig, ax = plt.subplots(figsize=(12, 8))

# Plot the footprint
area.plot(ax=ax, facecolor='black')

# Plot street edges
edges1.plot(ax=ax, linewidth=1, column='harassmentRisk', color='green')
edges2.plot(ax=ax, linewidth=1, column='harassmentRisk', color='orange')
edges3.plot(ax=ax, linewidth=1, column='harassmentRisk', color='purple')

plt.title("Rutas Alternativas Para Moverse En Medellín")
plt.tight_layout()
plt.savefig("Resultado.png")
