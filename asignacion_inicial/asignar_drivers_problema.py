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
NMIN = 4   # paquetes minimos
NMAX = 8   # paquetes maximos


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


asignacion = {}
for driver in drivers:
    asignacion[driver] = []
    for punto in puntos:
        if x[driver, punto].X == 1:
            asignacion[driver].append(punto)

print(asignacion)
