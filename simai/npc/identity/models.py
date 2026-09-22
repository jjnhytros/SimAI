"""Modelli del dominio identità (JSON-serializzabili)."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any

from simai.npc.identity.enums import CulturalTradition, TabooReaction


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


# ---------------------------------------------------------------------------
# Sexuality
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Sexuality:
    """Orientamento sessuale su 4 dimensioni continue in [0, 1].

    - attraction_to_male, attraction_to_female, attraction_to_nonbinary:
      livello di attrazione verso ciascun genere.
    - romantic_vs_sexual: 0 = solo romantico, 1 = solo sessuale.
    """

    attraction_to_male: float = 0.5
    attraction_to_female: float = 0.5
    attraction_to_nonbinary: float = 0.5
    romantic_vs_sexual: float = 0.5

    def __post_init__(self) -> None:
        for name in (
            "attraction_to_male",
            "attraction_to_female",
            "attraction_to_nonbinary",
            "romantic_vs_sexual",
        ):
            v = getattr(self, name)
            if not (0.0 <= v <= 1.0):
                raise ValueError(f"{name} deve essere in [0, 1], ricevuto {v}")

    def label(self) -> str:
        """Etichetta descrittiva (per CLI/debug)."""
        m = self.attraction_to_male
        f = self.attraction_to_female
        if m < 0.3 and f < 0.3:
            return "asexual"
        if m > 0.7 and f < 0.3:
            return "androphilic"
        if f > 0.7 and m < 0.3:
            return "gynephilic"
        if m > 0.5 and f > 0.5:
            return "bisexual"
        return "fluid"

    def with_drift(self, jitter: dict[str, float]) -> Sexuality:
        """Ritorna una nuova `Sexuality` con jitter applicato (clampato)."""
        return replace(
            self,
            attraction_to_male=_clamp(self.attraction_to_male + jitter.get("male", 0.0), 0.0, 1.0),
            attraction_to_female=_clamp(
                self.attraction_to_female + jitter.get("female", 0.0), 0.0, 1.0
            ),
            attraction_to_nonbinary=_clamp(
                self.attraction_to_nonbinary + jitter.get("nonbinary", 0.0),
                0.0,
                1.0,
            ),
            romantic_vs_sexual=_clamp(
                self.romantic_vs_sexual + jitter.get("romantic_vs_sexual", 0.0),
                0.0,
                1.0,
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "attraction_to_male": self.attraction_to_male,
            "attraction_to_female": self.attraction_to_female,
            "attraction_to_nonbinary": self.attraction_to_nonbinary,
            "romantic_vs_sexual": self.romantic_vs_sexual,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Sexuality:
        if not data:
            return cls()
        return cls(
            attraction_to_male=float(data.get("attraction_to_male", 0.5)),
            attraction_to_female=float(data.get("attraction_to_female", 0.5)),
            attraction_to_nonbinary=float(data.get("attraction_to_nonbinary", 0.5)),
            romantic_vs_sexual=float(data.get("romantic_vs_sexual", 0.5)),
        )


# ---------------------------------------------------------------------------
# SEP
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class SEP:
    """Sexual Education Profile.

    - knowledge: [0, 100] conoscenza sessuale.
    - comfort: [0, 1] comfort con l'intimità.
    - inhibition: [0, 1] inibizioni apprese.
    - received_at_age: età in anni Anthalys di ricezione educazione (o None).
    """

    knowledge: float = 0.0
    comfort: float = 0.5
    inhibition: float = 0.5
    received_at_age: int | None = None

    def __post_init__(self) -> None:
        if not (0.0 <= self.knowledge <= 100.0):
            raise ValueError(f"knowledge deve essere in [0, 100], ricevuto {self.knowledge}")
        if not (0.0 <= self.comfort <= 1.0):
            raise ValueError(f"comfort deve essere in [0, 1], ricevuto {self.comfort}")
        if not (0.0 <= self.inhibition <= 1.0):
            raise ValueError(f"inhibition deve essere in [0, 1], ricevuto {self.inhibition}")
        if self.received_at_age is not None and self.received_at_age < 0:
            raise ValueError(f"received_at_age deve essere >= 0, ricevuto {self.received_at_age}")

    def with_knowledge_delta(self, delta: float) -> SEP:
        return replace(
            self,
            knowledge=_clamp(self.knowledge + delta, 0.0, 100.0),
        )

    def with_comfort_delta(self, delta: float) -> SEP:
        return replace(self, comfort=_clamp(self.comfort + delta, 0.0, 1.0))

    def with_inhibition_delta(self, delta: float) -> SEP:
        return replace(self, inhibition=_clamp(self.inhibition + delta, 0.0, 1.0))

    def to_dict(self) -> dict[str, Any]:
        return {
            "knowledge": self.knowledge,
            "comfort": self.comfort,
            "inhibition": self.inhibition,
            "received_at_age": self.received_at_age,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SEP:
        if not data:
            return cls()
        received = data.get("received_at_age")
        return cls(
            knowledge=float(data.get("knowledge", 0.0)),
            comfort=float(data.get("comfort", 0.5)),
            inhibition=float(data.get("inhibition", 0.5)),
            received_at_age=int(received) if received is not None else None,
        )


# ---------------------------------------------------------------------------
# CulturalProfile
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class CulturalProfile:
    """Profilo culturale appreso."""

    permissiveness: float = 0.5
    modesty: float = 0.5
    gender_role_strict: float = 0.5
    reaction_to_taboo: TabooReaction = TabooReaction.MODERATE
    tradition: CulturalTradition = CulturalTradition.ANTHAL_CORE

    def __post_init__(self) -> None:
        for name in ("permissiveness", "modesty", "gender_role_strict"):
            v = getattr(self, name)
            if not (0.0 <= v <= 1.0):
                raise ValueError(f"{name} deve essere in [0, 1], ricevuto {v}")

    def to_dict(self) -> dict[str, Any]:
        return {
            "permissiveness": self.permissiveness,
            "modesty": self.modesty,
            "gender_role_strict": self.gender_role_strict,
            "reaction_to_taboo": self.reaction_to_taboo.value,
            "tradition": self.tradition.value,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CulturalProfile:
        if not data:
            return cls()
        taboo_raw = str(data.get("reaction_to_taboo", "MODERATE"))
        trad_raw = str(data.get("tradition", "ANTHAL_CORE"))
        try:
            taboo = TabooReaction(taboo_raw)
        except ValueError:
            taboo = TabooReaction.MODERATE
        try:
            tradition = CulturalTradition(trad_raw)
        except ValueError:
            tradition = CulturalTradition.ANTHAL_CORE
        return cls(
            permissiveness=float(data.get("permissiveness", 0.5)),
            modesty=float(data.get("modesty", 0.5)),
            gender_role_strict=float(data.get("gender_role_strict", 0.5)),
            reaction_to_taboo=taboo,
            tradition=tradition,
        )


# ---------------------------------------------------------------------------
# Container
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class IdentityProfile:
    """Bundle dei tre profili (sexuality + SEP + cultura)."""

    sexuality: Sexuality = field(default_factory=Sexuality)
    sep: SEP = field(default_factory=SEP)
    culture: CulturalProfile = field(default_factory=CulturalProfile)

    def to_dict(self) -> dict[str, Any]:
        return {
            "sexuality": self.sexuality.to_dict(),
            "sep": self.sep.to_dict(),
            "cultural_profile": self.culture.to_dict(),
        }


__all__ = ["SEP", "CulturalProfile", "IdentityProfile", "Sexuality"]
