"""
Tabulación completa de las 30 entrevistas para el informe ICD.
Genera CSVs en data/processed/final/CSV/ y reporta por consola.

Uso:
    source venv/bin/activate && python src/analysis/tabulacion_entrevistas.py

Entrada: data/processed/final/JSON/entrevistas_final_corregido.json
Salida: CSVs en data/processed/final/CSV/entrevistas_*.csv
"""
import json
from collections import Counter
from pathlib import Path
import pandas as pd

RUTA_JSON = Path("data/processed/final/JSON/entrevistas_final_corregido.json")
SALIDA = Path("data/processed/final/CSV")
SALIDA.mkdir(parents=True, exist_ok=True)

with open(RUTA_JSON, encoding="utf-8") as f:
    data = json.load(f)
entrevistas = data["entrevistas"]
N = len(entrevistas)
print(f"Total entrevistas: {N}\n")


def _limpiar(v):
    """Devuelve None si el valor está vacío."""
    if v in (None, "", [], {}):
        return None
    return str(v).strip()


def _tab(campo_bloque, campo, titulo, guardar_como=None, agrupador=None):
    """Tabulación genérica de un campo."""
    valores = []
    for e in entrevistas:
        v = _limpiar(e.get(campo_bloque, {}).get(campo))
        if v:
            valores.append(agrupador(v) if agrupador else v)
    conteo = Counter(valores)
    print(f"=== {titulo} ({sum(conteo.values())}/{N}) ===")
    for val, n in conteo.most_common():
        print(f"  {n:2d}  {val[:100]}")
    print()
    if guardar_como:
        df = pd.DataFrame(
            conteo.most_common(), columns=["categoria", "cantidad"]
        )
        df.to_csv(SALIDA / f"entrevistas_{guardar_como}.csv", index=False)
    return conteo


# ---------- 1. PERFIL ----------
edades = [
    e["perfil"]["edad"]
    for e in entrevistas
    if _limpiar(e.get("perfil", {}).get("edad"))
]
if edades:
    edades = [float(x) for x in edades]
    print(f"=== PERFIL: edad ===")
    print(f"  N={len(edades)}  Media={sum(edades)/len(edades):.1f}  "
          f"Min={min(edades)}  Max={max(edades)}\n")

_tab("perfil", "municipio", "PERFIL: municipio",
     guardar_como="municipio")

# ---------- 2. USO ----------
_tab("uso", "uso_comercial", "USO: comercial",
     guardar_como="uso_comercial")

