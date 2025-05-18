# game/src/ai/actions/seeking_bed.py
import logging
from typing import TYPE_CHECKING, Optional

# Importa dal package 'game'
from game import config
from game.src.utils import game as game_utils # Per is_close_to_point, occupy_bed_slot_for_character

if TYPE_CHECKING:
    from game.src.entities.character import Character
    from game.src.modules.game_state_module import GameState

logger = logging.getLogger(__name__)
DEBUG_AI = getattr(config, 'DEBUG_AI_ACTIVE', False)

def handle_arrival_at_bed(npc: 'Character', game_state: 'GameState', pf_grid) -> bool:
    """
    Gestisce l'arrivo dell'NPC al punto di interazione del letto.
    Tenta di occupare lo slot del letto e inizia l'azione "resting_on_bed".
    Restituisce True se l'NPC è entrato con successo nel letto e ha iniziato a riposare,
    False altrimenti (es. slot occupato, l'NPC tornerà idle).
    """
    if DEBUG_AI:
        logger.debug(f"AI ({npc.name}): Arrivato a destinazione per 'seeking_bed'. Target slot: {npc.bed_slot_index}, Posizione letto: {npc.target_destination}")

    # npc.target_destination dovrebbe essere il punto di interazione dello slot del letto targettizzato.
    # npc.bed_slot_index dovrebbe essere stato impostato da handle_idle_decision.

    if npc.bed_slot_index is None or npc.bed_slot_index == -1:
        logger.warning(f"AI WARN ({npc.name}): Arrivato al letto ma npc.bed_slot_index non è valido ({npc.bed_slot_index}). Imposto a idle.")
        npc.current_action = "idle"
        npc.target_destination = None # Resetta la destinazione
        npc.current_path = None       # Resetta il percorso
        return False # Azione fallita

    # Verifica se lo slot target è ancora libero (potrebbe essere stato preso da un altro NPC nel frattempo)
    slot_is_actually_free = False
    if npc.bed_slot_index == 0 and not game_state.bed_slot_1_occupied_by:
        slot_is_actually_free = True
    elif npc.bed_slot_index == 1 and not game_state.bed_slot_2_occupied_by:
        slot_is_actually_free = True
    
    if not slot_is_actually_free:
        if DEBUG_AI:
            logger.info(f"AI ({npc.name}): Arrivato al letto per slot {npc.bed_slot_index}, ma è stato occupato. Ritorno a idle.")
        npc.current_action = "idle"
        npc.target_destination = None
        npc.current_path = None
        npc.bed_slot_index = -1 # Resetta lo slot target
        return False # Non è riuscito ad entrare nel letto

    # Prova ad occupare lo slot (questa funzione aggiorna game_state e gli attributi dell'NPC)
    # game_utils.occupy_bed_slot_for_character ora è più un helper per impostare gli attributi.
    # L'azione principale di occupazione è qui.
    
    slot_occupied_successfully = False
    if npc.bed_slot_index == 0:
        game_state.bed_slot_1_occupied_by = npc.uuid
        slot_occupied_successfully = True
    elif npc.bed_slot_index == 1:
        game_state.bed_slot_2_occupied_by = npc.uuid
        slot_occupied_successfully = True

    if slot_occupied_successfully:
        npc.bed_object_id = "main_bed" # O un ID specifico se hai più letti e lo passi
        # npc.bed_slot_index è già impostato
        npc.is_on_bed = True
        npc.current_action = "resting_on_bed"
        npc.is_interacting = True # Interagisce con il letto
        npc.time_in_current_action = 0.0 # Resetta timer per la nuova azione

        # Posiziona l'NPC sulla "sleeping position" definita per lo slot
        sleep_pos_world = None
        if npc.bed_slot_index == 0 and game_state.bed_slot_1_sleep_pos_world:
            sleep_pos_world = game_state.bed_slot_1_sleep_pos_world
            npc.current_animation_key = "sleep_on_back" # o sleep_side_left, ecc. in base allo slot/preferenza
            npc.current_facing_direction = "left" # Esempio, o basato sull'animazione
        elif npc.bed_slot_index == 1 and game_state.bed_slot_2_sleep_pos_world:
            sleep_pos_world = game_state.bed_slot_2_sleep_pos_world
            npc.current_animation_key = "sleep_on_back" # o sleep_side_right
            npc.current_facing_direction = "right" # Esempio

        if sleep_pos_world:
            npc.x, npc.y = sleep_pos_world
            npc.rect.center = (int(npc.x), int(npc.y))
            npc.target_destination = None # Non ha più una destinazione di movimento
            npc.current_path = None       # Il percorso è stato completato
            if DEBUG_AI:
                logger.debug(f"AI ({npc.name}): Entrato nel letto slot {npc.bed_slot_index} a {sleep_pos_world}. Inizio 'resting_on_bed'.")
        else:
            if DEBUG_AI:
                logger.warning(f"AI WARN ({npc.name}): Posizione di sonno per slot {npc.bed_slot_index} non definita. Rimane al punto di interazione.")
            # L'NPC è comunque a letto e riposerà, ma la posizione potrebbe non essere ideale.
        
        return True # Azione di arrivo completata, iniziata nuova azione "resting_on_bed"
    else:
        # Questo caso non dovrebbe accadere se slot_is_actually_free era True,
        # ma è un fallback.
        if DEBUG_AI:
            logger.error(f"AI ERROR ({npc.name}): Fallito l'occupazione dello slot letto {npc.bed_slot_index} nonostante sembrasse libero.")
        npc.current_action = "idle"
        npc.target_destination = None
        npc.current_path = None
        npc.bed_slot_index = -1
        return False

# Nota: la logica per *decidere* di andare a letto e *trovare* un percorso è
# gestita in idle.py (o nel modulo decisionale principale).
# Questo modulo si concentra sull'azione una volta che la decisione è presa
# e sull'handler di arrivo.