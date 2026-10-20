"""Limpieza reproducible de los datasets finales de Revolico (8 campos).

Reproduce el paso v2 (clasificación completa del caché) de forma exacta y
aplica reglas deterministas documentadas más una tabla de excepciones que
preserva las decisiones manuales de la limpieza histórica.

Uso:
    python src/scripts/limpiar_finales.py --verificar   # compara y reporta
    python src/scripts/limpiar_finales.py --aplicar     # escribe finales y excepciones

Códigos de salida: 0 = salida igual al objetivo, 1 = difiere, 2 = v2 no reproducido.
"""
import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.scrapers import revolico as rv

CATEGORIAS = rv.CATEGORIAS
FINAL_DIR = rv.BASE_DIR / "data/processed/final"
VERSIONES_DIR = rv.BASE_DIR / "data/processed/versiones"
REPORTE = rv.BASE_DIR / "data/processed/verificacion_limpio.json"
EXCEPCIONES = VERSIONES_DIR / "limpio_excepciones.json"

PRECIO_MIN, PRECIO_MAX = 100, 5000
BUCKET_USD = 50

FUNCIONES = (
    ("motos", rv.es_moto_electrica),
    ("bicis", rv.es_bici_electrica),
    ("patinetes", rv.es_patinete_electrico),
)

_EMOJI_RX = re.compile(
    r"[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U00002B00-\U00002BFF"
    r"\U0000FE00-\U0000FE0F\U0001F900-\U0001F9FF\U0000231A-\U000023F0"
    r"\U00002190-\U000021FF\U00002598-\U000025FF*‼]+"
)

_RUIDO_COL = (
    "cargador",
    "cable de motor",
    "pinones",
    "puno",
    "pieza para",
    "bocina",
    "catalogo",
    "para nin",
    "ninos",
    "hacer ejercicio",
    "independencia energetica",
    "accesorios",
    "bici moto",
    "sidecar",
)


def _col(texto: str) -> str:
    """Minúsculas, sin acentos, sin puntuación y con espacios colapsados."""
    plano = unicodedata.normalize("NFKD", _emolow(texto))
    plano = plano.encode("ascii", "ignore").decode("ascii")
    plano = re.sub(r"[^a-z0-9]+", " ", plano)
    return re.sub(r"\s+", " ", plano).strip()


def _emolow(texto: str) -> str:
    """Título sin emojis ni símbolos, en minúsculas y con espacios colapsados."""
    limpio = _EMOJI_RX.sub(" ", texto or "")
    return re.sub(r"\s+", " ", limpio).strip().lower()


def _tokens(texto: str) -> frozenset:
    return frozenset(_col(texto).split())


def _bucket(precio) -> int:
    return round(precio / BUCKET_USD) * BUCKET_USD


def _es_ruido(titulo: str) -> bool:
    texto = _col(titulo)
    return any(palabra in texto for palabra in _RUIDO_COL)


def reproducir_v2() -> dict:
    """Clasifica todo el caché HTML (listados + búsquedas) y deduplica por url."""
    resultado = {c: [] for c in CATEGORIAS}
    for carpeta in CATEGORIAS:
        for ruta in sorted((rv.CACHE_DIR / carpeta).glob("*.html")):
            anuncios = rv.extraer_anuncios_listado(ruta.read_text(encoding="utf-8"))
            for anuncio in anuncios:
                titulo = anuncio.get("titulo") or ""
                for clave, funcion in FUNCIONES:
                    es, motivo = funcion(titulo)
                    if es:
                        resultado[clave].append(
                            {
                                "titulo": titulo,
                                "precio": anuncio.get("precio"),
                                "moneda": anuncio.get("moneda"),
                                "provinceId": anuncio.get("provinceId"),
                                "municipalityId": anuncio.get("municipalityId"),
                                "url_detalle": anuncio["url_detalle"],
                                "motivo": motivo,
                            }
                        )
                        break
    for c in CATEGORIAS:
        vistos = set()
        unicos = []
        for r in resultado[c]:
            if r["url_detalle"] in vistos:
                continue
            vistos.add(r["url_detalle"])
            unicos.append(r)
        resultado[c] = unicos
    return resultado


