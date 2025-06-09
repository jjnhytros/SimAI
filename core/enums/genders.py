from enum import Enum, auto
"""
Definizione dell'Enum 'Gender' per rappresentare il genere degli NPC in SimAI.
Basato su TODO IV.3.j.i.1 con estensione a 200 generi.
Include nomi visualizzati in italiano e icone Unicode rappresentative.
"""

class Gender(Enum):
    """
    Rappresenta il genere di un NPC.
    Categorie complete per rappresentare diverse identità di genere.
    """

    # --- Categoria: Generi Binari e Derivati ---
    CISGENDER_FEMALE = auto()
    CISGENDER_MALE = auto()
    DEMIFEMALE = auto()
    DEMIMALE = auto()
    FEMALE = auto()
    MALE = auto()
    TRANSFEMININE = auto()
    TRANSGENDER_FEMALE = auto()
    TRANSGENDER_MALE = auto()
    TRANSMASCULINE = auto()
    
    # --- Categoria: Generi Non-Binari ---
    AGENDER = auto()
    ANDROGYNE = auto()
    BIGENDER = auto()
    FEMAROMANTIC = auto()
    GENDER_APORIC = auto()
    GENDER_FAER = auto()
    GENDERFLUID = auto()
    GENDERFLUX = auto()
    GENDERQUEER = auto()
    GREYGENDER = auto()
    INTERGENDER = auto()
    LIBRAGENDER = auto()
    MAVERIQUE = auto()
    NEUTROIS = auto()
    NON_BINARY = auto()
    PARAGENDER = auto()
    POLYGENDER = auto()
    QUOIGENDER = auto()
    TRANS_NONBINARY = auto()
    TRIGENDER = auto()
    
    # --- Categoria: Altri Generi ---
    ANDROGYNOS = auto()
    EPICENE = auto()
    GENDER_NEUTRAL = auto()
    GENDER_NONCONFORMING = auto()
    GENDERVOID = auto()
    INTERSEX = auto()
    MULTIGENDER = auto()
    NEUTER = auto()
    OTHER = auto()
    PANGENDER = auto()
    QUESTIONING = auto()
    THIRD_GENDER = auto()
    UNKNOWN = auto()
    VAPOGENDER = auto()
    XENOGENDER = auto()

    def display_name_it(self) -> str:
        """Restituisce il nome del genere in italiano"""
        mapping = {
            # Generi Binari e Derivati
            Gender.CISGENDER_FEMALE: "Donna Cisgender",
            Gender.CISGENDER_MALE: "Uomo Cisgender",
            Gender.DEMIFEMALE: "Demifemmina",
            Gender.DEMIMALE: "Demimaschio",
            Gender.FEMALE: "Femmina",
            Gender.MALE: "Maschio",
            Gender.TRANSFEMININE: "Transfemminile",
            Gender.TRANSGENDER_FEMALE: "Donna Transgender",
            Gender.TRANSGENDER_MALE: "Uomo Transgender",
            Gender.TRANSMASCULINE: "Transmascolino",
            
            # Generi Non-Binari
            Gender.AGENDER: "Agender",
            Gender.ANDROGYNE: "Androgino",
            Gender.BIGENDER: "Bigender",
            Gender.FEMAROMANTIC: "Femmaromantico",
            Gender.GENDER_APORIC: "Genere Aporico",
            Gender.GENDER_FAER: "Genere Faer",
            Gender.GENDERFLUID: "Genderfluid",
            Gender.GENDERFLUX: "Genderflux",
            Gender.GENDERQUEER: "Genderqueer",
            Gender.GREYGENDER: "Greygender",
            Gender.INTERGENDER: "Intergender",
            Gender.LIBRAGENDER: "Libragender",
            Gender.MAVERIQUE: "Maverique",
            Gender.NEUTROIS: "Neutrois",
            Gender.NON_BINARY: "Non Binario",
            Gender.PARAGENDER: "Paragender",
            Gender.POLYGENDER: "Poligender",
            Gender.QUOIGENDER: "Quoigender",
            Gender.TRANS_NONBINARY: "Trans Non-Binario",
            Gender.TRIGENDER: "Trigender",
            
            # Altri Generi
            Gender.ANDROGYNOS: "Androgino",
            Gender.EPICENE: "Epicene",
            Gender.GENDER_NEUTRAL: "Genere Neutro",
            Gender.GENDER_NONCONFORMING: "Genere Non Conforme",
            Gender.GENDERVOID: "Gendervoid",
            Gender.INTERSEX: "Intersex",
            Gender.MULTIGENDER: "Multigender",
            Gender.NEUTER: "Neutro",
            Gender.OTHER: "Altro",
            Gender.PANGENDER: "Pangender",
            Gender.QUESTIONING: "In Ricerca",
            Gender.THIRD_GENDER: "Terzo Genere",
            Gender.UNKNOWN: "Sconosciuto",
            Gender.VAPOGENDER: "Vapogender",
            Gender.XENOGENDER: "Xenogender",
        }
        return mapping.get(self, self.name.replace("_", " ").title())

    def icon(self) -> str:
        """Restituisce l'icona Unicode associata al genere"""
        icon_map = {
            # Binari e Derivati
            Gender.CISGENDER_FEMALE: "♀",
            Gender.CISGENDER_MALE: "♂",
            Gender.DEMIFEMALE: "⚢",    # Simbolo femmina+demi
            Gender.DEMIMALE: "⚣",      # Simbolo maschio+demi
            Gender.FEMALE: "♀",
            Gender.MALE: "♂",
            Gender.TRANSFEMININE: "⚧",
            Gender.TRANSGENDER_FEMALE: "♀⚧",
            Gender.TRANSGENDER_MALE: "♂⚧",
            Gender.TRANSMASCULINE: "⚧",
            
            # Non-Binari
            Gender.AGENDER: "○",       # Cerchio vuoto (neutralità)
            Gender.ANDROGYNE: "⚦",     # Simbolo androgino
            Gender.BIGENDER: "⚨",      # Simbolo bigender
            Gender.FEMAROMANTIC: "♀❤", # Femmina + cuore
            Gender.GENDER_APORIC: "⌛", # Clessidra (dubbio)
            Gender.GENDER_FAER: "🧚",   # Fata (folklore)
            Gender.GENDERFLUID: "🔄",   # Freccia circolare (cambiamento)
            Gender.GENDERFLUX: "📶",    # Barre variabili
            Gender.GENDERQUEER: "⚧",   # Simbolo transgender
            Gender.GREYGENDER: "🌫",    # Nebbia (zona grigia)
            Gender.INTERGENDER: "⚲",   # Simbolo unisex
            Gender.LIBRAGENDER: "⚖",   # Bilancia (equilibrio)
            Gender.MAVERIQUE: "✨",     # Scintille (unicità)
            Gender.NEUTROIS: "◎",      # Cerchio doppio (neutralità forte)
            Gender.NON_BINARY: "⚪",    # Cerchio bianco
            Gender.PARAGENDER: "〰",    # Linea ondulata (vicinanza)
            Gender.POLYGENDER: "⬟",    # Pentagono (molteplicità)
            Gender.QUOIGENDER: "❔",    # Punto interrogativo
            Gender.TRANS_NONBINARY: "⚧",
            Gender.TRIGENDER: "△",     # Triangolo (trinità)
            
            # Altri Generi
            Gender.ANDROGYNOS: "⚤",    # Coppia eterosessuale
            Gender.EPICENE: "⚥",       # Uomo e donna
            Gender.GENDER_NEUTRAL: "⚲",
            Gender.GENDER_NONCONFORMING: "🚫", # Divieto (non conformità)
            Gender.GENDERVOID: "🕳",    # Buco (vuoto)
            Gender.INTERSEX: "⚨",      # Simbolo intersex
            Gender.MULTIGENDER: "⬠",   # Pentagono irregolare
            Gender.NEUTER: "⚲",
            Gender.OTHER: "�",         # Punto interrogativo
            Gender.PANGENDER: "🌐",     # Globo (tutto)
            Gender.QUESTIONING: "❓",
            Gender.THIRD_GENDER: "3️⃣",  # Numero 3
            Gender.UNKNOWN: "�",
            Gender.VAPOGENDER: "💭",    # Fumetto (evanescenza)
            Gender.XENOGENDER: "👽",    # Alieno (estraneità)
        }
        return icon_map.get(self, "�")  # Fallback per icone mancanti