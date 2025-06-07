# core/modules/actions/action_base.py
"""
Definizione della classe base astratta per tutte le Azioni.
"""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional, Dict, Any, Union

# Import degli Enum necessari per i type hint
from core.enums import NeedType, ActionType, FunActivityType, SocialInteractionType

if TYPE_CHECKING:
    from core.character import Character
    from core.simulation import Simulation
    from core.world.game_object import GameObject
    from core.AI.problem_definitions import Problem


class BaseAction(ABC):
    """Classe base astratta per tutte le azioni che un NPC può compiere."""

    def __init__(self,
                npc: 'Character',
                p_simulation_context: 'Simulation',
                duration_ticks: int,
                action_type_enum: Optional[ActionType] = None,
                action_type_name: Optional[str] = None, # Opzionale, può essere derivato dall'enum
                triggering_problem: Optional['Problem'] = None,
                is_outdoors: bool = False,
                is_noisy: bool = False,
                cognitive_effort: float = 0.1,
                is_interruptible: bool = True,
                ):
        
        self.npc: 'Character' = npc
        self.sim_context: 'Simulation' = p_simulation_context
        self.duration_ticks: int = duration_ticks
        self.triggering_problem: Optional['Problem'] = triggering_problem
        self.is_outdoors: bool = is_outdoors
        self.is_noisy: bool = is_noisy
        self.is_interruptible: bool = is_interruptible
        
        self.action_type_enum: Optional[ActionType] = action_type_enum
        self.action_type_name: str = action_type_name or (action_type_enum.name if action_type_enum else "UNKNOWN_ACTION")

        # Attributi di stato
        self.elapsed_ticks: int = 0
        self.is_started: bool = False
        self.is_finished: bool = False
        self.is_interrupted: bool = False

        # Effetti e target (popolati dalle sottoclassi)
        self.effects_on_needs: Dict[NeedType, float] = {}
        self.target_object: Optional['GameObject'] = None
        self.target_npc: Optional['Character'] = None
        self.activity_type: Optional[Union[FunActivityType, SocialInteractionType]] = None
        self.cognitive_effort: float = cognitive_effort

    @abstractmethod
    def is_valid(self) -> bool:
        """Controlla se l'NPC può attualmente eseguire questa azione."""
        # Un controllo base che le sottoclassi possono chiamare
        if not self.npc or not self.sim_context:
            return False
        return True

    def on_start(self):
        """Logica da eseguire una sola volta all'inizio dell'azione."""
        from core import settings # Import locale per il debug
        if settings.DEBUG_MODE:
            print(f"    [Action START - {self.npc.name}] Inizio azione: {self.action_type_name}")
        self.is_started = True
        self.is_finished = False
        self.is_interrupted = False
        self.elapsed_ticks = 0
        
    def execute_tick(self):
        """Logica eseguita ad ogni tick della simulazione mentre l'azione è attiva."""
        if not self.is_started or self.is_finished or self.is_interrupted:
            return
        self.elapsed_ticks += 1
        if self.duration_ticks > 0 and self.elapsed_ticks >= self.duration_ticks:
            self.on_finish()

    @abstractmethod
    def on_finish(self):
        """Logica da eseguire al completamento con successo dell'azione."""
        from core import settings
        if settings.DEBUG_MODE:
            print(f"    [Action FINISH - {self.npc.name}] Fine azione: {self.action_type_name}")
        self.is_finished = True
        self.is_started = False

    def interrupt(self):
        """Interrompe l'azione prima del suo completamento."""
        if self.is_started and not self.is_finished and not self.is_interrupted:
            from core import settings
            if settings.DEBUG_MODE:
                print(f"    [Action INTERRUPT - {self.npc.name}] Azione interrotta: {self.action_type_name}")
            self.is_interrupted = True
            self.is_started = False
            self.on_interrupt_effects()

    def on_interrupt_effects(self):
        """Logica specifica da eseguire quando un'azione viene interrotta."""
        pass # Le sottoclassi possono sovrascrivere questo per effetti parziali.

    def get_progress_percentage(self) -> float:
        """Restituisce il progresso dell'azione come percentuale (0.0 a 1.0)."""
        if self.duration_ticks == 0:
            return 1.0 if self.is_finished else 0.0
        if not self.is_started or self.is_finished or self.is_interrupted:
            return 1.0 if self.is_finished else 0.0
        progress = self.elapsed_ticks / self.duration_ticks
        return min(1.0, max(0.0, progress))

    def __str__(self) -> str:
        status = "Non Iniziata"
        if self.is_finished: status = "Completata"
        elif self.is_interrupted: status = "Interrotta"
        elif self.is_started: status = f"In Corso ({self.get_progress_percentage():.0%})"
        return f"{self.action_type_name} (Stato: {status})"