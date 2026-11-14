import json, re
from pathlib import Path

# Regex mejorado: captura espacios, +53, enlaces de WhatsApp, Telegram y Facebook
PATRON_TEL = re.compile(r'(\+?53[\s-]*\d[\s-]*\d{3}[\s-]*\d{4}|\b[5-7][\s-]*\d{3}[\s-]*\d{4}\b)')
PATRON_LINKS = re.compile(r'(wa\.me/message/[^\s"\\]+|t\.me/[^\s"\\]+|facebook\.com/profile\.php\?id=[^\s"\\]+)', re.IGNORECASE)
PATRON_EMAIL = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')

CAMPOS_TEXTO = ['titulo', 'descripcion', 'vendedor']
CARPETAS = [Path('data/final/JSON'), Path('data/processed')]

def limpiar_texto(texto):
    if not isinstance(texto, str): return texto
    texto = PATRON_TEL.sub('[TELÉFONO]', texto)
    texto = PATRON_LINKS.sub('[ENLACE]', texto)
    texto = PATRON_EMAIL.sub('[EMAIL]', texto)
    return texto

def limpiar_json(ruta):
    try:
        with open(ruta, 'r', encoding='utf-8') as f: datos = json.load(f)
    except: return False
    modificado = False
    if isinstance(datos, list):
        for reg in datos:
            if isinstance(reg, dict):
                for campo in CAMPOS_TEXTO:
                    if campo in reg and reg[campo]:
                        orig = reg[campo]
                        reg[campo] = limpiar_texto(orig)
                        if reg[campo] != orig: modificado = True
    elif isinstance(datos, dict):
        for clave, valor in datos.items():
            if isinstance(valor, str) and clave in CAMPOS_TEXTO:
                orig = valor
                datos[clave] = limpiar_texto(orig)
                if datos[clave] != orig: modificado = True
    if modificado:
        with open(ruta, 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
        return True
    return False

for carpeta in CARPETAS:
    if not carpeta.exists(): continue
    for ruta in carpeta.rglob('*.json'):
        if limpiar_json(ruta): print(f'✅ Limpiado: {ruta.name}')
