# core/enums/event_types.py
"""
Definizione dell'Enum 'EventType' per categorizzare il tipo di attività
o evento dei Social Hubs.
"""
from enum import Enum, auto

class EventType(Enum):
    """
    Rappresenta il tipo specifico di attività o evento di un Social Hub.
    """
    WEEKLY_MEETING = auto()         # Incontro Settimanale (es. Club del Libro)
    ART_EXHIBITION = auto()         # Esposizione d'Arte
    EVENING_COURSE = auto()         # Corso Serale (es. Cucina)
    WEEKEND_GROUP_ACTIVITY = auto() # Attività di Gruppo nel Weekend (es. Escursioni)
    FIXED_VENUE_FREE_ACTIVITY = auto() # Luogo Fisso con Attività Libera (es. Area Scacchi)
    LIVE_CONCERT = auto()           # Concerto dal Vivo
    LOCAL_MARKET_DAY = auto()       # Giorno di Mercato Locale
    VOLUNTEERING_OPPORTUNITY = auto() # Opportunità di Volontariato
    SPORTS_PRACTICE_MATCH = auto()  # Allenamento o Partita Sportiva
    WORKSHOP = auto()                 # Laboratorio / Workshop pratico
    SEMINAR_LECTURE = auto()        # Seminario / Lezione
    COMMUNITY_GATHERING = auto()    # Raduno Comunitario generico
    FESTIVAL = auto()                 # Festival / Sagra
    # Aggiungere altri tipi di evento/attività se necessario

    def display_name_it(self) -> str:
        mapping = {
            EventType.WEEKLY_MEETING: "Incontro Settimanale",
            EventType.ART_EXHIBITION: "Esposizione d'Arte",
            EventType.EVENING_COURSE: "Corso Serale",
            EventType.WEEKEND_GROUP_ACTIVITY: "Attività di Gruppo (Weekend)",
            EventType.FIXED_VENUE_FREE_ACTIVITY: "Attività Libera (Luogo Fisso)",
            EventType.LIVE_CONCERT: "Concerto dal Vivo",
            EventType.LOCAL_MARKET_DAY: "Mercato Locale",
            EventType.VOLUNTEERING_OPPORTUNITY: "Volontariato",
            EventType.SPORTS_PRACTICE_MATCH: "Attività Sportiva (Allenamento/Partita)",
            EventType.WORKSHOP: "Workshop / Laboratorio",
            EventType.SEMINAR_LECTURE: "Seminario / Lezione",
            EventType.COMMUNITY_GATHERING: "Raduno Comunitario",
            EventType.FESTIVAL: "Festival / Sagra",
        }
        return mapping.get(self, self.name.replace("_", " ").title())