# core/modules/actions/thirst_actions.py
"""
Azioni relative al bisogno di Sete (Thirst).
"""
from typing import TYPE_CHECKING, Optional

from core import settings
from core.enums import NeedType, ActionType
from .action_base import BaseAction

if TYPE_CHECKING:
    from core.character import Character
    from core.simulation import Simulation
    from core.world.location import Location

class DrinkWaterAction(BaseAction):
    """Azione per l'NPC di bere acqua e soddisfare la sete."""
    def __init__(self, npc: 'Character',
                 simulation_context: 'Simulation',
                 action_type_override: Optional[ActionType] = None):

        # Determina l'enum corretto da usare
        chosen_action_type_enum = action_type_override or ActionType.ACTION_DRINK_WATER

        super().__init__(
            npc=npc,
            action_type_name=chosen_action_type_enum.action_type_name,
            action_type_enum=chosen_action_type_enum,
            duration_ticks=settings.DRINK_WATER_DURATION_TICKS,
            p_simulation_context=simulation_context,
            is_interruptible=True
        )

    def is_valid(self) -> bool:
        """
        Verifica se l'azione è valida, controllando la presenza di una
        fonte d'acqua nella locazione attuale dell'NPC.
        """
        if not self.simulation_context:
            return False

        current_location: Optional['Location'] = self.npc.get_current_location(self.simulation_context)

        if not current_location:
            if settings.DEBUG_MODE:
                print(f"  [DrinkWaterAction] Azione non valida per '{self.npc.name}': nessuna locazione attuale.")
            return False

        for game_object in current_location.get_objects(): # Ripristinato .get_objects() basato sul file Location
            if game_object.is_water_source:
                if settings.DEBUG_MODE:
                    print(f"  [DrinkWaterAction] Trovata fonte d'acqua '{game_object.name}' per '{self.npc.name}' in '{current_location.name}'. Azione valida.")
                return True

        if settings.DEBUG_MODE:
            print(f"  [DrinkWaterAction] Azione non valida per '{self.npc.name}': nessuna fonte d'acqua in '{current_location.name}'.")

        return False

    def on_finish(self):
        """Chiamato al completamento. Soddisfa il bisogno di sete."""
        thirst_gain = settings.DRINK_WATER_THIRST_GAIN
        self.npc.change_need_value(NeedType.THIRST, thirst_gain)
        if settings.DEBUG_MODE:
            print(f"  [DrinkWaterAction] '{self.npc.name}' ha bevuto. Sete +{thirst_gain:.1f}.")
