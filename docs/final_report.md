# Análisis de Mercado de Vehículos Ligeros en La Habana

## Resumen Ejecutivo
Este estudio presenta un análisis integral del mercado de vehículos ligeros (motos eléctricas, de combustión, bicicletas y patinetes) en La Habana, abordando tanto la oferta del mercado informal como la percepción de los usuarios y el marco regulatorio vigente. Para ello, se empleó una metodología mixta que combinó el análisis masivo de anuncios clasificados, entrevistas en profundidad a usuarios y la revisión de fuentes normativas oficiales.

Los hallazgos principales revelan un mercado fuertemente centralizado en los municipios de mayor densidad comercial de la capital, donde la oferta informal domina en volumen. Contra la creencia popular, el estudio demuestra que el mercado informal no ofrece precios más competitivos que el canal formal. Por el contrario, los compradores asumen un sobreprecio significativo, impulsados por la necesidad de inmediatez y la escasez de inventario en las tiendas estatales. 

Asimismo, se identificó una profunda brecha entre la normativa estatal, que regula estrictamente los márgenes comerciales y establece incentivos fiscales para la movilidad eléctrica, y la realidad de un mercado informal caracterizado por la falta de garantías y la opacidad documental. Finalmente, el estudio concluye que la adopción masiva de vehículos eléctricos en La Habana no responde a una conciencia ecológica, sino a una estrategia de resiliencia y supervivencia económica de la población frente a la crisis del transporte público y el alto costo de los combustibles fósiles.

## 1. Introducción y Metodología

El presente estudio analiza el mercado de vehículos ligeros en La Habana (motos eléctricas, motos de combustión, bicicletas y patinetes), abarcando tanto la oferta del mercado informal como la percepción de los usuarios y el marco regulatorio vigente. La elección de este objeto de estudio responde al creciente papel de estos vehículos como alternativa de movilidad ante las limitaciones del transporte público y la crisis energética del país. 

Para abordar esta problemática, se empleó una metodología mixta (cuantitativa y cualitativa) que integró tres fuentes de información fundamentales:
1.  **Mercado informal:** Extracción y análisis de un corpus de 1,200 anuncios publicados en la plataforma Revolico (300 por cada categoría: motos eléctricas, combustión, bicicletas y patinetes).
2.  **Usuarios:** Realización de 30 entrevistas semiestructuradas a residentes en La Habana para comprender las motivaciones de compra, hábitos de uso y principales problemáticas.
3.  **Marco normativo y canal formal:** Revisión documental de más de 30 fuentes oficiales (Gacetas Oficiales, resoluciones de la Aduana, prensa oficial) y catálogos de tiendas estatales (VEDCA) y Mipymes (iTENCEL).

Para garantizar el rigor y la reproducibilidad técnica del análisis, el procesamiento de datos se ejecutó en Python, estructurado en cuatro fases principales:
*   **Fase 1 (Scraping):** Extracción automatizada de los anuncios mediante la librería `BeautifulSoup` y `httpx`, respetando los tiempos de espera éticos de la plataforma.
*   **Fase 2 (Limpieza):** Estandarización de variables (precios, municipios, tipos de vehículos) y eliminación de registros duplicados o inconsistentes.
*   **Fase 3 (Enriquecimiento):** Uso de expresiones regulares (Regex) para extraer marcas y estado legal directamente de los textos de los anuncios, llenando los vacíos de información de la base de datos original.
*   **Fase 4 (Análisis Estadístico):** Aplicación de estadística descriptiva (medianas, conteos) y algoritmos de *Machine Learning* (K-Means) para la segmentación de la oferta. 

Paralelamente, las 30 entrevistas de audio fueron transcritas de forma local utilizando modelos de IA (Whisper) y posteriormente procesadas con modelos de lenguaje locales (Ollama) para su estructuración en formato JSON, garantizando la privacidad de los datos. Finalmente, se realizó una validación manual de dichas entrevistas para asegurar la fidelidad de las citas y evitar sesgos o alucinaciones del modelo.

## 2. Resultados de la Oferta (Anuncios)

### 2.1. Precios por tipo de vehículo (Pregunta 2)
A partir del análisis de los 1,200 anuncios, se observa una clara jerarquía de precios según el tipo de vehículo. Las **motos eléctricas** presentan el precio mediano más alto, alcanzando los **$2,500 USD**. Le siguen las **motos de combustión** con una mediana de **$2,100 USD**. En un rango mucho más asequible se ubican las **bicicletas** (mediana de **$600 USD**) y los **patinetes** (mediana de **$595 USD**). Esto refleja que las motos son el principal medio de transporte motorizado en el mercado informal.

