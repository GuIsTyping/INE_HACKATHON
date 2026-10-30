# Bitacora de Cambios

## 2026-10-30

### Acentos en nombres de columna (notebooks y Knowledge Base)
- Reemplazadas 102 ocurrencias de SECCION/REGION (antes con acento) en las 11 libretas para que coincidan con los parquets generados por los scripts
- Actualizada la Knowledge Base con los mismos nombres sin acento

### Scripts de produccion
- `src/descarga_inicial.py`: actualizado docstring con autoria y mencion de shapefiles/ECEG
- `src/preprocesamiento.py` (nuevo, ~290 lineas): consolidacion federal con PyArrow, historial por seccion y celda, ECEG 2020. Codigo de produccion extraido de notebooks 01, 03 y 10
- `src/segmentacion.py` (nuevo, ~380 lineas): clases latentes (EM propio sobre terciles ponderados, k=6) y subperfiles anidados (KMeans, 27 subperfiles). Codigo extraido de notebooks 08 y 09
- `src/visualizacion.py` (nuevo, ~580 lineas): fichas PNG/PDF, mapa estatico, mapa interactivo folium, tablas CSV, cruce municipal por nombre. Codigo extraido de notebook 11
- Todos con logica skip-if-exists, autoria de Angel David Durazo Bartolini y Jehu Jonathan Ramirez Ramirez
- `ejecutar_pipeline.sh` (nuevo): script ejecutable que levanta el proyecto de cero (verifica UV, instala entorno, ejecuta los 4 scripts en orden) y al terminar inicia un servidor HTTP local en puerto 8765 para el mapa interactivo

## 2026-10-27

### Entregables en lenguaje más accesible
- `documento_tecnico.md`: sección 3 reescrita con tabla "Cómo leer las cifras", tabla de decisiones de partida, tabla de métodos probados y por qué se descartaron, explicación paso a paso de las clases latentes y justificación de k = 6 con la mejora del BIC (0.78% de 5 a 6 contra 0.28% de 6 a 7). Tabla de perfiles con encabezados completos y columna de asignación clara. Escolaridad redactada como dato de la sección, barreras como hipótesis, hallazgos sin afirmaciones causales, indicadores de avance en la matriz de intervención. Corregido: P2 no tiene la mayor escolaridad urbana (la tienen P5 y P4). Pasa de ~8 a ~10 cuartillas estimadas
- `estrategias_por_perfil.md`: nota sobre barreras como hipótesis y dato por sección; "barrera probable"; escolaridad de P1, P2 y P4 como dato de la sección; "señal de alerta" y prioridad "temprana" para P1
- `presentacion_ejecutiva.pptx`: diapositiva 4 en lenguaje llano con gráfica de P1 contra P2; etiquetas de la diapositiva 5 legibles ("Participación media", "Extra en presidenciales", "Cambio por elección"); quitada la afirmación "Las estrategias genéricas no funcionan"; "migrarán" pasa a "podría derivar"; "Microtargeting" pasa a "Focalización territorial"; sin menciones de ARI ni folium

## 2026-10-26

### Presentación ejecutiva (PPTX)
- `DATA/DOCS/presentacion_ejecutiva.pptx`: 10 diapositivas (portada, contexto, datos, metodología, 6 perfiles, hallazgos, estrategias I y II, viabilidad, conclusión). Formato widescreen, cards con colores por perfil, métricas destacadas

### Documento técnico (PDF)
- `DATA/DOCS/documento_tecnico.md`: contenido completo del documento técnico (introducción, datos, metodología, 6 perfiles, hallazgos transversales, estrategias diferenciadas, limitaciones, conclusiones, referencias)
- `DATA/DOCS/documento_tecnico.pdf`: PDF generado con Calibri 11, interlineado 1.5, 8 páginas. Formato conforme a la convocatoria

### Estrategias diferenciadas por perfil
- `DATA/DOCS/estrategias_por_perfil.md`: estrategia de intervención para cada uno de los 6 perfiles con diagnóstico, barrera principal, mensaje, canal, momento, territorio e indicador de éxito; incluye matriz de intervención y 5 hallazgos transversales

### UI del mapa interactivo
- `11_fichas_y_mapa.ipynb`: tiles Stadia Maps con `folium.TileLayer(name="Mapa base")` para que el LayerControl muestre texto limpio en vez de la URL cruda del tile
- Panel de perfiles rediseñado: cada perfil colapsado (nombre, población, promedio) se expande al hacer click con descriptor, métricas (promedio/brecha/tendencia en tarjetas), trayectoria SVG, barra de género, distribución de edad, región y escolaridad como gráficos SVG inline comparados contra el nacional (gris). CSS con `<details>` nativo y flecha animada. Distribuciones pre-computadas por groupby para eficiencia
- Reejecutado: mapa de 12.6 MB

