"""Post-procesamiento por reglas para los anuncios de Revolico.

Genera un JSON con exactamente siete campos:
marca, precio, municipio, papeles, uso, transporte y vendedores.

No usa IA ni modifica `data/raw/`.
"""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
FINAL_DIR = BASE_DIR / "data/processed/final"

CAMPOS_SALIDA = (
    "marca",
    "precio",
    "municipio",
    "papeles",
    "uso",
    "transporte",
    "vendedores",
)

CATEGORIAS_FUENTES = {
    "motos_electricas": (
        "motos_electricas_procesadas.json",
        "motos_final_limpio.json",
    ),
    "motos_combustion": (
        "motos_combustion_procesadas.json",
        "motos_combustion_candidatos_cache.json",
    ),
    "bicis": ("bicis_procesados.json", "bicis_final_limpio.json"),
    "patinetes": ("patinetes_procesados.json", "patinetes_candidatos.json"),
}

MARCAS_COMUNES = (
    (r"\bizuki\b", "Izuki"),
    (r"yoazaky|yoazaki|yoazak|yoa ?zaky|yoa ?zaki", "Yoazaki"),
    (r"\be\s?bike\b|\bebike\b", "E-bike"),
    (r"\bhalcon\b", "Halcón"),
    (r"\bmishozuki\b", "Mishozuki"),
    (r"\bpanda\b", "Panda"),
    (r"\btopmaq\b", "Topmaq"),
    (r"\bvedca\b", "Vedca"),
    (r"\bxmox\b", "Xmox"),
    (r"kvitova|kivitova|kitova", "Kvitova"),
    (r"bucatt?i|buccati", "Bucatti"),
    (r"\bmikazuki\b|\bmikasuki\b", "Mikazuki"),
    (r"\bmountain\b", "Mountain"),
    (r"\bmaf\b", "Maf"),
    (r"\bmaox\b", "Maox"),
    (r"\btorvan\b", "Torvan"),
    (r"\bfly\b", "Fly"),
    (r"\bdcmlz\b|\bdcmzl\b", "DCM-LZ"),
    (r"protenzza|protenza|prontenza|prontezza", "Protenzza"),
    (r"\bmurasaki\b|\bmurazaki\b", "Murasaki"),
    (r"\bvoltax\b", "Voltax"),
    (r"\bvolta\b", "Volta"),
    (r"\bmeacon\b", "Meacon"),
    (r"\bmidha\b", "Midha"),
    (r"\blaituning\b", "Laituning"),
    (r"\bxindi\b", "Xindi"),
    (r"\bcaroma\b", "Caroma"),
    (r"\bgalaxy\b", "Galaxy"),
    (r"\bsocling\b", "Socling"),
    (r"\bportobello\b", "Portobello"),
    (r"\bdyu\b", "DYU"),
    (r"\bsegway\b", "Segway"),
    (r"\bninebot\b", "Ninebot"),
    (r"\bjmd\b", "JMD"),
    (r"\broinside\b", "Roinside"),
    (r"\bsuzuki\b", "Suzuki"),
    (r"\bhonda\b", "Honda"),
    (r"\byamaha\b", "Yamaha"),
    (r"\bkawasaki\b", "Kawasaki"),
    (r"\bducati\b", "Ducati"),
    (r"\bbmw\b", "BMW"),
    (r"\bpulsar\b", "Pulsar"),
    (r"\bcbr\b", "CBR"),
    (r"\bjialing\b", "Jialing"),
    (r"\blifan\b", "Lifan"),
    (r"\bzongshen\b", "Zongshen"),
    (r"\bbajaj\b", "Bajaj"),
    (r"\btornado\b", "Tornado"),
    (r"\bninja\b", "Ninja"),
    (r"\bava\b", "Ava"),
    (r"\bcorcoveo\b", "Corcoveo"),
)

PATRONES_PAPELES = (
    r"\bpapeles\b",
    r"\blegal\b",
    r"\bfacturas?\b",
)

