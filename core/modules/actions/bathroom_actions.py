# core/modules/actions/bathroom_actions.py
from typing import Optional, TYPE_CHECKING, Dict

from core.enums import ActionType, NeedType, ObjectType
from core.modules.memory.memory_definitions import Problem
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
                for_need: NeedType,
                duration_ticks: int,
                bladder_relief: float,
                hygiene_gain: float,
                # Il target object è opzionale, verrà cercato in is_valid se non fornito
                target_object: Optional['GameObject'] = None,
                triggering_problem: Optional['Problem'] = None
                ):

        self.for_need_type: NeedType = for_need
        
        # Determina il nome specifico dell'azione
        action_name_suffix = "USE_TOILET" if self.for_need_type == NeedType.BLADDER else "TAKE_SHOWER_BATH"
        
        super().__init__(
            npc=npc,
            action_type_name=f"ACTION_{action_name_suffix}",
            action_type_enum=ActionType.ACTION_USE_BATHROOM,
            duration_ticks=duration_ticks,
            p_simulation_context=simulation_context,
            triggering_problem=triggering_problem
        )
        
        # --- CORREZIONE: Usa l'attributo standard self.target_object ---
        self.target_object = target_object
        
        # Popola gli effetti sui bisogni
        self.effects_on_needs: Dict[NeedType, float] = {}
        if bladder_relief > 0: self.effects_on_needs[NeedType.BLADDER] = bladder_relief
        if hygiene_gain > 0: self.effects_on_needs[NeedType.HYGIENE] = hygiene_gain

    def is_valid(self) -> bool:
        """
        Controlla se l'azione di usare il bagno è valida.
        Verifica le soglie dei bisogni e la presenza di un oggetto bagno disponibile.
        """
        # 1. Controlli di base
        if not super().is_valid():
            return False
        
        primary_need_obj = self.npc.needs.get(self.for_need_type)
        if not primary_need_obj:
            return False

        # 2. Controlla se l'azione è necessaria (il bisogno non è già alto)
        max_val = getattr(settings, 'NEED_MAX_VALUE', 100.0)
        
        if self.for_need_type == NeedType.BLADDER:
            threshold = max_val - getattr(settings, 'BATHROOM_BLADDER_VALID_THRESHOLD_FROM_MAX', 10.0)
            if primary_need_obj.get_value() >= threshold:
                return False
        elif self.for_need_type == NeedType.HYGIENE:
            threshold = max_val - getattr(settings, 'BATHROOM_HYGIENE_VALID_THRESHOLD_FROM_MAX', 20.0)
            if primary_need_obj.get_value() >= threshold:
                return False
        else: # Tipo di bisogno non supportato
            return False
        
        # 3. Trova un oggetto valido, se non già specificato
        if not self.target_object:
            if not self.sim_context or not self.npc.current_location_id:
                return False
            
            current_loc = self.sim_context.get_location_by_id(self.npc.current_location_id)
            if not current_loc:
                return False

            found_obj = None
            # Definisci i tipi di oggetto che stai cercando
            object_types_needed = (ObjectType.TOILET,) if self.for_need_type == NeedType.BLADDER else \
                                (ObjectType.SHOWER, ObjectType.BATHTUB)
            
            # Cerca un oggetto del tipo giusto CHE SIA DISPONIBILE
            for obj in current_loc.get_objects():
                if obj.object_type in object_types_needed:
                    if obj.is_available(): # Controlla se l'oggetto è libero e non rotto
                        found_obj = obj
                        break # Trovato un oggetto valido, interrompi la ricerca
            
            if found_obj:
                self.target_object = found_obj # Assegna l'oggetto trovato all'azione
            else:
                if settings.DEBUG_MODE:
                    print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Nessun oggetto bagno DISPONIBILE trovato.")
                return False # Nessun oggetto valido e disponibile trovato
        
        # 4. Se un oggetto target esiste (o è stato appena trovato), verifica un'ultima volta la sua disponibilità
        if self.target_object and not self.target_object.is_available():
            if settings.DEBUG_MODE:
                print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Oggetto target '{self.target_object.name}' non è disponibile.")
            return False

        # Se tutti i controlli sono passati, l'azione è valida
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