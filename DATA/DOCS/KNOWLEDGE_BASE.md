# Knowledge Base - Hackea la Participacion (INE Hackaton 2026)

## Objetivo del Proyecto

Participar en el **Reto 1: Perfiles ciudadanos de participacion** (Eje: Segmentacion sociodemografica) del hackaton "Hackea la participacion: Datos que construyen democracia" organizado por el INE.

**Pregunta guia:** Que tipos de ciudadania existen segun su comportamiento de participacion?

**Utilidad para el INE:** Diseno de campanas focalizadas y mensajes diferenciados por perfil.

## Fechas Clave

- Registro: 1 sep - 15 oct 2026
- Entrega: 31 oct 2026, 23:59 hrs
- Envio a: grecia.castro@ine.mx y cirse.rodriguez@ine.mx

## Entregables Obligatorios (Reto 1)

### Generales
- Presentacion ejecutiva (max 10 diapositivas)
- Codigo o enlace a repositorio
- Carta de cesion de derechos (firmada por todos)
- Carta declaratoria de decir verdad (firmada por todos)

### Especificos Reto 1
- **Documento tecnico:** 8-12 cuartillas (PDF, Arial/Calibri 11, interlineado 1.5) con 4-6 perfiles ciudadanos, metodologia de segmentacion y estrategias diferenciadas
- **Fichas de Perfil (Infografia/Dashboard):** PDF/PNG alta resolucion con resumen narrativo e iconografico de cada perfil

## Que Debemos Hacer

1. Definir y aplicar metodo de segmentacion (clustering u otra tecnica) sobre datos de participacion
2. Caracterizar cada grupo con: edad, sexo, posible escolaridad, region, historial de participacion
3. Nombrar y describir cada perfil narrativa y visualmente
4. Proponer estrategias diferenciadas de fomento a la participacion por perfil

## Criterios de Evaluacion (100 pts)

| Criterio | Peso | Puntos |
|---|---|---|
| Apego a la tematica | 35% | 35 |
| Claridad y solidez de la propuesta | 30% | 30 |
| Originalidad y creatividad | 20% | 20 |
| Viabilidad para aprovechamiento institucional | 15% | 15 |

## Estructura del Repositorio

```
INE_HACKATHON/
  pyproject.toml              Entorno UV (dependencias reproducibles)
  .python-version             Version de Python fijada (3.12)
  src/
    descarga_inicial.py       Script standalone de descarga y extraccion
  notebooks/
    01_ingesta_datos.ipynb    Descarga, extraccion y consolidacion
  DATA/
    RAW/
      ZIPS/                   ZIPs descargados del INE
      conteos2009/            CSVs extraidos (32 por entidad)
      conteos2012/
      conteos2015/
      conteos2018/
      conteos2021/
      conteos2024/
      conteosPJ2025/          31 CSVs (sin entidad 32)
      voto_anticipado_2024/   1 CSV
      prision_preventiva_2024/ 1 CSV
    PREPROCESSED/
      conteos_federal_2009_2024.parquet   54,872,712 filas (184 MB)
      conteos_pj2025.parquet              9,835,254 filas (76 MB)
      voto_anticipado_2024.parquet        3,449 filas
      prision_preventiva_2024.parquet     26,563 filas
    DOCS/
      KNOWLEDGE_BASE.md       Este archivo
      CHANGELOG.md            Bitacora de cambios
      *.pdf                   Convocatoria, cartas, manual CCPC
```

## Datos Disponibles

### Datasets Federales (conteos 2009-2024)

Cada ZIP contiene un solo ano de eleccion. 32 CSVs por entidad federativa.

| Dataset | Filas | Columnas | Marco cartografico |
|---|---|---|---|
| conteos2009 | ~8.7M | 16 (estandar) | DERFE 2021 |
| conteos2012 | ~8.6M | 16 (estandar) | DERFE 2021 |
| conteos2015 | ~9.1M | 16 (estandar) | DERFE 2021 |
| conteos2018 | ~9.3M | 16 (estandar) | DERFE 2021 |
| conteos2021 | ~9.4M | 16 (estandar) | DERFE 2021 |
| conteos2024 | ~9.8M | 16 (SEXO incluye 2=NB) | DERFE 2023 |

Columnas estandar: AELEC, FELECCION, EDOCVE, EDONOM, MPIOCVE, MPIONOM, SECCION, TIPOSEC, DEF, DEL, SEXO, EDAD, LN, SV, NV, NS

### Dataset PJ 2025 (conteosPJ2025)

- 31 CSVs, ~9.8M filas
- Columnas: AELEC, EDOCVE, EDONOM, MPIOCVE, MPIONOM, SECCION, TIPOSEC, DEF, CJ, DEJ, SEXO, EDAD, LN, SV, NV, NS
- Diferencias: sin FELECCION, sin DEL; usa CJ (Circuito Judicial) y DEJ (Distrito Judicial Electoral)
- Marco cartografico: DERFE 2025

### Descripcion de Variables Comunes

