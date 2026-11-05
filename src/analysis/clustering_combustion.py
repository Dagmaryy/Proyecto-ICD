import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

def clustering_combustion():
    df = pd.read_json('data/processed/final/motos_combustion_300_enriquecido.json')
    cols = ['precio_usd', 'cilindrada_cc']
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
        
    print(f"\nSilhouette Score: {silhouette_score(X_scaled, df_clean['cluster']):.3f}")

if __name__ == "__main__":
    clustering_combustion()
