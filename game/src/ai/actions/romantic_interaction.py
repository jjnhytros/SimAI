# game/src/ai/actions/romantic_interaction.py
import logging
import random # Per decidere l'esito dell'interazione
from typing import TYPE_CHECKING, Optional

# Importa dal package 'game'
from game import config
from game.src.utils import game as game_utils

if TYPE_CHECKING:
    from game.src.entities.character import Character
    from game.src.modules.game_state_module import GameState

logger = logging.getLogger(__name__)
DEBUG_AI = getattr(config, 'DEBUG_AI_ACTIVE', False)

# --- Funzioni di Aggiornamento per Azioni Continue ---

def update_romantic_interaction(npc: 'Character', game_state: 'GameState', hours_passed_this_tick: float) -> bool:
    """
    Aggiorna l'azione 'romantic_interaction_action'.
    Restituisce True se l'azione è in corso, False se terminata.
    """
    interaction_duration_hours = getattr(config, 'IMMEDIATE_INTIMACY_INTERACTION_DURATION_HOURS', 0.1) # Breve durata per l'interazione immediata
    npc.time_in_current_action += hours_passed_this_tick

    if npc.time_in_current_action >= interaction_duration_hours:
        partner = npc.target_partner
        partner_name = partner.name if partner else "unknown"
        if DEBUG_AI: logger.debug(f"AI ({npc.name}): Terminata 'romantic_interaction_action' con {partner_name}.")

        # Applica effetti del bisogno
        npc.intimacy.satisfy(getattr(config, 'INTIMACY_SATISFACTION_ROMANTIC', 60))
        # Potrebbe anche dare un piccolo boost a 'Fun' o 'Social'
        npc.fun.satisfy(getattr(config, 'FUN_FROM_ROMANTIC_INTERACTION', 5))


        # Sincronizza e resetta il partner se era nella stessa interazione
        if partner and partner.target_partner == npc and partner.current_action == "romantic_interaction_action":
            partner.intimacy.satisfy(getattr(config, 'INTIMACY_SATISFACTION_ROMANTIC', 60))
            partner.fun.satisfy(getattr(config, 'FUN_FROM_ROMANTIC_INTERACTION', 5))
            partner.current_action = "idle" # O "post_interaction_idle"
            partner.is_interacting = False
            partner.target_partner = None
            partner.time_in_current_action = 0.0
        
        npc.current_action = "idle" # O "post_interaction_idle" se vuoi un cooldown
        npc.is_interacting = False
        npc.target_partner = None
        npc.time_in_current_action = 0.0
        return False # Azione terminata
    else:
        # L'NPC e il partner dovrebbero stare fermi e guardarsi durante questa azione
        npc.target_destination = None
        npc.current_path = None
        if npc.target_partner:
            if npc.rect.centerx < npc.target_partner.rect.centerx:
                npc.current_facing_direction = "right"
            elif npc.rect.centerx > npc.target_partner.rect.centerx:
                npc.current_facing_direction = "left"
            # Potresti aggiungere logica per Y se sono disallineati verticalmente
        return True # Azione in corso

