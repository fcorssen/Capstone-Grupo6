import pandas as pd
import osmnx as ox
import networkx as nx
import random
from geopy.distance import great_circle


random.seed(12345)

df_delivey = pd.read_excel("datos/deliveries_data.xlsx", index_col=0)
df_driver = pd.read_excel("datos/driver_origins_data.xlsx")
df_center = pd.read_excel("datos/centers_data.xlsx")
df_eccomerce = pd.read_excel("datos/e-commerce_data.xlsx")

coordinate_eccomerce = []
coordinate_center = []
coordinate_driver = []
coordinate_delivery = []


# ------------- Separar por dias --------------
days = []
amountDays = []

for i in range(df_delivey['delivery_day'].size):
    days.append(df_delivey['delivery_day'].iat[i].day)

for i in range(30):
    value = days.count(i + 1)
    amountDays.append(value)

# ------------ Cargar Datos a listas--------------

for i in range(df_driver['latitude'].size):
    coordinate_driver.append([df_driver['latitude'].iat[i], df_driver['longitude'].iat[i]])

for i in range(df_eccomerce['latitude'].size):
    coordinate_eccomerce.append([df_eccomerce['latitude'].iat[i], df_eccomerce['longitude'].iat[i]])

# --------- Generar data frame para dia 1 ----------
df_deliver_day = df_delivey[:amountDays[0]]

# obtener coordenadas de centro de distribucion con id=4
for i in range(df_center['latitude'].size):
    if df_center['id'].iat[i] == 4:
        coordinate_center = [df_center['latitude'].iat[i], df_center['longitude'].iat[i]]   


# encontrar e-commerce mas lejano en linea recta del centro de distribucion con id=4 

max_distance = 0
for i in range(df_eccomerce['latitude'].size):
    distance = great_circle((coordinate_center[0], coordinate_center[1]), (df_eccomerce['latitude'].iat[i], df_eccomerce['longitude'].iat[i])).km
    if distance > max_distance:
        max_distance = distance
        max_ecommerce = [df_eccomerce['latitude'].iat[i], df_eccomerce['longitude'].iat[i]]
        # print(max_ecommerce)

# cargar mapa
G = ox.graph_from_point((coordinate_center[0], coordinate_center[1]), dist= 10000, dist_type='bbox', network_type='drive')

G = ox.add_edge_speeds(G)
G = ox.add_edge_travel_times(G)

# generar ruta desde centro de distribucion con id=4 hasta e-commerce mas lejano en linea recta
orig_node = ox.distance.nearest_nodes(G, coordinate_center[1], coordinate_center[0])
destination_node = ox.distance.nearest_nodes(G, max_ecommerce[1], max_ecommerce[0])

route = nx.shortest_path(G, orig_node, destination_node, weight='travel_time')

# plot mapa con grafo y ruta
ox.plot_graph_route(G, route, route_linewidth=6, node_size=0, bgcolor='k')



# generar cluster de 10 ecommerce cercanos en linea recta al max_ecommerce encontrado anteriormente

cluster = []
