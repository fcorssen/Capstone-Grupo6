from geopy import Point, distance
import pandas as pd
import numpy as np
import random
import folium
from folium.plugins import MarkerCluster
from folium.features import DivIcon
from sklearn import cluster
import matplotlib.cm as cm
import matplotlib.colors as cl
from clases import Driver, Paquete, Ecommerce, Centro
from operator import itemgetter
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from scipy.spatial.distance import cdist
from sklearn.cluster import DBSCAN
from scipy.spatial import ConvexHull, convex_hull_plot_2d
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

# ------------- Cargar los datos --------------

df_delivery = pd.read_excel("datos/deliveries_data.xlsx")
df_driver = pd.read_excel("datos/driver_origins_data.xlsx")
df_center = pd.read_excel("datos/centers_data.xlsx")
df_ecommerce = pd.read_excel("datos/e-commerce_data.xlsx")


# # ------------- Separar por dias --------------
days = []
amountDays = []

for i in range(df_delivery['delivery_day'].size):
    days.append(df_delivery['delivery_day'].iat[i].day)

for i in range(30):
    value = days.count(i + 1)
    amountDays.append(value)

# ---------- Instanciar los centros ----------
centros = []
for i in range(df_center['id'].size):
    centro = Centro(df_center['id'].iat[i], [df_center['latitude'].iat[i], df_center['longitude'].iat[i]])
    centros.append(centro)

# ---------- Instanciar los drivers ----------
drivers = []
for i in range(df_driver['id'].size):
    driver = Driver(df_driver['id'].iat[i], [df_driver['latitude'].iat[i], df_driver['longitude'].iat[i]])
    drivers.append(driver)

# ---------- Instanciar  m ecommerce ----------
ecommerces = []
for i in range(df_ecommerce['id'].size):
    ecommerce = Ecommerce(df_ecommerce['id'].iat[i], [df_ecommerce['latitude'].iat[i], df_ecommerce['longitude'].iat[i]])
    ecommerces.append(ecommerce)

# ----------  Instanciar los paquetes ----------
paquetes = []
for i in range(df_delivery['id'].size):
    paquete = Paquete(df_delivery['id'].iat[i], df_delivery['weight (kg)'].iat[i], [df_delivery['latitude'].iat[i], df_delivery['longitude'].iat[i]], df_delivery['x1 (largo en cm)'].iat[i], df_delivery['x2 (ancho en cm)'].iat[i], df_delivery['x3 (alto en cm)'].iat[i], df_delivery['delivery_day'].iat[i].day, df_delivery['e-commerce_id'].iat[i])
    paquetes.append(paquete)

# ---------- Paquetes dia 1 ----------
paquetes_dia_1 = paquetes[:amountDays[0]]

# ---------- Agregar paquetes a los ecommerce para el dia 1 ----------
for paquete in paquetes_dia_1:
    for ecommerce in ecommerces:
        if paquete.ecommerce == ecommerce.id:
            ecommerce.agregar_paquete(paquete)

# -------- Crear Mapa -----------
m = folium.Map(location=([-33.4369436, -70.634449]))

# ------ Agregar drivers a mapa ------------
for d in drivers:
    folium.CircleMarker(d.origen, color='black', radius=5, fill=True).add_to(m)


df_model = df_ecommerce[['latitude', 'longitude']]

ecommerce_loc = []
for e in ecommerces:
    ecommerce_loc.append(e.ubicacion)

# print(ecommerce_loc)



kmeans = KMeans(n_clusters=15, max_iter=6, random_state=121)

# Entrenar el modelo con las ubicaciones de los ecommerce
kmeans.fit(ecommerce_loc)

# Obtener las etiquetas de los clusters asignados a cada ecommerce
ecommerce_labels = kmeans.labels_

poligonos = []

for e in ecommerces:
    folium.CircleMarker(e.ubicacion, color='black', radius=5, fill=True).add_to(m)

for d in drivers:
    folium.CircleMarker(d.origen, color='black', radius=5, fill=True).add_to(m)


# Iterar sobre cada cluster
for i in range(15):
    # Obtener las ubicaciones de los ecommerce que pertenecen al cluster i
    cluster_loc = []
    for j in range(len(ecommerce_labels)):
        if ecommerce_labels[j] == i:
            cluster_loc.append(ecommerce_loc[j])
#     # Crear un polígono con las ubicaciones de los ecommerce del cluster i
    if len(cluster_loc) >0:
        poligono = folium.Polygon(locations=cluster_loc, color='blue', fill_opacity=0.1)
        poligonos.append(poligono)
    print(len(cluster_loc))

# # print(poligonos)

# # Agregar los polígonos al mapa
for poligono in poligonos:
    poligono.add_to(m)

# # Agregar los ecommerce al mapa
for e in ecommerces:
    folium.CircleMarker(e.ubicacion, color='red', radius=5, fill=True).add_to(m)

m.save("Poligonos2.html")

