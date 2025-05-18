# simai/game/src/modules/needs/energy.py
# MODIFIED: Made debug prints conditional using config.DEBUG_AI_ACTIVE.
# MODIFIED: Removed Fallback logic, critical imports will sys.exit().
# MODIFIED: Corrected import for _base_need. Made debug prints conditional.
# MODIFIED: Ensured critical imports lead to sys.exit().

import sys

try:
    from game.src.modules.needs._base_need import BaseNeed # <--- IMPORT CORRETTO

    from game import config as game_config
except ImportError as e:
    print(f"CRITICAL ERROR (EnergyNeed): Could not import BaseNeed or game_config: {e}")
    print("Ensure 'game.config' and 'game.src.modules.needs.base_need' are accessible.")
    sys.exit() # Esce se i moduli critici non sono trovati

# Leggi il flag di debug una volta, dopo aver importato config
DEBUG_VERBOSE = getattr(game_config, 'DEBUG_AI_ACTIVE', False)

class Energy(BaseNeed):
    def __init__(self, character_owner, max_value: float, 
                 initial_min_percentage: float, initial_max_percentage: float, 
                 base_rate: float, rate_multipliers: dict,
                 high_is_good: bool): # <<<< Deve accettare high_is_good
        super().__init__(character_owner, max_value, 
                         initial_min_percentage, initial_max_percentage, 
                         base_rate, rate_multipliers, 
                         high_is_good,
            name="Energy"
        )
        if DEBUG_VERBOSE:
            print(f"ENERGY_NEED_INIT ({self.character_owner.name}): Initialized. Value: {self.get_value():.2f}")


    # Il metodo update di BaseNeed gestisce il decay se high_is_good è True e base_rate è positivo.
    # Non è necessario fare override di update() a meno che l'energia non abbia una logica di decay
    # o condizioni di skip del decay molto specifiche non coperte da BaseNeed.
    # L'esempio in BaseNeed per saltare il decay di 'Energy' se si sta riposando è già lì.

    # Il metodo recover() in BaseNeed è già adatto per l'energia.
    # Non c'è bisogno di fare override qui a meno di una logica di recupero molto specifica
    # o stampe di debug aggiuntive per l'energia.

    # Esempio di override se volessi stampe specifiche per il recupero di energia:
    def recover(self, recovery_rate_per_hour: float, hours_passed: float):
        old_value = self.get_value()
        super().recover(recovery_rate_per_hour, hours_passed)
        if DEBUG_VERBOSE and abs(old_value - self.get_value()) > 0.01:
            print(f"ENERGY_RECOVER ({self.character_owner.name}): "
                  f"Recovered from {old_value:.2f} to {self.get_value():.2f} "
                  f"(Rate: {recovery_rate_per_hour:.2f}/hr for {hours_passed:.2f} hrs)")