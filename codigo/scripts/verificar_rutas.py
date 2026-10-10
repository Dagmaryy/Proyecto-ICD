#!/usr/bin/env python3
"""Verifica que las rutas citadas en el proyecto existan.

Busca rutas en README, AGENTS, config.yaml, scripts (.py), notebooks (.ipynb) y
documentos (.md), y avisa de las que apuntan a archivos o carpetas que no existen.
Sirve para ejecutarlo tras crear, mover o renombrar algo.

Uso (desde cualquier carpeta del proyecto):
    python3 verificar_rutas.py            # detecta la raíz buscando AGENTS.md
    python3 verificar_rutas.py RUTA_RAIZ  # o indicando la raíz

Código de salida: 0 si todo está bien, 1 si hay rutas rotas.
"""
import json
import re
import sys
from pathlib import Path

# Carpetas de primer nivel que se vigilan (incluye nombres históricos y nuevos,
# para detectar referencias que quedaron apuntando a nombres viejos).
PREFIJOS = (
    "data", "datos", "src", "codigo", "notebooks", "docs", "reports",
    "elements", "prompts", "historia", "opencode",
)
EXTENSIONES = {".md", ".py", ".yaml", ".yml", ".ipynb"}
EXCLUIR_DIRS = {".git", "venv", ".venv", "env", "__pycache__", "node_modules",
                ".ipynb_checkpoints"}
EXCLUIR_PREFIJOS_NOMBRE = ("_backup",)

RE_RUTA = re.compile(
    r"(?<![\w/.\-])((?:\.\./)*(?:" + "|".join(PREFIJOS) + r")/[^\s\"'`<>()\[\]{}*,;|]+)"
)
RE_BASE_DIR = re.compile(r'BASE_DIR\s*/\s*"([^"]+)"((?:\s*/\s*"[^"]+")*)')
RE_PARTES = re.compile(r'/\s*"([^"]+)"')


def encontrar_raiz(arg):
    if arg:
        return Path(arg).resolve()
    for base in (Path.cwd(), Path(__file__).resolve().parent):
        for carpeta in (base, *base.parents):
            if (carpeta / "AGENTS.md").exists():
                return carpeta
    sys.exit("No encuentro la raíz del proyecto (AGENTS.md). Indícala como argumento.")


def leer_gitignore(raiz):
    patrones = []
    ruta = raiz / ".gitignore"
    if ruta.exists():
        for linea in ruta.read_text(encoding="utf-8", errors="ignore").splitlines():
            linea = linea.strip()
            if linea and not linea.startswith("#") and not linea.startswith("!"):
                patrones.append(linea.rstrip("/"))
    return patrones


def esta_ignorada(rel, patrones):
    """Rutas ignoradas por git (caché, audios): no se exige que existan."""
    for p in patrones:
        base = re.split(r"[*?\[]", p)[0].rstrip("/")
        if base and (rel == base or rel.startswith(base + "/")):
            return True
    return False


def limpiar(ruta):
    return ruta.rstrip(".:;,)'\"`")


def candidatas(texto):
    """Devuelve (linea, ruta) de cada ruta citada en el texto."""
    res = []
    for n, linea in enumerate(texto.splitlines(), 1):
        for m in RE_BASE_DIR.finditer(linea):
            partes = [m.group(1)] + RE_PARTES.findall(m.group(2))
            res.append((n, "/".join(p.strip("/") for p in partes)))
        for m in RE_RUTA.finditer(linea):
            res.append((n, limpiar(m.group(1))))
    return res


def es_plantilla(ruta):
    return bool(re.search(r"XXX|\.\.\.|AAAA|NNN|<|>", ruta))


def textos_de(archivo):
    """Texto revisable del archivo (en notebooks, solo celdas, no salidas)."""
    if archivo.suffix == ".ipynb":
        try:
            nb = json.loads(archivo.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return ""
        return "\n".join("".join(c.get("source", [])) for c in nb.get("cells", []))
    return archivo.read_text(encoding="utf-8", errors="ignore")


def existe(ruta, archivo, raiz):
    candidatos = {raiz / ruta, archivo.parent / ruta}
    return any(c.resolve().exists() for c in candidatos)


def main():
    raiz = encontrar_raiz(sys.argv[1] if len(sys.argv) > 1 else None)
    ignoradas = leer_gitignore(raiz)
    rotas, revisadas = [], 0

    for archivo in sorted(raiz.rglob("*")):
        rel_arch = archivo.relative_to(raiz)
        if not archivo.is_file() or archivo.suffix not in EXTENSIONES:
            continue
        if any(p in EXCLUIR_DIRS or p.startswith(EXCLUIR_PREFIJOS_NOMBRE) for p in rel_arch.parts):
            continue
        cands = [(l, r) for l, r in candidatas(textos_de(archivo)) if not es_plantilla(r)]
        # Si una línea prueba varias variantes de la misma ruta (p. ej. "../data" y
        # "../../data") y alguna existe, las demás no cuentan como rotas.
        existentes = {(l, r.replace("../", "")) for l, r in cands if existe(r, archivo, raiz)}
        revisadas += len(cands)
        for linea, ruta in cands:
            if (linea, ruta.replace("../", "")) in existentes:
                continue
            normal = ruta
            if ruta.startswith("../"):
                try:
                    normal = str((archivo.parent / ruta).resolve().relative_to(raiz))
                except ValueError:
                    normal = ruta.replace("../", "")
            if esta_ignorada(normal, ignoradas) or esta_ignorada(ruta, ignoradas):
                continue
            if not existe(ruta, archivo, raiz):
                rotas.append((str(rel_arch), linea, ruta))

    # .gitignore: avisar si una regla apunta a una carpeta raíz que ya no existe
    avisos = []
    for p in ignoradas:
        primero = p.split("/")[0]
        if primero in PREFIJOS and not (raiz / primero).exists():
            avisos.append(p)

    print(f"Raíz: {raiz}")
    print(f"Rutas revisadas: {revisadas}")
    if rotas:
        print(f"\nRUTAS ROTAS ({len(rotas)}):")
        for arch, linea, ruta in rotas:
            print(f"  {arch}:{linea}  ->  {ruta}")
    if avisos:
        print("\nREGLAS DE .gitignore QUE APUNTAN A CARPETAS INEXISTENTES:")
        for p in avisos:
            print(f"  {p}")
    if not rotas and not avisos:
        print("\nTodo bien: no hay rutas rotas.")
    sys.exit(1 if rotas or avisos else 0)


if __name__ == "__main__":
    main()
