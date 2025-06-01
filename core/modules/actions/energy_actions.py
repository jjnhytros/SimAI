# core/modules/actions/energy_actions.py
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from core.character import Character
    from core.simulation import Simulation 

from core.enums import NeedType
from core import settings
from .action_base import BaseAction

# --- Costanti di Default a Livello di Modulo per SleepAction ---
_MODULE_DEFAULT_SLEEP_ACTION_HOURS: float = 7.0    # Default se nient'altro è specificato
_MODULE_DEFAULT_ENERGY_GAIN_PER_HOUR: float = 15.0 # Default se nient'altro è specificato
                                                   # (7 ore * 15 = 105 energia)

class SleepAction(BaseAction):
    """
    Azione per l'NPC di dormire e recuperare Energia.
    """
    def __init__(self, npc: 'Character',
                 duration_hours: Optional[float] = None, # Ore di sonno desiderate
                 simulation_context: 'Simulation',
                 action_type_override: Optional[ActionType] = None):

        # Determina la durata effettiva in ore e tick
        actual_duration_hours = duration_hours if duration_hours is not None else _MODULE_DEFAULT_HOURS
        actual_duration_ticks = int(actual_duration_hours * settings.IXH)
        
        super().__init__(npc=npc,
                         action_type=action_type_override if action_type_override else ActionType.ACTION_SLEEP,
                         duration_ticks=actual_duration_ticks,
                         simulation_context=simulation_context,
                         is_interruptible=True) # Il sonno può essere interrotto
        
        self.total_energy_to_gain = settings.NEED_MAX_VALUE - (self.npc.get_need_value(NeedType.ENERGY) or 0)
        # Guadagno per tick, gestito in execute_tick
        self.energy_gain_per_tick = self.total_energy_to_gain / self.duration_ticks if self.duration_ticks > 0 else 0

    def is_valid(self) -> bool:
        """L'azione di dormire è quasi sempre valida, a meno che l'NPC non sia già pieno di energia."""
        # Se l'NPC ha già molta energia, potrebbe non essere valido dormire
        current_energy = self.npc.get_need_value(NeedType.ENERGY)
        if current_energy is not None and current_energy >= settings.NEED_HIGH_THRESHOLD:
            if settings.DEBUG_MODE: print(f"  [SleepAction] '{self.npc.name}' ha già energia ({current_energy:.1f}). Non valido dormire.")
            return False
        return True

    def on_start(self):
        """Chiamato quando l'azione inizia."""
        if settings.DEBUG_MODE:
            duration_in_hours = self.duration_ticks / settings.IXH
            print(f"  [SleepAction] '{self.npc.name}' inizia a dormire per {duration_in_hours:.1f} ore.")

    def execute_tick(self):
        """Ad ogni tick di sonno, l'energia aumenta gradualmente."""
        self.npc.change_need_value(NeedType.ENERGY, self.energy_gain_per_tick)

    def on_finish(self):
        """
        Chiamato quando l'azione è completata (l'NPC ha dormito abbastanza).
        Imposta l'energia al massimo e regola gli altri bisogni fisiologici.
        """
        # 1. Imposta l'energia al massimo per sicurezza, nel caso il calcolo per tick non fosse perfetto.
        self.npc.change_need_value(NeedType.ENERGY, settings.NEED_MAX_VALUE) # Questo lo imposta al massimo
        
        # 2. Regola gli altri bisogni usando le nuove costanti da settings.
        needs_to_adjust = {
            NeedType.HUNGER: settings.NEED_VALUE_ON_WAKE_HUNGER,
            NeedType.THIRST: settings.NEED_VALUE_ON_WAKE_THIRST,
            NeedType.BLADDER: settings.NEED_VALUE_ON_WAKE_BLADDER
        }

        for need_type, target_value in needs_to_adjust.items():
            current_value = self.npc.get_need_value(need_type)
            if current_value is not None:
                delta = target_value - current_value
                self.npc.change_need_value(need_type, delta)
                if settings.DEBUG_MODE:
                    print(f"    [SleepAction Finish - {self.npc.name}] Bisogno '{need_type.name}' al risveglio impostato a {target_value:.1f} (precedente: {current_value:.1f}, delta: {delta:.1f}).")
        if settings.DEBUG_MODE:
            print(f"  [SleepAction] '{self.npc.name}' si è svegliato.")

    def on_interrupt(self):
        """Chiamato se l'azione viene interrotta."""
        # L'energia guadagnata fino a questo punto rimane.
        # Non è necessario fare altro, a meno di voler applicare un moodlet negativo.
        if settings.DEBUG_MODE:
            print(f"  [SleepAction] Il sonno di '{self.npc.name}' è stato interrotto.")
