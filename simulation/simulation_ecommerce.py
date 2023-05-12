import geopy.distance
import pandas as pd
import random
import folium
from folium.features import DivIcon
from clases import Driver, Paquete, Ecommerce, Centro
from funciones import calculate_distance, improve_route_aleatory, map_distance, generate_colors


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


# ---------- Creamos el mapa ----------
coordinate_center = [-33.4369436, -70.634449]
m = folium.Map(location=(coordinate_center[0], coordinate_center[1]))
folium.CircleMarker(coordinate_center, color='red', radius=5, fill=True).add_to(m)


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

    folium.CircleMarker(driver.origen, color='blue', radius=5, fill=True).add_to(m)
    driver_id_order.append(driver.id)
    driver_order.append(driver)

drivers = driver_order

# drivers.reverse()

# -------- Comenzamos a simular ---------- 
ecommerce_visited = []
centro = centros[3].ubicacion

for j in range(len(drivers)):
    route = []

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

    if j < 10:
        n = 7
    else:
        n = 4
    while len(drivers[j].ruta) < n:
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

# ----- Generamos los colores --------
colors = generate_colors(len(drivers))

# ------ Graficamos los puntos --------------
for i in range(len(drivers)):
    folium.Marker(drivers[i].origen, icon=DivIcon(
                icon_size=(150,36), icon_anchor=(7,20), html=f'<div style="font-size: 18pt; color : black">{i + 1}</div>',
                )).add_to(m)
    folium.PolyLine(drivers[i].ruta, color=colors[i], weight=3, opacity=1).add_to(m)

# ------------- Sumamos la distancia total ------------
print(calculate_distance(drivers))


# ----- Ver tiempo de recoleccion -------------
# for d in drivers:
#     distance1 = 0
#     for i in range(len(d.ruta)):
#         if i != len(d.ruta) - 1:
#             distance1 += geopy.distance.geodesic(d.ruta[i], d.ruta[i+1]).km

#     print(f'tiempo = {d.tiempo} ------ distance = {distance1}')
#     print()


# m.save("simulation/maps/ecommerce.html")

# -------- Guardamos ruta en TXT ------------
with open(r'simulation/txt/ruta_ecommerce.txt', 'w') as fp:
    for driver in drivers:
        fp.write("%s " % driver.ruta)
        fp.write("\n")

best_distance = calculate_distance(drivers)
# print(best_distance)

# --------------------------------------------------------------------------------------
#                     Mejorar aleatoriamente el caso base

# driver_improve = improve_route_aleatory(drivers, best_distance)
# map_distance(driver_improve)

# --------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------
#                                   2 OPT

