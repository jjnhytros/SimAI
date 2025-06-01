# simai.py
# File principale di avvio per SimAI - Simulazione Continua del Mondo

import random 
import time 
from typing import List, Optional, Tuple, Set, Dict, Any 

# Importazioni dal progetto core
from core import settings
from core.simulation import Simulation
from core.character import Character 
from core.modules.actions import ( 
    BaseAction, EatAction, SleepAction, UseBathroomAction, HaveFunAction, SocializeAction, EngageIntimacyAction
)
from core.enums import ( 
    Gender, Interest, LifeStage, RelationshipStatus, AspirationType, 
    SchoolLevel, NeedType, EventType, LocationType, FunActivityType, SocialInteractionType, RelationshipType, ObjectType
)
from core.modules.time_manager import TimeManager
from core.world.game_object import GameObject # Assicurati che sia importato
from core.world.location import Location     # Assicurati che sia importato


# --- FUNZIONI HELPER ---

def set_need_to_value(npc: Character, need_type: NeedType, target_value: float, suppress_log: bool = False):
    """Imposta artificialmente un bisogno di un NPC a un valore specifico."""
    current_value = npc.get_need_value(need_type)
    if current_value is not None:
        amount_to_change = target_value - current_value 
        npc.change_need_value(need_type, amount_to_change, is_decay_event=False) 
        
        if not suppress_log and settings.DEBUG_MODE:
            new_val_check = npc.get_need_value(need_type)
            need_display_name = need_type.display_name_it() if hasattr(need_type, 'display_name_it') else need_type.name
            print(f"    [Test Helper - Need Set] {npc.name} - {need_display_name}: {current_value:.2f} -> {new_val_check:.2f} (Target: {target_value:.1f}, AppliedChange: {amount_to_change:.2f})")
    elif settings.DEBUG_MODE:
        print(f"    [Test Helper WARN - {npc.name}] Impossibile trovare/impostare il bisogno {need_type.name}.")

def print_npc_needs_summary(npc: Character, primary_needs_order: List[NeedType]):
    """Stampa una lista formattata dei bisogni principali specificati per l'HUD."""
    if hasattr(npc, 'needs') and npc.needs:
        needs_to_print_list = []
        for need_type in primary_needs_order:
            need_obj = npc.needs.get(need_type)
            if need_obj:
                val = need_obj.get_value()
                bar_length = 10 
                filled_length = int(bar_length * val / settings.NEED_MAX_VALUE)
                bar = '█' * filled_length + '-' * (bar_length - filled_length)
                status_tag = ""
                critical_thresh = getattr(settings, "NEED_CRITICAL_THRESHOLD", 15.0)
                low_thresh = getattr(settings, "NEED_LOW_THRESHOLD", 30.0)
                if val <= critical_thresh: status_tag = "[!!]"
                elif val <= low_thresh: status_tag = "[!]"
                needs_to_print_list.append(f"{need_obj.display_name():<12}: [{bar}] {val:>5.1f} {status_tag}")
            else:
                need_display_name = need_type.display_name_it() if hasattr(need_type, 'display_name_it') else need_type.name
                needs_to_print_list.append(f"{need_display_name:<12}: [----------] N/A   ")
        
        col1_end_index = (len(needs_to_print_list) + 1) // 2
        col1 = needs_to_print_list[:col1_end_index]
        col2 = needs_to_print_list[col1_end_index:]
        max_lines = max(len(col1), len(col2))
        for i in range(max_lines):
            line_str1 = col1[i] if i < len(col1) else " " * 35 
            line_str2 = col2[i] if i < len(col2) else ""
            print(f"    {line_str1:<35} | {line_str2}")
    else:
        print(f"    (Bisogni non disponibili per {npc.name})")

