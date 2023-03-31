import osmnx as ox
import pandas as pd
import folium
import numpy as np



df_center = pd.read_excel("datos/centers_data.xlsx", index_col=0)

coordinate_center = []

for i in range(df_center['latitude'].size):
    coordinate_center.append([df_center['latitude'].iat[i], df_center['longitude'].iat[i]])

m = folium.Map(location=(coordinate_center[0][0], coordinate_center[0][1]))
for cor in coordinate_center:
        folium.Marker([cor[0], cor[1]], popup="<i>Center</i>", icon=folium.Icon(color='lightblue', icon='')).add_to(m)

m.save("maps/center.html")