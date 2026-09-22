"""LifecycleManager — orchestrazione per tick di aging/mortalità/gravidanze/famiglia/economia."""

from __future__ import annotations

from dataclasses import dataclass, field

from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from simai.config.anthalys import SECONDS_PER_DAY, SECONDS_PER_YEAR
from simai.core.anthalys_datetime import AnthalysDateTime
from simai.core.event_bus import EventBus
from simai.economy.companies.models import Company
from simai.npc.events import (
    EVENT_FAMILY_CONCEPTION_ATTEMPT,
    EVENT_FAMILY_GUARDIAN_ASSIGNED,
    EVENT_FAMILY_ORPHAN_REGISTERED,
    EVENT_NPC_ARRIVED,
    EVENT_NPC_BORN,
    EVENT_NPC_DIED,
    EVENT_NPC_LIFESTAGE_CHANGED,
    EVENT_PREGNANCY_COMPLETED,
    EVENT_PREGNANCY_CONCEIVED,
)
from simai.npc.identity import IdentityService
from simai.npc.lifecycle.aging import AgeTransition, AgingService
from simai.npc.lifecycle.death import DeathService
from simai.npc.lifecycle.enums import DeathCause, PregnancyStatus
from simai.npc.lifecycle.family_ai import FamilyAI
from simai.npc.lifecycle.pregnancy import Pregnancy, PregnancyService
from simai.npc.lifecycle.succession import SuccessionService
from simai.npc.lifestage_service import LifeStageService
from simai.npc.models import Character
from simai.npc.mood import MoodState
from simai.npc.needs.needs import Needs
from simai.npc.relationships.connection import ConnectionService
from simai.npc.relationships.enums import RelationshipKind
from simai.npc.relationships.family_tree import FamilyTreeService
from simai.npc.relationships.models import Relationship
from simai.npc.skills.enums import SkillType
from simai.npc.skills.service import SkillService


@dataclass(frozen=True, slots=True)
class LifecycleReport:
    """Esito di un tick di lifecycle."""

    dead_ids: list[int] = field(default_factory=list)
    birth_ids: list[int] = field(default_factory=list)
    pregnancy_completed_ids: list[int] = field(default_factory=list)
    pregnancy_started_ids: list[int] = field(default_factory=list)
    orphan_ids: list[int] = field(default_factory=list)
    guardian_assignments: list[tuple[int, int]] = field(default_factory=list)
    age_transitions: list[AgeTransition] = field(default_factory=list)
    conception_attempts: int = 0
    payday_paid_count: int = 0
    payday_total_paid: int = 0
    bank_interest_paid: int = 0
    loan_payments_succeeded: int = 0
    loan_payments_missed: int = 0
    loans_defaulted: int = 0
    loans_written_off: int = 0
    census_written: bool = False
    daily_work_done: bool = False
    arrival_ids: list[int] = field(default_factory=list)
    in_transit_ids: list[int] = field(default_factory=list)
    # --- Companies (Chunk 5.3b) ---
    companies_evaluated: int = 0
    company_hires: int = 0
    company_fires: int = 0
    company_dissolutions: int = 0
    company_tick_reports: int = 0
    # --- AION (Chunk 5.4e) ---
    aion_sellers_evaluated: int = 0
    aion_buyers_evaluated: int = 0
    aion_listings_created: int = 0
    aion_orders_placed: int = 0
    aion_orders_failed: int = 0
    aion_shipments_advanced: int = 0
    aion_shipments_delivered: int = 0
    aion_errors: list[str] = field(default_factory=list)


