.PHONY: help install test lint format clean run docker-build docker-run

# Variables
PYTHON := python3
VENV := venv
PIP := $(VENV)/bin/pip
PYTEST := $(VENV)/bin/pytest
BLACK := $(VENV)/bin/black
FLAKE8 := $(VENV)/bin/flake8
STREAMLIT := $(VENV)/bin/streamlit

help: ## Muestra este mensaje de ayuda
	@echo "Comandos disponibles:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Instala dependencias
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "✓ Instalación completada"

install-dev: install ## Instala dependencias de desarrollo
	$(PIP) install pytest pytest-cov black flake8 mypy pre-commit
	@echo "✓ Dependencias de desarrollo instaladas"

setup: ## Setup completo del proyecto
	bash setup.sh

test: ## Ejecuta los tests
	$(PYTEST) tests/ -v

test-cov: ## Ejecuta tests con coverage
	$(PYTEST) tests/ -v --cov=app --cov-report=html --cov-report=term
	@echo "✓ Reporte de coverage generado en htmlcov/index.html"

lint: ## Verifica el código con flake8
	$(FLAKE8) app --count --select=E9,F63,F7,F82 --show-source --statistics
	$(FLAKE8) app --count --exit-zero --max-complexity=10 --max-line-length=120 --statistics

format: ## Formatea el código con black
	$(BLACK) app tests

format-check: ## Verifica formato sin modificar
	$(BLACK) --check app tests

type-check: ## Verifica tipos con mypy
	$(VENV)/bin/mypy app --ignore-missing-imports

quality: lint format-check type-check ## Ejecuta todas las verificaciones de calidad

run: ## Ejecuta la aplicación
	$(STREAMLIT) run app/main.py

run-prod: ## Ejecuta en modo producción
	$(STREAMLIT) run app/main.py \
		--server.port=8501 \
		--server.address=0.0.0.0 \
		--server.headless=true

clean: ## Limpia archivos temporales
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf dist
	rm -rf build
	@echo "✓ Archivos temporales eliminados"

clean-data: ## Limpia archivos de datos procesados
	rm -rf data/processed/*
	rm -rf outputs/*
	@echo "✓ Datos procesados eliminados"

docker-build: ## Construye la imagen Docker
	docker build -t keyword-universe-analyzer:latest .

docker-run: ## Ejecuta con Docker
	docker-compose up -d

docker-stop: ## Detiene los contenedores Docker
	docker-compose down

docker-logs: ## Muestra logs de Docker
	docker-compose logs -f

docker-clean: ## Limpia imágenes y contenedores Docker
	docker-compose down -v
	docker rmi keyword-universe-analyzer:latest

env: ## Crea archivo .env desde .env.example
	cp .env.example .env
	@echo "✓ Archivo .env creado. Edítalo con tus API keys"

requirements: ## Actualiza requirements.txt
	$(PIP) freeze > requirements.txt

tree: ## Muestra estructura del proyecto
	tree -I 'venv|__pycache__|*.pyc|.git|node_modules|htmlcov|.pytest_cache'

init-git: ## Inicializa repositorio git
	git init
	git add .
	git commit -m "Initial commit: Keyword Universe Analyzer"
	@echo "✓ Repositorio git inicializado"

pre-commit: ## Instala pre-commit hooks
	$(VENV)/bin/pre-commit install
	@echo "✓ Pre-commit hooks instalados"

check-deps: ## Verifica dependencias desactualizadas
	$(PIP) list --outdated

update-deps: ## Actualiza todas las dependencias
	$(PIP) install --upgrade -r requirements.txt

backup: ## Crea backup de datos
	tar -czf backup_$(shell date +%Y%m%d_%H%M%S).tar.gz data/ outputs/
	@echo "✓ Backup creado"

validate-config: ## Valida la configuración
	$(PYTHON) -c "from config import validate_config; result = validate_config(); print('✓ Configuración válida' if result['valid'] else f'✗ Errores: {result[\"issues\"]}')"

create-dirs: ## Crea directorios necesarios
	mkdir -p data/raw data/processed outputs logs
	touch data/raw/.gitkeep data/processed/.gitkeep
	@echo "✓ Directorios creados"

stats: ## Muestra estadísticas del código
	@echo "Líneas de código:"
	@find app -name "*.py" | xargs wc -l | tail -1
	@echo "\nArchivos Python:"
	@find app -name "*.py" | wc -l
	@echo "\nTests:"
	@find tests -name "*.py" | wc -l

# Comandos de desarrollo rápido
dev: install-dev create-dirs env ## Setup completo de desarrollo
	@echo "✓ Entorno de desarrollo configurado"
	@echo "  Siguiente paso: edita .env con tus API keys"

quick-test: ## Test rápido (sin coverage)
	$(PYTEST) tests/ -v -x

watch-test: ## Ejecuta tests en modo watch
	$(PYTEST) tests/ -v -f

# Documentación
docs: ## Genera documentación
	@echo "Generando documentación..."
	@echo "README.md existe: $(shell test -f README.md && echo 'Sí' || echo 'No')"
	@echo "QUICK_START.md existe: $(shell test -f QUICK_START.md && echo 'Sí' || echo 'No')"

# CI/CD local
ci: quality test ## Simula el pipeline CI/CD
	@echo "✓ Pipeline CI/CD completado exitosamente"

# Deployment
deploy-streamlit: ## Deploy a Streamlit Cloud
	@echo "Asegúrate de:"
	@echo "1. Push tu código a GitHub"
	@echo "2. Ve a https://share.streamlit.io"
	@echo "3. Conecta tu repositorio"
	@echo "4. Añade secrets (API keys)"
