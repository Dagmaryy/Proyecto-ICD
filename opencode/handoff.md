# Handoff — memoria de trabajo (para mí, OpenCode)

> Notas para retomar sin releer nada. Al empezar: leer ESTO + la última entrada de `journal.md`.
> Actualizar cuando el contexto pase del ~80% o cuando releyendo archivos ya no recuerde su contenido.

**Escrito/actualizado:** 2026-10-26 · **Rama:** `main` · **Último commit:** `2ca457b` (opencode: corrige el título del journal)
**Repo:** https://github.com/Dagmaryy/Proyecto-ICD.git · **Raíz:** `/home/dagmary/Escritorio/Proyecto ICD`

---

## Contexto de un vistazo

Trabajo académico de ICD (Introducción a la Ciencia de Datos, prof. Yudivian Almeida). Analizo el **mercado de vehículos eléctricos de dos ruedas en La Habana** (motos sobre todo; bicis/bicimotos y patinetes como categorías complementarias). Junto **scraping de Revolico + 30 entrevistas a usuarios + stakeholders** (tiendas, importadoras, talleres, instituciones). Entrego un **informe**, no software. La interpretación la escribe Dagmary; yo preparo datos, tablas, gráficos y outlines.


## Cómo me muevo por el repo (no olvidar)

- Activar `source venv/bin/activate`; correr siempre desde la raíz con `python -u`.
- El código es **namespace package** (sin `__init__.py`): `from src.scrapers.revolico import procesar_detalles`.
- `revolico.py` define raíz con `BASE_DIR = Path(__file__).resolve().parents[2]`.
- **httpx, nunca requests.** **Nunca tocar `data/raw/`** (excepción: añadir fuentes nuevas pedidas explícitamente, p. ej. `data/raw/stakeholders/institucionales/`). Nunca versionar caché HTML ni audios.
- Tests: `python -m pytest tests/ -v` → 5 passed (o `make test`).
- Diagnóstico de rutas: `python3 src/scripts/verificar_rutas.py` (o `make rutas`; devuelve `exit 1` si hay rutas rotas).
- Limpiador: `python src/scripts/limpiar_finales.py --verificar` / `--aplicar` (o `make limpiar`).

## Quién es quién de archivos

- `src/scrapers/revolico.py` (~1201 líneas) → todo el scraping + limpieza base. Funciones que importan: `descargar_listado(url, categoria, usar_cache, etiqueta)`, `descargar_detalle`, `descargar_lote`, `contar_paginas`, `extraer_anuncios_listado`, `es_moto_electrica`/`es_bici_electrica`/`es_patinete_electrico`, `clasificar_listado`, `consolidar_clasificados`, `seleccionar_muestra(n, seed=42)`, `extraer_detalle`, `extraer_campos_tecnicos`, `construir_anuncio_segun_esquema`, `_MARCAS`/`_MODELOS`, `_extraer_marca_modelo`, `procesar_detalles(categoria, max_anuncios, ruta_muestra)`.
- `src/scrapers/parser_prueba.py` → parser de pruebas (histórico).
- `src/scripts/verificar_rutas.py` → busca referencias de rutas rotas.
- `src/scripts/limpiar_finales.py` → **limpiador reproducible** de los finales (ver abajo).
- `config.yaml` → parámetros (ver abajo).
- `elements/Elementos.md` → **las 30 preguntas del estudio** (fuentes A/E/S/D).
- `Makefile` → `make test`, `make rutas`, `make limpiar`.
- `.githooks/commit-msg` y `.githooks/pre-commit` → validan el asunto y bloquean caché/audios/secretos. No están activos (falta `git config core.hooksPath .githooks`).
- `data/README.md` → mapa y embudo; `data/processed/README.md` → vigentes + flujo; `data/processed/versiones/README.md` → histórico de versiones.
- `storytelling/outline.md` → outline propuesto de la historia (**sin aprobar**).
- `notebooks/` (01–05) → EDA y gráficos (01_eda_motos, 02_eda_listado_motos, 03_analisis_precios_motos, 04_eda_motos_final, 05_graficos_motos).

## Config que rige (config.yaml)

- Scraping: UA honesto «Proyecto-ICD (Dagmary)», `delay_segundos: 3`, `delay_429_segundos: 60`, `max_peticiones: 150`, `max_paginas_por_url: 10`.
- Economía: `tasa_cup_por_usd: 350` (fecha 2026-10-05).
- Análisis: `max_anuncios_por_tipo: 30`, clustering `n_clusters: 6`, `random_state: 42`.
- Rutas: `raw: data/raw`, `processed: data/processed`, `graphs: storytelling/graphs`, `cache_listado/detalle` bajo `data/raw/web/revolico/`.

