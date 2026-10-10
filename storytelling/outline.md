# [Título provisional] — Mercado de vehículos eléctricos en La Habana

**Autora:** Dagmary [apellidos]
**Asignatura:** [asignatura]
**Fecha:** [fecha]

## Introducción
- **Contexto:** situación del transporte en La Habana y aparición de motos, bicis y patinetes eléctricos como alternativa.
- **Pregunta de investigación:** qué se pregunta el estudio sobre este mercado.
- **Motivación:** por qué se elige el tema y a quién puede servir.

## Bloques de desarrollo
1. **La oferta de motos eléctricas** — qué motos eléctricas se anuncian y con qué volumen (marcas y modelos).
2. **Precios y segmentación de motos** — rangos de precio y segmentos que aparecen según marca y municipio.
3. **Bicicletas y patinetes eléctricos** — misma lectura de oferta y precios para bicis y patinetes, al mismo nivel que las motos (son ~71% del dataset limpio).
4. **Sesgo geográfico del dataset** — todos los anuncios son de La Habana y esto condiciona qué se puede afirmar del mercado.
5. **Características técnicas y prestaciones** — motor, batería, autonomía y velocidad, disponibles solo para motos (83 completos + 243 parciales); bicis y patinetes no tienen estos campos porque no se descargaron sus detalles.
6. **La demanda: usuarios de eléctricos** — quién compra, por qué y cómo es la experiencia de uso (basado en entrevistas).
7. **El ecosistema de compra: tiendas, importadoras y talleres** — dónde y cómo se compran y se reparan los vehículos (basado en el registro de stakeholders).
8. **Síntesis del mercado** — integración de la oferta, la demanda y el ecosistema de compra.

## Conclusión o cierre
- Cierre del trabajo: qué se ha mostrado y qué queda abierto.

## Metodología
- Enfoque, fuentes (Revolico como fuente principal de oferta), criterios de limpieza y validación, y limitaciones.

## Proceso de los datos
- Del scraping al dataset: descarga ética, caché, clasificación, deduplicación y verificación.
- **Hallazgo metodológico: clasificación de Revolico** — las categorías oficiales de la plataforma infravaloraban la oferta (la subcategoría oficial de bicis tenía 151 anuncios frente a 2.050 por búsquedas de texto, con el mismo patrón en motos y patinetes).
