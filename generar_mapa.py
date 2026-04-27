from pathlib import Path

import geopandas as gpd
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# --- 1. CONFIGURACION DE RUTAS ---
BASE_DIR = Path(__file__).resolve().parent

ruta_parquet = BASE_DIR / "predio_20260420_ZHG.parquet"
ruta_shapefile = BASE_DIR / "division_politica_cali.shp"
ruta_salida_html = BASE_DIR / "mapa_cali_interactivo_resaltado.html"
ruta_salida_looker = BASE_DIR / "mapa_cali_looker.html"
ruta_salida_claro = BASE_DIR / "mapa_comunas_claro.html"
ruta_salida_index = BASE_DIR / "index.html"
ruta_salida_geojson = BASE_DIR / "mapa_cali_predios.geojson"
ruta_salida_csv = BASE_DIR / "conteo_predios_por_comuna.csv"
ruta_salida_looker_nativo = BASE_DIR / "looker_mapa_nativo.csv"
ruta_salida_looker_poligonos = BASE_DIR / "looker_comunas_poligonos_wkt.csv"
ruta_salida_sin_geometria = BASE_DIR / "codigos_parquet_sin_geometria.csv"
ruta_salida_mapa_rural = BASE_DIR / "mapa_cali_rural.html"
ruta_salida_mapa_urbano = BASE_DIR / "mapa_cali_urbano_comunas_grises.html"
ruta_salida_rural_wkt = BASE_DIR / "looker_rural_poligonos_wkt.csv"
ruta_salida_urbano_wkt = BASE_DIR / "looker_urbano_poligonos_wkt.csv"

COMUNAS_APAGADAS = {5, 6, 15, 16, 18}
ESCALA_AZULES_OSCUROS = [
    [0.0, "#edf4fb"],
    [0.18, "#d5e6f5"],
    [0.4, "#9cc2e2"],
    [0.62, "#4d8fc3"],
    [0.82, "#1f6da8"],
    [1.0, "#0a3968"],
]


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

codigos_shapefile = set(gdf["comuna_id"])
codigos_parquet = set(conteo_por_comuna["comuna_id"])
codigos_sin_geometria = sorted(codigos_parquet - codigos_shapefile)
conteo_por_comuna[
    conteo_por_comuna["comuna_id"].isin(codigos_sin_geometria)
].to_csv(
    ruta_salida_sin_geometria,
    index=False,
    encoding="utf-8-sig",
)

gdf_final = gdf.merge(conteo_por_comuna, on="comuna_id", how="left")
gdf_final["total_predios"] = gdf_final["total_predios"].fillna(0).astype(int)
gdf_final["tipo_zona"] = gdf_final["codigo"].astype(int).apply(
    lambda codigo: "Comuna" if codigo <= 22 else "Corregimiento"
)

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

puntos_mapa = gdf_final.copy()
puntos_mapa["punto_mapa"] = puntos_mapa.geometry.representative_point()
puntos_mapa["latitud"] = puntos_mapa["punto_mapa"].y
puntos_mapa["longitud"] = puntos_mapa["punto_mapa"].x
puntos_mapa["ubicacion"] = (
    puntos_mapa["latitud"].round(7).astype(str)
    + ","
    + puntos_mapa["longitud"].round(7).astype(str)
)
puntos_mapa["tipo_zona"] = puntos_mapa["codigo"].astype(int).apply(
    lambda codigo: "Comuna" if codigo <= 22 else "Corregimiento"
)
puntos_mapa["etiqueta_mapa"] = puntos_mapa["codigo"].astype(str)

puntos_mapa[
    [
        "codigo",
        "nombre_mapa",
        "tipo_zona",
        "comuna_id",
        "total_predios",
        "latitud",
        "longitud",
        "ubicacion",
        "etiqueta_mapa",
    ]
].to_csv(
    ruta_salida_looker_nativo,
    index=False,
    encoding="utf-8-sig",
)

poligonos_wkt = gdf_final.copy()
poligonos_wkt["geometry_wkt"] = poligonos_wkt.geometry.to_wkt()
poligonos_wkt[
    [
        "codigo",
        "nombre_mapa",
        "tipo_zona",
        "comuna_id",
        "total_predios",
        "geometry_wkt",
    ]
].to_csv(
    ruta_salida_looker_poligonos,
    index=False,
    encoding="utf-8-sig",
)

gdf_rural = gdf_final[gdf_final["codigo"].astype(int) > 22].copy()
gdf_rural["estado_mapa"] = "Rural"
gdf_rural["grupo_mapa"] = "Rural de Cali"

gdf_urbano = gdf_final[gdf_final["codigo"].astype(int).between(1, 22)].copy()
gdf_urbano["codigo_int"] = gdf_urbano["codigo"].astype(int)
gdf_urbano["estado_mapa"] = gdf_urbano["codigo_int"].apply(
    lambda codigo: "Apagada" if codigo in COMUNAS_APAGADAS else "Urbana activa"
)
gdf_urbano["grupo_mapa"] = gdf_urbano["estado_mapa"]

for datos, ruta_csv in [
    (gdf_rural, ruta_salida_rural_wkt),
    (gdf_urbano, ruta_salida_urbano_wkt),
]:
    salida = datos.copy()
    salida["geometry_wkt"] = salida.geometry.to_wkt()
    salida[
        [
            "codigo",
            "nombre_mapa",
            "tipo_zona",
            "comuna_id",
            "total_predios",
            "estado_mapa",
            "grupo_mapa",
            "geometry_wkt",
        ]
    ].to_csv(ruta_csv, index=False, encoding="utf-8-sig")


