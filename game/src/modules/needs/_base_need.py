# simai/game/modules/needs/_base_need.py
# Last Updated: 2025-05-12 (English translation and review)

import random

class BaseNeed:
    """
    Base class for all character needs.
    Each need has a current value, a maximum value, a base rate of change,
    and can be influenced by period multipliers passed during its update.
    """
    def __init__(self, owner_character, name: str,
                 max_value: float, 
                 initial_fill_min_pct: float, initial_fill_max_pct: float, 
                 base_rate_per_hour: float, 
                 is_value_high_good: bool, # True if 100% is the desired state
                 rate_multipliers_dict: dict): # Specific multiplier dict for this need
        
        self.owner = owner_character 
        self.name = name             
        self.max_value = float(max_value)
        self.base_rate_per_hour = abs(float(base_rate_per_hour)) 
        self.is_value_high_good = is_value_high_good
        self.rate_multipliers = rate_multipliers_dict if isinstance(rate_multipliers_dict, dict) else {}

        min_initial_value = self.max_value * initial_fill_min_pct
        max_initial_value = self.max_value * initial_fill_max_pct
        self.current_value = random.uniform(min_initial_value, max_initial_value)
        self._clamp_value()

    def _clamp_value(self):
        """Ensures the current value stays within [0, max_value]."""
        self.current_value = max(0.0, min(self.current_value, self.max_value))

    def get_value(self) -> float:
        """Returns the current value of the need."""
        return self.current_value

    def randomize_value(self, min_percentage: float, max_percentage: float):
        """Re-randomizes the current value of the need based on new percentages."""
        min_val = self.max_value * min_percentage
        max_val = self.max_value * max_percentage
        self.current_value = random.uniform(min_val, max_val)
        self._clamp_value()

    def set_value(self, new_value: float):
        """Sets the current value of the need and clamps it."""
        self.current_value = new_value
        self._clamp_value()

    def get_percentage(self) -> float: 
        """Returns the current fill percentage of the need (0.0 to 1.0)."""
        return self.current_value / self.max_value if self.max_value > 0 else 0.0

    def get_goodness_factor(self) -> float: 
        """Returns a factor from 0.0 (bad state) to 1.0 (good state) for UI coloring."""
        raw_percentage = self.get_percentage()
        return raw_percentage if self.is_value_high_good else 1.0 - raw_percentage

    def _get_rate_multiplier_for_period(self, period_name: str) -> float:
        """Gets the rate multiplier for the given time period from the stored dictionary."""
        return self.rate_multipliers.get(period_name, 1.0) 

    def update(self, game_hours_advanced: float, period_name: str, 
               character_action: str = "idle", is_char_externally_resting: bool = False):
        """
        Updates the need value based on game time passed and period multipliers.
        Specific needs (like Energy) will override this for custom logic based on character_action.
        """
        if game_hours_advanced <= 0:
            return

        multiplier = self._get_rate_multiplier_for_period(period_name)
        effective_rate = self.base_rate_per_hour * multiplier
        change_amount = effective_rate * game_hours_advanced

        if self.is_value_high_good: # e.g., Energy, Fun, Social, Hygiene DECAY
            self.current_value -= change_amount
        else: # e.g., Hunger, Bladder, IntimacyDrive INCREASE
            self.current_value += change_amount
        
        self._clamp_value()

    def satisfy(self, amount: float): 
        """
        Satisfies the need by the given amount.
        'amount' is always positive and intended to make the need "better".
        """
        change = abs(amount)
        if self.is_value_high_good: # Making it "better" means increasing towards max_value
            self.current_value += change
        else: # Making it "better" means decreasing towards 0
            self.current_value -= change
        self._clamp_value()
    
    def to_dict(self) -> dict:
        """Serializes the need's current state."""
        return {"current_value": self.current_value}

    def from_dict(self, data_dict: dict):
        """Restores the need's current state from a dictionary."""
        # max_value and other init params are set by Character from config during Need creation
        self.current_value = data_dict.get("current_value", self.max_value * 0.5) # Sensible fallback
        self._clamp_value()

    def __str__(self):
        return f"{self.name}: {self.current_value:.0f}/{self.max_value:.0f} ({self.get_percentage()*100:.0f}%)"