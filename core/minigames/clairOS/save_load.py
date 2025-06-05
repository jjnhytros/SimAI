# simai/core/minigames/clairOS/save_load.py
import json
import os
from datetime import datetime
from . import constants as c
from .emotion_state import EmotionalState
from .memory_core import memory_core
from .constants import SAVE_FILE_NAME
from typing import Dict, Optional, Tuple

# --- Save/Load State ---
def save_game_state(state_to_save: EmotionalState, mem_core_to_save: Dict) -> None:
    """Salva lo stato corrente del gioco su file."""
    data_to_save = {"emotional_state": state_to_save.to_dict(), "memory_core": mem_core_to_save}
    try:
        with open(SAVE_FILE_NAME, 'w') as f:
            json.dump(data_to_save, f, indent=4)
        print(f"\n[Stato di Claire salvato in {SAVE_FILE_NAME}]")
    except IOError as e:
        print(f"\n[Errore salvataggio: Impossibile scrivere su {SAVE_FILE_NAME}. Dettagli: {e}]")

def load_game_state() -> Tuple[Optional[EmotionalState], Dict]:
    """Carica lo stato del gioco da file, se esistente."""
    global memory_core # memory_core è una variabile globale che verrà aggiornata
    try:
        with open(SAVE_FILE_NAME, 'r') as f:
            data_loaded = json.load(f)
        
        loaded_emotional_state = EmotionalState.from_dict(data_loaded["emotional_state"])
        # Aggiorna memory_core globale con quello caricato, con fallback al default se non presente nel save
        memory_core = data_loaded.get("memory_core", memory_core) 
        
        print(f"\n[Stato Claire caricato da {SAVE_FILE_NAME}]")
        print(f"[Bentornato/a. Amore al caricamento: {loaded_emotional_state.love}, Fiducia: {loaded_emotional_state.trust}, Pazienza: {loaded_emotional_state.patience}]")
        return loaded_emotional_state, memory_core
    except FileNotFoundError:
        print(f"\n[Nessun file di salvataggio '{SAVE_FILE_NAME}' trovato. Inizio una nuova sessione.]")
        return None, memory_core # Ritorna il memory_core globale di default
    except (IOError, json.JSONDecodeError, KeyError) as e:
        print(f"\n[Errore nel caricamento del salvataggio (Dettagli: {e}). Il file '{SAVE_FILE_NAME}' potrebbe essere corrotto o malformato. Inizio una nuova sessione.]")
        return None, memory_core
    except Exception as e: # Catch-all per altri errori imprevisti
        print(f"\n[Errore imprevisto durante il caricamento del salvataggio (Dettagli: {e}). Inizio una nuova sessione.]")
        return None, memory_core