## 2026-10-25

### Rasgos demográficos en los descriptores
- `11_fichas_y_mapa.ipynb`: el descriptor de cada perfil agrega edad, sexo, rural y región solo cuando destacan frente al nacional (`UMBRAL_INDICE = 1.4`, `UMBRAL_SEXO = 60`); acentos en los textos visibles. Reejecutado

### Nombres definitivos de los perfiles
- `11_fichas_y_mapa.ipynb`: `NOMBRES` fijados (Por convencer, Constancia que se apaga, Generación en ascenso, Paso firme, Voces que avanzan, Pilar democrático); los nombres automaticos pasan a `DESCRIPTORES` y se muestran como subtitulo en fichas, panel del mapa y `fichas_resumen_perfiles.csv`. Reejecutado

### Internet en la vivienda y conclusiones de las pruebas del censo
- `10_escolaridad_eceg.ipynb`: agregado % de viviendas con internet por sección (`VPH_INTER / VIVPARH_CV`) a `secciones_eceg_2020.parquet` y a los CSV `escolaridad_*`
- `11_fichas_y_mapa.ipynb`: internet en el resumen, en el bloque "Contexto de la sección" del panel de cada ficha, en popups y panel del mapa y en `fichas_municipios.csv`. Reejecutados 10 y 11: perfiles sin cambios
- Pruebas locales (no versionadas) de segmentación con marginación, economía, indígena, afromexicana y barrido de la ECEG: la segmentación oficial se mantiene; conclusiones en `KNOWLEDGE_BASE.md`

### Carpeta de pruebas locales
- `pruebas_locales/` agregada a `.gitignore`: pruebas exploratorias que no se versionan (primera: segmentación con escolaridad y marginación CONAPO)

### Escolaridad integrada en fichas y mapa
- Renumerados: `11_escolaridad_eceg.ipynb` pasa a `10_escolaridad_eceg.ipynb` y `10_fichas_y_mapa.ipynb` a `11_fichas_y_mapa.ipynb`, para que el orden siga la ejecución (las fichas leen `secciones_eceg_2020.parquet`)
- `11_fichas_y_mapa.ipynb`: escolaridad por sexo de la sección en cada celda; grado promedio y % posbásica en el resumen, encabezado y panel de cada ficha; nueva gráfica de tramos de escolaridad frente al nacional; columna de escolaridad en la tabla de subperfiles; escolaridad media en popups, panel del mapa y `fichas_municipios.csv`. Ficha a 16 x 20 con la tabla de subperfiles a todo lo ancho. Reejecutado: mismos perfiles y cruces
- Clases latentes confirmadas como segmentación final

### Escolaridad por sección (ECEG 2020)
- `src/descarga_inicial.py`: agregado el ZIP de Estadísticas Censales a Escalas Geoelectorales 2020 del INEGI (`eceg_2020`), extraido en `DATA/RAW/eceg_2020/` (agregado a `.gitignore`)
- `notebooks/11_escolaridad_eceg.ipynb`: limpieza de códigos `-6` y secciones vacias, union con las celdas por EDOCVE + SECCIÓN (100% de cobertura), escolaridad por sexo de la celda, relación escolaridad-participación por tipo de sección y escolaridad por perfil, subperfil y tipo de sección. Genera `secciones_eceg_2020.parquet` y CSV `escolaridad_*`

### Fichas y mapa de las clases latentes
- `notebooks/10_fichas_y_mapa.ipynb`: vista general, 6 fichas de perfil (PNG 200 dpi y PDF), mapa estático del perfil dominante por municipio y mapa interactivo folium; salidas en `DATA/PREPROCESSED/fichas/`
- Cruce municipal por nombre normalizado en lugar de clave: las claves municipales del INE no coinciden con las del INEGI (detectado error en el mapa del 04)
- Tiles del mapa por URL directa del CDN de CARTO (el alias de folium ahora pide API key)
- Shapefile `mun22gw` descargado localmente

### Campeche incluido en 08 y 09
- Detectado que PJ 2025 no tiene Campeche (no Zacatecas como decia la KB) y que el filtro de casos completos por `P_PJ2025` lo excluia de los notebooks 05-09
- 08 y 09 ya no filtran por `P_PJ2025`; promedios PJ calculados solo con celdas con dato. Reejecutados sobre 657,497 celdas: misma estructura de 6 clases (ARI bootstrap 0.98), 27 subperfiles
- 09: comparación con modelos previos tolera celdas sin etiqueta; con origen `base_04` se excluyen las celdas sin perfil

