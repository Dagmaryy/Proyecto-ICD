import pandas as pd
import os

def generar_mapa():
    base = 'data/processed/final/'
    archivos = ['motos_electricas_300.json', 'motos_combustion_300.json', 'bicis_300.json', 'patinetes_300.json']
    dfs = []
    for arch in archivos:
        dfs.append(pd.read_json(os.path.join(base, arch)))
    
    df_total = pd.concat(dfs, ignore_index=True)
    
    resumen = df_total.groupby('municipio').agg(
        total_anuncios=('id_anuncio', 'count'),
        precio_mediano=('precio_usd', 'median')
    ).reset_index()
    
    municipios_habana = [
        'Playa', 'Plaza de la Revolución', 'Centro Habana', 'La Habana Vieja', 'Regla',
        'La Habana del Este', 'Guanabacoa', 'San Miguel del Padrón', 'Diez de Octubre',
        'Cerro', 'Marianao', 'La Lisa', 'Boyeros', 'Arroyo Naranjo', 'Cotorro'
    ]
    
    resumen_completo = pd.DataFrame({'municipio': municipios_habana})
    resumen_final = pd.merge(resumen_completo, resumen, on='municipio', how='left').fillna(0)
    resumen_final['total_anuncios'] = resumen_final['total_anuncios'].astype(int)
    
    resumen_final.to_csv(os.path.join(base, 'datos_mapa_habana.csv'), index=False, encoding='utf-8-sig')
    print("✅ Datos del mapa generados.")

if __name__ == "__main__":
    generar_mapa()
