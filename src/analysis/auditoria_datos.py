import pandas as pd
import os

def auditar():
    base = 'data/final/JSON/'
    archivos = ['motos_electricas_300_enriquecido.json', 'motos_combustion_300_enriquecido.json', 'bicis_300_enriquecido.json', 'patinetes_300_enriquecido.json']
    for arch in archivos:
        df = pd.read_json(os.path.join(base, arch))
        print(f"\n=== {arch} ===")
        print(f"Registros: {len(df)} | Columnas: {len(df.columns)}")
        if 'precio_usd' in df.columns:
            print(f"Mediana precio: {df['precio_usd'].median()}")

if __name__ == "__main__":
    auditar()
