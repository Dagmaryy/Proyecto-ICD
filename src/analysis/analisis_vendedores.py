import pandas as pd
import os
import numpy as np

def analizar_vendedores():
    base = 'data/processed/final/'
    archivos = ['motos_electricas_300.json', 'motos_combustion_300.json', 'bicis_300.json', 'patinetes_300.json']
    
    dfs = []
    for arch in archivos:
        df = pd.read_json(os.path.join(base, arch))
        dfs.append(df[['vendedor_id', 'precio_usd']])
        
    df_total = pd.concat(dfs, ignore_index=True).dropna(subset=['vendedor_id'])
    
    # Contar anuncios por vendedor
    conteo = df_total['vendedor_id'].value_counts().reset_index()
    conteo.columns = ['vendedor_id', 'cantidad_anuncios']
    
    total_anuncios = conteo['cantidad_anuncios'].sum()
    total_vendedores = len(conteo)
    
    # 1. Principio de Pareto (¿Cuántos vendedores tienen el 80% de los anuncios?)
    conteo = conteo.sort_values(by='cantidad_anuncios', ascending=False)
    conteo['acumulado'] = conteo['cantidad_anuncios'].cumsum()
    conteo['porcentaje_acumulado'] = conteo['acumulado'] / total_anuncios
    vendedores_80 = len(conteo[conteo['porcentaje_acumulado'] <= 0.80]) + 1
    porcentaje_vendedores_80 = (vendedores_80 / total_vendedores) * 100
    
    # 2. Índice de Gini
    x = np.sort(conteo['cantidad_anuncios'].values)
    n = len(x)
    gini = (2 * np.sum((np.arange(1, n+1) * x)) / (n * np.sum(x))) - ((n + 1) / n)
    
    print("=== ANÁLISIS DE VENDEDORES ===")
    print(f"Total de anuncios analizados: {total_anuncios}")
    print(f"Total de vendedores únicos: {total_vendedores}")
    print(f"\nEl {porcentaje_vendedores_80:.1f}% de los vendedores ({vendedores_80} personas) concentran el 80% de los anuncios.")
    print(f"Índice de Gini: {gini:.3f} (0 = todos venden igual, 1 = un solo vendedor acapara todo)")
    
    print("\nTop 10 Vendedores (por cantidad de anuncios):")
    top10 = conteo.head(10)
    for _, row in top10.iterrows():
        print(f"- ID {row['vendedor_id']}: {row['cantidad_anuncios']} anuncios")

if __name__ == "__main__":
    analizar_vendedores()
