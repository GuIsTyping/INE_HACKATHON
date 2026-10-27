# Perfiles ciudadanos de participación electoral en México: segmentación sociodemográfica basada en datos del CCPC 2009-2024

**Reto 1: Perfiles ciudadanos de participación**
Hackea la participación: Datos que construyen democracia | INE, 2026

**Autores:** Ángel David Durazo Bartolini y Jehú Jonathan Ramírez Ramírez

---

## 1. Introducción

La participación electoral en México muestra patrones persistentes y diferenciados. Mientras que las elecciones presidenciales alcanzan tasas cercanas al 60%, las intermedias apenas superan el 47%, y esta brecha no afecta por igual a todos los segmentos de la población. El propósito de este documento es identificar y caracterizar perfiles ciudadanos de participación a partir de los registros del sistema de Conteos Censales de Participación Ciudadana (CCPC) del INE, abarcando seis elecciones federales (2009-2024) y la elección extraordinaria del Poder Judicial (2025).

El objetivo práctico es doble: primero, ofrecer al INE una tipología empírica de comportamientos electorales que trascienda la descripción demográfica convencional (edad, sexo, región); segundo, derivar estrategias diferenciadas de fomento a la participación que reconozcan las barreras y oportunidades específicas de cada perfil.

La unidad de análisis es la celda sociodemográfica (sección electoral x sexo x grupo de edad), la más fina disponible en el CCPC sin comprometer el anonimato. El universo comprende 657,497 celdas que representan a 71.2 millones de personas en la lista nominal de 2024.

## 2. Datos

### 2.1 Fuentes

| Fuente | Periodo | Registros | Uso |
|---|---|---|---|
| CCPC Federal | 2009, 2012, 2015, 2018, 2021, 2024 | 54.9M filas | Tasas de participación por celda |
| CCPC Poder Judicial | 2025 | 9.8M filas (31 entidades) | Descriptor complementario |
| ECEG 2020 (INEGI-INE) | Censo 2020 | 68,806 secciones | Escolaridad e internet por sección |
| Marco geoestadístico | 2022 | 2,475 municipios | Cartografía para mapas |

Cada celda tiene tasa de participación calculada como SV / (SV + NV) para cada elección, excluyendo los registros no especificados (NS) que corresponden a cuadernillos no disponibles. Se retienen únicamente celdas con al menos 20 votantes potenciales en las seis elecciones federales, garantizando estimaciones estables.

### 2.2 Indicadores de comportamiento

Para cada celda se calcularon cuatro indicadores sintéticos:

- **Promedio:** media aritmética de las seis tasas (nivel general de participación).
- **Desviación:** desviación estándar de las seis tasas (estabilidad entre elecciones).
- **Brecha presidencial:** promedio en presidenciales (2012, 2018, 2024) menos promedio en intermedias (2009, 2015, 2021). Mide la sensibilidad al tipo de elección.
- **Tendencia:** pendiente de la regresión lineal de las tasas sobre el tiempo, en puntos porcentuales por elección. Mide la dirección del cambio.

## 3. Metodología

### 3.1 Elección del método

Se evaluaron sistemáticamente más de 2,000 configuraciones de clustering (K-Means, Bisecting K-Means, Birch, GMM, aglomerativo, espectral, HDBSCAN) sobre nueve conjuntos de variables con tres preprocesamientos, además de 2,376 configuraciones con embeddings (UMAP, t-SNE) y variables de forma. La evaluación consideró silhouette, R-cuadrada del promedio, estabilidad por bootstrap y separación en un espacio de referencia común.

Los métodos clásicos de clustering tienden a segmentar por nivel de participación (particiones con R-cuadrada de 0.90 para el promedio pero 0.04 para la forma de la trayectoria), lo que produce grupos "alto/medio/bajo" sin distinguir patrones conductuales como la brecha presidencial o la tendencia temporal. La segmentación jerárquica resultó inestable (ARI bootstrap 0.33).

### 3.2 Análisis de Clases Latentes (LCA)

Se optó por un modelo de clases latentes propio, implementado como una mezcla de distribuciones categóricas con independencia local estimada por Esperanza-Maximización (EM). Cada elección federal se discretizó en terciles ponderados (baja, media, alta participación) relativos a esa elección, generando un patrón de seis indicadores ordinales por celda.

