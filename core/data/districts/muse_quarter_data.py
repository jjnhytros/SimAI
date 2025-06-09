# core/data/districts/muse_quarter_data.py
"""
Definizione delle location e degli oggetti specifici per il Quartiere delle Muse.
"""
from core.world.location import Location
from core.world.game_object import GameObject
from core.enums import LocationType, ObjectType

# --- DEFINIZIONE OGGETTI PER "CAFFÈ DELLE MUSE" ---
cafe_coffee_machine = GameObject(
    object_id="obj_muse_cafe_coffeemachine_01",
    name="Macchina da Caffè 'La Poetica'",
    object_type=ObjectType.COFFEE_MACHINE,
    logical_x=1,
    logical_y=5
)
cafe_table_1 = GameObject(
    object_id="obj_muse_cafe_table_01",
    name="Tavolino da Caffè",
    object_type=ObjectType.TABLE,
    logical_x=3,
    logical_y=3
)
cafe_chair_1 = GameObject(object_id="obj_muse_cafe_chair_01", name="Sedia in Legno", object_type=ObjectType.CHAIR, logical_x=2, logical_y=3)
cafe_chair_2 = GameObject(object_id="obj_muse_cafe_chair_02", name="Sedia in Legno", object_type=ObjectType.CHAIR, logical_x=4, logical_y=3)

# --- DEFINIZIONE DELLA LOCATION "CAFFÈ DELLE MUSE" ---
# 1. Prima creiamo l'istanza della Location con i suoi parametri base
muse_cafe = Location(
    location_id="loc_muse_cafe_01",
    name="Caffè delle Muse",
    location_type=LocationType.CAFE,
    logical_width=10,
    logical_height=8,
)

# 2. Poi creiamo e aggiungiamo gli oggetti al suo dizionario .objects
muse_cafe.objects = {
    "obj_muse_cafe_coffeemachine_01": GameObject(
        object_id="obj_muse_cafe_coffeemachine_01",
        name="Macchina da Caffè 'La Poetica'",
        object_type=ObjectType.COFFEE_MACHINE,
        logical_x=1, logical_y=5
    ),
    "obj_muse_cafe_table_01": GameObject(
        object_id="obj_muse_cafe_table_01",
        name="Tavolino da Caffè",
        object_type=ObjectType.TABLE,
        logical_x=3, logical_y=3
    ),
    # ... altri oggetti
}


# ... qui in futuro aggiungeremo le altre location del quartiere, come il Museo ...

# --- LISTA DI ESPORTAZIONE ---
# Esportiamo una lista di tutte le location definite in questo file.
district_locations = [
    muse_cafe,
]