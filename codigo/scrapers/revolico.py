import time
import hashlib
import json
import random
import re
import unicodedata
from pathlib import Path

import httpx
import yaml

BASE_DIR = Path(__file__).resolve().parents[2]

CONFIG = yaml.safe_load((BASE_DIR / "config.yaml").read_text(encoding="utf-8"))

CACHE_DIR = BASE_DIR / "data/raw/web/revolico/cache_html"
CATEGORIAS = ("motos", "bicis", "patinetes")

CACHE_DIR.mkdir(parents=True, exist_ok=True)
for _categoria in CATEGORIAS:
    (CACHE_DIR / _categoria).mkdir(parents=True, exist_ok=True)

HEADERS = {"User-Agent": CONFIG["scraping"]["user_agent"]}
DELAY = CONFIG["scraping"]["delay_segundos"]
DELAY_429 = CONFIG["scraping"]["delay_429_segundos"]
MAX_PETICIONES = CONFIG["scraping"]["max_peticiones"]

_contador_peticiones = 0


def reset_contador() -> None:
    """Pone el contador de peticiones a 0. Útil para pruebas."""
    global _contador_peticiones
    _contador_peticiones = 0


def _ruta_cache(url: str, categoria: str) -> Path:
    """Ruta de caché de una URL dentro de la subcarpeta de la categoría."""
    if categoria not in CATEGORIAS:
        raise ValueError(
            f"Categoría desconocida: {categoria!r}. Usa una de {CATEGORIAS}."
        )
    clave = hashlib.md5(url.encode()).hexdigest()[:12]
    return CACHE_DIR / categoria / f"listado_{clave}.html"


def descargar_listado(
    url: str,
    categoria: str,
    usar_cache: bool = True,
    etiqueta: str | None = None,
) -> str:
    """Descarga el HTML de un listado en la subcarpeta de `categoria`.

    Con `etiqueta` (p. ej. el término de búsqueda) el archivo se guarda como
    `busqueda_<etiqueta>_p<N>.html`; sin ella se usa el nombre hash por defecto.
    """
    global _contador_peticiones

    if etiqueta:
        coincidencia_pagina = re.search(r"[?&]page=(\d+)", url)
        pagina = coincidencia_pagina.group(1) if coincidencia_pagina else "1"
        ruta_cache = (
            CACHE_DIR
            / categoria
            / f"busqueda_{etiqueta.replace(' ', '_')}_p{pagina}.html"
        )
    else:
        ruta_cache = _ruta_cache(url, categoria)

    if usar_cache and ruta_cache.exists():
        print(f"[CACHE] {url}")
        return ruta_cache.read_text(encoding="utf-8")

    if _contador_peticiones >= MAX_PETICIONES:
        raise RuntimeError(
            f"Límite de {MAX_PETICIONES} peticiones alcanzado."
        )

    with httpx.Client(headers=HEADERS, follow_redirects=True, timeout=30) as cliente:
        try:
            respuesta = cliente.get(url)

            if respuesta.status_code == 429:
                print(f"[429] Esperando {DELAY_429} s...")
                time.sleep(DELAY_429)
                respuesta = cliente.get(url)
                if respuesta.status_code == 429:
                    raise RuntimeError(
                        f"Segundo 429 tras esperar {DELAY_429} s para {url}. Abortando."
                    )

            respuesta.raise_for_status()
        except httpx.HTTPError as exc:
            raise RuntimeError(f"Error de red al descargar {url}: {exc}") from exc
        finally:
            time.sleep(DELAY)

    _contador_peticiones += 1
    html = respuesta.text
    ruta_cache.parent.mkdir(parents=True, exist_ok=True)
    ruta_cache.write_text(html, encoding="utf-8")
    print(f"[OK] {url} (petición #{_contador_peticiones})")
    return html


def descargar_detalle(url: str, categoria: str) -> str:
    """Descarga el HTML de un detalle en cache_detalle/<categoria>/. Usa caché."""
    global _contador_peticiones

    if categoria not in CATEGORIAS:
        raise ValueError(
            f"Categoría desconocida: {categoria!r}. Usa una de {CATEGORIAS}."
        )

    anuncio_id = url.rstrip("/").rsplit("-", 1)[-1]
    ruta_cache = (
        BASE_DIR
        / "data/raw/web/revolico/cache_detalle"
        / categoria
        / f"detalle_{anuncio_id}.html"
    )

    if ruta_cache.exists():
        print(f"[CACHE] {url}")
        return ruta_cache.read_text(encoding="utf-8")

    if _contador_peticiones >= MAX_PETICIONES:
        raise RuntimeError(
            f"Límite de {MAX_PETICIONES} peticiones alcanzado."
        )

    with httpx.Client(headers=HEADERS, follow_redirects=True, timeout=30) as cliente:
        try:
            respuesta = cliente.get(url)

            if respuesta.status_code == 429:
                print(f"[429] Esperando {DELAY_429} s...")
                time.sleep(DELAY_429)
                respuesta = cliente.get(url)
                if respuesta.status_code == 429:
                    raise RuntimeError(
                        f"Segundo 429 tras esperar {DELAY_429} s para {url}. Abortando."
                    )

            respuesta.raise_for_status()
        except httpx.HTTPError as exc:
            raise RuntimeError(f"Error de red al descargar {url}: {exc}") from exc
        finally:
            time.sleep(DELAY)

    _contador_peticiones += 1
    html = respuesta.text
    ruta_cache.parent.mkdir(parents=True, exist_ok=True)
    ruta_cache.write_text(html, encoding="utf-8")
    print(f"[OK] {url} (petición #{_contador_peticiones})")
    return html


