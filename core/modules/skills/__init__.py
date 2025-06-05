# core/modules/skills/__init__.py
"""
Package per la gestione delle abilità (skills) degli NPC.
"""
from settings import DEBUG_MODE
from .base_skill import BaseSkill

# Import dalle sottocartelle di categoria
from .mental.logic_skill import LogicSkill
from .practical.cooking_skill import CookingSkill
from .children.motor_child_skill import MotorChildSkill
# ... Aggiungere import per ogni altra classe skill specifica man mano che vengono create

# Esempi di altre skill che potresti importare:
# from .physical.fitness_skill import FitnessSkill
# from .social.charisma_skill import CharismaSkill
# from .creative.painting_skill import PaintingSkill
# from .toddlers.movement_toddler_skill import MovementToddlerSkill

__all__ = [
    'BaseSkill',
    'LogicSkill',
    'CookingSkill',
    'MotorChildSkill',
    # 'FitnessSkill',
    # 'CharismaSkill',
    # 'PaintingSkill',
    # 'MovementToddlerSkill',
    # ... e i nomi delle altre classi Skill
]

if DEBUG_MODE: print("  [Skills Package] Package 'core.modules.skills' caricato.")