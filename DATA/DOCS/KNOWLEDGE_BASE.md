# Knowledge Base - Hackea la Participación (INE Hackaton 2026)

## Objetivo del Proyecto

Participar en el **Reto 1: Perfiles ciudadanos de participación** (Eje: Segmentación sociodemográfica) del hackaton "Hackea la participación: Datos que construyen democracia" organizado por el INE.

**Pregunta guia:** Que tipos de ciudadania existen segun su comportamiento de participación?

**Utilidad para el INE:** Diseño de campañas focalizadas y mensajes diferenciados por perfil.

## Fechas Clave

- Registro: 1 sep - 15 oct 2026
- Entrega: 31 oct 2026, 23:59 hrs
- Envio a: grecia.castro@ine.mx y cirse.rodriguez@ine.mx

## Entregables Obligatorios (Reto 1)

### Generales
- Presentación ejecutiva (max 10 diapositivas)
- Código o enlace a repositorio
- Carta de cesión de derechos (firmada por todos)
- Carta declaratoria de decir verdad (firmada por todos)

### Específicos Reto 1
- **Documento técnico:** 8-12 cuartillas (PDF, Arial/Calibri 11, interlineado 1.5) con 4-6 perfiles ciudadanos, metodología de segmentación y estrategias diferenciadas
- **Fichas de Perfil (Infografia/Dashboard):** PDF/PNG alta resolucion con resumen narrativo e iconografico de cada perfil

## Que Debemos Hacer

1. ~~Definir y aplicar método de segmentación~~ (completado: LCA k=6, ARI 0.98)
2. ~~Caracterizar cada grupo~~ (completado: edad, sexo, escolaridad, internet, región, historial)
3. ~~Nombrar y describir cada perfil~~ (completado: fichas PNG/PDF, mapa interactivo)
4. ~~Proponer estrategias diferenciadas~~ (completado: `DATA/DOCS/estrategias_por_perfil.md`)
5. ~~Documento técnico~~ (completado: `DATA/DOCS/documento_tecnico.pdf`, 8 páginas, Calibri 11, interlineado 1.5)
6. ~~Presentación ejecutiva~~ (completado: `DATA/DOCS/presentacion_ejecutiva.pptx`, 10 diapositivas)
7. Cartas firmadas (cesión de derechos + declaratoria) — pendiente (requiere firma del equipo)

## Criterios de Evaluación (100 pts)

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
  .python-versión             Versión de Python fijada (3.12)
  src/
    descarga_inicial.py       Script standalone de descarga y extracción
  notebooks/
    01_ingesta_datos.ipynb    Descarga, extracción y consolidación
    02_perfilado_datos.ipynb  Calidad, cobertura y participación por variable
    03_analisis_exploratorio.ipynb  Historial por sección y celda, cohortes, regiones, PJ 2025
    04_segmentacion.ipynb         Clustering nacional ponderado + mapa nacional interactivo
    05_experimentos_clustering.ipynb  Búsqueda en malla de variables, preprocesamiento y algoritmos (~19 min)
    06_experimentos_forma_embeddings.ipynb  Forma de trayectoria + UMAP/t-SNE (~37 min)
    07_segmentacion_jerarquica.ipynb  Microsegmentos KMeans + árbol Ward ponderado (perfil/subperfil/micro) (~2 min)
    08_clases_latentes.ipynb      Clases latentes sobre terciles por elección (~12 s)
    09_subperfiles_anidados.ipynb Clases latentes (o perfiles del 04) + subperfiles KMeans anidados + microtargeting (~20 s)
    10_escolaridad_eceg.ipynb     Escolaridad e internet por sección (ECEG 2020 INEGI-INE) unidos a celdas; por perfil y subperfil (~5 s)
    11_fichas_y_mapa.ipynb        Fichas PNG/PDF, vista general, mapa estático e interactivo de las clases latentes con escolaridad (~25 s)
  pruebas_locales/            Pruebas exploratorias no versionadas (en .gitignore); no forman parte del flujo
  DATA/
    RAW/
      ZIPS/                   ZIPs descargados del INE
      conteos2009/            CSVs extraidos (32 por entidad)
      conteos2012/
      conteos2015/
      conteos2018/
      conteos2021/
      conteos2024/
      conteosPJ2025/          31 CSVs (sin Campeche, entidad 4)
      voto_anticipado_2024/   1 CSV
      prision_preventiva_2024/ 1 CSV
      marco_geoestadistico/  Shapefile CONABIO municipios 2022 (mun22gw.*)
      eceg_2020/              Estadísticas Censales a Escalas Geoelectorales 2020 (INEGI): CSV por sección, distrito y entidad, diccionario y catálogos
    PREPROCESSED/
      conteos_federal_2009_2024.parquet   54,872,712 filas (184 MB)
      conteos_pj2025.parquet              9,835,254 filas (76 MB)
      voto_anticipado_2024.parquet        3,449 filas
      prision_preventiva_2024.parquet     26,563 filas
      secciones_historial.parquet         54,892 filas (generado en 03)
      celdas_historial.parquet            657,497 filas (generado en 03)
      experimentos_clustering.csv         2,028 configuraciones con métricas (generado en 05)
      experimentos_estabilidad.csv        18 candidatas con ARI bootstrap (generado en 05)
      experimentos_finalistas.csv         base_04 + 3 finalistas reajustadas (generado en 05)
      celdas_perfiles_candidatos.parquet  644,887 celdas con etiquetas de base_04 y finalistas (generado en 05)
      secciones_eceg_2020.parquet         68,806 secciones con escolaridad por sexo, % posbásica y % viviendas con internet (generado en 10)
      escolaridad_perfiles.csv, escolaridad_subperfiles.csv, escolaridad_perfil_tiposec.csv (generados en 10)
    DOCS/
      KNOWLEDGE_BASE.md       Este archivo
      CHANGELOG.md            Bitacora de cambios
      *.pdf                   Convocatoria, cartas, manual CCPC