def _url_pagina(url_base: str, pagina: int) -> str:
    """URL de una página concreta de la búsqueda."""
    if "{page}" in url_base:
        return url_base.format(page=pagina)
    if re.search(r"[?&]page=\d*", url_base):
        return re.sub(r"([?&]page=)\d*", rf"\g<1>{pagina}", url_base)
    separador = "&" if "?" in url_base else "?"
    return f"{url_base}{separador}page={pagina}"


def descargar_lote(url_base: str, categoria: str, desde: int, hasta: int) -> list[Path]:
    """Descarga las páginas `desde`..`hasta` (inclusive) y las deja en caché."""
    if desde < 1:
        raise ValueError("desde debe ser mayor o igual que 1.")
    if hasta < desde:
        raise ValueError("hasta debe ser mayor o igual que desde.")

    rutas = []
    for pagina in range(desde, hasta + 1):
        url = _url_pagina(url_base, pagina)
        descargar_listado(url, categoria)
        rutas.append(_ruta_cache(url, categoria))
    return rutas


def contar_paginas(url_base: str, categoria: str = "motos") -> int:
    """Total de páginas de la búsqueda (pageInfo.pageCount del APOLLO_STATE__)."""
    html = descargar_listado(url_base, categoria)

    coincidencia = re.search(
        r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
        html,
        flags=re.S,
    )
    if not coincidencia:
        raise ValueError("No se encontró el script __NEXT_DATA__ en el HTML.")

    datos = json.loads(coincidencia.group(1))
    estado = datos["props"]["pageProps"].get("__APOLLO_STATE__", {})
    consulta = estado.get("ROOT_QUERY", {})

    for clave, valor in consulta.items():
        if clave.startswith("adsPerPage("):
            return int(valor["pageInfo"]["pageCount"])

    raise ValueError("No se encontró pageInfo.pageCount en el APOLLO_STATE__.")


def extraer_anuncios_listado(html: str) -> list[dict]:
    """Extrae los anuncios de un listado de Revolico desde __NEXT_DATA__."""
    coincidencia = re.search(
        r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
        html,
        flags=re.S,
    )
    if not coincidencia:
        raise ValueError("No se encontró el script __NEXT_DATA__ en el HTML.")

    datos = json.loads(coincidencia.group(1))
    page_props = datos["props"]["pageProps"]
    estado = page_props.get("__APOLLO_STATE__", {})

    base = "https://www.revolico.com"
    canonica = page_props.get("canonicalSearchUrl") or ""
    match_base = re.match(r"(https?://[^/]+)", canonica)
    if match_base:
        base = match_base.group(1)

    referencias = []
    for clave, valor in estado.items():
        if not (clave.startswith("adsPerPage(") or clave.startswith("promotedAds(")):
            continue
        for borde in valor.get("edges") or []:
            ref = (borde.get("node") or {}).get("__ref")
            if ref:
                referencias.append(ref)

    if not referencias:
        referencias = [clave for clave in estado if clave.startswith("AdType:")]

    def _slug(texto: str) -> str:
        plano = unicodedata.normalize("NFKD", texto)
        plano = plano.encode("ascii", "ignore").decode("ascii")
        return re.sub(r"[^a-z0-9]+", "-", plano.lower()).strip("-")

    anuncios = []
    vistos = set()
    for ref in referencias:
        anuncio_id = ref.split(":", 1)[-1]
        if anuncio_id in vistos:
            continue
        vistos.add(anuncio_id)

        anuncio = estado.get(ref)
        if not anuncio:
            continue

        stub = anuncio.get("permalink")
        if not stub:
            slug = _slug(anuncio.get("title") or "anuncio")
            stub = f"/item/{slug}-{anuncio_id}"

        anuncios.append(
            {
                "titulo": anuncio.get("title"),
                "precio": anuncio.get("price"),
                "moneda": anuncio.get("currency"),
                "provinceId": anuncio.get("provinceId"),
                "municipalityId": anuncio.get("municipalityId"),
                "url_detalle": base + stub,
            }
        )
    return anuncios


def es_moto_electrica(titulo: str) -> tuple[bool, str]:
    """Decide si un título es de moto eléctrica. Devuelve (bool, motivo)."""

    def normalizar(texto: str) -> str:
        plano = unicodedata.normalize("NFKD", (texto or "").lower())
        plano = plano.encode("ascii", "ignore").decode("ascii")
        plano = re.sub(r"[^a-z0-9]+", " ", plano)
        return re.sub(r"\s+", " ", plano).strip()

    texto = normalizar(titulo)

    exclusiones = (
        (
            "tipo_vehiculo",
            (
                "scooter",
                "bicimoto",
                "bici electrica",
                "bicicleta electrica",
                "patinete",
                "patineta",
                "triciclo",
                "trimoto",
                "3 ruedas",
                "cuatriciclo",
                "4 ruedas",
                "infantil",
                "nino",
                "ciclomotor",
            ),
        ),
        (
            "combustion",
            (
                "gasolina",
                "combustion",
                "combustible",
                "nafta",
                "diesel",
                "cilindrada",
                "carburador",
            ),
        ),
    )

    for categoria, palabras in exclusiones:
        for palabra in palabras:
            if palabra in texto:
                return False, f"excluido:{categoria}:{palabra}"

    if re.search(r"\b(?:2t|4t)\b", texto):
        return False, "excluido:combustion:2t/4t"

    if "moto electrica" in texto:
        return True, "incluido:moto electrica"
    if "motico" in texto:
        return True, "incluido:motico"
    if "moto" in texto and "electrica" in texto:
        return True, "incluido:moto+electrica"

    return False, "sin_inclusion"


