from core.world.location import Location
from core.world.game_object import GameObject
from core.enums import LocationType, ObjectType, TileType

# Definiamo delle scorciatoie
CF = TileType.FLOOR_CAFE
WE = TileType.WALL_EXTERNAL
_  = TileType.EMPTY
D  = TileType.DOORWAY

# Mappa dei pavimenti per il caffè
cafe_floor_map = [
    [CF, CF, CF, CF, CF, CF, CF, CF],
    [CF, CF, CF, CF, CF, CF, CF, CF],
    [CF, CF, CF, CF, CF, CF, CF, CF],
    [CF, CF, CF, CF, CF, CF, CF, CF],
    [CF, CF, CF, CF, CF, CF, CF, CF],
    [CF, CF, CF, CF, CF, CF, CF, CF],
]

# Mappa dei muri e delle porte
cafe_wall_map = [
    [WE, WE, WE, WE, WE, WE, WE, WE],
    [WE, _,  _,  _,  _,  _,  _,  WE],
    [WE, _,  _,  _,  _,  _,  _,  WE],
    [WE, _,  _,  _,  _,  _,  _,  WE],
    [WE, _,  _,  _,  _,  _,  _,  WE],
    [WE, WE, D,  D,  WE, WE, WE, WE],
]

# Oggetti nel caffè
cafe_objects = {
    "obj_muse_cafe_counter": GameObject(object_id="obj_muse_cafe_counter", name="Bancone Caffè", object_type=ObjectType.BAR_COUNTER, logical_x=1, logical_y=1),
    "obj_muse_cafe_jukebox": GameObject(object_id="obj_muse_cafe_jukebox_01", name="Jukebox Classico", object_type=ObjectType.JUKEBOX, logical_x=6, logical_y=4)
}

# Creazione dell'istanza della Location con la firma corretta
muse_cafe = Location(
    location_id="loc_muse_cafe_01",
    name="Caffè delle Muse",
    location_type=LocationType.CAFE,
    logical_width=len(cafe_floor_map[0]),
    logical_height=len(cafe_floor_map),
    floor_map=cafe_floor_map,
    wall_map=cafe_wall_map,
    objects=cafe_objects
)

# La lista che viene esportata e usata dalla simulazione
district_locations = [
    muse_cafe,
]