# Diagnóstico del proyecto ICD

**Fecha:** 2026-10-20  
**Modo:** solo lectura. No se modificó ningún archivo versionado del proyecto; este informe es el único archivo creado.  
**Red:** 13 peticiones HTTP en total (10 + 2 + 1), con 3 s entre peticiones, User-Agent de `config.yaml` y sin errores 429. Dentro del máximo de 20.  
**Alcance:** revisión de código, tests, caché, datos procesados, fuentes, entrevistas, configuración, documentación y repositorio.

---

## A. Estado del código y los tests

### 1. `make test`: qué pasa y qué no cubre

`make test` ejecuta `python -m pytest tests/ -v` y da **4 passed en 0,17 s** (Python 3.14.4, pytest 9.1.1):

- `tests/test_smoke.py::test_procesar_detalles_motos` — PASSED
- `tests/test_smoke.py::test_limpios_existen` — PASSED
- `tests/test_smoke.py::test_limpios_campos` — PASSED
- `tests/test_smoke.py::test_esquemas_cargan` — PASSED

Dependencias reales de los tests:

| Test | Depende de | Si falta |
|---|---|---|
| `test_procesar_detalles_motos` | `cache_detalle/motos/` + `data/processed/muestras/motos_muestra_350.json` | `FileNotFoundError` o 0 completos; el test espera 3 completos de los 5 primeros |
| `test_limpios_existen` | `data/processed/final/{motos,bicis,patinetes}_final_limpio.json` | falla |
| `test_limpios_campos` | los 3 finales y sus 8 campos exactos | falla |
| `test_esquemas_cargan` | `docs/schemas/*.json` | falla |

No hay tests para: clasificación, embudo, `verificar_rutas`, `limpiar_finales`, configuración, red, bicis/patinetes con detalle ni entrevistas. El test de detalles usa `max_anuncios=5` y solo motos (`tests/test_smoke.py:28-32`).

### 2. URLs de búsqueda usadas por vehículo

Hay **148 HTML** en `data/raw/web/revolico/cache_html/`: 90 archivos `listado_*` (30 por categoría) y 58 `busqueda_*` (13 motos + 34 bicis + 11 patinetes, según `handoff.md:64`). Por contenido, **solo los 30 `listado_*` de motos** usan la subcategoría oficial (`subcategory=vehiculos-motos-electricas-y-triciclos`); los de bicis usan `q=electrica` + `subcategory=vehiculos-bicicletas` y los de patinetes usan `q=patinete+electrico`. El journal del 2026-10-08 habla de “42 páginas de búsquedas ampliadas” (`journal.md:109`); el cache actual tiene 58 archivos `busqueda_*`.

URLs canónicas (sin `&page=N`), con páginas, anuncios brutos, únicos por familia, asignación por clasificador y descartados:

| URL de búsqueda | Págs. | Brutos | Únicos | Moto | Bici | Patinete | Descartados |
|---|---:|---:|---:|---:|---:|---:|---:|
| `https://www.revolico.com/search?category=vehiculos&subcategory=vehiculos-motos-electricas-y-triciclos&order=date` | 30 | 3174 | 2939 | 537 | 429 | 66 | 1907 |
| `https://www.revolico.com/search?q=moticos&order=date` | 10 | 940 | 938 | 596 | 9 | 1 | 332 |
| `https://www.revolico.com/search?q=moto+electrica&order=date` | 1 | 114 | 114 | 100 | 1 | 0 | 13 |
| `https://www.revolico.com/search?q=trimoto+electrica&order=date` | 1 | 119 | 119 | 3 | 13 | 0 | 103 |
| `https://www.revolico.com/search?q=bici+electrica&order=date` | 3 | 274 | 269 | 44 | 150 | 0 | 75 |
| `https://www.revolico.com/search?q=bicicleta+electrica&order=date` | 31 | 3153 | 2993 | 23 | 2688 | 5 | 277 |
| `https://www.revolico.com/search?q=electrica&category=vehiculos&subcategory=vehiculos-bicicletas&order=date` | 30 | 217 | 217 | 0 | 176 | 1 | 40 |
| `https://www.revolico.com/search?q=patineta+electrica&order=date` | 2 | 240 | 220 | 8 | 5 | 165 | 42 |
| `https://www.revolico.com/search?q=patinete+electrico&order=date` | 31 | 267 | 110 | 1 | 8 | 83 | 18 |
| `https://www.revolico.com/search?q=scooter+electrico&order=date` | 3 | 306 | 209 | 8 | 6 | 116 | 79 |
| `https://www.revolico.com/search?q=scooter+electrico+plegable&order=date` | 2 | 114 | 112 | 0 | 5 | 89 | 18 |
| `https://www.revolico.com/search?q=scooter+plegable&order=date` | 2 | 118 | 116 | 0 | 6 | 88 | 22 |
| `https://www.revolico.com/search?q=monopatin&order=date` | 1 | 6 | 6 | 0 | 0 | 1 | 5 |
| `https://www.revolico.com/search?q=monopatin+electrico&order=date` | 1 | 22 | 22 | 0 | 0 | 1 | 21 |
| **Suma por familia** | **148** | **9064** | **8384** | **1320** | **3496** | **616** | **2952** |

