from geopy import Point, distance as geopy_distance
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
from sklearn.neighbors import NearestNeighbors
from scipy.spatial import distance_matrix
from scipy.spatial import distance

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

# ------ Agregar centros a mapa ------------
for c in centros:
    folium.CircleMarker(c.ubicacion, color='yellow', radius=5, fill=True).add_to(m)

df_model = df_ecommerce[['latitude', 'longitude']]

ecommerce_loc = []
for e in ecommerces:
    ecommerce_loc.append(e.ubicacion)

# print(ecommerce_loc)

num_nodes = 102
num_clusters = 15
nodes_per_cluster = 6

# Utilizar el algoritmo K-means para generar los clusters
kmeans = KMeans(n_clusters=num_clusters, random_state=121)
kmeans.fit(ecommerce_loc)

# Obtener las etiquetas de los clusters asignados a cada ecommerce
ecommerce_labels = kmeans.labels_

poligonos = []

# Crear diccionario para almacenar los nodos por cluster
cluster_nodes = [[] for _ in range(num_clusters)]
ecommerce_clusters = {cluster_id: [] for cluster_id in range(num_clusters)}


# Asignar cada ecommerce a su respectivo cluster
for i, label in enumerate(ecommerce_labels):
    cluster_nodes[label].append(ecommerce_loc[i])
    ecommerce_clusters[label].append(ecommerces[i])


# Verificar si existen clusters con un solo nodo
solo_nodo_clusters = []
dos_nodos_clusters = []
for cluster_id, cluster in enumerate(cluster_nodes):
    if len(cluster) == 1:
        solo_nodo_clusters.append(cluster_id)
    elif len(cluster) == 2:
        dos_nodos_clusters.append(cluster_id)

# Unir clusters de un solo nodo o dos nodos con cualquier otro cluster cercano
if solo_nodo_clusters or dos_nodos_clusters:
    centroides = kmeans.cluster_centers_
    distances = cdist(centroides, centroides)

    # Unir clusters de un solo nodo con cualquier otro cluster cercano
    for solo_nodo_cluster in solo_nodo_clusters:
        closest_cluster = np.argsort(distances[solo_nodo_cluster])[1]
        cluster_nodes[closest_cluster].extend(cluster_nodes[solo_nodo_cluster])
        cluster_nodes[solo_nodo_cluster] = []  # Marcar el cluster de un solo nodo como vacío

    # Unir clusters de dos nodos con cualquier otro cluster cercano
    for dos_nodos_cluster in dos_nodos_clusters:
        closest_cluster = np.argsort(distances[dos_nodos_cluster])[1]
        if closest_cluster != dos_nodos_cluster:
            cluster_nodes[closest_cluster].extend(cluster_nodes[dos_nodos_cluster])
            cluster_nodes[dos_nodos_cluster] = []  # Marcar el cluster de dos nodos como vacío

# Subdividir los clusters en subclusters con un número fijo de nodos
for cluster in cluster_nodes:
    if len(cluster) > nodes_per_cluster:
        # Crear los subclusters
        num_subclusters = len(cluster) // nodes_per_cluster
        if len(cluster) % nodes_per_cluster != 0:
            num_subclusters += 1
        
        subclusters = np.array_split(cluster, num_subclusters)
        
        for subcluster in subclusters:
            if len(subcluster) > 0:
                poligono = folium.Polygon(locations=subcluster, color='blue', fill_opacity=0.1)
                poligonos.append(poligono)
    else:
        if len(cluster):
            poligono = folium.Polygon(locations=cluster, color='blue', fill_opacity=0.1)
            poligonos.append(poligono)

new_nodes = []
# Agregar los polígonos al mapa
for poligono in poligonos:
    centro_1 = centros[3].ubicacion
    poligono.locations.append(centro_1)
   # poligono.add_to(m)

def calcular_distancia(p1, p2):
    return geopy_distance.distance(p1, p2).km

def nearest_driver(point, drivers):
    distances = [distance.euclidean(point, driver.origen) for driver in drivers]
    index = distances.index(min(distances))
    return drivers[index]

def encontrar_ruta_mas_corta(puntos, nodo_final):
    ruta = [nodo_final]
    nodos_restantes = puntos.copy()
    nodos_restantes.remove(nodo_final)

    while nodos_restantes:
        nodo_actual = ruta[-1]
        distancia_minima = float('inf')
        siguiente_nodo = None

        for nodo in nodos_restantes:
            distancia = calcular_distancia(nodo_actual, nodo)
            if distancia < distancia_minima:
                distancia_minima = distancia
                siguiente_nodo = nodo

        ruta.append(siguiente_nodo)
        nodos_restantes.remove(siguiente_nodo)

    return ruta

# Calcular la ruta más corta para cada polígono
rutas_mas_cortas = []
distancias_totales = []
for poligono in poligonos:
    puntos_poligono = poligono.locations
    ruta_mas_corta = encontrar_ruta_mas_corta(puntos_poligono, centro_1)
    rutas_mas_cortas.append(ruta_mas_corta)

distancias_recorridas = []
conductores_asignados = []
for ruta in rutas_mas_cortas:
    largo_ruta = len(ruta)
    nodo_inicial = ruta[largo_ruta - 1]
    
    # drivers disponibles
    conductores_disponibles = [driver for driver in drivers if driver not in conductores_asignados]
    
    # Verificar si hay conductores disponibles
    if conductores_disponibles:
        driver_cercano = nearest_driver(nodo_inicial, conductores_disponibles)
        
        # Calcular la distancia entre el nodo inicial y el conductor más cercano
        distancia_inicial_driver = calcular_distancia(nodo_inicial, driver_cercano.origen)
        
        # Agregar el nodo inicial y conectarlo con el conductor más cercano
        folium.CircleMarker(nodo_inicial, color='blue', radius=5, fill=True).add_to(m)
        folium.PolyLine(locations=[nodo_inicial, driver_cercano.origen], color='blue').add_to(m)
        
        # Agregar el conductor a la lista de conductores asignados
        conductores_asignados.append(driver_cercano)
        
        # Agregar el resto de la ruta y calcular la distancia recorrida
        distancia_recorrida = distancia_inicial_driver
        for i in range(len(ruta) - 1):
            distancia_recorrida += calcular_distancia(ruta[i], ruta[i+1])
            folium.PolyLine(locations=[ruta[i], ruta[i+1]], color='green').add_to(m)
        
        distancias_recorridas.append(distancia_recorrida)
    else:
        print(f"No hay conductores disponibles para la ruta {ruta}.")
        distancias_recorridas.append(0)  # Agregar una distancia de 0 para la ruta sin conductor asignado

tabla_distancias_recorridas = pd.DataFrame({'Polígono': range(1, len(poligonos) + 1), 'Distancia Recorrida (km)': distancias_recorridas})
print(tabla_distancias_recorridas)

# Calcular la distancia total recorrida
distancia_total_recorrida = sum(distancias_recorridas)
print(f'Distancia total recorrida: {distancia_total_recorrida} km')
# Agregar los ecommerce al mapa
for e in ecommerces:
    folium.CircleMarker(e.ubicacion, color='red', radius=5, fill=True).add_to(m)

m.save("Poligonos2.html")