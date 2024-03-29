# LIBRERIAS
import streamlit as st
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
sns.set_style('whitegrid')
import operator
import base64
import io
import os

from io import BytesIO
from pyxlsb import open_workbook as open_xlsb
from xlsxwriter import Workbook
from openpyxl.workbook import Workbook

def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    writer.close() # antes era writer.save() pero daba error 
    processed_data = output.getvalue()
    return processed_data



def app():
    st.header("CARGA DE DATO")
    st.subheader("Agregar archivo Excel con la base de datos") 
    st.write("\n")
    st.info("Las columnas deben ser exactamente las siguintes: FECHA, FACTURA, CLIENTE_CODIGO, CLIENTE_NOMBRE, SUCURSAL, SKU, UNIDADES, MONTO")
    st.info("Los campos numericos no deben tener formato, debe ser formato = General")
    st.info("Los campos: SUCURSAL,SKU y UNIDADES son opcionales")
    st.info("No se permite valores nulos en ningun campo")

    st.info("Descargar Plantilla de Excel de ejemplo")
    plantilla = pd.read_csv('data/plantilla.csv')
    plantilla_excel = to_excel(plantilla)
    st.download_button(label='📥 Descargar Plantilla RFM',
                    data=plantilla_excel ,
                    file_name= 'PlantillaRFM.xlsx')

    # BOTON PARA SELECCIONAR EL ARCHIVO
    archivo = st.file_uploader("Seleccione el archivo", type = ['csv', 'xlsx'])
    global data
    if archivo is not None:
        try:
            data = pd.read_csv(archivo)
        except Exception as e:
            print(e)
            data = pd.read_excel(archivo)
    #
    if 'data.csv' not in os.listdir('data'):
        st.markdown("Primero cargar el archivo...")
        # GUARDAR EL ARCHIVO EN LA CARPETA DATA
    if st.button("Cargar datos y limpiar"):
        try:
            # CLEAN
            st.header('C L E A N   D A T A')
            data = data.convert_dtypes()
            data['FECHA'] = pd.to_datetime(data['FECHA'],dayfirst=True)
            st.write('Eliminado CLIENTE_CODIGO= -1, -2, 5746')
            data = data[data['CLIENTE_CODIGO']!=-1]
            data = data[data['CLIENTE_CODIGO']!=-2]
            data = data[data['CLIENTE_CODIGO']!=5746]
            st.write('Eliminado CLIENTE_CODIGO nulos')
            data = data[data['CLIENTE_CODIGO'].notna()]
            st.write('Eliminado SKU nulos')
            data = data[data['SKU'].notna()]
            st.write('Eliminado UNIDADES y MONTO negativos o ceros')
            data = data[data['UNIDADES']>0]
            data = data[data['MONTO']>0]
            # Guardar
            data.to_csv('data/data.csv', index=False)
            # Mostrar
            st.write(data)
            #Guardar
            st.write('Data limpiada guardada')
        except:
            st.error("Debes cargar el archivo, click en el boton 'browser files' y seleccionar el excel a cargar...")
            st.stop()