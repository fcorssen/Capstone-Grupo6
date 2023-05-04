import geopy.distance
import pandas as pd
import osmnx as ox
import networkx as nx
import random
import itertools
import folium
from folium.features import DivIcon

random.seed(12345)


# ------------- Cargar los datos --------------
df_delivery = pd.read_excel("datos/deliveries_data.xlsx", index_col=0)
df_driver = pd.read_excel("datos/driver_origins_data.xlsx")
df_center = pd.read_excel("datos/centers_data.xlsx")
df_delivery_day = pd.read_excel("datos/delivery_ecommerce.xlsx")

# # ------------- Separar por dias --------------
days = []
amountDays = []

for i in range(df_delivery['delivery_day'].size):
    days.append(df_delivery['delivery_day'].iat[i].day)

for i in range(30):
    value = days.count(i + 1)
    amountDays.append(value)

# ----- Obtenemos coordenadas de centro de distribucion ------------
coor_center = df_center.values.tolist()[-1][1:]

# ---------- Creamos mapa ------------ 
m = folium.Map(location=(coor_center[0], coor_center[1]))
folium.CircleMarker(coor_center, color='red', radius=5, fill=True).add_to(m)

# --------- Generar data frame para dia 1 ----------
df_delivery_day = df_delivery_day[:amountDays[0]]


# ------- Crea lista con id del ecommerce y ubicacion
list_delivery = df_delivery_day[['latitude', 'longitude', 'weight (kg)', 'dimensiones']].values.tolist()
for i in range(len(list_delivery)):
    list_delivery[i].insert(0, i)

# --------- Ordenamos los driver por cercania a un punto ------------------- 
list_driver = df_driver.values.tolist()
driver_order = []
driver_id_order = []

for j in range(len(list_driver)):
    driver = 0
    distance = 1000000
    for i in range(len(list_driver)):
        if int(list_driver[i][0]) not in driver_id_order:
            if distance >= geopy.distance.geodesic(coor_center, [list_driver[i][1], list_driver[i][2]]).km:
                distance = geopy.distance.geodesic(coor_center, [list_driver[i][1], list_driver[i][2]]).km
                driver = [list_driver[i][1], list_driver[i][2]]
                driver_id = list_driver[i][0]

    folium.CircleMarker(driver, color='blue', radius=5, fill=True).add_to(m)
    driver_id_order.append(driver_id)
    driver_order.append(driver)


# ------- Simular -----------
delivery_visited = []
route_drivers = []
route_drivers_plot = []


for j in range(len(driver_order)):
    route = []
    plot_route = []
    weight = 0
    dim = 0
    delivery_id = 0

    distance = 100000000000

    for i in range(len(list_delivery)):
        if list_delivery[i][0] not in delivery_visited:
            if weight < 450 and dim < 2:
                if distance >= geopy.distance.geodesic(coor_center, [list_delivery[i][1], list_delivery[i][2]]).km:
                    distance = geopy.distance.geodesic(coor_center, [list_delivery[i][1], list_delivery[i][2]]).km
                    delivery_id = list_delivery[i][0]

        # Agregamos punto a la ruta
    route.append(list_delivery[delivery_id][0])
    delivery_visited.append(list_delivery[delivery_id][0])

    # Sumamos peso y dimensiones
    weight += list_delivery[delivery_id][3]
    dim += list_delivery[delivery_id][4]


    # Agregar direccion ecommerce
    plot_route.append([list_delivery[delivery_id][1], list_delivery[delivery_id][2]])

    while len(route) < 42:

        distance = 100000

        # Guardamos la minima distancia entre los puntos
        for i in range(len(list_delivery)):
            # Revisamos si el nodo ya esta en la ruta
            if list_delivery[i][0] not in delivery_visited:
                # Revisamos condicion de peso y dimensiones
                if weight < 450 and dim < 2:
                    if distance >= geopy.distance.geodesic([list_delivery[route[-1]][1], list_delivery[route[-1]][2]], [list_delivery[i][1], list_delivery[i][2]]).km:
                        distance = geopy.distance.geodesic([list_delivery[route[-1]][1], list_delivery[route[-1]][2]], [list_delivery[i][1], list_delivery[i][2]]).km
                        delivery_id = list_delivery[i][0]

        
        # Add to route 
        route.append(list_delivery[delivery_id][0])
        delivery_visited.append(list_delivery[delivery_id][0])
        plot_route.append([list_delivery[delivery_id][1], list_delivery[delivery_id][2]])

        # Sumamos peso y dimensiones
        weight += list_delivery[delivery_id][3]
        dim += list_delivery[delivery_id][4]
    
    plot_route.append([driver_order[j][0], driver_order[j][1]])

    route_drivers.append(route)
    route_drivers_plot.append(plot_route)   


# -------- Ploteamos los puntos -----------
for i in range(len(route_drivers)):
    for j in range(len(route_drivers[i])):
        pos = int(route_drivers[i][j])
        # Agregamos el punto al mapa
        folium.Marker([list_delivery[pos-1][1], list_delivery[pos-1][2]], icon=DivIcon(
                icon_size=(150,36), icon_anchor=(7,20), html=f'<div style="font-size: 18pt; color : black">{pos}</div>',
                )).add_to(m)
        for k in range(len(route_drivers_plot)):
            plot = route_drivers_plot[k]
            folium.PolyLine(plot, color="red", weight=1.5, opacity=1).add_to(m)

# -------- Sumamos la distancia total--------
distance = 0
for k in range(len(route_drivers_plot)):
    plot = route_drivers_plot[k]
    for i in range(len(plot)):
        if i != len(plot)-1:
            distance += geopy.distance.geodesic(plot[i], plot[i+1]).km
print(distance)

# ---- Guardamos el mapa ------
m.save("osmnx/maps/linea_recta_delivery.html")