Los “únicos” son únicos dentro de cada familia; entre familias hay solapamiento, por eso la suma (8384) no es el total global. “Descartados” = no aceptado por ninguno de los 3 clasificadores eléctricos.

Lectura por vehículo:

- **Motos:** subcategoría oficial (30 págs.) + `moticos` (10) + `moto electrica` (1) + `trimoto electrica` (1).
- **Bicis:** `bici electrica` (3) + `bicicleta electrica` (31) + subcategoría de bicis con `q=electrica` (30).
- **Patinetes:** `patineta electrica` (2) + `patinete electrico` (31) + `scooter electrico` (3) + `scooter electrico plegable` (2) + `scooter plegable` (2) + `monopatin` (1) + `monopatin electrico` (1).

Hallazgo: la subcategoría de bicis con `q=electrica` trae **217** anuncios, mientras que la búsqueda `bicicleta electrica` trae **2993** únicos. La subcategoría oficial de motos trae **2939** únicos. No hay una subcategoría oficial de patinetes en la caché: sus 30 `listado_*` son en realidad la búsqueda `q=patinete+electrico`. Además, las búsquedas no son puras: `bici electrica` produce 44 motos y `trimoto electrica` descarta 103 de 119.

### 3. 10 URLs aleatorias de bicis: estado y última actualización

Muestra aleatoria con semilla `20261020` (10 URLs de `bicis_final_limpio.json`). Resultado: **10/10 HTTP 200 y 0/10 HTTP 404**, pero no todas son detalles válidos.

| URL | HTTP | Estado real | Última actualización | Detalle |
|---|---:|---|---|---|
| `.../bicicleta-electrica-veloce-plus-pd-57866697` | 200 | activo (`AdType`, `isSold=false`) | 2026-10-20T17:34:49Z | título y precio 970 |
| `.../bicicleta-electrica-55966436` | 200 | **borrado** (`errorCode=cant-see-deleted-ad`, sin `AdType`) | — | no parseable |
| `.../bicicleta-electrica-57740725` | 200 | activo | 2026-09-28T13:50:56Z | precio 1000 |
| `.../bicicleta-electrica-marca-portobello-57016740` | 200 | activo | 2026-10-20T16:26:00Z | precio 550 |
| `.../bicicletas-electricas-57942549` | 200 | **borrado** (`errorCode=cant-see-deleted-ad`, sin `AdType`) | — | no parseable |
| `.../bicicleta-electrica-56880922` | 200 | activo | 2026-10-04T17:10:01Z | precio 450 |
| `.../bicicleta-electrica-plegable-verde-520-57223717` | 200 | activo | 2026-10-18T02:13:11Z | precio 520 |
| `.../bici-electrica-t-5-56776350` | 200 | **expirado** (`status=EXPIRED`) | — | precio `null`, descripción `null` |
| `.../bicicleta-electrica-tronluk-plegable-20-57908642` | 200 | activo | 2026-10-20T14:04:13Z | precio 740 |
| `.../bicimotos-electricas-challenger-corleone-56524453` | 200 | activo | 2026-09-16T12:08:20Z | precio 780 |

Conclusión del punto: **mirar solo el código HTTP no basta**. Los anuncios borrados devuelven 200 con `errorCode=cant-see-deleted-ad`; los expirados devuelven 200 con `status=EXPIRED`. De 10, 7 están activos, 2 borrados y 1 expirado. Actualizados hoy (2026-10-20): 3; el resto entre el 16-09 y el 18-10.

### 4. Detalle de 5 anuncios que cargan

