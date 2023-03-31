import geopy.distance
import pandas as pd

coords_1 = (52.2296756, 21.0122287)
coords_2 = (52.406374, 16.9251681)

print(geopy.distance.geodesic(coords_1, coords_2).km)


df = pd.read_excel("datos/deliveries_data.xlsx", index_col=0)
df_driver = pd.read_excel("datos/driver_origins_data.xlsx", index_col=0)
df_center = pd.read_excel("datos/centers_data.xlsx", index_col=0)
df_eccomerce = pd.read_excel("datos/e-commerce_data.xlsx", index_col=0)



list_center = list(zip(df_center['latitude'], df_center['longitude']))
list_eccoomerce = list(zip(df_eccomerce['latitude'], df_eccomerce['longitude']))
list_driver = list(zip(df_driver['latitude'], df_driver['longitude']))

for i in range(df_center.size):
    list = []
    
    coord_center = (df_center['latitude'].iat[i], df_center['longitude'].iat[i])
    distance = 10000000000
    for j in range(df_eccomerce.size):
        coord_eccomerce = (df_eccomerce['latitude'].iat[j], df_eccomerce['longitude'].iat[j])
        if distance < (geopy.distance.geodesic(coord_eccomerce, coord_center).km):
            pass

