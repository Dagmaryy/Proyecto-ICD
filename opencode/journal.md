# Journal — Mercado de motos eléctricas en La Habana

Registro cronológico del desarrollo del proyecto (análisis del mercado de vehículos eléctricos en La Habana). Reconstruido a partir del historial de git (`git log`), del sistema de archivos (mtime de los datos y la caché) y de los logs de scraping. Período cubierto: 17 de septiembre – 10 de octubre de 2026.

> Convención de cada entrada: **Qué hice · Evidencia · Qué aprendí · Qué me costó · Próximo paso**. Al terminar cada jornada de trabajo se añade una entrada nueva al final (ver AGENTS.md, sección «Flujo con OpenCode»).

---

## 2026-09-17 — Notas iniciales de fuentes

**Qué hice:** Creé los archivos semilla del proyecto: notas de fuentes documentales, presencia en redes y plantilla de entrevistas, además del archivo de reporte final. Todo quedó como marcador vacío, a la espera de contenido.

**Evidencia:** `data/raw/stakeholders/institucionales/ONCUBA.md`, `Postdata.club.md`, `data/raw/web/Telegram.md`, `Facebook.md`, `data/raw/interviews/transcripciones.md` (apunta a Otter.ai) y `storytelling/reports/final_report.md` (hoy vacío). Timestamps 17-sep 10:16–10:25.

**Qué aprendí:** Conviene separar desde el inicio fuentes documentales, redes, entrevistas y stakeholders en carpetas distintas para no mezclar tipos de evidencia.

**Qué me costó:** Fijar la estructura de carpetas antes de tener claro qué datos iba a recoger realmente.

**Próximo paso:** Armar el repositorio de git con esa estructura ya ordenada.

---

## 2026-09-21 — Arranque del repositorio

**Qué hice:** Inicialicé git y creé el primer commit con la estructura del proyecto: `.gitignore`, `AGENTS.md`, `README.md`, `elements/Elementos.md`, `prompts/sessions.md` y los placeholders de `data/raw/` y `data/processed/`.

**Evidencia:** commit `e6dbfb6` «Estructura inicial del proyecto ICD» (17 archivos, +69 líneas).

**Qué aprendí:** Que el `.gitignore` inicial quedó vacío y tuve que ampliarlo después; mejor definirlo con la lista de exclusiones (caché, audios) desde el principio.

**Qué me costó:** Decidir qué dejar fuera del control de versiones cuando aún no había datos pesados.

**Próximo paso:** Bajar HTML real de Revolico y probar un parser.

---

## 2026-10-03 — Parser de prueba sobre HTML real

**Qué hice:** Guardé una página real de listado de Revolico y escribí un parser de prueba (96 líneas) para ensayar la extracción de campos del listado. En ningún momento inventé selectores: los fijé contra el HTML guardado.

**Evidencia:** `data/raw/web/revolico/pruebas/motoprueba.html` (186 líneas, luego movido) y `src/scrapers/parser_prueba.py`. Commit `015d89b`.

**Qué aprendí:** Que sin un fragmento HTML real no se puede escribir un selector fiable. De ahí en adelante pedí siempre el HTML antes de tocar el parser.

**Qué me costó:** Elegir qué campos del listado valían la pena extraer en esta etapa y cuáles dejaba para el detalle.

**Próximo paso:** Formalizar la configuración del scraper (User-Agent, delays, límites).

---

## 2026-10-06 — Configuración y estructura formal

**Qué hice:** Añadí `config.yaml` con los parámetros de scraping ético (User-Agent honesto con contacto, delay 3 s, espera 60 s ante 429, máximo 150 peticiones), amplié el `.gitignore` a ~40 líneas, fijé `requirements.txt`, reorganicé `data/raw/institutional/` → `stakeholders/` y amplié README y AGENTS.md.

**Evidencia:** `config.yaml`, `.gitignore`, `requirements.txt`; commit `10a12ba`.

**Qué aprendí:** Que los límites éticos (delay, tope de peticiones) deben vivir en config, no incrustados en el código, para poder auditarlos.

**Qué me costó:** Reconciliar los nombres de carpetas que ya tenía con los que documentaba AGENTS.md.

**Próximo paso:** Ejecutar el scraping completo de listados en las tres categorías.

---

## 2026-10-07 — Primer scraping completo de listados

