# Metodología y Pipeline Técnico

Este documento resume las decisiones metodológicas del proyecto. El desarrollo completo de cada fase se encuentra detallado en la sección 1 del [Informe Final](final_report.md).

## 1. Diseño de la Investigación
Se empleó una metodología mixta con tres fuentes de datos:
*   **Oferta (Cuantitativa):** 1,200 anuncios de Revolico (300 por categoría: motos eléctricas, combustión, bicicletas y patinetes).
*   **Demanda (Cualitativa):** 30 entrevistas semiestructuradas a usuarios en La Habana.
*   **Normativa (Documental):** Revisión de 49 fuentes oficiales (Gacetas, Aduana, ONEI, VEDCA).

## 2. Pipeline de Datos en Python
El procesamiento técnico constó de las siguientes fases:
1.  **Web Scraping:** Extracción mediante `httpx` y `BeautifulSoup`. Se implementó caché local y límites éticos de peticiones.
2.  **Limpieza y Embudo:** Deduplicación, normalización de precios a USD y eliminación de atípicos. De 3,329 anuncios brutos se extrajo la muestra final de 1,200.
3.  **Enriquecimiento (Regex):** Uso de expresiones regulares para extraer campos técnicos (motor, autonomía) y legales (papeles) desde el texto libre.
4.  **Machine Learning:** Estandarización (`StandardScaler`) y segmentación de la oferta mediante el algoritmo **K-Means** (3 clústeres, seed=42).
5.  **Procesamiento de Audio:** Transcripción con `faster-whisper` (modelo medium, CPU) y estructuración con el LLM local `Ollama`.

## 3. Artefactos del Proyecto
*   Scripts de scraping: `src/scrapers/`
*   Scripts de análisis: `src/analysis/`
*   Datos procesados: `data/processed/final/`
