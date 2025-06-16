# core/modules/actions/crafting_actions.py
import random
from typing import TYPE_CHECKING
import uuid

from core.enums.need_types import NeedType
from core.enums.object_types import ObjectType
from .action_base import BaseAction
from core.enums import ActionType, SkillType, ItemQuality
from core import settings
from .hunger_actions import EatAction # Importa EatAction
from core.config import actions_config, time_config

if TYPE_CHECKING:
    from core.character import Character
    from core.simulation import Simulation
    from core.world.game_object import GameObject

class CookAction(BaseAction):
    """
    Azione per cucinare un pasto. L'esito è un oggetto 'cibo' e l'accodamento
    di una EatAction per consumarlo.
    """
    def __init__(self, npc, simulation_context, **kwargs):
        config = actions_config.SIMPLE_NEED_ACTION_CONFIGS.get(NeedType.HUNGER, {})
        duration = int(config.get("duration_hours", 0.75) * time_config.TXH_SIMULATION)
        super().__init__(npc, simulation_context, duration_ticks=duration, action_type_enum=ActionType.ACTION_COOK, **kwargs)

    def on_finish(self):
        super().on_finish()
        if not self.npc: return

        # 1. Calcola la qualità in base alla skill COOKING e alla "Regola del 12"
        skill_level = self.npc.skill_manager.get_skill_level(SkillType.COOKING)
        
        # Pesi per la probabilità: [Scadente, Normale, Buono, Eccellente, Capolavoro]
        # La somma di ogni lista è 120 (multiplo di 12)
        
        if skill_level < 5: # Livelli 1-4: Principiante
            # Alta probabilità di pasti Normali, bassa di Scadenti o Buoni
            weights = [24, 84, 12, 0, 0]
        elif skill_level < 9: # Livelli 5-8: Cuoco Competente
            # Ora produce principalmente pasti Buoni, con chance di Eccellenti
            weights = [6, 36, 60, 18, 0]
        elif skill_level < 12: # Livelli 9-11: Chef Esperto
            # Produce principalmente pasti Eccellenti, con una chance di Capolavoro
            weights = [0, 12, 48, 48, 12]
        else: # Livello 12+: Maestro Chef
            # Non produce più pasti Buoni, solo Eccellenti o Capolavori
            weights = [0, 0, 0, 84, 36]
        
        food_quality = random.choices(list(ItemQuality), weights=weights, k=1)[0]

        # 2. Crea il nuovo oggetto "Pasto" virtuale (logica invariata)
        food_object = GameObject(
            object_id=f"food_{uuid.uuid4().hex[:6]}",
            name=f"Pasto ({food_quality.name})",
            object_type=ObjectType.FOOD,
            quality=food_quality
        )
        if settings.DEBUG_MODE:
            print(f"    [CookAction] {self.npc.name} (Cooking Lvl {skill_level}) ha cucinato un pasto di qualità: {food_quality.name}")
        
        # 3. Prepara e accoda l'azione di mangiare (logica invariata)
        eat_config = {"duration_hours": 0.25, "hunger_gain": 75.0}
        eat_action = EatAction(
            npc=self.npc,
            simulation_context=self.sim_context,
            target_object=food_object,
            duration_ticks=int(eat_config["duration_hours"] * time_config.TXH_SIMULATION),
            hunger_gain=eat_config["hunger_gain"]
        )
        self.npc.add_action_to_queue(eat_action)
