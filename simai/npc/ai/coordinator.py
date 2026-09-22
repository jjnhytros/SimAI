"""AICoordinator — orchestrazione per-NPC di bisogni + AI + mood + skills + addictions."""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from simai.npc.addictions.enums import AddictionKind
from simai.npc.ai.actions import Action
from simai.npc.ai.executor import ActionExecutor, ActionProgress, BTActionExecutor
from simai.npc.ai.utility import AIDecisionMaker
from simai.npc.mood import Moodlet, MoodState, moodlet_for_need
from simai.npc.needs.needs import Needs
from simai.npc.needs.processor import NeedsProcessor, NeedTransition
from simai.npc.personality.enums import ValueAxis
from simai.npc.skills.enums import XP_PER_TICK, SkillType
from simai.npc.skills.service import SkillService
from simai.npc.traits.enums import Trait


@dataclass(frozen=True, slots=True)
class TickResult:
    """Risultato di un tick AI su un Character."""

    needs: Needs
    mood: MoodState
    action_progress: ActionProgress | None
    needs_transitions: tuple[NeedTransition, ...]
    new_moodlets: tuple[Moodlet, ...]
    action_started: Action | None
    action_completed: Action | None
    skill_xp_delta: dict[SkillType, float] = field(default_factory=dict)
    addiction_use: dict[AddictionKind, float] = field(default_factory=dict)


@dataclass(slots=True)
class AICoordinator:
    """Coordina NeedsProcessor, AIDecisionMaker, ActionExecutor, MoodState.

    Se `bt_executor` è impostato, le azioni passano per il Behaviour Tree.
    Altrimenti, usa il `executor` "classico".

    Skill training:
      - se `skill_levels` è fornito a `tick()`, il coordinator filtra le azioni
        per `min_skill_level` e applica `utility_skill_boost`.
      - `TickResult.skill_xp_delta` contiene XP base (talent-agnostico) da
        applicare: il manager moltiplica per `talent` e applica.

    Addiction craving:
      - se `addiction_cravings` è fornito a `tick()`, il decision maker applica
        un boost di utility alle azioni che soddisfano il craving.
      - `TickResult.addiction_use` contiene le addiction "usate" nel tick
        (una entry per azione avviata con `addiction_kind`).
    """

    seed: int = 0
    need_processor: NeedsProcessor = field(default_factory=NeedsProcessor)
    decision_maker: AIDecisionMaker = field(default_factory=AIDecisionMaker)
    executor: ActionExecutor = field(default_factory=ActionExecutor)
    bt_executor: BTActionExecutor | None = None
    _rng: random.Random = field(
        init=False,
        repr=False,
        compare=False,
        default_factory=random.Random,
    )

    def __post_init__(self) -> None:
        self._rng = random.Random(self.seed)

    @property
    def uses_bt(self) -> bool:
        """``True`` se la modalità BT è attiva."""
        return self.bt_executor is not None

    @property
    def current_progress(self) -> ActionProgress | None:
        """Progress dell'esecutore attivo (BT o classico)."""
        if self.bt_executor is not None:
            return self.bt_executor.progress
        return self.executor.progress

    # ------------------------------------------------------------------
    # Tick
    # ------------------------------------------------------------------

    def tick(
        self,
        needs: Needs,
        mood: MoodState,
        traits: list[Trait] | None = None,
        skill_levels: dict[SkillType, int] | None = None,
        addiction_cravings: dict[AddictionKind, float] | None = None,
        values: dict[ValueAxis, float] | None = None,
        job_skill: SkillType | None = None,
    ) -> TickResult:
        """Esegue un tick completo."""
        levels = skill_levels if skill_levels is not None else {}
        cravings = addiction_cravings if addiction_cravings is not None else {}
        vals = values if values is not None else {}

        # 1. Decay bisogni
        new_needs, transitions = self.need_processor.tick(needs)

        # 2. Moodlets (invariato)
        new_moodlets: list[Moodlet] = []
        for t in transitions:
            m = moodlet_for_need(t.need, t.to_state)
            if m is not None:
                new_moodlets.append(m)

        # 3. Azione
        action_started: Action | None = None
        skill_xp_delta: dict[SkillType, float] = {}
        addiction_use: dict[AddictionKind, float] = {}

        if self.bt_executor is not None:
            action_before = self.bt_executor.action
            if self.bt_executor.is_busy:
                new_needs, _ = self.bt_executor.tick(new_needs)
                self._record_xp(action_before, levels, skill_xp_delta)
            else:
                chosen = self.decision_maker.decide(
                    new_needs, self._rng, traits, levels, cravings, vals, job_skill
                )
                if chosen is not None:
                    self.bt_executor.start(chosen, initial_needs=new_needs)
                    action_started = chosen
                    new_needs, _ = self.bt_executor.tick(new_needs)
                    self._record_xp(chosen, levels, skill_xp_delta)
                    self._record_addiction_use(chosen, addiction_use)
        else:
            action_before = (
                self.executor.progress.action if self.executor.progress is not None else None
            )
            if self.executor.is_busy:
                new_needs, _ = self.executor.tick(new_needs)
                self._record_xp(action_before, levels, skill_xp_delta)
            else:
                chosen = self.decision_maker.decide(
                    new_needs, self._rng, traits, levels, cravings, vals, job_skill
                )
                if chosen is not None:
                    self.executor.start(chosen)
                    action_started = chosen
                    new_needs, _ = self.executor.tick(new_needs)
                    self._record_xp(chosen, levels, skill_xp_delta)
                    self._record_addiction_use(chosen, addiction_use)

        # 4. Mood
        new_mood = mood.tick(new_needs, tuple(new_moodlets))

        return TickResult(
            needs=new_needs,
            mood=new_mood,
            action_progress=self.current_progress,
            needs_transitions=tuple(transitions),
            new_moodlets=tuple(new_moodlets),
            action_started=action_started,
            action_completed=None,
            skill_xp_delta=skill_xp_delta,
            addiction_use=addiction_use,
        )

    # ------------------------------------------------------------------
    # Skill helper
    # ------------------------------------------------------------------

    @staticmethod
    def _record_xp(
        action: Action | None,
        levels: dict[SkillType, int],
        out: dict[SkillType, float],
    ) -> None:
        """Accumula XP base (talent-agnostico) per l'azione data."""
        if action is None or action.trains_skill is None:
            return
        level = levels.get(action.trains_skill, 0)
        base_xp = XP_PER_TICK * SkillService.level_penalty(level)
        out[action.trains_skill] = out.get(action.trains_skill, 0.0) + base_xp

    # ------------------------------------------------------------------
    # Addiction helper
    # ------------------------------------------------------------------

    @staticmethod
    def _record_addiction_use(
        action: Action,
        out: dict[AddictionKind, float],
    ) -> None:
        """Registra l'uso di una sostanza quando l'azione viene AVVIATA.

        Nota: viene registrato 1 uso per azione (non 1 per tick). Il manager
        accumula in `pending_addiction_uses` e applica in batch al flush.
        """
        if action.addiction_kind is None:
            return
        out[action.addiction_kind] = 1.0

    # ------------------------------------------------------------------
    # Reset
    # ------------------------------------------------------------------

    def reset_rng(self, seed: int | None = None) -> None:
        if seed is not None:
            self.seed = seed
        self._rng = random.Random(self.seed)


__all__ = ["AICoordinator", "TickResult"]
