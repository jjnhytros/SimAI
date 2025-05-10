# simai/game/modules/needs/hunger.py
from ._base_need import BaseNeed
# Non c'è bisogno di importare config qui

class Hunger(BaseNeed): # Fame: 0 = non affamato (bene), 100 = affamatissimo (male)
    def __init__(self, owner, max_val, initial_min_pct, initial_max_pct, 
                 base_rate, multipliers_actual_dict): # Riceve il dizionario dei moltiplicatori
        super().__init__(owner_character=owner, 
                         name="Hunger", 
                         max_value=max_val, 
                         initial_fill_min_pct=initial_min_pct, 
                         initial_fill_max_pct=initial_max_pct,
                         base_rate_per_hour=base_rate, 
                         high_value_is_good=False, # Valore alto di fame è male
                         rate_multipliers_dict=multipliers_actual_dict) # Passa il dizionario a BaseNeed

    # L'update di BaseNeed e satisfy() di BaseNeed dovrebbero andare bene