# core/modules/actions/travel_actions.py
from typing import Optional, TYPE_CHECKING
from .action_base import BaseAction
from core.enums import ActionType
from core.config import actions_config # Importa la configurazione

if TYPE_CHECKING:
    from core.character import Character
    from core.simulation import Simulation

class TravelToAction(BaseAction):
    """Azione per spostare un NPC tra due diverse locazioni."""

    def __init__(self, 
                npc: 'Character', 
                simulation_context: 'Simulation',
                destination_location_id: str,
                follow_up_action: Optional[BaseAction] = None,
                **kwargs
                ):
        
        # Ora la durata del viaggio è letta dalla configurazione
        duration = actions_config.TRAVEL_ACTION_DEFAULT_DURATION_TICKS

        super().__init__(
            npc=npc,
            p_simulation_context=simulation_context,
            duration_ticks=duration,
            action_type_enum=ActionType.ACTION_TRAVEL_TO,
            **kwargs
        )
        self.destination_location_id = destination_location_id
        self.follow_up_action = follow_up_action
        
    def is_valid(self) -> bool:
        if not super().is_valid(): return False
        # Il viaggio è valido se la destinazione esiste
        return self.sim_context.get_location_by_id(self.destination_location_id) is not None

    def on_finish(self):
        # Prima chiama super() per applicare eventuali effetti base
        super().on_finish()
        
        # Azione principale: cambia la locazione dell'NPC
        self.npc.set_location(self.destination_location_id, self.sim_context)
        
        # Se c'è un'azione da compiere all'arrivo, la accoda
        if self.follow_up_action:
            self.npc.add_action_to_queue(self.follow_up_action)
