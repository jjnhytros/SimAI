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
    location_id: str                # ID univoco della locazione (es. "max_casa_soggiorno")
    name: str                       # Nome visualizzato (es. "Soggiorno di Max", "Parco Centrale")
    location_type: LocationType     # Tipo di locazione dall'Enum (es. LocationType.RESIDENTIAL_LIVING_ROOM)
    description: Optional[str] = None # Breve descrizione del luogo

    # Oggetti presenti in questa locazione
    objects_in_location: List[GameObject] = field(default_factory=list)
    
    # NPC attualmente presenti in questa locazione (memorizza i loro ID)
    npcs_present_ids: Set[str] = field(default_factory=set)

    # (Futuro) Caratteristiche ambientali e di stato
    # environment_score: int = 50       # Punteggio base dell'ambiente (0-100)
    # cleanliness_level: int = 100      # Livello di pulizia (0-100)
    # light_level: int = 70             # Livello di illuminazione (0-100)
    # noise_level: int = 20             # Livello di rumore (0-100)
    # privacy_level: int = 5            # Livello di privacy (0=pubblico, 10=massima privacy)
    # max_capacity: Optional[int] = None # Numero massimo di NPC che possono stare qui contemporaneamente

    # (Futuro) Connessioni ad altre locazioni (per il pathfinding)
    # connected_locations: Dict[str, str] = field(default_factory=dict) # Es. {"porta_nord": "corridoio_01"}

    def __str__(self) -> str:
        object_names = [obj.name for obj in self.objects_in_location[:3]] # Mostra i primi 3 oggetti
        if len(self.objects_in_location) > 3:
            object_names.append("...")
        return (f"Location(ID: {self.location_id}, Nome: \"{self.name}\", Tipo: {self.location_type.name}, "
                f"NPCs Presenti: {len(self.npcs_present_ids)}, Oggetti: {object_names if object_names else 'Nessuno'})")

    def add_object(self, game_object: GameObject):
        """Aggiunge un oggetto alla locazione."""
        if game_object not in self.objects_in_location:
            self.objects_in_location.append(game_object)
            # if settings.DEBUG_MODE: print(f"  [Location - {self.name}] Oggetto '{game_object.name}' aggiunto.")

    def remove_object(self, game_object_id: str) -> Optional[GameObject]:
        """Rimuove un oggetto dalla locazione e lo restituisce."""
        obj_to_remove = next((obj for obj in self.objects_in_location if obj.object_id == game_object_id), None)
        if obj_to_remove:
            self.objects_in_location.remove(obj_to_remove)
            # if settings.DEBUG_MODE: print(f"  [Location - {self.name}] Oggetto '{obj_to_remove.name}' rimosso.")
            return obj_to_remove
        # if settings.DEBUG_MODE: print(f"  [Location - {self.name}] Oggetto con ID '{game_object_id}' non trovato per la rimozione.")
        return None

    def get_object_by_id(self, object_id: str) -> Optional[GameObject]:
        """Restituisce un oggetto specifico presente nella locazione tramite il suo ID."""
        return next((obj for obj in self.objects_in_location if obj.object_id == object_id), None)
        
    def get_objects_by_type(self, object_type: ObjectType) -> List[GameObject]:
        """Restituisce una lista di oggetti di un tipo specifico presenti nella locazione."""
        return [obj for obj in self.objects_in_location if obj.object_type == object_type]

    def add_npc(self, npc_id: str):
        """Registra che un NPC è entrato nella locazione."""
        self.npcs_present_ids.add(npc_id)
        # if settings.DEBUG_MODE: print(f"  [Location - {self.name}] NPC '{npc_id}' entrato.")

    def remove_npc(self, npc_id: str):
        """Registra che un NPC è uscito dalla locazione."""
        self.npcs_present_ids.discard(npc_id) # discard non solleva errore se l'elemento non c'è
        # if settings.DEBUG_MODE: print(f"  [Location - {self.name}] NPC '{npc_id}' uscito.")
        
    def is_npc_present(self, npc_id: str) -> bool:
        """Controlla se un NPC specifico è presente nella locazione."""
        return npc_id in self.npcs_present_ids

    # (Futuro) Metodi per calcolare punteggi ambientali, trovare oggetti specifici per azioni, ecc.
    # def get_available_object_for_activity(self, activity_type: FunActivityType) -> Optional[GameObject]:
    #     for obj in self.objects_in_location:
    #         if activity_type in obj.provides_fun_activities and not obj.is_in_use:
    #             return obj
    #     return None