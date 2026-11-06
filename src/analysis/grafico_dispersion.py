"""
Grafico de dispersion: precio vs autonomia en motos electricas.
Uso: source venv/bin/activate && python src/analysis/grafico_dispersion.py
"""
from pathlib import Path
import pandas as pd
import plotly.express as px

BASE = Path("data/processed/final")
OUT = Path("reports/plots")
OUT.mkdir(parents=True, exist_ok=True)

AZUL = "#1F4E79"
NARANJA = "#D97706"
FUENTE = "Inter, -apple-system, Segoe UI, Arial, sans-serif"


def _layout_base(fig, titulo, subtitulo, nota, altura=520):
    fig.update_layout(
        title=dict(
            text=f"<b>{titulo}</b><br>"
                 f"<span style='font-size:13px;color:#6B7280'>{subtitulo}</span>",
            font=dict(size=20, color="#1A1A1A", family=FUENTE),
            x=0.02, xanchor="left",
        ),
        font=dict(family=FUENTE, size=13, color="#333333"),
        plot_bgcolor="white",
        paper_bgcolor="white",
        height=altura,
        margin=dict(l=100, r=40, t=110, b=80),
        annotations=[
            dict(text=f"<i>{nota}</i>", xref="paper", yref="paper",
                 x=0, y=-0.18, showarrow=False,
                 font=dict(size=10, color="#6B7280"), align="left"),
        ],
    )
    return fig


df = pd.read_json(BASE / "JSON" / "motos_electricas_300_enriquecido.json")

# Detectar columnas
col_precio = next((c for c in ["precio_usd", "precio"] if c in df.columns), None)
col_aut = next((c for c in ["autonomia_km", "autonomia"] if c in df.columns), None)
col_pot = next((c for c in ["motor_w", "potencia_w", "potencia"] if c in df.columns), None)

if not col_precio or not col_aut:
    raise SystemExit(f"Faltan columnas: precio={col_precio}, autonomia={col_aut}")

df = df.rename(columns={col_precio: "precio", col_aut: "autonomia"})
if col_pot:
    df = df.rename(columns={col_pot: "potencia"})

df = df.dropna(subset=["precio", "autonomia"])
df = df[(df["precio"] >= 100) & (df["precio"] <= 5000)]
df = df[(df["autonomia"] > 0) & (df["autonomia"] <= 300)]

print(f"Dispersion sobre {len(df)} motos electricas con precio y autonomia")

if "potencia" in df.columns:
    fig = px.scatter(df, x="autonomia", y="precio",
                     size="potencia", color="precio",
                     color_continuous_scale=["#EFF6FF", AZUL],
                     hover_data={"potencia": True, "autonomia": True,
                                 "precio": True},
                     labels={"autonomia": "Autonomía (km)",
                             "precio": "Precio (USD)",
                             "potencia": "Potencia (W)"})
else:
    fig = px.scatter(df, x="autonomia", y="precio",
                     color_discrete_sequence=[AZUL],
                     labels={"autonomia": "Autonomía (km)",
                             "precio": "Precio (USD)"})

fig.update_traces(marker=dict(line=dict(width=1, color="white"),
                              opacity=0.8))

_layout_base(fig,
             "Precio vs autonomía en motos eléctricas",
             "Cada punto es un anuncio. El tamaño refleja la potencia del motor.",
             f"Fuente: {len(df)} motos eléctricas con precio y autonomía declarados. "
             "Filtro: precio $100–$5,000, autonomía 1–300 km.",
             altura=560)
fig.update_xaxes(showgrid=True, gridcolor="#F3F4F6")
fig.update_yaxes(showgrid=True, gridcolor="#F3F4F6")
fig.update_layout(coloraxis_showscale=False)

fig.write_html(OUT / "12_dispersion.html",
               include_plotlyjs="cdn",
               config={"displayModeBar": False, "responsive": True})
try:
    fig.write_image(OUT / "12_dispersion.png", scale=2)
except Exception:
    pass
print("OK 12_dispersion")
