"""Descarga y procesa detalles de motos de combustión de La Habana desde Revolico.

Reutiliza `revolico.py` sin modificarlo. Toma los candidatos de listados
cacheados (y búsquedas) filtrados estrictamente para combustión, descarga
sus detalles en `cache_detalle/motos/`, descarta los anuncios
borrados/expirados/ilegibles y procesa los válidos con el esquema de combustión.

Uso:
    python -u src/scrapers/moto_combustion.py --max 5
    python -u src/scrapers/moto_combustion.py --dry-run
"""

import argparse
import json
import re
import sys
import tempfile
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import scrapers.revolico as rv
from scrapers.revolico import (
    BASE_DIR,
    MAX_PETICIONES,
    descargar_detalle,
    _extraer_json_next,
)

CATEGORIA = "motos"
PROVINCIA_LA_HABANA = "1"
MAX_VALIDOS = 300

CACHE_DETALLE = BASE_DIR / "data/raw/web/revolico/cache_detalle" / CATEGORIA

RUTA_FINAL_LIMPIO = BASE_DIR / "data/processed/final/motos_combustion_candidatos_cache.json"
RUTA_PROCESADOS = BASE_DIR / "data/processed/final/motos_combustion_procesadas.json"
RUTA_DESCARTADOS = BASE_DIR / "data/processed/final/motos_combustion_descartados.json"
RUTA_OUTLIERS = BASE_DIR / "data/processed/final/motos_combustion_outliers.json"
RUTA_ESQUEMA_COMBUSTION = (
    BASE_DIR / "docs/schemas/esquema_moto_combustion.json"
)
PRECIO_MIN_USD = 100
PRECIO_MAX_USD = 5000

CAMPOS_OBLIGATORIOS_COMBUSTION = (
    "id_anuncio",
    "titulo",
    "precio_usd",
    "url_anuncio",
    "tipo_vehiculo",
    "descripcion",
    "ubicacion",
    "combustible",
)
CAMPOS_PARCIALES_COMBUSTION = (
    "id_anuncio",
    "titulo",
    "precio_usd",
    "url_anuncio",
    "tipo_vehiculo",
    "descripcion",
)

MOTIVO_BORRADO = "borrado"
MOTIVO_EXPIRADO = "expirado"
MOTIVO_ERROR_DESCARGA = "error_descarga"
MOTIVO_DETALLE_INVALIDO = "detalle_invalido"

ERRORCODES_BORRADO = (
    "cant-see-deleted-ad",
    "unpublished-ad",
    "deleted-ad",
)

