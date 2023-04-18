import osmnx as ox
import networkx as nx
import pandas as pd
import random

# random.seed(1000330) CON ESTOS VALORES NO SE PUEDE
random.seed(12345)

df_driver = pd.read_excel("datos/driver_origins_data.xlsx", index_col=0)
df_eccomerce = pd.read_excel("datos/e-commerce_data.xlsx", index_col=0)

coordinate_driver = []
for i in range(df_driver['latitude'].size):
    coordinate_driver.append([df_driver['latitude'].iat[i], df_driver['longitude'].iat[i]])

coordinate_eccomerce = []
for i in range(df_eccomerce['latitude'].size):
    coordinate_eccomerce.append([df_eccomerce['latitude'].iat[i], df_eccomerce['longitude'].iat[i]])


driver = random.choice(coordinate_driver)
eccomerce = random.choice(coordinate_eccomerce)
eccomerce1 = random.choice(coordinate_eccomerce)
eccomerce2 = random.choice(coordinate_eccomerce)



# place_name = "Provincia de Santiago, Chile"
# G = ox.graph_from_place(place_name, network_type="drive")
G = ox.graph_from_point((driver[0], driver[1]), dist= 5000, dist_type='bbox', network_type='drive')
# fig, ax = ox.plot_graph(graph, node_color="r") 

G = ox.add_edge_speeds(G)
G = ox.add_edge_travel_times(G)

orig_node = ox.distance.nearest_nodes(G, driver[1], driver[0])
destination_node = ox.distance.nearest_nodes(G, eccomerce[1], eccomerce[0])
destination_node1 = ox.distance.nearest_nodes(G, eccomerce1[1], eccomerce1[0])
destination_node2 = ox.distance.nearest_nodes(G, eccomerce2[1], eccomerce2[0])


route_distance = nx.shortest_path(G, orig_node, destination_node, weight='distance')

route_distance1 = nx.shortest_path(G, destination_node, destination_node1, weight='distance')
route_distance2 = nx.shortest_path(G, destination_node1, destination_node2, weight='distance')

routes = [route_distance, route_distance1, route_distance2]
rc = ['r', 'y', 'c']
fig, ax = ox.plot_graph_routes(G, routes, route_colors=rc, route_linewidth=6, node_size=0)

route_time = nx.shortest_path(G, orig_node, destination_node, weight='travel_time')
route_time1 = nx.shortest_path(G, destination_node, destination_node1, weight='distance')
route_time2 = nx.shortest_path(G, destination_node1, destination_node2, weight='distance')


edge_lengths = ox.utils_graph.get_route_edge_attributes(
    G, route_distance, 'length') 
total_route_length = sum(edge_lengths)
edge_lengths = ox.utils_graph.get_route_edge_attributes(
    G, route_distance1, 'length') 
total_route_length1 = sum(edge_lengths)
edge_lengths = ox.utils_graph.get_route_edge_attributes(
    G, route_distance2, 'length') 
total_route_length2 = sum(edge_lengths)
total_length = total_route_length + total_route_length1 + total_route_length2
print("Total route length in km:", total_length/1000)

edge_travel_time = ox.utils_graph.get_route_edge_attributes(
    G, route_time, 'travel_time') 
route_travel_time = sum(edge_travel_time)
edge_travel_time = ox.utils_graph.get_route_edge_attributes(
    G, route_time1, 'travel_time') 
route_travel_time1 = sum(edge_travel_time)
edge_travel_time = ox.utils_graph.get_route_edge_attributes(
    G, route_time2, 'travel_time') 
route_travel_time2 = sum(edge_travel_time)
total_time = route_travel_time + route_travel_time1 + route_travel_time2
print("Travel time in minutes:", total_time/60)