def render_ascii_hud(simulation: Simulation, monitored_npc_id: Optional[str] = None):
    """Stampa un semplice HUD testuale con mappa della casa, stato NPC e bisogni principali."""
    print("\n" + "="*80)
    print(f"|| SimAI HUD - Ora: {simulation.time_manager.get_formatted_datetime_string()} (Tick Mondo: {simulation.current_tick}) ||")
    print("="*80)

    print("Mappa Casa (S=Soggiorno, C=Cucina, B=Bagno, L=Letto):")
    map_layout = { 
        "max_casa_soggiorno": {"char": "🛋️ S", "row": 0, "col": 0},
        "max_casa_cucina":    {"char": "🍳 C", "row": 0, "col": 1},
        "max_casa_camera":    {"char": "🛏️ L", "row": 1, "col": 0},
        "max_casa_bagno":     {"char": "🚽 B", "row": 1, "col": 1}
    }
    grid_rows = 2; grid_cols = 2
    display_grid = [[" " * 5 for _ in range(grid_cols)] for _ in range(grid_rows)]
    for loc_id, data in map_layout.items():
        if data["row"] < grid_rows and data["col"] < grid_cols:
            display_grid[data["row"]][data["col"]] = f"{data['char']:<5}"
    for npc_id_map, npc_map in simulation.npcs.items():
        if npc_map.current_location_id and npc_map.current_location_id in map_layout:
            loc_data = map_layout[npc_map.current_location_id]
            current_cell_content = display_grid[loc_data["row"]][loc_data["col"]].strip()
            initial = npc_map.name[0] if npc_map.name else "?"
            if len(current_cell_content) < 3: 
                display_grid[loc_data["row"]][loc_data["col"]] = f"{current_cell_content}{initial} ".ljust(5)
            elif len(current_cell_content) < 5 :
                 display_grid[loc_data["row"]][loc_data["col"]] = f"{current_cell_content[:4]}{initial}"
    print("+-------+-------+")
    for r_idx in range(grid_rows): print(f"| {' | '.join(display_grid[r_idx])} |"); print("+-------+-------+")
    print("-" * 30) 

    if not monitored_npc_id and simulation.npcs:
        monitored_npc_id = list(simulation.npcs.keys())[0]
    npc_to_display = simulation.get_npc_by_id(monitored_npc_id)

    if npc_to_display:
        print(f"--- Stato di {npc_to_display.name} (ID: {npc_to_display.npc_id}) ---")
        current_loc = npc_to_display.get_current_location(simulation)
        loc_name = current_loc.name if current_loc else "Nessuna Locazione"
        loc_id_str = f"({npc_to_display.current_location_id})" if npc_to_display.current_location_id else ""
        print(f"  Locazione: {loc_name} {loc_id_str}")
        action_name = npc_to_display.current_action.action_type_name if npc_to_display.current_action else "Nessuna"
        action_progress = f"({npc_to_display.current_action.get_progress_percentage():.0%})" if npc_to_display.current_action and npc_to_display.current_action.is_started else ""
        print(f"  Azione Corrente: {action_name} {action_progress} (Occupato: {npc_to_display.is_busy}, Coda: {len(npc_to_display.action_queue)})")
        print("  Bisogni Principali:")
        primary_needs_to_display = [ 
            NeedType.ENERGY, NeedType.HUNGER, NeedType.THIRST, NeedType.HYGIENE,
            NeedType.FUN, NeedType.SOCIAL, NeedType.BLADDER, NeedType.INTIMACY
        ]
        print_npc_needs_summary(npc_to_display, primary_needs_to_display)
        if npc_to_display.relationships:
            print("  Relazioni (Top):")
            sorted_rels = sorted(npc_to_display.relationships.items(), key=lambda item: (item[1].score, item[0]), reverse=True)
            for target_id, rel_info in sorted_rels[:3]:
                target_npc = simulation.get_npc_by_id(target_id)
                if target_npc: print(f"    - {target_npc.name}: {rel_info.type.display_name_it()} ({rel_info.score})")
        print("---")
    else: print("Nessun NPC da monitorare o NPC non trovato.")
    print("="*80)


