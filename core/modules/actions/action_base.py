# core/modules/actions/action_base.py
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional, Dict, Any, Union
from core import settings
from core.enums import NeedType, ActionType, FunActivityType, SocialInteractionType

if TYPE_CHECKING:
    from core.character import Character
    from core.simulation import Simulation
    from core.world.game_object import GameObject
    from core.modules.memory.memory_definitions import Problem 

class BaseAction(ABC):
    def __init__(self,
                npc: 'Character',
                p_simulation_context: 'Simulation',
                duration_ticks: int,
                action_type_enum: Optional[ActionType] = None,
                action_type_name: Optional[str] = None,
                triggering_problem: Optional['Problem'] = None,
                is_outdoors: bool = False,
                is_noisy: bool = False,
                is_interruptible: bool = True,
                cognitive_effort: float = 0.2
                ):
        self.npc: 'Character' = npc
        self.sim_context: 'Simulation' = p_simulation_context
        self.duration_ticks: int = duration_ticks
        self.triggering_problem: Optional['Problem'] = triggering_problem
        self.is_outdoors: bool = is_outdoors
        self.is_noisy: bool = is_noisy
        self.is_interruptible: bool = is_interruptible
        self.cognitive_effort: float = cognitive_effort
        
        self.action_type_enum: Optional[ActionType] = action_type_enum
        self.action_type_name: str = action_type_name or (action_type_enum.name if action_type_enum else "UNKNOWN_ACTION")

        self.elapsed_ticks: int = 0
        self.is_started: bool = False
        self.is_finished: bool = False
        self.is_interrupted: bool = False

        self.effects_on_needs: Dict[NeedType, float] = {}
        self.target_object: Optional['GameObject'] = None
        self.target_npc: Optional['Character'] = None
        self.activity_type: Optional[Union[FunActivityType, SocialInteractionType]] = None
        self.manages_need: Optional[NeedType] = None

    @abstractmethod
    def is_valid(self) -> bool:
        if not self.npc or not self.sim_context: return False
        return True

    def on_start(self):
        from core import settings
        if settings.DEBUG_MODE: print(f"    [Action START - {self.npc.name}] Inizio azione: {self.action_type_name}")
        self.is_started = True
        self.is_finished = False
        self.is_interrupted = False
        self.elapsed_ticks = 0
        
    def execute_tick(self):
        if not self.is_started or self.is_finished or self.is_interrupted: return
        self.elapsed_ticks += 1
        if self.duration_ticks > 0 and self.elapsed_ticks >= self.duration_ticks:
            self.on_finish()

    @abstractmethod
    def on_finish(self):
        if settings.DEBUG_MODE:
            print(f"    [Action FINISH - {self.npc.name}] Fine azione: {self.action_type_name}")
        # Applica tutti gli effetti sui bisogni definiti nell'azione
        if self.npc and self.effects_on_needs:
            for need_type, change_amount in self.effects_on_needs.items():
                self.npc.change_need_value(need_type, change_amount)

        self.is_finished = True
        self.is_started = False

    def interrupt(self):
        if self.is_started and not self.is_finished and not self.is_interrupted:
            from core import settings
            if settings.DEBUG_MODE: print(f"    [Action INTERRUPT - {self.npc.name}] Azione interrotta: {self.action_type_name}")
            self.is_interrupted = True
            self.is_started = False
            self.on_interrupt_effects()

    def on_interrupt_effects(self):
        pass

    def get_progress_percentage(self) -> float:
        if self.duration_ticks <= 0: return 1.0 if self.is_finished else 0.0
        if not self.is_started: return 0.0
        if self.is_finished or self.is_interrupted: return 1.0
        progress = self.elapsed_ticks / self.duration_ticks
        return min(1.0, max(0.0, progress))

    def __str__(self) -> str:
        status = "Non Iniziata"
        if self.is_finished: status = "Completata"
        elif self.is_interrupted: status = "Interrotta"
        elif self.is_started: status = f"In Corso ({self.get_progress_percentage():.0%})"
        return f"{self.action_type_name} (Stato: {status})"