**Qué hice:** Ajusté el parser (20:55) y lancé el scraper de listados sobre las tres categorías. Descargué 90 páginas de listado: 30 de motos (22:44–23:31), 30 de bicis (23:31–23:39) y 30 de patinetes (23:39–23:48). Cada HTML quedó cacheado con nombre hash. A las 23:58 generé los tres listados crudos.

**Evidencia:** `data/raw/web/revolico/cache_html/{motos,bicis,patinetes}/listado_*.html` (30 + 30 + 30) y `data/processed/listados_crudos/{motos,bicis,patinetes}_listado.json`.

**Qué aprendí:** Que Revolico devuelve muchos duplicados entre búsquedas y hay que deduplicar por ID de anuncio.

**Qué me costó:** El delay de 3 s entre peticiones hace lento cada barrido; con 90 páginas el proceso se llevó cerca de una hora.

**Próximo paso:** Clasificar los listados, sacar muestras y descargar los detalles de las motos.

---

## 2026-10-08 (madrugada y mañana) — Clasificación, muestreo y descarga de detalles

**Qué hice:** Generé los clasificados de las tres categorías a las 00:04 y, entre 00:09 y 00:41, los ficheros `final` preliminares y las muestras (300 de bicis y patinetes, 300 y luego 350 de motos). Completé búsquedas de patinetes. Después descargué los **detalles de 350 motos** en dos tandas (00:46–01:37 y 09:32–10:30). Bicis y patinetes se quedaron sin detalle.

**Evidencia:** `data/processed/clasificados/*.json`, `data/processed/muestras/*_300.json` y `motos_muestra_350.json`, `data/raw/web/revolico/cache_detalle/motos/detalle_*.html` (350 archivos).

**Qué aprendí:** Que motor, voltaje, autonomía y batería solo están en la página de detalle; por eso solo las motos tienen datos técnicos. Esto condicionó el alcance del análisis técnico.

**Qué me costó:** 350 detalles con delay de 3 s ≈ dos tandas de casi una hora cada una.

**Próximo paso:** Consolidar los procesados de motos y rehacer el README.

---

## 2026-10-08 (tarde) — Consolidación, esquemas v2 y EDA

**Qué hice:** Consolidé `motos_procesados` (300 + 26 extra + 24 descartados), publiqué los clasificados (537 motos, 612 bicis, 366 patinetes candidatos), reescribí el README y arranqué el EDA. Creé los notebooks de análisis (listado, precios, finales) y generé 12 gráficos preliminares. Por la tarde revisé los esquemas a **v2**: moto con 27 campos y bici/patinete con 29, añadiendo `vendedor_id` y `garantia_dias`, y reprocesé los 326 válidos.

**Evidencia:** commits `88fa93d`, `6a55f68`, `76ce671`, `8332986`, `2ae65fc`, `5a8da51`, `4750b65`, `0a6f992`; `notebooks/02–04`; `storytelling/graphs/preliminar/*.png` (12); `data/processed/final/motos_{procesados,completos,parciales,descartados}.json`.

**Qué aprendí:** Que conviene subir la versión del esquema antes de reprocesar; reprocesar 326 válidos cambió la forma de todos los `final`.

**Qué me costó:** Mantener la coherencia entre el esquema, el scraper y los datos ya procesados cuando cambié campos a mitad de camino.

**Próximo paso:** Reorganizar carpetas y ampliar las búsquedas para no depender de las categorías oficiales de Revolico.

---

## 2026-10-08 (noche) — Reorganización, búsquedas ampliadas y limpieza

**Qué hice:** Pasé las carpetas `Revolico/STT` a minúsculas y moví los esquemas a `docs/schemas/`. Añadí el parámetro `etiqueta` a `descargar_listado` y lancé **42 páginas de búsquedas ampliadas** (archivos `busqueda_*.html`). Cerré el día con una limpieza conservadora: reclasificación v2, deduplicación v3 y los ficheros limpios por categoría.

**Evidencia:** commits `fdadf3d`, `1b37e11`, `2aafc02`; `data/raw/web/revolico/cache_html/*/busqueda_*.html` (13 motos + 34 bicis + 11 patinetes); `data/processed/versiones/*_final_v2.json`, `*_final_v3.json`.

