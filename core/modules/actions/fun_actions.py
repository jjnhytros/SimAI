# core/modules/actions/fun_actions.py
from typing import Dict, Optional, TYPE_CHECKING, Set as TypingSet, Tuple

if TYPE_CHECKING:
    from core.character import Character
    from core.simulation import Simulation
    from core.world.game_object import GameObject
    from core.world.location import Location

from core.enums import NeedType, FunActivityType, ActionType, ObjectType, SkillType
from core.config import time_config, actions_config, npc_config
from core import settings
from .action_base import BaseAction

ACTIVITIES_WITHOUT_OBJECTS: TypingSet[FunActivityType] = {
    FunActivityType.DANCE, FunActivityType.DAYDREAM, FunActivityType.JOG_IN_PLACE,
    FunActivityType.SING, FunActivityType.PRACTICE_PUBLIC_SPEAKING,
    FunActivityType.BROWSE_SOCIAL_MEDIA, FunActivityType.WATCH_CLOUDS,
    FunActivityType.MEDITATE, FunActivityType.PEOPLE_WATCH, FunActivityType.EXPLORE_NEIGHBORHOOD,
}

class HaveFunAction(BaseAction):
    """Azione per l'NPC di divertirsi con una specifica attività pre-configurata."""
    
    def __init__(self, 
                 npc: 'Character', 
                 simulation_context: 'Simulation',
                 activity_type: FunActivityType,
                 duration_ticks: int,
                 fun_gain: float,
                 required_object_types: Optional[Tuple[ObjectType, ...]] = None,
                 skill_to_practice: Optional[SkillType] = None,
                 skill_xp_gain: float = 0.0
                ):
        
        self.activity_type: FunActivityType = activity_type
        self.fun_gain: float = fun_gain
        self.skill_to_practice: Optional[SkillType] = skill_to_practice
        self.skill_xp_gain: float = skill_xp_gain
        self.required_object_types: Optional[Tuple[ObjectType, ...]] = required_object_types
        # self.target_object è inizializzato a None in BaseAction

        action_type_enum_val = ActionType.ACTION_HAVE_FUN
        action_name_str = f"ACTION_HAVE_FUN_{self.activity_type.name}"

        super().__init__(
            npc=npc,
            action_type_name=action_name_str, 
            action_type_enum=action_type_enum_val,
            duration_ticks=duration_ticks,
            p_simulation_context=simulation_context, 
            is_interruptible=True
        )
        
        self.effects_on_needs: Dict[NeedType, float] = {
            NeedType.FUN: self.fun_gain
        }
        
        if settings.DEBUG_MODE:
            skill_info = f", Skill: {self.skill_to_practice.name} +{self.skill_xp_gain}xp" if self.skill_to_practice else ""
            print(f"    [{self.action_type_name} INIT - {self.npc.name}] Creata per '{self.activity_type.name}'. "
                  f"Durata: {self.duration_ticks}t, Gain FUN: {self.fun_gain:.1f}{skill_info}")

    def is_valid(self) -> bool:
        if not super().is_valid(): return False
        
        current_fun = self.npc.get_need_value(NeedType.FUN)
        if current_fun is not None and current_fun >= (settings.NEED_MAX_VALUE - 5.0):
            return False

        if self.activity_type in ACTIVITIES_WITHOUT_OBJECTS:
            return True

        if not self.sim_context or not self.npc.current_location_id: return False
        current_location: Optional['Location'] = self.sim_context.get_location_by_id(self.npc.current_location_id)
        if not current_location: return False

        if not self.required_object_types:
            if settings.DEBUG_MODE: print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Attività '{self.activity_type.name}' necessita di un oggetto, ma 'required_object_types' non è configurato.")
            return False

        for game_obj in current_location.get_objects():
            # TODO: Aggiungere un controllo per vedere se l'oggetto è già in uso da un altro NPC
            # if hasattr(game_obj, 'is_in_use') and not game_obj.is_in_use:
            if game_obj.object_type in self.required_object_types:
                self.target_object = game_obj
                return True
        
        return False

    def on_start(self):
        super().on_start()
        # Se l'azione usa un oggetto, potremmo volerlo marcare come "in uso"
        # per evitare che altri NPC lo usino contemporaneamente.
        if self.target_object and hasattr(self.target_object, 'set_in_use'):
            self.target_object.set_in_use(self.npc.npc_id)

        if settings.DEBUG_MODE:
            target_info = f" usando '{self.target_object.name}'" if self.target_object else ""
            print(f"    [{self.action_type_name} START - {self.npc.name}] Inizia a: {self.activity_type.display_name_it()}{target_info}.")

    def execute_tick(self):
        super().execute_tick()
        # Per un'azione come questa, gli effetti principali sono applicati alla fine (on_finish)
        # o all'interruzione (on_interrupt_effects). Il tick serve solo a far passare il tempo.
        if self.is_started and settings.DEBUG_MODE:
            log_interval = max(1, self.duration_ticks // 4 if self.duration_ticks > 0 else 1)
            if self.ticks_elapsed > 0 and self.ticks_elapsed % log_interval == 0 and not self.is_finished:
                print(f"    [{self.action_type_name} PROGRESS - {self.npc.name}] Si sta divertendo ({self.activity_type.name})... ({self.get_progress_percentage():.0%})")

    def on_finish(self):
        if self.npc:
            if settings.DEBUG_MODE:
                print(f"    [{self.action_type_name} FINISH - {self.npc.name}] Finito di: {self.activity_type.name}. Applico effetti completi.")
            
            # Applica guadagno FUN completo
            self.npc.change_need_value(NeedType.FUN, self.fun_gain, is_decay_event=False)
            
            # Applica guadagno SKILL completo
            if self.skill_to_practice and self.skill_xp_gain > 0:
                # La logica effettiva per aggiungere XP sarà qui
                # Esempio: self.npc.skills_manager.add_experience(self.skill_to_practice, self.skill_xp_gain)
                if settings.DEBUG_MODE:
                    print(f"        -> Guadagno Skill: {self.skill_xp_gain:.1f} XP in {self.skill_to_practice.name}")
        
        # Libera l'oggetto se ne stava usando uno
        if self.target_object and hasattr(self.target_object, 'set_free'):
            self.target_object.set_free()
            
        super().on_finish()

    def on_interrupt_effects(self):
        super().on_interrupt_effects()
        
        # Applica effetti parziali in base a quanto è stata completata l'azione
        if self.npc and self.duration_ticks > 0:
            proportion_completed = self.ticks_elapsed / self.duration_ticks
            
            # Applica guadagno parziale di FUN, magari con una piccola "penalità" per non aver finito
            partial_fun_gain = self.fun_gain * proportion_completed * 0.75 
            if partial_fun_gain > 0:
                if settings.DEBUG_MODE:
                    print(f"    [{self.action_type_name} CANCEL - {self.npc.name}] Attività interrotta. Applicato guadagno FUN parziale: {partial_fun_gain:.2f}")
                self.npc.change_need_value(NeedType.FUN, partial_fun_gain, is_decay_event=False)

            # Applica guadagno parziale di SKILL
            if self.skill_to_practice and self.skill_xp_gain > 0:
                partial_xp_gain = self.skill_xp_gain * proportion_completed
                if partial_xp_gain > 0:
                    # Esempio: self.npc.skills_manager.add_experience(self.skill_to_practice, partial_xp_gain)
                    if settings.DEBUG_MODE:
                        print(f"        -> Guadagno Skill PARZIALE: {partial_xp_gain:.1f} XP in {self.skill_to_practice.name}")
        
        # Libera l'oggetto anche se l'azione viene interrotta
        if self.target_object and hasattr(self.target_object, 'set_free'):
            self.target_object.set_free()