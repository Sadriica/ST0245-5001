import pandas as pd 
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely import wkt
#Creation of graphs
graph_risk={}
graph_distance={}
graph_balanced={}

#Read CSV and create Pandas Dataframe
data = pd.read_csv("calles_de_medellin_con_acoso.csv", sep=";")
dataframe = pd.DataFrame(data)

#Risk prom
prom_risk=dataframe['harassmentRisk'].mean()

#Fill Nan
dataframe=dataframe.fillna(prom_risk)

#Fill graph with length priority
for i in range(len(dataframe.harassmentRisk)):
    if not(dataframe.origin[i] in graph_distance):
        graph_distance[dataframe.origin[i]]={}
        graph_distance[dataframe.origin[i]][dataframe.destination[i]]= (dataframe.length[i])/10
    else:
        graph_distance[dataframe.origin[i]][dataframe.destination[i]]= (dataframe.length[i])/10

    if not(dataframe.destination[i] in graph_distance) and (dataframe.oneway[i] == True) :
        graph_distance[dataframe.destination[i]]={}
        graph_distance[dataframe.destination[i]][dataframe.origin[i]]= (dataframe.length[i])/10

#Fill graph with risk priority
for i in range(len(dataframe.harassmentRisk)):
    if not(dataframe.origin[i] in graph_risk):
        graph_risk[dataframe.origin[i]]={}
        graph_risk[dataframe.origin[i]][dataframe.destination[i]]= (dataframe.length[i]*0.25)+(dataframe.harassmentRisk[i])
    else:
        graph_risk[dataframe.origin[i]][dataframe.destination[i]]= (dataframe.length[i]*0.25)+(dataframe.harassmentRisk[i])

    if not(dataframe.destination[i] in graph_risk) and (dataframe.oneway[i] == True) :
        graph_risk[dataframe.destination[i]]={}
        graph_risk[dataframe.destination[i]][dataframe.origin[i]]= (dataframe.length[i]*0.25)+(dataframe.harassmentRisk[i])

#Fill graph with mixed priority
for i in range(len(dataframe.harassmentRisk)):
    if not(dataframe.origin[i] in graph_balanced):
        graph_balanced[dataframe.origin[i]]={}
        graph_balanced[dataframe.origin[i]][dataframe.destination[i]]= (dataframe.harassmentRisk[i])/(dataframe.length[i])
    else:
        graph_balanced[dataframe.origin[i]][dataframe.destination[i]]= (dataframe.harassmentRisk[i])/(dataframe.length[i])

    if not(dataframe.destination[i] in graph_balanced) and (dataframe.oneway[i] == True) :
        graph_balanced[dataframe.destination[i]]={}
        graph_balanced[dataframe.destination[i]][dataframe.origin[i]]= (dataframe.harassmentRisk[i])/(dataframe.length[i])

#Function Dijkstra
def dijkstra(graph, start, goal):
    shortest_distance={}
    track_predecesor={}
    unseen_nodes=graph
    infinity=10000
    trackpath=[]

    for node in unseen_nodes:
        shortest_distance[node]=infinity
    shortest_distance[start]=0

    while unseen_nodes:
        mindistancenode=None
        for node in unseen_nodes:
            if mindistancenode is None:
                mindistancenode=node
            elif shortest_distance[node]<shortest_distance[mindistancenode]:
                mindistancenode=node
        pathoptions=graph[mindistancenode].items()

        for childnode, weight in pathoptions:
            if weight + shortest_distance[mindistancenode]< shortest_distance[childnode]:
                shortest_distance[childnode]= weight+shortest_distance[mindistancenode]
                track_predecesor[childnode]=mindistancenode
        unseen_nodes.pop(mindistancenode)
    currentnode=goal 
    while currentnode != start:
        try:
            trackpath.insert(0, currentnode)
            currentnode= track_predecesor[currentnode]

        except KeyError:
            print("Path is not reachable ")
            vacio=start
            return start
    trackpath.insert(0,start)

    if shortest_distance[goal] != infinity:
        #print("Optimal path is "+ str(trackpath))
        return trackpath

    #This code has been taken from https://www.youtube.com/watch?v=Ub4-nG09PFw
    #Thanks and recognition to Amitabha Dey