```

## Datos Disponibles

### Datasets Federales (conteos 2009-2024)

Cada ZIP contiene un solo año de elección. 32 CSVs por entidad federativa.

| Dataset | Filas | Columnas | Marco cartográfico |
|---|---|---|---|
| conteos2009 | ~8.7M | 16 (estándar) | DERFE 2021 |
| conteos2012 | ~8.6M | 16 (estándar) | DERFE 2021 |
| conteos2015 | ~9.1M | 16 (estándar) | DERFE 2021 |
| conteos2018 | ~9.3M | 16 (estándar) | DERFE 2021 |
| conteos2021 | ~9.4M | 16 (estándar) | DERFE 2021 |
| conteos2024 | ~9.8M | 16 (SEXO incluye 2=NB) | DERFE 2023 |

Columnas estándar: AELEC, FELECCION, EDOCVE, EDONOM, MPIOCVE, MPIONOM, SECCIÓN, TIPOSEC, DEF, DEL, SEXO, EDAD, LN, SV, NV, NS

### Dataset PJ 2025 (conteosPJ2025)

- 31 CSVs, ~9.8M filas. No incluye Campeche (EDOCVE 4): `P_PJ2025` es nulo en todas sus secciones
- Columnas: AELEC, EDOCVE, EDONOM, MPIOCVE, MPIONOM, SECCIÓN, TIPOSEC, DEF, CJ, DEJ, SEXO, EDAD, LN, SV, NV, NS
- Diferencias: sin FELECCION, sin DEL; usa CJ (Circuito Judicial) y DEJ (Distrito Judicial Electoral)
- Marco cartográfico: DERFE 2025

### Descripción de Variables Comunes

| Variable | Descripción |
|---|---|
| AELEC | Año de elección |
| FELECCION | Fecha de jornada electoral (no en PJ2025) |
| EDOCVE/EDONOM | Clave y nombre de entidad federativa |
| MPIOCVE/MPIONOM | Clave y nombre de municipio |
| SECCIÓN | Sección electoral |
| TIPOSEC | Tipo de sección (U=Urbana, M=Mixta, R=Rural) |
| DEF | Distrito Electoral Federal |
| DEL | Distrito Electoral Local (no en PJ2025) |
| CJ | Circuito Judicial (solo PJ2025) |
| DEJ | Distrito Judicial Electoral (solo PJ2025) |
| SEXO | 0=Hombre, 1=Mujer, 2=No binario (2 solo desde 2024) |
| EDAD | Años cumplidos al dia de la elección |
| LN | Lista nominal (total registros en cuadernillo) |
| SV | Registros con marca de voto (Si Voto) |
| NV | Registros sin marca de voto (No Voto) |
| NS | No especificados (cuadernillos no disponibles, etc.) |

### Notas sobre los datos
- Fuente: cuadernillos de lista nominal de casillas aprobadas por consejos distritales
- NO incluye: votos en casillas especiales ni voto desde el extranjero
- La sección corresponde al lugar de residencia en la credencial electoral
- Son datos agregados, sin datos personales
- Columnas DEF y DEL tienen tipos mixtos en los CSV originales (se almacenan como string en los parquet)

### Datasets Procesados (Parquet)

El parquet federal se escribió con PyArrow ParquetWriter (un row group por año) para evitar cargar los ~55M de filas en memoria de una vez.

| Archivo | Filas | Tamaño |
|---|---|---|
| `conteos_federal_2009_2024.parquet` | 54,872,712 | 184.3 MB |
| `conteos_pj2025.parquet` | 9,835,254 | 76.0 MB |
| `voto_anticipado_2024.parquet` | 3,449 | <0.1 MB |
| `prision_preventiva_2024.parquet` | 26,563 | <0.1 MB |

## Hallazgos del Perfilado (`02_perfilado_datos.ipynb`)

### Calidad
- Sin nulos en ningún dataset. `LN = SV + NV + NS` en el 100% de registros (federal y PJ 2025); ningún registro con LN = 0.
- % NS sobre LN por año: 2009 2.4, 2012 0.2, 2015 6.1, 2018 6.8, 2021 4.3, 2024 6.4. Por eso la participación se calcula sobre SV + NV.
- EDAD va de 18 a 140. Los valores altos NO son códigos: el diccionario de los ZIPs no define valores especiales, el manual CCPC trata EDAD como edad real (su último grupo quinquenal es "100+") y la distribución decrece suave sin picos.
  - Los registros envejecen entre elecciones (misma sección y sexo, edad + 3 años): 2021->2024 permanece 48% del grupo 90-99, 23% de 100-109 y 21% de 110+.
  - 90-99: 2.2M personas en LN acumulada, participación 26% (real). 100-109: 127 mil, participación 11% (centenarios reales más fallecidos no dados de baja). 110+: 4,319, participación 12-27% (biológicamente imposible en esa cantidad; con votos registrados, lo que apunta a fechas de nacimiento mal capturadas).
  - 2009 tiene muchos más centenarios que los demás años (100 años: 8,573 vs 3,864 en 2012); compatible con una depuración posterior del padrón (no confirmado en documentos).
  - Impacto mínimo: 100+ es 0.02% de la LN acumulada y 110+ es 0.001%. Se agrupan en 80+; excluir EDAD > 110 es opcional.
- SEXO = 2 solo en 2024 con 105 personas.
- Nombres de entidad distintos entre datasets (ej. `VERACRUZ` vs `VERACRUZ DE IGNACIO DE LA LLAVE`): unir por clave.
- Voto anticipado y prisión preventiva son un registro por voto (sin edad ni sección). En prisión preventiva la clave de entidad es `ESTADO`.

### Cobertura
- 32 entidades en todos los años federales (PJ 2025: 31, falta Campeche). Municipios 2,455-2,477; secciones 64,934 (2009) a 70,751 (2024).
- 72,681 secciones distintas (EDOCVE + SECCIÓN); 62,048 (85%) presentes en las 6 elecciones federales.

### Participación (SV / (SV + NV))
| Año | 2009 | 2012 | 2015 | 2018 | 2021 | 2024 |
|---|---|---|---|---|---|---|
| Nacional | 44.1 | 62.1 | 47.1 | 62.4 | 51.8 | 59.7 |
| Hombre | 40.5 | 57.8 | 43.0 | 58.1 | 47.8 | 54.8 |
| Mujer | 47.4 | 66.1 | 50.9 | 66.3 | 55.6 | 64.2 |

- Presidenciales (2012, 2018, 2024) ~60-62%; intermedias 44-52%.
- Edad: mínimo en 25-29, máximo en 60-79, cae en 80+.
- Rural > urbano en intermedias (2021: 58.4 vs 50.1); casi igual en presidenciales.
- 2024 por entidad: máximo Yucatan 71.5, mínimo Baja California 47.1; norte por debajo del promedio.
- PJ 2025: 13.0% de participación, mismo gradiente por edad (7.8% en 25-29, 22.1% en 70-79).
- Voto anticipado 2024: 3,449 votos, 62% mujeres. Prisión preventiva 2024: 26,563 votos, 91% hombres.

### Grupos de edad usados
18-24, 25-29, 30-39, 40-49, 50-59, 60-69, 70-79, 80+

## Hallazgos del Análisis Exploratorio (`03_analisis_exploratorio.ipynb`)

### Tablas para segmentación
| Archivo | Unidad | Filas | Columnas clave |
|---|---|---|---|
| `secciones_historial.parquet` | EDOCVE + SECCIÓN | 54,892 | P2009..P2024, promedio, desviación, brecha_pres, tendencia, TIPOSEC, LN2024, REGIÓN, P_PJ2025 |
| `celdas_historial.parquet` | EDOCVE + SECCIÓN + SEXO + GRUPO_EDAD | 657,497 | P2009..P2024, promedio, desviación, brecha_pres, tendencia, TIPOSEC, REGIÓN |

- Indicadores: `promedio` (nivel), `desviacion` (estabilidad), `brecha_pres` (promedio 2012/2018/2024 - promedio 2009/2015/2021), `tendencia` (pendiente en puntos por elección).
- Secciones: solo las que tienen tasa valida en las 6 elecciones (cubren 80M de 98M de LN 2024). 9,438 sección-año tienen todo el padrón en NS.
- Celdas: 6 elecciones y al menos 20 votantes potenciales (SV + NV) en cada una. La celda no sigue a las mismas personas.

### Regiones (por EDOCVE)
| Región | EDOCVE |
|---|---|
| Noroeste | 2, 3, 8, 10, 25, 26 |
| Noreste | 5, 19, 28 |
| Occidente | 1, 6, 11, 14, 16, 18, 32 |
| Centro | 9, 13, 15, 17, 21, 22, 24, 29 |
| Sur-Sureste | 4, 7, 12, 20, 23, 27, 30, 31 |

### Hallazgos
- Noroeste es la región con menor participación en todos los años (51.0 en 2024). Centro y Sur-Sureste son las más altas y las de mayor brecha presidencial.
- Efecto de primera elección: la cohorte 2000s tuvo 64.8 en 2018 y 46.8 en 2021. Las cohortes 1940s-1960s son las más participativas.
- Persistencia alta entre elecciones del mismo tipo (correlación 0.66-0.82 a nivel sección).
- Brecha presidencial: mediana +13 puntos; urbano 15.3, rural 8.5. Tendencia: mediana +2.1 puntos por elección.
- `desviacion`, `brecha_pres` y `tendencia` están correlacionadas (0.58-0.75) y casi no con `promedio`.
- PJ 2025 vs federal promedio: correlación 0.28 (dimensión distinta).
- Eta cuadrada del promedio por celda: sección 41%, grupo de edad 39%, entidad 12%, región 7%, sexo 6%, tipo de sección 1%.
- Mujeres participan más que hombres hasta 60-69; desde 70-79 se invierte.

## Segmentación nacional y mapa interactivo (`04_segmentacion.ipynb`)

### Enfoque

Clustering conductual ponderado por lista nominal: los perfiles emergen del
comportamiento electoral (promedio, brecha_pres, tendencia), no de la demografia.
K-Means con sample_weight = SV+NV de 2024 (71.2M personas).
Caracterización post-clustering por edad, sexo, región, tipo de sección y PJ 2025.

### Perfiles nacionales (k=4)

| Perfil | Personas | % | Prom | Brecha | Tend | %Mujer | PJ2025 | Descripción |
|---|---|---|---|---|---|---|---|---|
| 0 | 19.9M | 28% | 42.8 | +16.9 | +1.6 | 37% | 12.1 | Jóvenes (18-29), mayoría hombres, urbanos, baja participación (sensibles a presidenciales) |
| 1 | 13.5M | 19% | 49.5 | +5.7 | -1.8 | 41% | 10.3 | Adultos (30-49), semi-rurales, participación moderada (estables entre elecciones, en descenso) |
| 2 | 17.8M | 25% | 59.6 | +20.9 | +4.5 | 65% | 15.1 | Edad diversa, mayoría mujeres, urbanos, participación media-alta (sensibles a presidenciales, en ascenso) |
| 3 | 19.9M | 28% | 69.3 | +8.6 | +1.2 | 64% | 14.1 | Adultos maduros (50+), mayoría mujeres, semi-rurales, alta participación |

### Datos geográficos

Shapefile de división política municipal 2022, fuente CONABIO/INEGI (coordenadas geograficas EPSG:4326).
Descargado de `http://www.conabio.gob.mx/informacion/gis/maps/geo/mun22gw.zip`, almacenado en `DATA/RAW/marco_geoestadistico/`.
Descarga integrada en `src/descarga_inicial.py`.

