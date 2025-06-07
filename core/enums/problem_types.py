# core/enums/problem_types.py
"""
Definizione dell'Enum ProblemType per i tipi di problemi che un NPC può affrontare.
"""
from enum import Enum, auto

class ProblemType(Enum):
    """Tipi di problemi che un NPC può affrontare."""
    LOW_NEED = auto()
    # In futuro potremmo aggiungere:
    # THREAT_DETECTED = auto()
    # OPPORTUNITY_AVAILABLE = auto()
    # SOCIAL_CONFLICT = auto()
