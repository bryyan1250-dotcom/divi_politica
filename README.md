# Mapa interactivo de Cali

Mapa coropletico interactivo de predios por comuna y corregimiento para la Actualizacion Catastral Cali 2026.

## Archivos

- `index.html`: version compatible con Looker Studio, lista para publicar con GitHub Pages.
- `mapa_cali_looker.html`: copia de la version compatible con Looker Studio.
- `mapa_cali_interactivo_resaltado.html`: version original del mapa interactivo.
- `generar_mapa.py`: script para regenerar el mapa desde el shapefile y el Parquet local.
- `conteo_predios_por_comuna.csv`: conteo resumido por comuna/corregimiento.
- `looker_mapa_nativo.csv`: base con latitud/longitud para usar mapas nativos de Looker Studio.
- `mapa_cali_predios.geojson`: geometria con conteos agregados.

El archivo Parquet fuente no se sube al repositorio porque contiene datos prediales detallados.

## Regenerar

```powershell
py -3 generar_mapa.py
```
