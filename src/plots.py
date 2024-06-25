import plotly.graph_objects as go

def create_plot_rentabilidad_por_periodo_por_simulacion(rentabilidad_por_periodo_por_simulacion):
        
        """
        Crear el grafico de Rentabilidad por periodo por simulacion
 
        Args:
            rentabilidad_por_periodo_por_simulacion (data.frane): Data Frame con la rentabilidad por periodo por simulacion
 
        Returns:
            fig: Grafico
        """

        # Grouping by simulation_number
        rentabilidad_por_periodo_por_simulacion_grouped = rentabilidad_por_periodo_por_simulacion.groupby('simulation')
        
        # Creating traces for each simulation
        traces = []

        for name, group in rentabilidad_por_periodo_por_simulacion_grouped:
            trace = go.Scatter(
                x = group['period'],
                y = group['rentabilidad'],
                mode = 'lines',
                name = f'Simulacion {name}'
            )
            traces.append(trace)

        layout = go.Layout(
            title='Rentabilidad por Simulacion',
            xaxis=dict(title='Period'),
            yaxis=dict(title='Rentabilidad'),
            plot_bgcolor='rgba(255,255,255,0)'  # Setting plot background color to transparent
        )

        fig = go.Figure(data=traces, layout=layout)

        return(fig)


def create_plot_rentabilidad_final_por_activo_por_simulacion(rentabilidad_final_por_activo_por_simulacion):
        
        """
        Crear el grafico de Rentabilidad por activo por simulacion
 
        Args:
            rentabilidad_final_por_activo_por_simulacion
 
        Returns:
            fig: Grafico
        """

        fig = go.Figure()

        # Crear trace para cada Empresa
        for col in rentabilidad_final_por_activo_por_simulacion.columns[:-1]:
    
            fig.add_trace(go.Scatter(x = rentabilidad_final_por_activo_por_simulacion.index,
                                     y = rentabilidad_final_por_activo_por_simulacion[col],
                                     mode='lines',
                                     name=col))

        fig.update_layout(
            title='Rentabilidad por Activo por simulacion',
            xaxis_title='Iteracion', 
            yaxis_title='Rentabilidad',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis = dict(gridcolor='rgba(255,255,255,0.5)'), 
            yaxis = dict(gridcolor='rgba(255,255,255,0.5)')
            )

        return(fig)   

def create_plot_rentabilidad_por_simulacion(inversion_inicial, rentabilidad_final_por_activo_por_simulacion, rentabilidad_objetivo):
        """
        Crear el grafico de Rentabilidad por simulacion
 
        Args:
            inversion_inicial
            rentabilidad_final_por_activo_por_simulacion
            rentabilidad_objetivo
 
        Returns:
            fig: Grafico
        """


        fig = go.Figure()
        
        # Si la rentabilidad es menor que la inversion inicial entonces pintar el valor de rojo
        colors = ['red' if rentabilidad < inversion_inicial else 'blue' for rentabilidad in rentabilidad_final_por_activo_por_simulacion["rentabilidad_iteracion"]]

        # Si la rentabilidad es mayor que la rentabilidad objetivo entonces pintar el valor de verde
        colors = ['green' if rentabilidad > rentabilidad_objetivo else 'red' if rentabilidad < inversion_inicial else 'blue' for rentabilidad in rentabilidad_final_por_activo_por_simulacion["rentabilidad_iteracion"]]



        fig.add_trace(go.Scatter(x = rentabilidad_final_por_activo_por_simulacion.index,
                                 y = rentabilidad_final_por_activo_por_simulacion["rentabilidad_iteracion"],
                                 mode = 'lines+markers',
                                 line = dict(color='blue'),
                                 marker = dict(color=colors),
                                 name = "Rentabilidad"))
        fig.update_layout(
            title = 'Rentabilidad por Simulacion',
            xaxis_title = 'Iteracion',
            yaxis_title = 'Rentabilidad',
            plot_bgcolor = 'rgba(0,0,0,0)',
            xaxis = dict(gridcolor = 'rgba(255,255,255,0.5)'),
            yaxis = dict(gridcolor = 'rgba(255,255,255,0.5)')
            )
      
        return(fig)