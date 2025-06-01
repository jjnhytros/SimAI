# core/modules/needs/__init__.py
"""
Package per la gestione dei singoli oggetti Bisogno (Need).
"""
from .need_base import BaseNeed
from .common_needs import (
    AchievementNeed,
    AutonomyNeed,
    BladderNeed,
    ComfortNeed,
    CreativityNeed,
    EnergyNeed,
    EnvironmentNeed,
    FunNeed,
    HungerNeed, 
    HygieneNeed,
    IntimacyNeed,
    LearningNeed,
    SafetyNeed,
    SocialNeed,
    SpiritualityNeed,
)

__all__ = [
    'AchievementNeed',
    'AutonomyNeed',
    'BaseNeed',
    'BladderNeed',
    'ComfortNeed',
    'CreativityNeed',
    'EnergyNeed',
    'EnvironmentNeed',
    'FunNeed',
    'HungerNeed', 
    'HygieneNeed',
    'IntimacyNeed',
    'LearningNeed',
    'SafetyNeed',
    'SocialNeed',
    'SpiritualityNeed',
    # ...
]

print("  [Needs Package] Package 'core.modules.needs' caricato (con bisogni specifici).")