### 2.2. Marcas y Precios (Preguntas 1 y 3)
En el segmento de motos eléctricas, el mercado está dominado por cinco marcas principales. El análisis de frecuencia y precios revela la siguiente estructura:

| Marca | Cantidad de Anuncios | Precio Mediano (USD) |
| :--- | :---: | :---: |
| Topmaq | 55 | $2,600 |
| Vedca | 26 | $1,925 |
| Mountain | 22 | $2,800 |
| Yoazaki | 18 | $2,950 |
| Izuki | 17 | $2,800 |

Se observa que, aunque Topmaq lidera en volumen de oferta, Yoazaki ostenta el precio mediano más alto, lo que sugiere una percepción de mayor calidad o exclusividad en el mercado.

### 2.3. Distribución geográfica (Pregunta 4)
El análisis geográfico de los anuncios revela una fuerte centralización de la oferta en determinados municipios de La Habana. **Centro Habana** lidera con **303 anuncios**, seguido de **Playa** con **217**. Les siguen Diez de Octubre (131), Plaza (128) y Cerro (75). Los municipios periféricos presentan una oferta marginal, lo que sugiere que el mercado informal se concentra en zonas de alta densidad poblacional y flujo comercial.

### 2.4. Datos técnicos y Valor (Preguntas 5 y 6)
Las motos eléctricas en el mercado informal presentan un estándar técnico bastante homogéneo. La mediana de potencia es de **3,000 W**, con un voltaje de **72 V** y una autonomía de **120 km**. 
En términos de valor, el precio mediano de $2,500 USD dividido entre estas características arroja un costo aproximado de **$0.83 USD por cada vatio** de potencia, y de **$20.83 USD por cada kilómetro** de autonomía.

### 2.5. Formalidad y Logística (Preguntas 7, 8 y 9)
Un hallazgo crítico es la falta de información legal. El **83.2% de los anuncios no especifica** si el vehículo es nuevo o usado, y el **77.8% no menciona** si cuenta con papeles en regla. Esto evidencia la alta informalidad y el riesgo del mercado.
En cuanto a la logística, el **44% de los anuncios sí incluye transporte** o entrega en La Habana. Finalmente, el mercado está atomizado: existen **580 vendedores únicos**, y el mayor intermediario o revendedor solo concentra **27 anuncios**.

### 2.6. Segmentación de la oferta mediante Clustering (Pregunta 10)
Para comprender la estructura del mercado, se aplicó un algoritmo de agrupamiento (K-Means) sobre las 231 motos eléctricas que contaban con datos completos de precio, potencia y autonomía. El análisis reveló la existencia de tres segmentos claros y estadísticamente diferenciados:

1.  **Gama Económica (72 anuncios):** Agrupa las motos de entrada. El precio promedio es de **$1,322 USD**, con una potencia media de **968 W** y una autonomía de **70 km**. Están orientadas a trayectos cortos y presupuestos ajustados.
2.  **Gama Media (127 anuncios):** Es el segmento dominante del mercado. El precio promedio es de **$2,601 USD**, con una potencia de **2,728 W** y **121 km** de autonomía. Representa el estándar de compra del consumidor, buscando un equilibrio entre rendimiento y precio.
3.  **Gama Alta (32 anuncios):** Vehículos premium o de altas prestaciones. El precio promedio asciende a **$3,104 USD**, ofreciendo motores de **4,140 W** y una autonomía de **176 km**. Son adquiridos por usuarios que requieren máxima potencia y recorridos largos.

*Este análisis confirma que el mercado informal no es homogéneo, sino que está estratificado en capas socioeconómicas bien definidas.*

## 3. Perfil del Usuario y Entrevistas (Preguntas 11 a 20)

A partir del análisis de las 30 entrevistas realizadas a usuarios de vehículos ligeros en La Habana, se construyó el siguiente perfil.

### 3.1. Perfil demográfico y ubicación (P11)
El usuario típico de este mercado es una persona joven, con una **edad promedio de 27.1 años**, aunque el rango etario es bastante amplio, abarcando desde estudiantes de 16 años hasta profesionales de 63 años. 
En cuanto a la distribución geográfica, la muestra se concentró principalmente en tres municipios: **Habana del Este, Arroyo Naranjo y Playa** (con 4 entrevistados cada uno), seguidos de cerca por otros como Marianao y Diez de Octubre. Predominan los estudiantes universitarios y los trabajadores por cuenta propia (barberos, cocineros, cuentapropistas), así como profesores universitarios.

