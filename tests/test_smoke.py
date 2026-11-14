"""Tests de humo del pipeline de datos de ICD.
Comprueban la existencia de datos, los esquemas y la lógica de extracción (regex).
"""
import json
import sys
from pathlib import Path
import pytest

# Añadir la raíz del proyecto al path para importar src
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.config_paths import JSON_DIR, CSV_DIR, BASE_DIR

def test_datos_finales_existen():
    """Verifica que los 4 datasets finales + entrevistas existen en JSON/."""
    archivos_esperados = [
        "motos_electricas_300_enriquecido.json",
        "motos_combustion_300_enriquecido.json",
        "bicis_300_enriquecido.json",
        "patinetes_300_enriquecido.json",
        "entrevistas_final_corregido.json"
    ]
    for archivo in archivos_esperados:
        ruta = JSON_DIR / archivo
        assert ruta.is_file(), f"Falta el archivo: {ruta}"

def test_estructura_datos():
    """Verifica que los JSON tengan registros y los campos clave."""
    with open(JSON_DIR / "motos_electricas_300_enriquecido.json", "r", encoding="utf-8") as f:
        datos = json.load(f)
        assert len(datos) == 300, "El dataset de eléctricas no tiene 300 registros"
        assert "precio_usd" in datos[0], "Falta el campo precio_usd en el JSON"

def test_esquemas_cargan():
    """Verifica que los esquemas JSON sigan en docs/schemas/."""
    esquemas_dir = BASE_DIR / "docs" / "schemas"
    for ruta in sorted(esquemas_dir.glob("*.json")):
        with open(ruta, encoding="utf-8") as f:
            json.load(f)

def test_index_existe():
    """Verifica que el index.html esté en la raíz."""
    assert (BASE_DIR / "index.html").is_file(), "El index.html no está en la raíz"

def test_extraer_campos_tecnicos_regex():
    """Prueba la lógica de extracción técnica (No depende de archivos)."""
    from src.scrapers.revolico import extraer_campos_tecnicos

    tecnicos = extraer_campos_tecnicos(
        "Motor 500 Wats, 72 Voltios, 20 Amperios, batería LiFePO4, "
        "autonomía 125-140 KM, velocidad 45 km/h, peso 187.00 lb. "
        "Seminueva, papeles en regla.",
        "Bici plegable",
    )
    assert tecnicos["motor_w"] == 500
    assert tecnicos["voltaje_v"] == 72
    assert tecnicos["amperaje_ah"] == 20
    assert tecnicos["tipo_bateria"] == "lifepo4"
    assert tecnicos["autonomia_km"] == 140
    assert tecnicos["velocidad_max_kmh"] == 45
    assert tecnicos["peso_kg"] == 85
    assert tecnicos["estado"] == "Seminueva"
    assert tecnicos["papeles"] == "en regla"
    assert tecnicos["plegable"] is True

def test_normalizacion_guiones_no_fusiona_rangos():
    """Prueba la normalización de guiones (No depende de archivos)."""
    from src.scrapers.moto_combustion import _normalizar
    from src.scrapers.revolico import _normalizar_titulo

    casos = {
        "70–80 km": "70 80 km",
        "6–8 horas": "6 8 horas",
        "10‑20": "10 20",
        "4—5": "4 5",
        "1‒2": "1 2",
        "3―4": "3 4",
        "5－6": "5 6",
        "−5": "5",
    }
    for texto, esperado in casos.items():
        assert _normalizar_titulo(texto) == esperado
        assert _normalizar(texto) == esperado
