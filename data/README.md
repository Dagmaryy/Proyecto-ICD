# `data/` — mapa y embudo de datos

| Carpeta | Contenido |
|---|---|
| `raw/` | Fuentes originales. **No se modifica.** Web (Revolico y redes), entrevistas y stakeholders. |
| `processed/` | Datos derivados del scraping (listados, clasificados, muestras, finales). Ver `processed/README.md`. |
| `processed/versiones/` | Versiones históricas del pipeline. **No usar en el informe.** Ver `processed/versiones/README.md`. |

Los datasets vigentes para el informe son
`processed/final/{motos,bicis,patinetes}_final_limpio.json`.

## Embudo

Cifras tomadas de los artefactos actuales. **Las etapas no están anidadas**: cada tipo
se filtra de forma independiente sobre el conjunto de listados, de modo que un mismo
anuncio puede contar en más de un tipo. Por eso la suma de elegibles no es un
subconjunto de los crudos; la reconciliación exacta entre etapas queda **[pendiente]**.

| Etapa | Artefacto | Motos | Bicis | Patinetes | Total |
|---|---|---:|---:|---:|---:|
| Crudos (únicos) | `listados_crudos/` | 2939 | 217 | 109 | **3265** |
| Crudos (brutos, antes de dedup de listado) | `listados_crudos/` | 3174 | 217 | 167 | **3558** |
| Clasificados (partición excluyente) | `clasificados/` | 538 | 613 | 149 | **1300** (+ 1965 descartados) |
| Elegibles (v2) | `versiones/*_final_v2.json` | 1198 | 2861 | 373 | **4432** |
| Reglas de limpieza | `limpiar_finales.py` | 921 | 2058 | 316 | **3295** |
| **Muestra final limpia** | `final/*_final_limpio.json` | **966** | **2049** | **314** | **3329** |

Notas de lectura:

- **Crudos:** `total_brutos` cuenta anuncios antes de quitar repetidos del listado;
  `total_unicos` es la base de 3265.
- **Clasificados:** partición mutuamente excluyente por anuncio (motos 538 · bicis 613 ·
  patinetes 149 · descartados 1965 = 3265). En el `handoff` aparecen las cifras "nativas"
  de la 1ª pasada (537 motos · 176 bicis · 82 patinetes): son traza, no la partición total.
- **Elegibles (v2):** reclasificación por tipo sobre las búsquedas ampliadas. Supera a
  los crudos únicos porque un anuncio puede entrar en varios tipos (solapamiento).
- **Reglas de limpieza:** salida determinista del limpiador (moneda USD, precio 100–5000,
  dedup por título/emoji y por tokens + bucket de $50, ruido). Reconciliación exacta
  entre clasificados y elegibles: **[pendiente]**.
- **Muestra final:** reglas + tabla de excepciones (`versiones/limpio_excepciones.json`).
  Reproducible con `python src/scripts/limpiar_finales.py --verificar` (`exit 0` si hay
  paridad).

## Regenerar y verificar

```bash
source venv/bin/activate
python src/scripts/limpiar_finales.py --verificar   # paridad; escribe verificacion_limpio.json
python src/scripts/limpiar_finales.py --aplicar     # reescribe los 3 finales + excepciones
python -m pytest tests/ -v
```
