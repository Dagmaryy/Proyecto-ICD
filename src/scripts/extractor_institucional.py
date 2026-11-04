#!/usr/bin/env python3
"""Extrae el texto de fuentes oficiales sobre vehículos en Cuba.

Descarga cada URL con requests, limpia el HTML con BeautifulSoup o extrae
el texto de los PDF con pdfplumber, y guarda un Markdown por fuente en
data/raw/stakeholders/institucionales/.

Uso:
    python extractor_institucional.py
"""

from __future__ import annotations

import io
import json
import re
import sys
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse, unquote

import pdfplumber
import requests
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).resolve().parent
SALIDA_DIR = BASE_DIR / "data/raw/stakeholders/institucionales"

DELAY_SEGUNDOS = 2.0
TIMEOUT_SEGUNDOS = 30
MAX_REINTENTOS = 3
USER_AGENT = "Proyecto-ICD/1.0 (Dagmary; uso academico; contacto: proyecto ICD)"

URLS = [
    "https://www.gacetaoficial.gob.cu/es/decreto-163-de-2026-de-consejo-de-ministros",
    "https://www.gacetaoficial.gob.cu/es/resolucion-175-de-2026-de-ministerio-de-finanzas-y-precios",
    "https://www.aduana.gob.cu/front",
    "https://www.mindus.gob.cu/es/marco-regulatorio",
    "https://www.mfp.gob.cu/inicio/portada.php",
    "https://www.gacetaoficial.gob.cu/sites/default/files/goc-2026-o65_0.pdf",
    "https://www.gacetaoficial.gob.cu/sites/default/files/goc-2026-o83.pdf",
    "https://www.gacetaoficial.gob.cu/es/resolucion-340-de-2026-de-aduana-general-de-la-republica",
    "http://www.cubadebate.cu/noticias/2026/08/04/cuba-anuncia-nuevas-flexibilizaciones-para-la-transmision-importacion-y-comercializacion-de-vehiculos/",
    "https://www.mindus.gob.cu/es/noticias/vehiculos-electricos-del-caribe-asegurando-el-ciclo-de-produccion-para-una-movilidad",
    "http://redaccionmr.cubadebate.cu/mesa-redonda/2026/08/06/mesa-redonda-nuevas-facilidades-para-importar-vehiculos-e-impulsar-la-movilidad-electrica-en-cuba/",
    "https://www.granma.cu/cuba/2026-10-06/actualizan-disposiciones-para-la-importacion-de-mercancias-por-personas-naturales-06-10-2026-11-10-16",
    "https://www.gacetaoficial.gob.cu/es/resolucion-174-de-2026-de-ministerio-de-finanzas-y-precios",
    "https://www.gacetaoficial.gob.cu/es/resolucion-104-de-2026-de-ministerio-del-comercio-exterior-y-la-inversion-extranjera",
    "https://www.gacetaoficial.gob.cu/es/resolucion-17-de-2026-de-ministerio-del-comercio-interior",
    "https://www.aduana.gob.cu/pagina-basica/que-puedo-y-no-puedo-importar",
    "https://www.aduana.gob.cu/preguntas-frecuentes",
    "https://www.aduana.gob.cu/pagina-basica/equipaje-no-acompanado-0",
    "https://www.aduana.gob.cu/noticias/respuesta-consultas-de-las-personas",
    "https://www.granma.cu/cuba/2026-08-04/nuevas-flexibilizaciones-para-la-transmision-importacion-y-comercializacion-de-vehiculos-en-cuba",
    "https://www.juventudrebelde.cu/cuba/2026-08-04/publican-nuevas-normativas-relacionadas-con-los-vehiculos",
]

ETIQUETAS_SIEMPRE_RUIDO = (
    "script",
    "style",
    "noscript",
    "svg",
    "iframe",
    "form",
    "button",
    "nav",
    "footer",
)

ETIQUETAS_CONDICIONALES_RUIDO = ("header", "aside")

TOKENS_RUIDO = {
    "menu",
    "menus",
    "navbar",
    "nav",
    "navigation",
    "breadcrumb",
    "breadcrumbs",
    "sidebar",
    "footer",
    "header",
    "cookie",
    "cookies",
    "banner",
    "social",
    "share",
    "related",
    "comment",
    "comments",
    "newsletter",
    "subscribe",
    "advert",
    "advertisement",
    "ads",
    "popup",
    "modal",
    "skip",
    "visually",
    "hidden",
    "sr",
    "screen",
    "reader",
}

SELECTORES_CONTENIDO = (
    "article",
    "main",
    "[role='main']",
    "#main-content",
    ".main-content",
    ".region-content",
    ".node__content",
    ".field--name-body",
    ".entry-content",
    "#content",
    ".content",
)