_ACCESORIOS = (
    "inversor",
    "cargador",
    "lampara",
    "luces solares",
    "panel solar",
    "alarma",
    "capas",
    "cubierta",
    "funda",
    "repuesto",
    "accesorio",
    "controlador",
    "bocina",
    "combo de motor",
    "motor de 2500w",
    "motor de 1500w",
    "motor de 1800w",
    "motor d unico",
)
# Piezas que se anuncian como "para moto automática 4T" y que no son motos.
# Se revisan en el título para no dejar pasar repuestos que mencionan 4T/cc.
_TITULO_PARTE = (
    "filtro de aire",
    "filtro de gasolina",
    "filtros de gasolina",
    "filtro gasolina",
    "filtro",
    "tanque de gasolina",
    "tanques de gasolina",
    "tanque para combustible",
    "tanques para gasolina",
    "tanques para combustible",
    "bomba manual",
    "bombeta",
    "extractor de combustible",
    "velocimetro",
    "aceite de motor",
    "gasolina super especial",
    "manguera",
    "bateria",
    "embudo",
    "ciguenal",
    "compresion",
    "tornilleria",
    "tapa de valvula",
    "tapa valvula",
    "tapa de aceite",
    "tapa del diferencial",
    "tapa lateral",
    "caballitos",
    "rodamientos",
    "bolanta",
    "guitarra",
    "manifor",
    "arbol de levas",
    "motor de arranque",
    "vareador",
    "cloche",
    "tensor de cadena",
    "medidor de aceite",
    "valvulas",
    "patines",
    "encendido",
    "cadena distribucion",
    "kit de junta",
    "spra",
    "separa el agua",
    "mas piezas",
    "para moto automatica",
    "para moto automatico",
    "para motocicleta",
)
_TITULO_INICIO_PARTE = (
    "tanque",
    "tanques",
    "bomba",
    "bombeta",
    "extractor",
    "velocimetro",
    "filtro",
    "goma",
    "gomas",
    "foco",
    "focos",
    "llanta",
    "llantas",
    "neumatico",
    "neumaticos",
    "aceite",
    "aceites",
    "reten",
    "retenes",
    "miller",
    "milleros",
    "chucho",
    "correa",
    "correas",
    "cable",
    "cables",
    "buje",
    "bujes",
    "conmutador",
    "conmutadores",
    "flotante",
    "transmision",
    "tapa",
    "sistema",
    "kit",
)
_TITULO_INMUEBLE = (
    "apto en",
    "apartamento",
    "casa puerta de calle",
    "incluye una moto",
    "incluyendo una moto",
    "se incluye una moto",
    "se incluye moto",
)
_OTROS_VEHICULOS = (
    "bicimoto",
    "bicicleta",
    "patinete",
    "patineta",
    "scooter electrico",
)
_NO_VENTA = (
    "cambio pc",
    "busco",
    "compro",
    "se compra",
    "por encargo",
    "renta",
    "rentar",
    "alquiler",
)
_ELECTRICO = (
    "moto electrica",
    "motico electrico",
    "electrico",
    "electrica",
    "electric",
    "litio",
    "lifepo4",
    "li ion",
    "moto elec",
    "motico elec",
)
_COMBUSTION = (
    "gasolina",
    "nafta",
    "diesel",
    "combustion",
    "combustible",
    "carburador",
    "cilindrada",
)
_MARCAS_COMBUSTION = (
    "honda",
    "suzuki",
    "yamaha",
    "kawasaki",
    "ducati",
    "bmw",
    "pulsar",
    "cbr",
    "jialing",
    "lifan",
    "zongshen",
    "bajaj",
    "tornado",
    "ninja",
)
_VEHICULO = (
    "moto",
    "motos",
    "motico",
    "moticos",
    "motocicleta",
    "motocicletas",
    "motociclo",
    "motora",
    "motoras",
    "moped",
    "mopeds",
    "scooter",
    "scooters",
    "escuoter",
    "trimoto",
    "triciclo",
    "triciclos",
    "cuatrimoto",
    "cuatrimotos",
    "enduro",
    "pistera",
    "pisteras",
    "ciclomotor",
)
_ELECTRICO_FUERTE = (
    "litio",
    "lifepo4",
    "autonomia",
    "motor 3000",
    "motor 1500",
    "motor 2000",
    "motor 500",
    "3000 wats",
    "1500 wats",
    "2000 wats",
    "bateria de litio",
    "inversor",
    "cargador",
)
_GASOLINA_NEGADA = (
    "cero gasolina",
    "sin gasolina",
    "no gasta gasolina",
    "no usa gasolina",
    "no necesita gasolina",
)


def _ahora_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalizar(texto: str) -> str:
    plano = unicodedata.normalize("NFKD", rv.normalizar_guiones(texto).lower())
    plano = plano.encode("ascii", "ignore").decode("ascii")
    plano = re.sub(r"[^a-z0-9.,]+", " ", plano)
    return re.sub(r"\s+", " ", plano).strip()


def _extraer_cilindrada(texto: str) -> int | None:
    patrones = (
        r"cilindrada\D{0,12}(\d{2,4}(?:\.\d+)?)",
        r"\b(\d{2,4}(?:\.\d+)?)\s*(?:cc|cm3|c c)\b",
        r"\b(\d{2,3}(?:\.\d+)?)\s*(?:semiautomatica|semi automatica)\b",
        r"\b(\d{2,4})\s*rr\b",
    )
    for patron in patrones:
        coincidencia = re.search(patron, texto)
        if not coincidencia:
            continue
        valor = int(float(coincidencia.group(1)))
        if 30 <= valor <= 2000:
            return valor
    return None


def _extraer_kilometraje(texto: str) -> int | None:
    miles = re.search(
        r"\b(\d{1,3}(?:[.,]\d{1,3})?)\s*mil\s*(?:km|kms|kilometros)\b", texto
    )
    if miles:
        valor = int(float(miles.group(1).replace(",", ".")) * 1000)
        return valor if 100 <= valor <= 500000 else None

    coincidencia = re.search(
        r"\b(\d{1,3}(?:[.,\s]\d{3})+|\d{4,6})\s*(?:km|kms|kilometros)\b", texto
    )
    if not coincidencia:
        return None
    contexto = texto[max(0, coincidencia.start() - 30) : coincidencia.start()]
    if "autonomia" in contexto:
        return None
    valor = int(re.sub(r"[.,\s]", "", coincidencia.group(1)))
    return valor if 100 <= valor <= 500000 else None


