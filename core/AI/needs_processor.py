"""
Gestione avanzata dei bisogni NPC
"""
class NeedsProcessor:
    def update_needs(self, npc, time_delta):
        # Calcola il decadimento basato sul tempo
        for need_type in npc.needs:
            decay_rate = settings.config.NEED_DECAY_RATES.get(need_type, 0)
            npc.needs[need_type] += decay_rate * time_delta
            
        # Applica modificatori situazionali
        self._apply_environmental_effects(npc)
        self._apply_trait_effects(npc)
        
        # Mantieni i bisogni nei limiti
        self._clamp_needs(npc)
    
    def _apply_environmental_effects(self, npc):
        """Effetti dell'ambiente sui bisogni"""
        location = simulation.get_location(npc.location_id)
        if location.is_outdoor and weather.is_raining:
            npc.needs.comfort -= 0.1
    
    def _apply_trait_effects(self, npc):
        """Effetti dei tratti sui bisogni"""
        if "High Metabolism" in npc.traits:
            npc.needs.hunger *= 1.2
    
    def _clamp_needs(self, npc):
        """Mantieni i bisogni nei limiti 0-100"""
        for need_type in npc.needs:
            npc.needs[need_type] = max(0, min(100, npc.needs[need_type]))
    
    def get_priority_need(self, npc):
        """Restituisce il bisogno più urgente"""
        return min(npc.needs, key=npc.needs.get)