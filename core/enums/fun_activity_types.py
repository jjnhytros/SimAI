# core/enums/fun_activity_types.py
from enum import Enum, auto
"""
Definizione dell'Enum FunActivityType per le attività di svago degli NPC.
Questa è una versione fusa e dettagliata.
"""

class FunActivityType(Enum):
    """
    Enum per le diverse attività di svago (hobby, divertimento) che un NPC può compiere.
    """
    # --- Attività Creative e Artigianali (Specifiche) ---
    PAINT = auto()                      # Dipingere su cavalletto
    PLAY_GUITAR = auto()                # Suonare la chitarra
    PLAY_PIANO = auto()                 # Suonare il pianoforte
    PLAY_VIOLIN = auto()                # Suonare il violino
    SING = auto()                       # Cantare
    WRITE_BOOK_FOR_FUN = auto()         # Scrivere per diletto
    DJ_MIXING = auto()                  # Fare il DJ
    PHOTOGRAPHY = auto()                # Fare fotografia
    KNITTING = auto()                   # Lavorare a maglia
    POTTERY = auto()                    # Lavorare la ceramica
    WOODWORKING = auto()                # Lavorare il legno
    
    # --- Attività Intellettuali / tranquille ---
    READ_BOOK_FOR_FUN = auto()
    PLAY_CHESS = auto()
    DO_CROSSWORD_PUZZLE = auto()
    RESEARCH_INTEREST_ONLINE = auto()   # Ricercare un interesse online
    DAYDREAM = auto()                   # Sognare ad occhi aperti
    WATCH_CLOUDS = auto()               # Osservare le nuvole
    PEOPLE_WATCH = auto()               # Osservare la gente
    MEDITATE = auto()
    
    # --- Attività all'Aperto / Fisiche ---
    GO_FOR_A_JOG = auto()               # Fare jogging all'esterno
    JOG_IN_PLACE = auto()               # Corsa sul posto (alternativa indoor)
    GO_HIKING = auto()                  # Fare un'escursione
    SWIMMING = auto()
    GARDENING = auto()
    FISHING = auto()
    PLAY_SPORTS_CASUAL = auto()         # Praticare sport in modo informale
    EXPLORE_NEIGHBORHOOD = auto()       # Esplorare il quartiere

    # --- Attività Domestiche / Media ---
    WATCH_TV = auto()
    WATCH_MOVIE_AT_HOME = auto()        # Guardare un Film a Casa
    PLAY_VIDEO_GAMES = auto()           # Giocare ai videogiochi (copre PC e Console)
    LISTEN_TO_MUSIC = auto()
    BROWSE_SOCIAL_MEDIA = auto()        # Navigare sui Social Media

    # --- Attività Sociali e in Città ---
    GO_TO_BAR = auto()
    GO_DANCING = auto()                 # Andare a ballare in un locale
    DANCE = auto()                      # Danzare (generico)
    PLAY_BOARD_GAMES = auto()           # Giocare a giochi da tavolo con altri
    WINDOW_SHOPPING = auto()            # Guardare le vetrine per divertimento (senza acquisti)
    WATCH_MOVIE_AT_CINEMA = auto()      # Andare al cinema
    TELL_STORIES = auto()               # Raccontare storie
    PRACTICE_PUBLIC_SPEAKING = auto()   # Esercitarsi a parlare in pubblico
    
    # TODO: Aggiungere altre attività di divertimento specifiche per SimAI

    def display_name_it(self) -> str:
        """Restituisce un nome leggibile in italiano per l'attività."""
        mapping = {
            # Creative
            FunActivityType.PAINT: "Dipingere",
            FunActivityType.PLAY_GUITAR: "Suonare la Chitarra",
            FunActivityType.PLAY_PIANO: "Suonare il Pianoforte",
            FunActivityType.PLAY_VIOLIN: "Suonare il Violino",
            FunActivityType.SING: "Cantare",
            FunActivityType.WRITE_BOOK_FOR_FUN: "Scrivere per Piacere",
            FunActivityType.DJ_MIXING: "Fare il DJ",
            FunActivityType.PHOTOGRAPHY: "Fotografare",
            FunActivityType.KNITTING: "Lavorare a Maglia",
            FunActivityType.POTTERY: "Lavorare la Ceramica",
            FunActivityType.WOODWORKING: "Lavorare il Legno",
            # Intellettuali
            FunActivityType.READ_BOOK_FOR_FUN: "Leggere per Piacere",
            FunActivityType.PLAY_CHESS: "Giocare a Scacchi",
            FunActivityType.DO_CROSSWORD_PUZZLE: "Fare Parole Crociate",
            FunActivityType.RESEARCH_INTEREST_ONLINE: "Fare Ricerche Online",
            FunActivityType.DAYDREAM: "Sognare ad Occhi Aperti",
            FunActivityType.WATCH_CLOUDS: "Guardare le Nuvole",
            FunActivityType.PEOPLE_WATCH: "Osservare la Gente",
            FunActivityType.MEDITATE: "Meditare",
            # Fisiche
            FunActivityType.GO_FOR_A_JOG: "Fare Jogging",
            FunActivityType.JOG_IN_PLACE: "Corsa sul Posto",
            FunActivityType.GO_HIKING: "Fare Escursionismo",
            FunActivityType.SWIMMING: "Nuotare",
            FunActivityType.GARDENING: "Fare Giardinaggio",
            FunActivityType.FISHING: "Pescare",
            FunActivityType.PLAY_SPORTS_CASUAL: "Fare Sport",
            FunActivityType.EXPLORE_NEIGHBORHOOD: "Esplorare il Quartiere",
            # Media
            FunActivityType.WATCH_TV: "Guardare la TV",
            FunActivityType.WATCH_MOVIE_AT_HOME: "Guardare un Film a Casa",
            FunActivityType.PLAY_VIDEO_GAMES: "Giocare ai Videogiochi",
            FunActivityType.LISTEN_TO_MUSIC: "Ascoltare Musica",
            FunActivityType.BROWSE_SOCIAL_MEDIA: "Navigare sui Social",
            # Sociali / Città
            FunActivityType.GO_TO_BAR: "Andare al Bar",
            FunActivityType.GO_DANCING: "Andare a Ballare",
            FunActivityType.DANCE: "Ballare",
            FunActivityType.PLAY_BOARD_GAMES: "Fare Giochi da Tavolo",
            FunActivityType.WINDOW_SHOPPING: "Guardare le Vetrine",
            FunActivityType.WATCH_MOVIE_AT_CINEMA: "Andare al Cinema",
            FunActivityType.TELL_STORIES: "Raccontare Storie",
            FunActivityType.PRACTICE_PUBLIC_SPEAKING: "Esercitarsi a Parlare in Pubblico",
        }
        return mapping.get(self, self.name.replace("_", " ").title())
