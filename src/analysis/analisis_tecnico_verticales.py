import pandas as pd
import os

def analizar_verticales():
    base = 'data/processed/final/'
    
    # --- 1. ANÁLISIS DE ELÉCTRICOS (Motos, Bicis, Patinetes) ---
    electricos = {
        'Motos Eléctricas': 'motos_electricas_300_enriquecido.json',
        'Bicicletas': 'bicis_300_enriquecido.json',
        'Patinetes': 'patinetes_300_enriquecido.json'
    }
    
    print("=== TABLA 1: VEHÍCULOS ELÉCTRICOS (Costo por Vatio y Km) ===")
    print("| Categoría | Potencia (W) | Voltaje (V) | Autonomía (km) | Precio Mediano | Costo por Vatio | Costo por Km |")
    print("| :--- | :---: | :---: | :---: | :---: | :---: | :---: |")
    
    for tipo, arch in electricos.items():
        df = pd.read_json(os.path.join(base, arch))
        
        p_med = df['precio_usd'].median()
        w_med = df['motor_w'].median()
        v_med = df['voltaje_v'].median()
        km_med = df['autonomia_km'].median()
        
        costo_w = p_med / w_med if pd.notna(w_med) and w_med > 0 else 0
        costo_km = p_med / km_med if pd.notna(km_med) and km_med > 0 else 0
        
        print(f"| {tipo} | {w_med:.0f} W | {v_med:.0f} V | {km_med:.0f} km | ${p_med:.0f} | ${costo_w:.2f} | ${costo_km:.2f} |")

    # --- 2. ANÁLISIS DE COMBUSTIÓN ---
    print("\n=== TABLA 2: MOTOS DE COMBUSTIÓN (Cilindrada y Kilometraje) ===")
    df_comb = pd.read_json(os.path.join(base, 'motos_combustion_300_enriquecido.json'))
    
    print(f"Precio Mediano: ${df_comb['precio_usd'].median():.0f} USD")
    print(f"Cilindrada Mediana: {df_comb['cilindrada_cc'].median():.0f} cc")
    print(f"Año de Fabricación Mediano: {df_comb['anio_fabricacion'].median():.0f}")
    print(f"Kilometraje Mediano: {df_comb['kilometraje_km'].median():.0f} km")
    
    # Top 5 marcas de combustión
    print("\nTop 5 Marcas en Combustión:")
    top_marcas = df_comb.dropna(subset=['marca'])['marca'].value_counts().head(5)
    for marca, count in top_marcas.items():
        print(f"- {marca}: {count} anuncios")

if __name__ == "__main__":
    analizar_verticales()
