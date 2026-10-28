from simai.world.enums import LifeStage

# Soglie: l'inizio di ogni fascia. `age_years` confrontato con
# `< soglia_successiva`. Confine all'anno, `age_days` ignorato.
LIFESTAGE_THRESHOLDS: tuple[int, ...] = (0, 6, 12, 15, 20, 25, 40, 50, 60)

_PEDIATRIC_STAGES: frozenset[LifeStage] = frozenset(
    {
        LifeStage.EARLY_CHILDHOOD,
        LifeStage.CHILDHOOD,
        LifeStage.EARLY_ADOLESCENCE,
        LifeStage.LATE_ADOLESCENCE,
    }
)


def life_stage_for(age_years: int) -> LifeStage:
    """Fascia di età Anthalys.

    Confine all'anno: `age_years < 6` → EARLY_CHILDHOOD, ecc.
    `age_days` ignorato. `age_years` negativo viene clampato a 0
    (EARLY_CHILDHOOD).
    """
    years = max(0, age_years)
    if years < 6:
        return LifeStage.EARLY_CHILDHOOD
    if years < 12:
        return LifeStage.CHILDHOOD
    if years < 15:
        return LifeStage.EARLY_ADOLESCENCE
    if years < 20:
        return LifeStage.LATE_ADOLESCENCE
    if years < 25:
        return LifeStage.YOUNG_ADULT
    if years < 40:
        return LifeStage.EARLY_ADULTHOOD
    if years < 50:
        return LifeStage.MIDDLE_ADULTHOOD
    if years < 60:
        return LifeStage.LATE_ADULTHOOD
    return LifeStage.SENIORITY


def is_pediatric(stage: LifeStage) -> bool:
    """True per 0–20 anni (prima infanzia, infanzia, adolescenza)."""
    return stage in _PEDIATRIC_STAGES


def is_psychosocial(stage: LifeStage) -> bool:
    """True per 20+ anni (dalla giovinezza in poi)."""
    return stage not in _PEDIATRIC_STAGES