Este enfoque tiene tres ventajas sobre el clustering convencional:

1. **Asignación probabilística.** Cada celda recibe una probabilidad de pertenencia a cada clase, lo que permite medir la certeza de la clasificación (entropía relativa: 0.78; 69% de las celdas con probabilidad >= 0.80 en su clase asignada).
2. **Equilibrio nivel-forma.** A diferencia del clustering sobre tasas continuas, la discretización en terciles por elección normaliza el nivel y permite que la estructura del modelo capture tanto diferencias en participación como en patrón temporal.
3. **Estabilidad.** ARI bootstrap medio de 0.98 (mínimo 0.95 en 5 réplicas de Poisson), muy superior al clustering jerárquico (0.33) y comparable al mejor K-Means (0.93-0.98), pero con la ventaja de la asignación probabilística.

Se exploraron modelos de 2 a 8 clases con 20 inicializaciones aleatorias cada uno, seleccionando k = 6 por tener el menor BIC en el rango de 4 a 6 clases con un tamaño mínimo de clase >= 5%. La elección extraordinaria del Poder Judicial 2025 no se incluyó como variable de segmentación por representar una dimensión distinta (correlación 0.28 con el promedio federal); se usa como descriptor.

### 3.3 Subperfiles

Dentro de cada clase latente se aplicó K-Means ponderado sobre los tres indicadores conductuales (promedio, brecha, tendencia) para identificar subperfiles. El número de subperfiles por clase se seleccionó como el mayor k con ARI condicional >= 0.80 y tamaño mínimo >= 2% de la población total, resultando en 27 subperfiles (3 a 5 por clase).

### 3.4 Descriptores sociodemográficos

Los perfiles se caracterizan post-hoc por:
- **Variables del CCPC:** edad (8 grupos), sexo, tipo de sección (urbana/mixta/rural), entidad federativa y región.
- **ECEG 2020 (INEGI-INE):** grado promedio de escolaridad por sección y sexo, porcentaje con educación posbásica, porcentaje de viviendas con internet.
- **Índices de sobrerrepresentación** por entidad: (% de la población del perfil en la entidad) / (% de la población nacional en esa entidad) x 1000, para identificar territorios prioritarios.

Se probó sistemáticamente la inclusión de 118 indicadores censales de la ECEG en el modelo de clases latentes. Ninguno mejoró sustancialmente la segmentación (ARI >= 0.80 en todas las variantes) ni logró distinguir perfiles mejor que la edad o el sexo del CCPC (eta cuadrada máxima de 0.08 vs 0.29 de la edad). La decisión fue mantener la segmentación basada exclusivamente en conducta electoral y usar las variables censales como descriptores.

## 4. Resultados: seis perfiles ciudadanos

La siguiente tabla resume los seis perfiles identificados. Las cifras de población corresponden a la lista nominal de 2024.

| # | Nombre | Población | % | Prom | Brecha | Tendencia | % Mujer | Edad dom. |
|---|---|---|---|---|---|---|---|---|
| 0 | Por convencer | 15.3M | 21.4 | 37.3 | +14.3 | +1.1 | 25 | 30-39 |
| 1 | Constancia que se apaga | 5.9M | 8.3 | 48.5 | +7.6 | -1.6 | 44 | 30-39 |
| 2 | Generación en ascenso | 13.3M | 18.6 | 50.5 | +18.4 | +3.0 | 53 | 30-39 |
| 3 | Paso firme | 11.6M | 16.3 | 60.3 | +9.3 | -0.1 | 57 | 40-49 |
| 4 | Voces que avanzan | 8.4M | 11.8 | 62.0 | +19.5 | +4.5 | 68 | 40-49 |
| 5 | Pilar democrático | 16.7M | 23.5 | 72.8 | +10.6 | +1.8 | 69 | 50-59 |

*Prom: participación media 2009-2024 (%); Brecha: diferencia presidencial - intermedia (pp); Tendencia: cambio por elección (pp); Edad dom.: grupo de edad con mayor peso.*

### 4.1 Descripción de los perfiles

