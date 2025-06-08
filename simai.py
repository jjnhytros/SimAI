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
from core.config import time_config

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
    Configura una simulazione di test con locazioni, oggetti e un cast di NPC
    generati casualmente e posizionati in modo casuale nel mondo.
    """
    print("  [Setup] Avvio configurazione simulazione di test...")
    sim = Simulation()
    # Ora che posizioniamo gli NPC casualmente, il default non è più strettamente necessario per il setup
    # sim.default_starting_location_id = "max_casa_cucina" 

    # --- OTTIENI LISTA LOCAZIONI DISPONIBILI ---
    available_location_ids = list(sim.locations.keys())
    if not available_location_ids:
        print("  [Setup FATAL ERROR] Nessuna locazione definita nella simulazione. Impossibile posizionare gli NPC.")
        return sim # Ritorna una simulazione vuota

    # --- Creazione NPC Casuali con la Factory e POSIZIONAMENTO CASUALE ---
    npc_factory = NPCFactory()
    num_random_npcs = random.randint(4, 6)
    
    print(f"  [Setup] Generazione e posizionamento di {num_random_npcs} NPC casuali...")
    
    random_npcs_list: List[Character] = []
    for i in range(num_random_npcs):
        try:
            # 1. Scegli una locazione casuale
            chosen_loc_id = random.choice(available_location_ids)
            chosen_loc = sim.get_location_by_id(chosen_loc_id)
            if not chosen_loc: continue # Salta se la locazione non viene trovata

            # 2. Scegli coordinate casuali all'interno della locazione
            rand_x = random.randint(0, chosen_loc.logical_width - 1)
            rand_y = random.randint(0, chosen_loc.logical_height - 1)
            
            # 3. Crea l'NPC (la factory ora potrebbe accettare questi parametri o li impostiamo dopo)
            # Per semplicità, creiamo l'NPC e poi aggiorniamo la sua posizione.
            random_npc = npc_factory.create_random_npc()
            random_npc.current_location_id = chosen_loc_id
            random_npc.logical_x = rand_x
            random_npc.logical_y = rand_y

            sim.add_npc(random_npc)
            random_npcs_list.append(random_npc)
        except Exception as e:
            if settings.DEBUG_MODE:
                print(f"  [Setup ERROR] Impossibile creare l'NPC casuale n.{i+1}: {e}")
    
    # --- Creazione e POSIZIONAMENTO del Personaggio Principale ---
    print("  [Setup] Creazione e posizionamento del personaggio principale 'Alex Valdis'...")
    player_character: Optional[Character] = None
    player_traits = {TraitType.BOOKWORM, TraitType.LONER, TraitType.AMBITIOUS}
    try:
        # Scegli una locazione e coordinate anche per il personaggio principale
        player_loc_id = random.choice(available_location_ids)
        player_loc = sim.get_location_by_id(player_loc_id)
        player_x = 0
        player_y = 0
        if player_loc:
            player_x = random.randint(0, player_loc.logical_width - 1)
            player_y = random.randint(0, player_loc.logical_height - 1)
            
        player_character = Character(
            npc_id="player_char_001", 
            name="Alex Valdis",
            initial_gender=Gender.NON_BINARY,
            initial_age_days=int(25 * time_config.DXY),
            initial_traits=player_traits,
            initial_aspiration=AspirationType.LOREMASTER_OF_ANTHALYS,
            # Passa qui i valori di posizione
            initial_location_id=player_loc_id,
            initial_logical_x=player_x,
            initial_logical_y=player_y
        )
        sim.add_npc(player_character)
        sim.set_player_character(player_character.npc_id)
    except Exception as e:
        if settings.DEBUG_MODE:
            print(f"  [Setup ERROR] Impossibile creare il personaggio principale: {e}")

    if player_character and random_npcs_list:
        # Scegliamo il primo NPC casuale come target per la relazione
        first_random_npc = random_npcs_list[0]
        
        # Imposta il tipo di relazione e un punteggio iniziale
        initial_rel_type = RelationshipType.ACQUAINTANCE # Si conoscono appena
        initial_score = 15 # Un punteggio iniziale leggermente positivo
        
        # Imposta la relazione in entrambe le direzioni
        player_character.update_relationship(
            target_npc_id=first_random_npc.npc_id,
            new_type=initial_rel_type,
            new_score=initial_score
        )
        
        first_random_npc.update_relationship(
            target_npc_id=player_character.npc_id,
            new_type=initial_rel_type,
            new_score=initial_score
        )
        
        if settings.DEBUG_MODE:
            print(f"  [Setup] Creata relazione base ({initial_rel_type.name}, Score: {initial_score}) "
                f"tra {player_character.name} e {first_random_npc.name}.")

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