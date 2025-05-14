# simai/game/src/modules/needs/base_need.py
# MODIFIED: Made debug prints conditional using config.DEBUG_AI_ACTIVE

import random
import sys

try:
    from game import config as game_config # Assumendo che config sia in package 'game'
except ImportError:
    print("CRITICAL ERROR (BaseNeed): Could not import 'game.config'. Needs system may not function correctly.")
    # Fallback minimale per evitare crash immediati se config non è trovata,
    # ma questo indica un problema di setup.
    class ConfigPlaceholder:
        DEBUG_AI_ACTIVE = True # Per mostrare gli warning del placeholder
        DEFAULT_MAX_NEED_VALUE = 100.0
        def __getattr__(self, name): return None 
    game_config = ConfigPlaceholder()
    if getattr(game_config, 'DEBUG_AI_ACTIVE', True): # Stampa l'warning se il debug è attivo nel placeholder
        print("WARNING (BaseNeed): Using FallbackConfig due to import error. Functionality will be limited.")

# Leggi il flag di debug una volta, dopo aver importato (o usato il fallback) di config
DEBUG_VERBOSE = getattr(game_config, 'DEBUG_AI_ACTIVE', False)

class BaseNeed:
    def __init__(self, character_owner, max_value: float, 
                 initial_min_percentage: float, initial_max_percentage: float, 
                 base_rate: float, rate_multipliers: dict, high_is_good: bool, name: str):
        self.character_owner = character_owner # Riferimento al personaggio proprietario
        self.name = name
        self.max_value: float = float(max_value)
        self.current_value: float = self.max_value # Inizia pieno e poi randomizza
        self.base_rate: float = float(base_rate) # Tasso base di cambiamento (positivo)
        self.rate_multipliers: dict = rate_multipliers if isinstance(rate_multipliers, dict) else {}
        self.high_is_good: bool = high_is_good # True se un valore alto è positivo, False se un valore alto è negativo

        # Inizializzazione casuale del valore del bisogno
        self.randomize_value(initial_min_percentage, initial_max_percentage)

        if DEBUG_VERBOSE:
            print(f"NEED_INIT ({self.character_owner.name if self.character_owner else 'UnknownChar'} - {self.name}): "
                  f"Max={self.max_value:.0f}, Current={self.current_value:.0f}, BaseRate={self.base_rate}, HighIsGood={self.high_is_good}")


    def get_value(self) -> float:
        return self.current_value

    def set_value(self, new_value: float):
        self.current_value = max(0.0, min(float(new_value), self.max_value))

    def get_percentage(self) -> float:
        if self.max_value == 0: return 0.0 # Evita divisione per zero
        return self.current_value / self.max_value

    def get_goodness_factor(self) -> float:
        """Restituisce un valore da 0.0 (molto male) a 1.0 (molto bene)."""
        percentage = self.get_percentage()
        return percentage if self.high_is_good else (1.0 - percentage)

    def randomize_value(self, min_percentage: float, max_percentage: float):
        """Imposta il valore corrente a una percentuale casuale del massimo, tra min e max."""
        if not (0.0 <= min_percentage <= 1.0 and 0.0 <= max_percentage <= 1.0 and min_percentage <= max_percentage):
            if DEBUG_VERBOSE:
                print(f"NEED WARNING ({self.character_owner.name if self.character_owner else 'UnknownChar'} - {self.name}): "
                      f"Invalid percentages for randomize_value ({min_percentage}, {max_percentage}). Using 0-100%.")
            min_percentage = 0.0
            max_percentage = 1.0
        
        random_percentage = random.uniform(min_percentage, max_percentage)
        self.set_value(self.max_value * random_percentage)
        # if DEBUG_VERBOSE:
        #     print(f"NEED_RANDOMIZE ({self.character_owner.name if self.character_owner else 'UnknownChar'} - {self.name}): "
        #           f"Value set to {self.current_value:.2f} ({random_percentage*100:.1f}%) "
        #           f"within range [{min_percentage*100:.1f}%, {max_percentage*100:.1f}%]")


    def update(self, hours_passed: float, current_period_name: str = None, 
               character_action: str = "idle", character_is_resting: bool = False):
        """
        Aggiorna il valore del bisogno in base al tempo passato e ai moltiplicatori.
        Il cambiamento base è SEMPRE un AUMENTO se high_is_good=False (es. fame, vescica)
        o una DIMINUZIONE se high_is_good=True (es. energia, divertimento).
        I metodi satisfy/recover gestiranno la direzione opposta.
        """
        if hours_passed <= 0:
            return

        rate_multiplier = 1.0
        if current_period_name and current_period_name in self.rate_multipliers:
            rate_multiplier = self.rate_multipliers[current_period_name]
        
        # Esempio: l'energia non dovrebbe calare se si sta riposando (gestito da recover)
        if self.name == "Energy" and (character_action == "resting_on_bed" or character_is_resting):
             # if DEBUG_VERBOSE: print(f"NEED_UPDATE_SKIP ({self.character_owner.name} - {self.name}): Skipping decay due to rest.")
            return # La ricarica è gestita altrove (es. Character.rest())

        # Per altri bisogni, potremmo avere logiche simili per saltare il decay/increase base
        # Esempio: la fame non aumenta se l'NPC sta mangiando (l'azione "eating" dovrebbe chiamare satisfy)
        if self.name == "Hunger" and character_action == "eating_food": # Assumendo che "eating_food" sia un'azione
            # if DEBUG_VERBOSE: print(f"NEED_UPDATE_SKIP ({self.character_owner.name} - {self.name}): Skipping increase due to eating.")
            return

        # Esempio: la vescica non si riempie se l'NPC sta usando il bagno
        if self.name == "Bladder" and character_action == "using_toilet":
             # if DEBUG_VERBOSE: print(f"NEED_UPDATE_SKIP ({self.character_owner.name} - {self.name}): Skipping fill due to using toilet.")
            return
            
        change_amount = self.base_rate * rate_multiplier * hours_passed

        old_value = self.current_value
        if self.high_is_good: # Se alto è buono, il bisogno decade (diminuisce)
            self.set_value(self.current_value - change_amount)
        else: # Se alto è cattivo, il bisogno aumenta
            self.set_value(self.current_value + change_amount)
        
        # if DEBUG_VERBOSE and abs(old_value - self.current_value) > 0.01:
        #     direction = "decreased" if self.high_is_good else "increased"
        #     print(f"NEED_UPDATE ({self.character_owner.name if self.character_owner else 'UnknownChar'} - {self.name}): "
        #           f"Value {direction} from {old_value:.2f} to {self.current_value:.2f} (Change: {change_amount:.2f}, Mult: {rate_multiplier})")


    def satisfy(self, amount: float):
        """Soddisfa il bisogno (es. mangiare per la fame, usare il bagno per la vescica)."""
        if amount <= 0: return
        old_value = self.current_value
        if self.high_is_good: # Se alto è buono, "soddisfare" significa aumentare (es. divertimento, social)
            self.set_value(self.current_value + amount)
        else: # Se alto è cattivo, "soddisfare" significa diminuire (es. fame, vescica)
            self.set_value(self.current_value - amount)
        
        # if DEBUG_VERBOSE and abs(old_value - self.current_value) > 0.01:
        #     action_verb = "increased" if self.high_is_good else "decreased"
        #     print(f"NEED_SATISFY ({self.character_owner.name if self.character_owner else 'UnknownChar'} - {self.name}): "
        #           f"Value {action_verb} from {old_value:.2f} to {self.current_value:.2f} (Amount: {amount:.2f})")


    def recover(self, recovery_rate_per_hour: float, hours_passed: float):
        """Metodo specifico per bisogni che si 'ricaricano' nel tempo (es. Energia dormendo)."""
        if not self.high_is_good: # Ha senso solo per bisogni dove alto è buono
            if DEBUG_VERBOSE: print(f"NEED_RECOVER_WARN ({self.name}): Recover called on a need where high is not good.")
            return
        if recovery_rate_per_hour <=0 or hours_passed <= 0: return

        old_value = self.current_value
        recovery_amount = recovery_rate_per_hour * hours_passed
        self.set_value(self.current_value + recovery_amount)
        
        # if DEBUG_VERBOSE and abs(old_value - self.current_value) > 0.01:
        #     print(f"NEED_RECOVER ({self.character_owner.name if self.character_owner else 'UnknownChar'} - {self.name}): "
        #           f"Value increased from {old_value:.2f} to {self.current_value:.2f} (Amount: {recovery_amount:.2f})")

    def to_dict(self) -> dict:
        """Serializza lo stato del bisogno in un dizionario."""
        return {
            "name": self.name,
            "current_value": self.current_value,
            # Non è necessario salvare max_value, base_rate ecc. se vengono da config al caricamento/init
        }

    @classmethod
    def from_data(cls, character_owner, data: dict, max_val_cfg: float, 
                  init_min_pct_cfg: float, init_max_pct_cfg: float, 
                  base_rate_cfg: float, rate_mult_cfg: dict, high_is_good_cfg: bool, name_cfg: str):
        """Crea un'istanza di BaseNeed da un dizionario, usando i valori di config come base."""
        need_instance = cls(character_owner, max_val_cfg, init_min_pct_cfg, init_max_pct_cfg, 
                            base_rate_cfg, rate_mult_cfg, high_is_good_cfg, name_cfg)
        # Sovrascrive il current_value con quello salvato, se presente
        if "current_value" in data:
            need_instance.set_value(data["current_value"])
        # else:
            # Se current_value non è nei dati, si mantiene quello inizializzato casualmente
            # if DEBUG_VERBOSE: 
            #     print(f"NEED_FROM_DATA ({name_cfg}): 'current_value' not in data, using randomized initial value: {need_instance.current_value:.2f}")
        return need_instance