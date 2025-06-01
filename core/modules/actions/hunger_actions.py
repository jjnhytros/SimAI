# core/modules/actions/hunger_actions.py
from typing import Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from core.character import Character
    from core.simulation import Simulation # Necessario per il type hint di simulation_context

from core.enums import NeedType
from core import settings
from .action_base import BaseAction

_MODULE_DEFAULT_EAT_ACTION_DURATION_TICKS: int = 30
_MODULE_DEFAULT_EAT_ACTION_HUNGER_GAIN: float = 75.0

class EatAction(BaseAction):
    def __init__(self, 
                 npc: 'Character', 
                 simulation_context: Optional['Simulation'] = None, # <-- AGGIUNGI simulation_context QUI
                 duration_ticks: Optional[int] = None, 
                 hunger_gain: Optional[float] = None
                ):
        
        actual_duration = duration_ticks if duration_ticks is not None \
            else getattr(settings, 'EAT_ACTION_DURATION_TICKS', _MODULE_DEFAULT_EAT_ACTION_DURATION_TICKS)
        actual_gain = hunger_gain if hunger_gain is not None \
            else getattr(settings, 'EAT_ACTION_HUNGER_GAIN', _MODULE_DEFAULT_EAT_ACTION_HUNGER_GAIN)

        super().__init__(
            npc=npc,
            action_type_name="ACTION_EAT_MEAL",
            duration_ticks=actual_duration,
            simulation_context=simulation_context, # <-- PASSA A SUPER
            is_interruptible=True,
            description=f"Sta mangiando (Durata: {actual_duration}t)."
        )
        self.effects_on_needs = {NeedType.HUNGER: actual_gain}
        
        if settings.DEBUG_MODE:
            print(f"    [EatAction INIT - {self.npc.name}] Creata. Durata: {self.duration_ticks}t, Gain Fame: {actual_gain}")

    def is_valid(self) -> bool:
        """Controlla se l'NPC può attualmente mangiare."""
        if not self.npc: return False
        
        current_hunger = self.npc.get_need_value(NeedType.HUNGER)
        if current_hunger is None: return False # Il bisogno dovrebbe essere sempre inizializzato

        # L'NPC può mangiare se la sua fame non è al massimo.
        # Potremmo aggiungere altre condizioni: es. è vicino a cibo? È un orario consono?
        can_eat = current_hunger < settings.NEED_MAX_VALUE 
        
        # TODO VI.2.a: Aggiungere controllo disponibilità cibo.
        if not can_eat and settings.DEBUG_MODE:
            print(f"    [EatAction VALIDATE - {self.npc.name}] Non può mangiare, fame ({current_hunger:.1f}) già al massimo.")
        return can_eat

    def on_start(self):
        """Chiamato all'inizio dell'azione di mangiare."""
        super().on_start()
        if settings.DEBUG_MODE:
            print(f"    [EatAction START - {self.npc.name}] Ha iniziato a mangiare.")
        # Potrebbe impostare un'animazione testuale: self.npc.current_animation_state = "eating"

    def execute_tick(self):
        """Logica per ogni tick mentre l'NPC sta mangiando."""
        super().execute_tick() # Gestisce l'incremento di ticks_elapsed e chiama on_finish
        
        # Il log di progresso può essere reso meno frequente o rimosso
        # if self.is_started and settings.DEBUG_MODE:
        #     # Logga il progresso solo a intervalli significativi (es. 25%, 50%, 75%)
        #     # o meno frequentemente per azioni lunghe
        #     if self.duration_ticks > 0 and self.ticks_elapsed > 0:
        #         progress_interval = self.duration_ticks // 4 # Circa 4 log di progresso
        #         if progress_interval > 0 and self.ticks_elapsed % progress_interval == 0 and not self.is_finished:
        #             print(f"    [EatAction PROGRESS - {self.npc.name}] Sta mangiando... ({self.get_progress_percentage():.0%})")
        #         elif self.duration_ticks <= 4 and not self.is_finished: # Per azioni molto brevi, logga ogni tick
        #             print(f"    [EatAction PROGRESS - {self.npc.name}] Sta mangiando... ({self.get_progress_percentage():.0%})")
        pass # Commentare i log di progresso se non strettamente necessari

    def on_finish(self):
        """Chiamato quando l'NPC ha finito di mangiare."""
        if self.npc:
            if settings.DEBUG_MODE:
                print(f"    [EatAction FINISH - {self.npc.name}] Ha finito di mangiare. Applico effetti sui bisogni.")
            # Applica gli effetti definiti nel costruttore
            for need_type, change_amount in self.effects_on_needs.items():
                self.npc.change_need_value(need_type, change_amount, is_decay_event=False) # is_decay_event è False perché è un guadagno
        
        super().on_finish() # Imposta is_finished, is_started=False, ecc.
        # self.npc.current_animation_state = "idle"

    def on_interrupt_effects(self):
        """Logica se l'azione di mangiare viene interrotta."""
        super().on_interrupt_effects()
        if self.npc and settings.DEBUG_MODE:
            print(f"    [EatAction INTERRUPT - {self.npc.name}] Pasto interrotto.")
        # Considera se applicare effetti parziali in caso di interruzione (es. metà guadagno fame)
        # Per ora, l'interruzione non applica effetti parziali per EatAction.