class LifecycleManager:
    """Gestore del ciclo vita: gravidanze + aging + mortalità + famiglia + economia."""

    def __init__(
        self,
        session_factory: sessionmaker[Session],
        event_bus: EventBus,
        *,
        seed: int = 0,
        master_seed: int = 0,
    ) -> None:
        self._session_factory = session_factory
        self._event_bus = event_bus
        self._seed = seed
        self._master_seed = master_seed
        self._family_ai = FamilyAI(seed=seed + 2, master_seed=master_seed)
        self._last_day_index: int | None = None
        self._last_month_key: int | None = None

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def seed(self) -> int:
        return self._seed

    @property
    def family_ai(self) -> FamilyAI:
        return self._family_ai

    @property
    def last_day_index(self) -> int | None:
        return self._last_day_index

    @property
    def last_month_key(self) -> int | None:
        return self._last_month_key

    # ------------------------------------------------------------------
    # Tick
    # ------------------------------------------------------------------

    def tick(self, current_dt: AnthalysDateTime) -> LifecycleReport:
        """Esegue un tick di lifecycle. Ritorna il report."""
        current_secs = current_dt.to_total_seconds()
        day_index = current_secs // SECONDS_PER_DAY
        month_key = current_dt.year * 100 + current_dt.month

        dead_ids: list[int] = []
        birth_ids: list[int] = []
        completed_pregs: list[int] = []
        started_pregs: list[int] = []
        orphan_ids: list[int] = []
        guardian_assignments: list[tuple[int, int]] = []
        age_transitions: list[AgeTransition] = []
        conception_attempts = 0
        payday_paid_count = 0
        payday_total_paid = 0
        bank_interest_paid = 0
        loan_payments_succeeded = 0
        loan_payments_missed = 0
        loans_defaulted = 0
        loans_written_off = 0
        companies_evaluated = 0
        company_hires = 0
        company_fires = 0
        company_dissolutions = 0
        company_tick_reports = 0
        aion_sellers_evaluated = 0
        aion_buyers_evaluated = 0
        aion_listings_created = 0
        aion_orders_placed = 0
        aion_orders_failed = 0
        aion_shipments_advanced = 0
        aion_shipments_delivered = 0
        aion_errors: list[str] = []

        census_written = False
        daily_work_done = False

        with self._session_factory() as session:
            # --- 0. Transit tick (ad ogni tick, non solo al giorno) -----
            from simai.city.transport.transit import TransitService

            arrivals = TransitService.tick(session, current_dt)
            arrival_ids = [a.character_id for a in arrivals]
            in_transit_ids = list(TransitService.active_job_ids(session))

            # ------------------------------------------------------------------
            # 1. Avanza le gravidanze attive (ogni tick)
            # ------------------------------------------------------------------
            actives = list(
                session.scalars(
                    select(Pregnancy).where(Pregnancy.status == PregnancyStatus.ACTIVE.value)
                )
            )
            for preg in actives:
                children = PregnancyService.advance(
                    session,
                    preg,
                    current_dt,
                    self._family_ai._rng,  # riuso RNG del family AI
                    master_seed=self._master_seed,
                )
                if children:
                    birth_ids.extend(c.id for c in children)
                    completed_pregs.append(preg.id)

            # ------------------------------------------------------------------
            # 2. Lavoro giornaliero (una volta al giorno Anthalys)
            # ------------------------------------------------------------------
            if self._last_day_index != day_index:
                daily_work_done = True

                # Solo character già nati al tempo corrente (esclude i "futuri")
                chars = list(
                    session.scalars(
                        select(Character).where(
                            Character.is_alive.is_(True),
                            Character.birth_total_seconds <= current_secs,
                        )
                    )
                )

                # --- 2a. Aging -------------------------------------------------
                for c in chars:
                    transitions = AgingService.apply_aging(c, current_dt)
                    age_transitions.extend(transitions)

                # --- 2a-bis. Skill decay --------------------------------------

                for c in chars:
                    if not c.is_alive:
                        continue
                    SkillService.apply_daily_decay(session, character=c, current_dt=current_dt)

                # --- 2a-ter. Fluidity sessuale (ogni 30 giorni) --------------
                if day_index > 0 and day_index % 30 == 0:
                    for c in chars:
                        if not c.is_alive:
                            continue
                        age_secs = LifeStageService.age_seconds_at(
                            c.birth_total_seconds, current_dt
                        )
                        age_years = age_secs // SECONDS_PER_YEAR
                        IdentityService.apply_sexuality_drift(
                            c,
                            self._family_ai._rng,
                            age_years=int(age_years),
                        )

                # --- 2a-quater. Addictions: craving + withdrawal + decay ---
                from simai.npc.addictions import AddictionService
                from simai.npc.addictions.enums import (
                    MOODLET_DURATION_TICKS,
                    AddictionKind,
                )
                from simai.npc.mood import Moodlet

                for c in chars:
                    if not c.is_alive:
                        continue
                    addictions = AddictionService.all_of(session, c.id)
                    for add in addictions:
                        tick_result = AddictionService.daily_tick(
                            session, add, current_dt=current_dt
                        )
                        if tick_result.moodlet_delta != 0.0:
                            try:
                                ak = AddictionKind(add.kind)
                            except ValueError:
                                continue
                            mood = MoodState.from_dict(c.mood_json or {})
                            moodlet = Moodlet(
                                name=f"Craving {ak.value}",
                                remaining_ticks=MOODLET_DURATION_TICKS,
                                happiness_delta=tick_result.moodlet_delta,
                                source=f"addiction_{ak.value.lower()}",
                            )
                            new_mood = mood.tick(
                                Needs.from_dict(c.needs_json or {}),
                                (moodlet,),
                            )
                            c.mood_json = new_mood.to_dict()

                # --- 2a-quinquies. Desire refresh ----------------------------
                from simai.npc.desire import DesireService

                for c in chars:
                    if not c.is_alive:
                        continue
                    DesireService.recompute(session, c, current_dt=current_dt)

                # --- 2b. Mortalità --------------------------------------------
                for c in chars:
                    if not c.is_alive:
                        continue
                    age_secs = LifeStageService.age_seconds_at(c.birth_total_seconds, current_dt)
                    age_years = age_secs // SECONDS_PER_YEAR
                    p = DeathService.mortality_probability_per_day(age_years, c.sex)
                    if self._family_ai._rng.random() < p:
                        rv = self._family_ai._rng.random()
                        cause = DeathService.pick_cause(age_years, c.sex, random_value=rv)
                        DeathService.register_death(session, c, current_dt, cause)
                        dead_ids.append(c.id)

                # --- 2c. Successione (orfani + tutori) ------------------------
                if dead_ids:
                    orphan_infos = SuccessionService.process_deaths(session, dead_ids, current_dt)
                    for info in orphan_infos:
                        orphan_ids.append(info.child_id)
                        if info.guardian_id is not None:
                            guardian_assignments.append((info.child_id, info.guardian_id))

                # --- 2c-ter. Parent lost events -------------------------------
                if dead_ids:
                    from simai.npc.background import (
                        BackgroundService,
                        FormativeEventKind,
                    )

                    for dead_id in dead_ids:
                        children = FamilyTreeService.children_of(session, dead_id)
                        for child in children:
                            if not child.is_alive:
                                continue
                            # Età del figlio al momento della morte
                            age_secs = LifeStageService.age_seconds_at(
                                child.birth_total_seconds, current_dt
                            )
                            age_years = age_secs // SECONDS_PER_YEAR
                            if age_years > 25:
                                continue
                            BackgroundService.record_event(
                                session,
                                character=child,
                                kind=FormativeEventKind.PARENT_LOST,
                                occurred_at_age=int(age_years),
                                severity=0.80,
                                text=f"Perso {child.first_name and 'un genitore'}",
                                current_dt=current_dt,
                            )

                # --- 2c-bis. Eredità materiale --------------------------------
                if dead_ids:
                    from simai.npc.economy.inheritance import (
                        InheritanceService,
                    )

                    for dead_id in dead_ids:
                        deceased = session.get(Character, dead_id)
                        if deceased is not None:
                            InheritanceService.distribute(
                                session,
                                deceased=deceased,
                                current_dt=current_dt,
                            )

                # --- 2d. Family AI (concepimento) -----------------------------
                couples = self._find_couples(session, current_secs)
                for mother, father in couples:
                    eval_ = self._family_ai.evaluate_couple(session, mother, father, current_dt)
                    if not eval_.eligible:
                        continue
                    conception_attempts += 1
                    result = self._family_ai.try_conceive(session, mother, father, current_dt)
                    if result.success and result.pregnancy_id is not None:
                        started_pregs.append(result.pregnancy_id)

                # --- 2d-bis. Gossip propagation (promozioni) ---------------------
                from simai.economy.jobs import JobService
                from simai.npc.reputation import GossipTopic, ReputationService

                for c in chars:
                    if not c.is_alive or c.location_id is None:
                        continue
                    job = JobService.job_of(session, c.id)
                    if job is None:
                        continue
                    # Solo promozioni fresche (title appena cambiato)
                    # Tracciamo tramite metadata_json
                    md = dict(job.metadata_json or {})
                    promoted_at = md.get("promoted_at_day")
                    if promoted_at == day_index:
                        # Promozione appena avvenuta → broadcast
                        witnesses = ReputationService.witnesses_in_same_location(session, c)
                        if witnesses:
                            ReputationService.broadcast(
                                session,
                                speaker=c,
                                witnesses=witnesses,
                                target=c,
                                topic=GossipTopic.ACHIEVEMENT,
                                sentiment=0.7,
                                current_dt=current_dt,
                                strength=0.6,
                            )

                # --- 2d-ter. Boredom + Breakup ------------------------------
                from simai.npc.relationships.boredom import BoredomService
                from simai.npc.relationships.breakup import BreakupService
                from simai.npc.relationships.models import Relationship

                # --- 2d-quater. Connection decay -----------------------------
                social_kinds_conn = (
                    RelationshipKind.FRIEND_OF.value,
                    RelationshipKind.BEST_FRIEND_OF.value,
                    RelationshipKind.PARTNER_OF.value,
                    RelationshipKind.SPOUSE_OF.value,
                )
                conn_rels = list(
                    session.scalars(
                        select(Relationship).where(
                            Relationship.kind.in_(social_kinds_conn),
                            Relationship.from_id < Relationship.to_id,
                        )
                    )
                )
                for rel in conn_rels:
                    ConnectionService.tick_daily(rel)

                # 1. Boredom growth per relazioni "sociali" stabili
                social_kinds = (
                    RelationshipKind.FRIEND_OF.value,
                    RelationshipKind.BEST_FRIEND_OF.value,
                    RelationshipKind.PARTNER_OF.value,
                    RelationshipKind.SPOUSE_OF.value,
                )
                social_rels = list(
                    session.scalars(
                        select(Relationship).where(
                            Relationship.kind.in_(social_kinds),
                            Relationship.from_id < Relationship.to_id,
                        )
                    )
                )
                for rel in social_rels:
                    BoredomService.tick_daily(session, rel, strength=rel.strength)

                # 2. Check breakup
                rng_breakup = self._family_ai._rng
                for rel in social_rels:
                    should, reason = BreakupService.should_break_up(session, rel, rng_breakup)
                    if should:
                        BreakupService.breakup(
                            session, rel=rel, reason=reason, current_dt=current_dt
                        )

                # --- 2d-quinquies. Mentorship sessions -----------------------
                from simai.npc.relationships.mentorship import MentorshipService

                # Per ogni studente in mentorship attiva, tira per una sessione
                # se studente e mentore sono nella stessa location
                for rel in MentorshipService.all_mentorships(session):
                    md = rel.metadata_json or {}
                    if md.get("graduated", False):
                        continue
                    mentor = session.get(Character, rel.from_id)
                    student = session.get(Character, rel.to_id)
                    if (
                        mentor is None
                        or student is None
                        or not mentor.is_alive
                        or not student.is_alive
                    ):
                        continue
                    if mentor.location_id is None or mentor.location_id != student.location_id:
                        continue

                    skill_name = md.get("skill_type")
                    if not isinstance(skill_name, str):
                        continue
                    try:
                        st = SkillType(skill_name)
                    except ValueError:
                        continue

                    # 30% di chance di sessione al giorno
                    if self._family_ai._rng.random() >= 0.30:
                        continue

                    MentorshipService.register_session(
                        session,
                        rel,
                        mentor=mentor,
                        student=student,
                        skill_type=st,
                        current_dt=current_dt,
                        rng=self._family_ai._rng,
                    )

                # --- 2d-sexies. Family opinion boost -------------------------
                from simai.npc.relationships.intergenerational import (
                    IntergenerationalService,
                )

                IntergenerationalService.apply_family_opinion_boost(session, current_dt=current_dt)

                # --- 2d-septies. Passive social discovery --------------------
                from simai.npc.social_awareness import SocialAwarenessService

                # Chi è nella stessa location può scoprire qualcosa in più
                # con bassa probabilità (azione "ambientale").
                # Raggruppa per location
                by_location: dict[int, list[Character]] = {}
                for c in chars:
                    if c.location_id is None:
                        continue
                    by_location.setdefault(c.location_id, []).append(c)

                for _loc_id, group in by_location.items():
                    if len(group) < 2:
                        continue
                    for observer in group:
                        for target in group:
                            if observer.id == target.id:
                                continue
                            # 15% di chance per coppia/giorno
                            if self._family_ai._rng.random() >= 0.15:
                                continue
                            SocialAwarenessService.record_interaction(
                                observer,
                                target,
                                action_level=1,  # intensità bassa
                                rng=self._family_ai._rng,
                            )

                # --- 2d-septies-bis. Socialization (auto-relazioni) ---------
                from simai.npc.socialization import SocializationService

                SocializationService.daily_tick(
                    session,
                    chars,
                    current_dt=current_dt,
                    rng=self._family_ai._rng,
                )

                # --- 2d-octies. Reflection + Crisis -------------------------
                from simai.npc.reflection import (
                    NEGATIVE_STREAK_FOR_CRISIS,
                    REFLECTION_INTERVAL_DAYS,
                    CrisisService,
                    ReflectionService,
                )
                from simai.npc.reflection.models import ReflectionEntry

                for c in chars:
                    if not c.is_alive:
                        continue

                    # 1. Reflection settimanale
                    if day_index % REFLECTION_INTERVAL_DAYS == 0:
                        ReflectionService.reflect(
                            session,
                            c,
                            current_dt=current_dt,
                            rng=self._family_ai._rng,
                        )

                    # 2. Crisis check
                    recent = list(
                        session.scalars(
                            select(ReflectionEntry)
                            .where(ReflectionEntry.character_id == c.id)
                            .order_by(ReflectionEntry.at_total_seconds.desc())
                            .limit(NEGATIVE_STREAK_FOR_CRISIS)
                        )
                    )
                    streak = sum(1 for e in recent if e.sentiment < -0.3)

                    should_trigger, reason = CrisisService.check_trigger(
                        session,
                        c,
                        current_dt=current_dt,
                        recent_negative_streak=streak,
                    )
                    if should_trigger:
                        CrisisService.start_crisis(c, reason=reason, current_dt=current_dt)

                    # 3. Recovery tick (solo se crisi attiva)
                    CrisisService.recovery_tick(session, c, current_dt=current_dt)

                # --- 2e. Payday (ogni 7 giorni) -------------------------------
                if day_index > 0 and day_index % 7 == 0:
                    from simai.economy.payday import PaydayService

                    payday_report = PaydayService.process(session, current_dt)
                    payday_paid_count = payday_report.paid_count
                    payday_total_paid = payday_report.total_paid
                    if payday_report.paid_count > 0:
                        logger.info(
                            "Lifecycle: payday day={} pagati={} totale={}",
                            day_index,
                            payday_report.paid_count,
                            payday_report.total_paid,
                        )

                # --- 2e-bis. Costi di sussistenza ---------------------------
                from simai.npc.economy.service import (
                    DEFAULT_LIVING_COST,
                    WealthService,
                )

                for c in chars:
                    if not c.is_alive:
                        continue
                    WealthService.apply_living_costs(
                        session,
                        c,
                        daily_cost=DEFAULT_LIVING_COST,
                        current_dt=current_dt,
                    )

                # --- 2e-ter. Mutui + tasse proprietà ------------------------
                from simai.config.anthalys import DAYS_PER_MONTH
                from simai.economy.property import (
                    MortgageService,
                    PropertyTaxService,
                )

                # Rate mutuo mensili
                if day_index > 0 and day_index % DAYS_PER_MONTH == 0:
                    for mortgage in MortgageService.active_mortgages(session):
                        if current_secs >= mortgage.next_payment_at_total_seconds:
                            payment = MortgageService.pay_installment(
                                session,
                                mortgage=mortgage,
                                current_dt=current_dt,
                            )
                            if not payment.paid and MortgageService.should_foreclose(mortgage):
                                MortgageService.foreclose(
                                    session,
                                    mortgage=mortgage,
                                    current_dt=current_dt,
                                )

                    # Tasse mensili sulla proprietà
                    tax_report = PropertyTaxService.collect_all(session, current_dt=current_dt)
                    if tax_report.taxed > 0:
                        logger.info(
                            "Property tax collected: {} lotti, {} Athel",
                            tax_report.taxed,
                            tax_report.total_collected,
                        )

                    # --- 2e-ter-bis. Banking monthly tick ----------------
                    from simai.economy.banking import BankService

                    try:
                        BankService.ensure_primary_bank(session)
                        for bank_obj in BankService.all_banks(session, only_active=True):
                            bank_report = BankService.monthly_tick(
                                session,
                                current_dt=current_dt,
                                bank=bank_obj,
                            )
                            bank_interest_paid += bank_report.interest_paid_to_depositors
                            loan_payments_succeeded += bank_report.loan_payments_succeeded
                            loan_payments_missed += bank_report.loan_payments_missed
                            loans_defaulted += bank_report.loans_defaulted
                            loans_written_off += bank_report.loans_written_off
                            if (
                                bank_report.loan_payments_attempted > 0
                                or bank_report.deposit_accounts_credited > 0
                            ):
                                logger.info(
                                    "Banking monthly tick: bank={} "
                                    "interessi={} rate_ok={} rate_miss={} "
                                    "default={} writeoff={}",
                                    bank_obj.code,
                                    bank_report.interest_paid_to_depositors,
                                    bank_report.loan_payments_succeeded,
                                    bank_report.loan_payments_missed,
                                    bank_report.loans_defaulted,
                                    bank_report.loans_written_off,
                                )
                    except Exception as exc:  # pragma: no cover — safety net
                        logger.warning("Banking monthly tick fallito: {}", exc)

                # --- 2e-ter-quater. Companies daily tick ----------------
                from simai.economy.companies import (
                    CompanyService,
                    CompanyStatus,
                )
                from simai.economy.companies.ai import BusinessAI

                active_companies = list(
                    session.scalars(
                        select(Company).where(Company.status == CompanyStatus.ACTIVE.value)
                    )
                )
                # 1. Tick economico per ogni azienda
                for company in active_companies:
                    tick_report = CompanyService.daily_tick(
                        session, company=company, current_dt=current_dt
                    )
                    company_tick_reports += 1
                    if tick_report.declared_bankrupt:
                        logger.info(
                            "Company {} dichiarata BANKRUPT nel tick",
                            company.id,
                        )

                # 2. Decisioni AI (assunzioni, licenziamenti, dissoluzioni)
                ai_report = BusinessAI.daily_tick(
                    session,
                    active_companies,
                    current_dt=current_dt,
                    rng=self._family_ai._rng,
                )
                companies_evaluated = ai_report.companies_evaluated
                company_hires = ai_report.hires
                company_fires = ai_report.fires
                company_dissolutions = ai_report.dissolutions

                # --- 2e-quinquies. AION daily tick ----------------------
                # 1. Tick spedizioni + attività AI marketplace.
                #    - `AionAI.daily_tick` pubblica listing GOODS dai
                #      GameObject degli NPC, piazza ordini sui listing
                #      più economici e avanza le spedizioni in transito.
                # 2. Import lazy per evitare cicli (economy ↔ npc).
                from simai.economy.aion import AionAI

                try:
                    aion_report = AionAI.daily_tick(
                        session,
                        current_dt=current_dt,
                        rng=self._family_ai._rng,
                    )
                    aion_sellers_evaluated = aion_report.sellers_evaluated
                    aion_buyers_evaluated = aion_report.buyers_evaluated
                    aion_listings_created = aion_report.listings_created
                    aion_orders_placed = aion_report.orders_placed
                    aion_orders_failed = aion_report.orders_failed
                    aion_shipments_advanced = aion_report.shipments_advanced
                    aion_shipments_delivered = aion_report.shipments_delivered
                    aion_errors = list(aion_report.errors)
                    if (
                        aion_listings_created > 0
                        or aion_orders_placed > 0
                        or aion_shipments_delivered > 0
                    ):
                        logger.info(
                            "AION daily tick: listing={} ordini={} "
                            "sped_avanzate={} sped_consegnate={} errori={}",
                            aion_listings_created,
                            aion_orders_placed,
                            aion_shipments_advanced,
                            aion_shipments_delivered,
                            len(aion_errors),
                        )
                except Exception as exc:  # pragma: no cover — safety net
                    msg = f"AION daily tick fallito: {exc}"
                    logger.warning(msg)
                    aion_errors.append(msg)

                # --- 2e-quinquies-bis. Città: paga servizi -------------------
                from simai.city.service import CityService

                city_report = CityService.daily_tick(session, current_dt=current_dt)
                if city_report.services_unpaid > 0:
                    logger.warning(
                        "City daily tick: {} servizi non pagati, balance={}",
                        city_report.services_unpaid,
                        city_report.budget_balance,
                    )

                # --- 2e-sexies. City moodlets sui cittadini -----------------
                from simai.city.mood import CityMoodService

                mood_report = CityMoodService.daily_tick(session, chars, current_dt=current_dt)
                if mood_report.moodlets_applied > 0:
                    logger.debug(
                        "City moodlets: {} applicati a {} cittadini",
                        mood_report.moodlets_applied,
                        mood_report.citizens_processed,
                    )

                # --- 2e-septies. Infrastructure degradation ----------------
                from simai.city.infrastructure.service import (
                    InfrastructureService,
                )

                infra_report = InfrastructureService.daily_tick(session, current_dt=current_dt)
                if infra_report.lights_turned_off > 0:
                    logger.warning(
                        "Infrastructure: {} lampioni spenti per degrado",
                        infra_report.lights_turned_off,
                    )

                # --- 2e-octies. Spostamenti casa-lavoro --------------------
                from simai.city.transport import TransportService

                for c in chars:
                    if not c.is_alive:
                        continue
                    TransportService.daily_commute(
                        session,
                        character=c,
                        current_dt=current_dt,
                        rng=self._family_ai._rng,
                    )

                # --- 2e-quater. Housing AI (compravendite) -----------------
                from simai.npc.housing import RealEstateAI

                housing_report = RealEstateAI.daily_tick(
                    session,
                    chars,
                    current_dt=current_dt,
                    rng=self._family_ai._rng,
                )
                for ev in housing_report.events:
                    logger.info(
                        "Housing: char={} {} lot={} ({})",
                        ev.character_id,
                        ev.action.value,
                        ev.lot_id,
                        ev.reason,
                    )

                # --- 2e-quinquies. Restock fornitori -----------------------
                from simai.world.buy.supplier import SupplierService

                restocked = SupplierService.restock_all(session)
                if restocked > 0:
                    logger.debug("Restock: {} item riforniti", restocked)

                # --- 2e-bis. Promozioni skill-based --------------------------
                from simai.economy.jobs import JobService

                promoted_count = 0
                for c in chars:
                    if not c.is_alive:
                        continue
                    job = JobService.job_of(session, c.id)
                    if (
                        job is None
                        or job.promoted_title is None
                        or job.promotion_skill_level <= 0
                        or job.title == job.promoted_title
                        or job.required_skill_type is None
                    ):
                        continue
                    try:
                        st = SkillType(job.required_skill_type)
                    except ValueError:
                        continue
                    skill = SkillService.get_skill(session, c.id, st)
                    if skill is None or skill.level < job.promotion_skill_level:
                        continue
                    old_title = job.title
                    job.title = job.promoted_title
                    md = dict(job.metadata_json or {})
                    md["promoted_at_day"] = day_index
                    job.metadata_json = md
                    promoted_count += 1
                    logger.info(
                        "Promozione: char={} '{}' -> '{}' (skill {} lvl {})",
                        c.id,
                        old_title,
                        job.promoted_title,
                        st.value,
                        skill.level,
                    )
                if promoted_count:
                    logger.info("Lifecycle: {} promozioni effettuate", promoted_count)

                # --- 2f. Census mensile (primo tick del mese) -----------------
                if self._last_month_key != month_key:
                    from simai.npc.stats import PopulationStatsService

                    PopulationStatsService.snapshot(session, current_dt)
                    census_written = True
                    self._last_month_key = month_key

                self._last_day_index = day_index

            session.commit()

        # ------------------------------------------------------------------
        # 3. Emit eventi (fuori dalla session)
        # ------------------------------------------------------------------
        for cid in birth_ids:
            self._event_bus.emit(EVENT_NPC_BORN, character_id=cid)
        for pid in completed_pregs:
            self._event_bus.emit(EVENT_PREGNANCY_COMPLETED, pregnancy_id=pid)
        for pid in started_pregs:
            self._event_bus.emit(EVENT_PREGNANCY_CONCEIVED, pregnancy_id=pid)
        for t in age_transitions:
            self._event_bus.emit(
                EVENT_NPC_LIFESTAGE_CHANGED,
                character_id=t.character_id,
                field=t.field,
                old_stage=t.old_stage,
                new_stage=t.new_stage,
            )
        for cid in dead_ids:
            self._event_bus.emit(EVENT_NPC_DIED, character_id=cid)
        for cid in orphan_ids:
            self._event_bus.emit(EVENT_FAMILY_ORPHAN_REGISTERED, character_id=cid)
        for child_id, guardian_id in guardian_assignments:
            self._event_bus.emit(
                EVENT_FAMILY_GUARDIAN_ASSIGNED,
                child_id=child_id,
                guardian_id=guardian_id,
            )
        if conception_attempts:
            self._event_bus.emit(
                EVENT_FAMILY_CONCEPTION_ATTEMPT,
                attempts=conception_attempts,
            )
        for a in arrivals:
            self._event_bus.emit(
                EVENT_NPC_ARRIVED,
                character_id=a.character_id,
                location_id=a.to_location_id,
                mode=a.mode,
            )

        return LifecycleReport(
            dead_ids=dead_ids,
            birth_ids=birth_ids,
            pregnancy_completed_ids=completed_pregs,
            pregnancy_started_ids=started_pregs,
            orphan_ids=orphan_ids,
            guardian_assignments=guardian_assignments,
            age_transitions=age_transitions,
            conception_attempts=conception_attempts,
            payday_paid_count=payday_paid_count,
            payday_total_paid=payday_total_paid,
            census_written=census_written,
            daily_work_done=daily_work_done,
            arrival_ids=arrival_ids,
            in_transit_ids=in_transit_ids,
            # --- Banking ---
            bank_interest_paid=bank_interest_paid,
            loan_payments_succeeded=loan_payments_succeeded,
            loan_payments_missed=loan_payments_missed,
            loans_defaulted=loans_defaulted,
            loans_written_off=loans_written_off,
            # --- Companies ---
            companies_evaluated=companies_evaluated,
            company_hires=company_hires,
            company_fires=company_fires,
            company_dissolutions=company_dissolutions,
            company_tick_reports=company_tick_reports,
            # --- AION (Chunk 5.4e) ---
            aion_sellers_evaluated=aion_sellers_evaluated,
            aion_buyers_evaluated=aion_buyers_evaluated,
            aion_listings_created=aion_listings_created,
            aion_orders_placed=aion_orders_placed,
            aion_orders_failed=aion_orders_failed,
            aion_shipments_advanced=aion_shipments_advanced,
            aion_shipments_delivered=aion_shipments_delivered,
            aion_errors=aion_errors,
        )

    # ------------------------------------------------------------------
    # Helper
    # ------------------------------------------------------------------

    def _find_couples(
        self, session: Session, current_secs: int
    ) -> list[tuple[Character, Character]]:
        """Trova le coppie (SPOUSE_OF/PARTNER_OF) con `from_id < to_id`.

        Esclude coppie con partner non ancora nati o defunti al `current_secs`.
        Ritorna `[(mother, father), ...]` con mother=F, father=M.
        """
        kinds = (
            RelationshipKind.SPOUSE_OF.value,
            RelationshipKind.PARTNER_OF.value,
        )
        rows = session.scalars(
            select(Relationship).where(
                Relationship.kind.in_(kinds),
                Relationship.from_id < Relationship.to_id,
            )
        ).all()
        pairs: list[tuple[Character, Character]] = []
        for r in rows:
            a = session.get(Character, r.from_id)
            b = session.get(Character, r.to_id)
            if a is None or b is None:
                continue
            if not a.is_alive or not b.is_alive:
                continue
            if a.birth_total_seconds > current_secs or b.birth_total_seconds > current_secs:
                continue
            if a.sex == "female" and b.sex == "male":
                pairs.append((a, b))
            elif b.sex == "female" and a.sex == "male":
                pairs.append((b, a))
        return pairs

    # ------------------------------------------------------------------
    # Azioni esplicite (per CLI/test)
    # ------------------------------------------------------------------

    def force_daily_work(self, current_dt: AnthalysDateTime) -> LifecycleReport:
        """Forza l'esecuzione del lavoro giornaliero (aging/mortalità/famiglia/economia)."""
        self._last_day_index = None
        return self.tick(current_dt)

    def conceive(
        self,
        *,
        mother_id: int,
        father_id: int,
        current_dt: AnthalysDateTime,
        probability: float = 0.10,
    ) -> int | None:
        """Tenta un concepimento diretto (senza Family AI). Ritorna id o ``None``."""
        with self._session_factory() as session:
            mother = session.get(Character, mother_id)
            father = session.get(Character, father_id)
            if mother is None or father is None:
                return None
            result = PregnancyService.conceive(
                session,
                mother=mother,
                father=father,
                current_dt=current_dt,
                rng=self._family_ai._rng,
                probability=probability,
            )
            session.commit()
            if result.success and result.pregnancy_id is not None:
                self._event_bus.emit(
                    EVENT_PREGNANCY_CONCEIVED,
                    pregnancy_id=result.pregnancy_id,
                    mother_id=mother_id,
                    father_id=father_id,
                )
            return result.pregnancy_id

    def kill(
        self,
        character_id: int,
        current_dt: AnthalysDateTime,
        cause: str = "UNKNOWN",
    ) -> bool:
        """Registra la morte di un Character (dev/test)."""
        try:
            cause_enum = DeathCause(cause.upper())
        except ValueError:
            logger.warning("DeathCause sconosciuta: {}, uso UNKNOWN", cause)
            cause_enum = DeathCause.UNKNOWN

        with self._session_factory() as session:
            c = session.get(Character, character_id)
            if c is None or not c.is_alive:
                return False
            DeathService.register_death(session, c, current_dt, cause_enum)
            session.commit()

        self._event_bus.emit(EVENT_NPC_DIED, character_id=character_id)
        return True


__all__ = ["LifecycleManager", "LifecycleReport"]
