# AGENTS.md — Proyecto ICD

## Contexto
Análisis de mercado cubano. Datos en `data/raw/`. Resultados en `data/processed/`.

## Reglas
- No modificar nunca `data/raw/`.
- Documentar cada transformación en `src/transform/`.
- Usar formato CSV y JSON en `data/processed/`.
- Journal al final de cada sesión en `journal/YYYY-MM-DD.md`.
- Registrar prompts en `prompts/sesiones.md` con URL.

## Herramientas
- Python (pandas, requests, beautifulsoup4)
- OpenCode (agente Plan para explorar, Build para implementar)
- Git para control de versiones