def extraer_campos_combustion(titulo: str, descripcion: str) -> dict:
    """Extrae cilindrada, combustible y kilometraje de un anuncio de combustión."""
    texto = _normalizar(f"{titulo or ''} {descripcion or ''}")
    cilindrada = _extraer_cilindrada(texto)

    if re.search(r"\b(?:gasolina|nafta)\b", texto):
        combustible = "gasolina"
    elif re.search(r"\bdiesel\b", texto):
        combustible = "diesel"
    elif re.search(r"\b(?:combustion|combustible)\b|\b[24]t\b", texto):
        combustible = "gasolina"
    else:
        combustible = None

    return {
        "cilindrada_cc": cilindrada,
        "combustible": combustible,
        "kilometraje_km": _extraer_kilometraje(texto),
    }


def _tiene_senal_combustion(texto: str) -> bool:
    if any(palabra in texto for palabra in _COMBUSTION):
        return True
    if _extraer_cilindrada(texto) is not None:
        return True
    if re.search(r"\b(?:2t|4t)\b", texto):
        return True
    if "semiautomatica" in texto or "semi automatica" in texto:
        return True
    if any(
        re.search(rf"\b{re.escape(marca)}\b", texto)
        for marca in _MARCAS_COMBUSTION
    ):
        return True
    return False


def _tiene_senal_vehiculo(texto: str) -> bool:
    tokens = set(texto.split())
    return any(palabra in tokens for palabra in _VEHICULO)


def _es_titulo_parte(titulo_norm: str) -> bool:
    if any(titulo_norm.startswith(palabra) for palabra in _TITULO_INICIO_PARTE):
        return True
    if any(palabra in titulo_norm for palabra in _TITULO_PARTE):
        return True
    return any(palabra in titulo_norm for palabra in _TITULO_INMUEBLE)


def es_combustion_real(titulo: str, descripcion: str) -> bool:
    """Decide si el texto corresponde a una moto de combustión real.

    Los accesorios y otros vehículos solo descartan el anuncio si aparecen en
    el título o si la descripción no contiene ninguna señal de combustión. Así
    no se pierden dealers que también venden eléctricas o que listan alarma,
    luces, etc. como equipamiento de una moto de gasolina.
    """
    titulo_norm = _normalizar(titulo)
    texto = _normalizar(f"{titulo or ''} {descripcion or ''}")
    if not texto:
        return False

    if _es_titulo_parte(titulo_norm):
        return False
    if any(palabra in titulo_norm for palabra in _ACCESORIOS):
        return False
    if any(palabra in titulo_norm for palabra in _OTROS_VEHICULOS):
        return False
    if any(palabra in titulo_norm for palabra in _NO_VENTA):
        return False
    if any(palabra in texto for palabra in _GASOLINA_NEGADA):
        return False
    if "elect" in titulo_norm:
        return False
    if any(palabra in titulo_norm for palabra in _ELECTRICO_FUERTE):
        return False
    if re.search(r"\b(?:36|48|60|72|84)\s*(?:v|volt|voltios)\b", titulo_norm):
        return False
    if not _tiene_senal_vehiculo(titulo_norm) and not _tiene_senal_combustion(
        titulo_norm
    ):
        return False

    if _tiene_senal_combustion(titulo_norm):
        return True

    tiene_senal = _tiene_senal_combustion(texto)
    if any(palabra in texto for palabra in _ACCESORIOS) and not tiene_senal:
        return False
    if any(palabra in texto for palabra in _OTROS_VEHICULOS) and not tiene_senal:
        return False
    if any(palabra in texto for palabra in _NO_VENTA):
        return False
    if tiene_senal:
        return True

    if re.search(r"\b(?:36|48|60|72|84)\s*(?:v|volt|voltios)\b", texto):
        return False
    if any(palabra in texto for palabra in _ELECTRICO_FUERTE):
        return False
    if any(palabra in texto for palabra in _ELECTRICO):
        return False
    return False


def _campos_esquema_combustion() -> list[str]:
    with open(RUTA_ESQUEMA_COMBUSTION, encoding="utf-8") as f:
        esquema = json.load(f)
    return list(esquema["anuncios"][0].keys())


def _cargar_catalogos() -> dict:
    listados = sorted((rv.CACHE_DIR / CATEGORIA).glob("listado_*.html"))
    if not listados:
        return {"provincias": {}, "municipios": {}}
    return rv.extraer_catalogos(listados[0].read_text(encoding="utf-8"))


