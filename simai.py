# simai.py
"""
Punto di ingresso principale per la simulazione SimAI.
Gestisce l'inizializzazione e l'avvio della simulazione in modalità GUI o TUI.
"""
import sys
import os
import random
from typing import TYPE_CHECKING, List, Optional

from core.world.location import Location

# Aggiunge la directory principale al path per permettere import assoluti
# come 'from core.simulation import Simulation'
# path_to_scipy_parent_folder = '/usr/lib/python3/dist-packages' 
# if path_to_scipy_parent_folder not in sys.path:
#     sys.path.append(path_to_scipy_parent_folder)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# try:
#     from core import settings
#     from core.simulation import Simulation
#     from core.enums import (
#         Gender, TraitType, AspirationType, RelationshipType, SkillType, NeedType
#     )
#     from core.config import time_config
#     from core.factories.npc_factory import NPCFactory
#     from core.AI.ai_decision_maker import AIDecisionMaker
#     from core.world.ATHDateTime.ATHDateInterval import ATHDateInterval
#     from core.graphics.renderer import Renderer
    
#     # from core.tui.tui_manager import TuiManager # Decommenta quando crei la TUI
#     if TYPE_CHECKING:
#         from core.character import Character
        
# except ImportError as e:
#     print(f"Errore di importazione: {e}. Assicurati che i moduli siano nel PYTHONPATH.")
#     sys.exit(1)

from core import settings
from core.simulation import Simulation
from core.character import Character
from core.enums import * # O gli import specifici
from core.config import time_config
from core.factories.npc_factory import NPCFactory
from core.AI.ai_decision_maker import AIDecisionMaker
from core.world.ATHDateTime.ATHDateInterval import ATHDateInterval
from core.graphics.renderer import Renderer
# from core.tui.tui_manager import TuiManager


