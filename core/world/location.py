# core/world/location.py
"""
Definizione della classe Location, che rappresenta un luogo nel mondo di gioco
che può contenere oggetti e NPC.
Riferimento TODO: XVIII.1
"""
from dataclasses import dataclass, field
from typing import Any, List, Set, Optional, Dict
import random

from core.enums import LocationType, ObjectType
from core.enums.tile_types import TileType
from .game_object import GameObject  # Importa la classe GameObject che abbiamo appena definito
from core.config import graphics_config

@dataclass
class Location:
    """Rappresenta una locazione specifica nel mondo, come una stanza o un lotto."""
    location_id: str
    name: str
    location_type: LocationType
    logical_width: int
    logical_height: int
    floor_map: List[List[TileType]]
    wall_map: List[List[TileType]]
    style: str = "default"
    description: str = ""
    
    # --- CAMPI CON GESTIONE SPECIALE ---
    objects: Dict[str, GameObject] = field(default_factory=dict)
    npcs_present_ids: Set[str] = field(default_factory=set)
    walkable_grid: List[List[bool]] = field(init=False, default_factory=list)

    def __post_init__(self):
        """Metodo chiamato dopo l'__init__."""
        # Creiamo la griglia di calpestabilità basandoci solo sui muri
        self._create_walkability_grid()

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
                f"Size: ({self.logical_width}x{self.logical_height}), " # Aggiunto Size
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

    def _process_tile_map(self):
        """
        Analizza la mappa di base e crea una mappa processata e stabile.
        Sceglie una variante casuale per i tipi di mattonelle che ne hanno più di una.
        """
        self.processed_tile_map = []
        for y, row in enumerate(self.tile_map):
            new_row = []
            for x, tile_type in enumerate(row):
                tile_info = {"type": tile_type, "variant_index": 0}
                
                # Se il tipo di tile ha più varianti (come il nostro muro esterno)
                # Scegliamo una variante a caso QUI, una sola volta.
                tile_def = graphics_config.TILE_DEFINITIONS.get(self.style, {}).get(tile_type)
                if isinstance(tile_def, list) and len(tile_def) > 0:
                    tile_info["variant_index"] = random.randint(0, len(tile_def) - 1)
                
                new_row.append(tile_info)
            self.processed_tile_map.append(new_row)

    def _create_walkability_grid(self):
        """
        Crea una griglia booleana. Una mattonella è calpestabile se NON c'è un muro
        e NON c'è un oggetto solido.
        """
        self.walkable_grid = []
        # 1. Crea una mappa di base considerando solo la mappa dei muri
        for y, row in enumerate(self.wall_map):
            new_row = []
            for x, tile_type in enumerate(row):
                # Una mattonella è calpestabile se NON è un tipo di muro solido
                is_walkable = tile_type not in graphics_config.SOLID_TILE_TYPES
                new_row.append(is_walkable)
            self.walkable_grid.append(new_row)

        # 2. Ora "sovrascrivi" con le posizioni degli oggetti solidi
        for obj in self.objects.values():
            if obj.object_type in graphics_config.SOLID_OBJECT_TYPES:
                if 0 <= obj.logical_y < self.logical_height and 0 <= obj.logical_x < self.logical_width:
                    self.walkable_grid[obj.logical_y][obj.logical_x] = False