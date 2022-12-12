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

# Carga de datos
archivo_registros_presencia = st.sidebar.file_uploader('Seleccione un archivo CSV que siga el estándar DwC')

# Se continúa con el procesamiento solo si hay un archivo de datos cargado
if archivo_registros_presencia is not None:
    # Carga de registros de presencia en un dataframe
    registros_presencia = pd.read_csv(archivo_registros_presencia, delimiter='\t')
    # Conversión del dataframe de registros de presencia a geodataframe
    registros_presencia = gpd.GeoDataFrame(registros_presencia, 
                                           geometry=gpd.points_from_xy(registros_presencia.decimalLongitude, 
                                                                       registros_presencia.decimalLatitude),
                                           crs='EPSG:4326')
    # Carga de polígonos
    cantones = gpd.read_file("Datos/Cantones.geojson")

    # Limpieza de datos
    # Eliminación de registros con valores nulos en la columna 'species'
    registros_presencia = registros_presencia[registros_presencia['species'].notna()]
    # Cambio del tipo de datos del campo de fecha
    registros_presencia["eventDate"] = pd.to_datetime(registros_presencia["eventDate"]).dt.date
    # Especificación de filtros
    # Especie
    lista_especies = registros_presencia.species.unique().tolist()
    lista_especies.sort()
    filtro_especie = st.sidebar.selectbox('Seleccione la especie', lista_especies)

     # PROCESAMIENTO
    #

   # Filtrado
    registros_presencia = registros_presencia[registros_presencia['species'] == filtro_especie]

    # Cálculo de la cantidad de registros en Provincias
    # "Join" espacial de las capas de Provincias y registros de presencia
    provincia_contienen_registros = cantones.sjoin(registros_presencia, how="left", predicate="contains")
    # Conteo de registros de presencia en cada provincia
    provincia_registros = provincia_contienen_registros.groupby("CODNUM").agg(cantidad_registros_presencia1 = ("gbifID","count"))
    provincia_registros = provincia_registros.reset_index() # para convertir la serie a dataframe
    # Cálculo de la cantidad de registros en Cantones
    # "Join" espacial de las capas de Cantones y registros de presencia
    cantones_contienen_registros = cantones.sjoin(registros_presencia, how="left", predicate="contains")
    # Conteo de registros de presencia en cada canton
    cantones_registros = cantones_contienen_registros.groupby("CODNUM").agg(cantidad_registros_presencia = ("gbifID","count"))
    cantones_registros = cantones_registros.reset_index() # para convertir la serie a dataframe

   # SALIDAS
    # Tabla de registros de presencia
    st.header('Registros de presencia')
    st.dataframe(registros_presencia[['species', 'stateProvince', 'locality', 'eventDate']].rename(columns = {'species':'Especie', 'stateProvince':'Provincia', 'locality':'Localidad', 'eventDate':'Fecha'}))

   # Definición de columnas
    col1, col2 = st.columns(2)

    # Gráficos de cantidad de registros de presencia por provincia
    # "Join" para agregar la columna con el conteo a la capa de provincia
    provincia_registros = provincia_registros.join(cantones.set_index('CODNUM'), on='CODNUM', rsuffix='_b')
    # Dataframe filtrado para usar en graficación
    provincia_registros_grafico = provincia_registros.loc[provincia_registros['cantidad_registros_presencia1'] > 0, 
                                                            ["provincia", "cantidad_registros_presencia1"]].sort_values("cantidad_registros_presencia1", ascending=[False])
    provincia_registros_grafico = provincia_registros_grafico.set_index('provincia') 

    # "Join" para agregar la columna con el conteo a la capa de canton
    cantones_registros = cantones_registros.join(cantones.set_index('CODNUM'), on='CODNUM', rsuffix='_b')
    # Dataframe filtrado para usar en graficación
    cantones_registros_grafico = cantones_registros.loc[cantones_registros['cantidad_registros_presencia'] > 0, 
                                                            ["NCANTON", "cantidad_registros_presencia"]].sort_values("cantidad_registros_presencia", ascending=[False]).head(15)
    cantones_registros_grafico = cantones_registros_grafico.set_index('NCANTON') 

    # Gráficos
    with col1:
        st.header('Cantidad de registros por Provincia')
        fig = px.bar(provincia_registros_grafico, 
                    y = "cantidad_registros_presencia1",
                    labels={'provincia':'Provincia', 'cantidad_registros_presencia1':'Registros de presencia'})

        st.plotly_chart(fig) 

    with col2:
        st.header('Cantidad de registros por Cantón')
        fig = px.bar(cantones_registros_grafico, 
                    y = "cantidad_registros_presencia",
                    labels={'NCANTON':'Cantón', 'cantidad_registros_presencia':'Registros de presencia'})

        st.plotly_chart(fig) 

# Mapa final
    st.header('Mapa final')
        # Capa base
    m = folium.Map(location=[9.6, -84.2], tiles='CartoDB dark_matter', zoom_start=8, control_scale=True)
    folium.TileLayer( tiles='Stamen Terrain', name='Stamen Terrain').add_to(m)
        
# Capa de calor
    HeatMap(data=registros_presencia[['decimalLatitude', 'decimalLongitude']],
                overlay = True,
                name='Mapa de calor').add_to(m)
    
    folium.GeoJson(data=cantones, name='Cantones', show =False).add_to(m)
    # Capa de registros de presencia agrupados
    mc = MarkerCluster(name='Registros agrupados')
    for idx, row in registros_presencia.iterrows():
            if not math.isnan(row['decimalLongitude']) and not math.isnan(row['decimalLatitude']):
                        mc.add_child(Marker([row['decimalLatitude'], row['decimalLongitude']],
                            popup=[row['species'],
                            row['stateProvince'],
                            row['locality'],
                            row['eventDate']])).add_to(m)
    m.add_child(mc)

# Ventana emergente de Nombres de Cantones (Polígonos)
    gjson = folium.GeoJson("Datos/Cantones.geojson", name='Cantones').add_to(m)
    folium.features.GeoJsonPopup(fields=['NCANTON'],labels=False).add_to(gjson)

# Capa de coropletas
    folium.Choropleth(
        name="Cantidad de registros en Provincias",
        geo_data=cantones,
        data=provincia_registros,
        columns=['provincia', 'cantidad_registros_presencia1'],
        bins=8,
        key_on='feature.properties.provincia',
        fill_color='Blues', 
        fill_opacity=0.9, 
        line_opacity=1,
        legend_name='Cantidad de registros de presencia',
        show = (False),
        highlight = (True),
        smooth_factor=0).add_to(m)
# Capa de coropletas
    folium.Choropleth(
        name="Cantidad de registros en Cantones",
        geo_data=cantones,
        data=cantones_registros,
        columns=['CODNUM', 'cantidad_registros_presencia'],
        bins=8,
        key_on='feature.properties.CODNUM',
        fill_color='Reds', 
        fill_opacity=0.9, 
        line_opacity=1,
        show = (False),
        highlight = (True),
        legend_name='Cantidad de registros de presencia',
        smooth_factor=0).add_to(m)
# Control de capas
    folium.LayerControl().add_to(m)                       
    folium_static(m)