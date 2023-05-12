from funciones import calculate_distance
import geopy.distance

def distance(value1, value2):
    return geopy.distance.geodesic(value1, value2).km

def cost_change(route, pos1, pos2):
    print(route[pos1])
    print(route[pos2])
    print(route[pos1 + 1])
    print(route[pos2 + 1])
    print(distance(route[pos1], route[pos1 + 1]))
    print(distance(route[pos2], route[pos2 + 1]))
    print(distance(route[pos1 + 1], route[pos2 + 1]))
    print(distance(route[pos1], route[pos2]))
    return ( -distance(route[pos1], route[pos1 + 1]) - distance(route[pos2], route[pos2 + 1]) + 
            distance(route[pos1 + 1], route[pos2 + 1]) + distance(route[pos1], route[pos2]))


def two_opt(route):
    best = route
    improved = True
    while improved:
        improved = False
        for i in range(1, len(route) - 2):
            for j in range(i + 1, len(route) - 1):
                if j - i == 1: continue
                if cost_change(route, i, j) < 0:
                    best[i:j] = best[j - 1:i - 1:-1]
                    improved = True
        route = best
    return best

path = [[-33.42475869783682, -70.61891438686266], [-33.42225103306093, -70.62423686702182],
        [-33.41906417517651, -70.64188176896492], [-33.42371884079868, -70.64125894640664],
         [-33.41804072178575, -70.63004838032934], [-33.41959484504883, -70.63717244522564],
             [-33.42507612353619, -70.64258599831957], [-33.42691073042271, -70.64415831944888], [-33.4539817210464, -70.61069318480818]]

distance1 = 0
for j in range(len(path)):
            if j != len(path) - 1:
                distance1 += geopy.distance.geodesic(path[j], path[j+1]).km
# print(distance1)

# print(cost_change(path, 2, 3))

# print(two_opt(path))
# new_p = two_opt(path)

# distance2 = 0
# for j in range(len(new_p)):
#             if j != len(new_p) - 1:
#                 distance2 += geopy.distance.geodesic(new_p[j], new_p[j+1]).km
# print(distance2)





