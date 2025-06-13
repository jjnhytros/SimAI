# core/modules/needs/common_needs.py
from typing import TYPE_CHECKING, Optional
from core.enums import NeedType
from .need_base import BaseNeed

if TYPE_CHECKING:
    from core.character import Character

# Usiamo un pattern più semplice per tutte le classi di bisogno standard.
# Il costruttore non fa altro che passare le informazioni alla classe base.

class HungerNeed(BaseNeed):
    def __init__(self, character_owner: 'Character', p_need_type: NeedType):
        super().__init__(character_owner, p_need_type)
        self.display_name = "Fame"

class EnergyNeed(BaseNeed):
    def __init__(self, character_owner: 'Character', p_need_type: NeedType):
        super().__init__(character_owner, p_need_type)
        self.display_name = "Energia"

class ThirstNeed(BaseNeed):
    def __init__(self, character_owner: 'Character', p_need_type: NeedType):
        super().__init__(character_owner, p_need_type)
        self.display_name = "Sete"

class StressNeed(BaseNeed):
    def __init__(self, character_owner: 'Character', p_need_type: NeedType):
        # Lo stress parte da 0, che è corretto.
        super().__init__(character_owner, p_need_type, initial_value=0.0)
        self.display_name = "Stress"

    def get_value(self) -> float:
        """Il valore di questo bisogno è direttamente legato al carico cognitivo."""
        if self.character_owner:
            return self.character_owner.cognitive_load * 100.0
        return 0.0

    def change_value(self, amount: float, is_decay_event: bool = False, character_name_for_log: Optional[str] = None):
        """Il valore dello Stress non viene modificato direttamente."""
        pass # Corretto, questo bisogno è "read-only"

class AchievementNeed(BaseNeed):
    """
    Rappresenta il bisogno di un NPC di raggiungere obiettivi e sentirsi realizzato.
    """
    def __init__(self, character_owner: 'Character', p_need_type: NeedType):
        # Chiama il costruttore della classe base, passando il proprietario e il tipo
        super().__init__(character_owner, p_need_type)
        self.display_name = "Realizzazione"

class AutonomyNeed(BaseNeed):
    def __init__(self, character_owner: 'Character', p_need_type: NeedType):
        super().__init__(character_owner, p_need_type)
        self.display_name = "Autonomia"

class BladderNeed(BaseNeed):
    def __init__(self, character_owner: 'Character', p_need_type: NeedType):
        super().__init__(character_owner, p_need_type)
        self.display_name = "Vescica"

class ComfortNeed(BaseNeed):
    def __init__(self, character_owner: 'Character', p_need_type: NeedType):
        super().__init__(character_owner, p_need_type)
        self.display_name = "Comfort"

class CreativityNeed(BaseNeed):
    def __init__(self, character_owner: 'Character', p_need_type: NeedType):
        super().__init__(character_owner, p_need_type)
        self.display_name = "Creatività"

class EnvironmentNeed(BaseNeed):
    def __init__(self, character_owner: 'Character', p_need_type: NeedType):
        super().__init__(character_owner, p_need_type)
        self.display_name = "Ambiente"

class FunNeed(BaseNeed):
    def __init__(self, character_owner: 'Character', p_need_type: NeedType):
        super().__init__(character_owner, p_need_type)
        self.display_name = "Divertimento"

class HygieneNeed(BaseNeed):
    def __init__(self, character_owner: 'Character', p_need_type: NeedType):
        super().__init__(character_owner, p_need_type)
        self.display_name = "Igiene"

class IntimacyNeed(BaseNeed):
    def __init__(self, character_owner: 'Character', p_need_type: NeedType):
        super().__init__(character_owner, p_need_type)
        self.display_name = "Intimità"

class LearningNeed(BaseNeed):
    def __init__(self, character_owner: 'Character', p_need_type: NeedType):
        super().__init__(character_owner, p_need_type)
        self.display_name = "Apprendimento"

class SafetyNeed(BaseNeed):
    def __init__(self, character_owner: 'Character', p_need_type: NeedType):
        super().__init__(character_owner, p_need_type)
        self.display_name = "Sicurezza"

class SocialNeed(BaseNeed):
    def __init__(self, character_owner: 'Character', p_need_type: NeedType):
        super().__init__(character_owner, p_need_type)
        self.display_name = "Sociale"

class SpiritualityNeed(BaseNeed):
    def __init__(self, character_owner: 'Character', p_need_type: NeedType):
        super().__init__(character_owner, p_need_type)
        self.display_name = "Spiritualità"
