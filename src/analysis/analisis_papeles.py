import pandas as pd
import os

def analizar_papeles():
    base = 'data/processed/final/'
    archivos = {
        'Eléctricas': 'motos_electricas_300_enriquecido.json',
        'Combustión': 'motos_combustion_300_enriquecido.json',
        'Bicis': 'bicis_300_enriquecido.json',
        'Patinetes': 'patinetes_300_enriquecido.json'
    }
    for tipo, arch in archivos.items():
        df = pd.read_json(os.path.join(base, arch))
        nulos = df['papeles'].isna().sum()
        porcentaje = (nulos / len(df)) * 100
        print(f"{tipo}: {nulos} nulos ({porcentaje:.1f}%)")

if __name__ == "__main__":
    analizar_papeles()
