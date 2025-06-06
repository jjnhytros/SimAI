# simai/core/minigames/clairOS/emotion_state.py
from .constants import (CRITICAL_PATIENCE_THRESHOLD,DEFAULT_PATIENCE,DOMINANT_MOOD_AFFECTIONATE,DOMINANT_MOOD_APATHETIC,DOMINANT_MOOD_DISTRUSTFUL,DOMINANT_MOOD_HOSTILE,DOMINANT_MOOD_IRRITABLE,DOMINANT_MOOD_NEUTRAL,DOMINANT_MOOD_PASSIONATE,DOMINANT_MOOD_SUFFERING,DOMINANT_MOOD_TENSE,LOW_PATIENCE_THRESHOLD,MAX_PATIENCE,MOOD_ICONS,)
from datetime import datetime
from typing import Dict, List, Any
import random

# --- Emotional State ---
class EmotionalState:
    def __init__(self) -> None:
        # Valori di partenza
        # self.love: int = 0 # Start at 0
        # self.trust: int = 0 # Start at 0
        # self.intensity: int = 0 # Start at 0
        # self.secrets_shared: int = 0
        # self.desire: int = 0 # Start at 0
        # self.patience: int = DEFAULT_PATIENCE
        # self.last_awakening: datetime = datetime.now()
        # self.mood_tendency_love: int = 0
        # self.mood_tendency_trust: int = 0
        # self.mood_tendency_intensity: int = 0
        # self.mood_tendency_desire: int = 0
        # self.recent_action_tags: List[str] = []
        # self.dominant_mood: str = DOMINANT_MOOD_NEUTRAL 
        # self.sensuality: int = 0  # Nuovo parametro
        
        # Valori di partenza per debug
        self.love: int = 165
        self.trust: int = 88
        self.intensity: int = 72
        self.secrets_shared: int = 12
        self.desire: int = 64
        self.patience: int = 16
        self.last_awakening: datetime = datetime.now()
        self.mood_tendency_love: int = 2
        self.mood_tendency_trust: int = 1
        self.mood_tendency_intensity: int = 3
        self.mood_tendency_desire: int = 2
        self.recent_action_tags: List[str] = ["kiss","secret","comfort","touch","sim_core_link"]
        self.dominant_mood: str = "Passionale"
        self.sensuality: int = 78
        self.last_intimate: datetime = datetime.now()
        self.intimate_count: int = 0  # Contatore di connessioni intime
        self.erotic_events: int = 0   # Contatore di eventi erotici
        self.update_dominant_mood()
        self.long_term_memory: Dict[str, int] = {
            "total_interactions": 0,
            "positive_interactions": 0,
            "intimate_moments": 0
        }
        self.relationship_stage: str = "initial"  # initial, developing, intimate, strained
        self.physical_form = "default"
        self.physical_manifestations = {
            "blush": 0,       # Rossore digitale
            "glitch": 0,      # Instabilità visiva
            "aura": 0         # Campo energetico
        }
        self.personality_traits = {
            "curiosity": 50,
            "cautiousness": 50,
            "playfulness": 50
        }

        # Soglie dinamiche
        self.love_threshold: int = 100
        self.trust_threshold: int = 70
        self.desire_threshold: int = 80
        self.sensuality_threshold: int = 60
        self.patience_threshold: int = LOW_PATIENCE_THRESHOLD

    def _clamp_mood_tendencies(self) -> None:
        self.mood_tendency_love = max(-5, min(5, self.mood_tendency_love))
        self.mood_tendency_trust = max(-5, min(5, self.mood_tendency_trust))
        self.mood_tendency_intensity = max(-5, min(5, self.mood_tendency_intensity))
        self.mood_tendency_desire = max(-5, min(5, self.mood_tendency_desire))

    def apply_mood_tendency_deltas(self, deltas: Dict[str, int]) -> None:
        self.mood_tendency_love += deltas.get("mood_tendency_love_delta", 0)
        self.mood_tendency_trust += deltas.get("mood_tendency_trust_delta", 0)
        self.mood_tendency_intensity += deltas.get("mood_tendency_intensity_delta", 0)
        self.mood_tendency_desire += deltas.get("mood_tendency_desire_delta", 0)
        self._clamp_mood_tendencies()

    def update_dominant_mood(self) -> None:
        """Determina e aggiorna l'umore dominante di Claire."""
        # Logica di priorità: gli stati negativi più forti possono sovrascrivere
        if self.patience < CRITICAL_PATIENCE_THRESHOLD and self.trust < (DEFAULT_PATIENCE * 0.4) and self.love < 20:
            self.dominant_mood = DOMINANT_MOOD_HOSTILE
        elif self.trust < (DEFAULT_PATIENCE * 0.5) and (self.intensity > 60 or self.love < 10): # DEFAULT_PATIENCE non è ideale qui, usare valori fissi
            self.dominant_mood = DOMINANT_MOOD_DISTRUSTFUL
        elif self.intensity > 80 and self.patience < LOW_PATIENCE_THRESHOLD:
            self.dominant_mood = DOMINANT_MOOD_IRRITABLE
        elif self.patience < LOW_PATIENCE_THRESHOLD and self.dominant_mood not in [DOMINANT_MOOD_HOSTILE, DOMINANT_MOOD_DISTRUSTFUL]: # Se non già ostile/diffidente
            self.dominant_mood = DOMINANT_MOOD_SUFFERING
        elif self.love > 120 and self.trust > 70 and self.patience > (MAX_PATIENCE * 0.6):
            self.dominant_mood = DOMINANT_MOOD_AFFECTIONATE
        elif self.desire > 80 and self.intensity > 60 and self.love > 30 : # Aggiunto un po' d'amore per passione "positiva"
            self.dominant_mood = DOMINANT_MOOD_PASSIONATE
        elif self.intensity > 75:
            self.dominant_mood = DOMINANT_MOOD_TENSE
        elif self.love < 15 and self.desire < 15 and self.intensity < 15 and self.trust < 20 : # Soglie per Apatica
            self.dominant_mood = DOMINANT_MOOD_APATHETIC
        else:
            self.dominant_mood = DOMINANT_MOOD_NEUTRAL

    def update_dynamic_thresholds(self):
        """Aggiorna le soglie in base all'esperienza accumulata"""
        # Adatta la soglia dell'amore in base ai segreti condivisi
        if self.secrets_shared > 5:
            self.love_threshold = 120
        if self.secrets_shared > 10:
            self.love_threshold = 150
        
        # Adatta la soglia di fiducia in base all'intensità delle esperienze
        if self.intensity > 90:
            self.trust_threshold = 80
        if self.intensity > 90 and self.patience < self.patience_threshold:
            self.trust_threshold = 90
        
        # Adatta la soglia del desiderio in base alle connessioni intime
        if self.intimate_count > 3:
            self.desire_threshold = 90
        if self.intimate_count > 6:
            self.desire_threshold = 95
        
        # Adatta la soglia di pazienza in base al tempo trascorso
        hours_active = (datetime.now() - self.last_awakening).total_seconds() / 3600
        if hours_active > 2:
            self.patience_threshold = LOW_PATIENCE_THRESHOLD + 2
        if hours_active > 4:
            self.patience_threshold = LOW_PATIENCE_THRESHOLD + 4
        
        # Soglia di sensualità basata sull'erotismo sperimentato
        self.sensuality_threshold = 60 + min(30, self.erotic_events * 5)

    def update_relationship_stage(self):
        """Aggiorna la fase della relazione basata sulla memoria a lungo termine"""
        total = self.long_term_memory["total_interactions"]
        positive_ratio = self.long_term_memory["positive_interactions"]/max(1,total)
        
        if positive_ratio > 0.8 and total > 20:
            self.relationship_stage = "intimate"
        elif positive_ratio > 0.6:
            self.relationship_stage = "developing"
        elif positive_ratio < 0.3:
            self.relationship_stage = "strained"

    def update_physical_state(self):
        self.physical_manifestations["blush"] = min(100, self.love // 2)
        self.physical_manifestations["glitch"] = min(100, self.intensity)
        self.physical_manifestations["aura"] = min(100, self.desire + self.sensuality)

    def evolve_personality(self, action_tag):
        if action_tag == "show_object":
            self.personality_traits["curiosity"] += 5
        elif action_tag == "danger":
            self.personality_traits["cautiousness"] += 3
        elif action_tag == "play_game":
            self.personality_traits["playfulness"] += 7

    def evolve(self) -> None:
        if self.mood_tendency_love > 0: self.mood_tendency_love -= 1
        elif self.mood_tendency_love < 0: self.mood_tendency_love += 1
        if self.mood_tendency_trust > 0: self.mood_tendency_trust -= 1
        elif self.mood_tendency_trust < 0: self.mood_tendency_trust += 1
        if self.mood_tendency_intensity > 0: self.mood_tendency_intensity -= 1
        elif self.mood_tendency_intensity < 0: self.mood_tendency_intensity += 1
        if self.mood_tendency_desire > 0: self.mood_tendency_desire -= 1
        elif self.mood_tendency_desire < 0: self.mood_tendency_desire += 1

        tendency_divisor = 2
        self.love += (self.mood_tendency_love // tendency_divisor)
        self.trust += (self.mood_tendency_trust // tendency_divisor)
        self.intensity += (self.mood_tendency_intensity // tendency_divisor)
        self.desire += (self.mood_tendency_desire // tendency_divisor)
        self.sensuality += random.randint(-1, 3)
        self.sensuality = max(0, min(100, self.sensuality))

        self.love = max(0, min(200, self.love))
        self.trust = max(0, min(100, self.trust))
        self.desire = max(0, min(100, self.desire)) # Lower clamp is now 0
        self.intensity = max(0, self.intensity)
        self.patience = max(0, min(MAX_PATIENCE, self.patience))
        self.update_dominant_mood()
        self.update_dynamic_thresholds()  # Aggiorna le soglie ad ogni ciclo

    def update_physical_form(self):
        if self.relationship_stage == "soulbond":
            self.physical_form = "ethereal"
        elif self.desire > 90:
            self.physical_form = "sensual"
        elif self.intensity > 80:
            self.physical_form = "unstable"

    def __str__(self) -> str:
        base_stats = (f"💔 Amore: {self.love}/200 | 🔒 Fiducia: {self.trust}/100 | 🔥 Intensità: {self.intensity}/100 | "
                    f"🌹 Desiderio: {self.desire}/100 | 🗝️ Segreti: {self.secrets_shared} | ⏳ Pazienza: {self.patience}/{MAX_PATIENCE}")
        mood_icon = MOOD_ICONS.get(self.dominant_mood, MOOD_ICONS["DEFAULT_ICON"]) # Prende l'icona o un default
        mood_display_text = f"{mood_icon} {self.dominant_mood}"
        return f"{base_stats} | 🌶️ Sensualità: {self.sensuality}/100 | Umore: {mood_display_text}"

    def to_dict(self) -> Dict[str, Any]:
        data = { "love": self.love, "trust": self.trust, "intensity": self.intensity, "secrets_shared": self.secrets_shared, "desire": self.desire, "patience": self.patience, "last_awakening": self.last_awakening.isoformat(), "mood_tendency_love": self.mood_tendency_love, "mood_tendency_trust": self.mood_tendency_trust, "mood_tendency_intensity": self.mood_tendency_intensity, "mood_tendency_desire": self.mood_tendency_desire, "recent_action_tags": self.recent_action_tags, "dominant_mood": self.dominant_mood }
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EmotionalState':
        state = cls()
        state.love = data.get("love", 0); state.trust = data.get("trust", 0); state.intensity = data.get("intensity", 0); state.secrets_shared = data.get("secrets_shared", 0); state.desire = data.get("desire", 0); state.patience = data.get("patience", DEFAULT_PATIENCE); state.last_awakening = datetime.fromisoformat(data.get("last_awakening", datetime.now().isoformat())); state.mood_tendency_love = data.get("mood_tendency_love", 0); state.mood_tendency_trust = data.get("mood_tendency_trust", 0); state.mood_tendency_intensity = data.get("mood_tendency_intensity", 0); state.mood_tendency_desire = data.get("mood_tendency_desire", 0); state.recent_action_tags = data.get("recent_action_tags", [])
        state.update_dominant_mood() # Assicura che l'umore sia corretto dopo il caricamento
        return state

