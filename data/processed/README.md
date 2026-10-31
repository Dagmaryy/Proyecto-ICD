# `data/processed/` — datos vigentes y flujo

Datos derivados de Revolico. Aquí viven los artefactos **vigentes**; las versiones
intermedias y las trazas están en `versiones/` (ver `versiones/README.md`).

Los datasets que alimentan el informe son los `*_final_limpio.json`.

## Artefactos vigentes

| Artefacto | Ruta | Registros | Uso |
|---|---|---:|---|
| Listado crudo de motos | `listados_crudos/motos_listado.json` | 2939 únicos (3174 brutos) | Entrada del pipeline. |
| Listado crudo de bicis | `listados_crudos/bicis_listado.json` | 217 únicos (217 brutos) | Entrada del pipeline. |
| Listado crudo de patinetes | `listados_crudos/patinetes_listado.json` | 109 únicos (167 brutos) | Entrada del pipeline. |
| Clasificados (partición) | `clasificados/*_clasificado.json` | 3265 (538 motos · 613 bicis · 149 patinetes · 1965 descartados) | Traza de clasificación. No es cifra final. |
| Muestras para detalle | `muestras/motos_muestra_350.json` | 350 | Descarga de detalle de motos. |
| | `muestras/bicis_muestra_300.json` | 300 | Muestra de bicis. |
| | `muestras/patinetes_muestra_300.json` | 300 | Muestra de patinetes. |
| **Motos limpio** | `final/motos_final_limpio.json` | **966** | Dataset vigente de motos. |
| **Bicis limpio** | `final/bicis_final_limpio.json` | **2049** | Dataset vigente de bicis. |
| **Patinetes limpio** | `final/patinetes_final_limpio.json` | **314** | Dataset vigente de patinetes. |
| Motos procesadas | `final/motos_procesados.json` | 326 | Detalle de motos (326 válidos). |
| Motos completas | `final/motos_completos.json` | 83 | Subconjunto con todos los campos. |
| Motos parciales | `final/motos_parciales.json` | 243 | Subconjunto con campos faltantes. |
| Bicis procesadas | `final/bicis_procesados.json` | 414 | Detalle de bicis válidas (campos del esquema de bici). |
| Bicis descartadas | `final/bicis_descartados.json` | 184 | Bicis intentadas no válidas (`borrado`, `expirado`, `error_descarga`, `detalle_invalido`). Aditivo, sin duplicar por `id`. |
| Patinetes procesados | `final/patinetes_procesados.json` | 335 | Detalle de patinetes válidos (campos del esquema de patinete). |
| Patinetes descartados | `final/patinetes_descartados.json` | 110 | Patinetes intentados no válidos. Aditivo, sin duplicar por `id`. |
| Patinetes candidatos | `final/patinetes_candidatos.json` | 482 | Candidatos de La Habana para la fase de detalle. |
| Combustión candidatos | `final/motos_combustion_candidatos_cache.json` | 694 | Candidatos de La Habana de búsquedas específicas de combustión. |
| **Motos de combustión** | `final/motos_combustion_procesadas.json` | **325** | Dataset vigente de motos de combustión (30 campos del esquema de combustión). Objetivo de 300 superado. |
| Combustión outliers | `final/motos_combustion_outliers.json` | 9 | Motos válidas con precio fuera de 100–5000 USD (incluye la Honda CBR 600 a 8500 USD y 8 precios extraídos como 1 USD). |
| Combustión descartados | `final/motos_combustion_descartados.json` | 191 | Anuncios intentados no válidos o no-combustión. Aditivo, sin duplicar por `id`. |
| Verificación del limpiador | `verificacion_limpio.json` | — | Reporte de paridad (regenerable). |

Los tres `*_final_limpio.json` tienen 8 campos:
`titulo`, `precio_usd`, `marca`, `modelo`, `provinceId`, `municipalityId`,
`url_detalle`, `motivo`.

## Flujo

1. **Descarga de listados** → `listados_crudos/`
   (`src/scrapers/revolico.py`: `descargar_listado`, `descargar_lote`).
2. **Clasificación** → `clasificados/`
   (`clasificar_listado`, `consolidar_clasificados`).
3. **Muestreo** → `muestras/` (`seleccionar_muestra`, semilla 42).
4. **Detalle (solo motos)** → `final/motos_procesados.json` + `completos/parciales`
   (`procesar_detalles`).
4b. **Detalle de bicis (La Habana)** → `final/bicis_procesados.json` +
   `final/bicis_descartados.json` (`src/scrapers/bici.py`, reutiliza `procesar_detalles`).
4c. **Detalle de motos de combustión (La Habana)** → `final/motos_combustion_procesadas.json` +
   `final/motos_combustion_outliers.json` + `final/motos_combustion_descartados.json`
   (`src/scrapers/moto_combustion.py`; candidatos con `src/scrapers/refrescar_combustion.py`).
4d. **Detalle de patinetes** → `final/patinetes_procesados.json` +
   `final/patinetes_descartados.json` (`src/scrapers/patinete.py`).
5. **Limpieza final** → `final/*_final_limpio.json`
   (`src/scripts/limpiar_finales.py --aplicar`).
6. **Verificación** → `verificacion_limpio.json`
   (`src/scripts/limpiar_finales.py --verificar`, `exit 0` si hay paridad).

## Reglas

- Los limpios **no se editan a mano**: se regeneran con `limpiar_finales.py`.
- **No se borran los descartados**: son traza y fuente de análisis.
- `versiones/` es histórico: **no usar para el informe**.
- El orden de los registros no es parte del contrato; el script garantiza igualdad
  de URL y de campos por registro.
