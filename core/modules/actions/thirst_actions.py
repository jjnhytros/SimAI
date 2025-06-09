# core/modules/actions/thirst_actions.py
from typing import Optional, TYPE_CHECKING, Dict

from core.enums import ActionType, NeedType, ObjectType
from core.modules.memory.memory_definitions import Problem
from .action_base import BaseAction
from core.config import npc_config
from core import settings

if TYPE_CHECKING:
    from core.character import Character
    from core.simulation import Simulation
    from core.world.game_object import GameObject
    from core.world.location import Location

class DrinkAction(BaseAction):
    """Azione per l'NPC di bere, configurata dall'esterno."""

    def __init__(self,
                npc: 'Character',
                simulation_context: 'Simulation',
                drink_type_name: str,
                duration_ticks: int,
                thirst_gain: float,
                effects_on_other_needs: Optional[Dict[NeedType, float]] = None,
                # Il target object è opzionale
                target_object: Optional['GameObject'] = None,
                triggering_problem: Optional['Problem'] = None
                ):
        
        self.drink_type_name: str = drink_type_name
        self.thirst_gain: float = thirst_gain

        super().__init__(
            npc=npc,
            action_type_name=f"ACTION_DRINK_{self.drink_type_name.upper()}",
            action_type_enum=ActionType.ACTION_DRINK,
            duration_ticks=duration_ticks,
            p_simulation_context=simulation_context,
            triggering_problem=triggering_problem
        )

        # Usa l'attributo standard `target_object` ereditato da BaseAction
        self.target_object = target_object

        self.effects_on_needs: Dict[NeedType, float] = {NeedType.THIRST: self.thirst_gain}
        if effects_on_other_needs:
            self.effects_on_needs.update(effects_on_other_needs)

    def is_valid(self) -> bool:
        """Controlla se l'azione di bere è valida."""
        if not super().is_valid():
            return False

        thirst_need = self.npc.needs.get(NeedType.THIRST)
        if thirst_need and thirst_need.get_value() >= (npc_config.NEED_MAX_VALUE - 10.0):
            return False
        
        # Se un oggetto non è stato fornito, cercalo nell'ambiente
        if not self.target_object:
            if not self.sim_context or not self.npc.current_location_id: return False
            
            current_loc: Optional['Location'] = self.sim_context.get_location_by_id(self.npc.current_location_id)
            if not current_loc: return False

            found_obj: Optional['GameObject'] = None
            # Tipi di oggetto che possono soddisfare la sete
            drink_sources = {ObjectType.SINK, ObjectType.REFRIGERATOR, ObjectType.WATER_COOLER}
            
            for obj in current_loc.get_objects():
                # Controlla se l'oggetto è di un tipo valido E se è disponibile
                if obj.object_type in drink_sources and obj.is_available():
                    found_obj = obj
                    break
            
            if found_obj:
                self.target_object = found_obj # Assegna l'oggetto trovato
            else:
                if settings.DEBUG_MODE:
                    print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Nessuna fonte per bere disponibile trovata.")
                return False # Nessun oggetto valido e disponibile trovato
        
        # Se un oggetto target esiste (passato o appena trovato), verifica la sua disponibilità
        if not self.target_object.is_available():
            if settings.DEBUG_MODE:
                print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Oggetto target '{self.target_object.name}' non è disponibile.")
            return False

        return True

    def on_start(self):
        super().on_start()
        # Blocca l'oggetto quando l'azione inizia
        if self.target_object:
            self.target_object.set_in_use(self.npc.npc_id)

    def on_finish(self):
        # Applica gli effetti
        if self.npc:
            for need_type, change_amount in self.effects_on_needs.items():
                self.npc.change_need_value(need_type, change_amount)
        
        # Libera l'oggetto quando l'azione finisce
        if self.target_object:
            self.target_object.set_free()
        
        super().on_finish()

    def on_interrupt_effects(self):
        super().on_interrupt_effects()
        # Applica effetti parziali
        if self.npc and self.duration_ticks > 0:
            proportion_completed = self.elapsed_ticks / self.duration_ticks
            for need_type, total_amount in self.effects_on_needs.items():
                partial_amount = total_amount * proportion_completed
                self.npc.change_need_value(need_type, partial_amount)

        # Libera l'oggetto anche in caso di interruzione
        if self.target_object:
            self.target_object.set_free()