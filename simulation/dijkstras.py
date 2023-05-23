import geopy.distance
import pandas as pd
import random
import folium
from folium.features import DivIcon
from clases import Driver, Paquete, Ecommerce, Centro
from funciones import calculate_distance, improve_route_aleatory, map_distance, generate_colors
from graph_dijkstras import Graph


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

# ---------- Instanciar los ecommerce ---------- 
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


elementos = [i for i in range(102)]
lista_elementos = []
i = 0
for d in drivers:
    if i < 12:
        elem = random.sample(elementos, 6)
    else:
        elem = random.sample(elementos, 5)
    lista_elementos.append(elem)
    for e in elem:
        d.agregar_ecommerce(ecommerces[e])
        elementos.remove(e)
    i+=1


for d in drivers:
    d.ruta.insert(0, d.origen)
    d.ruta.append(centros[3].ubicacion)

graph = []
for i in range(len(drivers[0].ruta) - 1):
    g = []
    for j in range(len(drivers[0].ruta) - 1):
        g.append(geopy.distance.geodesic(drivers[0].ruta[i], drivers[0].ruta[j]).km)
    graph.append(g)
# print(graph)

# # Pa elem1 quiero la ruta mínima para recorrer sus nodos
# #elem1[0] un nodo: quiero elem1[0], elem1[1] = 102

g = Graph(7)
g.graph = graph



g.dijkstra(0,drivers[0].ruta)


# # Tienen 6 nodos, calcular el grafo entre estos 6 nodos,  n^2   

