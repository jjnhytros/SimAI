# core/modules/actions/thirst_actions.py
"""
Definizione dell'azione per bere (DrinkAction), 
soddisfacendo il bisogno di THIRST.
"""
from typing import Optional, TYPE_CHECKING, Dict

from core.enums import ActionType, NeedType, ObjectType
from .action_base import BaseAction
from core.config import time_config, npc_config, actions_config # Assumendo che actions_config possa avere defaults
from core import settings # Per DEBUG_MODE

if TYPE_CHECKING:
    from core.character import Character
    from core.simulation import Simulation
    from core.world.game_object import GameObject

# Costanti di default per questa azione (potrebbero andare in actions_config.py)
DEFAULT_DRINK_DURATION_TICKS = int(0.25 * (time_config.TXH_SIMULATION if hasattr(time_config, 'TXH_SIMULATION') else 1000)) # Es. 15 min di gioco
DEFAULT_THIRST_SATISFACTION_WATER = 40.0
DEFAULT_THIRST_SATISFACTION_JUICE = 30.0 # Esempio, il succo potrebbe dare anche FUN

class DrinkAction(BaseAction):
    """Azione per l'NPC di bere per soddisfare la sete."""

    def __init__(self,
                 npc: 'Character',
                 simulation_context: 'Simulation',
                 drink_source_object: Optional['GameObject'] = None, # Es. un rubinetto, una bottiglia
                 drink_type: Optional[str] = "WATER", # Es. "WATER", "JUICE", "SODA"
                 duration_ticks: Optional[int] = None,
                 satiation_amount: Optional[float] = None
                ):
        if drink_type is None:
            self.drink_type: str = "WATER" # Applica il default se None viene passato esplicitamente
        else:
            self.drink_source_object = drink_source_object
            self.drink_type = drink_type
        
        _actual_duration_ticks = duration_ticks
        if _actual_duration_ticks is None:
            # Potremmo avere durate diverse per tipo di bevanda o fonte in actions_config
            _actual_duration_ticks = DEFAULT_DRINK_DURATION_TICKS
        
        _actual_satiation = satiation_amount
        if _actual_satiation is None:
            if self.drink_type == "WATER":
                _actual_satiation = DEFAULT_THIRST_SATISFACTION_WATER
            elif self.drink_type == "JUICE":
                _actual_satiation = DEFAULT_THIRST_SATISFACTION_JUICE
            # ... altre logiche per diversi tipi di bevande ...
            else:
                _actual_satiation = DEFAULT_THIRST_SATISFACTION_WATER # Fallback

        self.thirst_satiation = _actual_satiation

        action_name_str = f"ACTION_DRINK_{self.drink_type.upper()}"
        if self.drink_source_object:
            action_name_str += f"_FROM_{self.drink_source_object.object_type.name}"


        super().__init__(
            npc=npc,
            action_type_name=action_name_str,
            action_type_enum=ActionType.ACTION_DRINK, # Assicurati che ACTION_DRINK esista in ActionType enum
            duration_ticks=_actual_duration_ticks,
            p_simulation_context=simulation_context,
            is_interruptible=True
        )

        self.effects_on_needs: Dict[NeedType, float] = {
            NeedType.THIRST: self.thirst_satiation 
            # Potrebbe influenzare anche BLADDER
        }
        if self.drink_type == "JUICE": # Esempio di effetto secondario
            self.effects_on_needs[NeedType.FUN] = 5.0 # Piccolo boost al divertimento

        if settings.DEBUG_MODE:
            print(f"    [{self.action_type_name} INIT - {self.npc.name}] Creata. "
                  f"Sorgente: {self.drink_source_object.name if self.drink_source_object else 'N/A'}, "
                  f"Tipo: {self.drink_type}, Sazietà: {self.thirst_satiation:.1f}, Durata: {self.duration_ticks}t")

    def is_valid(self) -> bool:
        """Controlla se l'azione di bere è valida."""
        if not super().is_valid(): # Buona pratica chiamare il metodo della classe base
            return False

        if not self.npc: # Assicurati che self.npc esista
             if settings.DEBUG_MODE:
                 print(f"    [{self.action_type_name} VALIDATE] NPC non definito.")
             return False

        thirst_need = self.npc.needs.get(NeedType.THIRST)
        # Assicurati che npc_config.NEED_MAX_VALUE sia accessibile
        max_thirst_value = npc_config.NEED_MAX_VALUE if hasattr(npc_config, 'NEED_MAX_VALUE') else 100.0
        if thirst_need and thirst_need.get_value() >= (max_thirst_value - 10.0):
            if settings.DEBUG_MODE:
                print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Sete ({thirst_need.get_value():.1f}) già troppo alta.")
            return False
        
        if self.drink_source_object:
            # Se un oggetto specifico è fornito
            # Assicurati che l'attributo is_water_source esista su GameObject
            is_source = hasattr(self.drink_source_object, 'is_water_source') and self.drink_source_object.is_water_source
            if self.drink_source_object.object_type == ObjectType.WATER_COOLER or \
               self.drink_source_object.object_type == ObjectType.SINK or \
               is_source:
                return True
            
        else: # Se nessun oggetto specifico, l'IA deve trovarne uno
            if not self.sim_context: # Assicurati che sim_context esista
                if settings.DEBUG_MODE:
                    print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Contesto di simulazione mancante.")
                return False

            # --- MODIFICA CHIAVE QUI ---
            npc_location_id = self.npc.current_location_id
            if npc_location_id is None: # Controllo esplicito che npc_location_id non sia None
                if settings.DEBUG_MODE:
                    print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] NPC current_location_id è None.")
                return False
            
            # Ora npc_location_id è sicuramente una stringa
            current_loc = self.sim_context.get_location_by_id(npc_location_id)
            # --- FINE MODIFICA CHIAVE ---
            
            if current_loc:
                for obj in current_loc.get_objects():
                    is_obj_water_source = hasattr(obj, 'is_water_source') and obj.is_water_source
                    if obj.object_type == ObjectType.SINK or \
                    obj.object_type == ObjectType.REFRIGERATOR or \
                    obj.object_type == ObjectType.WATER_COOLER or \
                    is_obj_water_source:
                        self.drink_source_object = obj 
                        if settings.DEBUG_MODE:
                            print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Trovato fonte: {obj.name}")
                        return True
            else: # current_loc è None
                if settings.DEBUG_MODE:
                    print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Impossibile trovare la locazione corrente: ID '{npc_location_id}'")


        if settings.DEBUG_MODE:
            print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Nessuna fonte per bere trovata o valida.")
        return False

    def on_start(self):
        super().on_start()
        # TODO: Animazione "sta bevendo"
        # if self.drink_source_object: self.drink_source_object.set_in_use(self.npc) # Se l'oggetto può essere usato solo da uno alla volta
        if settings.DEBUG_MODE:
            source_name = self.drink_source_object.name if self.drink_source_object else "fonte generica"
            print(f"    [{self.action_type_name} START - {self.npc.name}] Inizia a bere {self.drink_type} da {source_name}.")

    def execute_tick(self):
        super().execute_tick()
        # Il bisogno di sete viene soddisfatto istantaneamente in on_finish per semplicità

        if self.is_started and settings.DEBUG_MODE:
            log_interval = max(1, self.duration_ticks // 2 if self.duration_ticks > 0 else 1) 
            if self.ticks_elapsed > 0 and self.ticks_elapsed % log_interval == 0 and \
               self.ticks_elapsed < self.duration_ticks and not self.is_finished:
                print(f"    [{self.action_type_name} PROGRESS - {self.npc.name}] Sta bevendo... ({self.get_progress_percentage():.0%})")

    def on_finish(self):
        if self.npc:
            if settings.DEBUG_MODE:
                print(f"    [{self.action_type_name} FINISH - {self.npc.name}] Finito di bere. Applico effetti.")
            
            # Applica effetti principali
            self.npc.change_need_value(NeedType.THIRST, self.thirst_satiation)
            if self.drink_type == "JUICE": # Esempio
                self.npc.change_need_value(NeedType.FUN, self.effects_on_needs.get(NeedType.FUN, 0))
            
            # Possibile effetto sul bisogno BLADDER
            bladder_increase = self.thirst_satiation * 0.25 # Esempio: 25% di ciò che bevi va alla vescica
            self.npc.change_need_value(NeedType.BLADDER, -bladder_increase) # Decay per la vescica significa che si riempie

        # if self.drink_source_object: self.drink_source_object.set_free()
        super().on_finish()

    def on_interrupt_effects(self):
        super().on_interrupt_effects()
        # Applica effetti parziali se interrotta
        if self.npc and self.duration_ticks > 0:
            proportion_completed = self.ticks_elapsed / self.duration_ticks
            partial_satiation = self.thirst_satiation * proportion_completed
            
            if partial_satiation > 0:
                if settings.DEBUG_MODE:
                    print(f"    [{self.action_type_name} CANCEL - {self.npc.name}] Azione interrotta. "
                          f"Applicato sazietà THIRST parziale: {partial_satiation:.2f}")
                self.npc.change_need_value(NeedType.THIRST, partial_satiation)
                # Applica anche effetti secondari parziali
                if self.drink_type == "JUICE":
                    self.npc.change_need_value(NeedType.FUN, self.effects_on_needs.get(NeedType.FUN, 0) * proportion_completed)
                
                bladder_increase = partial_satiation * 0.25
                self.npc.change_need_value(NeedType.BLADDER, -bladder_increase)
        
        # if self.drink_source_object: self.drink_source_object.set_free()