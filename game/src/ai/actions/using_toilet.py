# game/src/ai/actions/using_toilet.py
import logging
from typing import TYPE_CHECKING, Optional

# Importa dal package 'game'
from game import config
# game_utils potrebbe essere necessario per is_close_to_point se l'interazione è più complessa
from game.src.utils import game as game_utils 

if TYPE_CHECKING:
    from game.src.entities.character import Character
    from game.src.modules.game_state_module import GameState

logger = logging.getLogger(__name__)
DEBUG_AI = getattr(config, 'DEBUG_AI_ACTIVE', False)

# --- Funzione Handler per Arrivo ---

def handle_arrival_at_toilet(npc: 'Character', game_state: 'GameState', pf_grid) -> bool:
    """
    Gestisce l'arrivo dell'NPC al punto di interazione del bagno.
    Inizia l'azione "using_toilet".
    Restituisce True se l'NPC ha iniziato a usare il bagno, False altrimenti.
    """
    if DEBUG_AI:
        logger.debug(f"AI ({npc.name}): Arrivato a destinazione per 'seeking_toilet'. Target: {npc.target_destination}")

    # Verifica se l'NPC è effettivamente vicino al bagno (il suo target_destination)
    # game_state.toilet_rect_instance contiene il Rect del bagno.
    # Il target_destination dell'NPC dovrebbe essere un punto di interazione vicino/davanti al bagno.
    # Per ora, assumiamo che l'arrivo al target_destination sia sufficiente.
    
    if game_state.toilet_rect_instance: # Assicurati che il bagno esista
        # (Opzionale: potresti voler controllare se il bagno è "occupato" se hai più NPC
        # e un solo bagno, ma per ora non implementiamo questa logica di "occupazione oggetto")

        npc.current_action = "using_toilet"
        npc.is_interacting = True # Sta interagendo con il bagno
        npc.time_in_current_action = 0.0 # Resetta il timer per la nuova azione
        
        # L'NPC dovrebbe girarsi verso il bagno (se hai animazioni/sprite specifici)
        # Ad esempio, se il punto di interazione è sotto il bagno, l'NPC guarda in alto.
        # Questo dipende da come hai definito il punto di interazione e lo sprite del bagno.
        # npc.current_facing_direction = "up" # Esempio
        
        # L'NPC smette di muoversi
        npc.target_destination = None
        npc.current_path = None
        
        if DEBUG_AI:
            logger.debug(f"AI ({npc.name}): Iniziato 'using_toilet'.")
        return True # Azione di arrivo completata, nuova azione iniziata
    else:
        if DEBUG_AI:
            logger.warning(f"AI WARN ({npc.name}): Arrivato per usare il bagno, ma game_state.toilet_rect_instance non è definito. Torno a idle.")
        npc.current_action = "idle"
        return False

# --- Funzione di Aggiornamento per Azione Continua ---

def update_using_toilet(npc: 'Character', game_state: 'GameState', hours_passed_this_tick: float) -> bool:
    """
    Aggiorna la logica per l'azione 'using_toilet'.
    L'NPC usa il bagno per una durata specifica per soddisfare il bisogno Bladder.
    Restituisce True se l'azione è ancora in corso, False se è terminata.
    """
    toilet_use_duration_hours = getattr(config, 'TOILET_USE_DURATION_HOURS', 0.20) # Durata in ore di gioco
    
    npc.time_in_current_action += hours_passed_this_tick

    if npc.time_in_current_action >= toilet_use_duration_hours:
        bladder_relief = getattr(config, 'BLADDER_RELIEF_AMOUNT', 85)
        npc.bladder.satisfy(bladder_relief) # Il metodo satisfy di BaseNeed gestirà la diminuzione
        
        # L'uso del bagno potrebbe anche influire leggermente sull'igiene (in positivo o negativo a seconda del design)
        hygiene_change_from_toilet = getattr(config, 'HYGIENE_CHANGE_FROM_TOILET', 0) # Es: 0 per nessun cambio, >0 per aumento, <0 per diminuzione
        if hygiene_change_from_toilet != 0:
            npc.hygiene.satisfy(hygiene_change_from_toilet)

        if DEBUG_AI:
            logger.debug(f"AI ({npc.name}): Finito di usare il bagno. Vescica soddisfatta di {bladder_relief}. Valore attuale: {npc.bladder.get_value():.1f}")
            if hygiene_change_from_toilet != 0:
                logger.debug(f"AI ({npc.name}): Igiene modificata di {hygiene_change_from_toilet}. Valore attuale: {npc.hygiene.get_value():.1f}")

        npc.current_action = "idle"
        npc.is_interacting = False
        npc.time_in_current_action = 0.0
        return False # Azione terminata
    else:
        if DEBUG_AI:
            # logger.debug(f"AI ({npc.name}): Sta ancora usando il bagno. Timer: {npc.time_in_current_action:.2f}/{toilet_use_duration_hours:.2f}")
            pass
        # Potresti voler impostare un'animazione specifica per "using_toilet" se l'hai
        # npc.current_animation_key = "sitting_on_toilet_anim_" + npc.current_facing_direction 
        return True # Azione ancora in corso