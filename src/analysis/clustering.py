import pandas as pd
import json
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def run_clustering():
    ruta = 'data/processed/final/motos_electricas_300.json'
    df = pd.read_json(ruta)
    cols = ['precio_usd', 'motor_w', 'autonomia_km']
    df_clean = df.dropna(subset=cols).copy()

    print(f"Analizando {len(df_clean)} motos eléctricas...")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df_clean[cols])

    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    df_clean['cluster'] = kmeans.fit_predict(X_scaled)

    centros_reales = scaler.inverse_transform(kmeans.cluster_centers_)
    centros_df = pd.DataFrame(centros_reales, columns=cols)
    orden_clusters = centros_df['precio_usd'].sort_values().index.tolist()
    etiquetas = {orden_clusters[0]: 'Gama Económica', orden_clusters[1]: 'Gama Media', orden_clusters[2]: 'Gama Alta'}

    reporte = []
    for i in orden_clusters:
        subset = df_clean[df_clean['cluster'] == i]
        reporte.append({
            "segmento": etiquetas[i],
            "cantidad_anuncios": len(subset),
            "precio_promedio_usd": round(subset['precio_usd'].mean(), 2),
            "potencia_promedio_w": round(subset['motor_w'].mean(), 2),
            "autonomia_promedio_km": round(subset['autonomia_km'].mean(), 2)
        })

    with open('data/processed/final/clustering_motos.json', 'w', encoding='utf-8') as f:
        json.dump(reporte, f, indent=2, ensure_ascii=False)
    
    print("✅ Clustering guardado en data/processed/final/clustering_motos.json")

if __name__ == "__main__":
    run_clustering()
