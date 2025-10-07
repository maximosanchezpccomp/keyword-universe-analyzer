"""
Keyword Universe Analyzer - Powered by PC Componentes

Este paquete contiene la aplicación de análisis de keywords con IA.
"""

import logging
import sys
from pathlib import Path

# Versión del paquete
__version__ = "1.0.0"
__author__ = "PC Componentes"
__email__ = "info@pccomponentes.com"
__license__ = "MIT"

# Añadir el directorio raíz al path para imports
ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Configurar logging básico
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Logger para el paquete
logger = logging.getLogger(__name__)
logger.info(f"Inicializando Keyword Universe Analyzer v{__version__}")

# ARREGLO: No importar componentes automáticamente para evitar importaciones circulares
# Los imports se harán directamente en los módulos que los necesiten
__all__ = ['__version__']

# Metadata del paquete
PACKAGE_INFO = {
    'name': 'Keyword Universe Analyzer',
    'version': __version__,
    'description': 'Herramienta de análisis SEO con IA para crear universos de keywords',
    'author': __author__,
    'email': __email__,
    'license': __license__,
    'url': 'https://github.com/pccomponentes/keyword-universe-analyzer',
    'keywords': ['seo', 'keywords', 'ai', 'claude', 'anthropic', 'semrush', 'analysis'],
}

def get_version() -> str:
    """Retorna la versión del paquete."""
    return __version__

def get_package_info() -> dict:
    """Retorna información del paquete."""
    return PACKAGE_INFO.copy()

# Lazy imports opcionales para evitar errores circulares
def get_anthropic_service():
    """Lazy import de AnthropicService"""
    try:
        from app.services.anthropic_service import AnthropicService
        return AnthropicService
    except ImportError as e:
        logger.warning(f"No se pudo importar AnthropicService: {e}")
        return None

def get_semrush_service():
    """Lazy import de SemrushService"""
    try:
        from app.services.semrush_service import SemrushService
        return SemrushService
    except ImportError as e:
        logger.warning(f"No se pudo importar SemrushService: {e}")
        return None

def get_data_processor():
    """Lazy import de DataProcessor"""
    try:
        from app.components.data_processor import DataProcessor
        return DataProcessor
    except ImportError as e:
        logger.warning(f"No se pudo importar DataProcessor: {e}")
        return None

def get_visualizer():
    """Lazy import de KeywordVisualizer"""
    try:
        from app.components.visualizer import KeywordVisualizer
        return KeywordVisualizer
    except ImportError as e:
        logger.warning(f"No se pudo importar KeywordVisualizer: {e}")
        return None

logger.info("Paquete inicializado correctamente")
