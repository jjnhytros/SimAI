#!/usr/bin/env python
"""Analisi bilanciamento SimAI dopo simulazione lunga.

Uso:
    uv run python scripts/analyze_simulation.py [--top N]

Copre:
  - Popolazione: vivi/morti/nati, distribuzione sesso/fascia età
  - Skill: distribuzione livelli, cap saturation, correlazione con età
  - Personality: trait strength, valori
  - Addictions: prevalenza, dependence, tipi
  - Relationships: breakup, boredom, connection, polyamory
  - Crisis: frequency, resolution rate
  - Reflections: entries per NPC
  - Mentorship: sessions, graduations
  - Economy: bilanci, jobs, promozioni
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from statistics import median

from sqlalchemy import func, select

from simai.core.anthalys_datetime import AnthalysDateTime
from simai.db.session import get_session_factory
from simai.npc import Character
from simai.npc.addictions import Addiction, AddictionKind
from simai.npc.lifestage_service import LifeStageService
from simai.npc.personality import PersonalityService, ValueAxis
from simai.npc.reflection import CrisisService
from simai.npc.reflection.models import ReflectionEntry
from simai.npc.relationships import (
    BoredomService,
    ConnectionService,
)
from simai.npc.relationships.models import Relationship
from simai.npc.skills import MAX_SKILL_LEVEL, Skill, SkillType


def hr(title: str) -> None:
    print()
    print("=" * 70)
    print(f"  {title}")
    print("=" * 70)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--top", type=int, default=10)
    parser.add_argument(
        "--at-tick",
        type=int,
        default=None,
        help="Tick di riferimento (default: leggo settings).",
    )
    args = parser.parse_args()

    # Determine current tick from max last_ai_tick
    factory = get_session_factory()

    with factory() as s:
        # --------------------------------------------------------------
        hr("POPOLAZIONE")
        # --------------------------------------------------------------
        alive = list(s.scalars(select(Character).where(Character.is_alive.is_(True))))
        dead = list(s.scalars(select(Character).where(Character.is_alive.is_(False))))
        total = len(alive) + len(dead)

        print(f"Totale character nel DB: {total}")
        print(f"Vivi:  {len(alive)}")
        print(f"Morti: {len(dead)}")
        if total > 0:
            print(f"Tasso sopravvivenza: {100 * len(alive) / total:.1f}%")

        if not alive:
            print("\n[!] Nessun character vivo. Analisi interrotta.")
            return

        # Sesso
        sex_counts: Counter[str] = Counter(c.sex for c in alive)
        print("\nDistribuzione sesso (vivi):")
        for sex, count in sex_counts.most_common():
            print(f"  {sex:10s}: {count} ({100 * count / len(alive):.1f}%)")

        # Età
        # Usa il tick più alto come riferimento
        max_tick = s.scalar(select(func.max(Character.last_ai_tick))) or 0
        print(f"\nTick di riferimento (max last_ai_tick): {max_tick}")

        # Ricostruisci current_dt
        # Per semplicità: assumo anno 5775 + tick/tick_per_year
        # Ma meglio usare settings starting_year + tick
        from simai.config.settings import get_settings
        from simai.core.time_manager import TimeManager

        settings = get_settings()
        start = AnthalysDateTime(
            settings.starting_year,
            settings.starting_month,
            settings.starting_day,
        )
        tm = TimeManager(start=start, tick_minutes=settings.tick_minutes)
        tm.advance_ticks(max_tick)
        current_dt = tm.current
        print(f"Data corrente stimata: {current_dt}")

        ages: list[int] = []
        for c in alive:
            age_secs = LifeStageService.age_seconds_at(c.birth_total_seconds, current_dt)
            years, _ = LifeStageService.age_years_days(age_secs)
            ages.append(years)
        if ages:
            print("\nEtà (anni Anthalys):")
            print(f"  min: {min(ages)}")
            print(f"  mediana: {int(median(ages))}")
            print(f"  media: {sum(ages) / len(ages):.1f}")
            print(f"  max: {max(ages)}")

        # Fascia pediatrica
        ped_counter: Counter[str] = Counter(c.life_stage_pediatric for c in alive)
        print("\nFasce pediatriche (vivi):")
        for stage, count in ped_counter.most_common():
            print(f"  {stage:22s}: {count}")

        # --------------------------------------------------------------
        hr("SKILL")
        # --------------------------------------------------------------
        all_skills = list(s.scalars(select(Skill)))
        by_type: dict[SkillType, list[int]] = defaultdict(list)
        for sk in all_skills:
            try:
                st = SkillType(sk.skill_type)
            except ValueError:
                continue
            by_type[st].append(sk.level)

        print(f"Righe skill totali: {len(all_skills)}")
        print(f"\n{'Skill':14s} {'n':>4s} {'avg':>6s} {'med':>6s} {'max':>4s} {'cap':>4s}")
        for st in SkillType:
            levels = by_type.get(st, [])
            if not levels:
                print(f"{st.value:14s} {'0':>4s}")
                continue
            avg = sum(levels) / len(levels)
            med = median(levels)
            mx = max(levels)
            at_cap = sum(1 for lv in levels if lv >= MAX_SKILL_LEVEL)
            print(f"{st.value:14s} {len(levels):>4d} {avg:>6.2f} {med:>6.0f} {mx:>4d} {at_cap:>4d}")

        # --------------------------------------------------------------
        hr("PERSONALITY (tratti dinamici)")
        # --------------------------------------------------------------
        trait_strength_all: dict[str, list[float]] = defaultdict(list)
        for c in alive:
            strength = PersonalityService.get_trait_strength(c)
            for name, s_val in strength.items():
                trait_strength_all[name].append(s_val)

        print(f"Tratti con almeno un portatore: {len(trait_strength_all)}")
        print(f"\n{'Tratto':30s} {'n':>5s} {'avg':>6s} {'active':>6s}")
        for name, strengths in sorted(trait_strength_all.items(), key=lambda kv: -len(kv[1])):
            avg = sum(strengths) / len(strengths)
            active = sum(1 for s_val in strengths if s_val >= 0.30)
            print(f"{name:30s} {len(strengths):>5d} {avg:>6.3f} {active:>6d}")

        # --------------------------------------------------------------
        hr("VALUES (assi valoriali)")
        # --------------------------------------------------------------
        values_all: dict[ValueAxis, list[float]] = defaultdict(list)
        for c in alive:
            values = PersonalityService.get_values(c)
            for axis, v in values.items():
                values_all[axis].append(v)

        print(f"{'Asse':18s} {'n':>5s} {'avg':>6s} {'min':>6s} {'max':>6s}")
        for axis in ValueAxis:
            vals = values_all.get(axis, [])
            if not vals:
                continue
            avg = sum(vals) / len(vals)
            print(
                f"{axis.value:18s} {len(vals):>5d} {avg:>6.3f} {min(vals):>6.3f} {max(vals):>6.3f}"
            )

        # --------------------------------------------------------------
        hr("ADDICTIONS")
        # --------------------------------------------------------------
        addictions = list(s.scalars(select(Addiction)))
        by_add_kind: dict[AddictionKind, list[float]] = defaultdict(list)
        for a in addictions:
            try:
                ak = AddictionKind(a.kind)
            except ValueError:
                continue
            by_add_kind[ak].append(a.dependence_level)

        print(f"Addictions totali: {len(addictions)}")
        print(f"Character con ≥1 addiction: {len({a.character_id for a in addictions})}")
        print(f"\n{'Kind':12s} {'n':>4s} {'avg_dep':>8s} {'max_dep':>8s}")
        for ak in AddictionKind:
            deps = by_add_kind.get(ak, [])
            if not deps:
                print(f"{ak.value:12s} {'0':>4s}")
                continue
            avg = sum(deps) / len(deps)
            print(f"{ak.value:12s} {len(deps):>4d} {avg:>8.2f} {max(deps):>8.2f}")

        # --------------------------------------------------------------
        hr("RELATIONSHIPS")
        # --------------------------------------------------------------
        all_rels = list(s.scalars(select(Relationship)))
        kind_counts: Counter[str] = Counter(r.kind for r in all_rels)
        print(f"Relazioni totali: {len(all_rels)}")
        print("\nDistribuzione per kind:")
        for kind, count in kind_counts.most_common():
            print(f"  {kind:20s}: {count}")

        # Boredom
        social_kinds = ("FRIEND_OF", "BEST_FRIEND_OF", "PARTNER_OF", "SPOUSE_OF")
        social_rels = [r for r in all_rels if r.kind in social_kinds and r.from_id < r.to_id]
        if social_rels:
            boredom_vals = [BoredomService.get_boredom(r) for r in social_rels]
            conn_vals = [ConnectionService.get(r) for r in social_rels]
            print(f"\nRelazioni sociali (univoche): {len(social_rels)}")
            print(f"  boredom avg: {sum(boredom_vals) / len(boredom_vals):.3f}")
            print(f"  boredom max: {max(boredom_vals):.3f}")
            print(f"  connection avg: {sum(conn_vals) / len(conn_vals):.3f}")
            print(f"  connection max: {max(conn_vals):.3f}")

        # --------------------------------------------------------------
        hr("REFLECTIONS + CRISIS")
        # --------------------------------------------------------------
        total_refl = s.scalar(select(func.count()).select_from(ReflectionEntry)) or 0
        print(f"Reflection entries totali: {total_refl}")
        if alive:
            print(f"  media per NPC: {total_refl / len(alive):.1f}")

        by_refl_kind: Counter[str] = Counter(e.kind for e in s.scalars(select(ReflectionEntry)))
        print("\nDistribuzione per kind:")
        for kind, count in by_refl_kind.most_common():
            print(f"  {kind:14s}: {count}")

        # Crisi attive
        active_crisis = 0
        crisis_history = 0
        for c in alive:
            status = CrisisService.get_status(c)
            if status.active:
                active_crisis += 1
            if status.started_at is not None:
                crisis_history += 1
        print(f"\nCrisis attive: {active_crisis}")
        print(f"Character con storia di crisi: {crisis_history}")

        # --------------------------------------------------------------
        hr("ECONOMY")
        # --------------------------------------------------------------
        balances = [int(c.athel_balance) for c in alive]
        if balances:
            print("Bilancio Athel (vivi):")
            print(f"  min: {min(balances)}")
            print(f"  mediana: {int(median(balances))}")
            print(f"  media: {sum(balances) / len(balances):.1f}")
            print(f"  max: {max(balances)}")
            print(f"  totale: {sum(balances)}")

        # Jobs
        from simai.economy.jobs import JobService

        active_jobs = JobService.all_active_jobs(s)
        promoted = 0
        for j in active_jobs:
            if j.promoted_title and j.title == j.promoted_title:
                promoted += 1
        print(f"\nJobs attivi: {len(active_jobs)}")
        print(f"  Promozioni: {promoted}")

        # --------------------------------------------------------------
        hr(f"TOP {args.top} NPC")
        # --------------------------------------------------------------
        # Best skill + best value + balance
        rows: list[tuple[int, str, int, str, int, float]] = []
        for c in alive:
            skills_c = list(s.scalars(select(Skill).where(Skill.character_id == c.id)))
            best_skill = max(skills_c, key=lambda x: x.level) if skills_c else None
            best_lvl = best_skill.level if best_skill else 0
            best_skill_name = best_skill.skill_type if best_skill else "—"

            values_c = PersonalityService.get_values(c)
            max_value = max(values_c.values()) if values_c else 0.5
            balance = int(c.athel_balance)

            rows.append((c.id, c.full_name, best_lvl, best_skill_name, balance, max_value))

        rows.sort(key=lambda r: -r[2])
        print(f"{'ID':>4s} {'Nome':30s} {'BestSkill':14s} {'Lvl':>3s} {'Athel':>8s} {'MaxVal':>6s}")
        for cid, name, lvl, skill, bal, maxv in rows[: args.top]:
            print(f"{cid:>4d} {name[:30]:30s} {skill:14s} {lvl:>3d} {bal:>8d} {maxv:>6.3f}")


if __name__ == "__main__":
    main()
