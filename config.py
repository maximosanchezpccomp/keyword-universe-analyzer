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

# Configuración de caché
CACHE_CONFIG = {
    "enabled": os.getenv("ENABLE_CACHE", "true").lower() == "true",
    "cache_dir": os.getenv("CACHE_DIR", "cache"),
    "default_ttl_hours": int(os.getenv("CACHE_TTL_HOURS", "24")),
    "max_size_mb": int(os.getenv("CACHE_MAX_SIZE_MB", "500")),
    "auto_cleanup_days": int(os.getenv("CACHE_AUTO_CLEANUP_DAYS", "30"))
}

# Estimaciones de coste por modelo (costes octubre 2025)
COST_ESTIMATES = {
    "claude-sonnet-4-5-20250929": {
        "input_per_1k": 0.003,   # $3 / 1M
        "output_per_1k": 0.015,  # $15 / 1M
        "avg_input_tokens": 10000,
        "avg_output_tokens": 5000
    },  # Anthropic mantiene $3/$15. :contentReference[oaicite:0]{index=0}

    "claude-opus-4-20250514": {
        "input_per_1k": 0.015,   # $15 / 1M
        "output_per_1k": 0.075,  # $75 / 1M
        "avg_input_tokens": 10000,
        "avg_output_tokens": 5000
    },  # Opus 4 sigue a $15/$75. :contentReference[oaicite:1]{index=1}

    "gpt-4o": {
        "input_per_1k": 0.005,   # $5 / 1M
        "output_per_1k": 0.015,  # $15 / 1M
        "avg_input_tokens": 10000,
        "avg_output_tokens": 5000
    },  # Precio base actual de 4o. :contentReference[oaicite:2]{index=2}

    "gpt-4-turbo": {
        "input_per_1k": 0.010,   # $10 / 1M
        "output_per_1k": 0.030,  # $30 / 1M
        "avg_input_tokens": 10000,
        "avg_output_tokens": 5000
    },  # Según la página de pricing. :contentReference[oaicite:3]{index=3}

    "gpt-4": {
        "input_per_1k": 0.030,   # $30 / 1M
        "output_per_1k": 0.060,  # $60 / 1M
        "avg_input_tokens": 10000,
        "avg_output_tokens": 5000
    }   # Según la página de pricing. :contentReference[oaicite:4]{index=4}
}

def estimate_analysis_cost(model: str, num_keywords: int = 1000) -> Dict[str, float]:
    """
    Estimar el coste de un análisis
    
    Args:
        model: Nombre del modelo
        num_keywords: Número de keywords a analizar
        
    Returns:
        Dict con costo estimado y tokens
    """
    if model not in COST_ESTIMATES:
        return {"cost": 0, "input_tokens": 0, "output_tokens": 0}
    
    config = COST_ESTIMATES[model]
    
    # Escalar tokens basado en número de keywords
    scale_factor = num_keywords / 1000
    input_tokens = int(config["avg_input_tokens"] * scale_factor)
    output_tokens = int(config["avg_output_tokens"] * scale_factor)
    
    # Calcular costo
    input_cost = (input_tokens / 1000) * config["input_per_1k"]
    output_cost = (output_tokens / 1000) * config["output_per_1k"]
    total_cost = input_cost + output_cost
    
    return {
        "cost": round(total_cost, 4),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "input_cost": round(input_cost, 4),
        "output_cost": round(output_cost, 4)
    }

# Configuración de visualización - Colores corporativos PC Componentes
VIZ_CONFIG = {
    "color_scheme": {
        1: "#FF6000",  # Naranja principal - Tier 1
        2: "#170453",  # Azul medio - Tier 2
        3: "#51437E",  # Azul medio claro - Tier 3
        4: "#8B81A9",  # Azul claro - Tier 4
        5: "#C5C0D4"   # Azul muy claro - Tier 5
    },
    "pc_colors": {
        "orange": "#FF6000",
        "orange_light": "#FF8640",
        "orange_lighter": "#FFD7BF",
        "blue_dark": "#090029",
        "blue_medium": "#170453",
        "blue_light": "#51437E",
        "blue_lighter": "#8B81A9",
        "blue_lightest": "#C5C0D4",
        "gray_dark": "#999999",
        "gray_medium": "#CCCCCC",
        "white": "#FFFFFF"
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
