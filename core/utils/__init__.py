# core/utils/__init__.py
"""
Il pacchetto 'utils' contiene funzioni helper e di utilità generiche
usate in diverse parti del progetto.
"""
# Importa le funzioni dai loro moduli specifici per renderle 
# accessibili direttamente dal pacchetto.

from .math_utils import calculate_distance
from .name_generator import gen_lastname

# La lista __all__ definisce quali nomi verranno importati 
# quando si fa "from core.utils import *"
__all__ = [
    'calculate_distance',
    'gen_lastname',
]