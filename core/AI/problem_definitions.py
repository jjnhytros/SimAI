# core/AI/problem_definitions.py
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional, Dict, Any, List # Aggiunto List per coerenza se lo userai
import uuid

# Assumiamo che NeedType sia in core.enums
from core.enums import NeedType # O il percorso corretto se l'hai spostato

class ProblemType(Enum):
    """Tipi di problemi che un NPC può affrontare."""
    LOW_NEED = auto()
    # In futuro potremmo aggiungere:
    # THREAT_DETECTED = auto()
    # OPPORTUNITY_AVAILABLE = auto()
    # SOCIAL_CONFLICT = auto()
    # GOAL_OBSTRUCTED = auto()
    # ENVIRONMENTAL_HAZARD = auto()

@dataclass
class Problem:
    """
    Rappresenta un problema strutturato che l'IA dell'NPC deve affrontare.
    """
    # --- Campi SENZA valore di default PRIMA ---
    npc_id: str                 # ID dell'NPC che ha il problema
    problem_type: ProblemType   # Tipo di problema
    urgency: float              # Normalizzata da 0.0 (non urgente) a 1.0 (massima urgenza)

    # --- Campi CON valore di default DOPO ---
    problem_id: uuid.UUID = field(default_factory=uuid.uuid4)
    details: Dict[str, Any] = field(default_factory=dict) # Dettagli specifici del problema
                                                    # Es. per LOW_NEED: {'need': NeedType.HUNGER, 'current_value': 15.0}
    timestamp: Optional[float] = None # Tempo della simulazione in cui il problema è stato identificato
    
    # Potenziali campi futuri (con default, quindi possono stare qui):
    # source_description: str = "" 
    # related_entities_ids: List[str] = field(default_factory=list)