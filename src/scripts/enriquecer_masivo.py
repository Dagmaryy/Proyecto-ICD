#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Any, Callable

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
DIR_FINAL = BASE_DIR / "data" / "processed" / "final"

ARCHIVOS = [
    "motos_electricas_300.json",
    "motos_combustion_300.json",
    "bicis_300.json",
    "patinetes_300.json",
]

CAMPOS_OBJETIVO = [
    "marca",
    "modelo",
    "papeles",
    "estado",
    "tipo_bateria",
    "accesorios",
    "garantia_dias",
]

COLUMNAS_PROTEGIDAS = [
    "precio_usd",
    "motor_w",
    "voltaje_v",
    "autonomia_km",
    "cilindrada_cc",
    "municipio",
]

PALABRAS_GENERICAS = {
    "moto", "motos", "motico", "moticos", "motocicleta", "motocicletas",
    "motor", "motores", "electrica", "electricas", "electrico", "electricos",
    "bicicleta", "bicicletas", "bici", "bicis", "bicimoto", "bicimotos",
    "patinete", "patinetes", "patineta", "patinetas", "scooter", "scooters",
    "carriola", "nueva", "nuevas", "nuevo", "nuevos", "usada", "usadas",
    "usado", "usados", "vendo", "vende", "venden", "venta", "se", "de", "la",
    "el", "los", "las", "con", "sin", "para", "por", "y", "a", "en", "del", "al",
    "gasolina", "combustion", "plegable", "plegables", "semiautomatica",
    "automatica", "importada", "importado", "todo", "todos", "toda", "todas",
    "bolsillo", "bolsillos", "alta", "gama", "super", "gran", "buen", "buena",
    "precio", "marca", "modelo", "sport", "racing", "dolares", "euros", "pesos",
    "mn", "zelle", "km", "kmh", "cc", "ah", "w", "v", "t", "hp", "usd", "cup",
    "rebaja", "rebajas", "oferta", "ofertas", "ganga", "gangas", "disponible",
    "disponibles", "entrega", "envio", "envios", "mensajeria", "gratis",
    "incluido", "incluida", "roja", "rojo", "negra", "negro", "blanca", "blanco",
    "azul", "verde", "naranja", "rosa", "gris", "amarilla", "amarillo",
    "deportiva", "deportivo", "moderna", "moderno", "clasica", "clasico",
    "estrenar", "factura", "potencia", "potecia", "velocidad", "perfecta",
    "comoda", "comodidad", "ideal", "gusto", "mayor", "solo", "si", "tu", "new",
    "mini", "superbicicleta", "mercancia", "paquete", "caja", "litio", "bateria",
    "voltaje", "autonomia", "unico", "paseo", "habana", "cuba", "bike", "ebike",
    "e-bike", "fat", "tire", "peak", "pro", "plus", "max", "star", "edition",
    "elegant", "mph", "wheel", "hasta", "soporta", "adultos", "suspension",
    "transporte", "asiento", "maxima", "son", "cuadro", "diseno", "mas",
    "moverte", "ojo", "lifepo", "edades", "vmax", "watts", "whatsapp", "usted",
    "papeles", "sidecar", "mini-sidecar", "garantia", "diferentes", "sports",
    "doble", "portabilidad", "store", "carrera", "desde",
}

UNIDADES = (
    "v", "volts?", "voltios?", "w", "watts?", "wats?", "watios?", "ah",
    "amps?", "amperes?", "amperios?", "km", "kmh", "km/h", "cc", "t", "hp",
    "dias", "dia", "mes", "meses", "anos", "ano", "horas", "usd", "cup", "kg",
    "lb", "d[oó]lares", "euros", "pesos", "mn", "zelle", "nuevas?", "nuevos?",
)

TOKEN_TITULO = re.compile(r"(?<![\wÁÉÍÓÚÜÑáéíóúüñ])([A-Za-zÁÉÍÓÚÜÑáéíóúüñ][A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9'’\-]*)")


def normalizar(texto: Any) -> str:
    if texto is None:
        return ""
    texto = unicodedata.normalize("NFKD", str(texto))
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return texto.lower()


