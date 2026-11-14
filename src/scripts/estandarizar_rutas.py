"""
Estandariza los nombres de archivos en los scripts de análisis.
Cambia las referencias a los archivos antiguos (ej. motos_electricas_300.json)
por los nuevos archivos enriquecidos (ej. motos_electricas_300_enriquecido.json).
"""
from pathlib import Path

SCRIPTS_DIR = Path('src/analysis')

def estandarizar():
    print("Estandarizando nombres de archivos en los scripts...")
    reemplazos = {
        'motos_electricas_300.json': 'motos_electricas_300_enriquecido.json',
        'motos_combustion_300.json': 'motos_combustion_300_enriquecido.json',
        'bicis_300.json': 'bicis_300_enriquecido.json',
        'patinetes_300.json': 'patinetes_300_enriquecido.json'
    }
    
    modificados = 0
    for script in SCRIPTS_DIR.glob('*.py'):
        contenido = script.read_text(encoding='utf-8')
        nuevo = contenido
        for viejo, nuevo_nombre in reemplazos.items():
            nuevo = nuevo.replace(viejo, nuevo_nombre)
        
        if nuevo != contenido:
            script.write_text(nuevo, encoding='utf-8')
            print(f"✅ Actualizado: {script.name}")
            modificados += 1
            
    print(f"\nTotal scripts modificados: {modificados}")

if __name__ == '__main__':
    estandarizar()