**P0 - Por convencer (15.3M, 21.4%).** La participación más baja (37.3%). Mayoritariamente masculino (75%) y joven (87% menor de 40 años). Concentrado en el Noroeste (Baja California, Sonora, Chihuahua). Escolaridad media de 9.3 grados, 51% con internet. Responde parcialmente a elecciones presidenciales pero su tendencia es apenas positiva. Es el perfil de la desvinculación: no rechaza la democracia, simplemente no participa en ella.

**P1 - Constancia que se apaga (5.9M, 8.3%).** Participación intermedia (48.5%) con la brecha presidencial más baja (7.6 puntos: participa de manera estable sin importar el tipo de elección) pero en descenso sostenido (-1.6 por elección), siendo el único perfil con tendencia negativa. Escolaridad y acceso a internet más bajos (9.1 grados, 49%). Concentrado en Occidente (Jalisco, Guanajuato, Colima). Es la alerta del sistema: ciudadanos que participaban pero están dejando de hacerlo. La baja certeza de su asignación (solo 44% con probabilidad >= 0.80) sugiere una población en transición.

**P2 - Generación en ascenso (13.3M, 18.6%).** Participación media (50.5%) con una marcada brecha presidencial (+18.4) y la segunda tendencia ascendente más alta (+3.0). Joven (66% menor de 40), equilibrado en género, predominantemente urbano (76%). La mayor escolaridad en zonas urbanas (10.6 grados) y el mayor acceso a internet (55%). Se moviliza en elecciones presidenciales pero se ausenta en las intermedias.

**P3 - Paso firme (11.6M, 16.3%).** Participación de 60.3%, la más estable de todos los perfiles (brecha 9.3, tendencia -0.1). Adultos de 40-49, 57% mujeres, fuerte en Occidente. Es el perfil del votante consistente: participa sin importar el tipo de elección y no muestra cambio en el tiempo.

**P4 - Voces que avanzan (8.4M, 11.8%).** Participación de 62.0% con la mayor brecha presidencial (+19.5) y la mayor tendencia ascendente (+4.5). Mayoría femenina (68%), adultas de 40-49, con la mayor escolaridad (10.1 grados, 50% posbásica) y mayor afiliación al ISSSTE (7.9%). Es el perfil de mayor dinamismo: mujeres educadas cuya participación crece con cada elección.

**P5 - Pilar democrático (16.7M, 23.5%).** La participación más alta (72.8%), estable y con tendencia positiva (+1.8). Mayores de 50 (85% mayor de 40), mayoría femenina (69%), el perfil más rural (38% en secciones rurales o mixtas). Escolaridad polarizada: la más baja en zonas rurales pero la más alta en urbanas (11.0 grados). Las secciones con presencia indígena (40%+ en hogares indígenas) participan más que el promedio nacional (63.1 vs 55.1) y se concentran en este perfil (13.2% vs 7.1% nacional).

### 4.2 Estructura emergente

Los seis perfiles revelan dos ejes ortogonales de variación en la participación ciudadana:

1. **Eje de nivel** (vertical): del 37% (P0) al 73% (P5), asociado a la edad y el sexo. Los jóvenes y los hombres participan menos.
2. **Eje de forma** (horizontal): del patrón estable (P1, P3, P5: brecha < 11 puntos) al patrón reactivo-presidencial (P0, P2, P4: brecha > 14 puntos), asociado al territorio (brecha mayor en zonas urbanas del centro).

Estos ejes son casi independientes: el ARI entre una segmentación por puro nivel y otra por pura forma es 0.03. La segmentación por clases latentes captura ambos simultáneamente.

## 5. Hallazgos transversales

### 5.1 La baja participación es urbana y joven, no rural ni marginada

Contrario a la narrativa convencional, el perfil de menor participación (P0) tiene solo 4-5% de su población en municipios de alta marginación. Las secciones rurales e indígenas participan por encima del promedio nacional. El 71% de los votantes vive en municipios de marginación muy baja. La brecha de participación no es un problema de acceso o marginación, sino de motivación en contextos urbanos.

### 5.2 Las secciones indígenas participan más

Las secciones con 40% o más de hogares indígenas (7% de los votantes) tienen una participación promedio de 63.1% contra 55.1% del resto. La diferencia es mayor en intermedias (2015: 58.4 vs 47.6; 2021: 64.9 vs 51.7) y la brecha presidencial es menor (10.7 vs 13.6 puntos). Se concentran en P5 y P4.