PATRONES_USO = (
    (r"\btrabajos?\b", "trabajo"),
    (r"\bmensajeria\b", "mensajería"),
    (r"\bpersonal\b", "personal"),
)

PATRONES_TRANSPORTE = (
    r"\btransportes?\b",
    r"\benvios?\b",
    r"\bmensajeria\b",
)

NEGACION_PAPELES = re.compile(
    r"\b(?:sin|no\s+tiene|no\s+posee|no\s+incluye)\s+"
    r"(?:los\s+|las\s+)?(?:papeles|documentos|facturas?)\b"
)

NEGACION_TRANSPORTE = re.compile(
    r"\b(?:sin|no\s+incluye|no\s+tiene|no\s+hay)\s+"
    r"(?:el\s+|la\s+)?(?:transporte|envio)\b"
    r"|\btransporte\s+no\s+incluido\b"
)


def _normalizar(texto) -> str:
    """Minúsculas, sin acentos, sin puntuación y con espacios colapsados."""
    plano = unicodedata.normalize("NFKD", (texto or "").lower())
    plano = plano.encode("ascii", "ignore").decode("ascii")
    plano = re.sub(r"[^a-z0-9]+", " ", plano)
    return re.sub(r"\s+", " ", plano).strip()


def _marca_vacia(marca) -> bool:
    if marca is None:
        return True
    texto = str(marca).strip()
    return not texto or texto.lower() in {"none", "null", "nan"}


def detectar_marca(titulo: str, marca=None):
    """Mantiene la marca existente; si está vacía, la busca en el título."""
    if not _marca_vacia(marca):
        return marca
    texto = _normalizar(titulo)
    for patron, canonica in MARCAS_COMUNES:
        if re.search(patron, texto):
            return canonica
    return None


def _coincide(texto: str, patrones) -> bool:
    return any(re.search(patron, texto) for patron in patrones)


def detectar_papeles(descripcion: str) -> bool:
    """True si la descripción menciona papeles, legal o factura."""
    texto = _normalizar(descripcion)
    if NEGACION_PAPELES.search(texto):
        return False
    return _coincide(texto, PATRONES_PAPELES)


def detectar_uso(descripcion: str):
    """Devuelve el primer uso encontrado: trabajo, mensajería o personal."""
    texto = _normalizar(descripcion)
    for patron, etiqueta in PATRONES_USO:
        if re.search(patron, texto):
            return etiqueta
    return None


def detectar_transporte(descripcion: str) -> bool:
    """True si la descripción menciona transporte, envío o mensajería."""
    texto = _normalizar(descripcion)
    if NEGACION_TRANSPORTE.search(texto):
        return False
    return _coincide(texto, PATRONES_TRANSPORTE)


def _cargar_json(ruta: Path):
    if not ruta.exists():
        return []
    with open(ruta, encoding="utf-8") as archivo:
        return json.load(archivo)


def _guardar_json(ruta: Path, datos) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    temporal = ruta.with_suffix(ruta.suffix + ".tmp")
    with open(temporal, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=2)
    temporal.replace(ruta)


def _id_desde_url(url) -> str:
    return str(url or "").rstrip("/").rsplit("-", 1)[-1]


def construir_mapa_ubicaciones() -> dict:
    """Construye mapas id→nombre usando candidatos y procesados ya existentes."""
    municipios: dict[str, str] = {}
    provincias: dict[str, str] = {}

    for nombre_procesados, nombre_candidatos in CATEGORIAS_FUENTES.values():
        procesados = _cargar_json(FINAL_DIR / nombre_procesados)
        candidatos = _cargar_json(FINAL_DIR / nombre_candidatos)
        por_id = {
            str(registro.get("id_anuncio")): registro for registro in procesados
        }

        for candidato in candidatos:
            url = candidato.get("url_detalle") or candidato.get("url_anuncio")
            procesado = por_id.get(_id_desde_url(url))
            if not procesado:
                continue

            municipality_id = candidato.get("municipalityId")
            municipality_name = procesado.get("municipio")
            if municipality_id is not None and municipality_name:
                municipios.setdefault(str(municipality_id), municipality_name)

            province_id = candidato.get("provinceId")
            province_name = procesado.get("ubicacion")
            if province_id is not None and province_name:
                provincias.setdefault(str(province_id), province_name)

    return {"municipios": municipios, "provincias": provincias}


