from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_RAW = BASE_DIR / "data" / "raw"
DATA_PROCESSED = BASE_DIR / "data" / "processed"
DATA_FINAL = BASE_DIR / "data" / "final"
JSON_DIR = DATA_FINAL / "JSON"
CSV_DIR = DATA_FINAL / "CSV"
PLOTS = BASE_DIR / "reports" / "plots"
SCHEMAS = BASE_DIR / "docs" / "schemas"

def dataset(nombre: str) -> Path:
    return JSON_DIR / f"{nombre}.json"

def table(nombre: str) -> Path:
    return CSV_DIR / f"{nombre}.csv"

def ensure_dirs():
    for d in (JSON_DIR, CSV_DIR, PLOTS):
        d.mkdir(parents=True, exist_ok=True)
