# Limitaciones y Sesgos del Estudio

Este documento resume las principales limitaciones identificadas durante la investigación. El desarrollo completo se encuentra en la Sección 5 del Informe Final.

## 1. Incidente de hardware y recuperación forense

Un fallo crítico en la partición de Linux durante el desarrollo obligó a detener el proyecto. Se utilizó la herramienta forense **TestDisk** para recuperar el 100% de los 1,200 JSONs, las transcripciones y los scripts. La caché HTML fue recuperada desde un respaldo externo. La única pérdida material fue la base de datos de OpenCode (agente de IA para desarrollo), sobre la que se aplicó un proceso de recuperación forense (`.recover` de SQLite + extracción binaria) que permitió rescatar 11 prompts de la fase de scraping. El resto se documentó como pérdida en `opencode/opencode_history.md`.

## 2. Informalidad del mercado

El alto porcentaje de nulos en los campos de "estado" (83.2%) y "papeles" (62.7%) impidió generar un análisis concluyente sobre la legalidad y condición de los vehículos.

## 3. Filtrado de fuentes normativas

Las 49 fuentes documentales fueron filtradas, extrayendo exclusivamente los artículos referentes a motos, bicicletas y patinetes, descartando normativas de otros vehículos (triciclos, remolques, vehículos de cuatro ruedas).

## 4. Cobertura del canal informal

La muestra se limita a los anuncios publicados en la plataforma Revolico. El mercado informal también opera a través de canales cerrados (grupos de Telegram, WhatsApp, Facebook Marketplace) y de la venta directa entre conocidos, que no fueron capturados por el scraping. La magnitud de estos canales es desconocida, pero las entrevistas sugieren que son relevantes: varios entrevistados mencionaron haber comprado a través de contactos personales o redes familiares (E10, E17, E22).

## 5. Sesgo temporal

Los precios reflejan una "instantánea" del mercado en septiembre-octubre de 2026, no una evolución histórica a largo plazo. Revolico solo expone anuncios de los últimos ~14 días, y la fecha disponible es la de última actualización, no la de publicación.

## 6. Precios pedidos vs. precios de transacción

El estudio analiza los precios publicados (pedidos), no los precios de cierre finales de las negociaciones, los cuales suelen ser menores. La brecha real entre oferta y transacción es probablemente menor que la reportada.

## 7. Validación de clústeres

Aunque se aplicaron pruebas estadísticas (Silhouette Score y ANOVA) que validaron la separación de los grupos, el clustering se realizó sobre una muestra de 231 motos eléctricas (las que tenían datos completos), lo que representa el 77% de la categoría.

## 8. Muestra de entrevistas no probabilística

Las 30 entrevistas semiestructuradas se seleccionaron por conveniencia y bola de nieve, no mediante muestreo aleatorio. Los porcentajes reportados en la Sección 4 (por ejemplo, 76% de preferencia por la moto eléctrica, 50% con problemas de carga, 53% sin licencia) describen la composición de esta muestra específica y no deben interpretarse como prevalencias poblacionales. Con N=30, los intervalos de confianza son amplios y el margen de error estimado supera ±15 puntos porcentuales.

## 9. Subrepresentación del universo importado

Si bien la muestra de 1,200 anuncios es robusta para caracterizar el canal Revolico, representa una fracción del total de vehículos que ingresan al país. Fuentes oficiales reportan 19,443 motos eléctricas importadas, lo que da una idea de la escala del mercado que subyace a los anuncios analizados.

## 10. Canal formal sin entrevistas primarias

Aunque el diseño original contemplaba entrevistas a stakeholders (tiendas, importadoras, talleres), el acceso a estos actores no fue posible en el marco del estudio. La caracterización del canal formal se construyó exclusivamente a partir de fuentes documentales y sitios web oficiales, lo que limita la triangulación de la información de precios y procesos internos.