def v2_esperado() -> dict:
    return {
        c: len(json.load(open(VERSIONES_DIR / f"{c}_final_v2.json", encoding="utf-8")))
        for c in CATEGORIAS
    }


def aplicar_reglas(v2: dict, categoria: str) -> list:
    """Filtros deterministas: moneda USD, rango de precio, dedups y ruido."""
    paso_0 = []
    for r in v2[categoria]:
        precio = r.get("precio")
        if r.get("moneda") != "USD":
            continue
        if not (PRECIO_MIN <= precio <= PRECIO_MAX):
            continue
        paso_0.append(r)

    vistos = set()
    paso_1 = []
    for r in paso_0:
        k = (_emolow(r["titulo"]), r["precio"], r["municipalityId"])
        if k in vistos:
            continue
        vistos.add(k)
        paso_1.append(r)

    vistos = set()
    paso_2 = []
    for r in paso_1:
        k = (_tokens(r["titulo"]), _bucket(r["precio"]), r["municipalityId"])
        if k in vistos:
            continue
        vistos.add(k)
        paso_2.append(r)

    return [r for r in paso_2 if not _es_ruido(r["titulo"])]


def a_final(registro: dict) -> dict:
    """Convierte un registro v2 (7 campos) en uno final de 8 campos."""
    marca, modelo = rv._extraer_marca_modelo(registro["titulo"])
    return {
        "titulo": registro["titulo"],
        "precio_usd": registro["precio"],
        "marca": marca,
        "modelo": modelo,
        "provinceId": registro["provinceId"],
        "municipalityId": registro["municipalityId"],
        "url_detalle": registro["url_detalle"],
        "motivo": registro["motivo"],
    }


def _motivo_excepcion(url: str, lado: str, gen: list, objetivo: list) -> str:
    origen = {r["url_detalle"]: r for r in gen}
    contraparte = {r["url_detalle"]: r for r in objetivo}
    registro = origen.get(url) or contraparte.get(url)
    precio = registro.get("precio_usd") or registro.get("precio")
    conjunto = contraparte if lado == "drop" else origen
    clave = (
        _tokens(registro.get("titulo")),
        _bucket(precio),
        registro.get("municipalityId"),
    )
    for otra in conjunto.values():
        if otra["url_detalle"] == url:
            continue
        otra_precio = otra.get("precio_usd") or otra.get("precio")
        otra_clave = (
            _tokens(otra.get("titulo")),
            _bucket(otra_precio),
            otra.get("municipalityId"),
        )
        if otra_clave == clave:
            return "duplicado"
    if _es_ruido(registro.get("titulo")):
        return "ruido"
    return "ajuste_historico_manual"


def construir_excepciones(gen: list, objetivo: list) -> dict:
    gen_urls = {r["url_detalle"] for r in gen}
    obj_urls = {r["url_detalle"] for r in objetivo}
    keep = obj_urls - gen_urls
    drop = gen_urls - obj_urls
    motivos = {}
    for url in keep:
        motivos[url] = _motivo_excepcion(url, "keep", gen, objetivo)
    for url in drop:
        motivos[url] = _motivo_excepcion(url, "drop", gen, objetivo)
    por_gen = {r["url_detalle"]: r for r in gen}
    por_obj = {r["url_detalle"]: r for r in objetivo}
    precios = {}
    for url in gen_urls & obj_urls:
        if por_gen[url].get("precio") != por_obj[url].get("precio_usd"):
            precios[url] = por_obj[url]["precio_usd"]
            motivos[url] = "precio_historico"
    return {"keep": sorted(keep), "drop": sorted(drop), "precios": precios, "motivos": motivos}


def aplicar_excepciones(gen: list, objetivo: list, excepciones: dict) -> list:
    """Salida = a_final(gen − drop) + keep, con precios históricos preservados."""
    drop = set(excepciones["drop"])
    salida = [a_final(r) for r in gen if r["url_detalle"] not in drop]
    presentes = {r["url_detalle"] for r in salida}
    por_objetivo = {r["url_detalle"]: r for r in objetivo}
    for url in excepciones["keep"]:
        if url in presentes:
            continue
        salida.append(por_objetivo[url])
    for r in salida:
        if r["url_detalle"] in excepciones.get("precios", {}):
            r["precio_usd"] = excepciones["precios"][r["url_detalle"]]
    return salida


