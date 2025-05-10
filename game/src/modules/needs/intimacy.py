# simai/game/modules/needs/intimacy.py
from ._base_need import BaseNeed

class Intimacy(BaseNeed): # Pulsione Intimità: 0 = bassa (stato "buono"), 100 = alta (stato "negativo" da risolvere)
    def __init__(self, owner, max_val, initial_min_pct, initial_max_pct, 
                 base_increase_rate, multipliers_dict_from_char):
        super().__init__(owner_character=owner,
                         name="Intimacy", 
                         max_value=max_val, 
                         initial_fill_min_pct=initial_min_pct, 
                         initial_fill_max_pct=initial_max_pct,
                         base_rate_per_hour=base_increase_rate, 
                         high_value_is_good=False, # Valore alto di pulsione è uno stato da risolvere (quindi "male" per la barra colore)
                         rate_multipliers_dict=multipliers_dict_from_char)

    def update(self, game_hours_advanced: float, period_name: str, character_action: str = "idle", is_char_externally_resting: bool = False):
        # La pulsione di intimità aumenta se non si è in un'azione che la soddisfa attivamente
        if character_action not in ["interacting_intimately"]: # Se l'NPC sta interagendo, non aumenta
            super().update(game_hours_advanced, period_name, character_action, is_char_externally_resting)
        # La soddisfazione avviene tramite il metodo satisfy() chiamato da Character/AI