def vacio(valor: Any) -> bool:
    if valor is None:
        return True
    if isinstance(valor, str):
        return not valor.strip()
    if isinstance(valor, (list, tuple, dict, set)):
        return len(valor) == 0
    try:
        if pd.isna(valor):
            return True
    except (TypeError, ValueError):
        pass
    return False


def extraer_marca(titulo: Any) -> str | None:
    for token in TOKEN_TITULO.findall(str(titulo or "")):
        limpio = token.strip("'’\\-")
        if len(limpio) < 2 or not limpio[0].isupper():
            continue
        base = normalizar(limpio)
        if base in PALABRAS_GENERICAS or any(c.isdigit() for c in limpio):
            continue
        return limpio
    return None


def extraer_modelo(titulo: Any) -> str | None:
    texto = str(titulo or "")
    for match in re.finditer(r"(?<![\w])([A-Za-z]{1,4}-?\d{1,4}[A-Za-z]?)(?![\w])", texto):
        codigo = match.group(1)
        if any(normalizar(codigo).startswith(u) for u in ("v", "w", "ah", "km", "cc", "hp")):
            continue
        return codigo
    for match in re.finditer(r"(?<![\w.,])(\d{3,4})(?![\w.,])", texto):
        numero = match.group(1)
        if re.fullmatch(r"(19|20)\d{2}", numero):
            continue
        despues = texto[match.end():match.end() + 10]
        antes = texto[max(0, match.start() - 12):match.start()]
        if re.match(r"\s*%", despues):
            continue
        if re.match(r"[\s:.\-]*(?:" + "|".join(UNIDADES) + r")\b", despues, re.IGNORECASE):
            continue
        if re.search(r"(?:usd|cup|\$|precio|solo|desde)[\s:.\-]*$", antes, re.IGNORECASE):
            continue
        return numero
    return None


def extraer_papeles(texto: Any) -> bool | None:
    t = normalizar(texto)
    if re.search(r"\bsin (?:papeles|documentos?|factura)\b|\bno (?:tiene|posee) (?:papeles|documentos?)\b", t):
        return False
    if re.search(r"\bfacturas?\b|\blegal(?:es)?\b|\bpapeles (?:en regla|al dia)\b|\bcon papeles\b|\bdocument(?:os?|acion)\b", t):
        return True
    return None


def extraer_estado(texto: Any) -> str | None:
    t = normalizar(texto)
    t = re.sub(r"\bsin (?:ningun )?detalles?\b", "", t)
    nuevo = re.search(r"\bnuev[ao]s?\b|\bestrenar\b|\bsin uso\b|\b0\s*km\b|\bcero km\b", t)
    usado = re.search(r"\busad[ao]s?\b|\bdetalles?\b|\bsegunda mano\b", t)
    if nuevo and not usado:
        return "Nuevo"
    if usado:
        return "Usado"
    if nuevo:
        return "Nuevo"
    return None


def extraer_tipo_bateria(texto: Any) -> str | None:
    t = normalizar(texto)
    if re.search(r"\blitio\b", t):
        return "litio"
    if re.search(r"\bgel\b", t):
        return "gel"
    if re.search(r"\bplomo\b", t):
        return "plomo"
    return None


def extraer_accesorios(texto: Any) -> list[str] | None:
    t = normalizar(texto)
    encontrados = []
    for patron, etiqueta in (
        (r"\balarmas?\b", "alarma"),
        (r"\bbaul(?:es)?\b", "baúl"),
        (r"\bcascos?\b", "casco"),
        (r"\bbluetooths?\b", "bluetooth"),
    ):
        if re.search(patron, t):
            encontrados.append(etiqueta)
    return encontrados or None


def extraer_garantia(texto: Any) -> int | None:
    t = normalizar(texto)
    match = re.search(r"garantia[\s:.\-]*(?:de[\s:.\-]*)?(\d{1,3})[\s:.\-]*dias?\b", t)
    if match:
        return int(match.group(1))
    match = re.search(r"(\d{1,3})[\s:.\-]*dias?[\s:.\-]*de[\s:.\-]*garantia\b", t)
    if match:
        return int(match.group(1))
    match = re.search(r"garantia[\s:.\-]*(?:de[\s:.\-]*)?(\d{1,2})[\s:.\-]*mes(?:es)?\b", t)
    if match:
        return int(match.group(1)) * 30
    match = re.search(r"(\d{1,2})[\s:.\-]*mes(?:es)?[\s:.\-]*de[\s:.\-]*garantia\b", t)
    if match:
        return int(match.group(1)) * 30
    return None


