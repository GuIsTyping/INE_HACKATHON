# Instrucciones del Proyecto

## Regla principal: Knowledge Base y Bitacora

Antes de cada accion en el proyecto, lee `DATA/DOCS/KNOWLEDGE_BASE.md`.
Despues de cada cambio, actualiza su contenido:

- **Agregar** informacion nueva: archivos, rutas, objetivos, hallazgos, variables, estado.
- **Modificar** informacion que cambio: rutas renombradas, datos actualizados, estado de tareas.
- **Eliminar** informacion obsoleta que ya no aplica.

La Knowledge Base NO es una bitacora. Solo contiene estado actual, nunca historial.
La bitacora de cambios es `DATA/DOCS/CHANGELOG.md`: registra ahi que se hizo y cuando.

## Estructura del repositorio

```
DATA/RAW/ZIPS/          ZIPs descargados del INE
DATA/RAW/<dataset>/     CSVs extraidos (uno por dataset/ano)
DATA/PREPROCESSED/      Parquets consolidados (listos para analisis)
DATA/DOCS/              PDFs, KNOWLEDGE_BASE.md, CHANGELOG.md
src/                    Scripts standalone
notebooks/              Jupyter notebooks (numerados por orden de ejecucion)
```

## Estilo de codigo y notebooks

- Celdas pequenas: cada celda hace un solo paso, con su subtitulo markdown y texto explicativo breve.
- Sin emojis en documentacion ni codigo.
- Texto conciso, sin exceso. Codigo modesto y legible.
- Sin comentarios innecesarios en el codigo; solo cuando el "por que" no es obvio.

## Convenciones de datos

- Cada ZIP del INE contiene UN solo ano de eleccion, no todos los anos.
- Los diccionarios dentro de cada ZIP listan todos los valores posibles del sistema (todas las elecciones), pero el CSV solo contiene datos del ano correspondiente a ese ZIP.
- Columnas DEF y DEL tienen tipos mixtos en los CSV originales: siempre leer con `dtype={"DEF": str, "DEL": str}`.
- El parquet federal se escribe con PyArrow ParquetWriter (un row group por ano) para no cargar ~55M filas en memoria de una vez.

## Flujo de trabajo

1. **Descarga y extraccion:** `src/descarga_inicial.py` o `notebooks/01_ingesta_datos.ipynb`
   - ZIPs -> `DATA/RAW/ZIPS/`
   - CSVs extraidos -> `DATA/RAW/<dataset>/`
   - PDFs -> `DATA/DOCS/`
   - Parquets consolidados -> `DATA/PREPROCESSED/`

2. **Analisis:** notebooks subsecuentes leen de `DATA/PREPROCESSED/`.

## Proyecto: INE Hackaton 2026

- **Reto 1:** Perfiles ciudadanos de participacion (segmentacion sociodemografica)
- **Entrega:** 31 octubre 2026, 23:59 hrs
- **Destinatarios:** grecia.castro@ine.mx y cirse.rodriguez@ine.mx
- **Entregables:** documento tecnico (8-12 cuartillas, 4-6 perfiles), fichas de perfil (infografia/dashboard), presentacion ejecutiva (max 10 diapositivas), codigo/repositorio, cartas firmadas.

## Estado actual

La ingesta de datos esta completa. Los siguientes pasos pendientes son:

- Analisis exploratorio
- Idear 5 maneras innovadoras de abordar el problema
- Diseno de metodologia de segmentacion / clustering
- Implementacion
- Caracterizacion de perfiles
- Propuesta de estrategias diferenciadas
- Documento tecnico, fichas de perfil, presentacion ejecutiva

Consulta `DATA/DOCS/KNOWLEDGE_BASE.md` para detalles completos de datos, variables, indicadores y plataforma CCPC.
