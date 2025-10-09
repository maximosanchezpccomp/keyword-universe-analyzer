"""
Servicios de integración con APIs externas

Este módulo proporciona acceso a los servicios de:
- Anthropic (Claude) - Análisis con IA
- Semrush - Datos de keywords y competidores
- OpenAI (opcional) - Análisis alternativo con GPT

Uso:
    from app.services import AnthropicService, SemrushService
    
    # Verificar disponibilidad
    from app.services import is_openai_available
    if is_openai_available():
        from app.services import OpenAIService
"""

import logging
from typing import List, Optional

# Configurar logger
logger = logging.getLogger(__name__)

# Servicios principales (siempre disponibles)
from app.services.anthropic_service import AnthropicService
from app.services.semrush_service import SemrushService

# OpenAI es opcional, solo importar si existe
OPENAI_AVAILABLE = False
OpenAIService = None

try:
    from app.services.openai_service import OpenAIService
    OPENAI_AVAILABLE = True
    __all__ = [
        'AnthropicService',
        'SemrushService',
        'OpenAIService',
        'is_openai_available',
        'get_available_services',
        'OPENAI_AVAILABLE',
    ]
    logger.info("✓ OpenAI service disponible")
except ImportError as e:
    __all__ = [
        'AnthropicService',
        'SemrushService',
        'is_openai_available',
        'get_available_services',
        'OPENAI_AVAILABLE',
    ]
    logger.debug(f"OpenAI service no disponible: {e}")


def is_openai_available() -> bool:
    """
    Verifica si el servicio de OpenAI está disponible
    
    Returns:
        bool: True si OpenAI está disponible, False en caso contrario
    
    Example:
        >>> from app.services import is_openai_available
        >>> if is_openai_available():
        ...     from app.services import OpenAIService
        ...     service = OpenAIService(api_key)
    """
    return OPENAI_AVAILABLE


def get_available_services() -> List[str]:
    """
    Obtiene la lista de servicios disponibles
    
    Returns:
        List[str]: Lista con los nombres de los servicios disponibles
    
    Example:
        >>> from app.services import get_available_services
        >>> services = get_available_services()
        >>> print(f"Servicios disponibles: {', '.join(services)}")
        Servicios disponibles: AnthropicService, SemrushService, OpenAIService
    """
    services = ['AnthropicService', 'SemrushService']
    if OPENAI_AVAILABLE:
        services.append('OpenAIService')
    return services


def get_service_info() -> dict:
    """
    Obtiene información detallada sobre los servicios disponibles
    
    Returns:
        dict: Diccionario con información de cada servicio
    
    Example:
        >>> from app.services import get_service_info
        >>> info = get_service_info()
        >>> for service, details in info.items():
        ...     print(f"{service}: {details['status']}")
    """
    info = {
        'AnthropicService': {
            'status': 'available',
            'description': 'Servicio de análisis con Claude (Anthropic)',
            'required': True,
            'provider': 'Anthropic'
        },
        'SemrushService': {
            'status': 'available',
            'description': 'Servicio de datos de keywords y competidores',
            'required': False,
            'provider': 'Semrush'
        },
        'OpenAIService': {
            'status': 'available' if OPENAI_AVAILABLE else 'not_available',
            'description': 'Servicio de análisis con GPT (OpenAI)',
            'required': False,
            'provider': 'OpenAI'
        }
    }
    return info


# Información del módulo
__version__ = '1.0.0'
__author__ = 'PC Componentes'

# Log de inicialización
logger.info(f"Módulo services inicializado - Servicios disponibles: {len(get_available_services())}")
