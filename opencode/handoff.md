# Handoff — memoria de trabajo (para mí, OpenCode)

> Notas para retomar sin releer nada. Al empezar: leer ESTO + la última entrada de `journal.md`.
> Actualizar cuando el contexto pase del ~80% o cuando releyendo archivos ya no recuerde su contenido.

**Escrito/actualizado:** 2026-10-10 · **Rama:** `main` · **Último commit:** `529c3ae` (estructura: reorg completa + previos + outline inicial)
**Repo:** https://github.com/Dagmaryy/ICD-Project.git · **Raíz:** `/home/dagmary/Escritorio/Proyecto ICD`

---

## Contexto de un vistazo

Trabajo académico de ICD (Introducción a la Ciencia de Datos, prof. Yudivian Almeida). Analizo el **mercado de vehículos eléctricos de dos ruedas en La Habana** (motos sobre todo; bicis/bicimotos y patinetes como categorías complementarias). Junto **scraping de Revolico + 30 entrevistas a usuarios + stakeholders** (tiendas, importadoras, talleres, instituciones). Entrego una **historia/informe**, no software. La interpretación la escribe Dagmary; yo preparo datos, tablas, gráficos y outlines.

Pregunta general: *¿cuál es el verdadero costo operativo, económico y regulatorio de adquirir y usar un eléctrico de dos ruedas en La Habana en 2026?*
Pista de marca para el título de la historia: «El Verdadero Costo de Moverse».

## Cómo me muevo por el repo (no olvidar)

- Activar `source venv/bin/activate`; correr siempre desde la raíz con `python -u`.
- El código es **namespace package** (sin `__init__.py`): `from codigo.scrapers.revolico import procesar_detalles`.
- `revolico.py` define raíz con `BASE_DIR = Path(__file__).resolve().parents[2]`.
- **httpx, nunca requests.** **Nunca tocar `data/raw/`.** Nunca versionar caché HTML ni audios.
- Tests: `python -m pytest tests/ -v` → 4 passed.
- Diagnóstico de rutas: `python3 codigo/scripts/verificar_rutas.py`.

## Quién es quién de archivos

- `codigo/scrapers/revolico.py` (~1201 líneas) → todo el scraping + limpieza base. Funciones que importan: `descargar_listado(url, categoria, usar_cache, etiqueta)`, `descargar_detalle`, `descargar_lote`, `contar_paginas`, `extraer_anuncios_listado`, `es_moto_electrica`/`es_bici_electrica`/`es_patinete_electrico`, `clasificar_listado`, `consolidar_clasificados`, `seleccionar_muestra(n, seed=42)`, `extraer_detalle`, `extraer_campos_tecnicos`, `construir_anuncio_segun_esquema`, `_MARCAS`/`_MODELOS`, `_extraer_marca_modelo`, `procesar_detalles(categoria, max_anuncios, ruta_muestra)`.
- `codigo/scrapers/parser_prueba.py` → parser de pruebas (histórico).
- `codigo/scripts/verificar_rutas.py` → busca referencias de rutas rotas.
- `codigo/scripts/limpiar_finales.py` → **limpiador reproducible** de los finales (ver abajo).
- `config.yaml` → parámetros (ver abajo).
- `elements/Elementos.md` → **las 30 preguntas del estudio** (fuentes A/E/S/D).
- `storytelling/outline.md` → outline propuesto de la historia (**sin aprobar**).
- `notebooks/01..05` → EDA y gráficos (01_eda_motos, 02_eda_listado_motos, 03_analisis_precios_motos, 04_eda_motos_final, 05_graficos_motos).

## Config que rige (config.yaml)

- Scraping: UA honesto «MiProyectoInvestigacion/1.0 (Dagmaryy; dagmary2222008@gmail.com)», `delay_segundos: 3`, `delay_429_segundos: 60`, `max_peticiones: 150`, `max_paginas_por_url: 10`.
- Economía: `tasa_cup_por_usd: 350` (fecha 2026-10-05).
- Análisis: `max_anuncios_por_tipo: 30`, clustering `n_clusters: 6`, `random_state: 42`.
- Rutas: `raw: data/raw`, `processed: data/processed`, `graphs: storytelling/graphs`, `cache_listado/detalle` bajo `data/raw/web/revolico/`.

## Datos: qué hay y cuánto (verificado 2026-10-10)

Embudo, de arriba abajo:

