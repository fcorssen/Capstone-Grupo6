import pandas as pd
import folium
from folium.features import DivIcon
import random
from folium.plugins import MarkerCluster


df = pd.read_excel("datos/deliveries_data.xlsx", index_col=0)
df_driver = pd.read_excel("datos/driver_origins_data.xlsx", index_col=0)
df_center = pd.read_excel("datos/centers_data.xlsx", index_col=0)
df_eccomerce = pd.read_excel("datos/e-commerce_data.xlsx", index_col=0)

coordinate_eccomerce = []
coordinate_center = []
coordinate_driver = []
coordinate = []

# ------------- Separar por dias --------------
days = []
amountDays = []

for i in range(df['delivery_day'].size):
    days.append(df['delivery_day'].iat[i].day)

for i in range(30):
    value = days.count(i + 1)
    amountDays.append(value)


# -------- ADD LOCATON DELIVERY --------
locations = list(zip(df['latitude'], df['longitude']))
m = folium.Map(location=(df['latitude'].iat[0], df['longitude'].iat[0]))

# for i in range(len(locations)):
#     folium.CircleMarker(location=locations[i],radius=1).add_to(m)

# cluster = folium.FeatureGroup(name='cluster')
# cluster.add_child(MarkerCluster(locations=locations[:amountDays[0]]))  
# m.add_child(cluster)


# ----- ADD DRIVERS ------
for i in range(df_driver['latitude'].size):
    coordinate_driver.append([df_driver['latitude'].iat[i], df_driver['longitude'].iat[i]])

# c = 0

# for cor in coordinate_driver:
#     if c < 10:
#         folium.CircleMarker([cor[0], cor[1]], color='green', radius=8, fill=True).add_to(m)
#     if c >= 10:
#         folium.CircleMarker([cor[0], cor[1]], color='red', radius=8, fill=True).add_to(m)
#     c += 1


# ------- ADD CENTER --------

for i in range(df_center['latitude'].size):
    coordinate_center.append([df_center['latitude'].iat[i], df_center['longitude'].iat[i]])

for cor in coordinate_center:
        folium.CircleMarker([cor[0], cor[1]], color='blue', radius=10, fill=True).add_to(m)



#  ------- ADD ECCOMERCE --------
for i in range(df_eccomerce['latitude'].size):
    coordinate_eccomerce.append([df_eccomerce['latitude'].iat[i], df_eccomerce['longitude'].iat[i]])

# for cor in coordinate_eccomerce:
#         # folium.Marker([cor[0], cor[1]], popup="<i>Ecommerce", icon=folium.Icon(color='orange', icon='')).add_to(m)
#         folium.CircleMarker([cor[0], cor[1]], color='black', radius=4, fill=True).add_to(m)


# -------------- Agregar Recorrido ----------------
points = random.choices(coordinate_eccomerce, k=5)
sorted(points , key=lambda k: [k[1], k[0]])
points.insert(0, random.choice(coordinate_driver))
points.append(random.choice(coordinate_center))

for i in range(len(points)):
     folium.Marker([points[i][0], points[i][1]], icon=DivIcon(
        icon_size=(150,36),
        icon_anchor=(7,20),
        html=f'<div style="font-size: 18pt; color : black">{i + 1}</div>',
        )).add_to(m)
folium.PolyLine(points, color="red", weight=1.5, opacity=1).add_to(m)


points_delivery = random.choices(locations[:amountDays[0]], k=5)
points_delivery.insert(0, coordinate_center[0])


for i in range(len(points_delivery)):
     folium.Marker([points_delivery[i][0], points_delivery[i][1]], icon=DivIcon(
        icon_size=(150,36),
        icon_anchor=(7,20),
        html=f'<div style="font-size: 18pt; color : Gray">{i + 7}</div>',
        )).add_to(m)


folium.PolyLine(points_delivery, color="green", weight=1.5, opacity=1).add_to(m)

# ----- GUARDO TOD0 ------
m.save("mapsCode/maps/mapDayDriver.html")