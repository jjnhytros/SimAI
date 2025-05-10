# simai/game/modules/needs/social.py
from ._base_need import BaseNeed

class Social(BaseNeed): # Socialità: 0 = solo (male), 100 = appagato (bene)
    def __init__(self, owner, max_val, initial_min_pct, initial_max_pct, 
                 base_decay_rate, multipliers_dict_from_char):
        super().__init__(owner_character=owner, 
                         name="Social", 
                         max_value=max_val, 
                         initial_fill_min_pct=initial_min_pct,
                         initial_fill_max_pct=initial_max_pct,
                         base_rate_per_hour=base_decay_rate, 
                         high_value_is_good=True, 
                         rate_multipliers_dict=multipliers_dict_from_char)

    def update(self, game_hours_advanced: float, period_name: str, character_action: str = "idle", is_char_externally_resting: bool = False):
        # La socialità decade se non si sta attivamente socializzando
        if character_action not in ["phoning", "interacting_intimately"]: # Aggiungi altri stati sociali qui
            super().update(game_hours_advanced, period_name, character_action, is_char_externally_resting)
        # La soddisfazione avviene tramite il metodo satisfy() o socialize_over_time() chiamato da Character/AI
        