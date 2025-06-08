# core/enums/__init__.py
"""
Questo file rende la cartella 'enums' un package Python.
Viene utilizzato per importare ed esporre centralmente tutte le Enum
definite nei moduli specifici all'interno di questo package.
"""

# Importa le Enum dai loro moduli specifici
from .action_types import ActionType
from .aspiration_types import AspirationType
from .event_types import EventType
from .fun_activity_types import FunActivityType 
from .genders import Gender
from .interests import Interest
from .life_stages import LifeStage
from .location_types import LocationType
from .moodlet_types import MoodletType
from .need_types import NeedType
from .object_types import ObjectType
from .problem_types import ProblemType
from .relationship_statuses import RelationshipStatus 
from .relationship_types import RelationshipType
from .school_levels import SchoolLevel
from .skill_types import SkillType
from .social_interaction_types import SocialInteractionType
from .time_of_day import TimeOfDay
from .trait_types import TraitType
from .weather_types import WeatherType

__all__ = [
    'ActionType',
    'AspirationType',
    'EventType',
    'FunActivityType',
    'Gender',
    'Interest',
    'LifeStage',
    'LocationType',
    'MoodletType',
    'NeedType',
    'ObjectType',
    'ProblemType',
    'RelationshipStatus',
    'RelationshipType',
    'SchoolLevel',
    'SkillType',
    'SocialInteractionType',
    'TimeOfDay',
    'TraitType',
    'WeatherType',
]

