import pandas as pd
import os
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

def clustering_combustion():
    print("=== CLUSTERING: MOTOS DE COMBUSTIÓN ===")
    df = pd.read_json('data/processed/final/motos_combustion_300_enriquecido.json')
    cols = ['precio_usd', 'cilindrada_cc', 'kilometraje_km']
    df_clean = df.dropna(subset=cols).copy()
    
    X_scaled = StandardScaler().fit_transform(df_clean[cols])
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    df_clean['cluster'] = kmeans.fit_predict(X_scaled)
    
    centros = StandardScaler().fit(df_clean[cols])
    centros_reales = centros.inverse_transform(kmeans.cluster_centers_)
    orden = centros_reales[:, 0].argsort()
    etiquetas = ['Gama Baja', 'Gama Media', 'Gama Alta']
    
    for i, idx in enumerate(orden):
        subset = df_clean[df_clean['cluster'] == idx]
        print(f"\n{etiquetas[i]} ({len(subset)} anuncios):")
        print(f"  Precio Promedio: ${subset['precio_usd'].mean():.0f} USD")
        print(f"  Cilindrada Promedio: {subset['cilindrada_cc'].mean():.0f} cc")
        print(f"  Kilometraje Promedio: {subset['kilometraje_km'].mean():.0f} km")
        
    sil = silhouette_score(X_scaled, df_clean['cluster'])
    print(f"\nSilhouette Score (Combustión): {sil:.3f}")

def clustering_global():
    print("\n\n=== CLUSTERING GLOBAL: TODAS LAS VERTICALES (POR PRECIO) ===")
    base = 'data/processed/final/'
    archivos = {
        'Eléctricas': 'motos_electricas_300.json', 
        'Combustión': 'motos_combustion_300.json', 
        'Bicicletas': 'bicis_300.json', 
        'Patinetes': 'patinetes_300.json'
    }
    
    dfs = []
    for tipo, arch in archivos.items():
        df = pd.read_json(os.path.join(base, arch))
        df['tipo'] = tipo
        dfs.append(df[['precio_usd', 'tipo']])
        
    df_total = pd.concat(dfs, ignore_index=True).dropna(subset=['precio_usd'])
    
    X = df_total[['precio_usd']]
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    df_total['cluster'] = kmeans.fit_predict(X)
    
    medias = df_total.groupby('cluster')['precio_usd'].mean().sort_values()
    etiquetas = ['Gama Baja', 'Gama Media', 'Gama Alta']
    
    for i, (cluster_id, media) in enumerate(medias.items()):
        subset = df_total[df_total['cluster'] == cluster_id]
        count = len(subset)
        print(f"\n{etiquetas[i]} ({count} anuncios):")
        print(f"  Precio Promedio: ${media:.0f} USD")
        
        # Mostrar la composición exacta de este clúster
        print("  Composición:")
        composicion = subset['tipo'].value_counts()
        for t, c in composicion.items():
            print(f"    - {t}: {c}")

if __name__ == "__main__":
    clustering_combustion()
    clustering_global()
