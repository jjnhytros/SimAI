# core/enums/relationship_types.py
from enum import Enum, auto

from core.enums.genders import Gender
"""
Definizione dell'Enum 'RelationshipType' per rappresentare i tipi di relazione
tra NPC in SimAI.
"""

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
    ROOMMATE = auto()                   # Coinquilino (se rilevante)

    AUNT_UNCLE = 100
    NEPHEW_NIECE = 101
    
    COUSIN = 110
    
    GREAT_AUNT_UNCLE = 120
    FIRST_COUSIN_ONCE_REMOVED = 121
    
    SECOND_COUSIN = 130

    def display_name_it(self, gender: Gender) -> str:
        """Restituisce un nome leggibile e declinato per il tipo di relazione."""
        mapping = {
            # --- FAMIGLIA NUCLEARE ---
            RelationshipType.PARENT: "Genitore",
            RelationshipType.CHILD: {Gender.MALE: "Figlio", Gender.FEMALE: "Figlia"},
            RelationshipType.SPOUSE: "Coniuge",
            RelationshipType.SIBLING: {Gender.MALE: "Fratello", Gender.FEMALE: "Sorella"},

            # --- FAMIGLIA DIRETTA ESTESA (Nonni, Nipoti di nonni) ---
            RelationshipType.GRANDPARENT: {Gender.MALE: "Nonno", Gender.FEMALE: "Nonna"},
            RelationshipType.GRANDCHILD: {Gender.MALE: "Nipote", Gender.FEMALE: "Nipote"}, # (di nonni)
            RelationshipType.GREAT_GRANDPARENT: {Gender.MALE: "Bisnonno", Gender.FEMALE: "Bisnonna"},
            RelationshipType.GREAT_GRANDCHILD: {Gender.MALE: "Pronipote", Gender.FEMALE: "Pronipote"},
            RelationshipType.GREAT_GREAT_GRANDPARENT: {Gender.MALE: "Trisnonno", Gender.FEMALE: "Trisnonna"},
            RelationshipType.GREAT_GREAT_GRANDCHILD: {Gender.MALE: "Bis-pronipote", Gender.FEMALE: "Bis-pronipote"},

            # --- FAMIGLIA COLLATERALE (Zii, Cugini, Nipoti di zii) ---
            RelationshipType.AUNT_UNCLE: {Gender.MALE: "Zio", Gender.FEMALE: "Zia"},
            RelationshipType.NEPHEW_NIECE: {Gender.MALE: "Nipote", Gender.FEMALE: "Nipote"}, # (di zii)
            RelationshipType.COUSIN: {Gender.MALE: "Cugino", Gender.FEMALE: "Cugina"},
            RelationshipType.GREAT_AUNT_UNCLE: {Gender.MALE: "Prozio", Gender.FEMALE: "Prozia"},
            RelationshipType.FIRST_COUSIN_ONCE_REMOVED: {Gender.MALE: "Cugino di 2° Grado", Gender.FEMALE: "Cugina di 2° Grado"}, # Esempio di traduzione
            RelationshipType.SECOND_COUSIN: {Gender.MALE: "Cugino di 3° Grado", Gender.FEMALE: "Cugina di 3° Grado"}, # Esempio di traduzione

            # --- ALTRE RELAZIONI ---
            RelationshipType.EXTENDED_FAMILY: "Parente",
            RelationshipType.ACQUAINTANCE: "Conoscente",
            RelationshipType.FRIEND_CLOSE: {Gender.MALE: "Amico Stretto", Gender.FEMALE: "Amica Stretta"},
            RelationshipType.FRIEND_REGULAR: {Gender.MALE: "Amico", Gender.FEMALE: "Amica"},
            RelationshipType.ROMANTIC_PARTNER: {Gender.MALE: "Partner", Gender.FEMALE: "Partner"},
            RelationshipType.EX_PARTNER: {Gender.MALE: "Ex Partner", Gender.FEMALE: "Ex Partner"},
            RelationshipType.CRUSH: "Cotta",
            RelationshipType.ENEMY_RIVAL: "Rivale",
            RelationshipType.ENEMY_DISLIKED: "Antipatia",
            RelationshipType.COLLEAGUE: "Collega",
            RelationshipType.NEIGHBOR: {Gender.MALE: "Vicino di Casa", Gender.FEMALE: "Vicina di Casa"},
            RelationshipType.MENTOR: "Mentore",
            RelationshipType.MENTEE: {Gender.MALE: "Allievo", Gender.FEMALE: "Allieva"},
            RelationshipType.ROOMMATE: {Gender.MALE: "Coinquilino", Gender.FEMALE: "Coinquilina"},
        }
        
        value = mapping.get(self)

        if isinstance(value, dict):
            return value.get(gender, value.get(Gender.MALE, "N/D"))
        elif isinstance(value, str):
            return value
        else:
            return self.name.replace("_", " ").title()
