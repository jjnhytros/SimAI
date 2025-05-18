# game/src/entities/components/aspiration_component.py
import logging
import random
from typing import Dict, Any, Optional, List, TYPE_CHECKING

# Importa dal package 'game'
from game import config # Per definizioni di aspirazioni o valori di default

if TYPE_CHECKING:
    from game.src.entities.character import Character # Per il type hint di character_owner

logger = logging.getLogger(__name__)
DEBUG_ASPIRATION = getattr(config, 'DEBUG_AI_ACTIVE', False) # Flag di debug specifico

# Esempi di aspirazioni (potrebbero essere definite in config.py o in un file JSON dedicato)
DEFAULT_ASPIRATION_LIST = [
    "Diventare Chef Stellato",
    "Scrivere un Romanzo Bestseller",
    "Diventare Atleta Professionista",
    "Trovare il Vero Amore",
    "Avere una Grande Famiglia",
    "Accumulare una Fortuna",
    "Padroneggiare un'Abilità (es. Pittura)",
    "Esplorare il Mondo" # Placeholder generico
]

class AspirationComponent:
    def __init__(self, character_owner: 'Character'):
        """
        Inizializza il componente delle aspirazioni.

        Args:
            character_owner (Character): Il personaggio a cui questo componente appartiene.
        """
        self.owner: 'Character' = character_owner
        self.owner_name: str = character_owner.name if character_owner else "NPC Sconosciuto"

        self.available_aspirations: List[str] = getattr(config, 'ASPIRATION_DEFINITIONS_LIST', DEFAULT_ASPIRATION_LIST)
        
        self.current_aspiration: Optional[str] = None
        self.aspiration_progress: float = 0.0  # Es. da 0.0 a 1.0 (o 0-100)
        self.is_completed: bool = False
        self.completion_reward_points: int = getattr(config, 'ASPIRATION_COMPLETION_REWARD_POINTS', 1000) # Punti "felicità" o simili

        # Potresti avere aspirazioni a breve e lungo termine
        # self.short_term_goal: Optional[str] = None
        # self.long_term_aspiration: Optional[str] = None

        self._select_initial_aspiration()

        if DEBUG_ASPIRATION:
            logger.debug(f"AspirationComponent per {self.owner_name} inizializzato. Aspirazione: {self.current_aspiration}, Progresso: {self.aspiration_progress:.2f}")

    def _select_initial_aspiration(self):
        """Seleziona un'aspirazione iniziale per l'NPC."""
        if self.available_aspirations:
            self.set_new_aspiration(random.choice(self.available_aspirations))
        else:
            logger.warning(f"Aspiration ({self.owner_name}): Lista aspirazioni disponibili vuota. Nessuna aspirazione iniziale impostata.")

    def set_new_aspiration(self, aspiration_name: str) -> bool:
        """Imposta una nuova aspirazione per l'NPC."""
        if aspiration_name in self.available_aspirations or getattr(config, "ALLOW_CUSTOM_ASPIRATIONS", False):
            self.current_aspiration = aspiration_name
            self.aspiration_progress = 0.0
            self.is_completed = False
            if DEBUG_ASPIRATION:
                logger.info(f"Aspiration ({self.owner_name}): Nuova aspirazione impostata a '{self.current_aspiration}'.")
            # Potrebbe influenzare l'umore o dare un piccolo boost iniziale
            if hasattr(self.owner, 'mood') and self.owner.mood:
                self.owner.mood.add_mood_modifier(getattr(config, "MOOD_BOOST_NEW_ASPIRATION", 5.0), "Nuova aspirazione")
            return True
        else:
            logger.warning(f"Aspiration ({self.owner_name}): Tentativo di impostare aspirazione non valida '{aspiration_name}'.")
            return False

    def add_progress(self, amount: float, source_action: Optional[str] = None):
        """
        Aggiunge progresso all'aspirazione corrente.
        'amount' è la quantità di progresso (es. 0.01 per 1%).
        """
        if self.is_completed or not self.current_aspiration:
            return

        self.aspiration_progress += amount
        self.aspiration_progress = max(0.0, min(1.0, self.aspiration_progress)) # Clamp tra 0 e 1 (o 0-100)

        if DEBUG_ASPIRATION:
            source_log = f" da '{source_action}'" if source_action else ""
            logger.debug(f"Aspiration ({self.owner_name}): Progresso per '{self.current_aspiration}' aggiunto di {amount:.2f}{source_log}. Totale: {self.aspiration_progress:.2f}")

        if self.aspiration_progress >= 1.0:
            self.complete_aspiration()

    def complete_aspiration(self):
        """Gestisce il completamento dell'aspirazione corrente."""
        if self.is_completed or not self.current_aspiration:
            return

        self.is_completed = True
        if DEBUG_ASPIRATION:
            logger.info(f"Aspiration ({self.owner_name}): ASPIRAZIONE COMPLETATA! '{self.current_aspiration}'")

        # Applica ricompense (es. punti felicità, tratto speciale, sblocco nuove interazioni)
        if hasattr(self.owner, 'mood') and self.owner.mood:
            self.owner.mood.add_mood_modifier(getattr(config, "MOOD_BOOST_ASPIRATION_COMPLETED", 50.0), f"Completata: {self.current_aspiration}")
        
        # Potrebbe sbloccare un "tratto di ricompensa"
        # if hasattr(self.owner, 'traits') and self.owner.traits:
        #     self.owner.traits.add_reward_trait(f"Tratto da {self.current_aspiration}")

        # Permetti all'NPC di scegliere una nuova aspirazione (o entra in uno stato "contento")
        # Per ora, selezioniamo subito una nuova aspirazione.
        # In futuro, potrebbe esserci un periodo di "soddisfazione" prima di sceglierne un'altra.
        previous_aspiration = self.current_aspiration
        self.current_aspiration = None # Resetta l'aspirazione corrente prima di sceglierne una nuova
        
        # Filtra l'aspirazione appena completata se non si vuole che si ripeta subito
        remaining_aspirations = [asp for asp in self.available_aspirations if asp != previous_aspiration]
        if not remaining_aspirations and self.available_aspirations: # Se ha completato tutte quelle uniche
            remaining_aspirations = self.available_aspirations # Permetti di ripeterle
            
        if remaining_aspirations:
            self.set_new_aspiration(random.choice(remaining_aspirations))
        else:
            logger.info(f"Aspiration ({self.owner_name}): Tutte le aspirazioni disponibili completate o nessuna aspirazione disponibile.")
            # L'NPC potrebbe rimanere senza aspirazioni o entrare in uno stato speciale.


    def update(self, character_state: 'Character'):
        """
        Aggiorna lo stato delle aspirazioni.
        Controlla se le azioni del personaggio o lo stato del mondo contribuiscono
        al progresso dell'aspirazione corrente.

        Args:
            character_state (Character): L'istanza Character completa per accedere ad altri componenti.
        """
        if self.is_completed or not self.current_aspiration:
            return

        # Questa è la parte più complessa e dipendente dal gioco.
        # Ogni aspirazione avrà condizioni di progresso diverse.
        # Esempio molto semplice:
        if self.current_aspiration == "Diventare Chef Stellato":
            if hasattr(character_state, 'skills') and character_state.skills:
                cucina_skill_level = character_state.skills.get_skill_level("cucina")
                # Il progresso potrebbe essere legato al livello di abilità in cucina
                # e al livello della carriera culinaria.
                # Progresso = (liv_cucina / 10 + liv_carriera_chef / 10) / 2 
                # Questo è solo un esempio, la logica reale sarebbe più dettagliata.
                # Per ora, il progresso deve essere aggiunto esternamente tramite self.add_progress()
                # da azioni specifiche (es. cucinare un pasto, andare al lavoro).
                pass
        elif self.current_aspiration == "Trovare il Vero Amore":
            if hasattr(character_state, 'relationships') and character_state.relationships:
                # Controlla se l'NPC ha una relazione romantica stabile e di alto livello
                # Per ora, progresso gestito esternamente.
                pass
        
        # In un sistema più avanzato, questo metodo 'update' potrebbe registrare
        # degli "ascoltatori" per eventi specifici del gioco o per il completamento di azioni
        # che poi chiamano self.add_progress().

    def get_current_aspiration_details(self) -> Optional[Dict[str, Any]]:
        """Restituisce i dettagli dell'aspirazione corrente."""
        if not self.current_aspiration:
            return None
        return {
            "name": self.current_aspiration,
            "progress": self.aspiration_progress, # Valore da 0.0 a 1.0
            "is_completed": self.is_completed
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serializza lo stato delle aspirazioni."""
        return {
            "current_aspiration": self.current_aspiration,
            "aspiration_progress": self.aspiration_progress,
            "is_completed": self.is_completed
        }

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]], character_owner: 'Character') -> 'AspirationComponent':
        """Crea un'istanza di AspirationComponent da dati serializzati."""
        instance = cls(character_owner) # Crea un'istanza (che potrebbe scegliere un'aspirazione iniziale)
        if data:
            instance.current_aspiration = data.get("current_aspiration") # Sovrascrive se presente
            instance.aspiration_progress = float(data.get("aspiration_progress", 0.0))
            instance.is_completed = data.get("is_completed", False)

            # Se non c'è un'aspirazione corrente caricata e non è completata, scegline una nuova.
            # Questo evita che un NPC caricato rimanga senza aspirazione se non ne aveva una salvata.
            if not instance.current_aspiration and not instance.is_completed:
                instance._select_initial_aspiration()
        
        if DEBUG_ASPIRATION and data:
            logger.debug(f"AspirationComponent per {character_owner.name} caricato. Aspirazione: {instance.current_aspiration}, Progresso: {instance.aspiration_progress:.2f}")
        return instance