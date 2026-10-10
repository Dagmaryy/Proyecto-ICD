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
    from codigo.scrapers.revolico import procesar_detalles

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
