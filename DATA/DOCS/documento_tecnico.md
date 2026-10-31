# Perfiles ciudadanos de participación electoral en México: segmentación sociodemográfica basada en datos del CCPC 2009-2024

**Reto 1: Perfiles ciudadanos de participación**
Hackea la participación: Datos que construyen democracia | INE, 2026

**Autores:** Ángel David Durazo Bartolini y Jehú Jonathan Ramírez Ramírez

---

## 1. Introducción

La participación electoral en México muestra patrones persistentes y diferenciados. Mientras que las elecciones presidenciales alcanzan tasas cercanas al 60%, las intermedias apenas superan el 47%, y esta brecha no afecta por igual a todos los segmentos de la población. El propósito de este documento es identificar y caracterizar perfiles ciudadanos de participación a partir de los registros del sistema de Conteos Censales de Participación Ciudadana (CCPC) del INE, abarcando seis elecciones federales (2009-2024) y la elección extraordinaria del Poder Judicial (2025).

El objetivo práctico es doble: primero, ofrecer al INE una tipología de comportamientos electorales que vaya más allá de la descripción demográfica convencional (edad, sexo, región); segundo, derivar estrategias diferenciadas de fomento a la participación que reconozcan las barreras y oportunidades específicas de cada perfil.

La unidad de análisis es la celda sociodemográfica (sección electoral x sexo x grupo de edad), la más fina disponible en el CCPC sin comprometer el anonimato. El universo comprende 657,497 celdas que representan a 71.2 millones de personas en la lista nominal de 2024.

## 2. Datos

### 2.1 Fuentes

| Fuente | Periodo | Registros | Uso |
|---|---|---|---|
| CCPC Federal | 2009, 2012, 2015, 2018, 2021, 2024 | 54.9M filas | Tasas de participación por celda |
| CCPC Poder Judicial | 2025 | 9.8M filas (31 entidades) | Descriptor complementario |
| ECEG 2020 (INEGI-INE) | Censo 2020 | 68,806 secciones | Escolaridad e internet por sección |
| Marco geoestadístico | 2022 | 2,475 municipios | Cartografía para mapas |

Cada celda tiene una tasa de participación por elección, calculada como SV / (SV + NV): personas que votaron entre personas registradas con dato. Se excluyen los registros no especificados (NS), que corresponden a cuadernillos no disponibles.

### 2.2 Indicadores de comportamiento

Para describir el historial de cada celda usamos cuatro indicadores:

- **Participación media:** promedio de las seis tasas. Responde a *cuánto* vota la celda.
- **Variabilidad:** desviación estándar de las seis tasas. Responde a *qué tan parejo* vota.
- **Extra en presidenciales (brecha):** promedio en presidenciales (2012, 2018, 2024) menos promedio en intermedias (2009, 2015, 2021), en puntos porcentuales. Una brecha de +18 significa que, en promedio, la celda vota 18 puntos más cuando se elige presidente.
- **Tendencia:** cuántos puntos gana o pierde la celda en cada elección, en promedio (pendiente de una recta ajustada a las seis tasas). Una tendencia de +4.5 equivale a unos 22 puntos más entre 2009 y 2024.

## 3. Metodología

La pregunta del reto es qué tipos de ciudadanía existen según su comportamiento de participación. Para responderla buscamos grupos de celdas con historiales de votación parecidos entre 2009 y 2024. Esta sección explica qué decisiones tomamos, qué probamos antes de llegar al método final y por qué elegimos un modelo de clases latentes.

### 3.1 Cómo leer las cifras de este documento

Usamos pocas medidas estadísticas y todas responden a una pregunta concreta:

