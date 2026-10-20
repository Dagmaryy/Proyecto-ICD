.PHONY: test rutas limpiar

test:
	python -m pytest tests/ -v

rutas:
	python src/scripts/verificar_rutas.py

limpiar:
	python src/scripts/limpiar_finales.py --aplicar