def reglas(titulo: pd.Series, descripcion: pd.Series) -> dict[str, tuple[pd.Series, Callable[[Any], Any]]]:
    completo = titulo.fillna("").astype(str) + " " + descripcion.fillna("").astype(str)
    return {
        "marca": (titulo, extraer_marca),
        "modelo": (titulo, extraer_modelo),
        "papeles": (completo, extraer_papeles),
        "estado": (completo, extraer_estado),
        "tipo_bateria": (completo, extraer_tipo_bateria),
        "accesorios": (completo, extraer_accesorios),
        "garantia_dias": (completo, extraer_garantia),
    }


def _jsonable(valor: Any) -> Any:
    if vacio(valor):
        return None
    if hasattr(valor, "item"):
        try:
            return valor.item()
        except (ValueError, AttributeError):
            return valor
    return valor


def procesar_archivo(nombre: str) -> dict[str, Any] | None:
    ruta = DIR_FINAL / nombre
    if not ruta.exists():
        print(f"AVISO: no existe {ruta}")
        return None

    with ruta.open(encoding="utf-8") as fh:
        registros = json.load(fh)

    if not isinstance(registros, list):
        raise ValueError(f"{ruta} no contiene una lista de registros")

    df = pd.DataFrame(registros)
    columnas_presentes = [columna for columna in CAMPOS_OBJETIVO if columna in df.columns]
    columnas_ausentes = [columna for columna in CAMPOS_OBJETIVO if columna not in df.columns]
    if columnas_ausentes:
        print(f"AVISO: {nombre} no tiene {', '.join(columnas_ausentes)}; se omite(n).")

    titulo = df["titulo"] if "titulo" in df.columns else pd.Series([""] * len(df))
    descripcion = df["descripcion"] if "descripcion" in df.columns else pd.Series([""] * len(df))
    fuentes = {columna: valor for columna, valor in reglas(titulo, descripcion).items() if columna in columnas_presentes}

    llenados: dict[tuple[int, str], Any] = {}
    conteo = {columna: 0 for columna in CAMPOS_OBJETIVO}

    for columna, (fuente, funcion) in fuentes.items():
        for idx in df.index:
            if not vacio(df.at[idx, columna]):
                continue
            valor = funcion(fuente.at[idx])
            if vacio(valor):
                continue
            llenados[(idx, columna)] = _jsonable(valor)
            conteo[columna] += 1

    salida = []
    for idx, original in enumerate(registros):
        nuevo = dict(original)
        for columna in CAMPOS_OBJETIVO:
            if (idx, columna) in llenados:
                if not vacio(original.get(columna)):
                    raise ValueError(f"{nombre}: intento de sobrescribir {columna} en el índice {idx}")
                nuevo[columna] = llenados[(idx, columna)]
        for columna in COLUMNAS_PROTEGIDAS:
            if columna in original and nuevo.get(columna) != original.get(columna):
                raise ValueError(f"{nombre}: se modificó la columna protegida {columna} en el índice {idx}")
        salida.append(nuevo)

    if len(salida) != len(registros):
        raise ValueError(f"{nombre}: cambió el número de registros")

    destino = ruta.with_name(f"{ruta.stem}_enriquecido.json")
    with destino.open("w", encoding="utf-8") as fh:
        json.dump(salida, fh, ensure_ascii=False, indent=2)

    return {
        "archivo": nombre,
        "salida": destino.name,
        "registros": len(salida),
        "conteo": conteo,
    }


def main() -> int:
    resultados = []
    for nombre in ARCHIVOS:
        resultado = procesar_archivo(nombre)
        if resultado:
            resultados.append(resultado)

    columnas = CAMPOS_OBJETIVO
    print(f"{'Archivo':34} {'N':>4} " + " ".join(f"{c:>13}" for c in columnas))
    for resultado in resultados:
        valores = " ".join(f"{resultado['conteo'][c]:>13}" for c in columnas)
        print(f"{resultado['archivo']:34} {resultado['registros']:>4} {valores}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