| Medida | Pregunta que responde | Cómo interpretarla |
|---|---|---|
| Estabilidad (ARI por remuestreo) | Si repetimos el análisis con otra muestra de los datos, ¿salen los mismos perfiles? | Va de 0 (coincidencia al azar) a 1 (idénticos). Arriba de 0.8 se considera estable. |
| Asignación clara | ¿Qué tan seguro está el modelo de que una persona pertenece a su perfil? | Porcentaje de personas con probabilidad de 0.8 o más de pertenecer a su perfil. |
| Separación (silhouette) | ¿Los grupos están separados por fronteras nítidas? | Va de -1 a 1. Valores bajos indican un continuo sin cortes naturales. |
| BIC | ¿Cuántos grupos conviene usar? | Premia que el modelo explique bien los datos y penaliza agregar grupos innecesarios. Menor es mejor. |
| Varianza explicada | ¿Qué parte de las diferencias entre celdas en un indicador se debe al perfil? | Va de 0 a 1. Un valor de 0.90 significa que conocer el perfil explica el 90% de las diferencias. |

### 3.2 Decisiones de partida

| Decisión | Qué elegimos | Por qué |
|---|---|---|
| Unidad de análisis | Celda sección x sexo x grupo de edad | Es el nivel más fino que ofrece el CCPC sin identificar personas. |
| Tamaño mínimo | Al menos 20 personas registradas en cada una de las seis elecciones | En celdas más chicas, que voten una o dos personas más mueve demasiado la tasa. |
| Variables para formar los perfiles | Solo la conducta electoral 2009-2024 | Queremos perfiles de *participación*. La demografía se usa después para describirlos (ver 3.3). |
| Poder Judicial 2025 | Descriptor, no variable de segmentación | Es un fenómeno distinto: su relación con el voto federal es débil (correlación de 0.28). |
| Ponderación | Cada celda pesa según su número de personas | Para que una celda de 300 personas cuente más que una de 25. |

### 3.3 Qué probamos antes de llegar al método final

No partimos de un método preestablecido: evaluamos más de 4,400 variantes que combinan algoritmos de agrupamiento, conjuntos de variables y formas de preparar los datos. La tabla resume lo que aprendimos.

| Qué probamos | Qué encontramos | Decisión |
|---|---|---|
| Agrupamiento clásico sobre las seis tasas (K-Means, Bisecting K-Means, mezclas gaussianas) | Grupos estables (0.93 a 0.98), pero que solo ordenan por nivel: votan poco, regular, mucho o muchísimo. El perfil explica 90% de las diferencias en participación media y apenas 4% de las diferencias en el patrón temporal. | Descartado: no distingue a quien vota parejo de quien solo vota en presidenciales. |
| Agrupamiento sobre los indicadores (media, brecha, tendencia) | Sí distingue tipos de conducta, pero los grupos cambian al repetir el análisis (estabilidad media 0.74; en algún remuestreo, 0.50). | Descartado por inestable. |
| Agrupamiento sobre la forma de la trayectoria (cada tasa menos el promedio de la celda) | Grupos estables (0.95) con patrones temporales claros, pero ignora el nivel: el perfil explica solo 8% de las diferencias en participación media. | Descartado: pierde la dimensión de cuánto vota la gente. |
| Agregar edad, sexo, tipo de sección o región como variables | Los grupos se separan por sexo en lugar de por conducta. En un caso, cada grupo quedó compuesto por un solo sexo. | Descartado: la demografía se usa solo como descriptor. |
| Jerárquico (Ward), Birch, espectral, por densidad (HDBSCAN), reducción previa con UMAP o t-SNE | Grupos inestables (Ward: 0.33; UMAP y t-SNE: 0.38 a 0.67), un grupo gigante con otros diminutos, o ningún grupo denso. | Descartados. |

**El hallazgo que cambió el enfoque.** Los experimentos mostraron que *cuánto* vota una celda y *cómo* vota (pareja entre elecciones o solo en presidenciales, al alza o a la baja) son dos dimensiones casi independientes. La coincidencia entre una segmentación por nivel y otra por forma fue de 0.03, prácticamente la que daría el azar. Esto importa para el INE porque dos poblaciones con la misma participación media pueden necesitar estrategias opuestas. El perfil P1 de este documento vota en promedio 48.5% y viene a la baja; el P2 vota 50.5%, pero partió de 36% en 2009 y llegó a 58% en 2024, con saltos de más de 20 puntos en las presidenciales de 2012 y 2018. Un agrupamiento por nivel los habría puesto en el mismo grupo.

