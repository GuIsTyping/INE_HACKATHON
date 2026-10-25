# Bitacora de Cambios

## 2026-10-24

### Nombres auto-generados y layout del mapa
- `generar_nombre_perfil()`: funcion que compone nombres descriptivos a partir de condiciones sobre edad, genero, tipo de asentamiento y comportamiento electoral (sin nombres hardcodeados)
- Panel lateral del mapa movido de derecha a izquierda para no solaparse con el LayerControl
- `.env` con API key de CARTO para tiles del mapa; `.env.example` con instrucciones para obtener la propia
- `.gitignore` actualizado para excluir `.env`
- Dependencia `python-dotenv` agregada a `pyproject.toml`

### Segmentacion nacional y mapa interactivo
- `notebooks/04_segmentacion.ipynb` (27 code, 27 markdown): segmentacion nacional + fichas de perfil + mapa nacional interactivo
- Clustering nacional ponderado por lista nominal 2024 (71.2M personas, 657k celdas)
- K-Means con sample_weight, k=4 (rango 4-6 alineado a convocatoria que pide 4-6 perfiles)
- Caracterizacion completa por perfil: trayectoria 2009-2024, edad, sexo, region, urbano/rural, PJ 2025
- Nombres descriptivos auto-generados para cada perfil
- Fichas de perfil (seccion 5.7): una figura consolidada por perfil con trayectoria vs nacional, metricas, edad, region, top 5 entidades
- Mapa nacional interactivo con tiles CARTO CDN (sin API key), 2 capas + LayerControl
  - Capa estatal: 32 entidades, popup con nombre de perfil y porcentaje
  - Capa municipal: 2,475 municipios (1,858 con clustering local, 518 bloqueados)
  - Popups compactos con nombre de perfil + clustering local con detalle demografico
  - Panel lateral desplegable con fichas detalladas de los 4 perfiles nacionales
- Genera `celdas_perfiladas.parquet`, `resumen_perfiles.csv`, `resumen_municipios.csv`, `mapa_nacional_segmentacion.html` (~24 MB)
- Descarga de shapefile CONABIO en `src/descarga_inicial.py`, dependencias `geopandas` y `folium` en `pyproject.toml`

### Limpieza de ramas
- Eliminadas 3 ramas remotas ya mergeadas: `fix/entorno-python-312`, `feat/perfilado-datos`, `feat/analisis-exploratorio`

## 2026-10-18

### Revision de edades mayores a 100
- Verificado que EDAD > 100 no es un codigo especial (diccionarios, manual CCPC y seguimiento de registros entre elecciones). Detalle en `KNOWLEDGE_BASE.md` (Hallazgos del Perfilado > Calidad)
- Agregadas a `KNOWLEDGE_BASE.md` las agrupaciones de edad oficiales del CCPC (etapa de vida y grupo quinquenal)

### Notebook de analisis exploratorio
- `notebooks/03_analisis_exploratorio.ipynb` (34 secciones): regiones, cohortes generacionales, historial por seccion y por celda (seccion x sexo x grupo de edad), indicadores de historial, persistencia, relacion con PJ 2025 y fuentes de variacion (eta cuadrada)
- Genera `secciones_historial.parquet` y `celdas_historial.parquet` en `DATA/PREPROCESSED/`
- Hallazgos agregados a `KNOWLEDGE_BASE.md`

### Notebook de perfilado
- `notebooks/02_perfilado_datos.ipynb` (35 secciones): inventario, esquema, carga con tipos compactos (~1.2 GB en memoria), nulos, cobertura, distribucion de edad, edades atipicas, consistencia LN = SV + NV + NS, NS por ano, participacion por ano, sexo, grupo de edad, tipo de seccion y entidad, secciones con historial completo, PJ 2025 y datasets complementarios
- Hallazgos agregados a `KNOWLEDGE_BASE.md`

### Version de Python fijada
- `.python-version` con 3.12 (`uv python pin 3.12`) para que todo el equipo use la misma version; antes `uv sync` tomaba la primera disponible (>=3.12)

### Fix en notebook de ingesta
- `01_ingesta_datos.ipynb` (seccion 11): `pf.schema_arrow.num_fields` -> `len(pf.schema_arrow)`; `num_fields` no existe en pyarrow 26 y detenia la ejecucion antes de guardar PJ 2025 y extras

### Configuracion de VS Code
- `.vscode/` agregado a `.gitignore`: la configuracion del editor es local de cada integrante y no se versiona

## 2026-10-17

### Estructura inicial del repositorio
- Creacion de estructura de carpetas: `DATA/RAW/ZIPS`, `DATA/RAW/<dataset>`, `DATA/PREPROCESSED`, `DATA/DOCS`
- `pyproject.toml` con dependencias del proyecto (UV, Python 3.12)
- `src/descarga_inicial.py`: script standalone para descarga de 9 ZIPs y 4 PDFs
- `notebooks/01_ingesta_datos.ipynb`: notebook de ingesta con 16 secciones
  - Descarga de ZIPs a `DATA/RAW/ZIPS/`
  - Descarga de PDFs a `DATA/DOCS/`
  - Extraccion de CSVs a `DATA/RAW/<dataset>/`
  - Consolidacion a Parquet en `DATA/PREPROCESSED/` usando PyArrow ParquetWriter (escritura secuencial para evitar OOM con ~55M filas)
  - Columnas DEF y DEL forzadas a string por tipos mixtos en CSVs originales
- `DATA/DOCS/KNOWLEDGE_BASE.md`: documentacion del proyecto, datos, variables, estado
- `DATA/DOCS/CHANGELOG.md`: este archivo