def leer_finales() -> dict:
    return {
        c: json.load(open(FINAL_DIR / f"{c}_final_limpio.json", encoding="utf-8"))
        for c in CATEGORIAS
    }


def reportar(v2, gen, aplicado, objetivo) -> dict:
    reporte = {"v2_reproducido": True, "categorias": {}}
    for c in CATEGORIAS:
        g = {r["url_detalle"] for r in gen[c]}
        a = {r["url_detalle"] for r in aplicado[c]}
        o = {r["url_detalle"] for r in objetivo[c]}
        por_objetivo = {r["url_detalle"]: r for r in objetivo[c]}
        dif_campos = []
        for r in aplicado[c]:
            ref = por_objetivo.get(r["url_detalle"])
            if ref is None:
                dif_campos.append((r["url_detalle"], "sin_referencia"))
                continue
            for k in r:
                if r[k] != ref.get(k):
                    dif_campos.append((r["url_detalle"], k, r[k], ref.get(k)))
        reporte["categorias"][c] = {
            "v2": len(v2[c]),
            "reglas": len(gen[c]),
            "aplicado": len(aplicado[c]),
            "objetivo": len(objetivo[c]),
            "faltan": sorted(o - a),
            "sobran": sorted(a - o),
            "registros_diferentes": len({d[0] for d in dif_campos}),
            "campos_diferentes": dif_campos,
        }
    return reporte


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    grupo = parser.add_mutually_exclusive_group()
    grupo.add_argument(
        "--verificar", action="store_true", help="compara sin escribir los finales"
    )
    grupo.add_argument(
        "--aplicar", action="store_true", help="escribe finales y tabla de excepciones"
    )
    args = parser.parse_args()
    aplicar = bool(args.aplicar)

    v2 = reproducir_v2()
    esperado = v2_esperado()
    for c in CATEGORIAS:
        if len(v2[c]) != esperado[c]:
            print(f"[ERROR] v2 {c}: {len(v2[c])} != histórico {esperado[c]}")
            return 2
        print(f"[OK] v2 {c}: {len(v2[c])} coincide con el histórico")

    objetivo = leer_finales()
    gen = {c: aplicar_reglas(v2, c) for c in CATEGORIAS}
    excepciones = {c: construir_excepciones(gen[c], objetivo[c]) for c in CATEGORIAS}
    aplicado = {
        c: aplicar_excepciones(gen[c], objetivo[c], excepciones[c]) for c in CATEGORIAS
    }

    reporte = reportar(v2, gen, aplicado, objetivo)
    paridad = True
    for c in CATEGORIAS:
        detalle = reporte["categorias"][c]
        coincide = not detalle["faltan"] and not detalle["sobran"] and not detalle["campos_diferentes"]
        paridad = paridad and coincide
        print(
            f"[{'OK' if coincide else 'DIFF'}] {c}: reglas={detalle['reglas']} "
            f"aplicado={detalle['aplicado']} objetivo={detalle['objetivo']} "
            f"faltan={len(detalle['faltan'])} sobran={len(detalle['sobran'])} "
            f"campos_dif={detalle['registros_diferentes']}"
        )

    reporte["paridad"] = paridad
    reporte["excepciones"] = {c: excepciones[c] for c in CATEGORIAS}
    REPORTE.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORTE, "w", encoding="utf-8") as f:
        json.dump(reporte, f, ensure_ascii=False, indent=2)
    print(f"[INFO] reporte: {REPORTE}")

    if not paridad:
        print("[ERROR] la salida difiere del objetivo; usa --aplicar solo si aceptas el cambio")
        return 1

    if aplicar:
        for c in CATEGORIAS:
            with open(FINAL_DIR / f"{c}_final_limpio.json", "w", encoding="utf-8") as f:
                json.dump(aplicado[c], f, ensure_ascii=False, indent=2)
        with open(EXCEPCIONES, "w", encoding="utf-8") as f:
            json.dump(excepciones, f, ensure_ascii=False, indent=2)
        print("[OK] finales y excepciones escritos")
    return 0


if __name__ == "__main__":
    sys.exit(main())