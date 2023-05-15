import geopy.distance
import random
import numpy as np
from copy import deepcopy
import folium
from folium.features import DivIcon
import matplotlib.cm as cm
import matplotlib.colors as cl
import time
from Opt2_function import opt2, distance_driver


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


def improve_route_aleatory(drivers, ecommerces, best_distance):

    drivers_copy = deepcopy(drivers)

    t_end = time.time() + 60 * 2

    while time.time() < t_end:
        try:
            driver_take = random.randint(0, len(drivers) - 1)
            driver_give = random.randint(0, len(drivers) - 1)
            

            # Asegurarse que son distinto drivers
            while driver_take == driver_give:
                driver_take = random.randint(0, len(drivers) - 1)
                driver_give = random.randint(0, len(drivers) - 1)

            if len(drivers[driver_take].ruta) > 4 and len(drivers[driver_give].ruta) < 7:
                
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

                # Actualizo peso y dimension de cada driver
                for e in ecommerces:
                    if e.ubicacion == value_change:
                        peso_change = e.peso
                        volumen_change = e.volumen
                drivers[driver_take].peso -= peso_change
                drivers[driver_take].volumen -= volumen_change
                drivers[driver_take].tiempo -= random.randint(8, 15)
                drivers[driver_give].peso += peso_change
                drivers[driver_give].volumen += volumen_change
                drivers[driver_give].tiempo += random.randint(8, 15)
                
                if drivers[driver_give].peso < 450 and drivers[driver_give].volumen < 2 and drivers[driver_take].peso < 450 and drivers[driver_take].volumen < 2:

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
                # else:
                #     print('No cumple condicion de Peso o Dimension')

        except:
            print("El driver ya no tiene ruta")
        

    # -------- Guardamos ruta en TXT ------------
    with open(r'simulation/txt/ruta_ecommerce_mejorada.txt', 'w') as fp:
        for driver in drivers:
            fp.write("%s " % driver.ruta)
            fp.write("\n")
    
    return drivers


def generate_colors(n):
    # Generate color palette for coordinates
    colors = cm.rainbow(np.linspace(0, 1, n))
    colors_new = []
    for el in colors:
        hex = cl.to_hex(el)
        colors_new += [hex]
    return colors_new


def map_distance(drivers, name):

    coordinate_center = [-33.4369436, -70.634449]

    m = folium.Map(location=(coordinate_center[0], coordinate_center[1]))
    colors = generate_colors(len(drivers))

    for i in range(len(drivers)):
        folium.CircleMarker(drivers[i].origen, color='black', radius=4, fill=True).add_to(m) 
        folium.PolyLine(drivers[i].ruta, color=colors[i], weight=3, opacity=1).add_to(m)

    m.save(name)


def swap_ecommerce(drivers, ecommerces, best_distance):

    drivers_copy = deepcopy(drivers)
    t_end = time.time() + 60 * 5

    while time.time() < t_end:
        try:
            driver1 = random.randint(0, len(drivers) - 1)
            driver2 = random.randint(0, len(drivers) - 1)

            while driver1 == driver2:
                driver1 = random.randint(0, len(drivers) - 1)
                driver2 = random.randint(0, len(drivers) - 1)
            
            pos_change1 = random.randint(1, len(drivers[driver1].ruta) - 2)
            pos_change2 = random.randint(1, len(drivers[driver2].ruta) - 2)

            value_change1 = drivers[driver1].ruta[pos_change1]
            value_change2 = drivers[driver2].ruta[pos_change2]

            drivers[driver1].ruta.remove(value_change1)
            drivers[driver2].ruta.remove(value_change2)

            drivers[driver1].ruta.insert(-1, value_change2)
            drivers[driver2].ruta.insert(-1, value_change1)


            for e in ecommerces:
                if e.ubicacion == value_change1:
                    peso_change1 = e.peso
                    volumen_change1 = e.volumen
                elif e.ubicacion == value_change2:
                    peso_change2 = e.peso
                    volumen_change2 = e.volumen
            drivers[driver1].peso -= peso_change1
            drivers[driver1].volumen -= volumen_change1
            drivers[driver2].peso += peso_change2
            drivers[driver2].volumen += volumen_change2

            if drivers[driver1].peso < 450 and drivers[driver1].volumen < 2 and drivers[driver2].peso < 450 and drivers[driver2].volumen < 2:

                cur_distance1 = distance_driver(drivers[driver1])
                new_distance1 = distance_driver(drivers[driver1])
                if new_distance1 < cur_distance1:
                    driver1.ruta = opt2(drivers[driver1].ruta)
                
                cur_distance2 = distance_driver(drivers[driver2])
                new_distance2 = distance_driver(drivers[driver2])
                if new_distance2 < cur_distance2:
                    driver2.ruta = opt2(drivers[driver2].ruta)
                
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
    with open(r'simulation/txt/ruta_ecommerce_swap.txt', 'w') as fp:
        for driver in drivers:
            fp.write("%s " % driver.ruta)
            fp.write("\n")
    
    return drivers


