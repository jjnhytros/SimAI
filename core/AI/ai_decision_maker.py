# core/AI/ai_decision_maker.py
import random
import importlib
from typing import Optional, TYPE_CHECKING, List, Dict, Any, Tuple, Union

# Import Enum
from core.enums import NeedType, ActionType, ProblemType
# Import Classi Azione, Sistemi IA, Definizioni, Config, etc.
from core.enums.object_types import ObjectType
from core.modules.actions import BaseAction
from .needs_processor import NeedsProcessor
from .thought import Thought, ScoredAction
from core.modules.memory.memory_definitions import Problem 
from core.config import npc_config, time_config, actions_config 
from core import settings

if TYPE_CHECKING:
    from core.character import Character
    from ..simulation import Simulation 
    from ..modules.time_manager import TimeManager

class AIDecisionMaker:
    """
    Orchestra il ciclo cognitivo dell'NPC per scegliere l'azione migliore.
    """
    BASE_ACTION_CHECK_INTERVAL_TICKS: int = 10 
    MAX_CONSECUTIVE_SAME_ACTION: int = 3

    # Mappa un NeedType complesso al percorso del suo discoverer specializzato.
    SOLUTION_DISCOVERER_PATHS: Dict[NeedType, str] = {
        NeedType.FUN: "core.AI.solution_discoverers.fun_discoverer.FunSolutionDiscoverer",
        NeedType.SOCIAL: "core.AI.solution_discoverers.social_discoverer.SocialSolutionDiscoverer",
        NeedType.INTIMACY: "core.AI.solution_discoverers.intimacy_discoverer.IntimacySolutionDiscoverer",
    }

    def __init__(self, npc: 'Character'):
        self.npc: 'Character' = npc
        self.needs_processor = NeedsProcessor()
        self.ticks_since_last_base_action_check: int = 0
        self.last_selected_action_type: Optional[ActionType] = None
        self.consecutive_action_type_count: int = 0

    def _get_required_object_for_action(self, need: NeedType) -> Optional[Union[ObjectType, Tuple[ObjectType, ...]]]:
        """Restituisce il tipo di oggetto primario richiesto da un'azione per un bisogno."""
        if need == NeedType.HUNGER: return ObjectType.REFRIGERATOR
        if need == NeedType.THIRST: return (ObjectType.SINK, ObjectType.WATER_COOLER, ObjectType.REFRIGERATOR)
        if need == NeedType.ENERGY: return ObjectType.BED
        if need == NeedType.BLADDER: return ObjectType.TOILET
        if need == NeedType.HYGIENE: return (ObjectType.SHOWER, ObjectType.BATHTUB)
        return None

    def _discover_and_instantiate_solutions(self, problem: Problem, simulation_context: 'Simulation') -> List['BaseAction']:
        """Usa la configurazione per trovare il discoverer e i parametri corretti."""
        if problem.problem_type != ProblemType.LOW_NEED: return []

        need_to_address = problem.details.get("need")
        if not isinstance(need_to_address, NeedType): return []

        # Cerca prima nella rubrica degli esperti per bisogni complessi
        discoverer_path_str = self.SOLUTION_DISCOVERER_PATHS.get(need_to_address)
        
        # Stampa di debug per vedere quale percorso viene scelto
        if settings.DEBUG_MODE:
            print(f"  [AIDecisionMaker] Bisogno: {need_to_address.name}. Percorso discoverer trovato: {discoverer_path_str}")

        if discoverer_path_str:
            # Se trova un esperto, usa quello e ferma la ricerca.
            try:
                module_path, class_name = discoverer_path_str.rsplit('.', 1)
                module = importlib.import_module(module_path)
                discoverer_class = getattr(module, class_name)
                discoverer_instance = discoverer_class()
                return discoverer_instance.discover(problem, self.npc, simulation_context)
            except (ImportError, AttributeError) as e:
                if settings.DEBUG_MODE:
                    print(f"  [AI Discover] Errore nell'import dinamico del discoverer: {e}")
                return []
        
        else: 
            # Se NON è stato trovato un esperto, allora gestisci come azione semplice.
            action_config = actions_config.SIMPLE_NEED_ACTION_CONFIGS.get(need_to_address)
            if action_config:
                from .solution_discoverers.simple_object_discoverer import SimpleObjectDiscoverer
                discoverer_instance = SimpleObjectDiscoverer(action_config)
                return discoverer_instance.discover(problem, self.npc, simulation_context)

        return []

    def decide_next_action(self, time_manager: 'TimeManager', simulation_context: 'Simulation') -> None:
        """
        Orchestra l'intero ciclo decisionale: identifica il problema, scopre
        le soluzioni, le valuta e sceglie la migliore da mettere in coda.
        """
        # 1. Identifica il problema più urgente
        problem = self.needs_processor.get_most_urgent_problem(self.npc)
        if not problem:
            return

        # 2. Scopri tutte le possibili azioni
        candidate_actions = self._discover_and_instantiate_solutions(problem, simulation_context)
        if not candidate_actions:
            if settings.DEBUG_MODE:
                print(f"    [AI Decision - {self.npc.name}] Nessuna azione valida trovata per il problema: {problem.problem_type.name}")
            return
        
        # 3. Valuta e assegna un punteggio a ogni azione
        scored_actions: List[ScoredAction] = []
        for action in candidate_actions:
            base_score = problem.urgency
            personality_modifier = 1.0
            for trait in self.npc.traits.values():
                personality_modifier *= trait.get_action_choice_priority_modifier(action, simulation_context)

            mood_modifier = 1.0 + (self.npc.overall_mood / 200.0)

            # --- Modificatore Ritmo Circadiano (per il sonno) ---
            time_modifier = 1.0
            if action.action_type_enum == ActionType.ACTION_SLEEP:
                current_hour = time_manager.get_current_hour()
                # ... (logica per is_sleep_time come l'abbiamo definita)
                is_sleep_time = True # Placeholder
                if is_sleep_time:
                    time_modifier = 3.0
                else:
                    energy_val = self.npc.get_need_value(NeedType.ENERGY)
                    if energy_val and energy_val > npc_config.NEED_CRITICAL_THRESHOLD:
                        time_modifier = 0.1

            # --- Modificatore Agenda dei Bisogni (per fame, socialità, ecc.) ---
            schedule_bonus = 0.0
            need_type = problem.details.get("need")
            if need_type and need_type in npc_config.NEED_SCHEDULE_CONFIG:
                schedule = npc_config.NEED_SCHEDULE_CONFIG[need_type]
                current_hour = time_manager.get_current_hour()
                for peak_hour in schedule["peak_times"]:
                    if abs(current_hour - peak_hour) <= 1:
                        schedule_bonus = schedule["peak_influence"]
                        break
            
            # Calcolo dello score finale
            final_score = (base_score) * personality_modifier * mood_modifier
            scored_actions.append(ScoredAction(action, final_score))
            # --- Fine Logica di Punteggio ---

        if not scored_actions:
            return

        # 4. Scegli l'azione migliore e mettila in coda
        scored_actions.sort(key=lambda x: x.score, reverse=True)
        best_scored_action = scored_actions[0]
        
        thought = Thought(
            npc_id=self.npc.npc_id, problem=problem,
            considered_actions=scored_actions, chosen_action=best_scored_action
        )
        if settings.DEBUG_MODE:
            print(thought.get_thought_log())

        self.npc.add_action_to_queue(best_scored_action.action)

    def reset_decision_state(self):
        """
        Resetta lo stato decisionale interno, come il contatore delle azioni
        consecutive, per dare all'IA una "nuova possibilità" di valutazione.
        Viene chiamato, ad esempio, all'inizio di ogni nuova ora.
        """
        self.ticks_since_last_base_action_check = self.BASE_ACTION_CHECK_INTERVAL_TICKS 
        self.last_selected_action_type = None
        self.consecutive_action_type_count = 0

