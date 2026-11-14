"""
Verifica que no queden teléfonos ni correos en data/final/.
"""
import re
from pathlib import Path

PATRON_TELEFONO = re.compile(r'(\+?53\s*\d{8,10}|\b\d{8}\b)')
PATRON_EMAIL = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
CARPETAS = [Path('data/final/JSON'), Path('data/final/CSV')]

def verificar():
    print("Verificando anonimización...")
    hallazgos = 0
    for carpeta in CARPETAS:
        if not carpeta.exists(): continue
        for ruta in carpeta.rglob('*'):
            if ruta.is_file() and ruta.suffix in ('.json', '.csv'):
                contenido = ruta.read_text(encoding='utf-8')
                telefonos = PATRON_TELEFONO.findall(contenido)
                emails = PATRON_EMAIL.findall(contenido)
                if telefonos or emails:
                    print(f"⚠️ {ruta.name}: {len(telefonos)} teléfonos, {len(emails)} emails.")
                    hallazgos += 1
                    
    if hallazgos == 0:
        print("✅ Todo limpio. No se encontraron teléfonos ni emails.")
    else:
        print(f"❌ Quedan {hallazgos} archivos con datos sensibles.")

if __name__ == '__main__':
    verificar()
