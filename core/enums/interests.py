# core/enums/interests.py
"""
Definizione dell'Enum 'Interest' per rappresentare i possibili
interessi e hobby degli NPC in SimAI.
"""
from enum import Enum, auto

class Interest(Enum):
    """
    Rappresenta i possibili interessi/hobby che un NPC può avere.
    Riferimento: TODO.md, Sezione X.1.a
    """
    # Aggiungere altri interessi specifici per Anthalys se emergono.
    ASTRONOMY = auto()               # Astronomia Osservativa
    BAKING = auto()                  # Pasticceria
    BOARD_GAMES = auto()             # Giochi da Tavolo e di Società
    COLLECTING = auto()              # Collezionismo
    COOKING = auto()                 # Cucina
    CRAFTS_GENERAL = auto()          # Artigianato Generale (es. fai-da-te, modellismo)
    FASHION = auto()                 # Moda
    FILM_TV_SERIES = auto()          # Cinema e Serie TV
    GAMING = auto()                  # Gaming (Videogiochi)
    GARDENING = auto()               # Giardinaggio
    HISTORY = auto()                 # Storia (generale o locale)
    MENTORING_AS_HOBBY = auto()      # Mentoring (inteso come passione/hobby)
    MUSIC_LISTENING = auto()         # Ascolto Musica
    MUSIC_PLAYING = auto()           # Suonare Strumenti Musicali
    NATURE_EXPLORATION = auto()      # Esplorazione della Natura, Escursionismo
    OUTDOOR_ACTIVITIES = auto()      # Attività all'Aperto (generico)
    PAINTING = auto()                # Pittura
    PHILOSOPHY_DEBATE = auto()       # Filosofia, Dibattito, Discussioni Intellettuali
    PHOTOGRAPHY = auto()             # Fotografia
    READING = auto()                 # Lettura
    SOCIAL_ACTIVISM = auto()         # Attivismo Sociale/Politico
    SPORTS_ACTIVE = auto()           # Praticare Sport Attivamente
    TECHNOLOGY = auto()              # Tecnologia e Informatica (come hobby)
    TOYS_PLAYING = auto()            # Giocare con Giocattoli
    TRAVEL = auto()                  # Viaggi ed Esplorazione
    VISUAL_ARTS = auto()             # Arti Visive (più generico di Pittura)
    VOLUNTEERING = auto()            # Volontariato
    WRITING = auto()                 # Scrittura

    # Esempio di come potresti aggiungere un metodo per un nome "display"
    # def display_name_it(self):
    #     mapping = {
    #         Interest.READING: "Lettura",
    #         Interest.GARDENING: "Giardinaggio",
    #         # ... e così via per tutti gli altri ...
    #         Interest.PHILOSOPHY_DEBATE: "Filosofia e Dibattito"
    #     }
    #     return mapping.get(self, self.name.replace("_", " ").title())

# Non è necessario un print qui, quello in __init__.py del package è sufficiente.