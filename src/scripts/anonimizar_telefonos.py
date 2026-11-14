"""
Script de anonimización de datos personales.
Busca números de teléfono cubanos (+53...) y enlaces de WhatsApp (wa.me/...)
en todos los archivos JSON de los datos procesados y los reemplaza por
'[TELÉFONO REDACTADO]'.

Uso:
    python src/scripts/anonimizar_telefonos.py
"""
import json
import re
from pathlib import Path

# Patrón de búsqueda:
# 1. Opcional +53, seguido de 8 a 10 dígitos (permitiendo espacios).
# 2. Enlaces tipo wa.me/12345678
PATRON_TELEFONO = re.compile(r'(\+?53\s*\d{8,10})|(wa\.me/\d+)', re.IGNORECASE)

RUTA_DATOS = Path("data/processed/final")

def anonimizar_json(archivo: Path) -> bool:
    """Lee un JSON, reemplaza los teléfonos y lo guarda si hubo cambios."""
    try:
        contenido_original = archivo.read_text(encoding="utf-8")
        contenido_limpio = PATRON_TELEFONO.sub("[TELÉFONO REDACTADO]", contenido_original)

        if contenido_original != contenido_limpio:
            # Validar que el JSON sigue siendo válido antes de sobrescribir
            json.loads(contenido_limpio)
            archivo.write_text(contenido_limpio, encoding="utf-8")
            return True
            
    except json.JSONDecodeError:
        print(f"❌ Error: El reemplazo rompería el JSON en {archivo.name}. Archivo omitido.")
    except Exception as e:
        print(f"⚠️ Error procesando {archivo.name}: {e}")
        
    return False

def main():
    print(f"Buscando teléfonos en: {RUTA_DATOS}...")
    modificados = 0
    
    # rglob('*.json') busca recursivamente en todas las subcarpetas
    for archivo in RUTA_DATOS.rglob("*.json"):
        if anonimizar_json(archivo):
            print(f"✅ Limpiado: {archivo.relative_to(RUTA_DATOS)}")
            modificados += 1
            
    print(f"\nProceso terminado. Archivos modificados: {modificados}")

if __name__ == "__main__":
    main()
