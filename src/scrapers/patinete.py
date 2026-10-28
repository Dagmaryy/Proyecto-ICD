"""Descarga y procesa detalles de patinetes de La Habana desde Revolico.

Reutiliza `revolico.py` sin modificarlo. Toma los candidatos de
`data/processed/patinetes_candidatos.json` (filtrados a La Habana),
descarga sus detalles en `cache_detalle/patinetes/`, descarta los anuncios
borrados/expirados/ilegibles y procesa los válidos con `procesar_detalles`.

Uso:
    python -u src/scrapers/patinete.py --max 5
    python -u src/scrapers/patinete.py --dry-run
"""

import argparse
import json
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import scrapers.revolico as rv
from scrapers.revolico import (
    BASE_DIR,
    MAX_PETICIONES,
    descargar_detalle,
    procesar_detalles,
    _extraer_json_next,
)

CATEGORIA = "patinetes"
PROVINCIA_LA_HABANA = "1"
MAX_VALIDOS = 300

CACHE_DETALLE = BASE_DIR / "data/raw/web/revolico/cache_detalle" / CATEGORIA

RUTA_FINAL_LIMPIO = BASE_DIR / "data/processed/final/patinetes_candidatos.json"
RUTA_PROCESADOS = BASE_DIR / "data/processed/final/patinetes_procesados.json"
RUTA_DESCARTADOS = BASE_DIR / "data/processed/final/patinetes_descartados.json"

MOTIVO_BORRADO = "borrado"
MOTIVO_EXPIRADO = "expirado"
MOTIVO_ERROR_DESCARGA = "error_descarga"
MOTIVO_DETALLE_INVALIDO = "detalle_invalido"

ERRORCODES_BORRADO = (
    "cant-see-deleted-ad",
    "unpublished-ad",
    "deleted-ad",
)

CAMPOS_OBLIGATORIOS_BICI = (
    "id_anuncio",
    "titulo",
    "precio_usd",
    "url_anuncio",
    "tipo_vehiculo",
    "descripcion",
    "motor_w",
    "tipo_bateria",
    "autonomia_km",
    "ubicacion",
)


def _ahora_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _id_desde_url(url: str) -> str:
    return url.rstrip("/").rsplit("-", 1)[-1]


def cargar_candidatos() -> list[dict]:
    """Candidatos de La Habana del listado final limpio."""
    with open(RUTA_FINAL_LIMPIO, encoding="utf-8") as f:
        registros = json.load(f)
    return [
        registro
        for registro in registros
        if str(registro.get("provinceId")) == PROVINCIA_LA_HABANA
    ]


def cargar_descartados_previos() -> dict[str, dict]:
    """Descartados ya guardados, indexados por id (para no duplicar)."""
    if not RUTA_DESCARTADOS.exists():
        return {}
    with open(RUTA_DESCARTADOS, encoding="utf-8") as f:
        previos = json.load(f)
    return {str(item.get("id")): item for item in previos}


