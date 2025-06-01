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
    ACTION_TYPE_NAME = "ACTION_SLEEP"
    
    def __init__(self, 
                npc: 'Character', 
                simulation_context: Optional['Simulation'] = None,
                duration_hours: Optional[float] = None, 
                custom_duration_ticks: Optional[int] = None, # Per massima precisione se serve
                energy_gain_per_hour: Optional[float] = None
                ):
        
        # 1. Determina le ore di sonno effettive
        actual_hours = duration_hours # Priorità 1: parametro diretto
        if actual_hours is None:
            # Priorità 2: da settings (es. sovrascritto da simai.py per test)
            actual_hours = getattr(settings, 'SLEEP_ACTION_DEFAULT_HOURS', None)
            if actual_hours is None:
                # Priorità 3: default del modulo
                actual_hours = _MODULE_DEFAULT_SLEEP_ACTION_HOURS 
        
        # 2. Determina i tick di durata effettivi
        actual_duration_ticks = custom_duration_ticks # Priorità 1: tick diretti
        if actual_duration_ticks is None:
            # Priorità 2: calcolato da actual_hours
            actual_duration_ticks = int(actual_hours * settings.IXH) # IXH deve essere in settings
            
        # 3. Determina il guadagno di energia orario effettivo
        self.energy_gain_per_hour = energy_gain_per_hour # Priorità 1: parametro diretto
        if self.energy_gain_per_hour is None:
            # Priorità 2: da settings
            self.energy_gain_per_hour = getattr(settings, 'SLEEP_ACTION_ENERGY_GAIN_PER_HOUR', None)
            if self.energy_gain_per_hour is None:
                # Priorità 3: default del modulo
                self.energy_gain_per_hour = _MODULE_DEFAULT_ENERGY_GAIN_PER_HOUR

        super().__init__(
            npc=npc,
            action_type_name=self.ACTION_TYPE_NAME,
            duration_ticks=actual_duration_ticks,
            simulation_context=simulation_context,
            is_interruptible=True, 
            description=f"Sta dormendo (Durata pianificata: {actual_hours:.1f}h)."
        )
        
        if settings.DEBUG_MODE:
            print(f"    [{self.action_type_name} INIT - {self.npc.name}] Creata. "
                f"Durata Effettiva: {actual_hours:.1f}h ({self.duration_ticks}t). Gain/ora: {self.energy_gain_per_hour:.1f}")

    # ... (is_valid, on_start, execute_tick, on_finish, _on_cancel come prima, 
    #      assicurati che on_finish/_on_cancel usino self.energy_gain_per_hour)
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
        super().on_start() # Chiama BaseAction.on_start()
        # Log specifico dell'azione
        if settings.DEBUG_MODE:
            print(f"    [{self.action_type_name} START - {self.npc.name}] Si è messo/a a dormire.")

    def execute_tick(self):
        super().execute_tick() # Chiama BaseAction.execute_tick()
        # Log di progresso specifico per SleepAction (es. ogni ora di gioco)
        if self.is_started and settings.DEBUG_MODE:
            if self.ticks_elapsed > 0 and self.ticks_elapsed % settings.IXH == 0 and \
            self.ticks_elapsed < self.duration_ticks and not self.is_finished:
                hours_slept = self.ticks_elapsed // settings.IXH
                print(f"    [{self.action_type_name} PROGRESS - {self.npc.name}] Sta dormendo... ({hours_slept} ore passate, {self.get_progress_percentage():.0%})")

    def _calculate_energy_gain(self) -> float:
        hours_slept = self.ticks_elapsed / settings.IXH
        energy_gained = hours_slept * self.energy_gain_per_hour
        return energy_gained

    def on_finish(self):
        if self.npc:
            energy_gained = self._calculate_energy_gain()
            if settings.DEBUG_MODE:
                print(f"    [{self.action_type_name} FINISH - {self.npc.name}] Finito di dormire. Tick dormiti: {self.ticks_elapsed}. Energia guadagnata stimata: {energy_gained:.2f}")
            self.npc.change_need_value(NeedType.ENERGY, energy_gained) # is_decay_event=False è il default
        super().on_finish()

    def _on_cancel(self):
        super()._on_cancel()
        if self.npc:
            energy_gained_on_interrupt = self._calculate_energy_gain()
            if settings.DEBUG_MODE:
                print(f"    [{self.action_type_name} CANCEL - {self.npc.name}] Sonno interrotto. Tick dormiti: {self.ticks_elapsed}. Energia guadagnata: {energy_gained_on_interrupt:.2f}")
            if energy_gained_on_interrupt > 0:
                self.npc.change_need_value(NeedType.ENERGY, energy_gained_on_interrupt)