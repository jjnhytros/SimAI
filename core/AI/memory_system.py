# Aggiunta nuovo sistema senza modifiche esistenti
# core/AI/memory_system.py
class MemorySystem:
    def record_event(self, npc, event):
        npc.memory.add_event(event)
        
    def recall_relevant_events(self, npc, context):
        return [e for e in npc.memory if e.relevance > 0.7]