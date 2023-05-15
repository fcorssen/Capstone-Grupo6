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

# Ordenar los ecomerce por ceracnia a un punto
ecom_order = []
ecom_id = []
for j in range(len(ecommerces)):
    distance = 1000000
    for i in range(len(ecommerces)):
        if ecommerces[i].id not in ecom_id:
            if distance >= geopy.distance.geodesic([-33.4369436, -70.634449], ecommerces[i].ubicacion).km:
                distance = geopy.distance.geodesic([-33.4369436, -70.634449], ecommerces[i].ubicacion).km
                ecom = ecommerces[i]

    ecom_id.append(ecom.id)
    ecom_order.append(ecom)

ecom_order.reverse()


# Asignar rutas por ecommerce
ecom_route = []
ecom_route_id = []
ecom_visited = []
centro = centros[3].ubicacion
for k in range(18):

    route = []
    route_id = []

    if k < 6:
        n = 5
    else:
        n = 6
    
    for i in range(len(ecom_order)):
        if ecom_order[i].id not in ecom_visited:
            route.append(ecom_order[i].ubicacion)
            ecom_visited.append(ecom_order[i].id)
            break

    while len(route) < n:
        min_dis = 100000
        for i in range(len(ecommerces)):
            if ecommerces[i].id not in ecom_visited:
                if min_dis >= geopy.distance.geodesic(route[-1], ecommerces[i].ubicacion).km:
                    min_dis = geopy.distance.geodesic(route[-1], ecommerces[i].ubicacion).km
                    ecom_add = ecommerces[i]

        route.append(ecom_add.ubicacion)
        ecom_visited.append(ecom_add.id)
        route_id.append(ecom_add)

    ecom_route.append(route)
    ecom_route_id.append(route_id)


# ecom_list = []
# for ecom in ecom_route:
#     lat_total = 0
#     lon_total = 0
#     for e in ecom:
#         lat_total += e[0]
#         lon_total += e[1] 
#     ecom_list.append([lat_total/len(ecom), lon_total/len(ecom)])

# driver_list = []
# for i in range(len(drivers)):
#     min_distance = 10000
#     for j in range(len(ecom_list)):
#         if j not in driver_list:
#             if min_distance >= geopy.distance.geodesic(drivers[i].origen, ecom_list[j]).km:
#                 min_distance = geopy.distance.geodesic(drivers[i].origen, ecom_list[j]).km
#                 pos = j
#     driver_list.append(pos)

driver_list = []
for i in range(len(drivers)):
    min_distance = 10000
    for j in range(len(ecom_route)):
        if j not in driver_list:
            if min_distance >= geopy.distance.geodesic(drivers[i].origen, ecom_route[j][0]).km:
                min_distance = geopy.distance.geodesic(drivers[i].origen, ecom_route[j][0]).km
                pos = j
    driver_list.append(pos)


for i in range(len(drivers)):
    drivers[i].ruta.append(drivers[i].origen)
    for j in ecom_route_id[driver_list[i]]:
        drivers[i].agregar_ecommerce(j)
    drivers[i].ruta.append(centro)

best_distance = calculate_distance(drivers)
print(best_distance)
driver_improve = improve_route_aleatory(drivers, ecommerces, best_distance)
best_distance = calculate_distance(driver_improve)
print(best_distance)

map_distance(drivers, "simulation/maps/ecommerce_ruta_vecindad.html")


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



        
    
