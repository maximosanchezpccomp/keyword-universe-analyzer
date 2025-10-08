"""
Servicios de integración con APIs externas
"""

from app.services.anthropic_service import AnthropicService
from app.services.semrush_service import SemrushService
from app.services.architecture_service import WebArchitectureService

# OpenAI es opcional, solo importar si existe
try:
    from app.services.openai_service import OpenAIService
    __all__ = [
        'AnthropicService',
        'SemrushService',
        'OpenAIService',
        'WebArchitectureService',
    ]
except ImportError:
    __all__ = [
        'AnthropicService',
        'SemrushService',
        'WebArchitectureService',
    ]
