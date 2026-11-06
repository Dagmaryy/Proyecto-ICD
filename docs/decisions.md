# Registro de Decisiones Técnicas (ADR)

Este documento registra las decisiones clave tomadas durante el desarrollo del proyecto, el contexto de cada una y sus consecuencias.

## Decisión 1: Uso de Regex para enriquecimiento en lugar de un LLM (Fase 3)

- **Contexto:** Los anuncios de Revolico tenían campos técnicos (motor, voltaje, autonomía) vacíos en la base de datos, pero presentes en el texto libre de las descripciones.
- **Decisión:** Se implementó un script en Python utilizando expresiones regulares (Regex) para extraer estos campos.
- **Razón:** Se probó inicialmente con un modelo local (`qwen2.5:3b`), pero arrojaba "alucinaciones" (confundía voltajes con potencias). El Regex es determinista, rápido y auditable.
- **Consecuencia:** Se logró un 44-50% de cobertura técnica sin riesgo de inventar datos. Los vacíos restantes se documentaron como limitación del anuncio original.

## Decisión 2: Configuración del Clustering (K-Means)

- **Contexto:** Se necesitaba segmentar el mercado de motos eléctricas. El archivo `config.yaml` original sugería 6 clústeres, pero tras el análisis exploratorio (EDA) visual, 6 grupos no aportaban valor diferenciador.
- **Decisión:** Se redujo a **3 clústeres** (Gama Económica, Media y Alta) utilizando `StandardScaler` y `random_state=42`.
- **Razón:** Tres grupos representan mejor la estratificación socioeconómica real del mercado cubano.
- **Consecuencia:** Se validó la decisión estadísticamente mediante el Coeficiente de Silhouette (0.548) y una prueba ANOVA (p < 0.0001).

## Decisión 3: Pipeline de procesamiento de entrevistas (Whisper + Ollama)

- **Contexto:** Se contaba con 30 audios de entrevistas que debían convertirse en datos estructurados.
- **Decisión:** Transcribir localmente con `faster-whisper` (modelo medium, CPU) y estructurar el texto con un LLM local (Ollama, `qwen2.5:3b`).
- **Razón:** Garantizar la privacidad de los entrevistados y evitar costos de APIs en la nube.
- **Consecuencia:** Se generó un JSON. Sin embargo, debido a que el modelo local aún presentaba pequeños fallos de formato, se decidió hacer una **validación y corrección manual** del JSON final para asegurar la calidad.

## Decisión 4: Priorizar el Canal Informal (Revolico) como fuente primaria

- **Contexto:** Existía la opción de centrarse en las tiendas formales (VEDCA, CIMEX).
- **Decisión:** Se le dio un peso del 80% al análisis de los 1,200 anuncios de Revolico.
- **Razón:** Revolico refleja el mercado real al que accede la mayoría de la población, mientras que el canal formal tiene limitaciones de stock y acceso.
- **Consecuencia:** Se evidenció que el mercado informal maneja sobreprecios y una alta opacidad legal en comparación con el canal formal.

## Decisión 5: Estrategia de recuperación ante el fallo de hardware

- **Contexto:** A mitad del proyecto, la partición raíz de Linux colapsó, dejando inaccesibles los 1,200 JSONs y el código.
- **Decisión:** No reinstalar de inmediato. Primero, usar el Live USB para ejecutar herramientas forenses (`TestDisk`) y rescatar los datos a una partición de Windows.
- **Razón:** Proteger el activo más valioso: los datos extraídos durante semanas.
- **Consecuencia:** Se rescató el 100% de los datos. Se perdió la caché HTML (recuperada luego desde un respaldo) y la base de datos de OpenCode. Sobre esta última se aplicó un proceso de recuperación forense (`.recover` de SQLite + extracción binaria) que permitió rescatar 11 prompts de la fase de scraping; el resto se documentó como pérdida material en `docs/opencode_history.md`. El proyecto se reinstaló sobre una base sólida y segura.

## Decisión 6: Anonimización de las entrevistas (E01–E30)

- **Contexto:** Las 30 entrevistas contenían nombres, municipios y, en algunos casos, lugares de trabajo de los participantes.
- **Decisión:** Asignar un código anónimo a cada entrevista (E01–E30) y eliminar cualquier dato identificable antes de incluirlas en el informe.
- **Razón:** Proteger la identidad de los entrevistados y cumplir con los principios de consentimiento informado que se leyeron al inicio de cada sesión.
- **Consecuencia:** El corpus final conserva la información sustantiva (edad, ocupación, municipio, precios, percepciones) sin exponer a los participantes. Las citas del informe se referencian únicamente con el código.

## Decisión 7: VEDCA como única referencia formal verificable

- **Contexto:** De las 21 entidades autorizadas para comercializar vehículos, solo VEDCA publica precios de vehículos completos en 2026.
- **Decisión:** Utilizar VEDCA como el único punto de comparación formal en el análisis de sobreprecio.
- **Razón:** Las demás entidades no publican catálogos con precios accesibles; usar precios de prensa de 2025 habría introducido ruido temporal en la comparación.
- **Consecuencia:** El sobreprecio del 86% (VEDCA-contra-VEDCA) es el dato más sólido del informe. El resto de las entidades se documentan como opacas en la Sección 3.2 y en el Anexo A, sin comparación cuantitativa.

## Decisión 8: Exclusión de triciclos y vehículos de cuatro ruedas

- **Contexto:** El mercado de vehículos en Cuba incluye también triciclos (eléctricos y de combustión) y vehículos de cuatro ruedas, que aparecían marginalmente en los anuncios de Revolico.
- **Decisión:** Excluirlos del alcance del estudio y limitarlo a motos eléctricas, motos de combustión, bicicletas y patinetes.
- **Razón:** Los triciclos y vehículos de cuatro ruedas tienen lógicas de uso distintas (carga, transporte comercial) y merecen un análisis propio. Incluirlos habría diluido el foco en movilidad personal.
- **Consecuencia:** El corpus final es homogéneo en las cuatro categorías analizadas (300 anuncios por categoría), lo que permite comparaciones directas sin contaminación de segmentos.

## Decisión 9: Filtro de outliers de precio ($100–$5,000)

- **Contexto:** Algunos anuncios de Revolico presentaban precios anómalos: valores simbólicos de 1 USD (usados como placeholder para atraer contactos) y valores extremos de hasta 8,500 USD que no correspondían al segmento analizado.
- **Decisión:** Filtrar los anuncios con precio fuera del rango de $100 a $5,000.
- **Razón:** Los precios de 1 USD no son precios reales de venta (son estrategias de contacto) y los de 8,500 USD corresponden a vehículos de gama alta que no representan el mercado masivo de vehículos ligeros.
- **Consecuencia:** Se descartaron 38 registros por inconsistencias, quedando un universo depurado del cual se extrajo la muestra final de 1,200 anuncios.

## Decisión 10: Uso de plotly para la generación de gráficos

- **Contexto:** Los gráficos del informe podían generarse con matplotlib, seaborn, plotly o herramientas externas como Datawrapper o Flourish.
- **Decisión:** Usar plotly para los gráficos del informe, exportados como HTML interactivo y PNG.
- **Razón:** Plotly genera HTML autocontenido que se integra directamente en el sitio web sin depender de servicios externos, es reproducible desde scripts versionados y permite interactividad (hover, zoom) sin código adicional.
- **Consecuencia:** Todos los gráficos son reproducibles ejecutando `src/analysis/graficos_finales.py`, y el sitio web los incrusta sin iframes de terceros.