def _extraer_campos_combustion_extra(titulo: str, descripcion: str) -> dict:
    """Extrae campos específicos del esquema de combustión."""
    texto = _normalizar(f"{titulo or ''} {descripcion or ''}")

    tipo_motor = None
    if re.search(r"\b2t\b|\b2 tiempos\b", texto):
        tipo_motor = "2T"
    elif re.search(r"\b4t\b|\b4 tiempos\b", texto):
        tipo_motor = "4T"

    transmision = None
    if "semiautomatica" in texto or "semi automatica" in texto:
        transmision = "semiautomática"
    elif "automatica" in texto:
        transmision = "automática"
    elif "manual" in texto or re.search(r"\b\d\s*velocidades\b", texto):
        transmision = "manual"

    tiene_arranque_electrico = (
        "motor de arranque" in texto or "arranque electrico" in texto
    )
    tiene_pata = bool(re.search(r"\bpata\b|\bpedal\b", texto))
    if tiene_arranque_electrico and tiene_pata:
        tipo_arranque = "eléctrico y patada"
    elif tiene_arranque_electrico:
        tipo_arranque = "eléctrico"
    elif tiene_pata:
        tipo_arranque = "patada"
    else:
        tipo_arranque = None

    anio_fabricacion = None
    for coincidencia in re.finditer(r"\b(19[5-9]\d|20[0-2]\d)\b", texto):
        contexto = texto[max(0, coincidencia.start() - 15) : coincidencia.start()]
        if any(palabra in contexto for palabra in ("precio", "usd", "cuesta", "valor")):
            continue
        valor = int(coincidencia.group(1))
        if valor <= 2026:
            anio_fabricacion = valor if anio_fabricacion is None else max(
                anio_fabricacion, valor
            )

    consumo_l_100km = None
    consumo = re.search(
        r"(\d{1,3}(?:[.,]\d+)?)\s*km\s*(?:/\s*|x\s*|por\s*|\s+)(?:l|litro)s?\b",
        texto,
    )
    if consumo:
        km_por_litro = float(consumo.group(1).replace(",", "."))
        if km_por_litro > 0:
            consumo_l_100km = round(100 / km_por_litro, 2)

    capacidad_tanque_l = None
    tanque = re.search(
        r"(?:tanque|capacidad)\D{0,15}(\d{1,2}(?:[.,]\d+)?)\s*(?:l|litros)\b",
        texto,
    )
    if tanque:
        capacidad_tanque_l = float(tanque.group(1).replace(",", "."))

    return {
        "tipo_motor": tipo_motor,
        "transmision": transmision,
        "tipo_arranque": tipo_arranque,
        "anio_fabricacion": anio_fabricacion,
        "consumo_l_100km": consumo_l_100km,
        "capacidad_tanque_l": capacidad_tanque_l,
    }


def _extraer_marca_combustion(titulo: str, descripcion: str) -> str | None:
    texto = _normalizar(f"{titulo or ''} {descripcion or ''}")
    marcas = (
        ("honda", "Honda"),
        ("suzuki", "Suzuki"),
        ("yamaha", "Yamaha"),
        ("kawasaki", "Kawasaki"),
        ("ducati", "Ducati"),
        ("bmw", "BMW"),
        ("ava", "Ava"),
        ("corcoveo", "Corcoveo"),
        ("jialing", "Jialing"),
        ("lifan", "Lifan"),
        ("zongshen", "Zongshen"),
        ("bajaj", "Bajaj"),
        ("pulsar", "Pulsar"),
    )
    for clave, canonica in marcas:
        if re.search(rf"\b{re.escape(clave)}\b", texto):
            return canonica
    return None


