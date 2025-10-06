"""
Test suite para Keyword Universe Analyzer
"""

import sys
from pathlib import Path

# Añadir el directorio raíz al path para poder importar app
ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
