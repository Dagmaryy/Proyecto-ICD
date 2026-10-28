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

---

## 2026-10-20 (tarde) — Scraper de detalle de bicis (`src/scrapers/bici.py`)

**Qué hice:** Creé `src/scrapers/bici.py`, que reutiliza `revolico.py` **sin modificarlo**, para descargar y procesar los detalles de las bicis de La Habana. Toma los candidatos de `data/processed/final/bicis_final_limpio.json` filtrando `provinceId == "1"` (1908 de 2049), descarga cada detalle con `descargar_detalle(url, "bicis")` (caché en `cache_detalle/bicis/`), clasifica el estado desde `pageProps` y descarta los no válidos con motivo, y procesa los válidos con `procesar_detalles("bicis", ruta_muestra=<tmp>)`. Salidas: `final/bicis_procesados.json` (lista con los campos exactos de `esquema_bici_electrica.json`) y `final/bicis_descartados.json` (aditivo, deduplicado por `id`, con `url_detalle`, `id`, `titulo`, `precio_usd`, `motivo`, `fecha_intento`). Añadí `--dry-run` y `--max N` (máximo de peticiones **nuevas** por ejecución; las cacheadas no cuentan), guardado incremental para reanudar y respeto al límite de 150 peticiones/run y 3 s/60 s. Actualicé `data/processed/README.md` con los dos artefactos nuevos y este journal.

**Evidencia:** `src/scrapers/bici.py`; prueba obligatoria `python -u src/scrapers/bici.py --max 5` (5 descargas OK → 5 válidos; luego con caché y más peticiones: 14 válidos, `completos=1, parciales=13`); `final/bicis_procesados.json` (14 registros, 29 campos = esquema de bici) y `final/bicis_descartados.json` (1: id `57957714`, `borrado`); `python -m pytest tests/ -q` → 4 passed; `verificar_rutas.py` → 27 rutas rotas (mismas que antes, ninguna nueva; revisadas 267).

**Qué aprendí:** (1) El código de error real de un anuncio retirado en Revolico **no es** `cant-see-deleted-ad`: el caso visto fue `unpublished-ad`, y en ese caso `__APOLLO_STATE__` **no trae ningún `AdType`**. Añadí una tupla `ERRORCODES_BORRADO` y, si no hay `AdType`, el detalle se marca `detalle_invalido` (no válido); esto alineó la clasificación con lo que `procesar_detalles` acepta. (2) El descarte por estado se detecta mirando `pageProps.errorCode` y `AdType.status == "EXPIRED"`. (3) El límite `--max` debe comprobarse **solo cuando el detalle no está en caché**, si no, una reejecución se corta sin procesar lo ya cacheado.

**Qué me costó:** Fijar la señal de borrado/expirado sin poder modificarlo en `revolico.py` (tuve que hacerlo en `bici.py` con `_extraer_json_next`) y decidir cómo derivar `id`/`titulo`/`precio_usd` de los descartes que devuelve `procesar_detalles` cuando el anuncio no trae `AdType`.

**Decisiones menores (mi criterio):** filtro `provinceId` tolerante a `1`/`"1"`; `fecha_intento` en ISO 8601 UTC; orden de candidatos el del listado final; `detalle_invalido` solo se añade si ese `id` no se descartó antes por estado; no creé `esquema_moto_combustion.json` (no existe y esta iteración es solo bici); la muestra temporal para `procesar_detalles` va en `/tmp` para no tocar `data/processed/muestras/`.

**Próximo paso:** Lanzar el proceso real hasta 300 válidos (con el límite de 150/run y reanudando), revisar el reparto de `motivo` en los descartes, y decidir si se extiende el mismo patrón a patinetes y motos.

---

## 2026-10-26 — Corrección de la contaminación de motos de combustión

