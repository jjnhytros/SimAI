# simai/game/modules/needs/bladder.py
# Need for Bladder: 0 = empty (good state), 100 = full (bad state, urgent)

from ._base_need import BaseNeed

class Bladder(BaseNeed):
    def __init__(self, owner_character, max_value: float, 
                 initial_fill_min_pct: float, initial_fill_max_pct: float, 
                 base_rate_per_hour: float, 
                 rate_multipliers_dict: dict):
        super().__init__(owner_character=owner_character,
                         name="Bladder", 
                         max_value=max_value, 
                         initial_fill_min_pct=initial_fill_min_pct, 
                         initial_fill_max_pct=initial_fill_max_pct,
                         base_rate_per_hour=base_rate_per_hour, 
                         is_value_high_good=False, 
                         rate_multipliers_dict=rate_multipliers_dict)

    # BaseNeed's update() (with is_value_high_good=False) correctly increases the value (fills up).
    # BaseNeed's satisfy() (with is_value_high_good=False) correctly decreases the value (empties).