def setup_sim_world_and_npcs(sim: Simulation) -> Tuple[Character, Character]:
    """Crea locazioni, oggetti, e gli NPC Max ed Erika."""
    # _create_test_locations_and_objects() viene già chiamato in Simulation.__init__
    # e dovrebbe impostare sim.default_starting_location_id.
    # Se non lo fa, creiamo una locazione di emergenza.
    if not sim.default_starting_location_id:
        if sim.locations:
            sim.default_starting_location_id = list(sim.locations.keys())[0]
            print(f"  [SimAI Setup WARN] Usata prima locazione disponibile come default: '{sim.default_starting_location_id}'.")
        else: 
            default_loc = Location(location_id="default_start_loc", name="Stanza Iniziale di Emergenza", location_type=LocationType.UNKNOWN_LOCATION)
            tv_default = GameObject("tv_emergency", "TV di Emergenza", ObjectType.TV, provides_fun_activities=[FunActivityType.WATCH_TV])
            default_loc.add_object(tv_default); sim.add_location(default_loc); sim.world_objects[tv_default.object_id] = tv_default
            sim.default_starting_location_id = default_loc.location_id
            print(f"  [SimAI Setup WARN] Creata locazione di emergenza '{default_loc.name}' con una TV.")

    max_interests = {Interest.TECHNOLOGY, Interest.GAMING, Interest.TRAVEL}
    max_npc = Character(
        npc_id="max_01", name="Max", initial_gender=Gender.MALE,
        initial_age_days=22 * settings.DXY, initial_interests=max_interests,
        initial_sexually_attracted_to_genders={Gender.FEMALE},
        initial_aspiration=AspirationType.KNOWLEDGE_SEEKER,
        initial_location_id=sim.default_starting_location_id 
    )
    sim.add_npc(max_npc)

    erika_interests = {Interest.MUSIC_LISTENING, Interest.READING, Interest.TRAVEL}
    erika_npc = Character(
        npc_id="erika_01", name="Erika", initial_gender=Gender.FEMALE,
        initial_age_days=23 * settings.DXY, initial_interests=erika_interests,
        initial_sexually_attracted_to_genders={Gender.MALE, Gender.FEMALE},
        initial_aspiration=AspirationType.CREATIVE_VISIONARY,
        initial_location_id=sim.default_starting_location_id 
    )
    sim.add_npc(erika_npc)
    
    print(f"    [SimAI Setup] Imposto relazione iniziale: Max ed Erika -> {RelationshipType.ACQUAINTANCE.display_name_it()} (Score 20).")
    max_npc.update_relationship(erika_npc.npc_id, RelationshipType.ACQUAINTANCE, new_score=20)
    erika_npc.update_relationship(max_npc.npc_id, RelationshipType.ACQUAINTANCE, new_score=20)
    
    return max_npc, erika_npc


