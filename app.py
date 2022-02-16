# LIBRERIAS
'''
conda install pandas
conda install -c anaconda seaborn
conda install -c plotly plotly
conda install -c conda-forge matplotlib
conda install -c conda-forge lifetimes 
conda install -c conda-forge nbformat
pip install openpyxl
pip install streamlit
pip install DateTime

# excel
conda install -c conda-forge pyxlsb
pip install XlsxWriter

base_38_rfm

https://guillaume-martin.github.io/rfm-segmentation-with-python.html
https://medium.com/@nurlan.imanov/CLIENTE_NOMBRE-segmentation-using-rfm-analysis-d2df1dfa2f9f
https://futurice.com/blog/know-your-CLIENTE_NOMBREs-with-rfm
https://clevertap.com/blog/rfm-analysis/
https://plotly.com/python/sunburst-charts/

'''
import os
import streamlit as st
import numpy as np
from PIL import  Image

# IMPORTAR LAS PAGINAS
from multipage import MultiPage
from pages import data_upload, pagina_01, pagina_02, pagina_03

# CREAR LA INSTANCIA APP
app = MultiPage()

# TITULO
# CARGAR LOGO
display = Image.open('logo_farmacorp.jpeg')
# 2 COLUMNAS
col1, col2 = st.columns(2)
col1.image(display, width = 70)
col2.title("SEGMENTACION RFM")

# CARGAR LAS PAGINAS
app.add_page("Cargar Datos", data_upload.app)
app.add_page("OUTLIERS de los Datos", pagina_01.app)
app.add_page("Ejecutar Modelo + Campos adicionales", pagina_02.app)
app.add_page("Graficos Segmentacion RFM", pagina_03.app)


# EJECUTAR
app.run()