import geopy.distance
import random
import numpy as np
from copy import deepcopy
import folium
from folium.features import DivIcon
import matplotlib.cm as cm
import matplotlib.colors as cl


# random.seed(343545)

def calculate_distance(drivers):
    distance = 0
    for i in range(len(drivers)):
        for j in range(len(drivers[i].ruta)):
            if j != len(drivers[i].ruta) - 1:
                distance += geopy.distance.geodesic(drivers[i].ruta[j], drivers[i].ruta[j+1]).km
    return distance


def min_route(ecommerces, driver):
    list_route = ecommerces
    route = []
    distance = 10000000
    for i in range(len(list_route)):
        if list_route[i] not in route:
            if driver.peso < 450 and driver.volumen < 2:
                if distance >= geopy.distance.geodesic(driver.origen, list_route[i]).km:
                    distance = geopy.distance.geodesic(driver.origen, list_route[i]).km
                    ecommerce = list_route[i]
    route.append(ecommerce)

    while len(route) < len(list_route):
        distance = 1000000
        
        for i in range(len(list_route)):
            if list_route[i] not in route:
                if driver.peso < 450 and driver.volumen < 2:
                    if distance >= geopy.distance.geodesic(route[-1], list_route[i]).km:
                        distance = geopy.distance.geodesic(route[-1], list_route[i]).km
                        ecommerce = list_route[i]
        route.append(ecommerce)

    return route


def improve_route_aleatory(drivers, best_distance):

    drivers_copy = deepcopy(drivers)

    
    # HAY Q REVISAR BIEN SI LA RUTA NO EXCEDE LAS CAPACIDADES DE PESO Y DIMENSION PQ
    # AL ITERAR 20000 VECES DIO UN  DRIVER CON MUCHISIMOS ECOMMERCE
    # Entre mas iteraciones mejor es el resultado
    for i in range(1000):
        try:
            driver_take = random.randint(0, len(drivers) - 1)
            driver_give = random.randint(0, len(drivers) - 1)
            

            # Asegurarse que son distinto drivers
            while driver_take == driver_give:
                driver_take = random.randint(0, len(drivers) - 1)
                driver_give = random.randint(0, len(drivers) - 1)

            if len(drivers[driver_take].ruta) > 2:
                
                # Posicion que se cambia
                pos_change = random.randint(1, len(drivers[driver_take].ruta) - 2)
                
                # Guardo el punto a cambiar, lo elimino de un driver y lo inserto en otro
                value_change = drivers[driver_take].ruta[pos_change]
                drivers[driver_give].ruta.insert(-1, value_change)
                drivers[driver_take].ruta.pop(pos_change)

                # Entrega nuevas listas con la minima distancia
                bodega = drivers[driver_take].ruta[-1]
                driver_take_coor = drivers[driver_take].ruta[0]
                driver_give_coor = drivers[driver_give].ruta[0]

                # Revisar nueva ruta para el driver que se le quita un ecommerce
                if len(drivers[driver_take].ruta) > 2:
                    route_take = min_route(drivers[driver_take].ruta[1:-1], drivers[driver_take])
                    # Agregamos la direccion del driver y bodega
                    drivers[driver_take].ruta = route_take
                    drivers[driver_take].ruta.insert(0, driver_take_coor)
                    drivers[driver_take].ruta.append(bodega)
                    
                else:
                    route_take = drivers[driver_take].ruta
                
                # Revisar nueva ruta para el driver que se le da un ecommerce
                if len(drivers[driver_give].ruta) > 2: 
                    route_give = min_route(drivers[driver_give].ruta[1:-1], drivers[driver_give])
                    drivers[driver_give].ruta = route_give
                    drivers[driver_give].ruta.insert(0, driver_give_coor)
                    drivers[driver_give].ruta.append(bodega)
                else:
                    route_give = drivers[driver_give].ruta

                # Cambio las lista por las nuevas y elimino las viejas
                drivers[driver_take].ruta = route_take
                drivers[driver_give].ruta = route_give

                new_distance = calculate_distance(drivers)

                if new_distance < best_distance:
                    print('--------------------------')
                    print(f'Mejor distancia ahora {new_distance} antes {best_distance}')
                    print('--------------------------')
                    best_distance = new_distance
                    drivers_copy = deepcopy(drivers)
                else:
                    drivers = deepcopy(drivers_copy)

        except:
            print("El driver ya no tiene ruta")
        

    # -------- Guardamos ruta en TXT ------------
    with open(r'simulation/txt/ruta_ecommerce_mejorada.txt', 'w') as fp:
        for driver in drivers:
            fp.write("%s " % driver.ruta)
            fp.write("\n")
    
    return drivers

def map_distance(drivers):

    coordinate_center = [-33.4369436, -70.634449]

    m = folium.Map(location=(coordinate_center[0], coordinate_center[1]))

    for driver in drivers:
        folium.CircleMarker(driver.origen, color='blue', radius=5, fill=True).add_to(m)

    for i in range(len(drivers)):
        folium.Marker(drivers[i].origen, icon=DivIcon(
                    icon_size=(150,36), icon_anchor=(7,20), html=f'<div style="font-size: 18pt; color : black">{i + 1}</div>',
                    )).add_to(m)
        folium.PolyLine(drivers[i].ruta, color="red", weight=1.5, opacity=1).add_to(m)

    m.save("simulation/maps/ecommerce_improve.html")


def generate_colors(n):
    # Generate color palette for coordinates
    colors = cm.rainbow(np.linspace(0, 1, n))
    colors_new = []
    for el in colors:
        hex = cl.to_hex(el)
        colors_new += [hex]
    return colors_new