def vecindad(ecommerces):
    for e in ecommerces:
        while len(e.vecindad) < 5:
            min_dis = 100000
            for i in range(len(ecommerces)):
                if e != ecommerces[i]:
                    if ecommerces[i] not in e.vecindad:
                        if min_dis >= geopy.distance.geodesic(e.ubicacion, ecommerces[i].ubicacion).km:
                            min_dis = geopy.distance.geodesic(e.ubicacion, ecommerces[i].ubicacion).km
                            ecom_add = ecommerces[i]
            e.vecindad.append(ecom_add)


def improve_route(drivers, ecommerces, best_distance):

    drivers_copy = deepcopy(drivers)

    t_end = time.time() + 60 * 1.5

    while time.time() < t_end:
        try:
            
            list_take = []
            for d in drivers:
                max_dis = 0
                if d not in list_take and len(list_take) < 5:
                    if max_dis < distance_driver(d):
                        list_take.append(d)
            list_give = []

            for d in drivers:
                min_dis = 10000
                if d not in list_give and len(list_give) < 8:
                    if min_dis > distance_driver(d):
                        list_give.append(d)

            driver_give = random.choice(list_give)
            driver_take = random.choice(list_take)
            

            # Asegurarse que son distinto drivers
            while driver_take == driver_give:
                # driver_take = random.randint(0, len(drivers) - 1)
                driver_give = random.choice(list_give)

            if len(driver_take.ruta) > 4 and len(driver_give.ruta) <= 8:
                
                # Posicion que se cambia
                pos_change = random.randint(1, len(driver_take.ruta) - 2)
                
                # Guardo el punto a cambiar, lo elimino de un driver y lo inserto en otro
                value_change = driver_take.ruta[pos_change]
                driver_give.ruta.insert(-1, value_change)
                driver_take.ruta.pop(pos_change)
                

                # Entrega nuevas listas con la minima distancia
                bodega = driver_take.ruta[-1]
                driver_take_coor = driver_take.ruta[0]
                driver_give_coor = driver_give.ruta[0]


                # Actualizo peso y dimension de cada driver
                for e in ecommerces:
                    if e.ubicacion == value_change:
                        peso_change = e.peso
                        volumen_change = e.volumen
                driver_take.peso -= peso_change
                driver_take.volumen -= volumen_change
                driver_take.tiempo -= random.randint(8, 15)
                driver_give.peso += peso_change
                driver_give.volumen += volumen_change
                driver_give.tiempo += random.randint(8, 15)
                
                if driver_give.peso < 450 and driver_give.volumen < 2 and driver_take.peso < 450 and driver_take.volumen < 2:

                    # Revisar nueva ruta para el driver que se le quita un ecommerce
                    if len(driver_take.ruta) > 2:
                        route_take = min_route(driver_take.ruta[1:-1], driver_take)
                        # Agregamos la direccion del driver y bodega
                        driver_take.ruta = route_take
                        driver_take.ruta.insert(0, driver_take_coor)
                        driver_take.ruta.append(bodega)
                        
                    else:
                        route_take = driver_take.ruta
                    
                    # Revisar nueva ruta para el driver que se le da un ecommerce
                    if len(driver_give.ruta) > 2: 
                        route_give = min_route(driver_give.ruta[1:-1], driver_give)
                        driver_give.ruta = route_give
                        driver_give.ruta.insert(0, driver_give_coor)
                        driver_give.ruta.append(bodega)
                    else:
                        route_give = driver_give.ruta

                    # Cambio las lista por las nuevas y elimino las viejas
                    driver_take.ruta = route_take
                    driver_give.ruta = route_give

                    new_distance = calculate_distance(drivers)

                    if new_distance < best_distance:
                        print('--------------------------')
                        print(f'Mejor distancia ahora {new_distance} antes {best_distance}')
                        print('--------------------------')
                        best_distance = new_distance
                        drivers_copy = deepcopy(drivers)
                    else:
                        drivers = deepcopy(drivers_copy)
                # else:
                #     print('No cumple condicion de Peso o Dimension')

        except:
            print("El driver ya no tiene ruta")
        

    # # -------- Guardamos ruta en TXT ------------
    # with open(r'simulation/txt/ruta_ecommerce_mejorada.txt', 'w') as fp:
    #     for driver in drivers:
    #         fp.write("%s " % driver.ruta)
    #         fp.write("\n")
    
    return drivers
