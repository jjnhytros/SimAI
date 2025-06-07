# core/enums/aspiration_types.py
from enum import Enum, auto
"""
Definizione dell'Enum AspirationType per gli obiettivi a lungo termine degli NPC,
basato sulla fusione delle liste fornite.
Riferimento TODO: IV.3.a
"""

class AspirationType(Enum):
    """Enum per le diverse aspirazioni di vita degli NPC."""

    # --- Categoria: Creatività (Obiettivi Specifici) ---
    BESTSELLING_AUTHOR = auto()
    MASTER_ARTISAN = auto()
    MASTER_PAINTER = auto()
    RENOWNED_MUSICIAN = auto()

    # --- Categoria: Conoscenza (Obiettivi Specifici) ---
    ACADEMIC_EXCELLENCE = auto()
    LOREMASTER_OF_ANTHALYS = auto()
    SCIENTIFIC_BREAKTHROUGH = auto()
    SKILL_MASTER = auto()           # Padroneggiare UNA abilità specifica al massimo livello
    SKILL_POLYGLOT = auto()         # Padroneggiare TUTTE le abilità
    KNOWLEDGE_SEEKER = auto()       # Ricercatore di conoscenza

    # --- Categoria: Fortuna (Obiettivi Specifici) ---
    FABULOUSLY_WEALTHY = auto()     # Diventare favolosamente ricco
    MANSION_BARON = auto()          # Possedere la villa più grande e costosa

    # --- Categoria: Famiglia (Obiettivi Specifici) ---
    FAMILY_LEGACY = auto()          # Vedere i propri nipoti
    LARGE_FAMILY = auto()           # Avere un certo numero di figli
    SUPER_PARENT = auto()           # Crescere figli con tratti positivi

    # --- Categoria: Sociale (Obiettivi Specifici) ---
    COMMUNITY_LEADER = auto()       # Essere un pilastro della comunità
    PERFECT_HOST = auto()           # Organizzare feste leggendarie
    SOCIAL_BUTTERFLY = auto()       # Avere un gran numero di amici

    # --- Categoria: Sport e Corpo (Obiettivi Specifici) ---
    ARENA_FUSION_CHAMPION = auto()  # Vincere il campionato di Arena Fusion
    BODY_PERFECTIONIST = auto()     # Raggiungere la perfezione fisica (Max Fitness, Salute ottimale)

    # --- Categoria: Natura (Obiettivi Specifici) ---
    ANGLING_ACE = auto()            # Asso della pesca
    FREELANCE_BOTANIST = auto()     # Collezionare tutte le piante
    MASTER_GARDENER = auto()

    # --- Categoria: Cibo (Obiettivi Specifici) ---
    MASTER_CHEF = auto()
    MASTER_MIXOLOGIST = auto()
    
    # --- Categoria: Stile di Vita (Obiettivi Ampi) ---
    HEDONIST_EPICUREAN = auto()     # Massimizzare il piacere e le esperienze piacevoli
    PEACEFUL_EXISTENCE = auto()     # Vita tranquilla, senza stress, coltivando hobby
    PHILANTHROPIST_ALTRUIST = auto()# Aiutare gli altri e migliorare la società
    
    # --- Categoria: Devianza (Negative) ---
    MASTER_THIEF = auto()           # (Richiede sistema di criminalità)
    PUBLIC_ENEMY = auto()           # Avere relazioni negative con tutti

    # --- Categoria: Uniche / Lore (Obiettivi Specifici) ---
    THE_CURATOR = auto()            # Completare tutte le collezioni
    WORLD_EXPLORER = auto()         # Visitare ogni lotto e luogo nascosto

    def display_name_it(self) -> str:
        """Restituisce un nome leggibile in italiano per l'aspirazione."""
        mapping = {
            # Creatività
            AspirationType.BESTSELLING_AUTHOR: "Autore di Bestseller",
            AspirationType.MASTER_ARTISAN: "Maestro Artigiano",
            AspirationType.MASTER_PAINTER: "Maestro Pittore",
            AspirationType.RENOWNED_MUSICIAN: "Musicista Famoso",

            # Conoscenza
            AspirationType.ACADEMIC_EXCELLENCE: "Eccellenza Accademica",
            AspirationType.LOREMASTER_OF_ANTHALYS: "Maestro del Sapere di Anthalys",
            AspirationType.SCIENTIFIC_BREAKTHROUGH: "Scoperta Scientifica",
            AspirationType.SKILL_MASTER: "Maestro di un'Abilità",
            AspirationType.SKILL_POLYGLOT: "Tuttologo",

            # Fortuna
            AspirationType.FABULOUSLY_WEALTHY: "Favolosamente Ricco",
            AspirationType.MANSION_BARON: "Barone delle Ville",

            # Famiglia
            AspirationType.FAMILY_LEGACY: "Eredità Familiare",
            AspirationType.LARGE_FAMILY: "Famiglia Numerosa",
            AspirationType.SUPER_PARENT: "Super Genitore",

            # Sociale
            AspirationType.COMMUNITY_LEADER: "Leader della Comunità",
            AspirationType.PERFECT_HOST: "Ospite Perfetto",
            AspirationType.SOCIAL_BUTTERFLY: "Anima della Festa",

            # Sport e Corpo
            AspirationType.ARENA_FUSION_CHAMPION: "Campione di Arena Fusion",
            AspirationType.BODY_PERFECTIONIST: "Perfezionista del Corpo",

            # Natura
            AspirationType.ANGLING_ACE: "Asso della Pesca",
            AspirationType.FREELANCE_BOTANIST: "Botanico Indipendente",
            AspirationType.MASTER_GARDENER: "Maestro Giardiniere",

            # Cibo
            AspirationType.MASTER_CHEF: "Master Chef",
            AspirationType.MASTER_MIXOLOGIST: "Maestro Mixologo",

            # Stile di Vita
            AspirationType.HEDONIST_EPICUREAN: "Edonista Epicureo",
            AspirationType.PEACEFUL_EXISTENCE: "Esistenza Pacifica",
            AspirationType.PHILANTHROPIST_ALTRUIST: "Filantropo Altruista",

            # Devianza
            AspirationType.MASTER_THIEF: "Maestro Ladro",
            AspirationType.PUBLIC_ENEMY: "Nemico Pubblico",

            # Uniche
            AspirationType.THE_CURATOR: "Il Curatore",
            AspirationType.WORLD_EXPLORER: "Esploratore del Mondo",
        }
        return mapping.get(self, self.name.replace("_", " ").title())