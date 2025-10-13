"""
Servicios de integración con APIs externas
"""

# Imports opcionales - evita errores si faltan dependencias
__all__ = []

try:
    from app.services.anthropic_service import AnthropicService
    __all__.append('AnthropicService')
except ImportError as e:
    print(f"Warning: AnthropicService no disponible: {e}")
    AnthropicService = None

try:
    from app.services.semrush_service import SemrushService
    __all__.append('SemrushService')
except ImportError as e:
    print(f"Warning: SemrushService no disponible: {e}")
    SemrushService = None

try:
    from app.services.openai_service import OpenAIService
    __all__.append('OpenAIService')
except ImportError as e:
    # OpenAI es completamente opcional
    OpenAIService = None
