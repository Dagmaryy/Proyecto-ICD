import pandas as pd
import os

def auditar():
    base = 'data/processed/final/'
    archivos = ['motos_electricas_300.json', 'motos_combustion_300.json', 'bicis_300.json', 'patinetes_300.json']
    for arch in archivos:
        df = pd.read_json(os.path.join(base, arch))
        print(f"\n=== {arch} ===")
        print(f"Registros: {len(df)} | Columnas: {len(df.columns)}")
        if 'precio_usd' in df.columns:
            print(f"Mediana precio: {df['precio_usd'].median()}")

if __name__ == "__main__":
    auditar()