### Subperfiles sobre clases latentes
- `notebooks/09_subperfiles_anidados.ipynb`: parametro `ORIGEN_PERFILES` (por defecto `"clases_latentes"`, alternativa `"base_04"`); reejecutado con las 6 clases latentes como perfiles: 27 subperfiles. Sobrescribe `celdas_subperfiles.parquet` y CSV `subperfiles_*`

### Subperfiles anidados
- `notebooks/09_subperfiles_anidados.ipynb`: árbol de arriba hacia abajo con los perfiles de base_04 y KMeans ponderado dentro de cada uno (18 subperfiles); índices de sobrerrepresentación por entidad y persona-tipo, municipios con mínimo de 1,000 personas. Genera `celdas_subperfiles.parquet` y CSV `subperfiles_*`
- Medida por primera vez la estabilidad de base_04: ARI bootstrap 0.74

### Ejecución de clases latentes
- `notebooks/08_clases_latentes.ipynb` ejecutado: k=6, ARI bootstrap 0.99. Genera `celdas_clases_latentes.parquet`, `lca_seleccion_k.csv`, `lca_clases.csv`

### Clases latentes (sin ejecutar)
- `notebooks/08_clases_latentes.ipynb`: LCA con EM propio sobre terciles ponderados de participación por elección, selección de k por BIC, asignación probabilística, bootstrap y comparación con modelos previos

### Ejecución de la segmentación jerárquica
- `notebooks/07_segmentacion_jerarquica.ipynb` ejecutado con A_base: 200 microsegmentos, 4 perfiles y 15 subperfiles; estabilidad baja (ARI 0.33). Genera `celdas_jerarquia.parquet` y los CSV `jerarquia_*`

## 2026-10-24

### Segmentación jerárquica (sin ejecutar)
- `notebooks/07_segmentacion_jerarquica.ipynb`: microsegmentos con KMeans ponderado y árbol Ward ponderado sobre sus centros; tres niveles anidados (perfil, subperfil, microsegmento), bootstrap de Poisson, tabla de microtargeting y tabla territorial por municipio

### Experimentos de forma y embeddings
- `notebooks/06_experimentos_forma_embeddings.ipynb`: clustering sobre la forma de la trayectoria (sin nivel) y con UMAP y t-SNE como reducción previa; 2,376 configuraciones evaluadas con lentes de nivel y forma
- Dependencia `umap-learn` agregada con `uv add`

### Experimentos de clustering
- `notebooks/05_experimentos_clustering.ipynb`: búsqueda en malla de 2,028 configuraciones (9 conjuntos de variables, 3 preprocesamientos, 7 algoritmos), estabilidad por bootstrap de 18 candidatas y reajuste de 3 finalistas con todos los datos frente al modelo del notebook 04
- Genera `experimentos_clustering.csv`, `experimentos_estabilidad.csv`, `experimentos_finalistas.csv` y `celdas_perfiles_candidatos.parquet`; no modifica salidas del notebook 04
- Regenerados localmente `celdas_historial.parquet` y `secciones_historial.parquet` ejecutando el notebook 03 (sin cambiar el archivo versionado)

### Limpieza de outputs del notebook 04
- `04_segmentacion.ipynb`: eliminado el output del mapa folium embebido (53.7 MB) y la línea `m` que lo desplegaba; el mapa se consulta desde `mapa_nacional_segmentacion.html`. El notebook pasa de 56.4 MB a ~1.3 MB y conserva el resto de outputs (gráficas, tablas)
- `02_perfilado_datos.ipynb` y `03_analisis_exploratorio.ipynb`: corregida la versión invalida `3.12.-1` en metadatos a `3.12`

### Nombres auto-generados y layout del mapa
- `generar_nombre_perfil()`: función que compone nombres descriptivos a partir de condiciones sobre edad, género, tipo de asentamiento y comportamiento electoral (sin nombres hardcodeados)
- Panel lateral del mapa movido de derecha a izquierda para no solaparse con el LayerControl
- `.env` con API key de CARTO para tiles del mapa; `.env.example` con instrucciones para obtener la propia
- `.gitignore` actualizado para excluir `.env`
- Dependencia `python-dotenv` agregada a `pyproject.toml`

