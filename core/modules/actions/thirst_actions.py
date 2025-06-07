# core/modules/actions/thirst_actions.py
from typing import Optional, TYPE_CHECKING, Dict

from core.enums import ActionType, NeedType, ObjectType
from .action_base import BaseAction
from core import settings

if TYPE_CHECKING:
    from core.character import Character
    from core.simulation import Simulation
    from core.world.game_object import GameObject

class DrinkAction(BaseAction):
    """Azione per l'NPC di bere, configurata dall'esterno."""

    def __init__(self,
                 npc: 'Character',
                 simulation_context: 'Simulation',
                 # --- Parametri di configurazione iniettati ---
                 drink_type_name: str,
                 duration_ticks: int,
                 thirst_gain: float,
                 effects_on_other_needs: Optional[Dict[NeedType, float]] = None
                ):
        
        self.drink_type_name = drink_type_name
        self.thirst_gain = thirst_gain
        # target_object viene trovato in is_valid, quindi lo inizializziamo in BaseAction

        super().__init__(
            npc=npc,
            action_type_name=f"ACTION_DRINK_{self.drink_type_name.upper()}",
            action_type_enum=ActionType.ACTION_DRINK,
            duration_ticks=duration_ticks,
            p_simulation_context=simulation_context,
            is_interruptible=True
        )

        self.effects_on_needs = {NeedType.THIRST: self.thirst_gain}
        if effects_on_other_needs:
            self.effects_on_needs.update(effects_on_other_needs)

        if settings.DEBUG_MODE:
            source_log = self.drink_source_object.name if self.drink_source_object else "auto-detect"
            print(f"    [{self.action_type_name} INIT - {self.npc.name}] Creata. "
                f"Tipo: {self.drink_type_name}, Sorgente: {source_log}, "
                f"Gain Sete: {self.thirst_gain:.1f}, Durata: {self.duration_ticks}t, "
                f"Altri Effetti: {self.effects_on_needs if effects_on_other_needs else 'Nessuno'}")

    def is_valid(self) -> bool:
        if not super().is_valid(): # Chiamata al metodo base se BaseAction.is_valid() ha logica comune
            return False # Ad esempio, se BaseAction.is_valid() controlla self.npc

        thirst_need = self.npc.needs.get(NeedType.THIRST)
        # Assicurati che npc_config sia importato o settings.NEED_MAX_VALUE
        max_thirst_value = getattr(settings, 'NEED_MAX_VALUE', 100.0) 
        if thirst_need and thirst_need.get_value() >= (max_thirst_value - 10.0): # Non bere se non si ha sete
            if settings.DEBUG_MODE:
                print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Sete ({thirst_need.get_value():.1f}) già troppo alta.")
            return False
        
        # Se un drink_source_object specifico non è stato passato, l'IA ne cerca uno.
        if not self.drink_source_object:
            if not self.sim_context: return False # sim_context è p_simulation_context da BaseAction
            
            npc_location_id = self.npc.current_location_id
            if npc_location_id is None: 
                if settings.DEBUG_MODE: print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] NPC current_location_id è None.")
                return False
            
            current_loc = self.sim_context.get_location_by_id(npc_location_id)
            if not current_loc:
                if settings.DEBUG_MODE: print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Locazione corrente non trovata.")
                return False

            found_object: Optional['GameObject'] = None
            # Logica per trovare un oggetto sorgente d'acqua appropriato (es. SINK, REFRIGERATOR, WATER_COOLER)
            # o qualsiasi oggetto con obj.is_water_source == True
            for obj in current_loc.get_objects():
                is_obj_water_source = hasattr(obj, 'is_water_source') and obj.is_water_source
                if obj.object_type == ObjectType.SINK or \
                   obj.object_type == ObjectType.REFRIGERATOR or \
                   obj.object_type == ObjectType.WATER_COOLER or \
                   is_obj_water_source:
                    # TODO: Qui potresti aggiungere logica per preferire fonti che corrispondono a self.drink_type_name
                    # se la simulazione traccia il contenuto specifico degli oggetti (es. frigo con succhi)
                    found_object = obj
                    break 
            
            if found_object:
                self.drink_source_object = found_object # Memorizza l'oggetto trovato
                # Aggiorna dinamicamente action_type_name se vuoi includere l'oggetto specifico
                self.action_type_name = f"ACTION_DRINK_{self.drink_type_name.upper()}_FROM_{self.drink_source_object.object_type.name}"
                if settings.DEBUG_MODE:
                    print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Trovato fonte automatica: {found_object.name}")
            else:
                if settings.DEBUG_MODE:
                    print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Nessuna fonte per bere ({self.drink_type_name}) trovata in {current_loc.name}.")
                return False
        
        # TODO: Controllare se self.drink_source_object è utilizzabile (es. non rotto, non occupato da altri)
        return True

    def on_start(self):
        super().on_start()
        # TODO: Animazione, l'oggetto potrebbe diventare "in uso"
        if settings.DEBUG_MODE:
            source_name = self.drink_source_object.name if self.drink_source_object else "fonte sconosciuta"
            print(f"    [{self.action_type_name} START - {self.npc.name}] Inizia a bere {self.drink_type_name} da {source_name}.")

    # execute_tick da BaseAction

    def on_finish(self):
        if self.npc:
            if settings.DEBUG_MODE:
                print(f"    [{self.action_type_name} FINISH - {self.npc.name}] Finito di bere {self.drink_type_name}. Applico effetti.")
            
            for need_type, change_amount in self.effects_on_needs.items():
                self.npc.change_need_value(need_type, change_amount, is_decay_event=False)
        
        # TODO: Se l'oggetto era una risorsa consumabile (es. bottiglia d'acqua), aggiorna il suo stato o rimuovilo.
        super().on_finish()

    def on_interrupt_effects(self):
        super().on_interrupt_effects()
        if self.npc and self.duration_ticks > 0:
            proportion_completed = self.ticks_elapsed / self.duration_ticks
            if settings.DEBUG_MODE:
                print(f"    [{self.action_type_name} CANCEL - {self.npc.name}] Azione bere interrotta. Applico effetti parziali.")
            
            for need_type, total_amount in self.effects_on_needs.items():
                partial_amount = total_amount * proportion_completed
                if partial_amount != 0: # Applica solo se c'è un cambiamento effettivo
                    self.npc.change_need_value(need_type, partial_amount, is_decay_event=False)