def _guardar_json(ruta: Path, datos) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    temporal = ruta.with_suffix(ruta.suffix + ".tmp")
    with open(temporal, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
    temporal.replace(ruta)


def _crear_descartado(registro: dict, motivo: str, extra: dict = None) -> dict:
    item = {
        "url_detalle": registro.get("url_detalle"),
        "id": _id_desde_url(registro.get("url_detalle", "")),
        "titulo": registro.get("titulo"),
        "precio_usd": registro.get("precio_usd"),
        "motivo": motivo,
        "fecha_intento": _ahora_iso(),
    }
    if extra:
        item.update(extra)
    return item


def clasificar_estado(html: str) -> str | None:
    """Motivo de descarte según el HTML, o None si el detalle es válido."""
    datos = _extraer_json_next(html)
    page_props = datos.get("props", {}).get("pageProps", {})
    error_code = page_props.get("errorCode")
    if error_code in ERRORCODES_BORRADO:
        return MOTIVO_BORRADO
    for clave, valor in page_props.get("__APOLLO_STATE__", {}).items():
        if clave.startswith("AdType:"):
            if valor.get("status") == "EXPIRED":
                return MOTIVO_EXPIRADO
            return None
    # Sin AdType: no es un detalle procesable (errorCode desconocido o vacío).
    return MOTIVO_DETALLE_INVALIDO


def _volcar_progreso(
    validos: list[dict], descartados: dict[str, dict], descartados_path: Path
) -> None:
    _guardar_json(descartados_path, list(descartados.values()))


def descargar_validos(
    candidatos: list[dict],
    limite_nuevas: int,
    descartados: dict[str, dict],
    dry_run: bool = False,
) -> list[dict]:
    """Descarga candidatos hasta que bicis_procesados.json alcance 300 o se agote el límite."""
    peticiones_iniciales = rv._contador_peticiones
    validos: list[dict] = []

    for registro in candidatos:
        # Parar cuando ya haya 300 procesados
        existentes = _cargar_procesados_existentes()
        if len(existentes) >= MAX_VALIDOS:
            print(f"[FIN] Alcanzados {MAX_VALIDOS} procesados.")
            break

        idd = _id_desde_url(registro.get("url_detalle", ""))
        en_cache = (CACHE_DETALLE / f"detalle_{idd}.html").exists()

        if not en_cache:
            peticiones_nuevas = rv._contador_peticiones - peticiones_iniciales
            if peticiones_nuevas >= limite_nuevas:
                print(f"[LIMITE] Alcanzado el límite de {limite_nuevas} peticiones nuevas.")
                break
            if rv._contador_peticiones >= MAX_PETICIONES:
                print(f"[LIMITE] Alcanzado el límite global de {MAX_PETICIONES} peticiones.")
                break

        if dry_run:
            print(f"[dry-run] descargaría {registro.get('url_detalle')}")
            continue

        try:
            html = descargar_detalle(registro["url_detalle"], CATEGORIA)
        except RuntimeError as exc:
            mensaje = str(exc)
            if "Límite de" in mensaje:
                print(f"[LIMITE] {mensaje}")
                break
            print(f"[ERROR] {registro.get('url_detalle')}: {mensaje}")
            descartados.setdefault(
                idd, _crear_descartado(registro, MOTIVO_ERROR_DESCARGA, {"error": mensaje})
            )
            _volcar_progreso(validos, descartados, RUTA_DESCARTADOS)
            continue

        try:
            motivo = clasificar_estado(html)
        except (ValueError, KeyError, json.JSONDecodeError) as exc:
            motivo = MOTIVO_ERROR_DESCARGA
            descartados.setdefault(
                idd, _crear_descartado(registro, motivo, {"error": f"detalle_ilegible: {exc}"})
            )
            _volcar_progreso(validos, descartados, RUTA_DESCARTADOS)
            continue

        if motivo is not None:
            print(f"[DESCARTADO:{motivo}] {registro.get('url_detalle')}")
            descartados.setdefault(idd, _crear_descartado(registro, motivo))
            _volcar_progreso(validos, descartados, RUTA_DESCARTADOS)
            continue

        # Evitar reprocesar si ya existe en procesados
        if idd in existentes:
            continue

        validos.append(registro)
        print(f"[VALIDO] {registro.get('url_detalle')} ({len(validos)} válidos)")

    return validos


def _cargar_procesados_existentes() -> dict[str, dict]:
    if not RUTA_PROCESADOS.exists():
        return {}
    try:
        with open(RUTA_PROCESADOS, encoding="utf-8") as f:
            datos = json.load(f)
        return {str(item.get("id_anuncio")): item for item in datos}
    except Exception:
        return {}


def procesar_validos(validos: list[dict], descartados: dict[str, dict]) -> None:
    """Procesa los válidos con procesar_detalles y guarda los resultados (acumulativo)."""
    existentes = _cargar_procesados_existentes()

    if not validos:
        _guardar_json(RUTA_PROCESADOS, list(existentes.values()))
        _volcar_progreso(validos, descartados, RUTA_DESCARTADOS)
        return

    # Solo procesar los que aún no estén en procesados
    nuevos_a_procesar = []
    for registro in validos:
        idd = _id_desde_url(registro.get("url_detalle", ""))
        if idd not in existentes:
            nuevos_a_procesar.append(registro)

    if not nuevos_a_procesar:
        _guardar_json(RUTA_PROCESADOS, list(existentes.values()))
        _volcar_progreso(validos, descartados, RUTA_DESCARTADOS)
        print(f"[PROCESADO] nuevos=0 acumulados={len(existentes)}")
        return

    with tempfile.NamedTemporaryFile(
        "w", suffix=".json", delete=False, encoding="utf-8"
    ) as tmp:
        json.dump(nuevos_a_procesar, tmp, ensure_ascii=False)
        ruta_muestra = tmp.name

    try:
        resultado = procesar_detalles(CATEGORIA, ruta_muestra=ruta_muestra)
    finally:
        Path(ruta_muestra).unlink(missing_ok=True)

    anuncios = resultado["validos_completos"] + resultado["validos_parciales"]
    for anuncio in anuncios:
        idd = str(anuncio.get("id_anuncio"))
        if idd:
            existentes[idd] = anuncio

    _guardar_json(RUTA_PROCESADOS, list(existentes.values()))

    by_id = {_id_desde_url(registro["url_detalle"]): registro for registro in nuevos_a_procesar}
    for descarte in resultado["descartados"]:
        anuncio = descarte.get("anuncio", {})
        idd = str(anuncio.get("id_anuncio") or "")
        if not idd or idd in descartados:
            continue
        registro = by_id.get(idd, {})
        item = {
            "url_detalle": registro.get("url_detalle") or anuncio.get("url_anuncio"),
            "id": idd,
            "titulo": anuncio.get("titulo") or registro.get("titulo"),
            "precio_usd": anuncio.get("precio_usd") or registro.get("precio_usd"),
            "motivo": MOTIVO_DETALLE_INVALIDO,
            "fecha_intento": _ahora_iso(),
            "campos_faltantes": descarte.get("campos_faltantes"),
        }
        descartados[idd] = item
    _volcar_progreso(nuevos_a_procesar, descartados, RUTA_DESCARTADOS)

    print(
        f"[PROCESADO] nuevos={len(anuncios)} acumulados={len(existentes)} "
        f"(completos={len(resultado['validos_completos'])}, "
        f"parciales={len(resultado['validos_parciales'])}) "
        f"descartados_nuevos={len(resultado['descartados'])}"
    )


def reprocesar_cache() -> int:
    """Reprocesa todos los detalles en caché sin hacer peticiones nuevas."""
    descartados = cargar_descartados_previos()
    existentes = _cargar_procesados_existentes()

    archivos = sorted(CACHE_DETALLE.glob("detalle_*.html"))
    print(f"[REPROCESAR] {len(archivos)} detalles en caché")

    validos_candidatos = []
    for ruta in archivos:
        idd = ruta.stem.replace("detalle_", "")
        try:
            html = ruta.read_text(encoding="utf-8")
            motivo = clasificar_estado(html)
        except Exception as exc:
            motivo = MOTIVO_DETALLE_INVALIDO
            if idd not in descartados:
                descartados[idd] = {
                    "url_detalle": None,
                    "id": idd,
                    "titulo": None,
                    "precio_usd": None,
                    "motivo": MOTIVO_DETALLE_INVALIDO,
                    "fecha_intento": _ahora_iso(),
                    "error": f"cache_ilegible: {exc}",
                }
            continue

        if motivo is not None:
            if idd not in descartados:
                descartados[idd] = {
                    "url_detalle": None,
                    "id": idd,
                    "titulo": None,
                    "precio_usd": None,
                    "motivo": motivo,
                    "fecha_intento": _ahora_iso(),
                }
            continue

        # Intentar obtener info mínima del candidato original si existe
        registro = {"url_detalle": f"https://www.revolico.com/item/x-{idd}"}
        validos_candidatos.append(registro)

    # Procesar todos los válidos encontrados en caché
    if not validos_candidatos:
        _guardar_json(RUTA_PROCESADOS, list(existentes.values()))
        _volcar_progreso([], descartados, RUTA_DESCARTADOS)
        print(f"[TOTAL] válidos acumulados: {len(existentes)}")
        return 0

    with tempfile.NamedTemporaryFile(
        "w", suffix=".json", delete=False, encoding="utf-8"
    ) as tmp:
        json.dump(validos_candidatos, tmp, ensure_ascii=False)
        ruta_muestra = tmp.name

    try:
        resultado = procesar_detalles(CATEGORIA, ruta_muestra=ruta_muestra)
    finally:
        Path(ruta_muestra).unlink(missing_ok=True)

    anuncios = resultado["validos_completos"] + resultado["validos_parciales"]
    for anuncio in anuncios:
        idd = str(anuncio.get("id_anuncio"))
        if idd:
            existentes[idd] = anuncio

    _guardar_json(RUTA_PROCESADOS, list(existentes.values()))

    by_id = {_id_desde_url(r["url_detalle"]): r for r in validos_candidatos}
    for descarte in resultado["descartados"]:
        anuncio = descarte.get("anuncio", {})
        idd = str(anuncio.get("id_anuncio") or "")
        if not idd or idd in descartados:
            continue
        registro = by_id.get(idd, {})
        item = {
            "url_detalle": anuncio.get("url_anuncio") or registro.get("url_detalle"),
            "id": idd,
            "titulo": anuncio.get("titulo"),
            "precio_usd": anuncio.get("precio_usd"),
            "motivo": MOTIVO_DETALLE_INVALIDO,
            "fecha_intento": _ahora_iso(),
            "campos_faltantes": descarte.get("campos_faltantes"),
        }
        descartados[idd] = item

    _volcar_progreso([], descartados, RUTA_DESCARTADOS)
    print(
        f"[PROCESADO] nuevos={len(anuncios)} acumulados={len(existentes)} "
        f"(completos={len(resultado['validos_completos'])}, "
        f"parciales={len(resultado['validos_parciales'])})"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Descarga y procesa detalles de patinetes.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Solo cuenta los candidatos a descargar, sin hacer peticiones.",
    )
    parser.add_argument(
        "--max",
        type=int,
        default=None,
        help=f"Máximo de peticiones nuevas en esta ejecución (por defecto {MAX_PETICIONES}).",
    )
    parser.add_argument(
        "--reprocesar-cache",
        action="store_true",
        help="Reprocesa todos los detalles en caché sin hacer peticiones nuevas.",
    )
    args = parser.parse_args(argv)

    if args.reprocesar_cache:
        return reprocesar_cache()

    candidatos = cargar_candidatos()
    limite = args.max if args.max is not None else MAX_PETICIONES
    existentes = _cargar_procesados_existentes()
    print(f"Candidatos de La Habana: {len(candidatos)} (límite de peticiones: {limite}) | procesados: {len(existentes)}")

    if args.dry_run:
        print(f"[dry-run] candidatos a intentar: {min(len(candidatos), limite)}")
        return 0

    descartados = cargar_descartados_previos()
    validos = descargar_validos(candidatos, limite, descartados)
    print(f"[TOTAL] válidos descargados en esta ejecución: {len(validos)}")
    procesar_validos(validos, descartados)
    existentes = _cargar_procesados_existentes()
    print(f"[FINAL] procesados={len(existentes)} faltan={max(0, MAX_VALIDOS-len(existentes))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
