# core/enums/relationship_types.py
"""
Definizione dell'Enum 'RelationshipType' per rappresentare i tipi di relazione
tra NPC in SimAI.
"""
from enum import Enum, auto

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
    # ROOMMATE = auto()                 # Coinquilino (se rilevante)

    def display_name_it(self) -> str:
        mapping = {
            RelationshipType.PARENT: "Genitore",
            RelationshipType.CHILD: "Figlio/a",
            RelationshipType.GRANDPARENT: "Nonno/a",
            RelationshipType.GRANDCHILD: "Nipote (di nonni)",
            RelationshipType.GREAT_GRANDPARENT: "Bisnonno/a",
            RelationshipType.GREAT_GRANDCHILD: "Pronipote (di bisnonni)",
            RelationshipType.GREAT_GREAT_GRANDPARENT: "Trisnonno/a",
            RelationshipType.GREAT_GREAT_GRANDCHILD: "Figlio/a di Pronipote",
            RelationshipType.SIBLING: "Fratello/Sorella",
            RelationshipType.SPOUSE: "Coniuge",
            RelationshipType.EXTENDED_FAMILY: "Parente Esteso",
            RelationshipType.FRIEND_CLOSE: "Amico Stretto",
            RelationshipType.FRIEND_REGULAR: "Amico",
            RelationshipType.ACQUAINTANCE: "Conoscente",
            RelationshipType.ROMANTIC_PARTNER: "Partner Romantico",
            RelationshipType.CRUSH: "Cotta",
            RelationshipType.EX_PARTNER: "Ex Partner",
            RelationshipType.ENEMY_RIVAL: "Nemico/Rivale",
            RelationshipType.ENEMY_DISLIKED: "Antipatia",
            RelationshipType.COLLEAGUE: "Collega",
            RelationshipType.NEIGHBOR: "Vicino di Casa",
            RelationshipType.MENTOR: "Mentore",
            RelationshipType.MENTEE: "Allievo",
        }
        return mapping.get(self, self.name.replace("_", " ").title())

    def is_direct_family_link(self) -> bool:
        """Indica se è un legame familiare diretto (ascendente/discendente/coniuge/fratello)."""
        return self in {
            RelationshipType.PARENT, RelationshipType.CHILD,
            RelationshipType.GRANDPARENT, RelationshipType.GRANDCHILD,
            RelationshipType.GREAT_GRANDPARENT, RelationshipType.GREAT_GRANDCHILD,
            RelationshipType.GREAT_GREAT_GRANDPARENT, RelationshipType.GREAT_GREAT_GRANDCHILD,
            RelationshipType.SIBLING, RelationshipType.SPOUSE
        }