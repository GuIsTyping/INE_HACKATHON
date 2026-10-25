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
    02_perfilado_datos.ipynb  Calidad, cobertura y participacion por variable
    03_analisis_exploratorio.ipynb  Historial por seccion y celda, cohortes, regiones, PJ 2025
    04_segmentacion.ipynb         Clustering nacional ponderado + mapa nacional interactivo
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
      marco_geoestadistico/  Shapefile CONABIO municipios 2022 (mun22gw.*)
    PREPROCESSED/
      conteos_federal_2009_2024.parquet   54,872,712 filas (184 MB)
      conteos_pj2025.parquet              9,835,254 filas (76 MB)
      voto_anticipado_2024.parquet        3,449 filas
      prision_preventiva_2024.parquet     26,563 filas
      secciones_historial.parquet         54,892 filas (generado en 03)
      celdas_historial.parquet            657,497 filas (generado en 03)
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

## Hallazgos del Perfilado (`02_perfilado_datos.ipynb`)

### Calidad
- Sin nulos en ningun dataset. `LN = SV + NV + NS` en el 100% de registros (federal y PJ 2025); ningun registro con LN = 0.
- % NS sobre LN por ano: 2009 2.4, 2012 0.2, 2015 6.1, 2018 6.8, 2021 4.3, 2024 6.4. Por eso la participacion se calcula sobre SV + NV.
- EDAD va de 18 a 140. Los valores altos NO son codigos: el diccionario de los ZIPs no define valores especiales, el manual CCPC trata EDAD como edad real (su ultimo grupo quinquenal es "100+") y la distribucion decrece suave sin picos.
  - Los registros envejecen entre elecciones (misma seccion y sexo, edad + 3 anos): 2021->2024 permanece 48% del grupo 90-99, 23% de 100-109 y 21% de 110+.
  - 90-99: 2.2M personas en LN acumulada, participacion 26% (real). 100-109: 127 mil, participacion 11% (centenarios reales mas fallecidos no dados de baja). 110+: 4,319, participacion 12-27% (biologicamente imposible en esa cantidad; con votos registrados, lo que apunta a fechas de nacimiento mal capturadas).
  - 2009 tiene muchos mas centenarios que los demas anos (100 anos: 8,573 vs 3,864 en 2012); compatible con una depuracion posterior del padron (no confirmado en documentos).
  - Impacto minimo: 100+ es 0.02% de la LN acumulada y 110+ es 0.001%. Se agrupan en 80+; excluir EDAD > 110 es opcional.
- SEXO = 2 solo en 2024 con 105 personas.
- Nombres de entidad distintos entre datasets (ej. `VERACRUZ` vs `VERACRUZ DE IGNACIO DE LA LLAVE`): unir por clave.
- Voto anticipado y prision preventiva son un registro por voto (sin edad ni seccion). En prision preventiva la clave de entidad es `ESTADO`.

### Cobertura
- 32 entidades en todos los anos federales (PJ 2025: 31). Municipios 2,455-2,477; secciones 64,934 (2009) a 70,751 (2024).
- 72,681 secciones distintas (EDOCVE + SECCION); 62,048 (85%) presentes en las 6 elecciones federales.

### Participacion (SV / (SV + NV))
| Ano | 2009 | 2012 | 2015 | 2018 | 2021 | 2024 |
|---|---|---|---|---|---|---|
| Nacional | 44.1 | 62.1 | 47.1 | 62.4 | 51.8 | 59.7 |
| Hombre | 40.5 | 57.8 | 43.0 | 58.1 | 47.8 | 54.8 |
| Mujer | 47.4 | 66.1 | 50.9 | 66.3 | 55.6 | 64.2 |

- Presidenciales (2012, 2018, 2024) ~60-62%; intermedias 44-52%.
- Edad: minimo en 25-29, maximo en 60-79, cae en 80+.
- Rural > urbano en intermedias (2021: 58.4 vs 50.1); casi igual en presidenciales.
- 2024 por entidad: maximo Yucatan 71.5, minimo Baja California 47.1; norte por debajo del promedio.
- PJ 2025: 13.0% de participacion, mismo gradiente por edad (7.8% en 25-29, 22.1% en 70-79).
- Voto anticipado 2024: 3,449 votos, 62% mujeres. Prision preventiva 2024: 26,563 votos, 91% hombres.

