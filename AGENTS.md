
# AGENTS.md

## Proyecto
Análisis de mercado de motos eléctricas en Cuba (ICD). Combina scraping de Revolico, 30 entrevistas a usuarios y registro de stakeholders (tiendas, importadoras, talleres).

## Fuentes de datos
- `data/raw/revolico/` → anuncios scrapeados
- `data/raw/stakeholders/` → tiendas, importadoras, talleres
- `data/raw/interviews/usuarios/` → transcripciones
- `data/raw/web/` → redes sociales (complementario)

## Esquemas JSON (en `data/processed/`)
- `esquema_moto_electrica.json` 
- `esquema_bici_electrica.json`
- `esquema_patinete_electrico.json`
- `esquema_entrevista_usuario.json`
- `esquema_talleres.json`
- `esquema_importadoras.json`

Campos compartidos: marca, modelo, precio, moneda, tipo_vehiculo, es_electrica, uso_principal, canal_compra.
No modificar campos sin consultar.

## Stack
- Python 3, venv en `venv/`
- httpx (no requests), BeautifulSoup + lxml
- pandas, pydantic, scikit-learn, matplotlib
- Scripts en `src/`, notebooks para explorar

## Reglas para OpenCode
1. No inventes selectores HTML. Pide un fragmento real.
2. Trabaja por partes, no generes scrapers completos de golpe.
3. Respeta los esquemas JSON. No añadas ni quites campos sin consultar.
4. Nunca modifiques `data/raw/`.
5. Usa httpx, no requests.
6. El foco es motos; bicis y patinetes son secundarios.
7. Documenta cada decisión en `methodology.md`.
8. Registra prompts de IA en `prompts/sessions.md`.

## Scraping (ético)
- User-Agent honesto (estudiante con contacto).
- Delay mínimo 3 s entre peticiones.
- Máximo 150 peticiones por sesión.
- Cachear HTML en `data/raw/revolico/cache_*`.
- Si error 429, esperar 60 s.

## Notas
Proyecto académico, no producto. Objetivo: informe de análisis de mercado.
La trazabilidad importa más que la elegancia.