**Qué hice:** Detecté que `motos_combustion_procesadas.json` tenía 379 registros, de los cuales 326 eran eléctricas y solo 53 candidatos. El filtro literal pedido (`tipo_vehiculo == "moto_electrica"` o `cilindrada_cc` nulo) habría dejado **0**, porque los 379 tenían `tipo_vehiculo = "moto_electrica"` y `cilindrada_cc = null`. Filtré por contenido con un clasificador estricto (señales de gasolina/cc/2T/4T frente a voltajes, accesorios, bicimotos, no-venta y anuncios genéricos): de los 53 solo **6** son combustión real. Refactoricé `src/scrapers/moto_combustion.py` para construir los registros contra `docs/schemas/esquema_moto_combustion.json` (30 campos: `cilindrada_cc`, `tipo_motor`, `combustible`, `consumo_l_100km`, `capacidad_tanque_l`, `transmision`, `tipo_arranque`, `anio_fabricacion`, etc.) en vez del esquema eléctrico. Añadí `--limpiar` para reconstruir desde caché, restringí `--reprocesar-cache` a los ids candidatos y evité descargar títulos obvios no-combustión. Procesé los 56 candidatos restantes: 29 peticiones nuevas, 23 detalles válidos, solo 1 aceptado inicialmente (`55010806`, dealer genérico «por encargo», precio 1), que eliminé; **neto 0 nuevos reales**. No toqué los procesados de eléctricas, bicis ni patinetes.

**Evidencia:** `src/scrapers/moto_combustion.py`; `data/processed/final/motos_combustion_procesadas.json` → **6 registros**, claves exactas del esquema de combustión, `tipo_vehiculo = "moto_combustion"`, 0 campos eléctricos; `motos_combustion_descartados.json` → 103 (64 con `detalle: no_es_moto_combustion`); `python -m pytest tests/ -q` → 4 passed; backup del contaminado en `/tmp/motos_combustion_procesadas.contaminado.json`. Los 6: `54458779` (Corcoveo, gasolina), `57134728` y `57134729` (Ava 125 cc, 4T, semiautomática, 2025), `57302018` (Honda CBR 600, 50.000 km, 2013), `57810366` (Suzuki 50 cc, 2T, automática) y `57944124` (150 cc, manual).

**Qué aprendí:** (1) El problema no era el filtro sino la fuente: el scraper usaba `procesar_detalles("motos")`, que aplica el esquema eléctrico, por eso `cilindrada_cc` y `combustible` salían nulos y `tipo_vehiculo` salía `moto_electrica`. (2) Los 53 «reales» eran 39 eléctricas, 8 ambiguas, 4 accesorios, 2 «cambio PC» y solo 6 combustión; el pool de 109 candidatos no contiene 300 motos de combustión. (3) El clasificador por marcas puede dar falsos negativos si la marca es ambigua (`Yamaki`) y el anuncio no trae descripción; los dejé fuera por falta de señal.

**Qué me costó:** Aceptar que la instrucción de «dejar las 53» era incorrecta y que el resultado honesto era 6; reconstruir los registros con el esquema correcto sin perder los 6 válidos; y separar los 23 detalles nuevos (casi todos eléctricos) del único dealer genérico.

**Próximo paso:** Para acercarse a 300 hace falta una fase nueva de búsquedas específicas de combustión («moto gasolina», «125cc», «150cc», «2T», «4T», «combustión», «semiautomática»), descargar candidatos nuevos con el límite de 150/run y repetir sesiones. Pendiente de que Dagmary lo apruebe.

---

## 2026-10-26 (tarde) — Fase de búsquedas específicas de combustión

**Qué hice:** Creé `src/scrapers/refrescar_combustion.py` con 10 términos de búsqueda (`moto gasolina`, `moto 125cc`, `moto 150cc`, `moto 200cc`, `moto 250cc`, `moto 2t`, `moto 4t`, `moto combustion`, `moto semiautomatica`, `moto 110cc`), hasta 9 páginas por término, filtro de La Habana y puntuación por señales de combustión/cc/2T/4T/marcas. Fusioné y deduplicué por `id`: **694 candidatos** (antes 109). Descargué detalles en tandas de 20 hasta agotar el tiempo de la sesión y reprocesé la caché. También corregí un precio: la Katzo Cheetah 200 tenía `precio_usd=200` en el detalle pero «Precio: 2000 USD» en la descripción; ahora se usa el precio del texto solo si es más del doble y está en rango (la Katzo quedó en 2000).

