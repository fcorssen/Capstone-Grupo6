import pandas as pd
import osmnx as ox
import networkx as nx
import random

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

# ---------- Driver al azar -----------------
driver = random.choice(coordinate_driver)

# --------- Generar data frame para dia 1 ----------
df_deliver_day = df_delivey[:amountDays[0]]

# ------- Cargar mapa -----------------
G = ox.graph_from_point((driver[0], driver[1]), dist= 10000, dist_type='bbox', network_type='drive')

G = ox.add_edge_speeds(G)
G = ox.add_edge_travel_times(G)

# # ---------- Generar ruta ------------
driver_route = []
# ecommerce = random.choice(coordinate_eccomerce)
ecommerce = random.sample(coordinate_eccomerce, 20)

orig_node = ox.distance.nearest_nodes(G, driver[1], driver[0])
destination_node = ox.distance.nearest_nodes(G, ecommerce[0][1], ecommerce[0][0])
route_distance = nx.shortest_path(G, orig_node, destination_node, weight='distance')
closest = 0

for i in range(len(ecommerce)):
    destination_node1 = ox.distance.nearest_nodes(G, ecommerce[i][1], ecommerce[i][0])
    if route_distance > nx.shortest_path(G, orig_node, destination_node1, weight='distance'):
        destination_node = destination_node1
        route_distance = nx.shortest_path(G, orig_node, destination_node, weight='distance')
        closest = i
ecommerce_ini = ecommerce[closest]
ecommerce.pop(closest)


driver_route.append(route_distance)

j = 0
while (len(driver_route) < 17):
    
    if j == 0:
        destination_node1 = ox.distance.nearest_nodes(G, ecommerce_ini[1], ecommerce_ini[0])
    else:
        destination_node1 = ox.distance.nearest_nodes(G, ecommerce1[1], ecommerce1[0])
    destination_node2 = ox.distance.nearest_nodes(G, ecommerce[0][1], ecommerce[0][0])
    route_distance2 = nx.shortest_path(G, destination_node1, destination_node2, weight='distance')
    # ecommerce = random.choice(coordinate_eccomerce)
    try:
        for i in range(len(ecommerce)):
            destination_node2 = ox.distance.nearest_nodes(G, ecommerce[i][1], ecommerce[i][0])

            if route_distance2 > nx.shortest_path(G, destination_node1, destination_node2, weight='distance'):
                route_distance2 = nx.shortest_path(G, destination_node1, destination_node2, weight='distance')
                destination_node1 = destination_node2
                closest = i
        
        print(closest, ecommerce)
        
        ecommerce1 = ecommerce[closest]
        ecommerce.pop(closest)
        driver_route.append(route_distance2)
        print(ecommerce1)
        print(ecommerce)
        print()
        j+=1
    except nx.NetworkXNoPath:
        print('No path')
    

# ox.save_load.save_graph_osm(G, filename='test.osm')
fig, ax = ox.plot_graph_routes(G, driver_route, route_linewidth=6, node_size=0)


# print(len(driver_route))
# print(driver_route)


                



