import networkx as nx
import random
import matplotlib.pyplot as plt
import math
import gurobipy as gp
from gurobipy import GRB
import pandas as pd
from clases import Driver, Paquete, Ecommerce, Centro


# # ------------------- CARGAR DATOS ----------
# # ------------- Cargar los datos --------------

# df_delivery = pd.read_excel("datos/deliveries_data.xlsx")
# df_driver = pd.read_excel("datos/driver_origins_data.xlsx")
# df_center = pd.read_excel("datos/centers_data.xlsx")
# df_ecommerce = pd.read_excel("datos/e-commerce_data.xlsx")


# # # ------------- Separar por dias --------------
# days = []
# amountDays = []

# for i in range(df_delivery['delivery_day'].size):
#     days.append(df_delivery['delivery_day'].iat[i].day)

# for i in range(30):
#     value = days.count(i + 1)
#     amountDays.append(value)

# # ---------- Instanciar los centros ---------- 
# centros = []
# for i in range(df_center['id'].size):
#     centro = Centro(df_center['id'].iat[i], [df_center['latitude'].iat[i], df_center['longitude'].iat[i]])
#     centros.append(centro)

# # ---------- Instanciar los drivers ---------- 
# drivers = []
# for i in range(df_driver['id'].size):
#     driver = Driver(df_driver['id'].iat[i], [df_driver['latitude'].iat[i], df_driver['longitude'].iat[i]])
#     drivers.append(driver)

# # ---------- Instanciar los ecommerce ---------- 
# ecommerces = []
# for i in range(df_ecommerce['id'].size):
#     ecommerce = Ecommerce(df_ecommerce['id'].iat[i], [df_ecommerce['latitude'].iat[i], df_ecommerce['longitude'].iat[i]])
#     ecommerces.append(ecommerce)


# ----------- RESOLVER PROBLEMA --------------------

k = 4       # number of vehicles
n = 20      # number of demand points

depot = 0                       
dem_points = list(range(1,n+1)) # nodes 1, 2, ..., 20


G = nx.complete_graph(n+1,nx.DiGraph())

my_pos = { i : ( random.random(), random.random() ) for i in dem_points } # pos[i] = (x_i, y_i)

# let's locate the depot in the middle
my_pos[depot] = (0.5, 0.5)

# nx.draw(G, pos=my_pos)


def eucl_dist(x1,y1,x2,y2):
    return math.sqrt( (x1-x2)**2 + (y1-y2)**2 )

for i,j in G.edges:
    (x1,y1) = my_pos[i]
    (x2,y2) = my_pos[j]
    G.edges[i,j]['length'] = eucl_dist(x1,y1,x2,y2)

# suppose each vehicle has capacity 100
Q = 100

# suppose each demand point has demand 20
q = { i : 20 for i in dem_points }

# First, solve a relaxation

m = gp.Model()
x = m.addVars(G.edges,vtype=GRB.BINARY)

m.setObjective( gp.quicksum( G.edges[i,j]['length'] * x[i,j] for i,j in G.edges ), GRB.MINIMIZE )

# Enter each demand point once
m.addConstrs( gp.quicksum( x[i,j] for i in G.predecessors(j) ) == 1 for j in dem_points )

# Leave each demand point once
m.addConstrs( gp.quicksum( x[i,j] for j in G.successors(i) ) == 1 for i in dem_points )

# Leave the depot k times
m.addConstr( gp.quicksum( x[depot,j] for j in G.successors(depot) ) == k )

m.optimize()

# get the solution and draw it
tour_edges = [ e for e in G.edges if x[e].x > 0.5 ]
# nx.draw(G.edge_subgraph(tour_edges), pos=my_pos)

# Add the MTZ variables and constraints, and solve
u = m.addVars( G.nodes )

u[depot].LB = 0
u[depot].UB = 0

for i in dem_points:
    u[i].LB = q[i]
    u[i].UB = Q

c = m.addConstrs( u[i] - u[j] + Q * x[i,j] <= Q - q[j] for i,j in G.edges if j != depot )

# m.optimize()

# Try again, using stronger ("lifted") version of these constraints

m.remove(c)  # remove the previous MTZ constraints
q[depot] = 0
m.addConstrs( u[i] - u[j] + Q * x[i,j] + ( Q - q[i] - q[j] ) * x[j,i] <= Q - q[j] for i,j in G.edges if j != depot )

m.reset()    # start solve process from scratch
m.optimize()

# get the solution and draw it
tour_edges = [ e for e in G.edges if x[e].x > 0.5 ]
nx.draw(G.edge_subgraph(tour_edges), pos=my_pos)
plt.show()
