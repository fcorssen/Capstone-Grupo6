import pandas as pd
import folium
import numpy as np
from folium.features import DivIcon
import random
from folium.plugins import MarkerCluster


df = pd.read_excel("datos/deliveries_data.xlsx", index_col=0)

# Renombrar las columnas
df.rename(columns = {'x2 (ancho en cm)':'ancho', 'x3 (alto en cm)':'alto', 
                     'x1 (largo en cm)':'largo', 'weight (kg)':'peso'}, inplace = True)

# Creamos una columna que son las dimensiones en m3
df['dimensiones'] = df['largo']/100 * df['ancho']/100 * df['alto']/100 

# ------------- Separar por dias --------------
days = []
amountDays = []

for i in range(df['delivery_day'].size):
    days.append(df['delivery_day'].iat[i].day)

for i in range(30):
    value = days.count(i + 1)
    amountDays.append(value)

# ------------------------------
peso = 0
print(amountDays[1])
print(len(df['peso'][amountDays[0]:amountDays[1] + 1]))
# for i in range(len(df['peso'][amountDays[1]])):
#     peso += df['peso'][amountDays[0]:amountDays[1]].iloc[i]

# print(peso)