from core.enums import LocationType, TileType, ObjectType

# Definiamo le chiavi per gli spritesheet
SHEET_FLOORS = "floors"
SHEET_DOORS = "doors-1"
SHEET_DARK_WOOD = "dark-wood"

SPRITE_DEFINITIONS = {
    # Usiamo dark-wood per gli oggetti
    SHEET_DARK_WOOD: {
        ObjectType.BED: {'rect': (0, 320, 64, 96)},     # ESEMPIO
        ObjectType.TABLE: {'rect': (192, 224, 64, 64)}, # ESEMPIO
        ObjectType.BOOKSHELF: {'rect': (512, 128, 64, 96)}, # ESEMPIO
        # ... Aggiungi qui gli altri oggetti da dark-wood.png
    }
}

TILE_DEFINITIONS = {
    SHEET_FLOORS: {
        TileType.FLOOR_LIVING_ROOM: {'rect': (352, 1376, 32, 32)},
        TileType.FLOOR_BEDROOM: {'rect': (192, 1632, 32, 32)},
        TileType.FLOOR_BATHROOM: {'rect': (128, 1696, 32, 32)},

        # --- AGGIUNTE MANCANTI (COORDINATE DA TROVARE) ---
        TileType.WALL: {'rect': (0, 0, 32, 32)},       # <-- ESEMPIO DA CAMBIARE!
        TileType.DOORWAY: {'rect': (32, 0, 32, 32)},   # <-- ESEMPIO DA CAMBIARE!
    },
    SHEET_DOORS: {
        TileType.DOOR_MAIN_ENTRANCE: {'rect': (32, 288, 32, 48)},
    }
}

# --- LOGICA DI SOLIDITÀ SEPARATA ---

# Lista dei TIPI DI MATTONELLA che sono intrinsecamente solidi
SOLID_TILE_TYPES = {
    TileType.WALL,
    # Aggiungi qui altri tipi di muro se necessario
}

# Lista dei TIPI DI OGGETTO che bloccano il movimento
SOLID_OBJECT_TYPES = {
    ObjectType.BED,
    ObjectType.TABLE,
    ObjectType.BOOKSHELF,
    ObjectType.REFRIGERATOR,
    ObjectType.FIREPLACE,
}


# Questa parte rimane, ma punta solo allo stile dei pavimenti
DEFAULT_TILES_BY_LOCATION = {
    "default": {
        "floor": TileType.FLOOR_LIVING_ROOM,
        "style": SHEET_FLOORS
    }
}