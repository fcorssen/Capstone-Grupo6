import geopy.distance
import pandas as pd
import random
import folium
from folium.features import DivIcon
from clases import Driver, Paquete, Ecommerce, Centro
from funciones import calculate_distance, improve_route_aleatory, map_distance, generate_colors, swap_ecommerce, vecindad, improve_route
from Opt2_function import distance_driver, opt2

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

# Definimos una vecindad a cada ecommerce
vecindad(ecommerces)

# ---------- Creamos el mapa ----------
coordinate_center = [-33.4369436, -70.634449]
m = folium.Map(location=(coordinate_center[0], coordinate_center[1]))
# folium.CircleMarker(coordinate_center, color='red', radius=5, fill=True).add_to(m)


# --------- Ordenamos los driver por cercania a un punto ------------------- 
driver_order = []
driver_id_order = []


for j in range(len(drivers)):
    distance = 1000000
    for i in range(len(drivers)):
        if drivers[i].id not in driver_id_order:
            if distance >= geopy.distance.geodesic(coordinate_center, drivers[i].origen).km:
                distance = geopy.distance.geodesic(coordinate_center, drivers[i].origen).km
                driver = drivers[i]

    driver_id_order.append(driver.id)
    driver_order.append(driver)

drivers = driver_order

drivers.reverse()

# -------- Comenzamos a simular ---------- 
ecommerce_visited = []
centro = centros[3].ubicacion

for j in range(len(drivers)):

    distance = 100000000000

    for i in range(len(ecommerces)):
        if ecommerces[i].id not in ecommerce_visited:
            if drivers[j].peso < 450 and drivers[j].volumen < 2:
                if distance >= geopy.distance.geodesic(drivers[j].origen, ecommerces[i].ubicacion).km:
                    distance = geopy.distance.geodesic(drivers[j].origen, ecommerces[i].ubicacion).km
                    ecommerce = ecommerces[i]

    # Agregamos punto a la ruta
    drivers[j].agregar_ecommerce(ecommerce)
    ecommerce_visited.append(ecommerce.id)

    if j < 12:
        n = 6
    else:
        n = 5
    
    while len(drivers[j].ruta) < n:
        vecindad = False
        distance = 10000
        for k in range(len(drivers[j].ecommerce[-1].vecindad)): 
            if drivers[j].ecommerce[-1].vecindad[k].id not in ecommerce_visited:
                if distance >= geopy.distance.geodesic(drivers[j].ruta[-1], drivers[j].ecommerce[-1].vecindad[k].ubicacion).km:
                        distance = geopy.distance.geodesic(drivers[j].ruta[-1], drivers[j].ecommerce[-1].vecindad[k].ubicacion).km
                        ec_add = drivers[j].ecommerce[-1].vecindad[k]
                        vecindad = True
        drivers[j].agregar_ecommerce(ec_add)
        ecommerce_visited.append(ec_add.id)
                

        if not vecindad: 
            distance = 100000
            # Guardamos la minima distancia entre los puntos
            for i in range(len(ecommerces)):
                # Revisamos si el nodo ya esta en la ruta
                if ecommerces[i].id not in ecommerce_visited:
                    # Revisamos condicion de peso y dimensiones
                    if drivers[j].peso < 450 and drivers[j].volumen < 2:
                        if distance >= geopy.distance.geodesic(drivers[j].ruta[-1], ecommerces[i].ubicacion).km:
                            distance = geopy.distance.geodesic(drivers[j].ruta[-1], ecommerces[i].ubicacion).km
                            ecommerce = ecommerces[i] 
            # Add to route 
            drivers[j].agregar_ecommerce(ecommerce)
            ecommerce_visited.append(ecommerce.id)
    
    # Agrego la ubicacion inical del driver y la bodega
    drivers[j].ruta.insert(0, drivers[j].origen)
    drivers[j].ruta.append(centro)


best_distance = calculate_distance(drivers)
print(best_distance)
# driver_improve = improve_route(drivers, ecommerces, best_distance)
for d in drivers:
    d.ruta = opt2(d.ruta)
best_distance = calculate_distance(drivers)
print(best_distance)
t_prom = 0
d_prom = 0
for d in drivers:
    dis = distance_driver(d)
    tiempo_recoleccion = (dis/30)*60
    print(f'{d.id} ---- Distancia {dis} ---- tiempo {d.tiempo + tiempo_recoleccion}')
    t_prom += d.tiempo + tiempo_recoleccion
    d_prom += dis
    print()
print(f'Tiempo promedio = {t_prom/18}')
print(f'Distancia promedio = {d_prom/18}')
# map_distance(drivers, "simulation/maps/ecommerce_vecindad_improve.html")