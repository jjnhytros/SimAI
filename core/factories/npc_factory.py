# core/factories/npc_factory.py
"""
Definisce la NPCFactory, una classe per la creazione procedurale di NPC.
"""
import random
import uuid
from typing import Set

from core.character import Character
from core.enums import (
    Gender, Interest, RelationshipStatus, AspirationType, TraitType,
    SchoolLevel, LODLevel
)
from core.config import npc_config, time_config
from core.utils import gen_lastname

class NPCFactory:
    """
    Classe responsabile della creazione di istanze di Character (NPC)
    con attributi generati casualmente.
    """
    def __init__(self):
        # Il factory potrebbe avere delle configurazioni, ma per ora è semplice.
        pass

    def create_random_npc(self) -> Character:
        """
        Crea e restituisce un singolo NPC con attributi casuali.
        """
        # Scegli un genere casuale, escludendo NON_BINARY per la scelta del nome
        gender = random.choice([Gender.MALE, Gender.FEMALE])
        
        # Scegli un nome in base al genere
        if gender == Gender.MALE:
            first_name = random.choice(npc_config.MALE_NAMES)
        else:
            first_name = random.choice(npc_config.FEMALE_NAMES)
        last_name = gen_lastname()
        full_name = f"{first_name} {last_name}"
        
        # Genera un ID unico
        npc_id = f"npc_random_{uuid.uuid4().hex[:8]}"

        # Genera età casuale (es. tra 20 e 40 anni)
        min_age_days = 20 * time_config.DXY
        max_age_days = 40 * time_config.DXY
        age_in_days = random.randint(min_age_days, max_age_days)

        # Seleziona un numero casuale di tratti
        num_traits = random.randint(npc_config.MIN_TRAITS_PER_NPC, npc_config.MAX_TRAITS_PER_NPC)
        # Seleziona tratti a caso, assicurandoti che siano unici
        traits_list = [t for t in TraitType if t != TraitType.EVIL] # Esempio di esclusione
        random_traits: Set[TraitType] = set(random.sample(traits_list, num_traits))
        
        # Seleziona un'aspirazione casuale
        random_aspiration: AspirationType = random.choice(list(AspirationType))

        # Seleziona interessi casuali
        num_interests = random.randint(1, npc_config.MAX_NPC_ACTIVE_INTERESTS)
        random_interests: Set[Interest] = set(random.sample(list(Interest), num_interests))

        # Crea l'istanza di Character
        new_npc = Character(
            npc_id=npc_id,
            name=full_name,
            initial_gender=gender,
            initial_age_days=age_in_days,
            initial_traits=random_traits,
            initial_aspiration=random_aspiration,
            initial_interests=random_interests
            # Gli altri parametri useranno i valori di default di Character.__init__
        )

        return new_npc