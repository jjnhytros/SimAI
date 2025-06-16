# core/modules/actions/thirst_actions.py
from typing import Optional, TYPE_CHECKING, Dict
from core.enums import ActionType, NeedType, ObjectType
from .action_base import BaseAction
from core.config import time_config, actions_config, npc_config

if TYPE_CHECKING:
    from core.character import Character
    from core.simulation import Simulation

class DrinkAction(BaseAction):
    """
    Azione per bere. La sete viene placata gradualmente ad ogni tick.
    """

    def __init__(self, npc: 'Character', simulation_context: 'Simulation', **kwargs):
        # 1. Recupera la configurazione per il bisogno THIRST
        config = actions_config.SIMPLE_NEED_ACTION_CONFIGS.get(NeedType.THIRST, {})
        duration = int(config.get("duration_hours", 0.2) * time_config.TXH_SIMULATION)

        super().__init__(
            npc=npc,
            p_simulation_context=simulation_context,
            duration_ticks=duration,
            action_type_enum=ActionType.ACTION_DRINK,
            **kwargs
        )

       # 2. Calcola il guadagno per tick e imposta il bisogno gestito
        thirst_gain = config.get("thirst_gain", 60.0)
        self.gain_per_tick = thirst_gain / duration if duration > 0 else 0
        self.manages_need = NeedType.THIRST # <-- Dice al sistema di non far calare la sete passivamente

        # In futuro, qui potremmo aggiungere effetti secondari come per il caffè
        # self.effects_on_needs.update(config.get("other_effects", {}))


    def is_valid(self) -> bool:
        """
        Controlla se l'azione di bere è valida.
        """
        # 1. Chiama il controllo della classe base (controlla se c'è un NPC, etc.)
        if not super().is_valid(): 
            return False
        
        # 2. Controlla se il bisogno non è già troppo alto
        thirst_need = self.npc.needs.get(NeedType.THIRST)
        if thirst_need and thirst_need.get_value() >= (npc_config.NEED_MAX_VALUE - 5.0):
            return False

        # 3. Controlla se l'oggetto target esiste ed è disponibile
        #    (il discoverer ce lo ha già assegnato)
        if not self.target_object or not self.target_object.is_available():
            return False
            
        return True # Se tutti i controlli passano, l'azione è valida

    # def on_start(self):
    #     super().on_start()
    #     # Blocca l'oggetto quando l'azione inizia
    #     if self.target_object:
    #         self.target_object.set_in_use(self.npc.npc_id)

    def execute_tick(self):
        """Ad ogni tick, placa una piccola parte del bisogno di sete."""
        super().execute_tick()
        if self.is_started and not self.is_finished:
            # Applica il guadagno incrementale
            self.npc.change_need_value(NeedType.THIRST, self.gain_per_tick)

    def on_finish(self):
        """Ora on_finish deve solo liberare l'oggetto."""
        super().on_finish()
        if self.target_object:
            self.target_object.set_free()

    def on_interrupt_effects(self):
        """Quando l'azione viene interrotta, dobbiamo solo liberare l'oggetto."""
        if self.target_object:
            self.target_object.set_free()

    # is_valid e on_start possono usare l'implementazione generica di BaseAction
    # o essere specializzati se necessario, ma la base è già robusta.
