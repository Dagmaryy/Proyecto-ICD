import pandas as pd
import os

def generar_csvs():
    base = 'data/processed/final/JSON/'
    dir_csv = os.path.join(base, 'CSV/')
    os.makedirs(dir_csv, exist_ok=True)

    dfs = []
    for arch, tipo in [('motos_electricas_300.json', 'Eléctricas'), 
                       ('motos_combustion_300.json', 'Combustión'), 
                       ('bicis_300.json', 'Bicis'), 
                       ('patinetes_300.json', 'Patinetes')]:
        df = pd.read_json(os.path.join(base, arch))
        df['tipo_vehiculo'] = tipo
        dfs.append(df[['tipo_vehiculo', 'municipio', 'precio_usd', 'transporte_incluido']])
    
    df_total = pd.concat(dfs, ignore_index=True)

    # 1. Precios por tipo
    g_precio = df_total.groupby('tipo_vehiculo')['precio_usd'].agg(['median', 'mean', 'count']).reset_index()
    g_precio.columns = ['tipo_vehiculo', 'precio_mediano', 'precio_promedio', 'cantidad_anuncios']
    g_precio.to_csv(os.path.join(dir_csv, '1_barras_precio_tipo.csv'), index=False, encoding='utf-8-sig')

    # 2. Mapa municipios
    g_muni = df_total.groupby('municipio')['precio_usd'].agg(['median', 'count']).reset_index()
    g_muni.columns = ['municipio', 'precio_mediano', 'cantidad_anuncios']
    g_muni.to_csv(os.path.join(dir_csv, '2_mapa_municipios.csv'), index=False, encoding='utf-8-sig')

    print("✅ CSVs generados en data/processed/final/CSV/")

if __name__ == "__main__":
    generar_csvs()
