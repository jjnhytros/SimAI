# simai/game/modules/needs/social.py
# Need for Social: 0 = lonely (bad state), 100 = socially fulfilled (good state)

from ._base_need import BaseNeed

class Social(BaseNeed):
    def __init__(self, owner_character, max_value: float, 
                 initial_fill_min_pct: float, initial_fill_max_pct: float, 
                 base_rate_per_hour: float, # This is the base *decay* rate
                 rate_multipliers_dict: dict):
        super().__init__(owner_character=owner_character, 
                         name="Social", 
                         max_value=max_value, 
                         initial_fill_min_pct=initial_fill_min_pct,
                         initial_fill_max_pct=initial_fill_max_pct,
                         base_rate_per_hour=base_rate_per_hour, 
                         is_value_high_good=True, # High social value is good
                         rate_multipliers_dict=rate_multipliers_dict)

    def update(self, game_hours_advanced: float, period_name: str, 
               character_action: str = "idle", is_char_externally_resting: bool = False):
        # Social need decays if not actively socializing.
        is_actively_socializing = character_action in ["phoning", 
                                                       "affectionate_interaction_action", # Flirting is social
                                                       "romantic_interaction_action"]    # Fiki Fiki is also social
        
        if not is_actively_socializing:
            super().update(game_hours_advanced, period_name, character_action, is_char_externally_resting)
        # Satisfaction happens via satisfy() method called by Character's socialize methods or AI.