"""
Genera los graficos del informe ICD en HTML interactivo + PNG.
Uso: source venv/bin/activate && python src/analysis/graficos_finales.py
Salida: reports/plots/*.html y *.png
"""
import json
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

BASE = Path("data/processed/final")
CSV = BASE / "CSV"
JSON_DIR = BASE / "JSON"
OUT = Path("reports/plots")
OUT.mkdir(parents=True, exist_ok=True)

# Paleta sobria (Azules y grises)
AZUL = "#1F4E79"
AZUL_MEDIO = "#4A7C9D"
GRIS_OSCURO = "#6B7280"
GRIS_CLARO = "#D1D5DB"
COLORES = [AZUL, AZUL_MEDIO, GRIS_OSCURO, GRIS_CLARO]

FUENTE = "Inter, -apple-system, Segoe UI, Arial, sans-serif"

def _layout_base(fig, titulo, subtitulo, nota, altura=480):
    fig.update_layout(
        title=dict(
            text=f"<b>{titulo}</b><br>"
                 f"<span style='font-size:13px;color:#6B7280'>{subtitulo}</span>",
            font=dict(size=20, color="#1A1A1A", family=FUENTE),
            x=0.02, xanchor="left",
        ),
        font=dict(family=FUENTE, size=13, color="#333333"),
        colorway=COLORES,
        plot_bgcolor="white",
        paper_bgcolor="white",
        height=altura,
        margin=dict(l=120, r=40, t=110, b=80),
        annotations=[
            dict(text=f"<i>{nota}</i>", xref="paper", yref="paper",
                 x=0, y=-0.18, showarrow=False,
                 font=dict(size=10, color="#6B7280"), align="left"),
        ],
    )
    return fig

def guardar(fig, nombre):
    fig.write_html(OUT / f"{nombre}.html",
                   include_plotlyjs="cdn",
                   config={"displayModeBar": False, "responsive": True})
    try:
        fig.write_image(OUT / f"{nombre}.png", scale=2)
    except Exception:
        pass
    print(f"OK {nombre}")

# ---------------------------------------------------------------
# 1. Precio mediano por tipo
# ---------------------------------------------------------------
df = pd.read_csv(CSV / "1_barras_precio_tipo.csv").sort_values("precio_mediano")
fig = px.bar(df, x="precio_mediano", y="tipo_vehiculo", orientation="h",
             text="precio_mediano", color_discrete_sequence=[AZUL])
fig.update_traces(texttemplate="<b>$%{text:,.0f}</b>", textposition="outside", marker_line_width=0)
_layout_base(fig, "Precio mediano por tipo de vehículo", "Precios pedidos en Revolico. La Habana, 2026.", "Fuente: 1,200 anuncios de Revolico. n=300 por categoría.", 440)
fig.update_xaxes(title="Precio mediano (USD)", showgrid=True, gridcolor="#F3F4F6", zeroline=False)
fig.update_yaxes(title="", showgrid=False)
guardar(fig, "01_precio_tipo")

# ---------------------------------------------------------------
# 2. Top marcas por tipo (apilado)
# ---------------------------------------------------------------
df = pd.read_csv(CSV / "9_top_marcas_por_categoria.csv")
top = df.groupby("marca")["cantidad"].sum().nlargest(10).index
df = df[df["marca"].isin(top)]
pivot = df.pivot_table(index="marca", columns="tipo_vehiculo", values="cantidad", aggfunc="sum").fillna(0)
pivot["__t"] = pivot.sum(axis=1)
pivot = pivot.sort_values("__t", ascending=True).drop(columns="__t")
fig = go.Figure()
for i, col in enumerate(pivot.columns):
    fig.add_trace(go.Bar(y=pivot.index, x=pivot[col], name=col, orientation="h", marker_color=COLORES[i % len(COLORES)], marker_line_width=0))
