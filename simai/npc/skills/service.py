"""SkillService — apprendimento, progresso, decay."""

from __future__ import annotations

from dataclasses import dataclass

from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.config.anthalys import SECONDS_PER_DAY
from simai.core.anthalys_datetime import AnthalysDateTime
from simai.npc.models import Character
from simai.npc.skills.enums import (
    DECAY_GRACE_DAYS,
    DECAY_RATE_PER_DAY,
    DEFAULT_TALENT,
    LEVEL_PENALTY_MAX,
    MAX_SKILL_LEVEL,
    XP_BASE,
    XP_PER_TICK,
    XP_STEP,
    SkillType,
)
from simai.npc.skills.models import Skill


@dataclass(frozen=True, slots=True)
class SkillDecay:
    """Una skill che ha subito decay."""

    skill_type: SkillType
    old_level: int
    new_level: int
    days_inactive: int


@dataclass(frozen=True, slots=True)
class LevelUpResult:
    """Esito di un `add_progress` con cambio di livello."""

    skill_type: SkillType
    old_level: int
    new_level: int
    xp_consumed: float


class SkillService:
    """Servizio stateless per la gestione delle abilità."""

    # ------------------------------------------------------------------
    # Formule
    # ------------------------------------------------------------------

    @staticmethod
    def xp_to_next_level(level: int) -> int:
        """XP per salire dal livello `level` a `level + 1`.

        Ritorna 0 se `level >= MAX_SKILL_LEVEL`.
        """
        if level < 0:
            raise ValueError(f"level non può essere negativo: {level}")
        if level >= MAX_SKILL_LEVEL:
            return 0
        return XP_BASE + XP_STEP * level

    @staticmethod
    def level_penalty(level: int) -> float:
        """Fattore riduttivo dell'apprendimento in [0.2, 1.0]."""
        if level < 0:
            raise ValueError(f"level non può essere negativo: {level}")
        if level >= MAX_SKILL_LEVEL:
            return 1.0 - LEVEL_PENALTY_MAX
        return 1.0 - (level / MAX_SKILL_LEVEL) * LEVEL_PENALTY_MAX

    @staticmethod
    def xp_per_tick(level: int, talent: float) -> float:
        """XP guadagnati per un tick di pratica a un dato livello e talent."""
        if talent <= 0:
            raise ValueError(f"talent deve essere > 0, ricevuto {talent}")
        return XP_PER_TICK * talent * SkillService.level_penalty(level)

    # ------------------------------------------------------------------
    # Pure operations (per cache in-memory, senza ORM)
    # ------------------------------------------------------------------

    @staticmethod
    def compute_xp_application(
        level: int,
        progress: float,
        xp_delta: float,
    ) -> tuple[int, float, int]:
        """Applica XP a una coppia (level, progress).

        Ritorna `(new_level, new_progress, levels_gained)`. Non tocca DB.
        """
        if xp_delta < 0:
            raise ValueError(f"xp_delta deve essere >= 0, ricevuto {xp_delta}")
        old_level = level
        remaining = xp_delta
        while remaining > 0 and level < MAX_SKILL_LEVEL:
            xp_needed = SkillService.xp_to_next_level(level)
            xp_left = xp_needed * (1.0 - progress)
            if remaining >= xp_left:
                remaining -= xp_left
                level += 1
                progress = 0.0
            else:
                progress += remaining / xp_needed
                remaining = 0.0
        if level >= MAX_SKILL_LEVEL:
            progress = 0.0
        return level, progress, level - old_level

    @staticmethod
    def compute_decay(
        level: int,
        progress: float,
        days_inactive: int,
    ) -> tuple[int, float]:
        """Applica un giorno di decay a (level, progress).

        Ritorna `(new_level, new_progress)`. Non tocca DB.
        """
        if days_inactive < DECAY_GRACE_DAYS:
            return level, progress
        total_before = level + progress
        total_after = total_before - DECAY_RATE_PER_DAY
        if total_after <= 0.0:
            return 0, 0.0
        new_level = int(total_after)
        new_progress = total_after - new_level
        return new_level, new_progress

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    @staticmethod
    def get_skill(
        session: Session,
        character_id: int,
        skill_type: SkillType,
    ) -> Skill | None:
        """Ritorna la skill del character se esiste, altrimenti ``None``."""
        return session.scalars(
            select(Skill).where(
                Skill.character_id == character_id,
                Skill.skill_type == skill_type.value,
            )
        ).first()

    @staticmethod
    def all_skills(session: Session, character_id: int) -> list[Skill]:
        """Tutte le skill di un character, ordinate per skill_type."""
        return list(
            session.scalars(
                select(Skill).where(Skill.character_id == character_id).order_by(Skill.skill_type)
            )
        )

    @staticmethod
    def get_or_create(
        session: Session,
        *,
        character_id: int,
        skill_type: SkillType,
        talent: float | None = None,
        current_dt: AnthalysDateTime,
        character: Character | None = None,
    ) -> Skill:
        """Ritorna la skill se esiste, altrimenti la crea a livello 0.

        Se `talent` è None e `character` è fornito, deriva il talent dal
        genoma del character (3.6c). Altrimenti usa `DEFAULT_TALENT`.
        """
        existing = SkillService.get_skill(session, character_id, skill_type)
        if existing is not None:
            return existing

        if talent is None:
            if character is not None and character.genome_json:
                from simai.npc.genetics import Genome
                from simai.npc.skills.talent import talent_for_skill

                try:
                    genome = Genome.from_dict(character.genome_json)
                    talent = talent_for_skill(genome, skill_type)
                except (ValueError, KeyError):
                    talent = DEFAULT_TALENT
            else:
                talent = DEFAULT_TALENT

        if talent <= 0:
            raise ValueError(f"talent deve essere > 0, ricevuto {talent}")

        skill = Skill(
            character_id=character_id,
            skill_type=skill_type.value,
            level=0,
            progress=0.0,
            talent=talent,
            last_used_total_seconds=current_dt.to_total_seconds(),
        )
        session.add(skill)
        session.flush()
        return skill

    # ------------------------------------------------------------------
    # Learning
    # ------------------------------------------------------------------

    @staticmethod
    def add_progress(
        session: Session,
        skill: Skill,
        *,
        xp_delta: float,
        current_dt: AnthalysDateTime,
    ) -> LevelUpResult | None:
        """Aggiunge `xp_delta` XP alla skill. Applica level-up con carryover.

        Ritorna `LevelUpResult` se c'è stato un level-up, altrimenti ``None``.
        Aggiorna sempre `last_used_total_seconds`.
        """
        old_level = skill.level
        new_level, new_progress, levels_gained = SkillService.compute_xp_application(
            skill.level, skill.progress, xp_delta
        )
        skill.level = new_level
        skill.progress = new_progress
        skill.last_used_total_seconds = current_dt.to_total_seconds()
        session.flush()

        if levels_gained > 0:
            logger.debug(
                "Level up: char={} skill={} {} -> {}",
                skill.character_id,
                skill.skill_type,
                old_level,
                new_level,
            )
            return LevelUpResult(
                skill_type=SkillType(skill.skill_type),
                old_level=old_level,
                new_level=new_level,
                xp_consumed=xp_delta,
            )
        return None

    # ------------------------------------------------------------------
    # Decay
    # ------------------------------------------------------------------

    @staticmethod
    def apply_daily_decay(
        session: Session,
        *,
        character: Character,
        current_dt: AnthalysDateTime,
    ) -> list[SkillDecay]:
        """Applica un giorno di decay a tutte le skill del character.

        Regole:
          - Dopo `DECAY_GRACE_DAYS` di inattività, sottrae `DECAY_RATE_PER_DAY`
            livelli al giorno.
          - Il decay agisce su `level + progress` come valore continuo.
          - A 0 non si scende sotto.

        Ritorna la lista delle skill che hanno subito decay.
        """
        current_secs = current_dt.to_total_seconds()
        decayed: list[SkillDecay] = []

        skills = SkillService.all_skills(session, character.id)
        for skill in skills:
            days_inactive = int((current_secs - skill.last_used_total_seconds) / SECONDS_PER_DAY)
            if days_inactive < DECAY_GRACE_DAYS:
                continue

            old_level = skill.level
            old_progress = skill.progress
            new_level, new_progress = SkillService.compute_decay(
                skill.level, skill.progress, days_inactive
            )
            if new_level != old_level or abs(new_progress - old_progress) > 1e-9:
                skill.level = new_level
                skill.progress = new_progress
                decayed.append(
                    SkillDecay(
                        skill_type=SkillType(skill.skill_type),
                        old_level=old_level,
                        new_level=new_level,
                        days_inactive=days_inactive,
                    )
                )

        if decayed:
            session.flush()
            logger.debug(
                "Skill decay: char={} {} skill decadute",
                character.id,
                len(decayed),
            )
        return decayed

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    @staticmethod
    def total_xp_to_max() -> int:
        """XP cumulativi per portare una skill da 0 a `MAX_SKILL_LEVEL`."""
        return sum(SkillService.xp_to_next_level(lvl) for lvl in range(MAX_SKILL_LEVEL))


__all__ = ["LevelUpResult", "SkillDecay", "SkillService"]
