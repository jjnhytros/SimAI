# core/modules/actions/bathroom_actions.py
"""
Definizione dell'azione per usare il bagno, soddisfacendo i bisogni di Vescica e Igiene.
Riferimento TODO: VI.2.c
"""
from typing import Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from core.character import Character
    from core.simulation import Simulation 

from core.enums import NeedType, LocationType 
from core import settings
from .action_base import BaseAction

_MODULE_DEFAULT_USE_BATHROOM_DURATION_TICKS: int = 10
_MODULE_DEFAULT_USE_BATHROOM_BLADDER_GAIN: float = 100.0 
_MODULE_DEFAULT_USE_BATHROOM_HYGIENE_GAIN: float = 15.0  

class UseBathroomAction(BaseAction):
    ACTION_TYPE_NAME = "ACTION_USE_BATHROOM" 
    
    def __init__(self, 
                 npc: 'Character', 
                 simulation_context: 'Simulation', 
                 duration_ticks: Optional[int] = None,
                 bladder_gain: Optional[float] = None,
                 hygiene_gain: Optional[float] = None
                ):
        
        actual_duration = duration_ticks if duration_ticks is not None \
            else getattr(settings, 'USE_BATHROOM_DEFAULT_DURATION_TICKS', _MODULE_DEFAULT_USE_BATHROOM_DURATION_TICKS)
        
        actual_bladder_gain = bladder_gain if bladder_gain is not None \
            else getattr(settings, 'USE_BATHROOM_BLADDER_GAIN', _MODULE_DEFAULT_USE_BATHROOM_BLADDER_GAIN)
        
        actual_hygiene_gain = hygiene_gain if hygiene_gain is not None \
            else getattr(settings, 'USE_BATHROOM_HYGIENE_GAIN', _MODULE_DEFAULT_USE_BATHROOM_HYGIENE_GAIN)
        
        # --- MODIFICA CHIAMATA A SUPER ---
        super().__init__(
            npc=npc,
            action_type_name=self.ACTION_TYPE_NAME, # Dovrebbe essere ActionType.ACTION_USE_BATHROOM.action_type_name
            action_type_enum=None, # TODO: Passare l'enum ActionType.ACTION_USE_BATHROOM
            duration_ticks=actual_duration,
            p_simulation_context=simulation_context, # Modificato da simulation_context
            is_interruptible=False,
            # description=f"Sta usando il bagno (Durata: {actual_duration}t)." # 'description' non è in BaseAction.__init__
        )
        # --- FINE MODIFICA ---
        self.effects_on_needs: Dict[NeedType, float] = {
            NeedType.BLADDER: actual_bladder_gain,
            NeedType.HYGIENE: actual_hygiene_gain 
        }
        
        if settings.DEBUG_MODE:
            print(f"    [{self.action_type_name} INIT - {self.npc.name}] Creata. "
                  f"Durata: {self.duration_ticks}t, Gain Vescica: {actual_bladder_gain:.1f}, Gain Igiene: {actual_hygiene_gain:.1f}")

    def is_valid(self) -> bool:
        if not self.npc: return False
        
        current_bladder = self.npc.get_need_value(NeedType.BLADDER)
        current_hygiene = self.npc.get_need_value(NeedType.HYGIENE)

        threshold_bladder = getattr(settings, 'BLADDER_THRESHOLD_TO_USE_BATHROOM', settings.NEED_LOW_THRESHOLD + 15)
        threshold_hygiene = getattr(settings, 'HYGIENE_THRESHOLD_TO_USE_BATHROOM', settings.NEED_LOW_THRESHOLD + 10)

        needs_to_go_for_bladder = current_bladder is not None and current_bladder < threshold_bladder
        needs_to_go_for_hygiene = current_hygiene is not None and current_hygiene < threshold_hygiene
        
        can_use_bathroom = needs_to_go_for_bladder or needs_to_go_for_hygiene
        
        # TODO VI.2.c: Implementare la verifica della disponibilità di un LocationType.BATHROOM
        # if self.sim_context and hasattr(self.npc, 'current_location_id'): # Usa self.sim_context
        #     current_loc = self.sim_context.get_location_by_id(self.npc.current_location_id)
        #     if not current_loc or current_loc.type != LocationType.BATHROOM:
        #          if settings.DEBUG_MODE: print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] No bagno disponibile.")
        #          return False
        
        if not can_use_bathroom and settings.DEBUG_MODE:
            print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Non motivato a usare il bagno (Vescica: {current_bladder:.1f}, Igiene: {current_hygiene:.1f})")
        
        if settings.DEBUG_MODE and can_use_bathroom:
            print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Azione considerata valida.")
        return can_use_bathroom

    def on_start(self):
        super().on_start()
        if settings.DEBUG_MODE:
            print(f"    [{self.action_type_name} START - {self.npc.name}] È entrato/a in bagno.")

    def execute_tick(self):
        super().execute_tick()

    def on_finish(self):
        if self.npc:
            if settings.DEBUG_MODE:
                print(f"    [{self.action_type_name} FINISH - {self.npc.name}] Ha finito in bagno. Applico effetti.")
            for need_type, change_amount in self.effects_on_needs.items():
                self.npc.change_need_value(need_type, change_amount, is_decay_event=False)
        super().on_finish() 

    def on_interrupt_effects(self): # Corretto da _on_cancel per coerenza con BaseAction
        super().on_interrupt_effects()
        if self.npc and settings.DEBUG_MODE:
            print(f"    [{self.action_type_name} CANCEL - {self.npc.name}] Uso del bagno interrotto!")