# core/AI/action_executor.py
"""
Esecuzione e monitoraggio delle azioni NPC
"""
# Importa settings se usato
from core import settings

class ActionExecutor:
    def __init__(self):
        self.active_actions = {}  # npc_id: azione corrente (Questa gestione potrebbe essere ridondante con Character.current_action)

    def execute_action(self, npc, action, time_delta): # 'action' qui è quella potenzialmente restituita da DecisionSystem
        # L'NPC ha già una sua logica di gestione dell'azione corrente e della coda.
        # Per ora, deleghiamo a Character.update_action per gestire il ciclo di vita dell'azione
        # e la scelta di nuove azioni tramite AIDecisionMaker.
        # 'action' ricevuto qui da DecisionSystem è None per ora.
        # 'time_delta' è 1 (tick)

        # In futuro, ActionExecutor gestirà l'avvio, il progresso e la conclusione delle azioni in modo più diretto.
        # Per ora, ci assicuriamo che Character.update_action venga chiamato.
        # Questo implica che AICoordinator deve passare il time_manager e simulation_context.
        # Modifichiamo l'AICoordinator per fare questo.

        # if npc.id in self.active_actions:
        #     if not self._should_interrupt(npc, action):
        #         self._continue_current_action(npc, time_delta)
        #         return
        #     self._interrupt_action(npc)
        # if action and action.validate(npc, simulation): # 'simulation' non è definito qui
        #     action.start(npc)
        #     self.active_actions[npc.id] = action
        # else:
        #     self._execute_fallback_action(npc)
        pass # La chiamata effettiva a npc.update_action sarà fatta da AICoordinator

    def _should_interrupt(self, npc, new_action):
        """Decidi se interrompere l'azione corrente"""
        # current_action = self.active_actions[npc.id]
        # return (
        #     new_action.priority > current_action.priority or
        #     npc.needs.get_priority_need() < settings.NEED_CRITICAL_THRESHOLD
        # )
        return False

    def _continue_current_action(self, npc, time_delta):
        """Prosegui con l'azione corrente"""
        # action = self.active_actions[npc.id]
        # result = action.progress(time_delta) # action non ha progress()
        # if result.completed:
        #     action.complete(npc) # action non ha complete()
        #     del self.active_actions[npc.id]
        pass

    def _execute_fallback_action(self, npc):
        """Azione di fallback quando la primaria non è valida"""
        # from core.modules.actions import SleepAction # Esempio, ma SleepAction richiede npc, context
        # if npc.get_need_value(settings.NeedType.ENERGY) < 30:
        #     # return SleepAction()
        #     pass
        # # return IdleAction() # IdleAction non definita
        pass