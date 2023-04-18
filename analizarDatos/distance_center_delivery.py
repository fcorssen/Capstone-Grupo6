import geopy.distance
import pandas as pd

df_center = pd.read_excel("datos/centers_data.xlsx", index_col=0)
df = pd.read_excel("datos/deliveries_data.xlsx", index_col=0)


c1 = 0
c2 = 0
c3 = 0
c4 = 0

for i in range(df['latitude'].size):
    coord_delivery = (df['latitude'].iat[i], df['longitude'].iat[i])
    distance = 10000000000000
    value = -1
    for j in range(df_center['latitude'].size):
        coord_center = (df_center['latitude'].iat[j], df_center['longitude'].iat[j])
        if distance > (geopy.distance.geodesic(coord_delivery, coord_center).km):
            distance = (geopy.distance.geodesic(coord_delivery, coord_center).km)
            value = j
    if value == 0:
        c1 += 1
    elif value == 1:
        c2 += 1
    elif value == 2:
        c3 += 1
    elif value == 3:
        c4 += 1

print('C1:', c1)
print('C2:', c2)
print('C3:', c3)
print('C4:', c4)
