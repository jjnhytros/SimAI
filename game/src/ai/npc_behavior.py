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
    from game import game_utils # Potrebbe servire per find_path_to_target, is_close_to_point, ecc.
    # Se GameState è stato spostato in src/modules/game_state_module.py
    from game.src.modules.game_state_module import GameState 
except ImportError as e:
    print(f"CRITICAL ERROR (npc_behavior.py): Could not import dependencies: {e}")
    sys.exit()

DEBUG_AI = getattr(config, 'DEBUG_AI_ACTIVE', False)

# --- DEFINIZIONI DELLE FUNZIONI HELPER (SOLO PER RIPOSO) ---

def _handle_continuous_actions(npc: Character, game_state: GameState) -> Optional[bool]:
    """Gestisce azioni continue, ora principalmente 'resting_on_bed'."""
    if npc.current_action == "resting_on_bed":
        # L'NPC sta dormendo. Controlla se deve svegliarsi.
        if npc.needs['energy'].get_value() >= npc.needs['energy'].max_value: # Svegliati se energia è piena
            # Logica per far "uscire" l'NPC dal letto
            # Questo include liberare lo slot del letto in GameState e aggiornare lo stato dell'NPC
            if npc.bed_object_id is not None and npc.bed_slot_index != -1:
                # Assumendo che game_state abbia una logica per liberare lo slot
                # Esempio: game_state.free_bed_slot(npc.bed_object_id, npc.bed_slot_index)
                if DEBUG_AI: print(f"AI: {npc.name} is freeing bed slot {npc.bed_slot_index} (ID: {npc.bed_object_id}).")
            
            npc.is_on_bed = False 
            npc.bed_object_id = None
            npc.bed_slot_index = -1
            npc.current_action = "idle"
            npc.is_interacting = False # Termina l'interazione "sonno"
            if DEBUG_AI: print(f"AI: {npc.name} woke up from bed. Energy: {npc.needs['energy'].get_value()}.")
            return False # Azione "resting_on_bed" terminata
        else:
            if DEBUG_AI: print(f"AI: {npc.name} is still resting_on_bed. Energy: {npc.needs['energy'].get_value()}.")
            return True # Azione "resting_on_bed" ancora in corso, blocca altre decisioni
            
    # Altre azioni continue (phoning, partner_seeking, etc.) sono state rimosse per focus sul riposo.
    # Se vuoi reintrodurle, la loro logica andrebbe qui.
    return None # Nessuna azione continua (rilevante per il riposo) ha gestito il tick o era attiva.

# _handle_partner_seeking, _check_and_handle_interruptions (per altri bisogni) sono commentate/rimosse

def _handle_arrival_at_destination(
    npc: Character, 
    game_state: GameState
    # Parametri per cibo, bagno, ecc. rimossi
) -> Optional[bool]:
    """Gestisce l'arrivo a destinazione, ora principalmente per 'seeking_bed'."""
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

    # Altre azioni di arrivo (cibo, bagno) sono state commentate.
    # else if action_at_arrival == "seeking_food": ...
    # else if action_at_arrival == "seeking_toilet": ...
        
    else:
        if npc.current_action != "idle" and DEBUG_AI:
            print(f"AI: {npc.name} arrived for unhandled/completed action '{action_at_arrival}'. Setting to idle.")
        npc.current_action = "idle" 

    npc.path = None 
    npc.target_destination = None
    return False # Default, nessun cibo mangiato


