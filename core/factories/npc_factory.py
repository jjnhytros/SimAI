# core/factories/npc_factory.py
"""
Definisce la NPCFactory, una classe per la creazione procedurale di NPC.
"""
import random
import uuid
from typing import TYPE_CHECKING, List, Set

from core.enums import (
    Gender, Interest, RelationshipStatus, AspirationType, TraitType,
    SchoolLevel, LODLevel
)
from core.config import npc_config, time_config
from core.utils import gen_lastname
from core.world.ATHDateTime.ATHDateTime import ATHDateTime
from core.character import Character
if TYPE_CHECKING:
    pass
class NPCFactory:
    """
    Classe responsabile della creazione di istanze di Character (NPC)
    con attributi generati casualmente.
    """
    def __init__(self):
        # Il factory potrebbe avere delle configurazioni, ma per ora è semplice.
        pass

    def create_random_npc(self, simulation_start_date: 'ATHDateTime', available_location_ids: List[str]) -> 'Character':
        """Crea un singolo NPC con attributi, data di nascita e posizione casuali."""
        from core.world.ATHDateTime.ATHDateInterval import ATHDateInterval

        gender = random.choice([Gender.MALE, Gender.FEMALE])
        first_name = random.choice(npc_config.MALE_NAMES if gender == Gender.MALE else npc_config.FEMALE_NAMES)
        last_name = gen_lastname()
        full_name = f"{first_name} {last_name}"
        
        # Calcola la data di nascita
        min_age_days = int(13 * time_config.DXY)
        max_age_days = int(40 * time_config.DXY)
        age_in_days = random.randint(min_age_days, max_age_days)
        age_interval = ATHDateInterval(days=age_in_days)
        birth_date = simulation_start_date.sub(age_interval)

        # Scegli tratti, aspirazione, interessi...
        num_traits = random.randint(npc_config.MIN_TRAITS_PER_NPC, npc_config.MAX_TRAITS_PER_NPC)
        traits_list = [t for t in TraitType]
        random_traits: Set[TraitType] = set(random.sample(
            npc_config.IMPLEMENTED_TRAITS, 
            min(num_traits, len(npc_config.IMPLEMENTED_TRAITS))
        ))
        random_aspiration = random.choice(list(AspirationType))
        num_interests = random.randint(1, npc_config.MAX_NPC_ACTIVE_INTERESTS)
        random_interests = set(random.sample(list(Interest), num_interests))

        # Scegli una locazione e coordinate casuali
        loc_id = random.choice(available_location_ids)
        # Il recupero dell'oggetto location e il calcolo x,y è meglio farlo nel setup principale
        # dato che la factory non ha accesso diretto a simulation_context.
        # Oppure, passa simulation_context anche alla factory. Per ora, passiamo solo l'ID.

        new_npc = Character(
            npc_id=f"npc_random_{uuid.uuid4().hex[:8]}",
            name=full_name,
            initial_gender=gender,
            initial_birth_date=birth_date,
            initial_traits=random_traits,
            initial_aspiration=random_aspiration,
            initial_interests=random_interests,
            initial_location_id=loc_id
        )
        return new_npc
