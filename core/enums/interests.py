# core/enums/interests.py
from enum import Enum, auto
"""
Definizione dell'Enum Interest per gli interessi degli NPC.
Riferimento TODO: II.2.b, IV.3.b
"""

class Interest(Enum):
    """Enum per i diversi interessi e passioni degli NPC."""

    # --- Interessi Accademici / Conoscenza ---
    HISTORY = auto()                # Storia e archeologia
    MEDICINE = auto()               # Medicina e salute
    PHILOSOPHY_DEBATE = auto()      # Filosofia e dibattito
    POLITICS = auto()               # Politica e attualità
    READING = auto()                # Lettura (più generico di Letteratura)
    SCIENCE = auto()                # Scienza in generale
    TECHNOLOGY = auto()             # Tecnologia, robotica, IA

    # --- Interessi Artistici e Culturali ---
    ARCHITECTURE = auto()           # Architettura e design urbano
    FASHION = auto()                # Moda e design di abiti
    FILM_TV_THEATER = auto()        # Film, Serie TV e Teatro
    MUSIC_LISTENING = auto()        # Ascoltare musica
    MUSIC_PLAYING = auto()          # Suonare uno o più strumenti
    PAINTING = auto()               # Interesse specifico nella pittura
    PHOTOGRAPHY = auto()            # Interesse specifico nella fotografia
    VISUAL_ARTS = auto()            # Pittura, scultura, disegno in generale
    WRITING = auto()                # Interesse specifico nella scrittura

    # --- Interessi Pratici / Hobby ---
    BOARD_GAMES = auto()            # Giochi da tavolo e di strategia
    COLLECTING = auto()             # Collezionismo (di qualsiasi tipo)
    COOKING_AND_FOOD = auto()       # Cucinare e il buon cibo
    CRAFTING = auto()               # Artigianato, fai-da-te, modellismo
    GAMING = auto()                 # Gaming (Videogiochi PC o Console)
    GARDENING = auto()              # Giardinaggio e botanica
    TOYS_PLAYING = auto()           # Giocare con giocattoli (per bambini)

    # --- Interessi legati a Stile di Vita e Attività ---
    ANIMALS = auto()                # Animali domestici e fauna selvatica
    FITNESS_AND_WELLNESS = auto()   # Fitness, yoga, meditazione, benessere
    NATURE_AND_OUTDOORS = auto()    # Natura, escursionismo, attività all'aperto
    SPORTS_PRACTICING = auto()      # Praticare sport attivamente
    SPORTS_WATCHING = auto()        # Seguire sport da spettatore
    TRAVEL = auto()                 # Viaggiare ed esplorare
    
    # --- Interessi Sociali ---
    GOSSIP = auto()                 # Pettegolezzi e dinamiche sociali
    MENTORING_AS_HOBBY = auto()     # Fare da mentore come passione
    SOCIALIZING = auto()            # Socializzare in generale, feste
    SOCIAL_ACTIVISM = auto()        # Attivismo Sociale, Politico, Volontariato

    def display_name_it(self) -> str:
        """Restituisce un nome leggibile in italiano per l'interesse."""
        mapping = {
            # Accademici
            Interest.HISTORY: "Storia",
            Interest.MEDICINE: "Medicina",
            Interest.PHILOSOPHY_DEBATE: "Filosofia e Dibattito",
            Interest.POLITICS: "Politica",
            Interest.READING: "Lettura",
            Interest.SCIENCE: "Scienza",
            Interest.TECHNOLOGY: "Tecnologia",

            # Artistici
            Interest.ARCHITECTURE: "Architettura",
            Interest.FASHION: "Moda",
            Interest.FILM_TV_THEATER: "Film, TV e Teatro",
            Interest.MUSIC_LISTENING: "Ascoltare Musica",
            Interest.MUSIC_PLAYING: "Suonare Strumenti",
            Interest.PAINTING: "Pittura",
            Interest.PHOTOGRAPHY: "Fotografia",
            Interest.VISUAL_ARTS: "Arti Visive",
            Interest.WRITING: "Scrittura",

            # Pratici
            Interest.BOARD_GAMES: "Giochi da Tavolo",
            Interest.COLLECTING: "Collezionismo",
            Interest.COOKING_AND_FOOD: "Cucina e Cibo",
            Interest.CRAFTING: "Artigianato",
            Interest.GAMING: "Gaming",
            Interest.GARDENING: "Giardinaggio",
            Interest.TOYS_PLAYING: "Giocare con Giocattoli",

            # Stile di Vita
            Interest.ANIMALS: "Animali",
            Interest.FITNESS_AND_WELLNESS: "Fitness e Benessere",
            Interest.NATURE_AND_OUTDOORS: "Natura ed Escursioni",
            Interest.SPORTS_PRACTICING: "Praticare Sport",
            Interest.SPORTS_WATCHING: "Seguire Sport",
            Interest.TRAVEL: "Viaggi",

            # Sociali
            Interest.GOSSIP: "Pettegolezzi",
            Interest.MENTORING_AS_HOBBY: "Fare da Mentore",
            Interest.SOCIALIZING: "Socializzare",
            Interest.SOCIAL_ACTIVISM: "Attivismo Sociale",
        }
        return mapping.get(self, self.name.replace("_", " ").title())
