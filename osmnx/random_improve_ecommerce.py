import geopy.distance
import pandas as pd
import osmnx as ox
import networkx as nx
import random
import itertools
import folium
from folium.features import DivIcon
from copy import deepcopy

random.seed(343545)

route_drivers_ecommerce = [
    [[-33.42475869783682, -70.61891438686266], [-33.42225103306093, -70.62423686702182], [-33.41804072178575, -70.63004838032934], [-33.41959484504883, -70.63717244522564], [-33.41906417517651, -70.64188176896492], [-33.42371884079868, -70.64125894640664], [-33.42507612353619, -70.64258599831957], [-33.42691073042271, -70.64415831944888], [-33.4539817210464, -70.61069318480818]],
    [[-33.45722836021753, -70.62438544407914], [-33.45300814597829, -70.62300812423292], [-33.44472149190693, -70.62222263019136], [-33.43536241228873, -70.63107898015966], [-33.43354910513401, -70.62734062089002], [-33.42941631825704, -70.62153410752785], [-33.42705967739409, -70.63248278616064], [-33.43451020093692, -70.64076610696773], [-33.4539817210464, -70.61069318480818]],
    [[-33.46013666537667, -70.62931733834137], [-33.46296153651627, -70.64126370220644], [-33.46897788151509, -70.63975194749847], [-33.47204426156802, -70.6395023423376], [-33.46935673947043, -70.64885867101242], [-33.47377070155471, -70.6627205089658], [-33.47653747259751, -70.6648393967031], [-33.48164142462833, -70.65482679504186], [-33.4539817210464, -70.61069318480818]],
    [[-33.4634739471992, -70.65173974688014], [-33.45675463531489, -70.64457749554776], [-33.44777992030463, -70.65402717921269], [-33.44255523923142, -70.66273985880713], [-33.44545612858779, -70.66843349034228], [-33.44279270425711, -70.6729228991528], [-33.44766500516289, -70.6752172599372], [-33.46039773073053, -70.67398694026748], [-33.4539817210464, -70.61069318480818]],
    [[-33.4133469072509, -70.65980346442899], [-33.41016826706196, -70.66344354190433], [-33.40612571206832, -70.67199957579226], [-33.40347661398336, -70.67358753877849], [-33.41478272146048, -70.6742437135735], [-33.41496462548562, -70.6731067333152], [-33.41766240678623, -70.67690725199964], [-33.41674155884687, -70.67944684094084], [-33.4539817210464, -70.61069318480818]],
    [[-33.45653392572637, -70.67544164389567], [-33.44522815834824, -70.69205562009128], [-33.44350646609591, -70.69390004498842], [-33.43816671587052, -70.68849544071024], [-33.43703424767286, -70.68493135713516], [-33.42277433459014, -70.67880556422887], [-33.42002884942843, -70.68485811750296], [-33.41443943634508, -70.68738264601713], [-33.4539817210464, -70.61069318480818]],
    [[-33.47143247178571, -70.61119989509753], [-33.49179685621576, -70.59517011891866], [-33.51362555647748, -70.58652885085768], [-33.56347864815567, -70.56050612499578], [-33.55281227134447, -70.66815747530303], [-33.52132423783303, -70.667832719485], [-33.51015932387511, -70.66037629317103], [-33.47258488163212, -70.68588283495964], [-33.4539817210464, -70.61069318480818]],
    [[-33.47865877907687, -70.64883335191256], [-33.4359600497046, -70.65382735061853], [-33.43461615917355, -70.6575511430273], [-33.43175178187915, -70.65847697847583], [-33.43314103093541, -70.66283437796147], [-33.42393744312063, -70.66329651644179], [-33.42574811057705, -70.6473484454851], [-33.41015098235179, -70.64057440015769], [-33.4539817210464, -70.61069318480818]],
    [[-33.4547994230244, -70.68177856856285], [-33.44131893637633, -70.70875807480459], [-33.42972331002353, -70.71702247619181], [-33.42389055938657, -70.71529153808049], [-33.42714952781416, -70.72358069130146], [-33.41172351784213, -70.73535204314098], [-33.40287427577779, -70.75911556209257], [-33.37921008584436, -70.75040888558641], [-33.4539817210464, -70.61069318480818]],
    [[-33.39966089929759, -70.6842984482419], [-33.39621398184207, -70.69356608627393], [-33.4104245282393, -70.69122758657889], [-33.41155714921368, -70.69624488379604], [-33.41999584236511, -70.70309171315336], [-33.40663129690812, -70.70903832605143], [-33.41484105662393, -70.67948895981704], [-33.41510871738915, -70.67919429954803], [-33.4539817210464, -70.61069318480818]],
    [[-33.40305370397851, -70.56314652160252], [-33.40520156005478, -70.5782452221826], [-33.40596600611256, -70.5922301943772], [-33.39638237927585, -70.60916095361034], [-33.3881622792935, -70.61198011629779], [-33.4539817210464, -70.61069318480818]],
    [[-33.47203031583582, -70.72389642030014], [-33.46870555407397, -70.71461401604897], [-33.54652694767388, -70.71945727408685], [-33.57557822073572, -70.73218574230273], [-33.45433606120825, -70.58555386524164], [-33.4539817210464, -70.61069318480818]],
    [[-33.37556001890029, -70.53998268769418], [-33.38946739734604, -70.59903888960336], [-33.41043552087503, -70.61599240287983], [-33.40753788433872, -70.62534312784236], [-33.4106915933427, -70.62919746252082], [-33.4539817210464, -70.61069318480818]],
    [[-33.34920223485847, -70.69221188547029], [-33.3512090204138, -70.68431301345639], [-33.3371310413377, -70.70265134737791], [-33.32238615870009, -70.71855257404529], [-33.29180024577838, -70.68971246279766], [-33.4539817210464, -70.61069318480818]],
    [[-33.56015803680171, -70.59316542172161], [-33.45311159946192, -70.5544374228378], [-33.42703703597657, -70.57993168269843], [-33.43336047747307, -70.60619302530729], [-33.4194025395777, -70.60645706294905], [-33.4539817210464, -70.61069318480818]],
    [[-33.51034443414655, -70.77580774678871], [-33.40631224916182, -70.65374228536189], [-33.40658158417009, -70.644099508857], [-33.39820692720235, -70.64349718484715], [-33.39765943103141, -70.64560259170514], [-33.4539817210464, -70.61069318480818]],
    [[-33.57125040135713, -70.56995081110463], [-33.40913937319159, -70.6307756375712], [-33.39566969010603, -70.64718196630001], [-33.3906616343177, -70.65618253716687], [-33.37661615187089, -70.66077264744143], [-33.4539817210464, -70.61069318480818]],
    [[-33.59470558033697, -70.70209182052085], [-33.37975999558638, -70.63581892182225], [-33.34537910208673, -70.63071147700214], [-33.32761600207031, -70.6096126339093], [-33.27097821915391, -70.68667313279227], [-33.4539817210464, -70.61069318480818]],
]