**Evidencia:** `data/processed/final/motos_combustion_procesadas.json` → **124** registros (antes 6), 30 campos exactos, `tipo_vehiculo = "moto_combustion"`, `combustible = "gasolina"`, 100 % La Habana, precios **500–4200 USD**, ids únicos; `motos_combustion_outliers.json` → **1** (Honda CBR 600, `57302018`, 8500 USD); `motos_combustion_descartados.json` → **107** (73 `detalle_invalido` —62 de ellos `no_es_moto_combustion`—, 28 `borrado`, 3 `error_descarga`, 3 `expirado`); `motos_combustion_candidatos_cache.json` → 694; `python -m pytest tests/ -q` → **4 passed**. `data/processed/README.md` actualizado con los artefactos de combustión, patinetes y los recuentos actuales de bicis.

**Qué aprendí:** (1) Las búsquedas específicas sí cambian el pool: 694 candidatos frente a 109, aunque muchos siguen siendo eléctricos o duplicados de dealer. (2) El clasificador refinado (`es_combustion_real`) ya no rechaza por menciones secundarias a accesorios en la descripción; solo rechaza si el título es de accesorio/no-vehículo o si no hay ninguna señal de combustión. (3) Los slugs viejos de Revolico pueden resolver a una moto real con otro título (caso `56843886`, «cafetera» → «Moto de Combustión Hongli 125cc»); no es un falso positivo del dataset. (4) Los anuncios de dealer con varias motos y un solo precio de detalle son válidos, pero inflan duplicados por título (4 títulos repetidos, 8 registros). (5) La red fue inestable: errores SSL, `Connection reset`, DNS y timeouts; los `error_descarga` se reintentan y los detalles ya cacheados se procesan con `--reprocesar-cache`.

**Qué me costó:** Aceptar que 300 no se alcanza en esta sesión: el pool filtrado es 694, pero tras 124 válidos quedan ~501 candidatos sin caché y muchos serán eléctricos, accesorios o anuncios inválidos. También decidir el umbral del precio (solo sustituir si el texto supera el doble del detalle) para no pisar diferencias menores como 1950 vs 2000.

**Pendiente de calidad:** 92 registros sin `marca` (74 %) y 3 sin `cilindrada_cc`; 4 títulos duplicados (8 registros) que son anuncios distintos de dealer. No se deduplicaron porque cada `id_anuncio` es un anuncio real.

**Próximo paso:** Continuar la fase de detalles con los ~501 candidatos sin caché, en tandas de 20 y con `--reprocesar-cache` al final de cada tanda; si se agota el pool, lanzar nuevos términos (`moto 300cc`, `moto enduro`, `moto pistera`, `moto trabajo`, `moto 0km`) o bajar el umbral de puntuación. Objetivo: 300 válidos; si no se llega, informar el progreso y no tocar los datasets de eléctricas, bicis ni patinetes.

---

## 2026-10-26 (tarde) — Normalización de guiones y reproceso de los 4 finales

**Qué hice:** Corregí la normalización que fusionaba rangos numéricos. Añadí `normalizar_guiones()` en `src/scrapers/revolico.py`: convierte todo carácter Unicode de categoría `Pd` (hyphen-minus, non-breaking hyphen, figure dash, en dash, em dash, horizontal bar, etc.) y el signo menos `U+2212` en espacio antes de `NFKD`/ASCII. La usan `_normalizar_titulo()` y `_normalizar()` de `moto_combustion.py`. Añadí un test de regresión con `70–80`, `6–8`, `10‑20`, `4—5` y `−5`. Después reprocesé los 4 JSON existentes desde la caché HTML, sin peticiones nuevas, conservando los mismos ids y el mismo número de registros: eléctricas 326, combustión 124, bicis 414 y patinetes 335. En bicis quité el `kilometraje_km` que añadía el parser actual para no cambiar el conjunto de 29 campos sin consultar.

