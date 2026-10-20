
# AGENTS.md

## Proyecto
Análisis de mercado de motos eléctricas en Cuba (ICD). Combina scraping de Revolico, 30 entrevistas a usuarios y registro de stakeholders (tiendas, importadoras, talleres).

## Fuentes de datos
- `data/raw/web/revolico/` → anuncios scrapeados
- `data/raw/stakeholders/` → tiendas, importadoras, talleres
- `data/raw/interviews/usuarios/` → transcripciones
- `data/raw/web/` → redes sociales (complementario)

## Esquemas JSON (en `docs/schemas/`)
- `esquema_moto_electrica.json` 
- `esquema_bici_electrica.json`
- `esquema_patinete_electrico.json`
- `esquema_entrevista.json`

Campos compartidos: marca, modelo, precio, moneda, tipo_vehiculo, es_electrica, uso_principal, canal_compra.
No modificar campos sin consultar.

## Stack
- Python 3, venv en `venv/`
- httpx (no requests), BeautifulSoup + lxml
- pandas, pydantic, scikit-learn, matplotlib
- Scripts en `src/`, notebooks para explorar

## Comandos
- `make test` → tests de humo (`pytest`).
- `make rutas` → `src/scripts/verificar_rutas.py`.
- `make limpiar` → regenera `final/*_final_limpio.json` + `versiones/limpio_excepciones.json`.
- Hooks en `.githooks/`: `commit-msg` valida `tipo: qué cambió`; `pre-commit` bloquea caché, audios, `.env`, `venv/` y respaldos. No se activan solos; para usarlos: `git config core.hooksPath .githooks` (OpenCode no lo ejecuta).

## Reglas para OpenCode
1. No inventes selectores HTML. Pide un fragmento real.
2. Trabaja por partes, no generes scrapers completos de golpe.
3. Respeta los esquemas JSON. No añadas ni quites campos sin consultar.
4. Nunca modifiques `data/raw/`.
5. Usa httpx, no requests.
6. El foco es motos; bicis y patinetes son secundarios.


## Scraping (ético)
- User-Agent honesto (estudiante con contacto).
- Delay mínimo 3 s entre peticiones.
- Máximo 150 peticiones por sesión.
- Cachear HTML en `data/raw/web/revolico/cache_html*`.
- Si error 429, esperar 60 s.

## Notas
Proyecto académico, no producto. Objetivo: informe de análisis de mercado.
La trazabilidad importa más que la elegancia.

## Estructura
- storytelling/: historia en Markdown (historia.md), metodología, limitaciones, fuentes y gráficos
- src/: todos los scripts (scrapers/) y notebooks/
- data/: JSON, esquemas (esquemas/) y evidencias. data/raw no se modifica
- opencode/: journal.md y handoff.md

## Flujo con OpenCode
1. Al empezar: leer opencode/handoff.md y la última entrada de opencode/journal.md.
2. Trabajar por partes y detenerse al final de cada una para que Dagmary confirme.
3. Al terminar: añadir una entrada a opencode/journal.md.
4. Cuando el contexto pase del ~80% (o notes que releyendo archivos ya no recuerdas su contenido): actualizar opencode/handoff.md antes de seguir.
5. No hacer commits sin que Dagmary lo pida; proponer el mensaje.

## Historia
- Formato Markdown, en storytelling/historia.md.
- Estructura: título y cabecera; introducción (contexto, pregunta, motivación); desarrollo por bloques; conclusión o cierre; metodología; proceso de los datos; fecha y autor.
- Primero se propone el outline y se espera su aprobación; no redactar sin outline aprobado.
- No interpretar ni sacar conclusiones de los datos: la interpretación la escribe Dagmary. OpenCode solo prepara datos, tablas, gráficos y outlines.

## Commits
- Un commit por punto del proyecto, con formato "tipo: qué cambió".
- Tipos: datos, codigo, historia, opencode, docs, estructura.
- Nunca incluir caché HTML, audios ni carpetas de respaldo.

## Entrevistas
- Audios fuera del repo; transcribir con Whisper en local.
- Transcripciones solo con códigos (user_001), sin nombres.
- Anonimizar teléfonos de vendedores en los datos procesados.
