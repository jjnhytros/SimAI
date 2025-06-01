# core/enums/social_interaction_types.py
"""
Definizione dell'Enum 'SocialInteractionType' per i tipi di interazione sociale.
"""
from enum import Enum, auto

class SocialInteractionType(Enum):
    ARGUE = auto()                  # Litigare (effetto negativo su relazione/sociale)
    CHAT_CASUAL = auto()            # Chiacchierata casuale, pettegolezzo leggero
    COMPLIMENT = auto()             # Fare un complimento
    DEEP_CONVERSATION = auto()      # Conversazione profonda, condividere pensieri/sentimenti
    FLIRT = auto()                  # Flirtare (potrebbe influenzare relazione romantica)
    OFFER_COMFORT = auto()          # Offrire conforto
    PROPOSE_INTIMACY = auto()       # Proposta di un momento di intimità
    SHARE_NEWS_GOSSIP = auto()      # Condividere notizie o pettegolezzi
    TELL_JOKE = auto()              # Raccontare una barzelletta
    # Aggiungere altri tipi specifici se necessario

    def display_name_it(self) -> str:
        # ... (implementa il mapping per i nomi italiani come per gli altri Enum) ...
        mapping = {
            SocialInteractionType.ARGUE: "Litigare",
            SocialInteractionType.CHAT_CASUAL: "Chiacchierata Casuale",
            SocialInteractionType.COMPLIMENT: "Fare un Complimento",
            SocialInteractionType.DEEP_CONVERSATION: "Conversazione Profonda",
            SocialInteractionType.FLIRT: "Flirtare",
            SocialInteractionType.OFFER_COMFORT: "Offrire Conforto",
            SocialInteractionType.PROPOSE_INTIMACY: "Proporre Momento Intimo",
            SocialInteractionType.SHARE_NEWS_GOSSIP: "Condividere Notizie/Pettegolezzi",
            SocialInteractionType.TELL_JOKE: "Raccontare Barzelletta",
        }
        return mapping.get(self, self.name.replace("_", " ").title())