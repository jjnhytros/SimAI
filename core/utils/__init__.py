# core/utils/__init__.py
"""
Il pacchetto 'utils' contiene funzioni helper e di utilità generiche
usate in diverse parti del progetto.
"""

# Importa la funzione dal suo modulo specifico per renderla 
# accessibile direttamente dal pacchetto.
from .math_utils import calculate_distance

# La lista __all__ definisce quali nomi verranno importati quando si fa "from core.utils import *"
__all__ = [
    'calculate_distance',
]
