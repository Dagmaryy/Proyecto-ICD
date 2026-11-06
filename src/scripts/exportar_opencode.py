"""
Exporta los prompts de OpenCode desde la base SQLite a Markdown legible.
Uso: python src/scripts/exportar_opencode.py
Salida: docs/opencode_prompts.md
"""
import json
import sqlite3
from datetime import datetime
from pathlib import Path

DB = Path.home() / ".local/share/opencode/opencode.db"
OUT = Path("docs/opencode_prompts.md")

conn = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Sesiones ordenadas por fecha
sesiones = cur.execute(
    "SELECT id, title, time_created FROM session ORDER BY time_created"
).fetchall()

def ts(ms):
    return datetime.fromtimestamp(ms / 1000).strftime("%Y-%m-%d %H:%M")

lineas = ["# Uso de OpenCode en el proyecto ICD", ""]
lineas.append(f"**Extraído:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
lineas.append(f"**Base:** `~/.local/share/opencode/opencode.db`")
lineas.append(f"**Sesiones:** {len(sesiones)}")
lineas.append("")
lineas.append("---")
lineas.append("")

total_prompts = 0

for ses in sesiones:
    sid = ses["id"]
    titulo = ses["title"] or "(sin título)"
    fecha = ts(ses["time_created"])

    # Mensajes user de esta sesión
    mensajes = cur.execute("""
        SELECT m.id, m.time_created, m.data as msg_data
        FROM message m
        WHERE m.session_id = ?
          AND json_extract(m.data, '$.role') = 'user'
        ORDER BY m.time_created
    """, (sid,)).fetchall()

    if not mensajes:
        continue

    lineas.append(f"## Sesión: {titulo}")
    lineas.append(f"**ID:** `{sid}` · **Fecha:** {fecha} · **Prompts:** {len(mensajes)}")
    lineas.append("")

    for i, msg in enumerate(mensajes, 1):
        # Buscar el part de tipo text de este mensaje
        part = cur.execute("""
            SELECT data FROM part
            WHERE message_id = ?
              AND json_extract(data, '$.type') = 'text'
            LIMIT 1
        """, (msg["id"],)).fetchone()

        if not part:
            continue

        try:
            texto = json.loads(part["data"]).get("text", "").strip()
        except Exception:
            continue

        if not texto:
            continue

        total_prompts += 1
        # Si el prompt es larguísimo, cortar a 600 chars
        if len(texto) > 600:
            texto = texto[:600] + " [...]"
        # Escapar markdown
        texto = texto.replace("```", "'''")

        lineas.append(f"### Prompt {i} · {ts(msg['time_created'])}")
        lineas.append("")
        lineas.append(f"> {texto}".replace("\n", "\n> "))
        lineas.append("")

    lineas.append("---")
    lineas.append("")

lineas.insert(5, f"**Total de prompts registrados:** {total_prompts}")
lineas.insert(6, "")

OUT.write_text("\n".join(lineas), encoding="utf-8")
print(f"OK: {OUT} ({total_prompts} prompts en {len(sesiones)} sesiones)")

conn.close()
