# INE Hackatón 2026 - Perfiles Ciudadanos de Participación

Reto 1: Segmentación sociodemográfica de la participación ciudadana a partir de los Conteos Censales del INE (2009-2025).

**Autores:** Ángel David Durazo Bartolini y Jehú Jonathan Ramírez Ramírez

## Requisitos

- [UV](https://docs.astral.sh/uv/) (gestor de entornos Python)
- Python 3.12+

## Instalación

```bash
git clone https://github.com/GuIsTyping/INE_HACKATHON.git
cd INE_HACKATHON
uv sync
```

Esto crea el entorno virtual e instala todas las dependencias definidas en `pyproject.toml`.

## Descarga de datos

Los datos NO están incluidos en el repositorio (son ~4 GB de CSVs). Hay dos formas de obtenerlos:

### Opción A: Script standalone

```bash
uv run python src/descarga_inicial.py
```

Descarga los 9 ZIPs del INE, los extrae y descarga los PDFs de referencia.

### Opción B: Notebook interactivo

```bash
uv run jupyter notebook notebooks/01_ingesta_datos.ipynb
```

Ejecuta las celdas en orden. Además de descargar y extraer, consolida los CSVs en archivos Parquet listos para análisis.

## Orden de ejecución

| Paso | Archivo | Qué hace |
|---|---|---|
| 1 | `notebooks/01_ingesta_datos.ipynb` | Descarga ZIPs, extrae CSVs, consolida a Parquet |
| 2 | `notebooks/02_perfilado_datos.ipynb` | Perfilado de calidad, cobertura y participación |
| 3 | `notebooks/03_analisis_exploratorio.ipynb` | Historial por sección y celda; indicadores de comportamiento |
| 4 | `notebooks/04_segmentacion.ipynb` | Segmentación nacional K-Means (exploratoria) |
| 5 | `notebooks/05_experimentos_clustering.ipynb` | Búsqueda en malla de 2,028 configuraciones de clustering |
| 6 | `notebooks/06_experimentos_forma_embeddings.ipynb` | Clustering con UMAP/t-SNE y variables de forma |
| 7 | `notebooks/07_segmentacion_jerarquica.ipynb` | Segmentación jerárquica (microsegmentos + Ward) |
| 8 | `notebooks/08_clases_latentes.ipynb` | Análisis de Clases Latentes (LCA) - segmentación final |
| 9 | `notebooks/09_subperfiles_anidados.ipynb` | 27 subperfiles dentro de las 6 clases latentes |
| 10 | `notebooks/10_escolaridad_eceg.ipynb` | Escolaridad e internet por sección (ECEG 2020) |
| 11 | `notebooks/11_fichas_y_mapa.ipynb` | Fichas de perfil (PNG/PDF) y mapa interactivo |

## Mapa interactivo

El notebook 11 genera un mapa interactivo en `DATA/PREPROCESSED/fichas/mapa_clases_latentes.html`. Los tiles del mapa (Stadia Maps) requieren servirse desde un servidor HTTP, no se pueden abrir directamente como archivo local.

Para visualizar el mapa:

```bash
cd DATA/PREPROCESSED/fichas
python -m http.server 8765
```

Luego abrir en el navegador: `http://localhost:8765/mapa_clases_latentes.html`

El mapa incluye capas municipal y estatal con el perfil dominante por territorio, popups con detalles y un panel lateral con los 6 perfiles.

## Estructura de carpetas

```
INE_HACKATHON/
  pyproject.toml              Dependencias (UV)
  src/
    descarga_inicial.py       Script de descarga y extracción
  notebooks/
    01 a 11                   Pipeline completo (ingesta a visualización)
  DATA/
    RAW/ZIPS/                 ZIPs descargados
    RAW/<dataset>/            CSVs extraídos por dataset
    PREPROCESSED/             Parquets consolidados
    PREPROCESSED/fichas/      Fichas PNG/PDF y mapa interactivo
    DOCS/                     PDFs, documento técnico, estrategias, Knowledge Base
```

## Datos generados (en DATA/PREPROCESSED/)

| Archivo | Contenido | Filas |
|---|---|---|
| `conteos_federal_2009_2024.parquet` | Elecciones federales 2009-2024 | 54,872,712 |
| `conteos_pj2025.parquet` | Elección Poder Judicial 2025 | 9,835,254 |
| `voto_anticipado_2024.parquet` | Voto anticipado 2024 | 3,449 |
| `prision_preventiva_2024.parquet` | Voto en prisión preventiva 2024 | 26,563 |
| `secciones_historial.parquet` | Historial e indicadores por sección | 54,892 |
| `celdas_historial.parquet` | Historial por sección x sexo x grupo de edad | 657,497 |
| `celdas_clases_latentes.parquet` | Asignación probabilística a 6 clases latentes | 657,497 |
| `celdas_subperfiles.parquet` | 27 subperfiles anidados | 657,497 |
| `secciones_eceg_2020.parquet` | Escolaridad e internet por sección (ECEG) | 68,806 |

## Entregables

| Documento | Archivo |
|---|---|
| Documento técnico (10 páginas, Calibri 11) | `DATA/DOCS/documento_tecnico.md` / `.pdf` |
| Estrategias diferenciadas por perfil | `DATA/DOCS/estrategias_por_perfil.md` |
| Presentación ejecutiva (10 diapositivas) | `DATA/DOCS/presentacion_ejecutiva.pptx` |
| Fichas de perfil (PNG 200 dpi + PDF) | `DATA/PREPROCESSED/fichas/` |
| Mapa interactivo | `DATA/PREPROCESSED/fichas/mapa_clases_latentes.html` |

## Documentación

- `DATA/DOCS/KNOWLEDGE_BASE.md` - Estado actual del proyecto, descripción de datos y variables
- `DATA/DOCS/CHANGELOG.md` - Bitácora de cambios
