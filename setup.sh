#!/bin/bash

# Script de instalación y configuración para Keyword Universe Analyzer
# Uso: bash setup.sh

set -e  # Salir si hay algún error

echo "🌌 Keyword Universe Analyzer - Setup Script"
echo "==========================================="
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Verificar Python
echo "Verificando requisitos del sistema..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 no está instalado"
    print_info "Por favor instala Python 3.9 o superior: https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d" " -f2 | cut -d"." -f1,2)
REQUIRED_VERSION="3.9"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    print_error "Python $PYTHON_VERSION encontrado. Se requiere Python 3.9 o superior"
    exit 1
fi

print_success "Python $PYTHON_VERSION encontrado"

# Verificar pip
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 no está instalado"
    print_info "Instalando pip..."
    python3 -m ensurepip --upgrade
fi

print_success "pip encontrado"

# Crear entorno virtual
echo ""
echo "Creando entorno virtual..."
if [ -d "venv" ]; then
    print_info "El entorno virtual ya existe. ¿Deseas recrearlo? (y/n)"
    read -r response
    if [ "$response" = "y" ]; then
        rm -rf venv
        python3 -m venv venv
        print_success "Entorno virtual recreado"
    else
        print_info "Usando entorno virtual existente"
    fi
else
    python3 -m venv venv
    print_success "Entorno virtual creado"
fi

# Activar entorno virtual
echo ""
echo "Activando entorno virtual..."
source venv/bin/activate
print_success "Entorno virtual activado"

# Actualizar pip
echo ""
echo "Actualizando pip..."
pip install --upgrade pip > /dev/null 2>&1
print_success "pip actualizado"

# Instalar dependencias
echo ""
echo "Instalando dependencias..."
print_info "Esto puede tomar unos minutos..."
pip install -r requirements.txt > /dev/null 2>&1
print_success "Dependencias instaladas"

# Crear directorios necesarios
echo ""
echo "Creando estructura de directorios..."
mkdir -p data/raw
mkdir -p data/processed
mkdir -p outputs
mkdir -p logs
touch data/raw/.gitkeep
touch data/processed/.gitkeep
print_success "Directorios creados"

# Configurar archivo .env
echo ""
if [ ! -f ".env" ]; then
    print_info "Creando archivo .env desde .env.example..."
    cp .env.example .env
    print_success "Archivo .env creado"
    print_info "⚠️  IMPORTANTE: Edita el archivo .env y añade tus API keys"
    echo ""
    echo "   - ANTHROPIC_API_KEY: Obtén tu key en https://console.anthropic.com/"
    echo "   - SEMRUSH_API_KEY (opcional): Obtén tu key en https://www.semrush.com/api-analytics/"
    echo ""
else
    print_info "El archivo .env ya existe"
fi

# Verificar configuración
echo ""
echo "Verificando configuración..."
python3 -c "
import sys
sys.path.append('.')
from config import validate_config

result = validate_config()
if not result['valid']:
    print('⚠️  Problemas encontrados en la configuración:')
    for issue in result['issues']:
        print(f'  - {issue}')
    print('\nPor favor revisa tu archivo .env')
else:
    print('✓ Configuración válida')
"

# Ejecutar tests (opcional)
echo ""
print_info "¿Deseas ejecutar los tests para verificar la instalación? (y/n)"
read -r response
if [ "$response" = "y" ]; then
    echo "Ejecutando tests..."
    pytest tests/ -v
    print_success "Tests completados"
fi

# Instrucciones finales
echo ""
echo "=========================================="
print_success "¡Instalación completada!"
echo "=========================================="
echo ""
echo "Próximos pasos:"
echo ""
echo "1. Edita el archivo .env con tus API keys:"
echo "   nano .env"
echo ""
echo "2. Activa el entorno virtual (si no está activo):"
echo "   source venv/bin/activate"
echo ""
echo "3. Inicia la aplicación:"
echo "   streamlit run app/main.py"
echo ""
echo "4. Abre tu navegador en:"
echo "   http://localhost:8501"
echo ""
echo "Para más información, consulta el README.md"
echo ""
print_info "¡Disfruta analizando tus keywords! 🚀"
