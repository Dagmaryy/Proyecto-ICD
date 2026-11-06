import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import scipy.stats as stats

def validar():
    df = pd.read_json('data/processed/final/JSON/motos_electricas_300.json')
    cols = ['precio_usd', 'motor_w', 'autonomia_km']
    df_clean = df.dropna(subset=cols).copy()
    X_scaled = StandardScaler().fit_transform(df_clean[cols])

    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X_scaled)

    sil_score = silhouette_score(X_scaled, clusters)
    print(f"Coeficiente de Silhouette: {sil_score:.3f}")

    grupo0 = df_clean[clusters == 0]['precio_usd']
    grupo1 = df_clean[clusters == 1]['precio_usd']
    grupo2 = df_clean[clusters == 2]['precio_usd']
    f_val, p_val = stats.f_oneway(grupo0, grupo1, grupo2)
    print(f"P-valor ANOVA (Precio): {p_val:.5f}")

if __name__ == "__main__":
    validar()