- **Listados crudos** (`data/processed/listados_crudos/`, únicos): motos **2.939** (de 3.174 brutos) · bicis **217** · patinetes **109** (de 167).
- **Clasificados** (`data/processed/clasificados/`, 1ª pasada del 08-oct): motos 537 · bicis 176 · patinetes 82. Ojo: son de la primera pasada y quedaron superados por las búsquedas ampliadas; sirven como traza, no como cifra final.
- **Muestras** (`data/processed/muestras/`): `motos_muestra_350.json` (350) · `bicis_muestra_300.json` (300) · `patinetes_muestra_300.json` (300).
- **Detalles descargados**: **350 motos** (`cache_detalle/motos/detalle_*.html`). Bicis y patinetes NO tienen detalle → no tienen datos técnicos.
- **Procesados de motos**: 326 válidos = **83 completos** + **243 parciales**; **24 descartados** (`previos/motos_descartados.json`). En `final/`: `motos_procesados.json` (326), `motos_completos.json` (83), `motos_parciales.json` (243).
- **Limpios finales** (`final/`, 8 campos: `titulo, precio_usd, marca, modelo, provinceId, municipalityId, url_detalle, motivo`): motos **966** · bicis **2.049** · patinetes **314**. Total 3.329; bicis+patinetes ≈ **71 %**. (10-oct: quitada la única anomalía real, bici «Alta Gama» con `precio_usd 650000` colado como USD; antigua 2.050.)
- **`limpiar_finales.py` (elige la vía limpia, no la regla manual):**
  - `python codigo/scripts/limpiar_finales.py --verificar` → reproduce v2 exacto desde caché (aborta `exit 2` si No coincide con 1198/2861/373), aplica las reglas deterministas, calibra con la tabla de excepciones y compara contra los finales actuales. Sale `exit 0` si paridad total; deja `data/processed/verificacion_limpio.json`.
  - `--aplicar` → escribe los 3 finales (regerados) + `data/processed/previos/limpio_excepciones.json`.
  - Reglas: solo USD; `100 ≤ precio ≤ 5000`; dedup por título sin emojis + precio + municipio; dedup por tokens + bucket $50 + municipio; ruido por palabras clave.
  - Excepciones (calibradas al histórico): 328 entradas (motos 86 keep/41 drop; bicis 88/97; patinetes 7/9) por `duplicado`/`ruido`/`ajuste_historico_manual` + **3 precios históricos** en motos (750→650 jmd, 2900→290, 1590→1620 vedca) conservados como `precio_historico` — el 290 parece errata a revisar a mano.
  - **El orden de los registros NO es contrato**; el script garantiza igualdad de URLs y de campos por registro. Para diffs limpios en git, los finales se han dejado = HEAD menos el cambio real (bicis 10 líneas quitadas).
- **`previos/`**: v1/v2/v3 de las 3 categorías + `bicis_final_limpio_agresivo.json` (1202, estructura antigua) + muestras viejas + descartados/extra. Es histórico: **no borrar, no usar para el informe**.
- **Caché HTML** (ignorada por git): `cache_html/` motos 30 listado + 13 búsqueda · bicis 30 + 34 · patinetes 30 + 11; `cache_detalle/motos/` 350.
- **Gráficos**: `storytelling/graphs/preliminar/` (12 PNG) → hechos con `motos_final.json` (538) y `motos_procesados.json` (300). Son preliminares; los definitivos van con los `*_final_limpio.json`.

Hallazgo metodológico que quiero recordar: **las categorías oficiales de Revolico infravaloraban la oferta** (subcategoría oficial de bicis ~151 anuncios vs **2.050** por búsqueda de texto; igual en motos y patinetes). Por eso busqué por texto, no por categoría.

## Esquemas (docs/schemas/)

- `esquema_moto_electrica.json` → 27 campos en `anuncio` (moto_electrica).
- `esquema_bici_electrica.json` y `esquema_patinete_electrico.json` → 29 campos (añaden `tamano_rueda_pulgadas`, `plegable`).
- `esquema_entrevista.json` → bloques: perfil, experiencia_compraventa, uso_contexto, experiencia_electrica, satisfaccion; id `user_XXX`.
- Se añadieron en v2: `vendedor_id`, `garantia_dias`. **No modificar campos sin consultar** (lo exige AGENTS.md).
- OJO: AGENTS.md menciona `esquema_talleres.json` y `esquema_importadoras.json` que **no existen todavía**.

## Decisiones ya tomadas (no re-litigar)

- Alcance **solo La Habana**; entrevistas solo a usuarios de eléctricos; 300 anuncios/categoría.
- Dedup de limpios **conservador**: tokens + bucket de $50 + municipio; filtros de precio 100–5000 y ruido. La versión agresiva queda como traza en `previos/`.
- Los limpios se regeneran solo con `limpiar_finales.py`; no se editan a mano. Las excepciones manuales de la limpieza histórica viven en `previos/limpio_excepciones.json`.
- **Nunca se borran descartados** (son traza y fuente de análisis).
- **Sin commits sin que Dagmary lo pida**; se propone el mensaje. Formato «tipo: qué cambió» (tipos: datos, codigo, historia, opencode, docs, estructura).
- La historia primero pide **outline aprobado**; sin aprobación no redacto.
- Entrevistas: audios fuera del repo; transcripción local con Whisper; solo códigos `user_XXX`, sin nombres; anonimizar teléfonos de vendedores.

## Trampas / gotchas (donde ya me he tropezado)

