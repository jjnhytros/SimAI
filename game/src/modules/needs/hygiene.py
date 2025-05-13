# simai/game/modules/needs/hygiene.py
# Need for Hygiene: 0 = dirty (bad state), 100 = clean (good state)

from ._base_need import BaseNeed

class Hygiene(BaseNeed):
    def __init__(self, owner_character, max_value: float, 
                 initial_fill_min_pct: float, initial_fill_max_pct: float, 
                 base_rate_per_hour: float, # This is the base *decay* rate
                 rate_multipliers_dict: dict):
        super().__init__(owner_character=owner_character,
                         name="Hygiene", 
                         max_value=max_value, 
                         initial_fill_min_pct=initial_fill_min_pct,
                         initial_fill_max_pct=initial_fill_max_pct,
                         base_rate_per_hour=base_rate_per_hour, 
                         is_value_high_good=True, # High hygiene value is good
                         rate_multipliers_dict=rate_multipliers_dict)

    # BaseNeed's update() (with is_value_high_good=True) correctly decreases the value (hygiene decays).
    # BaseNeed's satisfy() (with is_value_high_good=True) correctly increases the value.