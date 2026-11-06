import json

def normalizar():
    with open('data/processed/final/JSON/entrevistas_final.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for e in data['entrevistas']:
        # Normalizar preferencia
        pref = e['preferencia'].get('preferencia_vehiculo')
        if pref:
            if 'Eléctrica' in pref or 'eléctrica' in pref:
                e['preferencia']['preferencia_vehiculo'] = 'Eléctrica'
            elif 'Combustión' in pref or 'combustión' in pref:
                e['preferencia']['preferencia_vehiculo'] = 'Combustión'
                
        # Normalizar licencia
        lic = e['legal_seguridad'].get('tiene_licencia_chapa')
        if isinstance(lic, str):
            if 'no tiene' in lic.lower() or 'no' in lic.lower():
                e['legal_seguridad']['tiene_licencia_chapa'] = False
            elif 'tiene' in lic.lower():
                e['legal_seguridad']['tiene_licencia_chapa'] = True

    with open('data/processed/final/JSON/entrevistas_normalizadas.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("✅ Entrevistas normalizadas guardadas.")

if __name__ == "__main__":
    normalizar()
