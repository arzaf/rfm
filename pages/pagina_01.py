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
    st.write('IQR: ',IQR)
    upper_limit = Q3 + 1.5 * IQR
    st.write('Limite Superior: ',upper_limit)
    return upper_limit




# DETALLE DE LA PAGINA
def app():
    if 'data.csv' not in os.listdir('data'):
        st.markdown("Primero cargar el archivo...")
    else:
        data = pd.read_csv('data/data.csv')
        data = data.convert_dtypes()
        data['FECHA'] = pd.to_datetime(data['FECHA'],dayfirst=True)
        st.markdown("### OUTLIERS")
        st.write(data)
        # PARAMETROS
        st.subheader('Parametros')
        umbral_maximo = st.number_input('Umbral Maximo:', min_value=70, max_value=100, value=85, step=1)/100
        st.write('Umbral para los Outliers: ',umbral_maximo*100)
        NOW = data['FECHA'].max() + timedelta(days=1)
        end_date = data['FECHA'].max()
        start_date = data['FECHA'].min()
        period = abs((end_date - start_date).days)
        st.write('Facturas desde {} a {}'.format(data['FECHA'].min(),data['FECHA'].max()))
        st.write('Total dias en el perido analizado: ',period)
        data['DaysSinceOrder'] = data['FECHA'].apply(lambda x: (NOW - x).days)
        st.write(data)
        
        # Iniciar
        st.header('Preparando datos para iniciar el Modelo RFM...')
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
        
        # OUTLIER
        if st.button("Ejecutar OUTLIER"):
            st.header('OUTLIERS')
            columnas = columnas_nombres(rfm)
            for columna in columnas:
                st.write(':::::::::: VARIABLE ::::::::::',columna)
                st.write('::::::::::  Estadisticas   ::::::::::')
                st.write(rfm[[columna]].describe())
                st.write('::::::::::  Rango Intercuartilago   ::::::::::')
                st.write('Umbral Alto %: ',umbral_maximo)
                limite_superior = outlier_umbral_alto(rfm[columna],umbral_maximo)
                st.write('::::::::::  Ajustando Outliers por encima del Limite Superior   ::::::::::')
                rfm[columna] = np.where(rfm[columna] > limite_superior, limite_superior, rfm[columna])
                st.write(rfm[columna].describe())
                st.write('::::::::::  Grafico Histograma sin Outliers   ::::::::::')
                df = rfm
                fig = px.histogram(df, x=columna,
                                title='Histograma ' + columna,
                                labels={columna:columna}, # can specify one label per df column
                                opacity=0.8,
                                log_y=False, # represent bars with log scale
                                color_discrete_sequence=['indianred'] # color of histogram bars
                                )
                fig.show()
                
                st.write('::::::::::  Grafico BoxPlot sin Outliers   ::::::::::')
                df = rfm
                fig = px.box(df, y=columna,title='BoxPlot ' + columna)
                fig.show()
                # Guardar
                rfm.to_csv('data/rfm.csv', index=False)
                st.write('Guardando archivo RFM')
        
        
        