# core/modules/actions/bathroom_actions.py
from typing import Optional, TYPE_CHECKING, Dict

from core.enums import ActionType, NeedType, ObjectType
from .action_base import BaseAction
from core.config import time_config, npc_config # Per le costanti di default se necessarie a livello di modulo
from core import settings # Per DEBUG_MODE

if TYPE_CHECKING:
    from core.character import Character
    from core.simulation import Simulation
    from core.world.game_object import GameObject

# Rimuoviamo i DEFAULT a livello di modulo da qui, verranno letti da settings in AIDecisionMaker
# DEFAULT_BATHROOM_DURATION_TICKS = ...
# DEFAULT_BLADDER_RELIEF = ...
# DEFAULT_HYGIENE_GAIN_TOILET = ...
# DEFAULT_HYGIENE_GAIN_SHOWER_BATHTUB = ...

class UseBathroomAction(BaseAction):
    """Azione per l'NPC di usare il bagno."""

    def __init__(self,
                 npc: 'Character',
                 simulation_context: 'Simulation',
                 # --- Parametri di configurazione ora iniettati ---
                 for_need_type: NeedType,      # Il bisogno primario (BLADDER o HYGIENE)
                 duration_ticks: int,
                 bladder_relief_amount: float, # Sollievo per BLADDER (può essere 0 se for_need è HYGIENE)
                 hygiene_gain_amount: float,   # Guadagno IGIENE (primario se for_need è HYGIENE, secondario per BLADDER)
                 # Parametri opzionali
                 target_object: Optional['GameObject'] = None
                ):

        self.for_need_type: NeedType = for_need_type
        self.target_bathroom_object: Optional['GameObject'] = target_object
        
        # Determina il nome dell'azione e l'enum ActionType più specifico se possibile
        # Questo potrebbe essere ulteriormente raffinato in on_start quando l'oggetto target è certo.
        _action_name_suffix = "USE_BATHROOM_GENERIC"
        if self.for_need_type == NeedType.BLADDER:
            _action_name_suffix = "USE_TOILET"
        elif self.for_need_type == NeedType.HYGIENE:
            _action_name_suffix = "TAKE_SHOWER_BATH"
        
        _action_type_name_str = f"ACTION_{_action_name_suffix}"
        if self.target_bathroom_object:
            _action_type_name_str += f"_AT_{self.target_bathroom_object.object_type.name}"

        # Idealmente, avresti enum ActionType più specifici se vuoi distinguerli nettamente
        # Es. ActionType.ACTION_USE_TOILET, ActionType.ACTION_TAKE_SHOWER
        # Per ora, usiamo un generico ACTION_USE_BATHROOM come nel tuo codice originale.
        action_type_enum_val = ActionType.ACTION_USE_BATHROOM 

        super().__init__(
            npc=npc,
            action_type_name=_action_type_name_str,
            action_type_enum=action_type_enum_val,
            duration_ticks=duration_ticks,
            p_simulation_context=simulation_context,
            is_interruptible=True
        )

        # Popola gli effetti sui bisogni in base ai parametri iniettati
        self.effects_on_needs: Dict[NeedType, float] = {}
        if bladder_relief_amount > 0: # Si applica principalmente se for_need è BLADDER
            self.effects_on_needs[NeedType.BLADDER] = bladder_relief_amount
        if hygiene_gain_amount > 0: # Si applica se for_need è HYGIENE o come effetto secondario
            self.effects_on_needs[NeedType.HYGIENE] = hygiene_gain_amount
        
        if settings.DEBUG_MODE:
            obj_name_log = self.target_bathroom_object.name if self.target_bathroom_object else "auto-detect"
            print(f"    [{self.action_type_name} INIT - {self.npc.name}] Creata. "
                f"Per Bisogno: {self.for_need_type.name}, Target: {obj_name_log}, "
                f"Effetti: {self.effects_on_needs}, Durata: {self.duration_ticks}t")

    def is_valid(self) -> bool:
        if not super().is_valid(): return False # Controlli base di BaseAction
        if not self.npc: return False

        primary_need_obj = self.npc.needs.get(self.for_need_type)
        if not primary_need_obj: return False # Il bisogno primario deve esistere

        max_val = getattr(settings, 'NEED_MAX_VALUE', 100.0)
        
        # L'NPC usa il bagno se il bisogno primario non è già soddisfatto
        if self.for_need_type == NeedType.BLADDER:
            # Non andare se la vescica è quasi vuota (valore alto)
            if primary_need_obj.get_value() >= (max_val - getattr(settings, 'BATHROOM_BLADDER_VALID_THRESHOLD_FROM_MAX', 10.0)):
                if settings.DEBUG_MODE: print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Bisogno BLADDER ({primary_need_obj.get_value():.1f}) non abbastanza critico.")
                return False
        elif self.for_need_type == NeedType.HYGIENE:
            # Non farsi la doccia se già molto puliti
            if primary_need_obj.get_value() >= (max_val - getattr(settings, 'BATHROOM_HYGIENE_VALID_THRESHOLD_FROM_MAX', 20.0)): 
                if settings.DEBUG_MODE: print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Bisogno HYGIENE ({primary_need_obj.get_value():.1f}) già alto.")
                return False
        
        if not self.target_bathroom_object: # Se non è stato passato un oggetto target, cercalo
            if not self.sim_context or not self.npc.current_location_id: return False
            current_loc = self.sim_context.get_location_by_id(self.npc.current_location_id)
            if not current_loc: return False

            found_obj: Optional['GameObject'] = None
            if self.for_need_type == NeedType.BLADDER:
                object_type_to_find = ObjectType.TOILET
                for obj in current_loc.get_objects():
                    if obj.object_type == object_type_to_find: # Uso di '=='
                        found_obj = obj
                        break
            elif self.for_need_type == NeedType.HYGIENE:
                object_types_to_find = (ObjectType.SHOWER, ObjectType.BATHTUB) # Tupla
                for obj in current_loc.get_objects():
                    if obj.object_type in object_types_to_find: # Uso di 'in' con la tupla
                        found_obj = obj
                        break
            
            if self.for_need_type == NeedType.BLADDER:
                object_type_to_find = ObjectType.TOILET
                for obj in current_loc.get_objects():
                    if obj.object_type == object_type_to_find: # Uso di '=='
                        found_obj = obj
                        break
            elif self.for_need_type == NeedType.HYGIENE:
                object_types_to_find = (ObjectType.SHOWER, ObjectType.BATHTUB) # Tupla
                for obj in current_loc.get_objects():
                    if obj.object_type in object_types_to_find: # Uso di 'in' con la tupla
                        found_obj = obj
                        break
        
        # TODO: Controllare se self.target_bathroom_object è utilizzabile (non rotto, non occupato)
        # Esempio:
        # if self.target_bathroom_object and hasattr(self.target_bathroom_object, 'is_broken') and self.target_bathroom_object.is_broken:
        #     if settings.DEBUG_MODE: print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Oggetto {self.target_bathroom_object.name} è rotto.")
        #     return False
        # if self.target_bathroom_object and hasattr(self.target_bathroom_object, 'is_in_use_by') and self.target_bathroom_object.is_in_use_by is not None and self.target_bathroom_object.is_in_use_by != self.npc.npc_id:
        #     if settings.DEBUG_MODE: print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Oggetto {self.target_bathroom_object.name} è occupato.")
        #     return False
        return True

    def on_start(self):
        super().on_start()
        if settings.DEBUG_MODE:
            obj_name = self.target_bathroom_object.name if self.target_bathroom_object else "N/D"
            print(f"    [{self.action_type_name} START - {self.npc.name}] Inizia a usare {obj_name} per {self.for_need_type.name}.")

    # execute_tick da BaseAction

    def on_finish(self):
        if self.npc:
            if settings.DEBUG_MODE:
                print(f"    [{self.action_type_name} FINISH - {self.npc.name}] Finito di usare bagno. Applico effetti: {self.effects_on_needs}")
            for need_type, change_amount in self.effects_on_needs.items():
                self.npc.change_need_value(need_type, change_amount, is_decay_event=False)
        super().on_finish()

    def on_interrupt_effects(self):
        super().on_interrupt_effects()
        if self.npc and self.duration_ticks > 0:
            proportion_completed = self.ticks_elapsed / self.duration_ticks
            if settings.DEBUG_MODE:
                print(f"    [{self.action_type_name} CANCEL - {self.npc.name}] Azione interrotta. Applico effetti parziali.")
            for need_type, total_amount in self.effects_on_needs.items():
                partial_amount = total_amount * proportion_completed
                if partial_amount != 0:
                    self.npc.change_need_value(need_type, partial_amount, is_decay_event=False)