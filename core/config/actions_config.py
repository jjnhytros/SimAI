# core/config/actions_config.py
"""
Configurazioni di default per le azioni degli NPC.
"""

# --- HaveFunAction ---
# Guadagno di default per il bisogno FUN quando si completa un'azione generica di divertimento
DEFAULT_HAVEFUNACTION_FUN_GAIN: float = 35.0

# Guadagni specifici per attività (opzionale, per un tuning più fine)
# Esempio: FUN_ACT_READ_BOOK_FUN_GAIN: float = 40.0
# Esempio: FUN_ACT_DANCE_FUN_GAIN: float = 30.0

# Durate specifiche in tick (opzionale)
# Esempio: FUN_ACT_READ_BOOK_DURATION_TICKS: int = 240 # 2 ore se IXH è 120