# core/utils/math_utils.py
import math
from typing import Tuple

def calculate_distance(pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
    """Calcola la distanza euclidea tra due punti."""
    x1, y1 = pos1
    x2, y2 = pos2
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)