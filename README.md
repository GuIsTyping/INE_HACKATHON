# INE Hackaton 2026 - Perfiles Ciudadanos de Participación

Reto 1: Segmentación sociodemográfica de la participación ciudadana a partir de los Conteos Censales del INE (2009-2025).

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
| 3 | `notebooks/03_analisis_exploratorio.ipynb` | Historial por sección y celda; genera tablas para segmentación |
| 4 | (pendiente) | Segmentación / clustering |

## Estructura de carpetas

```
INE_HACKATHON/
  CLAUDE.md                 Instrucciones para Claude Code
  pyproject.toml            Dependencias (UV)
  src/
    descarga_inicial.py     Script de descarga y extracción
  notebooks/
    01_ingesta_datos.ipynb  Ingesta completa (descarga + consolidación)
    02_perfilado_datos.ipynb  Perfilado de datos
    03_analisis_exploratorio.ipynb  Análisis exploratorio
  DATA/
    RAW/ZIPS/               ZIPs descargados
    RAW/<dataset>/          CSVs extraidos por dataset
    PREPROCESSED/           Parquets consolidados
    DOCS/                   PDFs, Knowledge Base, Bitacora
```

## Datos generados (en DATA/PREPROCESSED/)

| Archivo | Contenido | Filas |
|---|---|---|
| `conteos_federal_2009_2024.parquet` | Elecciones federales 2009-2024 | 54,872,712 |
| `conteos_pj2025.parquet` | Elección Poder Judicial 2025 | 9,835,254 |
| `voto_anticipado_2024.parquet` | Voto anticipado 2024 | 3,449 |
| `prision_preventiva_2024.parquet` | Voto en prisión preventiva 2024 | 26,563 |
| `secciones_historial.parquet` | Historial e indicadores por sección (notebook 03) | 54,892 |
| `celdas_historial.parquet` | Historial e indicadores por sección x sexo x grupo de edad (notebook 03) | 657,497 |

## Documentación

- `DATA/DOCS/KNOWLEDGE_BASE.md` - Estado actual del proyecto, descripción de datos y variables
- `DATA/DOCS/CHANGELOG.md` - Bitácora de cambios
