# Se importan todas las bibliotecas
import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import folium
from folium import Marker
from folium.plugins import MarkerCluster
from folium.plugins import HeatMap
from streamlit_folium import folium_static
import math
# Carga de plotly graph objects (tabla)
import plotly.graph_objects as go

# Configuración de la página
st.set_page_config(layout='wide')


# TÍTULO Y DESCRIPCIÓN DE LA APLICACIÓN

st.title('Visualización de especies de Tucanes en Costa Rica')
st.markdown('Esta aplicación presenta visualizaciones tabulares, gráficas y geoespaciales de datos de biodiversidad que siguen el estándar [Darwin Core (DwC)](https://dwc.tdwg.org/terms/).')
st.markdown('El usuario debe seleccionar un archivo CSV basado en el DwC y posteriormente elegir una de las especies con datos contenidos en el archivo. **El archivo debe estar separado por tabuladores**. Este tipo de archivos puede obtenerse, entre otras formas, en el portal de la [Infraestructura Mundial de Información en Biodiversidad (GBIF)](https://www.gbif.org/).')
st.markdown('La aplicación muestra un conjunto de tablas, gráficos y mapas correspondientes a la distribución de la especie en el tiempo y en el espacio.')
