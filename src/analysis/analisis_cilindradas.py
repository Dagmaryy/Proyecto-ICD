import pandas as pd
import os

def analizar_cilindradas():
    df = pd.read_json('data/processed/final/motos_combustion_300_enriquecido.json')
    df_clean = df.dropna(subset=['cilindrada_cc']).copy()
    
    # Redondear cilindradas para agrupar (por ejemplo, 124cc y 125cc se vuelven 125cc)
    df_clean['cilindrada_rango'] = (df_clean['cilindrada_cc'] / 25).round() * 25
    df_clean = df_clean[df_clean['cilindrada_rango'] > 0]
    
    conteo = df_clean['cilindrada_rango'].value_counts().sort_index()
    total = len(df_clean)
    
    print(f"=== DISTRIBUCIÓN DE CILINDRADAS (Motos de Combustión, N={total}) ===")
    for cilindrada, count in conteo.items():
        porcentaje = (count / total) * 100
        print(f"- {int(cilindrada)} cc: {count} anuncios ({porcentaje:.1f}%)")
        
    print("\nPrecio Mediano por Rango de Cilindrada:")
    precios = df_clean.groupby('cilindrada_rango')['precio_usd'].median()
    for cilindrada, precio in precios.items():
        print(f"- {int(cilindrada)} cc: ${precio:.0f} USD")

if __name__ == "__main__":
    analizar_cilindradas()
