# game/src/ai/npc_behavior.py

# --- IMPORT ---
import math
import random
# import asyncio # Rimuovi se non usi coroutine nelle helper
import pygame 
import sys
from typing import Optional, Tuple, List

try:
    # Quando esegui con 'python -m game.main' dalla directory 'simai/'
    from game.src.entities.character import Character
    from game import config
    from game.src.utils import game as game_utils # Potrebbe servire per find_path_to_target, is_close_to_point, ecc.
    # Se GameState è stato spostato in src/modules/game_state_module.py
    from game.src.modules.game_state_module import GameState 
except ImportError as e:
    print(f"CRITICAL ERROR (npc_behavior.py): Could not import dependencies: {e}")
    sys.exit()

DEBUG_AI = getattr(config, 'DEBUG_AI_ACTIVE', False)

# --- DEFINIZIONI DELLE FUNZIONI HELPER (SOLO PER RIPOSO) ---

def _handle_continuous_actions(npc: Character, game_state: GameState, hours_passed_this_tick: float) -> Optional[bool]:
    if npc.current_action == "resting_on_bed":
        if npc.energy.get_value() >= npc.energy.max_value:
            if npc.bed_object_id is not None and npc.bed_slot_index != -1:
                # Usa la funzione helper che abbiamo definito, se game_utils è importato
                if 'game_utils' in sys.modules: # Controlla se game_utils è importato
                    game_utils.free_bed_slot_for_character(game_state, npc)
                else: # Fallback se game_utils non è importato qui (dovrebbe esserlo)
                    if npc.bed_slot_index == 0: game_state.bed_slot_1_occupied_by = None
                    elif npc.bed_slot_index == 1: game_state.bed_slot_2_occupied_by = None
                    if DEBUG_AI: print(f"AI WARN: game_utils not available in _handle_continuous_actions for freeing bed slot.")

            npc.is_on_bed = False
            npc.bed_object_id = None
            npc.bed_slot_index = -1 # o None
            npc.current_action = "idle"
            npc.is_interacting = False
            if DEBUG_AI: print(f"AI: {npc.name} woke up from bed. Energy: {npc.energy.get_value()}.")
            return False
        else:
            if DEBUG_AI: print(f"AI: {npc.name} is still resting_on_bed. Energy: {npc.energy.get_value()}.")
            return True

    elif npc.current_action == "phoning":
        phoning_duration = getattr(config, 'PHONING_DURATION_HOURS', 0.25)
        npc.time_in_current_action += hours_passed_this_tick # Ora usa il nome corretto del parametro
        if npc.time_in_current_action >= phoning_duration:
            if DEBUG_AI: print(f"AI: {npc.name} finished phoning.")
            npc.social.satisfy(getattr(config, 'SOCIAL_RECOVERY_FROM_PHONE', 20))
            npc.current_action = "idle"
            npc.is_interacting = False
            npc.time_in_current_action = 0.0
            return False
        else:
            if DEBUG_AI: print(f"AI: {npc.name} is still phoning. Timer: {npc.time_in_current_action:.2f}/{phoning_duration:.2f}")
            return True

    elif npc.current_action in ["romantic_interaction_action", "affectionate_interaction_action"]:
        interaction_duration_game_hours = getattr(config, 'IMMEDIATE_INTIMACY_INTERACTION_DURATION_HOURS', 0.1)
        npc.time_in_current_action += hours_passed_this_tick # Usa il nome corretto del parametro
        if npc.time_in_current_action >= interaction_duration_game_hours:
            # ... (logica di fine interazione, assicurati di resettare anche il partner)
            if npc.target_partner:
                if npc.current_action == "romantic_interaction_action":
                    npc.target_partner.intimacy.satisfy(config.INTIMACY_SATISFACTION_ROMANTIC)
                elif npc.current_action == "affectionate_interaction_action":
                    npc.target_partner.intimacy.satisfy(config.INTIMACY_SATISFACTION_AFFECTIONATE)
                    npc.target_partner.social.satisfy(config.SOCIAL_SATISFACTION_AFFECTIONATE)

                if npc.target_partner.target_partner == npc and npc.target_partner.current_action == npc.current_action:
                    npc.target_partner.current_action = "idle"
                    npc.target_partner.is_interacting = False
                    npc.target_partner.target_partner = None
                    npc.target_partner.time_in_current_action = 0.0

            if npc.current_action == "romantic_interaction_action":
                npc.intimacy.satisfy(config.INTIMACY_SATISFACTION_ROMANTIC)
            elif npc.current_action == "affectionate_interaction_action":
                npc.intimacy.satisfy(config.INTIMACY_SATISFACTION_AFFECTIONATE)
                npc.social.satisfy(config.SOCIAL_SATISFACTION_AFFECTIONATE)

            if DEBUG_AI: print(f"AI: {npc.name} finished {npc.current_action} with {npc.target_partner.name if npc.target_partner else 'unknown'}.")
            npc.current_action = "idle"
            npc.is_interacting = False
            npc.target_partner = None
            npc.time_in_current_action = 0.0
            return False
        else:
            npc.target_destination = None
            npc.current_path = None
            if DEBUG_AI: print(f"AI: {npc.name} continuing {npc.current_action}. Timer: {npc.time_in_current_action:.2f}")
            return True

    elif npc.current_action == "accepting_intimacy_and_waiting":
        waiting_timeout_hours = getattr(config, 'INTIMACY_WAITING_TIMEOUT_HOURS', 0.5)
        npc.time_in_current_action += hours_passed_this_tick # Usa il nome corretto del parametro
        requester = npc.target_partner
        if requester and requester.current_action == "seeking_partner_for_intimacy" and requester.target_partner == npc:
            if npc.time_in_current_action < waiting_timeout_hours:
                if DEBUG_AI: print(f"AI: {npc.name} is waiting for {requester.name}. Timer: {npc.time_in_current_action:.2f}/{waiting_timeout_hours:.2f}")
                return True
            else:
                if DEBUG_AI: print(f"AI: {npc.name} timed out waiting for {requester.name}. Returning to idle.")
                if requester: requester.target_partner = None
        else:
            if DEBUG_AI: print(f"AI: {npc.name} was waiting, but requester {requester.name if requester else 'None'} is no longer seeking them or is invalid. Returning to idle.")
        npc.current_action = "idle"
        npc.is_interacting = False
        npc.target_partner = None
        npc.time_in_current_action = 0.0
        return False

    elif npc.current_action == "going_to_bed_together_leader" or npc.current_action == "going_to_bed_together_follower":
        if not npc.current_path and not npc.target_destination:
             if DEBUG_AI: print(f"AI WARN: {npc.name} finished path for '{npc.current_action}' but not at bed? Returning to idle.")
             npc.current_action = "idle"
             if npc.target_partner and npc.target_partner.current_action == "going_to_bed_together_follower":
                  npc.target_partner.current_action = "idle"
                  npc.target_partner.target_destination = None
                  npc.target_partner.current_path = None
             npc.target_partner = None
             return False
        return True

    elif npc.current_action == "cuddling_in_bed":
        cuddling_duration_hours = getattr(config, 'CUDDLING_DURATION_HOURS', 1.0)
        npc.time_in_current_action += hours_passed_this_tick # Usa il nome corretto del parametro
        if npc.time_in_current_action >= cuddling_duration_hours:
            if DEBUG_AI: print(f"AI: {npc.name} finished cuddling_in_bed with {npc.target_partner.name if npc.target_partner else 'unknown'}.")
            intimacy_gain = getattr(config, 'INTIMACY_FROM_CUDDLING', 50)
            social_gain = getattr(config, 'SOCIAL_FROM_CUDDLING', 20)
            fun_gain = getattr(config, 'FUN_FROM_CUDDLING', 10)

            npc.intimacy.satisfy(intimacy_gain)
            npc.social.satisfy(social_gain)
            npc.fun.satisfy(fun_gain)

            if npc.target_partner:
                npc.target_partner.intimacy.satisfy(intimacy_gain)
                npc.target_partner.social.satisfy(social_gain)
                npc.target_partner.fun.satisfy(fun_gain)
                if npc.target_partner.target_partner == npc and npc.target_partner.current_action == "cuddling_in_bed":
                    game_utils.free_bed_slot_for_character(game_state, npc.target_partner)
                    npc.target_partner.current_action = "post_intimacy_idle"
                    npc.target_partner.is_on_bed = False
                    npc.target_partner.target_partner = None
                    npc.target_partner.time_in_current_action = 0.0

            game_utils.free_bed_slot_for_character(game_state, npc)
            npc.current_action = "post_intimacy_idle"
            npc.is_on_bed = False
            npc.target_partner = None
            npc.time_in_current_action = 0.0
            return False
        else:
            if npc.target_partner:
                if npc.rect.centerx < npc.target_partner.rect.centerx:
                    npc.current_facing_direction = "right"
                else:
                    npc.current_facing_direction = "left"
            if DEBUG_AI: print(f"AI: {npc.name} continuing cuddling_in_bed. Timer: {npc.time_in_current_action:.2f}/{cuddling_duration_hours:.2f}")
            return True

    elif npc.current_action == "post_intimacy_idle":
        post_interaction_idle_duration = getattr(config, 'POST_INTIMACY_IDLE_DURATION_HOURS', 0.1)
        npc.time_in_current_action += hours_passed_this_tick # Usa il nome corretto del parametro
        if npc.time_in_current_action >= post_interaction_idle_duration:
            npc.current_action = "idle"
            npc.time_in_current_action = 0.0
            return False
        return True
    return None