def _make_idle_decision(
    npc: Character, 
    all_npcs: list[Character], 
    pf_grid, # Griglia di pathfinding
    # food_is_visible, food_coords, toilet_obj_rect rimossi
    game_state: GameState
    # fun_obj_type_to_seek e shower_obj_type_to_seek rimossi
):
    # Ora l'unica decisione basata su bisogno è per l'Energia.
    
    # Energia / Sonno
    # Usiamo una soglia leggermente più alta per decidere di andare a letto rispetto alla soglia critica per le interruzioni.
    if npc.needs['energy'].get_value() < getattr(config, 'NPC_ENERGY_THRESHOLD_TO_SEEK_BED', config.NPC_ENERGY_THRESHOLD + 10):
        bed_interaction_pos = None
        chosen_slot_index = -1

        # Prova a trovare uno slot libero
        if game_state.bed_slot_1_interaction_pos_world and not game_state.bed_slot_1_occupied_by:
            bed_interaction_pos = game_state.bed_slot_1_interaction_pos_world
            chosen_slot_index = 0
        elif game_state.bed_slot_2_interaction_pos_world and not game_state.bed_slot_2_occupied_by:
            bed_interaction_pos = game_state.bed_slot_2_interaction_pos_world
            chosen_slot_index = 1
        
        if bed_interaction_pos:
            # Assicurati che bed_interaction_pos sia una tupla di interi per il pathfinding
            bed_interaction_pos_int = (int(bed_interaction_pos[0]), int(bed_interaction_pos[1]))
            
            # Verifica se l'NPC è già abbastanza vicino per evitare pathfinding inutile
            interaction_distance_bed = getattr(config, 'NPC_BED_REACH_DISTANCE', config.TILE_SIZE * 0.75)
            if game_utils.is_close_to_point(npc.rect.center, bed_interaction_pos_int, interaction_distance_bed):
                # Già vicino, prova ad occupare lo slot e andare a letto direttamente
                can_use_bed_now = False
                if chosen_slot_index == 0 and not game_state.bed_slot_1_occupied_by:
                    game_state.bed_slot_1_occupied_by = npc.uuid
                    can_use_bed_now = True
                elif chosen_slot_index == 1 and not game_state.bed_slot_2_occupied_by:
                    game_state.bed_slot_2_occupied_by = npc.uuid
                    can_use_bed_now = True
                
                if can_use_bed_now:
                    npc.bed_object_id = "main_bed" # ID generico del letto
                    npc.bed_slot_index = chosen_slot_index
                    npc.current_action = "resting_on_bed" 
                    npc.is_on_bed = True 
                    npc.is_interacting = True
                    sleep_pos_world = game_state.bed_slot_1_sleep_pos_world if chosen_slot_index == 0 else game_state.bed_slot_2_sleep_pos_world
                    if sleep_pos_world: npc.rect.center = sleep_pos_world
                    if DEBUG_AI: print(f"AI Decision: {npc.name} is tired and already near bed. Got into slot {chosen_slot_index}.")
                    return
            
            # Se non è abbastanza vicino, calcola il percorso
            path_to_bed = game_utils.find_path_to_target(npc, bed_interaction_pos_int, pf_grid, game_state.world_objects_list)
            if path_to_bed:
                if DEBUG_AI: print(f"AI Decision: {npc.name} is tired. Path found to bed slot {chosen_slot_index} at {bed_interaction_pos_int}.")
                npc.current_action = "seeking_bed"
                npc.target_destination = bed_interaction_pos_int
                npc.path = path_to_bed
                npc.bed_slot_index = chosen_slot_index # Memorizza lo slot a cui sta andando
                # npc.target_object_id = id_del_letto_se_hai_oggetti_letto # Se hai oggetti letto con ID
                return
            elif DEBUG_AI: print(f"AI WARN: {npc.name} No path to bed slot {chosen_slot_index} at {bed_interaction_pos_int}.")
        elif DEBUG_AI: print(f"AI INFO: {npc.name} is tired, but no free bed slot found or bed interaction positions undefined.")

    # Decisioni per Socialità e Intimità (se vuoi mantenerle)
    if npc.needs['social'].get_value() < config.NPC_SOCIAL_THRESHOLD:
        if DEBUG_AI: print(f"AI Decision: {npc.name} needs social. Starting 'phoning'.")
        npc.current_action = "phoning"
        npc.is_interacting = True 
        # npc.interaction_timer = durata_telefonata_da_config
        return

    if npc.needs['intimacy'].get_value() < config.NPC_INTIMACY_THRESHOLD and len(all_npcs) > 1:
        if DEBUG_AI: print(f"AI Decision: {npc.name} needs intimacy. Starting 'seeking_partner'.")
        npc.current_action = "seeking_partner"
        # La logica per trovare il partner e avviare il pathfinding potrebbe essere qui
        # o in Character.update quando l'azione è "seeking_partner".
        # Esempio:
        # partner = game_utils.find_suitable_partner(npc, all_npcs)
        # if partner:
        #     target_pos = partner.rect.center # O un punto di interazione vicino al partner
        #     path_to_partner = game_utils.find_path_to_target(npc, target_pos, pf_grid, game_state.world_objects_list)
        #     if path_to_partner:
        #         npc.target_destination = target_pos
        #         npc.path = path_to_partner
        #         npc.target_object_id = partner.uuid # Salva l'ID del partner target
        return

    # Altri bisogni (fame, vescica, fun, hygiene) sono commentati.
    # if npc.needs['hunger'].get_value() < config.NPC_HUNGER_THRESHOLD: ...
    # if npc.needs['bladder'].get_value() < config.NPC_BLADDER_THRESHOLD and toilet_obj_rect: ...

    # Fallback a wandering
    if random.random() < getattr(config, 'NPC_IDLE_WANDER_CHANCE', 0.05):
        target_wander_pos = game_utils.get_random_walkable_tile_in_radius(
            npc.rect.center, pf_grid, 
            min_dist_tiles=config.NPC_WANDER_MIN_DIST_TILES,
            max_dist_tiles=config.NPC_WANDER_MAX_DIST_TILES,
            world_obstacles=game_state.world_objects_list
        )
        if target_wander_pos:
            path_to_wander = game_utils.find_path_to_target(npc, target_wander_pos, pf_grid, game_state.world_objects_list)
            if path_to_wander:
                if DEBUG_AI: print(f"AI Decision: {npc.name} decided to wander to {target_wander_pos}.")
                npc.current_action = "wandering"
                npc.target_destination = target_wander_pos
                npc.path = path_to_wander
                return
            # else: if DEBUG_AI: print(f"AI WARN: {npc.name} No path for wandering to {target_wander_pos}")
    
    # Se nessuna decisione è stata presa, rimane idle (o l'azione corrente viene mantenuta se non è idle)
    if npc.current_action == "idle": # Assicurati che non sovrascriva un'azione impostata da una decisione precedente in questo tick
        pass # Già idle, non fare nulla o implementa un vero "idle" comportamento se diverso da "nessuna azione"


