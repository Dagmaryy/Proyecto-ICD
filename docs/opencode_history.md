# Evidencia de Uso de OpenCode

Este documento recopila la evidencia del uso de la herramienta OpenCode (asistente de programación con IA) durante el desarrollo del proyecto ICD.

## 1. Contexto del incidente
Durante el desarrollo del proyecto, un fallo crítico en el disco duro corrompió la base de datos SQLite donde OpenCode almacenaba el historial de las sesiones (archivo `opencode.db`). El mensaje de error original fue: `database disk image is malformed`. Gracias a un rescate forense, se lograron recuperar fragmentos de las sesiones en texto plano, los cuales se adjuntan a continuación.

## 2. Fragmentos recuperados de la sesión original (Rescate Forense)
Los siguientes fragmentos fueron extraídos directamente de los bloques corruptos de la base de datos y demuestran la interacción con el asistente para la ejecución de scripts:

*Nota: Los fragmentos de texto plano de la sesión original se encuentran guardados en la carpeta raíz como evidencia forense.*

## 3. Sesión de Auditoría Técnica (Post-recuperación)
Tras la reinstalación del sistema y la restauración de los datos, OpenCode fue utilizado nuevamente como auditor experto para revisar la coherencia del código y el informe final.

**Prompt enviado a OpenCode:**
> *"Actúa como un auditor experto en Ciencia de Datos... Revisa el código en src/, los datos en data/processed/ y evalúa si el informe final refleja la magnitud del proyecto..."*

**Respuesta resumida de OpenCode:**
> *"He auditado el proyecto. Veredicto: No es un ensayo teórico simple. El informe contiene resultados empíricos reales y las cifras principales coinciden con los datos... Sin embargo, el informe tiene 176 líneas y la metodología técnica ocupa solo las líneas 19-25; el resto es resultados e interpretación. El trabajo real incluye varios scrapers, 3.329 anuncios limpios... y una recuperación tras fallo de disco. Recomiendo añadir la sección de pipeline técnico, mencionar TestDisk y actualizar las referencias."*

## 4. Listado de Scripts Generados y Depurados con OpenCode
La herramienta fue utilizada para generar y corregir la sintaxis de los siguientes scripts del proyecto:
- `src/scrapers/revolico.py` (Lógica base de scraping).
- `src/scripts/enriquecer_masivo.py` (Extracción de marcas y papeles mediante Regex).
- `src/analysis/clustering.py` (Algoritmo K-Means).
- `src/analysis/validar_clustering.py` (Validación con Silhouette y ANOVA).
- `src/analysis/generar_csvs.py` (Generación de datasets para gráficos).