def _construir_anuncio_combustion(
    detalle: dict, tecnicos: dict, catalogos: dict
) -> dict:
    """Construye un anuncio con los campos exactos de esquema_moto_combustion.json."""
    provincia, municipio = rv.resolver_ubicacion(
        detalle.get("provinceId"), detalle.get("municipalityId"), catalogos
    )
    titulo = detalle.get("titulo")
    descripcion = detalle.get("descripcion")
    campos_combustion = extraer_campos_combustion(titulo, descripcion)
    extras = _extraer_campos_combustion_extra(titulo, descripcion)

    precio_detalle = detalle.get("precio_usd")
    precio_texto = tecnicos.get("precio_usd")
    precio_usd = precio_detalle if precio_detalle is not None else precio_texto
    try:
        if (
            precio_detalle is not None
            and precio_texto is not None
            and 100 <= float(precio_texto) <= 5000
            and float(precio_texto) > float(precio_detalle) * 2
        ):
            precio_usd = precio_texto
    except (TypeError, ValueError):
        pass

    base = {
        "id_anuncio": detalle.get("id_anuncio"),
        "titulo": rv.limpiar_emojis(titulo),
        "precio_usd": precio_usd,
        "fecha_publicacion": detalle.get("updatedOnByUser"),
        "marca": _extraer_marca_combustion(titulo, descripcion),
        "modelo": None,
        "tipo_vehiculo": "moto_combustion",
        "cilindrada_cc": campos_combustion.get("cilindrada_cc"),
        "tipo_motor": extras.get("tipo_motor"),
        "combustible": campos_combustion.get("combustible") or "gasolina",
        "consumo_l_100km": extras.get("consumo_l_100km"),
        "capacidad_tanque_l": extras.get("capacidad_tanque_l"),
        "transmision": extras.get("transmision"),
        "tipo_arranque": extras.get("tipo_arranque"),
        "anio_fabricacion": extras.get("anio_fabricacion"),
        "kilometraje_km": campos_combustion.get("kilometraje_km"),
        "velocidad_max_kmh": tecnicos.get("velocidad_max_kmh"),
        "garantia_dias": tecnicos.get("garantia_dias"),
        "peso_kg": tecnicos.get("peso_kg"),
        "tipo_frenos": tecnicos.get("tipo_frenos"),
        "suspension": tecnicos.get("suspension"),
        "estado": tecnicos.get("estado"),
        "papeles": tecnicos.get("papeles"),
        "accesorios": tecnicos.get("accesorios") or [],
        "ubicacion": provincia,
        "municipio": municipio,
        "descripcion": rv.limpiar_emojis(descripcion),
        "url_anuncio": detalle.get("url_anuncio"),
        "vendedor_id": rv._vendedor_id(detalle.get("vendedor")),
        "transporte_incluido": tecnicos.get("transporte_incluido"),
    }
    return {clave: base.get(clave) for clave in _campos_esquema_combustion()}


def _campos_faltantes(anuncio: dict, campos) -> list:
    return [campo for campo in campos if anuncio.get(campo) in (None, "")]


def _procesar_detalles_combustion(ruta_muestra: str) -> dict:
    """Procesa una muestra usando el esquema de combustión, no el eléctrico."""
    with open(ruta_muestra, encoding="utf-8") as f:
        muestra = json.load(f)

    catalogos = _cargar_catalogos()
    validos_completos = []
    validos_parciales = []
    descartados = []

    for item in muestra:
        idd = _id_desde_url(item.get("url_detalle", ""))
        ruta = CACHE_DETALLE / f"detalle_{idd}.html"
        if not ruta.exists():
            descartados.append(
                {"anuncio": {"id_anuncio": idd}, "campos_faltantes": ["detalle_faltante"]}
            )
            continue
        try:
            detalle = rv.extraer_detalle(ruta.read_text(encoding="utf-8"))
            tecnicos = rv.extraer_campos_tecnicos(detalle.get("descripcion"))
            anuncio = _construir_anuncio_combustion(detalle, tecnicos, catalogos)
        except (ValueError, KeyError, json.JSONDecodeError) as exc:
            descartados.append(
                {
                    "anuncio": {"id_anuncio": idd},
                    "campos_faltantes": [f"error_lectura: {exc}"],
                }
            )
            continue

        if not es_combustion_real(
            anuncio.get("titulo"), anuncio.get("descripcion")
        ):
            descartados.append(
                {
                    "anuncio": anuncio,
                    "campos_faltantes": ["no_es_moto_combustion"],
                }
            )
            continue

        faltantes = _campos_faltantes(anuncio, CAMPOS_OBLIGATORIOS_COMBUSTION)
        if not faltantes:
            validos_completos.append(anuncio)
            continue

        faltantes_parciales = _campos_faltantes(
            anuncio, CAMPOS_PARCIALES_COMBUSTION
        )
        if not faltantes_parciales:
            validos_parciales.append(anuncio)
        else:
            descartados.append(
                {"anuncio": anuncio, "campos_faltantes": faltantes_parciales}
            )

    return {
        "validos_completos": validos_completos,
        "validos_parciales": validos_parciales,
        "descartados": descartados,
        "total": len(muestra),
    }


def _titulo_obviamente_no_combustion(titulo: str) -> bool:
    """Evita descargar títulos que ya declaran accesorio u otro tipo de vehículo."""
    texto = _normalizar(titulo)
    if _es_titulo_parte(texto):
        return True
    if any(palabra in texto for palabra in _ACCESORIOS):
        return True
    if any(palabra in texto for palabra in _OTROS_VEHICULOS):
        return True
    if any(palabra in texto for palabra in _NO_VENTA):
        return True
    if "elect" in texto:
        return True
    if not _tiene_senal_vehiculo(texto) and not _tiene_senal_combustion(texto):
        return True
    return False


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