Se descargaron y parsearon en memoria (sin escribir `cache_detalle`). De las 10, **8/10** tienen `AdType`; las 2 borradas no. De las 8, 7 están activas y 1 expirada.

| Anuncio | Precio | Provincia/Municipio | Actualizado | Descripción | Campos técnicos extraídos |
|---|---:|---|---|---:|---|
| VELOCE PLUS (pd) | 970 | 1 / 37 | 2026-10-20 | 291 chars | 600 W, 48 V, 25 Ah, 60 km, litio |
| Bicicleta eléctrica (57740725) | 1000 | 1 / 36 | 2026-09-28 | 329 chars | 1000 W, 48 V, 22 Ah, 80 km |
| Portobello | 550 | 1 / 36 | 2026-10-20 | 233 chars | 400 W, 48 V, 12 Ah, 40 km, litio |
| Bicicleta eléctrica nueva | 450 | 1 / 38 | 2026-10-04 | 50 chars | sin motor/voltaje; 140 km |
| Tronluk plegable 20” | 740 | 1 / 42 | 2026-10-20 | 488 chars | 720 W, 48 V, 12 Ah, 32 km, 32 km/h, frenos de disco |

Los campos clave (`titulo`, `precio`, `provinceId`, `municipalityId`, `updatedOnByUser`) se extraen en los 7 activos y coinciden con el final, salvo el expirado T5: el final guarda 520 y la página actual ya no tiene precio. En los 2 borrados no hay detalle que extraer. Si se usara `procesar_detalles` con la caché de bicis vacía, los 300 registros caerían como `detalle_faltante` (`revolico.py:1119-1160`).

### 5. Contador de peticiones y coste de 300 detalles

- `_contador_peticiones` es una variable **global de módulo**, inicializada a 0 en cada proceso (`revolico.py:28`).
- `reset_contador()` solo se ejecuta si se llama a mano (`revolico.py:33-35`); no hay persistencia en disco.
- `descargar_detalle` incrementa el contador **solo tras una descarga correcta** (`revolico.py:152`); el reintento por 429 no incrementa aparte, así que las peticiones HTTP reales pueden ser más que el contador.
- Límite: `MAX_PETICIONES=150` (`config.yaml:19`, `revolico.py:26`).
- 300 detalles sin caché = **300 peticiones correctas**; a 3 s = **900 s ≈ 15 min** más latencia. Con el tope de 150 harían falta **al menos 2 procesos/sesiones** (o subir el límite). Para bicis y patinetes serían 300 cada uno; 300 motos también, aunque ya hay 350 detalles cacheados (esos consumen 0).
- `procesar_detalles` **no descarga**: solo lee `cache_detalle/<categoria>/detalle_<id>.html`. No hay orquestador/CLI para bajar detalles.

---

## B. Estado de los datos

### 6. `provinceId` fuera de La Habana y mapeo a nombres

| Categoría | Total | `provinceId != 1` | Nulos |
|---|---:|---:|---:|
| Motos | 966 | 12 | 0 |
| Bicis | 2049 | 141 | 0 |
| Patinetes | 314 | 15 | 0 |

Total fuera de La Habana: **168** (12 + 141 + 15); todos tienen `provinceId` no nulo.

No existe un mapeo `provinceId → nombre` persistido en el proyecto. El mapeo se construye **en tiempo de ejecución** desde el HTML cacheado:

- `extraer_catalogos(html)` lee `ProvinceType:*` y `MunicipalityType:*` del `__APOLLO_STATE__` y devuelve `{"provincias": {id: nombre}, "municipios": {id: nombre}}` (`revolico.py:701-715`).
- `resolver_ubicacion(provinceId, municipalityId, catalogos)` usa ese diccionario (`revolico.py:717-728`).
- `PROVINCIAS` (`revolico.py:643`) y `MUNICIPIOS` (`revolico.py:681`) son **nombre → nombre canónico**, no `id → nombre`; `MUNICIPIOS` tiene 167 entradas.
- Los finales de 8 campos conservan `provinceId`/`municipalityId` numéricos; no guardan el nombre. Sin HTML de caché no se pueden resolver los nombres desde el final solo.

### 7. Cobertura de campos en `motos_procesados.json` (326 registros)

