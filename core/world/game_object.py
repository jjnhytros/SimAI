# core/world/game_object.py
"""
Definizione della classe GameObject, per oggetti interattivi nel mondo di gioco.
"""
from dataclasses import dataclass, field
from typing import List, Optional

from core.enums import ObjectType, FunActivityType, ItemQuality

@dataclass
class GameObject:
    """Rappresenta un oggetto nel mondo con cui gli NPC possono interagire."""
    # --- Campi del costruttore (usati quando crei l'oggetto) ---
    object_id: str
    name: str
    object_type: ObjectType
    
    logical_x: int = 0
    logical_y: int = 0
    
    description: str = ""
    comfort_value: int = 0
    is_water_source: bool = False
    provides_fun_activities: List[FunActivityType] = field(default_factory=list)
    style: str = "default"
    quality: Optional[ItemQuality] = None
    # --- Campi di STATO (non nel costruttore, inizializzati dopo) ---
    # Usiamo init=False per dire alla dataclass di non includerli in __init__.
    # Saranno inizializzati a un valore di default tramite __post_init__.
    is_in_use_by: Optional[str] = field(init=False, default=None)
    is_broken: bool = field(init=False, default=False)
    
    def __post_init__(self):
        """
        Metodo speciale delle dataclass che viene chiamato automaticamente dopo __init__.
        Utile per inizializzare i campi con init=False.
        """
        self.is_in_use_by = None
        self.is_broken = False
    
    # --- Metodi per la gestione dello stato ---
    
    def is_available(self) -> bool:
        """Restituisce True se l'oggetto è libero e non è rotto."""
        return self.is_in_use_by is None and not self.is_broken

    def set_in_use(self, npc_id: str) -> bool:
        """
        Imposta l'oggetto come "in uso" da parte di un NPC.
        Restituisce True se l'operazione ha successo, False altrimenti.
        """
        if self.is_available():
            self.is_in_use_by = npc_id
            return True
        return False

    def set_free(self):
        """Libera l'oggetto, rendendolo di nuovo disponibile."""
        self.is_in_use_by = None

    def __str__(self):
        # La tua rappresentazione stringa esistente va benissimo
        return f"GameObject(ID: {self.object_id}, Nome: \"{self.name}\", Tipo: {self.object_type.name}, Pos: ({self.logical_x},{self.logical_y}))"