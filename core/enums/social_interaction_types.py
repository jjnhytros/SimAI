# core/enums/social_interaction_types.py
from enum import Enum, auto
"""
Definizione dell'Enum SocialInteractionType per le interazioni sociali tra NPC.
Riferimento TODO: VII.1.b
"""

class SocialInteractionType(Enum):
    """Enum per i diversi tipi di interazioni sociali che un NPC può avviare."""

    # --- Interazioni Amichevoli / Neutre ---
    CHAT_CASUAL = auto()                # Chiacchierata informale sul più e sul meno
    DEEP_CONVERSATION = auto()          # Conversazione profonda su vita, sogni, paure
    ASK_ABOUT_DAY = auto()              # Chiedere com'è andata la giornata
    SHARE_INTEREST = auto()             # Parlare di un interesse o hobby comune
    TELL_JOKE = auto()                  # Raccontare una barzelletta
    TELL_STORY = auto()                 # Raccontare una storia o un aneddoto
    COMPLIMENT = auto()                 # Fare un complimento generico (es. sulla personalità)
    OFFER_COMFORT = auto()              # Offrire conforto a chi è triste
    GIVE_ADVICE = auto()                # Dare un consiglio
    SHARE_SECRET = auto()               # Condividere un segreto

    # --- Interazioni Romantiche ---
    FLIRT = auto()                      # Flirtare in modo generico (potrebbe influenzare relazione romantica)
    COMPLIMENT_APPEARANCE = auto()      # Fare un complimento specifico sull'aspetto fisico
    CONFESS_ATTRACTION = auto()         # Confessare la propria attrazione
    PROPOSE_DATE = auto()               # Chiedere di uscire per un appuntamento
    PROPOSE_INTIMACY = auto()           # Proporre un momento di intimità
    PROPOSE_MARRIAGE = auto()           # Proposta di matrimonio

    # --- Interazioni Negative / Conflittuali ---
    ARGUE = auto()                      # Discutere animatamente / Litigare (effetto negativo su relazione/sociale)
    INSULT = auto()                     # Insultare
    CRITICIZE = auto()                  # Criticare
    YELL_AT = auto()                    # Urlare contro qualcuno
    GOSSIP_ABOUT_ANOTHER_NPC = auto()   # Spettegolare su un terzo NPC

    # --- Interazioni Familiari ---
    PARENTAL_ADVICE = auto()            # Un genitore dà un consiglio a un figlio
    SIBLING_TEASING = auto()            # Stuzzicare un fratello/sorella in modo bonario o fastidioso
    ASK_FOR_HELP_HOMEWORK = auto()      # Un bambino/adolescente chiede aiuto per i compiti

    # --- Interazioni Uniche / Contestuali ---
    DISCUSS_ART_THEORY = auto()         # Discutere di teoria dell'arte (tipico del Quartiere delle Muse)
    DEBATE_POLITICS = auto()            # Dibattere di politica (tipico della Cittadella)

    def display_name_it(self) -> str:
        """Restituisce un nome leggibile in italiano per il tipo di interazione."""
        mapping = {
            SocialInteractionType.CHAT_CASUAL: "Chiacchierata Informale",
            SocialInteractionType.DEEP_CONVERSATION: "Conversazione Profonda",
            SocialInteractionType.ASK_ABOUT_DAY: "Chiedere della Giornata",
            SocialInteractionType.SHARE_INTEREST: "Parlare di Interessi",
            SocialInteractionType.TELL_JOKE: "Raccontare una Barzelletta",
            SocialInteractionType.TELL_STORY: "Raccontare una Storia",
            SocialInteractionType.COMPLIMENT: "Fare un Complimento",
            SocialInteractionType.OFFER_COMFORT: "Offrire Conforto",
            SocialInteractionType.GIVE_ADVICE: "Dare un Consiglio",
            SocialInteractionType.SHARE_SECRET: "Condividere un Segreto",
            SocialInteractionType.FLIRT: "Flirtare",
            SocialInteractionType.COMPLIMENT_APPEARANCE: "Fare un Complimento sull'Aspetto",
            SocialInteractionType.CONFESS_ATTRACTION: "Confessare Attrazione",
            SocialInteractionType.PROPOSE_DATE: "Chiedere un Appuntamento",
            SocialInteractionType.PROPOSE_INTIMACY: "Proporre Intimità",
            SocialInteractionType.PROPOSE_MARRIAGE: "Proposta di Matrimonio",
            SocialInteractionType.ARGUE: "Litigare",
            SocialInteractionType.INSULT: "Insultare",
            SocialInteractionType.CRITICIZE: "Criticare",
            SocialInteractionType.YELL_AT: "Urlare Contro",
            SocialInteractionType.GOSSIP_ABOUT_ANOTHER_NPC: "Spettegolare su Qualcun Altro",
            SocialInteractionType.PARENTAL_ADVICE: "Consiglio da Genitore",
            SocialInteractionType.SIBLING_TEASING: "Prendere in Giro un Parente",
            SocialInteractionType.ASK_FOR_HELP_HOMEWORK: "Chiedere Aiuto per i Compiti",
            SocialInteractionType.DISCUSS_ART_THEORY: "Discutere di Arte",
            SocialInteractionType.DEBATE_POLITICS: "Dibattere di Politica",
        }
        return mapping.get(self, self.name.replace("_", " ").title())