def procesar_categoria(categoria: str) -> dict:
    """Lee los listados de `categoria`, extrae anuncios y deduplica por url_detalle."""
    if categoria not in CATEGORIAS:
        raise ValueError(
            f"Categoría desconocida: {categoria!r}. Usa una de {CATEGORIAS}."
        )

    anuncios = []
    for ruta in sorted((CACHE_DIR / categoria).glob("listado_*.html")):
        anuncios.extend(
            extraer_anuncios_listado(ruta.read_text(encoding="utf-8"))
        )

    unicos = []
    vistos = set()
    for anuncio in anuncios:
        if anuncio["url_detalle"] in vistos:
            continue
        vistos.add(anuncio["url_detalle"])
        unicos.append(anuncio)

    return {
        "categoria": categoria,
        "total_brutos": len(anuncios),
        "total_unicos": len(unicos),
        "anuncios": unicos,
    }


def _normalizar_titulo(texto: str) -> str:
    """Minúsculas, sin acentos y espacios colapsados."""
    plano = unicodedata.normalize("NFKD", (texto or "").lower())
    plano = plano.encode("ascii", "ignore").decode("ascii")
    plano = re.sub(r"[^a-z0-9]+", " ", plano)
    return re.sub(r"\s+", " ", plano).strip()


def limpiar_emojis(texto: str) -> str:
    """Elimina emojis y símbolos decorativos, colapsando espacios."""
    if not texto:
        return texto
    sin = re.sub(
        r"[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U00002B00-\U00002BFF"
        r"\U0000FE00-\U0000FE0F\U0001F900-\U0001F9FF\U0000231A-\U000023F0"
        r"\U00002190-\U000021FF\U00002598-\U000025FF]+",
        " ",
        texto,
    )
    return re.sub(r"\s+", " ", sin).strip()


_INCLUSION_BICI = (
    ("bici electrica", "incluido:bici electrica"),
    ("bicicleta electrica", "incluido:bicicleta electrica"),
)
_EXCLUSIONES_BICI = (
    (
        "tipo_vehiculo",
        (
            "scooter",
            "patinete",
            "patineta",
            "triciclo",
            "trimoto",
            "3 ruedas",
            "cuatriciclo",
            "4 ruedas",
            "infantil",
            "nino",
            "ciclomotor",
            "moto electrica",
            "motico",
        ),
    ),
    (
        "combustion",
        (
            "gasolina",
            "combustion",
            "combustible",
            "nafta",
            "diesel",
            "cilindrada",
            "carburador",
        ),
    ),
)


def es_bici_electrica(titulo: str) -> tuple[bool, str]:
    """Decide si un título es de bici eléctrica. Devuelve (bool, motivo)."""
    texto = _normalizar_titulo(titulo)

    for categoria, palabras in _EXCLUSIONES_BICI:
        for palabra in palabras:
            if palabra in texto:
                return False, f"excluido:{categoria}:{palabra}"

    if re.search(r"\b(?:2t|4t)\b", texto):
        return False, "excluido:combustion:2t/4t"
    if re.search(r"\bmoto\b", texto):
        return False, "excluido:tipo_vehiculo:moto"

    for frase, motivo in _INCLUSION_BICI:
        if frase in texto:
            return True, motivo
    if ("bici" in texto or "bicicleta" in texto) and "electr" in texto:
        return True, "incluido:bici+electrica"

    return False, "sin_inclusion"


_EXCLUSIONES_PATINETE = (
    (
        "tipo_vehiculo",
        (
            "triciclo",
            "trimoto",
            "3 ruedas",
            "cuatriciclo",
            "4 ruedas",
            "infantil",
            "nino",
            "ciclomotor",
            "moto electrica",
            "motico",
            "bicimoto",
            "bici electrica",
            "bicicleta electrica",
            "bicicleta",
        ),
    ),
    (
        "combustion",
        (
            "gasolina",
            "combustion",
            "combustible",
            "nafta",
            "diesel",
            "cilindrada",
            "carburador",
        ),
    ),
)


def es_patinete_electrico(titulo: str) -> tuple[bool, str]:
    """Decide si un título es de patinete eléctrico. Devuelve (bool, motivo)."""
    texto = _normalizar_titulo(titulo)

    for categoria, palabras in _EXCLUSIONES_PATINETE:
        for palabra in palabras:
            if palabra in texto:
                return False, f"excluido:{categoria}:{palabra}"

    if re.search(r"\b(?:2t|4t)\b", texto):
        return False, "excluido:combustion:2t/4t"
    if re.search(r"\bmoto\b", texto):
        return False, "excluido:tipo_vehiculo:moto"

    if any(p in texto for p in ("patinete", "patineta", "scooter")) and "electr" in texto:
        return True, "incluido:patinete+electrica"

    return False, "sin_inclusion"


def clasificar_listado(listado: dict) -> dict:
    """Clasifica los anuncios de un listado en moto/bici/patinete o descarte."""
    funciones = (
        ("moto", es_moto_electrica),
        ("bici", es_bici_electrica),
        ("patinete", es_patinete_electrico),
    )
    resultado = {
        "categoria_origen": listado.get("categoria"),
        "total": len(listado.get("anuncios", [])),
        "motos": [],
        "bicis": [],
        "patinetes": [],
        "descartados": [],
    }

    for anuncio in listado.get("anuncios", []):
        titulo = anuncio.get("titulo") or ""
        motivo = "sin_inclusion"
        asignado = False

        for clave, funcion in funciones:
            es, causa = funcion(titulo)
            if es:
                salida = dict(anuncio)
                salida["motivo"] = causa
                resultado[clave + "s"].append(salida)
                asignado = True
                break
            if causa != "sin_inclusion":
                motivo = causa

        if not asignado:
            salida = dict(anuncio)
            salida["motivo"] = motivo
            resultado["descartados"].append(salida)

    return resultado


