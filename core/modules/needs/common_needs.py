# core/modules/needs/common_needs.py
from typing import Optional

from core.enums import NeedType
from core import settings
from .need_base import BaseNeed

class HungerNeed(BaseNeed):
    def __init__(self, p_need_type: NeedType = NeedType.HUNGER, initial_value: Optional[float] = None):
        # Il parametro qui si chiama p_need_type per coerenza con BaseNeed, anche se non strettamente necessario
        # se la chiamata da Character è posizionale e il nome del parametro qui non crea ambiguità.
        # Tuttavia, l'errore indica che HungerNeed riceve un 'need_type' come keyword.
        # Per sicurezza, assicuriamoci che il primo parametro qui non si chiami 'need_type'
        # se la chiamata da Character è stata erroneamente fatta con keyword.
        #
        # Se la chiamata da Character è: need_class_map[need_type_enum](need_type_enum)
        # E HungerNeed.__init__ è: def __init__(self, actual_need_type: NeedType = NeedType.HUNGER, ...):
        # Allora 'actual_need_type' riceverà 'need_type_enum'.
        #
        # Manteniamo la firma precedente ma assicuriamoci che BaseNeed sia chiamata correttamente:
        # def __init__(self, need_type_arg: NeedType = NeedType.HUNGER, initial_value: Optional[float] = None):
        #     decay_rate = settings.NEED_DECAY_RATES.get(NeedType.HUNGER.name, 0.0)
        #     super().__init__(p_need_type=need_type_arg, initial_value=initial_value, decay_rate_per_hour=decay_rate)

        # Andiamo con la correzione più diretta: i costruttori delle classi concrete
        # prendono il tipo come primo argomento posizionale (che Character passa) e lo
        # passano a BaseNeed usando p_need_type.

        # Il parametro ricevuto da Character._initialize_needs è il primo argomento posizionale.
        # Chiamiamolo 'received_need_type' per chiarezza qui.
        # Il valore di default per 'received_need_type' assicura che il tipo sia corretto se non passato,
        # ma Character._initialize_needs lo passa sempre.
        decay_rate = settings.NEED_DECAY_RATES.get(NeedType.HUNGER.name, 0.0)
        super().__init__(p_need_type=p_need_type, initial_value=initial_value, decay_rate_per_hour=decay_rate)

class EnergyNeed(BaseNeed):
    def __init__(self, p_need_type: NeedType = NeedType.ENERGY, initial_value: Optional[float] = None):
        decay_rate = settings.NEED_DECAY_RATES.get(NeedType.ENERGY.name, 0.0)
        super().__init__(p_need_type=p_need_type, initial_value=initial_value, decay_rate_per_hour=decay_rate)

class BladderNeed(BaseNeed):
    def __init__(self, p_need_type: NeedType = NeedType.BLADDER, initial_value: Optional[float] = None):
        decay_rate = settings.NEED_DECAY_RATES.get(NeedType.BLADDER.name, 0.0)
        super().__init__(p_need_type=p_need_type, initial_value=initial_value, decay_rate_per_hour=decay_rate)

class HygieneNeed(BaseNeed):
    def __init__(self, p_need_type: NeedType = NeedType.HYGIENE, initial_value: Optional[float] = None):
        decay_rate = settings.NEED_DECAY_RATES.get(NeedType.HYGIENE.name, 0.0)
        super().__init__(p_need_type=p_need_type, initial_value=initial_value, decay_rate_per_hour=decay_rate)

class ThirstNeed(BaseNeed):
    def __init__(self, p_need_type: NeedType = NeedType.THIRST, initial_value: Optional[float] = None):
        decay_rate = settings.NEED_DECAY_RATES.get(NeedType.THIRST.name, 0.0)
        if NeedType.THIRST.name not in settings.NEED_DECAY_RATES and settings.DEBUG_MODE:
            print(f"    [WARN - ThirstNeed Init] Tasso di decadimento per THIRST non trovato in settings.NEED_DECAY_RATES. Userà 0.0.")
        super().__init__(p_need_type=p_need_type, initial_value=initial_value, decay_rate_per_hour=decay_rate)

class SocialNeed(BaseNeed):
    def __init__(self, p_need_type: NeedType = NeedType.SOCIAL, initial_value: Optional[float] = None):
        decay_rate = settings.NEED_DECAY_RATES.get(NeedType.SOCIAL.name, 0.0)
        super().__init__(p_need_type=p_need_type, initial_value=initial_value, decay_rate_per_hour=decay_rate)

