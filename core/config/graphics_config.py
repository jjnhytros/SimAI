from core.enums import LocationType, TileType
from core.enums.object_types import ObjectType

# Definiamo la chiave per il nostro unico spritesheet attivo
SHEET_FLOORS = "floors" # Corrisponde a floors.png
SHEET_DOORS = "doors-1"
SHEET_DARK_WOOD = "dark-wood"

# Rimuoviamo SPRITE_DEFINITIONS per ora, dato che non gestiamo oggetti

SPRITE_DEFINITIONS = {
    # Per ora, diciamo che gli oggetti usano lo stile "dark-wood"
    SHEET_DARK_WOOD: {
        # ATTENZIONE: Queste sono coordinate di ESEMPIO.
        # Dovrai trovare quelle corrette nel tuo file dark-wood.png
        ObjectType.BED: {'rect': (0, 320, 64, 96)},
        ObjectType.TABLE: {'rect': (192, 224, 64, 64)},
        ObjectType.BOOKSHELF: {'rect': (512, 128, 64, 96)},
        # ...
    }
}

TILE_DEFINITIONS = {
    SHEET_FLOORS: {
        # Pavimenti specifici con le coordinate che hai fornito
        TileType.FLOOR_BATHROOM: {'rect': (128, 1696, 32, 32)},
        TileType.FLOOR_BEDROOM: {'rect': (192, 1632, 32, 32)},
        # Manteniamo il vecchio come pavimento del soggiorno
        TileType.FLOOR_LIVING_ROOM: {'rect': (352, 1376, 32, 32)},

        # Muri specifici
        TileType.WALL_INTERNAL: {'rect': (224, 1632, 32, 32)},

        # --- NUOVA LOGICA: MURO CASUALE ---
        # Per il muro esterno, definiamo una LISTA di possibili rettangoli
        TileType.WALL_EXTERNAL: [
            {'rect': (0, 1952, 32, 32)},
            {'rect': (224, 2016, 32, 32)},
        ]
    },
    SHEET_DOORS: {
        TileType.DOOR_MAIN_ENTRANCE: {'rect': (32, 288, 32, 48)},
    }
}

SOLID_TILE_TYPES = {
    TileType.WALL,
    TileType.WALL_INTERNAL,
    TileType.WALL_EXTERNAL,
    ObjectType.TABLE,
    ObjectType.BOOKSHELF,
    # TileType.WALL_TOP,
    # TileType.WALL_SIDE_LEFT,
    # TileType.WALL_SIDE_RIGHT,
    # TileType.WALL_BOTTOM,
    # TileType.WALL_CORNER_TOP_LEFT,
    # TileType.WALL_CORNER_TOP_RIGHT,
    # TileType.WALL_CORNER_BOTTOM_LEFT,
    # TileType.WALL_CORNER_BOTTOM_RIGHT,
    # TileType.WALL_INNER_CORNER_BOTTOM_RIGHT,
    # TileType.WALL_INNER_CORNER_BOTTOM_LEFT,
    # TileType.WALL_INNER_CORNER_TOP_RIGHT,
    # TileType.WALL_INNER_CORNER_TOP_LEFT,
    # In futuro, potremmo aggiungere qui anche oggetti grandi come ObjectType.REFRIGERATOR
}

# Questa parte rimane, ma punta solo allo stile dei pavimenti
DEFAULT_TILES_BY_LOCATION = {
    "default": {
        "floor": TileType.FLOOR_LIVING_ROOM,
        "style": SHEET_FLOORS
    }
}