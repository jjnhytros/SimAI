# simai/game/modules/needs/energy.py
from ._base_need import BaseNeed

class Energy(BaseNeed): # Energia: 0 = scarico (male), 100 = pieno (bene)
    def __init__(self, owner, max_val, initial_min_pct, initial_max_pct, 
                 base_rate, multipliers_actual_dict): # Riceve il dizionario
        super().__init__(owner_character=owner, 
                         name="Energy", 
                         max_value=max_val, 
                         initial_fill_min_pct=initial_min_pct,
                         initial_fill_max_pct=initial_max_pct,
                         base_rate_per_hour=base_rate, 
                         high_value_is_good=True, # Valore alto di energia è bene
                         rate_multipliers_dict=multipliers_actual_dict) # Passa il dizionario

    def update(self, game_hours_advanced: float, period_name: str, character_action: str = "idle", is_char_externally_resting: bool = False):
        # L'energia ha regole speciali: non decade se si riposa o in certe azioni
        is_inactive = is_char_externally_resting or \
                      character_action in ["phoning", "resting_on_bed", "interacting_intimately", "contemplating_intimacy"] # Aggiunto contemplating_intimacy
        
        if not is_inactive: # Decade solo se attivo
            super().update(game_hours_advanced, period_name, character_action, is_char_externally_resting)
        # La soddisfazione (riposo) è gestita da un metodo specifico chiamato dall'esterno

    def recover(self, recovery_rate_per_hour, hours_slept_sim):
        amount_to_recover = recovery_rate_per_hour * hours_slept_sim
        self.satisfy(amount_to_recover)