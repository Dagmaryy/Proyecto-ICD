import pandas as pd
import os

def generar_top_global():
    base = 'data/processed/final/'
    archivos = {
        'Eléctricas': 'motos_electricas_300_enriquecido.json',
        'Combustión': 'motos_combustion_300_enriquecido.json',
        'Bicicletas': 'bicis_300_enriquecido.json',
        'Patinetes': 'patinetes_300_enriquecido.json'
    }
    dfs = []
    for tipo, arch in archivos.items():
        df = pd.read_json(os.path.join(base, arch))
        df['tipo_vehiculo'] = tipo
        dfs.append(df[['marca', 'tipo_vehiculo']])

    df_total = pd.concat(dfs, ignore_index=True)
    marcas_globales = df_total.dropna(subset=['marca']).groupby('marca').size().reset_index(name='total_anuncios')
    top_global = marcas_globales.sort_values(by='total_anuncios', ascending=False).head(15)
    
    dir_csv = os.path.join(base, 'csv_graficos/')
    top_global.to_csv(os.path.join(dir_csv, '8_top_marcas_global.csv'), index=False, encoding='utf-8-sig')
    print("✅ CSV del Top 15 global guardado.")

if __name__ == "__main__":
    generar_top_global()
