"""Tests de humo del pipeline de datos de ICD.

Sin fixtures ni mocks: solo comprueban que el código importa, que los
archivos finales existen con el esquema esperado y que los esquemas cargan.
"""

import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
FINAL_DIR = BASE_DIR / "data/processed/final"
SCHEMAS_DIR = BASE_DIR / "docs/schemas"

CAMPOS = {
    "titulo",
    "precio_usd",
    "marca",
    "modelo",
    "provinceId",
    "municipalityId",
    "url_detalle",
    "motivo",
}

CATEGORIAS = ("motos", "bicis", "patinetes")


def test_procesar_detalles_motos():
    from src.scrapers.revolico import procesar_detalles

    resultado = procesar_detalles("motos", max_anuncios=5)
    assert len(resultado["validos_completos"]) == 3


def test_limpios_existen():
    for categoria in CATEGORIAS:
        assert (FINAL_DIR / f"{categoria}_final_limpio.json").is_file()


def test_limpios_campos():
    for categoria in CATEGORIAS:
        with open(
            FINAL_DIR / f"{categoria}_final_limpio.json", encoding="utf-8"
        ) as f:
            registros = json.load(f)
        assert 100 <= len(registros) <= 10000, categoria
        for registro in registros:
            assert set(registro.keys()) == CAMPOS, categoria


def test_esquemas_cargan():
    for ruta in sorted(SCHEMAS_DIR.glob("*.json")):
        with open(ruta, encoding="utf-8") as f:
            json.load(f)


def test_extraer_campos_tecnicos_regex():
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

    tecnicos = extraer_campos_tecnicos("Moto 0km, 3 meses de uso", "Moto")
    assert tecnicos["estado"] == "Nueva"
    assert tecnicos["plegable"] is False

    tecnicos = extraer_campos_tecnicos("Autonomía 35-50 km, 30 km x hora", "Patinete")
    assert tecnicos["autonomia_km"] == 50
    assert tecnicos["velocidad_max_kmh"] == 30


def test_normalizacion_guiones_no_fusiona_rangos():
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
