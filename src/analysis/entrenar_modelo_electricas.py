"""Entrena un Random Forest para predecir precio de motos electricas.

Reporta dos metricas: la que incluye duplicados (inflada) y la que
colapsa especificaciones repetidas (honesta).
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold, cross_val_predict

BASE = Path(__file__).resolve().parents[2]
RUTA = BASE / "data" / "final" / "JSON" / "motos_electricas_300_enriquecido.json"


def normalizar_marca(m):
    if not m:
        return "Sin marca"
    m = str(m).strip().lower()
    return m.capitalize()


def cargar_datos():
    datos = json.load(open(RUTA, encoding="utf-8"))
    filas = []
    for r in datos:
        vals = [r.get("precio_usd"), r.get("motor_w"),
                r.get("autonomia_km"), r.get("voltaje_v")]
        if not all(v not in (None, "") for v in vals):
            continue
        try:
            filas.append({
                "precio_usd": float(vals[0]),
                "motor_w": float(vals[1]),
                "autonomia_km": float(vals[2]),
                "voltaje_v": float(vals[3]),
                "marca": normalizar_marca(r.get("marca")),
            })
        except (ValueError, TypeError):
            continue
    return pd.DataFrame(filas)


def agrupar_marcas(df, minimo=5):
    conteo = df["marca"].value_counts()
    raras = conteo[conteo < minimo].index
    df = df.copy()
    df.loc[df["marca"].isin(raras), "marca"] = "Otras"
    return df


def colapsar_duplicados(df):
    """Agrupa por especificaciones y toma la mediana de precio."""
    grupo = df.groupby(
        ["motor_w", "autonomia_km", "voltaje_v"],
        as_index=False,
    ).agg(
        precio_usd=("precio_usd", "median"),
        marca=("marca", lambda s: s.mode().iloc[0] if not s.mode().empty else "Otras"),
    )
    return grupo


def evaluar(df, etiqueta):
    X = pd.get_dummies(df[["motor_w", "autonomia_km", "voltaje_v", "marca"]],
                       columns=["marca"], drop_first=False)
    y = df["precio_usd"].values
    modelo = RandomForestRegressor(
        n_estimators=200, max_depth=6, min_samples_leaf=3,
        random_state=42, n_jobs=-1,
    )
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    pred = cross_val_predict(modelo, X, y, cv=kf)
    r2 = r2_score(y, pred)
    rmse = np.sqrt(mean_squared_error(y, pred))
    mae = mean_absolute_error(y, pred)
    print(f"  {etiqueta}")
    print(f"    Registros: {len(df)}")
    print(f"    R2:   {r2:.3f}")
    print(f"    RMSE: {rmse:.0f} USD")
    print(f"    MAE:  {mae:.0f} USD")
    print(f"    Error relativo: {mae / np.median(y) * 100:.1f}%")
    modelo.fit(X, y)
    return modelo, X.columns.tolist()


def main():
    df = cargar_datos()
    print(f"Registros cargados: {len(df)}")
    df = agrupar_marcas(df)
    print(f"Marcas despues de agrupar: {df['marca'].nunique()}")

    print("\n=== Metricas con duplicados (infladas) ===")
    evaluar(df, "Dataset completo")

    df_unico = colapsar_duplicados(df)
    print(f"\nCombinaciones unicas de motor+autonomia+voltaje: {len(df_unico)}")

    print("\n=== Metricas sin duplicados (honestas) ===")
    modelo, features = evaluar(df_unico, "Dataset deduplicado")

    importancias = sorted(
        zip(features, modelo.feature_importances_),
        key=lambda x: x[1], reverse=True,
    )
    print("\n=== Importancia de variables (top 8) ===")
    for nombre, imp in importancias[:8]:
        print(f"  {nombre:25s} {imp:.3f}")


if __name__ == "__main__":
    main()