**Qué aprendí (hallazgo metodológico):** que las categorías oficiales de Revolico **infravaloraban la oferta**: la subcategoría oficial de bicis tenía ~151 anuncios frente a 2.050 encontrados por búsqueda de texto; el mismo patrón apareció en motos y patinetes. Buscar por texto, no por categoría, fue decisivo.

**Qué me costó:** Diseñar los criterios de deduplicación sin borrar trazas: tuve que conservar las versiones agresivas como evidencia en `versiones/`.

**Próximo paso:** Fijar el alcance (La Habana), documentar decisiones y dejar los limpios definitivos.

---

## 2026-10-09 (madrugada) — Alcance La Habana y documentación de entrevistas

**Qué hice:** Dejé escrito el alcance (solo La Habana), preparé la guía y el registro de las 30 entrevistas a usuarios, y publiqué los esquemas v2 y el embudo de datos. Ajusté los `final_limpio` de las tres categorías.

**Evidencia:** commit `2bbd84c`; `data/raw/interviews/preguntas.md`, `registro.md`; `docs/schemas/esquema_entrevista.json`; `data/processed/final/*_final_limpio.json`.

**Qué aprendí:** Que anonimizar en origen (solo códigos `user_XXX`, sin nombres) simplifica todo el tratamiento posterior.

**Qué me costó:** Definir el embudo de datos de forma que cualquiera pudiera seguirlo del scraping al dataset final.

**Próximo paso:** Regenerar los limpios, revisar rutas rotas y dibujar los gráficos finales.

---

## 2026-10-09 (día) — Rutas, gráficos y outline de la historia

**Qué hice:** Regeneré los limpios definitivos (motos 966, bicis 2050, patinetes 314). Escribí `src/scripts/verificar_rutas.py` para cazar referencias rotas, actualicé `config.yaml`, añadí el notebook `05_graficos_motos`, documenté la carpeta de gráficos, corregí un fallo del glob de muestras en `revolico.py` y redacté el outline inicial de la historia.

**Evidencia:** commit `529c3ae`; `data/processed/final/{motos,bicis,patinetes}_final_limpio.json` (966 / 2050 / 314); `src/scripts/verificar_rutas.py`; `notebooks/05_graficos_motos.ipynb`; `storytelling/outline.md`; `opencode/handoff.md`.

**Qué aprendí:** Que las referencias a las rutas de scripts y gráficos seguían rotas tras la reorganización (hoy son `src/` y `storytelling/graphs`); un verificador de rutas ahorra tiempo.

**Qué me costó:** Cuadrar los conteos de cada etapa del embudo con los limpios finales.

**Próximo paso:** Reorganización final de carpetas, tests de humo y bitácora.

---

## 2026-10-09 (noche) — Reorganización final, tests y journal

**Qué hice:** Cerré la reorganización (`src/` → `src/`, `reports/` → `storytelling/`, esquemas a `docs/schemas/`, previos aparte) y escribí 4 tests de humo: procesar detalles de motos, existencia de los limpios, campos/esquema de los limpios y carga de los esquemas. Todos pasan en menos de 0,1 s.

**Evidencia:** commit `529c3ae`; `tests/test_smoke.py`; `python -m pytest tests/ -v` → 4 passed; `opencode/journal.md`.

**Qué aprendí:** Que unos tests sin fixtures, que solo verifican existencia, forma y carga, ya protegen el pipeline contra movimientos de archivos.

**Qué me costó:** Decidir qué testear en un proyecto académico sin sobrecargarlo de infraestructura.

**Próximo paso:** Fijar `pytest` en `requirements.txt` y preparar el entorno de secretos.

---

## 2026-10-10 — Contabilidad del entorno y reconstrucción de la bitácora

**Qué hice:** Añadí `pytest` a `requirements.txt` y lo instalé en `venv/` (verificado: `python -m pytest tests/ -v` → 4 passed). Dejé `/.env` y `.env.example` para sacar secretos del código. Reconstruí este journal completo a partir del historial de git y del sistema de archivos, y lo dejé con la convención de entradas que se amplía al final de cada jornada.

**Evidencia:** `requirements.txt`, `.env`, `.env.example`, `opencode/journal.md`.

**Qué aprendí:** Que reconstruir la cronología desde git + mtime de datos da una trazabilidad bastante fiel, incluso del trabajo hecho antes de versionar.

