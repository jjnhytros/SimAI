# core/modules/needs/__init__.py
"""
Package per la gestione dei singoli oggetti Bisogno (Need).
"""
from core.settings import DEBUG_MODE
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
    ThirstNeed,
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
    'ThirstNeed',
    'IntimacyNeed',
    'LearningNeed',
    'SafetyNeed',
    'SocialNeed',
    'SpiritualityNeed',
    # ...
]

if DEBUG_MODE: print("  [Needs Package] Package 'core.modules.needs' caricato (con bisogni specifici).")