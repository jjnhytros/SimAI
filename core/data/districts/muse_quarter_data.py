# core/data/districts/muse_quarter_data.py
"""
Definizione delle location e degli oggetti specifici per il Quartiere delle Muse.
"""
from core.world.location import Location
from core.world.game_object import GameObject
from core.enums import LocationType, ObjectType

# --- DEFINIZIONE OGGETTI PER IL JAZZ CLUB ---
jazz_stage = GameObject(object_id="obj_muse_jazz_stage_01", name="Palco del Blue Note", object_type=ObjectType.STAGE, logical_x=8, logical_y=2)
jazz_piano = GameObject(object_id="obj_muse_jazz_piano_01", name="Pianoforte a Coda", object_type=ObjectType.PIANO, logical_x=9, logical_y=2)
jazz_mic = GameObject(object_id="obj_muse_jazz_mic_01", name="Microfono Vintage", object_type=ObjectType.MICROPHONE, logical_x=7, logical_y=2)

# --- DEFINIZIONE DELLA LOCATION "JAZZ CLUB" ---
muse_jazz_club = Location(
    location_id="loc_muse_jazz_club_01",
    name="Blue Note di Anthalys",
    location_type=LocationType.JAZZ_CLUB,
    logical_width=15,
    logical_height=12
)
muse_jazz_club.objects = {
    jazz_stage.object_id: jazz_stage,
    jazz_piano.object_id: jazz_piano,
    jazz_mic.object_id: jazz_mic,
    # Aggiungi qui tavolini e sedie per il pubblico...
}

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
muse_cafe = Location(
    location_id="loc_muse_cafe_01",
    name="Caffè delle Muse",
    location_type=LocationType.CAFE,
    logical_width=10,
    logical_height=8
)
# Aggiunta degli oggetti alla location
muse_cafe.objects = {
    cafe_coffee_machine.object_id: cafe_coffee_machine,
    cafe_table_1.object_id: cafe_table_1,
    cafe_chair_1.object_id: cafe_chair_1,
    cafe_chair_2.object_id: cafe_chair_2,
}

# --- DEFINIZIONE OGGETTI PER "MUSEO D'ARTE DI ANTHALYS" ---
art_piece_1 = GameObject(object_id="obj_muse_museum_art_01", name="Installazione 'Eco Riflesso'", object_type=ObjectType.ART_INSTALLATION, logical_x=5, logical_y=5)
art_piece_2 = GameObject(object_id="obj_muse_museum_art_02", name="Scultura 'Il Silenzio'", object_type=ObjectType.SCULPTURE, logical_x=10, logical_y=10)

# --- DEFINIZIONE DELLA LOCATION "MUSEO D'ARTE DI ANTHALYS" ---
muse_museum = Location(
    location_id="loc_muse_museum_01",
    name="Museo d'Arte di Anthalys",
    location_type=LocationType.MUSEUM,
    logical_width=20,
    logical_height=20
)
# Aggiunta degli oggetti alla location
muse_museum.objects = {
    art_piece_1.object_id: art_piece_1,
    art_piece_2.object_id: art_piece_2,
}


# --- LISTA DI ESPORTAZIONE ---
# Esportiamo una lista di tutte le location definite in questo file.
district_locations = [
    muse_cafe,
    muse_museum,
    muse_jazz_club,
]