También aprendimos que la participación es un continuo: la mejor separación lograda fue de 0.31, lo que indica que no existen fronteras naturales entre grupos. Los perfiles funcionan como las tallas de ropa: no hay un salto natural entre una M y una L, pero distinguirlas es útil para atender a cada quien.

### 3.4 El método elegido: análisis de clases latentes

Necesitábamos un método que capturara nivel y forma a la vez, que fuera estable y que indicara qué tan segura es cada asignación. El análisis de clases latentes cumple las tres condiciones.

**Paso 1: cada elección se clasifica como baja, media o alta.** En cada elección ordenamos las celdas por su tasa de participación y las dividimos en tres tercios (ponderados por población): el tercio que menos votó, el intermedio y el que más votó. La clasificación es relativa a cada elección. Así, una celda con 55% en 2018 (año de participación alta en todo el país) puede quedar en el tercio medio, y la misma tasa en 2015 la pondría en el alto. Con esto, la forma de la trayectoria pesa tanto como el nivel, sin que los años de alta participación general dominen el resultado.

**Paso 2: el modelo busca los patrones que más se repiten.** Cada celda queda descrita por seis etiquetas (por ejemplo: baja, media, baja, alta, media, alta). El modelo supone que detrás de esas combinaciones hay unos cuantos tipos de ciudadanía, cada uno con su propia probabilidad de quedar en el tercio bajo, medio o alto en cada elección, y estima esos tipos con el algoritmo de Esperanza-Maximización (EM), que implementamos nosotros. Para no depender del punto de partida, cada modelo se estimó 20 veces desde inicios aleatorios distintos y se conservó la mejor solución.

**Paso 3: cada celda recibe una probabilidad de pertenecer a cada perfil.** A diferencia de los métodos clásicos, que asignan cada celda a un grupo sin matices, aquí sabemos qué tan segura es la asignación. Esto permite identificar poblaciones en transición, como el perfil P1.

**¿Por qué seis perfiles?** Estimamos modelos de 2 a 8 perfiles. El BIC mejora siempre al agregar perfiles, pero cada vez menos: pasar de 5 a 6 perfiles mejora el ajuste 0.78%, mientras que pasar de 6 a 7 lo mejora solo 0.28%, menos de la mitad. Además, la convocatoria pide de 4 a 6 perfiles y con seis todos conservan un tamaño útil para una campaña (el más chico agrupa al 8.3% de la población).

**¿Qué tan confiables son los perfiles?**

- **Estabilidad:** repetimos el modelo cinco veces sobre versiones remuestreadas de los datos. Los perfiles salieron prácticamente idénticos: coincidencia media de 0.98 y mínima de 0.95. Está al nivel de los métodos más estables evaluados, con la ventaja de capturar nivel y forma.
- **Claridad:** 69% de las personas pertenece a su perfil con probabilidad de 0.8 o más. El resto se parece a dos perfiles a la vez, algo esperable en un continuo.

### 3.5 Subperfiles

Dentro de cada perfil aplicamos un segundo agrupamiento (K-Means ponderado) sobre la participación media, la brecha y la tendencia para distinguir variantes más finas. En cada perfil elegimos el mayor número de subperfiles que cumpliera dos condiciones: que se mantuvieran estables al repetir el análisis (0.80 o más) y que cada uno representara al menos 2% de la población total. El resultado son 27 subperfiles, de 3 a 5 por perfil, útiles para la focalización territorial.

### 3.6 Descriptores sociodemográficos

Una vez formados los perfiles, los describimos con:

- **Variables del CCPC:** edad (8 grupos), sexo, tipo de sección (urbana, mixta o rural), entidad federativa y región.
- **ECEG 2020 (INEGI-INE):** grado promedio de escolaridad por sección y sexo, porcentaje con educación posbásica y porcentaje de viviendas con internet.
- **Índice de sobrerrepresentación por entidad:** (% de la población del perfil que vive en la entidad) / (% de la población nacional que vive en ella) x 100. Un índice de 100 indica una presencia proporcional; uno de 150, una presencia 50% mayor a la esperada.

