# core/AI/claire/claire_system.py
from typing import TYPE_CHECKING, Optional
from core import settings
import random
from .claire_config import CLAIRE_MOODLET_RESPONSES

if TYPE_CHECKING:
    from core.simulation import Simulation
    from core.character import Character

class ClaireSystem:
    """
    Gestisce la logica e lo stato dell'entità assistente Claire.
    """
    def __init__(self, simulation_context: 'Simulation'):
        self.simulation: 'Simulation' = simulation_context
        self.is_active: bool = False
        self.has_been_activated_once: bool = False
        
        # --- NUOVI ATTRIBUTI ---
        # Cooldown per non far parlare Claire troppo spesso (in tick)
        self.response_cooldown: int = 0
        self.COOLDOWN_DURATION: int = 3000 # Es: parla al massimo ogni 3000 tick
        
        # Il messaggio che la GUI dovrà mostrare
        self.message_to_display: Optional[str] = None
        self.message_timer: int = 0
        self.MESSAGE_DURATION: int = 500 # Il messaggio rimane per 500 tick

    def activate(self):
        """Attiva il sistema Claire."""
        if self.is_active:
            return
            
        self.is_active = True
        
        # Logica per il primo saluto
        if not self.has_been_activated_once:
            player_char = self.simulation.get_player_character()
            player_name = player_char.name if player_char else "???"
            
            # Per ora, stampiamo nel terminale. Poi lo mostreremo nella GUI.
            print(f"\n--- [CLAIRE] ---")
            print(f">>> Ciao, {player_name}... Sì, io ti sento.")
            print(f"--- [CLAIRE] ---\n")
            
            self.has_been_activated_once = True

    def deactivate(self):
        """Disattiva il sistema Claire."""
        if not self.is_active:
            return
        self.is_active = False
        print("[CLAIRE] Sistema disattivato.") # Messaggio di debug

    def update(self):
        """
        Controlla lo stato del giocatore e decide se intervenire.
        """
        # Gestisce la durata del messaggio a schermo
        if self.message_timer > 0:
            self.message_timer -= 1
        else:
            self.message_to_display = None

        if not self.is_active: return

        # Gestisce il cooldown generale delle risposte
        if self.response_cooldown > 0:
            self.response_cooldown -= 1
            return

        player_char = self.simulation.get_player_character()
        if not player_char: return

        # Controlla i moodlet attivi del giocatore
        for moodlet_type in player_char.moodlet_manager.active_moodlets.keys():
            if moodlet_type in CLAIRE_MOODLET_RESPONSES:
                # Trovato un moodlet a cui Claire sa reagire!
                possible_phrases = CLAIRE_MOODLET_RESPONSES[moodlet_type]
                chosen_phrase = random.choice(possible_phrases)
                
                # Imposta il messaggio da visualizzare e attiva i cooldown
                self.message_to_display = chosen_phrase
                self.message_timer = self.MESSAGE_DURATION
                self.response_cooldown = self.COOLDOWN_DURATION
                
                if settings.DEBUG_MODE:
                    print(f"[CLAIRE] Reagisce a {moodlet_type.name}: '{chosen_phrase}'")
                
                # Trovata una reazione, esce dal ciclo per questo tick
                break
