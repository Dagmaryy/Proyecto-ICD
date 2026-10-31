# Proyecto ICD — Análisis del Mercado de Motos Eléctricas en Cuba

| | |
|---|---|
| **Asignatura** | Introducción a la Ciencia de Datos |
| **Profesor** | Yudivian Almeida |
| **Estudiante** | Dagmary Pérez Aguiar |

---

## Objetivo

Análisis del mercado de vehículos ligeros en La Habana (motos eléctricas, motos de combustión, bicicletas y patinetes) combinando scraping de Revolico, entrevistas a usuarios y datos de stakeholders. El entregable es un informe de análisis de mercado.

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
- `data/processed/final/` — Los 4 datasets de 300 registros.
- `docs/` — Documentación, esquemas JSON y journal.
- `reports/` — Informe final y gráficos.
- `opencode/` — Handoff para el flujo con IA.
- `tests/` — Tests de integridad.

---

## Instalación y requisitos

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Reproducibilidad

- Para verificar la integridad: `make test`.
- Para verificar rutas: `python src/scripts/verificar_rutas.py`.

---

## Metodología

Investigación mixta: cuantitativa (scraping) + cualitativa (entrevistas).

### Técnicas de recolección

1. Scraping web (Revolico).
2. Entrevistas semiestructuradas.
3. Análisis documental (ONCUBA, Postdata.club, Decreto 163/2026).

### Técnicas de análisis

1. Limpieza y normalización.
2. Estadísticas descriptivas.
3. Triangulación de fuentes.

---

## Datasets finales

| Archivo | Registros | Descripción |
|---|---|---|
| `motos_electricas_300.json` | 300 | Motos eléctricas |
| `motos_combustion_300.json` | 300 | Motos de combustión |
| `bicis_300.json` | 300 | Bicicletas eléctricas |
| `patinetes_300.json` | 300 | Patinetes eléctricos |

---

## Consideraciones éticas y limitaciones

- **Ética:** consentimiento informado, User-Agent honesto, delay >=3s, máx. 150 peticiones por sesión.
- **Limitaciones:** 100% La Habana, múltiples ventanas de scraping (no serie temporal continua), ~60% de anuncios sin todos los campos técnicos, canal formal con información fragmentaria.

---

## Documentación

- `docs/outline.md` — Estructura del informe.
- `docs/final_report.md` — Informe final.
- `docs/elements.md` — Preguntas de investigación.
- `docs/schemas/` — Esquemas JSON.
- `docs/methodology.md`, `docs/decisions.md`, `docs/sources.md`, `docs/limitaciones.md` (si existen).
- `docs/journal.md` — Bitácora de trabajo.