También probamos incluir 118 indicadores del censo como variables del modelo. Ninguno cambió de forma importante los perfiles (coincidencia de 0.80 o más con el modelo original en todas las variantes) ni se diferencia entre perfiles tanto como la edad: el perfil explica como máximo 8% de las diferencias en un indicador censal, contra 29% en la edad. Por eso los perfiles se forman solo con conducta electoral y las variables censales se usan para describirlos.

## 4. Resultados: seis perfiles ciudadanos

La siguiente tabla resume los seis perfiles. Las cifras de población corresponden a la lista nominal de 2024.

| # | Nombre | Población | % | Participación media (%) | Extra en presidenciales (pts) | Cambio por elección (pts) | % mujeres | Edad predominante | Asignación clara (%) |
|---|---|---|---|---|---|---|---|---|---|
| 0 | Por convencer | 15.3M | 21.4 | 37.3 | +14.3 | +1.1 | 25 | 30-39 | 92 |
| 1 | Constancia que se apaga | 5.9M | 8.3 | 48.5 | +7.6 | -1.6 | 44 | 30-39 | 44 |
| 2 | Generación en ascenso | 13.3M | 18.6 | 50.5 | +18.4 | +3.0 | 53 | 30-39 | 59 |
| 3 | Paso firme | 11.6M | 16.3 | 60.3 | +9.3 | -0.1 | 57 | 40-49 | 57 |
| 4 | Voces que avanzan | 8.4M | 11.8 | 62.0 | +19.5 | +4.5 | 68 | 40-49 | 51 |
| 5 | Pilar democrático | 16.7M | 23.5 | 72.8 | +10.6 | +1.8 | 69 | 50-59 | 82 |

### 4.1 Descripción de los perfiles

**P0 - Por convencer (15.3M, 21.4%).** La participación más baja (37.3%). Mayoritariamente masculino (75%) y joven (87% menor de 40 años). Concentrado en el Noroeste (Baja California, Sonora, Chihuahua). Vive en secciones con escolaridad media de 9.3 grados y 51% de viviendas con internet. Vota algo más en presidenciales y su tendencia es apenas positiva. Es el perfil más claramente definido: 92% de sus integrantes pertenece a él sin ambigüedad. Es el grupo más alejado de las urnas en todas las elecciones.

**P1 - Constancia que se apaga (5.9M, 8.3%).** Participación intermedia (48.5%) y la brecha presidencial más baja (7.6 puntos): vota de manera pareja sin importar el tipo de elección. Pero viene en descenso (-1.6 puntos por elección) y es el único perfil con tendencia negativa. Vive en las secciones con menor escolaridad (9.1 grados) y con uno de los accesos a internet más bajos (49%). Concentrado en Occidente (Jalisco, Guanajuato, Colima). Solo 44% de sus integrantes pertenece claramente a este perfil; el resto se parece también a otro perfil vecino, lo que es coherente con una población en transición.

**P2 - Generación en ascenso (13.3M, 18.6%).** Participación media (50.5%) con una brecha presidencial marcada (+18.4) y la segunda tendencia ascendente más alta (+3.0): pasó de 36% en 2009 a 58% en 2024. Joven (66% menor de 40), equilibrado en género y predominantemente urbano (76%). En zonas urbanas vive en secciones con escolaridad alta (10.6 grados) y tiene el mayor acceso a internet (55%). Se moviliza en elecciones presidenciales pero se ausenta en las intermedias.

**P3 - Paso firme (11.6M, 16.3%).** Participación de 60.3% y el patrón más estable de todos (brecha 9.3, tendencia -0.1). Adultos de 40-49 años, 57% mujeres, con fuerte presencia en Occidente. Es el perfil del votante consistente: participa sin importar el tipo de elección y su participación no cambia con el tiempo.

