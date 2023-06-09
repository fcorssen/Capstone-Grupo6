import pandas as pd
import random
import geopy.distance

import gurobipy as gp
from gurobipy import GRB

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

lista_volumen = df_delivery['dimensiones'].tolist()
lista_peso = df_delivery['weight (kg)'].tolist()


# Cantidad de Drivers y Ecommerces
numero_puntos = df_delivery['longitude'].size
numero_drivers = df_driver['longitude'].size

puntos = range(numero_puntos)
drivers = range(numero_drivers)

# Distancia entre punto de inicio de cada driver y ecommerce
distancia = []


list_drivers = df_driver[['latitude', 'longitude']].values.tolist()
list_delivery = df_delivery[['latitude', 'longitude']].values.tolist()

for pos_driver in list_drivers:
    lista_dis = []
    for pos_delivery in list_delivery:
        lista_dis.append(geopy.distance.geodesic(pos_driver, pos_delivery).km)
    distancia.append(lista_dis)


WMAX = 450  # peso maximo por conductor
VMAX = 2  # volumen maximo por conductor
NMIN = 25   # paquetes minimos
NMAX = 60   # paquetes maximos


## No tocar ##

model = gp.Model()
x = model.addVars(drivers, puntos, vtype=GRB.BINARY)

for k in drivers:
    model.addConstr(gp.quicksum(x[k, i] * lista_volumen[i] for i in puntos) <= VMAX)
    model.addConstr(gp.quicksum(x[k, i] * lista_peso[i] for i in puntos) <= WMAX)
    model.addConstr(gp.quicksum(x[k, i] for i in puntos) >= NMIN)
    model.addConstr(gp.quicksum(x[k, i] for i in puntos) <= NMAX)

for i in puntos:
    model.addConstr(gp.quicksum(x[k, i] for k in drivers) == 1)

model.setObjective(gp.quicksum(x[k, i] * distancia[k][i] for k in drivers for i in puntos), GRB.MINIMIZE)


model.update()


model.optimize()


asignacion = {}
for driver in drivers:
    asignacion[driver] = []
    for punto in puntos:
        if x[driver, punto].X == 1:
            asignacion[driver].append(punto)

print(asignacion)