### Fichas de perfil (sección 5.7)

Una figura matplotlib por perfil que consolida: trayectoria 2009-2024 (vs promedio nacional gris),
panel de métricas (promedio, brecha, tendencia, género, tipo de sección, PJ 2025),
distribución de edad (vs nacional), distribución regional (vs nacional) y top 5 entidades.
Los datos del CCPC no incluyen escolaridad, ingreso ni autoadscripcion indígena/afromexicana. La escolaridad se agrega desde la ECEG 2020 en el notebook 10.

### Mapa nacional interactivo

Tiles CARTO CDN (light_all). Dos capas con folium LayerControl (esquina superior derecha):
1. **Estatal:** 32 entidades, perfil dominante con popup de distribución (nombre + porcentaje).
2. **Municipal:** 2,475 municipios (1,858 con clustering local, 518 bloqueados por muestra <30 celdas).
   Popup con distribución de perfiles + clustering local con detalle demográfico (sexo, edad).

Panel lateral izquierdo desplegable con fichas de los 4 perfiles nacionales (nombre auto-generado, stats, género, edad, tipo de sección).

Los nombres de perfil se generan automáticamente con `generar_nombre_perfil()` a partir de condiciones
sobre la distribución de edad, género y tipo de asentamiento del cluster, combinadas con el nivel de
participación, brecha y tendencia. No hay nombres hardcodeados.
Geometrías simplificadas (tolerancia 0.008 municipal, 0.01 estatal). HTML ~24 MB.

