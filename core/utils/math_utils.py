# core/utils/math_utils.py
import math
from typing import Tuple, Union

def calculate_distance(pos1: Tuple[Union[int, float], Union[int, float]], 
                        pos2: Tuple[Union[int, float], Union[int, float]]) -> float:
    """Calcola la distanza euclidea tra due punti (pos1 e pos2)."""
    
    # La formula matematica funziona perfettamente con int e float, non serve cambiare altro.
    dx = pos1[0] - pos2[0]
    dy = pos1[1] - pos2[1]
    return math.sqrt(dx*dx + dy*dy)
