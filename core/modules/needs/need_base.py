# core/modules/needs/need_base.py
from abc import ABC
from typing import TYPE_CHECKING, Optional
import random

from core.enums import NeedType, Gender
from core import settings
from core.config import npc_config # Importa npc_config

if TYPE_CHECKING:
    from core.character import Character

class BaseNeed(ABC):
    """
    Classe base per i bisogni degli NPC.
    Gestisce il valore del bisogno, il suo decadimento e i limiti tramite una property.
    """
    def __init__(self, character_owner: 'Character', p_need_type: NeedType, initial_value: Optional[float] = None):
        self.character_owner: 'Character' = character_owner
        self.need_type = p_need_type
        self.decay_rate_per_hour: float = npc_config.NEED_DECAY_RATES.get(self.need_type, 0.0)
        self.min_value: float = npc_config.NEED_MIN_VALUE
        self.max_value: float = npc_config.NEED_MAX_VALUE
        self.display_name: str = "Bisogno Sconosciuto"
        
        # Inizializziamo il valore INTERNO (_value)
        if initial_value is not None:
            self._value = initial_value
        else:
            self._value = 100.0
        
        self._clamp_value()

    @property
    def value(self) -> float:
        return self._value

    @value.setter
    def value(self, new_value: float):
        self._value = max(self.min_value, min(self.max_value, new_value))

    def _clamp_value(self):
        self.value = self._value

    def get_value(self) -> float:
        return self.value

    def set_value(self, new_value: float):
        self.value = new_value

    def change_value(self, amount: float, is_decay_event: bool = False):
        old_value = self.value
        self.value += amount

        # Logica di logging migliorata per ridurre la verbosità
        log_this_change = False
        if settings.DEBUG_MODE and self.character_owner and old_value != self.value:
            if not is_decay_event: # Logga sempre i guadagni o le perdite indotte
                log_this_change = True
            else: # Per i decadimenti, logga solo se supera soglie o è significativo
                is_now_low = self.value <= settings.NEED_LOW_THRESHOLD and old_value > settings.NEED_LOW_THRESHOLD
                is_now_critical = self.value <= settings.NEED_CRITICAL_THRESHOLD and old_value > settings.NEED_CRITICAL_THRESHOLD
                if is_now_low or is_now_critical:
                    log_this_change = True
        
        if log_this_change:
            decay_tag = " (Decay)" if is_decay_event else ""
            critical_status = ""
            if self.value <= settings.NEED_CRITICAL_THRESHOLD: critical_status = " [!!! CRITICO !!!]"
            elif self.value <= settings.NEED_LOW_THRESHOLD: critical_status = " [! Basso !]"
            
            print(f"    [Need Change - {self.character_owner.name}] {self!s} (Δ {amount:.1f})")


    def decay(self, fraction_of_hour_elapsed: float):
        if self.decay_rate_per_hour == 0:
            return
        amount_to_decay = self.decay_rate_per_hour * fraction_of_hour_elapsed
        if amount_to_decay != 0:
            self.change_value(amount_to_decay, is_decay_event=True)

    def get_display_name(self, gender: Gender) -> str:
        """Restituisce il nome leggibile e declinato del tipo di bisogno."""
        if hasattr(self.need_type, 'display_name_it'):
            # Ora passa il genere ricevuto al metodo dell'enum
            return self.need_type.display_name_it(gender)
        return self.need_type.name.capitalize().replace("_", " ")

    def __str__(self) -> str:
        # Recupera il genere dal proprietario e lo passa a get_display_name
        display_name = self.get_display_name(self.character_owner.gender)
        return f"{display_name}: {self.value:.1f}"
