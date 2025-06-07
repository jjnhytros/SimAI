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
            # Per ora, non creiamo ricordi per azioni interrotte,
            # ma potremmo aggiungere una logica per ricordi negativi di interruzione.
            return

        # Valori di default per il nuovo ricordo
        description: str = ""
        emotional_impact: float = 0.0
        salience: float = 0.0 # L'importanza del ricordo (0.0 a 1.0)
        
        # FIX 1: Inizializza un dizionario vuoto con il tipo corretto
        related_entities: Dict[str, Any] = {}
        
        # Popola subito le entità comuni
        if finished_action.action_type_enum:
            related_entities["action_type"] = finished_action.action_type_enum

        # Ottieni il timestamp dall'azione finita
        sim_context: 'Simulation' = finished_action.sim_context
        current_ticks = float(sim_context.time_manager.total_ticks)

        # --- Logica di analisi basata sul tipo di azione ---
        
        if isinstance(finished_action, SocializeAction):
            # Le interazioni sociali sono molto importanti per i ricordi
            target_npc = finished_action.target_npc
            interaction_type = finished_action.interaction_type
            rel_change = finished_action.relationship_score_change
            
            related_entities["interaction_type"] = interaction_type
            related_entities["target_npc_id"] = target_npc.npc_id

            # L'impatto emotivo è proporzionale al cambiamento della relazione
            # (es. +10 rel -> +0.2 impatto; -20 rel -> -0.4 impatto)
            emotional_impact = rel_change / 50.0 
            
            # La salienza (importanza) dipende dal tipo di interazione
            if interaction_type in {SocialInteractionType.DEEP_CONVERSATION, SocialInteractionType.ARGUE, SocialInteractionType.CONFESS_ATTRACTION}:
                salience = 0.6
            elif interaction_type == SocialInteractionType.FLIRT and rel_change > 0:
                salience = 0.7 # Un flirt andato bene è molto memorabile
            elif interaction_type == SocialInteractionType.PROPOSE_MARRIAGE and rel_change > 0:
                salience = 1.0 # Evento che cambia la vita
            else:
                salience = 0.2 # Una chiacchierata normale è meno importante
            
            description = f"Ho avuto una conversazione ({interaction_type.name}) con {target_npc.name}."

        elif isinstance(finished_action, EngageIntimacyAction):
            salience = 0.9 # Un momento molto importante
            emotional_impact = finished_action.initiator_intimacy_gain / 100.0 # Es: +60 gain -> +0.6 impatto
            description = f"Ho avuto un momento speciale con {finished_action.target_npc.name}."
            related_entities["target_npc_id"] = finished_action.target_npc.npc_id
        
        elif isinstance(finished_action, HaveFunAction):
            salience = (finished_action.fun_gain / 100.0) * 0.6 # Es: +50 fun -> salienza 0.3
            emotional_impact = salience * 0.8 # L'impatto emotivo è correlato
            description = f"Mi sono divertito/a: {finished_action.activity_type.display_name_it()}."
            related_entities["activity_type"] = finished_action.activity_type

        elif isinstance(finished_action, EatAction):
            description = "Ho mangiato qualcosa."
            salience = 0.05      # Di base è un ricordo banale
            emotional_impact = 0.05
            
            # FIX 2: Usa il problema che ha scatenato l'azione per capire il contesto
            trigger_problem = getattr(finished_action, 'triggering_problem', None)
            if trigger_problem and trigger_problem.problem_type == ProblemType.LOW_NEED:
                if trigger_problem.details.get('need') == NeedType.HUNGER and \
                   trigger_problem.details.get('current_value', 100.0) < npc_config.NEED_CRITICAL_THRESHOLD:
                    # Se si mangia in condizioni di fame critica, il ricordo è molto più importante e positivo
                    salience = 0.5
                    emotional_impact = 0.6
                    description = "Finalmente ho mangiato, stavo morendo di fame!"
            
        # Potremmo decidere di non creare ricordi per azioni di routine come muoversi,
        # a meno che non accada qualcosa di speciale durante il movimento.
        elif isinstance(finished_action, MoveToAction):
            return

        # Se abbiamo effettivamente deciso di creare un ricordo...
        if description and salience > 0.01: # Ignora ricordi troppo banali
            
            # FIX 3: Passa npc_id direttamente al costruttore di Memory
            new_memory = Memory(
                npc_id=npc.npc_id,
                event_description=description,
                emotional_impact=emotional_impact,
                salience=salience,
                timestamp=current_ticks,
                related_entities=related_entities
            )
            npc.memory_system.add_memory(new_memory)
