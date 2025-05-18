# game/src/ai/actions/phoning.py
import logging
from typing import TYPE_CHECKING

# Importa dal package 'game'
from game import config

if TYPE_CHECKING:
    from game.src.entities.character import Character
    from game.src.modules.game_state_module import GameState

logger = logging.getLogger(__name__)
DEBUG_AI = getattr(config, 'DEBUG_AI_ACTIVE', False)

def update_phoning(npc: 'Character', game_state: 'GameState', hours_passed_this_tick: float) -> bool:
    """
    Aggiorna la logica per l'azione 'phoning'.
    L'NPC "telefona" per una durata specifica per aumentare la socialità.
    Restituisce True se l'azione è ancora in corso, False se è terminata.
    """
    phoning_duration_hours = getattr(config, 'PHONING_DURATION_HOURS', 0.25) # Durata in ore di gioco
    
    npc.time_in_current_action += hours_passed_this_tick

    if npc.time_in_current_action >= phoning_duration_hours:
        social_gain = getattr(config, 'SOCIAL_RECOVERY_FROM_PHONE', 20)
        npc.social.satisfy(social_gain) # Il metodo satisfy di BaseNeed gestirà l'aumento
        
        if DEBUG_AI:
            logger.debug(f"AI ({npc.name}): Finito di telefonare. Socialità aumentata di {social_gain}. Valore attuale: {npc.social.get_value():.1f}")
        
        npc.current_action = "idle"
        npc.is_interacting = False # Non sta più attivamente telefonando
        npc.time_in_current_action = 0.0
        # Non c'è un target_partner specifico per l'azione "phoning" come implementata finora
        npc.target_partner = None 
        return False # Azione terminata
    else:
        if DEBUG_AI:
            # Questo log può essere molto frequente
            # logger.debug(f"AI ({npc.name}): Sta ancora telefonando. Timer: {npc.time_in_current_action:.2f}/{phoning_duration_hours:.2f}")
            pass
        # Potresti voler impostare un'animazione specifica per "phoning" se l'hai
        # npc.current_animation_key = "phoning_anim_" + npc.current_facing_direction 
        return True # Azione ancora in corso

# La decisione di INIZIARE l'azione "phoning" viene presa in idle.py (handle_idle_decision)
# quando il bisogno Social è basso. Quella funzione imposterà:
# npc.current_action = "phoning"
# npc.is_interacting = True
# npc.time_in_current_action = 0.0
# Non c'è un target_destination per questa azione, quindi l'NPC starà fermo.