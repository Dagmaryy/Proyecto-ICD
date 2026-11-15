# Versiones históricas (`data/processed/06_versiones/`)

Antes llamada `previos/`. Guarda las versiones intermedias del pipeline de Revolico
(v2), las muestras actuales y la tabla de excepciones del limpiador.

> **No usar para el informe y no borrar.** Es traza histórica. Los datasets vigentes
> están en `data/final/` y se documentan en `../README.md`.

## Archivos activos (input del pipeline)

| Archivo | Registros | Qué es |
|---|---:|---|
| `motos_final_v2.json` | 1198 | v2 · reclasificación tras las búsquedas ampliadas. |
| `bicis_final_v2.json` | 2861 | v2 · reclasificación tras las búsquedas ampliadas. |
| `patinetes_final_v2.json` | 373 | v2 · reclasificación tras las búsquedas ampliadas. |
| `motos_final_limpio.json` | — | Input de `src/scrapers/moto_electrica.py`. |
| `bicis_final_limpio.json` | — | Input de `src/scrapers/bici.py`. |
| `patinetes_final_limpio.json` | — | Input de `src/scrapers/refrescar_patinetes.py`. |
| `limpio_excepciones.json` | — | Tabla de excepciones del limpiador (keep/drop por URL y precios históricos). |

`limpio_excepciones.json` es un diccionario con claves `motos`, `bicis` y `patinetes`
(328 URL en total: 86/41, 88/97 y 7/9 de mantener/quitar, más 3 `precio_historico`).
Es la calibración manual que permite reproducir los limpios vigentes con
`src/scripts/limpiar_finales.py`.

## Reglas

- Las versiones **no se editan a mano** ni se borran.
- `*_final_v2.json` es la referencia que reproduce el limpiador (`--verificar`).

## `_historico/`

Versiones obsoletas conservadas por trazabilidad, **no usadas por el pipeline activo**.
Se incluyen aquí para que el revisor pueda ver la evolución del filtrado:

- `*_final.json` (v1, primera pasada).
- `*_final_v3.json` (v3, deduplicación sobre v2).
- `bicis_final_limpio_agresivo.json` (limpieza agresiva antigua).
- `*_muestra*.json` (muestras antiguas).
- `motos_extra.json`, `motos_descartados.json` (traza del proceso de muestreo).

Ninguno de estos archivos es leído por scripts en `src/`.
