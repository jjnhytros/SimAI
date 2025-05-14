# simai/game/src/modules/needs/_base_need.py (NOME FILE CORRETTO)
# MODIFIED: Made debug prints conditional using config.DEBUG_AI_ACTIVE.
# MODIFIED: Imports robusti con sys.exit().

import random
import sys

try:
    from game import config as game_config
except ImportError as e_cfg:
    print(f"CRITICAL ERROR (_base_need.py): Could not import 'game.config': {e_cfg}")
    sys.exit() # Config è essenziale

# Leggi il flag di debug una volta, dopo aver importato config
DEBUG_VERBOSE = getattr(game_config, 'DEBUG_AI_ACTIVE', False)

class BaseNeed:
    def __init__(self, character_owner, max_value: float, 
                 initial_min_percentage: float, initial_max_percentage: float, 
                 base_rate: float, rate_multipliers: dict, high_is_good: bool, name: str):
        self.character_owner = character_owner
        self.name = name
        self.max_value: float = float(max_value)
        self.current_value: float = self.max_value 
        self.base_rate: float = float(base_rate)
        self.rate_multipliers: dict = rate_multipliers if isinstance(rate_multipliers, dict) else {}
        self.high_is_good: bool = high_is_good

        self.randomize_value(initial_min_percentage, initial_max_percentage)

        if DEBUG_VERBOSE:
            owner_name = "UnknownChar"
            if hasattr(self.character_owner, 'name'): owner_name = self.character_owner.name
            elif self.character_owner is not None: owner_name = str(self.character_owner)
            print(f"NEED_INIT ({owner_name} - {self.name}): "
                  f"Max={self.max_value:.0f}, Current={self.current_value:.0f}, BaseRate={self.base_rate}, HighIsGood={self.high_is_good}")

    def get_value(self) -> float:
        return self.current_value

    def set_value(self, new_value: float):
        self.current_value = max(0.0, min(float(new_value), self.max_value))

    def get_percentage(self) -> float:
        if self.max_value == 0: return 0.0
        return self.current_value / self.max_value

    def get_goodness_factor(self) -> float:
        percentage = self.get_percentage()
        return percentage if self.high_is_good else (1.0 - percentage)

    def randomize_value(self, min_percentage: float, max_percentage: float):
        owner_name = "UnknownChar"
        if hasattr(self.character_owner, 'name'): owner_name = self.character_owner.name
        elif self.character_owner is not None: owner_name = str(self.character_owner)

        if not (0.0 <= min_percentage <= 1.0 and 0.0 <= max_percentage <= 1.0 and min_percentage <= max_percentage):
            if DEBUG_VERBOSE:
                print(f"NEED WARNING ({owner_name} - {self.name}): "
                      f"Invalid percentages for randomize_value ({min_percentage}, {max_percentage}). Using 0-100%.")
            min_percentage = 0.0
            max_percentage = 1.0
        
        random_percentage = random.uniform(min_percentage, max_percentage)
        self.set_value(self.max_value * random_percentage)
        if DEBUG_VERBOSE:
            print(f"NEED_RANDOMIZE ({owner_name} - {self.name}): "
                  f"Value set to {self.current_value:.2f} ({random_percentage*100:.1f}%) "
                  f"within range [{min_percentage*100:.1f}%, {max_percentage*100:.1f}%]")

    def update(self, hours_passed: float, current_period_name: str = None, 
               character_action: str = "idle", character_is_resting: bool = False):
        if hours_passed <= 0: return

        rate_multiplier = 1.0
        if current_period_name and current_period_name in self.rate_multipliers:
            rate_multiplier = self.rate_multipliers[current_period_name]
        
        owner_name = "UnknownChar"
        if hasattr(self.character_owner, 'name'): owner_name = self.character_owner.name
        elif self.character_owner is not None: owner_name = str(self.character_owner)

        # Condizioni di skip specifiche per tipo di bisogno
        if self.name == "Energy" and (character_action == "resting_on_bed" or character_is_resting):
            if DEBUG_VERBOSE: print(f"NEED_UPDATE_SKIP ({owner_name} - {self.name}): Skipping decay due to rest.")
            return 
        if self.name == "Hunger" and character_action == "eating_food": # Assumendo azione "eating_food"
            if DEBUG_VERBOSE: print(f"NEED_UPDATE_SKIP ({owner_name} - {self.name}): Skipping increase due to eating.")
            return
        if self.name == "Bladder" and character_action == "using_toilet":
            if DEBUG_VERBOSE: print(f"NEED_UPDATE_SKIP ({owner_name} - {self.name}): Skipping fill due to using toilet.")
            return
            
        change_amount = self.base_rate * rate_multiplier * hours_passed
        old_value = self.current_value
        if self.high_is_good: self.set_value(self.current_value - change_amount)
        else: self.set_value(self.current_value + change_amount)
        
        if DEBUG_VERBOSE and abs(old_value - self.current_value) > 0.01:
            direction = "decreased" if self.high_is_good else "increased"
            print(f"NEED_UPDATE ({owner_name} - {self.name}): "
                  f"Value {direction} from {old_value:.2f} to {self.current_value:.2f} (Change: {change_amount:.2f}, Mult: {rate_multiplier})")

    def satisfy(self, amount: float):
        if amount <= 0: return
        old_value = self.current_value
        owner_name = "UnknownChar"
        if hasattr(self.character_owner, 'name'): owner_name = self.character_owner.name
        elif self.character_owner is not None: owner_name = str(self.character_owner)

        if self.high_is_good: self.set_value(self.current_value + amount)
        else: self.set_value(self.current_value - amount)
        
        if DEBUG_VERBOSE and abs(old_value - self.current_value) > 0.01:
            action_verb = "increased" if self.high_is_good else "decreased"
            print(f"NEED_SATISFY ({owner_name} - {self.name}): "
                  f"Value {action_verb} from {old_value:.2f} to {self.current_value:.2f} (Amount: {amount:.2f})")

    def recover(self, recovery_rate_per_hour: float, hours_passed: float):
        owner_name = "UnknownChar"
        if hasattr(self.character_owner, 'name'): owner_name = self.character_owner.name
        elif self.character_owner is not None: owner_name = str(self.character_owner)

        if not self.high_is_good: 
            if DEBUG_VERBOSE: print(f"NEED_RECOVER_WARN ({owner_name} - {self.name}): Recover called on a need where high is not good.")
            return
        if recovery_rate_per_hour <=0 or hours_passed <= 0: return

        old_value = self.current_value
        recovery_amount = recovery_rate_per_hour * hours_passed
        self.set_value(self.current_value + recovery_amount)
        
        if DEBUG_VERBOSE and abs(old_value - self.current_value) > 0.01:
            print(f"NEED_RECOVER ({owner_name} - {self.name}): "
                  f"Value increased from {old_value:.2f} to {self.current_value:.2f} (Amount: {recovery_amount:.2f})")

    def to_dict(self) -> dict:
        return {"name": self.name, "current_value": self.current_value}

    @classmethod
    def from_data(cls, character_owner, data: dict, max_val_cfg: float, 
                  init_min_pct_cfg: float, init_max_pct_cfg: float, 
                  base_rate_cfg: float, rate_mult_cfg: dict, high_is_good_cfg: bool, name_cfg: str):
        need_instance = cls(character_owner, max_val_cfg, init_min_pct_cfg, init_max_pct_cfg, 
                            base_rate_cfg, rate_mult_cfg, high_is_good_cfg, name_cfg)
        if "current_value" in data:
            need_instance.set_value(data["current_value"])
        elif DEBUG_VERBOSE: 
            owner_name_fc = "UnknownChar"
            if hasattr(character_owner, 'name'): owner_name_fc = character_owner.name
            elif character_owner is not None: owner_name_fc = str(character_owner)
            print(f"NEED_FROM_DATA ({owner_name_fc} - {name_cfg}): 'current_value' not in data, using randomized initial value: {need_instance.current_value:.2f}")
        return need_instance