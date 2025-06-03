# core/enums/action_types.py
"""
Definizione dell'Enum ActionType per i tipi di azione.
"""
from enum import Enum, auto
from typing import cast

class ActionType(Enum):
    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        # Usa il nome della chiave come valore, ma in formato leggibile per i log
        processed_name = name.replace("ACTION_", "")
        return ' '.join(word.capitalize() for word in processed_name.split('_'))

    # Azioni di base per i bisogni
    ACTION_EAT = auto()
    ACTION_SLEEP = auto()
    ACTION_USE_BATHROOM = auto()
    ACTION_HAVE_FUN = auto()
    ACTION_DRINK = auto()

    # Azioni Sociali
    ACTION_SOCIALIZE_CHAT = auto()
    ACTION_SOCIALIZE_COMPLIMENT = auto()
    ACTION_SOCIALIZE_INSULT = auto()
    ACTION_SOCIALIZE_TELL_JOKE = auto()
    ACTION_SOCIALIZE_PROPOSE_INTIMACY = auto()
    ACTION_ENGAGE_INTIMACY = auto()

    # Azioni Lavorative/Scolastiche
    ACTION_GO_TO_WORK = auto()
    ACTION_WORK = auto()
    ACTION_GO_TO_SCHOOL = auto()
    ACTION_STUDY = auto()

    # Azioni Varie
    ACTION_IDLE = auto() # Azione di default quando non c'è nulla da fare

    @property
    def action_type_name(self) -> str:
        """Restituisce il valore stringa dell'azione, che è il nome formattato."""
        return cast(str, self.value)
