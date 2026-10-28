import pytest

from simai.npc.lifestage import (
    LIFESTAGE_THRESHOLDS,
    is_pediatric,
    is_psychosocial,
    life_stage_for,
)
from simai.world.enums import LifeStage


@pytest.mark.parametrize(
    "years,expected",
    [
        (0, LifeStage.EARLY_CHILDHOOD),
        (5, LifeStage.EARLY_CHILDHOOD),
        (6, LifeStage.CHILDHOOD),
        (11, LifeStage.CHILDHOOD),
        (12, LifeStage.EARLY_ADOLESCENCE),
        (14, LifeStage.EARLY_ADOLESCENCE),
        (15, LifeStage.LATE_ADOLESCENCE),
        (19, LifeStage.LATE_ADOLESCENCE),
        (20, LifeStage.YOUNG_ADULT),
        (24, LifeStage.YOUNG_ADULT),
        (25, LifeStage.EARLY_ADULTHOOD),
        (39, LifeStage.EARLY_ADULTHOOD),
        (40, LifeStage.MIDDLE_ADULTHOOD),
        (49, LifeStage.MIDDLE_ADULTHOOD),
        (50, LifeStage.LATE_ADULTHOOD),
        (59, LifeStage.LATE_ADULTHOOD),
        (60, LifeStage.SENIORITY),
        (100, LifeStage.SENIORITY),
    ],
)
def test_life_stage_for_boundaries(years: int, expected: LifeStage) -> None:
    assert life_stage_for(years) == expected


def test_life_stage_for_negative_clamped() -> None:
    assert life_stage_for(-1) == LifeStage.EARLY_CHILDHOOD


def test_thresholds_match_enum_length() -> None:
    # 9 fasce, 9 soglie di inizio
    assert len(LIFESTAGE_THRESHOLDS) == len(LifeStage)


def test_is_pediatric() -> None:
    assert is_pediatric(LifeStage.EARLY_CHILDHOOD)
    assert is_pediatric(LifeStage.CHILDHOOD)
    assert is_pediatric(LifeStage.EARLY_ADOLESCENCE)
    assert is_pediatric(LifeStage.LATE_ADOLESCENCE)
    assert not is_pediatric(LifeStage.YOUNG_ADULT)
    assert not is_pediatric(LifeStage.SENIORITY)


def test_is_psychosocial() -> None:
    assert is_psychosocial(LifeStage.YOUNG_ADULT)
    assert is_psychosocial(LifeStage.EARLY_ADULTHOOD)
    assert is_psychosocial(LifeStage.SENIORITY)
    assert not is_psychosocial(LifeStage.LATE_ADOLESCENCE)
    assert not is_psychosocial(LifeStage.EARLY_CHILDHOOD)


def test_seed_characters_stages() -> None:
    """Con il seed 1.8.0: erika/max 14, giulia 37, luca 42, player 30."""
    assert life_stage_for(14) == LifeStage.EARLY_ADOLESCENCE
    assert life_stage_for(37) == LifeStage.EARLY_ADULTHOOD
    assert life_stage_for(42) == LifeStage.MIDDLE_ADULTHOOD
    assert life_stage_for(30) == LifeStage.EARLY_ADULTHOOD
