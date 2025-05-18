# game/src/ai/actions/wandering.py
import logging
from typing import TYPE_CHECKING, Optional

# Importa dal package 'game'
from game import config
# game_utils potrebbe non essere strettamente necessario qui se la decisione e il pathfinding
# sono gestiti altrove (es. in idle.py)
# from game.src.utils import game as game_utils 

if TYPE_CHECKING:
    from game.src.entities.character import Character
    from game.src.modules.game_state_module import GameState

logger = logging.getLogger(__name__)
DEBUG_AI = getattr(config, 'DEBUG_AI_ACTIVE', False)

# L'azione "wandering" è principalmente uno stato di movimento verso una destinazione casuale.
# Non c'è una logica di "update" continuo specifica per il wandering stesso,
# oltre al movimento gestito da Character.update().
# Quindi, non abbiamo una funzione update_wandering() qui.
# La parte importante è handle_arrival_at_wander_destination.

def handle_arrival_at_wander_destination(npc: 'Character', game_state: 'GameState', pf_grid) -> bool:
    """
    Gestisce l'arrivo dell'NPC alla destinazione casuale del wandering.
    L'NPC tornerà semplicemente allo stato "idle".
    Restituisce True (per indicare che l'azione di "seeking" specifica è completata).
    """
    if DEBUG_AI:
        target_dest_log = npc.target_destination if hasattr(npc, 'target_destination') else "N/A" # Vecchia destinazione
        logger.debug(f"AI ({npc.name}): Arrivato alla destinazione di wandering {target_dest_log}. Ritorno a idle.")

    npc.current_action = "idle"
    npc.target_destination = None # Resetta la destinazione
    npc.current_path = None       # Resetta il percorso
    # npc.previous_action_was_movement_to_target dovrebbe essere resettato da npc_behavior.py
    # npc.current_action_before_movement dovrebbe essere resettato o gestito da npc_behavior.py

    # Il wandering di solito dà un piccolo, quasi trascurabile, aumento al Divertimento (Fun)
    # o semplicemente previene che scenda troppo rapidamente se l'NPC non ha nulla da fare.
    fun_gain_from_wander = getattr(config, 'FUN_GAIN_FROM_WANDERING', 0.5) # Molto piccolo
    if fun_gain_from_wander > 0:
        npc.fun.satisfy(fun_gain_from_wander)
        if DEBUG_AI:
            logger.debug(f"AI ({npc.name}): Leggero aumento Divertimento da wandering (+{fun_gain_from_wander:.2f}). Valore Fun: {npc.fun.get_value():.1f}")
            
    return True # L'azione di "seeking" per il wandering è considerata completata.
                # L'NPC è ora idle e prenderà una nuova decisione al prossimo tick AI.

# La logica per *decidere* di iniziare il wandering e *calcolare* la destinazione
# e il percorso si trova in `idle.py` (nella funzione `handle_idle_decision`).
# Quella funzione imposterà:
# npc.current_action_before_movement = "wandering"
# npc.current_action = "moving_to_target"
# npc.target_destination = target_wander_pos
# npc.current_path = path_to_wander
# npc.previous_action_was_movement_to_target = True