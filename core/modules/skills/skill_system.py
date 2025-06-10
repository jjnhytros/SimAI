# core/modules/skills/skill_system.py
"""
Definisce la classe SkillManager, il gestore di tutte le abilità di un NPC.
"""
from typing import Dict, TYPE_CHECKING
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
        """
        Restituisce l'oggetto Skill per un dato tipo.
        Se l'NPC non ha ancora quella skill, la crea usando il costruttore corretto.
        """
        if skill_type not in self.skills:
            if settings.DEBUG_MODE:
                print(f"    [SkillManager - {self.owner_npc.name}] Apprende una nuova abilità: {skill_type.name}")
            
            # Crea un'istanza di BaseSkill (o una sua sottoclasse)
            # passando i parametri richiesti dal tuo __init__: character_owner e skill_type.
            # In futuro, qui potrai decidere di creare istanze di classi specifiche
            # (es. CharismaSkill, ProgrammingSkill) invece di BaseSkill generica.
            self.skills[skill_type] = BaseSkill(
                character_owner=self.owner_npc,
                skill_type=skill_type
            )
        return self.skills[skill_type]

    def add_experience(self, skill_type: SkillType, xp_amount: float):
        """Aggiunge esperienza a una specifica abilità."""
        if xp_amount <= 0:
            return
        # Ottiene (o crea) la skill e poi chiama il suo metodo .add_experience
        skill_obj = self.get_skill(skill_type)
        skill_obj.add_experience(xp_amount)

    def get_skill_level(self, skill_type: SkillType) -> int:
        """Restituisce il livello di una skill, o 0 se non ancora appresa."""
        if skill_type in self.skills:
            return self.skills[skill_type].level
        # La tua BaseSkill inizia a livello 0, quindi potremmo voler restituire quello
        return 0