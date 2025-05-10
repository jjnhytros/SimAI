# simai/game/modules/needs/fun.py
from ._base_need import BaseNeed

class Fun(BaseNeed): # Divertimento: 0 = annoiato (male), 100 = divertito (bene)
    def __init__(self, owner, max_val, initial_min_pct, initial_max_pct, 
                 base_decay_rate, multipliers_dict_from_char):
        super().__init__(owner_character=owner,
                         name="Fun", 
                         max_value=max_val, 
                         initial_fill_min_pct=initial_min_pct,
                         initial_fill_max_pct=initial_max_pct,
                         base_rate_per_hour=base_decay_rate, 
                         high_value_is_good=True, 
                         rate_multipliers_dict=multipliers_dict_from_char)

    # L'update di BaseNeed (con high_value_is_good=True) fa diminuire il valore (decade)
    # satisfy() di BaseNeed (con high_value_is_good=True) fa aumentare il valore