_layout_base(fig, "Top 10 marcas por tipo de vehículo", "Cantidad de anuncios. Una barra por marca, segmentos por tipo.", "Fuente: 1,200 anuncios de Revolico. Marcas ordenadas por volumen total.", 520)
fig.update_layout(barmode="stack", legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, xanchor="left"))
fig.update_xaxes(title="Cantidad de anuncios", showgrid=True, gridcolor="#F3F4F6", zeroline=False)
fig.update_yaxes(title="", showgrid=False)
guardar(fig, "02_marcas_tipo")

# ---------------------------------------------------------------
# 3. Mapa
# ---------------------------------------------------------------
df = pd.read_csv(CSV / "datos_mapa_habana.csv")
df["municipio"] = df["municipio"].replace({"La Habana del Este": "Habana del Este"})
with open(CSV / "lha.geojson", encoding="utf-8") as f:
    gj = json.load(f)
fig = px.choropleth(df, geojson=gj, locations="municipio", featureidkey="properties.municipality", color="total_anuncios", hover_data={"precio_mediano": ":,.0f", "total_anuncios": True, "municipio": False}, color_continuous_scale=[GRIS_CLARO, AZUL], labels={"total_anuncios": "Anuncios", "precio_mediano": "Precio mediano (USD)"})
fig.update_geos(fitbounds="locations", visible=False, bgcolor="white", projection_type="mercator")
_layout_base(fig, "Cantidad de anuncios por municipio", "Color más intenso = mayor cantidad de anuncios.", "Fuente: 1,200 anuncios de Revolico. GeoJSON: DPA Cuba 2024.", 680)
fig.update_layout(margin=dict(l=20, r=20, t=110, b=60), coloraxis_colorbar=dict(title="Anuncios", thickness=12, len=0.6, yanchor="middle", y=0.5))
guardar(fig, "03_mapa")

# ---------------------------------------------------------------
# 4. Costo por vatio vs costo por km
# ---------------------------------------------------------------
df = pd.DataFrame({"categoria": ["Motos eléctricas", "Bicicletas", "Patinetes"], "Costo por vatio ($/W)": [0.83, 0.80, 1.19], "Costo por km ($/km)": [20.83, 10.91, 12.40]})
fig = go.Figure()
fig.add_trace(go.Bar(x=df["categoria"], y=df["Costo por vatio ($/W)"], name="Costo por vatio ($/W)", marker_color=AZUL, marker_line_width=0, text=df["Costo por vatio ($/W)"], texttemplate="$%{text:.2f}", textposition="outside"))
fig.add_trace(go.Bar(x=df["categoria"], y=df["Costo por km ($/km)"], name="Costo por km ($/km)", marker_color=AZUL_MEDIO, marker_line_width=0, yaxis="y2", text=df["Costo por km ($/km)"], texttemplate="$%{text:.2f}", textposition="outside"))
_layout_base(fig, "Costo por vatio vs costo por kilómetro", "Dos métricas de eficiencia que apuntan en direcciones opuestas.", "Fuente: medianas de precio, potencia y autonomía por categoría.", 480)
fig.update_layout(barmode="group", yaxis=dict(title="Costo por vatio ($/W)", showgrid=True, gridcolor="#F3F4F6"), yaxis2=dict(title="Costo por km ($/km)", overlaying="y", side="right", showgrid=False), legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, xanchor="left"), xaxis=dict(title=""))
guardar(fig, "04_costo_valor")

# ---------------------------------------------------------------
# 5. Cilindradas
# ---------------------------------------------------------------
df = pd.DataFrame({"cc": ["125 cc", "150 cc", "200 cc", "250 cc", "175 cc", "50 cc"], "cantidad": [109, 63, 60, 28, 10, 2]})
fig = px.bar(df, x="cc", y="cantidad", text="cantidad", color_discrete_sequence=[AZUL])
fig.update_traces(textposition="outside", texttemplate="<b>%{text}</b>", marker_line_width=0)
_layout_base(fig, "Distribución de cilindradas", "El mercado se concentra en motores de 125 cc y 150 cc.", "Fuente: 272 anuncios de motos de combustión.", 440)
fig.update_xaxes(title="", showgrid=False)
fig.update_yaxes(title="Anuncios", showgrid=True, gridcolor="#F3F4F6")
fig.update_layout(showlegend=False)
guardar(fig, "05_cilindradas")

