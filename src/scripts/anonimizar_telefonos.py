"""
Anonimiza teléfonos y correos SOLO en campos de texto (titulo, descripcion).
Evita borrar IDs de anuncios, precios o años.
"""
import json
import re
from pathlib import Path

# Regex para teléfonos: +53 seguido de 8-10 dígitos, o números de 8 dígitos que empiecen por 5, 6 o 7
PATRON_TELEFONO = re.compile(r'(\+?53\s*\d{8,10}|\b[5-7]\d{7}\b)')
PATRON_EMAIL = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')

# Solo limpiamos estos campos
CAMPOS_TEXTO = ['titulo', 'descripcion', 'vendedor']

CARPETAS = [Path('data/final/JSON'), Path('data/processed')]

def limpiar_texto(texto):
    if not isinstance(texto, str):
        return texto
    nuevo = PATRON_TELEFONO.sub('[TELÉFONO]', texto)
    nuevo = PATRON_EMAIL.sub('[EMAIL]', nuevo)
    return nuevo

def limpiar_json(ruta):
    try:
        with open(ruta, 'r', encoding='utf-8') as f:
            datos = json.load(f)
    except Exception:
        return False

    modificado = False
    # Si es una lista de registros
    if isinstance(datos, list):
        for registro in datos:
            if isinstance(registro, dict):
                for campo in CAMPOS_TEXTO:
                    if campo in registro and registro[campo]:
                        original = registro[campo]
                        registro[campo] = limpiar_texto(original)
                        if registro[campo] != original:
                            modificado = True
    
    # Si es un diccionario (ej. entrevistas)
    elif isinstance(datos, dict):
        for clave, valor in datos.items():
            if isinstance(valor, str) and clave in CAMPOS_TEXTO:
                original = valor
                datos[clave] = limpiar_texto(original)
                if datos[clave] != original:
                    modificado = True

    if modificado:
        with open(ruta, 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
        return True
    return False

def main():
    print("Iniciando anonimización quirúrgica...")
    modificados = 0
    for carpeta in CARPETAS:
        if not carpeta.exists(): continue
        for ruta in carpeta.rglob('*.json'):
            if limpiar_json(ruta):
                print(f"✅ Limpiado: {ruta.name}")
                modificados += 1
    print(f"\nTotal archivos modificados: {modificados}")

if __name__ == '__main__':
    main()
