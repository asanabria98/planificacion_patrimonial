#!/usr/bin/env python
# coding: utf-8

# In[1]:


import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# In[2]:


#Listas de empresas de las que queremos obtener los datos
empresas = ['AAPL', 'GOOGL', 'AMZN', 'ABNB', 'TSLA']

#definimos rango de fechas
start_date = '2023-01-01'
end_date = '2024-01-01'


inversion_inicial = 1000
distribucion_cartera = [0.2, 0.2, 0.2, 0.2, 0.2]


# In[3]:


#diccionario para almacenar datos individuales
datos_empresas = {}

# Descargar datos para cada empresa y almacenar en el diccionario
for empresa in empresas:
    datos = yf.download(empresa, start=start_date, end=end_date)
    datos_empresas[empresa] = datos[['Adj Close']].reset_index().set_index('Date')

# Crear un DataFrame consolidado con las columnas de fecha y Adj Close para cada empresa
df_consolidado = pd.DataFrame({empresa: datos['Adj Close'] for empresa, datos in datos_empresas.items()})

# Mostrar los primeros registros del DataFrame consolidado
print(df_consolidado)


# In[4]:


def metricas_para_simulacion(df_consolidado):
    
    # Ultimo Precio Por activo
    ultimo_precio_por_activo = df_consolidado.iloc[-1]
    ultimo_precio_por_activo = ultimo_precio_por_activo.tolist()

    # Calcular el rendimiento diario
    rendimiento_diario = df_consolidado.pct_change()

    # Calcular la media del rendimiento diario para obtener una estimación del rendimiento esperado
    rendimiento_esperado = rendimiento_diario.mean()
    rendimiento_esperado = rendimiento_esperado.tolist()

    # Calcular la volatilidad diaria para cada activo
    volatilidad_diaria = rendimiento_diario.std()
    volatilidad_diaria = volatilidad_diaria.tolist()
    
    metricas = [rendimiento_esperado , volatilidad_diaria, ultimo_precio_por_activo]
    
    return metricas


# In[5]:


def geometric_brownian_motion(T, mu, sigma, S0, dt, num_assets):
    """
    Genera una trayectoria de Geometric Brownian Motion.
    
    Args:
    - T: tiempo total de simulación
    - mu: tasa de rendimiento esperada
    - sigma: volatilidad
    - S0: precio inicial
    - dt: paso de tiempo
    - num_assets: numero de activos
    
    Returns:
    - t: array de tiempos
    - S: matriz de precios generados mediante GBM para cada activo
    """
    num_steps = int(T / dt) + 1
    t = np.linspace(0, T, num_steps)
    W = np.random.standard_normal(size=(num_assets, num_steps - 1))
    W = np.insert(W, 0, 0.0, axis=1)
    dW = np.sqrt(dt) * W
    S = np.zeros((num_assets, num_steps))
    S[:, 0] = S0

    for i in range(1, num_steps):
        drift = mu * S[:, i - 1] * dt
        diffusion = sigma * S[:, i - 1] * dW[:, i]
        S[:, i] = S[:, i - 1] + drift + diffusion

    return t, S


# In[6]:


def compute_cambio_porcentual_por_activo(S):
    
    # Lista para guardar el cambio porcentual de cada activo
    percentage_changes = []

    # Loop sobre cada activo
    for sublist in S:
        # Convert cada sublista en S en una serie
        series = pd.Series(sublist)

        # Calcular cambio porcentual
        series = series.pct_change()

        # remplazar 0s por NAs
        series = series.fillna(0)

        #guardar en la lista percentage_change
        percentage_changes.append(series)
        
    return percentage_changes


# In[11]:


def rentabilidad_cartera(percentage_changes, inversion_inicial, distribucion_cartera, num_assets): 
    
    # Rentabilidad de cartera

    rentabilidad_cartera = []

    # Seleccionar tasas de cambio de un activo

    for i in range(num_assets):

        activo = percentage_changes[i]

        # Iniciar un columna con el primer valor igual a la inversion inicial
        rentabilidad_activo = []
        rentabilidad_activo = [inversion_inicial * distribucion_cartera[i]]

        # Iterate over the values in column A starting from the second value
        for cambio_porcentual in activo[1:]:

            # Calculate the new value based on the formula
            rentabilidad = (cambio_porcentual + 1) * rentabilidad_activo[-1]

            # Agregar Rentabilidad del activo
            rentabilidad_activo.append(rentabilidad)

        rentabilidad_cartera.append(rentabilidad_activo[-1])

    # Sumar la rentabilidad de Cartera
    valor_rentabilidad_cartera = sum(rentabilidad_cartera)
    return valor_rentabilidad_cartera


# In[49]:


# Probar hacer 10 simulaciones
# Asumo que ya le entra el df consolidado
# Se asume que solo son 3 activos

# Calcular Metricas para simulacion
metricas = metricas_para_simulacion(df_consolidado)

# Rentabilidad Total
rentabilidad_total = []

for i in range(100):
    
    # Hacer Simulacion 
    t, S = geometric_brownian_motion(T = 15,
                                 mu = metricas[0], 
                                 sigma = metricas[1], 
                                 S0 = metricas[2], 
                                 dt = 1/365 , num_assets = len(empresas))
    
    # Calcular el cambio porcentual
    cambio_porcentual_por_activo = compute_cambio_porcentual_por_activo(S = S)
    
    # Calcular rentabilidad
    rentabilidad_cartera_n = rentabilidad_cartera(percentage_changes = cambio_porcentual_por_activo,
                                                  inversion_inicial = inversion_inicial, 
                                                  distribucion_cartera = distribucion_cartera,
                                                  num_assets = len(empresas))
    
    # Guardar Rentabilidad Total
    rentabilidad_total.append(rentabilidad_cartera_n)

    
    


# In[50]:


print(rentabilidad_total)


# In[51]:


# Media de rentabilidad
sum(rentabilidad_total) / len(rentabilidad_total) 


# In[47]:


df = pd.DataFrame(S)
df = df.transpose()
df.columns = empresas
df["date"] = list(range(1, len(df) + 1))
df


# In[48]:


plt.figure(figsize=(10, 6))
for column in df.columns[:-1]:
    plt.plot(df['date'], df[column], label=column)

plt.xlabel('Date')
plt.ylabel('Value')
plt.title('Stock Values Over Time')
plt.legend()
plt.grid(True)
plt.show()


# In[52]:


plt.figure(figsize=(10, 6))
plt.plot(list(range(1, len(rentabilidad_total) + 1)), rentabilidad_total)
plt.xlabel('Simulacion')
plt.ylabel('Rentabilidad')
plt.title('Rentabilidad por simulacion')
plt.legend()
plt.grid(True)
plt.show()


