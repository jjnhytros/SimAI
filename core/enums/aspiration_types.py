# core/enums/aspiration_types.py
"""
Definizione dell'Enum 'AspirationType' per rappresentare le aspirazioni
a lungo termine degli NPC in SimAI.
"""
from enum import Enum, auto

class AspirationType(Enum):
    """
    Rappresenta le diverse aspirazioni o obiettivi di vita a lungo termine di un NPC.
    Riferimento TODO: IV.3.a.i
    """
    ALTRUIST = auto()
    FITNESS_GURU = auto()
    MASTER_OF_SKILL = auto()
    CREATIVE_VISIONARY = auto()
    BODY_PERFECTIONIST = auto()     # Perfezionista del Corpo (es. massima forma fisica, salute ottimale)
    CREATIVE_SOUL = auto()          # Anima Creativa (es. creare capolavori, esprimersi artisticamente)
    FAMILY_ORIENTED = auto()        # Orientato alla Famiglia (es. grande famiglia felice, figli)
    HEDONIST_EPICUREAN = auto()     # Edonista / Epicureo (es. massimizzare il piacere e le esperienze piacevoli)
    KNOWLEDGE_SEEKER = auto()       # Cercatore di Conoscenza (es. imparare tutto, diventare un esperto)
    LEADER_INFLUENCER = auto()      # Leader / Influencer (es. carriera di successo, influenzare gli altri)
    PEACEFUL_EXISTENCE = auto()     # Esistenza Pacifica (es. vita tranquilla, senza stress, coltivare hobby)
    PHILANTHROPIST_ALTRUIST = auto() # Filantropo / Altruista (es. aiutare gli altri, migliorare la società)
    SKILL_MASTER = auto()           # Maestro di un'Abilità (es. eccellere in una specifica abilità)
    SOCIAL_BUTTERFLY = auto()       # Farfalla Sociale (es. avere molti amici, essere popolare)
    WEALTH_BUILDER = auto()         # Costruttore di Ricchezza (es. diventare ricco, sicurezza finanziaria)
    WORLD_EXPLORER = auto()         # Esploratore del Mondo (es. viaggiare, scoprire luoghi nuovi)
    # Aggiungere altre aspirazioni uniche per SimAI se necessario

    def display_name_it(self) -> str:
        # Mapping per i nomi italiani
        mapping = {
            AspirationType.ALTRUIST: "Altruista",
            AspirationType.BODY_PERFECTIONIST: "Perfezionista del Corpo",
            AspirationType.CREATIVE_SOUL: "Anima Creativa",
            AspirationType.FAMILY_ORIENTED: "Orientato alla Famiglia",
            AspirationType.FITNESS_GURU: "Guru del Fitness",
            AspirationType.HEDONIST_EPICUREAN: "Edonista ed Epicureo",
            AspirationType.KNOWLEDGE_SEEKER: "Cercatore di Conoscenza",
            AspirationType.LEADER_INFLUENCER: "Leader e Influencer",
            AspirationType.MASTER_OF_SKILL: "Maestro di Abilità",
            AspirationType.PEACEFUL_EXISTENCE: "Esistenza Pacifica",
            AspirationType.PHILANTHROPIST_ALTRUIST: "Filantropo e Altruista",
            AspirationType.SKILL_MASTER: "Maestro di un'Abilità",
            AspirationType.SOCIAL_BUTTERFLY: "Farfalla Sociale",
            AspirationType.WEALTH_BUILDER: "Costruttore di Ricchezza",
            AspirationType.WORLD_EXPLORER: "Esploratore del Mondo",
        }
        return mapping.get(self, self.name.replace("_", " ").title())