# core/data/residential/dosinvelos_data.py
from core.world.location import Location
from core.world.game_object import GameObject
from core.enums import LocationType, ObjectType
from core.enums import TileType, LocationType

# Definiamo delle scorciatoie per leggibilità
LV = TileType.FLOOR_LIVING_ROOM # Living Room
BD = TileType.FLOOR_BEDROOM     # Bedroom
BT = TileType.FLOOR_BATHROOM    # Bathroom
WI = TileType.WALL_INTERNAL     # Wall Internal
WE = TileType.WALL_EXTERNAL     # Wall External (casuale)
D = TileType.DOORWAY
P = TileType.DOOR_MAIN_ENTRANCE

# Disegniamo una pianta più grande, ad esempio 15x12
# Questo layout rappresenta un piccolo appartamento con un soggiorno,
# una camera da letto e un bagno.
dosinvelos_layout = [
    [WE, WE, WE, WE, WE, WE, WE, WE, WE, WE, WE, WE, WE, WE, WE],
    [WE, LV, LV, LV, LV, LV, WI, LV, WI, BT, BT, BT, BT, BT, WE],
    [WE, LV, LV, LV, LV, LV, LV, LV, BT, BT, BT, BT, BT, BT, WE],
    [WE, LV, LV, LV, LV, LV, WI, LV, WI, BT, BT, BT, BT, BT, WE],
    [WE, LV, LV, LV, LV, LV, WI, LV, WI, BT, BT, BT, BT, BT, WE],
    [WE, WI, WI, WI, WI, WI, WI, LV, WI, WI, WI, WI, WI, WI, WE],
    [WE, BD, BD, BD, BD, BD, BD, LV, LV, LV, LV, LV, LV, LV, WE],
    [WE, BD, BD, BD, BD, BD, WI, LV, LV, LV, LV, LV, LV, LV, WE],
    [WE, BD, BD, BD, BD, BD, WI, LV, LV, LV, LV, LV, LV, LV, WE],
    [WE, BD, BD, BD, BD, BD, WI, LV, LV, LV, LV, LV, LV, LV, WE],
    [WE, BD, BD, BD, BD, BD, WI, LV, LV, LV, LV, LV, LV, LV, WE],
    [WE, WE, WE, WE, WE, WE, WE, LV, WE, WE, WE, WE, WE, WE, WE],
]

# 1. Crea l'istanza della Location senza passare la tile_map nel costruttore
loc_dosinvelos = Location(
    location_id="loc_dosinvelos_apt_01",
    name="Appartamento Dosinvelos",
    location_type=LocationType.RESIDENTIAL_APARTMENT,
    style="floors", # Lo stile per le mattonelle
    logical_width=len(dosinvelos_layout[0]),
    logical_height=len(dosinvelos_layout),
    tile_map=dosinvelos_layout # <-- La mappa ora è un parametro
)

# 2. Assegna la pianta all'attributo .tile_map dopo la creazione
# loc_dosinvelos.tile_map = dosinvelos_layout

district_locations = [
    loc_dosinvelos,
]

# Aggiungi anche gli oggetti, se ne hai
# loc_dosinvelos.objects = { ... }

