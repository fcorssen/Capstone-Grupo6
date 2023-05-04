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

coordinate_center = [-33.4369436, -70.634449]
# Creamos mapa
m = folium.Map(location=(coordinate_center[0], coordinate_center[1]))
folium.CircleMarker(coordinate_center, color='red', radius=5, fill=True).add_to(m)

list_driver = df_driver.values.tolist()
driver_order = []
driver_id_order = []

for j in range(len(list_driver)):
    driver = 0
    distance = 1000000
    for i in range(len(list_driver)):
        if int(list_driver[i][0]) not in driver_id_order:
            if distance >= geopy.distance.geodesic(coordinate_center, [list_driver[i][1], list_driver[i][2]]).km:
                distance = geopy.distance.geodesic(coordinate_center, [list_driver[i][1], list_driver[i][2]]).km
                driver = [list_driver[i][1], list_driver[i][2]]
                driver_id = list_driver[i][0]

    folium.CircleMarker(driver, color='blue', radius=5, fill=True).add_to(m)
    driver_id_order.append(driver_id)
    driver_order.append(driver)

# --------- Generar data frame para dia 1 ----------
df_delivery_day = df_delivery_day[:amountDays[0]]


# ------ Craer dataframe con suma de dimensiones y peso
df_dim = df_delivery_day.groupby('e-commerce_id').agg({'dimensiones': ['count', 'sum'], 'weight (kg)': 'sum'})
df_dim.columns = ['count', 'dimension', 'weight']
list_dim = df_dim.values.tolist()

# ------- Crea lista con id del ecommerce y ubicacion
list_cor = df_delivery_day[['e-commerce_id', 'latitude_ecommerce', 'longitude_ecommerce']].values.tolist()

# ---- Elimimno los ecommerce repetidos ----------- 
list_cor.sort()
list_cor = list(list_cor for list_cor,_ in itertools.groupby(list_cor))

ecommerce_visited = []
route_drivers = []
route_drivers_plot = []


for j in range(len(driver_order)):
    route = []
    plot_route = []
    weight = 0
    dim = 0
    ecommerce_id = 0

    distance = 100000000000

    for i in range(len(list_cor)):
        if list_cor[i][0] not in ecommerce_visited:
            if weight < 450 and dim < 2:
                if distance >= geopy.distance.geodesic([driver_order[j][0], driver_order[j][1]], [list_cor[i][1], list_cor[i][2]]).km:
                    distance = geopy.distance.geodesic([driver_order[j][0], driver_order[j][1]], [list_cor[i][1], list_cor[i][2]]).km
                    ecommerce_id = list_cor[i][0]

        # Agregamos punto a la ruta
    route.append(list_cor[int(ecommerce_id) - 1][0])
    ecommerce_visited.append(list_cor[int(ecommerce_id) - 1][0])

    # Sumamos peso y dimensiones
    weight += list_dim[int(ecommerce_id) - 1][2]
    dim += list_dim[int(ecommerce_id) - 1][1]
    
    # Agregar direccion driver
    plot_route.append([driver_order[j][0], driver_order[j][1]])
    # Agregar direccion ecommerce
    plot_route.append([list_cor[int(ecommerce_id) - 1][1], list_cor[int(ecommerce_id) - 1][2]])
    if j < 10:
        n = 7
    else:
        n = 4
    while len(route) < n:

        distance = 100000

        # Guardamos la minima distancia entre los puntos
        for i in range(len(list_cor)):
            # Revisamos si el nodo ya esta en la ruta
            if list_cor[i][0] not in ecommerce_visited:
                # Revisamos condicion de peso y dimensiones
                if weight < 450 and dim < 2:
                    if distance >= geopy.distance.geodesic([list_cor[int(route[-1]) - 1][1], list_cor[int(route[-1]) - 1][2]], [list_cor[i][1], list_cor[i][2]]).km:
                        distance = geopy.distance.geodesic([list_cor[int(route[-1]) - 1][1], list_cor[int(route[-1]) - 1][2]], [list_cor[i][1], list_cor[i][2]]).km
                        ecommerce_id = list_cor[i][0]

        
        # Add to route 
        route.append(list_cor[int(ecommerce_id) - 1][0])
        ecommerce_visited.append(list_cor[int(ecommerce_id) - 1][0])
        plot_route.append([list_cor[int(ecommerce_id) - 1][1], list_cor[int(ecommerce_id) - 1][2]])

        # Sumamos peso y dimensiones
        weight += list_dim[int(ecommerce_id) - 1][2]
        dim += list_dim[int(ecommerce_id) - 1][1]

    route_drivers.append(route)
    route_drivers_plot.append(plot_route)   

# print(route_drivers)
# print(route_drivers_plot)
for i in range(len(route_drivers)):
    for j in range(len(route_drivers[i])):
        pos = int(route_drivers[i][j])
        # Agregamos el punto al mapa
        folium.Marker([list_cor[pos-1][1], list_cor[pos-1][2]], icon=DivIcon(
                icon_size=(150,36), icon_anchor=(7,20), html=f'<div style="font-size: 18pt; color : black">{pos}</div>',
                )).add_to(m)
        for k in range(len(route_drivers_plot)):
            plot = route_drivers_plot[k]
            folium.PolyLine(plot, color="red", weight=1.5, opacity=1).add_to(m)

m.save("osmnx/aa.html")

