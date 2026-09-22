"""ActionExecutor — esegue un'azione tick per tick, applicando effetti."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from simai.npc.ai.actions import Action
from simai.npc.ai.bt import Blackboard, BTNode, BTStatus
from simai.npc.ai.bt_templates import build_bt_for_action
from simai.npc.needs.enums import NeedType
from simai.npc.needs.needs import Needs


@dataclass(frozen=True, slots=True)
class ActionProgress:
    """Stato dell'azione in corso."""

    action: Action
    elapsed_ticks: int

    @property
    def remaining_ticks(self) -> int:
        return self.action.duration_ticks - self.elapsed_ticks

    @property
    def progress(self) -> float:
        """Frazione [0, 1] di completamento."""
        return self.elapsed_ticks / self.action.duration_ticks

    def to_dict(self) -> dict[str, object]:
        return {
            "action": self.action.to_dict(),
            "elapsed_ticks": self.elapsed_ticks,
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> ActionProgress:
        from simai.utils import coerce_int

        raw_action = data["action"]
        if not isinstance(raw_action, dict):
            raise ValueError(f"action: atteso dict, ricevuto {type(raw_action).__name__}")
        return cls(
            action=Action.from_dict(raw_action),
            elapsed_ticks=coerce_int(data["elapsed_ticks"], name="elapsed_ticks"),
        )


class ActionExecutor:
    """Esegue azioni applicando i loro effetti distribuiti sulla durata.

    Uso:
        ex = ActionExecutor()
        ex.start(ACTION_CATALOG[0])
        new_needs = ex.tick(needs)  # applica un tick di effetto
        if ex.is_done: ...
    """

    def __init__(self) -> None:
        self._progress: ActionProgress | None = None

    @property
    def progress(self) -> ActionProgress | None:
        return self._progress

    @property
    def is_busy(self) -> bool:
        return self._progress is not None

    @property
    def is_done(self) -> bool:
        return (
            self._progress is not None
            and self._progress.elapsed_ticks >= self._progress.action.duration_ticks
        )

    # ------------------------------------------------------------------
    # Controllo
    # ------------------------------------------------------------------

    def start(self, action: Action) -> None:
        """Inizia l'esecuzione di `action`. Sovrascrive eventuale azione in corso."""
        self._progress = ActionProgress(action=action, elapsed_ticks=0)

    def cancel(self) -> ActionProgress | None:
        """Annulla l'azione in corso. Ritorna l'azione interrotta (o None)."""
        old = self._progress
        self._progress = None
        return old

    def restore(self, progress: ActionProgress | None) -> None:
        """Ripristina lo stato dell'esecutore da un `ActionProgress`.

        Usato al load da DB per riprendere un'azione interrotta.
        """
        self._progress = progress

    # ------------------------------------------------------------------
    # Tick
    # ------------------------------------------------------------------

    def tick(self, needs: Needs) -> tuple[Needs, bool]:
        """Applica un tick di azione. Ritorna `(nuovo_needs, completata)`.

        Se nessuna azione in corso, ritorna `(needs, False)`.
        """
        if self._progress is None:
            return needs, False

        action = self._progress.action
        new_needs = needs
        for need in NeedType:
            delta = action.effect_per_tick(need)
            if delta != 0.0:
                new_needs = new_needs.with_delta(need, delta)

        new_elapsed = self._progress.elapsed_ticks + 1
        self._progress = ActionProgress(action=action, elapsed_ticks=new_elapsed)

        if new_elapsed >= action.duration_ticks:
            self._progress = None
            return new_needs, True
        return new_needs, False


__all__ = ["ActionExecutor", "ActionProgress"]


class BTActionExecutor:
    """Esegue un'azione tramite Behaviour Tree. Resumable tra tick.

    Differenze rispetto a `ActionExecutor`:
      - L'azione è rappresentata da un albero BT, non solo da effetti.
      - Supporta azioni composte (multi-step).
      - Traccia `elapsed_ticks` per compatibilità con `ActionProgress`.
    """

    def __init__(
        self,
        builder: Callable[[Action], BTNode] = build_bt_for_action,
    ) -> None:
        self._builder = builder
        self._action: Action | None = None
        self._tree: BTNode | None = None
        self._bb: Blackboard = Blackboard()
        self._elapsed: int = 0

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def is_busy(self) -> bool:
        return self._tree is not None

    @property
    def action(self) -> Action | None:
        return self._action

    @property
    def progress(self) -> ActionProgress | None:
        if self._action is None:
            return None
        return ActionProgress(action=self._action, elapsed_ticks=self._elapsed)

    # ------------------------------------------------------------------
    # Controllo
    # ------------------------------------------------------------------

    def start(self, action: Action, *, initial_needs: Needs) -> None:
        """Inizia l'esecuzione. `initial_needs` è lo stato di partenza (sul BB)."""
        self._action = action
        self._tree = self._builder(action)
        self._elapsed = 0
        self._bb.clear()
        self._bb.set("needs", initial_needs)

    def cancel(self) -> Action | None:
        """Annulla l'azione in corso. Ritorna l'azione interrotta o `None`."""
        old = self._action
        self._tree = None
        self._action = None
        self._bb.clear()
        self._elapsed = 0
        return old

    # ------------------------------------------------------------------
    # Tick
    # ------------------------------------------------------------------

    def tick(self, needs: Needs) -> tuple[Needs, bool]:
        """Esegue un tick del BT. Ritorna `(new_needs, completed)`.

        `completed` è True se il BT ha raggiunto SUCCESS o FAILURE.
        """
        if self._tree is None:
            return needs, False

        self._bb.set("needs", needs)
        self._elapsed += 1
        status = self._tree.tick(self._bb)
        new_needs = self._bb.get("needs", needs)
        if not isinstance(new_needs, Needs):
            new_needs = needs

        if status is BTStatus.SUCCESS:
            self._tree = None
            self._action = None
            self._bb.clear()
            return new_needs, True
        if status is BTStatus.FAILURE:
            # Fallimento: consideriamo l'azione chiusa (senza effetti finali)
            self._tree = None
            self._action = None
            self._bb.clear()
            return needs, True
        return new_needs, False
