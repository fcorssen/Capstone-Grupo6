import gurobipy as gp
from gurobipy import GRB
import numpy as np


numero_puntos = 10
numero_drivers = 2

puntos = range(numero_puntos)
drivers = range(numero_drivers)

# distancia[k][i] indica la distancia del punto inicial de k al punto i
distancia = [[1, 2, 3, 4, 5, 6, 7, 8, 1, 1],
             [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]]


# peso_total_punto[i] indica la suma de todos los pesos de los paquetes en punto i
peso_total_punto = [2, 4, 1, 4, 2, 1, 3, 2, 4, 1]

# peso_total_punto[i] indica la suma de todos los pesos de los paquetes en punto i
volumen_total_punto = [3, 2, 1, 2, 3, 2, 1, 2, 3, 1]

WMAX = 40  # peso maximo por conductor
VMAX = 35  # volumen maximo por conductor
NMIN = 2   # paquetes minimos


## No tocar ##

model = gp.Model()
x = model.addVars(drivers, puntos, vtype=GRB.BINARY)

for k in drivers:
    model.addConstr(gp.quicksum(x[k, i] * volumen_total_punto[i] for i in puntos) <= VMAX)
    model.addConstr(gp.quicksum(x[k, i] * peso_total_punto[i] for i in puntos) <= WMAX)
    model.addConstr(gp.quicksum(x[k, i] for i in puntos) >= 0)

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

    
