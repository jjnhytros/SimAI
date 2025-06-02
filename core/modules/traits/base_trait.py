# core/modules/traits/base_trait.py
"""
Definizione della classe base astratta per tutti i Tratti di Personalità degli NPC.
Riferimento TODO: IV.3.b, I.2.e.i
"""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from core.enums.trait_types import TraitType # Importa l'enum appena creato

if TYPE_CHECKING:
    from core.character import Character
    from core.enums import NeedType, ActionType
    # Potrebbe servire importare anche ActionType o classi Azione specifiche
    # from core.modules.actions import BaseAction

class BaseTrait(ABC):
    """
    Classe base astratta per i tratti di personalità.
    Ogni tratto specifico erediterà da questa classe e implementerà
    i metodi per definire i suoi effetti.
    """
    def __init__(self, trait_type: TraitType, character_owner: 'Character'):
        self._trait_type: TraitType = trait_type
        self._character_owner: 'Character' = character_owner

    @property
    def trait_type(self) -> TraitType:
        """Restituisce il tipo di tratto (membro dell'enum TraitType)."""
        return self._trait_type

    @property
    def name(self) -> str:
        """Restituisce il nome del tratto (dall'enum)."""
        return self._trait_type.name
    
    @property
    def display_name(self) -> str:
        """Restituisce il nome visualizzabile del tratto."""
        if hasattr(self._trait_type, 'display_name_it'):
            return self._trait_type.display_name_it()
        return self.name.replace("_", " ").capitalize()

    # @abstractmethod
    # def get_description(self) -> str:
    #     """Restituisce una descrizione testuale del tratto e dei suoi effetti."""
    #     # Potrebbe essere caricata da un file di configurazione o definita nelle sottoclassi
    #     pass

    # --- Esempi di metodi che le sottoclassi potrebbero implementare ---
    # Questi sono solo esempi; la struttura esatta degli effetti dei tratti
    # dipenderà da come vogliamo che interagiscano con gli altri sistemi.

    def get_need_decay_modifier(self, need_type: 'NeedType', base_decay_rate: float) -> float:
        """
        Restituisce un moltiplicatore per il tasso di decadimento di un bisogno specifico.
        Default: nessun modificatore (restituisce il tasso base).
        Le sottoclassi sovrascriveranno questo per specifici bisogni.
        Un valore > 1.0 accelera il decadimento (se il tasso base è negativo).
        Un valore < 1.0 rallenta il decadimento.
        Un valore di 0 blocca il decadimento (usare con cautela).
        """
        return base_decay_rate # Nessuna modifica di default

    def get_need_satisfaction_modifier(self, need_type: 'NeedType', base_satisfaction_gain: float) -> float:
        """
        Restituisce un moltiplicatore per il guadagno di soddisfazione di un bisogno da un'azione.
        Default: nessun modificatore.
        """
        return base_satisfaction_gain # Nessuna modifica di default

    def get_need_urgency_modifier(self, need_type: 'NeedType', current_urgency_score: float) -> float:
        """
        Modifica il punteggio di urgenza calcolato per un bisogno.
        Le sottoclassi possono sovrascrivere questo per aumentare o diminuire
        l'urgenza percepita di certi bisogni.
        Default: nessun modificatore.
        """
        return current_urgency_score # Restituisce l'urgenza invariata di default

    def get_action_preference_modifier(self, action_type: 'ActionType', character: 'Character') -> float:
        """
        Restituisce un moltiplicatore per la "desiderabilità" di un tipo di azione.
        Valori > 1.0 aumentano la preferenza, < 1.0 la diminuiscono.
        Default: 1.0 (nessuna modifica).
        Le sottoclassi sovrascriveranno questo.
        'character' è l'NPC che possiede il tratto, per accesso contestuale se necessario.
        """
        return 1.0

    def get_action_choice_weight_modifier(self, action_type_name: str, base_weight: float) -> float:
        """
        Restituisce un moltiplicatore per il peso/priorità di una specifica azione
        nella logica decisionale dell'IA.
        Default: nessun modificatore.
        """
        return base_weight # Nessuna modifica di default
        
    # def on_social_interaction(self, target: 'Character', interaction_type: 'SocialInteractionType') -> Optional[Dict[str, Any]]:
    #     """
    #     Chiamato quando l'NPC con questo tratto partecipa a un'interazione sociale.
    #     Può modificare l'esito, le reazioni, o triggerare effetti specifici.
    #     Restituisce un dizionario di modificatori o None.
    #     """
    #     return None

    # def on_skill_gain_modifier(self, skill_type: 'SkillType', base_gain_rate: float) -> float:
    #     """Modifica il tasso di apprendimento di una skill."""
    #     return base_gain_rate

    def __str__(self) -> str:
        return self.display_name