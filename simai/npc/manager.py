"""NPCManager — ticka tutti gli NPC con AI e persiste lo stato.

Implementa il protocollo `NPCManagerLike` (da `simai.core.simulation_loop`)
ed è iniettabile in `SimulationLoop`.

Design:
  - Carica NPC in-memory dal DB (`load_from_db`).
  - Ticka gli NPC FULL/REDUCED via `AICoordinator`; salta BACKGROUND (LOD).
  - Emette eventi sul `EventBus` per azioni/mood/bisogni critici.
  - Persiste lo stato "dirty" su DB (`flush`), opzionalmente ad ogni N tick.
  - Cache skill in-memory (snapshot), flush batch al `flush()`.

Modalità:
  - **Classica** (`use_bt=False`): `AICoordinator` usa `ActionExecutor`.
  - **BT** (`use_bt=True`): `AICoordinator` usa `BTActionExecutor`.
"""

from __future__ import annotations

import contextlib
import random
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from typing import Any

from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from simai.config.anthalys import SECONDS_PER_DAY
from simai.core.anthalys_datetime import AnthalysDateTime
from simai.core.event_bus import EventBus
from simai.core.lod import LODLevel
from simai.npc.addictions.enums import MAX_DEPENDENCE, AddictionKind
from simai.npc.addictions.service import AddictionService
from simai.npc.ai.coordinator import AICoordinator, TickResult
from simai.npc.ai.executor import ActionProgress, BTActionExecutor
from simai.npc.crafting import (
    MAX_CRAFTS_PER_DAY_PER_NPC,
    CraftingAI,
)
from simai.npc.events import (
    EVENT_NPC_ACTION_STARTED,
    EVENT_NPC_MOOD_CHANGED,
    EVENT_NPC_NEED_CRITICAL,
)
from simai.npc.genetics import Genome
from simai.npc.lifecycle.manager import LifecycleManager
from simai.npc.models import Character
from simai.npc.mood import MoodState
from simai.npc.needs.enums import NeedState
from simai.npc.needs.needs import Needs
from simai.npc.personality import PersonalityService, ValueAxis
from simai.npc.relationships.mentorship import MentorshipService
from simai.npc.skills.enums import DEFAULT_TALENT, SkillType
from simai.npc.skills.models import Skill
from simai.npc.skills.service import SkillService
from simai.npc.skills.talent import talent_for_skill
from simai.npc.traits.derivation import names_to_traits
from simai.npc.traits.enums import Trait

#: Soglia oltre cui emettere `npc.mood.changed`.
MOOD_CHANGE_THRESHOLD: float = 0.05


@dataclass(slots=True)
class SkillSnapshot:
    """Cache in-memory dello stato di una skill.

    Non è un ORM object. Viene sincronizzata con la tabella `skill`
    al `NPCManager.flush()`.
    """

    level: int
    progress: float
    talent: float
    last_used_total_seconds: int
    dirty: bool = False


@dataclass(slots=True)
class NPCState:
    """Stato in-memory di un NPC gestito dal manager."""

    character_id: int
    needs: Needs
    mood: MoodState
    traits: list[Trait]
    coordinator: AICoordinator
    skills: dict[SkillType, SkillSnapshot] = field(default_factory=dict)
    addictions: dict[AddictionKind, float] = field(default_factory=dict)
    pending_addiction_uses: dict[AddictionKind, int] = field(default_factory=dict)
    genome_json: dict[str, Any] = field(default_factory=dict)
    mentorship_skill: SkillType | None = None
    mentorship_boost: float = 0.0
    trait_strength: dict[str, float] = field(default_factory=dict)
    values: dict[ValueAxis, float] = field(default_factory=dict)
    lod: LODLevel = LODLevel.FULL
    dirty: bool = False
    ticks_since_flush: int = 0
    job_skill: SkillType | None = None
    ticks_since_decay: int = 0
    crafts_today: int = 0
    last_craft_day_index: int = -1