### 3.2. Uso y Contexto (P12)
El uso del vehículo es fundamentalmente un **transporte personal (27 de 30 entrevistados)**. Los usuarios lo utilizan para trasladarse a sus centros de estudio o trabajo, hacer mandados y visitar amistades. Solo un pequeño grupo de **3 entrevistados (10%)** declaró utilizar el vehículo para fines comerciales, específicamente para servicios de mensajería o entregas, compaginándolo con sus actividades principales.

### 3.3. Compra y Precio (P15 y P14)
El precio mediano pagado por los entrevistados fue de **$1,400 USD**, con un promedio de $1,363 USD. Es importante destacar que casi la totalidad de las transacciones se realizaron en **dólares estadounidenses (28 de 30)**, con casos aislados en CUP o EUR.
La mayoría de las compras se realizaron a través de **intermediarios, importadores particulares o conocidos**, y muchos de los vehículos fueron traídos del extranjero (Panamá, Estados Unidos, China) por familiares o amigos. Los usuarios destacan que elegir la moto eléctrica les permitió acceder a un vehículo más económico que las motos de combustión, sin necesidad de lidiar con los altos precios de la gasolina.

### 3.4. Operación, Apagones y Autonomía (P16 y P17)
La crisis energética es un factor determinante en la experiencia del usuario. **El 50% de los entrevistados (15 de 30) afirmó haber tenido problemas para cargar sus vehículos durante los apagones**. Para mitigar esto, los usuarios han desarrollado estrategias como cargar las baterías extraíbles en el trabajo (ej. universidades) o cargar en casas de familiares en zonas con menor afectación. 
Respecto al rendimiento, **8 de 30 usuarios reportaron que la autonomía real ha disminuido con el tiempo**, debido al desgaste natural de las celdas de la batería (especialmente en modelos con más de 3 años de uso).

### 3.5. Legalidad y Seguridad (P11 y P12)
Existe una alta prevalencia de operación al margen de la normativa. **16 de los 30 entrevistados afirmaron no tener licencia de conducción**. Muchos justifican esto comprando modelos clasificados como "bicimotos" (con pedales, aunque los quiten después) para evadir la necesidad legal de licencia. 
Para proteger sus vehículos, los métodos más comunes son el uso de **candados, alarmas (algunas con GPS) y guardarlos dentro de sus casas o garajes**, dado el alto índice de robos que mencionan en las entrevistas.

### 3.6. Satisfacción y Preferencia (P13)
A pesar de los problemas de apagones, la falta de licencia y el desgaste de las baterías, la satisfacción con la tecnología eléctrica es abrumadora. **23 de los 30 entrevistados (76%) prefieren la moto eléctrica sobre la de combustión**. La razón principal es puramente económica: la gasolina es percibida como excesivamente cara y difícil de conseguir. Los pocos que prefieren la combustión (4 de 30) lo hacen por la durabilidad del motor, la velocidad o porque tienen la posibilidad económica de mantenerla. 

En conclusión, la moto eléctrica se ha consolidado como el vehículo de movilidad por excelencia para el habanero de a pie, no por una conciencia ecológica, sino por pura supervivencia económica frente a la crisis del transporte y el combustible.

## 4. Entorno Normativo y Canal Formal (Institucional)

### 4.1. Marco legal, límites de importación y aranceles (Preguntas 21, 22 y 23)

El marco legal vigente está definido por el **Decreto 163/2026**, la **Resolución 312/2026 de la Aduana** y la **Resolución 340/2026**, publicadas en las Gacetas Oficiales No. 65 y 83. 

**Límites de importación (P21):**
Según el Artículo 10 del Decreto 163, las personas naturales pueden importar como equipaje no acompañado o envío:
*   Hasta **dos (2) ciclomotores o motocicletas eléctricas** (con o sin sidecar).
*   Un (1) ciclomotor o motocicleta de combustión de hasta 250 cc cada 5 años.
*   Hasta dos (2) bicicletas o patinetas eléctricas.

**Valores de referencia y Aranceles (P22):**
La Resolución 340 establece los valores de referencia en aduana (base imponible) para calcular los impuestos:
*   Motocicleta eléctrica: **$200.00 USD**.
*   Motocicleta de combustión sin sidecar: **$850.00 USD**.
*   Motocicleta de combustión con sidecar: **$950.00 USD**.
*   Bicicleta eléctrica: **$100.00 USD**.
*   Patineta eléctrica: **$60.00 USD**.
*   Batería de litio: **$60.00 USD**.

