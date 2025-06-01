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

class DrinkWaterAction(BaseAction):
    """Azione per l'NPC di bere acqua e soddisfare la sete."""
    def __init__(self, npc: 'Character',
                 simulation_context: 'Simulation',
                 action_type_override: Optional[ActionType] = None):

        super().__init__(
            npc=npc,
            action_type=action_type_override or ActionType.ACTION_DRINK_WATER,
            duration_ticks=settings.DRINK_WATER_DURATION_TICKS,
            simulation_context=simulation_context,
            is_interruptible=True
        )

    def is_valid(self) -> bool:
        """
        Verifica se l'azione è valida. Per ora è sempre valida.
        TODO: In futuro, verificare la presenza di una fonte d'acqua
              (rubinetto, frigorifero, fontana) nella locazione attuale.
        """
        return True

    def on_finish(self):
        """Chiamato al completamento. Soddisfa il bisogno di sete."""
        thirst_gain = settings.DRINK_WATER_THIRST_GAIN
        self.npc.change_need_value(NeedType.THIRST, thirst_gain)
        if settings.DEBUG_MODE:
            print(f"  [DrinkWaterAction] '{self.npc.name}' ha bevuto. Sete +{thirst_gain:.1f}.")