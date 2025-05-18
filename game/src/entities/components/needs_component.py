# game/src/entities/components/needs_component.py
import logging
from typing import Dict, Any, TYPE_CHECKING, Optional, List

# Importa dal package 'game'
from game import config
# Importa BaseNeed e tutte le classi di bisogno specifiche
from game.src.modules.needs._base_need import BaseNeed
from game.src.modules.needs.hunger import Hunger
from game.src.modules.needs.energy import Energy
from game.src.modules.needs.social import Social
from game.src.modules.needs.bladder import Bladder
from game.src.modules.needs.fun import Fun
from game.src.modules.needs.hygiene import Hygiene
from game.src.modules.needs.intimacy import Intimacy


if TYPE_CHECKING:
    from game.src.entities.character import Character # Per il type hint di character_owner

logger = logging.getLogger(__name__)
DEBUG_VERBOSE = getattr(config, 'DEBUG_AI_ACTIVE', False)

class NeedsComponent:
    def __init__(self, character_owner: 'Character'):
        """
        Inizializza il componente dei bisogni per un personaggio.
        TUTTI i bisogni ora seguono la logica: alto è buono, decadono naturalmente,
        e vengono soddisfatti (aumentati) dalle azioni.

        Args:
            character_owner (Character): Il personaggio a cui questo componente appartiene.
        """
        self.owner: 'Character' = character_owner
        self.owner_name: str = character_owner.name if character_owner else "NPC Sconosciuto"

        # Istanzia tutti i bisogni, passando il proprietario e i parametri da config.
        # 'base_rate' è sempre un tasso di decadimento.
        # 'high_is_good' è sempre True.
        self.hunger = Hunger( # Fame: alto = sazio, basso = affamato
            character_owner=self.owner,
            max_value=config.HUNGER_MAX_VALUE,
            initial_min_percentage=config.HUNGER_INITIAL_MIN_PCT,
            initial_max_percentage=config.HUNGER_INITIAL_MAX_PCT,
            base_rate=config.HUNGER_BASE_DECAY_RATE, # Rinominato per chiarezza
            rate_multipliers=config.HUNGER_RATE_MULTIPLIERS,
            high_is_good=True # Standardizzato
        )
        self.energy = Energy(
            character_owner=self.owner,
            max_value=config.ENERGY_MAX_VALUE,
            initial_min_percentage=config.ENERGY_INITIAL_MIN_PCT,
            initial_max_percentage=config.ENERGY_INITIAL_MAX_PCT,
            base_rate=config.ENERGY_BASE_DECAY_RATE,
            rate_multipliers=config.ENERGY_DECAY_MULTIPLIERS,
            high_is_good=True # Standardizzato
        )
        self.social = Social(
            character_owner=self.owner,
            max_value=config.SOCIAL_MAX_VALUE,
            initial_min_percentage=config.SOCIAL_INITIAL_MIN_PCT,
            initial_max_percentage=config.SOCIAL_INITIAL_MAX_PCT,
            base_rate=config.SOCIAL_BASE_DECAY_RATE,
            rate_multipliers=config.SOCIAL_DECAY_MULTIPLIERS,
            high_is_good=True # Standardizzato
        )
        self.bladder = Bladder( # Vescica: alto = sollievo/vuota, basso = piena/urgenza
            character_owner=self.owner,
            max_value=config.BLADDER_MAX_VALUE,
            initial_min_percentage=config.BLADDER_INITIAL_MIN_PCT,
            initial_max_percentage=config.BLADDER_INITIAL_MAX_PCT,
            base_rate=config.BLADDER_BASE_DECAY_RATE, # Rinominato da FILL_RATE a DECAY_RATE (del sollievo)
            rate_multipliers=config.BLADDER_FILL_MULTIPLIERS, # Questi ora sono moltiplicatori di decay del sollievo
            high_is_good=True # Standardizzato
        )
        self.fun = Fun(
            character_owner=self.owner,
            max_value=config.FUN_MAX_VALUE,
            initial_min_percentage=config.FUN_INITIAL_MIN_PCT,
            initial_max_percentage=config.FUN_INITIAL_MAX_PCT,
            base_rate=config.FUN_BASE_DECAY_RATE,
            rate_multipliers=config.FUN_DECAY_MULTIPLIERS,
            high_is_good=True # Standardizzato
        )
        self.hygiene = Hygiene(
            character_owner=self.owner,
            max_value=config.HYGIENE_MAX_VALUE,
            initial_min_percentage=config.HYGIENE_INITIAL_MIN_PCT,
            initial_max_percentage=config.HYGIENE_INITIAL_MAX_PCT,
            base_rate=config.HYGIENE_BASE_DECAY_RATE,
            rate_multipliers=config.HYGIENE_DECAY_MULTIPLIERS,
            high_is_good=True # Standardizzato
        )
        self.intimacy = Intimacy( # Intimità: alto = soddisfazione, basso = bisogno/desiderio
            character_owner=self.owner,
            max_value=config.INTIMACY_MAX_VALUE,
            initial_min_percentage=config.INTIMACY_INITIAL_MIN_PCT,
            initial_max_percentage=config.INTIMACY_INITIAL_MAX_PCT,
            base_rate=config.INTIMACY_BASE_DECAY_RATE, # Rinominato da INCREASE_RATE a DECAY_RATE (della soddisfazione)
            rate_multipliers=config.INTIMACY_INCREASE_RATE_MULTIPLIERS, # Questi ora sono moltiplicatori di decay della soddisfazione
            high_is_good=True # Standardizzato
        )

        self.all_needs: Dict[str, BaseNeed] = {
            "hunger": self.hunger, "energy": self.energy, "social": self.social,
            "bladder": self.bladder, "fun": self.fun, "hygiene": self.hygiene,
            "intimacy": self.intimacy,
        }
        if DEBUG_VERBOSE:
            logger.debug(f"NeedsComponent per {self.owner_name} inizializzato con {len(self.all_needs)} bisogni (standard: alto è buono).")

    def update(self, game_hours_advanced: float, current_period_name: str,
               character_action: str, character_is_resting: bool):
        if game_hours_advanced <= 0: return
        for need_name, need_obj in self.all_needs.items():
            if hasattr(need_obj, 'update') and callable(getattr(need_obj, 'update')):
                need_obj.update(game_hours_advanced, current_period_name, character_action, character_is_resting)
            else:
                logger.warning(f"L'oggetto bisogno '{need_name}' per {self.owner_name} non ha un metodo update().")

    def get_value(self, need_name: str) -> float:
        need_name_lower = need_name.lower()
        if need_name_lower in self.all_needs:
            return self.all_needs[need_name_lower].get_value()
        logger.warning(f"Tentativo di accedere al valore del bisogno '{need_name}' non esistente per {self.owner_name}.")
        return 0.0

    def satisfy(self, need_name: str, amount: float):
        """Soddisfa (AUMENTA) un bisogno specifico di una data quantità."""
        need_name_lower = need_name.lower()
        if need_name_lower in self.all_needs:
            # Con la nuova convenzione (high_is_good è sempre True),
            # BaseNeed.satisfy() dovrebbe sempre AUMENTARE il valore.
            self.all_needs[need_name_lower].satisfy(amount)
        else:
            logger.warning(f"Tentativo di soddisfare il bisogno '{need_name}' non esistente per {self.owner_name}.")

    def randomize_all_needs(self):
        if DEBUG_VERBOSE:
            logger.debug(f"NeedsComponent: Randomizzazione di tutti i bisogni per {self.owner_name}.")
        for need_name_key, need_obj in self.all_needs.items():
            min_pct_config_key = f"{need_name_key.upper()}_INITIAL_MIN_PCT"
            max_pct_config_key = f"{need_name_key.upper()}_INITIAL_MAX_PCT"
            debug_min_config_key = f"DEBUG_{min_pct_config_key}"
            debug_max_config_key = f"DEBUG_{max_pct_config_key}"
            min_percentage = getattr(config, min_pct_config_key, 0.0)
            max_percentage = getattr(config, max_pct_config_key, 1.0)
            if getattr(config, 'DEBUG_MODE_ACTIVE', False):
                min_percentage = getattr(config, debug_min_config_key, min_percentage)
                max_percentage = getattr(config, debug_max_config_key, max_percentage)
            need_obj.randomize_value(min_percentage, max_percentage)

    def get_all_needs_status(self) -> Dict[str, Dict[str, Any]]:
        status = {}
        for name, need_obj in self.all_needs.items():
            is_critical_val = False
            if hasattr(need_obj, 'is_critical') and callable(getattr(need_obj, 'is_critical')):
                 is_critical_val = need_obj.is_critical()
            status[name] = {
                "value": need_obj.get_value(),
                "max_value": need_obj.max_value,
                "percentage": (need_obj.get_value() / need_obj.max_value) * 100 if need_obj.max_value > 0 else 0,
                "is_critical": is_critical_val
            }
        return status

    def to_dict(self) -> Dict[str, Any]:
        needs_data_to_save = {}
        for name, need_obj in self.all_needs.items():
            if hasattr(need_obj, 'to_dict') and callable(getattr(need_obj, 'to_dict')):
                needs_data_to_save[name] = need_obj.to_dict()
            else: 
                needs_data_to_save[name] = {"current_value": need_obj.get_value()} # Fallback
        return needs_data_to_save

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]], character_owner: 'Character') -> 'NeedsComponent':
        instance = cls(character_owner) 
        if data:
            for need_name_saved, need_data_saved in data.items():
                if need_name_saved in instance.all_needs and isinstance(need_data_saved, dict):
                    need_object_to_repopulate = instance.all_needs[need_name_saved]
                    
                    # Carica i valori salvati, usando i default del costruttore se mancano nei dati salvati
                    need_object_to_repopulate.current_value = float(need_data_saved.get("current_value", need_object_to_repopulate.current_value))
                    need_object_to_repopulate.max_value = float(need_data_saved.get("max_value", need_object_to_repopulate.max_value))
                    need_object_to_repopulate.base_rate = float(need_data_saved.get("base_rate", need_object_to_repopulate.base_rate))
                    need_object_to_repopulate.rate_multipliers = need_data_saved.get("rate_multipliers", need_object_to_repopulate.rate_multipliers)
                    # high_is_good è ora sempre True, ma per completezza potresti caricarlo se salvato
                    need_object_to_repopulate.high_is_good = need_data_saved.get("high_is_good", True) 
                    if hasattr(need_object_to_repopulate, 'last_updated_total_game_hours'):
                        need_object_to_repopulate.last_updated_total_game_hours = float(need_data_saved.get("last_updated_total_game_hours", 0.0))
                elif DEBUG_VERBOSE:
                    logger.warning(f"NeedsComponent ({character_owner.name}): Bisogno '{need_name_saved}' dai dati salvati non è noto o i dati non sono un dict.")
        
        if DEBUG_VERBOSE and data:
            logger.debug(f"NeedsComponent per {character_owner.name} caricato/aggiornato con dati.")
        return instance