**Qué me costó:** Distinguir qué era trabajo real de cada día y qué era solo movimiento de archivos en el checkout.

**Próximo paso:** Abordar los pendientes del `handoff.md`: reconciliar nombres `historia/`↔`storytelling/` y `datos/`↔`data/`, ampliar `_MARCAS`/`_MODELOS` de bicis y patinetes, y decidir la promoción de los limpios. Diseñar las entrevistas para la semana del 12 de octubre.

---

## 2026-10-10 (tarde) — Handoff reescrito en formato extendido

**Qué hice:** Reescribí `opencode/handoff.md` con una estructura de 10 secciones (qué es el proyecto, estado actual, estructura, datos clave, preguntas del estudio, decisiones metodológicas, cómo continuar, gotchas, próximos pasos, fuentes), inspirada en un modelo de handoff más detallado, pero con los datos reales de nuestro repo. Actualicé la ruta raíz (era `/home/dagmary/Escritorio/ICD Project`, correcta `/home/dagmary/Escritorio/Proyecto ICD`), el remoto y el estado de commit real.

**Evidencia:** `opencode/handoff.md`; datos verificados con `git log/status`, `config.yaml`, `docs/schemas/`, y conteos de `data/processed/` (limpios 966/2050/314; procesados 326 = 83+243; 350 detalles).

**Qué aprendí:** Que AGENTS.md referencia dos esquemas inexistentes (`esquema_talleres.json`, `esquema_importadoras.json`) y que `requirements.txt` tenía `pytest` duplicado; ambos quedaron anotados como gotchas/pendientes.

**Qué me costó:** Casar los conteos de cada etapa del embudo (listados → clasificados → muestras → detalle → limpios) sin inventar cifras donde no hay artefacto verificable.

**Próximo paso:** Reconocer lo pendiente en git (`tests/`, `opencode/journal.md`, `requirements.txt`, `.env.example`) y proponer su commit; después, aprobar el outline de la historia.

---

## 2026-10-10 (noche) — Limpieza de anomalías y pipeline reproducible (tareas 2 y 3)

**Qué hice:** Eliminé de `bicis_final_limpio.json` la única anomalía real de los tres finales: la bici «🚲 Bicicleta Eléctrica de Alta Gama‼️‼️9» con `precio_usd 650000` (un CUP colado como USD), pasando de 2050 a **2049** registros (motos 966 y patinetes 314 intactos). Luego escribí `src/scripts/limpiar_finales.py`, el limpiador reproducible: reproduce el **v2 exacto** desde el caché (1198 / 2861 / 373, aborta en `exit 2` si difiere), aplica reglas deterministas documentadas (moneda USD, rango de precio 100–5000, dedup por título emoji-limpio + precio + municipio, dedup por tokens + bucket de $50 + municipio, ruido por palabras) y calibra con una **tabla de excepciones** (`versiones/limpio_excepciones.json`) que preserva las decisiones manuales de la limpieza histórica. Tiene `--verificar` (compara y deja `data/processed/verificacion_limpio.json`; `exit 1` si difiere) y `--aplicar` (escribe finales + excepciones).

**Evidencia:** borrado del outlier (tarjeta `56237039`); `src/scripts/limpiar_finales.py`; `data/processed/versiones/limpio_excepciones.json`; `data/processed/verificacion_limpio.json`; `--aplicar` → reglas 921/2058/316 y aplicado + excepciones = objetivo 966/2049/314 con **0 faltan / 0 sobran / 0 campos diferentes**; `python -m pytest tests/ -v` → 4 passed.

**Qué aprendí:** (1) La limpieza histórica v3→limpio no era reproducible por reglas puras: hizo falta una tabla de excepciones con 328 entradas (127 motos: 86 keep + 41 drop; 185 bicis: 88 + 97; 16 patinetes: 7 + 9), sobre todo por duplicados por tokens/bucket (250) y ruido (56), más 10 ajustes manuales. (2) Hay **3 registros de motos** cuyo `precio_usd` histórico difiere del caché (750→650, 2900→290, 1590→1620); los preservo como «precio_historico» en la tabla en vez de introducir cambios silenciosos; el 290 parece errata a revisar. (3) El primer `--aplicar` escribió registros de 7 campos (olvidé convertir con `a_final`); el reporte no lo detectó porque solo comparaba URLs. Añadí paridad **a nivel de registro** y ahora el reporte lista campos diferentes. (4) El contenido regenerado era idéntico pero el **orden** de registros no; resturé motos/patinetes a HEAD (contenido ya verificado idéntico) y dejé bicis = HEAD menos el outlier, para un diff limpio de solo 10 líneas.

