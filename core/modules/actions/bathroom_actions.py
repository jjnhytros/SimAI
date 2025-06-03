# core/modules/actions/bathroom_actions.py
"""
Definizione dell'azione per usare il bagno (UseBathroomAction),
soddisfacendo i bisogni di BLADDER e HYGIENE.
"""
from typing import Optional, TYPE_CHECKING, Dict

from core.enums import ActionType, NeedType, ObjectType
from .action_base import BaseAction
from core.config import time_config, npc_config # Per le costanti
from core import settings # Per DEBUG_MODE

if TYPE_CHECKING:
    from core.character import Character
    from core.simulation import Simulation
    from core.world.game_object import GameObject

# Costanti di default (potrebbero andare in actions_config.py)
DEFAULT_BATHROOM_DURATION_TICKS = int(0.15 * (time_config.TXH_SIMULATION if hasattr(time_config, 'TXH_SIMULATION') else 1000)) # Es. ~9 min di gioco
DEFAULT_BLADDER_RELIEF = 80.0
DEFAULT_HYGIENE_GAIN_TOILET = 10.0
DEFAULT_HYGIENE_GAIN_SHOWER_BATHTUB = 70.0

class UseBathroomAction(BaseAction):
    """Azione per l'NPC di usare il bagno."""

    def __init__(self,
                npc: 'Character',
                simulation_context: 'Simulation',
                # for_need specifica se l'azione è primariamente per BLADDER o HYGIENE (doccia/bagno)
                for_need: NeedType = NeedType.BLADDER,
                target_object: Optional['GameObject'] = None, # Es. un WC, una doccia
                duration_ticks: Optional[int] = None
                ):

        self.for_need_type = for_need # Il bisogno primario che si intende soddisfare
        self.target_bathroom_object = target_object
        
        _actual_duration_ticks = duration_ticks
        satiation_effects: Dict[NeedType, float] = {}
        
        action_name_suffix = ""

        if self.for_need_type == NeedType.BLADDER:
            satiation_effects[NeedType.BLADDER] = DEFAULT_BLADDER_RELIEF
            # Usare il WC può dare un piccolo boost all'igiene
            satiation_effects[NeedType.HYGIENE] = DEFAULT_HYGIENE_GAIN_TOILET 
            action_name_suffix = "USE_TOILET"
            if _actual_duration_ticks is None:
                _actual_duration_ticks = DEFAULT_BATHROOM_DURATION_TICKS
        elif self.for_need_type == NeedType.HYGIENE:
            # Se l'azione è per HYGIENE, assumiamo doccia/bagno
            satiation_effects[NeedType.HYGIENE] = DEFAULT_HYGIENE_GAIN_SHOWER_BATHTUB
            action_name_suffix = "TAKE_SHOWER_BATH" # Nome generico
            if _actual_duration_ticks is None:
                _actual_duration_ticks = int(0.5 * (time_config.TXH_SIMULATION if hasattr(time_config, 'TXH_SIMULATION') else 1000)) # Doccia più lunga
        else: # Fallback se for_need non è specificato correttamente
            satiation_effects[NeedType.BLADDER] = DEFAULT_BLADDER_RELIEF
            action_name_suffix = "USE_BATHROOM_GENERIC"
            if _actual_duration_ticks is None:
                _actual_duration_ticks = DEFAULT_BATHROOM_DURATION_TICKS
        
        action_name_str = f"ACTION_{action_name_suffix}"
        if self.target_bathroom_object:
            action_name_str += f"_AT_{self.target_bathroom_object.object_type.name}"

        super().__init__(
            npc=npc,
            action_type_name=action_name_str,
            action_type_enum=ActionType.ACTION_USE_BATHROOM, # Assicurati che esista in ActionType
            duration_ticks=_actual_duration_ticks,
            p_simulation_context=simulation_context,
            is_interruptible=True
        )

        self.effects_on_needs = satiation_effects

        if settings.DEBUG_MODE:
            print(f"    [{self.action_type_name} INIT - {self.npc.name}] Creata. "
                f"Target Obj: {self.target_bathroom_object.name if self.target_bathroom_object else 'N/A'}, "
                f"Effetti: {self.effects_on_needs}, Durata: {self.duration_ticks}t")

    def is_valid(self) -> bool:
        if not super().is_valid():
            return False
        if not self.npc: return False

        # Controlla il bisogno primario per cui l'azione è stata scelta
        primary_need_obj = self.npc.needs.get(self.for_need_type)
        max_val = npc_config.NEED_MAX_VALUE if hasattr(npc_config, 'NEED_MAX_VALUE') else 100.0
        
        if self.for_need_type == NeedType.BLADDER:
            if primary_need_obj and primary_need_obj.get_value() >= (max_val - 10.0): # Non andare se la vescica non è piena
                if settings.DEBUG_MODE:
                    print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Bisogno BLADDER ({primary_need_obj.get_value():.1f}) non abbastanza critico.")
                return False
        elif self.for_need_type == NeedType.HYGIENE:
            if primary_need_obj and primary_need_obj.get_value() >= (max_val - 20.0): # Non farsi la doccia se già puliti
                if settings.DEBUG_MODE:
                    print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Bisogno HYGIENE ({primary_need_obj.get_value():.1f}) già alto.")
                return False
        
        # Logica per trovare un oggetto bagno appropriato se non specificato
        if not self.target_bathroom_object:
            if not self.sim_context: return False
            npc_location_id = self.npc.current_location_id
            if npc_location_id is None: return False
            current_loc = self.sim_context.get_location_by_id(npc_location_id)
            if current_loc:
                found_object = None
                for obj in current_loc.get_objects():
                    if self.for_need_type == NeedType.BLADDER and obj.object_type == ObjectType.TOILET:
                        found_object = obj
                        break
                    elif self.for_need_type == NeedType.HYGIENE and \
                        (obj.object_type == ObjectType.SHOWER or obj.object_type == ObjectType.BATHTUB):
                        found_object = obj
                        break
                if found_object:
                    self.target_bathroom_object = found_object
                    if settings.DEBUG_MODE:
                        print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Trovato oggetto bagno: {found_object.name}")
                else:
                    if settings.DEBUG_MODE:
                        print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Nessun oggetto bagno ({self.for_need_type.name}) trovato.")
                    return False # Nessun oggetto appropriato trovato
            else:
                return False # Locazione non trovata
        
        # TODO: Controllare se self.target_bathroom_object è utilizzabile (es. non rotto, non occupato)
        return True

    def on_start(self):
        super().on_start()
        if settings.DEBUG_MODE:
            obj_name = self.target_bathroom_object.name if self.target_bathroom_object else "bagno generico"
            print(f"    [{self.action_type_name} START - {self.npc.name}] Inizia a usare {obj_name} per {self.for_need_type.name}.")

    def execute_tick(self):
        super().execute_tick()
        # Effetti applicati in on_finish

    def on_finish(self):
        if self.npc:
            if settings.DEBUG_MODE:
                print(f"    [{self.action_type_name} FINISH - {self.npc.name}] Finito di usare il bagno. Applico effetti.")
            for need_type, amount in self.effects_on_needs.items():
                self.npc.change_need_value(need_type, amount)
        super().on_finish()

    def on_interrupt_effects(self):
        super().on_interrupt_effects()
        if self.npc and self.duration_ticks > 0:
            proportion_completed = self.ticks_elapsed / self.duration_ticks
            if settings.DEBUG_MODE:
                print(f"    [{self.action_type_name} CANCEL - {self.npc.name}] Azione interrotta. Applico effetti parziali.")
            for need_type, total_amount in self.effects_on_needs.items():
                partial_amount = total_amount * proportion_completed
                self.npc.change_need_value(need_type, partial_amount)