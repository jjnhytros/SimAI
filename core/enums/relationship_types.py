# core/enums/relationship_types.py
from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, Tuple, Union

from core.enums.genders import Gender
"""
Definizione dell'Enum 'RelationshipType' per rappresentare i tipi di relazione
tra NPC in SimAI.
"""

@dataclass
class RelationshipMetadata:
    """Contiene i metadati per un tipo di relazione: nomi e colori."""
    display_names: Dict[Gender, str]
    
    # --- CORREZIONE QUI ---
    # Il colore può essere una singola tupla o un dizionario per genere
    color: Union[Tuple[int, int, int], Dict[Gender, Tuple[int, int, int]]]
class RelationshipType(Enum):
    """
    Rappresenta i diversi tipi di relazione che possono esistere tra due NPC.
    Riferimento TODO: VII.2.b, IV.2.f
    """
    # --- Relazioni Familiari Dirette (Linea Ascendente/Discendente) ---
    PARENT = auto()                     # Genitore
    CHILD = auto()                      # Figlio/a
    GRANDPARENT = auto()                # Nonno/a
    GRANDCHILD = auto()                 # Nipote (di nonno/a)
    GREAT_GRANDPARENT = auto()          # Bisnonno/a
    GREAT_GRANDCHILD = auto()           # Pronipote (di bisnonno/a)
    GREAT_GREAT_GRANDPARENT = auto()    # Trisnonno/a
    GREAT_GREAT_GRANDCHILD = auto()     # Figlio/a del pronipote

    # --- Altre Relazioni Familiari Primarie ---
    SIBLING = auto()                    # Fratello/Sorella (stesso livello)
    SPOUSE = auto()                     # Coniuge

    # --- Altri Parenti (Collaterali o più distanti, gestiti in modo più generico qui) ---
    # In futuro, la natura esatta (es. Zio, Cugino) verrà determinata dinamicamente
    # navigando l'albero genealogico, come da TODO IV.2.f.iv.
    EXTENDED_FAMILY = auto()            # Parente Esteso (es. zii, cugini, prozii)
    
    # --- Relazioni Sociali Non Familiari ---
    FRIEND_CLOSE = auto()               # Amico Stretto
    FRIEND_REGULAR = auto()             # Amico
    ACQUAINTANCE = auto()               # Conoscente
    CHILDHOOD_BEST_FRIEND = auto()      # Migliori Amici d'Infanzia
    ROMANTIC_PARTNER = auto()           # Partner Romantico (non sposato)
    CRUSH = auto()                      # Cotta / Infatuazione
    EX_PARTNER = auto()                 # Ex Partner Romantico / Ex Coniuge
    
    ENEMY_RIVAL = auto()                # Nemico / Rivale
    ENEMY_DISLIKED = auto()             # Antipatia / Persona Non Gradita
    
    # --- Relazioni Professionali / Contestuali ---
    COLLEAGUE = auto()                  # Collega di lavoro
    NEIGHBOR = auto()                   # Vicino di casa
    MENTOR = auto()                     # Mentore
    MENTEE = auto()                     # Allievo (di un mentore)
    ROOMMATE = auto()                   # Coinquilino (se rilevante)

    AUNT_UNCLE = 100
    NEPHEW_NIECE = 101
    
    COUSIN = 110
    
    GREAT_AUNT_UNCLE = 120
    FIRST_COUSIN_ONCE_REMOVED = 121
    
    SECOND_COUSIN = 130

    @property
    def metadata(self) -> RelationshipMetadata:
        """Restituisce la scheda informativa completa per questo tipo di relazione."""
        _metadata_map = {
            # --- FAMIGLIA NUCLEARE ---
            RelationshipType.SPOUSE: RelationshipMetadata(
                display_names={Gender.MALE: "Marito", Gender.FEMALE: "Moglie"},
                color={
                    Gender.MALE: (135, 206, 250),  # Celeste
                    Gender.FEMALE: (255, 182, 193)  # Rosa
                }
            ),
            RelationshipType.PARENT: RelationshipMetadata(
                display_names={Gender.MALE: "Padre", Gender.FEMALE: "Madre"},
                color={
                    Gender.MALE: (185, 150, 30),    # Oro scuro
                    Gender.FEMALE: (225, 190, 70)   # Oro chiaro
                }
            ),
            RelationshipType.CHILD: RelationshipMetadata(
                display_names={Gender.MALE: "Figlio", Gender.FEMALE: "Figlia"},
                color={
                    Gender.MALE: (235, 235, 80),    # Giallo scuro
                    Gender.FEMALE: (255, 255, 150)  # Giallo chiaro
                }
            ),
            RelationshipType.SIBLING: RelationshipMetadata(
                display_names={Gender.MALE: "Fratello", Gender.FEMALE: "Sorella"},
                color={
                    Gender.MALE: (0, 186, 189),     # Ciano scuro
                    Gender.FEMALE: (30, 226, 229)   # Ciano chiaro
                }
            ),
            # --- FAMIGLIA DIRETTA ESTESA ---
            RelationshipType.GRANDPARENT: RelationshipMetadata(
                display_names={Gender.MALE: "Nonno", Gender.FEMALE: "Nonna"},
                color={
                    Gender.MALE: (172, 172, 172),   # Argento scuro
                    Gender.FEMALE: (212, 212, 212)  # Argento chiaro
                }
            ),
            RelationshipType.GRANDCHILD: RelationshipMetadata(
                display_names={Gender.MALE: "Nipote", Gender.FEMALE: "Nipote"},
                color={
                    Gender.MALE: (235, 235, 100),   # Giallo-verde scuro
                    Gender.FEMALE: (255, 255, 160)  # Giallo-verde chiaro
                }
            ),
            RelationshipType.GREAT_GRANDPARENT: RelationshipMetadata(
                display_names={Gender.MALE: "Bisnonno", Gender.FEMALE: "Bisnonna"},
                color={
                    Gender.MALE: (191, 191, 191),   # Grigio medio scuro
                    Gender.FEMALE: (231, 231, 231)  # Grigio chiaro
                }
            ),
            RelationshipType.GREAT_GRANDCHILD: RelationshipMetadata(
                display_names={Gender.MALE: "Pronipote", Gender.FEMALE: "Pronipote"},
                color={
                    Gender.MALE: (245, 245, 130),   # Giallo sabbia
                    Gender.FEMALE: (255, 255, 180)  # Giallo crema
                }
            ),
            # --- FAMIGLIA COLLATERALE ---
            RelationshipType.AUNT_UNCLE: RelationshipMetadata(
                display_names={Gender.MALE: "Zio", Gender.FEMALE: "Zia"},
                color={
                    Gender.MALE: (87, 122, 15),     # Verde oliva scuro
                    Gender.FEMALE: (127, 162, 55)   # Verde oliva chiaro
                }
            ),
            RelationshipType.NEPHEW_NIECE: RelationshipMetadata(
                display_names={Gender.MALE: "Nipote", Gender.FEMALE: "Nipote"},
                color={
                    Gender.MALE: (97, 132, 25),     # Verde militare
                    Gender.FEMALE: (147, 182, 75)   # Verde pisello
                }
            ),
            RelationshipType.COUSIN: RelationshipMetadata(
                display_names={Gender.MALE: "Cugino", Gender.FEMALE: "Cugina"},
                color={
                    Gender.MALE: (134, 185, 40),    # Verde lime scuro
                    Gender.FEMALE: (174, 225, 80)   # Verde lime chiaro
                }
            ),
            RelationshipType.EXTENDED_FAMILY: RelationshipMetadata(
                display_names={Gender.MALE: "Parente", Gender.FEMALE: "Parente"},
                color={
                    Gender.MALE: (160, 160, 160),   # Grigio antracite
                    Gender.FEMALE: (200, 200, 200)  # Grigio perla
                }
            ),
            # --- RELAZIONI SOCIALI POSITIVE ---
            RelationshipType.CHILDHOOD_BEST_FRIEND: RelationshipMetadata(
                display_names={Gender.MALE: "Migliore Amico d'Infanzia", Gender.FEMALE: "Migliore Amica d'Infanzia"},
                color={
                    Gender.MALE: (235, 203, 0),     # Oro vecchio
                    Gender.FEMALE: (255, 243, 50)   # Oro lucente
                }
            ),
            RelationshipType.FRIEND_CLOSE: RelationshipMetadata(
                display_names={Gender.MALE: "Amico Stretto", Gender.FEMALE: "Amica Stretta"},
                color={
                    Gender.MALE: (153, 225, 37),    # Verde mela scuro
                    Gender.FEMALE: (193, 255, 87)   # Verde mela chiaro
                }
            ),
            RelationshipType.FRIEND_REGULAR: RelationshipMetadata(
                display_names={Gender.MALE: "Amico", Gender.FEMALE: "Amica"},
                color={
                    Gender.MALE: (90, 139, 227),    # Blu oceano
                    Gender.FEMALE: (130, 179, 255)  # Azzurro
                }
            ),
            RelationshipType.ACQUAINTANCE: RelationshipMetadata(
                display_names={Gender.MALE: "Conoscente", Gender.FEMALE: "Conoscente"},
                color={
                    Gender.MALE: (180, 180, 180),   # Grigio ferro
                    Gender.FEMALE: (220, 220, 220)  # Grigio nebbia
                }
            ),
            # --- RELAZIONI ROMANTICHE ---
            RelationshipType.ROMANTIC_PARTNER: RelationshipMetadata(
                display_names={Gender.MALE: "Partner", Gender.FEMALE: "Partner"},
                color={
                    Gender.MALE: (235, 85, 160),    # Fucsia
                    Gender.FEMALE: (255, 125, 200)  # Rosa shocking
                }
            ),
            RelationshipType.CRUSH: RelationshipMetadata(
                display_names={Gender.MALE: "Cotta", Gender.FEMALE: "Cotta"},
                color={
                    Gender.MALE: (245, 152, 182),   # Rosa pallido
                    Gender.FEMALE: (255, 192, 222)  # Rosa polvere
                }
            ),
            RelationshipType.EX_PARTNER: RelationshipMetadata(
                display_names={Gender.MALE: "Ex", Gender.FEMALE: "Ex"},
                color={
                    Gender.MALE: (118, 101, 133),   # Viola ardesia
                    Gender.FEMALE: (158, 141, 173)  # Viola chiaro
                }
            ),
            # --- RELAZIONI NEGATIVE ---
            RelationshipType.ENEMY_RIVAL: RelationshipMetadata(
                display_names={Gender.MALE: "Rivale", Gender.FEMALE: "Rivale"},
                color={
                    Gender.MALE: (235, 120, 0),     # Arancio bruciato
                    Gender.FEMALE: (255, 160, 40)   # Arancio chiaro
                }
            ),
            RelationshipType.ENEMY_DISLIKED: RelationshipMetadata(
                display_names={Gender.MALE: "Antipatico", Gender.FEMALE: "Antipatica"},
                color={
                    Gender.MALE: (235, 49, 0),      # Rosso fuoco
                    Gender.FEMALE: (255, 89, 40)    # Rosso corallo
                }
            ),
            # --- RELAZIONI PROFESSIONALI / CONTESTUALI ---
            RelationshipType.COLLEAGUE: RelationshipMetadata(
                display_names={Gender.MALE: "Collega", Gender.FEMALE: "Collega"},
                color={
                    Gender.MALE: (50, 110, 160),    # Blu notte
                    Gender.FEMALE: (90, 150, 200)   # Blu cielo
                }
            ),
            RelationshipType.NEIGHBOR: RelationshipMetadata(
                display_names={Gender.MALE: "Vicino", Gender.FEMALE: "Vicina"},
                color={
                    Gender.MALE: (140, 62, 25),     # Marrone cioccolato
                    Gender.FEMALE: (180, 102, 65)   # Marrone terra
                }
            ),
            RelationshipType.MENTOR: RelationshipMetadata(
                display_names={Gender.MALE: "Mentore", Gender.FEMALE: "Mentore"},
                color={
                    Gender.MALE: (127, 92, 199),    # Viola intenso
                    Gender.FEMALE: (167, 132, 239)  # Viola pastello
                }
            ),
            RelationshipType.MENTEE: RelationshipMetadata(
                display_names={Gender.MALE: "Allievo", Gender.FEMALE: "Allieva"},
                color={
                    Gender.MALE: (156, 204, 210),   # Azzurro ghiaccio
                    Gender.FEMALE: (196, 244, 250)  # Azzurro polvere
                }
            ),
            RelationshipType.ROOMMATE: RelationshipMetadata(
                display_names={Gender.MALE: "Coinquilino", Gender.FEMALE: "Coinquilina"},
                color={
                    Gender.MALE: (164, 114, 1),     # Ocraceo scuro
                    Gender.FEMALE: (204, 154, 41)   # Ocraceo chiaro
                }
            ),
            # --- FAMIGLIA ESTESA ---
            RelationshipType.GREAT_AUNT_UNCLE: RelationshipMetadata(
                display_names={Gender.MALE: "Prozio", Gender.FEMALE: "Prozia"},
                color={
                    Gender.MALE: (119, 49, 9),       # Marrone cuoio
                    Gender.FEMALE: (159, 89, 49)     # Marrone sabbia
                }
            ),
            RelationshipType.FIRST_COUSIN_ONCE_REMOVED: RelationshipMetadata(
                display_names={Gender.MALE: "Pro-cugino", Gender.FEMALE: "Pro-cugina"},
                color={
                    Gender.MALE: (145, 22, 22),      # Bordeux
                    Gender.FEMALE: (185, 62, 62)     # Rosso mattone
                }
            ),
            RelationshipType.SECOND_COUSIN: RelationshipMetadata(
                display_names={Gender.MALE: "Cugino Lontano", Gender.FEMALE: "Cugina Lontana"},
                color={
                    Gender.MALE: (190, 160, 120),    # Beige scuro
                    Gender.FEMALE: (230, 200, 160)   # Beige chiaro
                }
            ),
        }
        return _metadata_map.get(
            self, 
            RelationshipMetadata(
                display_names={Gender.MALE: self.name, Gender.FEMALE: self.name},
                color={
                    Gender.MALE: (140, 140, 140),   # Grigio scuro
                    Gender.FEMALE: (180, 180, 180)   # Grigio chiaro
                }
            )
        )

    def display_name_it(self, gender: Gender) -> str:
        """Restituisce il nome declinato corretto."""
        return self.metadata.display_names.get(gender, self.metadata.display_names[Gender.MALE])

    def get_color(self, gender: Gender) -> Tuple[int, int, int]:
        """
        Restituisce il colore associato, specifico per genere se definito.
        """
        colors = self.metadata.color
        # Se 'colors' è un dizionario, prendi il colore per il genere specifico
        if isinstance(colors, dict):
            # Usa il colore MALE come fallback se il genere non è trovato
            return colors.get(gender, colors.get(Gender.MALE, (255, 255, 255)))
        # Altrimenti, è una tupla di colore singolo, restituiscila
        return colors