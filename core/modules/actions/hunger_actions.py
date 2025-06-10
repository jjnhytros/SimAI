# core/modules/actions/hunger_actions.py
from typing import Optional, TYPE_CHECKING, Dict

from core.enums import ActionType, NeedType, ObjectType
from core.enums.item_quality import ItemQuality
from core.enums.moodlet_types import MoodletType
from core.modules.moodlets.moodlet_definitions import Moodlet
from .action_base import BaseAction
from core import settings
from core.config import npc_config

if TYPE_CHECKING:
    from core.character import Character
    from core.simulation import Simulation
    from core.world.game_object import GameObject
    from core.world.location import Location
    from core.modules.memory.memory_definitions import Problem

class EatAction(BaseAction):
    """Azione per l'NPC di mangiare, con gestione dell'oggetto sorgente di cibo."""

    def __init__(self, 
                npc: 'Character', 
                simulation_context: 'Simulation', 
                duration_ticks: int, 
                hunger_gain: float,
                triggering_problem: Optional['Problem'] = None):
        
        super().__init__(
            npc=npc,
            p_simulation_context=simulation_context,
            duration_ticks=duration_ticks,
            action_type_enum=ActionType.ACTION_EAT,
            triggering_problem=triggering_problem
        )
        self.hunger_gain = hunger_gain
        self.effects_on_needs = {NeedType.HUNGER: self.hunger_gain}

    def is_valid(self) -> bool:
        if not super().is_valid(): return False
        
        hunger_need = self.npc.needs.get(NeedType.HUNGER)
        if hunger_need and hunger_need.get_value() >= (npc_config.NEED_MAX_VALUE - 5.0):
            return False

        if not self.target_object:
            if not self.sim_context or not self.npc.current_location_id: return False
            current_loc: Optional['Location'] = self.sim_context.get_location_by_id(self.npc.current_location_id)
            if not current_loc: return False

            food_source = None
            for obj in current_loc.get_objects():
                if obj.object_type == ObjectType.REFRIGERATOR and obj.is_available():
                    food_source = obj
                    break
            
            if food_source:
                self.target_object = food_source
            else:
                return False
        
        return self.target_object.is_available()

    def on_start(self):
        super().on_start()
        if self.target_object:
            self.target_object.set_in_use(self.npc.npc_id)

    def on_finish(self):
        if self.npc and self.target_object:
            # Modificatore di default
            quality_modifier = 1.0 
            food_quality = getattr(self.target_object, 'quality', ItemQuality.NORMAL)

            if food_quality == ItemQuality.POOR: quality_modifier = 0.7
            elif food_quality == ItemQuality.GOOD: quality_modifier = 1.1
            elif food_quality == ItemQuality.EXCELLENT: quality_modifier = 1.3
            elif food_quality == ItemQuality.MASTERPIECE: quality_modifier = 1.6

            # Applica il guadagno di fame modificato dalla qualità
            final_hunger_gain = self.hunger_gain * quality_modifier
            self.npc.change_need_value(NeedType.HUNGER, final_hunger_gain)
            
            # Aggiungi un moodlet in base alla qualità
            if food_quality in {ItemQuality.EXCELLENT, ItemQuality.MASTERPIECE}:
                self.npc.moodlet_manager.add_moodlet(Moodlet(
                    moodlet_type=MoodletType.AMAZING_MEAL, # Da creare
                    display_name="Pasto Incredibile",
                    emotional_impact=+15, source_description="Quel piatto era un capolavoro!"
                ))
            
        if self.target_object:
            self.target_object.set_free()
        super().on_finish()

    def on_interrupt_effects(self):
        super().on_interrupt_effects()
        # Potremmo applicare effetti parziali qui se volessimo
        if self.target_object:
            self.target_object.set_free()