**Evidencia:** `src/scrapers/revolico.py` (`normalizar_guiones`), `src/scrapers/moto_combustion.py` (`_normalizar`), `tests/test_smoke.py`; `python -m pytest tests/ -q` → **5 passed**. Antes/después: `autonomia_km` con valores fusionados ≥1000 pasó de **29** (1 eléctrica + 16 bicis + 12 patinetes) a **0**; `tiempo_carga_horas` fusionado en bicis pasó de **10** casos (35, 45, 46, 48, 56, 68) a **0**; `velocidad_max_kmh` no tenía fusionados antes ni después. Ejemplos: `57075044` 7080→80, `57954117` 5060→60, `56266612` 68→8, `57345614` 5060→60. Colateral positivo: `57945136` pasó de `kilometraje_km=4045` a `None` (era “40–45 km/h”). Respaldo previo en `/tmp/icd_normalizacion_before/`.

**Qué aprendí:** (1) El orden importa: si se elimina el guion después de `ASCII ignore`, los dígitos ya están pegados; hay que sustituirlo por espacio **antes** de normalizar. (2) El bug afectaba sobre todo a `autonomia_km` y `tiempo_carga_horas`; `velocidad_max_kmh` a menudo se salvaba por accidente porque el regex tomaba los últimos 3 dígitos. (3) Queda un `48` en `tiempo_carga_horas` de `57539366` que no es una fusión: viene de “entrega en menos de 48 horas”. No lo toqué para no ampliar el alcance.

**Qué me costó:** Reprocesar sin inflar los datasets: los `--reprocesar-cache` de bicis/patinetes procesan toda la caché (593/443 HTML), no solo los registros vigentes. Usé una muestra temporal con los `url_anuncio` de los JSON actuales y verifiqué que el conjunto de ids no cambiara antes de escribir.

**Próximo paso:** Decidir si se corrige el falso positivo de tiempo de entrega (`48 horas`) en una tarea aparte; el bug de rangos numéricos queda cerrado.

---

## 2026-10-26 (noche) — Segunda tanda de combustión: 150 peticiones y limpieza de accesorios

**Qué hice:** Continué la recolección de motos de combustión con **150 peticiones nuevas** (60 en una primera ejecución que cortó el timeout de la herramienta y 90 en la segunda; la caché de la primera quedó guardada). Antes de reprocesar detecté que el clasificador dejaba pasar accesorios que mencionan “4T/cc/moto” (filtros, tanques, bombas, cigüeñales, kits, etc.) y anuncios de inmuebles que incluyen una moto. Endurecí `es_combustion_real()` con `_TITULO_PARTE`, `_TITULO_INICIO_PARTE` y `_TITULO_INMUEBLE` en `src/scrapers/moto_combustion.py`, de modo que rechaza piezas y propiedades sin tocar los 124 válidos previos. Después corrí `--reprocesar-cache` y `--limpiar`; eliminé de procesados el velocímetro `56097007` y moví a descartados 15 outliers que eran accesorios o inmuebles. Dejé los outliers reales separados.

**Evidencia:** `data/processed/final/motos_combustion_procesadas.json` → **196** registros (antes 124), 30 campos, 196 ids únicos; `motos_combustion_outliers.json` → **7** motos reales con precio inválido (`57302018` 8500 USD y seis con precio 1 USD); `motos_combustion_descartados.json` → **148**; `motos_combustion_candidatos_cache.json` → 694; caché de detalle de combustión → **732** HTML (582 antes de la tanda). `python -m pytest tests/ -q` → **5 passed**. Respaldos de la tanda en `/tmp/icd_combustion_batch2/`.

**Qué aprendí:** (1) Un filtro que acepta cualquier título con “gasolina/4T/cc” contamina con repuestos y anuncios de combustible suelto; hace falta mirar el inicio del título y términos de pieza/inmueble. (2) El timeout de la herramienta no guarda la lista en memoria de válidos, pero sí la caché HTML: la recuperación correcta es reprocesar caché, no volver a pedir. (3) Los outliers de precio no son basura automáticamente: 7 son motos reales con precio mal extraído; hay que separarlos, no borrarlos.

