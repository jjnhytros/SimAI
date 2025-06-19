# core/config/skills_config.py
"""
Configurazioni per il sistema di Abilità (Skills).
Definisce la progressione, i livelli massimi e altre regole di bilanciamento.
"""
from core.enums import SkillType
from core.enums.trait_types import TraitType

# Livello massimo di default per la maggior parte delle abilità
DEFAULT_SKILL_MAX_LEVEL = 12

# Livelli massimi specifici per abilità che fanno eccezione
# Alcune skill hanno diversi MAX_LEVELS (sempre divisori o multipli di 12 [1,2,3,4,6,12,18,24,36,...])
SKILL_SPECIFIC_MAX_LEVELS = {
    # SkillType.POTTY_TODDLER: 3,
    # SkillType.BOWLING: 6,
    # Aggiungi qui altre eventuali eccezioni
}

def _generate_xp_curve(max_level=144, base_xp=120, exponent=1.8) -> dict[int, int]:
    """
    Genera un dizionario di XP cumulativo necessario per ogni livello.
    
    Args:
        max_level: Il livello massimo per cui generare i dati.
        base_xp: L'XP necessario per il primo livello (da 1 a 2).
        exponent: Controlla quanto ripidamente aumenta la difficoltà.
                    Valori comuni sono tra 1.5 (più facile) e 2.5 (più difficile).
    
    Returns:
        Un dizionario {livello: xp_totale_necessario}.
    """
    xp_map = {1: 0}
    for level in range(2, max_level + 1):
        # Formula per XP cumulativo basata sul livello precedente
        required_for_this_level = base_xp * ((level - 1) ** exponent)
        # Arrotondiamo a un multiplo di 12 per coerenza con la nostra teoria
        rounded_xp = int(round(required_for_this_level / 12) * 12)
        xp_map[level] = xp_map[level - 1] + rounded_xp
    return xp_map

# Definisce l'XP TOTALE CUMULATIVO necessario per raggiungere un dato livello.
# Ora viene generato automaticamente, supportando fino al livello 144.
XP_PER_LEVEL = _generate_xp_curve()

# Bonus iniziali per tratti specifici (struttura per il futuro)
SKILL_INITIAL_LEVEL_BONUS = {
    TraitType.CREATIVE: {
        SkillType.PAINTING: {"level": 2, "xp": XP_PER_LEVEL[2]},
    },
    TraitType.GOOD: { # Esempio: Il tratto "Buono" non dà bonus diretti alle skill
        SkillType.CHARISMA: {"level": 1, "xp": 60}, # Ma potrebbe dare un piccolo boost iniziale
    },
}

