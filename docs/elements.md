
## Alcance del estudio

Mercado de vehículos ligeros en **La Habana**, analizado en cuatro verticales con igual peso: **motos eléctricas, motos de combustión, bicicletas eléctricas y patinetes eléctricos**.

- **Anuncios (Revolico):** instantánea del 24 de septiembre al 8 de octubre de 2026. Revolico solo muestra anuncios de los últimos ~14 días, casi todos de La Habana, y la fecha disponible es la de última actualización, no la de publicación. Los precios son **precios pedidos**, no precios de venta.
- **Entrevistas:** 30 usuarios en La Habana, semiestructuradas y anonimizadas (E01–E30).
- **Canal formal:** verificación documental de los sitios web y canales de Telegram de las entidades autorizadas. No se realizaron entrevistas presenciales a stakeholders (ver Limitación 10 del informe final).

**Fuentes:** A = Anuncios (Revolico) · E = Entrevistas (30 usuarios) · D = Documental (Gacetas Oficiales, ONEI, prensa oficial, sitios web de entidades)

---

## 1. Oferta y precios en anuncios (A)

| # | Pregunta | Fuente | Variables |
|---|---|---|---|
| 1 | ¿Qué marcas y modelos se anuncian en La Habana? | A | marca, modelo |
| 2 | ¿Cuál es el precio mediano pedido de cada tipo de vehículo (moto eléctrica, moto de combustión, bici, patinete)? | A | precio_usd, tipo_vehiculo |
| 3 | ¿Cómo varía el precio pedido según la marca? | A | precio_usd, marca |
| 4 | ¿Cómo varía el precio pedido entre municipios de La Habana? | A | precio_usd, municipio |
| 5 | ¿Qué potencia, voltaje, autonomía, cilindrada y tipo de batería predominan en los anuncios? | A | motor_w, voltaje_v, autonomia_km, cilindrada_cc, tipo_bateria |
| 6 | ¿Cuánto cuesta cada watt y cada km de autonomía anunciados? | A | precio_usd, motor_w, autonomia_km |
| 7 | ¿Qué proporción de anuncios son de vehículos nuevos o usados, y cuántos dicen tener papeles en regla? | A | estado, papeles |
| 8 | ¿Qué proporción de anuncios incluye transporte o entrega? | A | transporte_incluido |
| 9 | ¿Cuántos vendedores concentran los anuncios y qué proporción son reposteos? | A | vendedor, descripcion, titulo |
| 10 | ¿Qué segmentos de oferta aparecen al agrupar los anuncios por precio y características? | A | clustering (K-Means) |

## 2. Usuarios (E)

| # | Pregunta | Fuente |
|---|---|---|
| 11 | ¿Qué edad tienes, a qué te dedicas y en qué municipio vives? | E |
| 12 | Para qué usas tu vehículo (trabajo, transporte personal, mensajería, ocio) | E |
| 13 | ¿Por qué elegiste una moto eléctrica/combustión? ¿Qué pesó más: precio, motor, autonomía o marca? | E |
| 14 | ¿Dónde lo compraste (Revolico, Telegram, importadora, conocido) y por qué ahí? | E |
| 15 | ¿Cuánto pagaste en total, con extras y en qué moneda? | E |
| 16 | ¿Cada cuánto lo cargas, cuánto demora y dónde? ¿Has tenido problemas en días de apagón? | E |
| 17 | ¿La autonomía real coincide con la que anunció el vendedor, y ha bajado con el tiempo? ¿Has tenido fallos técnicos? | E |
| 18 | ¿Cuánto has gastado en baterías, repuestos y mantenimiento? | E |
| 19 | ¿Qué hiciste con las baterías usadas y a cuánto revenderías el vehículo? | E |
| 20 | Si tuvieras que elegir hoy entre eléctrica y gasolina, ¿cuál preferirías y por qué? | E |

## 3. Canal formal, normativa y servicios (D)

| # | Pregunta | Fuente |
|---|---|---|
| 21 | ¿Qué normativa autoriza importar vehículos eléctricos como equipaje y cuántas unidades puede traer una persona al año? | D |
| 22 | ¿Qué arancel y qué valor de referencia en aduana se aplican a cada tipo de vehículo? | D |
| 23 | ¿Qué entidades están autorizadas a comercializar estos vehículos? | D |
| 24 | ¿Cuánto cuesta el mismo tipo de vehículo en tiendas e importadoras frente a los anuncios de Revolico (canal formal vs informal)? | D, A |
| 25 | ¿Qué garantía y postventa ofrecen tiendas e importadoras? | D |
| 26 | ¿Cuánto tarda y qué stock hay en los canales oficiales? | D |
| 27 | ¿Dónde están las importadoras y los talleres de reparación, por municipio? | D |
| 28 | ¿Qué fallas y repuestos son los más frecuentes en los talleres y a qué costo? | D |
| 29 | ¿Cuál es el margen estimado del intermediario sobre el precio final? | D |
| 30 | ¿Qué capacidad de importación o ensamblaje tienen los actores no estatales? | D |

---

## Lo que este estudio no responde (y por qué)

- **Evolución del precio en el tiempo:** Revolico solo ofrece ~14 días y la fecha es de última actualización.
- **Comparación entre provincias:** casi todos los anuncios son de La Habana.
- **Comparación exhaustiva entre canales formales:** de las 21 entidades autorizadas, solo VEDCA publica precios verificables. El resto se documenta como opaco.
- **Triciclos y vehículos de cuatro ruedas:** excluidos del alcance por tener lógicas de uso distintas (carga, transporte comercial). Ver Decisión 8.
- **Peso, tiempo de carga, tamaño de rueda:** casi nunca aparecen en los anuncios. Se preguntan en entrevistas y talleres.
