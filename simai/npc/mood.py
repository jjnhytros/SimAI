"""Moodlets e stato d'umore di un Character."""

from __future__ import annotations

from dataclasses import dataclass, field

from simai.npc.needs.enums import NeedState, NeedType
from simai.npc.needs.needs import Needs

# ---------------------------------------------------------------------------
# Moodlet
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Moodlet:
    """Un modificatore temporaneo dell'umore."""

    name: str
    remaining_ticks: int
    happiness_delta: float  # contributo per tick al target happiness
    source: str = ""  # es. "hunger_critical", "slept_well"

    def __post_init__(self) -> None:
        if self.remaining_ticks < 0:
            raise ValueError(f"remaining_ticks deve essere >= 0, ricevuto {self.remaining_ticks}")
        if not (-1.0 <= self.happiness_delta <= 1.0):
            raise ValueError(
                f"happiness_delta deve essere in [-1, 1], ricevuto {self.happiness_delta}"
            )

    def ticked(self) -> Moodlet | None:
        """Ritorna il moodlet dopo un tick, o ``None`` se scaduto."""
        if self.remaining_ticks <= 1:
            return None
        return Moodlet(
            name=self.name,
            remaining_ticks=self.remaining_ticks - 1,
            happiness_delta=self.happiness_delta,
            source=self.source,
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "remaining_ticks": self.remaining_ticks,
            "happiness_delta": self.happiness_delta,
            "source": self.source,
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> Moodlet:
        from simai.utils import coerce_float, coerce_int, coerce_str

        return cls(
            name=coerce_str(data["name"], name="moodlet.name"),
            remaining_ticks=coerce_int(data["remaining_ticks"], name="moodlet.remaining_ticks"),
            happiness_delta=coerce_float(data["happiness_delta"], name="moodlet.happiness_delta"),
            source=coerce_str(data.get("source", ""), name="moodlet.source"),
        )


# ---------------------------------------------------------------------------
# MoodletRegistry — regole che generano moodlets da bisogni
# ---------------------------------------------------------------------------

#: Durata (tick) dei moodlet automatici generati da bisogni.
_NEED_MOODLET_DURATION: int = 30

#: Mappa: (need, state) -> (nome moodlet, delta happiness)
_NEED_MOODLET_MAP: dict[tuple[NeedType, NeedState], tuple[str, float]] = {
    (NeedType.HUNGER, NeedState.CRITICAL): ("Affamato", -0.35),
    (NeedType.HUNGER, NeedState.LOW): ("Fame", -0.15),
    (NeedType.HUNGER, NeedState.HIGH): ("Sazio", 0.10),
    (NeedType.THIRST, NeedState.CRITICAL): ("Disidratato", -0.40),
    (NeedType.THIRST, NeedState.LOW): ("Sete", -0.15),
    (NeedType.THIRST, NeedState.HIGH): ("Idratato", 0.05),
    (NeedType.BLADDER, NeedState.CRITICAL): ("Bisogno impellente", -0.30),
    (NeedType.BLADDER, NeedState.LOW): ("Vescica piena", -0.10),
    (NeedType.ENERGY, NeedState.CRITICAL): ("Esausto", -0.35),
    (NeedType.ENERGY, NeedState.LOW): ("Stanco", -0.15),
    (NeedType.ENERGY, NeedState.HIGH): ("Riposato", 0.15),
    (NeedType.HYGIENE, NeedState.CRITICAL): ("Sudicio", -0.25),
    (NeedType.HYGIENE, NeedState.LOW): ("Poco pulito", -0.10),
    (NeedType.SOCIAL, NeedState.CRITICAL): ("Isolato", -0.30),
    (NeedType.SOCIAL, NeedState.LOW): ("Solo", -0.15),
    (NeedType.SOCIAL, NeedState.HIGH): ("Accompagnato", 0.10),
    (NeedType.FUN, NeedState.CRITICAL): ("Depresso", -0.25),
    (NeedType.FUN, NeedState.LOW): ("Annoiato", -0.10),
    (NeedType.FUN, NeedState.HIGH): ("Divertito", 0.10),
    (NeedType.COMFORT, NeedState.CRITICAL): ("A disagio", -0.20),
    (NeedType.COMFORT, NeedState.LOW): ("Scomodo", -0.08),
    (NeedType.COMFORT, NeedState.HIGH): ("A proprio agio", 0.08),
}


def moodlet_for_need(need: NeedType, state: NeedState) -> Moodlet | None:
    """Ritorna un moodlet per la coppia (need, state), o ``None``."""
    entry = _NEED_MOODLET_MAP.get((need, state))
    if entry is None:
        return None
    name, delta = entry
    return Moodlet(
        name=name,
        remaining_ticks=_NEED_MOODLET_DURATION,
        happiness_delta=delta,
        source=f"{need.value}_{state.value.lower()}",
    )


# ---------------------------------------------------------------------------
# MoodState
# ---------------------------------------------------------------------------

#: Peso dei bisogni sulla felicità di base (somma = 1.0).
_BASE_HAPPINESS_WEIGHTS: dict[NeedType, float] = {
    NeedType.HUNGER: 0.15,
    NeedType.THIRST: 0.15,
    NeedType.BLADDER: 0.10,
    NeedType.ENERGY: 0.20,
    NeedType.HYGIENE: 0.10,
    NeedType.SOCIAL: 0.10,
    NeedType.FUN: 0.10,
    NeedType.COMFORT: 0.10,
}

#: Velocità di avvicinamento al target (0..1 per tick).
_HAPPINESS_SMOOTHING: float = 0.02


@dataclass(frozen=True, slots=True)
class MoodState:
    """Stato d'umore di un Character.

    `happiness` in [0, 1] è smoothed verso un target calcolato da:
      - media pesata dei bisogni
      - somma dei `happiness_delta` dei moodlet attivi
    """

    happiness: float = 0.5
    moodlets: tuple[Moodlet, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not (0.0 <= self.happiness <= 1.0):
            raise ValueError(f"happiness deve essere in [0, 1], ricevuto {self.happiness}")

    # ------------------------------------------------------------------
    # Derivazione
    # ------------------------------------------------------------------

    @staticmethod
    def target_from(needs: Needs, moodlets: tuple[Moodlet, ...]) -> float:
        """Calcola il target di felicità da bisogni + moodlets."""
        # Base: media pesata dei bisogni (0..1)
        base = 0.0
        for need, weight in _BASE_HAPPINESS_WEIGHTS.items():
            base += weight * (needs.get(need) / 100.0)
        # Moodlets: somma dei delta
        moodlet_delta = sum(m.happiness_delta for m in moodlets)
        target = base + moodlet_delta
        return max(0.0, min(1.0, target))

    # ------------------------------------------------------------------
    # Tick
    # ------------------------------------------------------------------

    def tick(
        self,
        needs: Needs,
        new_moodlets: tuple[Moodlet, ...] = (),
    ) -> MoodState:
        """Avanza di un tick: aggiorna moodlets, calcola target, applica smoothing."""
        # 1. Combina moodlet esistenti (decrementati) + nuovi (sovrascrittura per nome)
        existing: dict[str, Moodlet] = {}
        for m in self.moodlets:
            ticked = m.ticked()
            if ticked is not None:
                existing[m.name] = ticked
        for m in new_moodlets:
            existing[m.name] = m

        merged = tuple(existing.values())

        # 2. Target
        target = MoodState.target_from(needs, merged)

        # 3. Smoothing esponenziale
        new_happiness = self.happiness + (target - self.happiness) * _HAPPINESS_SMOOTHING
        new_happiness = max(0.0, min(1.0, new_happiness))

        return MoodState(happiness=new_happiness, moodlets=merged)

    # ------------------------------------------------------------------
    # Serializzazione
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, object]:
        return {
            "happiness": self.happiness,
            "moodlets": [m.to_dict() for m in self.moodlets],
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> MoodState:
        raw_moodlets = data.get("moodlets", [])
        moodlets: list[Moodlet] = []
        if isinstance(raw_moodlets, list):
            for item in raw_moodlets:
                if isinstance(item, dict):
                    moodlets.append(Moodlet.from_dict(item))
        return cls(
            happiness=float(data.get("happiness", 0.5)),  # type: ignore[arg-type]
            moodlets=tuple(moodlets),
        )

    @classmethod
    def default(cls) -> MoodState:
        return cls(happiness=0.5, moodlets=())


__all__ = ["MoodState", "Moodlet", "moodlet_for_need"]
