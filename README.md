Proyecto ICD — Análisis del Mercado de Motos

Asignatura: Introducción a la Ciencia de Datos
Profesor: Yudivian Almeida
Estudiante: Dagmary Pérez Aguiar
Mercado analizado: Motos eléctricas en Cuba

---

Descripción

Proyecto de investigación que combina scraping web (Revolico), entrevistas a usuarios y datos de stakeholders (tiendas, importadoras, talleres e instituciones) para analizar el mercado de motos eléctricas en Cuba.

Se incluyen también bicicletas eléctricas y patinetes como categorías complementarias del mismo mercado de movilidad eléctrica.

Objetivo final: un informe de análisis de mercado, no un software.

---

Instalación

```bash
# 1. Crear y activar el entorno virtual
python3 -m venv venv
source venv/bin/activate

# 2. Instalar dependencias
pip install -r requirements.txt
```

---

Metodología

Investigación mixta: cuantitativa (scraping y clustering) + cualitativa (entrevistas).

Población y muestra

Fuente Cantidad Descripción
Anuncios 30 Motos, bicicletas y patinetes eléctricos de Revolico
Entrevistas 30 Usuarios del mercado

Técnicas de recolección

1. Scraping web — Revolico
2. Entrevistas semiestructuradas
3. Análisis documental — ONCUBA, Postdata.club, Decreto 163/2026

Técnicas de análisis

1. Limpieza y normalización — regex, tasa CUP/USD
2. Clustering — K-Means sobre TF-IDF + variables numéricas
3. Visualización — Matplotlib, Seaborn, Plotly
4. Triangulación de fuentes

---

Limitaciones

· Reposteos en Revolico
· Precios mixtos (USD / CUP)
· Sesgo de la fuente (solo anuncios publicados)
· No hay análisis temporal mensual (ver nota abajo)

---

Consideraciones éticas

· Consentimiento informado en entrevistas
· User-Agent honesto en scraping
· Delay de 3 segundos entre peticiones

---

Nota importante sobre las fechas

Revolico no expone la fecha original de publicación, solo la de última actualización. Las fechas de los anuncios scrapeados se concentran entre el 24 de septiembre y el 8 de octubre de 2026, porque la plataforma solo muestra anuncios recientes.

No es posible hacer análisis temporal mensual.

---
