"""CharacterGenerator — generazione procedurale deterministica di Character."""

from __future__ import annotations

import random

from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.config.anthalys import DAYS_PER_YEAR, SECONDS_PER_DAY
from simai.core.anthalys_datetime import AnthalysDateTime
from simai.npc.background import BackgroundService
from simai.npc.enums import Sex
from simai.npc.genetics import (
    Genome,
    generate_from_parents,
    generate_random_genome,
    phenotype_from_genome,
)
from simai.npc.lifestage_service import LifeStageService
from simai.npc.models import Character
from simai.npc.name_generator import NameGenerator
from simai.npc.relationships.enums import RelationshipKind
from simai.npc.relationships.service import RelationshipError, create_relationship
from simai.npc.traits import (
    derive_aspiration,
    derive_mask_trait,
    derive_traits,
)


class CharacterGenerator:
    """Genera Character procedurali deterministici dal seed.

    Il seed effettivo di ogni personaggio è `master_seed + birth_total_seconds`,
    garantendo riproducibilità senza collisioni.
    """

    def __init__(
        self,
        *,
        master_seed: int = 0,
        name_generator: NameGenerator | None = None,
    ) -> None:
        self._master_seed = master_seed
        self._names = name_generator if name_generator is not None else NameGenerator()

    @property
    def master_seed(self) -> int:
        return self._master_seed

    # ------------------------------------------------------------------
    # Generazione base
    # ------------------------------------------------------------------

    def generate(
        self,
        *,
        birth_datetime: AnthalysDateTime,
        current_datetime: AnthalysDateTime,
        sex: Sex | None = None,
        genome: Genome | None = None,
        parents: tuple[Character, Character] | None = None,
    ) -> Character:
        """Genera un Character.

        Se `genome` è fornito, viene usato direttamente.
        Se `parents` è fornito, il genoma è ereditato dai genitori.
        Altrimenti, genoma casuale.
        """
        birth_seconds = birth_datetime.to_total_seconds()
        rng = random.Random(self._master_seed + birth_seconds)

        if sex is None:
            sex = rng.choice([Sex.MALE, Sex.FEMALE])

        # --- Genoma ---
        if genome is None:
            if parents is not None:
                father, mother = parents
                father_g = Genome.from_dict(father.genome_json)
                mother_g = Genome.from_dict(mother.genome_json)
                genome = generate_from_parents(father_g, mother_g, rng)
            else:
                genome = generate_random_genome(rng)

        appearance = phenotype_from_genome(genome, sex)

        # --- Tratti (derivati dal genoma) ---
        base_traits = derive_traits(genome, rng)
        mask_trait = derive_mask_trait(base_traits, rng)
        all_traits = list(base_traits)
        if mask_trait is not None:
            all_traits.append(mask_trait)
        all_traits.sort(key=lambda t: t.value)

        # --- Aspirazione ---
        aspiration = derive_aspiration(base_traits, genome, rng)

        # --- Nomi ---
        first_name = self._names.generate_first_name(rng, sex)
        last_name = self._names.generate_last_name(rng)
        if parents is not None:
            last_name = parents[0].last_name

        gender = self._random_gender(rng, sex)

        age_seconds = LifeStageService.age_seconds_at(birth_seconds, current_datetime)
        pediatric = LifeStageService.get_pediatric_stage(age_seconds)
        psychosocial = LifeStageService.get_psychosocial_stage(age_seconds)

        # Bilancio iniziale: derivato da età + rumore deterministico
        age_years_for_wealth = LifeStageService.age_seconds_at(birth_seconds, current_datetime) // (
            432 * 28 * 3600
        )
        base_wealth = 100 + max(0, age_years_for_wealth) * 30
        wealth = base_wealth + rng.randint(0, 500)

        # --- Identity (Chunk 3.6a) ---
        from simai.npc.identity import IdentityService

        age_years_for_identity = LifeStageService.age_seconds_at(
            birth_seconds, current_datetime
        ) // (432 * 28 * 3600)
        identity_rng = random.Random(self._master_seed + birth_seconds + 777)
        identity = IdentityService.initialize(
            character=None,  # type: ignore[arg-type]  # non serve durante init
            rng=identity_rng,
            age_years=int(age_years_for_identity),
            parents=parents,
        )

        return Character(
            first_name=first_name,
            last_name=last_name,
            sex=sex.value,
            gender=gender,
            birth_total_seconds=birth_seconds,
            birth_iso=birth_datetime.to_iso_string(),
            death_total_seconds=None,
            death_iso=None,
            is_alive=True,
            life_stage_pediatric=pediatric.value,
            life_stage_psychosocial=psychosocial.value,
            location_id=None,
            master_seed=self._master_seed,
            appearance_json=appearance,
            traits_json=[t.value for t in all_traits],
            aspirations_json=[aspiration.value],
            genome_json=genome.to_dict(),
            athel_balance=wealth,
            attributes_json={
                "mask_trait": mask_trait.value if mask_trait is not None else None,
                **identity.to_dict(),
            },
        )

    def generate_at_age(
        self,
        *,
        age_years: int,
        age_days: int,
        current_datetime: AnthalysDateTime,
        sex: Sex | None = None,
        genome: Genome | None = None,
        parents: tuple[Character, Character] | None = None,
    ) -> Character:
        """Genera un Character di età esatta `age_years` anni + `age_days` giorni."""
        if age_years < 0 or age_days < 0:
            raise ValueError(
                f"age_years e age_days devono essere >= 0, ricevuti {age_years}, {age_days}"
            )
        age_in_days = age_years * DAYS_PER_YEAR + age_days
        age_seconds = age_in_days * SECONDS_PER_DAY
        birth_seconds = current_datetime.to_total_seconds() - age_seconds
        if birth_seconds < 0:
            raise ValueError(
                f"Data di nascita precedente all'anno 1: "
                f"age={age_years}y {age_days}d @ {current_datetime}"
            )
        birth_datetime = AnthalysDateTime.from_total_seconds(birth_seconds)
        return self.generate(
            birth_datetime=birth_datetime,
            current_datetime=current_datetime,
            sex=sex,
            genome=genome,
            parents=parents,
        )

    # ------------------------------------------------------------------
    # Attributi random non-genetici
    # ------------------------------------------------------------------

    @staticmethod
    def _random_gender(rng: random.Random, sex: Sex) -> str:
        if sex is Sex.MALE:
            return "man"
        if sex is Sex.FEMALE:
            return "woman"
        return rng.choice(["nonbinary", "genderfluid", "agender"])