def run_simulation_loop():
    print("*****************************************************************")
    print("* AVVIO SIMULAZIONE CONTINUA DEL MONDO DI MAX & ERIKA         *")
    print("*****************************************************************")

    settings.DEBUG_MODE = True # Metti a False per un output HUD più pulito
    simulation_instance = Simulation()
    max_npc, erika_npc = setup_sim_world_and_npcs(simulation_instance)

    # Impostiamo i bisogni iniziali per stimolare azioni
    for npc in [max_npc, erika_npc]:
        for need_type_enum_val in NeedType: # Itera sui membri dell'Enum
            if npc.needs.get(need_type_enum_val):
                if need_type_enum_val == NeedType.INTIMACY:
                    set_need_to_value(npc, need_type_enum_val, random.randint(30, 50), suppress_log=True)
                elif need_type_enum_val == NeedType.THIRST: # Assumendo che THIRST esista
                    set_need_to_value(npc, need_type_enum_val, random.randint(40, 70), suppress_log=True)
                else:
                    set_need_to_value(npc, need_type_enum_val, random.randint(45, 75), suppress_log=True)
    
    set_need_to_value(max_npc, NeedType.FUN, 35, suppress_log=True) 
    set_need_to_value(erika_npc, NeedType.SOCIAL, 38, suppress_log=True) 

    ticks_per_step = settings.IXH // 12  # Avanza di 5 minuti di gioco
    total_game_hours_to_simulate = 24 # Simula per 1 giorno intero
    max_simulation_ticks = int(total_game_hours_to_simulate * settings.IXH)
    
    current_monitored_npc_id = max_npc.npc_id 

    for loop_idx in range(max_simulation_ticks // ticks_per_step):
        if simulation_instance.current_tick >= max_simulation_ticks: break

        render_ascii_hud(simulation_instance, current_monitored_npc_id)

        # Stampa log azioni conciso se DEBUG_MODE è False
        if not settings.DEBUG_MODE:
            print(f"Ora: {simulation_instance.time_manager.get_formatted_datetime_string()}")
            for npc_obj_log in simulation_instance.npcs.values():
                action_str_log = npc_obj_log.current_action.description if npc_obj_log.current_action else "Inattivo/a"
                loc_obj_log = npc_obj_log.get_current_location(simulation_instance)
                loc_name_log = loc_obj_log.name if loc_obj_log else "N/D"
                print(f"  {npc_obj_log.name} ({loc_name_log}): {action_str_log}")
            print("-" * 30)

        # Avanzamento e Interazione Utente
        print(f"\nTick Mondo: {simulation_instance.current_tick}. Premi Invio per {ticks_per_step} tick (o 'm'/'e' per cambiare NPC, 'q' per uscire)...")
        user_input = input()
        if user_input.lower() == 'q': break
        elif user_input.lower() == 'm': current_monitored_npc_id = max_npc.npc_id
        elif user_input.lower() == 'e': current_monitored_npc_id = erika_npc
        
        for _ in range(ticks_per_step):
            if simulation_instance.current_tick >= max_simulation_ticks: break
            simulation_instance._update_simulation_state()
    
    print("\n*****************************************************************")
    print("* FINE SIMULAZIONE CONTINUA                     *")
    print("*****************************************************************")
    print("Stato finale degli NPC:")
    render_ascii_hud(simulation_instance, max_npc.npc_id)
    render_ascii_hud(simulation_instance, erika_npc.npc_id)

if __name__ == "__main__":
    # --- Blocco di fallback per settings ---
    # Assicurati che queste costanti siano definite o che il tuo settings.py le fornisca.
    # Generali
    if not hasattr(settings, 'DXY'): settings.DXY = 28 * 24 # Ore al giorno * tick (minuti) per ora
    if not hasattr(settings, 'DEBUG_MODE'): settings.DEBUG_MODE = True 
    if not hasattr(settings, 'IXH'): settings.IXH = 60 # Tick (minuti) per ora
    if not hasattr(settings, 'MAX_NPC_ACTIVE_INTERESTS'): settings.MAX_NPC_ACTIVE_INTERESTS = 3
    
    # Life Stages
    if not hasattr(settings, 'LIFE_STAGE_AGE_THRESHOLDS_DAYS'):
        settings.LIFE_STAGE_AGE_THRESHOLDS_DAYS = { 
            "INFANCY": 0, "TODDLERHOOD": int(1.5*settings.DXY), "EARLY_CHILDHOOD": 3*settings.DXY, 
            "MIDDLE_CHILDHOOD": 7*settings.DXY, "ADOLESCENCE": 13*settings.DXY, 
            "EARLY_ADULTHOOD": 20*settings.DXY, "MIDDLE_ADULTHOOD": 40*settings.DXY, 
            "LATE_ADULTHOOD": 65*settings.DXY, "ELDERLY": 80*settings.DXY
        }
    
    # Bisogni
    if not hasattr(settings, 'NEED_MIN_VALUE'): settings.NEED_MIN_VALUE = 0.0
    if not hasattr(settings, 'NEED_MAX_VALUE'): settings.NEED_MAX_VALUE = 100.0
    if not hasattr(settings, 'NEED_DEFAULT_START_MIN'): settings.NEED_DEFAULT_START_MIN = 60.0 
    if not hasattr(settings, 'NEED_DEFAULT_START_MAX'): settings.NEED_DEFAULT_START_MAX = 95.0
    if not hasattr(settings, 'NEED_CRITICAL_THRESHOLD'): settings.NEED_CRITICAL_THRESHOLD = 20.0 
    if not hasattr(settings, 'NEED_LOW_THRESHOLD'): settings.NEED_LOW_THRESHOLD = 40.0 
    if not hasattr(settings, 'NEED_DECAY_RATES'): 
        settings.NEED_DECAY_RATES = {nt.name: -2.0 for nt in NeedType if nt.name != "THIRST"} # Decadimento più lento
        settings.NEED_DECAY_RATES.update({ 
            "HUNGER": -3.0, "ENERGY": -3.5, "BLADDER": -4.5, "HYGIENE": -1.5, 
            "FUN": -2.5, "SOCIAL": -2.5, "INTIMACY": -1.5, "THIRST": -3.5 # AGGIUNTO THIRST
        })
    
    # Intimità & Relazioni
    if not hasattr(settings, 'MIN_AGE_FOR_INTIMACY_DAYS'): 
        min_age_intimacy_years = getattr(settings, "MIN_AGE_FOR_INTIMACY_YEARS", 18)
        settings.MIN_AGE_FOR_INTIMACY_DAYS = min_age_intimacy_years * settings.DXY
    if not hasattr(settings, 'MIN_REL_SCORE_FOR_INTIMACY'): settings.MIN_REL_SCORE_FOR_INTIMACY = 40
    if not hasattr(settings, 'MIN_REL_SCORE_FOR_INTIMACY_PROPOSAL_ACCEPTANCE'): settings.MIN_REL_SCORE_FOR_INTIMACY_PROPOSAL_ACCEPTANCE = 30
    if not hasattr(settings, 'TARGET_INTIMACY_RECEPTIVENESS_THRESHOLD'): settings.TARGET_INTIMACY_RECEPTIVENESS_THRESHOLD = 60.0
    if not hasattr(settings, 'INTIMACY_PROPOSAL_COOLDOWN_TICKS'): settings.INTIMACY_PROPOSAL_COOLDOWN_TICKS = settings.IXH * 1 # 1 ora di gioco
    if not hasattr(settings, 'SCORE_THRESHOLD_FOR_FRIENDSHIP'): settings.SCORE_THRESHOLD_FOR_FRIENDSHIP = 25
    if not hasattr(settings, 'MIN_REL_SCORE_FOR_FLIRT'): settings.MIN_REL_SCORE_FOR_FLIRT = -5 # Si può flirtare anche se non si è amici
    if not hasattr(settings, 'FIRST_IMPRESSION_MIN_MOD'): settings.FIRST_IMPRESSION_MIN_MOD = -3
    if not hasattr(settings, 'FIRST_IMPRESSION_MAX_MOD'): settings.FIRST_IMPRESSION_MAX_MOD = 3
    
    # SoNet
    if not hasattr(settings, 'MAX_MATCHMAKING_SUGGESTIONS'): settings.MAX_MATCHMAKING_SUGGESTIONS = 3

    # Costanti di Default per Azioni (per il test in simai.py)
    # Assicurati che i nomi delle chiavi qui corrispondano a quelli cercati negli __init__ delle Azioni
    settings.EAT_ACTION_DURATION_TICKS = 20; settings.EAT_ACTION_HUNGER_GAIN = 70.0
    settings.SLEEP_ACTION_DEFAULT_HOURS = 7.0; settings.SLEEP_ACTION_DEFAULT_DURATION_TICKS = int(settings.SLEEP_ACTION_DEFAULT_HOURS * settings.IXH); settings.SLEEP_ACTION_ENERGY_GAIN_PER_HOUR = (100.0 / 7.0) 
    settings.USE_BATHROOM_DEFAULT_DURATION_TICKS = 7; settings.USE_BATHROOM_BLADDER_GAIN = 100.0; settings.USE_BATHROOM_HYGIENE_GAIN = 20.0
    settings.DEFAULT_HAVEFUNACTION_DURATION_TICKS = settings.IXH * 1; settings.DEFAULT_HAVEFUNACTION_FUN_GAIN = 40.0
    settings.SOCIAL_PROPOSE_INTIMACY_DURATION_TICKS = 10
    settings.DEFAULT_SOCIALIZE_CHAT_DURATION_TICKS = 25
    settings.SOCIAL_ACT_TELL_JOKE_DURATION_TICKS = 7
    settings.SOCIAL_ACT_DEEP_CONVERSATION_DURATION_TICKS = 45
    settings.SOCIAL_ACT_FLIRT_DURATION_TICKS = 15
    settings.DEFAULT_SOCIALIZE_SOCIAL_GAIN = 20.0
    settings.DEFAULT_RELATIONSHIP_SCORE_CHANGE_CHAT = 2
    settings.INTIMACY_ACTION_DURATION_TICKS = settings.IXH // 2 ; settings.INTIMACY_ACTION_INITIATOR_GAIN = 50.0; settings.INTIMACY_ACTION_TARGET_GAIN = 50.0; settings.INTIMACY_ACTION_REL_GAIN = 15.0
    settings.SOCIAL_TELL_JOKE_FUN_GAIN = 15.0
        
    run_simulation_loop() # Esegui la simulazione continua