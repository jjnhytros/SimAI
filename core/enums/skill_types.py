# core/enums/skill_types.py
"""
Definizione dell'Enum 'SkillType' per rappresentare i tipi di abilità
che gli NPC possono sviluppare in SimAI.
Riferimento TODO: IX.a.i, IX.e
"""
from enum import Enum, auto

class SkillType(Enum):
    # Mental
    LOGIC = auto()
    PROGRAMMING = auto()
    WRITING = auto()
    RESEARCH_DEBATE = auto() # Ricerca e Dibattito
    ROCKET_SCIENCE = auto()
    # Aggiungere: MATHEMATICS, LINGUISTICS, HISTORY, PHILOSOPHY, SCIENCE (generica)

    # Physical
    FITNESS = auto()
    DANCING = auto()
    SKIING = auto()
    ROCK_CLIMBING = auto()
    WELLNESS = auto() # Include Yoga, Meditazione
    MARTIAL_ARTS = auto()
    SWIMMING = auto()

    # Social
    CHARISMA = auto()
    COMEDY = auto()
    MISCHIEF = auto() # Malizia
    PARENTING = auto()
    NEGOTIATION = auto()
    SEDUCTION = auto()
    SOCIAL_MEDIA = auto()
    TEACHING = auto()

    # Creative
    PAINTING = auto()
    GUITAR = auto()
    PIANO = auto()
    VIOLIN = auto()
    DRUMS = auto() # Batteria (era Battery Drum)
    SINGING = auto()
    DJ_MIXING = auto()
    PHOTOGRAPHY = auto()
    FABRICATION = auto() # Fabbricazione (es. con stampante 3D)
    FLOWER_ARRANGING = auto()
    WRITING_CREATIVE = auto() # Potrebbe essere separata da WRITING (saggistica/tecnica)
    
    # Practical
    COOKING = auto()
    GOURMET_COOKING = auto()
    BAKING = auto()
    MIXOLOGY = auto() # Preparazione drink
    HANDINESS = auto() # Manualità, riparazioni
    HERBALISM = auto()
    GARDENING = auto()
    FISHING = auto()
    POTTERY = auto()
    KNITTING = auto()
    WOODWORKING = auto() # Lavorazione legno
    MECHANICS = auto() # Meccanica (auto, macchinari)

    # Children (specifiche per bambini)
    CREATIVITY_CHILD = auto()
    MENTAL_CHILD = auto()
    MOTOR_CHILD = auto()
    SOCIAL_CHILD = auto()

    # Toddlers (specifiche per toddler)
    COMMUNICATION_TODDLER = auto()
    IMAGINATION_TODDLER = auto()
    MOVEMENT_TODDLER = auto()
    POTTY_TODDLER = auto()
    THINKING_TODDLER = auto()
    
    # Professional (alcune potrebbero sovrapporsi, ma indicano focus lavorativo)
    VETERINARIAN = auto() # Richiede DLC C.5
    MEDICAL = auto()      # Medicina generale
    ARCHAEOLOGY = auto()
    BOTANY = auto()

    def display_name_it(self) -> str:
        # Mappatura parziale, da espandere o rendere più generica
        mapping = {
            SkillType.LOGIC: "Logica", SkillType.FITNESS: "Fitness", SkillType.CHARISMA: "Carisma",
            SkillType.PAINTING: "Pittura", SkillType.COOKING: "Cucina",
            SkillType.MOTOR_CHILD: "Abilità Motorie (Bambino)",
            SkillType.MOVEMENT_TODDLER: "Movimento (Toddler)",
            SkillType.ROCKET_SCIENCE: "Scienza Missilistica",
            SkillType.RESEARCH_DEBATE: "Ricerca e Dibattito",
            SkillType.WRITING_CREATIVE: "Scrittura Creativa"
            # ...ecc...
        }
        return mapping.get(self, self.name.replace("_", " ").title())