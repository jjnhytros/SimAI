# core/enums/skill_types.py
from enum import Enum, auto
"""
Definizione dell'Enum 'SkillType' per rappresentare i tipi di abilità
che gli NPC possono sviluppare in SimAI.
"""

class SkillType(Enum):
    """Enum per i diversi tipi di abilità (skills)."""

    # --- Skill Mentali ---
    LOGIC = auto()
    PROGRAMMING = auto()
    RESEARCH_DEBATE = auto() # Ricerca e Dibattito
    ROCKET_SCIENCE = auto()
    WRITING = auto()

    # --- Skill Fisiche ---
    DANCING = auto()
    FITNESS = auto()
    MARTIAL_ARTS = auto()
    ROCK_CLIMBING = auto()
    SKIING = auto()
    SWIMMING = auto()
    WELLNESS = auto() # Benessere (Yoga, Meditazione)

    # --- Skill Sociali ---
    CHARISMA = auto()
    COMEDY = auto()
    MISCHIEF = auto() # Malizia
    NEGOTIATION = auto()
    PARENTING = auto()
    SEDUCTION = auto()
    SOCIAL_MEDIA = auto()
    TEACHING = auto()

    # --- Skill Creative ---
    DJ_MIXING = auto()
    DRUMS = auto()
    FABRICATION = auto() # Fabbricazione
    FLOWER_ARRANGING = auto()
    GUITAR = auto()
    PAINTING = auto()
    PHOTOGRAPHY = auto()
    PIANO = auto()
    SINGING = auto()
    VIOLIN = auto()
    WRITING_CREATIVE = auto()
    
    # --- Skill Pratiche ---
    BAKING = auto()
    COOKING = auto()
    FISHING = auto()
    GARDENING = auto()
    GOURMET_COOKING = auto()
    HANDINESS = auto() # Manualità
    HERBALISM = auto()
    KNITTING = auto()
    MECHANICS = auto()
    MIXOLOGY = auto() # Preparazione drink
    POTTERY = auto()
    WOODWORKING = auto()

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
    
    # --- Skill Professionali ---
    ARCHAEOLOGY = auto()
    BOTANY = auto()
    MEDICAL = auto()
    VETERINARIAN = auto()



    # ... Aggiungi qui altre skill dalla tua lista TODO IX.e man mano ...

    def display_name_it(self) -> str:
        """Restituisce un nome leggibile in italiano per la skill."""
        mapping = {
            # Mentali
            SkillType.LOGIC: "Logica",
            SkillType.PROGRAMMING: "Programmazione",
            SkillType.RESEARCH_DEBATE: "Ricerca e Dibattito",
            SkillType.ROCKET_SCIENCE: "Scienza Missilistica",
            SkillType.WRITING: "Scrittura Tecnica",

            # Fisiche
            SkillType.DANCING: "Ballo",
            SkillType.FITNESS: "Fitness",
            SkillType.MARTIAL_ARTS: "Arti Marziali",
            SkillType.ROCK_CLIMBING: "Arrampicata",
            SkillType.SKIING: "Sci",
            SkillType.SWIMMING: "Nuoto",
            SkillType.WELLNESS: "Benessere",

            # Sociali
            SkillType.CHARISMA: "Carisma",
            SkillType.COMEDY: "Commedia",
            SkillType.MISCHIEF: "Malizia",
            SkillType.NEGOTIATION: "Negoziazione",
            SkillType.PARENTING: "Genitorialità",
            SkillType.SEDUCTION: "Seduzione",
            SkillType.SOCIAL_MEDIA: "Social Media",
            SkillType.TEACHING: "Insegnamento",

            # Creative
            SkillType.DJ_MIXING: "Mixaggio DJ",
            SkillType.DRUMS: "Batteria",
            SkillType.FABRICATION: "Fabbricazione Digitale",
            SkillType.FLOWER_ARRANGING: "Composizione Floreale",
            SkillType.GUITAR: "Chitarra",
            SkillType.PAINTING: "Pittura",
            SkillType.PHOTOGRAPHY: "Fotografia",
            SkillType.PIANO: "Pianoforte",
            SkillType.SINGING: "Canto",
            SkillType.VIOLIN: "Violino",
            SkillType.WRITING_CREATIVE: "Scrittura Creativa",

            # Pratiche
            SkillType.BAKING: "Pasticceria",
            SkillType.COOKING: "Cucina",
            SkillType.FISHING: "Pesca",
            SkillType.GARDENING: "Giardinaggio",
            SkillType.GOURMET_COOKING: "Cucina Gourmet",
            SkillType.HANDINESS: "Manualità",
            SkillType.HERBALISM: "Erboristeria",
            SkillType.KNITTING: "Lavoro a Maglia",
            SkillType.MECHANICS: "Meccanica",
            SkillType.MIXOLOGY: "Mixologia",
            SkillType.POTTERY: "Ceramica",
            SkillType.WOODWORKING: "Lavorazione del Legno",

            # Bambini
            SkillType.CREATIVITY_CHILD: "Creatività (Bambino)",
            SkillType.MENTAL_CHILD: "Mentale (Bambino)",
            SkillType.MOTOR_CHILD: "Abilità Motorie (Bambino)",
            SkillType.SOCIAL_CHILD: "Sociale (Bambino)",

            # Toddler
            SkillType.COMMUNICATION_TODDLER: "Comunicazione (Toddler)",
            SkillType.IMAGINATION_TODDLER: "Immaginazione (Toddler)",
            SkillType.MOVEMENT_TODDLER: "Movimento (Toddler)",
            SkillType.POTTY_TODDLER: "Uso del Vasino (Toddler)",
            SkillType.THINKING_TODDLER: "Pensiero (Toddler)",

            # Professionali
            SkillType.ARCHAEOLOGY: "Archeologia",
            SkillType.BOTANY: "Botanica",
            SkillType.MEDICAL: "Medicina",
            SkillType.VETERINARIAN: "Veterinaria",
        }
        return mapping.get(self, self.name.replace("_", " ").title())
