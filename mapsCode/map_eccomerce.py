import pandas as pd
import folium
from folium.features import DivIcon


df_eccomerce = pd.read_excel("datos/e-commerce_data.xlsx", index_col=0)

coordinate_eccomerce = []

for i in range(df_eccomerce['latitude'].size):
    coordinate_eccomerce.append([df_eccomerce['latitude'].iat[i], df_eccomerce['longitude'].iat[i]])

m = folium.Map(location=(coordinate_eccomerce[0][0], coordinate_eccomerce[0][0]))
i = 0
for cor in coordinate_eccomerce:
        # folium.Marker([cor[0], cor[1]], popup="<i>{i}", icon=folium.Icon(color='orange', icon='')).add_to(m)
        folium.Marker([cor[0], cor[1]], icon=DivIcon(
        icon_size=(150,36), icon_anchor=(7,20), html=f'<div style="font-size: 18pt; color : black">{i + 1}</div>',
        )).add_to(m)
        i+=1
m.save("mapsCode/maps/eccomerce.html")