### Grupos de edad usados
18-24, 25-29, 30-39, 40-49, 50-59, 60-69, 70-79, 80+

## Hallazgos del Analisis Exploratorio (`03_analisis_exploratorio.ipynb`)

### Tablas para segmentacion
| Archivo | Unidad | Filas | Columnas clave |
|---|---|---|---|
| `secciones_historial.parquet` | EDOCVE + SECCION | 54,892 | P2009..P2024, promedio, desviacion, brecha_pres, tendencia, TIPOSEC, LN2024, REGION, P_PJ2025 |
| `celdas_historial.parquet` | EDOCVE + SECCION + SEXO + GRUPO_EDAD | 657,497 | P2009..P2024, promedio, desviacion, brecha_pres, tendencia, TIPOSEC, REGION |

- Indicadores: `promedio` (nivel), `desviacion` (estabilidad), `brecha_pres` (promedio 2012/2018/2024 - promedio 2009/2015/2021), `tendencia` (pendiente en puntos por eleccion).
- Secciones: solo las que tienen tasa valida en las 6 elecciones (cubren 80M de 98M de LN 2024). 9,438 seccion-ano tienen todo el padron en NS.
- Celdas: 6 elecciones y al menos 20 votantes potenciales (SV + NV) en cada una. La celda no sigue a las mismas personas.

### Regiones (por EDOCVE)
| Region | EDOCVE |
|---|---|
| Noroeste | 2, 3, 8, 10, 25, 26 |
| Noreste | 5, 19, 28 |
| Occidente | 1, 6, 11, 14, 16, 18, 32 |
| Centro | 9, 13, 15, 17, 21, 22, 24, 29 |
| Sur-Sureste | 4, 7, 12, 20, 23, 27, 30, 31 |

### Hallazgos
- Noroeste es la region con menor participacion en todos los anos (51.0 en 2024). Centro y Sur-Sureste son las mas altas y las de mayor brecha presidencial.
- Efecto de primera eleccion: la cohorte 2000s tuvo 64.8 en 2018 y 46.8 en 2021. Las cohortes 1940s-1960s son las mas participativas.
- Persistencia alta entre elecciones del mismo tipo (correlacion 0.66-0.82 a nivel seccion).
- Brecha presidencial: mediana +13 puntos; urbano 15.3, rural 8.5. Tendencia: mediana +2.1 puntos por eleccion.
- `desviacion`, `brecha_pres` y `tendencia` estan correlacionadas (0.58-0.75) y casi no con `promedio`.
- PJ 2025 vs federal promedio: correlacion 0.28 (dimension distinta).
- Eta cuadrada del promedio por celda: seccion 41%, grupo de edad 39%, entidad 12%, region 7%, sexo 6%, tipo de seccion 1%.
- Mujeres participan mas que hombres hasta 60-69; desde 70-79 se invierte.

## Segmentacion nacional y mapa interactivo (`04_segmentacion.ipynb`)

### Enfoque

Clustering conductual ponderado por lista nominal: los perfiles emergen del
comportamiento electoral (promedio, brecha_pres, tendencia), no de la demografia.
K-Means con sample_weight = SV+NV de 2024 (71.2M personas).
Caracterizacion post-clustering por edad, sexo, region, tipo de seccion y PJ 2025.

### Perfiles nacionales (k=4)

