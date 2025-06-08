# simai.py
"""
SimAI - Simulatore di Vita Artificiale
Punto di ingresso principale per l'applicazione.
"""
import sys
import os
import random
from typing import Set

project_root = os.path.dirname(os.path.abspath(__file__))
settings_path_check = os.path.join(project_root, 'core', 'settings.py')
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from core.simulation import Simulation
    from core.character import Character
    from core.enums import (
        Gender, Interest, RelationshipStatus, AspirationType, TraitType
    )
    from core import settings
    from core.graphics import Renderer
except ImportError as e:
    print(f"Errore di importazione: {e}. Assicurati che i moduli siano nel PYTHONPATH.")
    sys.exit(1)

def setup_test_simulation() -> Simulation:
    """Imposta una simulazione di test con alcuni NPC e locazioni."""
    sim = Simulation() # La creazione delle locazioni e degli oggetti con coordinate logiche avviene qui dentro

    if sim.locations:
        sim.default_starting_location_id = list(sim.locations.keys())[0] # Es. "max_casa_cucina"
    else:
        print("[Setup WARN] Nessuna locazione creata. Impossibile impostare default_starting_location_id per NPC.")

    npc1_interests: Set[Interest] = {Interest.READING, Interest.MUSIC_PLAYING, Interest.TECHNOLOGY}
    npc1_attr_genders: Set[Gender] = {Gender.FEMALE, Gender.NON_BINARY}
    npc1_traits: Set[TraitType] = {TraitType.BOOKWORM, TraitType.LOGICAL, TraitType.LONER}
    npc1 = Character(
        npc_id="Max001", name="Max Power", initial_gender=Gender.MALE,
        initial_age_days=16 * settings.DXY,
        initial_logical_x=2,  # Coordinate logiche per Max
        initial_logical_y=2,
        initial_interests=npc1_interests,
        initial_sexually_attracted_to_genders=npc1_attr_genders,
        initial_romantically_attracted_to_genders=npc1_attr_genders,
        initial_relationship_status=RelationshipStatus.SINGLE,
        initial_aspiration=AspirationType.KNOWLEDGE_SEEKER,
        initial_traits=npc1_traits
    )
    sim.add_npc(npc1)
    sim.set_player_character(npc1.npc_id) 


    npc2_interests: Set[Interest] = {Interest.SPORTS_PRACTICING, Interest.GAMING}
    npc2_traits: Set[TraitType] = {TraitType.ACTIVE, TraitType.SOCIAL, TraitType.OPTIMIST}
    npc2 = Character(
        npc_id="Erika002", name="Erika Sky", initial_gender=Gender.FEMALE,
        initial_age_days=14 * settings.DXY,
        initial_logical_x=4,  # Coordinate logiche per Erika
        initial_logical_y=2,
        initial_interests=npc2_interests,
        initial_sexually_attracted_to_genders={Gender.MALE},
        initial_romantically_attracted_to_genders={Gender.MALE},
        initial_traits=npc2_traits
    )
    sim.add_npc(npc2)
    
    if settings.DEBUG_MODE:
        print(f"  [Setup] {npc1.name} si trova in locazione ID: {npc1.current_location_id}")
        print(f"  [Setup] {npc2.name} si trova in locazione ID: {npc2.current_location_id}")

        print("\n--- Bisogni Iniziali NPC ---")
        for npc_obj in sim.npcs.values():
            npc_obj.print_needs_summary()
        print("----------------------------\n")
        
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