**P4 - Voces que avanzan (8.4M, 11.8%).** Participación de 62.0%, con la mayor brecha presidencial (+19.5) y la mayor tendencia ascendente (+4.5, unos 22 puntos entre 2009 y 2024). Mayoría femenina (68%), adultas de 40-49 años. Vive en las secciones de mayor escolaridad (10.1 grados, 50% con educación posbásica) y con mayor afiliación al ISSSTE (7.9%). Es el perfil de mayor dinamismo: su participación crece en cada elección.

**P5 - Pilar democrático (16.7M, 23.5%).** La participación más alta (72.8%), estable y con tendencia positiva (+1.8). Mayores de 50 años (85% mayor de 40), mayoría femenina (69%) y el perfil más rural (38% en secciones rurales o mixtas). Su escolaridad es polarizada: en zonas rurales vive en secciones de baja escolaridad y en zonas urbanas en las de mayor escolaridad (11.0 grados). Las secciones con 40% o más de hogares indígenas tienen mayor presencia en este perfil (13.2% de su población, contra 7.1% nacional).

### 4.2 Estructura de los perfiles

Los seis perfiles se ordenan en dos ejes casi independientes:

1. **Cuánto vota (nivel):** del 37% de P0 al 73% de P5. Está asociado a la edad y el sexo: los jóvenes y los hombres participan menos.
2. **Cómo vota (forma):** del patrón parejo (P1, P3, P5, con brecha menor a 11 puntos) al patrón que se activa en presidenciales (P0, P2, P4, con brecha mayor a 14 puntos). Está asociado al territorio, con brechas mayores en zonas urbanas del centro.

En los niveles medios de participación, el modelo separa a la población por forma: P1 y P2 votan en promedio casi lo mismo (48.5% y 50.5%), igual que P3 y P4 (60.3% y 62.0%), pero con trayectorias muy distintas. Esa distinción es la que permite diseñar estrategias diferenciadas.

## 5. Hallazgos transversales

### 5.1 La baja participación es urbana y joven, no rural ni marginada

Contrario a la narrativa convencional, el perfil de menor participación (P0) tiene solo 4-5% de su población en municipios de alta marginación. Las secciones rurales e indígenas participan por encima del promedio nacional, y el 71% de los votantes vive en municipios de marginación muy baja. Los datos sugieren que la barrera principal no es el acceso físico a la casilla, sino la relación de ciertos grupos urbanos y jóvenes con el proceso electoral.

### 5.2 Las secciones indígenas participan más

Las secciones con 40% o más de hogares indígenas (7% de los votantes) tienen una participación promedio de 63.1%, contra 55.1% del resto. La diferencia es mayor en intermedias (2015: 58.4 contra 47.6; 2021: 64.9 contra 51.7) y su brecha presidencial es menor (10.7 contra 13.6 puntos). Se concentran en P5 y P4.

### 5.3 La brecha presidencial-intermedia es el problema central

P0, P2 y P4 suman 52% de la población analizada y su participación en intermedias está entre 14 y 20 puntos por debajo de la de presidenciales. El principal desafío no es incorporar a quienes nunca votan, sino sostener en las intermedias la participación de quienes sí votan en presidenciales.

### 5.4 P1 es la señal de alerta

Es el único perfil en descenso sostenido, el de asignación menos clara y el que vive en secciones con menor escolaridad y uno de los de menor acceso a internet. Si la tendencia continúa, estos 5.9 millones de ciudadanos podrían acercarse al comportamiento de P0.

## 6. Estrategias diferenciadas

Cada estrategia parte del diagnóstico del perfil: barrera, mensaje, canal, momento y territorio. El CCPC registra si una persona votó, no por qué; por eso las barreras son hipótesis derivadas del patrón observado y se proponen para validarse mediante pilotos en los territorios prioritarios. Todos los mensajes son institucionales y no partidistas.

### P0 - Por convencer: acercamiento por relevancia

