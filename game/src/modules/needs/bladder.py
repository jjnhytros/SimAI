# simai/game/modules/needs/bladder.py
from ._base_need import BaseNeed

class Bladder(BaseNeed): # Vescica: 0 = vuota (bene), 100 = piena (male)
    def __init__(self, owner, max_val, initial_min_pct, initial_max_pct, 
                 base_fill_rate, multipliers_dict_from_char):
        super().__init__(owner_character=owner,
                         name="Bladder", 
                         max_value=max_val, 
                         initial_fill_min_pct=initial_min_pct,
                         initial_fill_max_pct=initial_max_pct,
                         base_rate_per_hour=base_fill_rate, 
                         high_value_is_good=False, 
                         rate_multipliers_dict=multipliers_dict_from_char)

    # L'update di BaseNeed (con high_value_is_good=False) fa aumentare il valore (riempie)
    # satisfy() di BaseNeed (con high_value_is_good=False) fa diminuire il valore (svuota)
    