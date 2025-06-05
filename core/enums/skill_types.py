# core/enums/skill_types.py
"""
Definizione dell'Enum 'SkillType' per rappresentare i tipi di abilità
che gli NPC possono sviluppare in SimAI.
"""
from enum import Enum, auto

class SkillType(Enum):
    """Enum per i diversi tipi di abilità (skills)."""
    
    # --- Skill Mentali ---
    LOGIC = auto()
    PROGRAMMING = auto()
    RESEARCH_DEBATE = auto() # Ricerca e Dibattito
    ROCKET_SCIENCE = auto()
    WRITING = auto()

    # --- Skill Fisiche ---
    FITNESS = auto()
    DANCING = auto()
    SKIING = auto()
    ROCK_CLIMBING = auto()
    WELLNESS = auto() # Benessere (Yoga, Meditazione)

    # --- Skill Sociali ---
    CHARISMA = auto()
    COMEDY = auto()
    MISCHIEF = auto() # Malizia
    PARENTING = auto()
    
    # --- Skill Creative ---
    PAINTING = auto()
    GUITAR = auto()
    PIANO = auto()
    VIOLIN = auto()
    SINGING = auto()
    PHOTOGRAPHY = auto()
    FABRICATION = auto() # Fabbricazione
    
    # --- Skill Pratiche ---
    COOKING = auto()
    GOURMET_COOKING = auto()
    BAKING = auto()
    MIXOLOGY = auto() # Preparazione drink
    HANDINESS = auto() # Manualità
    HERBALISM = auto()
    GARDENING = auto()
    FISHING = auto()
    POTTERY = auto()

    # --- Skill per Bambini (Child) ---
    CREATIVITY_CHILD = auto()
    MENTAL_CHILD = auto()
    MOTOR_CHILD = auto()
    SOCIAL_CHILD = auto()

    # --- Skill per Toddler ---
    COMMUNICATION_TODDLER = auto()
    IMAGINATION_TODDLER = auto()
    MOVEMENT_TODDLER = auto()
    POTTY_TODDLER = auto()
    THINKING_TODDLER = auto()

    # ... Aggiungi qui altre skill dalla tua lista TODO IX.e man mano ...

    def display_name_it(self) -> str:
        """Restituisce un nome leggibile in italiano per la skill."""
        # Usa una mappa per le traduzioni specifiche, con un fallback generico
        mapping = {
            SkillType.LOGIC: "Logica",
            SkillType.PROGRAMMING: "Programmazione",
            SkillType.RESEARCH_DEBATE: "Ricerca e Dibattito",
            SkillType.ROCKET_SCIENCE: "Scienza Missilistica",
            SkillType.WRITING: "Scrittura",
            SkillType.FITNESS: "Fitness",
            SkillType.DANCING: "Ballo",
            SkillType.CHARISMA: "Carisma",
            SkillType.COMEDY: "Commedia",
            SkillType.PARENTING: "Genitorialità",
            SkillType.PAINTING: "Pittura",
            SkillType.GUITAR: "Chitarra",
            SkillType.COOKING: "Cucina",
            SkillType.GOURMET_COOKING: "Cucina Gourmet",
            SkillType.BAKING: "Pasticceria",
            SkillType.MIXOLOGY: "Mixologia",
            SkillType.HANDINESS: "Manualità",
            SkillType.GARDENING: "Giardinaggio",
            SkillType.FISHING: "Pesca",
            SkillType.MOTOR_CHILD: "Abilità Motorie (Bambino)",
            SkillType.MOVEMENT_TODDLER: "Movimento (Toddler)",
        }
        return mapping.get(self, self.name.replace("_", " ").title())