- **Nombres inconsistentes AGENTS.md ↔ realidad:** AGENTS.md dice `historia/` (es `storytelling/`), `datos/` (es `data/`) y «scripts en `src/`» (es `codigo/`).
- `verificar_rutas.py` reportaba ~**28 rutas rotas** (estuve a punto de dejarlo en 22): notebooks apuntan a `src/scrapers`/`reports/graphs`; refs en `AGENTS.md`, handoff y `config.yaml`.
- `_MARCAS`/`_MODELOS` son **moto-céntricos**: cobertura marca motos 54,3 % vs bicis 8,1 % y patinetes 7,3 %. `bucatt?i` NO captura «Buckatti». Faltan marcas bici/patinete: A12, Ava, Okday, Portobello, DTTZH, Onebot, Ridstar, JMD, Roinside, Caroma, Werhy, Segway, Laituning, Midha. (Para ampliar y regenerar limpios con `limpiar_finales.py`.)
- Filtro de ruido: `accesorio` matchea «accesorios» (2 falsos positivos en patinetes).
- `requirements.txt` tiene **`pytest` duplicado** (líneas 30-31, en `# Tests`). Pendiente limpiar antes de commit.
- El primer `--aplicar` de `limpiar_finales.py` escribió registros de 7 campos (faltaba convertir con `a_final`); el `--verificar` original solo comparaba URLs y no lo detectó. Ya compara **campo a campo**. Si tocas el script, añade esa paridad por registro en el reporte.
- `procesar_detalles` antes fijaba `_muestra_300.json` y rompía con motos (`_350`); ya usa glob `{categoria}_muestra_*.json` + `sorted(...)[0]`, y `FileNotFoundError` claro si no hay.
- Revolico no da fecha de publicación (solo de última actualización) y guarda ~14 días → **no puedo hacer análisis temporal**.
- La subcarpeta `data/processed/_backup_antes_esquema_v2/` estaba trackeada contra la regla de AGENTS.md; ya se movió a `previos/` y se ignora.

## Estado de git ahora mismo

- Trackeados y modificados: `opencode/handoff.md`, `requirements.txt`, `data/processed/final/bicis_final_limpio.json` (outlier eliminado; motos/patinetes intactos).
- Sin trackear: `.env.example` (`.env` está ignorado), `opencode/journal.md`, `tests/`, `codigo/scripts/limpiar_finales.py`, `data/processed/previos/limpio_excepciones.json`, `data/processed/verificacion_limpio.json` (reporte; decidir si se versiona).
- Ignorados: `venv/`, `.pytest_cache/`, `__pycache__/`, `data/raw/web/revolico/`.
- `git status` debe quedar **sin caché HTML ni audios**.

## Pendientes, por prioridad

1. **Acordar el commit** de lo pendiente (tipos `datos`+`codigo`+`opencode`): `bicis_final_limpio.json` (2049), `codigo/scripts/limpiar_finales.py`, `previos/limpio_excepciones.json`, `tests/`, `opencode/`, `requirements.txt` (+ quitar el `pytest` duplicado antes), `.env.example`.
2. **Revisar a mano** los 3 precios de motos marcados `precio_historico` (jmd 650, el 290 sospechoso, vedca 1620) y, si se corrigen, reflejarlo en la tabla de excepciones.
3. **Reconciliar nombres** (`historia/`↔`storytelling/`, `datos/`↔`data/`) y arreglar las rutas rotas hasta que `verificar_rutas.py` salga limpio.
4. **Aprobar el outline** de `storytelling/outline.md`.
5. Preparar tablas y **gráficos definitivos** con los `*_final_limpio.json`.
6. **Ampliar `_MARCAS`/`_MODELOS`** (bicis/patinetes) y regenerar limpios con `limpiar_finales.py --aplicar`.
7. **Entrevistas**: ejecutar 30 (semana del 12-oct), volcar a `data/processed/entrevistas_usuarios.json`.
8. **Stakeholders**: crear esquemas de talleres e importadoras y registrar datos.

## Cómo comprobar que todo sigue bien

- `python -m pytest tests/ -v` → 4 passed (procesar_detalles motos da 3 completos con max 5; limpios existen y tienen los 8 campos; esquemas cargan).
- `procesar_detalles('motos')` → 83 completos / 243 parciales / 24 descartados.
- `python codigo/scripts/limpiar_finales.py --verificar` → `exit 0` con paridad total (v2 1198/2861/373 + reglas + excepciones = 966/2049/314).
- `python3 codigo/scripts/verificar_rutas.py` → sin rutas rotas (una vez reconciliado).
- `git status` sin caché ni audios.

## Fuentes y enlaces

- Preguntas del estudio: `elements/Elementos.md`. Guía de entrevista: `data/raw/interviews/preguntas.md`. Registro: `data/raw/interviews/registro.md` (0/30).
- Documentales previstas (aún vacías): `data/raw/stakeholders/institucionales/ONCUBA.md`, `Postdata.club.md`. Redes: `data/raw/web/{Telegram,Facebook}.md`.
- `ARCHIVO`/`previos` son histórico; el informe sale de los limpios + entrevistas + stakeholders.
