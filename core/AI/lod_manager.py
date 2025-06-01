# core/AI/lod_manager.py
class LODManager:
    HIGH_DETAIL_RADIUS = 50  # Unità di gioco
    
    def update_detail_level(self, player_position):
        for npc in simulation.npcs:
            distance = calculate_distance(player_position, npc.position)
            npc.lod = LOD.HIGH if distance < self.HIGH_DETAIL_RADIUS else LOD.LOW