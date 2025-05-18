# game/src/entities/components/mood_component.py
import logging
import random
from collections import deque
from typing import Dict, Any, Optional, List, TYPE_CHECKING

# Importa dal package 'game'
from game import config # Per valori di default come EMOTION_LIST

if TYPE_CHECKING:
    from game.src.entities.character import Character # Per il type hint di character_owner

logger = logging.getLogger(__name__)
DEBUG_MOOD = getattr(config, 'DEBUG_AI_ACTIVE', False) # Puoi usare un flag di debug specifico

# Valori di default se non definiti in config.py
DEFAULT_EMOTION_LIST = ["Neutro", "Felice", "Triste", "Arrabbiato", "Stressato", "Contento", "Annoiato", "Eccitato"]
DEFAULT_MOOD_VALUE_MIN = -100
DEFAULT_MOOD_VALUE_MAX = 100
DEFAULT_MOOD_STARTING_MIN_PCT = 0.3 # Percentuale del range (0 a 1) per il valore iniziale min
DEFAULT_MOOD_STARTING_MAX_PCT = 0.7 # Percentuale del range (0 a 1) per il valore iniziale max


class MoodComponent:
    def __init__(self, character_owner: 'Character'):
        """
        Inizializza il componente dell'umore/emozioni.

        Args:
            character_owner (Character): Il personaggio a cui questo componente appartiene.
        """
        self.owner: 'Character' = character_owner
        self.owner_name: str = character_owner.name if character_owner else "NPC Sconosciuto"

        self.emotion_list: List[str] = getattr(config, 'EMOTION_LIST', DEFAULT_EMOTION_LIST)
        
        # Umore generale (es. da -100 a 100)
        self.mood_value_min: float = float(getattr(config, 'MOOD_VALUE_MIN', DEFAULT_MOOD_VALUE_MIN))
        self.mood_value_max: float = float(getattr(config, 'MOOD_VALUE_MAX', DEFAULT_MOOD_VALUE_MAX))
        
        # Calcola il range per il valore iniziale dell'umore
        mood_range = self.mood_value_max - self.mood_value_min
        starting_min_val = self.mood_value_min + mood_range * getattr(config, 'MOOD_STARTING_MIN_PCT', DEFAULT_MOOD_STARTING_MIN_PCT)
        starting_max_val = self.mood_value_min + mood_range * getattr(config, 'MOOD_STARTING_MAX_PCT', DEFAULT_MOOD_STARTING_MAX_PCT)
        self.current_mood_value: float = random.uniform(starting_min_val, starting_max_val)
        
        # Emozione dominante corrente (stringa)
        self.dominant_emotion: str = self._determine_emotion_from_mood_value(self.current_mood_value)
        
        # Cronologia delle emozioni recenti (stringhe)
        self.recent_emotions_log: deque[str] = deque(maxlen=getattr(config, 'MAX_RECENT_EMOTIONS_LOG', 5))
        self.recent_emotions_log.append(self.dominant_emotion)

        # Potenziale per un sistema più complesso:
        # self.active_emotions: Dict[str, float] = {} # Es. {"felicità": 0.8, "tristezza": 0.1}
        # self.personality_traits: List[str] = [] # Es. ["Ottimista", "Irritabile"] che influenzano le reazioni

        if DEBUG_MOOD:
            logger.debug(f"MoodComponent per {self.owner_name} inizializzato. Umore: {self.current_mood_value:.1f}, Emozione: {self.dominant_emotion}")

    def _determine_emotion_from_mood_value(self, mood_value: float) -> str:
        """Determina un'emozione stringa basata sul valore numerico dell'umore."""
        # Questa è una logica molto semplice, da espandere.
        # Potresti avere soglie più definite in config.py
        # Esempio: MOOD_THRESHOLDS = {"Triste": -50, "Neutro": -10, "Contento": 10, "Felice": 50, "Eccitato": 80}
        
        if mood_value < self.mood_value_min * 0.6: return "Molto Triste" # o "Depresso"
        elif mood_value < self.mood_value_min * 0.2: return "Triste"
        elif mood_value < 0: return "Leggermente Giù"
        elif mood_value == 0: return "Neutro"
        elif mood_value > self.mood_value_max * 0.6: return "Molto Felice" # o "Euforico"
        elif mood_value > self.mood_value_max * 0.2: return "Felice"
        elif mood_value > 0: return "Contento"
        
        return random.choice(self.emotion_list) if self.emotion_list else "Neutro" # Fallback


    def update(self, dt_real_seconds: float, character_state: 'Character'):
        """
        Aggiorna lo stato dell'umore.
        Potrebbe includere decadimento dell'umore verso la neutralità,
        o reazioni a bisogni critici, eventi, interazioni.

        Args:
            dt_real_seconds (float): Tempo reale trascorso dall'ultimo frame.
            character_state (Character): L'istanza Character per accedere ad altri componenti (es. bisogni).
        """
        # Esempio: Decadimento dell'umore verso lo 0 (neutralità) nel tempo
        decay_rate_per_second = getattr(config, 'MOOD_DECAY_RATE_PER_SECOND', 0.01) # Piccola quantità
        if self.current_mood_value > 0:
            self.current_mood_value -= decay_rate_per_second * dt_real_seconds
            self.current_mood_value = max(0, self.current_mood_value) # Non scendere sotto 0 per decay positivo
        elif self.current_mood_value < 0:
            self.current_mood_value += decay_rate_per_second * dt_real_seconds
            self.current_mood_value = min(0, self.current_mood_value) # Non salire sopra 0 per decay negativo

        # Esempio: Influenza dei bisogni sull'umore
        # Questa logica potrebbe diventare molto complessa
        if character_state.needs:
            if character_state.needs.get_value("hunger") < getattr(config, "HUNGER_CRITICAL_THRESHOLD_FOR_MOOD", 20):
                self.add_mood_modifier(getattr(config, "MOOD_MODIFIER_HUNGER_CRITICAL", -0.5) * dt_real_seconds, "Fame critica")
            if character_state.needs.get_value("energy") < getattr(config, "ENERGY_CRITICAL_THRESHOLD_FOR_MOOD", 15):
                self.add_mood_modifier(getattr(config, "MOOD_MODIFIER_ENERGY_CRITICAL", -0.5) * dt_real_seconds, "Energia critica")
            # ... e così via per altri bisogni ...
            if character_state.needs.get_value("fun") > getattr(config, "FUN_HIGH_THRESHOLD_FOR_MOOD", 80) and \
               character_state.current_action in getattr(config, "FUN_ACTIONS_FOR_MOOD_BOOST", ["playing_game", "socializing_fun"]):
                self.add_mood_modifier(getattr(config, "MOOD_MODIFIER_FUN_HIGH", 0.2) * dt_real_seconds, "Molto divertimento")


        # Aggiorna l'emozione dominante
        new_dominant_emotion = self._determine_emotion_from_mood_value(self.current_mood_value)
        if new_dominant_emotion != self.dominant_emotion:
            self.dominant_emotion = new_dominant_emotion
            self.recent_emotions_log.append(self.dominant_emotion)
            if DEBUG_MOOD:
                logger.debug(f"Mood ({self.owner_name}): Emozione dominante cambiata in '{self.dominant_emotion}' (Umore: {self.current_mood_value:.1f})")

    def add_mood_modifier(self, amount: float, source_description: str):
        """
        Modifica il valore dell'umore corrente e logga la fonte.
        'amount' può essere positivo o negativo.
        """
        old_mood = self.current_mood_value
        self.current_mood_value += amount
        self.current_mood_value = max(self.mood_value_min, min(self.mood_value_max, self.current_mood_value)) # Clamp
        
        if DEBUG_MOOD and abs(old_mood - self.current_mood_value) > 0.01 : # Logga solo se c'è un cambiamento significativo
            logger.debug(f"Mood ({self.owner_name}): Modificatore umore '{source_description}' di {amount:+.1f}. Umore: {old_mood:.1f} -> {self.current_mood_value:.1f}")
        
        # L'emozione dominante verrà aggiornata nel prossimo ciclo di update()
        # o potresti aggiornarla qui se il modificatore è molto forte.

    def get_current_mood_value(self) -> float:
        return self.current_mood_value

    def get_dominant_emotion(self) -> str:
        return self.dominant_emotion
    
    def get_recent_emotions(self) -> List[str]:
        return list(self.recent_emotions_log)

    def to_dict(self) -> Dict[str, Any]:
        """Serializza lo stato dell'umore."""
        return {
            "current_mood_value": self.current_mood_value,
            "dominant_emotion": self.dominant_emotion,
            "recent_emotions_log": list(self.recent_emotions_log)
        }

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]], character_owner: 'Character') -> 'MoodComponent':
        """Crea un'istanza di MoodComponent da dati serializzati."""
        instance = cls(character_owner) # Crea un'istanza con valori di default/randomizzati
        if data:
            instance.current_mood_value = float(data.get("current_mood_value", instance.current_mood_value))
            instance.dominant_emotion = data.get("dominant_emotion", instance._determine_emotion_from_mood_value(instance.current_mood_value))
            
            saved_log = data.get("recent_emotions_log")
            if saved_log and isinstance(saved_log, list):
                instance.recent_emotions_log.clear()
                for emotion_str in saved_log:
                    instance.recent_emotions_log.append(str(emotion_str))
            elif not instance.recent_emotions_log: # Assicura che ci sia almeno l'emozione corrente se il log salvato è vuoto
                 instance.recent_emotions_log.append(instance.dominant_emotion)


        if DEBUG_MOOD and data:
            logger.debug(f"MoodComponent per {character_owner.name} caricato. Umore: {instance.current_mood_value:.1f}, Emozione: {instance.dominant_emotion}")
        return instance