**Qué me costó:** Distinguir accesorios de motos reales sin rechazar títulos legítimos que mencionan “tanque de 16,5 litros” o “filtro” como equipamiento. La solución fue combinar términos de pieza, patrones de inicio de título y términos de inmueble, y verificar que ninguno de los 124/196 procesados cayera.

**Próximo paso:** Quedan **104** válidos para llegar a 300 en el dataset (196 + 7 outliers = 203 motos reales detectadas). Continuar los ~343 candidatos restantes en tandas de 20–90 con `--reprocesar-cache` al final; revisar a mano los 7 outliers de precio y el `kilometraje_km=240280` de `58026629`.

---

## 2026-10-26 (noche) — Cierre de combustión: 325 válidos y objetivo de 300 superado

**Qué hice:** Continué desde los 196 válidos con **150 peticiones nuevas** en dos tandas de 75. En la primera tanda aparecieron gomas, focos y rentas; en la segunda, aceites, retenes, milleros y otras piezas. Endurecí de nuevo `_TITULO_INICIO_PARTE` en `src/scrapers/moto_combustion.py` con `aceite(s)`, `reten(es)`, `miller(os)`, `chucho`, `correa(s)`, `cable(s)`, `buje(s)`, `conmutador(es)`, `flotante`, `transmision`, `tapa`, `sistema` y `kit`. Limpié los outliers contaminados: 10 en la primera revisión y 3 en la segunda (aceites, retenes y milleros) pasaron a descartados. Los 325 procesados pasan el filtro actual; no se tocaron eléctricas, bicis ni patinetes.

**Evidencia:** `data/processed/final/motos_combustion_procesadas.json` → **325** registros, 30 campos, 325 ids únicos, precios **500–4200 USD**, 0 rechazados por el filtro; `motos_combustion_outliers.json` → **9** motos reales con precio inválido (`57302018` 8500 USD + ocho a 1 USD); `motos_combustion_descartados.json` → **191**; `motos_combustion_candidatos_cache.json` → **694**; caché de detalle → **882** HTML (732 antes de esta continuación). `python -m pytest tests/ -q` → **5 passed**. Respaldos en `/tmp/icd_combustion_batch3/` y `/tmp/icd_combustion_batch4/`. README y handoff actualizados.

**Qué aprendí:** (1) El filtro de piezas necesita ampliarse por familias, no solo por casos vistos: “aceites 2T”, “retenes” y “milleros” entraban como válidos si su precio caía en rango. (2) Los títulos “MOTOR MT 125 CC”, “Motor Jin 150cc” y similares son motos de dealer, no motores sueltos: sus descripciones hablan de garantía, factura y transporte; por eso no se rechazan por empezar con “motor”. (3) Con 325 válidos en rango el objetivo de 300 queda cumplido; no conviene seguir pidiendo solo para engordar el dataset.

**Qué me costó:** Separar piezas de motos reales que comparten palabras (“motor”, “4T”, “cc”) y decidir que los outliers de precio reales se conservan, mientras que los accesorios se mueven a descartados. También verificar que el filtro nuevo no rechazara ninguno de los 325 ya procesados.

**Próximo paso:** Revisar a mano los 9 outliers de precio y el `kilometraje_km=240280` de `58026629`; decidir si se corrigen `modelo` nulo, `plegable` y los demás defectos de parseo antes del informe. No hace falta continuar la recolección.

---

## 2026-10-27 — Extracción técnica por regex y reproceso de eléctricas, bicis y patinetes

