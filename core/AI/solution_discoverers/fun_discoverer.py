# core/AI/solution_discoverers/fun_discoverer.py
from typing import List, Optional, TYPE_CHECKING

from core.enums.action_types import ActionType
from core.enums.skill_types import SkillType

from .base_discoverer import BaseSolutionDiscoverer
from core.enums import FunActivityType, LocationType, TraitType, Interest
from core.modules.actions import HaveFunAction, TravelToAction
from core.config import actions_config, time_config
from core import settings

if TYPE_CHECKING:
    from core.modules.memory.memory_definitions import Problem
    from core.character import Character
    from core.simulation import Simulation
    from core.modules.actions.action_base import BaseAction
    from core.world.location import Location

class FunSolutionDiscoverer(BaseSolutionDiscoverer):
    """Scopre tutte le possibili attività di divertimento, sia locali che remote."""

    def discover(self, problem: 'Problem', npc: 'Character', simulation_context: 'Simulation') -> List['BaseAction']:
        valid_actions: List['BaseAction'] = []

        # --- 1. SCOPERTA NELLA LOCAZIONE ATTUALE ---
        # L'IA controlla tutte le attività di divertimento possibili nella stanza in cui si trova.
        for activity_type in FunActivityType:
            action_instance = self._create_fun_action(npc, simulation_context, problem, activity_type)
            if action_instance.is_valid():
                valid_actions.append(action_instance)

        # --- 2. SCOPERTA IN ALTRE LOCAZIONI (VIAGGIO) ---
        # Se il bisogno di FUN è ancora il problema principale e l'NPC ha interessi specifici,
        # l'IA "pensa" a luoghi interessanti da visitare per divertirsi.
        
        # Esempio: Un NPC con interesse per l'arte e la cultura considera di andare al museo.
        if npc.has_trait(TraitType.ART_LOVER) or Interest.VISUAL_ARTS in npc.get_interests():
            self._discover_remote_location(
                npc, simulation_context, problem, valid_actions,
                LocationType.MUSEUM, FunActivityType.VISIT_MUSEUM
            )

        # Esempio: Un NPC con il tratto (ipotetico) CAFE_LOVER considera di andare al bar.
        if npc.has_trait(TraitType.CAFE_LOVER):
            self._discover_remote_location(
                npc, simulation_context, problem, valid_actions,
                LocationType.CAFE, FunActivityType.DRINK_COFFEE
            )
            
        if npc.has_trait(TraitType.MUSIC_LOVER) or npc.skill_manager.get_skill_level(SkillType.PIANO) > 0:
            # Se è un musicista, potrebbe voler esibirsi. Altrimenti, ascoltare.
            if npc.skill_manager.get_skill_level(SkillType.PIANO) > 4: # Soglia per esibirsi
                activity_to_perform = FunActivityType.PERFORM_JAZZ
            else:
                activity_to_perform = FunActivityType.LISTEN_TO_LIVE_JAZZ
            
            self._discover_remote_location(
                npc, simulation_context, problem, valid_actions,
                LocationType.JAZZ_CLUB, activity_to_perform
            )

        skill_level = npc.skill_manager.get_skill_level(SkillType.GUITAR)
        if skill_level > 2: # Deve avere un minimo di abilità per esibirsi
            
            # Cerca un luogo adatto, come un parco o una piazza
            for loc_id, location in simulation_context.locations.items():
                if location.location_type in {LocationType.PARK, LocationType.PUBLIC_PLAZA}: # Aggiungi PUBLIC_PLAZA all'enum
                    
                    activity_to_perform = FunActivityType.PERFORM_ON_STREET
                    
                    # Passiamo la skill giusta all'azione da creare
                    fun_action_config = {"skill_to_practice": SkillType.GUITAR}
                    
                    follow_up_action = self._create_fun_action(
                        npc, simulation_context, problem, 
                        activity_to_perform,
                        # Passa una configurazione parziale per sovrascrivere il default
                        partial_config=fun_action_config 
                    )

                    travel_action = TravelToAction(
                        npc=npc, simulation_context=simulation_context,
                        destination_location_id=loc_id,
                        follow_up_action=follow_up_action
                    )
                    if travel_action.is_valid():
                        valid_actions.append(travel_action)
                    return valid_actions # Trovata una soluzione, esci

        return valid_actions

    def _create_fun_action(self, npc: 'Character', sim: 'Simulation', problem: 'Problem', activity: FunActivityType) -> 'HaveFunAction':
        """Metodo helper per creare un'istanza di HaveFunAction con la configurazione corretta."""
        config = actions_config.HAVEFUN_ACTIVITY_CONFIGS.get(activity, {})
        duration = config.get("duration_hours", actions_config.HAVEFUN_DEFAULT_DURATION_HOURS)
        
        return HaveFunAction(
            npc=npc,
            simulation_context=sim,
            activity_type=activity,
            duration_ticks=int(duration * time_config.IXH),
            fun_gain=config.get("fun_gain", actions_config.HAVEFUN_DEFAULT_FUN_GAIN),
            required_object_types=config.get("required_object_types"),
            skill_to_practice=config.get("skill_to_practice"),
            skill_xp_gain=config.get("skill_xp_gain", 0.0),
            cognitive_effort=config.get("cognitive_effort", actions_config.HAVEFUN_DEFAULT_COGNITIVE_EFFORT),
            triggering_problem=problem
        )
    
    def _discover_remote_location(self, npc, sim, problem, valid_actions, loc_type, activity_type):
        """Metodo helper per cercare una locazione e creare l'azione di viaggio."""
        # Controlla se abbiamo già un piano per andare in un luogo di questo tipo
        for action in valid_actions:
            if isinstance(action, TravelToAction) and \
            isinstance(action.follow_up_action, HaveFunAction) and \
            action.follow_up_action.activity_type == activity_type:
                return # Abbiamo già un piano per questa attività, non ne creiamo un altro

        for loc_id, location in sim.locations.items():
            if location.location_type == loc_type:
                follow_up_action = self._create_fun_action(npc, sim, problem, activity_type)
                travel_action = TravelToAction(
                    npc=npc, simulation_context=sim,
                    destination_location_id=loc_id,
                    follow_up_action=follow_up_action
                )
                if travel_action.is_valid():
                    valid_actions.append(travel_action)
                return # Trovato un luogo, non ne cerchiamo altri per ora