def update_affectionate_interaction(npc: 'Character', game_state: 'GameState', hours_passed_this_tick: float) -> bool:
    """
    Aggiorna l'azione 'affectionate_interaction_action'.
    Restituisce True se l'azione è in corso, False se terminata.
    """
    interaction_duration_hours = getattr(config, 'IMMEDIATE_INTIMACY_INTERACTION_DURATION_HOURS', 0.1)
    npc.time_in_current_action += hours_passed_this_tick

    if npc.time_in_current_action >= interaction_duration_hours:
        partner = npc.target_partner
        partner_name = partner.name if partner else "unknown"
        if DEBUG_AI: logger.debug(f"AI ({npc.name}): Terminata 'affectionate_interaction_action' con {partner_name}.")

        npc.intimacy.satisfy(getattr(config, 'INTIMACY_SATISFACTION_AFFECTIONATE', 15))
        npc.social.satisfy(getattr(config, 'SOCIAL_SATISFACTION_AFFECTIONATE', 10))
        npc.fun.satisfy(getattr(config, 'FUN_FROM_AFFECTIONATE_INTERACTION', 2))


        if partner and partner.target_partner == npc and partner.current_action == "affectionate_interaction_action":
            partner.intimacy.satisfy(getattr(config, 'INTIMACY_SATISFACTION_AFFECTIONATE', 15))
            partner.social.satisfy(getattr(config, 'SOCIAL_SATISFACTION_AFFECTIONATE', 10))
            partner.fun.satisfy(getattr(config, 'FUN_FROM_AFFECTIONATE_INTERACTION', 2))
            partner.current_action = "idle"
            partner.is_interacting = False
            partner.target_partner = None
            partner.time_in_current_action = 0.0

        npc.current_action = "idle"
        npc.is_interacting = False
        npc.target_partner = None
        npc.time_in_current_action = 0.0
        return False # Azione terminata
    else:
        npc.target_destination = None
        npc.current_path = None
        if npc.target_partner: # Logica per guardarsi
             if npc.rect.centerx < npc.target_partner.rect.centerx: npc.current_facing_direction = "right"
             elif npc.rect.centerx > npc.target_partner.rect.centerx: npc.current_facing_direction = "left"
        return True # Azione in corso

def update_accepting_intimacy_and_waiting(npc: 'Character', game_state: 'GameState', hours_passed_this_tick: float) -> bool:
    """
    Aggiorna lo stato dell'NPC che ha accettato una proposta di intimità e sta aspettando il richiedente.
    Restituisce True se l'NPC sta ancora aspettando, False se l'attesa è terminata (timeout o richiedente arrivato/annullato).
    """
    waiting_timeout_hours = getattr(config, 'INTIMACY_WAITING_TIMEOUT_HOURS', 0.5) # Ore di gioco
    npc.time_in_current_action += hours_passed_this_tick
    
    requester = npc.target_partner # L'NPC che ha fatto la richiesta (e che dovrebbe raggiungere npc)

    # Controlla se il richiedente è ancora valido e sta ancora venendo
    if not requester or \
       requester.target_partner != npc or \
       requester.current_action not in ["moving_to_target", "seeking_partner_for_intimacy"]: # Aggiunto moving_to_target
        if DEBUG_AI:
            requester_name = requester.name if requester else "Nessuno"
            requester_action = requester.current_action if requester else "N/A"
            logger.debug(f"AI ({npc.name}): Stava aspettando, ma il richiedente ({requester_name}, azione: {requester_action}) non è più valido o non sta più venendo. Ritorno a idle.")
        npc.current_action = "idle"
        npc.is_interacting = False
        npc.target_partner = None
        npc.time_in_current_action = 0.0
        return False # Fine attesa

    # Controlla il timeout
    if npc.time_in_current_action >= waiting_timeout_hours:
        if DEBUG_AI:
            logger.debug(f"AI ({npc.name}): Timeout attesa per {requester.name}. Ritorno a idle.")
        # Informa il richiedente che l'attesa è finita (se è ancora in targeting)
        if requester and requester.target_partner == npc:
            requester.target_partner = None
            requester.target_destination = None # Annulla il suo movimento se stava venendo
            requester.current_path = None
            if requester.current_action == "moving_to_target" and requester.current_action_before_movement == "seeking_partner_for_intimacy":
                 requester.current_action = "idle" # Anche il richiedente torna idle
                 requester.previous_action_was_movement_to_target = False


        npc.current_action = "idle"
        npc.is_interacting = False
        npc.target_partner = None
        npc.time_in_current_action = 0.0
        return False # Fine attesa per timeout
    
    # L'NPC rimane fermo e in attesa
    npc.target_destination = None
    npc.current_path = None
    if DEBUG_AI:
        # Questo log potrebbe essere frequente
        # logger.debug(f"AI ({npc.name}): In attesa di {requester.name}. Timer: {npc.time_in_current_action:.2f}/{waiting_timeout_hours:.2f}")
        pass
    return True # Ancora in attesa

