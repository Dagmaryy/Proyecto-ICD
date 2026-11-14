"""
Configuración centralizada de rutas del proyecto.
Cualquier script que necesite leer o escribir datos debe importar desde aquí.
"""
from pathlib import Path

# Detecta la raíz del proyecto (donde está este archivo, sube un nivel)
ROOT_DIR = Path(__file__).resolve().parent.parent

# Directorios de datos
DATA_RAW = ROOT_DIR / "data" / "raw"
DATA_PROCESSED = ROOT_DIR / "data" / "processed"
JSON_DIR = DATA_PROCESSED / "final" / "JSON"
CSV_DIR = DATA_PROCESSED / "final" / "CSV"

# Directorios de salida y web
REPORTS_PLOTS = ROOT_DIR / "reports" / "plots"
WEB_DIR = ROOT_DIR # El index.html ahora está en la raíz

# Asegurar que las carpetas existan al importar el módulo
for d in [DATA_PROCESSED, JSON_DIR, CSV_DIR, REPORTS_PLOTS]:
    d.mkdir(parents=True, exist_ok=True)