def _deduplicar(anuncios: list[dict]) -> list[dict]:
    """Elimina duplicados por url_detalle conservando el primer cruce."""
    unicos = []
    vistos = set()
    for anuncio in anuncios:
        if anuncio["url_detalle"] in vistos:
            continue
        vistos.add(anuncio["url_detalle"])
        unicos.append(anuncio)
    return unicos


def consolidar_clasificados() -> tuple[list[dict], list[dict], list[dict]]:
    """Junta los 3 clasificados por categoría, sin duplicados por url_detalle."""
    carpeta = BASE_DIR / "data" / "processed" / "clasificados"
    motos, bicis, patinetes = [], [], []
    for categoria in CATEGORIAS:
        with open(carpeta / f"{categoria}_clasificado.json", encoding="utf-8") as f:
            clasificado = json.load(f)
        motos.extend(clasificado["motos"])
        bicis.extend(clasificado["bicis"])
        patinetes.extend(clasificado["patinetes"])
    return _deduplicar(motos), _deduplicar(bicis), _deduplicar(patinetes)


def extraer_patinetes_de_busquedas() -> list[dict]:
    """Extrae los patinetes válidos de los HTML de búsquedas alternativas."""
    patinetes = []
    carpeta = CACHE_DIR / "patinetes"
    for ruta in sorted(carpeta.glob("busqueda_*.html")):
        for anuncio in extraer_anuncios_listado(ruta.read_text(encoding="utf-8")):
            es, _ = es_patinete_electrico(anuncio["titulo"])
            if es:
                patinetes.append(anuncio)
    return patinetes


def seleccionar_muestra(lista: list[dict], n: int, seed: int = 42) -> list[dict]:
    """Devuelve una muestra aleatoria de `n` anuncios (fija si es menor)."""
    if len(lista) <= n:
        return list(lista)
    random.seed(seed)
    return random.sample(lista, n)


def _extraer_json_next(html: str) -> dict:
    """Devuelve el JSON del script __NEXT_DATA__ del HTML."""
    coincidencia = re.search(
        r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
        html,
        flags=re.S,
    )
    if not coincidencia:
        raise ValueError("No se encontró el script __NEXT_DATA__ en el HTML.")
    return json.loads(coincidencia.group(1))


_ESQUEMA_SINGULAR = {"motos": "moto", "bicis": "bici", "patinetes": "patinete"}


def _clave_normalizada(nombre) -> str:
    """Minúsculas, sin acentos y con separadores unificados."""
    texto = unicodedata.normalize("NFKD", (nombre or "").lower())
    texto = texto.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", " ", texto).strip()


def _titulo_es(nombre) -> str:
    """Title-case en español: conectores en minúscula."""
    conectores = {"de", "del", "la", "las", "el", "los", "al", "y"}
    palabras = []
    for i, parte in enumerate((nombre or "").strip().split()):
        if i > 0 and parte.lower() in conectores:
            palabras.append(parte.lower())
        else:
            palabras.append(parte[:1].upper() + parte[1:])
    return " ".join(palabras)


_PROVINCIAS_CANONICAS = (
    "Pinar del Río",
    "Artemisa",
    "La Habana",
    "Mayabeque",
    "Matanzas",
    "Cienfuegos",
    "Villa Clara",
    "Sancti Spíritus",
    "Ciego de Ávila",
    "Camagüey",
    "Las Tunas",
    "Holguín",
    "Granma",
    "Santiago de Cuba",
    "Guantánamo",
    "Isla de la Juventud",
)

PROVINCIAS = {_clave_normalizada(nombre): nombre for nombre in _PROVINCIAS_CANONICAS}

_MUNICIPIOS_CANONICOS = (
    "Consolación del Sur", "Guane", "La Palma", "Los Palacios", "Mantua",
    "Minas de Matahambre", "Pinar del Río", "San Juan y Martínez", "San Luis",
    "Sandino", "Viñales", "Alquízar", "Artemisa", "Bauta", "Caimito", "Guanajay",
    "Güira de Melena", "Mariel", "San Antonio de los Baños", "Bahía Honda",
    "San Cristóbal", "Candelaria", "Batabanó", "Bejucal", "Güines", "Jaruco",
    "Madruga", "Melena del Sur", "Nueva Paz", "Quivicán", "San José de las Lajas",
    "San Nicolás de Bari", "Santa Cruz del Norte", "Arroyo Naranjo", "Boyeros",
    "Centro Habana", "Cerro", "Cotorro", "Diez de Octubre", "Guanabacoa",
    "Habana del Este", "Habana Vieja", "La Lisa", "Marianao", "Playa", "Plaza",
    "Regla", "San Miguel del Padrón", "Calimete", "Cárdenas", "Ciénaga de Zapata",
    "Colón", "Jagüey Grande", "Jovellanos", "Limonar", "Los Arabos", "Martí",
    "Matanzas", "Pedro Betancourt", "Perico", "Unión de Reyes", "Abreus",
    "Aguada de Pasajeros", "Cienfuegos", "Cruces", "Cumanayagua", "Palmira",
    "Rodas", "Santa Isabel de las Lajas", "Caibarién", "Camajuaní", "Cifuentes",
    "Corralillo", "Encrucijada", "Manicaragua", "Placetas", "Quemado de Güines",
    "Ranchuelo", "Remedios", "Sagua la Grande", "Santa Clara", "Santo Domingo",
    "Cabaiguán", "Fomento", "Jatibonico", "La Sierpe", "Sancti Spíritus",
    "Taguasco", "Trinidad", "Yaguajay", "Ciro Redondo", "Baraguá", "Bolivia",
    "Chambas", "Ciego de Ávila", "Florencia", "Majagua", "Morón",
    "Primero de Enero", "Venezuela", "Camagüey", "Carlos Manuel de Céspedes",
    "Esmeralda", "Florida", "Guáimaro", "Jimaguayú", "Minas", "Najasa", "Nuevitas",
    "Santa Cruz del Sur", "Sibanicú", "Sierra de Cubitas", "Vertientes",
    "Amancio Rodríguez", "Colombia", "Jesús Menéndez", "Jobabo", "Las Tunas",
    "Majibacoa", "Manatí", "Puerto Padre", "Antilla", "Báguanos", "Banes",
    "Cacocum", "Calixto García", "Cueto", "Frank País", "Gibara", "Holguín",
    "Mayarí", "Moa", "Rafael Freyre", "Sagua de Tánamo", "Urbano Noris",
    "Bartolomé Masó", "Bayamo", "Buey Arriba", "Campechuela", "Cauto Cristo",
    "Guisa", "Jiguaní", "Manzanillo", "Media Luna", "Niquero", "Pilón",
    "Río Cauto", "Yara", "Contramaestre", "Guamá", "Julio Antonio Mella",
    "Palma Soriano", "San Luis", "Santiago de Cuba", "Segundo Frente",
    "Songo-La Maya", "Tercer Frente", "Baracoa", "Caimanera", "El Salvador",
    "Guantánamo", "Imías", "Maisí", "Manuel Tames", "Niceto Pérez",
    "San Antonio del Sur", "Yateras", "Isla de la Juventud",
)

