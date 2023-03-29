import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt



# Lee los datos
df = pd.read_excel("datos/deliveries_data.xlsx", index_col=0)

# Renombrar las columnas
df.rename(columns = {'x2 (ancho en cm)':'ancho', 'x3 (alto en cm)':'alto', 
                     'x1 (largo en cm)':'largo', 'weight (kg)':'peso'}, inplace = True)

# Creamos una columna que son las dimensiones en m3
df['dimensiones'] = df['largo']/100 * df['ancho']/100 * df['alto']/100 



# Distribucion Dimension

# plt.figure(figsize = (8,5))
# plt.title('Distribución de las Dimensiones')
# sns.histplot(data=df['dimensiones'], bins = 30, kde=True)
# plt.show()


# Distribucion Peso

# plt.figure(figsize = (8,5))
# plt.title('Distribución de las Peso')
# sns.histplot(data=df['peso'], bins = 20)
# plt.show()

weigth = []
weigthAmount = []
value = []
for i in range(df['peso'].size):
    weigth.append(df['peso'].iat[i])

c = min(weigth)
while int(c) != int(max(weigth)):
    # weigthAmount.append([round(c, 1), weigth.count(round(c, 1))])
    weigthAmount.append(weigth.count(round(c, 1)))
    value.append(round(c, 1))
    c += 0.1
    
plt.bar(value, weigthAmount) 
plt.show()

# Correlacion

# corr = df.corr().values
# plt.figure(figsize = (8,5))
# correlation_matrix = df.corr()
# sns.heatmap(data = correlation_matrix, annot = True)
# plt.show()


# plt.figure(figsize = (11,11))
# plt.scatter(df['dimensiones'], df['peso'], marker='o')
# plt.xlabel("dimensiones")
# plt.ylabel("peso")
# plt.show()

# print(df['dimensiones'].corr(df['peso']))

# No hay correlacion entre peso y dimension


# Eccomerce Id

# plt.figure(figsize = (8,5))
# plt.title('Distribución de las Eccomerce')
# sns.histplot(data=df['e-commerce_id'], bins = 102)
# plt.show()


# # Fecha
# days = []
# amountDays = []

# for i in range(df['delivery_day'].size):
#     days.append(df['delivery_day'].iat[i].day)

# for i in range(30):
#     value = days.count(i + 1)
#     amountDays.append(value)


# plt.figure(figsize = (8,5))
# plt.title('Distribución de pedidos por dia')
# sns.histplot(data=amountDays, bins = 30)
# plt.show()

# plt.bar(range(30), amountDays)
# plt.show()