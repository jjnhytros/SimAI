# simai/game/src/modules/needs/_base_need.py
import random

class BaseNeed:
    def __init__(self, owner_character, name: str,
                 max_value: float, 
                 initial_fill_min_pct: float, initial_fill_max_pct: float, 
                 base_rate_per_hour: float, 
                 high_value_is_good: bool, 
                 rate_multipliers_dict: dict):
        
        self.owner = owner_character # Riferimento al personaggio
        self.name = name
        self.max_value = float(max_value)
        self.base_rate_per_hour = abs(float(base_rate_per_hour)) 
        self.high_value_is_good = high_value_is_good # True se 100% è lo stato desiderato
        self.rate_multipliers = rate_multipliers_dict if isinstance(rate_multipliers_dict, dict) else {}

        min_val = self.max_value * initial_fill_min_pct
        max_val = self.max_value * initial_fill_max_pct
        self.current_value = random.uniform(min_val, max_val)
        self._clamp()

    def _clamp(self):
        self.current_value = max(0.0, min(self.current_value, self.max_value))

    def get_value(self) -> float:
        return self.current_value

    def set_value(self, new_value: float):
        self.current_value = new_value
        self._clamp()

    def randomize_value(self, min_percentage: float, max_percentage: float):
        """Ri-randomizza il valore corrente del bisogno basandosi su nuove percentuali."""
        min_val = self.max_value * min_percentage
        max_val = self.max_value * max_percentage
        self.current_value = random.uniform(min_val, max_val)
        self._clamp()

    def get_percentage(self) -> float: # Percentuale di riempimento (0.0 a 1.0)
        return self.current_value / self.max_value if self.max_value > 0 else 0.0

    def get_goodness_factor(self) -> float: # Per colore UI (0.0=male, 1.0=bene)
        raw_percentage = self.get_percentage()
        return raw_percentage if self.high_value_is_good else 1.0 - raw_percentage

    def _get_period_multiplier(self, period_name: str) -> float:
        return self.rate_multipliers.get(period_name, 1.0)

    def update(self, game_hours_advanced: float, period_name: str, character_action: str = "idle", is_char_externally_resting: bool = False):
        if game_hours_advanced <= 0:
            return

        multiplier = self._get_period_multiplier(period_name)
        effective_rate = self.base_rate_per_hour * multiplier
        change = effective_rate * game_hours_advanced

        # Comportamento di default:
        # Se high_value_is_good=True (es. Energia), il bisogno DECADE (sottraiamo 'change').
        # Se high_value_is_good=False (es. Fame, Vescica, Pulsione Intimità), il bisogno AUMENTA (aggiungiamo 'change').
        if self.high_value_is_good:
            self.current_value -= change
        else:
            self.current_value += change
        
        self._clamp()

    def satisfy(self, amount: float): # 'amount' è sempre inteso per "migliorare" il bisogno
        change = abs(amount)
        if self.high_value_is_good: # Migliorare significa aumentare verso il massimo
            self.current_value += change
        else: # Migliorare significa diminuire verso lo zero
            self.current_value -= change
        self._clamp()

    def __str__(self):
        return f"{self.name}: {self.current_value:.0f}/{self.max_value:.0f} ({self.get_percentage()*100:.0f}%)"