import pandas as pd
import os

def generar_datos_apilados():
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

    df_total = pd.concat(dfs, ignore_index=True).dropna(subset=['marca'])
    
    # Crosstab (Matriz de marcas por categoría)
    tabla = pd.crosstab(df_total['marca'], df_total['tipo_vehiculo'])
    tabla['Total'] = tabla.sum(axis=1)
    tabla = tabla.sort_values(by='Total', ascending=False).head(15).reset_index()

    ruta_salida = os.path.join(base, 'CSV/11_marcas_apiladas.csv')
    tabla.to_csv(ruta_salida, index=False, encoding='utf-8-sig')
    print("✅ CSV para el gráfico de barras apiladas guardado.")

if __name__ == "__main__":
    generar_datos_apilados()
