import pandas as pd
import osmnx as ox
import networkx as nx
import random

random.seed(12345)


# Cargar los datos
df_delivery = pd.read_excel("datos/deliveries_data.xlsx", index_col=0)
df_driver = pd.read_excel("datos/driver_origins_data.xlsx")
df_center = pd.read_excel("datos/centers_data.xlsx")
df_eccomerce = pd.read_excel("datos/e-commerce_data.xlsx")
df_delivery_day = pd.read_excel("datos/delivery_ecommerce.xlsx")


# # ------------- Separar por dias --------------
days = []
amountDays = []

for i in range(df_delivery['delivery_day'].size):
    days.append(df_delivery['delivery_day'].iat[i].day)

for i in range(30):
    value = days.count(i + 1)
    amountDays.append(value)


# # ---------- Driver al azar -----------------
driver = random.choice(df_driver[['latitude', 'longitude']].values.tolist())

# # --------- Generar data frame para dia 1 ----------
df_delivery_day = df_delivery_day[:amountDays[0]]
# print(df_delivery_day.groupby('e-commerce_id')['dimensiones'].sum())


# # # ------- Cargar mapa -----------------
G = ox.graph_from_point((driver[0], driver[1]), dist= 10000, dist_type='bbox', network_type='drive')

G = ox.add_edge_speeds(G)
G = ox.add_edge_travel_times(G)

# # # # ---------- Generar ruta ------------
driver_route = []
total_lenght = 0

# Selecciono una muestra de los ecommerce
ecommerce = random.sample(df_delivery_day[['latitude_ecommerce', 'longitude_ecommerce']].values.tolist(), 20)


# Escogo el nodo mas cerca del driver elegido
orig_node = ox.distance.nearest_nodes(G, driver[1], driver[0])
destination_node = ox.distance.nearest_nodes(G, ecommerce[0][1], ecommerce[0][0])
route_distance = nx.shortest_path(G, orig_node, destination_node, weight='distance')
closest = 0
ruta = []

for i in range(len(ecommerce)):
    destination_node1 = ox.distance.nearest_nodes(G, ecommerce[i][1], ecommerce[i][0])
    edge_lengths = ox.utils_graph.get_route_edge_attributes(
        G, nx.shortest_path(G, orig_node, destination_node1, weight='distance'), 'length')
    print(sum(edge_lengths))
    if route_distance > nx.shortest_path(G, orig_node, destination_node1, weight='distance'):
        destination_node = destination_node1
        route_distance = nx.shortest_path(G, orig_node, destination_node, weight='distance')
        closest = i

edge_lengths = ox.utils_graph.get_route_edge_attributes(
    G, route_distance, 'length') 
print('MIN distance', sum(edge_lengths))
print()
ruta.append([orig_node, destination_node])

# Guardamos la distancia mas corta para 
ecommerce_ini = ecommerce[closest]
ecommerce.pop(closest)
total_lenght += sum(edge_lengths)


driver_route.append(route_distance)

j = 0
while (len(driver_route) < 6):
    
    if j == 0:
        destination_node1 = ox.distance.nearest_nodes(G, ecommerce_ini[1], ecommerce_ini[0])
    else:
        destination_node1 = ox.distance.nearest_nodes(G, ecommerce1[1], ecommerce1[0])
    destination_node2 = ox.distance.nearest_nodes(G, ecommerce[0][1], ecommerce[0][0])
    route_distance = nx.shortest_path(G, destination_node1, destination_node2, weight='distance')
    # ecommerce = random.choice(coordinate_eccomerce)
    print()
    print('-------------------------------------------------------------------')
    print()

    try:
        for i in range(len(ecommerce)):
            destination_node2 = ox.distance.nearest_nodes(G, ecommerce[i][1], ecommerce[i][0])

            edge_lengths = ox.utils_graph.get_route_edge_attributes(
                G, route_distance, 'length') 
            print('MIN ', sum(edge_lengths))
            print('----- Es menor? ----')
            print(route_distance >= nx.shortest_path(G, destination_node1, destination_node2, weight='distance'))
            print(format(sum(edge_lengths), ".6f"), format(sum(ox.utils_graph.get_route_edge_attributes(
                G, nx.shortest_path(G, destination_node1, destination_node2, weight='distance'), 'length')), ".6f"))
            print()

            if route_distance >= nx.shortest_path(G, destination_node1, destination_node2, weight='distance'):
                
                route_distance = nx.shortest_path(G, destination_node1, destination_node2, weight='distance')
                edge_lengths = ox.utils_graph.get_route_edge_attributes(
                    G, route_distance, 'length') 
                print('MIN distance', sum(edge_lengths))
                destination_node1 = destination_node2
                closest = i
                
        ecommerce1 = ecommerce[closest]
        print('---- Ultimo punto ---   ', ecommerce1)
        ecommerce.pop(closest)
        driver_route.append(route_distance)
        ruta.append([destination_node1, destination_node2])
        j+=1
        edge_lengths = ox.utils_graph.get_route_edge_attributes(
            G, route_distance, 'length') 
        total_lenght += sum(edge_lengths)  
    except nx.NetworkXNoPath:
        print('No path')
    

# # ox.save_load.save_graph_osm(G, filename='test.osm')
# rc = ['r', 'y', 'c', 'r']
print()
print('---------- Total Length ------------', total_lenght/1000)
print()
# fig, ax = ox.plot_graph_routes(G, driver_route, route_linewidth=6, node_size=0)

print(ruta)
