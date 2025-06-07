# core/utils/math_utils.py
import math
from typing import Tuple

def calculate_distance(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
    """Calcola la distanza Euclidea tra due punti."""
    x1, y1 = float(pos1[0]), float(pos1[1])
    x2, y2 = float(pos2[0]), float(pos2[1])
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