| Variable | Descripcion |
|---|---|
| AELEC | Ano de eleccion |
| FELECCION | Fecha de jornada electoral (no en PJ2025) |
| EDOCVE/EDONOM | Clave y nombre de entidad federativa |
| MPIOCVE/MPIONOM | Clave y nombre de municipio |
| SECCION | Seccion electoral |
| TIPOSEC | Tipo de seccion (U=Urbana, M=Mixta, R=Rural) |
| DEF | Distrito Electoral Federal |
| DEL | Distrito Electoral Local (no en PJ2025) |
| CJ | Circuito Judicial (solo PJ2025) |
| DEJ | Distrito Judicial Electoral (solo PJ2025) |
| SEXO | 0=Hombre, 1=Mujer, 2=No binario (2 solo desde 2024) |
| EDAD | Anos cumplidos al dia de la eleccion |
| LN | Lista nominal (total registros en cuadernillo) |
| SV | Registros con marca de voto (Si Voto) |
| NV | Registros sin marca de voto (No Voto) |
| NS | No especificados (cuadernillos no disponibles, etc.) |

### Notas sobre los datos
- Fuente: cuadernillos de lista nominal de casillas aprobadas por consejos distritales
- NO incluye: votos en casillas especiales ni voto desde el extranjero
- La seccion corresponde al lugar de residencia en la credencial electoral
- Son datos agregados, sin datos personales
- Columnas DEF y DEL tienen tipos mixtos en los CSV originales (se almacenan como string en los parquet)

### Datasets Procesados (Parquet)

El parquet federal se escribio con PyArrow ParquetWriter (un row group por ano) para evitar cargar los ~55M de filas en memoria de una vez.

| Archivo | Filas | Tamano |
|---|---|---|
| `conteos_federal_2009_2024.parquet` | 54,872,712 | 184.3 MB |
| `conteos_pj2025.parquet` | 9,835,254 | 76.0 MB |
| `voto_anticipado_2024.parquet` | 3,449 | <0.1 MB |
| `prision_preventiva_2024.parquet` | 26,563 | <0.1 MB |

## Entorno

- **Gestor:** UV (reproducible con `uv sync`)
- **Python:** 3.12 (fijado en `.python-version`; `uv sync` lo respeta aunque haya otras versiones instaladas)
- **Dependencias:** pandas, numpy, matplotlib, seaborn, scikit-learn, jupyter, requests, tqdm, pyarrow

## Variables Sugeridas para Segmentacion

- Edad (rangos generacionales)
- Sexo
- Tipo de seccion (urbana/mixta/rural)
- Entidad federativa / region
- Historial de participacion por eleccion (2009-2024)
- Tasa de participacion (SV/LN)

## Plataforma CCPC

- **URL:** https://ine.mx/transparencia/datos-abiertos/visualizacion-datos/conteos-censales-participacion/
- **Manual de uso (PDF, 38 pags):** descargado en `DATA/DOCS/Manual_Conteos_Censales_2009_2024.pdf`
- **Tecnologia:** Tableau Desktop 2024.3.5
- **Cartografia base:** corte mayo 2023
- Dos secciones principales: **Elecciones Federales** (2009-2024) y **Poder Judicial** (2024-2025)

### 5 Tableros Interactivos (Elecciones Federales)

| Tablero | Contenido |
|---|---|
| **1. Datos Generales** | Resumen estadistico: LN, SV, NV, %Participacion, %Abstension, IML, IMV |
| **2. Datos Sociodemograficos** | Participacion por ano, grupo quinquenal, etapa de vida, mapa geografico |
| **3. Datos Comparativos** | Comparacion entre estados, anos, tipo seccion, cuartiles |
| **4. Voto Anticipado 2024** | Proporcion H/M, votacion por estado |
| **5. Voto en Prision Preventiva 2024** | Comportamiento votacion, proporcion H/M, mapa |

### Indicadores Clave
- % Participacion = SV / (SV + NV)
- % Abstension = NV / (SV + NV)
- IML = (Hombres en LN / Mujeres en LN) x 100
- IMV = (Hombres que SV / Mujeres que SV) x 100

**Nota:** Los datos de poblacion indigena y afromexicana estan disponibles como FILTRO en los tableros interactivos pero NO aparecen como columna en los CSVs descargados.

## Estado del Proyecto

- [x] Lectura de convocatoria y rubrica
- [x] Extraccion y revision de datasets
- [x] Creacion de knowledge base
- [x] Revision de pagina INE y tableros interactivos
- [x] Lectura del manual de la plataforma CCPC (38 pags)
- [x] Configuracion de entorno UV (Python 3.12 + dependencias)
- [x] Notebook de ingesta de datos
- [x] Consolidacion de datos a Parquet (54.8M filas federales + 9.8M PJ + extras)
- [ ] Perfilado de datos
- [ ] Analisis exploratorio
- [ ] Diseno de metodologia de segmentacion
- [ ] Implementacion de clustering
- [ ] Caracterizacion de perfiles
- [ ] Propuesta de estrategias
- [ ] Documento tecnico
- [ ] Fichas de perfil
- [ ] Presentacion ejecutiva
