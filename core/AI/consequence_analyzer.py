# core/AI/consequence_analyzer.py
"""
Definisce la classe ConsequenceAnalyzer, responsabile di analizzare le azioni
compiute e di generare ricordi significativi per gli NPC.
"""
from typing import TYPE_CHECKING, Optional, Dict, Any, cast

from core.enums.fun_activity_types import FunActivityType
from core.modules.memory.memory_definitions import Memory
from core.enums import ActionType, SocialInteractionType, NeedType, ProblemType
from core.modules.actions import (
    BaseAction, SocializeAction, EatAction, DrinkAction, MoveToAction, 
    HaveFunAction, UseBathroomAction, SleepAction, EngageIntimacyAction
)
from core.config import actions_config, npc_config
from core import settings

if TYPE_CHECKING:
    from core.character import Character
    from core.simulation import Simulation

class ConsequenceAnalyzer:
    """
    Analizza le azioni completate e crea ricordi con un impatto emotivo
    e una salienza appropriati, che vengono poi aggiunti al MemorySystem dell'NPC.
    """
    def __init__(self):
        if settings.DEBUG_MODE:
            print("  [ConsequenceAnalyzer INIT] ConsequenceAnalyzer creato.")

    def analyze_action_and_create_memory(self, npc: 'Character', finished_action: 'BaseAction'):
        if not npc.memory_system or finished_action.is_interrupted:
            return

        # Valori di default per il nuovo ricordo
        description: str = ""
        emotional_impact: float = 0.0
        salience: float = 0.0 # L'importanza del ricordo (0.0 a 1.0)
        related_entities: Dict[str, Any] = {}
        if finished_action.action_type_enum:
            related_entities["action_type"] = finished_action.action_type_enum

        sim_context: 'Simulation' = finished_action.sim_context
        current_ticks = float(sim_context.time_manager.total_ticks_sim_run)
        
        # ORA IL PROBLEMA VIENE LETTO DAL CHARACTER, NON DALL'AZIONE
        trigger_problem = npc.current_problem

        # --- Logica di analisi basata sul tipo di azione ---
        
        if isinstance(finished_action, SocializeAction):
            target_npc = finished_action.target_npc
            if not target_npc: return

            interaction_type = finished_action.interaction_type
            config = actions_config.SOCIALIZE_INTERACTION_CONFIGS.get(interaction_type, {})
            rel_change = config.get("rel_change_success", 0) # Usiamo il guadagno potenziale come base
            
            emotional_impact = rel_change / 40.0
            related_entities.update({"interaction_type": interaction_type, "target_npc_id": target_npc.npc_id})
            
            emotional_impact = rel_change / 40.0
            salience = abs(emotional_impact) + 0.1
            description = f"Ho interagito con {target_npc.name}."
            if interaction_type in {SocialInteractionType.DEEP_CONVERSATION, SocialInteractionType.ARGUE, SocialInteractionType.FLIRT, SocialInteractionType.CONFESS_ATTRACTION, SocialInteractionType.PROPOSE_MARRIAGE}:
                salience = min(1.0, salience * 2)

        elif isinstance(finished_action, EngageIntimacyAction):
            target_npc = finished_action.target_npc
            if not target_npc: return
            # Leggiamo i valori dalla configurazione, non dall'oggetto azione
            config = actions_config.INTIMACY_ACTION_CONFIG.get(NeedType.INTIMACY, {})
            initiator_gain = config.get("initiator_intimacy_gain", 0)
            rel_gain = config.get("relationship_score_gain", 0)
            
            salience = 0.9
            emotional_impact = (initiator_gain / 100.0) + (rel_gain / 50.0)
            description = f"Ho avuto un momento speciale con {target_npc.name}."
            related_entities["target_npc_id"] = target_npc.npc_id
        
        elif isinstance(finished_action, HaveFunAction):
            activity = finished_action.activity_type
            if not activity: return # Sicurezza

            # 1. Leggi la configurazione per questa specifica attività
            activity_safe = cast(FunActivityType, activity)
            config = actions_config.HAVEFUN_ACTIVITY_CONFIGS.get(activity_safe, {})
            
            # 2. Ottieni il guadagno totale di FUN dalla configurazione
            total_potential_fun_gain = config.get("fun_gain", 0.0)
            
            # 3. Calcola la salienza basandoti su questo valore
            salience = (total_potential_fun_gain / 100.0) * 0.6
            emotional_impact = salience * 0.9
            
            description = f"Mi sono divertito/a facendo: {activity.name}"
            related_entities["activity_type"] = finished_action.activity_type

        elif isinstance(finished_action, (EatAction, DrinkAction, UseBathroomAction, SleepAction)):
            salience = 0.05
            emotional_impact = 0.05
            
            if trigger_problem and trigger_problem.problem_type == ProblemType.LOW_NEED:
                need_type = trigger_problem.details.get('need')
                need_value = trigger_problem.details.get('current_value', 100.0)

                if need_value < npc_config.NEED_CRITICAL_THRESHOLD:
                    salience = 0.6
                    emotional_impact = 0.7
                    
                    if need_type == NeedType.HUNGER: description = "Finalmente ho mangiato, stavo morendo di fame!"
                    elif need_type == NeedType.THIRST: description = "Finalmente ho bevuto, non ne potevo più!"
                    elif need_type == NeedType.BLADDER: description = "Che sollievo! Non ne potevo più!"
                    elif need_type == NeedType.ENERGY: description = "Finalmente ho dormito, non mi reggevo in piedi!"
            
            if not description: # Se il bisogno non era critico, usa una descrizione generica
                if isinstance(finished_action, EatAction): description = "Ho mangiato qualcosa."
                elif isinstance(finished_action, DrinkAction): description = "Ho bevuto un po' d'acqua."
                elif isinstance(finished_action, UseBathroomAction): description = "Ho usato il bagno."
                elif isinstance(finished_action, SleepAction): description = "Ho dormito."

        elif isinstance(finished_action, MoveToAction):
            return # Nessun ricordo per un semplice movimento

        # Se abbiamo effettivamente deciso di creare un ricordo...
        if description and salience > 0.01:
            new_memory = Memory(
                npc_id=npc.npc_id,
                event_description=description,
                emotional_impact=max(-1.0, min(1.0, emotional_impact)),
                salience=max(0.0, min(1.0, salience)),
                timestamp=current_ticks,
                related_entities=related_entities
            )
            npc.memory_system.add_memory(new_memory)
            
            # Una volta che l'azione è finita e il ricordo è stato creato,
            # l'NPC non è più attivamente concentrato su quel problema.
            npc.current_problem = None