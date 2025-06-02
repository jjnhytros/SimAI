# core/world/game_object.py
"""
Definizione della classe GameObject, per oggetti interattivi nel mondo di gioco.
"""
from dataclasses import dataclass, field
from typing import List, Optional

from core.enums import ObjectType, FunActivityType

@dataclass
class GameObject:
    """Rappresenta un oggetto nel mondo con cui gli NPC possono interagire."""
    object_id: str
    name: str
    object_type: ObjectType
    
    # Coordinate logiche dell'oggetto all'interno della sua locazione (es. su una griglia)
    logical_x: int = 0
    logical_y: int = 0
    
    description: str = ""
    comfort_value: int = 0
    is_water_source: bool = False
    provides_fun_activities: List[FunActivityType] = field(default_factory=list)

    def __str__(self):
        return f"GameObject(ID: {self.object_id}, Nome: \"{self.name}\", Tipo: {self.object_type.name}, Pos: ({self.logical_x},{self.logical_y}))"