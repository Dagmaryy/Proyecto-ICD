# Análisis de Mercado de Vehículos Ligeros en La Habana

## Resumen Ejecutivo
Este estudio presenta un análisis integral del mercado de vehículos ligeros (motos eléctricas, motos de combustión, bicicletas y patinetes) en La Habana. A través de una metodología mixta que combinó el análisis de 1,200 anuncios de Revolico, 30 entrevistas a usuarios y la revisión de 30 fuentes normativas, se identificó un mercado centralizado en Centro Habana y Playa, con una mediana de precios de $2,500 USD para motos eléctricas. El estudio revela una paridad de precios entre el canal formal e informal, y una profunda brecha entre los márgenes comerciales regulados por ley (3%) y la realidad del mercado informal.

## 1. Introducción y Metodología
El presente estudio analiza el mercado de vehículos ligeros en La Habana (motos eléctricas, motos de combustión, bicicletas y patinetes). Para ello, se empleó una metodología mixta que incluye la extracción de 1,200 anuncios del mercado informal (plataforma Revolico), el análisis de 30 entrevistas a usuarios y la revisión de 30 fuentes documentales e institucionales (Gaceta Oficial, Aduana, prensa oficial y catálogos del canal formal como VEDCA e iTENCEL). El procesamiento de los datos se realizó mediante herramientas de ciencia de datos en Python.

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

*(Nota metodológica: Esta sección se completará con los datos del análisis de las 30 entrevistas).*

### 3.1. Perfil demográfico (P11)
[Pendiente de redacción con datos del CSV de entrevistas: edad, ocupación y municipio].

### 3.2. Uso y Contexto (P12)
[Pendiente de redacción sobre el uso principal: trabajo, transporte personal o mensajería].

### 3.3. Motivación de compra (P13 y P14)
[Pendiente de redacción sobre las razones de elección (precio, autonomía) y el canal de compra].

### 3.4. Operación y Resiliencia (P16 y P17)
[Pendiente de redacción sobre frecuencia de carga, apagones, autonomía real y fallos técnicos].

### 3.5. Legalidad y Seguridad (P11 y P12)
[Pendiente de redacción sobre tenencia de licencia, uso de pedales y métodos de protección].

### 3.6. Satisfacción y Preferencia (P13)
[Pendiente de redacción sobre la preferencia entre eléctrica y gasolina y las citas textuales de los usuarios].

## 4. Entorno Normativo y Canal Formal (Institucional)

### 4.1. Marco legal y aranceles (Preguntas 21, 22 y 23)
Según el Decreto 163/2026 y las resoluciones de la Aduana General, las personas naturales pueden importar, por única vez, hasta **dos ciclomotores o motocicletas eléctricas**. La Gaceta 83/2026 permite también la importación de hasta dos bicicletas o patinetes. El pago de aranceles para un ciclomotor eléctrico es de solo **22 USD**, y se exonera la importación de motores eléctricos para remotorización.

### 4.2. Comparación de precios: Formal vs. Informal (Pregunta 24)
Existe una diferencia clara entre los precios del canal formal y el informal. En el canal formal:
*   **VEDCA** vende motos eléctricas entre **$1,300 USD** y **$2,115 USD**.
*   **CIMEX** comercializa modelos (como la Moto Diana) por casi **$3,000 USD**.
*   **iTENCEL** (marketplace de Mipymes) ofrece modelos como el Topmaq F3 por **$2,700 USD**.

Al comparar con la mediana del mercado informal (Revolico) de **$2,500 USD**, se concluye que **el mercado informal no es más barato**. Los precios se equiparan, e incluso superan a las tiendas formales en algunos modelos, lo que indica que los compradores pagan una prima por la inmediatez y la disponibilidad, no por un ahorro real.

### 4.3. Garantías y postestad (Preguntas 25 y 26)
El canal formal ofrece garantías reales (VEDCA ofrece **6 meses**), mientras que en Revolico la garantía es inexistente o de palabra, lo que constituye el principal riesgo. El stock en tiendas formales está limitado por la capacidad de importación, mientras que el mercado informal ofrece disponibilidad inmediata.

### 4.4. Talleres, Repuestos y Capacidad de Actores (Preguntas 27 a 30)
*   **P27 y P28 (Talleres y Repuestos):** La normativa oficial (Gaceta Oficial No. 65) establece la autorización para la "comercialización de piezas de repuesto, agregados y accesorios". Se documenta la existencia de talleres estatales y privados (como D. Fabrik en Diez de Octubre). Sin embargo, las fuentes oficiales no desglosan un listado de las fallas mecánicas más comunes, un dato que suele obtenerse de la observación empírica.
*   **P29 (Margen comercial):** El Decreto 163/2026 establece explícitamente un **margen comercial de hasta el tres por ciento (3%)** en dólares para la comercialización formal, un control estricto que contrasta con el mercado informal.
*   **P30 (Actores no estatales):** La Gaceta 65/2026 autoriza a las personas jurídicas no estatales (Mipymes) a realizar el ensamblaje o fabricación de ciclomotores y motos. Esta capacidad, sumada a la importación de piezas con aranceles preferenciales, representa un canal semi-formal en crecimiento.

## 5. Discusión: La brecha entre la ley y el mercado
El cruce de los datos extraídos de Revolico con las fuentes documentales permite identificar una distorsión entre lo que dicta la ley y la realidad. La Gaceta Oficial No. 65/2026 establece un margen comercial de hasta el **3%** para la comercialización formal, lo que permite a VEDCA ofrecer motos desde **$1,925 USD**. Sin embargo, en Revolico, la mediana es de **$2,500 USD**. Esta diferencia de más de $500 USD sugiere que los importadores informales aplican un margen de intermediación mucho más agresivo (estimado entre un 20% y 40%), aprovechando la inmediatez y la falta de stock en las tiendas estatales.

## 6. Limitaciones del Estudio
1.  **Pérdida de datos por fallo técnico:** Un fallo en el disco duro requirió una reinstalación del sistema. Aunque los datos de los anuncios fueron recuperados exitosamente, la base de datos de la herramienta OpenCode (utilizada para NLP) se corrompió.
2.  **Informalidad del mercado:** El alto porcentaje de nulos en los campos de "estado" y "papeles" (más del 75%) impidió generar un análisis concluyente sobre la legalidad de los vehículos.
3.  **Filtrado de fuentes normativas:** Las 30 fuentes documentales fueron filtradas, extrayendo exclusivamente los artículos referentes a motos, bicicletas y patinetes, descartando normativas de otros vehículos (autos, remolques).

## 7. Conclusiones
El mercado de vehículos ligeros en La Habana se caracteriza por una alta informalidad, concentración geográfica en Centro Habana y Playa, y una paridad de precios entre el canal formal (VEDCA, CIMEX) y el informal (Revolico). A pesar de las flexibilizaciones legales del Decreto 163/2026, el mercado informal sigue dominando el volumen de oferta, aunque carece de garantías y trazabilidad legal para el comprador.
