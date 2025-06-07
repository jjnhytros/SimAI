# Proposta per un nuovo file: core/modules/memory/memory_definitions.py

from typing import Dict, Any, Optional
from core.enums import ActionType, SocialInteractionType

class Memory:
    def __init__(self,
                 memory_id: str,
                 timestamp: float, # Il tick della simulazione in cui è avvenuto
                 event_description: str, # Una stringa leggibile per il debug, es: "Ho flirtato con Sara"
                 
                 # Il cuore del ricordo: che effetto emotivo ha avuto?
                 # Da -1.0 (traumatico) a 1.0 (estremamente positivo)
                 emotional_impact: float, 
                 
                 # Quanto è importante questo ricordo? Influenzerà la sua "durata".
                 # Da 0.0 (banale) a 1.0 (evento che cambia la vita)
                 salience: float,

                 # Dizionario di entità collegate, per poterle cercare
                 related_entities: Dict[str, Any]
                ):
        self.memory_id = memory_id
        self.timestamp = timestamp
        self.event_description = event_description
        self.emotional_impact = emotional_impact
        self.salience = salience
        self.related_entities = related_entities # Es: {'target_npc_id': 'npc_sara_id', 'action_type': 'FLIRT'}