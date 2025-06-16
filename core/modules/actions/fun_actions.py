from typing import Dict, Optional, TYPE_CHECKING, Set as TypingSet, Tuple, cast

from core.enums.trait_types import TraitType
from core.modules.memory.memory_definitions import Problem
from core.enums import NeedType, ActionType, ObjectType, SkillType, FunActivityType
from core.config import npc_config, time_config, actions_config
from core import settings
from .action_base import BaseAction

if TYPE_CHECKING:
    from core.character import Character
    from core.simulation import Simulation
    from core.world.game_object import GameObject
    from core.world.location import Location

class HaveFunAction(BaseAction):
    """
    Azione per divertirsi. Il guadagno di FUN e XP è calcolato dinamicamente
    ad ogni tick in base a tratti e interessi.
    """
    def __init__(self, npc: 'Character', simulation_context: 'Simulation',
                 activity_type: FunActivityType, **kwargs):
        activity_type_safe = cast(FunActivityType, activity_type)
        config = actions_config.HAVEFUN_ACTIVITY_CONFIGS.get(activity_type_safe, {}) 
        duration = int(config.get("duration_hours", 1.0) * time_config.TXH_SIMULATION)

        super().__init__(
            npc=npc,
            p_simulation_context=simulation_context,
            duration_ticks=duration,
            action_type_name=f"ACTION_HAVE_FUN_{activity_type_safe.name}",
            action_type_enum=ActionType.ACTION_HAVE_FUN,
            **kwargs
        )
        
        self.activity_type = activity_type
        # Salviamo i valori di base dalla configurazione
        self.base_fun_gain_total = config.get("fun_gain", 0.0)
        self.base_skill_xp_gain_total = config.get("skill_xp_gain", 0.0)
        
        self.skill_to_practice = config.get("skill_to_practice")
        self.required_object_types = config.get("required_object_types")
        self.manages_need = NeedType.FUN

    def is_valid(self) -> bool:
        activity_type_safe = cast(FunActivityType, self.activity_type)
        if not super().is_valid() or not activity_type_safe: return False
        
        current_fun = self.npc.get_need_value(NeedType.FUN)
        if current_fun is not None and current_fun >= (npc_config.NEED_MAX_VALUE - 5.0):
            return False

        if self.activity_type in actions_config.ACTIVITIES_WITHOUT_OBJECTS:
            return True

        # La logica per trovare l'oggetto ora è nel Discoverer, qui basta controllare
        if not self.target_object or not self.target_object.is_available():
            return False

        return True

    def execute_tick(self):
        super().execute_tick()
        if not self.is_started or not self.is_finished: return
        activity_type_safe = cast(FunActivityType, self.activity_type)

        # --- NUOVA LOGICA DI GUADAGNO DINAMICO ---
        # 1. Calcola il guadagno di base per questo tick
        base_gain_per_tick = self.base_fun_gain_total / self.duration_ticks if self.duration_ticks > 0 else 0
        
        # 2. Applica i modificatori dei Tratti
        personality_modifier = 1.0
        # Esempio: Erika, che è PARTY_ANIMAL, si divertirà il doppio a ballare
        if self.activity_type == FunActivityType.DANCE and self.npc.has_trait(TraitType.PARTY_ANIMAL):
            personality_modifier = 2.0
        # Esempio: Max, che è LONER, si divertirebbe la metà a ballare
        elif self.activity_type == FunActivityType.DANCE and self.npc.has_trait(TraitType.LONER):
            personality_modifier = 0.5
        
        # 3. Applica i modificatori degli Interessi
        interest_modifier = 1.0
        related_interest = actions_config.ACTIVITY_TO_INTEREST_MAP.get(activity_type_safe)
        if related_interest and related_interest in self.npc.get_interests():
            interest_modifier = 1.5

        # 4. Calcola il guadagno finale per questo tick
        final_gain_this_tick = base_gain_per_tick * personality_modifier * interest_modifier
        
        # Applica il guadagno di FUN
        self.npc.change_need_value(NeedType.FUN, final_gain_this_tick)
        
        # Applica il guadagno di SKILL (anche questo può essere dinamico)
        base_xp_per_tick = self.base_skill_xp_gain_total / self.duration_ticks if self.duration_ticks > 0 else 0
        if self.skill_to_practice and base_xp_per_tick > 0:
            # Qui potremmo aggiungere un modificatore per i tratti (es. GENIUS impara più in fretta)
            self.npc.skill_manager.add_experience(self.skill_to_practice, base_xp_per_tick)

    def on_start(self):
        super().on_start()
        if self.target_object:
            self.target_object.set_in_use(self.npc.npc_id)
        # La stampa di debug in on_start può rimanere, ma non è più essenziale

    def on_finish(self):
        """Alla fine, applica solo effetti secondari (come il denaro) e libera l'oggetto."""
        # La chiamata a super() qui ora è pulita
        super().on_finish()
        
        # TODO: Logica per il guadagno economico (quando Character.money sarà implementato)
        # config = actions_config.HAVEFUN_ACTIVITY_CONFIGS.get(self.activity_type, {})
        # money_gain = config.get("money_gain", 0.0) ...
        
        if self.target_object:
            self.target_object.set_free()

    def on_interrupt_effects(self):
        """Quando interrotta, libera solo l'oggetto. I guadagni parziali sono già stati applicati."""
        if self.target_object:
            self.target_object.set_free()