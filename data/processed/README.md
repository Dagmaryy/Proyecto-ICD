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
