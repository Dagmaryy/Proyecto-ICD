"""Genera los JSON finales de 7 campos a partir de los anuncios procesados.

Uso:
    python -u src/scripts/generar_500_limpio.py
    python -u src/scripts/generar_500_limpio.py --categoria bicis
    python -u src/scripts/generar_500_limpio.py --limite 500 --salida-dir /tmp/prueba
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.scrapers.reglas_limpieza import CATEGORIAS_FUENTES, generar_limpios_500


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Genera [categoria]_500_limpio.json con 7 campos por reglas."
    )
    parser.add_argument(
        "--categoria",
        choices=(*CATEGORIAS_FUENTES, "todas"),
        default="todas",
        help="Categoría a procesar (por defecto todas).",
    )
    parser.add_argument(
        "--limite",
        type=int,
        default=500,
        help="Máximo de registros por categoría (por defecto 500).",
    )
    parser.add_argument(
        "--salida-dir",
        type=Path,
        default=None,
        help="Directorio de salida alternativo (por defecto data/processed/final).",
    )
    args = parser.parse_args(argv)

    categorias = (
        list(CATEGORIAS_FUENTES)
        if args.categoria == "todas"
        else [args.categoria]
    )
    resumen = generar_limpios_500(
        categorias,
        limite=args.limite,
        directorio_salida=args.salida_dir,
    )
    for categoria, total in resumen.items():
        print(f"[OK] {categoria}: {total} registros")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
