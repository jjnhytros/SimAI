# core/modules/actions/fun_actions.py
"""
Definizione dell'azione per divertirsi (HaveFunAction), 
soddisfacendo il bisogno di FUN.
Riferimento TODO: IV.4.c.iv (nel TODO_Generale.md)
"""
from typing import Dict, Optional, TYPE_CHECKING, Set as TypingSet # Rinominato per evitare conflitto con variabile 'set'
import random 

if TYPE_CHECKING:
    from core.character import Character
    from core.simulation import Simulation
    from core.world.location import Location

from core.enums import NeedType, FunActivityType, ActionType 
from core import settings
from .action_base import BaseAction

# --- Costanti di Default a Livello di Modulo per HaveFunAction ---
_MODULE_DEFAULT_HAVEFUNACTION_DURATION_TICKS: int = settings.IXH * 1 # Default a 1 ora di gioco
_MODULE_DEFAULT_HAVEFUNACTION_FUN_GAIN: float = 35.0 

# Definiamo un set di attività che non richiedono un oggetto specifico
ACTIVITIES_WITHOUT_OBJECTS: TypingSet[FunActivityType] = { # Usiamo TypingSet per il type hint
    FunActivityType.DANCE,
    FunActivityType.DAYDREAM,
    FunActivityType.JOG_IN_PLACE,
    FunActivityType.SING,
    FunActivityType.PRACTICE_PUBLIC_SPEAKING,
    FunActivityType.SOCIAL_MEDIA_Browse, # Navigare sui social media potrebbe non richiedere un PC se hanno dispositivi personali
    FunActivityType.WATCH_CLOUDS,
    FunActivityType.MEDITATE,
    # Aggiungi altre attività che ritieni non necessitino di un oggetto specifico
}