def calculate_distance(list_route):
    distance = 0
    for k in range(len(list_route)):
        plot = list_route[k]
        for i in range(len(plot)):
            if i != len(plot)-1:
                distance += geopy.distance.geodesic(plot[i], plot[i+1]).km
    return distance

def min_route(list_r, driver):
    list_route = list_r
    visited = []
    route = []
    node_visited = []
    pos = 0
    distance = 10000000
    # driver = list_route[0]
    # bodega = list_route[-1]
    # list_route.pop(0)
    # list_route.pop(-1)

    # route.append(driver)
    for i in range(len(list_route)):
        if distance >= geopy.distance.geodesic(driver, [list_route[i][0], list_route[i][1]]).km:
            distance = geopy.distance.geodesic(driver, [list_route[i][0], list_route[i][1]]).km
            pos = i
    visited.append(list_route[pos][0])
    list_route[pos][0]
    node_visited.append(pos)
    route.append(list_route[pos])


    while len(visited) < len(list_route):
        distance = 1000000
        
        for i in range(len(list_route)):
            if list_route[i][0] not in visited:
                if distance >= geopy.distance.geodesic([list_route[node_visited[-1]][0], list_route[node_visited[-1]][1]], [list_route[i][0], list_route[i][1]]).km:
                    distance = geopy.distance.geodesic([list_route[node_visited[-1]][0], list_route[node_visited[-1]][1]], [list_route[i][0], list_route[i][1]]).km
                    pos = i
        visited.append(list_route[pos][0])
        route.append(list_route[pos])
        node_visited.append(pos)

    # route.append(bodega)
    return route



