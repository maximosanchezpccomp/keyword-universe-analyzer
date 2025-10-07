"""
Utilidades y funciones auxiliares

NOTA: Los imports se hacen directamente en los módulos que los necesitan
      para evitar importaciones circulares.
"""

# No importar nada automáticamente para evitar circular imports
__all__ = []

# Si necesitas hacer imports, hazlos de forma lazy:
def get_helpers():
    """Lazy import de funciones helper"""
    from app.utils import helpers
    return helpers

def get_prompts():
    """Lazy import de prompts"""
    from app.utils import prompts
    return prompts