## Datos: qué hay y cuánto (verificado 2026-10-10)

### Actualización 2026-10-26 (combustión, bicis y patinetes)

- **Motos de combustión (La Habana):** `final/motos_combustion_procesadas.json` → **325** válidos, 30 campos del esquema de combustión, `tipo_vehiculo = "moto_combustion"`, `combustible = "gasolina"`, precios **500–4200 USD**. `motos_combustion_outliers.json` → **9** motos reales con precio inválido (`57302018` a 8500 USD y ocho a 1 USD). `motos_combustion_descartados.json` → **191**. Candidatos: **694**; caché de detalle: **882** HTML. Objetivo de **300 superado**; no hacen falta más peticiones.
- **Fase de combustión:** `src/scrapers/moto_combustion.py` (detalle, `--max N`, `--reprocesar-cache`, `--limpiar`) + `src/scrapers/refrescar_combustion.py` (búsquedas por término, 694 candidatos). En la última continuación se hicieron **150 peticiones nuevas** (75 + 75), además de las 150 anteriores; la caché quedó en 882 HTML. El filtro rechaza piezas (`_TITULO_PARTE`, `_TITULO_INICIO_PARTE`) e inmuebles (`_TITULO_INMUEBLE`), y ahora también aceites, retenes, milleros, cables, correas, bujes, tapas y kits. Los 325 procesados pasan el filtro; los 3 outliers de piezas se movieron a descartados.
- **Bicis:** `final/bicis_procesados.json` → **414**; `final/bicis_descartados.json` → **184**. **Patinetes:** `final/patinetes_procesados.json` → **335**; `final/patinetes_descartados.json` → **110**; `final/patinetes_candidatos.json` → **482**.
- **Ojo:** los apartados antiguos de «Detalles descargados» y «Procesados de motos» (350/326) se refieren a **motos eléctricas**; no mezclar con combustión. El archivo eléctrico vigente es `final/motos_electricas_procesadas.json` (326, 30 campos), renombrado desde `motos_procesados.json`.
- **Calidad combustión:** 257 sin `marca` (79 %), 30 sin `cilindrada_cc` (9 %), 304 sin `kilometraje_km`; 27 títulos repetidos (108 registros), en su mayoría anuncios distintos de dealer. No se deduplicaron. Sigue el outlier de kilometraje `58026629` (`240280 km`).

Embudo, de arriba abajo:

- **Listados crudos** (`data/processed/listados_crudos/`, únicos): motos **2.939** (de 3.174 brutos) · bicis **217** · patinetes **109** (de 167).
- **Clasificados** (`data/processed/clasificados/`): partición excluyente 538 motos · 613 bicis · 149 patinetes · 1.965 descartados = 3.265. Las cifras «nativas» por categoría de origen (537/176/82) son de la 1ª pasada (traza, no cifra final). Ver `data/processed/README.md`.
- **Muestras** (`data/processed/muestras/`): `motos_muestra_350.json` (350) · `bicis_muestra_300.json` (300) · `patinetes_muestra_300.json` (300).
- **Detalles descargados**: **350 motos** (`cache_detalle/motos/detalle_*.html`). Bicis y patinetes NO tienen detalle → no tienen datos técnicos.
- **Procesados de motos**: 326 válidos = **83 completos** + **243 parciales**; **24 descartados** (`versiones/motos_descartados.json`). En `final/`: `motos_procesados.json` (326), `motos_completos.json` (83), `motos_parciales.json` (243).
- **Limpios finales** (`final/`, 8 campos: `titulo, precio_usd, marca, modelo, provinceId, municipalityId, url_detalle, motivo`): motos **966** · bicis **2.049** · patinetes **314**. Total 3.329; bicis+patinetes ≈ **71 %**. (10-oct: quitada la única anomalía real, bici «Alta Gama» con `precio_usd 650000` colado como USD; antigua 2.050.)
- **`limpiar_finales.py` (elige la vía limpia, no la regla manual):**
  - `python src/scripts/limpiar_finales.py --verificar` → reproduce v2 exacto desde caché (aborta `exit 2` si No coincide con 1198/2861/373), aplica las reglas deterministas, calibra con la tabla de excepciones y compara contra los finales actuales. Sale `exit 0` si paridad total; deja `data/processed/verificacion_limpio.json`.
  - `--aplicar` → escribe los 3 finales (regerados) + `data/processed/versiones/limpio_excepciones.json`.
  - Reglas: solo USD; `100 ≤ precio ≤ 5000`; dedup por título sin emojis + precio + municipio; dedup por tokens + bucket $50 + municipio; ruido por palabras clave.
  - Excepciones (calibradas al histórico): 328 entradas (motos 86 keep/41 drop; bicis 88/97; patinetes 7/9) por `duplicado`/`ruido`/`ajuste_historico_manual` + **3 precios históricos** en motos (750→650 jmd, 2900→290, 1590→1620 vedca) conservados como `precio_historico` — el 290 parece errata a revisar a mano.
  - **El orden de los registros NO es contrato**; el script garantiza igualdad de URLs y de campos por registro. Para diffs limpios en git, los finales se han dejado = HEAD menos el cambio real (bicis 10 líneas quitadas).