# ---------- 3. PRECIO PAGADO ----------
precios = [
    float(e["compra"]["precio_total"])
    for e in entrevistas
    if _limpiar(e.get("compra", {}).get("precio_total"))
]
if precios:
    precios_sorted = sorted(precios)
    mediana = precios_sorted[len(precios_sorted) // 2]
    print(f"=== PRECIO PAGADO ===")
    print(f"  N={len(precios)}  Mediana=${mediana:.0f}  "
          f"Media=${sum(precios)/len(precios):.0f}\n")

_tab("compra", "moneda", "MONEDA", guardar_como="moneda")

# ---------- 4. APAGONES Y AUTONOMÍA ----------
_tab("operacion", "problemas_apagones",
     "APAGONES: ¿ha tenido problemas?",
     guardar_como="apagones")

_tab("rendimiento", "ha_bajado_autonomia",
     "AUTONOMÍA: ¿ha bajado?",
     guardar_como="autonomia_bajada")

# ---------- 5. PREFERENCIA ----------
def _agrupar_preferencia(v):
    v_low = v.lower()
    if "eléctric" in v_low or "electric" in v_low:
        return "Eléctrica"
    if "combusti" in v_low or "gasolina" in v_low:
        return "Combustión"
    return "No especificado"

_tab("preferencia", "preferencia_vehiculo",
     "PREFERENCIA: ¿eléctrica o combustión?",
     guardar_como="preferencia",
     agrupador=_agrupar_preferencia)

# ---------- 6. LEGALIDAD ----------
def _agrupar_licencia(v):
    v_low = v.lower()
    if v_low in ("true", "sí", "si"):
        return "Con licencia"
    if v_low in ("false", "no"):
        return "Sin licencia"
    if "bicimoto" in v_low:
        return "Bicimoto (sin requisito)"
    if "trámite" in v_low or "proceso" in v_low:
        return "Licencia en trámite"
    if "permiso" in v_low:
        return "Con permiso, sin licencia"
    if "no tiene licencia" in v_low:
        return "Sin licencia"
    if "tiene licencia" in v_low:
        return "Con licencia"
    return "Mixto / otro"

_tab("legal_seguridad", "tiene_licencia_chapa",
     "LEGALIDAD: licencia/chapa",
     guardar_como="legalidad",
     agrupador=_agrupar_licencia)

# ---------- 7. FACTOR PRINCIPAL DE COMPRA ----------
def _agrupar_factor(v):
    v_low = v.lower()
    factores = []
    if "precio" in v_low or "econ" in v_low:
        factores.append("Precio")
    if "autonom" in v_low:
        factores.append("Autonomía")
    if "motor" in v_low or "potencia" in v_low:
        factores.append("Motor/Potencia")
    if "marca" in v_low or "confi" in v_low:
        factores.append("Marca/Confiabilidad")
    if "gusto" in v_low or "pasi" in v_low:
        factores.append("Gusto/Pasión")
    if "disponibilidad" in v_low:
        factores.append("Disponibilidad")
    return " + ".join(factores) if factores else "Otro"

_tab("eleccion", "factor_principal",
     "FACTOR PRINCIPAL DE COMPRA",
     guardar_como="factor_principal",
     agrupador=_agrupar_factor)

# ---------- 8. FALLOS TÉCNICOS ----------
def _agrupar_fallos(v):
    v_low = v.lower()
    if "ninguno" in v_low and "grave" not in v_low:
        return "Sin fallos"
    if "batería" in v_low or "bateria" in v_low or "celda" in v_low:
        return "Batería"
    if "controlador" in v_low or "regulador" in v_low or "pantalla" in v_low \
            or "acelerador" in v_low or "eléctric" in v_low:
        return "Sistema eléctrico / controlador"
    if "freno" in v_low or "bujía" in v_low or "pinchazo" in v_low \
            or "mecánic" in v_low or "reposapiés" in v_low:
        return "Mecánico menor"
    return "Otro / genérico"

_tab("rendimiento", "fallos_tecnicos",
     "FALLOS TÉCNICOS",
     guardar_como="fallos_tecnicos",
     agrupador=_agrupar_fallos)

# ---------- 9. FRECUENCIA DE CARGA ----------
def _agrupar_frecuencia(v):
    v_low = v.lower()
    if "diaria" in v_low or "diario" in v_low or "todos los días" in v_low:
        return "Diaria"
    if "3 o 4" in v_low or "2 o 3" in v_low or "3-4" in v_low \
            or "2-3" in v_low:
        return "Cada 2-4 días"
    if "semana" in v_low:
        return "Semanal o menos"
    if "rayita" in v_low or "raya" in v_low or "carga" in v_low \
            or "necesidad" in v_low or "regular" in v_low:
        return "Según nivel de carga"
    return "Otro"

_tab("operacion", "frecuencia_carga",
     "FRECUENCIA DE CARGA",
     guardar_como="frecuencia_carga",
     agrupador=_agrupar_frecuencia)

# ---------- 10. RAZÓN DEL CANAL ----------
def _agrupar_razon(v):
    v_low = v.lower()
    if "barat" in v_low or "precio" in v_low or "econ" in v_low:
        return "Precio más bajo"
    if "confianza" in v_low or "confiable" in v_low \
            or "recomend" in v_low or "seguridad" in v_low:
        return "Confianza / recomendación"
    if "familiar" in v_low or "conocid" in v_low:
        return "Familiares / conocidos"
    if "disponib" in v_low or "encontr" in v_low or "en Cuba no" in v_low \
            or "donde vendían" in v_low:
        return "Disponibilidad / exclusividad"
    if "envío" in v_low or "envio" in v_low:
        return "Costo de envío"
    return "Otro"

_tab("compra", "razon_canal",
     "RAZÓN DEL CANAL DE COMPRA",
     guardar_como="razon_canal",
     agrupador=_agrupar_razon)

print(f"CSVs guardados en: {SALIDA}/")
print("Prefijo: entrevistas_*.csv")
