# Versiones históricas (`data/processed/versiones/`)

Antes llamada `previos/`. Guarda las versiones intermedias del pipeline de Revolico
(v1, v2, v3), las muestras antiguas, los descartados/extra y la tabla de excepciones
del limpiador.

> **No usar para el informe y no borrar.** Es traza histórica. Los datasets vigentes
> están en `data/processed/final/` y se documentan en `../README.md`.

## Archivos

| Archivo | Registros | Qué es |
|---|---:|---|
| `motos_final.json` | 538 | v1 · salida preliminar de la 1ª pasada (estructura antigua). |
| `bicis_final.json` | 612 | v1 · salida preliminar de la 1ª pasada. |
| `patinetes_final.json` | 366 | v1 · salida preliminar de la 1ª pasada. |
| `motos_final_v2.json` | 1198 | v2 · reclasificación tras las búsquedas ampliadas. |
| `bicis_final_v2.json` | 2861 | v2 · reclasificación tras las búsquedas ampliadas. |
| `patinetes_final_v2.json` | 373 | v2 · reclasificación tras las búsquedas ampliadas. |
| `motos_final_v3.json` | 1089 | v3 · deduplicación sobre v2. |
| `bicis_final_v3.json` | 2460 | v3 · deduplicación sobre v2. |
| `patinetes_final_v3.json` | 357 | v3 · deduplicación sobre v2. |
| `bicis_final_limpio_agresivo.json` | 1202 | Limpieza agresiva (estructura antigua). Traza, no usar. |
| `motos_muestra.json` | 130 | Muestra vieja de motos. |
| `bicis_muestra.json` | 130 | Muestra vieja de bicis. |
| `patinetes_muestra.json` | 130 | Muestra vieja de patinetes. |
| `motos_muestra_300.json` | 300 | Muestra de motos para descargar detalle. |
| `motos_muestra_ampliada.json` | 50 | Ampliación de la muestra de motos. |
| `motos_extra.json` | 26 | Anuncios extra incorporados a la muestra de motos. |
| `motos_descartados.json` | 24 | Anuncios descartados por campos faltantes al procesar el detalle. |
| `limpio_excepciones.json` | — | Tabla de excepciones del limpiador (keep/drop por URL y precios históricos). |

`limpio_excepciones.json` es un diccionario con claves `motos`, `bicis` y `patinetes`
(328 URL en total: 86/41, 88/97 y 7/9 de mantener/quitar, más 3 `precio_historico`).
Es la calibración manual que permite reproducir los limpios vigentes con
`src/scripts/limpiar_finales.py`.

## Reglas

- Las versiones **no se editan a mano** ni se borran.
- `*_final_v2.json` es la referencia que reproduce el limpiador (`--verificar`).
- Las muestras antiguas y el `agresivo` quedan solo como evidencia del proceso.