**Qué me costó:** Conseguir reproducibilidad exacta (v2 desde caché) y decidir que el orden de los registros no es parte del contrato: lo que garantiza el script es igualdad de URLs y de campos por registro.

**Próximo paso:** Acordar el commit de lo pendiente (`opencode/`, `tests/`, `requirements.txt` con `pytest` duplicado, `src/scripts/limpiar_finales.py`, `data/processed/versiones/limpio_excepciones.json`, `data/processed/final/bicis_final_limpio.json`) con mensaje que lo describa; revisar a mano los 3 precios de motos marcados como `precio_historico`; decidir si `verificacion_limpio.json` se versiona o queda como reporte.

---

## 2026-10-20 — Reestructuración por partes, fuentes oficiales, READMEs y Makefile

**Qué hice:** Reestructuré el proyecto en cinco partes controladas. (1) Renombré `previos/` → `versiones/` en `data/processed/` con `git mv` (18 archivos) y actualicé sus referencias. (2) Corregí rutas: los notebooks 02, 04 y 05 pasan de `motos_final.json` a `motos_final_limpio.json`, y el 05 usa `storytelling/graphs`; limpié `AGENTS.md` (quité los dos esquemas de talleres/importadoras inexistentes, normalicé las rutas a `data/raw` y `storytelling/historia.md`, y corregí el typo «4. 4.»). (3) Escribí `data/README.md` (mapa y embudo), `data/processed/README.md` (vigentes + flujo) y `data/processed/versiones/README.md` (histórico). (4) Creé `Makefile` (`test`/`rutas`/`limpiar`) y `.githooks/{commit-msg,pre-commit}` ejecutables, sin activar `core.hooksPath`; añadí la sección «Comandos» a `AGENTS.md`. (5) Actualicé este journal y `opencode/handoff.md`. Aparte, descargué 6 fuentes oficiales a `data/raw/stakeholders/institucionales/` (5 OK; MITRANS falló por SSL y no reintenté, según la regla) y creé `_fuentes.md`.

**Evidencia:** `git mv` de 18 archivos (`previos/`→`versiones/`); notebooks 02/04/05 con `motos_final_limpio.json`; `data/README.md`, `data/processed/README.md`, `data/processed/versiones/README.md`; `Makefile`; `.githooks/commit-msg` y `.githooks/pre-commit` (chmod +x, `core.hooksPath` sin configurar; probados: asunto inválido→1, válido→0, `Merge`→0; pre-commit en repo temporal: caché→1, normal→0, `.env`→1); `make test` → 4 passed; `verificar_rutas.py` → de 17 a **6** rutas rotas (ninguna nueva); fuentes `decreto_163_2026.html`, `resolucion_175_2026.html`, `aduana_portada.html`, `mindus_marco.html`, `mfp_portada.html` + `_fuentes.md`.

**Qué aprendí:** (1) `verificar_rutas.py` devuelve `exit 1`, así que `make rutas` «falla» mientras existan rutas rotas; es comportamiento correcto, no un error del Makefile. (2) El embudo no es una cadena anidada: los elegibles v2 (4.432) superan los crudos únicos (3.265) porque cada tipo se filtra por separado y un anuncio puede contar en varios; lo documenté con `[pendiente]` en vez de forzar cifras. (3) La skill `journal-del-dia` dice insertar arriba, pero el propio journal (línea 5) y `AGENTS.md` dicen «al final»; mantuve el orden cronológico.

**Qué me costó:** Cuadrar las cifras del embudo sin que aniden y clasificar las rutas rotas restantes entre reales (config), futuras (entrevistas) e históricas/notación (journal). También el fallo SSL de MITRANS, que no reintenté por la regla.

**Próximo paso:** Decidir si se limpian las 6 rutas restantes o se dejan como traza; revisar los 3 `precio_historico`; aprobar el outline; y acordar el commit de todo lo pendiente cuando Dagmary lo pida.