El mapa no se despliega dentro del notebook (embebido pesaria ~54 MB y GitHub no podría renderizarlo).
Se consulta abriendo `mapa_nacional_segmentacion.html`. El notebook se versiona con el resto de sus outputs (~1.3 MB).

**Error de cruce municipal:** el 04 une datos y shapefile por clave (`MPIOCVE` = `CVE_MUN`), pero las claves
municipales del INE no son las del INEGI: solo ~1,085 de 2,477 municipios coinciden en clave y nombre. Muchos
municipios del mapa muestran datos de otro municipio. El notebook 11 cruza por nombre.

### Archivos generados

| Archivo | Contenido |
|---|---|
| `celdas_perfiladas.parquet` | 657,497 celdas nacionales con perfil y peso |
| `resumen_perfiles.csv` | 4 perfiles con estadísticas ponderadas y nombre descriptivo |
| `resumen_municipios.csv` | 1,858 municipios con k local y perfil dominante |
| `mapa_nacional_segmentacion.html` | Mapa interactivo folium con 2 capas y panel (~24 MB) |

## Experimentos de clustering (`05_experimentos_clustering.ipynb`)

### Diseño
- Población: 644,887 celdas con peso y P_PJ2025 (96.4% del peso). **Este filtro excluye todo Campeche** (sin datos PJ 2025) y ~8k celdas de otras entidades; aplica a los notebooks 05, 06 y 07. Los notebooks 08-10 ya no lo aplican. Muestras extraidas con probabilidad proporcional al peso (eval 10k fija, fit 60k, sub 8k).
- 9 conjuntos de variables: A_base (promedio, brecha, tendencia), B_indicadores (+desviación, P_PJ2025), C_trayectoria (P2009..P2024), D_trayectoria_pj, E-H (conducta + edad ordinal, mujer, tipo de sección ordinal, región dummies), I_solo_demo (control).
- Preprocesamiento: estándar, robusto, estándar + PCA 90% (solo con más de 3 variables). 26 combinaciones.
- Algoritmos: KMeans, BisectingKMeans, Birch, GMM (4 covarianzas), aglomerativo (ward, average, complete), espectral, HDBSCAN. k de 3 a 8. 2,028 configuraciones.
- Métricas: sil, db, ch (espacio propio), sil_ref (espacio común: 6 tasas + PJ estandarizadas), r2_prom (eta cuadrada del promedio), V de Cramer con edad y sexo.
- Validez: k 4-6, perfil mínimo 5%, ruido máximo 10%. Puntaje = promedio de rangos de sil, sil_ref y r2_prom. Estabilidad: ARI medio en 5 bootstraps (umbral 0.8).

### Resultados
- 521 de 2,028 configuraciones validas. Silhouette máximo 0.31: los datos son un continuo, no grupos separados.
- Demografia como variable: descartada. Baja sil_ref (0.12 -> 0.00) y r2_prom (0.69 -> 0.36) y los perfiles se separan por sexo (V sexo 0.57; HDBSCAN en E_base_demo da V sexo = 1.0). Solo demografia: sil_ref negativo.
- Algoritmos descartados: aglomerativo average/complete (un cluster gigante), HDBSCAN (sin estructura de densidad; k fuera de rango o separa por sexo), Birch y aglomerativo ward (ARI < 0.5), espectral k=5 y GMM diag/tied en D (inestables).
- Ganador: C_trayectoria + estándar + PCA, k=4. GMM esferico, BisectingKMeans y KMeans dan casi la misma particion (ARI entre ellos 0.83-0.95; ARI bootstrap 0.93-0.98).
- Los finalistas son niveles de participación (promedio 35 / 49 / 62 / 75) con brecha y tendencia casi iguales entre perfiles. base_04 (A_base) separa tipos de conducta (brecha 5 a 22, tendencia -1.7 a +4.4) con menor separación. ARI base_04 vs finalistas: 0.20 (segmentaciones distintas).
- Sesgo del puntaje: r2_prom y sil_ref favorecen particiones por nivel, y el espacio de referencia es casi igual a C_trayectoria. La elección entre "niveles" (C) y "tipos de conducta" (A) queda pendiente del equipo.

## Forma de trayectoria y embeddings (`06_experimentos_forma_embeddings.ipynb`)