def _es_precio_outlier(anuncio: dict) -> bool:
    precio = anuncio.get("precio_usd")
    if precio is None:
        return True
    try:
        valor = float(precio)
    except (TypeError, ValueError):
        return True
    return valor < PRECIO_MIN_USD or valor > PRECIO_MAX_USD


def _separar_outliers(anuncios: list[dict]) -> tuple[list[dict], list[dict]]:
    en_rango = []
    fuera = []
    for anuncio in anuncios:
        if _es_precio_outlier(anuncio):
            fuera.append(anuncio)
        else:
            en_rango.append(anuncio)
    return en_rango, fuera


def _cargar_outliers() -> dict[str, dict]:
    if not RUTA_OUTLIERS.exists():
        return {}
    with open(RUTA_OUTLIERS, encoding="utf-8") as f:
        datos = json.load(f)
    return {str(item.get("id_anuncio")): item for item in datos}


def _guardar_outliers(outliers: dict[str, dict]) -> None:
    _guardar_json(RUTA_OUTLIERS, list(outliers.values()))


def _actualizar_outliers(
    outliers: dict[str, dict], en_rango: list[dict], fuera: list[dict]
) -> None:
    for anuncio in en_rango:
        idd = str(anuncio.get("id_anuncio") or "")
        if idd:
            outliers.pop(idd, None)
    for anuncio in fuera:
        idd = str(anuncio.get("id_anuncio") or "")
        if idd:
            outliers[idd] = anuncio


def _guardar_procesados(existentes: dict[str, dict]) -> tuple[int, int]:
    anuncios = list(existentes.values())
    en_rango, fuera = _separar_outliers(anuncios)
    outliers = _cargar_outliers()
    _actualizar_outliers(outliers, en_rango, fuera)
    for anuncio in fuera:
        existentes.pop(str(anuncio.get("id_anuncio") or ""), None)
    _guardar_json(RUTA_PROCESADOS, list(existentes.values()))
    _guardar_outliers(outliers)
    return len(en_rango), len(fuera)


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

        if idd in existentes:
            continue
        if idd in descartados and descartados[idd].get("detalle") == "no_es_moto_combustion":
            continue
        if idd in descartados and descartados[idd].get("motivo") in (
            MOTIVO_BORRADO,
            MOTIVO_EXPIRADO,
        ):
            continue

        if _titulo_obviamente_no_combustion(registro.get("titulo")):
            descartados.setdefault(
                idd,
                _crear_descartado(
                    registro,
                    MOTIVO_DETALLE_INVALIDO,
                    {"detalle": "no_es_moto_combustion"},
                ),
            )
            _volcar_progreso(validos, descartados, RUTA_DESCARTADOS)
            print(f"[DESCARTADO:no_es_combustion] {registro.get('url_detalle')}")
            continue

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
    """Procesa los válidos con el esquema de combustión (acumulativo)."""
    existentes = _cargar_procesados_existentes()

    if not validos:
        en_rango, fuera = _guardar_procesados(existentes)
        _volcar_progreso(validos, descartados, RUTA_DESCARTADOS)
        print(
            f"[PROCESADO] sin nuevos; en_rango={en_rango} outliers={fuera}"
        )
        return

    # Solo procesar los que aún no estén en procesados
    nuevos_a_procesar = []
    for registro in validos:
        idd = _id_desde_url(registro.get("url_detalle", ""))
        if idd not in existentes:
            nuevos_a_procesar.append(registro)

    if not nuevos_a_procesar:
        en_rango, fuera = _guardar_procesados(existentes)
        _volcar_progreso(validos, descartados, RUTA_DESCARTADOS)
        print(
            f"[PROCESADO] nuevos=0 en_rango={en_rango} outliers={fuera} "
            f"acumulados={len(existentes)}"
        )
        return

    with tempfile.NamedTemporaryFile(
        "w", suffix=".json", delete=False, encoding="utf-8"
    ) as tmp:
        json.dump(nuevos_a_procesar, tmp, ensure_ascii=False)
        ruta_muestra = tmp.name

    try:
        resultado = _procesar_detalles_combustion(ruta_muestra)
    finally:
        Path(ruta_muestra).unlink(missing_ok=True)

    anuncios = resultado["validos_completos"] + resultado["validos_parciales"]
    anuncios_validos = []
    for anuncio in anuncios:
        idd = str(anuncio.get("id_anuncio") or "")
        if not es_combustion_real(anuncio.get("titulo"), anuncio.get("descripcion")):
            if idd and idd not in descartados:
                descartados[idd] = {
                    "url_detalle": anuncio.get("url_anuncio"),
                    "id": idd,
                    "titulo": anuncio.get("titulo"),
                    "precio_usd": anuncio.get("precio_usd"),
                    "motivo": MOTIVO_DETALLE_INVALIDO,
                    "fecha_intento": _ahora_iso(),
                    "detalle": "no_es_moto_combustion",
                }
            continue
        if idd:
            existentes[idd] = anuncio
            descartados.pop(idd, None)
            anuncios_validos.append(anuncio)

    en_rango, fuera = _separar_outliers(anuncios_validos)
    _guardar_procesados(existentes)

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
        f"[PROCESADO] nuevos_en_rango={len(en_rango)} outliers={len(fuera)} "
        f"acumulados={len(existentes)} "
        f"(completos={len(resultado['validos_completos'])}, "
        f"parciales={len(resultado['validos_parciales'])}) "
        f"rechazados_no_combustion={len(anuncios) - len(anuncios_validos)} "
        f"descartados_nuevos={len(resultado['descartados'])}"
    )


