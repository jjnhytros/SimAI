# simai/game/modules/needs/intimacy.py
# Need for Intimacy (Drive): 0 = low drive (good state), 100 = high drive (bad state, needs satisfaction)

from ._base_need import BaseNeed

class Intimacy(BaseNeed): 
    def __init__(self, owner_character, max_value: float, 
                 initial_fill_min_pct: float, initial_fill_max_pct: float, 
                 base_rate_per_hour: float, # This is the base *increase* rate for the drive
                 rate_multipliers_dict: dict):
        super().__init__(owner_character=owner_character,
                         name="Intimacy", 
                         max_value=max_value, 
                         initial_fill_min_pct=initial_fill_min_pct, 
                         initial_fill_max_pct=initial_fill_max_pct,
                         base_rate_per_hour=base_rate_per_hour, 
                         is_value_high_good=False, # High drive value is a "need to satisfy" state
                         rate_multipliers_dict=rate_multipliers_dict)

    def update(self, game_hours_advanced: float, period_name: str, 
               character_action: str = "idle", is_char_externally_resting: bool = False):
        # Intimacy drive increases if not in a satisfying interaction or specific blocking states.
        # The actual satisfaction is handled by calling self.satisfy() from AI/Character methods
        # after a successful romantic/affectionate interaction.
        if character_action not in ["romantic_interaction_action", "affectionate_interaction_action"]:
            super().update(game_hours_advanced, period_name, character_action, is_char_externally_resting)
    
    # BaseNeed's satisfy() (with is_value_high_good=False) correctly decreases the drive.