**Qué hice:** Reescribí `extraer_campos_tecnicos()` en `src/scrapers/revolico.py` para extraer motor, voltaje, amperaje, tipo de batería, autonomía, velocidad, peso, estado, papeles y plegable. Añadí helpers (`_a_float`, `_numero`, `texto_punt`, `texto_plegable`) y pasé el título a la función. Corregí dos bugs del primer intento: el amperaje decimal se rompía al normalizar (`10.4 Ah` → `4`) y la autonomía confundía rangos de velocidad (`32 km/h`) con autonomía. La autonomía ahora busca números con unidad de distancia y elige el más cercano a la palabra “autonomía”, con prioridad al valor posterior en caso de empate; los rangos toman el máximo. El peso acepta `peso`, `peso máximo`, `carga máxima` y `soporta hasta`, y convierte libras a kg. `plegable` siempre devuelve `True`/`False`. Reprocesé solo los tres JSON eléctricos desde la caché HTML, sin peticiones nuevas, conservando campos, orden, ids y número de registros.

**Evidencia:** `src/scrapers/revolico.py`, `tests/test_smoke.py` (test de regresión de regex); `python -m pytest tests/ -q` → **6 passed**. Estructura verificada: motos 326 registros/30 campos, bicis 414/29, patinetes 335/30; ids únicos y mismo orden. Antes → después (% lleno): motos motor 48.2→76.1, voltaje 50.6→81.9, amperaje 53.1→80.1, batería 39.6→49.7, autonomía 85.0→85.0, peso 0.9→1.2; bicis motor 59.7→64.7, voltaje 60.1→67.4, amperaje 47.1→54.8, batería 34.8→36.2, autonomía 63.0→64.0, peso 0.7→7.5, plegable 0→100; patinetes motor 81.8→86.6, voltaje 63.0→67.8, amperaje 60.0→68.1, batería 33.1→58.8, autonomía 86.3→86.6, peso 0→7.8, plegable 0→100. Respaldo original en `/tmp/icd_regex_before/`. No se tocaron esquemas ni combustión.

**Qué aprendí:** (1) Elegir “el primer número antes/después de la palabra” falla en catálogos multi-modelo y en frases como “Velocidad 25km Autonomía 40km”; hay que comparar distancias y desempatar hacia el número que sigue a la palabra. (2) Para amperajes decimales no sirve el texto normalizado sin puntuación; hay que conservar punto/coma. (3) `plegable` es un campo booleano: llenarlo con `False` es información válida, no un dato ausente.

**Qué me costó:** Separar autonomía de velocidad cuando el anuncio pone ambos números juntos y evitar que un rango de velocidad posterior pisara la autonomía real. También distinguir peso del vehículo de capacidad de carga: el regex actual captura ambos, así que los valores de bicis/patinetes deben interpretarse como peso máximo/carga en muchos casos.

**Próximo paso:** Revisar la semántica de `peso_kg` (peso del vehículo vs. carga máxima) antes de usarlo en el informe; el resto de campos técnicos queda reprocesado y validado.

---

## 2026-10-27 — Limpieza de descartes en eléctricas, bicis y patinetes

**Qué hice:** Creé `data/processed/final/descartes.json` con 15 registros movidos desde los procesados: 13 con motivo `basura` (accesorios, generadores, baterías/cargadores y vehículos de otro tipo) y 2 con motivo `mal_clasificado` (`56513009` y `56915982`). Cada entrada conserva el registro completo, el archivo de origen y el motivo. Eliminé solo esos IDs de los tres JSON; no toqué los 8 dudosos ni los falsos positivos.

**Evidencia:** `motos_electricas_procesadas.json` 326 → **321**, `bicis_procesados.json` 414 → **407**, `patinetes_procesados.json` 335 → **332**. `descartes.json` → **15** registros (13 `basura`, 2 `mal_clasificado`), 15 IDs únicos. Verifiqué que la diferencia de IDs contra el respaldo fuera exactamente el conjunto objetivo y que se conservaran campos, orden y los IDs dudosos/falsos positivos. Respaldo previo en `/tmp/icd_limpieza_before/`. `make test` → **6 passed**.

**Qué aprendí:** Los descartes de accesorios no siempre carecen de palabra de vehículo (“Batería para bicicletas”), así que el criterio útil es que el accesorio sea el objeto principal del título. Los títulos “bici moto” necesitan revisión manual: algunos son bicis, otros motos con título ambiguo.

**Próximo paso:** Revisar uno por uno los dudosos restantes (`56145852`, `57233797`, `57278985`, `57957448`, `57960574`, `57960812`, `57893054`) antes de moverlos o borrarlos.

