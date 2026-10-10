# Handoff — memoria de trabajo de OpenCode

> Escrito para que yo (el agente) pueda retomar la conversación sin releer todo.
> Regla de oro: al empezar, LEER esto + la última entrada de `opencode/journal.md`. Cuando el contexto pase del ~80%, actualizar este archivo.

**Actualizado:** 2026-10-09 21:11
**Rama:** `main` (antes `esquemas-v2`)
**Objetivo:** análisis del mercado de motos eléctricas en La Habana (trabajo académico, no producto)

## Entorno
- Raíz: `/home/dagmary/Escritorio/ICD Project`
- Python: `source venv/bin/activate` (hay `venv/`). Ejecutar scripts con `python -u`.
- `codigo/scrapers/revolico.py`: `BASE_DIR = Path(__file__).resolve().parents[2]` → raíz del repo. Import desde la raíz: `from codigo.scrapers.revolico import procesar_detalles` (namespace package, sin `__init__.py`).
- Nunca usar `requests` (es httpx). Nunca tocar `data/raw/`.

## Estructura real de carpetas
- `codigo/scrapers/` (revolico.py, parser_prueba.py), `codigo/stt/`, `codigo/opencode/verificar_rutas.py`
- `data/raw/web/revolico/` (cache_html, cache_detalle), `data/raw/stakeholders/`, `data/raw/interviews/`
- `data/processed/` → `clasificados/` (3 dicts), `final/` (6), `listados_crudos/` (3), `muestras/` (3), `previos/` (17)
- `docs/` (methodology, decisions, sources, limitations, `schemas/`)
- `storytelling/` (graphs/, reports/) ← ojo: AGENTS.md dice `historia/`
- `opencode/` (handoff.md; `journal.md` AÚN NO EXISTE)
- Inconsistencia de nombres: AGENTS.md ↔ realidad: `historia/`↔`storytelling/`, `datos/`↔`data/`

## Datasets canónicos (8 campos: titulo, precio_usd, marca, modelo, provinceId, municipalityId, url_detalle, motivo)
- `data/processed/final/motos_final_limpio.json` → 966
- `data/processed/final/bicis_final_limpio.json` → 2050
- `data/processed/final/patinetes_final_limpio.json` → 314
- En `final/` también: `motos_procesados.json` (326), `motos_completos.json` (83), `motos_parciales.json` (243) [se quedan aquí por decisión]
- `muestras/`: `motos_muestra_350.json` (350), `bicis_muestra_300.json` (300), `patinetes_muestra_300.json` (300)
- `previos/`: v1/v2/v3 de las 3 categorías + `bicis_final_limpio_agresivo.json` (1202, estructura antigua) + descartados/extra + muestras viejas

## Trabajo staged SIN commit (git index)
1. Reorg: `src/scrapers/`→`codigo/scrapers/`, `reports/graphs/`→`storytelling/graphs/`, `reports/final_report.md`→`storytelling/reports/final_report.md`; `AGENTS.md` y `config.yaml` modificados.
- Nuevos: `codigo/opencode/verificar_rutas.py`, `opencode/handoff.md`.
- `data/processed/_backup_antes_esquema_v2/` eliminada (movida parcialmente a `previos/`).
- Renombre limpias bicis: canónico = `bicis_final_limpio.json` (2050); `bicis_final_limpio_agresivo.json` (1202, traza en `previos/`).
- Muestras viejas movidas a `previos/` (a decisión confirmada).

## Cambio reciente en código (sin commit)
- `procesar_detalles(categoria, ...)`: si `ruta_muestra is None`, hace glob de `{categoria}_muestra_*.json` en `data/processed/muestras/`, usa `sorted(...)[0]`, y si no hay, `FileNotFoundError` con categoría y carpeta. Antes fijaba `_muestra_300.json` (rompía con motos `_350`). Probado: `procesar_detalles('motos', max_anuncios=5)` → OK: 3 completos.

## Decisiones tomadas
- Alcance: La Habana. Entrevistas solo a usuarios de eléctricos. 300 anuncios/categoría. No se borran descartados.
- Dedup limpias: canónico = tokens+bucket $50+municipio (conservador), filtros precio 100–5000 y ruido. Agresivo se conserva como traza.
- Sin commits sin pedido explícito (proponer mensaje). Sin caché HTML/audios/respaldos en commits.

## Trampas a recordar
- `verificar_rutas.py` reporta ~22 rutas rotas: notebooks apuntan a `src/scrapers`/`reports/graphs`; refs en `AGENTS.md`, `opencode/handoff.md`, `config.yaml:9`.
- `_MARCAS`/`_MODELOS` son moto-céntricos: cobertura marca motos 54.3%, bicis 8.1%, patinetes 7.3%. `bucatt?i` NO captura "Buckatti". Marcas bicis/patinetes ausentes: A12, Ava, Okday, Portobello, DTTZH, Onebot, Ridstar, JMD, Roinside, Caroma, Werhy, Segway, Laituning, Midha.
- Filtro de ruido: `accesorio` matchea "accesorios" (2 falsos positivos en patinetes).
- Backup `_backup_antes_esquema_v2/` estaba trackeada (26 archivos) contra la regla de AGENTS.md.
- Motos keyword lookup: sin rastro de gasolina/combustión; "bici moto" (31) y "motor de" (3) son eléctricas.

## Pendiente (por prioridad)
1. Commit de todo lo staged (proponer mensaje).
2. Reconciliar nombres `historia/`↔`storytelling/`, `datos/`↔`data/` y arreglar rutas rotas.
- 3. Ampliar `_MARCAS`/`_MODELOS` (bicis/patinetes).
- 4. Decidir promoción de los finales limpios.
- 5. Entrevistas/stakeholders.
- 6. Outline de la historia (AGENTS.md exige outline aprobado antes de redactar; yo no interpreto datos, solo preparo tablas/gráficos/outlines).
- Crear `opencode/journal.md`.

## Cómo verificar que todo sigue bien
- Caché con 350 detalles de motos.
- `procesar_detalles('motos')` → 83 completos / 243 parciales / 24 descartados.
- `python3 codigo/opencode/verificar_rutas.py` (esperado: sin rutas rotas una vez reconciliado).
- `git status` sin caché ni audios.
