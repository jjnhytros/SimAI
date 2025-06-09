# core/AI/solution_discoverers/hunger_discoverer.py
from typing import List, Optional, TYPE_CHECKING

from core.enums.action_types import ActionType

from .base_discoverer import BaseSolutionDiscoverer
from core.enums import ObjectType
from core.modules.actions.hunger_actions import EatAction
from core.modules.actions.travel_actions import TravelToAction
from core.config import actions_config, time_config

if TYPE_CHECKING:
    from core.modules.memory.memory_definitions import Problem
    from core.character import Character
    from core.simulation import Simulation
    from core.modules.actions.action_base import BaseAction
    from core.world.location import Location

class HungerSolutionDiscoverer(BaseSolutionDiscoverer):
    """Scopre tutte le possibili soluzioni per soddisfare il bisogno di HUNGER."""

    def discover(self, problem: 'Problem', npc: 'Character', simulation_context: 'Simulation') -> List['BaseAction']:
        valid_actions: List['BaseAction'] = []
        
        # 1. Cerca un frigorifero nella locazione attuale
        current_loc: Optional['Location'] = None
        if npc.current_location_id:
            current_loc = simulation_context.get_location_by_id(npc.current_location_id)
        if current_loc:
            for obj in current_loc.get_objects():
                if obj.object_type == ObjectType.REFRIGERATOR and obj.is_available():
                    # Trovato! Crea un'azione per mangiare qui e ora.
                    eat_action = self._create_eat_action(npc, simulation_context, problem)
                    eat_action.target_object = obj # Assegna l'oggetto trovato
                    if eat_action.is_valid():
                        valid_actions.append(eat_action)
                        # Trovata la soluzione migliore (nella stessa stanza), non ne cerchiamo altre
                        return valid_actions 

        # 2. Se non c'è un frigo qui, cercalo in altre locazioni
        for loc_id, location in simulation_context.locations.items():
            if loc_id == npc.current_location_id: continue

            for obj in location.get_objects():
                if obj.object_type == ObjectType.REFRIGERATOR:
                    # Trovato un frigo in un'altra stanza! Pianifica un viaggio.
                    follow_up_action = self._create_eat_action(npc, simulation_context, problem)
                    travel_action = TravelToAction(
                        npc=npc,
                        simulation_context=simulation_context,
                        destination_location_id=loc_id,
                        follow_up_action=follow_up_action
                    )
                    if travel_action.is_valid():
                        valid_actions.append(travel_action)
                    # Trovata una soluzione di viaggio, interrompi la ricerca
                    return valid_actions
        
        return valid_actions

    def _create_eat_action(self, npc: 'Character', sim: 'Simulation', problem: 'Problem') -> 'EatAction':
        """Metodo helper per creare un'istanza di EatAction con la configurazione corretta."""
        duration = getattr(actions_config, 'EAT_ACTION_DEFAULT_DURATION_HOURS', 0.5)
        hunger_gain = getattr(actions_config, 'EAT_ACTION_DEFAULT_HUNGER_GAIN', 70.0)
        
        return EatAction(
            npc=npc,
            simulation_context=sim,
            duration_ticks=int(duration * time_config.IXH),
            hunger_gain=hunger_gain,
            triggering_problem=problem
        )