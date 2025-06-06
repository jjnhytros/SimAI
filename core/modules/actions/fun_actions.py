# core/modules/actions/fun_actions.py
from typing import Dict, Optional, TYPE_CHECKING, Set as TypingSet, Tuple

if TYPE_CHECKING:
    from core.character import Character
    from core.simulation import Simulation
    from core.world.game_object import GameObject
    from core.world.location import Location

# Import corretti
from core.enums import NeedType, FunActivityType, ActionType, ObjectType, SkillType
from core.config import npc_config, actions_config # Assumiamo actions_config
from core import settings
from .action_base import BaseAction

# Questo set può essere spostato in actions_config.py per centralizzazione
# e usato da AIDecisionMaker per scegliere un'attività se non trova oggetti.
ACTIVITIES_WITHOUT_OBJECTS: TypingSet[FunActivityType] = {
    FunActivityType.DANCE, FunActivityType.DAYDREAM, FunActivityType.JOG_IN_PLACE,
    FunActivityType.SING, FunActivityType.PRACTICE_PUBLIC_SPEAKING,
    FunActivityType.SOCIAL_MEDIA_Browse, FunActivityType.WATCH_CLOUDS,
    FunActivityType.MEDITATE,
}

class HaveFunAction(BaseAction):
    """Azione per l'NPC di divertirsi con una specifica attività."""
    
    def __init__(self, 
                 npc: 'Character', 
                 simulation_context: 'Simulation',
                 # --- Parametri di configurazione ora iniettati ---
                 activity_type: FunActivityType,
                 duration_ticks: int,
                 fun_gain: float,
                 # Parametri opzionali per attività avanzate
                 required_object_types: Optional[Tuple[ObjectType, ...]] = None,
                 skill_to_practice: Optional[SkillType] = None,
                 skill_xp_gain: float = 0.0
                ):
        
        self.activity_type: FunActivityType = activity_type
        self.fun_gain: float = fun_gain
        self.skill_to_practice: Optional[SkillType] = skill_to_practice
        self.skill_xp_gain: float = skill_xp_gain
        self.required_object_types: Optional[Tuple[ObjectType, ...]] = required_object_types
        self.target_object: Optional['GameObject'] = None

        action_type_enum_val = ActionType.ACTION_HAVE_FUN
        action_name_str = f"ACTION_HAVE_FUN_{self.activity_type.name}"

        super().__init__(
            npc=npc,
            action_type_name=action_name_str, 
            action_type_enum=action_type_enum_to_use,
            duration_ticks=duration_ticks,
            p_simulation_context=simulation_context, 
            is_interruptible=True
        )
        
        self.effects_on_needs: Dict[NeedType, float] = {
            NeedType.FUN: self.fun_gain
        }
        
        if settings.DEBUG_MODE:
            skill_info = f", Skill: {self.skill_to_practice.name} +{self.skill_xp_gain}xp" if self.skill_to_practice else ""
            print(f"    [{self.action_type_name} INIT - {self.npc.name}] Creata per '{activity_type.name}'. "
                f"Durata: {self.duration_ticks}t, Gain FUN: {self.fun_gain:.1f}{skill_info}")

    def is_valid(self) -> bool:
        if not super().is_valid(): return False
        
        current_fun = self.npc.get_need_value(NeedType.FUN)
        if current_fun is not None and current_fun >= (settings.NEED_MAX_VALUE - 5.0):
            if settings.DEBUG_MODE: 
                print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] FUN ({current_fun:.1f}) già troppo alto.")
            return False

        if not self.required_object_types: # Se non richiede oggetti
            if settings.DEBUG_MODE: 
                print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Attività '{self.activity_type.name}' non richiede oggetto. Azione valida.")
            return True

        if not self.sim_context or not self.npc.current_location_id: return False
        current_location: Optional['Location'] = self.sim_context.get_location_by_id(self.npc.current_location_id)
        if not current_location: return False

        for game_obj in current_location.get_objects():
            if game_obj.object_type in self.required_object_types:
                # TODO: Controllare se l'oggetto è utilizzabile (non rotto, non occupato)
                self.target_object = game_obj # Memorizza l'oggetto target
                if settings.DEBUG_MODE:
                    print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Trovato oggetto '{game_obj.name}' per '{self.activity_type.name}'. Azione valida.")
                return True
        
        if settings.DEBUG_MODE:
            print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Nessun oggetto disponibile trovato per '{self.activity_type.name}' in {current_location.name}.")
        return False

    def on_finish(self):
        if self.npc:
            if settings.DEBUG_MODE:
                print(f"    [{self.action_type_name} FINISH - {self.npc.name}] Finito di: {self.activity_type.name}. Applico effetti.")
            
            self.npc.change_need_value(NeedType.FUN, self.fun_gain, is_decay_event=False)
            
            if self.skill_to_practice and self.skill_xp_gain > 0:
                # TODO: Integrare con il sistema di skill dell'NPC
                # Esempio: self.npc.skills_manager.add_experience(self.skill_to_practice, self.skill_xp_gain)
                if settings.DEBUG_MODE:
                    print(f"        -> Guadagno Skill: {self.skill_xp_gain:.1f} XP in {self.skill_to_practice.name}")
        
        super().on_finish()