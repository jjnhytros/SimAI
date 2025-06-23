from core.world.location import Location
from core.world.game_object import GameObject
from core.enums import LocationType, ObjectType, TileType

# Definiamo delle scorciatoie per leggibilità della mappa
LV = TileType.FLOOR_LIVING_ROOM
BD = TileType.FLOOR_BEDROOM
BT = TileType.FLOOR_BATHROOM
WE = TileType.WALL_EXTERNAL
WI = TileType.WALL_INTERNAL
D  = TileType.DOORWAY
P  = TileType.DOOR_MAIN_ENTRANCE
_  = TileType.EMPTY # Spazio vuoto, nessuna mattonella di muro

# --- STRUTTURA A STRATI DELL'APPARTAMENTO ---

# 1. Mappa dei PAVIMENTI
dosinvelos_floor_map = [
    # Colonna: 0   1   2   3   4   5   6   7   8   9   10  11  12  13  14
    [LV, LV, LV, LV, LV, LV, LV, LV, LV, BT, BT, BT, BT, BT, LV], # Riga 0
    [LV, LV, LV, LV, LV, LV, LV, LV, LV, BT, BT, BT, BT, BT, LV], # Riga 1
    [LV, LV, LV, LV, LV, LV, LV, LV, LV, BT, BT, BT, BT, BT, LV], # Riga 2
    [LV, LV, LV, LV, LV, LV, LV, LV, LV, BT, BT, BT, BT, BT, LV], # Riga 3
    [LV, LV, LV, LV, LV, LV, LV, LV, LV, BT, BT, BT, BT, BT, LV], # Riga 4
    [BD, BD, BD, BD, BD, BD, LV, LV, LV, LV, LV, LV, LV, LV, LV], # Riga 5
    [BD, BD, BD, BD, BD, BD, LV, LV, LV, LV, LV, LV, LV, LV, LV], # Riga 6
    [BD, BD, BD, BD, BD, BD, LV, LV, LV, LV, LV, LV, LV, LV, LV], # Riga 7
    [BD, BD, BD, BD, BD, BD, LV, LV, LV, LV, LV, LV, LV, LV, LV], # Riga 8
    [BD, BD, BD, BD, BD, BD, LV, LV, LV, LV, LV, LV, LV, LV, LV], # Riga 9
    [BD, BD, BD, BD, BD, BD, LV, LV, LV, LV, LV, LV, LV, LV, LV], # Riga 10
    [LV, LV, LV, LV, LV, LV, LV, LV, LV, LV, LV, LV, LV, LV, LV], # Riga 11
]

# 2. Mappa dei MURI e delle PORTE
dosinvelos_wall_map = [
    # Colonna: 0   1   2   3   4   5   6   7   8   9   10  11  12  13  14
    [WE, WE, WE, WE, WE, WE, WE, WE, WE, WE, WE, WE, WE, WE, WE], # Riga 0
    [WE, _,  _,  _,  _,  _,  WI, _,  WI, _,  _,  _,  _,  _,  WE], # Riga 1
    [WE, _,  _,  _,  _,  _,  _,  _,  _,  _,  _,  _,  _,  _,  WE], # Riga 2
    [WE, _,  _,  _,  _,  _,  WI, _,  WI, _,  _,  _,  _,  _,  WE], # Riga 3
    [WE, _,  _,  _,  _,  _,  WI, _,  D,  _,  _,  _,  _,  _,  WE], # Riga 4 (Porta bagno)
    [WE, WI, WI, WI, WI, D,  WI, _,  WI, WI, WI, WI, WI, WI, WE], # Riga 5 (Porta camera)
    [WE, _,  _,  _,  _,  _,  WI, _,  _,  _,  _,  _,  _,  _,  WE], # Riga 6
    [WE, _,  _,  _,  _,  _,  WI, _,  _,  _,  _,  _,  _,  _,  WE], # Riga 7
    [WE, _,  _,  _,  _,  _,  D,  _,  _,  _,  _,  _,  _,  _,  WE], # Riga 8 (Altra porta camera?)
    [WE, _,  _,  _,  _,  _,  WI, _,  _,  _,  _,  _,  _,  _,  WE], # Riga 9
    [WE, _,  _,  _,  _,  _,  WI, _,  _,  _,  _,  _,  _,  _,  WE], # Riga 10
    [WE, WE, WE, WE, D,  WE, WE, _,  WE, WE, WE, WE, WE, P,  WE], # Riga 11 (Porta principale)
]

