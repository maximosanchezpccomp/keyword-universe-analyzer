import os
from dotenv import load_dotenv
from pathlib import Path

# Cargar variables de entorno
load_dotenv()

# Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
OUTPUT_DIR = BASE_DIR / "outputs"

# Crear directorios si no existen
for directory in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, OUTPUT_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# API Keys
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SEMRUSH_API_KEY = os.getenv("SEMRUSH_API_KEY")

# Configuración de la aplicación
APP_CONFIG = {
    "title": os.getenv("APP_TITLE", "Keyword Universe Analyzer"),
    "version": "1.0.0",
    "author": "Tu Nombre",
    "description": "Herramienta de análisis SEO con IA"
}

# Configuración de Claude
CLAUDE_CONFIG = {
    "model": os.getenv("DEFAULT_MODEL", "claude-sonnet-4-5-20250929"),
    "max_tokens": 16000,
    "temperature": 0.3,
    "models_available": [
        "claude-sonnet-4-5-20250929",
        "claude-opus-4-20250514",
        "claude-sonnet-4-20250514"
    ]
}

# Configuración de OpenAI
OPENAI_CONFIG = {
    "model": "gpt-4o",
    "max_tokens": 16000,
    "temperature": 0.3,
    "models_available": [
        "gpt-4o",
        "gpt-4-turbo",
        "gpt-4",
        "gpt-3.5-turbo"
    ]
}

# Configuración de Semrush
SEMRUSH_CONFIG = {
    "base_url": "https://api.semrush.com/",
    "default_database": os.getenv("DEFAULT_DATABASE", "us"),
    "rate_limit_delay": 1.0,  # segundos entre requests
    "max_keywords_per_request": 10000
}

# Configuración de análisis
ANALYSIS_CONFIG = {
    "max_keywords_per_file": int(os.getenv("MAX_KEYWORDS_PER_FILE", 1000)),
    "default_tiers": int(os.getenv("DEFAULT_TIERS", 3)),
    "min_volume": int(os.getenv("MIN_VOLUME", 10)),
    "sample_size_for_ai": 1000,  # Número de keywords a enviar a Claude
    "enable_cache": os.getenv("ENABLE_CACHE", "true").lower() == "true",
    "cache_ttl": int(os.getenv("CACHE_TTL", 3600))
}

# Configuración de visualización
VIZ_CONFIG = {
    "color_scheme": {
        1: "#667eea",  # Púrpura
        2: "#764ba2",  # Morado
        3: "#f093fb",  # Rosa
        4: "#4facfe",  # Azul
        5: "#43e97b"   # Verde
    },
    "default_chart_height": 600,
    "bubble_size_multiplier": 0.5
}

# Stopwords para análisis (expandir según necesidad)
STOPWORDS = {
    'en': ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 
           'for', 'of', 'with', 'by', 'from', 'up', 'about', 'into'],
    'es': ['el', 'la', 'los', 'las', 'un', 'una', 'y', 'o', 'en', 'de',
           'del', 'por', 'para', 'con', 'sin', 'sobre', 'entre']
}

# Configuración de exportación
EXPORT_CONFIG = {
    "excel_engine": "openpyxl",
    "csv_encoding": "utf-8",
    "include_index": False
}

# Mensajes y textos de la UI
UI_MESSAGES = {
    "welcome": "👋 Bienvenido al Keyword Universe Analyzer",
    "upload_prompt": "Sube tus archivos de keywords para comenzar",
    "analyzing": "🧠 Analizando tus keywords con Claude...",
    "success": "✅ Análisis completado exitosamente",
    "error": "❌ Ocurrió un error durante el análisis",
    "no_data": "📁 No hay datos disponibles. Por favor carga archivos primero.",
    "api_key_missing": "⚠️ Por favor configura tu API key en la barra lateral"
}

# Validación de configuración
def validate_config():
    """Valida que la configuración esté correcta"""
    issues = []
    
    if not ANTHROPIC_API_KEY:
        issues.append("ANTHROPIC_API_KEY no está configurada")
    
    if ANALYSIS_CONFIG["max_keywords_per_file"] < 100:
        issues.append("max_keywords_per_file debe ser al menos 100")
    
    if ANALYSIS_CONFIG["default_tiers"] < 2 or ANALYSIS_CONFIG["default_tiers"] > 5:
        issues.append("default_tiers debe estar entre 2 y 5")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues
    }

# Logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default"
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": "app.log",
            "formatter": "default"
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["console", "file"]
    }
}