- Variables de forma: `F2009..F2024` (tasa menos promedio de la celda) y `Z2009..Z2024` (forma estandarizada por fila). Conjuntos: A_base, C_trayectoria (referencias), S_forma, S_forma_pj, S_forma_z.
- Embeddings sobre la muestra sub (8k): ninguno, UMAP (n_neighbors 15/50, min_dist 0.0/0.1, 2/5 dimensiones), t-SNE (perplejidad 30/100). Clustering en el embedding y extensión por KNN en el espacio original. Métricas siempre en el espacio original.
- Algoritmos: KMeans, GMM full, ward, HDBSCAN. 2,376 configuraciones. Dos puntajes: score_nivel (sil, sil_nivel, r2_prom) y score_forma (sil, sil_forma, r2_forma = eta cuadrada media de brecha y tendencia).
- Estabilidad con 3 bootstraps; finalistas: 2 por forma y 1 por nivel, más base_04 y ganador_05 como referencias.
- Salidas: `experimentos_forma_embeddings.csv`, `experimentos_forma_estabilidad.csv`, `experimentos_forma_finalistas.csv`, `celdas_perfiles_candidatos_forma.parquet`.
- 884 de 2,376 configuraciones validas.
- UMAP y t-SNE: descartados. No mejoran ninguna métrica frente a no usar embedding y son menos estables (UMAP sobre S_forma ARI 0.56-0.67; t-SNE 0.38). HDBSCAN sobre UMAP sigue sin estructura: 128 de 432 con ruido > 10%, solo 4 validas.
- Forma: S_forma + KMeans k=5 es estable (ARI 0.95). Perfiles con nivel parecido (promedio 51-61) pero brecha de 7.5 a 20.9 y tendencia de -1.8 a +5.1. Casi independientes de la demografia (V edad 0.14, V sexo 0.06) y ligados al territorio (rural o mixta de 14% a 49%).
- Nivel y forma son ejes ortogonales: ARI entre el ganador de nivel (C) y el de forma (S) = 0.03. La edad y el sexo explican el nivel, no la forma.
- base_04 (A_base) es el único balanceado: r2_prom 0.57 y r2_forma 0.58. Ganador_05 explica nivel (0.90) pero no forma (0.04); S_forma al reves (0.08 y 0.62).
- S_forma con y sin PCA producen la misma particion (ARI 1.0), por lo que dos finalistas de forma son duplicados; nivel_3 es identico a ganador_05.

## Segmentación jerárquica (`07_segmentacion_jerarquica.ipynb`)

Ejecutado con `VARIABLES = "A_base"` (~2 min).

- Etapa 1: KMeans ponderado con 50, 100 o 200 microsegmentos sobre todas las celdas; se elige el menor con R2 ponderado >= 0.95.
- Etapa 2: Ward ponderado (implementación propia, costo `w_a w_b / (w_a + w_b) ||c_a - c_b||^2`, salida en formato `linkage` de scipy) sobre los centros. Se valida contra el Ward de scipy con pesos iguales.
- Cortes: 4-6 perfiles (por silhouette) y 15 subperfiles, anidados. Perfiles numerados por promedio; subperfiles como `p.j`.
- Espacio configurable con `VARIABLES` (A_base, C_trayectoria, S_forma) y `USAR_PCA`; por defecto A_base hasta decidir niveles vs forma.
- Estabilidad por bootstrap de Poisson (3 réplicas), comparación ARI con `celdas_perfiles_candidatos.parquet`, tabla territorial por municipio.
- Salidas: `celdas_jerarquia.parquet`, `jerarquia_perfiles.csv`, `jerarquia_subperfiles.csv`, `jerarquia_microsegmentos.csv`, `jerarquia_municipios.csv`.

### Resultados
- N_MICRO = 200 (R2 0.961; 50 y 100 no llegan a 0.95). Microsegmentos de tamaño casi uniforme (0.09-0.9% de personas). Ward ponderado validado contra scipy (ARI 1.0).
- K = 4 por silhouette (0.20; base_04 tiene 0.26). R2 0.51 (k=4) a 0.60 (k=6). Subperfiles por perfil: 5, 2, 5, 3.
- **Inestable:** ARI bootstrap 0.33 (perfil) y 0.27 (subperfil). ARI vs base_04: 0.33. El árbol construido de abajo hacia arriba sobre un continuo cambia mucho entre remuestreos; el nivel macro no debe reemplazar a base_04.
- Subperfiles descriptivamente utiles (ej. 3.1: brecha -0.3 y tendencia -2.3, rural 53%, Occidente; 2.2: brecha 23 y tendencia +7.4; 0.5: brecha 29.5).
- Limitaciones de las tablas: `top_entidades` muestra los estados más poblados (México, CDMX, Veracruz) en casi todos los microsegmentos; conviene un índice de sobrerrepresentación. La tabla municipal ordenada por `pct_micro` muestra municipios muy chicos (20-50 personas) con 100% en un microsegmento; conviene filtrar por tamaño.

## Clases latentes (`08_clases_latentes.ipynb`)

Ejecutado (~12 s) sobre 657,497 celdas (71.2M personas): conserva las celdas sin PJ 2025, incluido Campeche.

- Indicadores: cada elección federal en terciles ponderados (baja, media, alta), relativos a esa elección. `INCLUIR_PJ` agrega PJ 2025 como septimo indicador (por defecto no).
- Celdas colapsadas a patrones unicos (máximo 729) con su peso; peso normalizado para sumar el número de celdas.
- EM propio (mezcla de categóricas con independencia local), 20 inicios, k de 2 a 8. Selección: menor BIC en 4-6 con clase mínima >= 5%; se reportan AIC, entropía relativa y mejora del BIC.
- Asignación modal por celda con `prob_clase`; asignación clara si prob >= 0.8.
- Bootstrap de Poisson (5 réplicas) y ARI contra base_04, candidato_1 (05), forma_1 (06) y perfil (07).
- Salidas: `celdas_clases_latentes.parquet`, `lca_seleccion_k.csv`, `lca_clases.csv`.

### Resultados
- 728 de 729 patrones observados. Los más comunes: siempre bajo (12.3% de personas) y siempre alto (11.3%).
- BIC baja en todo el rango (mejora 1.1% de 3 a 4 clases, < 0.3% desde 7). Elegido k = 6 (menor BIC en 4-6, clase mínima 8.3%). Entropía 0.78; 69.0% de personas con asignación clara.
- **Muy estable:** ARI bootstrap 0.98 (mínimo 0.95).
- Estructura nivel x forma emergente: los niveles medios se dividen por forma.

| Clase | % pob | Prom | Brecha | Tend | % mujer | Edad dominante | Asignación clara |
|---|---|---|---|---|---|---|---|
| 0 | 21.4 | 37.3 | 14.3 | +1.1 | 25 | 30-39 (87% < 40) | 92% |
| 1 | 8.3 | 48.5 | 7.6 | -1.6 | 44 | 30-39 | 44% |
| 2 | 18.6 | 50.5 | 18.4 | +3.0 | 53 | 30-39 | 59% |
| 3 | 16.3 | 60.3 | 9.3 | -0.1 | 57 | 40-49 | 57% |
| 4 | 11.8 | 62.0 | 19.5 | +4.5 | 68 | 40-49 | 51% |
| 5 | 23.5 | 72.8 | 10.6 | +1.8 | 69 | 50-59 | 82% |

