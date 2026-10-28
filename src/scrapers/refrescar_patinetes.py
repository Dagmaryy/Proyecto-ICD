"""Refresca los listados de patinetes y calcula los candidatos de La Habana.

Vuelve a descargar hasta 10 páginas de cada búsqueda de patinetes, une los
anuncios con `final/patinetes_final_limpio.json` y con los patinetes elegibles
de `versiones/patinetes_final_v2.json`, quita duplicados por el número final
de la URL y filtra `provinceId == 1`.

Uso:
    python -u src/scrapers/refrescar_patinetes.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import scrapers.revolico as rv
from scrapers.revolico import (
    BASE_DIR,
    MAX_PETICIONES,
    _url_pagina,
    descargar_listado,
    es_patinete_electrico,
    extraer_anuncios_listado,
)

CATEGORIA = "patinetes"
MAX_PAGINAS = 10
PROVINCIA_LA_HABANA = "1"

TERMINOS = (
    "patinete electrico",
    "patineta electrica",
    "scooter electrico",
    "scooter electrico plegable",
    "scooter plegable",
)

RUTA_FINAL_LIMPIO = BASE_DIR / "data/processed/final/patinetes_final_limpio.json"
RUTA_V2 = BASE_DIR / "data/processed/versiones/patinetes_final_v2.json"
RUTA_SALIDA = BASE_DIR / "data/processed/final/patinetes_candidatos.json"


def _url_busqueda(termino: str, pagina: int) -> str:
    from urllib.parse import quote_plus

    return (
        f"https://www.revolico.com/search?q={quote_plus(termino)}"
        f"&order=date&page={pagina}&cu=1"
    )


def _id_url(url: str) -> str:
    return (url or "").rstrip("/").rsplit("-", 1)[-1]


def _cargar_json(ruta: Path) -> list:
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


def descargar_busquedas() -> list[dict]:
    """Descarga hasta 10 páginas por término y devuelve los patinetes vistos."""
    anuncios: list[dict] = []
    peticiones_iniciales = rv._contador_peticiones

    for termino in TERMINOS:
        for pagina in range(1, MAX_PAGINAS + 1):
            if rv._contador_peticiones >= MAX_PETICIONES:
                print(f"[LIMITE] Alcanzado el límite global de {MAX_PETICIONES}.")
                print(f"[INFO] Peticiones nuevas en esta ejecución: "
                      f"{rv._contador_peticiones - peticiones_iniciales}")
                return anuncios
            url = _url_busqueda(termino, pagina)
            try:
                html = descargar_listado(url, CATEGORIA, etiqueta=termino)
            except RuntimeError as exc:
                print(f"[ERROR] {url}: {exc}")
                continue
            try:
                del_listado = extraer_anuncios_listado(html)
            except ValueError as exc:
                print(f"[ERROR] {termino} p{pagina}: {exc}")
                continue
            if not del_listado:
                break
            for anuncio in del_listado:
                es, _ = es_patinete_electrico(anuncio["titulo"])
                if es:
                    anuncios.append(anuncio)

    print(f"[INFO] Peticiones nuevas en esta ejecución: "
          f"{rv._contador_peticiones - peticiones_iniciales}")
    return anuncios


def _a_candidato(registro: dict) -> dict:
    return {
        "titulo": registro.get("titulo"),
        "precio_usd": registro.get("precio_usd", registro.get("precio")),
        "marca": registro.get("marca"),
        "modelo": registro.get("modelo"),
        "provinceId": registro.get("provinceId"),
        "municipalityId": registro.get("municipalityId"),
        "url_detalle": registro.get("url_detalle"),
        "motivo": registro.get("motivo"),
    }


def fusionar(descargados: list[dict], final_limpio: list[dict], v2: list[dict]) -> list[dict]:
    """Une las tres fuentes, deduplica por id de URL y filtra La Habana."""
    unicos: dict[str, dict] = {}

    for registro in descargados:
        idd = _id_url(registro.get("url_detalle"))
        if idd:
            unicos.setdefault(idd, _a_candidato(registro))
    for registro in final_limpio:
        idd = _id_url(registro.get("url_detalle"))
        if idd:
            unicos.setdefault(idd, _a_candidato(registro))
    for registro in v2:
        idd = _id_url(registro.get("url_detalle"))
        if idd:
            unicos.setdefault(idd, _a_candidato(registro))

    return [
        registro
        for registro in unicos.values()
        if str(registro.get("provinceId")) == PROVINCIA_LA_HABANA
    ]


def main(argv: list[str] | None = None) -> int:
    descargados = descargar_busquedas()
    print(f"[DESCARGADOS] patinetes eléctricos de búsquedas: {len(descargados)}")

    final_limpio = _cargar_json(RUTA_FINAL_LIMPIO)
    v2 = _cargar_json(RUTA_V2)
    print(f"[FUENTES] final_limpio={len(final_limpio)} v2={len(v2)}")

    candidatos = fusionar(descargados, final_limpio, v2)
    print(f"[CANDIDATOS] La Habana, únicos por id: {len(candidatos)}")

    RUTA_SALIDA.parent.mkdir(parents=True, exist_ok=True)
    with open(RUTA_SALIDA, "w", encoding="utf-8") as f:
        json.dump(candidatos, f, ensure_ascii=False, indent=2)
    print(f"[SALIDA] {RUTA_SALIDA}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
