# core/enums/fun_activity_types.py
"""
Definizione dell'Enum 'FunActivityType' per categorizzare i tipi di attività
divertenti che un NPC può svolgere.
"""
from enum import Enum, auto

class FunActivityType(Enum):
    """Tipi di attività che gli NPC possono compiere per soddisfare il bisogno di FUN."""
    
    # Attività che tipicamente richiedono oggetti specifici
    PLAY_COMPUTER_GAME = auto()         # Giocare al Computer
    PLAY_CONSOLE_GAME = auto()          # Giocare alla Console (se diversa da PC)
    PLAY_BOARD_GAMES = auto()           # Giocare a Giochi da Tavolo
    READ_BOOK_FOR_FUN = auto()          # Leggere un Libro per Divertimento
    LISTEN_TO_MUSIC = auto()            # Ascoltare Musica (da stereo, cuffie)
    PLAY_MUSICAL_INSTRUMENT = auto()    # Suonare uno Strumento Musicale
    WATCH_TV = auto()                   # Guardare la TV
    WATCH_MOVIE_AT_HOME = auto()      # Guardare un Film a Casa
    WATCH_MOVIE_AT_CINEMA = auto()    # Guardare un Film al Cinema
    ENGAGE_IN_HOBBY_ARTISTIC = auto()   # Dedicarsi a Hobby Artistici (Pittura, Scultura)
    ENGAGE_IN_HOBBY_CRAFT = auto()      # Dedicarsi a Hobby Manuali (Lavorare a Maglia, Modellismo)
    DO_SPORTS_FOR_FUN = auto()          # Fare Sport per Divertimento (es. Basket, Calcio con oggetti)
    GO_SHOPPING_FOR_FUN = auto()      # Fare Shopping per Divertimento
    
    # --- ATTIVITÀ CHE POTREBBERO NON RICHIEDERE OGGETTI (aggiunte/verificate) ---
    DANCE = auto()                      # Ballare (potrebbe essere con o senza musica/oggetto)
    SING = auto()                       # Cantare
    DAYDREAM = auto()                   # Sognare ad Occhi Aperti <-- AGGIUNTO SE MANCAVA
    JOG_IN_PLACE = auto()               # Corsa sul Posto <-- AGGIUNTO SE MANCAVA
    PRACTICE_PUBLIC_SPEAKING = auto()   # Esercitarsi a Parlare in Pubblico <-- AGGIUNTO SE MANCAVA
    SOCIAL_MEDIA_Browse = auto()      # Navigare sui Social Media (potrebbe usare un telefono, ma è un'azione a sé)
    WATCH_CLOUDS = auto()               # Guardare le Nuvole <-- AGGIUNTO SE MANCAVA
    MEDITATE = auto()                   # Meditare <-- AGGIUNTO SE MANCAVA
    TELL_STORIES = auto()               # Raccontare Storie
    PEOPLE_WATCH = auto()               # Osservare la Gente
    WINDOW_SHOPPING = auto()            # Guardare Vetrine (senza comprare)
    EXPLORE_NEIGHBORHOOD = auto()     # Esplorare il Quartiere
    PLAY_GUITAR = auto()
    
    # TODO: Aggiungere altre attività di divertimento specifiche per SimAI

    def display_name_it(self) -> str:
        """Restituisce un nome leggibile in italiano per l'attività."""
        # Sostituisci con nomi più appropriati o usa un sistema di localizzazione
        return self.name.replace("_", " ").capitalize()
