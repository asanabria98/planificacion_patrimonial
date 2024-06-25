from src.plots import create_plot_rentabilidad_por_periodo_por_simulacion, create_plot_rentabilidad_final_por_activo_por_simulacion, create_plot_rentabilidad_por_simulacion
from src.rentabilidad import clean_rentabilidad_por_periodo
from src.simulation import run_multiple_simulations
from datetime import datetime, timedelta
from src.load_data import load_data
import plotly.graph_objects as go
import streamlit as st
import pandas as pd



def home():

    # Titulo del app
    st.markdown('<p style="font-size: 24px; color: black;">Planificación Patrimonial</p>', unsafe_allow_html=True)

    # Sidebar
    inversion_inicial = st.sidebar.number_input("Ingrese el valor inicial inicial", value = 1000, placeholder = None, step=1)
    rentabilidad_objetivo = st.sidebar.number_input("Ingrese el monto final objetivo", value = 1000, placeholder = None, step=1)

    inflacion = st.sidebar.number_input("Ingrese la inflacion anual %", value = 2, placeholder = None, step=1)
    
    balanceo = st.sidebar.selectbox('Seleccione cada cuanto desea realizar el rebalanceo', ('Mensual', 'Trimestral', 'Semestral', 'Anual'))

    #dias_balanceo = st.sidebar.number_input("Ingrese cada cuantos dias quiere realizar el rebalanceo", value = 30, placeholder = None, step=1)
    fase = st.sidebar.radio("Seleccione la fase en la que se encuentra", ["Acumulación", "Distribución"])
    
    if fase == "Acumulación":
        fase_dinero = st.sidebar.number_input("Ingrese dinero que desea invertir en cada periodo de rebalanceo", value = 0, placeholder = None, step=1)
    else :
        fase_dinero = st.sidebar.number_input("Ingrese dinero que desea retirar en cada periodo de rebalanceo", value = 0, placeholder = None, step=1)
    
    num_simulaciones = st.sidebar.number_input("Ingrese el numero de simulaciones", value = 10, placeholder = None, step=1)
    periodo_simulacion = st.sidebar.number_input("Ingrese el periodo por el cual desea simular en años", value = 1, placeholder = None, step=1, min_value = 1, max_value = 50)

    # Definir opciones de pares
    activos_data = pd.read_csv('data/nasdaq_screener.csv') 
    activos = activos_data["Symbol"].unique().tolist()

    activos_seleccionados =  st.sidebar.multiselect(label = "Selecione los activos de su cartera", options = activos, key = "select_activos")

    if st.sidebar.button("Simular", type="primary", key="simular") :

        # Load Base Data
        # Calculate the current date
        end_date = datetime.today()

        # Calculate the date three years ago from today
        start_date = end_date - timedelta(days=3*365)

        # Format the dates as strings in 'YYYY-MM-DD' format
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')

        print(start_date_str)
        print(end_date_str)
        
        base_data = load_data(empresas = activos_seleccionados, start_date = start_date_str, end_date = end_date_str) 

        # Run Simulations and get Rentabilidad Total
        rentabilidad_total, rentabilidad_por_periodo, rentabilidad_total_nominal, rentabilidad_por_periodo_nominal = run_multiple_simulations(df_consolidado = base_data,
                                                                                                                                              T = periodo_simulacion,
                                                                                                                                              activos_seleccionados = activos_seleccionados,
                                                                                                                                              inversion_inicial = inversion_inicial,
                                                                                                                                              distribucion_cartera = [1 / len(activos_seleccionados)] * len(activos_seleccionados),
                                                                                                                                              num_simulaciones = int(num_simulaciones),
                                                                                                                                              balanceo = balanceo,
                                                                                                                                              fase = fase,
                                                                                                                                              fase_dinero = fase_dinero,
                                                                                                                                              inflacion = inflacion)
        
        # Rentabilidaid Final por activo por simulacion
        rentabilidad_final_por_activo_por_simulacion = pd.DataFrame(rentabilidad_total, columns =  activos_seleccionados)
        rentabilidad_final_por_activo_por_simulacion_nominal = pd.DataFrame(rentabilidad_total_nominal, columns =  activos_seleccionados)

        # Calcular rentabilidad total por iteracion
        rentabilidad_final_por_activo_por_simulacion['rentabilidad_iteracion'] = rentabilidad_final_por_activo_por_simulacion.sum(axis=1)
        rentabilidad_final_por_activo_por_simulacion_nominal['rentabilidad_iteracion'] = rentabilidad_final_por_activo_por_simulacion_nominal.sum(axis=1)

        # Metrics
        # Calculate % Probabilidad de Alcanzar Rentabilidad Objetivo
        n_iteraciones = len(rentabilidad_final_por_activo_por_simulacion)
        n_iteraciones_favorables = (rentabilidad_final_por_activo_por_simulacion['rentabilidad_iteracion'] > rentabilidad_objetivo).sum()
        p_iteraciones_favorables = (n_iteraciones_favorables / n_iteraciones) * 100

        # Mejor simulacion
        promedio_simulacion = round(rentabilidad_final_por_activo_por_simulacion['rentabilidad_iteracion'].mean(), 0)
        mejor_simulacion = round(rentabilidad_final_por_activo_por_simulacion['rentabilidad_iteracion'].max(), 0)
        peor_simulacion = round(rentabilidad_final_por_activo_por_simulacion['rentabilidad_iteracion'].min(), 0)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Prob. Monto Objetivo", f"{p_iteraciones_favorables:.2f}%")
        col2.metric("Rentabilidad Media", f"${promedio_simulacion:,.0f}")
        col3.metric("Mejor Iteracion", f"${mejor_simulacion:,.0f}")
        col4.metric("Peor Iteración", f"${peor_simulacion:,.0f}")
        
        # Resumen Rentabilidad Real por Simulacion
        st.write("Resumen de Rentabilidad Real por simulación")    
        metrics_rentabilidad_final_por_activo_por_simulacion = pd.DataFrame({
            'Rent. Media': rentabilidad_final_por_activo_por_simulacion.mean(),
            'Desv.': rentabilidad_final_por_activo_por_simulacion.std(),
            'Mejor Iter.':  rentabilidad_final_por_activo_por_simulacion.max(),
            'Peor Iter.':  rentabilidad_final_por_activo_por_simulacion.min()
            })

        metrics_rentabilidad_final_por_activo_por_simulacion.index = metrics_rentabilidad_final_por_activo_por_simulacion.index[:-1].tolist() + ["Rentabilidad Total"]
        st.write(metrics_rentabilidad_final_por_activo_por_simulacion)
        st.download_button(label="Descargar",
                           data= metrics_rentabilidad_final_por_activo_por_simulacion.to_csv().encode("utf-8"),
                           file_name = "simulation_metrics.csv",
                           mime = "text/csv") 
      
        # Grafico Rentabilidad por periodo para cada Simulacion
        rentabilidad_por_periodo_por_simulacion = clean_rentabilidad_por_periodo(rentabilidad_por_periodo)
        rentabilidad_por_periodo_por_simulacion_nominal = clean_rentabilidad_por_periodo(rentabilidad_por_periodo_nominal)

        plot_rentabilidad_por_periodo_por_simulacion = create_plot_rentabilidad_por_periodo_por_simulacion(rentabilidad_por_periodo_por_simulacion)
        plot_rentabilidad_por_periodo_por_simulacion_nominal = create_plot_rentabilidad_por_periodo_por_simulacion(rentabilidad_por_periodo_por_simulacion_nominal)
        

        # Rentabilidad Final por activo por simulacion
        plot_rentabilidad_final_por_activo_por_simulacion = create_plot_rentabilidad_final_por_activo_por_simulacion(rentabilidad_final_por_activo_por_simulacion)
        plot_rentabilidad_final_por_activo_por_simulacion_nominal = create_plot_rentabilidad_final_por_activo_por_simulacion(rentabilidad_final_por_activo_por_simulacion_nominal)


        # Rentabilidad Total
        plot_rentabilidad_por_simulacion = create_plot_rentabilidad_por_simulacion(inversion_inicial, rentabilidad_final_por_activo_por_simulacion, rentabilidad_objetivo)
        plot_rentabilidad_por_simulacion_nominal = create_plot_rentabilidad_por_simulacion(inversion_inicial, rentabilidad_final_por_activo_por_simulacion_nominal, rentabilidad_objetivo)  

        tab1, tab2 = st.tabs(["Real", "Nominal"])

        with tab1:
            st.plotly_chart(plot_rentabilidad_por_periodo_por_simulacion)
            st.plotly_chart(plot_rentabilidad_final_por_activo_por_simulacion)
            st.plotly_chart(plot_rentabilidad_por_simulacion)

        with tab2:
            st.plotly_chart(plot_rentabilidad_por_periodo_por_simulacion_nominal)
            st.plotly_chart(plot_rentabilidad_final_por_activo_por_simulacion_nominal)
            st.plotly_chart(plot_rentabilidad_por_simulacion_nominal)

    
    st.write("Activos Disponibles")
    st.write(activos_data)


if __name__ == "__main__":
    home()