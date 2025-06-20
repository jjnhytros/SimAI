# core/modules/skills/base_skill.py
from typing import TYPE_CHECKING, Dict, List
from core import settings
from core.enums import SkillType, Gender
from core.config import skills_config

if TYPE_CHECKING:
    from core.character import Character

class BaseSkill:
    def __init__(self, character_owner: 'Character', skill_type: SkillType,
                initial_level: int = 1, initial_xp: float = 0.0):
        self.character_owner: 'Character' = character_owner
        self.skill_type: SkillType = skill_type
        
        self.max_level = skills_config.SKILL_SPECIFIC_MAX_LEVELS.get(self.skill_type, skills_config.DEFAULT_SKILL_MAX_LEVEL)
        self.xp_per_level_map = skills_config.XP_PER_LEVEL
        
        self._level: int = initial_level
        self._xp: float = initial_xp
        
        self.max_level: int = skills_config.SKILL_SPECIFIC_MAX_LEVELS.get(
            skill_type, skills_config.DEFAULT_SKILL_MAX_LEVEL
        )

    @property
    def level(self) -> int:
        return self._level

    @level.setter
    def level(self, value: int):
        """Setter: Imposta un nuovo livello, con controlli."""
        self._level = max(1, min(self.max_level, value))

    @property
    def xp(self) -> float:
        """Getter: Restituisce l'XP corrente."""
        return self._xp

    @xp.setter
    def xp(self, value: float):
        """Setter: Imposta un nuovo valore di XP."""
        # L'XP non può essere negativo
        self._xp = max(0, value)

    def add_experience(self, amount: float):
        if self._level >= self.max_level:
            return

        self._xp += amount
        
        while self._level < self.max_level:
            xp_needed_for_next_level = self.get_xp_for_level(self._level + 1)
            if self._xp >= xp_needed_for_next_level:
                self._level_up()
            else:
                break
        
        # Assicura che l'XP non superi il cap del livello massimo
        if self._level >= self.max_level:
            max_xp = self.get_xp_for_level(self.max_level + 1) # Ottiene l'ultimo valore definito
            self._xp = max_xp

    def _level_up(self):
        """Gestisce l'aumento di livello."""
        self._level += 1
        if settings.DEBUG_MODE:
            print(f"  [SKILL UP! - {self.character_owner.name}] {self.skill_type.display_name_it(self.character_owner.gender)} è ora al livello {self._level}!")
        self.on_level_up(self._level)

    def get_xp_for_level(self, target_level: int) -> float:
        """Restituisce l'XP totale cumulativo necessario per raggiungere un dato livello."""
        if not (1 <= target_level <= self.max_level + 1):
            return float('inf')
        
        # Se il livello richiesto è oltre il massimo, restituiamo l'ultimo valore di XP definito come cap
        if target_level > self.max_level:
            return self.xp_per_level_map.get(self.max_level, float('inf'))

        return self.xp_per_level_map.get(target_level, float('inf'))

    def get_progress_to_next_level(self) -> float:
        """Restituisce la percentuale di progresso XP verso il prossimo livello (0.0 a 1.0)."""
        if self._level >= self.max_level:
            return 1.0
        
        xp_for_current_level_start = self.get_xp_for_level(self.level)
        xp_for_next_level_target = self.get_xp_for_level(self.level + 1)
        
        total_xp_for_this_level_span = xp_for_next_level_target - xp_for_current_level_start
        if total_xp_for_this_level_span <= 0:
            return 1.0 if self._xp >= xp_for_next_level_target else 0.0

        current_xp_in_this_level_span = self._xp - xp_for_current_level_start
        progress = current_xp_in_this_level_span / total_xp_for_this_level_span
        return max(0.0, min(1.0, progress))

    def on_level_up(self, new_level: int):
        """Chiamato quando la skill sale di livello. Le sottoclassi possono sovrascriverlo."""
        pass

    def get_level_benefits(self) -> Dict[int, List[str]]:
        """Restituisce benefici per livello. Da sovrascrivere nelle sottoclassi."""
        return {}

    def get_display_name(self, gender: Gender) -> str:
        """Restituisce il nome leggibile dell'abilità."""
        return self.skill_type.display_name_it(gender)

    def __str__(self) -> str:
        display_name = self.get_display_name(self.character_owner.gender)
        return f"{display_name}: Liv {self.level}/{self.max_level} (XP: {self.xp:.0f})"