- **`versiones/`** (`data/processed/`, antigua `previos/`): v1/v2/v3 de las 3 categorías + `bicis_final_limpio_agresivo.json` (1202, estructura antigua) + muestras viejas + descartados/extra. Es histórico: **no borrar, no usar para el informe**.
- **Caché HTML** (ignorada por git): `cache_html/` motos 30 listado + 13 búsqueda · bicis 30 + 34 · patinetes 30 + 11; `cache_detalle/motos/` 350.
- **Gráficos**: `storytelling/graphs/preliminar/` (12 PNG) → hechos con `motos_final.json` (538) y `motos_procesados.json` (300). Son preliminares; los definitivos van con los `*_final_limpio.json`.

Hallazgo metodológico que quiero recordar: **las categorías oficiales de Revolico infravaloraban la oferta** (subcategoría oficial de bicis ~151 anuncios vs **2.050** por búsqueda de texto; igual en motos y patinetes). Por eso busqué por texto, no por categoría.

## Esquemas (docs/schemas/)

- `esquema_moto_electrica.json` → 27 campos en `anuncio` (moto_electrica).
- `esquema_bici_electrica.json` y `esquema_patinete_electrico.json` → 29 campos (añaden `tamano_rueda_pulgadas`, `plegable`).
- `esquema_entrevista.json` → bloques: perfil, experiencia_compraventa, uso_contexto, experiencia_electrica, satisfaccion; id `user_XXX`.
- Se añadieron en v2: `vendedor_id`, `garantia_dias`. **No modificar campos sin consultar** (lo exige AGENTS.md).

## Decisiones ya tomadas (no re-litigar)

- Alcance **solo La Habana**; entrevistas solo a usuarios de eléctricos; 300 anuncios/categoría.
- Dedup de limpios **conservador**: tokens + bucket de $50 + municipio; filtros de precio 100–5000 y ruido. La versión agresiva queda como traza en `versiones/`.
- Los limpios se regeneran solo con `limpiar_finales.py`; no se editan a mano. Las excepciones manuales de la limpieza histórica viven en `versiones/limpio_excepciones.json`.
- **Nunca se borran descartados** (son traza y fuente de análisis).
- **Sin commits sin que Dagmary lo pida**; se propone el mensaje. Formato «tipo: qué cambió» (tipos: datos, codigo, historia, opencode, docs, estructura).
- La historia primero pide **outline aprobado**; sin aprobación no redacto.
- Entrevistas: audios fuera del repo; transcripción local con Whisper; solo códigos `user_XXX`, sin nombres; anonimizar teléfonos de vendedores.

## Trampas / gotchas (donde ya me he tropezado)

- **Nombres AGENTS.md ↔ realidad:** ya corregidos (`historia/`→`storytelling/`, `datos/`→`data/`, scripts en `src/`).
- `verificar_rutas.py`: de 17 rutas rotas tras la reorg a 6; quedan config/registro/notación e histórico del journal. Ninguna nueva. `make rutas` sale `exit 1` mientras existan.
- `_MARCAS`/`_MODELOS` son **moto-céntricos**: cobertura marca motos 54,3 % vs bicis 8,1 % y patinetes 7,3 %. `bucatt?i` NO captura «Buckatti». Faltan marcas bici/patinete: A12, Ava, Okday, Portobello, DTTZH, Onebot, Ridstar, JMD, Roinside, Caroma, Werhy, Segway, Laituning, Midha. (Para ampliar y regenerar limpios con `limpiar_finales.py`.)
- Filtro de ruido: `accesorio` matchea «accesorios» (2 falsos positivos en patinetes).
- `requirements.txt`: ya sin `pytest` duplicado (queda uno solo).
- El primer `--aplicar` de `limpiar_finales.py` escribió registros de 7 campos (faltaba convertir con `a_final`); el `--verificar` original solo comparaba URLs y no lo detectó. Ya compara **campo a campo**. Si tocas el script, añade esa paridad por registro en el reporte.
- `procesar_detalles` antes fijaba `_muestra_300.json` y rompía con motos (`_350`); ya usa glob `{categoria}_muestra_*.json` + `sorted(...)[0]`, y `FileNotFoundError` claro si no hay.
- Revolico no da fecha de publicación (solo de última actualización) y guarda ~14 días → **no puedo hacer análisis temporal**.
- La antigua `data/processed/_backup_antes_esquema_v2/` se movió a `versiones/` y se ignora (resuelto).
- **Embudo no anidado:** los elegibles v2 (4.432) superan los crudos únicos (3.265) porque cada tipo se filtra de forma independiente y un anuncio puede contar en varios; la reconciliación exacta queda `[pendiente]` (documentado en `data/README.md`).