class FunNeed(BaseNeed):
    def __init__(self, p_need_type: NeedType = NeedType.FUN, initial_value: Optional[float] = None):
        decay_rate = settings.NEED_DECAY_RATES.get(NeedType.FUN.name, 0.0)
        super().__init__(p_need_type=p_need_type, initial_value=initial_value, decay_rate_per_hour=decay_rate)

class IntimacyNeed(BaseNeed):
    def __init__(self, p_need_type: NeedType = NeedType.INTIMACY, initial_value: Optional[float] = None):
        decay_rate = settings.NEED_DECAY_RATES.get(NeedType.INTIMACY.name, 0.0)
        super().__init__(p_need_type=p_need_type, initial_value=initial_value, decay_rate_per_hour=decay_rate)

    def decay(self, fraction_of_hour_elapsed: float,
            character_age_days: Optional[int] = None,
            character_name_for_log: Optional[str] = None):
        if character_age_days is not None and \
        character_age_days < settings.MIN_AGE_FOR_INTIMACY_DAYS:
            return
        super().decay(fraction_of_hour_elapsed, character_name_for_log=character_name_for_log)

class ComfortNeed(BaseNeed):
    def __init__(self, p_need_type: NeedType = NeedType.COMFORT, initial_value: Optional[float] = None):
        decay_rate = settings.NEED_DECAY_RATES.get(NeedType.COMFORT.name, 0.0)
        super().__init__(p_need_type=p_need_type, initial_value=initial_value, decay_rate_per_hour=decay_rate)

class EnvironmentNeed(BaseNeed):
    def __init__(self, p_need_type: NeedType = NeedType.ENVIRONMENT, initial_value: Optional[float] = None):
        decay_rate = settings.NEED_DECAY_RATES.get(NeedType.ENVIRONMENT.name, 0.0)
        super().__init__(p_need_type=p_need_type, initial_value=initial_value, decay_rate_per_hour=decay_rate)

class SafetyNeed(BaseNeed):
    def __init__(self, p_need_type: NeedType = NeedType.SAFETY, initial_value: Optional[float] = None):
        decay_rate = settings.NEED_DECAY_RATES.get(NeedType.SAFETY.name, 0.0)
        super().__init__(p_need_type=p_need_type, initial_value=initial_value, decay_rate_per_hour=decay_rate)

class CreativityNeed(BaseNeed):
    def __init__(self, p_need_type: NeedType = NeedType.CREATIVITY, initial_value: Optional[float] = None):
        decay_rate = settings.NEED_DECAY_RATES.get(NeedType.CREATIVITY.name, 0.0)
        super().__init__(p_need_type=p_need_type, initial_value=initial_value, decay_rate_per_hour=decay_rate)

class LearningNeed(BaseNeed):
    def __init__(self, p_need_type: NeedType = NeedType.LEARNING, initial_value: Optional[float] = None):
        decay_rate = settings.NEED_DECAY_RATES.get(NeedType.LEARNING.name, 0.0)
        super().__init__(p_need_type=p_need_type, initial_value=initial_value, decay_rate_per_hour=decay_rate)

class SpiritualityNeed(BaseNeed):
    def __init__(self, p_need_type: NeedType = NeedType.SPIRITUALITY, initial_value: Optional[float] = None):
        decay_rate = settings.NEED_DECAY_RATES.get(NeedType.SPIRITUALITY.name, 0.0)
        super().__init__(p_need_type=p_need_type, initial_value=initial_value, decay_rate_per_hour=decay_rate)

class AutonomyNeed(BaseNeed):
    def __init__(self, p_need_type: NeedType = NeedType.AUTONOMY, initial_value: Optional[float] = None):
        decay_rate = settings.NEED_DECAY_RATES.get(NeedType.AUTONOMY.name, 0.0)
        super().__init__(p_need_type=p_need_type, initial_value=initial_value, decay_rate_per_hour=decay_rate)

class AchievementNeed(BaseNeed):
    def __init__(self, p_need_type: NeedType = NeedType.ACHIEVEMENT, initial_value: Optional[float] = None):
        decay_rate = settings.NEED_DECAY_RATES.get(NeedType.ACHIEVEMENT.name, 0.0)
        super().__init__(p_need_type=p_need_type, initial_value=initial_value, decay_rate_per_hour=decay_rate)