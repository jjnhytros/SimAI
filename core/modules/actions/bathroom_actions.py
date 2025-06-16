from typing import Optional, TYPE_CHECKING, Dict

from core.enums import ActionType, NeedType, ObjectType
from core.modules.memory.memory_definitions import Problem
from .action_base import BaseAction
from core.config import npc_config, time_config, actions_config

if TYPE_CHECKING:
    from core.character import Character
    from core.simulation import Simulation
    from core.world.game_object import GameObject

class UseBathroomAction(BaseAction):
    """
    Azione per usare il bagno. Il sollievo alla vescica è graduale,
    mentre il guadagno di igiene è istantaneo alla fine.
    """

    def __init__(self, npc: 'Character', simulation_context: 'Simulation', **kwargs):
        # 1. Recupera la configurazione per il bisogno che ha scatenato l'azione
        problem = kwargs.get('triggering_problem')
        primary_need = problem.details.get('need') if problem and problem.details else NeedType.BLADDER
        
        config = actions_config.SIMPLE_NEED_ACTION_CONFIGS.get(primary_need, {})
        duration = int(config.get("duration_hours", 0.25) * time_config.TXH_SIMULATION)

        super().__init__(
            npc=npc,
            p_simulation_context=simulation_context,
            duration_ticks=duration,
            action_type_enum=ActionType.ACTION_USE_BATHROOM,
            **kwargs
        )

        # 2. Imposta l'effetto graduale
        bladder_gain = config.get("bladder_gain", 100.0)
        self.gain_per_tick = bladder_gain / duration if duration > 0 else 0
        self.manages_need = NeedType.BLADDER # Il decadimento passivo della vescica si ferma

        # 3. Imposta l'effetto istantaneo che avverrà alla fine
        self.effects_on_needs: Dict[NeedType, float] = {
            NeedType.HYGIENE: config.get("hygiene_gain", 15.0)
        }

    def is_valid(self) -> bool:
        """
        Controlla se l'azione di andare in bagno è valida.
        """
        # 1. Chiama il controllo della classe base (controlla se c'è un NPC, etc.)
        if not super().is_valid(): 
            return False
        
        # 2. Controlla se il bisogno non è già troppo alto
        bladder_need = self.npc.needs.get(NeedType.BLADDER)
        if bladder_need and bladder_need.get_value() >= (npc_config.NEED_MAX_VALUE - 5.0):
            return False

        # 3. Controlla se l'oggetto target esiste ed è disponibile
        #    (il discoverer ce lo ha già assegnato)
        if not self.target_object or not self.target_object.is_available():
            return False
            
        return True # Se tutti i controlli passano, l'azione è valida

    def execute_tick(self):
        """Ad ogni tick, soddisfa una piccola parte del bisogno BLADDER."""
        super().execute_tick()
        if self.is_started and not self.is_finished:
            self.npc.change_need_value(NeedType.BLADDER, self.gain_per_tick)

    def on_start(self):
        super().on_start()
        if self.target_object:
            self.target_object.set_in_use(self.npc.npc_id)

    def on_finish(self):
        # La chiamata a super() qui applicherà il guadagno di IGIENE definito in effects_on_needs
        super().on_finish()
        if self.target_object:
            self.target_object.set_free()