class HaveFunAction(BaseAction):
    """Azione per l'NPC di divertirsi con una specifica attività."""
    
    def __init__(self, 
                 npc: 'Character', 
                 activity_type: FunActivityType, 
                 simulation_context: 'Simulation', # Rimosso Optional
                 duration_ticks: Optional[int] = None,
                 fun_gain: Optional[float] = None
                ):
        
        self.activity_type: FunActivityType = activity_type
        
        _actual_duration = duration_ticks
        if _actual_duration is None:
            specific_duration_key = f"FUN_ACT_{activity_type.name}_DURATION_TICKS"
            _actual_duration = getattr(settings, specific_duration_key, None)
            if _actual_duration is None:
                generic_action_duration_key = "DEFAULT_HAVEFUNACTION_DURATION_TICKS"
                _actual_duration = getattr(settings, generic_action_duration_key, None)
                if _actual_duration is None:
                    _actual_duration = _MODULE_DEFAULT_HAVEFUNACTION_DURATION_TICKS
        
        _actual_fun_gain = fun_gain
        if _actual_fun_gain is None:
            specific_gain_key = f"FUN_ACT_{activity_type.name}_FUN_GAIN"
            _actual_fun_gain = getattr(settings, specific_gain_key, None)
            if _actual_fun_gain is None:
                generic_action_gain_key = "DEFAULT_HAVEFUNACTION_FUN_GAIN"
                _actual_fun_gain = getattr(settings, generic_action_gain_key, None)
                if _actual_fun_gain is None:
                    _actual_fun_gain = _MODULE_DEFAULT_HAVEFUNACTION_FUN_GAIN
        
        self.fun_gain = _actual_fun_gain 

        # Determina l'ActionType enum. Potrebbe essere generico o specifico.
        # Per ora, usiamo un ActionType generico per tutte le HaveFunAction.
        # In futuro, potremmo avere ActionType più specifici se necessario.
        action_type_enum_to_use = ActionType.ACTION_HAVE_FUN
        action_name_str = f"ACTION_HAVE_FUN_{activity_type.name}" # Nome più specifico per i log

        super().__init__(
            npc=npc,
            action_type_name=action_name_str, 
            action_type_enum=action_type_enum_to_use,
            duration_ticks=_actual_duration,
            p_simulation_context=simulation_context, 
            is_interruptible=True
        )
        
        self.effects_on_needs: Dict[NeedType, float] = {
            NeedType.FUN: self.fun_gain
        }
        
        if settings.DEBUG_MODE:
             print(f"    [{self.action_type_name} INIT - {self.npc.name}] Creata per '{activity_type.name}'. "
                   f"Durata: {self.duration_ticks}t, Gain FUN: {self.fun_gain:.1f}")

    def is_valid(self) -> bool:
        """
        Controlla se l'azione di divertimento è valida.
        Alcune attività non richiedono oggetti; altre sì.
        """
        if not self.npc: return False # NPC deve esistere
        
        # Controlla se l'NPC ha già il bisogno di FUN quasi al massimo
        current_fun = self.npc.get_need_value(NeedType.FUN)
        if current_fun is not None and current_fun >= (settings.NEED_MAX_VALUE - 5.0): # Non iniziare se FUN è >= 95
            if settings.DEBUG_MODE: 
                print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] FUN ({current_fun:.1f}) già troppo alto per iniziare nuova attività.")
            return False

        # Se l'attività non richiede un oggetto specifico, è generalmente valida
        if self.activity_type in ACTIVITIES_WITHOUT_OBJECTS:
            if settings.DEBUG_MODE: 
                print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Attività '{self.activity_type.display_name_it()}' non richiede oggetto. Azione valida.")
            return True

        # Se l'attività richiede un oggetto, cerca un oggetto appropriato nella locazione
        # self.sim_context è l'attributo corretto ereditato da BaseAction
        if not self.sim_context or not self.npc.current_location_id:
            if settings.DEBUG_MODE: 
                print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Contesto di simulazione o locazione NPC mancante per attività con oggetto.")
            return False

        current_location: Optional['Location'] = self.sim_context.get_location_by_id(self.npc.current_location_id)
        if not current_location:
            if settings.DEBUG_MODE: 
                print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Impossibile trovare la locazione corrente: {self.npc.current_location_id}")
            return False

        for game_obj in current_location.get_objects(): # Usa il metodo corretto get_objects()
            if self.activity_type in game_obj.provides_fun_activities:
                # TODO: Aggiungere un controllo se l'oggetto 'game_obj' è attualmente in uso da un altro NPC
                # if not game_obj.is_in_use: 
                if settings.DEBUG_MODE:
                    print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Trovato oggetto '{game_obj.name}' che fornisce '{self.activity_type.display_name_it()}' in {current_location.name}. Azione valida.")
                return True
                # else:
                #    if settings.DEBUG_MODE: print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Oggetto '{game_obj.name}' per '{self.activity_type.display_name_it()}' è già in uso.")
        
        if settings.DEBUG_MODE:
            print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Nessun oggetto disponibile trovato per l'attività '{self.activity_type.display_name_it()}' in {current_location.name}.")
        return False

    def on_start(self):
        super().on_start()
        # TODO: Se l'azione usa un oggetto, impostare l'oggetto come "in uso" da questo NPC.
        if settings.DEBUG_MODE:
            print(f"    [{self.action_type_name} START - {self.npc.name}] Inizia a: {self.activity_type.display_name_it()}.")

    def execute_tick(self):
        super().execute_tick()
        if self.is_started and settings.DEBUG_MODE:
            log_interval = max(1, self.duration_ticks // 4) # Logga circa 4 volte
            if self.ticks_elapsed > 0 and self.ticks_elapsed % log_interval == 0 and \
               self.ticks_elapsed < self.duration_ticks and not self.is_finished:
                print(f"    [{self.action_type_name} PROGRESS - {self.npc.name}] Si sta divertendo ({self.activity_type.name})... ({self.get_progress_percentage():.0%})")

    def on_finish(self):
        if self.npc:
            if settings.DEBUG_MODE:
                print(f"    [{self.action_type_name} FINISH - {self.npc.name}] Finito di: {self.activity_type.display_name_it()}. Applico effetti.")
            self.npc.change_need_value(NeedType.FUN, self.fun_gain, is_decay_event=False)
        
        # TODO: Se l'azione usava un oggetto, impostare l'oggetto come "libero".
        super().on_finish()

    def on_interrupt_effects(self):
        super().on_interrupt_effects()
        # TODO: Se l'azione usava un oggetto, impostare l'oggetto come "libero".
        if self.npc and self.duration_ticks > 0:
            proportion_completed = self.ticks_elapsed / self.duration_ticks
            # Guadagno parziale ridotto se interrotto (es. 75% del proporzionale)
            partial_gain = self.fun_gain * proportion_completed * 0.75 
            
            if partial_gain > 0:
                if settings.DEBUG_MODE:
                    print(f"    [{self.action_type_name} CANCEL - {self.npc.name}] Attività {self.activity_type.name} interrotta. "
                          f"Applicato guadagno FUN parziale: {partial_gain:.2f}")
                self.npc.change_need_value(NeedType.FUN, partial_gain, is_decay_event=False)
            elif settings.DEBUG_MODE and self.npc:
                 print(f"    [{self.action_type_name} CANCEL - {self.npc.name}] Attività {self.activity_type.name} interrotta. Nessun guadagno parziale.")