# simai/game/src/modules/needs/hunger.py
# MODIFIED: Corrected import for _base_need. Made debug prints conditional.
# MODIFIED: Ensured critical imports lead to sys.exit().

import sys

try:
    from game.src.modules.needs._base_need import BaseNeed # <--- IMPORT CORRETTO
    from game import config as game_config
except ImportError as e:
    print(f"CRITICAL ERROR (HungerNeed): Could not import _base_need.BaseNeed or game_config: {e}")
    print("Ensure 'game.config' and 'game.src.modules.needs._base_need' are accessible and correctly named.")
    sys.exit()

# Leggi il flag di debug una volta, dopo aver importato config
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
            high_is_good=getattr(game_config, 'HUNGER_HIGH_IS_GOOD', False), 
            name="Hunger"
        )
        if DEBUG_VERBOSE:
            owner_name = "UnknownChar"
            if hasattr(self.character_owner, 'name'): owner_name = self.character_owner.name
            elif self.character_owner is not None: owner_name = str(self.character_owner)
            # La stampa di BaseNeed.__init__ include già il nome del bisogno.
            # Questa è solo se vuoi loggare qualcosa di specifico per Hunger qui.
            # print(f"HUNGER_NEED_INIT ({owner_name}): Initialized specific. Value: {self.get_value():.2f}")

    # Eventuali override o metodi specifici di Hunger con stampe if DEBUG_VERBOSE:
    # ...