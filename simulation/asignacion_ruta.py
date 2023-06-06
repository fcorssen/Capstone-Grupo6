import pandas as pd
import random
import geopy.distance
import math

from clases import Driver, Paquete, Ecommerce, Centro

import gurobipy as gp
from gurobipy import GRB

import networkx as nx
import matplotlib.pyplot as plt

from funciones import calculate_distance, time_drivers, map_distance
from Opt2_function import opt2, distance_driver

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

df_delivery = df_delivery[:amountDays[0]]



# Creamos una columna que son las dimensiones en m3
df_delivery['dimensiones'] = df_delivery['x1 (largo en cm)']/100 * df_delivery['x2 (ancho en cm)']/100 * df_delivery['x3 (alto en cm)']/100 

# ------ Craer dataframe con suma de dimensiones y peso
df_dim = df_delivery.groupby('e-commerce_id').agg({'dimensiones': ['count', 'sum'], 'weight (kg)': 'sum'})
df_dim.columns = ['count', 'dimension', 'weight']
list_dim = df_dim.values.tolist()

# Creamos lista con peso y volumen ecommerces
peso_total_punto = []
volumen_total_punto = []
for count, volumen, peso in list_dim:
    peso_total_punto.append(peso)
    volumen_total_punto.append(volumen)

# Cantidad de Drivers y Ecommerces
numero_puntos = df_ecommerce['longitude'].size
numero_drivers = df_driver['longitude'].size

puntos = range(numero_puntos)
drivers = range(numero_drivers)

# Distancia entre punto de inicio de cada driver y ecommerce
distancia = []

list_drivers = df_driver[['latitude', 'longitude']].values.tolist()
list_ecommerces = df_ecommerce[['latitude', 'longitude']].values.tolist()

for pos_driver in list_drivers:
    lista_dis = []
    for pos_ecommerce in list_ecommerces:
        lista_dis.append(geopy.distance.geodesic(pos_driver, pos_ecommerce).km)
    distancia.append(lista_dis)


WMAX = 450  # peso maximo por conductor
VMAX = 2  # volumen maximo por conductor
NMIN = 5   # paquetes minimos
NMAX = 7   # paquetes maximos


## No tocar ##

model = gp.Model()
x = model.addVars(drivers, puntos, vtype=GRB.BINARY)

for k in drivers:
    model.addConstr(gp.quicksum(x[k, i] * volumen_total_punto[i] for i in puntos) <= VMAX)
    model.addConstr(gp.quicksum(x[k, i] * peso_total_punto[i] for i in puntos) <= WMAX)
    model.addConstr(gp.quicksum(x[k, i] for i in puntos) >= NMIN)
    model.addConstr(gp.quicksum(x[k, i] for i in puntos) <= NMAX)

for i in puntos:
    model.addConstr(gp.quicksum(x[k, i] for k in drivers) == 1)

model.setObjective(gp.quicksum(x[k, i] * distancia[k][i] for k in drivers for i in puntos), GRB.MINIMIZE)


model.update()


model.optimize()



# Instanciamos las clases

# ---------- Instanciar los centros ---------- 
lista_centros = []
for i in range(df_center['id'].size):
    centro = Centro(df_center['id'].iat[i], [df_center['latitude'].iat[i], df_center['longitude'].iat[i]])
    lista_centros.append(centro)

# ---------- Instanciar los drivers ---------- 
lista_drivers = []
for i in range(df_driver['id'].size):
    d = Driver(df_driver['id'].iat[i], [df_driver['latitude'].iat[i], df_driver['longitude'].iat[i]])
    lista_drivers.append(d)

# ---------- Instanciar los ecommerce ---------- 
lista_ecommerces = []
for i in range(df_ecommerce['id'].size):
    ecommerce = Ecommerce(df_ecommerce['id'].iat[i], [df_ecommerce['latitude'].iat[i], df_ecommerce['longitude'].iat[i]])
    lista_ecommerces.append(ecommerce)

# ----------  Instanciar los paquetes ---------- 
lista_paquetes = []
for i in range(df_delivery['id'].size):
    paquete = Paquete(df_delivery['id'].iat[i], df_delivery['weight (kg)'].iat[i], [df_delivery['latitude'].iat[i], df_delivery['longitude'].iat[i]], df_delivery['x1 (largo en cm)'].iat[i], df_delivery['x2 (ancho en cm)'].iat[i], df_delivery['x3 (alto en cm)'].iat[i], df_delivery['delivery_day'].iat[i].day, df_delivery['e-commerce_id'].iat[i])
    lista_paquetes.append(paquete)

# ---------- Paquetes dia 1 ----------
paquetes_dia_1 = lista_paquetes[:amountDays[0]]   

# ---------- Agregar paquetes a los ecommerce para el dia 1 ----------
for paquete in paquetes_dia_1:
    for ecommerce in lista_ecommerces:
        if paquete.ecommerce == ecommerce.id:
            ecommerce.agregar_paquete(paquete)



# Agregamos los ecommmerce a la ruta de los drivers

for i in range(len(lista_drivers)):
    for punto in puntos:
        if x[i, punto].X == 1:
            lista_drivers[i].agregar_ecommerce(lista_ecommerces[punto])
    lista_drivers[i].ruta.append(lista_centros[-1].ubicacion)
    lista_drivers[i].ruta.insert(0, lista_drivers[i].origen)

print()
print(lista_drivers[5].ruta)
print()
n = len(lista_drivers[5].ruta)
G = nx.complete_graph(n, nx.DiGraph())

my_pos = { i : ( lista_drivers[5].ruta[i][0], lista_drivers[5].ruta[i][1] ) for i in G.nodes } 

for i,j in G.edges:
    (x1,y1) = my_pos[i]
    (x2,y2) = my_pos[j]
    G.edges[i,j]['length'] = math.sqrt( (x1-x2)**2 + (y1-y2)**2 )


m = gp.Model()
x = m.addVars(G.edges,vtype=GRB.BINARY)

m.setObjective( gp.quicksum( G.edges[i,j]['length'] * x[i,j] for i,j in G.edges ), GRB.MINIMIZE )

# Enter each city once
m.addConstrs( gp.quicksum( x[i,j] for i in G.predecessors(j) ) == 1 for j in G.nodes if j != 0)
m.addConstrs( gp.quicksum( x[i,j] for i in G.predecessors(j) ) == 0 for j in G.nodes if j == 0)

# Leave each city once
m.addConstrs( gp.quicksum( x[i,j] for j in G.successors(i) ) == 1 for i in G.nodes if i != n-1)
m.addConstrs( gp.quicksum( x[i,j] for j in G.successors(i) ) == 0 for i in G.nodes if i == n-1)

u = m.addVars( G.nodes )

m.addConstrs( u[i] - u[j] + (n-1) * x[i,j] + (n-3) * x[j,i] <= n-2 for i,j in G.edges if j != 0 if (i,j) in G.edges)

m.optimize()

tour_edges = [ e for e in G.edges if x[e].x > 0.5 ]
nx.draw(G.edge_subgraph(tour_edges), pos=my_pos)
plt.show()



# print()

# for d in lista_drivers:
#     d.ruta = opt2(d.ruta)

# lista_drivers = time_drivers(lista_drivers)
# for d in lista_drivers:
#     dis = distance_driver(d)
#     print(f'Distancia {dis} ---- Tiempo {d.tiempo} ---- N Paquetes {len(d.ruta) - 2}')


# map_distance(lista_drivers, 'simulation/maps/asignacionGurobi.html')