#Dijkstra invoked for each graph

#Try to put some coordenates to test the code with each graph. 

print("Camino que prioriza el riesgo")
#dijkstra(graph_risk, input("Coordenadas de origen"), input("Coordenadas de destino"))
ruta1=dijkstra(graph_risk, dataframe.origin[0], dataframe.destination[0])

print("Camino que prioriza la distancia")
#dijkstra(graph_distance, input("Coordenadas de origen"), input("Coordenadas de destino"))
ruta2=dijkstra(graph_distance, dataframe.origin[0], dataframe.destination[0])

print("Camino que balancea ambas variables")
#dijkstra(graph_balanced, input("Coordenadas de origen"), input("Coordenadas de destino"))
ruta3=dijkstra(graph_balanced, dataframe.origin[0], dataframe.destination[0])


#Grafication. The next code has been taken from the github of MauricioToro
#and we take the idea of grafication and a little modifications from Stiven Ocampo
area = pd.read_csv('poligono_de_medellin.csv',sep=';')
area['geometry'] = area['geometry'].apply(wkt.loads)
area = gpd.GeoDataFrame(area)

#Load streets
edges1 = pd.read_csv('calles_de_medellin_con_acoso.csv',sep=';')
edges1['harassmentRisk'] = edges1['harassmentRisk'].fillna(edges1['harassmentRisk'].mean())
edges1.loc[edges1.harassmentRisk<50,'harassmentRisk']=0
for i in range(len(ruta1)-2):
    edges1.loc[(edges1['origin'] == ruta1[i]) & (edges1['destination'] == ruta1[i+1]),'harassmentRisk']=100

edges1 = edges1.loc[edges1['harassmentRisk']>0]


edges1['geometry'] = edges1['geometry'].apply(wkt.loads)
edges1 = gpd.GeoDataFrame(edges1)

edges2 = pd.read_csv('calles_de_medellin_con_acoso.csv',sep=';')
edges2['harassmentRisk'] = edges2['harassmentRisk'].fillna(edges2['harassmentRisk'].mean())
edges2.loc[edges2.harassmentRisk<50,'harassmentRisk']=0
for i in range(len(ruta2)-2):
    edges2.loc[(edges2['origin'] == ruta2[i]) & (edges2['destination'] == ruta2[i+1]),'harassmentRisk']=100

edges2 = edges2.loc[edges2['harassmentRisk']>0]


edges2['geometry'] = edges2['geometry'].apply(wkt.loads)
edges2 = gpd.GeoDataFrame(edges2)

edges3 = pd.read_csv('calles_de_medellin_con_acoso.csv',sep=';')
edges3['harassmentRisk'] = edges3['harassmentRisk'].fillna(edges3['harassmentRisk'].mean())
edges3.loc[edges3.harassmentRisk<50,'harassmentRisk']=0
for i in range(len(ruta3)-2):
    edges3.loc[(edges3['origin'] == ruta3[i]) & (edges3['destination'] == ruta3[i+1]),'harassmentRisk']=100

edges3 = edges3.loc[edges3['harassmentRisk']>0]

edges3['geometry'] = edges3['geometry'].apply(wkt.loads)
edges3 = gpd.GeoDataFrame(edges3)

#Create plot
fig, ax = plt.subplots(figsize=(12,8))

# Plot the footprint
area.plot(ax=ax, facecolor='black')

# Plot street edges
edges1.plot(ax=ax, linewidth=1, column='harassmentRisk', color='white')
edges2.plot(ax=ax, linewidth=1, column='harassmentRisk', color='red')
edges3.plot(ax=ax, linewidth=1, column='harassmentRisk', color='blue')

plt.title("Rutas Alternativas Para Moverse En Medellín")
plt.tight_layout()
plt.savefig("Resultado.png")