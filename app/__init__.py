"""
Keyword Universe Analyzer - Aplicación Principal

Este paquete contiene la aplicación de análisis de keywords con IA.
"""

import logging
import sys
from pathlib import Path

# Versión del paquete
__version__ = "1.0.0"
__author__ = "Tu Nombre"
__email__ = "tu-email@ejemplo.com"
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

# Importar componentes principales (lazy loading para evitar errores circulares)
try:
    from app.services.anthropic_service import AnthropicService
    from app.services.semrush_service import SemrushService
    from app.components.data_processor import DataProcessor
    from app.components.visualizer import KeywordVisualizer
    
    __all__ = [
        'AnthropicService',
        'SemrushService',
        'DataProcessor',
        'KeywordVisualizer',
        '__version__',
    ]
    
    logger.info("Componentes principales cargados correctamente")
    
except ImportError as e:
    logger.warning(f"Algunos componentes no pudieron ser importados: {e}")
    __all__ = ['__version__']

# Metadata del paquete
PACKAGE_INFO = {
    'name': 'Keyword Universe Analyzer',
    'version': __version__,
    'description': 'Herramienta de análisis SEO con IA para crear universos de keywords',
    'author': __author__,
    'email': __email__,
    'license': __license__,
    'url': 'https://github.com/tu-usuario/keyword-universe-analyzer',
    'keywords': ['seo', 'keywords', 'ai', 'claude', 'anthropic', 'semrush', 'analysis'],
}

def get_version() -> str:
    """Retorna la versión del paquete."""
    return __version__

def get_package_info() -> dict:
    """Retorna información del paquete."""
    return PACKAGE_INFO.copy()
