# core/modules/actions/energy_actions.py
from typing import Optional, TYPE_CHECKING, cast

if TYPE_CHECKING:
    from core.character import Character
    from core.simulation import Simulation 

from core.enums import NeedType, ActionType # Importa ActionType
from core.config import time_config, npc_config # Aggiungi time_config
from core import settings # Lascia per DEBUG_MODE se usato
from .action_base import BaseAction

_MODULE_DEFAULT_SLEEP_ACTION_HOURS: float = 7.0
_MODULE_DEFAULT_ENERGY_GAIN_PER_HOUR: float = 15.0

class SleepAction(BaseAction):
    # ACTION_TYPE_NAME = "ACTION_SLEEP" # Non più necessario come costante di classe se usiamo l'enum
    
    def __init__(self, 
                npc: 'Character', 
                simulation_context: 'Simulation', 
                duration_hours: Optional[float] = None, 
                custom_duration_ticks: Optional[int] = None, 
                energy_gain_per_hour: Optional[float] = None
                ):
        
        actual_hours = duration_hours 
        if actual_hours is None:
            actual_hours = getattr(settings, 'SLEEP_ACTION_DEFAULT_HOURS', None)
            if actual_hours is None:
                actual_hours = _MODULE_DEFAULT_SLEEP_ACTION_HOURS 
        
        actual_duration_ticks = custom_duration_ticks 
        if actual_duration_ticks is None:
            actual_duration_ticks = int(actual_hours * time_config.IXH)
            
        self.energy_gain_per_hour = energy_gain_per_hour 
        if self.energy_gain_per_hour is None:
            self.energy_gain_per_hour = getattr(settings, 'SLEEP_ACTION_ENERGY_GAIN_PER_HOUR', None)
            if self.energy_gain_per_hour is None:
                self.energy_gain_per_hour = _MODULE_DEFAULT_ENERGY_GAIN_PER_HOUR

        action_type_enum = ActionType.ACTION_SLEEP
        super().__init__(
            npc=npc,
            action_type_name=action_type_enum.action_type_name,
            action_type_enum=action_type_enum,
            duration_ticks=actual_duration_ticks,
            p_simulation_context=simulation_context, # Modificato
            is_interruptible=True
            # description=f"Sta dormendo (Durata pianificata: {actual_hours:.1f}h)." # description rimossa
        )
        
        if settings.DEBUG_MODE:
            print(f"    [{self.action_type_name} INIT - {self.npc.name}] Creata. "
                f"Durata Effettiva: {actual_hours:.1f}h ({self.duration_ticks}t). Gain/ora: {self.energy_gain_per_hour:.1f}")

    def is_valid(self) -> bool:
        if not self.npc: return False
        current_energy = self.npc.get_need_value(NeedType.ENERGY)
        if current_energy is None: return False
        threshold_to_sleep = getattr(settings, 'ENERGY_THRESHOLD_TO_CONSIDER_SLEEP', settings.NEED_LOW_THRESHOLD + 10)
        can_sleep = current_energy < threshold_to_sleep
        if not can_sleep and settings.DEBUG_MODE:
            print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Non ha bisogno di dormire, energia ({current_energy:.1f}) >= soglia ({threshold_to_sleep:.1f})")
        return can_sleep

    def on_start(self):
        super().on_start()
        if settings.DEBUG_MODE:
            print(f"    [{self.action_type_name} START - {self.npc.name}] Si è messo/a a dormire.")

    def execute_tick(self):
        super().execute_tick()
        if self.is_started and settings.DEBUG_MODE:
            if self.ticks_elapsed > 0 and self.ticks_elapsed % time_config.IXH == 0 and \
            self.ticks_elapsed < self.duration_ticks and not self.is_finished:
                hours_slept = self.ticks_elapsed // time_config.IXH
                print(f"    [{self.action_type_name} PROGRESS - {self.npc.name}] Sta dormendo... ({hours_slept} ore passate, {self.get_progress_percentage():.0%})")

    def _calculate_energy_gain(self) -> float:
        hours_slept = self.ticks_elapsed / time_config.IXH
        energy_gained = hours_slept * cast(float, self.energy_gain_per_hour)
        return energy_gained

    def on_finish(self):
        if self.npc:
            # Ricarica l'energia completamente al termine del sonno
            self.npc.change_need_value(NeedType.ENERGY, settings.NEED_MAX_VALUE - (self.npc.get_need_value(NeedType.ENERGY) or 0))

            # Regola gli altri bisogni al risveglio
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
        super().on_finish()
        if settings.DEBUG_MODE:
            print(f"    [{self.action_type_name} FINISH - {self.npc.name}] Si è svegliato.")


    def on_interrupt_effects(self): # Corretto da _on_cancel
        super().on_interrupt_effects()
        if self.npc:
            energy_gained_on_interrupt = self._calculate_energy_gain()
            if settings.DEBUG_MODE:
                print(f"    [{self.action_type_name} CANCEL - {self.npc.name}] Sonno interrotto. Tick dormiti: {self.ticks_elapsed}. Energia guadagnata: {energy_gained_on_interrupt:.2f}")
            if energy_gained_on_interrupt > 0:
                self.npc.change_need_value(NeedType.ENERGY, energy_gained_on_interrupt)