- **Barrera probable:** la participación electoral no forma parte de su rutina ni de su identidad.
- **Mensaje:** cómo las decisiones electorales afectan su vida cotidiana (empleo, seguridad, servicios urbanos), sin mensajes moralizantes.
- **Canal:** digital (redes sociales, video corto) y presencia en espacios urbanos (universidades, centros deportivos).
- **Momento y territorio:** activación 3-4 meses antes de las intermedias, donde más cae. Noroeste (Baja California, Sonora, Chihuahua, Sinaloa).

### P1 - Constancia que se apaga: reactivación temprana

- **Barrera probable:** desencanto progresivo; participaban y están dejando de hacerlo.
- **Mensaje:** reconocer su participación pasada y mostrar con datos locales que cada voto cuenta.
- **Canal:** radio local, perifoneo y organizaciones comunitarias. Su acceso a internet es de los más bajos (49%); lo digital es complementario.
- **Momento y territorio:** vinculación cívica permanente, no solo en periodo electoral. Occidente (Jalisco, Guanajuato, Colima); el subperfil 1.1, que pierde 3.8 puntos por elección, es el caso más urgente.

### P2 - Generación en ascenso: sostener el impulso

- **Barrera probable:** participación selectiva; responde a la elección presidencial pero no percibe las intermedias como relevantes.
- **Mensaje:** las intermedias definen servicios locales (transporte, educación, salud); apelación a su identidad generacional.
- **Canal:** digital (55% con internet, el más alto): redes sociales, video, contenido interactivo y compartible.
- **Momento y territorio:** esfuerzo concentrado 6 meses antes de las intermedias. Urbano nacional; el subperfil 2.1 (+6.4 puntos por elección) destaca en Tlaxcala y el centro.

### P3 - Paso firme: reconocer, mantener y multiplicar

- **Barrera probable:** ninguna crítica. El riesgo es darlo por sentado.
- **Mensaje:** reconocimiento por su constancia e invitación a ser multiplicadores en su entorno.
- **Canal:** mixto (52% con internet) y programas de promotores cívicos voluntarios reclutados de este perfil.
- **Momento y territorio:** mantenimiento continuo con refuerzo electoral. Occidente (Jalisco, Guanajuato, Michoacán); atención al subperfil 3.5, que va a la baja.

### P4 - Voces que avanzan: canalizar el liderazgo cívico femenino

- **Barrera probable:** la misma brecha presidencial-intermedia que P2, pero sobre una participación base alta. La oportunidad es el liderazgo cívico.
- **Mensaje:** invitación a roles de observadoras electorales, capacitadoras y promotoras del voto; visibilizar con datos el crecimiento de la participación femenina.
- **Canal:** digital (53% con internet) y redes de mujeres organizadas (asociaciones, sindicatos, comités vecinales).
- **Momento y territorio:** aprovechar el impulso posterior a cada presidencial para sostener las intermedias. Presencia nacional; el subperfil 4.3 (+7.3 puntos por elección, dominante en 201 municipios, fuerte en Tlaxcala) es buen candidato para un piloto.

### P5 - Pilar democrático: preservar, facilitar y transmitir

- **Barrera probable:** envejecimiento y movilidad; en zonas rurales, la distancia a la casilla.
- **Mensaje:** reconocimiento institucional e invitación a transmitir el hábito del voto a las generaciones jóvenes.
- **Canal:** presencial y medios tradicionales (radio comunitaria, televisión, impresos).
- **Momento y territorio:** permanente, con casillas accesibles y asistencia a personas mayores en cada jornada. Rural y Sur-Sureste; el subperfil 5.5 (76.5% de participación, 62% rural) destaca en Campeche.

### Matriz de intervención