---

## 2026-10-27 — Cierre de outliers de combustión

**Qué hice:** Moví los 9 registros de `motos_combustion_outliers.json` a `descartes.json`: 4 con motivo `listado_multiple` (`56542487`, `57049769`, `58230707`, `58356620`) y 5 con `sin_precio_real` (`57302018`, `56135611`, `56412008`, `57236865`, `57248589`). Cada entrada conserva el registro completo y el archivo de origen. Dejé `motos_combustion_outliers.json` como `[]`.

**Evidencia:** `descartes.json` → **24** registros, 24 IDs únicos (13 `basura`, 2 `mal_clasificado`, 4 `listado_multiple`, 5 `sin_precio_real`). `motos_combustion_outliers.json` → **`[]`**. `motos_combustion_procesadas.json` quedó **sin cambios, 325 registros**: los 9 IDs de outliers no estaban en procesadas, así que no había nada que restar allí. Respaldo previo en `/tmp/icd_outliers_cierre_before/`. `make test` → **6 passed**.

**Qué aprendí:** El conteo esperado de 316 no se cumple porque presupone que los outliers formaban parte de las 325 procesadas; en realidad son conjuntos disjuntos (325 válidas + 9 outliers). Borrar 9 válidas para forzar 316 habría sido incorrecto.

**Próximo paso:** Confirmar con Dagmary si el conteo final de combustión debe ser 325 válidas (sin tocar procesadas) o si quiere revisar el conjunto de 325 por otro criterio.

---

## 2026-10-27 — Cierre de limpieza y generación de los 4 archivos de 300

**Qué hice:** Moví 14 registros desde los procesados a `descartes.json`: 7 de eléctricas con `precio_placeholder` (`57233797`, `57578875`, `57914342`, `57955401`, `57959675`, `57968734`, `57968735`), 5 de eléctricas con `mal_clasificado` (`56145852`, `57278985`, `57957448`, `57960574`, `57960812`), 1 de bicis con `listado_multiple` (`57642350`) y 1 de patinetes con `precio_placeholder` (`57999470`). Cada descarte conserva el registro completo. Después generé `motos_electricas_300.json`, `motos_combustion_300.json`, `bicis_300.json` y `patinetes_300.json` con `random.Random(42)`, tomando 300 registros por archivo y conservando el orden original de los seleccionados.

**Evidencia:** Procesados: eléctricas **309**, combustión **325**, bicis **406**, patinetes **331**. `descartes.json` → **38** registros, 38 IDs únicos (13 `basura`, 7 `mal_clasificado`, 5 `sin_precio_real`, 5 `listado_multiple`, 8 `precio_placeholder`). Archivos de 300: **300** registros cada uno, **0** IDs duplicados, **0** precios fuera de `[100, 5000]` y **0** precios nulos. Cobertura técnica global: eléctricas **44.6%**, combustión **32.9%**, bicis **43.1%**, patinetes **44.8%**. Verifiqué que cada muestra es subconjunto de su procesado y que no contiene IDs descartados. `make test` → **6 passed**. Respaldo previo en `/tmp/icd_cierre_final_before/`.

**Qué aprendí:** Los precios `1 USD` sin precio alternativo en la descripción son placeholders y deben salir del análisis, no repararse inventando un valor. Los “bicimoto” son un caso híbrido: el esquema los ubica en bicis, pero como el objetivo aquí es motos y Dagmary pidió descartarlos, quedaron en `mal_clasificado` en vez de moverlos entre datasets.

**Qué me costó:** Decidir un único motivo para `57233797`, que era a la vez precio placeholder y “bici moto”; se priorizó `precio_placeholder` porque el precio inválido es el defecto que impide usarlo. También cuidar que los 300 no arrastraran ningún ID recién descartado.

**Próximo paso:** Revisar la semántica de `peso_kg` (peso del vehículo vs. carga máxima) antes de usarlo en el informe y decidir si los 300 son la base definitiva del análisis o solo una muestra de trabajo.
