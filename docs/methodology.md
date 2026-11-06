# Metodología y Pipeline Técnico

Este documento resume las decisiones metodológicas del proyecto. El desarrollo completo de cada fase se encuentra detallado en la Sección 1 del [Informe Final](final_report.md).

## 1. Diseño de la Investigación

Se empleó una metodología mixta con tres fuentes de datos:

- **Oferta (Cuantitativa):** 1,200 anuncios de Revolico (300 por categoría: motos eléctricas, motos de combustión, bicicletas y patinetes).
- **Demanda (Cualitativa):** 30 entrevistas semiestructuradas a usuarios en La Habana, anonimizadas (E01–E30).
- **Normativa (Documental):** Revisión de 49 fuentes oficiales (Gacetas Oficiales, Aduana, ONEI, VEDCA, prensa oficial).

## 2. Pipeline de Datos en Python

El procesamiento técnico se estructuró en cuatro fases principales, más el procesamiento paralelo de entrevistas.

### Fase 1 — Web Scraping en dos etapas

Extracción mediante `httpx` y `BeautifulSoup`. El proceso constó de una fase de listado (148 páginas HTML de búsquedas) y una fase de detalle (882 archivos HTML de vehículos individuales). Se implementó caché local, reintentos automáticos, un límite ético de 150 peticiones por sesión y pausas de 3 segundos (60 segundos ante errores HTTP 429).

### Fase 2 — Limpieza de Datos

A partir de un universo bruto de 3,329 anuncios, se aplicó: deduplicación por título y tokens, normalización de moneda a USD, eliminación de valores atípicos (precios fuera del rango $100–$5,000), eliminación de ruido y agrupación en *buckets* de precios. Tras descartar 38 registros por inconsistencias, se extrajo la muestra final de 1,200 anuncios (300 por categoría).

### Fase 3 — Enriquecimiento con Regex

Uso de expresiones regulares para extraer campos técnicos (motor, voltaje, autonomía, cilindrada) y de estado legal (papeles, factura) desde el texto libre de las descripciones. El enriquecimiento se aplicó exclusivamente sobre los campos nulos, alcanzando una cobertura técnica del 44% al 50% en variables clave. Se eligió Regex sobre LLM por ser determinista y auditable.

### Fase 4 — Machine Learning (K-Means)

Estandarización con `StandardScaler` y segmentación con K-Means (`random_state=42`, `n_init=10`) en **tres enfoques**:

- **Motos eléctricas:** 3 clústeres (Silhouette 0.548, ANOVA p < 0.0001) sobre 231 motos con datos completos.
- **Motos de combustión:** 3 clústeres (Silhouette 0.575) sobre 272 motos con precio y cilindrada.
- **Global:** 3 capas socioeconómicas sobre los 1,200 anuncios.

## 3. Procesamiento de Entrevistas

Las 30 entrevistas de audio fueron transcritas localmente con `faster-whisper` (modelo medium, CPU, precisión int8) y estructuradas con el LLM local Ollama (`qwen2.5:3b`). Posteriormente se realizó una **validación y corrección manual** del JSON para asegurar la fidelidad de las citas y mitigar cualquier alucinación del modelo.

## 4. Artefactos del Proyecto

- Scripts de scraping: `src/scrapers/`
- Scripts de análisis: `src/analysis/`
- Scripts de tabulación de entrevistas: `src/analysis/tabulacion_entrevistas.py`
- Scripts de gráficos: `src/analysis/graficos_finales.py`
- Datos procesados: `data/processed/final/`
- Gráficos generados: `reports/plots/`
- Informe final: `docs/final_report.md`