# _handle_partner_seeking, _check_and_handle_interruptions (per altri bisogni) sono commentate/rimosse

def _handle_arrival_at_destination(npc: Character, game_state: GameState, pf_grid) -> Optional[bool]:
    action_at_arrival = npc.current_action
    if DEBUG_AI: print(f"AI: {npc.name} evaluating arrival for action: {action_at_arrival}")

    if action_at_arrival == "seeking_bed":
        # L'NPC è arrivato alla destinazione del letto.
        # Qui dovrebbe esserci la logica per "entrare" nel letto e cambiare azione a "resting_on_bed".
        # Questo include occupare lo slot del letto in GameState e aggiornare lo stato dell'NPC.
        
        # Verifica se il target_destination corrisponde a un punto di interazione del letto
        # e se lo slot è ancora libero.
        # Questa logica dipende da come identifichi i letti e gli slot (es. tramite ID oggetto, coordinate).
        
        # Esempio semplificato: se l'NPC è arrivato vicino al target e lo slot è quello targettizzato
        # (npc.bed_slot_index dovrebbe essere stato impostato da _make_idle_decision)
        
        can_use_bed = False
        bed_interaction_target = npc.target_destination # Il punto di interazione a cui si è mosso
        
        # Determina quale slot del letto è stato raggiunto (logica semplificata)
        # Questa parte andrebbe migliorata con una gestione oggetti più robusta
        target_slot_index = -1
        if game_state.bed_slot_1_interaction_pos_world and \
           game_utils.are_coords_equal(bed_interaction_target, game_state.bed_slot_1_interaction_pos_world, tolerance=config.TILE_SIZE // 2):
            target_slot_index = 0
        elif game_state.bed_slot_2_interaction_pos_world and \
             game_utils.are_coords_equal(bed_interaction_target, game_state.bed_slot_2_interaction_pos_world, tolerance=config.TILE_SIZE // 2):
            target_slot_index = 1

        if target_slot_index == 0 and not game_state.bed_slot_1_occupied_by:
            game_state.bed_slot_1_occupied_by = npc.uuid
            npc.bed_object_id = "main_bed" # ID generico del letto, o l'ID dell'oggetto letto se ne hai
            npc.bed_slot_index = 0
            can_use_bed = True
        elif target_slot_index == 1 and not game_state.bed_slot_2_occupied_by:
            game_state.bed_slot_2_occupied_by = npc.uuid
            npc.bed_object_id = "main_bed"
            npc.bed_slot_index = 1
            can_use_bed = True

        if can_use_bed:
            npc.current_action = "resting_on_bed" 
            npc.is_on_bed = True 
            npc.is_interacting = True # Inizia interazione "sonno"
            # L'NPC si "teletrasporta" alla sleeping_pos dello slot (o l'animazione gestisce il movimento finale)
            if npc.bed_slot_index == 0 and game_state.bed_slot_1_sleep_pos_world:
                npc.rect.center = game_state.bed_slot_1_sleep_pos_world
            elif npc.bed_slot_index == 1 and game_state.bed_slot_2_sleep_pos_world:
                npc.rect.center = game_state.bed_slot_2_sleep_pos_world
            if DEBUG_AI: print(f"AI: {npc.name} got into bed slot {npc.bed_slot_index}.")
        else:
            if DEBUG_AI: print(f"AI: {npc.name} arrived at bed, but slot {target_slot_index} (intended: {npc.bed_slot_index}) is occupied or invalid.")
            npc.current_action = "idle" # Non può usare il letto, torna idle
            npc.bed_slot_index = -1 # Resetta lo slot target

        npc.path = None 
        npc.target_destination = None
        return False # Azione "seeking_bed" terminata (o passata a "resting_on_bed"), nessun cibo mangiato

    elif action_at_arrival == "seeking_partner_for_intimacy":
        if DEBUG_AI: print(f"AI: {npc.name} arrived near target partner {npc.target_partner.name if npc.target_partner else 'None'} for intimacy.")
        partner = npc.target_partner
        if partner and hasattr(partner, 'rect') and game_utils.is_close_to_point(npc.rect.center, partner.rect.center, config.NPC_PARTNER_INTERACTION_DISTANCE * 1.5):
            # Partner trovato e vicino. Ora il partner deve rispondere e andare a letto insieme.
            # L'NPC iniziatore potrebbe entrare in uno stato di attesa "waiting_for_partner_to_go_to_bed"
            # Il partner, se accetta, cambierà stato in "responding_to_intimacy_invite" e poi "going_to_bed_together_follower"
            if DEBUG_AI: print(f"AI: {npc.name} initiating bed sequence with {partner.name}.")

            # Trova uno slot libero nel letto per la coppia
            slot1_pos_interaction = game_state.bed_slot_1_interaction_pos_world
            slot2_pos_interaction = game_state.bed_slot_2_interaction_pos_world
            chosen_slot_npc = -1
            chosen_slot_partner = -1

            if slot1_pos_interaction and not game_state.bed_slot_1_occupied_by:
                if slot2_pos_interaction and not game_state.bed_slot_2_occupied_by:
                    # Entrambi liberi, assegna casualmente o in base alla vicinanza
                    chosen_slot_npc = 0 # NPC iniziatore prende slot 0
                    chosen_slot_partner = 1 # Partner prende slot 1
                else: # Solo slot 1 libero
                    pass # Non abbastanza spazio per due
            elif slot2_pos_interaction and not game_state.bed_slot_2_occupied_by:
                 # Solo slot 2 libero
                 pass # Non abbastanza spazio per due

            if chosen_slot_npc != -1 and chosen_slot_partner != -1:
                npc_bed_destination_interaction = game_state.bed_slot_1_interaction_pos_world if chosen_slot_npc == 0 else game_state.bed_slot_2_interaction_pos_world
                partner_bed_destination_interaction = game_state.bed_slot_1_interaction_pos_world if chosen_slot_partner == 0 else game_state.bed_slot_2_interaction_pos_world

                # USA pf_grid (passato come argomento) o game_state.a_star_grid_instance
                # È meglio essere consistenti. Se pf_grid è la griglia aggiornata, usala.
                # Se game_state.a_star_grid_instance è sempre la fonte di verità, usala.
                # Dato che pf_grid è passato a run_npc_ai_logic, usiamo quello.
                path_npc_to_bed = game_utils.find_path_to_target(npc, npc_bed_destination_interaction, pf_grid, game_state.world_objects_list)
                path_partner_to_bed = game_utils.find_path_to_target(partner, partner_bed_destination_interaction, pf_grid, game_state.world_objects_list)

                if path_npc_to_bed and path_partner_to_bed:
                    npc.current_action = "going_to_bed_together_leader"
                    npc.target_destination = npc_bed_destination_interaction
                    npc.current_path = path_npc_to_bed
                    npc.bed_slot_index = chosen_slot_npc # Memorizza lo slot target
                    npc.target_partner = partner # Mantieni il riferimento al partner

                    partner.current_action = "going_to_bed_together_follower"
                    partner.target_destination = partner_bed_destination_interaction
                    partner.current_path = path_partner_to_bed
                    partner.bed_slot_index = chosen_slot_partner
                    partner.target_partner = npc # Il partner sa con chi sta andando
                    partner.is_interacting = True # Il partner è ora impegnato

                    if DEBUG_AI: print(f"AI: {npc.name} (leader) and {partner.name} (follower) going to bed together.")
                else:
                    if DEBUG_AI: print(f"AI WARN: {npc.name} or {partner.name} could not find path to bed for intimacy.")
                    npc.current_action = "idle" # Fallback
                    partner.current_action = "idle"
                    npc.target_partner = None
            else:
                if DEBUG_AI: print(f"AI INFO: {npc.name} wanted intimacy with {partner.name}, but no two free bed slots available.")
                npc.current_action = "idle"
                npc.target_partner = None
        else:
            if DEBUG_AI: print(f"AI: {npc.name} arrived but partner {npc.target_partner.name if npc.target_partner else 'None'} is no longer valid/close for intimacy initiation.")
            npc.current_action = "idle"
            npc.target_partner = None
        npc.current_path = None # Path per raggiungere il partner è completato
        npc.target_destination = None # Resetta la destinazione del partner
        return False

    elif action_at_arrival == "seeking_partner_for_intimacy": # Questo è l'NPC richiedente che arriva
        partner = npc.target_partner # Il partner che dovrebbe essere in attesa
        if DEBUG_AI: print(f"AI: {npc.name} (requester) arrived near {partner.name if partner else 'None'}.")

        # Controlla se il partner è effettivamente in attesa di questo NPC
        if partner and partner.current_action == "accepting_intimacy_and_waiting" and \
           partner.target_partner == npc and \
           game_utils.is_close_to_point(npc.rect.center, partner.rect.center, config.NPC_PARTNER_INTERACTION_DISTANCE * 1.5):
            
            if DEBUG_AI: print(f"AI: {npc.name} and {partner.name} successfully met. Initiating bed sequence.")
            # Logica per trovare due slot letto e far muovere entrambi gli NPC
            # (Questa parte era già stata abbozzata prima e usava pf_grid)
            slot1_pos_interaction = game_state.bed_slot_1_interaction_pos_world
            slot2_pos_interaction = game_state.bed_slot_2_interaction_pos_world
            chosen_slot_npc = -1
            chosen_slot_partner = -1

            if slot1_pos_interaction and not game_state.bed_slot_1_occupied_by and \
               slot2_pos_interaction and not game_state.bed_slot_2_occupied_by:
                # Assegna slot (es. NPC più vicino a slot 0 prende slot 0)
                # Semplificazione: npc prende slot 0, partner slot 1
                chosen_slot_npc = 0
                chosen_slot_partner = 1
            # Potresti aggiungere logica per controllare altri casi (solo uno slot libero, ecc.)

            if chosen_slot_npc != -1 and chosen_slot_partner != -1:
                npc_bed_dest_interaction = slot1_pos_interaction if chosen_slot_npc == 0 else slot2_pos_interaction
                partner_bed_dest_interaction = slot1_pos_interaction if chosen_slot_partner == 0 else slot2_pos_interaction
                
                # pf_grid qui è passato come argomento a _handle_arrival_at_destination
                path_npc_to_bed = game_utils.find_path_to_target(npc, npc_bed_dest_interaction, pf_grid, game_state.world_objects_list)
                path_partner_to_bed = game_utils.find_path_to_target(partner, partner_bed_dest_interaction, pf_grid, game_state.world_objects_list)

                if path_npc_to_bed and path_partner_to_bed:
                    npc.current_action = "going_to_bed_together_leader"
                    npc.target_destination = npc_bed_dest_interaction
                    npc.current_path = path_npc_to_bed
                    npc.bed_slot_index = chosen_slot_npc
                    # npc.target_partner rimane lo stesso

                    partner.current_action = "going_to_bed_together_follower"
                    partner.target_destination = partner_bed_dest_interaction
                    partner.current_path = path_partner_to_bed
                    partner.bed_slot_index = chosen_slot_partner
                    # partner.target_partner è già npc
                    partner.is_interacting = True # Il partner è ora impegnato in questa sequenza

                    if DEBUG_AI: print(f"AI: {npc.name} (leader) and {partner.name} (follower) going to bed together.")
                else:
                    if DEBUG_AI: print(f"AI WARN: {npc.name} or {partner.name} could not find path to bed for intimacy after meeting.")
                    npc.current_action = "idle"; partner.current_action = "idle"
                    npc.target_partner = None; partner.target_partner = None # Resetta
            else:
                if DEBUG_AI: print(f"AI INFO: {npc.name} and {partner.name} met, but no two free bed slots available.")
                npc.current_action = "idle"; partner.current_action = "idle"
                npc.target_partner = None; partner.target_partner = None
        else:
            if DEBUG_AI: print(f"AI: {npc.name} arrived, but partner {partner.name if partner else 'None'} was not waiting or too far. Returning to idle.")
            if partner and partner.target_partner == npc: # Se il partner stava aspettando questo NPC
                partner.current_action = "idle" # Il partner smette di aspettare
                partner.target_partner = None
            npc.current_action = "idle"
            npc.target_partner = None

        npc.current_path = None
        npc.target_destination = None
        return False # Azione gestita


    elif action_at_arrival == "going_to_bed_together_leader" or action_at_arrival == "going_to_bed_together_follower":
        if DEBUG_AI: print(f"AI: {npc.name} ({action_at_arrival}) arrived at bed destination for intimacy.")
        # Entrambi dovrebbero essere arrivati o quasi
        # Qui si verifica se entrambi sono a letto e pronti per l'azione "cuddling_in_bed"

        # Occupa lo slot del letto per questo NPC
        slot_occupied_successfully = game_utils.occupy_bed_slot_for_character(game_state, npc, npc.bed_slot_index)

        if slot_occupied_successfully:
            npc.is_on_bed = True
            # Posiziona l'NPC sulla sleeping_pos
            sleep_pos = game_state.bed_slot_1_sleep_pos_world if npc.bed_slot_index == 0 else game_state.bed_slot_2_sleep_pos_world
            if sleep_pos: npc.rect.center = sleep_pos; npc.x, npc.y = sleep_pos

            partner = npc.target_partner
            # Se anche il partner è arrivato e sul letto nello slot corretto
            if partner and partner.is_on_bed and partner.bed_slot_index is not None and \
               partner.current_action in ["going_to_bed_together_follower", "going_to_bed_together_leader", "cuddling_in_bed"] and \
               partner.target_partner == npc:
                if DEBUG_AI: print(f"AI: Both {npc.name} and {partner.name} are in bed. Starting cuddling.")
                npc.current_action = "cuddling_in_bed"
                partner.current_action = "cuddling_in_bed" # Sincronizza azione del partner
                npc.time_in_current_action = 0.0
                partner.time_in_current_action = 0.0
                # Logica per farli guardare l'un l'altro
                if npc.bed_slot_index == 0: # Assumendo slot 0 a sx, slot 1 a dx
                    npc.current_facing_direction = "right"
                    partner.current_facing_direction = "left"
                else:
                    npc.current_facing_direction = "left"
                    partner.current_facing_direction = "right"
            elif partner and not partner.is_on_bed and partner.current_action in ["going_to_bed_together_follower", "going_to_bed_together_leader"]:
                if DEBUG_AI: print(f"AI: {npc.name} is in bed, waiting for {partner.name} to get in bed.")
                # L'NPC attende che il partner arrivi/entri, potrebbe rimanere in questo stato o avere un timeout
                npc.current_action = "waiting_in_bed_for_partner" # Nuovo stato possibile
            else: # Partner non è a letto o non è più in questa interazione
                if DEBUG_AI: print(f"AI WARN: {npc.name} is in bed, but partner {partner.name if partner else 'None'} is not ready. {npc.name} goes idle.")
                game_utils.free_bed_slot_for_character(game_state, npc) # Libera lo slot
                npc.current_action = "idle"
                npc.is_on_bed = False
                npc.target_partner = None
        else:
            if DEBUG_AI: print(f"AI WARN: {npc.name} arrived at bed for intimacy, but failed to occupy slot {npc.bed_slot_index}.")
            npc.current_action = "idle"

        npc.current_path = None
        npc.target_destination = None
        return False
    # ... (altre azioni come prima) ...
    else:
        # ... (codice di fallback come prima) ...
        if npc.current_action != "idle" and DEBUG_AI:
            print(f"AI: {npc.name} arrived for unhandled/completed action '{action_at_arrival}'. Setting to idle.")
        npc.current_action = "idle"

    npc.current_path = None
    npc.target_destination = None
    if action_at_arrival != "seeking_partner_for_intimacy" and \
        action_at_arrival != "going_to_bed_together_leader" and \
        action_at_arrival != "going_to_bed_together_follower":
        npc.target_partner = None # Resetta solo se non è parte di una sequenza di intimità in corso
    return False


def _make_idle_decision(
    npc: Character, 
    all_npcs: list[Character], 
    pf_grid, 
    game_state: GameState
):
    # Energia / Sonno
    if npc.energy.get_value() < getattr(config, 'NPC_ENERGY_THRESHOLD_TO_SEEK_BED', config.NPC_ENERGY_THRESHOLD + 10):
        bed_interaction_pos = None
        chosen_slot_index = -1

        if game_state.bed_slot_1_interaction_pos_world and not game_state.bed_slot_1_occupied_by:
            bed_interaction_pos = game_state.bed_slot_1_interaction_pos_world
            chosen_slot_index = 0
        elif game_state.bed_slot_2_interaction_pos_world and not game_state.bed_slot_2_occupied_by:
            bed_interaction_pos = game_state.bed_slot_2_interaction_pos_world
            chosen_slot_index = 1

        if bed_interaction_pos:
            bed_interaction_pos_int = (int(bed_interaction_pos[0]), int(bed_interaction_pos[1]))
            interaction_distance_bed = getattr(config, 'NPC_BED_REACH_DISTANCE', config.TILE_SIZE * 0.75)

            if game_utils.is_close_to_point(npc.rect.center, bed_interaction_pos_int, interaction_distance_bed):
                can_use_bed_now = False
                if chosen_slot_index == 0 and not game_state.bed_slot_1_occupied_by:
                    game_state.bed_slot_1_occupied_by = npc.uuid
                    can_use_bed_now = True
                elif chosen_slot_index == 1 and not game_state.bed_slot_2_occupied_by:
                    game_state.bed_slot_2_occupied_by = npc.uuid
                    can_use_bed_now = True

                if can_use_bed_now:
                    npc.bed_object_id = "main_bed"
                    npc.bed_slot_index = chosen_slot_index
                    npc.current_action = "resting_on_bed"
                    npc.is_on_bed = True
                    npc.is_interacting = True
                    sleep_pos_world = game_state.bed_slot_1_sleep_pos_world if chosen_slot_index == 0 else game_state.bed_slot_2_sleep_pos_world
                    if sleep_pos_world: npc.rect.center = sleep_pos_world
                    if DEBUG_AI: print(f"AI Decision: {npc.name} is tired and already near bed. Got into slot {chosen_slot_index}.")
                    return
            start_grid_pos_debug = game_utils.world_to_grid(npc.rect.centerx, npc.rect.centery)
            target_grid_pos_debug = game_utils.world_to_grid(bed_interaction_pos_int[0], bed_interaction_pos_int[1])
            if DEBUG_AI: print(f"AI DEBUG: {npc.name} attempting path to bed from grid {start_grid_pos_debug} to grid {target_grid_pos_debug} (world: {bed_interaction_pos_int})")
            path_to_bed = game_utils.find_path_to_target(npc, bed_interaction_pos_int, pf_grid, game_state.world_objects_list)
            if path_to_bed:
                if DEBUG_AI: print(f"AI Decision: {npc.name} is tired. Path found to bed slot {chosen_slot_index} at {bed_interaction_pos_int}.")
                npc.current_action = "seeking_bed"
                npc.target_destination = bed_interaction_pos_int
                npc.current_path = path_to_bed # Assicurati di usare current_path
                npc.bed_slot_index = chosen_slot_index
                return
            elif DEBUG_AI: print(f"AI WARN: {npc.name} No path to bed slot {chosen_slot_index} at {bed_interaction_pos_int}.")
        elif DEBUG_AI: print(f"AI INFO: {npc.name} is tired, but no free bed slot found or bed interaction positions undefined.")

    # Decisioni per Socialità e Intimità
    # MODIFICATO: npc.needs['social'] -> npc.social
    if npc.social.get_value() < config.NPC_SOCIAL_THRESHOLD:
        if DEBUG_AI: print(f"AI Decision: {npc.name} needs social. Starting 'phoning'.")
        npc.current_action = "phoning"
        npc.is_interacting = True
        return

    # Intimità - ora con la nuova sequenza
    if npc.pending_intimacy_requester and npc.current_action == "idle":
        partner_candidate = npc.pending_intimacy_requester
        # Qui l'NPC (npc) è il DESTINATARIO. Decide se accettare.
        # Per semplicità, accettiamo sempre se idle. Potresti aggiungere più logica.
        if DEBUG_AI: print(f"AI Decision: {npc.name} received intimacy request from {partner_candidate.name}. Accepting and waiting.")
        npc.current_action = "accepting_intimacy_and_waiting"
        npc.target_partner = partner_candidate # Ricorda chi è il richiedente
        npc.target_destination = None # Smetti di muoverti
        npc.current_path = None
        npc.is_interacting = True # È in un'interazione di attesa
        npc.pending_intimacy_requester = None # Richiesta gestita
        return # Decisione presa

    # Logica per l'NPC che VUOLE INIZIARE l'intimità
    if npc.intimacy.get_value() > config.NPC_INTIMACY_THRESHOLD and \
       len(all_npcs) > 1 and npc.current_action == "idle":
        if DEBUG_AI: print(f"AI Decision: {npc.name} needs intimacy. Looking for an idle partner.")

        potential_partners = [p for p in all_npcs if p.uuid != npc.uuid and p.current_action == "idle" and p.pending_intimacy_requester is None]
        if potential_partners:
            chosen_partner = random.choice(potential_partners)
            npc.target_partner = chosen_partner

            # "Invia" la richiesta al partner scelto
            chosen_partner.pending_intimacy_requester = npc # L'NPC corrente è il richiedente
            if DEBUG_AI: print(f"AI Decision: {npc.name} sent intimacy request to {chosen_partner.name}.")

            interaction_offset_x = random.choice([-config.TILE_SIZE, config.TILE_SIZE])
            target_pos_world_for_meeting = (chosen_partner.rect.centerx + interaction_offset_x, chosen_partner.rect.centery)
            path_to_meet_partner = game_utils.find_path_to_target(npc, target_pos_world_for_meeting, pf_grid, game_state.world_objects_list)

            if path_to_meet_partner:
                npc.current_action = "seeking_partner_for_intimacy" # L'iniziatore si muove
                npc.target_destination = target_pos_world_for_meeting
                npc.current_path = path_to_meet_partner
                if DEBUG_AI: print(f"AI Decision: {npc.name} pathing to meet {chosen_partner.name} (who should now be waiting).")
                return
            else:
                if DEBUG_AI: print(f"AI WARN: {npc.name} could not find path to meet partner {chosen_partner.name}. Resetting request.")
                chosen_partner.pending_intimacy_requester = None # Annulla la richiesta se non posso raggiungerlo
                npc.target_partner = None
        else:
            if DEBUG_AI: print(f"AI INFO: {npc.name} needs intimacy, but no idle partners (not already requested) available.")
    # ... (logica per Socialità e Wandering come prima, ma assicurati che ritornino se prendono una decisione) ...
    if npc.social.get_value() < config.NPC_SOCIAL_THRESHOLD and npc.current_action == "idle":
        if DEBUG_AI: print(f"AI Decision: {npc.name} needs social. Starting 'phoning'.")
        npc.current_action = "phoning"
        npc.is_interacting = True
        npc.time_in_current_action = 0.0 # Inizia timer
        return

    # Fallback a wandering
    if random.random() < getattr(config, 'NPC_IDLE_WANDER_CHANCE', 0.02):
        target_wander_pos = game_utils.get_random_walkable_tile_in_radius(
            npc.rect.center, pf_grid,
            min_dist_tiles=config.NPC_WANDER_MIN_DIST_TILES,
            max_dist_tiles=config.NPC_WANDER_MAX_DIST_TILES,
            world_obstacles=game_state.world_objects_list # Questo non è usato da get_random_walkable_tile_in_radius
        )
        if target_wander_pos:
            path_to_wander = game_utils.find_path_to_target(npc, target_wander_pos, pf_grid, game_state.world_objects_list)
            if path_to_wander:
                if DEBUG_AI: print(f"AI Decision: {npc.name} decided to wander to {target_wander_pos}.")
                npc.current_action = "wandering"
                npc.target_destination = target_wander_pos
                npc.current_path = path_to_wander # Assicurati di usare current_path
                return
    if npc.current_action == "idle":
        pass # Già idle, non fare nulla o implementa un vero "idle" comportamento se diverso da "nessuna azione"


# --- Funzione Principale dell'IA (Modificata per solo Riposo e bisogni base Social/Intimacy) ---
def run_npc_ai_logic(
    npc: Character,
    all_npcs: list[Character],
    game_hours_tick: float, # Questo è il nome corretto del parametro ricevuto
    pf_grid,
    game_state: GameState
) -> bool:
    """
    Orchestra la logica IA per un NPC, focalizzandosi sul riposo e bisogni base.
    Restituisce sempre False perché la gestione del cibo è stata rimossa.
    """
    # food_eaten_this_tick = False # Non più necessario

    # Recupera le informazioni necessarie da game_state o config se non passate direttamente
    # (Queste erano prima parametri, ora le prendiamo da game_state o config se necessario nelle helper)
    food_is_visible = game_state.food_visible if hasattr(game_state, 'food_visible') else False
    # food_coords = config.FOOD_POS # O da game_state se dinamico
    # toilet_obj_rect = game_state.toilet_rect_instance if hasattr(game_state, 'toilet_rect_instance') else None


    # Sezione 0: Gestione Azioni Bloccanti/Continue (es. dormire, telefonare)
    continuous_action_result = _handle_continuous_actions(npc, game_state, game_hours_tick)
    if continuous_action_result is not None:
        return False

    # Sezione 1: Gestione "Seeking Partner" (se implementata e attiva)
    # partner_seeking_result = _handle_partner_seeking(npc, all_npcs, game_state)
    # if partner_seeking_result is not None:
    #     return False

    # Sezione 2: Interruzione Azioni A* (es. pathfinding per bisogni critici)
    # action_was_interrupted = _check_and_handle_interruptions(npc, food_is_visible, game_state)
    # if action_was_interrupted:
    #     return False 

    # Sezione 3: Gestione Arrivo a Destinazione A*
    # Se l'NPC era in movimento (aveva un path o un target_destination) e ora non più,
    # significa che è arrivato o il path è stato cancellato.
    # Escludi azioni che hanno la loro gestione continua (come quelle in _handle_continuous_actions)
    is_currently_pathfinding_or_has_target = bool(npc.current_path or npc.target_destination) # <--- MODIFICATO
    non_pathfinding_continuous_actions = ["resting_on_bed", "phoning", "using_toilet",
                                          "romantic_interaction_action", "affectionate_interaction_action"]

    if not is_currently_pathfinding_or_has_target and \
       npc.current_action not in ["idle"] and \
       npc.current_action not in non_pathfinding_continuous_actions:

        # Modifica la chiamata per passare pf_grid
        arrival_result = _handle_arrival_at_destination(npc, game_state, pf_grid) # <--- PASSATO pf_grid
        if arrival_result is not None:
             return False

    # Sezione 4: Logica Decisionale (se l'NPC è "idle")
    if npc.current_action == "idle":
        _make_idle_decision(
            npc,
            all_npcs,
            pf_grid,
            game_state
        )
    return False