# ---------------------------------------------------------------------------
# Seed iniziale
# ---------------------------------------------------------------------------


def seed_characters(
    session: Session,
    *,
    current_datetime: AnthalysDateTime,
    master_seed: int,
    n_random: int = 4,
) -> list[Character]:
    """Popola il DB con Erika, Max e N NPC random (idempotente)."""
    existing = session.scalars(select(Character)).first()
    if existing is not None:
        return []

    gen = CharacterGenerator(master_seed=master_seed)
    characters: list[Character] = []

    # 1. Erika (14 anni + 24 giorni)
    erika = gen.generate_at_age(
        age_years=14,
        age_days=24,
        current_datetime=current_datetime,
        sex=Sex.FEMALE,
    )
    erika.first_name = "Erika"
    erika.last_name = "Lamborghetti"
    characters.append(erika)

    # 2. Max (14 anni + 32 giorni)
    max_char = gen.generate_at_age(
        age_years=14,
        age_days=32,
        current_datetime=current_datetime,
        sex=Sex.MALE,
    )
    max_char.first_name = "Max"
    max_char.last_name = "Volpi"
    characters.append(max_char)

    # 3. NPC random
    rng = random.Random(master_seed + 1)
    for _ in range(n_random):
        years = rng.randint(5, 60)
        days = rng.randint(0, DAYS_PER_YEAR - 1)
        char = gen.generate_at_age(
            age_years=years,
            age_days=days,
            current_datetime=current_datetime,
        )
        characters.append(char)

    # 4. Persist — session.add + flush -> id popolati da QUI in poi
    for c in characters:
        session.add(c)
    session.flush()  # ⚠️ FONDAMENTALE: popola gli id

    # 4-bis. Assegna location "casa" a tutti i character (Chunk 3.14)
    from simai.world.location_service import list_locations

    locations = list_locations(session)
    if locations:
        house = next(
            (loc for loc in locations if loc.type == "BUILDING"),
            locations[0],
        )
        for c in characters:
            if c.location_id is None:
                c.location_id = house.id
        session.flush()

    # 5. Desire init
    from simai.npc.desire import DesireService

    rng_desire = random.Random(master_seed + 2468)
    for c in characters:
        state = DesireService.initialize(c, rng_desire, current_dt=current_datetime)
        DesireService.write_state(c, state)

    # 5-bis. Libido baseline
    from simai.npc.relationships.libido import LibidoService

    rng_libido = random.Random(master_seed + 3579)
    for c in characters:
        value = LibidoService.initialize_baseline(c, rng_libido)
        LibidoService.write_baseline(c, value)

    # 5-ter. LGBTQ disclosure init
    from simai.npc.identity.lgbtq import LGBTQService

    for c in characters:
        if LGBTQService.is_lgbtq(c):
            default_level = LGBTQService._default_disclosure_for(c)
            LGBTQService.set_disclosure(c, default_level)

    # 5-quater. Social awareness init
    from simai.npc.social_awareness import SocialAwarenessService

    rng_aware = random.Random(master_seed + 4680)
    for c in characters:
        SocialAwarenessService.initialize_for(c)
    for c in characters:
        SocialAwarenessService.initialize_family_knowledge(session, c, rng=rng_aware)

    # 6. Background formativo
    rng_bg = random.Random(master_seed + 1234)
    for c in characters:
        age_secs = current_datetime.to_total_seconds() - c.birth_total_seconds
        age_years = int(age_secs // (432 * 28 * 3600))
        if age_years < 1:
            continue
        events = BackgroundService.generate_seed_events(rng_bg, age_years=age_years)
        BackgroundService.persist_seed_events(
            session,
            character=c,
            events=events,
            current_dt=current_datetime,
        )

    # 7. Addictions (15% adulti, garantendo almeno 1)
    from simai.npc.addictions import AddictionKind, AddictionService

    rng_addict = random.Random(master_seed + 999)
    adult_candidates: list[Character] = []
    for c in characters:
        if c.first_name in ("Erika", "Max"):
            continue
        age_secs = current_datetime.to_total_seconds() - c.birth_total_seconds
        age_years = int(age_secs // (432 * 28 * 3600))
        if age_years >= 18:
            adult_candidates.append(c)

    # Garantisce almeno 1 addicted: se non ci sono adulti, pesca chiunque
    pool = adult_candidates if adult_candidates else list(characters)
    guaranteed = rng_addict.choice(pool)
    guaranteed_kind = rng_addict.choice(
        [AddictionKind.CAFFEINE, AddictionKind.ALCOHOL, AddictionKind.TOBACCO]
    )
    AddictionService.start_addiction(
        session,
        character_id=guaranteed.id,
        kind=guaranteed_kind,
        current_dt=current_datetime,
        initial_dependence=rng_addict.uniform(20.0, 35.0),
    )
    for _ in range(2):
        AddictionService.use(
            session,
            character_id=guaranteed.id,
            kind=guaranteed_kind,
            current_dt=current_datetime,
            rng=rng_addict,
        )
    logger.info(
        "Seed addiction garantita: char={} kind={}",
        guaranteed.id,
        guaranteed_kind.value,
    )

    # Poi il 15% normale sugli altri adulti
    for c in adult_candidates:
        if c.id == guaranteed.id:
            continue
        if rng_addict.random() < 0.15:
            kind = rng_addict.choice(
                [
                    AddictionKind.ALCOHOL,
                    AddictionKind.TOBACCO,
                    AddictionKind.CAFFEINE,
                ]
            )
            AddictionService.start_addiction(
                session,
                character_id=c.id,
                kind=kind,
                current_dt=current_datetime,
                initial_dependence=rng_addict.uniform(10.0, 25.0),
            )

    # 7-bis. Bootstrap opinion (Chunk 3.14)
    from simai.npc.reputation import ReputationService

    rng_opinion = random.Random(master_seed + 7777)
    for i, a in enumerate(characters):
        for b in characters[i + 1 :]:
            ReputationService.update_opinion(
                session,
                observer_id=a.id,
                target_id=b.id,
                delta=rng_opinion.uniform(5.0, 25.0),
                current_dt=current_datetime,
            )
            ReputationService.update_opinion(
                session,
                observer_id=b.id,
                target_id=a.id,
                delta=rng_opinion.uniform(5.0, 25.0),
                current_dt=current_datetime,
            )

    # 8. Relazioni demo: Erika <-> Max FRIEND_OF
    if len(characters) >= 2:
        try:
            create_relationship(
                session,
                from_id=characters[0].id,
                to_id=characters[1].id,
                kind=RelationshipKind.FRIEND_OF,
                strength=0.7,
            )
        except RelationshipError as exc:
            logger.warning("Impossibile creare relazione demo: {}", exc)

    return characters


__all__ = ["CharacterGenerator", "seed_characters"]