| Campo | Con dato | % |
|---|---:|---:|
| `motor_w` | 157 | 48,2 % |
| `voltaje_v` | 165 | 50,6 % |
| `autonomia_km` | 275 | 84,4 % |
| `tipo_bateria` | 129 | 39,6 % |
| `estado` | 50 | 15,3 % |
| `papeles` | 138 | 42,3 % |
| `garantia_dias` | 139 | 42,6 % |
| `vendedor_id` | 326 | 100,0 % |
| `municipio` | 326 | 100,0 % |

Los 326 son 83 completos + 243 parciales; 24 descartados. La cobertura técnica es parcial y muy desigual: `estado` (15,3 %) y `tipo_bateria` (39,6 %) son los más débiles.

### 8. Clasificadores: exclusión, combustión y contaminación

- **Títulos que aceptan más de un clasificador: 6**, todos en motos. Ejemplos: “Bicicletas eléctricas y bicimotos…”, “Bicicletas eléctricas motor de 350 W”, “Venta de bici motos eléctricas”, “Se venden motos y bicicletas eléctricas”. La causa es que `es_moto_electrica` y `es_bici_electrica` aceptan “bici/moto” en el mismo título; `clasificar_listado` evalúa moto → bici → patinete y se queda con el primero (`revolico.py:505-510`).
- **Títulos con pinta de combustión:** 3 coinciden con los términos pedidos, pero solo **1** es realmente de combustión por “cc”: “Moto electrica 150cc otalika”. Los otros dos son falsos positivos por autonomía: “…150 KM de Autonomía” y “…Autonomía de 125 km”. No hay “gasolina”, “suzuki” ni “yamaha” en los finales.
- **`motos_procesados` con títulos de bici/patinete: 2** — “Bici motos eléctricas” y “BICICLETAS ELÉCTRICA WARYOA…”. Son contaminación del sample de motos por el mismo solapamiento.
- Bicis y patinetes no tienen títulos con pinta de combustión.

### 9. “Maf” y cobertura de marca/modelo

“Maf” aparece en **94 títulos**: 76 motos, 3 bicis y 15 patinetes. Ejemplos: “Motico MAF de paseo con Mini-Sidecar”, “Bicicleta eléctrica marca MAF”, “Patineta eléctrica MAF”.

No es un artefacto puro del diccionario: el token aparece en los anuncios. Pero el campo `marca` se asigna por una lista manual (`_MARCAS`, `revolico.py:932-960`; `maf` en `:944`), así que la canonización es del diccionario. No hay fuente en el repo que confirme que “MAF” sea una marca registrada; podría ser marca/ensamblador local. La evidencia disponible solo permite decir que es un nombre recurrente en los títulos.

Cobertura de marca/modelo:

| Categoría | Marca | Modelo | Marcas distintas |
|---|---:|---:|---:|
| Motos | 525/966 (54,3 %) | 338/966 (35,0 %) | 21 |
| Bicis | 167/2049 (8,2 %) | 107/2049 (5,2 %) | 13 |
| Patinetes | 23/314 (7,3 %) | 19/314 (6,1 %) | 5 |

El diccionario es moto-céntrico: fuera de motos, `marca` y `modelo` no son fiables.

### 10. Los 3 precios “históricos”

En `data/processed/versiones/limpio_excepciones.json`, dentro de `motos`:

| URL | Precio conservado | Motivo |
|---|---:|---|
| `.../motico-electrica-jmd-57954969` | 650 | `precio_historico` |
| `.../moto-electrica-57968312` | 290 | `precio_historico` |
| `.../moto-electrica-vedca-n3-57942983` | 1620 | `precio_historico` |

Los 3 están en `precios` y en `motivos` como `precio_historico`. **No se guarda el precio anterior**: el archivo solo conserva el valor final. El `handoff` menciona “750→650, 2900→290, 1590→1620”, pero esa secuencia no está en el artefacto actual. Bicis y patinetes: 0 precios históricos. `precio_historico` es una etiqueta de motivo, no un campo aparte de los finales.

### 11. Embudo: reconciliación

| Etapa | Motos | Bicis | Patinetes | Suma | Unión global |
|---|---:|---:|---:|---:|---:|
| Crudos únicos | 2939 | 217 | 109 | 3265 | **3256** |
| Clasificados (partición por archivo) | 538 | 613 | 149 | 1300 + 1965 desc. = 3265 | 3256 |
| Elegibles v2 | 1198 | 2861 | 373 | 4432 | **4431** |
| Reglas de limpieza | 921 | 2058 | 316 | 3295 | **3294** |
| Final limpio | 966 | 2049 | 314 | 3329 | **3328** |