# --- Funzione Principale dell'IA (Modificata per solo Riposo e bisogni base Social/Intimacy) ---
def run_npc_ai_logic(
    npc: Character,                   
    all_npcs: list[Character],      
    game_hours_tick: float, # Non più usato direttamente qui, Character.update_needs usa il tempo globale      
    pf_grid, # Istanza della griglia di pathfinding           
    # food_is_visible, food_coords, toilet_obj_rect, fun_obj_type, shower_obj_type rimossi dalla firma
    game_state: GameState # Ora passiamo l'intera istanza di GameState (o 'GameState' per type hint)
) -> bool: # Restituisce sempre False dato che il cibo è stato rimosso          
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
    continuous_action_result = _handle_continuous_actions(npc, game_state)
    if continuous_action_result is not None: # True (azione continua) o False (azione terminata)
        return False # Nessun cibo mangiato, decisione presa/azione in corso

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
    is_currently_pathfinding_or_has_target = bool(npc.path or npc.target_destination)
    non_pathfinding_continuous_actions = ["resting_on_bed", "phoning", "using_toilet", 
                                          "romantic_interaction_action", "affectionate_interaction_action"]
                                          # "seeking_partner" potrebbe iniziare un path, quindi va valutato

    if not is_currently_pathfinding_or_has_target and \
       npc.current_action not in ["idle"] and \
       npc.current_action not in non_pathfinding_continuous_actions:
        
        # L'NPC è arrivato a destinazione per un'azione di "seeking_X"
        # Passiamo solo i parametri necessari ora (nessuno per fun/hygiene/food/toilet)
        arrival_result = _handle_arrival_at_destination(npc, game_state)
        if arrival_result is not None: 
             # _handle_arrival_at_destination ora restituisce False perché non gestisce il cibo.
             return False

    # Sezione 4: Logica Decisionale (se l'NPC è "idle")
    if npc.current_action == "idle":
        # Passiamo solo i parametri necessari
        _make_idle_decision( 
            npc, all_npcs, pf_grid, 
            food_is_visible, # Anche se non usata, la passiamo per coerenza se la riattivi
            config.FOOD_POS, # Come sopra
            game_state, 
            game_state.toilet_rect_instance if hasattr(game_state, 'toilet_rect_instance') else None
            # fun_obj_type e shower_obj_type rimossi
        )

    return False # Nessun cibo è gestito o mangiato in questa versione semplificata