# ---------------------------------------------------------------
# 6. Bateria
# ---------------------------------------------------------------
df = pd.DataFrame({"tipo": ["Litio", "Gel/Plomo"], "cantidad": [323, 109]})
fig = px.pie(df, values="cantidad", names="tipo", hole=0.58, color_discrete_sequence=[AZUL, GRIS_CLARO])
fig.update_traces(textinfo="value+percent", textfont=dict(size=14), marker=dict(line=dict(color="white", width=2)))
_layout_base(fig, "Tecnología de batería", "El litio se consolidó como estándar sin sobreprecio significativo.", "Fuente: 432 anuncios que declaran tipo de batería.", 440)
fig.update_layout(margin=dict(l=40, r=40, t=110, b=80))
guardar(fig, "06_bateria")

# ---------------------------------------------------------------
# 7. Clustering
# ---------------------------------------------------------------
df = pd.DataFrame({"gama": ["Gama baja<br>(micromovilidad)", "Gama media", "Gama alta"], "precio": [650, 1841, 2711]})
fig = px.bar(df, x="gama", y="precio", text="precio", color_discrete_sequence=[AZUL])
fig.update_traces(texttemplate="<b>$%{text:,.0f}</b>", textposition="outside", marker_line_width=0)
_layout_base(fig, "Estratificación del mercado", "El clustering agrupa los 1,200 anuncios por poder adquisitivo.", "Fuente: K-Means sobre precio (n=1,200).", 460)
fig.update_xaxes(title="", showgrid=False)
fig.update_yaxes(title="Precio promedio (USD)", showgrid=True, gridcolor="#F3F4F6")
fig.update_layout(showlegend=False)
guardar(fig, "07_clustering")

# ---------------------------------------------------------------
# 8. Formal vs informal
# ---------------------------------------------------------------
df = pd.DataFrame({"canal": ["Formal (VEDCA)", "Informal (Revolico)"], "precio": [1300, 2420]})
fig = px.bar(df, x="canal", y="precio", text="precio", color="canal", color_discrete_map={"Formal (VEDCA)": AZUL, "Informal (Revolico)": GRIS_OSCURO})
fig.update_traces(texttemplate="<b>$%{text:,.0f}</b>", textposition="outside", marker_line_width=0)
_layout_base(fig, "Sobreprecio del mercado informal (VEDCA)", "Precio mediano de la marca VEDCA en cada canal.", "Fuente: VEDCA y 43 anuncios de VEDCA en Revolico.", 460)
fig.update_xaxes(title="", showgrid=False)
fig.update_yaxes(title="Precio mediano (USD)", showgrid=True, gridcolor="#F3F4F6")
fig.update_layout(showlegend=False)
guardar(fig, "08_formal_informal")

# ---------------------------------------------------------------
# 9. Papeles
# ---------------------------------------------------------------
df = pd.read_csv(CSV / "6_dona_papeles.csv")
no_m = df[df["papeles"] == "No especificado"]["cantidad"].sum()
si_m = df[df["papeles"] != "No especificado"]["cantidad"].sum()
df2 = pd.DataFrame({"estado": ["No menciona", "Menciona"], "cantidad": [no_m, si_m]})
fig = px.pie(df2, values="cantidad", names="estado", hole=0.58, color_discrete_sequence=[GRIS_OSCURO, AZUL])
fig.update_traces(textinfo="value+percent", textfont=dict(size=14), marker=dict(line=dict(color="white", width=2)))
_layout_base(fig, "Mención de papeles en regla", "El 62.7% de los anuncios no especifica si tiene papeles.", "Fuente: 1,200 anuncios de Revolico.", 440)
fig.update_layout(margin=dict(l=40, r=40, t=110, b=80))
guardar(fig, "09_papeles")

