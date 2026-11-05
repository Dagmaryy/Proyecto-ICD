# Registro de Decisiones Técnicas (ADR)

Este documento registra las decisiones clave tomadas durante el desarrollo del proyecto, el contexto de cada una y sus consecuencias.

## Decisión 1: Uso de Regex para enriquecimiento en lugar de un LLM (Fase 3)
*   **Contexto:** Los anuncios de Revolico tenían campos técnicos (motor, voltaje, autonomía) vacíos en la base de datos, pero presentes en el texto libre de las descripciones.
*   **Decisión:** Se implementó un script en Python utilizando expresiones regulares (Regex) para extraer estos campos.
*   **Razón:** Se probó inicialmente con un modelo local (Qwen 2.5b), pero arrojaba "alucinaciones" (confundía voltajes con potencias). El Regex es determinista, rápido y auditable.
*   **Consecuencia:** Se logró un 44-50% de cobertura técnica sin riesgo de inventar datos. Los vacíos restantes se documentaron como limitación del anuncio original.

## Decisión 2: Configuración del Clustering (K-Means)
*   **Contexto:** Se necesitaba segmentar el mercado de motos eléctricas. El archivo `config.yaml` original sugería 6 clústeres, pero tras el análisis exploratorio (EDA) visual, 6 grupos no aportaban valor diferenciador.
*   **Decisión:** Se redujo a **3 clústeres** (Gama Económica, Media y Alta) utilizando `StandardScaler` y `random_state=42`.
*   **Razón:** Tres grupos representan mejor la estratificación socioeconómica real del mercado cubano.
*   **Consecuencia:** Se validó la decisión estadísticamente mediante el Coeficiente de Silhouette (0.548) y una prueba ANOVA (p-valor 0.00000).

## Decisión 3: Pipeline de procesamiento de entrevistas (Whisper + Ollama)
*   **Contexto:** Se contaba con 30 audios de entrevistas que debían convertirse en datos estructurados.
*   **Decisión:** Transcribir localmente con `faster-whisper` (modelo medium, CPU) y estructurar el texto con un LLM local (`Ollama`).
*   **Razón:** Garantizar la privacidad de los entrevistados y evitar costos de APIs en la nube.
*   **Consecuencia:** Se generó un JSON. Sin embargo, debido a que el modelo local aún presentaba pequeños fallos de formato, se decidió hacer una **validación y corrección manual** del JSON final para asegurar la calidad.

## Decisión 4: Priorizar el Canal Informal (Revolico) como fuente primaria
*   **Contexto:** Existía la opción de centrarse en las tiendas formales (VEDCA, CIMEX).
*   **Decisión:** Se le dio un peso del 80% al análisis de los 1,200 anuncios de Revolico.
*   **Razón:** Revolico refleja el mercado real al que accede la mayoría de la población, mientras que el canal formal tiene limitaciones de stock y acceso.
*   **Consecuencia:** Se evidenció que el mercado informal maneja sobreprecios y una alta opacidad legal en comparación con el canal formal.

## Decisión 5: Estrategia de recuperación ante el fallo de hardware
*   **Contexto:** A mitad del proyecto, la partición raíz de Linux colapsó, dejando inaccesibles los 1,200 JSONs y el código.
*   **Decisión:** No reinstalar de inmediato. Primero, usar el Live USB para ejecutar herramientas forenses (`TestDisk`) y rescatar los datos a una partición de Windows.
*   **Razón:** Proteger el activo más valioso: los datos extraídos durante semanas.
*   **Consecuencia:** Se rescató el 100% de los datos. Se perdió la caché HTML (recuperada luego desde un respaldo) y la base de datos de OpenCode. El proyecto se reinstaló sobre una base sólida y segura.
