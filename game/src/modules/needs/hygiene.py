# simai/game/modules/needs/hygiene.py
from ._base_need import BaseNeed

class Hygiene(BaseNeed): # Igiene: 0 = sporco (male), 100 = pulito (bene)
    def __init__(self, owner, max_val, initial_min_pct, initial_max_pct, 
                 base_decay_rate, multipliers_dict_from_char):
        super().__init__(owner_character=owner,
                         name="Hygiene", 
                         max_value=max_val, 
                         initial_fill_min_pct=initial_min_pct,
                         initial_fill_max_pct=initial_max_pct,
                         base_rate_per_hour=base_decay_rate, 
                         high_value_is_good=True, 
                         rate_multipliers_dict=multipliers_dict_from_char)

    # L'update di BaseNeed (con high_value_is_good=True) fa diminuire il valore (decade)
    # satisfy() di BaseNeed (con high_value_is_good=True) fa aumentare il valore