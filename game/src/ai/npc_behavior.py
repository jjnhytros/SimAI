# game/src/ai/npc_behavior.py
import logging
from typing import TYPE_CHECKING, List, Dict, Any, Optional

from game import config
from game.src.modules.game_state_module import GameState

# Importa i moduli delle azioni
from .actions import idle as idle_action_module
from .actions import resting_on_bed, seeking_bed, phoning, romantic_interaction, \
                     going_to_bed_together, cuddling_in_bed, wandering, using_toilet

if TYPE_CHECKING:
    from game.src.entities.character import Character

logger = logging.getLogger(__name__)
DEBUG_AI = getattr(config, 'DEBUG_AI_ACTIVE', False)

ACTION_UPDATE_HANDLERS: Dict[str, Any] = {
    "resting_on_bed": resting_on_bed.update_resting_on_bed,
    "phoning": phoning.update_phoning,
    "romantic_interaction_action": romantic_interaction.update_romantic_interaction,
    "affectionate_interaction_action": romantic_interaction.update_affectionate_interaction,
    "cuddling_in_bed": cuddling_in_bed.update_cuddling_in_bed,
    "accepting_intimacy_and_waiting": romantic_interaction.update_accepting_intimacy_and_waiting,
    "waiting_in_bed_for_partner": going_to_bed_together.update_waiting_in_bed_for_partner,
    "post_intimacy_idle": idle_action_module.update_post_interaction_idle,
    "using_toilet": using_toilet.update_using_toilet,
}

ACTION_ARRIVAL_HANDLERS: Dict[str, Any] = {
    "seeking_bed": seeking_bed.handle_arrival_at_bed,
    "seeking_partner_for_intimacy": romantic_interaction.handle_arrival_at_partner_for_intimacy,
    "going_to_bed_together_leader": going_to_bed_together.handle_arrival_at_bed_leader,
    "going_to_bed_together_follower": going_to_bed_together.handle_arrival_at_bed_follower,
    "seeking_toilet": using_toilet.handle_arrival_at_toilet,
    "wandering": wandering.handle_arrival_at_wander_destination,
}

def run_npc_ai_logic(
    npc: 'Character',
    all_npcs: List['Character'],
    game_hours_tick: float,
    pf_grid, # Pathfinding grid
    game_state: GameState
):
    if DEBUG_AI and npc.current_action not in ["moving_to_target", "idle"]:
        logger.debug(f"AI LOGIC START ({npc.name}): Azione: '{npc.current_action}', TargetDest: {npc.target_destination}, PathLen: {len(npc.current_path) if npc.current_path else 0}")

    # 1. Gestione Azioni Continue / Basate sul Tempo
    if npc.current_action in ACTION_UPDATE_HANDLERS:
        action_is_still_ongoing = ACTION_UPDATE_HANDLERS[npc.current_action](npc, game_state, game_hours_tick)
        if action_is_still_ongoing:
            return 
        if DEBUG_AI and npc.current_action != "idle":
             logger.debug(f"AI LOGIC ({npc.name}): Azione continua '{npc.current_action}' (prima) terminata. Nuova azione: '{npc.current_action}' (impostata dall'handler)")

    # 2. Gestione Arrivo a Destinazione
    if npc.current_action == "moving_to_target" and \
       not npc.current_path and \
       not npc.target_destination and \
       npc.previous_action_was_movement_to_target:

        action_that_triggered_movement = npc.current_action_before_movement
        if DEBUG_AI:
            logger.debug(f"AI LOGIC ({npc.name}): Arrivato per l'azione originale: '{action_that_triggered_movement}'")

        original_action_for_arrival = npc.current_action # Salva l'azione corrente nel caso l'handler di arrivo la cambi
        
        if action_that_triggered_movement in ACTION_ARRIVAL_HANDLERS:
            arrival_action_successful = ACTION_ARRIVAL_HANDLERS[action_that_triggered_movement](npc, game_state, pf_grid)
            
            if not arrival_action_successful and npc.current_action == original_action_for_arrival: # Controlla se l'handler non ha cambiato azione e ha fallito
                logger.warning(f"AI LOGIC ({npc.name}): Handler di arrivo per '{action_that_triggered_movement}' non completato con successo. Forzo idle.")
                npc.current_action = "idle"
        else:
            logger.warning(f"AI LOGIC ({npc.name}): Nessun handler di arrivo definito per '{action_that_triggered_movement}'. Imposto a idle.")
            npc.current_action = "idle"
        
        npc.previous_action_was_movement_to_target = False
        npc.current_action_before_movement = None # Resetta dopo aver gestito l'arrivo
        # Non fare return qui, se l'NPC è ora idle, deve prendere una nuova decisione

    # 3. Logica Decisionale (se l'NPC è ora "idle")
    if npc.current_action == "idle":
        if DEBUG_AI:
            logger.debug(f"AI LOGIC ({npc.name}): In stato idle. Chiamo handle_idle_decision.")
        idle_action_module.handle_idle_decision(npc, all_npcs, pf_grid, game_state)
        
        if DEBUG_AI and npc.current_action != "idle":
            logger.debug(f"AI LOGIC ({npc.name}): Decisione presa in idle. Nuova azione pre-movimento: '{npc.current_action_before_movement}', Stato attuale: '{npc.current_action}'")