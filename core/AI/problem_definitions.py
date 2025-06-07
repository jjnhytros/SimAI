# core/AI/problem_definitions.py
"""
Definisce la dataclass Problem, che rappresenta un problema strutturato
che l'IA dell'NPC deve affrontare.
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import uuid

# Importa ProblemType dalla sua nuova posizione centralizzata
from core.enums import ProblemType, NeedType

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
    timestamp: Optional[float] = None # Tempo della simulazione in cui il problema è stato identificato
    
    # Potenziali campi futuri (con default, quindi possono stare qui):
    # source_description: str = "" 
    # related_entities_ids: List[str] = field(default_factory=list)