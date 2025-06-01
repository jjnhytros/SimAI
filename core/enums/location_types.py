# core/enums/location_types.py
from enum import Enum, auto

class LocationType(Enum):
    # Tipi Residenziali
    RESIDENTIAL_HOME = auto()          # Una casa/appartamento generico
    RESIDENTIAL_LIVING_ROOM = auto()   # Soggiorno
    RESIDENTIAL_KITCHEN = auto()       # Cucina
    RESIDENTIAL_BEDROOM = auto()       # Camera da letto
    RESIDENTIAL_BATHROOM = auto()      # Bagno
    RESIDENTIAL_DINING_ROOM = auto()   # Sala da pranzo
    RESIDENTIAL_STUDY_OFFICE = auto()  # Studio / Ufficio in casa
    RESIDENTIAL_GARDEN = auto()        # Giardino privato
    RESIDENTIAL_BALCONY = auto()       # Balcone
    RESIDENTIAL_BASEMENT = auto()      # Cantina / Seminterrato
    RESIDENTIAL_ATTIC = auto()         # Soffitta
    RESIDENTIAL_GARAGE = auto()        # Garage

    # Tipi Comunitari / Commerciali
    COMMUNITY_LOT_PARK = auto()        # Parco pubblico
    COMMUNITY_LOT_LIBRARY = auto()     # Biblioteca (ex LIBRARY)
    COMMUNITY_LOT_MUSEUM = auto()      # Museo (ex MUSEUM)
    COMMUNITY_LOT_GYM = auto()         # Palestra
    COMMUNITY_LOT_RESTAURANT = auto()  # Ristorante
    COMMUNITY_LOT_CAFE_BAR = auto()    # Caffè / Bar
    COMMUNITY_LOT_SHOP_GENERAL = auto()# Negozio generico
    COMMUNITY_LOT_SHOP_CLOTHING = auto()# Negozio di abbigliamento
    COMMUNITY_LOT_SHOP_BOOKS = auto()  # Libreria (negozio)
    COMMUNITY_LOT_CINEMA = auto()      # Cinema
    COMMUNITY_LOT_NIGHTCLUB = auto()   # Locale notturno
    COMMUNITY_LOT_POOL = auto()        # Piscina pubblica
    COMMUNITY_LOT_BEACH = auto()       # Spiaggia

    # Luoghi di Lavoro / Educazione (esempi)
    WORKPLACE_OFFICE = auto()
    WORKPLACE_LABORATORY = auto()
    WORKPLACE_HOSPITAL = auto()
    WORKPLACE_RETAIL = auto() # Generico per negozi
    SCHOOL_PRIMARY = auto()
    SCHOOL_SECONDARY = auto()
    UNIVERSITY_CAMPUS = auto()
    UNIVERSITY_CLASSROOM = auto()
    UNIVERSITY_LIBRARY = auto() # Biblioteca universitaria, diversa da quella pubblica

    # Luoghi Esterni / Naturali (oltre ai parchi)
    FOREST = auto()
    MOUNTAIN_TRAIL = auto()
    RIVERBANK = auto()
    LAKE_SHORE = auto()

    # Altro
    STREET = auto()
    PUBLIC_TRANSPORT_STOP = auto()
    UNKNOWN_LOCATION = auto() # Tipo sconosciuto o non specificato

    def display_name_it(self) -> str:
        # Crea un mapping per i nomi italiani se vuoi essere più preciso
        # Altrimenti, una formattazione generica può bastare per iniziare
        name_map = {
            LocationType.RESIDENTIAL_LIVING_ROOM: "Soggiorno (Residenziale)",
            LocationType.RESIDENTIAL_KITCHEN: "Cucina (Residenziale)",
            LocationType.RESIDENTIAL_BEDROOM: "Camera da Letto (Residenziale)",
            LocationType.RESIDENTIAL_BATHROOM: "Bagno (Residenziale)",
            LocationType.COMMUNITY_LOT_LIBRARY: "Biblioteca Comunitaria",
            LocationType.COMMUNITY_LOT_MUSEUM: "Museo Comunitario",
            # ... aggiungi altri se necessario ...
        }
        default_name = self.name.replace("_", " ").title()
        return name_map.get(self, default_name)