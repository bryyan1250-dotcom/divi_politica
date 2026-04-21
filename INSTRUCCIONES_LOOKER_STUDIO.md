# Mapa interactivo en Looker Studio

Archivos generados:

- `index.html`: mapa Plotly compatible con Looker Studio y listo para GitHub Pages.
- `mapa_cali_looker.html`: copia del mapa compatible con Looker Studio.
- `mapa_cali_interactivo_resaltado.html`: mapa Plotly con mapa base externo para uso fuera de Looker Studio.
- `mapa_cali_predios.geojson`: geometria + conteo de predios por comuna/corregimiento.
- `conteo_predios_por_comuna.csv`: tabla resumida para conectar a Looker Studio.
- `looker_mapa_nativo.csv`: tabla con latitud/longitud para usar graficos de mapa nativos de Looker Studio.
- `looker_comunas_poligonos_wkt.csv`: tabla con poligonos WKT para BigQuery GEOGRAPHY o visualizaciones compatibles.
- `codigos_parquet_sin_geometria.csv`: codigos del Parquet que no tienen poligono en el shapefile actual.

## Opcion recomendada: insertar el HTML como contenido embebido

Looker Studio no puede leer un archivo HTML local desde `C:\...`. Para que conserve hover e interactividad, el archivo `index.html` debe estar publicado en una URL HTTPS.

Puedes publicarlo, por ejemplo, con GitHub Pages, Netlify, Vercel o un servidor web propio.

Luego en Looker Studio:

1. Abre el informe.
2. Ve a `Insertar` > `URL insertada`.
3. Pega la URL HTTPS del HTML publicado, por ejemplo `https://bryyan1250-dotcom.github.io/divi_politica/`.
4. Ajusta el tamano del marco dentro del informe.

## Alternativa: usar datos dentro de Looker Studio

Usa `conteo_predios_por_comuna.csv` como fuente de datos si quieres construir graficos y filtros nativos de Looker Studio.

Para usar un mapa nativo de Looker Studio, carga `looker_mapa_nativo.csv` como fuente de datos. Luego crea un grafico de `Google Maps` o `Mapa` y configura:

- Dimension de ubicacion: `ubicacion`, o usa `latitud` y `longitud` si el grafico permite coordenadas separadas.
- Dimension de desglose: `nombre_mapa`.
- Metrica: `total_predios`.
- Campo de color o tamano: `total_predios`.

Esta opcion muestra puntos o burbujas sobre el mapa de Google. Los mapas nativos de Looker Studio no dibujan automaticamente los poligonos personalizados del shapefile.

Para un mapa con poligonos personalizados, usa `mapa_cali_predios.geojson` en una visualizacion compatible con GeoJSON o en una visualizacion comunitaria. Esta ruta depende del conector/visualizacion disponible en tu cuenta de Looker Studio.

Si el tablero debe mostrar divisiones reales de comunas/corregimientos dentro de un mapa de Google, la ruta mas robusta es cargar `looker_comunas_poligonos_wkt.csv` en BigQuery, convertir `geometry_wkt` a un campo `GEOGRAPHY` con `ST_GEOGFROMTEXT`, y conectar esa tabla a Looker Studio. Un CSV subido directamente a Looker Studio no convierte poligonos WKT en geometria nativa.

## Regenerar el mapa

Ejecuta:

```powershell
py -3 generar_mapa.py
```
