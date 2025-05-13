# simai/game/modules/needs/hunger.py
# Need for Hunger: 0 = not hungry (good state), 100 = starving (bad state)

from ._base_need import BaseNeed

class Hunger(BaseNeed):
    def __init__(self, owner_character, max_value: float, 
                 initial_fill_min_pct: float, initial_fill_max_pct: float, 
                 base_rate_per_hour: float, 
                 rate_multipliers_dict: dict):
        super().__init__(owner_character=owner_character, 
                         name="Hunger", 
                         max_value=max_value, 
                         initial_fill_min_pct=initial_fill_min_pct, 
                         initial_fill_max_pct=initial_fill_max_pct,
                         base_rate_per_hour=base_rate_per_hour, 
                         is_value_high_good=False, # High hunger value is bad
                         rate_multipliers_dict=rate_multipliers_dict)

    # BaseNeed's update() method (with is_value_high_good=False) correctly increases hunger.
    # BaseNeed's satisfy() method (with is_value_high_good=False) correctly decreases hunger (eating).