# --- 3. CREACION DEL MAPA INTERACTIVO ---
print("Generando mapa interactivo...")
geojson = gdf_final.__geo_interface__

fig = px.choropleth_map(
    gdf_final,
    geojson=geojson,
    locations="feature_id",
    featureidkey="properties.feature_id",
    color="total_predios",
    color_continuous_scale=ESCALA_AZULES_OSCUROS,
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
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    coloraxis_showscale=False,
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
    color_continuous_scale=ESCALA_AZULES_OSCUROS,
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

fig_looker.add_trace(
    go.Scattergeo(
        lat=puntos_mapa["latitud"],
        lon=puntos_mapa["longitud"],
        text=puntos_mapa["etiqueta_mapa"],
        mode="text",
        textfont={"size": 10, "color": "#042a4f", "family": "Arial Black, Arial"},
        hoverinfo="skip",
        showlegend=False,
    )
)

fig_looker.update_geos(
    fitbounds="locations",
    visible=False,
    projection_type="mercator",
)

fig_looker.update_layout(
    paper_bgcolor="white",
    plot_bgcolor="white",
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    coloraxis_showscale=False,
    hoverlabel={"bgcolor": "white", "font_size": 14, "font_family": "Arial"},
)

config_looker = {
    "displaylogo": False,
    "responsive": True,
    "scrollZoom": True,
    "modeBarButtonsToRemove": ["lasso2d", "select2d"],
}


def guardar_mapa_division(datos, ruta_html, centro, zoom):
    figura = px.choropleth_map(
        datos,
        geojson=datos.__geo_interface__,
        locations="feature_id",
        featureidkey="properties.feature_id",
        color="total_predios",
        color_continuous_scale=ESCALA_AZULES_OSCUROS,
        map_style="carto-positron",
        zoom=zoom,
        center=centro,
        opacity=0.88,
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

    figura.update_traces(
        marker_line_width=1.4,
        marker_line_color="#ffffff",
        hovertemplate="<b>%{hovertext}</b><br>Total predios: %{z:,.0f}<extra></extra>",
    )

    figura.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        coloraxis_showscale=False,
        hoverlabel={"bgcolor": "white", "font_size": 14, "font_family": "Arial"},
    )

    print(f"Guardando mapa en: {ruta_html}")
    figura.write_html(
        ruta_html,
        include_plotlyjs=True,
        full_html=True,
        config=config_looker,
    )

print(f"Guardando version compatible con Looker Studio en: {ruta_salida_looker}")
fig_looker.write_html(
    ruta_salida_looker,
    include_plotlyjs=True,
    full_html=True,
    config=config_looker,
)

guardar_mapa_division(
    gdf_rural,
    ruta_salida_mapa_rural,
    {"lat": 3.455, "lon": -76.577},
    10.4,
)

guardar_mapa_division(
    gdf_urbano,
    ruta_salida_mapa_urbano,
    {"lat": 3.4372, "lon": -76.5225},
    11.15,
)

print(f"Actualizando pagina principal en: {ruta_salida_index}")
fig_looker.write_html(
    ruta_salida_index,
    include_plotlyjs=True,
    full_html=True,
    config=config_looker,
)

fig_claro = px.choropleth(
    gdf_final,
    geojson=geojson,
    locations="feature_id",
    featureidkey="properties.feature_id",
    color="tipo_zona",
    color_discrete_map={
        "Comuna": "#d7ebf7",
        "Corregimiento": "#f2f7fb",
    },
    hover_name="nombre_mapa",
    hover_data={
        "feature_id": False,
        "codigo": False,
        "comuna_id": False,
        "nombre_mapa": False,
        "tipo_zona": True,
        "total_predios": ":,.0f",
    },
    labels={"total_predios": "Total predios", "tipo_zona": "Tipo"},
)

fig_claro.update_traces(
    marker_line_width=2.2,
    marker_line_color="#ffffff",
    hovertemplate="<b>%{hovertext}</b><br>Tipo: %{customdata[0]}<br>Total predios: %{customdata[1]:,.0f}<extra></extra>",
)

fig_claro.add_trace(
    go.Scattergeo(
        lat=puntos_mapa["latitud"],
        lon=puntos_mapa["longitud"],
        text=puntos_mapa["etiqueta_mapa"],
        mode="text",
        textfont={"size": 11, "color": "#042a4f", "family": "Arial Black, Arial"},
        hoverinfo="skip",
        showlegend=False,
    )
)

fig_claro.update_geos(
    fitbounds="locations",
    visible=False,
    projection_type="mercator",
)

fig_claro.update_layout(
    paper_bgcolor="white",
    plot_bgcolor="white",
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    legend={
        "orientation": "h",
        "yanchor": "bottom",
        "y": 0.01,
        "xanchor": "left",
        "x": 0.01,
        "bgcolor": "rgba(255,255,255,0.8)",
    },
    hoverlabel={"bgcolor": "white", "font_size": 14, "font_family": "Arial"},
)

print(f"Guardando version clara de comunas en: {ruta_salida_claro}")
fig_claro.write_html(
    ruta_salida_claro,
    include_plotlyjs=True,
    full_html=True,
    config=config_looker,
)

print(f"GeoJSON guardado en: {ruta_salida_geojson}")
print(f"CSV guardado en: {ruta_salida_csv}")
print(f"CSV para mapa nativo de Looker guardado en: {ruta_salida_looker_nativo}")
print(f"CSV con poligonos WKT guardado en: {ruta_salida_looker_poligonos}")
if codigos_sin_geometria:
    print(f"Codigos del Parquet sin geometria en shapefile: {', '.join(codigos_sin_geometria)}")
    print(f"Detalle guardado en: {ruta_salida_sin_geometria}")
print("Proceso completado con exito.")