MUNICIPIOS = {_clave_normalizada(nombre): nombre for nombre in _MUNICIPIOS_CANONICOS}


def normalizar_provincia(nombre: str) -> str:
    """Devuelve el nombre canónico de la provincia."""
    return PROVINCIAS.get(_clave_normalizada(nombre)) or _titulo_es(nombre)


def normalizar_municipio(nombre: str) -> str:
    """Devuelve el nombre canónico del municipio."""
    return MUNICIPIOS.get(_clave_normalizada(nombre)) or _titulo_es(nombre)


def normalizar_moneda(moneda) -> str:
    """'usd' → 'USD'."""
    if not moneda:
        return None
    return moneda.strip().upper()


def extraer_catalogos(html: str) -> dict:
    """Resuelve los catálogos de provincias y municipios del APOLLO_STATE__.

    Devuelve {"provincias": {id: nombre}, "municipios": {id: nombre}}.
    """
    estado = _extraer_json_next(html)["props"]["pageProps"].get("__APOLLO_STATE__", {})
    provincias = {}
    municipios = {}
    for clave, valor in estado.items():
        if clave.startswith("ProvinceType:"):
            provincias[clave.split(":", 1)[1]] = valor.get("name")
        elif clave.startswith("MunicipalityType:"):
            municipios[clave.split(":", 1)[1]] = valor.get("name")
    return {"provincias": provincias, "municipios": municipios}


def resolver_ubicacion(provinceId, municipalityId, catalogos: dict):
    """Devuelve (provincia, municipio) canónicos a partir de los ids resueltos."""
    nombre_provincia = catalogos.get("provincias", {}).get(str(provinceId))
    nombre_municipio = catalogos.get("municipios", {}).get(str(municipalityId))
    if nombre_provincia:
        nombre_provincia = normalizar_provincia(nombre_provincia)
    if nombre_municipio:
        nombre_municipio = normalizar_municipio(nombre_municipio)
    return nombre_provincia, nombre_municipio


def extraer_detalle(html: str) -> dict:
    """Extrae los campos generales de un anuncio desde el APOLLO_STATE__."""
    datos = _extraer_json_next(html)
    page_props = datos["props"]["pageProps"]
    estado = page_props.get("__APOLLO_STATE__", {})

    anuncio = None
    for clave, valor in estado.items():
        if clave.startswith("AdType:"):
            anuncio = valor
            break
    if not anuncio:
        raise ValueError("No se encontró AdType en el APOLLO_STATE__.")

    base = "https://www.revolico.com"
    canonica = page_props.get("canonicalSearchUrl") or ""
    match_base = re.match(r"(https?://[^/]+)", canonica)
    if match_base:
        base = match_base.group(1)

    def _ref_id(valor):
        return (valor or {}).get("__ref", "").split(":", 1)[-1] or None

    return {
        "id_anuncio": anuncio.get("id"),
        "titulo": anuncio.get("title"),
        "descripcion": anuncio.get("description"),
        "precio_usd": anuncio.get("price"),
        "vendedor": anuncio.get("name"),
        "url_anuncio": base + (anuncio.get("permalink") or ""),
        "provinceId": _ref_id(anuncio.get("province")),
        "municipalityId": _ref_id(anuncio.get("municipality")),
        "viewCount": anuncio.get("viewCount"),
        "isSold": anuncio.get("isSold"),
        "updatedOnByUser": anuncio.get("updatedOnByUser"),
    }


