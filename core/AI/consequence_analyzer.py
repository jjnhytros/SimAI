# core/AI/consequence_analyzer.py
from typing import TYPE_CHECKING, Optional, Dict, Any

from core.modules.memory.memory_definitions import Memory
from core.enums import ProblemType, SocialInteractionType, NeedType # Importa NeedType
from core.modules.actions import (
    SocializeAction, EatAction, MoveToAction, HaveFunAction, EngageIntimacyAction
)
from core import settings

if TYPE_CHECKING:
    from core.character import Character
    from core.modules.actions.action_base import BaseAction
    from core.simulation import Simulation # Necessario per il timestamp
    from core.config import npc_config

class ConsequenceAnalyzer:
    def __init__(self):
        if settings.DEBUG_MODE:
            print("  [ConsequenceAnalyzer INIT] ConsequenceAnalyzer creato.")

    def analyze_action_and_create_memory(self, npc: 'Character', finished_action: 'BaseAction'):
        """
        Analizza un'azione completata e, se rilevante, crea e aggiunge un
        oggetto Memory al MemorySystem dell'NPC.
        """
        if not npc.memory_system or finished_action.is_interrupted:
            # Per ora, non creiamo ricordi per azioni interrotte.
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
        trigger_problem = getattr(finished_action, 'triggering_problem', None)

        # --- Logica di analisi basata sul tipo di azione ---
        
        if isinstance(finished_action, SocializeAction):
            target_npc = finished_action.target_npc
            interaction_type = finished_action.interaction_type
            rel_change = finished_action.relationship_score_change
            related_entities.update({
                "interaction_type": interaction_type,
                "target_npc_id": target_npc.npc_id
            })
            emotional_impact = rel_change / 40.0 # Normalizza il cambio di relazione
            salience = abs(emotional_impact) + 0.1 # La salienza è legata all'intensità dell'emozione
            description = f"Ho interagito ({interaction_type.name}) con {target_npc.name}."
            if interaction_type in {SocialInteractionType.DEEP_CONVERSATION, SocialInteractionType.ARGUE, SocialInteractionType.FLIRT, SocialInteractionType.CONFESS_ATTRACTION, SocialInteractionType.PROPOSE_MARRIAGE}:
                salience = min(1.0, salience * 2) # Rende le interazioni forti più salienti

        elif isinstance(finished_action, EngageIntimacyAction):
            salience = 0.9
            emotional_impact = (finished_action.initiator_intimacy_gain / 100.0) + (finished_action.relationship_score_change / 50.0)
            description = f"Ho avuto un momento speciale con {finished_action.target_npc.name}."
            related_entities["target_npc_id"] = finished_action.target_npc.npc_id
        
        elif isinstance(finished_action, HaveFunAction):
            salience = (finished_action.fun_gain / 100.0) * 0.5
            emotional_impact = salience * 0.9 # L'impatto emotivo è quasi uguale alla salienza
            description = f"Mi sono divertito/a: {finished_action.activity_type.display_name_it()}."
            related_entities["activity_type"] = finished_action.activity_type

        elif isinstance(finished_action, (EatAction, DrinkAction)):
            salience = 0.05
            emotional_impact = 0.05
            need_type_to_check = NeedType.HUNGER if isinstance(finished_action, EatAction) else NeedType.THIRST
            description = f"Ho mangiato qualcosa." if isinstance(finished_action, EatAction) else f"Ho bevuto un po' d'acqua."

            if trigger_problem and trigger_problem.details.get('need') == need_type_to_check:
                if trigger_problem.details.get('current_value', 100.0) < npc_config.NEED_CRITICAL_THRESHOLD:
                    salience = 0.5
                    emotional_impact = 0.6
                    description = f"Finalmente ho {'mangiato' if need_type_to_check == NeedType.HUNGER else 'bevuto'}, non ne potevo più!"
        
        elif isinstance(finished_action, UseBathroomAction):
            description = "Ho usato il bagno."
            salience = 0.05
            emotional_impact = 0.1
            if trigger_problem and trigger_problem.details.get('need') == NeedType.BLADDER:
                if trigger_problem.details.get('current_value', 100.0) < npc_config.NEED_CRITICAL_THRESHOLD:
                    salience = 0.6
                    emotional_impact = 0.7
                    description = "Che sollievo! Non ne potevo più!"
            related_entities["for_need_type"] = finished_action.for_need_type

        elif isinstance(finished_action, SleepAction):
            description = "Ho dormito."
            salience = 0.1
            emotional_impact = 0.2 # Svegliarsi riposati è piacevole
            if trigger_problem and trigger_problem.details.get('need') == NeedType.ENERGY:
                if trigger_problem.details.get('current_value', 100.0) < npc_config.NEED_CRITICAL_THRESHOLD:
                    salience = 0.7
                    emotional_impact = 0.8
                    description = "Finalmente ho dormito, non mi reggevo in piedi!"

        # Non creiamo ricordi per azioni di routine come muoversi
        elif isinstance(finished_action, MoveToAction):
            return

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
