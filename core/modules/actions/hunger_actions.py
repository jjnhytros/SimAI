from typing import Optional, TYPE_CHECKING
from core.enums import ActionType, NeedType
from core.enums.item_quality import ItemQuality
from .action_base import BaseAction
from core.config import npc_config, time_config, actions_config

if TYPE_CHECKING:
    from core.character import Character
    from core.simulation import Simulation

class EatAction(BaseAction):
    """
    Azione per mangiare. La fame viene soddisfatta gradualmente ad ogni tick.
    """

    def __init__(self, npc, simulation_context, target_object, duration_ticks, hunger_gain, **kwargs):
        super().__init__(npc, simulation_context, **kwargs)
        self.target_object = target_object # L'oggetto cibo da mangiare
        
        # Calcola il guadagno per tick in base alla qualità
        quality_modifier = 1.0
        food_quality = self.target_object.quality or ItemQuality.NORMAL
        if food_quality == ItemQuality.POOR: quality_modifier = 0.7
        elif food_quality == ItemQuality.GOOD: quality_modifier = 1.2
        elif food_quality == ItemQuality.EXCELLENT: quality_modifier = 1.5
        elif food_quality == ItemQuality.MASTERPIECE: quality_modifier = 2.0
        
        final_hunger_gain = hunger_gain * quality_modifier
        self.gain_per_tick = final_hunger_gain / duration_ticks if duration_ticks > 0 else 0
        self.manages_need = NeedType.HUNGER

    def is_valid(self) -> bool:
        """
        Controlla se l'azione di mangiare è valida.
        """
        # 1. Chiama il controllo della classe base (controlla se c'è un NPC, etc.)
        if not super().is_valid(): 
            return False
        
        # 2. Controlla se il bisogno non è già troppo alto
        hunger_need = self.npc.needs.get(NeedType.HUNGER)
        if hunger_need and hunger_need.get_value() >= (npc_config.NEED_MAX_VALUE - 5.0):
            return False

        # 3. Controlla se l'oggetto target esiste ed è disponibile
        #    (il discoverer ce lo ha già assegnato)
        if not self.target_object or not self.target_object.is_available():
            return False
            
        return True # Se tutti i controlli passano, l'azione è valida

    def on_finish(self):
        """Metodo chiamato al completamento dell'azione."""
        # Non c'è bisogno di fare nulla di speciale qui, perché il guadagno
        # è già avvenuto in execute_tick e BaseAction gestisce lo stato.
        super().on_finish()

    def execute_tick(self):
        super().execute_tick()
        if self.is_started and not self.is_finished:
            self.npc.change_need_value(NeedType.HUNGER, self.gain_per_tick)

    def on_interrupt_effects(self):
        """Quando l'azione viene interrotta, libera solo l'oggetto."""
        if self.target_object:
            self.target_object.set_free()

