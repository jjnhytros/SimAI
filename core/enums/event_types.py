# core/enums/event_types.py
from enum import Enum, auto
"""
Definizione dell'Enum EventType per gli eventi speciali che accadono nel mondo di SimAI.
Contiene sia eventi specifici/nominati sia categorie di eventi generici.
"""

class EventType(Enum):
    """Enum per i diversi tipi di eventi, raggruppati per categoria."""
    
    # --- Categoria: Tipi di Evento Generici / Ricorrenti ---
    WEEKLY_MEETING = auto()         # Incontro Settimanale (es. Club del Libro)
    ART_EXHIBITION = auto()         # Esposizione d'Arte generica
    EVENING_COURSE = auto()         # Corso Serale generico
    WEEKEND_GROUP_ACTIVITY = auto() # Attività di Gruppo nel Weekend (es. Escursioni)
    FIXED_VENUE_FREE_ACTIVITY = auto() # Luogo Fisso con Attività Libera (es. Area Scacchi)
    LIVE_CONCERT = auto()           # Concerto dal Vivo generico
    LOCAL_MARKET_DAY = auto()       # Giorno di Mercato Locale generico
    VOLUNTEERING_OPPORTUNITY = auto() # Opportunità di Volontariato
    SPORTS_PRACTICE_MATCH = auto()  # Allenamento o Partita Sportiva amatoriale
    WORKSHOP = auto()               # Laboratorio / Workshop pratico generico
    SEMINAR_LECTURE = auto()        # Seminario / Lezione generica
    COMMUNITY_GATHERING = auto()    # Raduno Comunitario generico
    FESTIVAL = auto()               # Festival / Sagra generica

    # --- Categoria: Eventi Personali Specifici (Generati dagli NPC) ---
    BIRTHDAY_PARTY = auto()
    WEDDING = auto()
    FUNERAL = auto()
    HOUSE_PARTY = auto()
    DORM_PARTY = auto()
    NEIGHBORHOOD_BBQ = auto()

    # --- Categoria: Eventi Civici / Governativi Specifici ---
    FOUNDATION_DAY_CEREMONY = auto()
    GOVERNOR_SPEECH = auto()
    ELECTION_DAY = auto()

    # --- Categoria: Eventi Culturali Specifici ---
    INDEPENDENT_FILM_FESTIVAL = auto()
    POETRY_SLAM = auto()
    THEATER_PREMIERE = auto()

    # --- Categoria: Eventi Commerciali Specifici ---
    PRODUCT_LAUNCH = auto()
    FASHION_WEEK = auto()
    SEASONAL_SALE = auto()

    # --- Categoria: Eventi Sportivi Specifici ---
    ARENA_FUSION_MATCH = auto()
    ARENA_FUSION_FINAL = auto()
    MAJOR_CONCERT = auto() # Mega-concerto allo stadio

    # --- Categoria: Eventi Comunitari Specifici ---
    SPRING_FLOWER_FESTIVAL = auto() # Festival dei Fiori di Primavera
    REPAIR_CAFE = auto()            # Evento specifico di tipo WORKSHOP
    CHARITY_RUN = auto()            # Corsa di beneficenza

    # --- Categoria: Eventi Accademici Specifici ---
    ACADEMIC_CONFERENCE = auto()
    GRADUATION_CEREMONY = auto()
    EXAM_PERIOD = auto()

    # --- Categoria: Eventi Rari / Emergenze ---
    INDUSTRIAL_ACCIDENT = auto()
    DISEASE_OUTBREAK = auto()
    POWER_OUTAGE = auto()
    
    def display_name_it(self) -> str:
        """Restituisce un nome leggibile in italiano per il tipo di evento."""
        mapping = {
            # Generici
            EventType.WEEKLY_MEETING: "Incontro Settimanale",
            EventType.ART_EXHIBITION: "Esposizione d'Arte",
            EventType.EVENING_COURSE: "Corso Serale",
            EventType.WEEKEND_GROUP_ACTIVITY: "Attività di Gruppo (Weekend)",
            EventType.FIXED_VENUE_FREE_ACTIVITY: "Attività Libera",
            EventType.LIVE_CONCERT: "Concerto dal Vivo",
            EventType.LOCAL_MARKET_DAY: "Mercato Locale",
            EventType.VOLUNTEERING_OPPORTUNITY: "Volontariato",
            EventType.SPORTS_PRACTICE_MATCH: "Partita/Allenamento Amatoriale",
            EventType.WORKSHOP: "Workshop",
            EventType.SEMINAR_LECTURE: "Seminario",
            EventType.COMMUNITY_GATHERING: "Raduno Comunitario",
            EventType.FESTIVAL: "Festival",
            # Specifici
            EventType.FOUNDATION_DAY_CEREMONY: "Cerimonia del Giorno della Fondazione",
            EventType.INDEPENDENT_FILM_FESTIVAL: "Festival del Cinema Indipendente",
            EventType.ARENA_FUSION_MATCH: "Partita di Arena Fusion",
            EventType.SPRING_FLOWER_FESTIVAL: "Festival dei Fiori di Primavera",
            EventType.REPAIR_CAFE: "Repair Café",
            EventType.POWER_OUTAGE: "Blackout",
            EventType.DISEASE_OUTBREAK: "Focolaio Epidemico",
        }
        # Fallback alla formattazione generica se non in mappa
        return mapping.get(self, self.name.replace("_", " ").title())