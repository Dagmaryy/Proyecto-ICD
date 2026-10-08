from bs4 import BeautifulSoup
import re


def extraer_anuncio_ruta(ruta_archivo="data/raw/revolico/motoprueba.html"):
    """
    Lee un archivo HTML de un anuncio de Revolico y extrae 4 campos:
    titulo, precio_usd, descripcion y url_anuncio.

    Args:
        ruta_archivo (str): Ruta al archivo HTML a procesar.

    Returns:
        dict: Diccionario con los campos extraídos.
    """
    # Leer archivo HTML
    with open(ruta_archivo, "r", encoding="utf-8", errors="ignore") as archivo:
        html = archivo.read()

    # Parsear HTML con BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    # Extraer título (comúnmente en etiqueta h1)
    titulo = ""
    tag_titulo = soup.find("h1")
    if tag_titulo:
        titulo = tag_titulo.get_text(strip=True)

    # Extraer precio en USD
    precio_usd = ""
    # Buscar patrones comunes: $ XX USD, USD XX, XX USD
    texto_html = soup.get_text(" ", strip=True)
    patron_precio = re.search(r"(?:\$|USD)\s*([0-9]+(?:\.[0-9]+)?)", texto_html, re.IGNORECASE)
    if patron_precio:
        precio_usd = patron_precio.group(1).strip()
    else:
        # Alternativa: buscar números con $ delante
        patron_precio_alt = re.search(r"\$\s*([0-9]+(?:\.[0-9]+)?)", texto_html)
        if patron_precio_alt:
            precio_usd = patron_precio_alt.group(1).strip()

    # Extraer descripción del anuncio
    descripcion = ""
    # Intentar con contenedor de descripción más común en Revolico
    contenedor_desc = (
        soup.find("div", class_=re.compile(r"(description|content|texto|detalle)", re.IGNORECASE))
        or soup.find("section", class_=re.compile(r"(description|content)", re.IGNORECASE))
        or soup.find("article")
    )
    if contenedor_desc:
        # Eliminar posibles scripts o estilos
        for tag in contenedor_desc.find_all(["script", "style"]):
            tag.decompose()
        descripcion = contenedor_desc.get_text(separator=" ", strip=True)
    else:
        # Fallback: usar cuerpo completo y limpiar
        cuerpo = soup.find("body")
        if cuerpo:
            for tag in cuerpo.find_all(["script", "style", "nav", "header", "footer"]):
                tag.decompose()
            descripcion = cuerpo.get_text(separator=" ", strip=True)

    # Extraer URL del anuncio
    url_anuncio = ""
    # Buscar canonical o enlace permanente
    link_canonical = soup.find("link", rel=re.compile(r"canonical", re.IGNORECASE))
    if link_canonical and link_canonical.get("href"):
        url_anuncio = link_canonical.get("href").strip()

    # Alternativas: meta og:url o enlace con rel=bookmark
    if not url_anuncio:
        meta_og = soup.find("meta", property=re.compile(r"og:url", re.IGNORECASE))
        if meta_og and meta_og.get("content"):
            url_anuncio = meta_og.get("content").strip()

    if not url_anuncio:
        link_bookmark = soup.find("a", rel=re.compile(r"bookmark", re.IGNORECASE))
        if link_bookmark and link_bookmark.get("href"):
            url_anuncio = link_bookmark.get("href").strip()

    # Resultado
    resultado = {
        "titulo": titulo,
        "precio_usd": precio_usd,
        "descripcion": descripcion,
        "url_anuncio": url_anuncio,
    }

    return resultado


# Ejemplo de uso
if __name__ == "__main__":
    datos = extraer_anuncio_ruta()
    print(datos)

