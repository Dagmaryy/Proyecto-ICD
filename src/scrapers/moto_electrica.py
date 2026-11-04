"""Descarga y procesa detalles de motos eléctricas de La Habana desde Revolico.

Reutiliza `revolico.py` sin modificarlo. Toma los candidatos de
`data/processed/final/motos_final_limpio.json` (filtrados a La Habana),
descarga sus detalles en `cache_detalle/motos_electricas/`, descarta los anuncios
borrados/expirados/ilegibles y procesa los válidos con `procesar_detalles`.

Uso:
    python -u src/scrapers/moto_electrica.py --max 5
    python -u src/scrapers/moto_electrica.py --dry-run
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
from scrapers.reglas_limpieza import generar_limpios_500

CATEGORIA = "motos_electricas"
PROVINCIA_LA_HABANA = "1"
MAX_VALIDOS = 500

CACHE_DETALLE = BASE_DIR / "data/raw/web/revolico/cache_detalle" / CATEGORIA

RUTA_FINAL_LIMPIO = BASE_DIR / "data/processed/final/motos_final_limpio.json"
RUTA_PROCESADOS = BASE_DIR / "data/processed/final/motos_electricas_procesadas.json"
RUTA_DESCARTADOS = BASE_DIR / "data/processed/final/motos_electricas_descartados.json"

MOTIVO_BORRADO = "borrado"
MOTIVO_EXPIRADO = "expirado"
MOTIVO_ERROR_DESCARGA = "error_descarga"
MOTIVO_DETALLE_INVALIDO = "detalle_invalido"

ERRORCODES_BORRADO = (
    "cant-see-deleted-ad",
    "unpublished-ad",
    "deleted-ad",
)

CAMPOS_OBLIGATORIOS_MOTO_ELECTRICA = (
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


def _cargar_procesados_existentes() -> dict[str, dict]:
    if not RUTA_PROCESADOS.exists():
        return {}
    with open(RUTA_PROCESADOS, encoding="utf-8") as f:
        registros = json.load(f)
    return {str(registro.get("id_anuncio")): registro for registro in registros}


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
    """Descarga candidatos hasta que motos_electricas_procesadas.json alcance 300 o se agote el límite."""
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

        # Detalle válido: añadir a candidatos para procesar
        registro_valido = dict(registro)
        registro_valido["url_detalle"] = registro["url_detalle"]
        validos.append(registro_valido)
        _volcar_progreso(validos, descartados, RUTA_DESCARTADOS)

    return validos


def procesar_y_guardar(candidatos_detalle: list[dict], descartados: dict[str, dict]) -> None:
    """Procesa detalles válidos con procesar_detalles y actualiza motos_electricas_procesadas.json."""
    if not candidatos_detalle:
        print("[AVISO] No hay detalles válidos para procesar.")
        _guardar_json(RUTA_DESCARTADOS, list(descartados.values()))
        return

    existentes = _cargar_procesados_existentes()
    urls_existentes = set()
    for reg in existentes.values():
        url = reg.get("url_anuncio") or reg.get("url_detalle")
        if url:
            urls_existentes.add(url)

    nuevos_a_procesar = []
    for registro in candidatos_detalle:
        url = registro.get("url_detalle")
        if url and url in urls_existentes:
            continue
        nuevos_a_procesar.append(registro)

    if not nuevos_a_procesar:
        print("[AVISO] Todos los detalles válidos ya están en procesados.")
        _guardar_json(RUTA_DESCARTADOS, list(descartados.values()))
        return

    resultado = procesar_detalles("motos_electricas", anuncios=nuevos_a_procesar)
    nuevos_validos = resultado.get("validos_completos", [])

    # Añadir al conjunto existente
    for reg in nuevos_validos:
        idd = reg.get("id_anuncio") or _id_desde_url(reg.get("url_anuncio", ""))
        if idd:
            existentes[idd] = reg

    _guardar_json(RUTA_PROCESADOS, list(existentes.values()))
    print(f"[OK] Procesados guardados: {len(existentes)} en {RUTA_PROCESADOS}")
    _guardar_json(RUTA_DESCARTADOS, list(descartados.values()))


def main() -> int:
    parser = argparse.ArgumentParser(description="Descarga y procesa detalles de motos eléctricas")
    parser.add_argument("--max", type=int, default=0, help="Máximo de peticiones nuevas (0 = sin límite)")
    parser.add_argument("--dry-run", action="store_true", help="Solo mostrar qué se descargaría")
    args = parser.parse_args()

    CACHE_DETALLE.mkdir(parents=True, exist_ok=True)
    RUTA_PROCESADOS.parent.mkdir(parents=True, exist_ok=True)

    print(f"[INFO] Candidatos: {RUTA_FINAL_LIMPIO}")
    print(f"[INFO] Procesados: {RUTA_PROCESADOS}")
    print(f"[INFO] Descartados: {RUTA_DESCARTADOS}")
    print(f"[INFO] Cache detalle: {CACHE_DETALLE}")

    candidatos = cargar_candidatos()
    print(f"[INFO] Candidatos Habana: {len(candidatos)}")

    descartados = cargar_descartados_previos()
    print(f"[INFO] Descartados previos: {len(descartados)}")

    limite_nuevas = args.max if args.max > 0 else MAX_PETICIONES
    validos_detalle = descargar_validos(candidatos, limite_nuevas, descartados, args.dry_run)

    if args.dry_run:
        print(f"[DRY-RUN] {len(validos_detalle)} detalles válidos listos para procesar")
        return 0

    procesar_y_guardar(validos_detalle, descartados)
    resumen = generar_limpios_500(categorias=(CATEGORIA,))
    print(
        f"[LIMPIO] {CATEGORIA}: {resumen.get(CATEGORIA, 0)} registros "
        f"en {CATEGORIA}_500_limpio.json"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