def extraer_campos_tecnicos(descripcion: str) -> dict:
    """Extrae los campos técnicos de la descripción vía regex. Se normaliza antes."""
    texto = _normalizar_titulo(descripcion)
    crudo = descripcion or ""

    def _primero(patron, convertir=int):
        coincidencia = re.search(patron, texto)
        if not coincidencia:
            return None
        valor = coincidencia.group(1)
        return convertir(valor)

    def _a_int(numero_txt):
        limpio = numero_txt.replace(",", "")
        if re.fullmatch(r"\d{1,3}(?:\.\d{3})+", limpio):
            return int(limpio.replace(".", ""))
        return int(round(float(limpio)))

    motor = _primero(r"\b(\d{1,4})\s*w(?:atts)?\b")
    voltaje = _primero(r"\b(\d{1,3})\s*v\b")

    amperaje = None
    coincidencia = re.search(r"\b(\d{1,3}(?:\.\d+)?)\s*ah\b", crudo, re.I)
    if coincidencia:
        amperaje = int(float(coincidencia.group(1)))

    autonomia = None
    for patron_contexto in (
        r"autonomia\D{0,15}?(\d{1,4})\s*km",
        r"(\d{1,4})\s*km\s*(?:de\s+)?(?:autonomia|recorrido|alcance)",
    ):
        coincidencia = re.search(patron_contexto, texto)
        if coincidencia:
            valor = int(coincidencia.group(1))
            if valor >= 10:
                autonomia = valor
                break
    if autonomia is None:
        for coincidencia in re.finditer(r"(?<![\d,.])(\d{1,4})\s*km\b(?!\s*h)", texto):
            valor = int(coincidencia.group(1))
            if valor >= 10:
                autonomia = valor
                break

    velocidad = None
    coincidencia = re.search(r"(\d{1,3})\s*km\s*h\b", texto)
    if coincidencia:
        velocidad = int(coincidencia.group(1))

    compacto = re.search(r"(\d{2,3})\s*v\s*(\d{1,3})\s*ah", texto)
    if compacto:
        if voltaje is None:
            voltaje = int(compacto.group(1))
        if amperaje is None:
            amperaje = int(compacto.group(2))

    motor_v = re.search(r"(\d{3,5})\s*w\s*(\d{2,3})\s*v", texto)
    if motor_v:
        if motor is None:
            motor = int(motor_v.group(1))
        if voltaje is None:
            voltaje = int(motor_v.group(2))

    if re.search(r"lit(?:io|ium|hium|ihum)|\bli\s?ion\b", texto):
        tipo_bateria = "litio"
    elif "plomo" in texto or "lead acid" in texto:
        tipo_bateria = "plomo"
    else:
        tipo_bateria = None

    precio_usd = None
    moneda = None
    coincidencia = re.search(r"\bprecio\s*[:=]?\s*\$?\s*(\d[\d.,]*)\s*(usd|cup)?\b", crudo, re.I)
    if coincidencia:
        moneda = normalizar_moneda(coincidencia.group(2) or "usd")
        if moneda == "USD":
            precio_usd = _a_int(coincidencia.group(1))

    transporte_incluido = bool(re.search(
        r"transporte\s+incluido|transportacion\s+incluida|transporte\s+gratis|transportacion\s+gratis|"
        r"entrega\s+incluida|entrega\s+gratis|envio\s+incluido|envio\s+gratis|mensajeria\s+incluida|"
        r"domicilio\s+incluido|entrega\s+a\s+domicilio\s+incluida|envio\s+a\s+domicilio|"
        r"sin\s+costo\s+de\s+envio|llevo\s+hasta|(?:se|te)\s+la\s+llev[oa]",
        texto,
    ))

    papeles = "en regla" if re.search(r"papeles (en regla|al dia)|con papeles", texto) else None

    estado = None
    if re.search(r"\b0\s*km\b|\bnueva\b|\bnuevas\b", texto):
        estado = "Nueva"
    elif "seminueva" in texto or "semi nueva" in texto:
        estado = "Seminueva"
    elif re.search(r"\busada\b|\busado\b|segunda mano|primera mano", texto):
        estado = "Usada"

    tiempo_carga_horas = None
    coincidencia = re.search(r"(?:carga|recarga).{0,25}?(\d{1,2}(?:\.\d+)?)\s*horas?\b", texto)
    if not coincidencia:
        coincidencia = re.search(r"(\d{1,2}(?:\.\d+)?)\s*horas?\b", texto)
    if coincidencia:
        tiempo_carga_horas = int(float(coincidencia.group(1)))

    garantia_dias = None
    if re.search(r"garant[ií]a", texto):
        coincidencia = re.search(r"garant[ií]a.{0,20}?(\d{1,3})\s*mes(?:es)?", texto)
        if coincidencia:
            garantia_dias = int(coincidencia.group(1)) * 30
        else:
            coincidencia = re.search(r"garant[ií]a.{0,20}?(\d{1,4})\s*d[ií]as?", texto)
            if coincidencia:
                garantia_dias = int(coincidencia.group(1))

    peso_kg = None
    coincidencia = re.search(r"peso\s*[:]?\s*(\d{2,4})\s*kg\b", texto)
    if coincidencia:
        peso_kg = int(coincidencia.group(1))

    tipo_frenos = None
    if re.search(r"freno", texto):
        disco = "disco" in texto
        tambor = "tambor" in texto
        if disco and tambor:
            tipo_frenos = "disco y tambor"
        elif disco:
            tipo_frenos = "disco"
        elif tambor:
            tipo_frenos = "tambor"

    tamano_rueda_pulgadas = None
    coincidencia = re.search(r"(\d{2})\s*(?:pulgadas|pulg)\b", texto)
    if coincidencia:
        tamano_rueda_pulgadas = int(coincidencia.group(1))

    suspension = None
    if re.search(r"suspen[cs]ion|amortiguador", texto):
        suspension = True

    accesorios = []
    for palabra in ("casco", "guantes", "mochila", "candado", "alarma",
                    "bluetooth", "cargador", "espejos", "matricula"):
        if palabra in texto:
            accesorios.append(palabra)

    return {
        "motor_w": motor,
        "voltaje_v": voltaje,
        "amperaje_ah": amperaje,
        "autonomia_km": autonomia,
        "velocidad_max_kmh": velocidad,
        "tipo_bateria": tipo_bateria.lower() if tipo_bateria else None,
        "precio_usd": precio_usd,
        "moneda": moneda,
        "transporte_incluido": transporte_incluido,
        "papeles": papeles,
        "estado": estado,
        "tiempo_carga_horas": tiempo_carga_horas,
        "garantia_dias": garantia_dias,
        "peso_kg": peso_kg,
        "tipo_frenos": tipo_frenos,
        "tamano_rueda_pulgadas": tamano_rueda_pulgadas,
        "suspension": suspension,
        "accesorios": accesorios,
    }


