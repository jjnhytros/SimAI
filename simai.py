# simai.py
"""
Punto di ingresso principale per la simulazione SimAI.
Gestisce l'inizializzazione e l'avvio della simulazione in modalità GUI o TUI.
"""
import sys
import os
import random
from typing import TYPE_CHECKING, List, Optional

# Aggiunge la directory principale al path per permettere import assoluti
# come 'from core.simulation import Simulation'
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

    # --- Caricamento Dati del Mondo ---
    # Importa le location dai file di dati dei distretti
    try:
        from core.data.districts.muse_quarter_data import district_locations as muse_locations
        from core.data.residential.dosinvelos_data import district_locations as dosinvelos_locations
        
        all_locations = muse_locations + dosinvelos_locations
        
        for loc in all_locations:
            sim.locations[loc.location_id] = loc
            for obj_id, obj in loc.objects.items():
                sim.world_objects[obj_id] = obj
    except ImportError:
        print("  [Setup WARN] File di dati dei distretti non trovati. Caricamento saltato.")
    
    available_location_ids = list(sim.locations.keys())
    if not available_location_ids:
        print("  [Setup FATAL ERROR] Nessuna locazione definita. Impossibile creare NPC.")
        return sim

    # --- Creazione NPC Fissi (Erika e Max) ---
    print("  [Setup] Creazione di Erika Lamboretti e Max Volpi...")
    try:
        # Calcola la loro data di nascita condivisa (15 anni)
        age_in_days = int(15 * time_config.DXY)
        birth_date = sim_start_date.sub(ATHDateInterval(days=age_in_days))

        # --- LOGICA DI POSIZIONAMENTO CASUALE ---
        dosinvelos_loc_id = "loc_dosinvelos_apt_01"
        dosinvelos_loc = sim.get_location_by_id(dosinvelos_loc_id)
        
        erika_x, erika_y, max_x, max_y = 0, 0, 1, 1 # Valori di default

        if dosinvelos_loc:
            # Calcola posizioni casuali entro i limiti della location
            erika_x = random.randint(0, dosinvelos_loc.logical_width - 1)
            erika_y = random.randint(0, dosinvelos_loc.logical_height - 1)
            
            # Calcola una posizione diversa per Max
            max_x = random.randint(0, dosinvelos_loc.logical_width - 1)
            max_y = random.randint(0, dosinvelos_loc.logical_height - 1)
        else:
            if settings.DEBUG_MODE:
                print(f"  [Setup WARN] Locazione '{dosinvelos_loc_id}' non trovata per posizionare Erika e Max.")
        # --- FINE LOGICA DI POSIZIONAMENTO ---

        # Creazione di Erika
        erika = Character(
            npc_id="erika_lamboretti", name="Erika Lamboretti", initial_gender=Gender.FEMALE,
            initial_birth_date=birth_date,
            initial_traits={TraitType.SOCIAL, TraitType.ACTIVE, TraitType.PARTY_ANIMAL, TraitType.UNINHIBITED},
            initial_aspiration=AspirationType.SOCIAL_BUTTERFLY,
            initial_location_id=dosinvelos_loc_id,
            initial_logical_x=erika_x, # <-- Usa la coordinata casuale
            initial_logical_y=erika_y,  # <-- Usa la coordinata casuale
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
            initial_logical_x=max_x, # <-- Usa la coordinata casuale
            initial_logical_y=max_y,  # <-- Usa la coordinata casuale
            is_player_character=True
        )
        max_v.ai_decision_maker = AIDecisionMaker(max_v)
        max_v.skill_manager.get_skill(SkillType.WRITING)._level = 4
        max_v.skill_manager.get_skill(SkillType.LOGIC)._level = 3
        max_v.skill_manager.get_skill(SkillType.PROGRAMMING)._level = 2
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

    # --- Creazione NPC Casuali ---
    npc_factory = NPCFactory()
    num_random_npcs = random.randint(4, 6)
    print(f"  [Setup] Generazione di {num_random_npcs} NPC casuali...")
    
    for i in range(num_random_npcs):
        try:
            random_npc = npc_factory.create_random_npc(
                simulation_start_date=sim_start_date,
                available_location_ids=available_location_ids
            )
            random_npc.ai_decision_maker = AIDecisionMaker(random_npc)
            sim.add_npc(random_npc)
        except Exception as e:
            print(f"  [Setup ERROR] Impossibile creare l'NPC casuale n.{i+1}: {e}")
    
    print("  [Setup] Configurazione simulazione completata.")
    return sim


def main():
    """Punto di ingresso principale dell'applicazione."""
    print(f"--- Avvio SimAI {settings.GAME_VERSION} ---")
    
    simulation = setup_test_simulation()

    if settings.DEBUG_MODE:
        # --- ESECUZIONE IN MODALITÀ TESTUALE (TUI) ---
        print("  Modalità Testuale (TUI/Debug) attivata.")
        max_ticks_tui = 5000
        print(f"  Simulazione testuale verrà eseguita per un massimo di {max_ticks_tui} tick.")
        simulation.run(max_ticks=max_ticks_tui)
    else:
        # --- ESECUZIONE IN MODALITÀ GRAFICA (GUI) ---
        print("  Modalità GUI Pygame attivata.")
        renderer = Renderer(width=1280, height=768)
        renderer.run_game_loop(simulation)

    print("--- Fine Simulazione SimAI ---")

if __name__ == "__main__":
    main()