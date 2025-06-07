# core/modules/actions/bathroom_actions.py
from typing import Optional, TYPE_CHECKING, Dict

from core.enums import ActionType, NeedType, ObjectType
from .action_base import BaseAction
from core import settings # Per DEBUG_MODE

if TYPE_CHECKING:
    from core.character import Character
    from core.simulation import Simulation
    from core.world.game_object import GameObject

class UseBathroomAction(BaseAction):
    """Azione per l'NPC di usare il bagno, per Vescica o Igiene."""

    def __init__(self,
                npc: 'Character',
                simulation_context: 'Simulation',
                # --- Parametri di configurazione ora iniettati ---
                for_need: NeedType,      # Il bisogno primario (BLADDER o HYGIENE)
                duration_ticks: int,
                bladder_relief: float, # Sollievo per BLADDER (può essere 0 se for_need è HYGIENE)
                hygiene_gain: float   # Guadagno IGIENE (primario se for_need è HYGIENE, secondario per BLADDER)
                ):

        self.for_need_type: NeedType = for_need
        # self.target_bathroom_object è ora inizializzato in BaseAction come None
        
        # Determina il nome specifico dell'azione
        _action_name_suffix = "USE_TOILET" if self.for_need_type == NeedType.BLADDER else "TAKE_SHOWER_BATH"
        _action_type_name_str = f"ACTION_{_action_name_suffix}"
        
        super().__init__(
            npc=npc,
            action_type_name=_action_type_name_str,
            action_type_enum=ActionType.ACTION_USE_BATHROOM, # Enum generico
            duration_ticks=duration_ticks,
            p_simulation_context=simulation_context,
            is_interruptible=True
        )

        # Popola gli effetti sui bisogni in base ai parametri iniettati
        self.effects_on_needs: Dict[NeedType, float] = {}
        if bladder_relief > 0:
            self.effects_on_needs[NeedType.BLADDER] = bladder_relief
        if hygiene_gain > 0:
            self.effects_on_needs[NeedType.HYGIENE] = hygiene_gain
        
        if settings.DEBUG_MODE:
            print(f"    [{self.action_type_name} INIT - {self.npc.name}] Creata. "
                f"Per Bisogno: {self.for_need_type.name}, Effetti: {self.effects_on_needs}")

    def is_valid(self) -> bool:
        if not super().is_valid(): return False
        
        primary_need_obj = self.npc.needs.get(self.for_need_type)
        if not primary_need_obj: return False

        max_val = getattr(settings, 'NEED_MAX_VALUE', 100.0)
        
        # L'NPC non esegue l'azione se il bisogno è già quasi soddisfatto
        if self.for_need_type == NeedType.BLADDER:
            threshold = max_val - getattr(settings, 'BATHROOM_BLADDER_VALID_THRESHOLD_FROM_MAX', 10.0)
            if primary_need_obj.get_value() >= threshold:
                return False
        elif self.for_need_type == NeedType.HYGIENE:
            threshold = max_val - getattr(settings, 'BATHROOM_HYGIENE_VALID_THRESHOLD_FROM_MAX', 20.0)
            if primary_need_obj.get_value() >= threshold:
                return False
        
        if not self.target_bathroom_object:
            if not self.sim_context or not self.npc.current_location_id: return False
            current_loc = self.sim_context.get_location_by_id(self.npc.current_location_id)
            if not current_loc: return False

            found_obj: Optional['GameObject'] = None
            object_type_needed = ObjectType.TOILET if self.for_need_type == NeedType.BLADDER else (ObjectType.SHOWER, ObjectType.BATHTUB)
            
            for obj in current_loc.get_objects():
                if isinstance(object_type_needed, tuple):
                    if obj.object_type in object_type_needed:
                        found_obj = obj; break
                elif obj.object_type == object_type_needed:
                    found_obj = obj; break
            
            if found_obj:
                self.target_bathroom_object = found_obj
            else:
                return False # Nessun oggetto valido trovato
        
        return True

    def on_finish(self):
        if self.npc:
            if settings.DEBUG_MODE:
                print(f"    [{self.action_type_name} FINISH - {self.npc.name}] Applico effetti: {self.effects_on_needs}")
            for need_type, change_amount in self.effects_on_needs.items():
                self.npc.change_need_value(need_type, change_amount, is_decay_event=False)
        super().on_finish()

    # on_start, execute_tick e on_interrupt_effects possono rimanere come li avevi definiti,
    # usando self.effects_on_needs per calcolare gli effetti parziali.