def reprocesar_cache() -> int:
    """Reprocesa solo los candidatos de combustión en caché, sin peticiones nuevas."""
    descartados = cargar_descartados_previos()
    existentes = _cargar_procesados_existentes()

    candidatos = cargar_candidatos()
    ids_candidatos = {_id_desde_url(c.get("url_detalle", "")) for c in candidatos}
    por_id = {_id_desde_url(c.get("url_detalle", "")): c for c in candidatos}

    archivos = sorted(CACHE_DETALLE.glob("detalle_*.html"))
    print(
        f"[REPROCESAR] {len(archivos)} detalles en caché; "
        f"{len(ids_candidatos)} candidatos de combustión"
    )

    validos_candidatos = []
    ignorados = 0
    for ruta in archivos:
        idd = ruta.stem.replace("detalle_", "")
        if idd not in ids_candidatos:
            ignorados += 1
            continue
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

        registro = dict(por_id.get(idd) or {})
        registro.setdefault(
            "url_detalle", f"https://www.revolico.com/item/x-{idd}"
        )
        validos_candidatos.append(registro)

    print(f"[REPROCESAR] ignorados fuera de candidatos: {ignorados}")

    if not validos_candidatos:
        en_rango, fuera = _guardar_procesados(existentes)
        _volcar_progreso([], descartados, RUTA_DESCARTADOS)
        print(
            f"[TOTAL] combustión en rango={en_rango} outliers={fuera}"
        )
        return 0

    with tempfile.NamedTemporaryFile(
        "w", suffix=".json", delete=False, encoding="utf-8"
    ) as tmp:
        json.dump(validos_candidatos, tmp, ensure_ascii=False)
        ruta_muestra = tmp.name

    try:
        resultado = _procesar_detalles_combustion(ruta_muestra)
    finally:
        Path(ruta_muestra).unlink(missing_ok=True)

    anuncios = resultado["validos_completos"] + resultado["validos_parciales"]
    anuncios_validos = []
    for anuncio in anuncios:
        idd = str(anuncio.get("id_anuncio") or "")
        if not es_combustion_real(anuncio.get("titulo"), anuncio.get("descripcion")):
            if idd and idd not in descartados:
                descartados[idd] = {
                    "url_detalle": anuncio.get("url_anuncio"),
                    "id": idd,
                    "titulo": anuncio.get("titulo"),
                    "precio_usd": anuncio.get("precio_usd"),
                    "motivo": MOTIVO_DETALLE_INVALIDO,
                    "fecha_intento": _ahora_iso(),
                    "detalle": "no_es_moto_combustion",
                }
            continue
        if idd:
            existentes[idd] = anuncio
            descartados.pop(idd, None)
            anuncios_validos.append(anuncio)

    en_rango, fuera = _separar_outliers(anuncios_validos)
    _guardar_procesados(existentes)

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
        f"[PROCESADO] nuevos_en_rango={len(en_rango)} outliers={len(fuera)} "
        f"acumulados={len(existentes)} "
        f"(completos={len(resultado['validos_completos'])}, "
        f"parciales={len(resultado['validos_parciales'])}) "
        f"rechazados_no_combustion={len(anuncios) - len(anuncios_validos)}"
    )
    return 0


