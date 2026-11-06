# Limitaciones y Sesgos del Estudio

Este documento resume las principales limitaciones identificadas durante la investigación. El desarrollo completo se encuentra en la sección 5 del [Informe Final](final_report.md).

## 1. Incidente de Hardware
Durante el desarrollo, un fallo crítico en la partición de Linux obligó a detener el proyecto. Se utilizó la herramienta forense **TestDisk** para recuperar el 100% de los JSONs y scripts. La caché HTML fue recuperada desde un respaldo externo. La única pérdida fue la base de datos de OpenCode (NLP).

## 2. Limitaciones de la Muestra
*   **Sesgo de plataforma:** Los datos de oferta provienen únicamente de Revolico, excluyendo otros canales informales (Telegram, WhatsApp).
*   **Sesgo temporal:** Los precios reflejan una "instantánea" de septiembre-octubre de 2026, no una serie histórica.
*   **Precios pedidos:** El análisis se basa en los precios publicados por los vendedores, no en los precios finales de transacción (que suelen ser menores).

## 3. Limitaciones de los Datos
*   **Informalidad:** El 62.7% de los anuncios no menciona si el vehículo tiene "papeles en regla", lo que imposibilita un análisis legal concluyente.
*   **Datos técnicos incompletos:** El clustering se realizó sobre las 231 motos eléctricas (77%) que tenían datos completos de precio, potencia y autonomía.
