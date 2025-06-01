# core/modules/actions/fun_actions.py
"""
Definizione dell'azione per divertirsi (HaveFunAction), 
soddisfacendo il bisogno di FUN.
"""
from typing import Dict, Optional, TYPE_CHECKING
import random 

if TYPE_CHECKING:
    from core.character import Character
    from core.simulation import Simulation

from core.enums import NeedType, FunActivityType 
from core import settings
from .action_base import BaseAction

# --- Costanti di Default a Livello di Modulo per HaveFunAction ---
_MODULE_DEFAULT_HAVEFUNACTION_DURATION_TICKS: int = 60 
_MODULE_DEFAULT_HAVEFUNACTION_FUN_GAIN: float = 35.0 

class HaveFunAction(BaseAction):
    ACTION_TYPE_NAME_PREFIX = "ACTION_HAVE_FUN_" # Prefisso per il nome del tipo di azione
    
    def __init__(self, 
                 npc: 'Character', 
                 activity_type: FunActivityType, 
                 simulation_context: Optional['Simulation'] = None, # Accetta simulation_context
                 duration_ticks: Optional[int] = None,
                 fun_gain: Optional[float] = None
                ):
        
        self.activity_type: FunActivityType = activity_type
        
        _actual_duration = duration_ticks
        if _actual_duration is None:
            specific_duration_key = f"FUN_ACT_{activity_type.name}_DURATION_TICKS"
            _actual_duration = getattr(settings, specific_duration_key, None)
            if _actual_duration is None:
                generic_action_duration_key = "DEFAULT_HAVEFUNACTION_DURATION_TICKS"
                _actual_duration = getattr(settings, generic_action_duration_key, None)
                if _actual_duration is None:
                    _actual_duration = _MODULE_DEFAULT_HAVEFUNACTION_DURATION_TICKS
        
        _actual_fun_gain = fun_gain
        if _actual_fun_gain is None:
            specific_gain_key = f"FUN_ACT_{activity_type.name}_FUN_GAIN"
            _actual_fun_gain = getattr(settings, specific_gain_key, None)
            if _actual_fun_gain is None:
                generic_action_gain_key = "DEFAULT_HAVEFUNACTION_FUN_GAIN"
                _actual_fun_gain = getattr(settings, generic_action_gain_key, None)
                if _actual_fun_gain is None:
                    _actual_fun_gain = _MODULE_DEFAULT_HAVEFUNACTION_FUN_GAIN
        
        self.fun_gain = _actual_fun_gain 

        super().__init__(
            npc=npc,
            action_type_name=f"{self.ACTION_TYPE_NAME_PREFIX}{activity_type.name}", 
            duration_ticks=_actual_duration,
            simulation_context=simulation_context, # Passa a super()
            is_interruptible=True,
            description=f"Si sta divertendo con: {activity_type.display_name_it()}."
        )
        
        self.effects_on_needs: Dict[NeedType, float] = {
            NeedType.FUN: self.fun_gain # Usiamo il guadagno determinato
        }
        
        if settings.DEBUG_MODE:
             print(f"    [{self.action_type_name} INIT - {self.npc.name}] Creata per '{activity_type.name}'. "
                   f"Durata: {self.duration_ticks}t, Gain FUN: {self.fun_gain:.1f}")

    def is_valid(self) -> bool:
        # if not super().is_valid(): return False # Se BaseAction avesse controlli

        if not self.npc: return False
        current_fun = self.npc.get_need_value(NeedType.FUN)
        if current_fun is None: return False
        if current_fun >= settings.NEED_MAX_VALUE - 5:
            if settings.DEBUG_MODE: print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] FUN ({current_fun:.1f}) già alto.")
            return False

        # L'azione ha bisogno del simulation_context per accedere alle locazioni
        if not self.simulation_context or not self.npc.current_location_id:
            if settings.DEBUG_MODE: print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Contesto di simulazione o locazione NPC mancante.")
            return False # Non possiamo validare senza sapere dove si trova l'NPC o quali oggetti ci sono

        current_location = self.simulation_context.get_location_by_id(self.npc.current_location_id)
        if not current_location:
            if settings.DEBUG_MODE: print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Impossibile trovare la locazione corrente.")
            return False

        # Verifica se un oggetto che fornisce questa FunActivityType è disponibile
        object_found_for_activity = False
        for obj in current_location.objects_in_location:
            if self.activity_type in obj.provides_fun_activities:
                if not obj.is_in_use: # L'oggetto deve essere libero
                    object_found_for_activity = True
                    if settings.DEBUG_MODE: print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Trovato oggetto '{obj.name}' per '{self.activity_type.display_name_it()}' in {current_location.name}.")
                    break 
                elif settings.DEBUG_MODE:
                    print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Oggetto '{obj.name}' per '{self.activity_type.display_name_it()}' è già in uso.")
        
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
            # Usa self.fun_gain che è stato determinato nell'__init__
            self.npc.change_need_value(NeedType.FUN, self.fun_gain, is_decay_event=False)
        super().on_finish()

    def _on_cancel(self): # Nome corretto
        super()._on_cancel()
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