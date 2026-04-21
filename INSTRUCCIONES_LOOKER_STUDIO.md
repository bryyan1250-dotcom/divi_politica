# Mapa interactivo en Looker Studio

Archivos generados:

- `index.html`: mapa Plotly compatible con Looker Studio y listo para GitHub Pages.
- `mapa_cali_looker.html`: copia del mapa compatible con Looker Studio.
- `mapa_cali_interactivo_resaltado.html`: mapa Plotly con mapa base externo para uso fuera de Looker Studio.
- `mapa_cali_predios.geojson`: geometria + conteo de predios por comuna/corregimiento.
- `conteo_predios_por_comuna.csv`: tabla resumida para conectar a Looker Studio.

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

Para un mapa con poligonos personalizados, usa `mapa_cali_predios.geojson` en una visualizacion compatible con GeoJSON o en una visualizacion comunitaria. Esta ruta depende del conector/visualizacion disponible en tu cuenta de Looker Studio.

## Regenerar el mapa

Ejecuta:

```powershell
py -3 generar_mapa.py
```
