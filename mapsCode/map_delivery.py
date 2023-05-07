import pandas as pd
import folium
from folium.plugins import MarkerCluster


df = pd.read_excel("datos/deliveries_data.xlsx", index_col=0)

coordinate = []


# for i in range(df['latitude'].size):
#     coordinate.append([df['latitude'].iat[i], df['longitude'].iat[i]])


locations = list(zip(df['latitude'], df['longitude']))
m = folium.Map(location=(df['latitude'].iat[0], df['longitude'].iat[0]))

# for i in range(len(locations)):
#     folium.CircleMarker(location=locations[i],radius=1).add_to(m)

cluster = folium.FeatureGroup(name='cluster')
cluster.add_child(MarkerCluster(locations=locations))  
m.add_child(cluster)
m.save("mapsCode/maps/delivery.html")