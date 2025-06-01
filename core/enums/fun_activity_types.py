# core/enums/fun_activity_types.py
"""
Definizione dell'Enum 'FunActivityType' per categorizzare i tipi di attività
divertenti che un NPC può svolgere.
"""
from enum import Enum, auto

class FunActivityType(Enum):
    """
    Rappresenta i diversi tipi di attività per soddisfare il bisogno di Divertimento (FUN).
    Riferimento TODO: VI.2.e
    """
    WATCH_TV = auto()                   # Guardare la TV
    PLAY_COMPUTER_GAME = auto()         # Giocare al computer
    READ_BOOK_FOR_FUN = auto()          # Leggere un libro per divertimento (diverso da studio)
    LISTEN_TO_MUSIC = auto()            # Ascoltare musica
    PLAY_MUSICAL_INSTRUMENT = auto()    # Suonare uno strumento musicale (come hobby)
    ENGAGE_IN_HOBBY_CRAFT = auto()      # Dedicarsi a un hobby manuale/artigianale
    ENGAGE_IN_HOBBY_ARTISTIC = auto()   # Dedicarsi a un hobby artistico (pittura, scrittura)
    PLAY_BOARD_GAMES = auto()           # Giocare a giochi da tavolo/società
    DO_SPORTS_FOR_FUN = auto()          # Fare sport per divertimento
    SOCIAL_MEDIA_Browse = auto()      # Navigare sui social media (SoNet?)
    GO_SHOPPING_FOR_FUN = auto()        # Fare shopping per diletto (non per necessità)
    TELL_JOKES = auto()                 # Raccontare barzellette (interazione sociale divertente)
    DANCE = auto()                      # Ballare
    # Aggiungere altre attività divertenti specifiche di Anthalys

    def display_name_it(self) -> str:
        mapping = {
            FunActivityType.WATCH_TV: "Guardare la TV",
            FunActivityType.PLAY_COMPUTER_GAME: "Giocare al Computer",
            FunActivityType.READ_BOOK_FOR_FUN: "Leggere un Libro (Diletto)",
            FunActivityType.LISTEN_TO_MUSIC: "Ascoltare Musica",
            FunActivityType.PLAY_MUSICAL_INSTRUMENT: "Suonare uno Strumento",
            FunActivityType.ENGAGE_IN_HOBBY_CRAFT: "Dedicarsi a Hobby Manuali",
            FunActivityType.ENGAGE_IN_HOBBY_ARTISTIC: "Dedicarsi a Hobby Artistici",
            FunActivityType.PLAY_BOARD_GAMES: "Giocare a Giochi da Tavolo",
            FunActivityType.DO_SPORTS_FOR_FUN: "Fare Sport (Divertimento)",
            FunActivityType.SOCIAL_MEDIA_Browse: "Navigare sui Social Media",
            FunActivityType.GO_SHOPPING_FOR_FUN: "Fare Shopping (Diletto)",
            FunActivityType.TELL_JOKES: "Raccontare Barzellette",
            FunActivityType.DANCE: "Ballare",
        }
        return mapping.get(self, self.name.replace("_", " ").title())