# ---------------------------------------------------------------
# 10. Preferencia
# ---------------------------------------------------------------
df = pd.read_csv(CSV / "entrevistas_preferencia.csv")
fig = px.pie(df, values="cantidad", names="categoria", hole=0.58, color="categoria", color_discrete_map={"Eléctrica": AZUL, "Combustión": AZUL_MEDIO, "No especificado": GRIS_CLARO})
fig.update_traces(textinfo="value+percent", textfont=dict(size=14), marker=dict(line=dict(color="white", width=2)))
_layout_base(fig, "Preferencia declarada por los usuarios", "El 80% prefiere la moto eléctrica sobre la de combustión.", "Fuente: 30 entrevistas semiestructuradas.", 440)
fig.update_layout(margin=dict(l=40, r=40, t=110, b=80))
guardar(fig, "10_preferencia")

# ---------------------------------------------------------------
# 11. Factor principal de compra
# ---------------------------------------------------------------
df = pd.read_csv(CSV / "entrevistas_factor_principal.csv")
df = df.sort_values("cantidad", ascending=True)
fig = px.bar(df, x="cantidad", y="categoria", orientation="h", text="cantidad", color_discrete_sequence=[AZUL])
fig.update_traces(textposition="outside", marker_line_width=0)
_layout_base(fig, "Factor principal de compra", "¿Qué pesó más en la decisión? El precio domina (63%).", "Fuente: 30 entrevistas. n=27.", 500)
fig.update_xaxes(title="Cantidad de menciones", showgrid=True, gridcolor="#F3F4F6", zeroline=False)
fig.update_yaxes(title="", showgrid=False)
guardar(fig, "11_factor_compra")

# ---------------------------------------------------------------
# 12. Frecuencia de carga
# ---------------------------------------------------------------
df = pd.read_csv(CSV / "entrevistas_frecuencia_carga.csv")
df = df.sort_values("cantidad", ascending=False)
fig = px.bar(df, x="categoria", y="cantidad", text="cantidad", color_discrete_sequence=[AZUL])
fig.update_traces(textposition="outside", marker_line_width=0)
_layout_base(fig, "Frecuencia de carga", "40% carga a diario; dependencia de la disponibilidad de corriente.", "Fuente: 30 entrevistas. n=20.", 480)
fig.update_xaxes(title="", showgrid=False, tickangle=-20)
fig.update_yaxes(title="Cantidad", showgrid=True, gridcolor="#F3F4F6")
fig.update_layout(showlegend=False)
guardar(fig, "12_frecuencia_carga")

# ---------------------------------------------------------------
# 13. Fallos técnicos
# ---------------------------------------------------------------
df = pd.read_csv(CSV / "entrevistas_fallos_tecnicos.csv")
df = df.sort_values("cantidad", ascending=True)
fig = px.bar(df, x="cantidad", y="categoria", orientation="h", text="cantidad", color_discrete_sequence=[AZUL])
fig.update_traces(textposition="outside", marker_line_width=0)
_layout_base(fig, "Fallos técnicos reportados", "42.3% reportó al menos un problema desde la compra.", "Fuente: 30 entrevistas. n=26.", 440)
fig.update_xaxes(title="Cantidad de entrevistados", showgrid=True, gridcolor="#F3F4F6", zeroline=False)
fig.update_yaxes(title="", showgrid=False)
guardar(fig, "13_fallos_tecnicos")

# ---------------------------------------------------------------
# 14. Apagones
# ---------------------------------------------------------------
df = pd.read_csv(CSV / "entrevistas_apagones.csv")
fig = px.pie(df, values="cantidad", names="categoria", hole=0.58, color="categoria", color_discrete_map={"True": AZUL, "False": GRIS_CLARO})
fig.update_traces(textinfo="value+percent", textfont=dict(size=14), marker=dict(line=dict(color="white", width=2)))
_layout_base(fig, "Problemas de carga durante los apagones", "La mitad de los entrevistados reportó dificultades.", "Fuente: 30 entrevistas. n=19.", 440)
fig.update_layout(margin=dict(l=40, r=40, t=110, b=80))
guardar(fig, "14_apagones")

print(f"\nTodos los graficos en: {OUT.resolve()}")