- ARI vs base_04 0.32, vs ganador_05 0.38, vs forma_1 0.08, vs perfil del 07 0.26 (esos modelos no incluyen Campeche).

## Subperfiles anidados (`09_subperfiles_anidados.ipynb`)

Ejecutado (~20 s) sobre 657,497 celdas (incluye Campeche). Árbol de arriba hacia abajo: perfiles de origen configurable (`ORIGEN_PERFILES`, por defecto `"clases_latentes"`; alternativa `"base_04"`), renumerados por promedio, y KMeans ponderado dentro de cada perfil sobre A_base.

- **Los perfiles de base_04 son solo moderadamente estables:** ARI bootstrap medio 0.74, mínimo 0.50 (medido en este notebook con `ORIGEN_PERFILES = "base_04"`). Por eso el origen por defecto son las clases latentes (ARI 0.98).
- Selección por perfil: mayor k con ARI >= 0.8 y subperfil mínimo >= 2% de la población. Con clases latentes: {0: 5, 1: 3, 2: 5, 3: 5, 4: 4, 5: 5} = 27 subperfiles (2.2% a 6.4% de la población), ARI condicional 0.93-0.98. Con base_04 eran 18.
- Subperfiles destacados (clases latentes): 1.1 (brecha 2.2, tendencia -3.8; Sonora índice 833, Colima 555); 3.5 (brecha 0.7, tendencia -3.1, 57% rural; Colima 842); 4.3 (brecha 21.9, tendencia +7.3; Tlaxcala 1046; dominante en 201 municipios); 2.1 (tendencia +6.4; Tlaxcala 940); 0.1 (promedio 33.2, 17% mujeres, 48% rural); 5.5 (promedio 76.5, brecha 1.8, 62% rural; Campeche 715; dominante en 311 municipios).
- Microtargeting: índice de sobrerrepresentación por entidad (mínimo 20k personas) y por persona-tipo sexo x edad; subperfil dominante en 2,175 municipios con al menos 1,000 personas (tabla con nombres y claves INE, sin geometría).
- ARI perfil vs base_04 0.32; vs perfil del 07 0.26.
- Salidas: `celdas_subperfiles.parquet`, `subperfiles_resumen.csv`, `subperfiles_microtargeting.csv`, `subperfiles_entidades.csv`, `subperfiles_personas_tipo.csv`, `subperfiles_municipios.csv`.

## Escolaridad e internet por sección (`10_escolaridad_eceg.ipynb`)

Fuente: **Estadísticas Censales a Escalas Geoelectorales 2020** (ECEG), producto INEGI-INE con 220 indicadores del Censo 2020 por sección electoral (marco seccional INE, corte enero 2021). URL: `https://www.inegi.org.mx/contenidos/programas/ccpv/2020/datosabiertos/geoelectorales/eceg_2020_csv.zip`, descargada por `src/descarga_inicial.py` a `DATA/RAW/eceg_2020/`.

- Archivo usado: `conjunto_de_datos/INE_SECCION_2020.csv` (latin-1, 68,806 secciones, llave `ENTIDAD` + `SECCION`). Diccionario en `diccionario_de_datos/Descriptor_indicadores_ECEG_Seccion_2020.csv.csv`.
- Variables: `GRAPROES` (grado promedio de escolaridad, 15 años y más) con `_F` y `_M`; `P18YM_PB / P_18YMAS` (% con educación posbásica, 18 y más) por sexo; `VPH_INTER / VIVPARH_CV` (% de viviendas particulares habitadas con internet, sin versión por sexo).
- `-6` es código de confidencialidad (6 secciones) y 66 secciones sin población traen `0`: ambos se tratan como faltante. Afecta a 10,279 personas.
- Union: 100% de las 657,497 celdas y de los 71.2M de personas. Cada celda toma la escolaridad de su sección para su sexo.
- El resto de los indicadores de la ECEG se probó en `pruebas_locales/` y no se integra (ver Pruebas con variables del censo).

### Resultados
- Escolaridad y participación por sección: correlación ponderada 0.10 en general; 0.41 en urbanas, casi 0 en mixtas (-0.04) y rurales (0.02). En urbanas, secciones con 12+ grados participan 60.6 contra 50.9 en las de 8-10.
- Grado promedio nacional ponderado por votantes: 9.68. Viviendas con internet: 51.4%.
- Internet por perfil: P0 50.6, P1 49.3, P2 54.6, P3 51.8, P4 53.3, P5 49.1. Más en P2 y P4 (urbanos y escolarizados), menos en P1 y P5.

| Perfil | Grados | % posbásica | % en secciones <8 | % en 12+ | Urbana | Rural |
|---|---|---|---|---|---|---|
| 0 | 9.33 | 41.0 | 18.8 | 5.1 | 9.81 | 7.11 |
| 1 | 9.12 | 38.2 | 23.9 | 4.8 | 9.71 | 7.28 |
| 2 | 10.00 | 48.6 | 15.7 | 15.7 | 10.61 | 7.19 |
| 3 | 9.60 | 43.6 | 19.2 | 10.9 | 10.28 | 7.42 |
| 4 | 10.11 | 49.9 | 20.0 | 21.8 | 10.99 | 6.93 |
| 5 | 9.78 | 46.2 | 25.5 | 19.4 | 11.01 | 7.17 |

- P0 y P1 viven sobre todo en secciones de escolaridad media (8-10 grados) y casi nunca en las de 12+. P1 es el de menor escolaridad.
- P5 esta polarizado: el mayor porcentaje en secciones <8 (rurales) y 19% en 12+ (urbanas); en urbanas tiene la escolaridad más alta (11.0).
- Dentro de cada tipo de sección el rural es parejo (6.9-7.4); las diferencias entre perfiles están en lo urbano.
- Subperfiles extremos: 0.1 (8.18 grados, 43% en secciones <8), 5.5 (8.73), 4.4 (8.95) contra 4.1 (11.17), 2.2 (10.94) y 5.1 (10.83).
- Limitación: dato ecológico (promedio de la sección para el sexo, 15 y más), no escolaridad individual ni del grupo de edad. Censo 2020 contra lista nominal 2024.

