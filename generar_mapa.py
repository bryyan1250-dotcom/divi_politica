from pathlib import Path

import geopandas as gpd
import pandas as pd
import plotly.express as px


# --- 1. CONFIGURACION DE RUTAS ---
BASE_DIR = Path(__file__).resolve().parent

ruta_parquet = BASE_DIR / "tabla_construcciones_anexos_20260210.parquet"
ruta_shapefile = BASE_DIR / "division_politica_cali.shp"
ruta_salida_html = BASE_DIR / "mapa_cali_interactivo_resaltado.html"
ruta_salida_looker = BASE_DIR / "mapa_cali_looker.html"
ruta_salida_index = BASE_DIR / "index.html"
ruta_salida_geojson = BASE_DIR / "mapa_cali_predios.geojson"
ruta_salida_csv = BASE_DIR / "conteo_predios_por_comuna.csv"


# --- 2. PROCESAMIENTO DE DATOS ---
print("Cargando datos Parquet...")
df_datos = pd.read_parquet(
    ruta_parquet,
    columns=["COMUNA", "ID_PREDIO"],
)

conteo_por_comuna = (
    df_datos.dropna(subset=["COMUNA"])
    .assign(comuna_id=lambda df: df["COMUNA"].astype(str).str.extract(r"(\d+)")[0].str.zfill(2))
    .groupby("comuna_id", as_index=False)["ID_PREDIO"]
    .count()
    .rename(columns={"ID_PREDIO": "total_predios"})
)

print("Cargando Shapefile...")
gdf = gpd.read_file(ruta_shapefile)

gdf["comuna_id"] = gdf["codigo"].astype(str).str.extract(r"(\d+)")[0].str.zfill(2)
gdf["nombre_mapa"] = gdf["nombre"].astype(str)

gdf_final = gdf.merge(conteo_por_comuna, on="comuna_id", how="left")
gdf_final["total_predios"] = gdf_final["total_predios"].fillna(0).astype(int)

# Plotly trabaja mejor con coordenadas geograficas WGS84.
if gdf_final.crs is None:
    raise ValueError("El shapefile no tiene CRS definido. Revisa el archivo .prj.")

if gdf_final.crs.to_epsg() != 4326:
    gdf_final = gdf_final.to_crs(epsg=4326)

gdf_final = gdf_final.reset_index(drop=True)
gdf_final["feature_id"] = gdf_final.index.astype(str)

# Guardar estos archivos ayuda si decides alimentar Looker Studio con datos/geometria.
gdf_final[
    ["feature_id", "codigo", "nombre_mapa", "comuna_id", "total_predios", "geometry"]
].to_file(ruta_salida_geojson, driver="GeoJSON")

gdf_final[["codigo", "nombre_mapa", "comuna_id", "total_predios"]].to_csv(
    ruta_salida_csv,
    index=False,
    encoding="utf-8-sig",
)


# --- 3. CREACION DEL MAPA INTERACTIVO ---
print("Generando mapa interactivo...")
geojson = gdf_final.__geo_interface__

fig = px.choropleth_map(
    gdf_final,
    geojson=geojson,
    locations="feature_id",
    featureidkey="properties.feature_id",
    color="total_predios",
    color_continuous_scale=px.colors.sequential.Blues,
    map_style="carto-positron",
    zoom=10.5,
    center={"lat": 3.4372, "lon": -76.5225},
    opacity=0.82,
    hover_name="nombre_mapa",
    hover_data={
        "feature_id": False,
        "codigo": False,
        "comuna_id": False,
        "nombre_mapa": False,
        "total_predios": ":,.0f",
    },
    labels={"total_predios": "Total predios"},
)


# --- 4. ESTILO Y RESALTADO ---
fig.update_traces(
    marker_line_width=1.2,
    marker_line_color="white",
    hovertemplate="<b>%{hovertext}</b><br>Total predios: %{z:,.0f}<extra></extra>",
)

fig.update_layout(
    title={
        "text": "<b>Actualizacion Catastral Cali 2026: Predios por Comuna y Corregimiento</b>",
        "y": 0.97,
        "x": 0.5,
        "xanchor": "center",
        "yanchor": "top",
        "font": {"size": 20, "color": "#042a4f"},
    },
    margin={"r": 0, "t": 48, "l": 0, "b": 0},
    coloraxis_colorbar={
        "title": "Predios",
        "thicknessmode": "pixels",
        "thickness": 15,
        "lenmode": "pixels",
        "len": 300,
        "yanchor": "top",
        "y": 0.85,
        "ticks": "outside",
    },
    hoverlabel={"bgcolor": "white", "font_size": 14, "font_family": "Arial"},
)


# --- 5. GUARDAR ---
print(f"Guardando mapa interactivo en: {ruta_salida_html}")
fig.write_html(
    ruta_salida_html,
    include_plotlyjs=True,
    full_html=True,
    config={
        "displaylogo": False,
        "responsive": True,
        "scrollZoom": True,
        "modeBarButtonsToRemove": ["lasso2d", "select2d"],
    },
)


# Version compatible con Looker Studio:
# no usa mapa base externo ni tiles; Plotly dibuja los poligonos como SVG.
fig_looker = px.choropleth(
    gdf_final,
    geojson=geojson,
    locations="feature_id",
    featureidkey="properties.feature_id",
    color="total_predios",
    color_continuous_scale=px.colors.sequential.Blues,
    hover_name="nombre_mapa",
    hover_data={
        "feature_id": False,
        "codigo": False,
        "comuna_id": False,
        "nombre_mapa": False,
        "total_predios": ":,.0f",
    },
    labels={"total_predios": "Total predios"},
)

fig_looker.update_traces(
    marker_line_width=1.1,
    marker_line_color="white",
    hovertemplate="<b>%{hovertext}</b><br>Total predios: %{z:,.0f}<extra></extra>",
)

fig_looker.update_geos(
    fitbounds="locations",
    visible=False,
    projection_type="mercator",
)

fig_looker.update_layout(
    title={
        "text": "<b>Actualizacion Catastral Cali 2026: Predios por Comuna y Corregimiento</b>",
        "y": 0.98,
        "x": 0.5,
        "xanchor": "center",
        "yanchor": "top",
        "font": {"size": 18, "color": "#042a4f"},
    },
    paper_bgcolor="white",
    plot_bgcolor="white",
    margin={"r": 0, "t": 48, "l": 0, "b": 0},
    coloraxis_colorbar={
        "title": "Predios",
        "thicknessmode": "pixels",
        "thickness": 15,
        "lenmode": "pixels",
        "len": 280,
        "yanchor": "top",
        "y": 0.86,
        "ticks": "outside",
    },
    hoverlabel={"bgcolor": "white", "font_size": 14, "font_family": "Arial"},
)

config_looker = {
    "displaylogo": False,
    "responsive": True,
    "scrollZoom": True,
    "modeBarButtonsToRemove": ["lasso2d", "select2d"],
}

print(f"Guardando version compatible con Looker Studio en: {ruta_salida_looker}")
fig_looker.write_html(
    ruta_salida_looker,
    include_plotlyjs=True,
    full_html=True,
    config=config_looker,
)

print(f"Actualizando pagina principal en: {ruta_salida_index}")
fig_looker.write_html(
    ruta_salida_index,
    include_plotlyjs=True,
    full_html=True,
    config=config_looker,
)

print(f"GeoJSON guardado en: {ruta_salida_geojson}")
print(f"CSV guardado en: {ruta_salida_csv}")
print("Proceso completado con exito.")