def limpiar_procesados() -> int:
    """Deja solo motos de combustión reales y limpia descartados de otros tipos."""
    existentes = _cargar_procesados_existentes()
    antes = len(existentes)
    candidatos = cargar_candidatos()
    ids_candidatos = {
        _id_desde_url(c.get("url_detalle", "")) for c in candidatos
    }
    por_id = {
        _id_desde_url(c.get("url_detalle", "")): c for c in candidatos
    }
    descartados = cargar_descartados_previos()
    eliminados = []
    muestra = []

    for idd, anuncio in existentes.items():
        if not es_combustion_real(anuncio.get("titulo"), anuncio.get("descripcion")):
            eliminados.append((idd, anuncio.get("titulo")))
            if idd in ids_candidatos and idd not in descartados:
                descartados[idd] = {
                    "url_detalle": anuncio.get("url_anuncio"),
                    "id": idd,
                    "titulo": anuncio.get("titulo"),
                    "precio_usd": anuncio.get("precio_usd"),
                    "motivo": MOTIVO_DETALLE_INVALIDO,
                    "fecha_intento": _ahora_iso(),
                    "detalle": "no_es_moto_combustion",
                }
            continue
        registro = dict(por_id.get(idd) or {})
        if not registro.get("url_detalle"):
            registro["url_detalle"] = (
                anuncio.get("url_anuncio")
                or f"https://www.revolico.com/item/x-{idd}"
            )
        muestra.append(registro)

    limpios = {}
    if muestra:
        with tempfile.NamedTemporaryFile(
            "w", suffix=".json", delete=False, encoding="utf-8"
        ) as tmp:
            json.dump(muestra, tmp, ensure_ascii=False)
            ruta_muestra = tmp.name
        try:
            resultado = _procesar_detalles_combustion(ruta_muestra)
        finally:
            Path(ruta_muestra).unlink(missing_ok=True)

        for anuncio in (
            resultado["validos_completos"] + resultado["validos_parciales"]
        ):
            idd = str(anuncio.get("id_anuncio") or "")
            if idd:
                limpios[idd] = anuncio
                descartados.pop(idd, None)

        for descarte in resultado["descartados"]:
            anuncio = descarte.get("anuncio", {})
            idd = str(anuncio.get("id_anuncio") or "")
            if not idd or idd in descartados:
                continue
            item = {
                "url_detalle": anuncio.get("url_anuncio"),
                "id": idd,
                "titulo": anuncio.get("titulo"),
                "precio_usd": anuncio.get("precio_usd"),
                "motivo": MOTIVO_DETALLE_INVALIDO,
                "fecha_intento": _ahora_iso(),
                "campos_faltantes": descarte.get("campos_faltantes"),
            }
            if descarte.get("campos_faltantes") == ["no_es_moto_combustion"]:
                item["detalle"] = "no_es_moto_combustion"
            descartados[idd] = item

    en_rango, fuera = _separar_outliers(list(limpios.values()))
    outliers = _cargar_outliers()
    _actualizar_outliers(outliers, en_rango, fuera)
    for anuncio in fuera:
        limpios.pop(str(anuncio.get("id_anuncio") or ""), None)
    _guardar_json(RUTA_PROCESADOS, list(limpios.values()))
    _guardar_outliers(outliers)

    descartados_limpios = {
        idd: item for idd, item in descartados.items() if idd in ids_candidatos
    }
    _guardar_json(RUTA_DESCARTADOS, list(descartados_limpios.values()))

    print(
        f"[LIMPIAR] antes={antes} combustion_real={len(limpios)} "
        f"outliers={len(fuera)} eliminados={len(eliminados)} "
        f"descartados={len(descartados_limpios)} "
        f"reconstruidos_con_esquema_combustion={len(muestra)}"
    )
    for idd, anuncio in limpios.items():
        print(
            f"  [COMB] {idd} | {anuncio.get('titulo')} | "
            f"cc={anuncio.get('cilindrada_cc')} "
            f"comb={anuncio.get('combustible')} "
            f"km={anuncio.get('kilometraje_km')} "
            f"motor={anuncio.get('tipo_motor')}"
        )
    for anuncio in fuera:
        print(
            f"  [OUTLIER] {anuncio.get('id_anuncio')} | "
            f"{anuncio.get('titulo')} | precio={anuncio.get('precio_usd')} USD"
        )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Descarga y procesa detalles de motos de combustión.")
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
        help="Reprocesa solo los candidatos de combustión en caché, sin peticiones nuevas.",
    )
    parser.add_argument(
        "--limpiar",
        action="store_true",
        help="Elimina de los procesados todo lo que no sea moto de combustión real.",
    )
    args = parser.parse_args(argv)

    if args.limpiar:
        return limpiar_procesados()
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
    outliers = _cargar_outliers()
    print(
        f"[FINAL] procesados={len(existentes)} outliers={len(outliers)} "
        f"faltan={max(0, MAX_VALIDOS-len(existentes))}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
