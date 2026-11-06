# Prompts recuperados del disco corrupto

**Total:** 18

---

### Prompt 1

> Corregido y reprocesado. No hice peticiones nuevas: usé la caché HTML. Los 4 archivos conservan sus IDs y sus conteos.
> 
> ## Cambio aplicado
> 
> - `src/scrapers/revolico.py:367`: nueva `normalizar_guiones()` que convierte en espacio cualquier guion Unicode de categoría `Pd` (hyphen, non-breaking hyphen, figure dash, en dash, em dash, horizontal bar, fullwidth hyphen, etc.) y el signo menos `U+2212`.
> - Se aplica **antes** de `NFKD`/ASCII en `_normalizar_titulo()` (`revolico.py:377`).
> - `src/scrapers/moto_combustion.py:196`: `_normalizar()` usa la misma función.
> - Test de regresión en `tests/test_smoke.py:57` con `70–80`, `6–8`, `10‑20`, `4—5`, `1‒2`, `3―4`, `5－6` y `−5`.
> - Bicis sigue con **29 campos**: quité el `kilometraje_km` que añadía el parser actual para no cambiar el conjunto de campos s [...]

### Prompt 2

> Ya está aplicado y reprocesado. Verifiqué el estado actual del árbol: `normalizar_guiones()` convierte en espacio cualquier guion `Pd` y `U+2212` antes de `NFKD`/ASCII, y `moto_combustion._normalizar()` la reutiliza. `make test` → **5 passed**.
> 
> ## Antes / después
> 
> | Archivo | `autonomia_km` fusionados | `velocidad_max_kmh` fusionados | `tiempo_carga_horas` fusionados |
> |---|---:|---:|---:|
> | Eléctricas | 1 → **0** | 0 → 0 | 0 → 0 |
> | Combustión | N/A | 0 → 0 | N/A |
> | Bicis | 16 → **0** | 0 → 0 | 10 → **0** |
> | Patinetes | 12 → **0** | 0 → 0 | 0 → 0 |
> 
> Cambios en los campos pedidos: eléctricas 3, combustión 0, bicis 27, patinetes 12. La velocidad no cambió porque no tenía valores fusionados.
> 
> ## Ejemplos
> 
> | ID | Archivo | Campo | Antes | Después | Texto |
> |---|---|---|---:|---:|---|
> | `57 [...]

### Prompt 3

> Build: Ahora vamos a terminar de recolectar las motos de combustión. Haz otra tanda de hasta 150 peticiones nuevas para los candidatos que quedan. Si no llegas a 300 válidos en esta sesión, guarda el progreso y avísame para continuar. Al terminar, dime cuántos válidos tienes en total. 

### Prompt 4

> No llegué a 300. Hice **150 peticiones nuevas** en total: 60 en una primera tanda que cortó el timeout (la caché sí quedó guardada) y 90 en la segunda.
> 
> ## Resultado
> 
> | Métrica | Total |
> |---|---:|
> | Válidos en el dataset | **196** |
> | Outliers: motos reales con precio inválido | **7** |
> | Motos reales detectadas (dataset + outliers) | **203** |
> | Descartados | **148** |
> | Candidatos totales | **694** |
> | Caché de detalle de combustión | **732** HTML |
> | Faltan para 300 en el dataset | **104** |
> 
> Los 7 outliers son motos reales, pero con precio mal extraído: la Honda CBR 600 `57302018` a 8500 USD y seis anuncios con precio `1 USD`.
> 
> ## Limpieza adicional
> 
> El clasificador estaba aceptando accesorios que mencionaban “4T/cc/moto” y anuncios de inmuebles que incluían una moto. Endurecí el filt [...]

### Prompt 5

> Listo. Cerré la recolección de combustión:
> 
> - **325 válidos** en `motos_combustion_procesadas.json` → objetivo de 300 superado.
> - **9 outliers** reales por precio inválido (1 a 8500 USD y 8 a 1 USD).
> - **191 descartados**; **694 candidatos**; **882 HTML** en caché.
> - Usé **150 peticiones nuevas** en esta continuación (75 + 75), sin más descargas pendientes.
> - Limpié aceites, retenes, milleros y otras piezas; los 325 procesados pasan el filtro actual.
> - `make test` → **5 passed**. README, journal y handoff actualizados. Sin commit.
> 
> Pendiente: revisar a mano los 9 outliers y el kilometraje `240280` de `58026629`, y decidir correcciones de parseo antes del informe.

### Prompt 6

> Build: Vamos a arreglar el regex de extracción técnica en `src/scrapers/revolico.py` (función `extraer_campos_tecnicos`). 
> 
> 1. **Motor**: acepta "Wats", "Watts", "W". Patrón: r"\b(\d{1,4})\s*(?:w(?:atts?)?)\b"
> 2. **Voltaje**: acepta "Volt", "Voltios", "V". Patrón: r"\b(\d{1,3})\s*(?:v(?:olt(?:ios)?)?)\b"
> 3. **Amperaje**: acepta "Amp", "Amperios", "Ah". Patrón: r"\b(\d{1,3}(?:\.\d+)?)\s*(?:ah|amp(?:erios)?)\b"
> 4. **Batería**: reconoce "GEL", "LiFePO4", "Lithium" (además de litio y plomo).
> 5. **Velocidad**: reconoce "km/h", "km x hora", "kmh", "kilómetros por hora". Patrón: r"(\d{1,3})\s*(?:km\s*(?:/|x|por)\s*h(?:ora)?|kmh)"
> 6. **Peso**: busca "Peso", "Peso total", "Carga máxima", "Soporta hasta". Si la unidad es "lb" o "libras", convierte a kg dividiendo entre 2.204.
> 7. **Autonomía con rang [...]

### Prompt 7

> Listo. Reprocesé los 3 JSON desde caché, sin peticiones nuevas, conservando campos, orden e IDs.
> 
> ### Motos eléctricas (326)
> | Campo | Antes | Después |
> |---|---:|---:|
> | motor_w | 48.2% | 76.1% |
> | voltaje_v | 50.6% | 81.9% |
> | amperaje_ah | 53.1% | 80.1% |
> | tipo_bateria | 39.6% | 49.7% |
> | autonomia_km | 85.0% | 85.0% |
> | velocidad_max_kmh | 40.8% | 41.1% |
> | peso_kg | 0.9% | 1.2% |
> | estado | 15.3% | 16.3% |
> | papeles | 42.3% | 42.3% |
> 
> ### Bicicletas (414)
> | Campo | Antes | Después |
> |---|---:|---:|
> | motor_w | 59.7% | 64.7% |
> | voltaje_v | 60.1% | 67.4% |
> | amperaje_ah | 47.1% | 54.8% |
> | tipo_bateria | 34.8% | 36.2% |
> | autonomia_km | 63.0% | 64.0% |
> | velocidad_max_kmh | 36.2% | 37.0% |
> | peso_kg | 0.7% | 7.5% |
> | estado | 20.5% | 21.0% |
> | papeles | 8.9% | 8.9% |
> | plegable | 0.0% [...]

### Prompt 8

> Plan: Vamos a identificar la basura antes de borrarla. No modifiques nada.
> 
> Revisa los 3 archivos procesados (eléctricas, bicis, patinetes) y hazme una lista exacta de los registros que cumplen alguna de estas condiciones:
> 1. El título contiene palabras de accesorios (cargador, batería, bocina, generador, repuesto, cubierta, toldo, etc.).
> 2. El título no contiene ninguna palabra de vehículo (moto, bici, patinete, scooter, etc.).
> 3. El título dice que es un vehículo diferente al del archivo (ej: "bicicleta" en el archivo de motos, "bicicleta" en el de patinetes).
> 
> Para cada registro, dame: id, título, archivo y el motivo por el que lo descartarías. Muéstrame la lista completa (o los primeros 20 si hay muchos). 

### Prompt 9

> Plan: Muéstrame los 9 registros de `motos_combustion_outliers.json`. Para cada uno, dame el ID, el título, el precio actual y un fragmento de la descripción donde se mencione el precio (si es que se menciona). No modifiques nada. 

### Prompt 10

> Limpieza completada.
> 
> - `motos_electricas_procesadas.json`: **321** registros (antes 326; se quitaron 5).
> - `bicis_procesados.json`: **407** registros (antes 414; se quitaron 7).
> - `patinetes_procesados.json`: **332** registros (antes 335; se quitaron 3).
> 
> Archivo creado: `data/processed/final/descartes.json` con **15 registros**: 13 con motivo `basura` y 2 con motivo `mal_clasificado`. Cada entrada conserva el registro completo, archivo de origen, título y motivo.
> 
> Verificado que no se tocó ningún otro ID, que se mantienen campos y orden, y que los dudosos/falsos positivos siguen intactos. `make test` → **6 passed**. Respaldo previo en `/tmp/icd_limpieza_before/`.

### Prompt 11

> No modifiqué nada. Estos son los 9 registros de `motos_combustion_outliers.json`:
> 
> 1. **ID:** `57302018`  
>    **Título:** “Vendo o cambio por auto o recojo moto menor precio negotiable .”  
>    **Precio actual:** `8500 USD`  
>    **Mención de precio:** la descripción no contiene una cifra. Solo dice:  
>    > “Vendo , o recojo otra moto menor y vuelto o cambio por auto .”
> 
> 2. **ID:** `56135611`  
>    **Título:** “MOTO DE COMBUSTION”  
>    **Precio actual:** `1 USD`  
>    **Mención de precio:** no menciona precio. Solo formas de pago:  
>    > “FORMAS DE PAGO USD, EUR, ZELLE, MN”
> 
> 3. **ID:** `56412008`  
>    **Título:** “MOTO DE GASOLINA”  
>    **Precio actual:** `1 USD`  
>    **Mención de precio:** solo una referencia genérica, sin cifra:  
>    > “¡Contáctanos y recibe actualización constante de modelo [...]

### Prompt 12

> Build: Vamos a cerrar los outliers de combustión. 
> 
> 1. Los 9 registros de `motos_combustion_outliers.json` se descartan. 
> 2. Muévelos al archivo `descartes.json` (que ya existe) con el motivo "listado_multiple" (para los que tienen varios precios) o "sin_precio_real" (para los que no tienen precio explícito). 
> 3. El archivo `motos_combustion_outliers.json` debe quedar vacío (solo un array vacío `[]`).
> 4. Al terminar, dime cuántos registros quedan en `motos_combustion_procesadas.json` (deberían ser 316) y confirma que outliers está vacío. 

### Prompt 13

> Plan: Vamos a hacer la auditoría final de los 4 archivos procesados antes de generar los de 300.
> 
> Revisa motos_electricas_procesadas.json, motos_combustion_procesadas.json, bicis_procesados.json y patinetes_procesados.json.
> 
> Para cada archivo, dame:
> 1. Total de registros.
> 2. Porcentaje de campos técnicos llenos (motor/cc, autonomía, batería, etc.).
> 3. Cuántos registros tienen precios fuera de rango (menores a 100 o mayores a 5000 USD).
> 4. Cuántos registros tienen títulos duplicados o IDs duplicados.
> 5. Si hay algún registro que siga siendo claramente un accesorio (cargador, batería suelta, etc.) o un vehículo mal clasificado.
> 6. Muéstrame 5 títulos aleatorios de cada archivo (semilla 42) para verificar visualmente que son del vehículo correcto. 

### Prompt 14

> Hecho, con una aclaración importante sobre el conteo.
> 
> - Los **9 outliers** se movieron a `data/processed/final/descartes.json`:
>   - `listado_multiple`: 4 (`56542487`, `57049769`, `58230707`, `58356620`).
>   - `sin_precio_real`: 5 (`57302018`, `56135611`, `56412008`, `57236865`, `57248589`).
> - `descartes.json` queda con **24 registros** en total.
> - `motos_combustion_outliers.json` quedó vacío: **`[]`**.
> - `motos_combustion_procesadas.json` queda con **325 registros**, no 316.
> 
> La razón: los 9 IDs de outliers **no estaban dentro de `motos_combustion_procesadas.json`**. Son conjuntos disjuntos: 325 válidas + 9 outliers. Restar 9 de las procesadas habría eliminado 9 motos válidas que no forman parte de este descarte. Verifiqué que la intersección de IDs es **0**.
> 
> `make test` → **6 passed**. R [...]

### Prompt 15

> Investigación read-only terminada. No modifiqué nada.
> 
> ## Hallazgos que faltaban
> 
> - **Los 8 precios `1 USD` no se pueden reparar:** no hay precio real en la descripción. Son placeholders. Recomiendo descartarlos con motivo `sin_precio_real`.
>   - Eléctricas: `57233797`, `57578875`, `57914342`, `57955401`, `57959675`, `57968734`, `57968735`.
>   - Patinetes: `57999470`.
> - **`57642350` es un listado mixto real:** el precio `125 USD` corresponde al mini split, no a la bici; en la descripción la bici vale `500 USD`. Recomiendo descartarlo con `listado_multiple`.
> - **Los 5 “bicimoto” restantes están mal clasificados según el esquema:** `esquema_bici_electrica.json` define `bicicleta_electrica_bicimoto` y `tipo_vehiculo: bicimoto`. Recomiendo mover a bicis:
>   - `56145852`, `57278985`, `57957448`, ` [...]

