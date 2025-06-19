# core/modules/skills/skill_system.py
"""
Definisce la classe SkillManager, il gestore di tutte le abilità di un NPC.
"""
from typing import Dict, TYPE_CHECKING
from core.config import skills_config
from core.enums import SkillType
from core import settings

# Importa la TUA classe BaseSkill dal suo file corretto
from .base_skill import BaseSkill

if TYPE_CHECKING:
    from core.character import Character

class SkillManager:
    """Gestisce tutte le abilità di un singolo NPC."""
    
    def __init__(self, owner_npc: 'Character'):
        self.owner_npc: 'Character' = owner_npc
        self.skills: Dict[SkillType, BaseSkill] = {}

    def get_skill(self, skill_type: SkillType) -> BaseSkill:
        """Restituisce un'abilità, creandola se non esiste."""
        if skill_type not in self.skills:
            # Crea una nuova abilità al livello 1 con 0 XP
            self.skills[skill_type] = BaseSkill(self.owner_npc, skill_type)
            if settings.DEBUG_MODE:
                print(f"    [SkillManager - {self.owner_npc.name}] Apprende una nuova abilità: {skill_type.name}")
        return self.skills[skill_type]

    def get_skill_level(self, skill_type: SkillType) -> int:
        """Restituisce il livello di un'abilità, o 0 se non conosciuta."""
        if skill_type in self.skills:
            return self.skills[skill_type].level
        return 0

    def add_experience(self, skill_type: SkillType, xp_amount: float):
        if xp_amount <= 0: return
        
        skill = self.get_skill(skill_type)
        if skill.level >= skill.max_level: return # Non si guadagna più XP al livello massimo

        skill.xp += xp_amount
        self._check_for_level_up(skill)

    def _check_for_level_up(self, skill: BaseSkill):
        current_level = skill.level
        if current_level >= skill.max_level: return

        # Controlla il prossimo livello
        next_level = current_level + 1
        xp_needed = skills_config.XP_PER_LEVEL.get(next_level)

        # Continua a salire di livello finché l'XP è sufficiente
        while xp_needed is not None and skill.xp >= xp_needed:
            skill.level = next_level
            if settings.DEBUG_MODE:
                print(f"    [SkillManager - {self.owner_npc.name}] LEVEL UP! {skill.skill_type.name} è ora a livello {skill.level}!")
            
            current_level = skill.level
            if current_level >= skill.max_level: break
            
            next_level = current_level + 1
            xp_needed = skills_config.XP_PER_LEVEL.get(next_level)
