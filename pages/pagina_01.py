# LIBRERIAS
import streamlit as st
import numpy as np
import pandas as pd
import os

from lifetimes.utils import summary_data_from_transaction_data
from datetime import timedelta
import datetime

import matplotlib.pyplot as plt
#%matplotlib inline
import plotly.offline as pyoff
import plotly.graph_objs as go
import plotly.express as px



# ARRAY con la lista de todas las columnas
def columnas_nombres(data):
    col = data.columns.values
    index = 0 # vamos a eliminar la primer columna que corresponde a periodo o bodega
    # Eliminar
    col = np.delete(col, index)
    return col


# OUTLIER CAPPING AL UMBRAL ALTO
def outlier_umbral_alto(columna,umbral_alto=0.75):
    Q3 = np.quantile(columna, umbral_alto) # defaul 0.75
    Q1 = np.quantile(columna, 0.25) # default 0.25
    IQR = Q3 - Q1
    #st.write('IQR: ','{:.0f}'.format(IQR))
    upper_limit = Q3 + 1.5 * IQR
    st.write('Limite Superior: ','{:.0f}'.format(upper_limit))
    return upper_limit




# DETALLE DE LA PAGINA
def app():
    if 'data.csv' not in os.listdir('data'):
        st.markdown("Primero cargar el archivo...")
    else:
        data = pd.read_csv('data/data.csv')
        # Formatear el df
        data = data.convert_dtypes()
        #data['FECHA'] = pd.to_datetime(data['FECHA'],dayfirst=True)
        data['FECHA'] = pd.to_datetime(data['FECHA'], errors='coerce', format='%Y-%d-%m')
        st.header("EJECUTAR RFM + OUTLIERS")
        # PARAMETROS :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        st.header('P A R A M E T R O S')
        umbral_maximo = st.number_input('% Umbral Maximo:', min_value=70, max_value=100, value=85, step=1)/100
        st.write('Umbral para los Outliers: ','{:.0%}'.format(umbral_maximo))
        NOW = data['FECHA'].max() + timedelta(days=1)
        end_date = data['FECHA'].max()
        start_date = data['FECHA'].min()
        period = abs((end_date - start_date).days)
        st.write('Facturas desde {} a {}'.format(data['FECHA'].min(),data['FECHA'].max()))
        st.write('Total dias en el perido analizado: ',period)
        data['DaysSinceOrder'] = data['FECHA'].apply(lambda x: (NOW - x).days)
        # PARAMETRO SI GRAFICA
        graficar = st.radio('Con Graficos?', ['Si', 'No'],index=1,)
        
        # INCIAR EL MODELO ::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        if st.button("Calcular el Modelo RFM y limpiar Outliers"):
            st.subheader('Inciando el Modelo RFM...')
            aggr = {
                'DaysSinceOrder': lambda x: x.min(),  # the number of days since last order (Recency)
                'FECHA': lambda x: len([d for d in x if d >= NOW - timedelta(days=period)]), # the total number of orders in the last period (Frequency)
            }
            rfm = data.groupby('CLIENTE_CODIGO').agg(aggr).reset_index()
            rfm.rename(columns={'DaysSinceOrder': 'Recency', 'FECHA': 'Frequency'}, inplace=True)
            # Ejecutar
            rfm['Monetary'] = rfm['CLIENTE_CODIGO'].apply(lambda x: data[(data['CLIENTE_CODIGO'] == x) & \
                                                                    (data['FECHA'] >= NOW - timedelta(days=period))]\
                                                                    ['MONTO'].sum())
            rfm = rfm[rfm['Frequency']>0]
            st.write(rfm)
        
            # OUTLIER RFM ::::::::::::::::::::::::::::::::::::::::::::::::::::::::
            st.markdown("""---""")
            st.subheader('Limpiando OUTLIERS')
            columnas = columnas_nombres(rfm)
            for columna in columnas:
                st.markdown("""---""")
                st.subheader('VARIABLE: ' + columna)
                st.write('::::::::::  Estadisticas   ::::::::::')
                st.write(rfm[[columna]].describe())
                #
                if graficar == 'Si':
                    # GRAFICO ::::::::::::::
                    st.write('::::::::::  Grafico BoxPlot  ::::::::::')
                    df = rfm
                    fig = px.box(df, y=columna,title='BoxPlot ' + columna)
                    st.plotly_chart(fig)
                
                st.write('::::::::::  OUTLIER   ::::::::::')
                st.write('Umbral Alto: ','{:.0%}'.format(umbral_maximo))
                limite_superior = outlier_umbral_alto(rfm[columna],umbral_maximo)
                st.write('::::::::::  Ajustando Outliers por encima del Limite Superior   ::::::::::')
                rfm[columna] = np.where(rfm[columna] > limite_superior, limite_superior, rfm[columna])
                st.write(rfm[columna].describe())
                if graficar == 'Si':
                    # GRAFICO ::::::::::::::
                    st.write('::::::::::  Grafico Histograma sin Outliers   ::::::::::')
                    df = rfm
                    fig = px.histogram(df, x=columna,
                                    title='Histograma ' + columna,
                                    labels={columna:columna}, # can specify one label per df column
                                    opacity=0.8,
                                    log_y=False, # represent bars with log scale
                                    color_discrete_sequence=['indianred'] # color of histogram bars
                                    )
                    st.plotly_chart(fig)

                # Guardar
                rfm.to_csv('data/rfm.csv', index=False)
                st.write('Guardando archivo RFM sin Outliers')
 
            # RUN EJECUTAR SEGMENTACION :::::::::::::::::::::::::::::::::::::::::::::::::::
            st.markdown("""---""")
            st.header("S E G M E N T A N D O")
            st.write('Creando los Quartiles')
            quantiles = rfm[['Recency', 'Frequency', 'Monetary']].quantile([.2, .4, .6, .8]).to_dict()
            print(quantiles)
            # Definir formulas
            def r_score(x):
                if x <= quantiles['Recency'][.2]:
                    return 5
                elif x <= quantiles['Recency'][.4]:
                    return 4
                elif x <= quantiles['Recency'][.6]:
                    return 3
                elif x <= quantiles['Recency'][.8]:
                    return 2
                else:
                    return 1

            def fm_score(x, c):
                if x <= quantiles[c][.2]:
                    return 1
                elif x <= quantiles[c][.4]:
                    return 2
                elif x <= quantiles[c][.6]:
                    return 3
                elif x <= quantiles[c][.8]:
                    return 4
                else:
                    return 5  
            st.write('Asignar Segmentacion')
            rfm['R'] = rfm['Recency'].apply(lambda x: r_score(x))
            rfm['F'] = rfm['Frequency'].apply(lambda x: fm_score(x, 'Frequency'))
            rfm['M'] = rfm['Monetary'].apply(lambda x: fm_score(x, 'Monetary'))
            st.write('Asignar Score')
            rfm['RFM Score'] = rfm['R'].map(str) + rfm['F'].map(str) + rfm['M'].map(str)
            st.write('Asignando etiquetas')
            segt_map = {
                r'[1-2][1-2]': 'Hibernando', # Hibernating
                r'[1-2][3-4]': 'En Riesgo', # At Risk
                r'[1-2]5': 'No puedo Perderlos', # Can\'t Loose
                r'3[1-2]': 'A Punto de Dormir', # About to Sleep
                r'33': 'Necesitan Atencion', # Need Attention
                r'[3-4][4-5]': 'Leales', # Loyal CLIENTE_NOMBREs
                r'41': 'Prometedores', # Promising
                r'51': 'Nuevos', # New CLIENTE_NOMBREs
                r'[4-5][2-3]': 'Potencialmente Leales', # Potential Loyalists
                r'5[4-5]': 'Campeones' # Champions
            }
            rfm['Segment'] = rfm['R'].map(str) + rfm['F'].map(str)
            rfm['Segment'] = rfm['Segment'].replace(segt_map, regex=True)
            st.write('Calculando RFM_Score')
            rfm['TotalRFM'] = rfm[['R','F','M']].sum(axis=1)
            st.write('Asignado nombres del SCORE')
            rfm['Score'] = 'Bronce'
            rfm.loc[rfm['TotalRFM']>6,'Score'] = 'Plata' 
            rfm.loc[rfm['TotalRFM']>9,'Score'] = 'Oro' 
            rfm.loc[rfm['TotalRFM']>12,'Score'] = 'Platino'
            st.write(rfm)
            # Guardar RFM con los Segmentos
            rfm.to_csv('data/rfm.csv', index=False)
            st.write('Guardando archivo RFM con los Segmentos')
            
        
            # AGREGAR CAMPOS ADICIONALES :::::::::::::::::::::::::::::::::::::::::::::::::::::::
            st.markdown("""---""")
            st.subheader('Agregando campos adicionales del cliente')
            # Cargando data
            '''
            data = pd.read_csv('data/data.csv')
            data = data.convert_dtypes()
            data['FECHA'] = pd.to_datetime(data['FECHA'],dayfirst=True)
            '''
            #st.write(data)
            #st.write(rfm)
            clientes = data.groupby(['CLIENTE_CODIGO', 'CLIENTE_NOMBRE']).count().reset_index()
            # Crear rfm2 con campos adicionales del cliente
            rfm2 = rfm.merge(clientes, on='CLIENTE_CODIGO', how='inner')
            # Agregar contador de clientes ID
            rfm2['id'] = 1
            # Agregar TICKET PROMEDIO
            rfm2['Ticket'] = round(rfm2['MONTO']/rfm2['Frequency'],0)
            st.write(rfm2)
            # Guardar
            rfm2.to_csv('data/rfm2.csv', index=False)
            st.write('Guardando archivo RFM con campos adicionales')
            
        
            # OUTLIER :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
            st.markdown("""---""")
            st.subheader('OUTLIERS de campos recien agregados')
            columnas = ['UNIDADES','Ticket','SKU']
            for columna in columnas:
                st.markdown("""---""")
                st.subheader('VARIABLE: ' + columna)
                st.write('::::::::::  Estadisticas   ::::::::::')
                st.write(rfm2[[columna]].describe())
                # GRAFICAR ::::::::::::::::::::::::::
                if graficar == 'Si':
                    st.write('::::::::::  Grafico BoxPlot sin Outliers   ::::::::::')
                    df = rfm2
                    fig = px.box(df, y=columna,title='BoxPlot ' + columna)
                    st.plotly_chart(fig)
                st.write('::::::::::  OUTLIER   ::::::::::')
                st.write('Umbral Alto %: ','{:.0%}'.format(umbral_maximo))
                limite_superior = outlier_umbral_alto(rfm2[columna],umbral_maximo)
                st.write('::::::::::  Ajustando Outliers por encima del Limite Superior   ::::::::::')
                rfm2[columna] = np.where(rfm2[columna] > limite_superior, limite_superior, rfm2[columna])
                st.write(rfm2[columna].describe())
                # GRAFICAR ::::::::::::::::::::::::::
                if graficar == 'Si':
                    st.write('::::::::::  Grafico Histograma sin Outliers   ::::::::::')
                    df = rfm2
                    fig = px.histogram(df, x=columna,
                                    title='Histograma ' + columna,
                                    labels={columna:columna}, # can specify one label per df column
                                    opacity=0.8,
                                    log_y=False, # represent bars with log scale
                                    color_discrete_sequence=['indianred'] # color of histogram bars
                                    )
                    st.plotly_chart(fig)

                # Cargar data
                rfm2.to_csv('data/rfm3.csv', index=False)
                st.write('Guardando archivo RFM con campos adicionales sin Outliers')
        
        