**Entidades autorizadas (P23):**
La Resolución 104 del MINCEX autoriza explícitamente a **SOLIMPORT S.U.R.L.** la importación de ciclomotores y motocicletas. Asimismo, la Resolución 17 del MINCIN autoriza a **DIVSE** e **IMPLUS** (del Grupo PALCO) la comercialización de estos vehículos en USD.

### 4.2. Comparación de precios: Formal vs. Informal (Pregunta 24)

Existe una diferencia clara entre los precios del canal formal y el informal. En el canal formal, **VEDCA** vende motos eléctricas entre **$1,300 USD** y **$2,115 USD**, mientras que **CIMEX** comercializa modelos (como la Moto Diana) por casi **$3,000 USD**, y los marketplaces de Mipymes como **iTENCEL** ofrecen modelos (ej. Topmaq F3) por **$2,700 USD**.

Al comparar con la mediana del mercado informal (Revolico) de **$2,500 USD**, se concluye que **el mercado informal no es más barato**. Los precios se equiparan, e incluso superan a las tiendas formales en algunos modelos. 

La siguiente tabla resume las diferencias estructurales entre ambos canales:

| Característica | Canal Formal (VEDCA / CIMEX) | Canal Informal (Revolico) |
| :--- | :--- | :--- |
| **Precio Promedio** | $1,300 - $2,115 USD (VEDCA) | $2,500 USD (Mediana) |
| **Garantía** | 6 meses (VEDCA) | Inexistente o de palabra |
| **Disponibilidad** | Limitada por stock estatal | Inmediata |
| **Legalidad (Papeles)** | 100% legalizado y facturado | 77.8% no menciona papeles |
| **Riesgo de Estafa** | Nulo | Documentado (ej. caso de $1,200 USD) |

Esta paridad de precios indica que los compradores pagan una prima por la inmediatez y la disponibilidad en el mercado informal, no por un ahorro real frente a las tiendas estatales o las Mipymes autorizadas.

### 4.3. Garantías y postventa (Preguntas 25 y 26)
El canal formal ofrece garantías reales (VEDCA ofrece **6 meses**), mientras que en Revolico la garantía es inexistente o de palabra, lo que constituye el principal riesgo. El stock en tiendas formales está limitado por la capacidad de importación, mientras que el mercado informal ofrece disponibilidad inmediata.

**Sobre el stock y los tiempos de entrega (P26):**
Según la información oficial de VEDCA, el proceso de compra opera bajo la modalidad de "llave en mano": el cliente compra en la tienda (42 y 23, Playa), realiza el pago bancario, y la orden se procesa en aproximadamente **24 horas** para que el cliente retire el vehículo en la propia fábrica. Aunque las fuentes oficiales no documentan la existencia de "listas de espera" o colas públicas, la limitada capacidad de importación del país y la alta demanda (evidenciada en las entrevistas) sugieren que el acceso a estos vehículos formales puede estar sujeto a la disponibilidad de inventario en el momento de la compra.

### 4.4. Talleres, Repuestos y Capacidad de Actores (Preguntas 27 a 30)

*   **P27 y P28 (Talleres y Repuestos):** La normativa oficial (Gaceta Oficial No. 65) establece la autorización para la "comercialización de piezas de repuesto, agregados y accesorios". En cuanto a la infraestructura de reparación, se documentan dos talleres principales en La Habana: el **Taller Oficial de VEDCA**, ubicado en Avenida Independencia (Boyeros), que brinda asistencia técnica directa para sus modelos, y el **Taller E-Motors** (privado), ubicado en Juan Delgado #224, Diez de Octubre, que se especializa en la reparación de motos eléctricas y de combustión. Aunque las fuentes oficiales no desglosan un listado de las fallas mecánicas más comunes, los usuarios en las entrevistas mencionaron recurrentemente problemas con el desgaste de las baterías, los frenos y los controladores.
*   **P29 (Margen comercial):** El Decreto 163/2026 establece explícitamente un **margen comercial de hasta el tres por ciento (3%)** en dólares para la comercialización formal, un control estricto que contrasta con el mercado informal.
*   **P30 (Actores no estatales):** La Gaceta 65/2026 autoriza a las personas jurídicas no estatales (Mipymes) a realizar el ensamblaje o fabricación de ciclomotores y motos. Esta capacidad, sumada a la importación de piezas con aranceles preferenciales, representa un canal semi-formal en crecimiento.

