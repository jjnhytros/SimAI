#!/usr/bin/env python
"""Analisi delle skill dopo una simulazione lunga.

Uso:
    uv run python scripts/analyze_skills.py [--top N]
"""

from __future__ import annotations

import argparse
from collections import defaultdict

from sqlalchemy import select

from simai.db.session import get_session_factory
from simai.npc import Character
from simai.npc.genetics import Genome
from simai.npc.skills import (
    MAX_SKILL_LEVEL,
    Skill,
    SkillType,
    talent_for_skill,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--top", type=int, default=10, help="Top N per skill")
    args = parser.parse_args()

    factory = get_session_factory()
    with factory() as s:
        # Carica tutti i character vivi
        chars = {c.id: c for c in s.scalars(select(Character).where(Character.is_alive.is_(True)))}
        print(f"Character vivi: {len(chars)}")
        if not chars:
            return

        # Carica tutte le skill
        skills = list(s.scalars(select(Skill)))
        print(f"Righe skill totali: {len(skills)}")
        print()

        # --- 1. Distribuzione per tipo ---
        print("=== Distribuzione livelli per skill ===")
        by_type: dict[SkillType, list[int]] = defaultdict(list)
        for sk in skills:
            try:
                st = SkillType(sk.skill_type)
            except ValueError:
                continue
            by_type[st].append(sk.level)

        for st in SkillType:
            levels = by_type.get(st, [])
            if not levels:
                print(f"  {st.value:14s}: nessuna pratica")
                continue
            avg = sum(levels) / len(levels)
            max_lvl = max(levels)
            at_max = sum(1 for lv in levels if lv >= MAX_SKILL_LEVEL)
            print(
                f"  {st.value:14s}: n={len(levels):2d} "
                f"avg={avg:5.2f} max={max_lvl:2d} at_max={at_max}"
            )
        print()

        # --- 2. Correlazione talent vs livello ---
        print("=== Correlazione talent <-> livello raggiunto ===")
        buckets: dict[str, list[int]] = {
            "talent <0.8": [],
            "talent 0.8-1.2": [],
            "talent 1.2-1.6": [],
            "talent >=1.6": [],
        }
        for sk in skills:
            c = chars.get(sk.character_id)
            if c is None or not c.genome_json:
                continue
            try:
                st = SkillType(sk.skill_type)
                genome = Genome.from_dict(c.genome_json)
                talent = talent_for_skill(genome, st)
            except (ValueError, KeyError):
                continue
            if talent < 0.8:
                buckets["talent <0.8"].append(sk.level)
            elif talent < 1.2:
                buckets["talent 0.8-1.2"].append(sk.level)
            elif talent < 1.6:
                buckets["talent 1.2-1.6"].append(sk.level)
            else:
                buckets["talent >=1.6"].append(sk.level)

        for label, levels in buckets.items():
            if not levels:
                print(f"  {label:14s}: n=0")
                continue
            avg = sum(levels) / len(levels)
            max_lvl = max(levels)
            print(f"  {label:14s}: n={len(levels):2d} avg={avg:5.2f} max={max_lvl:2d}")
        print()

        # --- 3. Top NPC per skill ---
        print(f"=== Top {args.top} NPC per skill massima ===")
        by_char: dict[int, list[tuple[SkillType, int]]] = defaultdict(list)
        for sk in skills:
            try:
                st = SkillType(sk.skill_type)
            except ValueError:
                continue
            by_char[sk.character_id].append((st, sk.level))

        rows: list[tuple[int, str, int, str, int]] = []
        for cid, char_skills in by_char.items():
            c = chars.get(cid)
            if c is None:
                continue
            char_skills.sort(key=lambda x: -x[1])
            best_skill, best_level = char_skills[0]
            rows.append((cid, c.full_name, best_level, best_skill.value, len(char_skills)))

        rows.sort(key=lambda r: -r[2])
        for cid, name, lvl, skill, n in rows[: args.top]:
            print(f"  [{cid:3d}] {name:30s} best={skill:14s} lv={lvl:2d} (n_skills={n})")
        print()

        # --- 4. Promozioni ---
        print("=== Promozioni ===")
        from simai.economy.jobs import JobService

        promotions = 0
        active_jobs = 0
        for cid, c in chars.items():
            job = JobService.job_of(s, cid)
            if job is None:
                continue
            active_jobs += 1
            if job.promoted_title and job.title == job.promoted_title:
                promotions += 1
                print(f"  [{cid:3d}] {c.full_name:30s} -> {job.title}")
        print(f"  Totale: {promotions} promozioni / {active_jobs} job attivi")
        print()

        # --- 5. Distribuzione talent (sanity) ---
        print("=== Distribuzione talent medio ===")
        talents: list[float] = []
        for c in chars.values():
            if not c.genome_json:
                continue
            try:
                genome = Genome.from_dict(c.genome_json)
                # Talent medio su tutte le skill
                t_avg = sum(talent_for_skill(genome, st) for st in SkillType) / len(list(SkillType))
                talents.append(t_avg)
            except (ValueError, KeyError):
                continue
        if talents:
            print(
                f"  n={len(talents)} avg={sum(talents) / len(talents):.3f} "
                f"min={min(talents):.3f} max={max(talents):.3f}"
            )
            print("  Atteso: avg ~1.25, range ~[0.5, 2.0]")
        print()


if __name__ == "__main__":
    main()
