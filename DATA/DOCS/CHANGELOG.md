# Bitacora de Cambios

## 2026-10-18

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
