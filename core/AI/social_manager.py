"""
Gestione delle interazioni sociali e relazioni
"""
class SocialManager:
    def handle_social_interactions(self, npc, simulation):
        # Interazioni nella stessa locazione
        nearby_npcs = simulation.get_npcs_in_location(npc.location_id)
        for other in nearby_npcs:
            if other != npc and self._should_interact(npc, other):
                self._initiate_interaction(npc, other)
        
        # Aggiornamento relazioni a lungo termine
        self._update_relationships(npc, simulation)
    
    def _should_interact(self, npc, other):
        """Determina se due NPC dovrebbero interagire"""
        relationship = npc.relationships.get(other.id)
        return (
            relationship and 
            relationship.score > 50 and
            not other.is_busy and
            random.random() < 0.3  # Probabilità casuale
        )
    
    def _initiate_interaction(self, npc, other):
        """Avvia un'interazione sociale"""
        interaction_type = self._select_interaction_type(npc, other)
        interaction = SocialInteraction(npc, other, interaction_type)
        interaction.execute()
        
        # Aggiorna la relazione
        self._update_relationship_from_interaction(
            npc, other, interaction
        )
    
    def _update_relationships(self, npc, simulation):
        """Aggiornamento passivo delle relazioni"""
        for relation in npc.relationships.values():
            # Decadimento naturale
            relation.score = max(0, relation.score - 0.01)
            
            # Effetti da tratti
            if "Lonely" in npc.traits:
                relation.score = max(0, relation.score - 0.05)