## Fichas y mapa (`11_fichas_y_mapa.ipynb`)

Ejecutado (~1 min). Visualizaciones de las 6 clases latentes (08) con subperfiles (09), escolaridad e internet (10); requiere el 09 ejecutado con `ORIGEN_PERFILES = "clases_latentes"` y el 10 ejecutado.

- Nombres definitivos (`NOMBRES`): P0 Por convencer; P1 Constancia que se apaga; P2 Generación en ascenso; P3 Paso firme; P4 Voces que avanzan; P5 Pilar democrático. Se evitaron nombres que estigmatizan o que excluyen a parte del perfil (P4 es 68% mujeres, P2 no es el perfil más joven).
- Descriptor automático (`DESCRIPTORES`) como subtitulo en fichas, panel del mapa y `fichas_resumen_perfiles.csv`. Conducta (reglas de nivel, brecha y tendencia) más rasgos demográficos solo si destacan frente al nacional (índice = % perfil / % nacional): banda de edad con índice >= 1.4 (`UMBRAL_INDICE`; jóvenes 18-24, adultos jóvenes 25-39, adultos 40-59, mayores 60+), sexo >= 60% (`UMBRAL_SEXO`), rural con índice >= 1.4 y región con índice >= 1.4. Idea de un integrante del equipo; en lugar de "mayoría" se compara contra el nacional porque todos los perfiles son 62-76% urbanos.
  - P0: Baja participación · jóvenes (18-24) · mayoría hombres · fuerte en el Noroeste
  - P1: Participación media, estable entre elecciones, en descenso · fuerte en el Occidente
  - P2: Participación media, se moviliza en presidenciales, en ascenso · jóvenes (18-24)
  - P3: Participación media-alta, estable entre elecciones · adultos (40-59) · fuerte en el Occidente
  - P4: Participación media-alta, se moviliza en presidenciales, en ascenso · mayoría mujeres
  - P5: Alta participación · mayores (60+) · mayoría mujeres · más rural
- Cruce municipal por nombre normalizado dentro de cada entidad: 2,354 exactos, 10 por contenido, 7 aproximados (revisables en la sección 6.3), 5 sin cruce (nombres ambiguos de Oaxaca y municipios nuevos de Sinaloa; 54,695 personas). Municipios con menos de 1,000 personas se muestran sin datos: 2,171 de 2,475 con datos.
- Perfil dominante por municipio: P0 346, P1 38, P2 315, P3 215, P4 307, P5 950.
- Escolaridad e internet integrados: grado promedio, % posbásica y % viviendas con internet en el resumen y en el bloque "Contexto de la sección" del panel de cada ficha (escolaridad también en el encabezado); gráfica de tramos de escolaridad frente al nacional; columna de escolaridad en la tabla de subperfiles; escolaridad e internet en los popups municipal y estatal, en el panel del mapa y en `fichas_municipios.csv`.
- Ficha de 16 x 20 pulgadas: trayectoria y métricas; edad, región y escolaridad; entidades sobrerrepresentadas (8) y mapa de presencia; tabla de subperfiles a todo lo ancho.
- Mapa interactivo: tiles Stadia Maps (`alidade_smooth`); `folium.TileLayer` con `name="Mapa base"` para que el LayerControl muestre un nombre limpio. Capa municipal (opacidad segun % del perfil dominante, popup con composición y subperfil dominante) y estatal. Panel interactivo abajo a la izquierda: cada perfil colapsado (nombre, población, promedio) se expande al hacer click mostrando descriptor, métricas (promedio/brecha/tendencia), trayectoria SVG, género, edad, región y escolaridad como gráficos SVG inline frente al nacional (gris). ~12.6 MB; no se despliega en el notebook.
- Salidas en `DATA/PREPROCESSED/fichas/`: `vista_general.png`, `ficha_perfil_{0..5}.png` (200 dpi), `fichas_perfiles.pdf`, `mapa_perfil_dominante.png`, `mapa_clases_latentes.html`, `fichas_resumen_perfiles.csv`, `fichas_municipios.csv`, `fichas_cruce_municipios.csv`.
- Shapefile `mun22gw` descargado localmente en `DATA/RAW/marco_geoestadistico/` con las funciones de `src/descarga_inicial.py`.

## Pruebas con variables del censo (`pruebas_locales/`, no versionado)

Pregunta: cambia la segmentación si el modelo de clases latentes recibe, además de las 6 elecciones, variables de contexto como indicadores. Mismo EM y regla de selección de k que el 08; además, descriptiva por perfil contra el nacional. Notebooks: `prueba_escolaridad_marginacion`, `prueba_escolaridad_economia`, `prueba_indigena_afro_descriptores`, `prueba_barrido_censo`.

**Decisión:** la segmentación oficial (solo conducta) se queda. Las variables de contexto se usan como descriptores, no como entradas. Separar por el eje territorial no evalua comportamiento: describe lugares.

