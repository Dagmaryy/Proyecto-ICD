# Proyecto ICD — Análisis del Mercado de Motos Eléctricas en Cuba

| | |
|---|---|
| **Asignatura** | Introducción a la Ciencia de Datos |
| **Profesor** | Yudivian Almeida |
| **Estudiante** | Dagmary Pérez Aguiar |

---

## Objetivo

Análisis del mercado de vehículos ligeros en La Habana (motos eléctricas, motos de combustión, bicicletas y patinetes) combinando scraping de Revolico, entrevistas a usuarios y datos de stakeholders.

---

## Datos y muestra

- **Fuente principal:** Revolico (scraping).
- **Cobertura geográfica:** La Habana.
- **Ventana temporal:** Los datos provienen de varias tandas de scraping entre septiembre y octubre de 2026. Revolico solo muestra anuncios recientes, por lo que no es posible hacer un análisis temporal continuo.
- **Muestra final:** 4 datasets de 300 registros cada uno.

---

## Estructura del repositorio

- `src/` — Scrapers y scripts de procesamiento.
- `data/raw/` — Datos crudos (no se versionan).
- `data/processed/final/JSON/` — Los 4 datasets finales + entrevistas.
- `data/processed/final/CSV/` — CSVs para gráficos.
- `docs/` — Documentación, esquemas JSON y journal.
- `reports/plots/` — 10 gráficos del informe (HTML + PNG).
- `web/` — Sitio web estático (`index.html`).
- `opencode/` — Handoff para el flujo con IA.
- `tests/` — Tests de integridad.

---

## Instalación y requisitos

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Reproducibilidad

```bash
# Verificar integridad
make test

# Verificar rutas
python src/scripts/verificar_rutas.py

# Regenerar CSVs y gráficos
python src/analysis/generar_csvs.py
python src/analysis/tabulacion_entrevistas.py
python src/analysis/graficos_finales.py
```

Metodología

Investigación mixta: cuantitativa (scraping) + cualitativa (entrevistas).

Técnicas de recolección

1. Scraping web (Revolico).
2. Entrevistas semiestructuradas.
3. Análisis documental (49 fuentes: Gacetas Oficiales, ONEI, Cubadebate, Granma, VEDCA, etc.).

Técnicas de análisis

1. Limpieza y normalización.
2. Estadísticas descriptivas.
3. Triangulación de fuentes.

##Datasets Finales
| Archivo | Registros | Descripción |
|---|---|---|
| `JSON/motos_electricas_300_enriquecido.json` | 300 | Motos eléctricas |
| `JSON/motos_combustion_300_enriquecido.json` | 300 | Motos de combustión |
| `JSON/bicis_300_enriquecido.json` | 300 | Bicicletas eléctricas |
| `JSON/patinetes_300_enriquecido.json` | 300 | Patinetes eléctricos |
| `JSON/entrevistas_final_corregido.json` | 30 | Entrevistas a usuarios |
| `JSON/clustering_motos.json` | — | Resultados del clustering (K-Means) |

Estado del proyecto (noviembre 2026)

· Informe final: docs/final_report.md (7 secciones, cerrado)
· Datos: 1,200 anuncios de Revolico + 30 entrevistas
· Fuentes: 49 documentos normativos y de prensa
· Gráficos: 10 generados en reports/plots/, 6 integrados en el sitio web
· Sitio web: web/index.html
· Evidencia OpenCode: docs/opencode_history.md + 11 prompts recuperados

Consideraciones éticas y limitaciones

· Ética: consentimiento informado, User-Agent honesto, delay >=3s, máx. 150 peticiones por sesión.
· Limitaciones: 100% La Habana, múltiples ventanas de scraping (no serie temporal continua), ~60% de anuncios sin todos los campos técnicos, canal formal con información fragmentaria.

---

Documentación

· docs/final_report.md — Informe final (7 secciones).
· docs/methodology.md — Pipeline técnico y fases.
· docs/limitations.md — 10 limitaciones del estudio.
· docs/decisions.md — 10 decisiones técnicas (ADR).
· docs/sources.md — 49 fuentes normativas y de prensa.
· docs/journal.md — Bitácora cronológica del desarrollo.
· docs/opencode_history.md — Evidencia de uso de OpenCode.