### Segmentación nacional y mapa interactivo
- `notebooks/04_segmentacion.ipynb` (27 code, 27 markdown): segmentación nacional + fichas de perfil + mapa nacional interactivo
- Clustering nacional ponderado por lista nominal 2024 (71.2M personas, 657k celdas)
- K-Means con sample_weight, k=4 (rango 4-6 alineado a convocatoria que pide 4-6 perfiles)
- Caracterización completa por perfil: trayectoria 2009-2024, edad, sexo, región, urbano/rural, PJ 2025
- Nombres descriptivos auto-generados para cada perfil
- Fichas de perfil (sección 5.7): una figura consolidada por perfil con trayectoria vs nacional, métricas, edad, región, top 5 entidades
- Mapa nacional interactivo con tiles CARTO CDN (sin API key), 2 capas + LayerControl
  - Capa estatal: 32 entidades, popup con nombre de perfil y porcentaje
  - Capa municipal: 2,475 municipios (1,858 con clustering local, 518 bloqueados)
  - Popups compactos con nombre de perfil + clustering local con detalle demográfico
  - Panel lateral desplegable con fichas detalladas de los 4 perfiles nacionales
- Genera `celdas_perfiladas.parquet`, `resumen_perfiles.csv`, `resumen_municipios.csv`, `mapa_nacional_segmentacion.html` (~24 MB)
- Descarga de shapefile CONABIO en `src/descarga_inicial.py`, dependencias `geopandas` y `folium` en `pyproject.toml`

### Limpieza de ramas
- Eliminadas 3 ramas remotas ya mergeadas: `fix/entorno-python-312`, `feat/perfilado-datos`, `feat/analisis-exploratorio`

## 2026-10-18

### Revisión de edades mayores a 100
- Verificado que EDAD > 100 no es un código especial (diccionarios, manual CCPC y seguimiento de registros entre elecciones). Detalle en `KNOWLEDGE_BASE.md` (Hallazgos del Perfilado > Calidad)
- Agregadas a `KNOWLEDGE_BASE.md` las agrupaciones de edad oficiales del CCPC (etapa de vida y grupo quinquenal)

### Notebook de análisis exploratorio
- `notebooks/03_analisis_exploratorio.ipynb` (34 secciones): regiones, cohortes generacionales, historial por sección y por celda (sección x sexo x grupo de edad), indicadores de historial, persistencia, relación con PJ 2025 y fuentes de variación (eta cuadrada)
- Genera `secciones_historial.parquet` y `celdas_historial.parquet` en `DATA/PREPROCESSED/`
- Hallazgos agregados a `KNOWLEDGE_BASE.md`

### Notebook de perfilado
- `notebooks/02_perfilado_datos.ipynb` (35 secciones): inventario, esquema, carga con tipos compactos (~1.2 GB en memoria), nulos, cobertura, distribución de edad, edades atípicas, consistencia LN = SV + NV + NS, NS por año, participación por año, sexo, grupo de edad, tipo de sección y entidad, secciones con historial completo, PJ 2025 y datasets complementarios
- Hallazgos agregados a `KNOWLEDGE_BASE.md`

### Versión de Python fijada
- `.python-version` con 3.12 (`uv python pin 3.12`) para que todo el equipo use la misma versión; antes `uv sync` tomaba la primera disponible (>=3.12)

### Fix en notebook de ingesta
- `01_ingesta_datos.ipynb` (sección 11): `pf.schema_arrow.num_fields` -> `len(pf.schema_arrow)`; `num_fields` no existe en pyarrow 26 y detenia la ejecución antes de guardar PJ 2025 y extras

### Configuración de VS Code
- `.vscode/` agregado a `.gitignore`: la configuración del editor es local de cada integrante y no se versiona

## 2026-10-17

### Estructura inicial del repositorio
- Creación de estructura de carpetas: `DATA/RAW/ZIPS`, `DATA/RAW/<dataset>`, `DATA/PREPROCESSED`, `DATA/DOCS`
- `pyproject.toml` con dependencias del proyecto (UV, Python 3.12)
- `src/descarga_inicial.py`: script standalone para descarga de 9 ZIPs y 4 PDFs
- `notebooks/01_ingesta_datos.ipynb`: notebook de ingesta con 16 secciones
  - Descarga de ZIPs a `DATA/RAW/ZIPS/`
  - Descarga de PDFs a `DATA/DOCS/`
  - Extracción de CSVs a `DATA/RAW/<dataset>/`
  - Consolidación a Parquet en `DATA/PREPROCESSED/` usando PyArrow ParquetWriter (escritura secuencial para evitar OOM con ~55M filas)
  - Columnas DEF y DEL forzadas a string por tipos mixtos en CSVs originales
- `DATA/DOCS/KNOWLEDGE_BASE.md`: documentación del proyecto, datos, variables, estado
- `DATA/DOCS/CHANGELOG.md`: este archivo
