"""
Esecuzione e monitoraggio delle azioni NPC
"""
class ActionExecutor:
    def __init__(self):
        self.active_actions = {}  # npc_id: azione corrente
    
    def execute_action(self, npc, action, time_delta):
        # Interrompi azione corrente se necessario
        if npc.id in self.active_actions:
            if not self._should_interrupt(npc, action):
                self._continue_current_action(npc, time_delta)
                return
            self._interrupt_action(npc)
        
        # Inizia nuova azione
        if action.validate(npc, simulation):
            action.start(npc)
            self.active_actions[npc.id] = action
        else:
            # Fallback a azione alternativa
            self._execute_fallback_action(npc)
    
    def _should_interrupt(self, npc, new_action):
        """Decidi se interrompere l'azione corrente"""
        current_action = self.active_actions[npc.id]
        return (
            new_action.priority > current_action.priority or 
            npc.needs.get_priority_need() < settings.NEED_CRITICAL_THRESHOLD
        )
    
    def _continue_current_action(self, npc, time_delta):
        """Prosegui con l'azione corrente"""
        action = self.active_actions[npc.id]
        result = action.progress(time_delta)
        
        if result.completed:
            action.complete(npc)
            del self.active_actions[npc.id]
    
    def _execute_fallback_action(self, npc):
        """Azione di fallback quando la primaria non è valida"""
        if npc.needs.energy < 30:
            return SleepAction()
        return IdleAction()