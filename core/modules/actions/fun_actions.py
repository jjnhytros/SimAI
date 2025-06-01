# core/modules/actions/fun_actions.py
from typing import Dict, Optional, TYPE_CHECKING
import random 

if TYPE_CHECKING:
    from core.character import Character
    from core.simulation import Simulation

from core.enums import NeedType, FunActivityType, ActionType # Importa ActionType
from core import settings
from .action_base import BaseAction

_MODULE_DEFAULT_HAVEFUNACTION_DURATION_TICKS: int = 60 
_MODULE_DEFAULT_HAVEFUNACTION_FUN_GAIN: float = 35.0 

class HaveFunAction(BaseAction):
    # ACTION_TYPE_NAME_PREFIX = "ACTION_HAVE_FUN_" # Non più necessario come costante di classe
    
    def __init__(self, 
                 npc: 'Character', 
                 activity_type: FunActivityType, 
                 simulation_context: 'Simulation', 
                 duration_ticks: Optional[int] = None,
                 fun_gain: Optional[float] = None
                ):
        
        self.activity_type: FunActivityType = activity_type
        
        _actual_duration = duration_ticks
        # ... (logica per _actual_duration come prima) ...
        if _actual_duration is None:
            specific_duration_key = f"FUN_ACT_{activity_type.name}_DURATION_TICKS"
            _actual_duration = getattr(settings, specific_duration_key, None)
            if _actual_duration is None:
                generic_action_duration_key = "DEFAULT_HAVEFUNACTION_DURATION_TICKS"
                _actual_duration = getattr(settings, generic_action_duration_key, None)
                if _actual_duration is None:
                    _actual_duration = _MODULE_DEFAULT_HAVEFUNACTION_DURATION_TICKS
        
        _actual_fun_gain = fun_gain
        # ... (logica per _actual_fun_gain come prima) ...
        if _actual_fun_gain is None:
            specific_gain_key = f"FUN_ACT_{activity_type.name}_FUN_GAIN"
            _actual_fun_gain = getattr(settings, specific_gain_key, None)
            if _actual_fun_gain is None:
                generic_action_gain_key = "DEFAULT_HAVEFUNACTION_FUN_GAIN"
                _actual_fun_gain = getattr(settings, generic_action_gain_key, None)
                if _actual_fun_gain is None:
                    _actual_fun_gain = _MODULE_DEFAULT_HAVEFUNACTION_FUN_GAIN
        
        self.fun_gain = _actual_fun_gain 

        action_type_enum = ActionType.ACTION_HAVE_FUN # Potrebbe essere più specifico se avessimo enum per ogni FunActivityType
        action_name_str = f"ACTION_HAVE_FUN_{activity_type.name}"
        
        super().__init__(
            npc=npc,
            action_type_name=action_name_str, # Nome specifico basato sull'attività
            action_type_enum=action_type_enum, # Enum generico per "Have Fun"
            duration_ticks=_actual_duration,
            p_simulation_context=simulation_context, # Modificato
            is_interruptible=True
            # description=f"Si sta divertendo con: {activity_type.display_name_it()}." # Rimosso
        )
        
        self.effects_on_needs: Dict[NeedType, float] = {
            NeedType.FUN: self.fun_gain
        }
        
        if settings.DEBUG_MODE:
             print(f"    [{self.action_type_name} INIT - {self.npc.name}] Creata per '{activity_type.name}'. "
                   f"Durata: {self.duration_ticks}t, Gain FUN: {self.fun_gain:.1f}")

    def is_valid(self) -> bool:
        if not self.npc: return False
        current_fun = self.npc.get_need_value(NeedType.FUN)
        if current_fun is None: return False
        if current_fun >= settings.NEED_MAX_VALUE - 5:
            if settings.DEBUG_MODE: print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] FUN ({current_fun:.1f}) già alto.")
            return False

        if not self.sim_context or not self.npc.current_location_id: # Usa self.sim_context
            if settings.DEBUG_MODE: print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Contesto di simulazione o locazione NPC mancante.")
            return False

        current_location = self.sim_context.get_location_by_id(self.npc.current_location_id) # Usa self.sim_context
        if not current_location:
            if settings.DEBUG_MODE: print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Impossibile trovare la locazione corrente.")
            return False
        
        object_found_for_activity = False
        # Assumendo che Location.objects sia un dict. In precedenza usavi .objects_in_location
        # La definizione corretta è Location.get_objects() che restituisce una lista
        for obj in current_location.get_objects(): 
            if self.activity_type in obj.provides_fun_activities:
                # TODO: Aggiungere un controllo se l'oggetto è in uso da un altro NPC
                # if not obj.is_in_use: 
                object_found_for_activity = True
                if settings.DEBUG_MODE: print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Trovato oggetto '{obj.name}' per '{self.activity_type.display_name_it()}' in {current_location.name}.")
                break 
                # elif settings.DEBUG_MODE:
                # print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Oggetto '{obj.name}' per '{self.activity_type.display_name_it()}' è già in uso.")
        
        if not object_found_for_activity:
            if settings.DEBUG_MODE:
                print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Nessun oggetto disponibile trovato per l'attività '{self.activity_type.display_name_it()}' in {current_location.name}.")
            return False
            
        if settings.DEBUG_MODE:
            print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Attività {self.activity_type.display_name_it()} considerata valida.")
        return True

    def on_start(self):
        super().on_start()
        if settings.DEBUG_MODE:
            print(f"    [{self.action_type_name} START - {self.npc.name}] Inizia a: {self.activity_type.display_name_it()}.")

    def execute_tick(self):
        super().execute_tick()
        if self.is_started and settings.DEBUG_MODE:
            log_interval = max(1, self.duration_ticks // 4)
            if self.ticks_elapsed > 0 and self.ticks_elapsed % log_interval == 0 and \
               self.ticks_elapsed < self.duration_ticks and not self.is_finished:
                print(f"    [{self.action_type_name} PROGRESS - {self.npc.name}] Si sta divertendo ({self.activity_type.name})... ({self.get_progress_percentage():.0%})")

    def on_finish(self):
        if self.npc:
            if settings.DEBUG_MODE:
                print(f"    [{self.action_type_name} FINISH - {self.npc.name}] Finito di: {self.activity_type.display_name_it()}. Applico effetti.")
            self.npc.change_need_value(NeedType.FUN, self.fun_gain, is_decay_event=False)
        super().on_finish()

    def on_interrupt_effects(self): # Corretto da _on_cancel
        super().on_interrupt_effects()
        if self.npc and self.duration_ticks > 0:
            proportion_completed = self.ticks_elapsed / self.duration_ticks
            partial_gain = self.fun_gain * proportion_completed * 0.75 
            
            if partial_gain > 0:
                if settings.DEBUG_MODE:
                    print(f"    [{self.action_type_name} CANCEL - {self.npc.name}] Attività {self.activity_type.name} interrotta. "
                          f"Applicato guadagno FUN parziale: {partial_gain:.2f}")
                self.npc.change_need_value(NeedType.FUN, partial_gain, is_decay_event=False)
            elif settings.DEBUG_MODE and self.npc:
                 print(f"    [{self.action_type_name} CANCEL - {self.npc.name}] Attività {self.activity_type.name} interrotta. Nessun guadagno parziale.")