### 5.3 La brecha presidencial-intermedia es el problema central

P0, P2 y P4 suman 52% de la población analizada y su participación en intermedias está 14-20 puntos por debajo de su nivel en presidenciales. El principal desafío del INE no es incorporar ciudadanos que nunca votan, sino sostener la participación de quienes ya votan en presidenciales durante las elecciones intermedias.

### 5.4 P1 es la alerta roja del sistema

Es el único perfil en descenso sostenido, el de menor claridad de asignación y el de menor escolaridad y acceso a internet. Si no se interviene, estos 5.9 millones de ciudadanos podrían migrar conductualmente hacia P0.

## 6. Estrategias diferenciadas

Cada estrategia se fundamenta en el diagnóstico del perfil (barrera, canal viable, momento crítico y territorio prioritario).

### P0 - Por convencer: acercamiento por relevancia

- **Barrera:** desvinculación; la participación electoral no forma parte de su identidad.
- **Mensaje:** centrar la comunicación en cómo las decisiones electorales afectan su cotidianidad (empleo, seguridad, servicios urbanos). Evitar mensajes moralizantes; privilegiar el impacto personal.
- **Canal:** digital (redes sociales, video corto) complementado con presencia en espacios urbanos (universidades, centros deportivos). El 51% con internet permite estrategia mixta.
- **Momento:** elecciones intermedias, donde la caída es más pronunciada. Activación 3-4 meses antes.
- **Territorio:** Noroeste (Baja California, Sonora, Chihuahua, Sinaloa).

### P1 - Constancia que se apaga: reactivación urgente

- **Barrera:** desencanto progresivo; participaban pero están dejando de hacerlo.
- **Mensaje:** reconocer su participación pasada y mostrar resultados tangibles de elecciones recientes en su región. Evidencia local de márgenes estrechos.
- **Canal:** medios tradicionales (radio local, perifoneo) y organizaciones comunitarias. Internet es el más bajo (49%); lo digital es complementario.
- **Momento:** intervención continua, no solo en periodo electoral. Programas de vinculación cívica permanente.
- **Territorio:** Occidente (Jalisco, Guanajuato, Colima). Subperfil 1.1 (caída de -3.8 por elección) como caso crítico.

### P2 - Generación en ascenso: sostener el impulso

- **Barrera:** participación selectiva; responde a la "emoción" presidencial pero no percibe las intermedias como relevantes.
- **Mensaje:** comunicar que las elecciones intermedias definen servicios locales. Datos locales de márgenes estrechos. Identidad generacional ascendente.
- **Canal:** digital (55% internet, el más alto). Redes sociales, plataformas de video, contenido interactivo y compartible.
- **Momento:** esfuerzo concentrado 6 meses antes de intermedias. En presidenciales ya se movilizan solos.
- **Territorio:** distribución amplia urbana. Subperfil 2.1 (tendencia +6.4) fuerte en Tlaxcala y centro.

### P3 - Paso firme: reconocer, mantener y multiplicar

- **Barrera:** ninguna crítica. El riesgo es la complacencia institucional.
- **Mensaje:** reconocimiento por su constancia. Invitarlos como multiplicadores en su entorno.
- **Canal:** mixto (52% internet). Programas de promotores cívicos voluntarios reclutados de este perfil.
- **Momento:** mantenimiento continuo con refuerzo electoral. Atención al subperfil 3.5 en declive.
- **Territorio:** Occidente (Jalisco, Guanajuato, Michoacán).

### P4 - Voces que avanzan: canalizar el liderazgo cívico femenino

- **Barrera:** brecha presidencial-intermedia, pero con base alta. La oportunidad es el liderazgo cívico.
- **Mensaje:** empoderar: invitar a roles de observadoras electorales, capacitadoras, promotoras del voto. Visibilizar el impacto de la participación femenina con datos.
- **Canal:** digital (53% internet) y redes de mujeres organizadas (asociaciones, sindicatos). Contenido con perspectiva de género.
- **Momento:** aprovechar el impulso post-presidencial para institucionalizar participación en intermedias.
- **Territorio:** amplia presencia. Subperfil 4.3 (tendencia +7.3) fuerte en Tlaxcala, dominante en 201 municipios.

