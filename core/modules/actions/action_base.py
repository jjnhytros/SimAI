# core/modules/actions/action_base.py
"""
Definizione della classe base astratta per tutte le Azioni.
"""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional, Dict

from core.enums import NeedType, ActionType # ActionType è usato qui
from core.world.game_object import GameObject
from core.AI.problem_definitions import Problem

if TYPE_CHECKING:
    from core.character import Character
    from core.simulation import Simulation

class BaseAction(ABC):
    """Classe base astratta per tutte le azioni che un NPC può compiere."""

    def __init__(self,
                npc: 'Character',
                action_type_name: str,
                duration_ticks: int,
                p_simulation_context: 'Simulation',
                is_outdoors: bool = False, # L'azione si svolge all'aperto?
                is_noisy: bool = False,    # L'azione è rumorosa?
                is_interruptible: bool = True,
                action_type_enum: Optional[ActionType] = None,
                triggering_problem: Optional['Problem'] = None,
                ):
        self.npc: 'Character' = npc
        self.action_type_name: str = action_type_name
        self.duration_ticks: int = duration_ticks
        self.sim_context: 'Simulation' = p_simulation_context
        self.is_outdoors: bool = is_outdoors
        self.is_noisy: bool = is_noisy
        self.is_interruptible: bool = is_interruptible
        
        self.action_type_enum: Optional[ActionType] = action_type_enum # Memorizza l'enum se fornito

        self.elapsed_ticks: int = 0
        self.is_started: bool = False
        self.is_finished: bool = False
        self.is_interrupted: bool = False

        # Effetti sui bisogni (possono essere definiti dalle sottoclassi)
        # Esempio: {NeedType.HUNGER: 50.0, NeedType.ENERGY: -5.0}
        self.effects_on_needs: Dict[NeedType, float] = {}
        self.target_object: Optional['GameObject'] = None
        self.triggering_problem: Optional['Problem'] = triggering_problem # <-- MEMORIZZA IL PROBLEMA

        # TODO VI.1.b: Aggiungere altri attributi previsti come:
        # self.required_objects: List[str] = []
        # self.required_location_type: Optional[LocationType] = None
        # self.required_skills: Dict[SkillName, int] = {}
        # self.generates_event_on_finish: Optional[str] = None # ID evento
        # self.npc_display_status: str = f"Sta compiendo: {self.description}" # Per TUI

    @abstractmethod
    def is_valid(self) -> bool:
        """
        Controlla se l'NPC può attualmente eseguire questa azione.
        (Es. ha gli oggetti necessari? È nel luogo giusto? I suoi bisogni lo permettono?)
        Deve essere implementato dalle sottoclassi.
        Restituisce True se l'azione è valida, False altrimenti.
        """
        pass

    def on_start(self):
        # Accedi a settings tramite self.npc se Character ha un riferimento a settings
        # o se settings è un modulo globale importato (ma attenzione a import circolari anche lì)
        # Per ora, assumiamo che settings.DEBUG_MODE sia accessibile globalmente se importato
        # In alternativa, passa settings o DEBUG_MODE a BaseAction se necessario
        from core import settings # Import locale se strettamente necessario e sicuro
        if settings.DEBUG_MODE:
            print(f"    [Action START - {self.npc.name}] Inizio azione: {self.action_type_name}")
        self.is_started = True
        self.is_finished = False
        self.is_interrupted = False
        self.ticks_elapsed = 0
        # TODO: Modificare lo stato dell'NPC, es. self.npc.is_busy = True
        # TODO: Potrebbe bloccare la coda delle decisioni dell'IA dell'NPC

    def execute_tick(self):
        if not self.is_started or self.is_finished or self.is_interrupted:
            return
        self.ticks_elapsed += 1
        if self.duration_ticks > 0 and self.ticks_elapsed >= self.duration_ticks:
            self.on_finish()

    @abstractmethod
    def on_finish(self):
        from core import settings # Import locale se strettamente necessario e sicuro
        if settings.DEBUG_MODE:
            print(f"    [Action FINISH - {self.npc.name}] Fine azione: {self.action_type_name}")
        self.is_finished = True
        self.is_started = False 
        # TODO: Modificare lo stato dell'NPC, es. self.npc.is_busy = False
        # TODO: Rimuovere questa azione dalla coda dell'NPC
        # TODO: Applicare self.effects_on_needs
        # for need_type, change_amount in self.effects_on_needs.items():
        #     self.npc.change_need_value(need_type, change_amount)

    def interrupt(self):
        if self.is_started and not self.is_finished and not self.is_interrupted:
            from core import settings # Import locale
            if settings.DEBUG_MODE:
                print(f"    [Action INTERRUPT - {self.npc.name}] Azione interrotta: {self.action_type_name}")
            self.is_interrupted = True
            self.is_started = False 
            self.on_interrupt_effects()
            # TODO: Modificare stato NPC, pulire coda azioni

    def on_interrupt_effects(self):
        """
        Logica specifica da eseguire quando un'azione viene interrotta.
        Le sottoclassi possono sovrascrivere questo per effetti specifici.
        """
        # Esempio: potrebbe esserci una piccola penalità all'umore o a un bisogno.
        pass

    def get_progress_percentage(self) -> float:
        if self.duration_ticks == 0: 
            return 1.0 if self.is_finished else 0.0
        if not self.is_started or self.is_finished or self.is_interrupted:
            return 1.0 if self.is_finished else 0.0
        progress = self.ticks_elapsed / self.duration_ticks
        return min(1.0, max(0.0, progress))

    def __str__(self) -> str:
        status = "Non Iniziata"
        if self.is_finished: status = "Completata"
        elif self.is_interrupted: status = "Interrotta"
        elif self.is_started: status = f"In Corso ({self.ticks_elapsed}/{self.duration_ticks} ticks, {self.get_progress_percentage():.0%})"
        return f"Azione(Tipo: {self.action_type_name}, NPC: {self.npc.name if self.npc else 'N/A'}, Stato: {status})"
