# core/modules/actions/hunger_actions.py
from typing import Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from core.character import Character
    from core.simulation import Simulation

from core.enums import NeedType, ActionType, ObjectType
from core import settings # Solo per DEBUG_MODE (idealmente passato tramite contesto o rimosso dai log di basso livello)
from .action_base import BaseAction
from core.world.game_object import GameObject

# Rimuoviamo i _MODULE_DEFAULT qui perché i valori verranno iniettati

class EatAction(BaseAction):
    def __init__(self, 
                npc: 'Character', 
                simulation_context: 'Simulation',
                duration_ticks: int, 
                hunger_gain: float,
                target_object: Optional['GameObject'] = None # Puoi passare l'oggetto target qui
                ):
        
        action_type_enum_val = ActionType.ACTION_EAT
        
        # La chiamata a super() ora è sintatticamente corretta
        super().__init__(
            npc=npc,
            action_type_name=action_type_enum_val.name,
            action_type_enum=action_type_enum_val,
            duration_ticks=duration_ticks,
            p_simulation_context=simulation_context,
            is_interruptible=True
        )
        
        # Salva i parametri specifici dell'azione e popola effects_on_needs
        self.hunger_gain = hunger_gain
        self.effects_on_needs = {NeedType.HUNGER: self.hunger_gain}
        # if effects_on_other_needs:
        #     self.effects_on_needs.update(effects_on_other_needs)
        
        if settings.DEBUG_MODE:
            print(f"    [{self.action_type_name} INIT - {self.npc.name}] Creata. "
                f"Durata: {self.duration_ticks}t, Gain Fame: {self.hunger_gain:.1f}")

    def is_valid(self) -> bool:
        # La logica di validazione rimane simile, ma non dovrebbe più fare affidamento 
        # su settings per i parametri di comportamento dell'azione stessa.
        # Può usare self.npc, self.sim_context e i parametri dell'azione (es. self.hunger_gain).
        if not self.sim_context or not self.npc.current_location_id: return False
        current_loc = self.sim_context.get_location_by_id(self.npc.current_location_id)
        if not current_loc: return False

        found_food_source = None
        for obj in current_loc.get_objects():
            if obj.object_type == ObjectType.REFRIGERATOR: # Esempio
                # TODO: Controlla se l'oggetto è utilizzabile
                found_food_source = obj
                break
        
        if found_food_source:
            self.target_object = found_food_source # <-- MEMORIZZA L'OGGETTO TROVATO
            if settings.DEBUG_MODE:
                print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Trovato fonte di cibo: {self.target_object.name}")
            return True
        else:
            if settings.DEBUG_MODE:
                print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Nessuna fonte di cibo trovata.")
            return False

    def on_start(self):
        super().on_start()
        if settings.DEBUG_MODE:
            print(f"    [{self.action_type_name} START - {self.npc.name}] Ha iniziato a mangiare.")

    def execute_tick(self):
        super().execute_tick()
        # La logica di applicazione degli effetti è in on_finish

    def on_finish(self):
        if self.npc:
            if settings.DEBUG_MODE:
                print(f"    [{self.action_type_name} FINISH - {self.npc.name}] Ha finito di mangiare. Applico effetti sui bisogni.")
            # Applica gli effetti definiti in self.effects_on_needs
            for need_type, change_amount in self.effects_on_needs.items():
                self.npc.change_need_value(need_type, change_amount, is_decay_event=False)
        
        super().on_finish()

    def on_interrupt_effects(self):
        super().on_interrupt_effects()
        # Applica effetti parziali in base a quanto è stata completata l'azione
        if self.npc and self.duration_ticks > 0:
            proportion_completed = self.ticks_elapsed / self.duration_ticks
            partial_hunger_gain = self.effects_on_needs.get(NeedType.HUNGER, 0.0) * proportion_completed
            
            if partial_hunger_gain > 0:
                if settings.DEBUG_MODE:
                    print(f"    [{self.action_type_name} CANCEL - {self.npc.name}] Pasto interrotto. "
                          f"Applicato guadagno FAME parziale: {partial_hunger_gain:.2f}")
                self.npc.change_need_value(NeedType.HUNGER, partial_hunger_gain, is_decay_event=False)
            elif settings.DEBUG_MODE:
                 print(f"    [{self.action_type_name} CANCEL - {self.npc.name}] Pasto interrotto. Nessun guadagno parziale di fame.")