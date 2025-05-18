# game/src/modules/needs/_base_need.py
import random
import sys
import logging # Aggiunto per logging
from typing import Dict, Any, TYPE_CHECKING, Optional, List

try:
    from game import config as game_config
except ImportError as e_cfg:
    print(f"CRITICAL ERROR (_base_need.py): Could not import 'game.config': {e_cfg}")
    sys.exit()

logger = logging.getLogger(__name__) # Logger per questo modulo
DEBUG_VERBOSE = getattr(game_config, 'DEBUG_AI_ACTIVE', False)

class BaseNeed:
    def __init__(self, character_owner, max_value: float, 
                initial_min_percentage: float, initial_max_percentage: float, 
                base_rate: float, rate_multipliers: dict, 
                high_is_good: bool,
                name: str):
        self.character_owner = character_owner # Riferimento al Character proprietario
        self.name: str = name
        self.max_value: float = float(max_value)
        self.current_value: float = self.max_value # Inizia pieno o randomizzato
        self.base_rate: float = float(base_rate) # Tasso di decadimento orario
        self.rate_multipliers: dict = rate_multipliers if isinstance(rate_multipliers, dict) else {}
        
        # high_is_good è ora implicitamente True per tutti i bisogni con la nuova logica.
        # Manteniamo l'attributo se qualche logica esterna dovesse ancora farvi riferimento,
        # ma la logica interna di update/satisfy ora assume che un valore alto sia buono.
        self.high_is_good: bool = high_is_good

        self.randomize_value(initial_min_percentage, initial_max_percentage)

        # Per tracciare l'ultimo aggiornamento basato sul tempo di gioco globale
        self.last_updated_total_game_hours: float = 0.0
        if self.character_owner and hasattr(self.character_owner, 'game_state_ref') and \
           self.character_owner.game_state_ref and \
           hasattr(self.character_owner.game_state_ref, 'current_game_total_sim_hours_elapsed'):
            self.last_updated_total_game_hours = self.character_owner.game_state_ref.current_game_total_sim_hours_elapsed
        
        if DEBUG_VERBOSE:
            owner_name = getattr(self.character_owner, 'name', 'UnknownChar')
            logger.debug(f"NEED_INIT ({owner_name} - {self.name}): Max={self.max_value:.0f}, Current={self.current_value:.1f}, BaseDecayRate={self.base_rate:.2f}/hr")

    def get_value(self) -> float:
        return self.current_value

    def set_value(self, new_value: float):
        self.current_value = max(0.0, min(float(new_value), self.max_value))

    def get_percentage(self) -> float:
        return (self.current_value / self.max_value) if self.max_value > 0 else 0.0

    def get_goodness_factor(self) -> float:
        # Con la nuova convenzione, percentage è già il goodness_factor
        return self.get_percentage()

    def randomize_value(self, min_percentage: float, max_percentage: float):
        owner_name = getattr(self.character_owner, 'name', 'UnknownChar')
        if not (0.0 <= min_percentage <= 1.0 and 0.0 <= max_percentage <= 1.0 and min_percentage <= max_percentage):
            if DEBUG_VERBOSE:
                logger.warning(f"NEED_RANDOMIZE ({owner_name} - {self.name}): Percentuali non valide ({min_percentage}, {max_percentage}). Uso 0-100%.")
            min_percentage, max_percentage = 0.0, 1.0
        
        random_percentage = random.uniform(min_percentage, max_percentage)
        self.set_value(self.max_value * random_percentage)
        if DEBUG_VERBOSE:
            logger.debug(f"NEED_RANDOMIZE ({owner_name} - {self.name}): Valore impostato a {self.current_value:.2f} ({random_percentage*100:.1f}%) in range [{min_percentage*100:.1f}%, {max_percentage*100:.1f}%]")

    def update(self, game_hours_passed: float, current_period_name: Optional[str] = None,
               character_action: str = "idle", character_is_resting: bool = False):
        """Aggiorna il bisogno facendolo decadere nel tempo."""
        if game_hours_passed <= 0:
            return

        # Condizioni per saltare il decadimento
        if self.name == "Energy" and (character_action == "resting_on_bed" or character_is_resting or character_action == "cuddling_in_bed"):
            if DEBUG_VERBOSE: logger.debug(f"NEED_UPDATE_SKIP ({getattr(self.character_owner, 'name', '')} - {self.name}): Salto decay per riposo/azione '{character_action}'.")
            return
        if self.name == "Hunger" and character_action == "eating_food": # Assumendo un'azione del genere
            if DEBUG_VERBOSE: logger.debug(f"NEED_UPDATE_SKIP ({getattr(self.character_owner, 'name', '')} - {self.name}): Salto decay per azione '{character_action}'.")
            return
        if self.name == "Bladder" and character_action == "using_toilet":
            if DEBUG_VERBOSE: logger.debug(f"NEED_UPDATE_SKIP ({getattr(self.character_owner, 'name', '')} - {self.name}): Salto decay per azione '{character_action}'.")
            return
        # Aggiungi altre condizioni di skip se necessario per altri bisogni

        rate_multiplier = 1.0
        if current_period_name and current_period_name in self.rate_multipliers:
            rate_multiplier = self.rate_multipliers[current_period_name]
        
        decay_amount = self.base_rate * rate_multiplier * game_hours_passed
        
        old_value = self.current_value
        self.set_value(self.current_value - decay_amount) # Tutti i bisogni ora decadono (scendono)
        
        if DEBUG_VERBOSE and abs(old_value - self.current_value) > 0.01:
            logger.debug(f"NEED_UPDATE ({getattr(self.character_owner, 'name', '')} - {self.name}): "
                          f"Valore sceso da {old_value:.2f} a {self.current_value:.2f} (Decay: {decay_amount:.2f}, Mult: {rate_multiplier})")

    def satisfy(self, amount: float):
        """Soddisfa il bisogno aumentandone il valore."""
        if amount <= 0: # Non si può soddisfare con un valore nullo o negativo
            if amount < 0 and DEBUG_VERBOSE: logger.warning(f"NEED_SATISFY ({getattr(self.character_owner, 'name', '')} - {self.name}): Tentativo di soddisfare con importo negativo {amount:.2f}.")
            return

        old_value = self.current_value
        self.set_value(self.current_value + amount) # Aumenta sempre il valore
        
        if DEBUG_VERBOSE and abs(old_value - self.current_value) > 0.01:
            logger.debug(f"NEED_SATISFY ({getattr(self.character_owner, 'name', '')} - {self.name}): "
                          f"Valore aumentato da {old_value:.2f} a {self.current_value:.2f} (Quantità: {amount:.2f})")

    def recover(self, recovery_rate_per_hour: float, hours_passed: float):
        """Metodo specifico per recuperare un bisogno (come l'energia dormendo). Aumenta il valore."""
        if recovery_rate_per_hour <=0 or hours_passed <= 0:
            return

        old_value = self.current_value
        recovery_amount = recovery_rate_per_hour * hours_passed
        self.satisfy(recovery_amount) # Usa satisfy per aumentare e clampare
        
        if DEBUG_VERBOSE and abs(old_value - self.current_value) > 0.01: # Logga solo se c'è stato un cambiamento reale
            logger.debug(f"NEED_RECOVER ({getattr(self.character_owner, 'name', '')} - {self.name}): "
                          f"Valore recuperato da {old_value:.2f} a {self.current_value:.2f} (Recupero: {recovery_amount:.2f})")
    
    def is_critical(self) -> bool:
         """Verifica se il bisogno è a un livello critico (basso)."""
         # Assumiamo che esista una soglia critica definita in config per ogni bisogno
         # Es. config.HUNGER_CRITICAL_THRESHOLD, config.ENERGY_CRITICAL_THRESHOLD
         # La soglia dovrebbe essere in termini di valore assoluto o percentuale.
         # Per ora, usiamo una percentuale generica se non definita.
         critical_threshold_pct = getattr(config, f"{self.name.upper()}_CRITICAL_THRESHOLD_PCT", 0.15) # Default al 15%
         return self.get_percentage() <= critical_threshold_pct

    def to_dict(self) -> dict:
        return {
            "name": self.name, # Utile per debug o ricostruzione se necessario
            "current_value": self.current_value,
            "max_value": self.max_value, # Salva anche max_value se può cambiare o per riferimento
            "base_rate": self.base_rate,
            "rate_multipliers": self.rate_multipliers,
            "high_is_good": self.high_is_good, # Anche se ora è sempre True, per completezza
            "last_updated_total_game_hours": self.last_updated_total_game_hours
         }

    @classmethod
    def from_dict(cls, data: dict, character_owner: 'Character', 
                  # Passa i default da config nel caso manchino nel file di salvataggio
                  default_max_value: float, 
                  default_initial_min_pct: float, default_initial_max_pct: float,
                  default_base_rate: float, default_rate_multipliers: dict,
                  default_high_is_good: bool, default_need_name: str) -> 'BaseNeed':
        
        instance = cls(
            character_owner=character_owner,
            max_value=float(data.get("max_value", default_max_value)),
            initial_min_percentage=default_initial_min_pct, # Verrà sovrascritto da current_value
            initial_max_percentage=default_initial_max_pct, # Verrà sovrascritto da current_value
            base_rate=float(data.get("base_rate", default_base_rate)),
            rate_multipliers=data.get("rate_multipliers", default_rate_multipliers),
            high_is_good=data.get("high_is_good", default_high_is_good), # Dovrebbe essere True
            name=data.get("name", default_need_name)
        )
        instance.current_value = float(data.get("current_value", instance.max_value * random.uniform(default_initial_min_pct, default_initial_max_pct)))
        instance.last_updated_total_game_hours = float(data.get("last_updated_total_game_hours", 0.0))
        # Se game_state non è ancora completamente pronto al momento della creazione di BaseNeed da from_dict,
        # last_updated_total_game_hours potrebbe necessitare di essere impostato dopo.
        return instance