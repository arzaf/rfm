# LIBRERIAS
from re import A
#from tkinter import HORIZONTAL
import streamlit as st
import numpy as np
import pandas as pd
import os
import base64
import io

from lifetimes.utils import summary_data_from_transaction_data
from datetime import timedelta
import datetime
import seaborn as sns
import matplotlib.pyplot as plt
#%matplotlib inline
import plotly.offline as pyoff
import plotly.graph_objs as go
import plotly.express as px



import pandas as pd
from io import BytesIO
from pyxlsb import open_workbook as open_xlsb
from xlsxwriter import Workbook
import streamlit as st




def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    format1 = workbook.add_format({'num_format': '0.00'}) 
    worksheet.set_column('A:A', None, format1)  
    writer.save()
    processed_data = output.getvalue()
    return processed_data


# DETALLE DE LA PAGINA
def app():
    if 'rfm3.csv' not in os.listdir('data'):
        st.markdown("Primero ejecutar los 2 pasos anteriores del menu...")
    else:
        st.header("ANALISIS EXPLORATORIO DE DATOS (EDA)")
        # DESCARGAR ARCHIVO EN EXCEL ::::::::::::::::::::::::::::::::::::::::::::::::::
        st.subheader('Resultado de la Segmentacion RFM')
        # Cargar datos
        rfm3 = pd.read_csv('data/rfm3.csv')
        st.write(rfm3)
        df_xlsx = to_excel(rfm3)
        st.download_button(label='📥 Descargar Segmentacion RFM',
                        data=df_xlsx ,
                        file_name= 'SegmentacionRFM.xlsx')
        #######################################################################
        st.markdown("""---""")
        if st.button("Generar Analisis (Graficos"):
            # cargar datos
            rfm3 = pd.read_csv('data/rfm3.csv')
            # GRAFICOS EDA ::::::::::::::::::::::::::::::::::::::::::::::::::
            # df con total clientes x segmentos
            st.subheader('TOTAL CLIENTES X SEGMENTACION RFM')
            df = rfm3['Segment'].str.strip().value_counts()
            st.table(df)
            st.write('Total clientes: ' + str('{:,}'.format(len(rfm3))))

            '''
            st.subheader('TOTAL CLIENTES X SEGMENTACION RFM')
            segments_counts = rfm3['Segment'].value_counts().sort_values(ascending=True)
            fig, ax = plt.subplots()
            bars = ax.barh(range(len(segments_counts)),
                        segments_counts,
                        color='#50B2C0')
            ax.set_frame_on(False)
            ax.tick_params(left=False,
                        bottom=False,
                        labelbottom=False)
            ax.set_yticks(range(len(segments_counts)))
            ax.set_yticklabels(segments_counts.index)
            for i, bar in enumerate(bars):
                    value = bar.get_width()
                    if segments_counts.index[i] in ['Campeones', 'Leales','Potencialmente Leales']:
                        bar.set_color('red')
                    ax.text(value,
                            bar.get_y() + bar.get_height()/2,
                            '{:,} ({:}%)'.format(int(value),
                                            int(value*100/segments_counts.sum())),
                            va='center',
                            ha='left'
                        )
            st.plotly_chart(fig)
            '''

            # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
            #st.markdown("""---""")
            #st.subheader('TOTAL CLIENTES X SEGMENTACION RFM')
            df = rfm3
            line_colors = ["#7CEA9C", '#50B2C0', "rgb(114, 78, 145)", "hsv(348, 66%, 90%)", "hsl(45, 93%, 58%)"]
            fig = px.pie(df, values='id', names='Segment',
                        title='',
                        hover_data=['Monetary'],color_discrete_sequence=line_colors)
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig)
            
            # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
            st.markdown("""---""")
            st.subheader('DISTRIBUICION X FRECUENCY')
            fig = px.bar(rfm3, y='Frequency', x='Segment', text_auto='.2s',
                        title="Segmentos x FRECUENCY",
                        hover_name="CLIENTE_NOMBRE",template='none',color_discrete_sequence=["hsv(348, 66%, 90%)"]) # templates: ggplot2, none
            st.plotly_chart(fig)
            
            # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
            st.markdown("""---""")
            st.subheader('DISTRIBUICION X RECENCY')
            fig = px.bar(rfm3, y='Recency', x='Segment', text_auto='.2s',
                        title="Segmentos x RECENCY",
                        hover_name="CLIENTE_NOMBRE",template='none',color_discrete_sequence=["hsl(45, 93%, 58%)"]) # templates: ggplot2, none
            st.plotly_chart(fig)
            
            # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
            st.markdown("""---""")
            st.subheader('DISTRIBUICION X MONETARY')
            fig = px.bar(rfm3, y='Monetary', x='Segment', text_auto='.2s',
                        title="Segmentos x MONETARY",
                        hover_name="CLIENTE_NOMBRE",template='none',color_discrete_sequence=["#7CEA9C"]) # templates: ggplot2, none
            st.plotly_chart(fig)
            
            # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
            st.markdown("""---""")
            st.subheader('SEGMENTACION RFM')
            fig = px.scatter(rfm3, x="Recency", y="Frequency",
                        size="Monetary", color="Segment",
                            hover_name="CLIENTE_NOMBRE", log_x=False, size_max=60,template='ggplot2') # templates: ggplot2, none
            st.plotly_chart(fig)
            
            # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
            st.markdown("""---""")
            st.subheader('UNIDADES vs TICKET PROMEDIO')
            fig = px.scatter(rfm3, x="UNIDADES", y="Ticket",
                        size="Monetary", color="Segment",
                            hover_name="CLIENTE_NOMBRE", log_x=False, size_max=60,template='ggplot2') # templates: ggplot2, none
            st.plotly_chart(fig)
            
            # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
            st.markdown("""---""")
            st.subheader('SKU vs TICKET PROMEDIO')
            fig = px.scatter(rfm3, x="SKU", y="Ticket",
                        size="Monetary", color="Segment",
                            hover_name="CLIENTE_NOMBRE", log_x=False, size_max=60,template='ggplot2') # templates: ggplot2, none
            st.plotly_chart(fig)
            
            # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
            st.markdown("""---""")
            st.subheader('UNIDADES vs SKU')
            fig = px.scatter(rfm3, x="UNIDADES", y="SKU",
                        size="Monetary", color="Segment",
                            hover_name="CLIENTE_NOMBRE", log_x=False, size_max=60,template='ggplot2') # templates: ggplot2, none
            st.plotly_chart(fig)
            
            # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
            st.markdown("""---""")
            st.subheader('SEGMENTACION RFM X SCORE')
            df = rfm3
            line_colors = ["#7CEA9C", '#50B2C0', "rgb(114, 78, 145)", "hsv(348, 66%, 90%)", "hsl(45, 93%, 58%)"]
            fig = px.treemap(df, path=[px.Constant('Segment'), 'Segment','Score'], values='Monetary',
                            hover_data=['Monetary'],color_discrete_sequence=line_colors)
            st.plotly_chart(fig)
        
            # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
            st.markdown("""---""")
            st.subheader('SEGMENTACION RFM X SCORE')
            df = rfm3
            fig = px.sunburst(df, path=['Segment','Score'], values='Monetary')
            st.plotly_chart(fig)
