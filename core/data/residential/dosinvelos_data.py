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

dosinvelos_fridge = GameObject(object_id="obj_dosinvelos_fridge", name="Frigo Anni '90", object_type=ObjectType.REFRIGERATOR, style="dark-wood", logical_x=1, logical_y=1)
dosinvelos_bed_erika = GameObject(object_id="obj_dosinvelos_bed_erika", name="Letto di Erika", object_type=ObjectType.BED, style="dark-wood", logical_x=1, logical_y=6)
dosinvelos_bed_max = GameObject(object_id="obj_dosinvelos_bed_max", name="Letto di Max", object_type=ObjectType.BED, style="dark-wood", logical_x=4, logical_y=6)
dosinvelos_computer = GameObject(object_id="obj_dosinvelos_computer", name="PC Assemblato", object_type=ObjectType.COMPUTER, style="dark-wood", logical_x=1, logical_y=2)
dosinvelos_bookshelf = GameObject(object_id="obj_dosinvelos_bookshelf", name="Libreria Caotica", object_type=ObjectType.BOOKSHELF, style="dark-wood", logical_x=3, logical_y=1)
dosinvelos_toilet = GameObject(object_id="obj_dosinvelos_toilet", name="WC", object_type=ObjectType.TOILET, style="dark-wood", logical_x=11, logical_y=1)
dosinvelos_sink = GameObject(object_id="obj_dosinvelos_sink", name="Lavandino", object_type=ObjectType.SINK, style="dark-wood", logical_x=13, logical_y=1)

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
loc_dosinvelos.objects = {
    dosinvelos_fridge.object_id: dosinvelos_fridge,
    dosinvelos_bed_erika.object_id: dosinvelos_bed_erika,
    dosinvelos_bed_max.object_id: dosinvelos_bed_max,
    dosinvelos_computer.object_id: dosinvelos_computer,
    dosinvelos_bookshelf.object_id: dosinvelos_bookshelf,
    dosinvelos_toilet.object_id: dosinvelos_toilet,
    dosinvelos_sink.object_id: dosinvelos_sink,
}


# --- LISTA DI ESPORTAZIONE ---
district_locations = [
    loc_dosinvelos,
]