### P5 - Pilar democrático: preservar, facilitar y transmitir

- **Barrera:** envejecimiento y accesibilidad. Edad avanzada plantea retos de movilidad.
- **Mensaje:** gratitud institucional. Invitarlos a transmitir el hábito del voto a generaciones jóvenes.
- **Canal:** presencial y medios tradicionales (radio comunitaria, televisión, materiales impresos). Internet es secundario (49% y edad avanzada).
- **Momento:** permanente. Asegurar condiciones logísticas: casillas accesibles, asistencia para mayores.
- **Territorio:** distribución rural amplia. Subperfil 5.5 (76.5%, 62% rural) en Campeche y Sur-Sureste. Secciones indígenas como activo a preservar.

### Matriz de intervención

| Perfil | Prioridad | Objetivo | Canal | Territorio |
|---|---|---|---|---|
| P0 Por convencer | Muy alta | Incorporar | Digital + presencial urbano | Noroeste |
| P1 Constancia que se apaga | Alta (urgente) | Reactivar | Tradicional, comunidad | Occidente |
| P2 Generación en ascenso | Alta | Sostener en intermedias | Digital | Nacional urbano |
| P3 Paso firme | Media | Mantener, multiplicar | Mixto | Occidente |
| P4 Voces que avanzan | Media-alta | Liderazgo cívico | Digital + redes mujeres | Nacional |
| P5 Pilar democrático | Alta (preservar) | Facilitar, transmitir | Presencial, radio | Rural, Sur-Sureste |

## 7. Limitaciones

1. **Dato ecológico.** La escolaridad e internet provienen del promedio de la sección (ECEG 2020), no de los individuos de la celda. La celda sociodemográfica del CCPC tampoco sigue a las mismas personas entre elecciones.
2. **Desfase temporal.** Los indicadores censales son de 2020; la lista nominal de 2024 refleja cambios demográficos y migratorios no capturados.
3. **Continuo subyacente.** La participación electoral es un continuo, no clusters discretos (silhouette máximo 0.31 en clustering convencional). Los perfiles son zonas de densidad en ese continuo, no fronteras netas. La entropía relativa de 0.78 y el 69% de asignaciones claras reflejan esta realidad.
4. **Ausencia de Campeche en PJ 2025.** Los datos del Poder Judicial no incluyen a Campeche, por lo que sus celdas carecen de ese descriptor.
5. **Voto anticipado y prisión preventiva.** Estos registros (30,012 votos en total) carecen de sección y edad, por lo que no se integran a la segmentación. Su volumen es marginal frente a los 71.2 millones del universo analizado.

## 8. Conclusiones

La segmentación por clases latentes sobre el comportamiento electoral de 2009 a 2024 revela seis perfiles ciudadanos estables (ARI 0.98), diferenciados no solo por su nivel de participación sino por su patrón temporal: la brecha presidencial-intermedia y la tendencia son ejes de variación independientes del nivel.

Tres hallazgos desafían supuestos convencionales: la baja participación se concentra en zonas urbanas y jóvenes (no en las marginadas), las secciones indígenas participan por encima del promedio, y el principal reto no es incorporar a quienes nunca votan sino sostener a quienes solo votan en presidenciales. Los perfiles P0, P2 y P4, que suman 52% de la población, pierden entre 14 y 20 puntos porcentuales en elecciones intermedias.

Las estrategias propuestas responden a esta evidencia: canales digitales para los perfiles jóvenes y urbanos con internet (P0, P2, P4), medios tradicionales y comunitarios para los de menor acceso (P1, P5), y mensajes diferenciados que van desde la relevancia personal (P0) hasta el reconocimiento del liderazgo cívico femenino (P4) y la transmisión intergeneracional del hábito democrático (P5).

## Referencias

- INE. *Conteos Censales de Participación Ciudadana 2009-2024.* Sistema CCPC, datos abiertos.
- INE. *Manual de uso de la plataforma de Conteos Censales de Participación Ciudadana.* 38 pp.
- INEGI-INE. *Estadísticas Censales a Escalas Geoelectorales 2020 (ECEG).* Censo de Población y Vivienda 2020 por sección electoral.
- CONABIO-INEGI. *División política municipal 2022.* Marco geoestadístico nacional.