def setup_test_simulation() -> Simulation:
    """
    Configura una simulazione di test con locazioni, oggetti,
    i due NPC principali (Erika e Max) e un cast di personaggi casuali.
    """
    print("  [Setup] Avvio configurazione simulazione di test...")
    sim = Simulation()
    sim_start_date = sim.time_manager.get_current_time()
    all_locations: List[Location] = [] # Assicurati di importare List e Location da typing

    # --- Caricamento Dati del Mondo ---
    all_locations: List['Location'] = [] 

    try:
        from core.data.districts.muse_quarter_data import district_locations as muse_locations
        from core.data.residential.dosinvelos_data import district_locations as dosinvelos_locations
        
        all_locations = muse_locations + dosinvelos_locations
        
        for loc in all_locations:
            sim.locations[loc.location_id] = loc
            for obj_id, obj in loc.objects.items():
                sim.world_objects[obj_id] = obj

    # --- MODIFICA QUI ---
    except ImportError as e:
        # Stampiamo l'errore esatto per capire cosa non va
        print(f"\n  [Setup FATAL ERROR] Impossibile importare i file di dati dei distretti: {e}")
        print("  [Setup INFO] Assicurati che i file .py dei dati e le cartelle che li contengono (data, districts, residential) abbiano tutte un file __init__.py vuoto.\n")
    # --- FINE MODIFICA ---
    
    available_location_ids = list(sim.locations.keys())
    if not available_location_ids:
        print("  [Setup FATAL ERROR] Nessuna locazione definita. Impossibile creare NPC.")
        return sim
    # if not public_spawn_location_ids:
    #     # Se non ci sono locazioni pubbliche, usiamo tutte quelle disponibili come fallback
    #     print("  [Setup WARN] Nessuna locazione pubblica per lo spawn trovata. Uso tutte le locazioni.")
    #     public_spawn_location_ids = list(sim.locations.keys())


    # --- Creazione NPC Fissi (Erika e Max) ---
    print("  [Setup] Creazione di Erika Lamborghetti e Max Volpi...")
    try:
        # Calcola la loro data di nascita condivisa (15 anni)
        age_in_days = int(15.153845649346 * time_config.DXY)
        birth_date = sim_start_date.sub(ATHDateInterval(days=age_in_days))

        # --- LOGICA DI POSIZIONAMENTO CASUALE ---
        dosinvelos_loc_id = "loc_dosinvelos_apt_01"
        dosinvelos_loc = sim.get_location_by_id(dosinvelos_loc_id)

        # --- LOGICA DI POSIZIONAMENTO SICURO ---
        walkable_tiles = []
        if dosinvelos_loc and dosinvelos_loc.walkable_grid:
            # Trova tutte le coordinate (x,y) dove il valore è True
            walkable_tiles = [
                (x, y) for y, row in enumerate(dosinvelos_loc.walkable_grid)
                for x, is_walkable in enumerate(row) if is_walkable
            ]

        if walkable_tiles:
            # Scegli due posizioni casuali dalla lista di quelle valide
            pos_erika = random.choice(walkable_tiles)
            pos_max = random.choice(walkable_tiles)
        else:
            # Fallback se non ci sono tile calpestabili
            pos_erika, pos_max = (0, 0), (1, 1)
            if settings.DEBUG_MODE:
                print(f"  [Setup WARN] Nessuna mattonella calpestabile trovata in '{dosinvelos_loc_id}'.")
        # --- FINE LOGICA DI POSIZIONAMENTO ---

        # Creazione di Erika
        erika = Character(
            npc_id="erika_lamborghetti", name="Erika Lamborghetti", initial_gender=Gender.FEMALE,
            initial_birth_date=birth_date,
            initial_traits={TraitType.SOCIAL, TraitType.ACTIVE, TraitType.PARTY_ANIMAL, TraitType.UNINHIBITED},
            initial_aspiration=AspirationType.SOCIAL_BUTTERFLY,
            initial_location_id=dosinvelos_loc_id,
            initial_logical_x=pos_erika[0], # Usa la coordinata x sicura
            initial_logical_y=pos_erika[1], # Usa la coordinata y sicura
            is_player_character=True
        )
        erika.ai_decision_maker = AIDecisionMaker(erika)
        erika.skill_manager.get_skill(SkillType.COOKING)._level = 3
        erika.skill_manager.get_skill(SkillType.CHARISMA)._level = 4
        erika.skill_manager.get_skill(SkillType.DANCING)._level = 2
        sim.add_npc(erika)

        # Creazione di Max
        max_v = Character(
            npc_id="max_volpi", name="Max Volpi", initial_gender=Gender.MALE,
            initial_birth_date=birth_date,
            initial_traits={TraitType.LONER, TraitType.BOOKWORM, TraitType.CREATIVE, TraitType.UNINHIBITED},
            initial_aspiration=AspirationType.BESTSELLING_AUTHOR,
            initial_location_id=dosinvelos_loc_id,
            initial_logical_x=pos_max[0], # Usa la coordinata x sicura
            initial_logical_y=pos_max[1], # Usa la coordinata y sicura
            is_player_character=True
        )
        max_v.ai_decision_maker = AIDecisionMaker(max_v)
        max_v.skill_manager.get_skill(SkillType.WRITING)._level = 4
        max_v.skill_manager.get_skill(SkillType.LOGIC)._level = 3
        max_v.skill_manager.get_skill(SkillType.PROGRAMMING)._level = 2
        # --- ESPERIMENTO: INNESCO DEI BISOGNI ---
        print("  [Setup] Innesco bisogni per test IA...")
        
        # Imposta la fame di Max a un livello basso ma non critico
        max_v.change_need_value(NeedType.HUNGER, -60) # Valore finale sarà ~30-40

        if settings.DEBUG_MODE:
            print(f"    Bisogno HUNGER di Max: {max_v.get_need_value(NeedType.HUNGER):.1f}")
        # --- FINE ESPERIMENTO ---

        sim.add_npc(max_v)

        # Imposta la loro relazione speciale
        erika.update_relationship(max_v.npc_id, RelationshipType.CHILDHOOD_BEST_FRIEND, new_score=96)
        max_v.update_relationship(erika.npc_id, RelationshipType.CHILDHOOD_BEST_FRIEND, new_score=96)

        # --- ESPERIMENTO: INNESCO DEI BISOGNI ---
        print("  [Setup] Innesco bisogni per test IA...")
        
        # Rendiamo Erika molto annoiata
        erika.change_need_value(NeedType.FUN, -75) # Imposta il divertimento a 25
        
        # Rendiamo Max molto solo
        max_v.change_need_value(NeedType.SOCIAL, -80) # Imposta la socialità a 20

        if settings.DEBUG_MODE:
            print(f"    Bisogno FUN di Erika: {erika.get_need_value(NeedType.FUN):.1f}")
            print(f"    Bisogno SOCIAL di Max: {max_v.get_need_value(NeedType.SOCIAL):.1f}")
        # --- FINE ESPERIMENTO ---

        # Imposta Erika come personaggio "osservato" di default
        sim.set_player_character(erika.npc_id)

    except Exception as e:
        print(f"  [Setup ERROR] Impossibile creare gli NPC principali: {e}")

    # Filtra le locazioni per trovare quelle pubbliche adatte allo spawn
    public_spawn_location_types = {
        LocationType.PARK, 
        LocationType.CAFE, 
        LocationType.MUSEUM, 
        LocationType.JAZZ_CLUB
    }
    public_spawn_location_ids = [
        loc.location_id for loc in sim.locations.values() if loc.location_type in public_spawn_location_types
    ]
    # Se non ci sono locazioni pubbliche, usiamo tutte quelle disponibili come fallback
    if not public_spawn_location_ids:
        public_spawn_location_ids = list(sim.locations.keys())

    # --- Creazione NPC Casuali ---
    npc_factory = NPCFactory()
    num_random_npcs = random.randint(4, 6)
    print(f"  [Setup] Generazione di {num_random_npcs} NPC casuali...")
    
    for i in range(num_random_npcs):
        try:
            # 1. Scegli una locazione pubblica a caso dove far apparire l'NPC
            random_loc_id = random.choice(public_spawn_location_ids)
            spawn_loc = sim.get_location_by_id(random_loc_id)
            
            if not spawn_loc: continue # Salta se la locazione non esiste

            # 2. Trova tutte le mattonelle calpestabili in quella locazione
            walkable_tiles = []
            if spawn_loc.walkable_grid:
                walkable_tiles = [
                    (x, y) for y, row in enumerate(spawn_loc.walkable_grid)
                    for x, is_walkable in enumerate(row) if is_walkable
                ]
            
            # Se non ci sono punti validi, salta la creazione di questo NPC
            if not walkable_tiles: continue

            # 3. Scegli coordinate casuali da quelle valide
            spawn_x, spawn_y = random.choice(walkable_tiles)

            # 4. Crea l'NPC "vuoto" con la factory
            random_npc = npc_factory.create_random_npc(
                simulation_start_date=sim_start_date
            )
            
            # 5. Assegna la posizione e l'IA all'NPC appena creato
            random_npc.current_location_id = random_loc_id
            random_npc.logical_x = spawn_x
            random_npc.logical_y = spawn_y
            random_npc.ai_decision_maker = AIDecisionMaker(random_npc)
            
            # 6. Aggiungi l'NPC completo alla simulazione
            sim.add_npc(random_npc)

        except Exception as e:
            print(f"  [Setup ERROR] Impossibile creare l'NPC casuale n.{i+1}: {e}")
    
    print("  [Setup] Configurazione simulazione completata.")
    return sim


def main():
    """Punto di ingresso principale dell'applicazione."""
    print(f"--- Avvio SimAI {settings.GAME_VERSION} ---")
    
    # 1. Crea l'istanza della simulazione
    simulation = setup_test_simulation()

    # 2. Controlla la modalità di esecuzione
    if not settings.GUI_ENABLED:
        # Esecuzione in Modalità Testuale (TUI)
        print("  Modalità Testuale (TUI/Debug) attivata.")
        max_ticks_tui = 5000
        print(f"  Simulazione testuale verrà eseguita per un massimo di {max_ticks_tui} tick.")
        # Assumiamo che ci sia un metodo .run() per la TUI
        simulation.run(max_ticks=max_ticks_tui) 
    else:
        # Esecuzione in Modalità Grafica (GUI)
        print("  Modalità GUI Pygame attivata.")
        # a. Crea il renderer
        renderer = Renderer() 
        # b. Avvia il loop di gioco. Sarà lui a gestire tutto da ora in poi.
        renderer.run_game_loop(simulation)

    print("--- Fine Simulazione SimAI ---")

if __name__ == "__main__":
    main()
