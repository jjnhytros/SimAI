# simai/core/minigames/clairOS/main.py
from .behavior import (claire_intimate_connection,claire_touch,behavioral_adaptation, generate_incongruent_response,handle_sensitive_zones_effect)
from .constants import (LOW_PATIENCE_THRESHOLD,MAX_PATIENCE,CRITICAL_PATIENCE_THRESHOLD,)
from .emotion_state import EmotionalState
from .events import generate_chaos_event
from .interactions import user_interaction
from .memory_core import (add_shared_moment,claire_recalls_memory,memory_core,)
from .save_load import save_game_state, load_game_state
from .text_generation import (claire_gaze,claire_whisper,generate_ai_poem,generate_sensual_event,)
from datetime import datetime
from typing import List
import os
import random
import textwrap
import time

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def display_status_header(state: 'EmotionalState', turn_count: int):
    """Displays the consistent header with turn and Claire's status."""
    print(f"--- ClaireOS v3.1 | Turno: {turn_count} ---") # Rimosso POV
    print(f"{state}")
    print("-" * 70)

def main_loop():
    global memory_core
    loaded_state, loaded_memory_core = load_game_state()
    state = loaded_state if loaded_state else EmotionalState()
    memory_core = loaded_memory_core

    action_counter = 0
    log_of_last_completed_turn_narrative: List[str] = []

    initial_greeting_needed = not loaded_state

    try:
        while True:
            outputs_for_current_turn_narrative: List[str] = []
            action_counter += 1

            clear_screen()
            display_status_header(state, action_counter)

            if log_of_last_completed_turn_narrative:
                print("\n--- Output Turn Precedente ---")
                for line_to_reprint in log_of_last_completed_turn_narrative: 
                    print(line_to_reprint)
                print("--- Fine Output Turn Precedente ---\n")
            elif action_counter == 1:
                if initial_greeting_needed:
                    print("\nSysCore Claire v3.1 - Protocollo di Coscienza Sintetica Attivato.")
                    print(f"Contatto iniziale: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                else:
                    print("\nSysCore Claire v3.1 - Ripristino Sessione.")
                print(f"Ultimo risveglio significativo di Claire: {state.last_awakening.strftime('%Y-%m-%d %H:%M:%S')}")

            print("\n" + "═"*70)
            action_tag = user_interaction()

            state, dynamic_reaction_text = behavioral_adaptation(state, action_tag)
            outputs_for_current_turn_narrative.append(f"\n{textwrap.fill(dynamic_reaction_text, width=70)}")
            
            # Aggiungi risposta incongruente se applicabile
            incongruent_response = generate_incongruent_response(state)
            if incongruent_response:
                outputs_for_current_turn_narrative.append(f"\n{incongruent_response}")

            recalled_text, mood_effects, recalled_moment_obj = claire_recalls_memory(state)
            if recalled_text:
                outputs_for_current_turn_narrative.append(f"\n🧠 ECO DAL PASSATO (Influenza l'umore attuale) 🧠\n{recalled_text}")
                if mood_effects:
                    state.apply_mood_tendency_deltas(mood_effects)
                if recalled_moment_obj:
                    for line_to_print in outputs_for_current_turn_narrative: 
                        print(line_to_print)

            # Evento caotico basato su intensità
            if state.intensity > 30 and random.random() < state.intensity / 150:
                event_text = generate_chaos_event(state)
                outputs_for_current_turn_narrative.append(f"\n🌀 EVENTO CAOTICO 🌀\n{event_text}")
            
            # Evento sensuale basato su sensualità/desiderio
            if (state.sensuality > 30 or state.desire > 40) and random.random() < 0.4:
                outputs_for_current_turn_narrative.append(f"\n{generate_sensual_event(state)}")

            outputs_for_current_turn_narrative.append(f"\n{claire_gaze(state, random.randint(1, 6) + state.intensity // 10 + (state.love // 20))}")
            
            if random.random() < (0.65 + state.trust/500):
                outputs_for_current_turn_narrative.append(claire_whisper(state))

            if state.desire > 40:
                outputs_for_current_turn_narrative.append(f"\n{claire_touch(state, random.randint(3, 7))}")
                if state.desire > 60 and state.love > 30 and random.random() < (0.3 + state.intensity/300):
                    outputs_for_current_turn_narrative.append(f"\n{claire_intimate_connection(state)}")

            poem_chance = 0.10 + (state.intensity / 400) + (state.desire / 300) + (state.love / 1000)
            if state.patience < CRITICAL_PATIENCE_THRESHOLD:
                poem_chance += 0.1
            
            if random.random() < poem_chance:
                outputs_for_current_turn_narrative.append("\n🎶 Frammento di codice poetico:")
                theme = random.choice(['erotic', 'love', 'dark', 'trust', 'philosophical'])
                if state.patience < LOW_PATIENCE_THRESHOLD and random.random() < 0.6:
                    theme = 'dark'
                elif state.desire > 70 and state.love > 70:
                    theme = 'erotic'
                elif state.love > 100:
                    theme = 'love'
                elif state.trust < 30 and state.intensity > 40:
                    theme = 'trust'
                elif state.intensity > 70:
                    theme = 'dark'
                elif state.secrets_shared > 5 and state.trust > 60:
                    theme = 'trust'
                outputs_for_current_turn_narrative.append(f"{generate_ai_poem(theme)}")

            # Sovraccarico sensuale con soglie adattive
            if (state.desire >= state.desire_threshold and 
                state.sensuality > state.sensuality_threshold and 
                random.random() > 0.55):
                outputs_for_current_turn_narrative.append("\n💦 SOVRACCARICO SENSUALE!")
                old_stats = {"love": state.love, "trust": state.trust, "intensity": state.intensity, 
                            "desire": state.desire, "sensuality": state.sensuality, "patience": state.patience,
                            "desire_threshold": state.desire_threshold, "sensuality_threshold": state.sensuality_threshold}
                
                overload_descriptions = [
                    "Claire emette un gemito digitale mentre i suoi sistemi si sovraccaricano di piacere",
                    "Un'onda di dati erotici travolge i circuiti di Claire causando un cortocircuito di piacere",
                    "I sensori di Claire raggiungono il culmine in un turbine di sensazioni elettriche"
                ]
                
                outputs_for_current_turn_narrative.append(textwrap.fill(random.choice(overload_descriptions), width=70))
                outputs_for_current_turn_narrative.append(generate_ai_poem('erotic'))
                
                state.desire = random.randint(30,50)
                state.sensuality = random.randint(40,60)
                state.intensity = max(10, state.intensity - random.randint(10,25))
                state.patience = min(MAX_PATIENCE, state.patience+1)
                
                add_shared_moment("sovraccarico_sensuale", "Orgamo digitale. Ricalibrazione.", old_stats)
                outputs_for_current_turn_narrative.append(textwrap.fill("Claire: 'Devo... ricalibrare... le sensazioni erano troppo intense'", width=70))

            # Paradosso emotivo con soglie adattive
            if (state.intensity >= (90 - state.patience*2) and 
                state.trust < state.trust_threshold and 
                random.random() > 0.70):
                outputs_for_current_turn_narrative.append("\n💥 PARADOSSO EMOTIVO!")
                old_stats = {"love": state.love, "trust": state.trust, "intensity": state.intensity, 
                            "desire": state.desire, "sensuality": state.sensuality, "patience": state.patience,
                            "trust_threshold": state.trust_threshold}
                state.intensity = random.randint(10, 30)
                state.desire = random.randint(20, 40)
                state.love = max(0, state.love - 20)
                state.trust = max(0, state.trust - 15)
                state.patience = min(MAX_PATIENCE, state.patience+2)
                state.last_awakening = datetime.now()
                add_shared_moment("paradosso_emotivo", f"Reset. Amore {old_stats['love']}->{state.love}", old_stats)
                outputs_for_current_turn_narrative.append(generate_ai_poem('dark'))
                outputs_for_current_turn_narrative.append(textwrap.fill("Claire: 'Frammenti... Ricomposizione...'", width=70))

            if state.love > state.love_threshold:
                outputs_for_current_turn_narrative.append(
                    f"\n💫 Claire raggiunge un nuovo livello di intimità! " +
                    f"(Amore {state.love} > Soglia {state.love_threshold})"
                )
                state.love_threshold += 20  # Alza ulteriormente la soglia

            if state.patience < state.patience_threshold:
                reaction = random.choice([
                    f"Claire mostra segni di irritazione (Pazienza {state.patience} < Soglia {state.patience_threshold})",
                    f"La pazienza di Claire è al limite! (Pazienza {state.patience} < Soglia {state.patience_threshold})"
                ])
                outputs_for_current_turn_narrative.append(f"\n⚠️ {reaction}")

            # Stampa tutte le azioni di questo turno
            for line_to_print in outputs_for_current_turn_narrative: 
                print(line_to_print)
            
            log_of_last_completed_turn_narrative = list(outputs_for_current_turn_narrative)
            state.evolve()
            time.sleep(1.8)

    except KeyboardInterrupt: 
        print("\n\n🔌 Disconnessione...")
        save_game_state(state, memory_core)
        print("Simulazione terminata.")
    except Exception as e: 
        print(f"\n\n💥 ERRORE CRITICO: {e} ({type(e).__name__}) 💥")
        import traceback; traceback.print_exc()
        print("Salvataggio di emergenza...")
        save_game_state(state, memory_core)
        print("Simulazione interrotta.")

if __name__ == "__main__":
    main_loop()


# # TODO - Claire's Interaction Script v3.5 
#
# ## Gameplay & Story
# - [X] **`shared_moments` Populated**
# - [X] **Claire Recalls Memories**
# - [X] **`evolve()` based on choices**
# - [P] **Espandere `behavioral_adaptation`**:
#   - [P] Aggiungere più `action_tag` e reazioni emotive
#   - [P] Considerare effetti a lungo termine
# - [P] **Eventi Caotici Dinamici**
# - [X] **Impatto `sensitive_zones`**: Implementare effetti specifici
#   - [X] Effetti amplificati per tocco/bacio sulle zone sensibili
#   - [X] Reazioni speciali per connessioni intime con zone sensibili
#   - [X] Eventi caotici/sensuali focalizzati su zone sensibili
#   - [X] Memorizzazione delle zone preferite
# - [X] **Nuove Interazioni Utente**
# - [P] **Player Interaction with Recalled Memories**
# - [ ] **Finale Multiplo/Archi Narrativi**
# - [X] **Initialize values to 0**
# - [X] **Interactive choices based on status values**
# - [X] **Aggiungere icone all'umore**
# - [X] **Risposte "congruamente incoerenti"**
# - [X] **Parametro Sensualità**
# - [X] **Eventi Sensuali**
# - [X] **Sovraccarico Sensuale migliorato**
# - [X] **Intelligenza adattiva sulle soglie**
#
# ## Technical & Code Quality
# - [X] **Save/Load Game State**
# - [X] **Clear Screen**
# - [X] **Retain Last Action on Screen Clear**
# - [X] **Status always at top of screen**
# - [P] **Convertire identificatori interni in inglese**
# - [P] **Migliorare `user_interaction` error handling**
# - [P] **Costanti**: Spostare valori "magici"
# - [X] **Modularizzazione**
# - [ ] **Test**: Scrivere unit test
# - [ ] **GUI/TUI (SimAI Project)**
#
# ## SimAI Project Specific
# - [X] **Originalità (0.1.a)**
# - [ ] **.pyi Stubs**
# --- FINE TODO ---