### Resultados por tema
- **Escolaridad:** ARI vs oficial 0.82, estable; solo separa la parte rural del P2 (18%). Es la variable del censo que mejor describe a los perfiles y resiste el control por sexo.
- **Marginación municipal CONAPO 2020:** ARI 0.67; arma una clase de municipios marginados (8%). Con escolaridad (ARI 0.49) el modelo divide el territorio en urbano-escolarizado y rural-marginado. El 71% de los votantes vive en municipios de marginación muy baja.
- **Economía (PEA, desocupacion):** sin efecto. El gradiente aparente (69.7% de participación económica en P0 a 55.8% en P5) es composición por sexo: dentro de cada sexo ningún perfil se aleja más de 1.5 puntos del nacional. Escolaridad + economía con terciles globales es la única variante inestable (ARI bootstrap 0.69); con terciles dentro del sexo se estabiliza (0.98).
- **Indígena y afromexicana:** no cambian la segmentación (ARI 0.95-0.99). Secciones con 40% o más en hogares indígenas (7% de votantes) participan más: 63.1 contra 55.1 en promedio y 11-13 puntos más en intermedias (2015: 58.4 vs 47.6; 2021: 64.9 vs 51.7), con menor brecha presidencial (10.7 vs 13.6). Se concentran en P5 (13.2% vive en secciones indígenas, nacional 7.1%) y P4 (8.1%). Afromexicana sin diferencias.
- **Barrido de 118 indicadores base de la ECEG:** el mejor (secundaria completa) tiene eta cuadrada de 0.08 dentro de sexo; edad < 40 tiene 0.29 y sexo 0.10. Ningún indicador del censo describe a los perfiles tanto como la edad o el sexo del CCPC. Destacan: estructura educativa, estructura de edad de la sección, afiliación al ISSSTE (P4 7.9%, P2 7.3%, P1 3.8%) y bienes de vivienda (cisterna, internet, computadora, más en P2 y P4). Discapacidad, migración, situación conyugal, jefatura de hogar y salud no distinguen.
- **11 variantes del barrido:** todas k = 6. Casi identicas a la oficial salvo internet (ARI 0.85, bootstrap mínimo 0.75) y fecundidad (ARI 0.80), que separan la parte rural del P2.

### Hallazgos para el documento
- **Eje territorial:** aparece con escolaridad, marginación, economía, internet y fecundidad: rural, baja escolaridad, más presencia indígena y participación igual o mayor al promedio (clases de 8-14% con 54-72% de participación). La baja participación es urbana y joven, no rural ni marginada: P0 tiene 4-5% en municipios de marginación alta.
- Secciones indígenas con mayor participación, sobre todo en intermedias.
- Internet en la vivienda como guia de canales: digital para P2 y P4; presencial o medios tradicionales para P1 y P5.
- Limitación común: datos ecológicos de la sección (2020) y marginación municipal.

## Entorno

- **Gestor:** UV (reproducible con `uv sync`)
- **Python:** 3.12 (fijado en `.python-version`; `uv sync` lo respeta aunque haya otras versiones instaladas)
- **Dependencias:** pandas, numpy, matplotlib, seaborn, scikit-learn, jupyter, requests, tqdm, pyarrow, geopandas, folium, python-dotenv, umap-learn

## Variables Sugeridas para Segmentación

- Edad (rangos generacionales)
- Sexo
- Tipo de sección (urbana/mixta/rural)
- Entidad federativa / región
- Historial de participación por elección (2009-2024)
- Tasa de participación (SV/LN)

## Plataforma CCPC

- **URL:** https://ine.mx/transparencia/datos-abiertos/visualización-datos/conteos-censales-participación/
- **Manual de uso (PDF, 38 pags):** descargado en `DATA/DOCS/Manual_Conteos_Censales_2009_2024.pdf`
- **Tecnologia:** Tableau Desktop 2024.3.5
- **Cartografía base:** corte mayo 2023
- Dos secciones principales: **Elecciones Federales** (2009-2024) y **Poder Judicial** (2024-2025)

### 5 Tableros Interactivos (Elecciones Federales)

| Tablero | Contenido |
|---|---|
| **1. Datos Generales** | Resumen estadístico: LN, SV, NV, %Participación, %Abstension, IML, IMV |
| **2. Datos Sociodemográficos** | Participación por año, grupo quinquenal, etapa de vida, mapa geográfico |

**Agrupaciones de edad oficiales del CCPC (manual, pag. 12):**
- Etapa de vida: Juventud 18-24, Adulta Joven 25-34, Adulta 35-44, Adulta Plena 45-59, Adulta Mayor 60+.
- Grupo quinquenal: 18-19, 20-24, 25-29, ..., 95-99, 100+.
| **3. Datos Comparativos** | Comparación entre estados, años, tipo sección, cuartiles |
| **4. Voto Anticipado 2024** | Proporción H/M, votacion por estado |
| **5. Voto en Prisión Preventiva 2024** | Comportamiento votacion, proporción H/M, mapa |

### Indicadores Clave
- % Participación = SV / (SV + NV)
- % Abstension = NV / (SV + NV)
- IML = (Hombres en LN / Mujeres en LN) x 100
- IMV = (Hombres que SV / Mujeres que SV) x 100

**Nota:** Los datos de población indígena y afromexicana están disponibles como FILTRO en los tableros interactivos pero NO aparecen como columna en los CSVs descargados. Por sección se pueden tomar de la ECEG 2020 (`PHOG_IND`, `POB_AFRO`).

## Estado del Proyecto

- [x] Lectura de convocatoria y rubrica
- [x] Extracción y revisión de datasets
- [x] Creación de knowledge base
- [x] Revisión de página INE y tableros interactivos
- [x] Lectura del manual de la plataforma CCPC (38 pags)
- [x] Configuración de entorno UV (Python 3.12 + dependencias)
- [x] Notebook de ingesta de datos
- [x] Consolidación de datos a Parquet (54.8M filas federales + 9.8M PJ + extras)
- [x] Perfilado de datos
- [x] Análisis exploratorio
- [x] Segmentación nacional ponderada (k=4, 71.2M personas) con caracterización completa
- [x] Mapa nacional interactivo con 2 capas (estatal + municipal) y clustering local en 1,858 municipios
- [x] Experimentos de clustering (2,028 configuraciones, estabilidad y finalistas)
- [x] Experimentos de forma y embeddings (notebook 06)
- [x] Segmentación jerárquica macro/micro (notebook 07; inestable, ARI 0.33)
- [x] Clases latentes (notebook 08; k=6, ARI 0.98)
- [x] Subperfiles anidados en clases latentes (notebook 09; 6 perfiles, 27 subperfiles)
- [x] Escolaridad por sección desde la ECEG 2020 (notebook 10)
- [x] Fichas y mapa de las clases latentes con escolaridad (notebook 11)
- [x] Segmentación final: clases latentes (notebook 08, k=6) con subperfiles del 09
- [x] Nombres definitivos de los perfiles (`NOMBRES` en el 11)
- [ ] Propuesta de estrategias
- [ ] Documento técnico
- [ ] Fichas de perfil
- [ ] Presentación ejecutiva
