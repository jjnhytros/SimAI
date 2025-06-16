from typing import Optional, TYPE_CHECKING
from core.enums import NeedType, ActionType, ObjectType
from core.config import npc_config, time_config, actions_config
from .action_base import BaseAction

if TYPE_CHECKING:
    from core.character import Character
    from core.simulation import Simulation

class SleepAction(BaseAction):
    """
    Azione per dormire. L'energia viene recuperata gradualmente ad ogni tick.
    """
    def __init__(self, npc: 'Character', simulation_context: 'Simulation', **kwargs):
        # 1. Recupera la configurazione completa per l'azione di dormire
        config = actions_config.SIMPLE_NEED_ACTION_CONFIGS.get(NeedType.ENERGY, {})
        
        duration = int(config.get("duration_hours", 8.0) * time_config.TXH_SIMULATION)

        super().__init__(
            npc=npc,
            p_simulation_context=simulation_context,
            duration_ticks=duration,
            action_type_enum=ActionType.ACTION_SLEEP,
            is_interruptible=False,
            **kwargs
        )
        
        # 2. Salva i parametri specifici e calcola il guadagno per tick
        self.validation_threshold = config.get("validation_threshold", 60.0)
        energy_gain_per_hour = config.get("energy_gain_per_hour", 12.5)
        self.gain_per_tick = (energy_gain_per_hour / time_config.TXH_SIMULATION) * (duration / self.duration_ticks) if self.duration_ticks > 0 else 0
        
        # 3. Imposta il bisogno gestito da questa azione
        self.manages_need = NeedType.ENERGY

    def is_valid(self) -> bool:
        """
        Controlla se l'azione di dormire è valida.
        """
        # 1. Chiama il controllo della classe base (controlla se c'è un NPC, etc.)
        if not super().is_valid(): 
            return False
        
        # 2. Controlla se il bisogno non è già troppo alto
        energy_need = self.npc.needs.get(NeedType.ENERGY)
        if energy_need and energy_need.get_value() >= (npc_config.NEED_MAX_VALUE - 5.0):
            return False

        # 3. Controlla se l'oggetto target esiste ed è disponibile
        #    (il discoverer ce lo ha già assegnato)
        if not self.target_object or not self.target_object.is_available():
            return False
            
        return True # Se tutti i controlli passano, l'azione è valida

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
        """Quando l'azione viene interrotta, dobbiamo solo liberare l'oggetto."""
        if self.target_object:
            self.target_object.set_free()
