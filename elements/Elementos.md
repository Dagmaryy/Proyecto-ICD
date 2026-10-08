
## Alcance del estudio

Mercado de motos eléctricas en **La Habana**, con bicicletas y patinetes eléctricos como categorías complementarias.

- **Anuncios (Revolico):** instantánea del 24 de septiembre al 8 de octubre de 2026. Revolico solo muestra anuncios de los últimos ~14 días, casi todos de La Habana, y la fecha disponible es la de última actualización, no la de publicación. Los precios son **precios pedidos**, no precios de venta.
- **Entrevistas y stakeholders:** también en La Habana, para poder comparar las fuentes entre sí.

**Fuentes:** A = Anuncios (Revolico) · E = Entrevistas (30 usuarios) · S = Stakeholders (tiendas, importadoras, talleres) · D = Documental (ONCUBA, Postdata.club, Decreto 163/2026)

---

## 1. Oferta y precios en anuncios (A)

| # | Pregunta | Fuente | Variables |
|---|---|---|---|
| 1 | ¿Qué marcas y modelos se anuncian en La Habana y con qué frecuencia? | A | marca, modelo |
| 2 | ¿Cuál es el precio mediano pedido de cada tipo de vehículo (moto, bici, patinete)? | A | precio_usd, tipo_vehiculo |
| 3 | ¿Cómo varía el precio pedido según la marca? | A | precio_usd, marca |
| 4 | ¿Cómo varía el precio pedido entre municipios de La Habana? | A | precio_usd, municipio |
| 5 | ¿Qué potencia, voltaje, autonomía y tipo de batería predominan en los anuncios? | A | motor_w, voltaje_v, autonomia_km, tipo_bateria |
| 6 | ¿Cuánto cuesta cada watt y cada km de autonomía anunciados? | A | precio_usd, motor_w, autonomia_km |
| 7 | ¿Qué proporción de anuncios son de vehículos nuevos o usados, y cuántos dicen tener papeles en regla? | A | estado, papeles |
| 8 | ¿Qué proporción de anuncios incluye transporte o entrega? | A | transporte_incluido |
| 9 | ¿Cuántos vendedores concentran los anuncios y qué proporción son reposteos? | A | vendedor, descripcion, titulo |
| 10 | ¿Qué segmentos de oferta aparecen al agrupar los anuncios por precio y características? | A | clustering (K-Means) |

## 2. Usuarios (E)

| # | Pregunta | Fuente |
|---|---|---|
| 11 | ¿Cuál es el perfil del comprador en La Habana (edad, ocupación, municipio)? | E |
| 12 | ¿Cuál es su motivación principal de compra (ahorro, apagones, transporte, negocio)? | E |
| 13 | ¿Qué porcentaje usa el vehículo para trabajo o negocio? | E |
| 14 | ¿Por qué eligió moto, bici o patinete y no otro tipo? | E |
| 15 | ¿En qué canal compró (Revolico, tienda, importadora, equipaje, conocido) y por qué? | E |
| 16 | ¿Cuánto pagó en total, incluyendo papeles, envío y accesorios? | E |
| 17 | ¿Cómo influyó la garantía o la postventa en su decisión? | E |
| 18 | ¿Dónde y cuánto tiempo carga el vehículo, y cómo le afectan los apagones? | E |
| 19 | ¿Qué gastos ha tenido en baterías, repuestos y mantenimiento? | E |
| 20 | ¿Qué hace con las baterías usadas y a qué precio revendería el vehículo? | E |

## 3. Canal formal, normativa y servicios (S, D)

| # | Pregunta | Fuente |
|---|---|---|
| 21 | ¿Qué normativa autoriza importar vehículos eléctricos como equipaje y cuántas unidades puede traer una persona al año? | D |
| 22 | ¿Qué arancel y qué valor de referencia en aduana se aplican a cada tipo de vehículo? | D |
| 23 | ¿Qué entidades están autorizadas a comercializar estos vehículos? | D, S |
| 24 | ¿Cuánto cuesta el mismo tipo de vehículo en tiendas e importadoras frente a los anuncios de Revolico (canal formal vs informal)? | S, A |
| 25 | ¿Qué garantía y postventa ofrecen tiendas e importadoras? | S |
| 26 | ¿Cuánto tarda y qué stock hay en los canales oficiales? | S |
| 27 | ¿Dónde están las importadoras y los talleres de reparación, por municipio? | S |
| 28 | ¿Qué fallas y repuestos son los más frecuentes en los talleres y a qué costo? | S |
| 29 | ¿Cuál es el margen estimado del intermediario sobre el precio final? | S |
| 30 | ¿Qué capacidad de importación o ensamblaje tienen los actores no estatales? | S, D |

---

## Lo que este estudio no responde (y por qué)

- **Evolución del precio en el tiempo:** Revolico solo ofrece ~14 días y la fecha es de última actualización.
- **Comparación entre provincias:** casi todos los anuncios son de La Habana.
- **Peso, tiempo de carga, tamaño de rueda:** casi nunca aparecen en los anuncios. Se preguntan en entrevistas y talleres.

## Datos a conservar de los anuncios

- `vendedor` y `viewCount` (indicador de demanda) ya se extraen del HTML de detalle, pero no llegan al esquema JSON. Hay que decidir si se añaden, ya que `AGENTS.md` pide consultar antes de modificar campos.

