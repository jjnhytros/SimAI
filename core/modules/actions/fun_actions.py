# core/modules/actions/fun_actions.py
"""
Definizione dell'azione per divertirsi (HaveFunAction), 
soddisfacendo il bisogno di FUN.
Riferimento TODO: IV.4.c.iv (nel TODO_Generale.md)
"""
from typing import Dict, Optional, TYPE_CHECKING, Set as TypingSet, Tuple

if TYPE_CHECKING:
    from core.character import Character
    from core.simulation import Simulation
    from core.world.game_object import GameObject
    from core.world.location import Location

# --- Import Corretti ---
# Aggiungi SkillType e ObjectType se non già presenti
from core.enums import NeedType, FunActivityType, ActionType, ObjectType, SkillType 
from core.config import time_config, actions_config, npc_config
from core import settings
from .action_base import BaseAction

# ... (resto del file come prima)

class HaveFunAction(BaseAction):
    """Azione per l'NPC di divertirsi con una specifica attività."""
    
    def __init__(self, 
                 npc: 'Character', 
                 simulation_context: 'Simulation',
                 # --- Parametri di configurazione iniettati ---
                 activity_type: FunActivityType,
                 duration_ticks: int,
                 fun_gain: float,
                 # Parametri opzionali per attività avanzate
                 required_object_types: Optional[Tuple[ObjectType, ...]] = None,
                 skill_to_practice: Optional[SkillType] = None, # <-- ORA SkillType è definito
                 skill_xp_gain: float = 0.0
                ):
        # ... (il resto del metodo __init__ rimane invariato)
        # ...
        super().__init__(
            npc=npc,
            action_type_name=f"ACTION_HAVE_FUN_{activity_type.name}", 
            action_type_enum=ActionType.ACTION_HAVE_FUN,
            duration_ticks=duration_ticks,
            p_simulation_context=simulation_context, 
            is_interruptible=True
        )
        self.activity_type = activity_type
        self.fun_gain = fun_gain
        self.skill_to_practice = skill_to_practice
        self.skill_xp_gain = skill_xp_gain
        self.required_object_types = required_object_types
        self.target_object: Optional['GameObject'] = None

        self.effects_on_needs: Dict[NeedType, float] = {
            NeedType.FUN: self.fun_gain
        }
        
        if settings.DEBUG_MODE:
            skill_info = f", Skill: {self.skill_to_practice.name} +{self.skill_xp_gain}xp" if self.skill_to_practice else ""
            print(f"    [{self.action_type_name} INIT - {self.npc.name}] Creata per '{activity_type.name}'. "
                  f"Durata: {self.duration_ticks}t, Gain FUN: {self.fun_gain:.1f}{skill_info}")

    def is_valid(self) -> bool:
        if not self.npc: return False
        
        current_fun = self.npc.get_need_value(NeedType.FUN)
        if current_fun is not None and current_fun >= (settings.NEED_MAX_VALUE - 5.0):
            if settings.DEBUG_MODE: 
                print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] FUN ({current_fun:.1f}) già troppo alto.")
            return False

        # Se non richiede oggetti, l'azione è valida ovunque
        if not self.required_object_types:
            # Potresti anche usare la lista ACTIVITIES_WITHOUT_OBJECTS se la mantieni aggiornata
            # if self.activity_type in ACTIVITIES_WITHOUT_OBJECTS:
            if settings.DEBUG_MODE: 
                print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Attività '{self.activity_type.name}' non richiede oggetto. Azione valida.")
            return True

        if not self.sim_context or not self.npc.current_location_id:
            if settings.DEBUG_MODE: 
                print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Contesto di simulazione o locazione NPC mancante.")
            return False

        current_location: Optional['Location'] = self.sim_context.get_location_by_id(self.npc.current_location_id)
        if not current_location:
            if settings.DEBUG_MODE: 
                print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Impossibile trovare la locazione corrente: {self.npc.current_location_id}")
            return False

        for game_obj in current_location.get_objects():
            if game_obj.object_type in self.required_object_types:
                # TODO: Aggiungere logica per verificare se l'oggetto è utilizzabile (non rotto, non occupato)
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
            
            # Applica guadagno skill se presente
            if self.skill_to_practice and self.skill_xp_gain > 0:
                # TODO: Bisognerà importare il sistema delle skill e chiamare un metodo come:
                # self.npc.skills_manager.add_experience(self.skill_to_practice, self.skill_xp_gain)
                if settings.DEBUG_MODE:
                    print(f"        -> Guadagno Skill: {self.skill_xp_gain:.1f} XP in {self.skill_to_practice.name}")
        
        super().on_finish()

    # on_interrupt_effects può applicare un guadagno parziale di FUN e XP