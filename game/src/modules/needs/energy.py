# simai/game/modules/needs/energy.py
# Need for Energy: 0 = exhausted (bad state), 100 = fully energized (good state)

from ._base_need import BaseNeed

class Energy(BaseNeed):
    def __init__(self, owner_character, max_value: float, 
                 initial_fill_min_pct: float, initial_fill_max_pct: float, 
                 base_rate_per_hour: float, # This is the base *decay* rate
                 rate_multipliers_dict: dict):
        super().__init__(owner_character=owner_character, 
                         name="Energy", 
                         max_value=max_value, 
                         initial_fill_min_pct=initial_fill_min_pct,
                         initial_fill_max_pct=initial_fill_max_pct,
                         base_rate_per_hour=base_rate_per_hour, 
                         is_value_high_good=True, # High energy value is good
                         rate_multipliers_dict=rate_multipliers_dict)

    def update(self, game_hours_advanced: float, period_name: str, 
               character_action: str = "idle", is_char_externally_resting: bool = False):
        # Energy only decays if the character is not in a state that prevents decay or recovers energy.
        is_actually_resting_or_blocked = is_char_externally_resting or \
                                         character_action in ["phoning", "resting_on_bed", 
                                                              "romantic_interaction_action", 
                                                              "affectionate_interaction_action"]
        
        if not is_actually_resting_or_blocked:
            super().update(game_hours_advanced, period_name, character_action, is_char_externally_resting)
        # Energy recovery is handled by the `recover` method, typically called when `character_action == "resting_on_bed"`.

    def recover(self, recovery_rate_per_hour: float, hours_slept_sim: float):
        """Specific method to recover energy (e.g., while sleeping)."""
        amount_to_recover = recovery_rate_per_hour * hours_slept_sim
        self.satisfy(amount_to_recover) # Uses BaseNeed's satisfy method, which increases for high_is_good=True