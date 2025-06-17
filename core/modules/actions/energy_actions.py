from typing import Optional, TYPE_CHECKING
from .action_base import BaseAction
from core.enums import ActionType, NeedType
from core.config import npc_config

if TYPE_CHECKING:
    from core.character import Character
    from core.simulation import Simulation
    from core.world.game_object import GameObject

class SleepAction(BaseAction):
    """Azione per dormire. L'energia viene recuperata gradualmente ad ogni tick."""

    def __init__(self, npc: 'Character', simulation_context: 'Simulation', 
                 target_object: 'GameObject', duration_ticks: int, energy_gain: float,
                 validation_threshold: float, **kwargs):
        
        super().__init__(
            npc=npc,
            p_simulation_context=simulation_context,
            duration_ticks=duration_ticks,
            action_type_enum=ActionType.ACTION_SLEEP,
            is_interruptible=False, # Dormire è difficile da interrompere
            **kwargs
        )
        
        self.target_object = target_object
        self.gain_per_tick = energy_gain / duration_ticks if duration_ticks > 0 else 0
        self.manages_need = NeedType.ENERGY
        self.validation_threshold = validation_threshold

    def is_valid(self) -> bool:
        if not super().is_valid(): return False
        
        # Controlla se l'azione è necessaria
        current_energy = self.npc.get_need_value(NeedType.ENERGY)
        if current_energy is None or current_energy >= self.validation_threshold:
            return False

        # Il discoverer ha già trovato e assegnato il letto
        if not self.target_object or not self.target_object.is_available():
            return False
            
        return True

    def execute_tick(self):
        super().execute_tick()
        if self.is_started and not self.is_finished:
            # Applica il guadagno di energia incrementale
            self.npc.change_need_value(NeedType.ENERGY, self.gain_per_tick)

    def on_start(self):
        super().on_start()
        if self.target_object:
            self.target_object.set_in_use(self.npc.npc_id)

    def on_finish(self):
        super().on_finish()
        if self.target_object:
            self.target_object.set_free()

    def on_interrupt_effects(self):
        # Essendo non interrompibile, questo metodo potrebbe non essere mai chiamato,
        # ma è buona pratica liberare l'oggetto per sicurezza.
        if self.target_object:
            self.target_object.set_free()