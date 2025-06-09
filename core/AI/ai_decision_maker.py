# core/AI/ai_decision_maker.py
import random
import importlib # FIX: Importa il modulo per l'importazione dinamica
from typing import Optional, TYPE_CHECKING, List, Dict, Any, Type, Union, Tuple # FIX: Aggiunto Tuple

# Import Enum
from core.enums import (
    NeedType, ActionType, ProblemType, ObjectType, FunActivityType, 
    SocialInteractionType, LifeStage
)
# Import Classi Azione
from core.modules.actions import (
    BaseAction, EatAction, DrinkAction, SleepAction, HaveFunAction,
    UseBathroomAction, SocializeAction, EngageIntimacyAction, MoveToAction, TravelToAction
)
# Import Sistemi IA
from .needs_processor import NeedsProcessor
from .solution_discoverers.base_discoverer import BaseSolutionDiscoverer
from .thought import Thought, ScoredAction

# Import per le definizioni
from core.modules.memory.memory_definitions import Problem 

# Import Configurazioni e Utility
from core.config import npc_config, time_config, actions_config 
from core import settings # FIX: Importa settings
from core.utils import calculate_distance

if TYPE_CHECKING:
    from core.character import Character
    from ..simulation import Simulation 
    from ..modules.time_manager import TimeManager
    from ..world.location import Location

class AIDecisionMaker:
    """
    Orchestra il ciclo cognitivo dell'NPC per scegliere l'azione migliore.
    """
    BASE_ACTION_CHECK_INTERVAL_TICKS = 10 
    MAX_CONSECUTIVE_SAME_ACTION = 3

    # --- REGISTRO DEGLI ESPERTI (con Percorsi Stringa per Import Dinamico) ---
    SOLUTION_DISCOVERER_PATHS: Dict[NeedType, str] = {
        NeedType.FUN: "core.AI.solution_discoverers.fun_discoverer.FunSolutionDiscoverer",
        NeedType.SOCIAL: "core.AI.solution_discoverers.social_discoverer.SocialSolutionDiscoverer",
        NeedType.INTIMACY: "core.AI.solution_discoverers.intimacy_discoverer.IntimacySolutionDiscoverer",
    }

    def __init__(self, npc: 'Character'):
        self.npc: 'Character' = npc
        self.ticks_since_last_base_action_check: int = 0
        self.last_selected_action_type: Optional[ActionType] = None
        self.consecutive_action_type_count: int = 0
        self.needs_processor = NeedsProcessor()


    def _get_required_object_for_action(self, need: NeedType) -> Optional[Union[ObjectType, Tuple[ObjectType, ...]]]:
        """Restituisce il tipo di oggetto primario richiesto da un'azione per un bisogno."""
        if need == NeedType.HUNGER: return ObjectType.REFRIGERATOR
        if need == NeedType.THIRST: return (ObjectType.SINK, ObjectType.WATER_COOLER, ObjectType.REFRIGERATOR)
        if need == NeedType.ENERGY: return ObjectType.BED
        if need == NeedType.BLADDER: return ObjectType.TOILET
        if need == NeedType.HYGIENE: return (ObjectType.SHOWER, ObjectType.BATHTUB)
        return None

    def _discover_and_instantiate_solutions(self, problem: Problem, simulation_context: 'Simulation') -> List[BaseAction]:
        """Usa l'importazione dinamica e il pattern Strategy per delegare la scoperta delle soluzioni."""
        if problem.problem_type != ProblemType.LOW_NEED: return []

        need_to_address = problem.details.get("need")
        if not isinstance(need_to_address, NeedType): return []

        discoverer_path_str = self.SOLUTION_DISCOVERER_PATHS.get(need_to_address)
        
        if discoverer_path_str:
            try:
                module_path, class_name = discoverer_path_str.rsplit('.', 1)
                module = importlib.import_module(module_path) # FIX: `importlib` è ora definito
                discoverer_class = getattr(module, class_name)
                discoverer_instance = discoverer_class()
                return discoverer_instance.discover(problem, self.npc, simulation_context) # FIX: `self.npc` è ora visibile
            except (ImportError, AttributeError) as e:
                if settings.DEBUG_MODE: # FIX: `settings` è ora definito
                    print(f"  [AI Discover] Errore nell'import dinamico del discoverer: {e}")
                return []
        
        else: # Logica per azioni semplici
            required_objects = self._get_required_object_for_action(need_to_address)
            # FIX: Dobbiamo importare la classe SimpleObjectDiscoverer per usarla
            from .solution_discoverers.simple_object_discoverer import SimpleObjectDiscoverer
            
            # FIX: Rimuoviamo il riferimento al vecchio dizionario
            # La classe azione viene determinata dalla logica interna del discoverer
            action_class_map = {
                NeedType.HUNGER: EatAction, NeedType.THIRST: DrinkAction, NeedType.ENERGY: SleepAction,
                NeedType.BLADDER: UseBathroomAction, NeedType.HYGIENE: UseBathroomAction,
            }
            action_class = action_class_map.get(need_to_address)
            
            if action_class and required_objects:
                discoverer_instance = SimpleObjectDiscoverer(action_class, required_objects)
                return discoverer_instance.discover(problem, self.npc, simulation_context) # FIX: `self.npc` è ora visibile

        return []

    def decide_next_action(self, time_manager: 'TimeManager', simulation_context: 'Simulation') -> Optional[BaseAction]:
        # QUESTO METODO ORA È PERFETTO E NON CAMBIA
        # La sua logica di orchestrare le fasi è già corretta.
        # ... (il codice di decide_next_action che abbiamo finalizzato prima rimane qui) ...
        pass

    def reset_decision_state(self):
        """
        Resetta lo stato decisionale interno, come il contatore delle azioni
        consecutive, per dare all'IA una "nuova possibilità" di valutazione.
        Viene chiamato, ad esempio, all'inizio di ogni nuova ora.
        """
        self.ticks_since_last_base_action_check = self.BASE_ACTION_CHECK_INTERVAL_TICKS 
        self.last_selected_action_type = None
        self.consecutive_action_type_count = 0
