# game/src/ai/actions/resting_on_bed.py
import logging
from typing import TYPE_CHECKING

# Importa dal package 'game'
from game import config
# game_utils potrebbe non essere necessario qui se l'occupazione/liberazione slot
# è gestita altrove (es. in seeking_bed.handle_arrival_at_bed o in npc_behavior)
from game.src.utils import game as game_utils


if TYPE_CHECKING:
    from game.src.entities.character import Character
    from game.src.modules.game_state_module import GameState

logger = logging.getLogger(__name__)
DEBUG_AI = getattr(config, 'DEBUG_AI_ACTIVE', False)

def update_resting_on_bed(npc: 'Character', game_state: 'GameState', hours_passed_this_tick: float) -> bool:
    """
    Aggiorna la logica per l'azione 'resting_on_bed'.
    L'NPC recupera energia. L'azione termina quando l'energia è piena.
    Restituisce True se l'azione è ancora in corso, False se è terminata.
    """
    if not npc.is_on_bed: # Controllo di sicurezza
        logger.warning(f"AI WARN ({npc.name}): update_resting_on_bed chiamato ma is_on_bed è False. Imposto azione a idle.")
        npc.current_action = "idle"
        # Assicurati che lo slot del letto sia liberato se c'è un'incongruenza
        if npc.bed_object_id and npc.bed_slot_index != -1:
             game_utils.free_bed_slot_for_character(game_state, npc)
        return False

    # La logica di recupero dell'energia è già gestita da npc.energy.recover()
    # chiamata da Character.rest(), che a sua volta è chiamata da Character.update()
    # quando current_action è "resting_on_bed".
    # Qui dobbiamo solo controllare se l'energia è piena per terminare l'azione.

    if npc.energy.get_value() >= npc.energy.max_value:
        if DEBUG_AI:
            logger.debug(f"AI ({npc.name}): Energia piena ({npc.energy.get_value():.1f}). Fine riposo.")
        
        # Libera lo slot del letto
        game_utils.free_bed_slot_for_character(game_state, npc)
        # npc.is_on_bed è già impostato a False da free_bed_slot_for_character

        npc.current_action = "idle" # Torna idle dopo essersi svegliato
        npc.is_interacting = False # Non sta più interagendo con il letto
        # npc.bed_object_id = None (gestito da free_bed_slot_for_character)
        # npc.bed_slot_index = -1 (gestito da free_bed_slot_for_character)
        
        return False # Azione terminata
    else:
        if DEBUG_AI:
            # Questo log potrebbe essere molto frequente, valuta se tenerlo
            logger.debug(f"AI ({npc.name}): Sta ancora riposando. Energia: {npc.energy.get_value():.1f}/{npc.energy.max_value:.0f}")
        return True # Azione ancora in corso

# La logica per "iniziare" l'azione "resting_on_bed" (cioè, entrare fisicamente nel letto
# e cambiare lo stato) è meglio gestirla in `seeking_bed.handle_arrival_at_bed`.
# Questa funzione qui sopra si occupa solo dell'aggiornamento una volta che l'NPC *è già* a letto.