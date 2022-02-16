# LIBRERIAS
import streamlit as st
import numpy as np
import pandas as pd
import os

import matplotlib.pyplot as plt
#%matplotlib inline
import plotly.offline as pyoff
import plotly.graph_objs as go
import plotly.express as px




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
    if 'rfm.csv' not in os.listdir('data'):
        st.markdown("Primero cargar el archivo luego ejecutar OUTLIER")
    else:
        # Parametros
        st.subheader('Parametros')
        umbral_maximo = st.number_input('Umbral Maximo:', min_value=70, max_value=100, value=85, step=1)/100
        st.write('Umbral para los Outliers: ',umbral_maximo*100)
        # Cargar data
        st.markdown("Cargando archivo RFM")
        rfm = pd.read_csv('data/rfm.csv')
        st.write(rfm)
        # RUN EJECUTAR SEGMENTACION
        formulario = st.form(key='mi-formulario')
        boton_run_segmentacion = formulario.form_submit_button('EJECUTAR SEGMENTACION')
        if boton_run_segmentacion:
                    st.markdown("EJECUTAR SEGMENTACION")
                    # Creando los Quartiles
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
                    # Asignar Segmentacion
                    rfm['R'] = rfm['Recency'].apply(lambda x: r_score(x))
                    rfm['F'] = rfm['Frequency'].apply(lambda x: fm_score(x, 'Frequency'))
                    rfm['M'] = rfm['Monetary'].apply(lambda x: fm_score(x, 'Monetary'))
                    # Asignar Score
                    rfm['RFM Score'] = rfm['R'].map(str) + rfm['F'].map(str) + rfm['M'].map(str)
                    # Asignando etiquetas
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
                    # Calculando RFM_Score
                    rfm['TotalRFM'] = rfm[['R','F','M']].sum(axis=1)
                    # Creando los SCORES
                    rfm['Score'] = 'Bronce'
                    rfm.loc[rfm['TotalRFM']>6,'Score'] = 'Plata' 
                    rfm.loc[rfm['TotalRFM']>9,'Score'] = 'Oro' 
                    rfm.loc[rfm['TotalRFM']>12,'Score'] = 'Platino'
                    st.write(rfm)
                    # Guardar RFM con los Segmentos
                    rfm.to_csv('data/rfm.csv', index=False)
                    st.write('Guardando archivo RFM con los Segmentos')
                    

                    
                    
        # AGREGAR CAMPOS ADICIONALES
        formulario2 = st.form(key='mi-formulario2')
        boton_run_agregar = formulario2.form_submit_button('AGREGAR TICKET PROMEDIO, SKU, UNIDADES')
        if boton_run_agregar:
            st.write(':::::::::: Agregando campos adicionales del cliente   ::::::::::')
            # Cargando data
            data = pd.read_csv('data/data.csv')
            data = data.convert_dtypes()
            data['FECHA'] = pd.to_datetime(data['FECHA'],dayfirst=True)
            clientes = data.groupby(['CLIENTE_CODIGO', 'CLIENTE_NOMBRE']).sum().reset_index()
            # Consolidar con nombre de cliente
            # Cargar datos RFM con segmentacion
            rfm = pd.read_csv('data/rfm.csv')
            
            rfm2 = rfm.merge(clientes, on='CLIENTE_CODIGO', how='inner')
            # Agregar contador de clientes ID
            rfm2['id'] = 1
            # Agregar TICKET PROMEDIO
            rfm2['Ticket'] = round(rfm2['MONTO']/rfm2['Frequency'],0)
            st.write(rfm2)
            # Guardar
            rfm2.to_csv('data/rfm2.csv', index=False)
            st.write('Guardando archivo RFM con campos adicionales')
            
            
            
        # OUTLIER 
        st.write(':::  OUTLIERS  DE CAMPOS RECIEN AGREGADOS :::')
        formulario3 = st.form(key='mi-formulario3')
        boton_run_outliers = formulario3.form_submit_button('EJECUTAR OUTLIERS PARA TICKET PROMEDIO, SKU, UNIDADES')
        if boton_run_outliers:
            # Cargar data
            rfm2 = pd.read_csv('data/rfm2.csv')
            columnas = ['UNIDADES','Ticket','SKU']
            for columna in columnas:
                st.write(':::::::::: VARIABLE ::::::::::',columna)
                st.write('::::::::::  Estadisticas   ::::::::::')
                st.write(rfm2[[columna]].describe())
                st.write('::::::::::  Rango Intercuartilago   ::::::::::')
                st.write('Umbral Alto %: ',umbral_maximo)
                limite_superior = outlier_umbral_alto(rfm2[columna],umbral_maximo)
                st.write('::::::::::  Ajustando Outliers por encima del Limite Superior   ::::::::::')
                rfm2[columna] = np.where(rfm2[columna] > limite_superior, limite_superior, rfm2[columna])
                st.write(rfm2[columna].describe())
                st.write('::::::::::  Grafico Histograma sin Outliers   ::::::::::')
                df = rfm2
                fig = px.histogram(df, x=columna,
                                title='Histograma ' + columna,
                                labels={columna:columna}, # can specify one label per df column
                                opacity=0.8,
                                log_y=False, # represent bars with log scale
                                color_discrete_sequence=['indianred'] # color of histogram bars
                                )
                fig.show()
                
                st.write('::::::::::  Grafico BoxPlot sin Outliers   ::::::::::')
                df = rfm2
                fig = px.box(df, y=columna,title='BoxPlot ' + columna)
                fig.show()
                # Cargar data
                rfm2.to_csv('data/rfm3.csv', index=False)
                st.write('Guardando archivo RFM con campos adicionales sin Outliers')