def resolver_municipio(registro: dict, mapas: dict | None = None):
    """Resuelve el municipio desde el nombre, municipalityId o provinceId."""
    mapas = mapas or {}
    actual = registro.get("municipio")
    if actual not in (None, ""):
        texto = str(actual).strip()
        if texto.isdigit():
            return mapas.get("municipios", {}).get(texto) or texto
        return texto

    municipality_id = registro.get("municipalityId")
    if municipality_id is not None:
        nombre = mapas.get("municipios", {}).get(str(municipality_id))
        if nombre:
            return nombre

    province_id = registro.get("provinceId")
    if province_id is not None:
        return mapas.get("provincias", {}).get(str(province_id))

    return None


def construir_registro_limpio(registro: dict, mapas: dict | None = None) -> dict:
    """Devuelve exactamente los siete campos solicitados."""
    descripcion = registro.get("descripcion") or ""
    return {
        "marca": detectar_marca(registro.get("titulo"), registro.get("marca")),
        "precio": registro.get("precio_usd"),
        "municipio": resolver_municipio(registro, mapas),
        "papeles": detectar_papeles(descripcion),
        "uso": detectar_uso(descripcion),
        "transporte": detectar_transporte(descripcion),
        "vendedores": registro.get("vendedor_id"),
    }


def procesar_categoria(
    categoria: str,
    limite: int = 500,
    mapas: dict | None = None,
    ruta_procesados: Path | None = None,
    ruta_salida: Path | None = None,
) -> list[dict]:
    """Lee los procesados de una categoría y escribe su *_500_limpio.json."""
    if categoria not in CATEGORIAS_FUENTES:
        raise ValueError(
            f"Categoría desconocida: {categoria!r}. "
            f"Usa una de {tuple(CATEGORIAS_FUENTES)}."
        )

    nombre_procesados, _ = CATEGORIAS_FUENTES[categoria]
    origen = Path(ruta_procesados) if ruta_procesados else FINAL_DIR / nombre_procesados
    registros = _cargar_json(origen)
    mapas = mapas or construir_mapa_ubicaciones()

    salida = []
    vistos = set()
    for registro in registros:
        clave = str(
            registro.get("id_anuncio")
            or registro.get("url_anuncio")
            or registro.get("url_detalle")
            or ""
        )
        if clave:
            if clave in vistos:
                continue
            vistos.add(clave)

        salida.append(construir_registro_limpio(registro, mapas))
        if limite and len(salida) >= limite:
            break

    destino = (
        Path(ruta_salida)
        if ruta_salida
        else FINAL_DIR / f"{categoria}_500_limpio.json"
    )
    _guardar_json(destino, salida)
    return salida


def generar_limpios_500(
    categorias=None,
    limite: int = 500,
    directorio_salida: Path | None = None,
) -> dict[str, int]:
    """Genera los JSON finales de las categorías indicadas."""
    mapas = construir_mapa_ubicaciones()
    resumen: dict[str, int] = {}

    for categoria in categorias or tuple(CATEGORIAS_FUENTES):
        ruta_salida = None
        if directorio_salida is not None:
            ruta_salida = Path(directorio_salida) / f"{categoria}_500_limpio.json"
        registros = procesar_categoria(
            categoria,
            limite=limite,
            mapas=mapas,
            ruta_salida=ruta_salida,
        )
        resumen[categoria] = len(registros)

    return resumen