class NPCManager:
    """Gestore di tutti gli NPC attivi in una simulazione."""

    def __init__(
        self,
        session_factory: sessionmaker[Session],
        event_bus: EventBus,
        *,
        seed: int = 0,
        autosave_every: int = 0,
        default_lod: LODLevel = LODLevel.FULL,
        lifecycle: LifecycleManager | None = None,
        time_provider: Callable[[], AnthalysDateTime] | None = None,
        use_bt: bool = False,
    ) -> None:
        if autosave_every < 0:
            raise ValueError(f"autosave_every deve essere >= 0, ricevuto {autosave_every}")
        self._session_factory = session_factory
        self._event_bus = event_bus
        self._seed = seed
        self._autosave_every = autosave_every
        self._default_lod = default_lod
        self._states: dict[int, NPCState] = {}
        self._ticks_since_flush: int = 0
        self._flush_count: int = 0
        self._last_flushed_count: int = 0
        self._lifecycle = lifecycle
        self._time_provider = time_provider
        self._use_bt = use_bt
        self._addiction_rng = random.Random(seed + 555)
        self._crafting_rng = random.Random(seed + 777)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def seed(self) -> int:
        return self._seed

    @property
    def autosave_every(self) -> int:
        return self._autosave_every

    @property
    def flush_count(self) -> int:
        return self._flush_count

    @property
    def last_flushed_count(self) -> int:
        return self._last_flushed_count

    @property
    def use_bt(self) -> bool:
        return self._use_bt

    # ------------------------------------------------------------------
    # Caricamento
    # ------------------------------------------------------------------

    def load_from_db(self, *, alive_only: bool = True) -> int:
        """Carica NPC dal DB in-memory. Ritorna il numero di NPC caricati."""
        self._states.clear()
        with self._session_factory() as session:
            stmt = select(Character)
            if alive_only:
                stmt = stmt.where(Character.is_alive.is_(True))
            stmt = stmt.order_by(Character.id)
            characters = list(session.scalars(stmt))
            for c in characters:
                self._states[c.id] = self._state_from_character(c, session)
        logger.info(
            "NPCManager: caricati {} NPC (bt={})",
            len(self._states),
            self._use_bt,
        )
        return len(self._states)

    def _state_from_character(self, c: Character, session: Session) -> NPCState:
        needs = Needs.from_dict(c.needs_json) if c.needs_json else Needs.default()
        mood = MoodState.from_dict(c.mood_json) if c.mood_json else MoodState.default()
        traits = names_to_traits(c.traits_json)
        # Mentorship tracking
        mentorship_skill = None
        mentorship_boost = 0.0
        mentor_rel = MentorshipService.active_mentor_of(session, c.id)
        if mentor_rel is not None:
            md = mentor_rel.metadata_json or {}
            skill_name = md.get("skill_type")
            if isinstance(skill_name, str):
                try:
                    mentorship_skill = SkillType(skill_name)
                    mentorship_boost = MentorshipService.talent_boost_for(
                        mentor_rel, mentorship_skill
                    )
                except ValueError:
                    pass

        # Job skill (Chunk 3.14)
        job_skill: SkillType | None = None
        from simai.economy.jobs import JobService

        job = JobService.job_of(session, c.id)
        if job is not None and job.required_skill_type:
            with contextlib.suppress(ValueError):
                job_skill = SkillType(job.required_skill_type)

        # Personality (Chunk 3.6d)
        PersonalityService.initialize(c)
        trait_strength = PersonalityService.get_trait_strength(c)
        values = PersonalityService.get_values(c)

        # Cache skills
        skills_dict: dict[SkillType, SkillSnapshot] = {}
        for skill in SkillService.all_skills(session, c.id):
            try:
                st = SkillType(skill.skill_type)
            except ValueError:
                continue
            skills_dict[st] = SkillSnapshot(
                level=skill.level,
                progress=skill.progress,
                talent=skill.talent,
                last_used_total_seconds=skill.last_used_total_seconds,
            )

        # Cache addictions
        addictions_dict: dict[AddictionKind, float] = {}
        for add in AddictionService.all_of(session, c.id):
            try:
                ak = AddictionKind(add.kind)
            except ValueError:
                continue
            addictions_dict[ak] = add.dependence_level

        bt_executor = BTActionExecutor() if self._use_bt else None
        coordinator = AICoordinator(
            seed=c.master_seed + c.id,
            bt_executor=bt_executor,
        )

        # Restore azione (solo in modalità classica: BT non è resumable)
        if not self._use_bt and c.current_action_json:
            try:
                progress = ActionProgress.from_dict(c.current_action_json)
                coordinator.executor.restore(progress)
            except (KeyError, ValueError, TypeError) as exc:
                logger.warning(
                    "Impossibile ripristinare azione per char {}: {}",
                    c.id,
                    exc,
                )

        return NPCState(
            character_id=c.id,
            needs=needs,
            mood=mood,
            traits=traits,
            coordinator=coordinator,
            skills=skills_dict,
            genome_json=dict(c.genome_json or {}),
            lod=self._default_lod,
            dirty=False,
            ticks_since_flush=0,
            addictions=addictions_dict,
            mentorship_skill=mentorship_skill,
            mentorship_boost=mentorship_boost,
            trait_strength=trait_strength,
            values=values,
            job_skill=job_skill,
        )

    # ------------------------------------------------------------------
    # Protocollo NPCManagerLike
    # ------------------------------------------------------------------

    def update_all_npcs(self) -> None:
        """Ticka tutti gli NPC attivi (FULL/REDUCED). Salta BACKGROUND."""
        # 1. Lifecycle (una sola chiamata per tick)
        in_transit: set[int] = set()
        if self._lifecycle is not None and self._time_provider is not None:
            now = self._time_provider()
            report = self._lifecycle.tick(now)

            for cid in report.dead_ids:
                self._states.pop(cid, None)

            if report.birth_ids:
                with self._session_factory() as session:
                    for cid in report.birth_ids:
                        c = session.get(Character, cid)
                        if c is not None:
                            self._states[cid] = self._state_from_character(c, session)

            in_transit = set(report.in_transit_ids)

        # 2. Tick NPC (salta quelli in transito)
        simulated = 0
        for state in list(self._states.values()):
            if not state.lod.is_simulated:
                continue
            if state.character_id in in_transit:
                continue
            self._tick_one(state)
            simulated += 1

        self._ticks_since_flush += 1
        if self._autosave_every > 0 and self._ticks_since_flush >= self._autosave_every:
            self.flush()

        if simulated == 0 and self._states:
            logger.debug("NPCManager: nessun NPC simulato (tutti BACKGROUND o vuoto)")

    def count(self) -> int:
        return len(self._states)

    def count_simulated(self) -> int:
        return sum(1 for s in self._states.values() if s.lod.is_simulated)

    def count_by_lod(self) -> dict[LODLevel, int]:
        counts: dict[LODLevel, int] = dict.fromkeys(LODLevel, 0)
        for s in self._states.values():
            counts[s.lod] += 1
        return counts

    # ------------------------------------------------------------------
    # Tick singolo NPC
    # ------------------------------------------------------------------

    def _tick_one(self, state: NPCState) -> None:
        """Ticka un singolo NPC. Applica skill XP, addiction uses, personality."""
        # 1. Input per il coordinator
        skill_levels = {st: snap.level for st, snap in state.skills.items()}
        cravings = self._compute_cravings(state)

        # 2. Tick del coordinator
        result = state.coordinator.tick(
            state.needs,
            state.mood,
            state.traits,
            skill_levels,
            cravings,
            state.values,
            state.job_skill,
        )

        # 3. Emit eventi
        self._emit_tick_events(state, result)

        # 4. Side-effects

        # 4a. Skill XP
        if result.skill_xp_delta:
            self._apply_skill_xp(state, result.skill_xp_delta)

        # 4b. Addiction uses
        if result.addiction_use:
            for kind in result.addiction_use:
                state.pending_addiction_uses[kind] = state.pending_addiction_uses.get(kind, 0) + 1
            state.dirty = True

        # 4c. Personality reinforce
        if result.action_started is not None:
            PersonalityService.reinforce_inmemory(
                state.trait_strength,
                state.values,
                result.action_started.type,
            )
            state.dirty = True

        # 4d. Personality decay (Chunk 3.14 — 1 volta al giorno = 336 tick)
        state.ticks_since_decay += 1
        if state.ticks_since_decay >= 336:
            state.ticks_since_decay = 0
            PersonalityService.decay_inmemory(state.trait_strength, state.values)
            # Riallinea state.traits agli attivi
            active = PersonalityService.active_traits(state.trait_strength)
            state.traits = names_to_traits(active)
            state.dirty = True

        # 4e. Crafting AI (Chunk 4.8b)
        if self._time_provider is not None:
            now = self._time_provider()
            current_day_index = now.to_total_seconds() // SECONDS_PER_DAY

            # Reset del contatore al cambio giorno
            if state.last_craft_day_index != current_day_index:
                state.crafts_today = 0
                state.last_craft_day_index = current_day_index

            if state.crafts_today < MAX_CRAFTS_PER_DAY_PER_NPC:
                # Recupera il character dalla sessione
                with self._session_factory() as session:
                    c = session.get(Character, state.character_id)
                    if c is not None:
                        report = CraftingAI.maybe_craft(
                            session,
                            c,
                            current_dt=now,
                            rng=self._crafting_rng,
                            crafts_today=state.crafts_today,
                        )
                        if report is not None and report.attempted and report.success:
                            state.crafts_today += 1
                            state.dirty = True
                            logger.debug(
                                "Craft AI: char={} {} → {}",
                                state.character_id,
                                report.recipe_code,
                                report.output_type,
                            )
                            # Non incrementare se fallito
                        session.commit()

        # 5. Update stato
        state.needs = result.needs
        state.mood = result.mood
        state.dirty = True
        state.ticks_since_flush += 1

    # ------------------------------------------------------------------
    # Persistenza
    # ------------------------------------------------------------------

    def flush(self) -> int:
        """Persiste lo stato dirty su DB. Ritorna il numero di NPC persistiti."""
        dirty_states = [s for s in self._states.values() if s.dirty]
        if not dirty_states:
            self._ticks_since_flush = 0
            self._last_flushed_count = 0
            return 0

        persisted = 0
        with self._session_factory() as session:
            dirty_ids = [s.character_id for s in dirty_states]
            all_skill_rows: dict[tuple[int, str], Skill] = {
                (sk.character_id, sk.skill_type): sk
                for sk in session.scalars(select(Skill).where(Skill.character_id.in_(dirty_ids)))
            }

            for state in dirty_states:
                c = session.get(Character, state.character_id)
                if c is None:
                    logger.warning(
                        "NPCManager.flush: char {} non trovato",
                        state.character_id,
                    )
                    state.dirty = False
                    state.ticks_since_flush = 0
                    continue

                c.needs_json = state.needs.to_dict()
                c.mood_json = state.mood.to_dict()
                progress = state.coordinator.current_progress
                c.current_action_json = progress.to_dict() if progress is not None else None
                c.last_ai_tick += state.ticks_since_flush

                # Flush skill dirty
                for skill_type, snapshot in state.skills.items():
                    if not snapshot.dirty:
                        continue
                    key = (state.character_id, skill_type.value)
                    skill_row = all_skill_rows.get(key)
                    if skill_row is None:
                        skill_row = Skill(
                            character_id=state.character_id,
                            skill_type=skill_type.value,
                            level=snapshot.level,
                            progress=snapshot.progress,
                            talent=snapshot.talent,
                            last_used_total_seconds=snapshot.last_used_total_seconds,
                        )
                        session.add(skill_row)
                        all_skill_rows[key] = skill_row
                    else:
                        skill_row.level = snapshot.level
                        skill_row.progress = snapshot.progress
                        skill_row.last_used_total_seconds = snapshot.last_used_total_seconds
                    snapshot.dirty = False

                # Flush addiction uses
                if state.pending_addiction_uses:
                    for kind, count in state.pending_addiction_uses.items():
                        for _ in range(count):
                            use_result = AddictionService.use(
                                session,
                                character_id=state.character_id,
                                kind=kind,
                                current_dt=self._time_provider()
                                if self._time_provider is not None
                                else AnthalysDateTime(1, 1, 1),
                                rng=self._addiction_rng,
                            )
                            if use_result.dependence_after > 0:
                                state.addictions[kind] = use_result.dependence_after
                    state.pending_addiction_uses.clear()

                # Personality sync (Chunk 3.6d)
                PersonalityService.sync_from_state(c, state.trait_strength, state.values)

                state.dirty = False
                state.ticks_since_flush = 0
                persisted += 1

            session.commit()

        self._flush_count += 1
        self._ticks_since_flush = 0
        self._last_flushed_count = persisted
        logger.debug("NPCManager.flush: {} NPC persistiti", persisted)
        return persisted

    # ------------------------------------------------------------------
    # LOD
    # ------------------------------------------------------------------

    def set_lod(self, character_id: int, lod: LODLevel) -> None:
        if character_id not in self._states:
            raise KeyError(f"NPC {character_id} non caricato")
        self._states[character_id].lod = lod

    def set_default_lod(self, lod: LODLevel) -> None:
        self._default_lod = lod

    def reset_lod_to_default(self) -> None:
        for state in self._states.values():
            state.lod = self._default_lod

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def __contains__(self, character_id: object) -> bool:
        return character_id in self._states

    def __iter__(self) -> Iterator[NPCState]:
        return iter(self._states.values())

    def get_state(self, character_id: int) -> NPCState | None:
        return self._states.get(character_id)

    def all_states(self) -> list[NPCState]:
        return list(self._states.values())

    def stats(self) -> dict[str, Any]:
        by_lod = self.count_by_lod()
        total_skills = sum(len(s.skills) for s in self._states.values())
        dirty_skills = sum(
            1 for s in self._states.values() for snap in s.skills.values() if snap.dirty
        )
        return {
            "total": len(self._states),
            "simulated": self.count_simulated(),
            "full": by_lod[LODLevel.FULL],
            "reduced": by_lod[LODLevel.REDUCED],
            "background": by_lod[LODLevel.BACKGROUND],
            "flush_count": self._flush_count,
            "ticks_since_flush": self._ticks_since_flush,
            "use_bt": self._use_bt,
            "total_skills": total_skills,
            "dirty_skills": dirty_skills,
        }

    # ------------------------------------------------------------------
    # Helper interni
    # ------------------------------------------------------------------

    def _compute_cravings(self, state: NPCState) -> dict[AddictionKind, float]:
        """Calcola il craving attuale per ogni addiction dello NPC.

        Formula semplificata (usata dal decision maker):
            craving = min(1.0, dependence / MAX_DEPENDENCE)

        La formula completa (con `days_since_use`) vive in
        `AddictionService.craving_factor`. Qui usiamo dependence pura perché
        il manager non traccia il tempo di ultimo uso in cache.
        """
        if not state.addictions:
            return {}
        return {
            kind: min(1.0, dep / MAX_DEPENDENCE)
            for kind, dep in state.addictions.items()
            if dep > 0.0
        }

    def _emit_tick_events(self, state: NPCState, result: TickResult) -> None:
        """Emette eventi su EventBus relativi al tick corrente."""
        # Action started
        if result.action_started is not None:
            self._event_bus.emit(
                EVENT_NPC_ACTION_STARTED,
                character_id=state.character_id,
                action=result.action_started.type.value,
                label=result.action_started.label,
            )

        # Need critical
        for t in result.needs_transitions:
            if t.to_state is NeedState.CRITICAL:
                self._event_bus.emit(
                    EVENT_NPC_NEED_CRITICAL,
                    character_id=state.character_id,
                    need=t.need.value,
                    value=result.needs.get(t.need),
                )

        # Mood changed (soglia)
        old_happiness = state.mood.happiness
        new_happiness = result.mood.happiness
        if abs(new_happiness - old_happiness) > MOOD_CHANGE_THRESHOLD:
            self._event_bus.emit(
                EVENT_NPC_MOOD_CHANGED,
                character_id=state.character_id,
                old=old_happiness,
                new=new_happiness,
                delta=new_happiness - old_happiness,
            )

    def _apply_skill_xp(
        self,
        state: NPCState,
        xp_delta: dict[SkillType, float],
    ) -> None:
        """Applica XP alle skill in cache. Moltiplica per talent.

        Se la skill non esiste in cache, la crea (level 0) con talent
        derivato dal genoma dello NPC.
        """
        if self._time_provider is None:
            return
        current_secs = self._time_provider().to_total_seconds()

        for skill_type, raw_xp in xp_delta.items():
            snapshot = state.skills.get(skill_type)
            if snapshot is None:
                talent = DEFAULT_TALENT
                boost = state.mentorship_boost if state.mentorship_skill == skill_type else 0.0
                try:
                    genome = Genome.from_dict(state.genome_json)
                    talent = talent_for_skill(genome, skill_type, mentorship_boost=boost)
                except (ValueError, KeyError):
                    pass
                snapshot = SkillSnapshot(
                    level=0,
                    progress=0.0,
                    talent=talent,
                    last_used_total_seconds=current_secs,
                )
                state.skills[skill_type] = snapshot

            actual_xp = raw_xp * snapshot.talent
            new_level, new_progress, levels_gained = SkillService.compute_xp_application(
                snapshot.level, snapshot.progress, actual_xp
            )
            snapshot.level = new_level
            snapshot.progress = new_progress
            snapshot.last_used_total_seconds = current_secs
            snapshot.dirty = True

            if levels_gained > 0:
                logger.debug(
                    "Skill level up: char={} {} -> {}",
                    state.character_id,
                    skill_type.value,
                    new_level,
                )


__all__ = [
    "MOOD_CHANGE_THRESHOLD",
    "NPCManager",
    "NPCState",
    "SkillSnapshot",
]
