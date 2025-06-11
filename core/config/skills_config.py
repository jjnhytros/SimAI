# core/config/skills_config.py
"""
Configurazioni per il sistema di Abilità (Skills).
Definisce la progressione, i livelli massimi e altre regole di bilanciamento.
"""
from core.enums import SkillType

# Livello massimo di default per la maggior parte delle abilità
DEFAULT_SKILL_MAX_LEVEL = 12

# Livelli massimi specifici per abilità che fanno eccezione
SKILL_SPECIFIC_MAX_LEVELS = {
    # SkillType.POTTY_TODDLER: 3,
    # SkillType.BOWLING: 6,
    # Aggiungi qui altre eventuali eccezioni
}

# Definisce l'XP TOTALE CUMULATIVO necessario per raggiungere un dato livello.
# Esempio: Per raggiungere il livello 3, un NPC deve avere accumulato in totale 250 XP.
XP_PER_LEVEL = {
    1: 0,        # Livello 1 si inizia con 0 XP
    2: 100,      # Raggiungi il Lvl 2 a 100 XP totali
    3: 200,      # Raggiungi il Lvl 3 a 200 XP totali
    4: 400,
    5: 800,
    6: 1600,
    7: 3200,
    8: 6400,
    9: 12800,
    10: 25600,
    11: 51200,
    12: 102400,
    13: 204800,
    14: 409600,
    15: 819200,
    16: 1638400,
    17: 3276800,
    18: 6553600,
    19: 13107200,
    20: 26214400,
    21: 52428800,
    22: 104857600,
    23: 209715200,
    24: 419430400,
}

# Bonus iniziali per tratti specifici (da implementare in futuro)
# Esempio di struttura:
# SKILL_INITIAL_LEVEL_BONUS = {
#     TraitType.GENIUS: {
#         SkillType.LOGIC: {"level": 2, "xp": 100},
#     }
# }