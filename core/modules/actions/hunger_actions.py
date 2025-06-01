# core/modules/actions/hunger_actions.py
from typing import Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from core.character import Character
    from core.simulation import Simulation

from core.enums import NeedType, ActionType # Importa ActionType
from core import settings
from .action_base import BaseAction

_MODULE_DEFAULT_EAT_ACTION_DURATION_TICKS: int = 30
_MODULE_DEFAULT_EAT_ACTION_HUNGER_GAIN: float = 75.0

class EatAction(BaseAction):
    def __init__(self, 
                 npc: 'Character', 
                 simulation_context: 'Simulation', 
                 duration_ticks: Optional[int] = None, 
                 hunger_gain: Optional[float] = None
                ):
        
        actual_duration = duration_ticks if duration_ticks is not None \
            else getattr(settings, 'EAT_ACTION_DURATION_TICKS', _MODULE_DEFAULT_EAT_ACTION_DURATION_TICKS)
        actual_gain = hunger_gain if hunger_gain is not None \
            else getattr(settings, 'EAT_ACTION_HUNGER_GAIN', _MODULE_DEFAULT_EAT_ACTION_HUNGER_GAIN)

        action_type_enum = ActionType.ACTION_EAT # Nome dell'azione per mangiare
        super().__init__(
            npc=npc,
            action_type_name=action_type_enum.action_type_name,
            action_type_enum=action_type_enum,
            duration_ticks=actual_duration,
            p_simulation_context=simulation_context, # Modificato
            is_interruptible=True
            # description=f"Sta mangiando (Durata: {actual_duration}t)." # Rimosso
        )
        self.effects_on_needs = {NeedType.HUNGER: actual_gain}
        
        if settings.DEBUG_MODE:
            print(f"    [EatAction INIT - {self.npc.name}] Creata. Durata: {self.duration_ticks}t, Gain Fame: {actual_gain}")

    def is_valid(self) -> bool:
        if not self.npc: return False
        
        current_hunger = self.npc.get_need_value(NeedType.HUNGER)
        if current_hunger is None: return False

        can_eat = current_hunger < settings.NEED_MAX_VALUE 
        
        if not can_eat and settings.DEBUG_MODE:
            print(f"    [EatAction VALIDATE - {self.npc.name}] Non può mangiare, fame ({current_hunger:.1f}) già al massimo.")
        return can_eat

    def on_start(self):
        super().on_start()
        if settings.DEBUG_MODE:
            print(f"    [EatAction START - {self.npc.name}] Ha iniziato a mangiare.")

    def execute_tick(self):
        super().execute_tick()
        pass

    def on_finish(self):
        if self.npc:
            if settings.DEBUG_MODE:
                print(f"    [EatAction FINISH - {self.npc.name}] Ha finito di mangiare. Applico effetti sui bisogni.")
            for need_type, change_amount in self.effects_on_needs.items():
                self.npc.change_need_value(need_type, change_amount, is_decay_event=False)
        
        super().on_finish()

    def on_interrupt_effects(self):
        super().on_interrupt_effects()
        if self.npc and settings.DEBUG_MODE:
            print(f"    [EatAction INTERRUPT - {self.npc.name}] Pasto interrotto.")