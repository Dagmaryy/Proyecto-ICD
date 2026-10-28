"""Descarga búsquedas específicas de motos de combustión y actualiza candidatos.

Hace hasta 90 peticiones de listado (10 términos x 9 páginas), filtra La Habana,
descarta títulos obvios de eléctricos/accesorios y fusiona con los candidatos
existentes. No descarga detalles: de eso se encarga `moto_combustion.py`.

Uso:
    python -u src/scrapers/refrescar_combustion.py
"""

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import quote_plus

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import scrapers.revolico as rv
from scrapers.moto_combustion import (
    _COMBUSTION,
    _ELECTRICO,
    _ELECTRICO_FUERTE,
    _GASOLINA_NEGADA,
    _MARCAS_COMBUSTION,
    _extraer_cilindrada,
    _normalizar,
    _titulo_obviamente_no_combustion,
)
from scrapers.revolico import (
    BASE_DIR,
    MAX_PETICIONES,
    descargar_listado,
    extraer_anuncios_listado,
)

CATEGORIA = "motos"
PROVINCIA_LA_HABANA = "1"
MAX_PAGINAS = 9
MAX_LISTADO = 90

TERMINOS = (
    "moto gasolina",
    "moto 125cc",
    "moto 150cc",
    "moto 200cc",
    "moto 250cc",
    "moto 2t",
    "moto 4t",
    "moto combustion",
    "moto semiautomatica",
    "moto 110cc",
)

RUTA_CANDIDATOS = (
    BASE_DIR / "data/processed/final/motos_combustion_candidatos_cache.json"
)


def _url_busqueda(termino: str, pagina: int) -> str:
    return (
        f"https://www.revolico.com/search?q={quote_plus(termino)}"
        f"&order=date&page={pagina}&cu=1"
    )


def _id_url(url: str) -> str:
    return (url or "").rstrip("/").rsplit("-", 1)[-1]


def _cargar_json(ruta: Path) -> list:
    if not ruta.exists():
        return []
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


def _puntaje(titulo: str) -> int:
    """Prioriza títulos con señales claras de combustión; -1 descarta."""
    texto = _normalizar(titulo)
    if not texto:
        return -1
    if _titulo_obviamente_no_combustion(titulo):
        return -1
    if any(palabra in texto for palabra in _GASOLINA_NEGADA):
        return -1
    if re.search(r"\b(?:36|48|60|72|84)\s*(?:v|volt|voltios)\b", texto):
        return -1
    if any(palabra in texto for palabra in _ELECTRICO_FUERTE):
        return -1
    if any(palabra in texto for palabra in _ELECTRICO):
        return -1

    puntaje = 0
    if any(palabra in texto for palabra in _COMBUSTION):
        puntaje += 3
    if _extraer_cilindrada(texto) is not None:
        puntaje += 2
    if re.search(r"\b(?:2t|4t)\b", texto):
        puntaje += 2
    if "semiautomatica" in texto or "semi automatica" in texto:
        puntaje += 1
    if any(
        re.search(rf"\b{re.escape(marca)}\b", texto)
        for marca in _MARCAS_COMBUSTION
    ):
        puntaje += 1
    return puntaje


def _a_candidato(anuncio: dict, termino: str) -> dict:
    precio = anuncio.get("precio")
    moneda = anuncio.get("moneda")
    return {
        "titulo": anuncio.get("titulo"),
        "precio_usd": precio if moneda == "USD" else None,
        "precio": precio,
        "moneda": moneda,
        "provinceId": anuncio.get("provinceId"),
        "municipalityId": anuncio.get("municipalityId"),
        "url_detalle": anuncio.get("url_detalle"),
        "origen_busqueda": termino,
    }


def descargar_termino(termino: str, max_paginas: int) -> list[dict]:
    anuncios: list[dict] = []
    peticiones_iniciales = rv._contador_peticiones

    for pagina in range(1, max_paginas + 1):
        nuevas = rv._contador_peticiones - peticiones_iniciales
        if nuevas >= MAX_LISTADO or rv._contador_peticiones >= MAX_PETICIONES:
            print(f"[LIMITE] Listado detenido en {nuevas} peticiones nuevas.")
            break
        url = _url_busqueda(termino, pagina)
        try:
            html = descargar_listado(
                url, CATEGORIA, etiqueta=f"comb_{termino}"
            )
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
            if str(anuncio.get("provinceId")) != PROVINCIA_LA_HABANA:
                continue
            if _puntaje(anuncio.get("titulo")) < 0:
                continue
            anuncios.append(_a_candidato(anuncio, termino))

    print(
        f"[BUSQUEDA] {termino}: {len(anuncios)} candidatos, "
        f"{rv._contador_peticiones - peticiones_iniciales} peticiones nuevas"
    )
    return anuncios


def fusionar(descargados: list[dict], existentes: list[dict]) -> list[dict]:
    unicos: dict[str, dict] = {}
    for registro in existentes:
        idd = _id_url(registro.get("url_detalle", ""))
        if idd:
            unicos.setdefault(idd, registro)
    for registro in descargados:
        idd = _id_url(registro.get("url_detalle", ""))
        if idd:
            unicos.setdefault(idd, registro)

    candidatos = [
        registro
        for registro in unicos.values()
        if str(registro.get("provinceId")) == PROVINCIA_LA_HABANA
        and _puntaje(registro.get("titulo")) >= 0
    ]
    candidatos.sort(
        key=lambda registro: (
            -_puntaje(registro.get("titulo")),
            _id_url(registro.get("url_detalle", "")),
        )
    )
    return candidatos


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Descarga búsquedas específicas de motos de combustión."
    )
    parser.add_argument(
        "--terminos",
        default=",".join(TERMINOS),
        help="Términos separados por coma.",
    )
    parser.add_argument(
        "--paginas",
        type=int,
        default=MAX_PAGINAS,
        help=f"Máximo de páginas por término (por defecto {MAX_PAGINAS}).",
    )
    args = parser.parse_args(argv)

    terminos = [t.strip() for t in args.terminos.split(",") if t.strip()]
    paginas = max(1, min(args.paginas, MAX_PAGINAS))
    candidatos = _cargar_json(RUTA_CANDIDATOS)
    print(f"[FUENTES] candidatos previos: {len(candidatos)}")

    for termino in terminos:
        nuevos = descargar_termino(termino, paginas)
        candidatos = fusionar(nuevos, candidatos)
        print(
            f"[CANDIDATOS] tras «{termino}»: {len(candidatos)} "
            f"(nuevos vistos: {len(nuevos)})"
        )
        RUTA_CANDIDATOS.parent.mkdir(parents=True, exist_ok=True)
        with open(RUTA_CANDIDATOS, "w", encoding="utf-8") as f:
            json.dump(candidatos, f, ensure_ascii=False, indent=2)

    print(f"[SALIDA] {RUTA_CANDIDATOS} ({len(candidatos)} candidatos)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