ESTADOS_REINTENTO = {429, 500, 502, 503, 504}


def normalizar_texto(texto: str) -> str:
    """Quita espacios sobrantes y líneas vacías repetidas."""
    texto = texto.replace("\xa0", " ")
    lineas = []
    for linea in texto.splitlines():
        linea = re.sub(r"[ \t]+", " ", linea).strip()
        if linea:
            lineas.append(linea)
    return "\n".join(lineas)


def slug_desde_url(url: str, indice: int) -> str:
    """Construye un nombre de archivo descriptivo y seguro desde la URL."""
    partes = urlparse(url)
    base = f"{partes.netloc}{unquote(partes.path)}"
    base = base.replace("www.", "")
    base = unicodedata.normalize("NFKD", base)
    base = "".join(c for c in base if not unicodedata.combining(c))
    slug = re.sub(r"[^A-Za-z0-9]+", "-", base).strip("-").lower()
    slug = re.sub(r"-+", "-", slug)[:140].strip("-")
    return f"{indice:02d}_{slug}.md"


def es_pdf(url: str, content_type: str) -> bool:
    return urlparse(url).path.lower().endswith(".pdf") or "application/pdf" in (
        content_type or ""
    ).lower()


def descargar(sesion: requests.Session, url: str) -> requests.Response:
    """Descarga con reintentos para errores temporales."""
    ultimo_error: Exception | None = None

    for intento in range(1, MAX_REINTENTOS + 1):
        try:
            respuesta = sesion.get(url, timeout=TIMEOUT_SEGUNDOS)
            if respuesta.status_code in ESTADOS_REINTENTO and intento < MAX_REINTENTOS:
                espera = 60 if respuesta.status_code == 429 else 5 * intento
                print(
                    f"    HTTP {respuesta.status_code}; reintento "
                    f"{intento}/{MAX_REINTENTOS - 1} en {espera}s...",
                    file=sys.stderr,
                )
                time.sleep(espera)
                continue
            respuesta.raise_for_status()
            return respuesta
        except requests.RequestException as exc:
            ultimo_error = exc
            estado = exc.response.status_code if exc.response is not None else None
            if estado is not None and estado not in ESTADOS_REINTENTO:
                break
            if intento >= MAX_REINTENTOS:
                break
            espera = 5 * intento
            print(
                f"    Error de red: {exc}. Reintento "
                f"{intento}/{MAX_REINTENTOS - 1} en {espera}s...",
                file=sys.stderr,
            )
            time.sleep(espera)

    raise RuntimeError(f"No se pudo descargar {url}: {ultimo_error}")


def titulo_html(soup: BeautifulSoup) -> str:
    candidatos = []
    if soup.find("h1"):
        candidatos.append(normalizar_texto(soup.find("h1").get_text(" ", strip=True)))
    if soup.title:
        candidatos.append(normalizar_texto(soup.title.get_text(" ", strip=True)))
    candidatos = [c for c in candidatos if c]
    return max(candidatos, key=len) if candidatos else "Sin titulo"


def _densidad_enlaces(elemento) -> float:
    texto = elemento.get_text(" ", strip=True)
    if not texto:
        return 0.0
    texto_enlaces = " ".join(
        enlace.get_text(" ", strip=True) for enlace in elemento.find_all("a")
    )
    return min(len(texto_enlaces) / len(texto), 1.0)


def _es_contenido_principal(elemento) -> bool:
    if getattr(elemento, "decomposed", False) or elemento.attrs is None:
        return True
    if elemento.name in {"body", "html", "main", "article"}:
        return True
    if elemento.get("role") == "main":
        return True
    return bool(
        elemento.find_parent(["article", "main"])
        or elemento.find_parent(attrs={"role": "main"})
    )


def _tiene_token_ruido(elemento) -> bool:
    for atributo in ("class", "id"):
        valor = elemento.get(atributo)
        if not valor:
            continue
        tokens = valor if isinstance(valor, list) else str(valor).split()
        for token in tokens:
            partes = set(re.split(r"[-_]+", token.lower()))
            if partes & TOKENS_RUIDO:
                return True
    return False


