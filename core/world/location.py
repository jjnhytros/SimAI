# core/world/location.py
"""
Definizione della classe Location, che rappresenta un luogo nel mondo di gioco
che può contenere oggetti e NPC.
Riferimento TODO: XVIII.1
"""
from dataclasses import dataclass, field
from typing import List, Set, Optional, Dict

from core.enums import LocationType, ObjectType
from .game_object import GameObject  # Importa la classe GameObject che abbiamo appena definito

@dataclass
class Location:
    """Rappresenta una locazione specifica nel mondo, come una stanza o un lotto."""
    location_id: str
    name: str
    location_type: LocationType
    description: str = ""
    
    # Dizionario degli oggetti presenti in questa locazione (object_id -> GameObject)
    objects: Dict[str, GameObject] = field(default_factory=dict)
    
    # Set degli ID degli NPC attualmente presenti in questa locazione
    npcs_present_ids: Set[str] = field(default_factory=set)

    def add_object(self, obj: GameObject):
        """Aggiunge un oggetto alla locazione."""
        if obj.object_id not in self.objects:
            self.objects[obj.object_id] = obj

    def remove_object(self, object_id: str):
        """Rimuove un oggetto dalla locazione."""
        if object_id in self.objects:
            del self.objects[object_id]

    def add_npc(self, npc_id: str):
        """Registra che un NPC è entrato nella locazione."""
        self.npcs_present_ids.add(npc_id)
        # if settings.DEBUG_MODE: print(f"  [Location - {self.name}] NPC '{npc_id}' entrato.")

    def remove_npc(self, npc_id: str):
        """Registra che un NPC è uscito dalla locazione."""
        self.npcs_present_ids.discard(npc_id) # discard non solleva errore se l'elemento non c'è
        # if settings.DEBUG_MODE: print(f"  [Location - {self.name}] NPC '{npc_id}' uscito.")

    def get_objects(self):
        """Restituisce un elenco di tutti gli oggetti GameObject nella locazione."""
        return list(self.objects.values())

    def __str__(self):
        return (f"Location(ID: {self.location_id}, Name: \"{self.name}\", "
                f"NPCs: {len(self.npcs_present_ids)}, Objects: {len(self.objects)})")

    # def get_object_by_id(self, object_id: str) -> Optional[GameObject]:
    #     """Restituisce un oggetto specifico presente nella locazione tramite il suo ID."""
    #     return next((obj for obj in self.objects_in_location if obj.object_id == object_id), None)
        
    # def get_objects_by_type(self, object_type: ObjectType) -> List[GameObject]:
    #     """Restituisce una lista di oggetti di un tipo specifico presenti nella locazione."""
    #     return [obj for obj in self.objects_in_location if obj.object_type == object_type]


        
    def is_npc_present(self, npc_id: str) -> bool:
        """Controlla se un NPC specifico è presente nella locazione."""
        return npc_id in self.npcs_present_ids

    # (Futuro) Metodi per calcolare punteggi ambientali, trovare oggetti specifici per azioni, ecc.
    # def get_available_object_for_activity(self, activity_type: FunActivityType) -> Optional[GameObject]:
    #     for obj in self.objects_in_location:
    #         if activity_type in obj.provides_fun_activities and not obj.is_in_use:
    #             return obj
    #     return None