### Prompt 16

> Build: Vamos a cerrar la limpieza final y generar los 4 archivos de 300. 
> 
> 1. **Descartes**: Añade a `descartes.json` los siguientes registros (búscalos en los archivos procesados y elimínalos de ahí):
>    - Eléctricas: 57233797, 57578875, 57914342, 57955401, 57959675, 57968734, 57968735, 56145852, 57278985, 57957448, 57960574, 57960812 (motivo: "precio_placeholder" o "mal_clasificado" según corresponda).
>    - Bicis: 57642350 (motivo: "listado_multiple").
>    - Patinetes: 57999470 (motivo: "precio_placeholder").
> 
> 2. **Archivos de 300**: Con los archivos ya limpios (eléctricas, combustión, bicis y patinetes), genera:
>    - `motos_electricas_300.json`
>    - `motos_combustion_300.json`
>    - `bicis_300.json`
>    - `patinetes_300.json`
>    Usa muestreo aleatorio con semilla 42. Si un archivo tiene me [...]

### Prompt 17

> Build: Vamos a limpiar la raíz del proyecto. 
> 
> 1. Crea una carpeta `tmp/` en la raíz del proyecto.
> 2. Mueve a `tmp/` los archivos `transcribir.py`, `estado_proyecto.txt` y `tree.txt`.
> 3. Añade `tmp/` al archivo `.gitignore` para que no se suba a GitHub.
> 4. Muéstrame cómo queda la raíz del proyecto (solo los archivos y carpetas de primer nivel). 

### Prompt 18

> Limpieza cerrada y archivos generados.
> 
> - `descartes.json`: **38** registros, 38 IDs únicos (+14: 8 `precio_placeholder`, 6 `mal_clasificado`, 1 `listado_multiple`).
> - Procesados restantes: eléctricas **309**, combustión **325**, bicis **406**, patinetes **331**.
> - Muestreo con `random.Random(42)`; 300 por archivo.
> - `make test`: **6 passed**.
> - Journal actualizado.
> 
> | Archivo | Registros | IDs duplicados | Precios fuera de [100, 5000] | % campos técnicos llenos |
> |---|---:|---:|---:|---:|
> | `motos_electricas_300.json` | 300 | 0 | 0 | **44.6%** |
> | `motos_combustion_300.json` | 300 | 0 | 0 | **32.9%** |
> | `bicis_300.json` | 300 | 0 | 0 | **43.1%** |
> | `patinetes_300.json` | 300 | 0 | 0 | **44.8%** |
> 
> También verifiqué que no hay precios nulos y que ningún ID descartado aparece en los archi [...]