### 4.5. Contexto de Seguridad Vial (Datos ONEI 2025)

Para dimensionar el impacto de los vehículos ligeros (motos y bicicletas) en el entorno urbano, se consultó el Anuario Estadístico de Cuba 2025 (Capítulo 13: Transporte y Seguridad Vial) de la ONEI. 

Aunque el parque automotor de cuatro ruedas sigue siendo el principal involucrado en siniestros, los datos oficiales revelan la vulnerabilidad de los conductores de ciclos (motos y bicicletas). En 2025, las **"violaciones de los conductores de ciclos"** provocaron **31 accidentes**, dejando **5 fallecidos** y **31 lesionados** en todo el país. 
A nivel macro, La Habana es la provincia con mayor siniestralidad del país (2,590 accidentes en 2025), lo que correlaciona con la alta densidad de vehículos ligeros y la congestión del tráfico que los usuarios mencionaron en las entrevistas. Este contexto refuerza el hallazgo cualitativo de que el mercado informal opera en un entorno de alto riesgo, no solo legal (por la falta de papeles y licencias), sino también físico para los conductores.

## 5. Discusión: La brecha entre la ley y el mercado
El cruce de los datos extraídos de Revolico con las fuentes documentales permite identificar una distorsión entre lo que dicta la ley y la realidad. La Gaceta Oficial No. 65/2026 establece un margen comercial de hasta el **3%** para la comercialización formal, lo que permite a VEDCA ofrecer motos desde **$1,925 USD**. Sin embargo, en Revolico, la mediana es de **$2,500 USD**. Esta diferencia de más de $500 USD sugiere que los importadores informales aplican un margen de intermediación mucho más agresivo (estimado entre un 20% y 40%), aprovechando la inmediatez y la falta de stock en las tiendas estatales.

"Esta realidad es confirmada por los usuarios en las entrevistas: el 76% prefiere la moto eléctrica, a pesar de pagar sobreprecios en el mercado informal, porque la gasolina representa un gasto inasumible. Así, el sobreprecio del mercado informal es, en realidad, el costo de la supervivencia."

## 6. Limitaciones del Estudio
Este estudio presenta las siguientes limitaciones metodológicas:

1.  **Pérdida de datos por fallo técnico:** Un fallo en el disco duro requirió una reinstalación del sistema. Aunque los datos de los anuncios fueron recuperados exitosamente mediante herramientas forenses, la base de datos de la herramienta OpenCode se corrompió.
2.  **Informalidad del mercado:** El alto porcentaje de nulos en los campos de "estado" y "papeles" (más del 75%) impidió generar un análisis concluyente sobre la legalidad de los vehículos en el mercado informal.
3.  **Filtrado de fuentes normativas:** Las 30 fuentes documentales fueron filtradas, extrayendo exclusivamente los artículos referentes a motos, bicicletas y patinetes, descartando normativas de otros vehículos (autos, remolques).
4.  **Cobertura del canal informal:** La muestra se limita a los anuncios publicados en la plataforma Revolico. El mercado informal de La Habana también opera a través de otros canales cerrados (grupos de Telegram, WhatsApp, Facebook) que no fueron capturados en este scraping, lo que significa que los datos representan una muestra significativa, pero no la totalidad del mercado.
5.  **Sesgo temporal:** Revolico muestra principalmente anuncios activos de los últimos 14 días. Por lo tanto, los precios reflejan una "instantánea" del mercado en septiembre-octubre de 2026, y no una evolución histórica a largo plazo.

## 7. Referencias
*   Gaceta Oficial de la República de Cuba. (2026). *Decreto 163/2026* y *Gaceta No. 65 y 83*.
*   Aduana General de la República. (2026). *Resoluciones y aranceles aduaneros*.
*   VEDCA. (2026). *Catálogo de productos y precios*.
*   Cibercuba. (2025). *Noticias sobre precios de motos en CIMEX y Tiendas Caribe*.
*   Datos primarios extraídos de Revolico (septiembre-octubre 2026) y 30 entrevistas a usuarios en La Habana.

## 8. Conclusiones
El mercado de vehículos ligeros en La Habana se caracteriza por una alta informalidad, concentración geográfica en Centro Habana y Playa, y una paridad de precios entre el canal formal (VEDCA, CIMEX) y el informal (Revolico). A pesar de las flexibilizaciones legales del Decreto 163/2026, el mercado informal sigue dominando el volumen de oferta, aunque carece de garantías y trazabilidad legal para el comprador.
