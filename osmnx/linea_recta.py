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


# # ---------- Driver al azar -----------------
driver = random.choice(df_driver[['latitude', 'longitude']].values.tolist())

# # --------- Generar data frame para dia 1 ----------
df_delivery_day = df_delivery_day[:amountDays[0]]


# ------ Craer dataframe con suma de dimensiones y peso
df_dim = df_delivery_day.groupby('e-commerce_id').agg({'dimensiones': ['count', 'sum'], 'weight (kg)': 'sum'})
df_dim.columns = ['count', 'dimension', 'weight']

# ------- Crea lista con id del ecommerce y ubicacion
list_cor = df_delivery_day[['e-commerce_id', 'latitude_ecommerce', 'longitude_ecommerce']].values.tolist()

# ---- Elimimno los ecommerce repetidos ----------- 
list_cor.sort()
list_cor = list(list_cor for list_cor,_ in itertools.groupby(list_cor))

# Creamos mapa
m = folium.Map(location=(driver[0], driver[1]))
folium.CircleMarker([driver[0], driver[1]], color='blue', radius=5, fill=True).add_to(m)


# Creo la distancia para partir entre driver y primer ecommerce
distance = geopy.distance.geodesic(driver, [list_cor[0][1], list_cor[0][2]]).km

route = []
plot_route = []
ecommerce_id = 0

for i in range(len(list_cor)):
    if distance >= geopy.distance.geodesic(driver, [list_cor[i][1], list_cor[i][2]]).km:
        distance = geopy.distance.geodesic(driver, [list_cor[i][1], list_cor[i][2]]).km
        ecommerce_id = list_cor[i][0]

# Agregamos el punto al mapa
folium.Marker([list_cor[int(ecommerce_id) - 1][1], list_cor[int(ecommerce_id) - 1][2]], icon=DivIcon(
        icon_size=(150,36), icon_anchor=(7,20), html=f'<div style="font-size: 18pt; color : black">{int(ecommerce_id)}</div>',
        )).add_to(m)

# Agregamos punto a la ruta
route.append(list_cor[int(ecommerce_id) - 1][0])
plot_route.append([list_cor[int(ecommerce_id) - 1][1], list_cor[int(ecommerce_id) - 1][2]])


i = 0

while len(route) < 10:

    distance = geopy.distance.geodesic([list_cor[0][1], list_cor[0][2]], [list_cor[int(route[-1]) - 1][1], list_cor[int(route[-1]) - 1][2]]).km
    
    # Guardamos la minima distancia entre los puntos
    for i in range(len(list_cor)):
        # Revisamos si el nodo ya esta en la ruta
        if list_cor[i][0] not in route:
            # print(f'i {i} ----  Distance {distance} ---- newD { geopy.distance.geodesic([list_cor[i][1], list_cor[i][2]], [list_cor[i][1], list_cor[i][2]]).km}')
            if distance >= geopy.distance.geodesic([list_cor[int(route[-1]) - 1][1], list_cor[int(route[-1]) - 1][2]], [list_cor[i][1], list_cor[i][2]]).km:
                distance = geopy.distance.geodesic([list_cor[int(route[-1]) - 1][1], list_cor[int(route[-1]) - 1][2]], [list_cor[i][1], list_cor[i][2]]).km
                ecommerce_id = list_cor[i][0]
    
    # Add to route 
    route.append(list_cor[int(ecommerce_id) - 1][0])
    plot_route.append([list_cor[int(ecommerce_id) - 1][1], list_cor[int(ecommerce_id) - 1][2]])
    # Agregamos el ecommerce al mapa
    folium.Marker([list_cor[int(ecommerce_id) - 1][1], list_cor[int(ecommerce_id) - 1][2]], icon=DivIcon(
        icon_size=(150,36), icon_anchor=(7,20), html=f'<div style="font-size: 18pt; color : black">{list_cor[int(ecommerce_id) - 1][0]}</div>',
        )).add_to(m)



print(route)
print(plot_route)
folium.PolyLine(plot_route, color="red", weight=1.5, opacity=1).add_to(m)
m.save("osmnx/linea_recta.html")

