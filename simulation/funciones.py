import geopy.distance


def distancia_total(drivers):
    distance = 0
    for i in range(len(drivers)):
        for j in range(len(drivers[i].ruta)):
            if j != len(drivers[i].ruta) - 1:
                distance += geopy.distance.geodesic(drivers[i].ruta[j], drivers[i].ruta[j+1]).km
    return distance


def min_route(ecommerces, driver):
    list_route = ecommerces
    visited = []
    route = []
    distance = 10000000
    for i in range(len(list_route)):
        if list_route[i].id not in visited:
            if driver.peso < 450 and driver.volumen < 2:
                if distance >= geopy.distance.geodesic(driver.origen, list_route[i].ubicacion).km:
                    distance = geopy.distance.geodesic(driver.origen, list_route[i].ubicacion).km
                    ecommerce = list_route[i]
    visited.append(ecommerce.id)
    route.append(ecommerce.ubicacion)


    while len(visited) < len(list_route):
        distance = 1000000
        
        for i in range(len(list_route)):
            if list_route[i].id not in visited:
                if driver.peso < 450 and driver.volumen < 2:
                    if distance >= geopy.distance.geodesic(route[-1], list_route[i].ubicacion).km:
                        distance = geopy.distance.geodesic(route[-1], list_route[i].ubicacion).km
                        ecommerce = list_route[i]
        visited.append(ecommerce.id)
    route.append(ecommerce.ubicacion)
    
    return route