_MARCAS = (
    (r"\btopmaq\b", "Topmaq"),
    (r"yoazaky|yoazaki|yoazak|yoa ?zaky", "Yoazaki"),
    (r"\bizuki\b", "Izuki"),
    (r"\bxmox\b", "Xmox"),
    (r"\bvedca\b", "Vedca"),
    (r"kvitova|kivitova|kitova", "Kvitova"),
    (r"bucatt?i|buccati", "Bucatti"),
    (r"\bmishozuki\b", "Mishozuki"),
    (r"\bmikazuki\b", "Mikazuki"),
    (r"\bhalcon\b", "Halcon"),
    (r"\bmountain\b", "Mountain"),
    (r"\bmaf\b", "Maf"),
    (r"\bmaox\b", "Maox"),
    (r"\btorvan\b", "Torvan"),
    (r"\bpanda\b", "Panda"),
    (r"\bfly\b", "Fly"),
    (r"\bdcmlz\b", "DCM-LZ"),
    (r"protenzza|protenza|prontenza", "Protenzza"),
    (r"\bmurasaki\b", "Murasaki"),
    (r"\bvoltax\b", "Voltax"),
    (r"\bvolta\b", "Volta"),
    (r"\bmeacon\b", "Meacon"),
)

_MODELOS = (
    (r"new big shark 2", "New Big Shark 2"),
    (r"big shark 2", "Big Shark 2"),
    (r"buho ultra", "Búho Ultra"),
    (r"predator max", "Predator Max"),
    (r"mountain racer", "Mountain Racer"),
    (r"super run", "Super Run"),
    (r"panda city", "Panda City"),
    (r"\bavispon\b", "Avispón"),
    (r"pla ?51", "Pla 51"),
    (r"\bcorleone\b", "Corleone"),
    (r"\bchallenger\b", "Challenger"),
    (r"\bshikra\b", "Shikra"),
    (r"\bt[- ]max\b", "T-Max"),
    (r"\belegant\b", "Elegant"),
    (r"\bee04\b", "EE04"),
    (r"\bff04\b", "FF04"),
    (r"\be[- ]4\b", "E4"),
    (r"\be3\b", "E3"),
    (r"\bflamen?go\b", "Flamingo"),
    (r"\baguila\b", "Águila"),
    (r"shark sport", "Shark Sport"),
    (r"\bf3\b", "F3"),
    (r"\bs90\b", "S90"),
    (r"\bn3\b", "N3"),
    (r"\btank\b", "Tank"),
    (r"\b707\b", "707"),
    (r"\bpd\b", "PD"),
    (r"\bb1\b", "B1"),
    (r"\brx\b", "RX"),
    (r"\bsport\b", "Sport"),
)


def _extraer_marca_modelo(texto: str) -> tuple:
    """Devuelve (marca, modelo) canónicos a partir de título+descripción."""
    texto = _clave_normalizada(texto)
    marca = None
    for patron, canonic in _MARCAS:
        if re.search(patron, texto):
            marca = canonic
            break
    modelo = None
    for patron, canonic in _MODELOS:
        if re.search(patron, texto):
            modelo = canonic
            break
    return marca, modelo


def _vendedor_id(nombre) -> str:
    """Hash anónimo del vendedor: SHA-256 truncado a 10 caracteres. Nunca el nombre real."""
    if not nombre:
        return None
    clave = _clave_normalizada(nombre)
    return hashlib.sha256(clave.encode("utf-8")).hexdigest()[:10]


def construir_anuncio_segun_esquema(
    detalle: dict, tecnicos: dict, categoria: str
) -> dict:
    """Construye un anuncio con todos los campos del esquema de `categoria`."""
    singular = _ESQUEMA_SINGULAR.get(categoria, categoria)
    nombre_esquema = {
        "moto": "esquema_moto_electrica.json",
        "bici": "esquema_bici_electrica.json",
        "patinete": "esquema_patinete_electrico.json",
    }.get(singular, f"esquema_{singular}_electrica.json")
    ruta_esquema = BASE_DIR / "docs/schemas" / nombre_esquema

    with open(ruta_esquema, encoding="utf-8") as f:
        esquema = json.load(f)

    campos = esquema["anuncios"][0]
    ejemplo_tipo_vehiculo = campos.get("tipo_vehiculo")

    marca, modelo = _extraer_marca_modelo(
        f"{detalle.get('titulo')} {detalle.get('descripcion')}"
    )

    mapeo = {
        "id_anuncio": detalle.get("id_anuncio"),
        "titulo": limpiar_emojis(detalle.get("titulo")),
        "precio_usd": detalle.get("precio_usd") or tecnicos.get("precio_usd"),
        "fecha_publicacion": detalle.get("updatedOnByUser"),
        "marca": marca,
        "modelo": modelo,
        "tipo_vehiculo": ejemplo_tipo_vehiculo,
        "motor_w": tecnicos.get("motor_w"),
        "voltaje_v": tecnicos.get("voltaje_v"),
        "amperaje_ah": tecnicos.get("amperaje_ah"),
        "tipo_bateria": tecnicos.get("tipo_bateria"),
        "autonomia_km": tecnicos.get("autonomia_km"),
        "velocidad_max_kmh": tecnicos.get("velocidad_max_kmh"),
        "tiempo_carga_horas": tecnicos.get("tiempo_carga_horas"),
        "garantia_dias": tecnicos.get("garantia_dias"),
        "peso_kg": tecnicos.get("peso_kg"),
        "tamano_rueda_pulgadas": tecnicos.get("tamano_rueda_pulgadas"),
        "tipo_frenos": tecnicos.get("tipo_frenos"),
        "suspension": tecnicos.get("suspension"),
        "estado": tecnicos.get("estado"),
        "papeles": tecnicos.get("papeles"),
        "accesorios": tecnicos.get("accesorios") or [],
        "municipio": detalle.get("municipalityId"),
        "descripcion": limpiar_emojis(detalle.get("descripcion")),
        "url_anuncio": detalle.get("url_anuncio"),
        "vendedor_id": _vendedor_id(detalle.get("vendedor")),
        "transporte_incluido": tecnicos.get("transporte_incluido"),
    }

    anuncio = {}
    for clave in campos:
        if clave == "accesorios":
            valor = mapeo.get("accesorios") or []
        elif clave in ("plegable", "ubicacion"):
            valor = None
        else:
            valor = mapeo.get(clave, None)
        anuncio[clave] = valor

    return anuncio