# 3. Definizione degli OGGETTI con le loro coordinate logiche
dosinvelos_objects = {
    "obj_dosinvelos_fridge": GameObject(object_id="obj_dosinvelos_fridge", name="Frigo Anni '90", object_type=ObjectType.REFRIGERATOR, style="dark-wood", logical_x=1, logical_y=1),
    "obj_dosinvelos_bed_erika": GameObject(object_id="obj_dosinvelos_bed_erika", name="Letto di Erika", object_type=ObjectType.BED, style="dark-wood", logical_x=1, logical_y=6),
    "obj_dosinvelos_bed_max": GameObject(object_id="obj_dosinvelos_bed_max", name="Letto di Max", object_type=ObjectType.BED, style="dark-wood", logical_x=4, logical_y=6),
    "obj_dosinvelos_computer": GameObject(object_id="obj_dosinvelos_computer", name="PC Assemblato", object_type=ObjectType.COMPUTER, style="dark-wood", logical_x=1, logical_y=2),
    "obj_dosinvelos_bookshelf": GameObject(object_id="obj_dosinvelos_bookshelf", name="Libreria Caotica", object_type=ObjectType.BOOKSHELF, style="dark-wood", logical_x=3, logical_y=1),
    "obj_dosinvelos_toilet": GameObject(object_id="obj_dosinvelos_toilet", name="WC", object_type=ObjectType.TOILET, style="dark-wood", logical_x=11, logical_y=1),
    "obj_dosinvelos_sink": GameObject(object_id="obj_dosinvelos_sink", name="Lavandino", object_type=ObjectType.SINK, style="dark-wood", logical_x=13, logical_y=1),
    "obj_dosinvelos_sofa": GameObject(object_id="obj_dosinvelos_sofa_01", name="Divano Comodo", object_type=ObjectType.SOFA, style="dark-wood", logical_x=1, logical_y=10),
    "obj_dosinvelos_coffee_table": GameObject(object_id="obj_dosinvelos_coffee_table_01", name="Tavolino da Caffè", object_type=ObjectType.COFFEE_TABLE, style="dark-wood", logical_x=3, logical_y=10),
    "obj_dosinvelos_dining_table": GameObject(object_id="obj_dosinvelos_dining_table_01", name="Tavolo da Pranzo", object_type=ObjectType.DINING_TABLE, style="dark-wood", logical_x=12, logical_y=8),
    "obj_dosinvelos_chair1": GameObject(object_id="obj_dosinvelos_chair_01", name="Sedia", object_type=ObjectType.DINING_CHAIR, style="dark-wood", logical_x=11, logical_y=8),
    "obj_dosinvelos_chair2": GameObject(object_id="obj_dosinvelos_chair_02", name="Sedia", object_type=ObjectType.DINING_CHAIR, style="dark-wood", logical_x=13, logical_y=8),
}


# 4. Creazione dell'istanza della Location con la nuova firma
loc_dosinvelos = Location(
    location_id="loc_dosinvelos_apt_01",
    name="Appartamento Dosinvelos",
    location_type=LocationType.RESIDENTIAL_APARTMENT,
    logical_width=len(dosinvelos_floor_map[0]),
    logical_height=len(dosinvelos_floor_map),
    floor_map=dosinvelos_floor_map,
    wall_map=dosinvelos_wall_map,
    objects=dosinvelos_objects
)


# --- LISTA DI ESPORTAZIONE ---
# Questa è la lista che viene importata da simulation.py
district_locations = [
    loc_dosinvelos,
]