# core/config/actions_config.py
"""
Configurazioni di default per le azioni degli NPC.
"""

from core.enums import FunActivityType, ObjectType, SkillType

# --- EatAction ---
# Guadagno di default per il bisogno HUNGER quando si completa un'azione generica di mangiare.
EAT_ACTION_DEFAULT_DURATION_HOURS = 0.5 # Mezz'ora di gioco
EAT_ACTION_DEFAULT_HUNGER_GAIN = 75.0
# EAT_ACTION_DEFAULT_DURATION_TICKS = ... (se preferisci definirlo direttamente in tick)

# --- DrinkAction ---
DRINK_DEFAULT_DURATION_HOURS = 0.2
DRINK_DEFAULT_THIRST_GAIN = 40.0
DRINK_DEFAULT_BLADDER_EFFECT = -10.0 # Negativo per aumentare il riempimento della vescica

DRINK_WATER_DURATION_HOURS = 0.2
DRINK_WATER_THIRST_GAIN = 60.0
DRINK_WATER_BLADDER_EFFECT = -15.0

DRINK_JUICE_DURATION_HOURS = 0.25
DRINK_JUICE_THIRST_GAIN = 45.0
DRINK_JUICE_FUN_GAIN = 10.0
DRINK_JUICE_BLADDER_EFFECT = -12.0

# Default per attività non configurate specificamente
HAVEFUN_DEFAULT_FUN_GAIN = 25.0
HAVEFUN_DEFAULT_DURATION_HOURS = 1.0

# Mappa di configurazione per ogni attività di divertimento
HAVEFUN_ACTIVITY_CONFIGS = {
    # ... (configurazioni per WATCH_TV, READ_BOOK_FOR_FUN) ...
    
    FunActivityType.PLAY_GUITAR: { # Esempio di attività futura
        "fun_gain": 40.0,
        "duration_hours": 1.0,
        "required_object_types": (ObjectType.GUITAR,),
        "skill_to_practice": SkillType.GUITAR, # <-- ORA SkillType è definito
        "xp_gain": 50.0,
    },
    FunActivityType.DAYDREAM: {
        "fun_gain": 15.0,
        "duration_hours": 0.5,
        "required_object_types": None,
        "skill_to_practice": SkillType.IMAGINATION_TODDLER, # <-- ORA SkillType è definito
        "xp_gain": 10.0
    },
    # ... config per tutte le altre FunActivityType ...
}
