# core/enums/life_stages.py
from enum import Enum, auto

from core.enums.genders import Gender

class LifeStage(Enum):
    """
    Rappresenta le diverse fasi e sotto-fasi della vita di un NPC.
    Ampliato per maggiore granularità.
    Riferimento TODO: IV.2.d
    """
    # Fase Infantile (0-3 anni)
    NEWBORN = auto()           # Neonato (0 - ~2 mesi)
    INFANT = auto()            # Lattante (~2 mesi - 1 anno)
    TODDLER = auto()           # Primi passi (1 - 3 anni)
    
    # Fase Fanciullezza (3-12 anni)
    PRESCHOOLER = auto()       # Età prescolare (3 - 6 anni)
    CHILD = auto()             # Bambino/a (6 - 9 anni)
    PRE_TEEN = auto()          # Preadolescente (9 - 12 anni)

    # Fase Adolescenza (12-20 anni)
    EARLY_ADOLESCENCE = auto() # Prima adolescenza (12 - 15 anni)
    MID_ADOLESCENCE = auto()   # Media adolescenza (15 - 18 anni)
    LATE_ADOLESCENCE = auto()  # Tarda adolescenza (18 - 20 anni)

    # Fase Adulta (20-60 anni)
    YOUNG_ADULT = auto()       # Giovane adulto (20 - 30 anni)
    ADULT = auto()             # Adulto (30 - 40 anni)
    MIDDLE_AGED = auto()       # Mezza età (40 - 60 anni)

    # Fase Anziana (60+ anni)
    MATURE_ADULT = auto()      # Adulto maturo (60 - 75 anni)
    SENIOR = auto()            # Anziano (75 - 90 anni)
    ELDERLY = auto()           # Grande anziano (90+ anni)
    
    # Stato speciale
    NONE = auto()              # Non applicabile

    def display_name_it(self, gender: Gender) -> str:
        """Restituisce un nome leggibile e declinato in base al genere per lo stadio di vita."""
        mapping = {
            # --- Declinabili ---
            LifeStage.NEWBORN: {Gender.MALE: "Neonato", Gender.FEMALE: "Neonata"},
            LifeStage.CHILD: {Gender.MALE: "Bambino", Gender.FEMALE: "Bambina"},
            LifeStage.YOUNG_ADULT: {Gender.MALE: "Giovane Adulto", Gender.FEMALE: "Giovane Adulta"},
            LifeStage.ADULT: {Gender.MALE: "Adulto", Gender.FEMALE: "Adulta"},
            LifeStage.MATURE_ADULT: {Gender.MALE: "Adulto Maturo", Gender.FEMALE: "Adulta Matura"},
            LifeStage.SENIOR: {Gender.MALE: "Anziano", Gender.FEMALE: "Anziana"},
            LifeStage.ELDERLY: {Gender.MALE: "Grande Anziano", Gender.FEMALE: "Grande Anziana"},
            LifeStage.NONE: {Gender.MALE: "Nessuno", Gender.FEMALE: "Nessuna"},

            # --- Invariabili ---
            LifeStage.INFANT: "Lattante",
            LifeStage.TODDLER: "Primi Passi",
            LifeStage.PRESCHOOLER: "Età Prescolare",
            LifeStage.PRE_TEEN: "Preadolescente",
            LifeStage.EARLY_ADOLESCENCE: "Prima Adolescenza",
            LifeStage.MID_ADOLESCENCE: "Media Adolescenza",
            LifeStage.LATE_ADOLESCENCE: "Tarda Adolescenza",
            LifeStage.MIDDLE_AGED: "Mezza Età",
        }
        value = mapping.get(self)

        if isinstance(value, dict):
            # Se il valore è un dizionario, restituisci la chiave per il genere corretto.
            # Usa il maschile come fallback.
            return value.get(gender, value.get(Gender.MALE, "N/D"))
        elif isinstance(value, str):
            # Se è una stringa, è invariabile.
            return value
        else:
            # Fallback se lo stadio di vita non è nella mappa.
            return self.name.replace("_", " ").title()

    # --- Metodi Helper (MOLTO CONSIGLIATI) ---
    @property
    def is_infant_or_toddler(self) -> bool:
        """Vero se è un neonato, lattante o toddler."""
        return self in {LifeStage.NEWBORN, LifeStage.INFANT, LifeStage.TODDLER}

    @property
    def is_child(self) -> bool:
        """Vero se è in età scolare (non adolescente)."""
        return self in {LifeStage.PRESCHOOLER, LifeStage.CHILD, LifeStage.PRE_TEEN}
        
    @property
    def is_teenager(self) -> bool:
        """Vero se è in una qualsiasi fase dell'adolescenza."""
        return self in {LifeStage.EARLY_ADOLESCENCE, LifeStage.MID_ADOLESCENCE, LifeStage.LATE_ADOLESCENCE}
        
    @property
    def is_adult(self) -> bool:
        """Vero se è in una qualsiasi fase adulta (non anziano)."""
        return self in {LifeStage.YOUNG_ADULT, LifeStage.ADULT, LifeStage.MIDDLE_AGED}

    @property
    def is_elder(self) -> bool:
        """Vero se è in una qualsiasi fase anziana."""
        return self in {LifeStage.MATURE_ADULT, LifeStage.SENIOR, LifeStage.ELDERLY}