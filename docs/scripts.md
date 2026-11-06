# Scripts del proyecto

Trazabilidad de los scripts de análisis. Todos se ejecutan desde la raíz del proyecto con el venv activado.

## Extracción y limpieza

| Script | Qué hace | Entrada | Salida |
|---|---|---|---|
| `src/scrapers/revolico.py` | Scraper base de Revolico | HTML en `data/raw/web/revolico/` | JSONs en `data/processed/` |
| `src/scrapers/moto_electrica.py` | Scraper de motos eléctricas | Listados HTML | `motos_electricas_300.json` |
| `src/scrapers/moto_combustion.py` | Scraper de motos de combustión | Listados HTML | `motos_combustion_300.json` |
| `src/scrapers/bici.py` | Scraper de bicicletas | Listados HTML | `bicis_300.json` |
| `src/scrapers/patinete.py` | Scraper de patinetes | Listados HTML | `patinetes_300.json` |
| `src/scripts/enriquecer_masivo.py` | Enriquecimiento con regex sobre campos nulos | JSONs de 300 | `*_enriquecido.json` |

## Análisis de anuncios

| Script | Qué hace | Salida |
|---|---|---|
| `src/analysis/generar_csvs.py` | Genera todos los CSVs de anuncios para gráficos | `csv_graficos/*.csv` |
| `src/analysis/generar_datos_mapa.py` | Agrega los 1,200 anuncios por municipio | `datos_mapa_habana.csv` |
| `src/analysis/clustering.py` | K-Means de motos eléctricas | `clustering_motos.json` |
| `src/analysis/clustering_combustion.py` | K-Means de motos de combustión | stats en consola |
| `src/analysis/clustering_multiple.py` | K-Means global de las 4 categorías | stats en consola |
| `src/analysis/validar_clustering.py` | Silhouette y ANOVA de los clústeres | stats en consola |
| `src/analysis/analisis_vendedores.py` | Índice de Gini y concentración de vendedores | stats en consola |
| `src/analysis/analisis_cilindradas.py` | Distribución de cilindradas | stats en consola |
| `src/analysis/analisis_papeles.py` | Cobertura de papeles y garantías | stats en consola |
| `src/analysis/analisis_tecnico_verticales.py` | Costo por vatio y por km | stats en consola |
| `src/analysis/analisis_avanzado.py` | Análisis general de la oferta | stats en consola |

## Análisis de entrevistas

| Script | Qué hace | Salida |
|---|---|---|
| `src/analysis/normalizar_entrevistas.py` | Normaliza el JSON de entrevistas | `entrevistas_final_corregido.json` |
| `src/analysis/tabulacion_entrevistas.py` | Tabula los 11 campos del JSON y exporta CSVs | `csv_graficos/entrevistas_*.csv` |

## Generación de gráficos

| Script | Qué hace | Salida |
|---|---|---|
| `src/analysis/graficos_finales.py` | Genera los 10 gráficos del informe en HTML interactivo | `reports/plots/*.html` y `*.png` |

## Cómo reproducir el pipeline completo

```bash
# 1. Activar entorno
source venv/bin/activate

# 2. Regenerar CSVs de anuncios (si es necesario)
python src/analysis/generar_csvs.py
python src/analysis/generar_datos_mapa.py

# 3. Regenerar CSVs de entrevistas (si es necesario)
python src/analysis/tabulacion_entrevistas.py

# 4. Generar todos los gráficos
python src/analysis/graficos_finales.py