- **Crudos:** 9 URLs aparecen en más de una categoría; por eso la suma 3265 y la unión 3256. El “total único” de `data/README.md` es una suma por archivo, no una unión global.
- **Clasificados:** 538/613/149 + 1965 = 3265 es la suma de las particiones de los 3 archivos; cada archivo es excluyente, pero entre archivos hay 9 duplicados. Las cifras “nativas” 537/176/82 son los conteos por archivo (motos, bicis y patinetes respectivamente), no una etapa distinta.
- **Por qué v2 supera a crudos:** v2 no sale solo de los listados oficiales; reclasifica **todas** las páginas de `cache_html` (incluidas las búsquedas) con los 3 clasificadores. Los listados tienen 3256 únicos; las búsquedas, 4810; la intersección es 873. De las 4431 URLs de v2, **3139 no están en crudos y todas están en búsquedas**. El solapamiento entre tipos es mínimo: solo **1 URL** está en 2 tipos. La explicación de `data/README.md` (“un anuncio puede entrar en varios tipos”) no es la causa principal; la causa es la ampliación por búsquedas.
- **Clasificación cruzada por carpeta:** v2 aplica los 3 clasificadores a cada carpeta. Ejemplo (con solapamiento entre carpetas): de las 2861 bicis v2, 445 aparecen en la carpeta `motos`, 2774 en `bicis` y 19 en `patinetes`; de las 1198 motos, 1145 aparecen en `motos`, 59 en `bicis`, 17 en `patinetes`.
- **Por qué el final no coincide con las reglas:** `limpiar_finales.py` aplica la tabla de excepciones. Motos: +86 `keep` −41 `drop` → 921 + 86 − 41 = **966**. Bicis: +88 −97 → 2058 + 88 − 97 = **2049**. Patinetes: +7 −9 → 316 + 7 − 9 = **314**. No hay otra diferencia: los conjuntos `final − reglas` y `reglas − final` son exactamente esos `keep`/`drop`.
- **Final:** 3329 por suma, 3328 por unión; la URL `.../patinetas-halcon-55181089` está a la vez en bicis y patinetes.

La reconciliación exacta ya se puede hacer; el “[pendiente]” de `data/README.md` quedó resuelto con estas cifras.

---

## C. Cobertura frente a los objetivos

### 12. Detalle de La Habana: 300 por tipo

| Tipo | Con detalle | Faltan para 300 | Caché de detalle | Fecha |
|---|---:|---:|---:|---|
| Motos | **326** (todos `ubicacion=La Habana`) | **0** (sobran 26) | 350 HTML | 2026-10-08/09 |
| Bicis | **0** | **300** | 0 | — |
| Patinetes | **0** | **300** | 0 | — |
| Motos de combustión | **0** | **300** | 0 | — |

- “Hoy” (2026-10-20): **0 detalles nuevos**. Los 326 procesados son del 2026-10-09 y la caché es del 2026-10-08; no se ha vuelto a procesar nada hoy.
- Las 326 motos son todas de La Habana (`ubicacion` = “La Habana” en el 100 %). No faltan motos para 300; hay 26 de más.
- Bicis y patinetes no tienen ni un detalle descargado: `cache_detalle/bicis` y `cache_detalle/patinetes` están vacíos.
- Motos de combustión: no hay detalles dedicados. En `motos_procesados` hay 2 títulos con “pinta” de combustión, pero ambos son anuncios eléctricos: “Moto electrica 150cc otalika” y “MAOX … 125 km” (falso positivo por autonomía). No hay caché de motos de gasolina.
- La muestra de motos es 350 detalles → 326 válidos (83 completos + 243 parciales; 24 descartados), según `handoff.md:54-55`.

### 13. Fuentes en `stakeholders`

Fuentes distintas utilizables: **6 organizaciones / 12 documentos**.

| Organización | Documentos |
|---|---|
| Gaceta Oficial | `decreto_163_2026.html`, `resolucion_175_2026.html`, `gaceta_65_2026.pdf`, `gaceta_83_2026.pdf`, `resolucion_340_ficha.html` (+ `decreto_163_ficha.html`, duplicado de la misma URL) |
| Aduana | `aduana_portada.html` (+ el texto derivado `resolucion_340_anexos.txt`) |
| MFP | `mfp_portada.html` |
| MINDUS | `mindus_marco.html`, `mindus_vedca.html` |
| Cubadebate | `cubadebate_flexibilizaciones.html`, `cubadebate_mesa_redonda_vehiculos.html` |
| Granma | `granma_importaciones_octubre.html` |

