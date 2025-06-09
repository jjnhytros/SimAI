# simai.py
"""
SimAI - Simulatore di Vita Artificiale
Punto di ingresso principale per l'applicazione.
"""
import sys
import os
import random
from typing import List, Optional
from core.factories.npc_factory import NPCFactory
from core.AI.ai_decision_maker import AIDecisionMaker
from core.config import time_config
from core.world.ATHDateTime.ATHDateInterval import ATHDateInterval

project_root = os.path.dirname(os.path.abspath(__file__))
settings_path_check = os.path.join(project_root, 'core', 'settings.py')
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from core.simulation import Simulation
    from core.character import Character
    from core.enums import (
        Gender, Interest, RelationshipType, AspirationType, TraitType
    )
    from core import settings
    from core.graphics import Renderer
except ImportError as e:
    print(f"Errore di importazione: {e}. Assicurati che i moduli siano nel PYTHONPATH.")
    sys.exit(1)

def setup_test_simulation() -> Simulation:
    """
    Configura una simulazione di test con NPC generati casualmente
    con una data di nascita e posizione casuale.
    """
    print("  [Setup] Avvio configurazione simulazione di test...")
    sim = Simulation()
    
    # Ottieni la data di inizio per i calcoli della data di nascita
    sim_start_date = sim.time_manager.get_current_time()

    available_location_ids = list(sim.locations.keys())
    if not available_location_ids:
        print("  [Setup FATAL ERROR] Nessuna locazione definita. Impossibile creare NPC.")
        return sim

    # --- Creazione NPC Casuali ---
    npc_factory = NPCFactory()
    num_random_npcs = random.randint(4, 6)
    print(f"  [Setup] Generazione e posizionamento di {num_random_npcs} NPC casuali...")
    
    for i in range(num_random_npcs):
        try:
            # La factory ora richiede la data di inizio per calcolare la nascita
            random_npc = npc_factory.create_random_npc(
                simulation_start_date=sim_start_date,
                available_location_ids=available_location_ids
            )
            sim.add_npc(random_npc)
        except Exception as e:
            print(f"  [Setup ERROR] Impossibile creare l'NPC casuale n.{i+1}: {e}")
    
    # --- Creazione Personaggio Principale ---
    print("  [Setup] Creazione del personaggio principale 'Alex Valdis'...")
    try:
        player_age_days = int(25 * time_config.DXY)
        player_age_interval = ATHDateInterval(days=player_age_days)
        player_birth_date = sim_start_date.sub(player_age_interval)
        
        player_loc_id = random.choice(available_location_ids)
        player_loc = sim.get_location_by_id(player_loc_id)
        player_x = random.randint(0, player_loc.logical_width - 1) if player_loc else 0
        player_y = random.randint(0, player_loc.logical_height - 1) if player_loc else 0

        player_character = Character(
            npc_id="player_char_001", 
            name="Alex Valdis",
            initial_gender=Gender.NON_BINARY,
            initial_birth_date=player_birth_date,
            initial_traits={TraitType.BOOKWORM, TraitType.LONER, TraitType.AMBITIOUS},
            initial_aspiration=AspirationType.LOREMASTER_OF_ANTHALYS,
            initial_location_id=player_loc_id,
            initial_logical_x=player_x,
            initial_logical_y=player_y
        )
        sim.add_npc(player_character)
        sim.set_player_character(player_character.npc_id)
    except Exception as e:
        print(f"  [Setup ERROR] Impossibile creare il personaggio principale: {e}")

    print("  [Setup] Configurazione simulazione completata.")
    return sim

def main():
    """Funzione principale che avvia la simulazione."""
    print(f"--- Avvio {settings.GAME_NAME} v{settings.GAME_VERSION} ---")

    simulation = setup_test_simulation()

    if not settings.DEBUG_MODE: # Se DEBUG_MODE è False, avvia la GUI
        print("  Modalità GUI Pygame attivata.")
        renderer = Renderer(caption=f"{settings.GAME_NAME} - GUI Edition")
        # Passa la simulazione al game loop della GUI in modo che possa accedervi
        renderer.run_game_loop(simulation) 
    else: # Altrimenti (DEBUG_MODE è True), avvia la simulazione testuale come prima
        print("  Modalità Testuale (TUI/Debug) attivata.")
        # Esegui per un numero limitato di tick per il test in modalità TUI
        # Oppure un loop più lungo se la TUI è interattiva
        max_ticks_tui = 5000 # Esempio, puoi cambiarlo o rimuoverlo per un loop infinito
        print(f"  Simulazione testuale verrà eseguita per un massimo di {max_ticks_tui} tick.")
        simulation.run(max_ticks=max_ticks_tui)

    print(f"--- Fine Simulazione {settings.GAME_NAME} ---")

if __name__ == "__main__":
    main()