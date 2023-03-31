import osmnx as ox
import pandas as pd
import folium
import numpy as np



df_eccomerce = pd.read_excel("datos/e-commerce_data.xlsx", index_col=0)

coordinate_eccomerce = []

for i in range(df_eccomerce['latitude'].size):
    coordinate_eccomerce.append([df_eccomerce['latitude'].iat[i], df_eccomerce['longitude'].iat[i]])

m = folium.Map(location=(coordinate_eccomerce[0][0], coordinate_eccomerce[0][0]))
for cor in coordinate_eccomerce:
        folium.Marker([cor[0], cor[1]], popup="<i>Ecommerce", icon=folium.Icon(color='orange', icon='')).add_to(m)

m.save("maps/eccomerce.html")