- `resolucion_340_anexos.txt` es derivado de `gaceta_83_2026.pdf`, no una fuente independiente.
- `decreto_163_ficha.html` es duplicado de `decreto_163_2026.html`.
- `mitrans_faq.html` falló por SSL (`CERTIFICATE_VERIFY_FAILED`) y no se reintentó; está documentado en `_fuentes.md:10`.
- `ONCUBA.md` y `Postdata.club.md` existen pero tienen **0 bytes**: no son fuentes utilizables.
- `data/raw/stakeholders/tiendas/`, `importadoras/` y `talleres/` están **vacíos**: 0 fichas de stakeholders.
- `Facebook.md` tiene 1 byte (un salto de línea) y `Telegram.md` 0 bytes: no hay datos de redes.

Faltantes para 30: **24 organizaciones** o **18 documentos** si se cuenta documento; y **30 fichas** si el objetivo son tiendas/importadoras/talleres. En cualquier lectura, la cobertura de stakeholders es mínima.

### 14. Entrevistas

- `data/raw/interviews/registro.md`: 30 filas `user_001`…`user_030`, **0 con fecha, consentimiento, transcripción o JSON**. El control de cobertura dice 0/30 en todos los indicadores.
- `data/raw/interviews/usuarios/`: **no existe**.
- `data/raw/interviews/transcripciones.md`: 14 bytes, contenido ` en otter.ai` (sin URL completa ni transcripción).
- `data/raw/interviews/preguntas.md`: 5.060 bytes; es la guía, no una entrevista.
- No existe `data/processed/entrevistas_usuarios.json`.

Cobertura: **0/30 entrevistas**; faltan 30. El registro preveía empezar la semana del 12 de octubre de 2026 (`registro.md:4`); a 20 de octubre sigue en 0.

---

## D. Salud del repositorio

### 15. `verificar_rutas.py`

`python3 src/scripts/verificar_rutas.py` revisa 197 rutas y devuelve **6 rotas** (exit 1):

1. `config.yaml:9` → `data/exports` (no existe; la carpeta real de salida no está creada).
2. `data/raw/interviews/registro.md:16` → `data/processed/entrevistas_usuarios.json` (no existe).
3. `opencode/journal.md:25` → `prompts/sessions.md` (ruta antigua).
4. `opencode/journal.md:53` → `data/raw/institutional/` (nombre antiguo; la carpeta actual es `data/raw/stakeholders/institucionales/`).
5. `opencode/journal.md:97` → `notebooks/02–04` (guion largo y nombre antiguo).
6. `opencode/journal.md:97` → `data/processed/final/motos_` (ruta truncada).

### 16. Teléfonos en JSON

Se escanearon los **34 JSON** de `data/` (no hay JSON en `data/raw/`). **32 archivos** contienen números de 8 dígitos que empiezan por 5 o 7 en `titulo` o `descripcion`.

| Carpeta | Archivos | Teléfonos |
|---|---:|---:|
| `data/processed/final/` | 6 | `motos_completos` 8, `motos_final_limpio` 13, `motos_parciales` 27, `motos_procesados` 35, `bicis_final_limpio` 29, `patinetes_final_limpio` 2 |
| `data/processed/clasificados/` | 3 | motos 60, bicis 6, patinetes 2 |
| `data/processed/listados_crudos/` | 3 | motos 60, bicis 6, patinetes 2 |
| `data/processed/muestras/` | 3 | motos 6, bicis 7, patinetes 1 |
| `data/processed/versiones/` | 17 | entre 1 y 32 por archivo (p. ej. `bicis_final_v2` 32, `bicis_final_v3` 32) |

Los finales vigentes no están anonimizados: 13 motos, 29 bicis y 2 patinetes todavía tienen teléfonos. Esto contradice `AGENTS.md:81` (“Anonimizar teléfonos de vendedores en los datos procesados”). Los 2 JSON sin teléfonos son, previsiblemente, los de control (`limpio_excepciones.json` y `verificacion_limpio.json`).

### 17. `config.yaml`: claves usadas y obsoletas

Solo se usan 4 claves de `scraping` (`revolico.py:23-26`): `user_agent`, `delay_segundos`, `delay_429_segundos` y `max_peticiones`.

