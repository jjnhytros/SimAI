# core/data/districts/muse_quarter_data.py
from core.world.location import Location
from core.world.game_object import GameObject
from core.enums import LocationType, ObjectType, TileType

# --- Pianta e Oggetti per "Caffè delle Muse" ---
cafe_layout = [
    [TileType.WALL, TileType.WALL, TileType.WALL, TileType.WALL, TileType.WALL],
    [TileType.WALL, TileType.FLOOR_WOOD, TileType.FLOOR_WOOD, TileType.FLOOR_WOOD, TileType.WALL],
    [TileType.WALL, TileType.FLOOR_WOOD, TileType.FLOOR_WOOD, TileType.FLOOR_WOOD, TileType.WALL],
    [TileType.WALL, TileType.WALL, TileType.DOORWAY, TileType.WALL, TileType.WALL],
]
cafe_toilet = GameObject(object_id="obj_muse_cafe_toilet_01", name="WC del Caffè", object_type=ObjectType.TOILET, style="interior", logical_x=4, logical_y=1)

muse_cafe = Location(
    location_id="loc_muse_cafe_01",
    name="Caffè delle Muse",
    location_type=LocationType.CAFE,
    style="floors",
    logical_width=len(cafe_layout[0]),
    logical_height=len(cafe_layout),
    tile_map=cafe_layout # <-- Passa la pianta
)
muse_cafe.objects = {
    # ... (gli altri oggetti)
    cafe_toilet.object_id: cafe_toilet, # <-- Aggiungi il WC agli oggetti del caffè
}

# --- Pianta e Oggetti per "Museo d'Arte di Anthalys" ---
museum_layout = [
    [TileType.WALL, TileType.WALL, TileType.DOORWAY, TileType.WALL, TileType.WALL],
    [TileType.WALL, TileType.FLOOR_WOOD, TileType.FLOOR_WOOD, TileType.FLOOR_WOOD, TileType.WALL],
    [TileType.WALL, TileType.FLOOR_WOOD, TileType.FLOOR_WOOD, TileType.FLOOR_WOOD, TileType.WALL],
    [TileType.WALL, TileType.WALL, TileType.WALL, TileType.WALL, TileType.WALL],
]
muse_museum = Location(
    location_id="loc_muse_museum_01",
    name="Museo d'Arte di Anthalys",
    location_type=LocationType.MUSEUM,
    style="floors",
    logical_width=len(museum_layout[0]),
    logical_height=len(museum_layout),
    tile_map=museum_layout # <-- Passa la pianta
)

# --- Pianta e Oggetti per "Jazz Club" ---
jazz_club_layout = [
    [TileType.WALL, TileType.WALL, TileType.WALL, TileType.WALL, TileType.DOORWAY, TileType.WALL, TileType.WALL],
    [TileType.WALL, TileType.FLOOR_WOOD, TileType.FLOOR_WOOD, TileType.FLOOR_WOOD, TileType.FLOOR_WOOD, TileType.FLOOR_WOOD, TileType.WALL],
    [TileType.WALL, TileType.FLOOR_WOOD, TileType.FLOOR_WOOD, TileType.FLOOR_WOOD, TileType.FLOOR_WOOD, TileType.FLOOR_WOOD, TileType.WALL],
    [TileType.WALL, TileType.WALL, TileType.WALL, TileType.WALL, TileType.WALL, TileType.WALL, TileType.WALL],
]
muse_jazz_club = Location(
    location_id="loc_muse_jazz_club_01",
    name="Blue Note di Anthalys",
    location_type=LocationType.JAZZ_CLUB,
    style="floors",
    logical_width=len(jazz_club_layout[0]),
    logical_height=len(jazz_club_layout),
    tile_map=jazz_club_layout # <-- Passa la pianta
)

# --- LISTA DI ESPORTAZIONE ---
district_locations = [
    muse_cafe,
    muse_museum,
    muse_jazz_club,
]