# core/modules/actions/fun_actions.py
"""
Definizione dell'azione per divertirsi (HaveFunAction), 
soddisfacendo il bisogno di FUN.
Riferimento TODO: IV.4.c.iv (nel TODO_Generale.md)
"""
from typing import Dict, Optional, TYPE_CHECKING, Set as TypingSet
import random 

if TYPE_CHECKING:
    from core.character import Character
    from core.simulation import Simulation
    from core.world.location import Location

# --- Import Corretti ---
from core.enums import NeedType, FunActivityType, ActionType 
from core.config import time_config, actions_config, npc_config
from core import settings # Per l'accesso a DEBUG_MODE
from .action_base import BaseAction

# --- Costanti di Default a Livello di Modulo per HaveFunAction ---
_MODULE_DEFAULT_HAVEFUNACTION_DURATION_TICKS: int = time_config.IXH * 1 
_MODULE_DEFAULT_HAVEFUNACTION_FUN_GAIN: float = actions_config.DEFAULT_HAVEFUNACTION_FUN_GAIN
_MODULE_DEFAULT_HAVEFUNACTION_NEED_FULFILLMENT_RATE: float = 0.5 

ACTIVITIES_WITHOUT_OBJECTS: TypingSet[FunActivityType] = {
    FunActivityType.DANCE, FunActivityType.DAYDREAM, FunActivityType.JOG_IN_PLACE,
    FunActivityType.SING, FunActivityType.PRACTICE_PUBLIC_SPEAKING,
    FunActivityType.SOCIAL_MEDIA_Browse, FunActivityType.WATCH_CLOUDS,
    FunActivityType.MEDITATE,
}

class HaveFunAction(BaseAction):
    """Azione per l'NPC di divertirsi con una specifica attività."""
    
    def __init__(self, 
                npc: 'Character', 
                activity_type: FunActivityType, 
                simulation_context: 'Simulation',
                duration_ticks: Optional[int] = None,
                fun_gain: Optional[float] = None
                ):
        
        self.activity_type: FunActivityType = activity_type
        
        _actual_duration = duration_ticks
        if _actual_duration is None:
            specific_duration_key = f"FUN_ACT_{activity_type.name}_DURATION_TICKS"
            # CORREZIONE: Cerca in actions_config
            _actual_duration = getattr(actions_config, specific_duration_key, _MODULE_DEFAULT_HAVEFUNACTION_DURATION_TICKS)
        
        _actual_fun_gain = fun_gain
        if _actual_fun_gain is None:
            specific_gain_key = f"FUN_ACT_{activity_type.name}_FUN_GAIN"
            # CORREZIONE: Cerca in actions_config
            _actual_fun_gain = getattr(actions_config, specific_gain_key, _MODULE_DEFAULT_HAVEFUNACTION_FUN_GAIN)
        
        self.fun_gain = _actual_fun_gain 

        action_type_enum_to_use = ActionType.ACTION_HAVE_FUN
        action_name_str = f"ACTION_HAVE_FUN_{activity_type.name}"

        super().__init__(
            npc=npc,
            action_type_name=action_name_str, 
            action_type_enum=action_type_enum_to_use,
            duration_ticks=_actual_duration,
            p_simulation_context=simulation_context, 
            is_interruptible=True
        )
        
        self.effects_on_needs: Dict[NeedType, float] = {
            NeedType.FUN: self.fun_gain
        }
        
        if settings.DEBUG_MODE:
            print(f"    [{self.action_type_name} INIT - {self.npc.name}] Creata per '{activity_type.name}'. "
                f"Durata: {self.duration_ticks}t, Gain FUN: {self.fun_gain:.1f}")

    def is_valid(self) -> bool:
        """
        Controlla se l'azione di divertimento è valida.
        """
        if not self.npc: return False
        
        current_fun = self.npc.get_need_value(NeedType.FUN)
        # CORREZIONE: Usa npc_config.NEED_MAX_VALUE
        if current_fun is not None and current_fun >= (npc_config.NEED_MAX_VALUE - 5.0):
            if settings.DEBUG_MODE: 
                print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] FUN ({current_fun:.1f}) già troppo alto per iniziare nuova attività.")
            return False

        if self.activity_type in ACTIVITIES_WITHOUT_OBJECTS:
            if settings.DEBUG_MODE: 
                print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Attività '{self.activity_type.name}' non richiede oggetto. Azione valida.")
            return True

        if not self.sim_context or not self.npc.current_location_id:
            if settings.DEBUG_MODE: 
                print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Contesto di simulazione o locazione NPC mancante.")
            return False

        current_location: Optional['Location'] = self.sim_context.get_location_by_id(self.npc.current_location_id)
        if not current_location:
            if settings.DEBUG_MODE: 
                print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Impossibile trovare la locazione corrente: {self.npc.current_location_id}")
            return False

        for game_obj in current_location.get_objects():
            if self.activity_type in game_obj.provides_fun_activities:
                if settings.DEBUG_MODE:
                    print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Trovato oggetto '{game_obj.name}' per '{self.activity_type.name}' in {current_location.name}. Azione valida.")
                return True
        
        if settings.DEBUG_MODE:
            print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Nessun oggetto disponibile trovato per '{self.activity_type.name}' in {current_location.name}.")
        return False

    def on_start(self):
        super().on_start()
        if settings.DEBUG_MODE:
            print(f"    [{self.action_type_name} START - {self.npc.name}] Inizia a: {self.activity_type.name}.")

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
                print(f"    [{self.action_type_name} FINISH - {self.npc.name}] Finito di: {self.activity_type.name}. Applico effetti.")
            self.npc.change_need_value(NeedType.FUN, self.fun_gain, is_decay_event=False)
        super().on_finish()

    def on_interrupt_effects(self):
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