import json
import pandas as pd
import os

def generar_estadisticas_entrevistas():
    ruta_json = 'data/processed/final/entrevistas_final.json'
    
    if not os.path.exists(ruta_json):
        print(f"❌ Error: No se encontró {ruta_json}")
        return

    with open(ruta_json, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Aplanar los datos para convertirlos en una tabla fácil de analizar
    registros = []
    for e in data['entrevistas']:
        flat = {
            'id': e.get('id_entrevista'),
            'edad': e.get('perfil', {}).get('edad'),
            'ocupacion': e.get('perfil', {}).get('ocupacion'),
            'municipio': e.get('perfil', {}).get('municipio'),
            'uso_principal': e.get('uso', {}).get('uso_principal'),
            'uso_comercial': e.get('uso', {}).get('uso_comercial'),
            'tipo_vehiculo': e.get('eleccion', {}).get('tipo_vehiculo'),
            'precio': e.get('compra', {}).get('precio_total'),
            'moneda': e.get('compra', {}).get('moneda'),
            'problemas_apagones': e.get('operacion', {}).get('problemas_apagones'),
            'ha_bajado_autonomia': e.get('rendimiento', {}).get('ha_bajado_autonomia'),
            'preferencia': e.get('preferencia', {}).get('preferencia_vehiculo'),
            'tiene_licencia': e.get('legal_seguridad', {}).get('tiene_licencia_chapa')
        }
        registros.append(flat)

    df = pd.DataFrame(registros)

    print("=== 1. PERFIL (P11) ===")
    edades_validas = pd.to_numeric(df['edad'], errors='coerce').dropna()
    print(f"Edad promedio: {edades_validas.mean():.1f} años (Min: {edades_validas.min()}, Max: {edades_validas.max()})")
    print("\nTop 3 Municipios:")
    print(df['municipio'].value_counts().head(3).to_string())

    print("\n=== 2. USO (P12) ===")
    print(f"Uso comercial (mensajería/trabajo): {df['uso_comercial'].sum()} de {len(df)}")

    print("\n=== 3. PRECIO PAGADO (P15) ===")
    precios = pd.to_numeric(df['precio'], errors='coerce').dropna()
    print(f"Precio mediano: ${precios.median():.0f} USD | Precio promedio: ${precios.mean():.0f} USD")
    print("Monedas utilizadas:")
    print(df['moneda'].value_counts().to_string())

    print("\n=== 4. APAGONES Y AUTONOMÍA (P16, P17) ===")
    print(f"Han tenido problemas con apagones: {df['problemas_apagones'].sum()} de {len(df)}")
    print(f"Reportan caída de autonomía con el tiempo: {df['ha_bajado_autonomia'].sum()} de {len(df)}")

    print("\n=== 5. PREFERENCIA FINAL (P20) ===")
    print(df['preferencia'].value_counts().to_string())

    print("\n=== 6. LEGALIDAD (P11) ===")
    print(df['tiene_licencia'].value_counts().to_string())

if __name__ == "__main__":
    generar_estadisticas_entrevistas()
