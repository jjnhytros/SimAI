# game/src/ai/actions/cuddling_in_bed.py
import logging
from typing import TYPE_CHECKING

# Importa dal package 'game'
from game import config
from game.src.utils import game as game_utils # Per free_bed_slot_for_character

if TYPE_CHECKING:
    from game.src.entities.character import Character
    from game.src.modules.game_state_module import GameState

logger = logging.getLogger(__name__)
DEBUG_AI = getattr(config, 'DEBUG_AI_ACTIVE', False)

def start_cuddling_in_bed(npc1: 'Character', npc2: 'Character', game_state: 'GameState') -> bool:
    """
    Inizia l'azione 'cuddling_in_bed' per entrambi gli NPC.
    Chiamata quando entrambi gli NPC sono a letto e pronti.
    Restituisce True se l'azione è iniziata con successo.
    """
    if not (npc1 and npc2 and npc1.is_on_bed and npc2.is_on_bed and \
            npc1.bed_object_id == "main_bed" and npc2.bed_object_id == "main_bed" and \
            npc1.bed_slot_index != -1 and npc2.bed_slot_index != -1 and \
            npc1.bed_slot_index != npc2.bed_slot_index): # Assicura che siano su slot diversi dello stesso letto
        logger.warning(f"AI WARN: Tentativo di iniziare cuddling_in_bed per {npc1.name} e {npc2.name} fallito. Condizioni non soddisfatte.")
        # Potrebbe essere necessario resettare lo stato di uno o entrambi se sono in uno stato di attesa errato
        if npc1.current_action == "waiting_in_bed_for_partner": npc1.current_action = "idle"
        if npc2.current_action == "waiting_in_bed_for_partner": npc2.current_action = "idle"
        return False

    if DEBUG_AI:
        logger.debug(f"AI: {npc1.name} e {npc2.name} iniziano 'cuddling_in_bed'.")

    npc1.current_action = "cuddling_in_bed"
    npc1.target_partner = npc2 # Assicurati che il partner sia impostato per l'azione
    npc1.time_in_current_action = 0.0
    npc1.is_interacting = True # Ora stanno interagendo attivamente

    npc2.current_action = "cuddling_in_bed"
    npc2.target_partner = npc1
    npc2.time_in_current_action = 0.0
    npc2.is_interacting = True

    # Logica per farli guardare l'un l'altro (basata sugli slot o posizione)
    # Assumiamo che lo slot 0 sia a sinistra e lo slot 1 a destra del letto (visivamente)
    if npc1.bed_slot_index == 0 and npc2.bed_slot_index == 1:
        npc1.current_facing_direction = "right" # Guarda verso il partner
        npc2.current_facing_direction = "left"  # Guarda verso il partner
    elif npc1.bed_slot_index == 1 and npc2.bed_slot_index == 0:
        npc1.current_facing_direction = "left"
        npc2.current_facing_direction = "right"
    else:
        # Fallback se gli slot non sono 0 e 1 come previsto, potrebbero guardare in alto
        npc1.current_facing_direction = "up"
        npc2.current_facing_direction = "up"
        logger.warning(f"AI WARN: Direzione cuddling non standard per {npc1.name} (slot {npc1.bed_slot_index}) e {npc2.name} (slot {npc2.bed_slot_index})")
        
    # Qui potresti voler cambiare l'animazione a una specifica per "cuddling" se l'hai
    # npc1.current_animation_key = "cuddling_animation_slot0" # o simile
    # npc2.current_animation_key = "cuddling_animation_slot1"
    # Altrimenti, l'animazione di sonno impostata quando sono entrati nel letto continuerà.

    return True


def update_cuddling_in_bed(npc: 'Character', game_state: 'GameState', hours_passed_this_tick: float) -> bool:
    """
    Aggiorna la logica per l'azione 'cuddling_in_bed'.
    L'azione ha una durata e fornisce benefici ai bisogni.
    Restituisce True se l'azione è ancora in corso, False se è terminata.
    """
    if not npc.is_on_bed or not npc.target_partner or not npc.target_partner.is_on_bed or \
       npc.target_partner.current_action != "cuddling_in_bed" or npc.target_partner.target_partner != npc:
        # Il partner ha interrotto l'azione o c'è un'incongruenza
        if DEBUG_AI:
            partner_name = npc.target_partner.name if npc.target_partner else "Nessuno"
            logger.info(f"AI ({npc.name}): Cuddling interrotto. Partner ({partner_name}) non più in cuddling o non valido. {npc.name} esce dal letto.")
        game_utils.free_bed_slot_for_character(game_state, npc)
        npc.current_action = "idle" # O "post_intimacy_idle"
        npc.target_partner = None
        npc.is_interacting = False
        return False

    cuddling_duration_hours = getattr(config, 'CUDDLING_DURATION_HOURS', 1.0)
    npc.time_in_current_action += hours_passed_this_tick

    if npc.time_in_current_action >= cuddling_duration_hours:
        partner = npc.target_partner # Dovrebbe essere ancora valido a questo punto
        partner_name = partner.name if partner else "sconosciuto"
        if DEBUG_AI:
            logger.debug(f"AI ({npc.name}): Finito 'cuddling_in_bed' con {partner_name}.")

        intimacy_gain = getattr(config, 'INTIMACY_FROM_CUDDLING', 50)
        social_gain = getattr(config, 'SOCIAL_FROM_CUDDLING', 20)
        fun_gain = getattr(config, 'FUN_FROM_CUDDLING', 10)
        energy_gain_cuddling = getattr(config, 'ENERGY_RECOVERY_WHILE_CUDDLING_RATE', 5.0) # Potrebbero recuperare meno energia

        npc.intimacy.satisfy(intimacy_gain)
        npc.social.satisfy(social_gain)
        npc.fun.satisfy(fun_gain)
        npc.energy.recover(energy_gain_cuddling, npc.time_in_current_action) # Recupera un po' di energia

        # Libera lo slot del letto per l'NPC corrente
        game_utils.free_bed_slot_for_character(game_state, npc)
        npc.current_action = "post_intimacy_idle"
        npc.is_interacting = False # Non più interagendo con il letto o il partner in questo modo
        npc.target_partner = None # L'interazione cuddling è finita
        npc.time_in_current_action = 0.0
        
        # Il partner verrà gestito dal suo ciclo di update_cuddling_in_bed.
        # Non c'è bisogno di resettare lo stato del partner qui,
        # altrimenti lo si farebbe due volte.
        # La funzione free_bed_slot_for_character gestisce l'aggiornamento di is_on_bed a False.
        
        return False # Azione terminata
    else:
        # L'NPC e il partner dovrebbero rimanere fermi, l'animazione (di sonno o cuddling) continua.
        # La direzione è già stata impostata da start_cuddling_in_bed.
        if DEBUG_AI:
            # logger.debug(f"AI ({npc.name}): Ancora in 'cuddling_in_bed'. Timer: {npc.time_in_current_action:.2f}/{cuddling_duration_hours:.2f}")
            pass
        return True # Azione ancora in corso