# --- Funzioni Handler per Arrivo (per l'NPC che inizia l'interazione) ---

def handle_arrival_at_partner_for_intimacy(npc: 'Character', game_state: 'GameState', pf_grid) -> bool:
    """
    Gestisce l'arrivo dell'NPC (richiedente) vicino al potenziale partner per un'interazione di intimità.
    Il partner dovrebbe essere in stato "accepting_intimacy_and_waiting".
    Decide se iniziare un'interazione romantica/affettuosa o procedere verso il letto.
    Restituisce True se un'azione significativa è iniziata, False se l'NPC torna idle.
    """
    partner = npc.target_partner
    if DEBUG_AI:
        partner_name = partner.name if partner else "None"
        partner_action = partner.current_action if partner else "N/A"
        logger.debug(f"AI ({npc.name}): Arrivato vicino a {partner_name} (azione: {partner_action}) per intimità.")

    # Controlla se il partner è valido, sta aspettando questo NPC, ed è abbastanza vicino
    if not partner or \
       partner.current_action != "accepting_intimacy_and_waiting" or \
       partner.target_partner != npc or \
       not game_utils.is_close_to_point(npc.rect.center, partner.rect.center, config.NPC_PARTNER_INTERACTION_DISTANCE * 1.5):
        
        if DEBUG_AI:
            logger.warning(f"AI WARN ({npc.name}): Arrivato per intimità, ma il partner ({partner_name}) non è valido/in attesa/vicino. Ritorno a idle.")
        if partner and partner.target_partner == npc and partner.current_action == "accepting_intimacy_and_waiting":
            partner.current_action = "idle" # Il partner smette di aspettare
            partner.target_partner = None
            partner.is_interacting = False
            partner.time_in_current_action = 0.0
        
        npc.current_action = "idle"
        npc.target_partner = None
        return False # Interazione fallita

    # Partner è valido e in attesa. Decide cosa fare dopo: interazione immediata o andare a letto.
    # Per ora, l'esempio originale andava direttamente a letto.
    # Manteniamo questa logica per ora, la parte di "interazione romantica/affettuosa"
    # potrebbe essere un'alternativa o un passo precedente.

    if DEBUG_AI:
        logger.debug(f"AI ({npc.name}) e ({partner.name}) si sono incontrati con successo. Inizio sequenza per andare a letto.")

    # Logica per trovare due slot letto liberi e avviare l'azione "going_to_bed_together"
    # Questo è un duplicato della logica che potrebbe essere in `idle.py` o `going_to_bed_together.py`
    # Idealmente, questa parte dovrebbe essere una chiamata a una funzione condivisa
    # o la transizione a uno stato che `going_to_bed_together.py` gestisce.

    # Per semplicità, assumiamo che la decisione di andare a letto sia presa qui.
    # Se l'intimità immediata è un'opzione, andrebbe qui.
    # In questo refactoring, le azioni "romantic_interaction_action" e "affectionate_interaction_action"
    # sono separate e non sono direttamente parte di questa sequenza di "andare a letto".
    # Potresti volerle integrare come possibili esiti di "seeking_partner_for_intimacy".

    # Per ora, questa funzione delega la decisione di andare a letto all'azione "idle" del partner
    # che ora sa che il richiedente è arrivato. O meglio, questa funzione dovrebbe iniziare
    # la sequenza di "andare a letto insieme".

    from .going_to_bed_together import start_going_to_bed_together # Importa la funzione di avvio
    if start_going_to_bed_together(npc, partner, game_state, pf_grid):
        return True # Sequenza per andare a letto iniziata
    else:
        # Fallimento nel trovare slot o path per il letto
        if DEBUG_AI: logger.warning(f"AI WARN ({npc.name}): Fallito l'avvio di 'going_to_bed_together' con {partner.name}.")
        npc.current_action = "idle"
        partner.current_action = "idle" # Anche il partner torna idle
        partner.is_interacting = False
        partner.target_partner = None
        npc.target_partner = None
        return False