# core/world/game_object.py
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Set # Aggiunto Set per coerenza

# Assicurati che gli Enum siano importati correttamente
from core.enums import FunActivityType, ObjectType, NeedType 
# from core.enums import SkillName # Da importare quando SkillName sarà definito
# Non importare settings qui se non strettamente necessario per evitare dipendenze incrociate

@dataclass
class GameObject:
    object_id: str
    name: str
    object_type: ObjectType
    description: Optional[str] = None
    provides_fun_activities: List[FunActivityType] = field(default_factory=list)
    comfort_value: int = 0
    environment_score_modifier: int = 0
    is_usable: bool = True
    is_in_use: bool = False
    user_npc_id: Optional[str] = None
    is_water_source: bool = False # Indica se l'oggetto può essere usato per bere
    # required_skills_to_use: Dict['SkillName', int] = field(default_factory=dict)
    # effects_on_needs_direct: Dict[NeedType, float] = field(default_factory=dict)
    # provides_skill_gain: Optional['SkillName'] = None

    def __str__(self):
        return f"GameObject(ID: {self.object_id}, Nome: \"{self.name}\", Tipo: {self.object_type.name})"

    def start_use(self, npc_id: str) -> bool:
        # from core import settings # Import locale se serve DEBUG_MODE qui
        if not self.is_usable:
            # if settings.DEBUG_MODE: print(f"  [GameObject - {self.name}] Tentativo di usare oggetto non usabile.")
            return False
        if self.is_in_use:
            # if settings.DEBUG_MODE: print(f"  [GameObject - {self.name}] Tentativo di usare oggetto già in uso da {self.user_npc_id}.")
            return False
        self.is_in_use = True
        self.user_npc_id = npc_id
        # if settings.DEBUG_MODE: print(f"  [GameObject - {self.name}] Ora in uso da {npc_id}.")
        return True

    def stop_use(self, npc_id: str):
        # from core import settings # Import locale se serve DEBUG_MODE qui
        if self.user_npc_id == npc_id:
            self.is_in_use = False
            self.user_npc_id = None
            # if settings.DEBUG_MODE: print(f"  [GameObject - {self.name}] Ora libero.")
        # elif settings.DEBUG_MODE:
            # print(f"  [GameObject - {self.name}] Tentativo di liberare da NPC ({npc_id}) che non lo sta usando (Usato da: {self.user_npc_id}).")