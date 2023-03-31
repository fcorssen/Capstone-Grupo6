import osmnx as ox
import pandas as pd
import folium
import numpy as np
from folium.plugins import MarkerCluster


df = pd.read_excel("datos/deliveries_data.xlsx", index_col=0)
df_driver = pd.read_excel("datos/driver_origins_data.xlsx", index_col=0)
df_center = pd.read_excel("datos/centers_data.xlsx", index_col=0)
df_eccomerce = pd.read_excel("datos/e-commerce_data.xlsx", index_col=0)

coordinate_eccomerce = []
coordinate_center = []
coordinate_driver = []
coordinate = []

# ------------- Separar por dias --------------
days = []
amountDays = []

for i in range(df['delivery_day'].size):
    days.append(df['delivery_day'].iat[i].day)

for i in range(30):
    value = days.count(i + 1)
    amountDays.append(value)


# -------- ADD LOCATON DELIVERY --------
locations = list(zip(df['latitude'], df['longitude']))
m = folium.Map(location=(df['latitude'].iat[0], df['longitude'].iat[0]))

# for i in range(len(locations)):
#     folium.CircleMarker(location=locations[i],radius=1).add_to(m)

cluster = folium.FeatureGroup(name='cluster')
cluster.add_child(MarkerCluster(locations=locations))  
m.add_child(cluster)


# ----- ADD DRIVERS ------
for i in range(df_driver['latitude'].size):
    coordinate_driver.append([df_driver['latitude'].iat[i], df_driver['longitude'].iat[i]])

c = 0

for cor in coordinate_driver:
    if c < 10:
        folium.CircleMarker([cor[0], cor[1]], color='green', radius=8, fill=True).add_to(m)
    if c >= 10:
        folium.CircleMarker([cor[0], cor[1]], color='red', radius=8, fill=True).add_to(m)
    c += 1


# ------- ADD CENTER --------

for i in range(df_center['latitude'].size):
    coordinate_center.append([df_center['latitude'].iat[i], df_center['longitude'].iat[i]])

for cor in coordinate_center:
        folium.CircleMarker([cor[0], cor[1]], color='blue', radius=10, fill=True).add_to(m)



#  ------- ADD ECCOMERCE --------
for i in range(df_eccomerce['latitude'].size):
    coordinate_eccomerce.append([df_eccomerce['latitude'].iat[i], df_eccomerce['longitude'].iat[i]])

for cor in coordinate_eccomerce:
        # folium.Marker([cor[0], cor[1]], popup="<i>Ecommerce", icon=folium.Icon(color='orange', icon='')).add_to(m)
        folium.CircleMarker([cor[0], cor[1]], color='black', radius=4, fill=True).add_to(m)

# ----- GUARDO TOD0 ------
m.save("maps/map.html")