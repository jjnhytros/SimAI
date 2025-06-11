# core/data/residential/dosinvelos_data.py
from core.world.location import Location
from core.world.game_object import GameObject
from core.enums import LocationType, ObjectType

# Oggetti per l'appartamento
dosinvelos_fridge = GameObject(object_id="obj_dosinvelos_fridge", name="Frigo Anni '90", object_type=ObjectType.REFRIGERATOR, logical_x=1, logical_y=1)
dosinvelos_bed_erika = GameObject(object_id="obj_dosinvelos_bed_erika", name="Letto di Erika", object_type=ObjectType.BED, logical_x=8, logical_y=2)
dosinvelos_bed_max = GameObject(object_id="obj_dosinvelos_bed_max", name="Letto di Max", object_type=ObjectType.BED, logical_x=8, logical_y=6)
dosinvelos_computer = GameObject(object_id="obj_dosinvelos_computer", name="PC Assemblato", object_type=ObjectType.COMPUTER, logical_x=2, logical_y=8)
dosinvelos_bookshelf = GameObject(object_id="obj_dosinvelos_bookshelf", name="Libreria Caotica", object_type=ObjectType.BOOKSHELF, logical_x=1, logical_y=8)

# La Location
loc_dosinvelos = Location(
    location_id="loc_dosinvelos_apt_01",
    name="Appartamento Dosinvelos",
    location_type=LocationType.RESIDENTIAL_APARTMENT, # Da aggiungere a LocationType
    logical_width=10, logical_height=10
)
loc_dosinvelos.objects = {
    dosinvelos_fridge.object_id: dosinvelos_fridge,
    dosinvelos_bed_erika.object_id: dosinvelos_bed_erika,
    dosinvelos_bed_max.object_id: dosinvelos_bed_max,
    dosinvelos_computer.object_id: dosinvelos_computer,
    dosinvelos_bookshelf.object_id: dosinvelos_bookshelf,
}

district_locations = [loc_dosinvelos]