import geopy.distance
import pandas as pd
import numpy as np
import random
import folium
from folium.plugins import MarkerCluster
from folium.features import DivIcon
from sklearn import cluster
import matplotlib.cm as cm
import matplotlib.colors as cl
from clases import Driver, Paquete, Ecommerce, Centro


# ------------- Cargar los datos --------------

df_delivery = pd.read_excel("datos/deliveries_data.xlsx")
df_driver = pd.read_excel("datos/driver_origins_data.xlsx")
df_center = pd.read_excel("datos/centers_data.xlsx")
df_ecommerce = pd.read_excel("datos/e-commerce_data.xlsx")


# # ------------- Separar por dias --------------
days = []
amountDays = []

for i in range(df_delivery['delivery_day'].size):
    days.append(df_delivery['delivery_day'].iat[i].day)

for i in range(30):
    value = days.count(i + 1)
    amountDays.append(value)

# ---------- Instanciar los centros ---------- 
centros = []
for i in range(df_center['id'].size):
    centro = Centro(df_center['id'].iat[i], [df_center['latitude'].iat[i], df_center['longitude'].iat[i]])
    centros.append(centro)

# ---------- Instanciar los drivers ---------- 
drivers = []
for i in range(df_driver['id'].size):
    driver = Driver(df_driver['id'].iat[i], [df_driver['latitude'].iat[i], df_driver['longitude'].iat[i]])
    drivers.append(driver)

# ---------- Instanciar los ecommerce ---------- 
ecommerces = []
for i in range(df_ecommerce['id'].size):
    ecommerce = Ecommerce(df_ecommerce['id'].iat[i], [df_ecommerce['latitude'].iat[i], df_ecommerce['longitude'].iat[i]])
    ecommerces.append(ecommerce)

# ----------  Instanciar los paquetes ---------- 
paquetes = []
for i in range(df_delivery['id'].size):
    paquete = Paquete(df_delivery['id'].iat[i], df_delivery['weight (kg)'].iat[i], [df_delivery['latitude'].iat[i], df_delivery['longitude'].iat[i]], df_delivery['x1 (largo en cm)'].iat[i], df_delivery['x2 (ancho en cm)'].iat[i], df_delivery['x3 (alto en cm)'].iat[i], df_delivery['delivery_day'].iat[i].day, df_delivery['e-commerce_id'].iat[i])
    paquetes.append(paquete)

# ---------- Paquetes dia 1 ----------
paquetes_dia_1 = paquetes[:amountDays[0]]   

# ---------- Agregar paquetes a los ecommerce para el dia 1 ----------
for paquete in paquetes_dia_1:
    for ecommerce in ecommerces:
        if paquete.ecommerce == ecommerce.id:
            ecommerce.agregar_paquete(paquete)

# -------- Crear Mapa -----------
m = folium.Map(location=([-33.4369436, -70.634449]))

# ------ Agregar drivers a mapa ------------ 
for d in drivers:
    folium.CircleMarker(d.origen, color='black', radius=5, fill=True).add_to(m)


ecommerce_loc = []
for e in ecommerces:
    ecommerce_loc.append(e.ubicacion)


df_model = df_ecommerce[['latitude', 'longitude']]

model = cluster.AgglomerativeClustering(distance_threshold=0.03,
                                     n_clusters=None,
                                     metric='manhattan',
                                     linkage='complete').fit(df_model)
cluster_labels = model.labels_
num_clusters = len(set(cluster_labels))
df_model['labels'] = cluster_labels
df_model['labels'] = df_model['labels'].astype('category').cat.codes

# Generate color palette for coordinates
colors = cm.rainbow(np.linspace(0, 1, num_clusters))
colors_new = []
for el in colors:
    hex = cl.to_hex(el)
    colors_new += [hex]
colors_dict = {df_model.labels.unique()[i]: colors_new[i] for i in range(num_clusters)}


for _, data in df_model.iterrows():
    folium.CircleMarker([data['latitude'], data['longitude']],
                        fill = True,
                        radius = 4,
                        fill_color = colors_dict[data['labels']],
                        alpha = 1.0,
                        color= colors_dict[data['labels']]
                       ).add_to(m)

print(df_model.head())

m.save("simulation/maps/clusters_per_driver.html")
