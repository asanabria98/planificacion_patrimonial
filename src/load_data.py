
import yfinance as yf
import pandas as pd

def load_data(empresas, start_date, end_date):
    
    """
    Cargar datos de yfinance 
 
    Args:
        empresas (list): Lista de empresas para las que se quiere data
        start_date (string): String con la fecha de inicio para la que se quiere la data
        end_date (string): String con la fecha final para la que se quiere la data
 
    Returns:
        base_data: Data de yfinance para las empresas seleccionadas
    """

    #diccionario para almacenar datos individuales
    datos_empresas = {}

    # Descargar datos para cada empresa y almacenar en el diccionario
    for empresa in empresas:
        datos = yf.download(empresa, start=start_date, end=end_date)
        datos_empresas[empresa] = datos[['Adj Close']].reset_index().set_index('Date')

    # Crear un DataFrame consolidado con las columnas de fecha y Adj Close para cada empresa
    df_consolidado = pd.DataFrame({empresa: datos['Adj Close'] for empresa, datos in datos_empresas.items()})

    return df_consolidado

#print(load_data(empresas = ['AAPL', 'GOOGL', 'AMZN', 'ABNB', 'TSLA'], start_date = '2023-01-01', end_date = '2024-01-01'))