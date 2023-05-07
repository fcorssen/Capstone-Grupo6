import pandas as pd
import folium


df_driver = pd.read_excel("datos/driver_origins_data.xlsx", index_col=0)

coordinate_driver = []


for i in range(df_driver['latitude'].size):
    coordinate_driver.append([df_driver['latitude'].iat[i], df_driver['longitude'].iat[i]])

m = folium.Map(location=(coordinate_driver[0][0], coordinate_driver[0][1]))
c = 1
for cor in coordinate_driver:
    if c <= 10:
        folium.Marker([cor[0], cor[1]], popup="<i>Driver: Courier 1</i>", icon=folium.Icon(color='green', icon='')).add_to(m)
    if c > 10:
        folium.Marker([cor[0], cor[1]], popup="<i>Driver: Courier 2</i>", icon=folium.Icon(color='red', icon='')).add_to(m)
    c += 1
m.save("mapsCode/maps/driver.html")