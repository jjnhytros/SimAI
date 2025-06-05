# core/modules/skills/base_skill.py
"""
Definizione della classe BaseSkill, la classe genitore per tutte le abilità specifiche.
"""
from typing import TYPE_CHECKING, List, Dict, Any
# Assumiamo che SkillType sia in core.enums.skill_types
# e settings in core.settings
from core.enums.skill_types import SkillType
from core import settings

if TYPE_CHECKING:
    from core.character import Character # Per type hinting

class BaseSkill:
    def __init__(self, character_owner: 'Character', skill_type: SkillType, initial_level: int = 0, initial_xp: float = 0.0):
        self.character_owner = character_owner
        self.skill_type = skill_type
        self._level = initial_level
        self._xp = initial_xp
        
        # Carica max_level e xp_per_level da settings
        self.max_level = settings.SKILL_MAX_LEVELS.get(self.skill_type, settings.DEFAULT_SKILL_MAX_LEVEL)
        self.xp_per_level = settings.SKILL_XP_PER_LEVEL.get(self.skill_type, settings.DEFAULT_SKILL_XP_SCHEDULE)

        # Applica bonus iniziali se presenti e se la skill parte da zero
        if self._level == 0 and self._xp == 0.0:
            initial_bonus = settings.SKILL_INITIAL_LEVEL_BONUS.get(self.skill_type)
            if initial_bonus:
                self._level = initial_bonus.get("level", 0)
                self._xp = initial_bonus.get("xp", 0.0)
                # Assicura che l'XP iniziale non superi il necessario per il livello iniziale bonus
                if self._level > 0 and self._level <= self.max_level:
                    xp_for_bonus_level = self.get_xp_for_level(self._level)
                    xp_for_next_from_bonus = self.get_xp_for_level(self._level + 1)
                    self._xp = min(self._xp, xp_for_next_from_bonus - 1 if xp_for_next_from_bonus > xp_for_bonus_level else xp_for_bonus_level)


    @property
    def level(self) -> int:
        return self._level

    @property
    def xp(self) -> float:
        return self._xp

    def add_experience(self, amount: float):
        if self._level >= self.max_level:
            # Se già al massimo livello, assicurati che l'XP sia al cap per quel livello
            if self.max_level > 0 and self.xp_per_level and len(self.xp_per_level) >= self.max_level:
                 self._xp = self.xp_per_level[self.max_level -1]
            return

        self._xp += amount
        
        # Loop per gestire avanzamenti di più livelli
        while self._level < self.max_level:
            xp_needed_for_next_level = self.get_xp_for_level(self._level + 1)
            if self._xp >= xp_needed_for_next_level:
                self._level += 1
                if settings.DEBUG_MODE:
                    print(f"  [SKILL UP! - {self.character_owner.name}] {self.skill_type.display_name_it()} è ora al livello {self._level}!")
                self.on_level_up(self._level)
            else:
                # XP non sufficienti per il prossimo livello, esci dal loop
                break
        
        # Se si raggiunge il livello massimo, normalizza l'XP al valore massimo per quel livello
        if self._level >= self.max_level:
            self._level = self.max_level # Assicura che non superi il massimo
            if self.max_level > 0 and self.xp_per_level and len(self.xp_per_level) >= self.max_level:
                self._xp = self.xp_per_level[self.max_level -1]
        # Altrimenti, se non al massimo livello, assicurati che l'xp non superi il necessario per il prossimo livello -1
        elif self._level < self.max_level :
             xp_for_next = self.get_xp_for_level(self._level + 1)
             self._xp = min(self._xp, xp_for_next - 0.01 if xp_for_next > 0 else 0) # -0.01 per evitare problemi di float esatto


    def get_xp_for_level(self, target_level: int) -> float:
        """Restituisce l'XP totale cumulativo necessario per raggiungere un dato livello."""
        if not (1 <= target_level <= self.max_level +1): # +1 per poter controllare il cap del livello max
             # Per il livello massimo, restituisci l'ultimo valore XP definito
            if target_level == self.max_level + 1 and self.max_level > 0 and self.xp_per_level and len(self.xp_per_level) >= self.max_level:
                return self.xp_per_level[self.max_level-1]
            return float('inf')
        
        if not self.xp_per_level or len(self.xp_per_level) < target_level:
            if settings.DEBUG_MODE:
                print(f"Attenzione: Programmazione XP per {self.skill_type.name} livello {target_level} non definita o incompleta.")
            return float('inf')
        return self.xp_per_level[target_level - 1] # L'array è 0-indexed

    def get_progress_to_next_level(self) -> float:
        """Restituisce la percentuale di progresso XP verso il prossimo livello (0.0 a 1.0)."""
        if self._level >= self.max_level:
            return 1.0
        
        xp_for_current_level_start = self.get_xp_for_level(self.level) if self.level > 0 else 0.0
        xp_for_next_level_target = self.get_xp_for_level(self.level + 1)
        
        total_xp_for_this_level_span = xp_for_next_level_target - xp_for_current_level_start
        if total_xp_for_this_level_span <= 0: # Evita divisione per zero o progresso negativo
            return 1.0 if self._xp >= xp_for_next_level_target else 0.0

        current_xp_in_this_level_span = self._xp - xp_for_current_level_start
        progress = current_xp_in_this_level_span / total_xp_for_this_level_span
        return max(0.0, min(1.0, progress))

    def on_level_up(self, new_level: int):
        """Chiamato quando la skill sale di livello."""
        pass # Le sottoclassi possono sovrascriverlo

    def get_level_benefits(self) -> Dict[int, List[str]]:
        """Restituisce benefici per livello. Da sovrascrivere nelle sottoclassi."""
        return {}

    def __str__(self):
        return f"{self.skill_type.display_name_it()}: Liv {self.level}/{self.max_level} (XP: {self.xp:.0f})"