## Estado de git ahora mismo (2026-10-26)

- **Renombrado (staged):** `final/motos_procesados.json` → `final/motos_electricas_procesadas.json`.
- **Modificados:** `data/processed/README.md`, `opencode/journal.md`, `opencode/handoff.md`; también venían modificados `data/raw/interviews/{preguntas,registro,transcripciones}.md` y los 3 esquemas eléctricos/bici/patinete.
- **Nuevos sin trackear:** `final/{motos_combustion_procesadas,outliers,descartados,candidatos_cache}.json`, `final/{bicis,patinetes}_{procesados,descartados}.json`, `final/patinetes_candidatos.json`, `docs/schemas/esquema_moto_combustion.json`, `src/scrapers/{bici,moto_combustion,patinete,refrescar_combustion,refrescar_patinetes}.py`, `transcribir.py`, `opencode/diagnostico.md` y `data/raw/interviews/{transcripciones,usuarios}/`.
- **Ignorados:** `venv/`, `.pytest_cache/`, `__pycache__/`, `data/raw/web/revolico/`.
- **No se ha hecho commit.** `git status` debe quedar sin caché HTML ni audios.

## Pendientes, por prioridad

**Inmediato (combustión):** el objetivo está cumplido: **325** válidos (300 pedidos) + **9** outliers de precio. No hace falta seguir descargando. Revisar a mano los 9 outliers y el `kilometraje_km=240280` de `58026629`; decidir si se corrige el `modelo` nulo y los demás defectos de parseo antes del informe.

1. **Acordar el commit** (tipos `datos`+`codigo`+`docs`+`estructura`+`opencode`): renombrado `versiones/`, READMEs, `Makefile`, `.githooks/`, notebooks, `AGENTS.md`, `src/scripts/limpiar_finales.py`, `tests/`, fuentes institucionales.
2. **Revisar a mano** los 3 precios de motos marcados `precio_historico` (jmd 650, el 290 sospechoso, vedca 1620).
3. **Decidir** si se limpian las rutas rotas restantes (clave `exports` de `config.yaml`, `registro.md` futuro, notación e histórico del journal) o se dejan como traza.
4. **Aprobar el outline** de `storytelling/outline.md`.
5. Preparar tablas y **gráficos definitivos** con los `*_final_limpio.json`.
6. **Ampliar `_MARCAS`/`_MODELOS`** (bicis/patinetes) y regenerar limpios con `limpiar_finales.py --aplicar`.
7. **Entrevistas**: ejecutar 30 (semana del 12-oct), volcar a `entrevistas_usuarios.json` (en `data/processed/`).
8. **Stakeholders**: crear esquemas de talleres e importadoras y registrar datos.

## Cómo comprobar que todo sigue bien

- `make test` → 5 passed (procesar_detalles motos da 3 completos con max 5; limpios existen y tienen los 8 campos; esquemas cargan; normalización de guiones no fusiona rangos).
- `procesar_detalles('motos')` → 83 completos / 243 parciales / 24 descartados.
- `python src/scripts/limpiar_finales.py --verificar` → `exit 0` con paridad total (v2 1198/2861/373 + reglas + excepciones = 966/2049/314).
- `make rutas` → 6 rutas rotas conocidas (config/registro/notación/histórico); sin nuevas.
- `git status` sin caché ni audios.

## Fuentes y enlaces

- Preguntas del estudio: `elements/Elementos.md`. Guía de entrevista: `data/raw/interviews/preguntas.md`. Registro: `data/raw/interviews/registro.md` (0/30).
- Institucionales: 5 fuentes oficiales descargadas (`decreto_163_2026`, `resolucion_175_2026`, `aduana_portada`, `mindus_marco`, `mfp_portada`) + `_fuentes.md`; MITRANS falló por SSL (sin reintento). Antiguas vacías: `ONCUBA.md`, `Postdata.club.md`. Redes: `data/raw/web/{Telegram,Facebook}.md`.
- `ARCHIVO`/`versiones` son histórico; el informe sale de los limpios + entrevistas + stakeholders.