# Guardo la mejor ruta y distancia
route_drivers_ecommerce_best =deepcopy(route_drivers_ecommerce)
best_distance = calculate_distance(route_drivers_ecommerce)


for i in range(10000):
    
    try:
        driver_take = random.randint(0, len(route_drivers_ecommerce) - 1)
        driver_give = random.randint(0, len(route_drivers_ecommerce) - 1)

        # Asegurarse que son distinto drivers
        while driver_take == driver_give:
            driver_take = random.randint(0, len(route_drivers_ecommerce) - 1)
            driver_give = random.randint(0, len(route_drivers_ecommerce) - 1)


        if len(route_drivers_ecommerce[driver_take]) > 2:
            
            # Posicion que se cambia
            pos_change = random.randint(1, len(route_drivers_ecommerce[driver_take]) - 2)

            # Guardo el punto a cambiar, lo elimino de un driver y lo inserto en otro
            value_change = route_drivers_ecommerce[driver_take][pos_change]
            route_drivers_ecommerce[driver_give].insert(-1, value_change)
            route_drivers_ecommerce[driver_take].pop(pos_change)

        #     # Entrega nuevas listas con la minima distancia
            bodega = route_drivers_ecommerce[driver_take][-1]
            driver_take_coor = route_drivers_ecommerce[driver_take][0]
            driver_give_coor = route_drivers_ecommerce[driver_give][0]

            if len(route_drivers_ecommerce[driver_take][1:-1]) > 2:
                route_take = min_route(route_drivers_ecommerce[driver_take][1:-1], driver_take_coor)
                # Agregamos la direccion del driver y bodega
                route_take.insert(0, driver_take_coor)
                route_take.append(bodega)
            else:
                route_take = route_drivers_ecommerce[driver_take]
            if len(route_drivers_ecommerce[driver_give][1:-1]) > 2: 
                route_give = min_route(route_drivers_ecommerce[driver_give][1:-1], driver_give_coor)
                route_give.insert(0, driver_give_coor)
                route_give.append(bodega)
            else:
                route_give = route_drivers_ecommerce[driver_give]
        
            # Cambio las lista por las nuevas y elimino las viejas
            route_drivers_ecommerce.pop(driver_take)
            route_drivers_ecommerce.insert(driver_take, route_take)
            route_drivers_ecommerce.pop(driver_give) 
            route_drivers_ecommerce.insert(driver_give, route_give)

            new_distance = calculate_distance(route_drivers_ecommerce)

            if new_distance <= best_distance:
                print('--------------------------')
                print(f'Mejor distancia ahora {new_distance} antes {best_distance}')
                print('--------------------------')
                best_distance = new_distance
                route_drivers_ecommerce_best = deepcopy(route_drivers_ecommerce)
            else:
                route_drivers_ecommerce = deepcopy(route_drivers_ecommerce_best)

    except:
        print("El driver ya no tiene ruta")


print(best_distance)

# Escribo en txt
with open(r'osmnx/txt/ruta_ecommerce_VEERR.txt', 'w') as fp:
    for k in range(len(route_drivers_ecommerce)):
        plot = route_drivers_ecommerce[k]
        for route in plot:
            fp.write("%s " % route)
        fp.write("\n")

coordinate_center = [-33.4369436, -70.634449]
# Creamos mapa
m = folium.Map(location=(coordinate_center[0], coordinate_center[1]))
folium.CircleMarker(coordinate_center, color='red', radius=5, fill=True).add_to(m)

for k in range(len(route_drivers_ecommerce_best)):
    plot = route_drivers_ecommerce_best[k]
    folium.PolyLine(plot, color="red", weight=1.5, opacity=1).add_to(m)

m.save("osmnx/maps/linea_recta_ecommerce_mejorado.html")