| Perfil | Prioridad | Objetivo | Canal | Territorio | Cómo medir el avance |
|---|---|---|---|---|---|
| P0 Por convencer | Muy alta | Incorporar | Digital + presencial urbano | Noroeste | Participación en intermedias |
| P1 Constancia que se apaga | Alta (temprana) | Reactivar | Tradicional, comunidad | Occidente | Que la tendencia deje de caer |
| P2 Generación en ascenso | Alta | Sostener en intermedias | Digital | Nacional urbano | Brecha presidencial-intermedia menor |
| P3 Paso firme | Media | Mantener, multiplicar | Mixto | Occidente | Participación arriba de 60% |
| P4 Voces que avanzan | Media-alta | Liderazgo cívico | Digital + redes de mujeres | Nacional | Observadoras y capacitadoras del perfil |
| P5 Pilar democrático | Alta (preservar) | Facilitar, transmitir | Presencial, radio | Rural, Sur-Sureste | Participación joven en sus secciones |

Cada indicador se mide en las secciones donde el perfil tiene mayor concentración, comparando antes y después de la intervención.

## 7. Limitaciones

1. **Dato agregado, no individual.** La escolaridad y el internet son promedios de la sección (ECEG 2020), no características de las personas de la celda. Afirmaciones como "P4 vive en secciones de mayor escolaridad" no implican que sus integrantes tengan, individualmente, mayor escolaridad. Además, la celda no sigue a las mismas personas entre elecciones: describe a quienes tienen ese sexo y edad en esa sección en cada momento.
2. **Desfase temporal.** Los indicadores censales son de 2020; la lista nominal de 2024 refleja cambios demográficos y migratorios no capturados.
3. **La participación es un continuo.** No hay fronteras naturales entre grupos (separación máxima de 0.31). Los perfiles son zonas donde se concentran comportamientos parecidos, no categorías cerradas; por eso 31% de las personas tiene una asignación menos clara.
4. **Las barreras son hipótesis.** El CCPC muestra si se votó, no por qué. Las barreras y mensajes propuestos deben validarse con pilotos o encuestas antes de escalarse.
5. **Ausencia de Campeche en PJ 2025.** Los datos del Poder Judicial no incluyen a Campeche, por lo que sus celdas carecen de ese descriptor.
6. **Voto anticipado y prisión preventiva.** Estos registros (30,012 votos en total) no tienen sección ni edad, por lo que no se integran a la segmentación. Su volumen es marginal frente a los 71.2 millones del universo analizado.

## 8. Conclusiones

El análisis de clases latentes sobre la conducta electoral de 2009 a 2024 identifica seis perfiles ciudadanos que se reproducen casi idénticos al repetir el análisis (estabilidad de 0.98 sobre 1). Los perfiles se distinguen no solo por cuánto vota la gente, sino por cómo vota: la diferencia entre presidenciales e intermedias y la tendencia en el tiempo son dimensiones independientes del nivel, y son las que hacen falta para diseñar estrategias distintas.

Tres hallazgos desafían supuestos convencionales: la baja participación se concentra en zonas urbanas y entre jóvenes, no en zonas marginadas; las secciones indígenas participan por encima del promedio; y el principal reto no es incorporar a quienes nunca votan, sino sostener a quienes solo votan en presidenciales. P0, P2 y P4, que suman 52% de la población, votan entre 14 y 20 puntos menos en las intermedias.

Las estrategias propuestas responden a esta evidencia: canales digitales para los perfiles jóvenes y urbanos con mayor acceso a internet (P0, P2, P4), medios tradicionales y comunitarios para los de menor acceso (P1, P5), y mensajes diferenciados que van desde la relevancia personal (P0) hasta el liderazgo cívico femenino (P4) y la transmisión del hábito democrático entre generaciones (P5). La metodología es reproducible y puede reaplicarse con los datos de cada nueva elección para seguir la evolución de los perfiles.

## Referencias

- INE. *Conteos Censales de Participación Ciudadana 2009-2024.* Sistema CCPC, datos abiertos.
- INE. *Manual de uso de la plataforma de Conteos Censales de Participación Ciudadana.* 38 pp.
- INEGI-INE. *Estadísticas Censales a Escalas Geoelectorales 2020 (ECEG).* Censo de Población y Vivienda 2020 por sección electoral.
- CONABIO-INEGI. *División política municipal 2022.* Marco geoestadístico nacional.
