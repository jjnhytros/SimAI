# simai/game/src/modules/needs/hunger.py
# MODIFIED: Made debug prints conditional (if any specific to this class exist)

import sys
try:
    from game.src.modules.needs._base_need import BaseNeed
    from game import config as game_config # Per accedere a DEBUG_AI_ACTIVE
except ImportError:
    print("CRITICAL ERROR (HungerNeed): Could not import BaseNeed or game_config.")
    # Fallback minimale per BaseNeed se necessario per test isolati, ma indica problemi
    class BaseNeed:
        def __init__(self, *args, **kwargs): pass
        def update(self, *args, **kwargs): pass
        def satisfy(self, *args, **kwargs): pass
        def get_value(self): return 50.0
        def get_goodness_factor(self): return 0.5
        def to_dict(self): return {}
    # Config non ha un fallback semplice qui se non importato
    # game_config = None # o un placeholder se strettamente necessario
    sys.exit()


# Leggi il flag di debug una volta
DEBUG_VERBOSE = False
if game_config: # Assicurati che game_config sia stato importato
    DEBUG_VERBOSE = getattr(game_config, 'DEBUG_AI_ACTIVE', False)


class Hunger(BaseNeed):
    def __init__(self, character_owner, max_value, 
                 initial_min_percentage, initial_max_percentage, 
                 base_rate, rate_multipliers):
        super().__init__(
            character_owner=character_owner,
            max_value=max_value,
            initial_min_percentage=initial_min_percentage,
            initial_max_percentage=initial_max_percentage,
            base_rate=base_rate,
            rate_multipliers=rate_multipliers,
            high_is_good=getattr(game_config, 'HUNGER_HIGH_IS_GOOD', False), # Alto valore di fame è CATTIVO
            name="Hunger"
        )
        # Stampe specifiche per Hunger (se ce ne sono) dovrebbero usare DEBUG_VERBOSE
        if DEBUG_VERBOSE:
            print(f"Hunger specific init for {character_owner.name}")

    # Override di update o satisfy se Hunger ha una logica di debug specifica
    # Esempio:
    def update(self, hours_passed: float, current_period_name: str = None, 
               character_action: str = "idle", character_is_resting: bool = False):
        super().update(hours_passed, current_period_name, character_action, character_is_resting)
        if DEBUG_VERBOSE and self.get_value() > 80:
            print(f"HUNGER_DEBUG ({self.character_owner.name}): Extremely hungry! Value: {self.get_value():.1f}")