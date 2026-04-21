# Mapa interactivo de Cali

Mapa coropletico interactivo de predios por comuna y corregimiento para la Actualizacion Catastral Cali 2026.

## Archivos

- `index.html`: version compatible con Looker Studio, lista para publicar con GitHub Pages.
- `mapa_cali_looker.html`: copia de la version compatible con Looker Studio.
- `mapa_comunas_claro.html`: version enfocada en ver claramente las divisiones, sin coropleta por predios.
- `mapa_cali_interactivo_resaltado.html`: version original del mapa interactivo.
- `generar_mapa.py`: script para regenerar el mapa desde el shapefile y el Parquet local.
- `conteo_predios_por_comuna.csv`: conteo resumido por comuna/corregimiento.
- `looker_mapa_nativo.csv`: base con latitud/longitud para usar mapas nativos de Looker Studio.
- `looker_comunas_poligonos_wkt.csv`: base con poligonos en WKT para usar con BigQuery GEOGRAPHY o visualizaciones que acepten WKT.
- `codigos_parquet_sin_geometria.csv`: codigos presentes en el Parquet que no existen en el shapefile.
- `mapa_cali_predios.geojson`: geometria con conteos agregados.
- `bigquery_crear_vista_comunas.sql`: SQL para convertir WKT a `GEOGRAPHY` en BigQuery.

Los archivos Parquet fuente no se suben al repositorio porque contienen datos prediales detallados.

## Regenerar

```powershell
py -3 generar_mapa.py
```
