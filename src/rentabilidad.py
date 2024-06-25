import pandas as pd
import numpy as np

def compute_cambio_porcentual_por_activo(S):
    
    """
    Calcula el cambio porcentual para cada activo
    
    Args:
    - S: Lista de Listas, donde cada lista representa el precio generado mediante GBM para cada activo
    
    Returns:
    - percentage_changes: lista de listas, donde cada lista repersenta el cambio porcentual de el precio generado mediante GBM para cada activo

    """
    
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
        
        # Convertir en Lista
        series = series.tolist()

        #guardar en la lista percentage_change
        percentage_changes.append(series)
        
    return percentage_changes


def clean_rentabilidad_por_periodo(rentabilidad_por_periodo):

    """
    Limpia el objeto Rentabilidad por Periodo. 
    
    Args:
    - rentabilidad_por_periodo: Lista de simulaciones, donde cada lista interna son los valores de rentabilidad en cada periodo
    
    Returns:
    - rentabilidad_por_periodo_por_simulacion: dataframe con los valores de la rentabilidad en cada periodo para cada simulacion

    """

    # Initialize an empty DataFrame
    rentabilidad_por_periodo_por_simulacion = pd.DataFrame()

    for i, rentabilidad in enumerate(rentabilidad_por_periodo):
        # Create a temporary DataFrame for the current simulation
        temp_df = pd.DataFrame({'period': range(1, len(rentabilidad) + 1),
                            'rentabilidad': rentabilidad,
                            'simulation': i + 1})
        # Append the temporary DataFrame to the main DataFrame
        rentabilidad_por_periodo_por_simulacion = pd.concat([rentabilidad_por_periodo_por_simulacion, temp_df], ignore_index=True)

    return rentabilidad_por_periodo_por_simulacion


def get_periodo_rebalanceo(balanceo):
    
    """
    Calcula  cada cuantos dias hacer rebalanceo 

    Args:
    - balanceo(str): String indicando cada cuanto hacer el rebalanceo
    
    Returns:
    - dias_rebalanceo(Int): Dias del periodo de rebalanceo

    """

    if balanceo == "Mensual":
        dias_rebalanceo = 30
    elif balanceo == "Trimestral":
        dias_rebalanceo = 60
    elif balanceo == "Semestral":
        dias_rebalanceo = 180
    elif balanceo == "Anual":
        dias_rebalanceo = 365
    else:
        dias_rebalanceo = "Error: Opcion de rebalanceo no valida"
    
    return dias_rebalanceo

def rentabilidad_cartera_rebalanceo(inversion_disponible, tasa_de_cambio, pesos, num_periodos, num_assets, balanceo, fase, fase_dinero):
    
    """
    Calcula la rentabilidad de la cartera con rebalanceo
    
    Args:
    - inversion_disponible: Lista con la Inversion Inicial
    - tasa_de_cambio: Lista de Listas, donde cada lista es la tasa de cambio de un activo a traves del tiempo
    - pesos: lista de pesos iniciales para cada Activo
    - num_periodos: Numero de periodos para los que se tiene una simulacion
    - num_assets: Numero de assets en la cartera
    - balanceo: Cada cuanto aplicar rebalanceo
    - fase: Fase en la que se encuentra, Acumulacion o Distribucion
    - fase_dinero: Dinero que desea retirar o invertir en cada periodo
    
    Returns:
    - rentabilidad: Rentabilidad de Cartera al final del periodo. Una lista con la rentabilidad de cada activo al final del periodo
    - rentabilidad_total: Rentabilidad de cartera n en todos los periodos

    """
    rentabilidad_total = [] 

    rentabilidad_total_periodo = [] # Almacena la rentabilidad total en cada periodo
    
    pesos = pesos.copy()
    
    periodo = 0 # Variable creada para controlar el rebalanceo

    # Definir el periodo de rebalanceo

    periodo_rebalanceo = get_periodo_rebalanceo(balanceo)

    for i in range(0, num_periodos): # For Loop periods
        
        periodo +=1
    
        rentabilidad_periodo = []
    
        # Logica Rebalanceo
        if i != 0 and (periodo % periodo_rebalanceo == 0): # Si es el periodo 1, no hacer rebalanceo
            
            iteracion_anterior = i - 1
            
            cambio_porcentual_rentabilidad = []
        
            # Calcular el denominador para modificar los pesos: Sum de todos los activos (Cambio % activo i + 1) * Rentabilidad Activo i periodo anterior
            for y in range(0, num_assets): # Para cada activo 
                
                cambio_porcentual_rentabilidad_activo = ((tasa_de_cambio[y][i] + 1)*rentabilidad_total[iteracion_anterior][y])
            
                cambio_porcentual_rentabilidad.append(cambio_porcentual_rentabilidad_activo)
            
            cambio_porcentual_rentabilidad = sum(cambio_porcentual_rentabilidad)
        
            # Modificar Pesos : (Cambio % activo i + 1) * Rentabilidad Activo i periodo anterior/Denominador calculado en el paso anterior
        
            for w in range(0, num_assets):
            
                pesos[w] = ((tasa_de_cambio[w][i] + 1)*rentabilidad_total[iteracion_anterior][w])/cambio_porcentual_rentabilidad
    
        for j in range(0, num_assets): # For loop activos
                
            rentabilidad_activo_en_periodo = (tasa_de_cambio[j][i] + 1) * pesos[j] * inversion_disponible[0]
        
            rentabilidad_periodo.append(rentabilidad_activo_en_periodo)

        rentabilidad_total.append(rentabilidad_periodo)

        # Almacenar la rentabilidad total de ese periodo
        rentabilidad_total_periodo.append(sum(rentabilidad_periodo))

        # Calcular inversion disponible para la proxima iteracion
        # Si es periodo de rebalanceo, hacer retiro e ingreso de dinero correspondiente
        if i != 0 and (periodo % periodo_rebalanceo == 0):
            if fase == "Acumulación":
                inversion_disponible = [sum(rentabilidad_periodo) + (fase_dinero)]
            else:
                inversion_disponible = [sum(rentabilidad_periodo) - (fase_dinero)]
        else:
            inversion_disponible = [sum(rentabilidad_periodo)]
    
    rentabilidad_cartera = rentabilidad_total[-1]
    
    return rentabilidad_cartera, rentabilidad_total_periodo
    


