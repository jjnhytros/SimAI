# core/graphics/__init__.py
from .renderer import Renderer
from core.settings import DEBUG_MODE
if DEBUG_MODE == True:
    print("  [graphics/__init__] Modulo Grafica caricato.")