| Clave | ¿Se usa? | Observación |
|---|---|---|
| `proyecto.*` | No | Metadatos sin consumo por el código. |
| `rutas.*` | No | Las rutas están hardcodeadas en `revolico.py`. `exports` apunta a `data/exports` (no existe); `reports` apunta a `reports/` (la real es `storytelling/reports/`); `graphs` tampoco se usa. |
| `max_paginas_por_url: 10` | No | Hay 30 páginas por listado oficial en caché. |
| `timeout_segundos: 30` | No | El timeout está hardcodeado como `30` (`revolico.py:74`). |
| `economia.tasa_cup_por_usd` / `fecha_tasa` | No | No hay conversión CUP/USD en el pipeline. |
| `analisis.max_anuncios_por_tipo: 30` | No | Las muestras son de 300/350. |
| `analisis.clustering.*` | No | No hay K-Means/TF-IDF en `src/` ni en notebooks. |

La configuración describe un pipeline distinto del que existe: promete 10 páginas, 30 anuncios, tasa CUP y clustering que el código no aplica.

### 18. Afirmaciones falsas o desactualizadas

| Archivo:línea | Afirmación | Realidad |
|---|---|---|
| `README.md:14` | Datos de stakeholders de “tiendas, importadoras, talleres e instituciones” | `tiendas/`, `importadoras/` y `talleres/` están vacíos; solo hay instituciones. |
| `README.md:35` y `:51` | “Clustering” / K-Means sobre TF-IDF + variables numéricas | No hay código de clustering ni notebook que lo use; `sklearn` no se importa en `src/`. |
| `README.md:39` | “30 motos, bicicletas y patinetes” como muestra | Los finales tienen 966/2049/314; 30 era el mínimo, no la muestra actual. |
| `README.md:40` | “30 usuarios” | 0/30 entrevistas. |
| `README.md:46` | Análisis documental de ONCUBA y Postdata.club | Ambos archivos tienen 0 bytes. |
| `README.md:62` | Anuncios entre el 24-09 y el 08-10-2026 | Hoy se verificaron anuncios actualizados el 18-10 y el 20-10; el rango está desactualizado. |
| `AGENTS.md:5` | “30 entrevistas a usuarios” | 0/30; es una meta, no un hecho. |
| `AGENTS.md:9` | `data/raw/stakeholders/` → tiendas, importadoras, talleres | Los 3 directorios están vacíos. |
| `AGENTS.md:10` | `data/raw/interviews/usuarios/` → transcripciones | El directorio no existe. |
| `AGENTS.md:11` | `data/raw/web/` → redes sociales | `Facebook.md` 1 byte y `Telegram.md` 0 bytes. |
| `AGENTS.md:19` | Campos compartidos: `precio`, `moneda`, `tipo_vehiculo`, `es_electrica`, `uso_principal`, `canal_compra` | El final tiene 8 campos y usa `precio_usd`; no existen `moneda`, `tipo_vehiculo`, `es_electrica`, `uso_principal` ni `canal_compra`. |
| `AGENTS.md:55` y `:68` | `storytelling/historia.md` | No existe; hay `outline.md` y `reports/final_report.md` (0 bytes). |
| `AGENTS.md:56` | “`src/`: … y notebooks/” | Los notebooks están en `notebooks/` en la raíz, no en `src/`. |
| `AGENTS.md:57` | Esquemas en `data/esquemas/` | Están en `docs/schemas/`. |
| `AGENTS.md:81` | Anonimizar teléfonos en datos procesados | 32 JSON, incluidos los finales, conservan teléfonos. |
| `data/README.md:21` | “Crudos (únicos) … 3265” | Suma 3265; unión global 3256 (9 URLs en más de una categoría). |
| `data/README.md:23` | “Partición excluyente” con total 3265 | Cada archivo es excluyente; entre archivos hay 9 duplicados. |
| `data/README.md:24` y `:35-36` | v2 = 4432 y “supera a crudos porque un anuncio puede entrar en varios tipos” | Unión v2 = 4431; solo 1 URL está en 2 tipos. Las 3139 URLs extra vienen de búsquedas, no de solapamiento. |
| `data/README.md:31` | “`total_unicos` es la base de 3265” | Es la suma de únicos por archivo; la unión global es 3256. |
| `data/README.md:33-34` | 537/176/82 son “traza” y no la partición total | Son los conteos nativos de cada archivo (motos/bicis/patinetes); la partición agregada es 538/613/149. La nota confunde más que aclara. |