def extraer_texto_html(contenido: bytes) -> tuple[str, str]:
    soup = BeautifulSoup(contenido, "lxml")
    titulo = titulo_html(soup)

    for etiqueta in soup.find_all(ETIQUETAS_SIEMPRE_RUIDO):
        etiqueta.decompose()

    for etiqueta in soup.find_all(ETIQUETAS_CONDICIONALES_RUIDO):
        if not _es_contenido_principal(etiqueta):
            etiqueta.decompose()

    for elemento in soup.find_all(True):
        if _es_contenido_principal(elemento):
            continue
        if _tiene_token_ruido(elemento):
            elemento.decompose()

    candidatos = []
    for selector in SELECTORES_CONTENIDO:
        for elemento in soup.select(selector):
            texto = normalizar_texto(elemento.get_text("\n", strip=True))
            if len(texto) < 200:
                continue
            densidad = _densidad_enlaces(elemento)
            puntaje = len(texto) * (1.0 - densidad)
            candidatos.append((puntaje, len(texto), elemento, texto))

    if not candidatos:
        if soup.body is None:
            raise ValueError("El HTML no contiene texto extraíble")
        texto = normalizar_texto(soup.body.get_text("\n", strip=True))
        if not texto:
            raise ValueError("El HTML no contiene texto extraíble")
        return titulo, texto

    articulos = [c for c in candidatos if c[2].name == "article"]
    mejor_general = max(candidatos, key=lambda c: c[0])
    if articulos:
        mejor_articulo = max(articulos, key=lambda c: c[1])
        if mejor_articulo[1] >= 0.5 * mejor_general[1]:
            return titulo, mejor_articulo[3]

    return titulo, mejor_general[3]


def extraer_texto_pdf(contenido: bytes) -> tuple[str, int]:
    paginas = []
    with pdfplumber.open(io.BytesIO(contenido)) as pdf:
        for numero, pagina in enumerate(pdf.pages, start=1):
            texto = normalizar_texto(pagina.extract_text() or "")
            if texto:
                paginas.append(f"## Página {numero}\n\n{texto}")
        total_paginas = len(pdf.pages)

    if not paginas:
        raise ValueError("El PDF no contiene texto extraíble (¿documento escaneado?)")

    return "\n\n".join(paginas), total_paginas


def guardar_markdown(ruta: Path, metadatos: dict, texto: str) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    lineas_yaml = ["---"]
    for clave, valor in metadatos.items():
        lineas_yaml.append(f"{clave}: {json.dumps(valor, ensure_ascii=False)}")
    lineas_yaml.extend(["---", ""])

    contenido = "\n".join(lineas_yaml)
    contenido += f"# {metadatos['titulo']}\n\n{texto}\n"

    temporal = ruta.with_suffix(ruta.suffix + ".tmp")
    temporal.write_text(contenido, encoding="utf-8")
    temporal.replace(ruta)


def main() -> int:
    SALIDA_DIR.mkdir(parents=True, exist_ok=True)

    sesion = requests.Session()
    sesion.headers.update(
        {
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/pdf,*/*;q=0.8",
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.5",
        }
    )

    resultados = []
    total = len(URLS)

    for indice, url in enumerate(URLS, start=1):
        nombre_archivo = slug_desde_url(url, indice)
        destino = SALIDA_DIR / nombre_archivo
        print(f"[{indice:02d}/{total}] {url}")

        if indice > 1:
            time.sleep(DELAY_SEGUNDOS)

        try:
            respuesta = descargar(sesion, url)
            content_type = respuesta.headers.get("Content-Type", "")
            fecha = datetime.now(timezone.utc).isoformat(timespec="seconds")
            metadatos = {
                "titulo": "",
                "url": url,
                "fuente": urlparse(url).netloc,
                "tipo": "pdf" if es_pdf(url, content_type) else "html",
                "estado_http": respuesta.status_code,
                "content_type": content_type,
                "fecha_extraccion": fecha,
            }

            if es_pdf(url, content_type):
                texto, paginas = extraer_texto_pdf(respuesta.content)
                nombre_pdf = Path(unquote(urlparse(url).path)).name
                titulo = nombre_pdf or "Documento PDF"
                metadatos["paginas"] = paginas
            else:
                titulo, texto = extraer_texto_html(respuesta.content)
                metadatos["paginas"] = None

            metadatos["titulo"] = titulo
            metadatos["bytes"] = len(respuesta.content)
            metadatos["caracteres_texto"] = len(texto)
            guardar_markdown(destino, metadatos, texto)

            resultados.append((indice, url, "OK", len(texto), nombre_archivo))
            print(f"    OK -> {nombre_archivo} ({len(texto)} caracteres)")

        except Exception as exc:
            resultados.append((indice, url, "ERROR", 0, str(exc)))
            print(f"    ERROR: {exc}", file=sys.stderr)

    correctas = sum(1 for r in resultados if r[2] == "OK")
    print("\nResumen de extracción")
    print(f"  Correctas: {correctas}/{total}")
    for indice, url, estado, detalle, extra in resultados:
        if estado == "OK":
            print(f"  [{indice:02d}] OK    {extra} ({detalle} caracteres)")
        else:
            print(f"  [{indice:02d}] ERROR {url} -> {extra}")

    return 0 if correctas == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