| Perfil | Personas | % | Prom | Brecha | Tend | %Mujer | PJ2025 | Descripcion |
|---|---|---|---|---|---|---|---|---|
| 0 | 19.9M | 28% | 42.8 | +16.9 | +1.6 | 37% | 12.1 | Jovenes (18-29), mayoria hombres, urbanos, baja participacion (sensibles a presidenciales) |
| 1 | 13.5M | 19% | 49.5 | +5.7 | -1.8 | 41% | 10.3 | Adultos (30-49), semi-rurales, participacion moderada (estables entre elecciones, en descenso) |
| 2 | 17.8M | 25% | 59.6 | +20.9 | +4.5 | 65% | 15.1 | Edad diversa, mayoria mujeres, urbanos, participacion media-alta (sensibles a presidenciales, en ascenso) |
| 3 | 19.9M | 28% | 69.3 | +8.6 | +1.2 | 64% | 14.1 | Adultos maduros (50+), mayoria mujeres, semi-rurales, alta participacion |

### Datos geograficos

Shapefile de division politica municipal 2022, fuente CONABIO/INEGI (coordenadas geograficas EPSG:4326).
Descargado de `http://www.conabio.gob.mx/informacion/gis/maps/geo/mun22gw.zip`, almacenado en `DATA/RAW/marco_geoestadistico/`.
Descarga integrada en `src/descarga_inicial.py`.

### Fichas de perfil (seccion 5.7)

Una figura matplotlib por perfil que consolida: trayectoria 2009-2024 (vs promedio nacional gris),
panel de metricas (promedio, brecha, tendencia, genero, tipo de seccion, PJ 2025),
distribucion de edad (vs nacional), distribucion regional (vs nacional) y top 5 entidades.
Los datos del CCPC no incluyen escolaridad, ingreso ni autoadscripcion indigena/afromexicana.

### Mapa nacional interactivo

Tiles CARTO CDN (light_all). Dos capas con folium LayerControl (esquina superior derecha):
1. **Estatal:** 32 entidades, perfil dominante con popup de distribucion (nombre + porcentaje).
2. **Municipal:** 2,475 municipios (1,858 con clustering local, 518 bloqueados por muestra <30 celdas).
   Popup con distribucion de perfiles + clustering local con detalle demografico (sexo, edad).

Panel lateral izquierdo desplegable con fichas de los 4 perfiles nacionales (nombre auto-generado, stats, genero, edad, tipo de seccion).

Los nombres de perfil se generan automaticamente con `generar_nombre_perfil()` a partir de condiciones
sobre la distribucion de edad, genero y tipo de asentamiento del cluster, combinadas con el nivel de
participacion, brecha y tendencia. No hay nombres hardcodeados.
Geometrias simplificadas (tolerancia 0.008 municipal, 0.01 estatal). HTML ~24 MB.

### Archivos generados

| Archivo | Contenido |
|---|---|
| `celdas_perfiladas.parquet` | 657,497 celdas nacionales con perfil y peso |
| `resumen_perfiles.csv` | 4 perfiles con estadisticas ponderadas y nombre descriptivo |
| `resumen_municipios.csv` | 1,858 municipios con k local y perfil dominante |
| `mapa_nacional_segmentacion.html` | Mapa interactivo folium con 2 capas y panel (~24 MB) |

## Entorno

- **Gestor:** UV (reproducible con `uv sync`)
- **Python:** 3.12 (fijado en `.python-version`; `uv sync` lo respeta aunque haya otras versiones instaladas)
- **Dependencias:** pandas, numpy, matplotlib, seaborn, scikit-learn, jupyter, requests, tqdm, pyarrow, geopandas, folium

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

**Agrupaciones de edad oficiales del CCPC (manual, pag. 12):**
- Etapa de vida: Juventud 18-24, Adulta Joven 25-34, Adulta 35-44, Adulta Plena 45-59, Adulta Mayor 60+.
- Grupo quinquenal: 18-19, 20-24, 25-29, ..., 95-99, 100+.
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
- [x] Perfilado de datos
- [x] Analisis exploratorio
- [x] Segmentacion nacional ponderada (k=4, 71.2M personas) con caracterizacion completa
- [x] Mapa nacional interactivo con 2 capas (estatal + municipal) y clustering local en 1,858 municipios
- [ ] Propuesta de estrategias
- [ ] Documento tecnico
- [ ] Fichas de perfil
- [ ] Presentacion ejecutiva