### 19. Archivos vacíos o solo con encabezado

| Archivo | Tamaño | Estado |
|---|---:|---|
| `storytelling/reports/final_report.md` | 0 B | vacío |
| `data/raw/web/Telegram.md` | 0 B | vacío |
| `data/raw/stakeholders/institucionales/ONCUBA.md` | 0 B | vacío |
| `data/raw/stakeholders/institucionales/Postdata.club.md` | 0 B | vacío |
| `data/raw/web/Facebook.md` | 1 B | solo un salto de línea |
| `data/raw/interviews/transcripciones.md` | 14 B | solo ` en otter.ai` |
| `docs/decisions.md` | 162 B | título + una frase (“Aquí se registrarán…”) |
| `docs/limitations.md` | 181 B | título + una frase |
| `docs/methodology.md` | 193 B | título + una frase |
| `docs/sources.md` | 142 B | título + una frase |

También están vacíos los directorios `data/raw/stakeholders/{tiendas,importadoras,talleres}/`. No existe `storytelling/historia.md`. En cambio, `storytelling/graphs/preliminar/` sí tiene 12 PNG y `docs/schemas/` tiene 4 esquemas válidos.

### 20. `git status` y último commit

- `git status --short`: **sin cambios** (0 líneas).
- Rama: `main`.
- Último commit: `3d7431a estructura: renombrar previos→versiones, añadir READMEs, Makefile, hooks y fuentes institucionales`.
- Ese commit incluye la reestructuración (`previos` → `versiones`), los READMEs, `Makefile`, `.githooks/`, `_fuentes.md` y las 13 fuentes institucionales.
- No hay nada sin commitear antes de este informe. `opencode/diagnostico.md` queda como archivo nuevo sin commitear, porque el diagnóstico no hace commits.

---

## E. Tabla resumen

| # | Ítem | Estado |
|---:|---|---|
| 1 | `make test` | **Funciona** (4/4), con cobertura limitada |
| 2 | URLs de búsqueda por vehículo | **Funciona** (14 familias, 148 HTML), con redundancia y páginas vacías |
| 3 | 10 URLs aleatorias de bicis | **Está roto o incompleto**: 10/10 HTTP 200, pero 2 borradas y 1 expirada; el HTTP no basta |
| 4 | Detalle de 5 anuncios | **Está roto o incompleto**: 8/10 parsean; la expirada pierde precio/descripción |
| 5 | Contador de peticiones | **Funciona** (global, 150), pero no persiste y 300 detalles exigen 2 sesiones |
| 6 | `provinceId` fuera de La Habana y mapeo | **Está roto o incompleto**: 168 fuera; no hay mapeo persistido id→nombre |
| 7 | Cobertura de campos técnicos | **Está roto o incompleto**: 15,3 %–84,4 % según campo |
| 8 | Clasificadores | **Está roto o incompleto**: 6 títulos multi-clase y 2 motos contaminadas con bicis |
| 9 | “Maf” y marca/modelo | **Está roto o incompleto**: 94 títulos, canonización manual, cobertura 7,3 %–54,3 % |
| 10 | Precios históricos | **Funciona** (3), pero solo guarda el valor final, no el anterior |
| 11 | Embudo | **Funciona** (reconciliado); la explicación de `data/README.md` es incorrecta |
| 12 | Detalle de La Habana (300 por tipo) | **Falta**: motos 326/300; bicis 0/300; patinetes 0/300; combustión 0/300 |
| 13 | Fuentes de stakeholders | **Falta**: 6 organizaciones/12 documentos; 0 tiendas/importadoras/talleres |
| 14 | Entrevistas | **Falta**: 0/30 |
| 15 | `verificar_rutas.py` | **Está roto o incompleto**: 6 rutas rotas |
| 16 | Teléfonos en JSON | **Está roto o incompleto**: 32/34 archivos, incluidos los finales |
| 17 | `config.yaml` | **Está roto o incompleto**: solo 4 claves se usan; el resto está obsoleto o contradice el código |
| 18 | Afirmaciones de README/AGENTS/data README | **Está roto o incompleto**: varias falsas o desactualizadas |
| 19 | Archivos vacíos o solo encabezado | **Falta**: 10 archivos y 3 directorios |
| 20 | Git | **Funciona**: limpio; último commit `3d7431a` |
