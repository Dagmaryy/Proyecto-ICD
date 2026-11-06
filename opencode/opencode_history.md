# Uso de OpenCode en el proyecto ICD

## 1. Propósito del documento

Este documento registra el uso de la herramienta OpenCode (agente de IA para desarrollo asistido) durante el desarrollo del proyecto ICD: análisis de mercado de vehículos ligeros en La Habana. Se documentan las fases en las que se utilizó, la evidencia recuperable de cada fase, y el incidente de corrupción de la base de datos que afectó parte del registro histórico.

## 2. Fases de uso

OpenCode se utilizó en tres fases del proyecto:

| Fase | Período | Tareas principales | Evidencia |
|---|---|---|---|
| Fase 1: Scraping y limpieza | sept-oct 2026 | Extracción de anuncios de Revolico, corrección de bugs (normalización de títulos, regex de campos técnicos), clasificación y limpieza de datos, manejo de outliers | 11 prompts recuperados (ver Sección 3) |
| Fase 2: Recuperación post-colapso | 3-nov 2026 | Recuperación forense del proyecto tras el fallo del disco, restauración de la caché HTML, verificación de datos | 7 sesiones, 262 mensajes (ver Sección 4) |
| Fase 3: Análisis final y cierre | 3-6 nov 2026 | Tabulación de entrevistas, generación de gráficos, auditoría de consistencia del informe, documentación | Incluida en Sección 4 |

## 3. Evidencia de la fase 1 (recuperada del disco corrupto)

El 3 de noviembre de 2026, el disco principal colapsó y corrompió la base de datos de OpenCode (581 MB). Se aplicó un proceso de recuperación forense (ver Sección 5) que permitió rescatar **11 prompts** del usuario correspondientes a la fase de scraping y limpieza.

Los prompts recuperados documentan las siguientes tareas:

1. Corrección de bug de normalización de guiones (que fusionaba rangos numéricos)
2. Recolección de motos de combustión (primera tanda de 150 peticiones)
3. Recolección de motos de combustión (segunda tanda de 150 peticiones)
4. Corrección de regex de extracción técnica (motor, voltaje, autonomía)
5. Identificación de registros basura antes de eliminarlos
6. Limpieza segura de datos con creación de archivo de descartes
7. Verificación de outliers de combustión (9 registros)
8. Cierre de outliers y movimiento a descartes
9. Auditoría final de los 4 archivos procesados
10. Cierre de limpieza final y generación de los 4 archivos de 300 registros
11. Limpieza de la raíz del proyecto

El detalle completo de cada prompt está en `docs/opencode_prompts_recuperados.md`.

## 4. Evidencia de las fases 2 y 3 (sesión actual)

La base de datos actual de OpenCode (`~/.local/share/opencode/opencode.db`) contiene:

- **7 sesiones** registradas entre el 3 y el 6 de noviembre de 2026
- **262 mensajes** totales (prompts del usuario + respuestas del agente)

Sesiones registradas:

| Título | Fecha | Propósito |
|---|---|---|
| New session | 2026-11-03 23:14 | Primera sesión post-recuperación |
| Proyecto ICD pt3 | 2026-11-03 23:16 | Continuación del proyecto |
| Web scraping vehicle importation | 2026-11-03 23:21 | Extracción de fuentes normativas oficiales |
| enriquecer.py logic fix required | 2026-11-03 02:36 | Corrección del script de enriquecimiento |
| Hola conversation plan | 2026-11-04 23:10 | Planificación |
| Verificar columnas de datasets | 2026-11-05 23:05 | Validación de datos procesados |
| Proyecto ICD | 2026-11-05 23:06 | Sesión de cierre |

Los 7 títulos y los 262 mensajes están exportados en `docs/opencode_prompts.md`.

## 5. Incidente forense: corrupción y recuperación

### El incidente

El 3 de noviembre de 2026, un fallo crítico en la partición del sistema operativo (Linux) provocó la corrupción de la base de datos de OpenCode. El archivo afectado (`opencode_vieja_corrupta.db`, 581 MB) quedó inaccesible para SQLite estándar.

### Proceso de recuperación

Se aplicaron tres técnicas forenses en orden:

1. **`PRAGMA integrity_check`**: confirmó que la base de datos estaba corrupta.
2. **`sqlite3 .recover`**: recuperó 20,152 líneas de SQL, pero solo la tabla `lost_and_found` con fragmentos de IDs de sesión. Las tablas `session`, `message` y `part` no se pudieron reconstruir.
3. **Extracción binaria con `strings` + parseo JSON manual**: identificó 275 ocurrencias de `"role":"user"` en el binario, de las cuales se pudieron parsear 32 bloques `type:text` completos. De estos, 11 corresponden a prompts reales del usuario (los que empiezan con `Build:` o `Plan:`).

### Resultado

- **11 prompts recuperados** de la fase de scraping y limpieza.
- **262 mensajes preservados** de la fase post-colapso (base de datos actual intacta).
- **La copia de la base de datos corrupta** se conserva como evidencia forense.

### Lo que se perdió

Los prompts de las sesiones de entrevistas, análisis de clustering, gráficos y redacción del informe **no se pudieron recuperar** de la base de datos corrupta. Sin embargo, el trabajo realizado en esas fases quedó documentado en:

- Los commits de Git del repositorio
- Los archivos de salida en `data/processed/` y `reports/plots/`
- Los scripts versionados en `src/`
- El informe final en `docs/final_report.md`

## 6. Contribución de OpenCode al proyecto

OpenCode se utilizó como agente de desarrollo asistido en tareas de:

- **Scraping**: generación y corrección iterativa de scripts de extracción con manejo de caché, reintentos y límites éticos.
- **Limpieza de datos**: normalización de títulos, extracción de campos técnicos por regex, identificación y manejo de outliers.
- **Recuperación forense**: asistencia en la restauración de la caché HTML tras el colapso del disco.
- **Análisis**: tabulación de entrevistas, generación de gráficos, auditoría de consistencia del informe.
- **Documentación**: redacción de scripts de trazabilidad, verificación de coherencia entre archivos.

Toda la evidencia está versionada en el repositorio y disponible para auditoría.
