# core/enums/tile_types.py
from enum import IntEnum, auto

from enum import IntEnum, auto

class TileType(IntEnum):
    """Definisce i tipi di mattonelle per pavimenti, muri, ecc."""
    EMPTY = 0
    FLOOR_LIVING_ROOM = auto() # Pavimento Soggiorno
    FLOOR_BEDROOM = auto()     # Pavimento Camera
    FLOOR_BATHROOM = auto()    # Pavimento Bagno
    WALL_INTERNAL = auto()     # Muro Interno
    WALL_EXTERNAL = auto()     # Muro Esterno (che sarà casuale)
    DOORWAY = auto()
    DOOR_MAIN_ENTRANCE = auto()
    WALL = auto()
    FLOOR_WOOD = auto()
    FLOOR_CAFE = auto() # Pavimento per il caffè
    FLOOR_GRASS = auto() # Erba per l'esterno