CAMPOS_OBLIGATORIOS = (
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

CAMPOS_PARCIALES = (
    "id_anuncio",
    "titulo",
    "precio_usd",
    "url_anuncio",
    "tipo_vehiculo",
    "descripcion",
)


def _campos_faltantes(anuncio: dict, campos) -> list:
    return [campo for campo in campos if anuncio.get(campo) in (None, "")]


def validar_anuncio_completo(anuncio: dict) -> tuple[bool, list]:
    """Devuelve (True, []) si cumple los 10 campos obligatorios o (False, faltantes)."""
    faltantes = _campos_faltantes(anuncio, CAMPOS_OBLIGATORIOS)
    return (not faltantes, faltantes)


def validar_anuncio_parcial(anuncio: dict) -> tuple[bool, list]:
    """Devuelve (True, []) si cumple los 6 campos básicos o (False, faltantes)."""
    faltantes = _campos_faltantes(anuncio, CAMPOS_PARCIALES)
    return (not faltantes, faltantes)


def procesar_detalles(categoria: str, max_anuncios: int = None, ruta_muestra: str = None) -> dict:
    """Procesa los detalles cacheados de una muestra y los valida por categoría."""
    if ruta_muestra is None:
        carpeta_muestras = BASE_DIR / "data/processed/muestras"
        candidatos = sorted(carpeta_muestras.glob(f"{categoria}_muestra_*.json"))
        if not candidatos:
            raise FileNotFoundError(
                f"No hay ninguna muestra para '{categoria}' en {carpeta_muestras} "
                f"(patrón buscado: {categoria}_muestra_*.json)"
            )
        ruta_muestra = candidatos[0]
    ruta = Path(ruta_muestra)
    if not ruta.is_absolute():
        if ruta.parent == Path("."):
            ruta = BASE_DIR / "data/processed/muestras" / ruta
        else:
            ruta = BASE_DIR / ruta
    with open(ruta, encoding="utf-8") as f:
        muestra = json.load(f)
    if max_anuncios is not None:
        muestra = muestra[:max_anuncios]

    carpeta_detalle = CACHE_DIR.parent / "cache_detalle" / categoria

    catalogos = {"provincias": {}, "municipios": {}}
    listados = sorted((CACHE_DIR / categoria).glob("listado_*.html"))
    if listados:
        catalogos = extraer_catalogos(listados[0].read_text(encoding="utf-8"))

    validos_completos = []
    validos_parciales = []
    descartados = []
    for item in muestra:
        idd = item["url_detalle"].rstrip("/").rsplit("-", 1)[-1]
        ruta = carpeta_detalle / f"detalle_{idd}.html"
        if not ruta.exists():
            descartados.append({"anuncio": {"id_anuncio": idd}, "campos_faltantes": ["detalle_faltante"]})
            continue
        try:
            html = ruta.read_text(encoding="utf-8")
            detalle = extraer_detalle(html)
            tecnicos = extraer_campos_tecnicos(detalle["descripcion"])
            anuncio = construir_anuncio_segun_esquema(detalle, tecnicos, categoria)
            provincia, municipio = resolver_ubicacion(
                detalle["provinceId"], detalle["municipalityId"], catalogos
            )
            anuncio["municipio"] = municipio
            anuncio["ubicacion"] = provincia
        except (ValueError, KeyError, json.JSONDecodeError) as e:
            descartados.append({"anuncio": {"id_anuncio": idd}, "campos_faltantes": [f"error_lectura: {e}"]})
            continue

        ok_completo, _ = validar_anuncio_completo(anuncio)
        if ok_completo:
            validos_completos.append(anuncio)
            continue

        ok_parcial, faltantes = validar_anuncio_parcial(anuncio)
        if ok_parcial:
            validos_parciales.append(anuncio)
        else:
            descartados.append({"anuncio": anuncio, "campos_faltantes": faltantes})

    return {
        "validos_completos": validos_completos,
        "validos_parciales": validos_parciales,
        "descartados": descartados,
        "total": len(muestra),
    }


if __name__ == "__main__":
    casos = [
        ("https://www.revolico.com/search?a=b", 3, "https://www.revolico.com/search?a=b&page=3"),
        ("https://www.revolico.com/search?a=b&page=5", 7, "https://www.revolico.com/search?a=b&page=7"),
        ("https://www.revolico.com/search?a=b&page=", 3, "https://www.revolico.com/search?a=b&page=3"),
        ("https://www.revolico.com/search?a=b&page={page}", 7, "https://www.revolico.com/search?a=b&page=7"),
    ]
    for entrada, pagina, esperada in casos:
        resultado = _url_pagina(entrada, pagina)
        assert resultado == esperada, f"{entrada!r} -> {resultado!r} (esperado {esperada!r})"
    print("_url_pagina: 4 casos OK")

