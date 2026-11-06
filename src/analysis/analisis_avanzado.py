import pandas as pd
import os
import re

def cargar_datos():
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
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True)

def analizar_accesorios(df):
    print("\n=== 1. IMPACTO DE LOS ACCESORIOS EN EL PRECIO ===")
    accesorios_buscar = ['alarma', 'gps', 'baul', 'baúl', 'casco']
    
    for accesorio in accesorios_buscar:
        # Buscar en la columna accesorios o en la descripción
        df['tiene_accesorio'] = df.apply(
            lambda row: accesorio in str(row.get('accesorios', '')).lower() or 
                        accesorio in str(row.get('descripcion', '')).lower(), 
            axis=1
        )
        
        con_accesorio = df[df['tiene_accesorio']]
        sin_accesorio = df[~df['tiene_accesorio']]
        
        if len(con_accesorio) > 5:
            p_med_con = con_accesorio['precio_usd'].median()
            p_med_sin = sin_accesorio['precio_usd'].median()
            diff = p_med_con - p_med_sin
            print(f"- '{accesorio.capitalize()}': {len(con_accesorio)} anuncios. Precio mediano: ${p_med_con:.0f} (Diferencia: {diff:+.0f} USD vs sin accesorio)")

def analizar_baterias(df):
    print("\n=== 2. BATERÍAS EN VEHÍCULOS ELÉCTRICOS ===")
    df_elec = df[df['tipo_vehiculo'].isin(['Eléctricas', 'Bicicletas', 'Patinetes'])].copy()
    
    def clasificar_bateria(bat):
        bat = str(bat).lower()
        if 'litio' in bat: return 'Litio'
        if 'gel' in bat or 'plomo' in bat: return 'Gel/Plomo'
        return 'No especificado'
        
    df_elec['tipo_bateria_limpio'] = df_elec['tipo_bateria'].apply(clasificar_bateria)
    
    resumen = df_elec.groupby('tipo_bateria_limpio').agg(
        cantidad=('id_anuncio', 'count'),
        precio_mediano=('precio_usd', 'median'),
        tiempo_carga_mediano=('tiempo_carga_horas', 'median')
    ).reset_index()
    
    for _, row in resumen.iterrows():
        if row['cantidad'] > 0:
            print(f"- {row['tipo_bateria_limpio']}: {row['cantidad']} anuncios | Precio Mediano: ${row['precio_mediano']:.0f} | Carga: {row['tiempo_carga_mediano']} horas")

def analizar_garantia(df):
    print("\n=== 3. GARANTÍA EN EL MERCADO INFORMAL ===")
    # Filtrar los que tienen garantía mayor a 0
    df_garantia = df[df['garantia_dias'] > 0].copy()
    
    print(f"Anuncios que ofrecen garantía explícita: {len(df_garantia)} de {len(df)}")
    
    if len(df_garantia) > 0:
        print(f"Garantía mediana ofrecida: {df_garantia['garantia_dias'].median():.0f} días")
        print("Top 5 marcas que más ofrecen garantía:")
        top_marcas = df_garantia.dropna(subset=['marca'])['marca'].value_counts().head(5)
        for marca, count in top_marcas.items():
            print(f"  - {marca}: {count} anuncios con garantía")

if __name__ == "__main__":
    df_total = cargar_datos()
    analizar_accesorios(df_total)
    analizar_baterias(df_total)
    analizar_garantia(df_total)
