# core/modules/needs/common_needs.py
"""
Definizione delle classi concrete per tutti i bisogni degli NPC.
Ereditano da BaseNeed.
"""
from typing import Optional

from core.enums import NeedType
from core import settings
from .need_base import BaseNeed # Importa la classe base dal modulo need_base.py

# Bisogni Primari / Fisiologici
class HungerNeed(BaseNeed):
    def __init__(self, initial_value: Optional[float] = None):
        decay_rate = settings.NEED_DECAY_RATES.get(NeedType.HUNGER.name, 0.0)
        super().__init__(NeedType.HUNGER, initial_value, decay_rate_per_hour=decay_rate)

class EnergyNeed(BaseNeed):
    def __init__(self, initial_value: Optional[float] = None):
        decay_rate = settings.NEED_DECAY_RATES.get(NeedType.ENERGY.name, 0.0)
        super().__init__(NeedType.ENERGY, initial_value, decay_rate_per_hour=decay_rate)

class BladderNeed(BaseNeed):
    def __init__(self, initial_value: Optional[float] = None):
        decay_rate = settings.NEED_DECAY_RATES.get(NeedType.BLADDER.name, 0.0)
        super().__init__(NeedType.BLADDER, initial_value, decay_rate_per_hour=decay_rate)

class HygieneNeed(BaseNeed):
    def __init__(self, initial_value: Optional[float] = None):
        decay_rate = settings.NEED_DECAY_RATES.get(NeedType.HYGIENE.name, 0.0)
        super().__init__(NeedType.HYGIENE, initial_value, decay_rate_per_hour=decay_rate)

# Bisogni Sociali / Emotivi
class SocialNeed(BaseNeed):
    def __init__(self, initial_value: Optional[float] = None):
        decay_rate = settings.NEED_DECAY_RATES.get(NeedType.SOCIAL.name, 0.0)
        super().__init__(NeedType.SOCIAL, initial_value, decay_rate_per_hour=decay_rate)

class FunNeed(BaseNeed):
    def __init__(self, initial_value: Optional[float] = None):
        decay_rate = settings.NEED_DECAY_RATES.get(NeedType.FUN.name, 0.0)
        super().__init__(NeedType.FUN, initial_value, decay_rate_per_hour=decay_rate)

class IntimacyNeed(BaseNeed):
    def __init__(self, initial_value: Optional[float] = None):
        decay_rate = settings.NEED_DECAY_RATES.get(NeedType.INTIMACY.name, 0.0)
        super().__init__(NeedType.INTIMACY, initial_value, decay_rate_per_hour=decay_rate)

    def decay(self, fraction_of_hour_elapsed: float, 
              character_age_days: Optional[int] = None, # Aggiunto per il controllo età
              character_name_for_log: Optional[str] = None):
        """
        Sovrascrive il metodo decay per implementare la logica condizionale
        basata sull'età del personaggio.
        """
        if character_age_days is not None and \
           character_age_days < settings.MIN_AGE_FOR_INTIMACY_DAYS:
            # Non decade se l'NPC è troppo giovane
            # if settings.DEBUG_MODE and character_name_for_log:
            #     print(f"    [Need INTIMACY - {character_name_for_log}] Salto decadimento (troppo giovane: {character_age_days}gg).")
            return 
        # Se l'età è appropriata, chiama il metodo decay della classe base
        super().decay(fraction_of_hour_elapsed, character_name_for_log=character_name_for_log)

# Bisogni di Livello Superiore / Ambientali
class ComfortNeed(BaseNeed):
    def __init__(self, initial_value: Optional[float] = None):
        decay_rate = settings.NEED_DECAY_RATES.get(NeedType.COMFORT.name, 0.0)
        super().__init__(NeedType.COMFORT, initial_value, decay_rate_per_hour=decay_rate)

class EnvironmentNeed(BaseNeed):
    def __init__(self, initial_value: Optional[float] = None):
        decay_rate = settings.NEED_DECAY_RATES.get(NeedType.ENVIRONMENT.name, 0.0)
        super().__init__(NeedType.ENVIRONMENT, initial_value, decay_rate_per_hour=decay_rate)

class SafetyNeed(BaseNeed):
    def __init__(self, initial_value: Optional[float] = None):
        decay_rate = settings.NEED_DECAY_RATES.get(NeedType.SAFETY.name, 0.0)
        super().__init__(NeedType.SAFETY, initial_value, decay_rate_per_hour=decay_rate)

class CreativityNeed(BaseNeed):
    def __init__(self, initial_value: Optional[float] = None):
        decay_rate = settings.NEED_DECAY_RATES.get(NeedType.CREATIVITY.name, 0.0)
        super().__init__(NeedType.CREATIVITY, initial_value, decay_rate_per_hour=decay_rate)

class LearningNeed(BaseNeed):
    def __init__(self, initial_value: Optional[float] = None):
        decay_rate = settings.NEED_DECAY_RATES.get(NeedType.LEARNING.name, 0.0)
        super().__init__(NeedType.LEARNING, initial_value, decay_rate_per_hour=decay_rate)

class SpiritualityNeed(BaseNeed):
    def __init__(self, initial_value: Optional[float] = None):
        decay_rate = settings.NEED_DECAY_RATES.get(NeedType.SPIRITUALITY.name, 0.0)
        super().__init__(NeedType.SPIRITUALITY, initial_value, decay_rate_per_hour=decay_rate)

class AutonomyNeed(BaseNeed):
    def __init__(self, initial_value: Optional[float] = None):
        decay_rate = settings.NEED_DECAY_RATES.get(NeedType.AUTONOMY.name, 0.0)
        super().__init__(NeedType.AUTONOMY, initial_value, decay_rate_per_hour=decay_rate)

class AchievementNeed(BaseNeed):
    def __init__(self, initial_value: Optional[float] = None):
        decay_rate = settings.NEED_DECAY_RATES.get(NeedType.ACHIEVEMENT.name, 0.0)
        super().__init__(NeedType.ACHIEVEMENT, initial_value, decay_rate_per_hour=decay_rate)