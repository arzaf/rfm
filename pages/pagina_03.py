# LIBRERIAS
from re import A
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
        st.markdown("Primero cargar el archivo y procesar los pasos del menu")
    else:
        st.markdown("Cargando archivo RFM")
        rfm3 = pd.read_csv('data/rfm3.csv')
        st.markdown("### ANALISIS EXPLORATORIO DE DATOS (EDA)")
        st.write(rfm3)
        # Descargar arhivo EXCEL
        df_xlsx = to_excel(rfm3)
        st.download_button(label='📥 Descargar Segmentacion RFM',
                           data=df_xlsx ,
                           file_name= 'SegmentacionRFM.xlsx')
        # Graficos
        if st.button("Procesar Graficos"):
            st.write(':::  E D A  :::')
            st.write(':::  A N A L I S I S        E X P L O R A T O R I O       D E       D A T O S  ::::')
            st.write(':::  GRAFICO DE BARRA TOTAL CLIENTES X SEGMENTACION RFM  ::::')
            segments_counts = rfm3['Segment'].value_counts().sort_values(ascending=True)
            fig, ax = plt.subplots()
            bars = ax.barh(range(len(segments_counts)),
                        segments_counts,
                        color='silver')
            ax.set_frame_on(False)
            ax.tick_params(left=False,
                        bottom=False,
                        labelbottom=False)
            ax.set_yticks(range(len(segments_counts)))
            ax.set_yticklabels(segments_counts.index)

            for i, bar in enumerate(bars):
                    value = bar.get_width()
                    if segments_counts.index[i] in ['Campeones', 'Leales','Potencialmente Leales']:
                        bar.set_color('firebrick')
                    ax.text(value,
                            bar.get_y() + bar.get_height()/2,
                            '{:,} ({:}%)'.format(int(value),
                                            int(value*100/segments_counts.sum())),
                            va='center',
                            ha='left'
                        )
            plt.show()
            

            st.write(':::  GRAFICO PIE TOTAL CLIENTES X SEGMENTACION RFM :::')
            df = rfm3
            line_colors = ["#7CEA9C", '#50B2C0', "rgb(114, 78, 145)", "hsv(348, 66%, 90%)", "hsl(45, 93%, 58%)"]
            fig = px.pie(df, values='id', names='Segment',
                        title='',
                        hover_data=['Monetary'],color_discrete_sequence=line_colors)
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.show()


            st.write(':::  GRAFICO DISTRIBUICION X FRECUENCY :::')
            fig = px.bar(rfm3, y='Frequency', x='Segment', text_auto='.2s',
                        title="Segmentos x FRECUENCY",
                        hover_name="CLIENTE_NOMBRE",template='none',color_discrete_sequence=["hsv(348, 66%, 90%)"]) # templates: ggplot2, none
            fig.show()


            st.write(':::  GRAFICO DISTRIBUICION X RECENCY :::')
            fig = px.bar(rfm3, y='Recency', x='Segment', text_auto='.2s',
                        title="Segmentos x RECENCY",
                        hover_name="CLIENTE_NOMBRE",template='none',color_discrete_sequence=["hsv(348, 66%, 90%)"]) # templates: ggplot2, none
            fig.show()


            st.write(':::  GRAFICO DISTRIBUICION X MONETARY :::')
            fig = px.bar(rfm3, y='Monetary', x='Segment', text_auto='.2s',
                        title="Segmentos x MONETARY",
                        hover_name="CLIENTE_NOMBRE",template='none',color_discrete_sequence=["hsv(348, 66%, 90%)"]) # templates: ggplot2, none
            fig.show()


            st.write(':::  GRAFICO DE BURBUJAS SEGMENTACION RFM :::')
            fig = px.scatter(rfm3, x="Recency", y="Frequency",
                        size="Monetary", color="Segment",
                            hover_name="CLIENTE_NOMBRE", log_x=False, size_max=60,template='ggplot2') # templates: ggplot2, none
            fig.show()


            st.write(':::  GRAFICO DE BURBUJAS UNIDADES vs TICKET PROMEDIO :::')
            fig = px.scatter(rfm3, x="UNIDADES", y="Ticket",
                        size="Monetary", color="Segment",
                            hover_name="CLIENTE_NOMBRE", log_x=False, size_max=60,template='ggplot2') # templates: ggplot2, none
            fig.show()


            st.write(':::  GRAFICO DE BURBUJAS SKU vs TICKET PROMEDIO :::')
            fig = px.scatter(rfm3, x="SKU", y="Ticket",
                        size="Monetary", color="Segment",
                            hover_name="CLIENTE_NOMBRE", log_x=False, size_max=60,template='ggplot2') # templates: ggplot2, none
            fig.show()


            st.write(':::  GRAFICO DE BURBUJAS UNIDADES vs SKU :::')
            fig = px.scatter(rfm3, x="UNIDADES", y="SKU",
                        size="Monetary", color="Segment",
                            hover_name="CLIENTE_NOMBRE", log_x=False, size_max=60,template='ggplot2') # templates: ggplot2, none
            fig.show()


            st.write(':::  GRAFICO SEGMENTACION RFM X SCORE :::')
            df = rfm3
            line_colors = ["#7CEA9C", '#50B2C0', "rgb(114, 78, 145)", "hsv(348, 66%, 90%)", "hsl(45, 93%, 58%)"]
            fig = px.treemap(df, path=[px.Constant('Segment'), 'Segment','Score'], values='Monetary',
                            hover_data=['Monetary'],color_discrete_sequence=line_colors)
            fig.show()


            st.write(':::  GRAFICO SEGMENTACION RFM X SCORE :::')
            df = rfm3
            fig = px.sunburst(df, path=['Segment','Score'], values='Monetary')
            fig.show()

        
        
        