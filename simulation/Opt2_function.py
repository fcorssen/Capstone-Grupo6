import geopy.distance

def distance(value1, value2):
    return geopy.distance.geodesic(value1, value2).km

def opt2(tour):
    n = len(tour) - 1
    tour_edges = [(tour[i], tour[i+1]) for i in range(n)]
    improved = True

    while improved:
        
        improved = False
        # range(1, n)
        for i in range(1, n):
            for j in range(i+1, n - 1):
            # for j in range(i+1, n):

                # current node
                cur1 = (tour[i], tour[i+1])
                cur2 = (tour[j], tour[(j+1)%n])
                cur_length = distance(tour[i], tour[i+1]) + distance(tour[j], tour[(j+1)%n])

                # Two new edges for tour
                new1 = (tour[i], tour[j])
                new2 = (tour[i+1], tour[(j+1)%n])
                new_length = distance(tour[i], tour[j]) + distance(tour[i+1], tour[(j+1)%n])

                # Reviso si al cambiar los nodos la distancia es menor
                if new_length < cur_length:
                    # print(f'sawp {cur1} {cur2} with {new1} {new2}')
                    # Los nodos que estan entre los nodos escogicos se invierten
                    tour[i+1:j+1] = tour[i+1:j+1][::-1]
                    tour_edges = [(tour[i], tour[i + 1]) for i in range(n)]
                    improved = True
    return tour

def distance_driver(driver):
    distance = 0
    for j in range(len(driver.ruta)):
        if j != len(driver.ruta) - 1:
            distance += geopy.distance.geodesic(driver.ruta[j], driver.ruta[j+1]).km
    return distance


