# core/config/skills_config.py
from core.enums.skill_types import SkillType # Importa il tuo SkillType Enum

# --- SKILL SYSTEM CONFIGURATION ---
DEFAULT_SKILL_MAX_LEVEL = 10 # Livello massimo di default per le skill

# Livelli massimi specifici per skill (se diversi dal default)
SKILL_MAX_LEVELS = {
    SkillType.COOKING: 10,
    SkillType.LOGIC: 10,
    SkillType.ROCKET_SCIENCE: 12, # Esempio di skill con più livelli
    SkillType.MOTOR_CHILD: 5,
    SkillType.MOVEMENT_TODDLER: 5,
    SkillType.POTTY_TODDLER: 3,
}

# XP CUMULATIVO richiesto per raggiungere ogni livello.
# L'indice 0 è per il livello 1, l'indice 1 per il livello 2, ecc.
# Assicurati che la lunghezza della lista sia uguale al max_level per quella skill.
DEFAULT_SKILL_XP_SCHEDULE = [100, 250, 500, 800, 1200, 1700, 2300, 3000, 3800, 5000] # Per 10 livelli

SKILL_XP_PER_LEVEL = {
    SkillType.COOKING: [100, 220, 450, 700, 1000, 1400, 1900, 2500, 3200, 4000], # Esempio personalizzato
    SkillType.LOGIC: DEFAULT_SKILL_XP_SCHEDULE, # Usa lo schedule di default
    SkillType.MOTOR_CHILD: [50, 120, 200, 300, 450], # XP per 5 livelli
    # ... definisci schedule per altre skill se necessario, altrimenti usano DEFAULT_SKILL_XP_SCHEDULE
    # adattato al loro SKILL_MAX_LEVELS se diverso da DEFAULT_SKILL_MAX_LEVEL.
    # (La logica in BaseSkill dovrebbe gestire l'adattamento o potresti definire schedule completi qui)
}

# Bonus iniziali per alcune skill (opzionale)
SKILL_INITIAL_LEVEL_BONUS = {
    # SkillType.LOGIC: {"level": 1, "xp": 10.0}, # Esempio: Inizia Logica a liv 1 con 10xp
}

# ...