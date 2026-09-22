"""LifeNarrativeService — composizione della storia di vita (template-based)."""

from __future__ import annotations

from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from simai.core.anthalys_datetime import AnthalysDateTime
from simai.npc.background.service import BackgroundService
from simai.npc.lifestage_service import LifeStageService
from simai.npc.models import Character
from simai.npc.reflection.models import ReflectionEntry
from simai.npc.relationships.family_tree import FamilyTreeService
from simai.npc.skills.service import SkillService


@dataclass(frozen=True, slots=True)
class LifeChapter:
    """Capitolo della storia di vita."""

    title: str
    text: str
    at_age: int | None = None


@dataclass(frozen=True, slots=True)
class LifeNarrative:
    """Storia di vita composta."""

    character_name: str
    current_age_years: int
    chapters: list[LifeChapter] = field(default_factory=list)
    summary: str = ""


class LifeNarrativeService:
    """Servizio stateless che compone una storia di vita."""

    @staticmethod
    def compose(
        session: Session,
        character: Character,
        *,
        current_dt: AnthalysDateTime,
    ) -> LifeNarrative:
        """Compone la narrativa di vita del character."""
        age_secs = LifeStageService.age_seconds_at(character.birth_total_seconds, current_dt)
        age_years, _ = LifeStageService.age_years_days(age_secs)

        chapters: list[LifeChapter] = []

        # 1. Nascita
        chapters.append(
            LifeChapter(
                title="Nascita",
                text=(f"{character.full_name} è nato/a il {character.birth_iso}."),
                at_age=0,
            )
        )

        # 2. Background formativo
        bg_events = BackgroundService.all_of(session, character.id)
        for ev in sorted(bg_events, key=lambda e: e.occurred_at_age):
            chapters.append(
                LifeChapter(
                    title=ev.kind,
                    text=ev.text,
                    at_age=ev.occurred_at_age,
                )
            )

        # 3. Famiglia
        parents = FamilyTreeService.parents_of(session, character.id)
        if parents:
            names = ", ".join(p.full_name for p in parents)
            chapters.append(
                LifeChapter(
                    title="Famiglia d'origine",
                    text=f"Figlio/a di {names}.",
                )
            )

        siblings = FamilyTreeService.siblings_of(session, character.id)
        if siblings:
            chapters.append(
                LifeChapter(
                    title="Fratelli/sorelle",
                    text=f"Ha {len(siblings)} fratelli/sorelle.",
                )
            )

        # 4. Skill principali
        skills = SkillService.all_skills(session, character.id)
        top_skills = sorted(skills, key=lambda s: -s.level)[:3]
        for sk in top_skills:
            if sk.level >= 5:
                chapters.append(
                    LifeChapter(
                        title=f"Talento in {sk.skill_type}",
                        text=(f"Ha sviluppato competenze in {sk.skill_type} (livello {sk.level})."),
                    )
                )

        # 5. Riflessioni recenti
        recent = list(
            session.query(ReflectionEntry)
            .filter(ReflectionEntry.character_id == character.id)
            .order_by(ReflectionEntry.at_total_seconds.desc())
            .limit(3)
            .all()
        )
        for entry in reversed(recent):
            chapters.append(
                LifeChapter(
                    title="Riflessione",
                    text=f'"{entry.text}"',
                )
            )

        # 6. Stato attuale
        if not character.is_alive:
            chapters.append(
                LifeChapter(
                    title="Fine",
                    text=(
                        f"È morto/a il {character.death_iso} "
                        f"(causa: {character.death_cause or 'sconosciuta'})."
                    ),
                )
            )

        summary = LifeNarrativeService._build_summary(character, age_years, chapters)

        return LifeNarrative(
            character_name=character.full_name,
            current_age_years=int(age_years),
            chapters=chapters,
            summary=summary,
        )

    @staticmethod
    def _build_summary(
        character: Character,
        age_years: int,
        chapters: list[LifeChapter],
    ) -> str:
        state = "vivo/a" if character.is_alive else "morto/a"
        return (
            f"{character.full_name}, {int(age_years)} anni, {state}. "
            f"{len(chapters)} momenti nella sua storia."
        )


__all__ = ["LifeChapter", "LifeNarrative", "LifeNarrativeService"]
