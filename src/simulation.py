from src.rentabilidad import rentabilidad_cartera_rebalanceo_inflacion
from src.rentabilidad import compute_cambio_porcentual_por_activo
import pandas as pd
import numpy as np
import math

def metricas_para_simulacion(df_consolidado):
    
    """
    Calcula el rendimiento esperado, la votalidad diaria, y el ultimo precio para cada activo
 
    Args:
        df_cosolidado (data.frane): Data Frame con la serie temportal de los precios de las acciones
 
    Returns:
        metricas: Una lista de listas, donde las listas internas corresponden al rendimiento esperado,  la volatilidad diaria y el ultimo precio para cada activo
    """
    
    # Ultimo Precio Por activo
    ultimo_precio_por_activo = df_consolidado.iloc[-1]
    ultimo_precio_por_activo = ultimo_precio_por_activo.tolist()

    # Calcular el rendimiento diario
    rendimiento_diario = df_consolidado.pct_change()

    # Calcular la media del rendimiento diario para obtener una estimación del rendimiento esperado
    #rendimiento_esperado = rendimiento_diario.mean()
    rendimiento_esperado = rendimiento_diario.median()
    rendimiento_esperado = rendimiento_esperado.tolist()

    # Calcular la volatilidad diaria para cada activo
    volatilidad_diaria = rendimiento_diario.std()
    volatilidad_diaria = volatilidad_diaria.tolist()
    
    metricas = [rendimiento_esperado , volatilidad_diaria, ultimo_precio_por_activo]
    
    return metricas

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
    - S: Lista de Listas, donde cada lista representa el precio generado mediante GBM para cada activo
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


def run_multiple_simulations(df_consolidado, T, activos_seleccionados, inversion_inicial, distribucion_cartera, num_simulaciones, balanceo, fase, fase_dinero, inflacion):

    """
    Corre multiples simulaciones y calcula la rentabilidad
    
    Args:
    - df_consolidado:df_cosolidado (data.frane): Data Frame con la serie temportal de los precios de las acciones
    - T: Periodo por el cual se desea simular en años
    - activos_seleccionados (list): Lista de activos seleccionados
    - num_simulaciones (float): Numero de simulaciones por realizar
    - inversion_inicial (list) : Lista con la Inversion Inicial 
    - distribucion_cartera: lista de pesos iniciales para cada Activo
    - balanceo: Cada cuantos realizar el balanceo
    - fase: Fase en la que se encuentra, Acumulacion o Distribucion
    - fase_dinero: Dinero que desea retirar o invertir en cada periodo
    - inflacion: inflacion anual

    Returns:
    - 

    """

    metricas = metricas_para_simulacion(df_consolidado)
    print(metricas[0])
    print(((1 + metricas[0][0]) ** 365 - 1))
    # Rentabilidad Total
    rentabilidad_total = []
    rentabilidad_total_nominal = []

    # Rentabilidad Todos los periodos
    rentabilidad_por_periodo = []
    rentabilidad_por_periodo_nominal = []

    for i in range(num_simulaciones):

        # Hacer Simulacion 
        t, S = geometric_brownian_motion(T = T,
                                         #mu = metricas[0],
                                         mu = ((1 + metricas[0][0]) ** 365 - 1),
                                         #sigma = metricas[1],
                                         sigma = (metricas[1][0]) *  math.sqrt(365),
                                         S0 = metricas[2],
                                         dt = 1/365 ,
                                         num_assets = len(activos_seleccionados))
    
        # Calcular el cambio porcentual
        cambio_porcentual_por_activo = compute_cambio_porcentual_por_activo(S = S)
    
        # Calcular rentabilidad real
        rentabilidad_cartera_n, rentabilidad_cartera_n_por_periodo = rentabilidad_cartera_rebalanceo_inflacion(inversion_disponible = [inversion_inicial],
                                                                 tasa_de_cambio = cambio_porcentual_por_activo,
                                                                 pesos = distribucion_cartera,
                                                                 num_periodos = len(cambio_porcentual_por_activo[0]),
                                                                 num_assets = len(cambio_porcentual_por_activo),
                                                                 balanceo = balanceo,
                                                                 fase = fase,
                                                                 fase_dinero = fase_dinero,
                                                                 inflacion = inflacion,
                                                                 tipo_rentabilidad = "real")
        
        # Calcular rentabilidad nominal
        rentabilidad_cartera_n_nominal, rentabilidad_cartera_n_por_periodo_nominal = rentabilidad_cartera_rebalanceo_inflacion(inversion_disponible = [inversion_inicial],
                                                                 tasa_de_cambio = cambio_porcentual_por_activo,
                                                                 pesos = distribucion_cartera,
                                                                 num_periodos = len(cambio_porcentual_por_activo[0]),
                                                                 num_assets = len(cambio_porcentual_por_activo),
                                                                 balanceo = balanceo,
                                                                 fase = fase,
                                                                 fase_dinero = fase_dinero,
                                                                 inflacion = inflacion,
                                                                 tipo_rentabilidad = "nominal")        
    
        # Guardar Rentabilidad Total
        rentabilidad_total.append(rentabilidad_cartera_n)
        rentabilidad_total_nominal.append(rentabilidad_cartera_n_nominal)

        # Guardar Rentabilidad por periodo
        rentabilidad_por_periodo.append(rentabilidad_cartera_n_por_periodo)
        rentabilidad_por_periodo_nominal.append(rentabilidad_cartera_n_por_periodo_nominal)

    return rentabilidad_total, rentabilidad_por_periodo, rentabilidad_total_nominal, rentabilidad_por_periodo_nominal