-- Reemplaza `TU_PROYECTO.TU_DATASET` por tu proyecto y dataset de BigQuery.
-- 1) Primero carga looker_comunas_poligonos_wkt.csv a una tabla llamada comunas_wkt.
-- 2) Luego ejecuta este SQL para crear una vista con geometria nativa.

CREATE OR REPLACE VIEW `TU_PROYECTO.TU_DATASET.comunas_geography` AS
SELECT
  CAST(codigo AS INT64) AS codigo,
  nombre_mapa,
  tipo_zona,
  comuna_id,
  CAST(total_predios AS INT64) AS total_predios,
  ST_GEOGFROMTEXT(geometry_wkt) AS geometry
FROM `TU_PROYECTO.TU_DATASET.comunas_wkt`;

-- Version opcional simplificada si Looker queda lento o faltan poligonos.
-- Ajusta la tolerancia: 5 equivale aproximadamente a 5 metros.
CREATE OR REPLACE VIEW `TU_PROYECTO.TU_DATASET.comunas_geography_simplificada` AS
SELECT
  codigo,
  nombre_mapa,
  tipo_zona,
  comuna_id,
  total_predios,
  ST_SIMPLIFY(geometry, 5) AS geometry
FROM `TU_PROYECTO.TU_DATASET.comunas_geography`;