def rentabilidad_cartera_rebalanceo_inflacion(inversion_disponible, tasa_de_cambio, pesos, num_periodos, num_assets, balanceo, fase, fase_dinero, inflacion, tipo_rentabilidad):
    
    """
    Calcula la rentabilidad de la cartera con rebalanceo
    
    Args:
    - inversion_disponible: Lista con la Inversion Inicial
    - tasa_de_cambio: Lista de Listas, donde cada lista es la tasa de cambio de un activo a traves del tiempo
    - pesos: lista de pesos iniciales para cada Activo
    - num_periodos: Numero de periodos para los que se tiene una simulacion
    - num_assets: Numero de assets en la cartera
    - balanceo: Cada cuanto aplicar rebalanceo
    - fase: Fase en la que se encuentra, Acumulacion o Distribucion
    - fase_dinero: Dinero que desea retirar o invertir en cada periodo
    - inflacion: Inflacion anual
    - tipo_rentabilidad: nominal (Sin Inflacion) o real (Con Inflacion)
    
    Returns:
    - rentabilidad: Rentabilidad de Cartera al final del periodo. Una lista con la rentabilidad de cada activo al final del periodo
    - rentabilidad_total: Rentabilidad de cartera n en todos los periodos

    """
    rentabilidad_total = [] 

    rentabilidad_total_periodo = [] # Almacena la rentabilidad total en cada periodo
    
    pesos = pesos.copy()
    
    periodo = 0 # Variable creada para controlar el rebalanceo

    # Definir el periodo de rebalanceo

    periodo_rebalanceo = get_periodo_rebalanceo(balanceo)

    # Calcular la inflacion diaria
    inflacion_diaria = (inflacion/365)/100

    for i in range(0, num_periodos): # For Loop periods
        
        periodo +=1
    
        rentabilidad_periodo = []
    
        # Logica Rebalanceo
        if i != 0 and (periodo % periodo_rebalanceo == 0): # Si es el periodo 1, no hacer rebalanceo
            
            iteracion_anterior = i - 1
            
            cambio_porcentual_rentabilidad = []
        
            # Calcular el denominador para modificar los pesos: Sum de todos los activos (Cambio % activo i + 1) * Rentabilidad Activo i periodo anterior
            for y in range(0, num_assets): # Para cada activo 
                
                cambio_porcentual_rentabilidad_activo = ((tasa_de_cambio[y][i] + 1)*rentabilidad_total[iteracion_anterior][y])
            
                cambio_porcentual_rentabilidad.append(cambio_porcentual_rentabilidad_activo)
            
            cambio_porcentual_rentabilidad = sum(cambio_porcentual_rentabilidad)
        
            # Modificar Pesos : (Cambio % activo i + 1) * Rentabilidad Activo i periodo anterior/Denominador calculado en el paso anterior
        
            for w in range(0, num_assets):
            
                pesos[w] = ((tasa_de_cambio[w][i] + 1)*rentabilidad_total[iteracion_anterior][w])/cambio_porcentual_rentabilidad
    
        for j in range(0, num_assets): # For loop activos
                
            rentabilidad_activo_en_periodo = (tasa_de_cambio[j][i] + 1) * pesos[j] * inversion_disponible[0]

            # Calcular rentabilidad Real o Nominal
            if tipo_rentabilidad == "real":

                # Considerar la inflacion diaria
                rentabilidad_activo_en_periodo = rentabilidad_activo_en_periodo - (inflacion_diaria*rentabilidad_activo_en_periodo)
                 
            rentabilidad_periodo.append(rentabilidad_activo_en_periodo)

        rentabilidad_total.append(rentabilidad_periodo)

        # Almacenar la rentabilidad total de ese periodo
        rentabilidad_total_periodo.append(sum(rentabilidad_periodo))

        # Calcular inversion disponible para la proxima iteracion
        # Si es periodo de rebalanceo, hacer retiro e ingreso de dinero correspondiente
        if i != 0 and (periodo % periodo_rebalanceo == 0):
            if fase == "Acumulación":
                inversion_disponible = [sum(rentabilidad_periodo) + (fase_dinero)]
            else:
                inversion_disponible = [sum(rentabilidad_periodo) - (fase_dinero)]
        else:
            inversion_disponible = [sum(rentabilidad_periodo)]
    
    rentabilidad_cartera = rentabilidad_total[-1]
    
    return rentabilidad_cartera, rentabilidad_total_periodo