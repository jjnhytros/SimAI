# core/enums/location_types.py
from enum import Enum, auto

class LocationType(Enum):
    """
    Enum per i diversi tipi di locazioni e lotti, raggruppati per distretto concettuale.
    """
    # --- Tipi Generici o Non Assegnati ---
    GENERIC_COMMUNITY_LOT = auto()
    GENERIC_LOT = auto()

    # --- Tipi di Stanze / Micro-Locazioni (Interni) ---
    RESIDENTIAL_BATHROOM = auto()
    RESIDENTIAL_BEDROOM = auto()
    RESIDENTIAL_GARDEN = auto()
    RESIDENTIAL_KITCHEN = auto()
    RESIDENTIAL_LIVING_ROOM = auto()
    RESIDENTIAL_STUDY = auto() # Studio/Ufficio

    # La Cittadella (Distretto 1)
    CENTRAL_BANK_HQ = auto()
    CIVIC_AUDITORIUM = auto()
    COURTHOUSE = auto()
    GOVERNMENT_OFFICE = auto()
    GOVERNOR_PALACE = auto()
    NATIONAL_ARCHIVE = auto()
    PARLIAMENT_BUILDING = auto()

    # Quartiere delle Muse (Distretto 2)
    ANTIQUE_BOOKSTORE = auto()
    ART_GALLERY = auto()
    ART_SUPPLY_STORE = auto()
    CAFE = auto()
    CONCERT_HALL = auto() # Potrebbe essere anche nel distretto Arena
    CONSERVATORY = auto()
    INDEPENDENT_CINEMA = auto()
    JAZZ_CLUB = auto()
    MUSEUM = auto()
    MUSIC_VENUE_SMALL = auto() # Es. Jazz Club
    PUBLIC_LIBRARY = auto()
    THEATER_VENUE = auto()

    # Via Aeterna (Distretto 3)
    BANK_BRANCH = auto()
    CORPORATE_HQ_TOWER = auto()
    DEPARTMENT_STORE = auto()
    FANCY_RESTAURANT = auto()
    LUXURY_SHOP = auto()
    ROOFTOP_BAR = auto()
    STOCK_EXCHANGE = auto()

    # Complesso del Salice Argenteo (Distretto 4)
    BLOOD_DONATION_CENTER = auto()
    CHILDREN_HOSPITAL = auto()
    ENGINEERING_LAB = auto()
    GAO_RESEARCH_INSTITUTE = auto()
    GERIATRIC_HOSPITAL = auto()
    HOSPITAL = auto()
    MENTAL_HEALTH_CLINIC = auto()
    ONCOLOGY_HOSPITAL = auto()
    PHARMACY = auto()
    REHABILITATION_CENTER = auto()
    SCIENCE_LAB = auto()
    UNIVERSITY_BOOKSTORE = auto() # Presente anche nel Distretto 5
    UNIVERSITY_DORMITORY = auto() # Presente anche nel Distretto 5
    UNIVERSITY_LECTURE_HALL = auto() # Presente anche nel Distretto 5
    UNIVERSITY_LIBRARY = auto() # Presente anche nel Distretto 5
    VETERINARY_CLINIC = auto()

    # La Loggia del Sapere (Distretto 5)
    #UNIVERSITY_DORMITORY = auto()
    #UNIVERSITY_LECTURE_HALL = auto()
    #UNIVERSITY_LIBRARY = auto()
    FACULTY_BUILDING = auto()
    PERFORMING_ARTS_STUDIO = auto()
    STUDENT_UNION = auto()
    UNIVERSITY = auto()
    UNIVERSITY_FACULTY_LAW = auto()
    UNIVERSITY_FACULTY_ARTS = auto()
    STUDENT_UNION_BUILDING = auto()
    CAMPUS_CAFE = auto()

    # Porto di Levante (Distretto 6)
    AION_WAREHOUSE = auto()
    CARGO_DOCKS = auto()
    CUSTOMS_OFFICE = auto()
    FACTORY = auto()
    LOGISTICS_HUB = auto()
    SHIPYARD = auto()
    SPECIAL_ECONOMIC_ZONE = auto()
    WORKERS_CANTEEN = auto()
    AION_WAREHOUSE_ACCESS = auto()

    # Giardini Sospesi (Distretto 7)
    AMPHITHEATER = auto()
    BOTANICAL_GARDEN = auto()
    CENTRAL_PARK = auto()
    COMMUNITY_GARDEN = auto()
    DOG_PARK = auto()
    LAKE_CAFE = auto()
    PARK = auto() # Tipo generico, ma il principale è qui
    PLAYGROUND = auto() # Tipo generico, ma il più grande è qui
    SKATE_PARK = auto()
    
    # Borgo Antico (Distretto 8)
    EXCLUSIVE_HEALTH_CLUB = auto()
    GOURMET_FOOD_STORE = auto()
    LUXURY_CONDO = auto()
    PRIVATE_ART_GALLERY = auto()
    RESIDENTIAL_LUXURY_CONDO_SMALL = auto()
    RESIDENTIAL_VILLA = auto()

    # Solara (Distretto 9)
    BIKE_RENTAL_STATION = auto()
    CAR_SHARING_STATION = auto()
    COMMUNITY_HUB = auto()
    ECO_CONDO = auto()
    ECO_HOUSE = auto()
    ORGANIC_CAFE = auto()
    RESIDENTIAL_ECO_CONDO_LARGE = auto()
    RESIDENTIAL_ECO_CONDO_MEDIUM = auto()
    RESIDENTIAL_ECO_HOUSE = auto()
    URBAN_FARM = auto()
    ZERO_WASTE_STORE = auto()

    # Nido del Fiume (Distretto 10)
    APARTMENT_BUILDING = auto()
    COMMUNITY_POOL = auto()
    DAYCARE_CENTER = auto()
    PEDIATRICIAN_OFFICE = auto()
    RESIDENTIAL_APARTMENT_BUILDING_SMALL = auto()
    RESIDENTIAL_HOUSE = auto() # Casa unifamiliare generica
    RESIDENTIAL_TOWNHOUSE = auto() # Villetta a schiera
    SCHOOL = auto() # Tipo generico
    SUPERMARKET = auto() # Tipo generico
    TOWNHOUSE = auto()

    # Crocevia dei Mercanti (Distretto 11)
    ARTISAN_SHOP = auto()
    ETHNIC_RESTAURANT = auto()
    FABRIC_STORE = auto()
    FOOD_STALL = auto()
    HOSTEL = auto()
    OPEN_AIR_MARKET = auto()
    RESIDENTIAL_APT_ABOVE_SHOP = auto() # Generico per sopra i negozi
    SPICE_SHOP = auto()

    # L'Arena (Distretto 12)
    EVENT_HOTEL = auto()
    INDOOR_ARENA = auto()
    LARGE_EVENT_HOTEL = auto()
    SPORTS_BAR = auto()
    SPORTS_MUSEUM = auto()
    STADIUM = auto()
    TEAM_MERCHANDISE_STORE = auto()
    TEAM_STORE = auto()
    TRAINING_FACILITY = auto()

    # Vecchio Castello (Distretto 13)
    ARMORY = auto()
    CASTLE_DUNGEONS = auto()
    CASTLE_GARDENS = auto()
    HISTORICAL_CASTLE = auto()
    ROYAL_APARTMENTS = auto()
    THRONE_ROOM = auto()

    # Il Grande Albero (Distretto 14)
    GREAT_TREE_HILL = auto()

    # Altro
    UNKNOWN_LOCATION = auto() # Tipo sconosciuto o non specificato

    # --- METODI HELPER ---
    @property
    def is_residential(self) -> bool:
        """Restituisce True se è un tipo di lotto residenziale."""
        return self.name.startswith("RESIDENTIAL_") or self in {
            LocationType.UNIVERSITY_DORMITORY, LocationType.HOSTEL
        }

    @property
    def is_workplace(self) -> bool:
        """Restituisce True se è un tipico luogo di lavoro."""
        # Elenca qui i tipi di luoghi che NON sono primariamente luoghi di lavoro.
        non_work_types = {
            LocationType.PARK, 
            LocationType.PLAYGROUND, 
            LocationType.SKATE_PARK,
            LocationType.DOG_PARK,
            LocationType.AMPHITHEATER,
            # STUDENT_UNION_BUILDING è un luogo sociale/ricreativo, non primariamente un lavoro
            LocationType.STUDENT_UNION_BUILDING,
        }
        # Un luogo di lavoro è un luogo che non è residenziale e non è nella lista di esclusione.
        return not self.is_residential and self not in non_work_types

    @property
    def is_commercial(self) -> bool:
        """Restituisce True se è un tipo di lotto commerciale/negozio."""
        return self in {
            LocationType.DEPARTMENT_STORE, LocationType.LUXURY_SHOP,
            LocationType.SUPERMARKET, LocationType.ARTISAN_SHOP,
            LocationType.GOURMET_FOOD_STORE, LocationType.ZERO_WASTE_STORE,
            LocationType.FOOD_STALL, LocationType.SPICE_SHOP, 
            LocationType.FABRIC_STORE, LocationType.TEAM_MERCHANDISE_STORE,
            LocationType.ANTIQUE_BOOKSTORE, LocationType.UNIVERSITY_BOOKSTORE,
            LocationType.CAFE, LocationType.CAMPUS_CAFE, LocationType.LAKE_CAFE, # Aggiunti i caffè
            LocationType.FANCY_RESTAURANT, LocationType.ETHNIC_RESTAURANT,
            LocationType.SPORTS_BAR, LocationType.ROOFTOP_BAR,
        }

    # Aggiungere altri helper se necessario, es:
    # @property
    # def is_outdoors(self) -> bool: ...
    # @property
    # def is_educational(self) -> bool: ...

    def display_name_it(self) -> str:
        """Restituisce un nome leggibile in italiano per il tipo di locazione."""
        return self.name.replace("_", " ").title()
