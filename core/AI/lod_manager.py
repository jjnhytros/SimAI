# core/AI/lod_manager.py
from typing import TYPE_CHECKING, Tuple, Optional

# Importa l'Enum LODLevel dalla sua nuova posizione
from ..enums.lod_level import LODLevel 
# Importa la funzione calculate_distance dalla sua nuova posizione
from core.utils.math_utils import calculate_distance 
from core.config import npc_config

if TYPE_CHECKING:
    from core.simulation import Simulation # Per type hinting
    from core.character import Character # Per type hinting

class LODManager:
    def __init__(self, simulation_instance: 'Simulation'):
        """
        Inizializza il LODManager.

        Args:
            simulation_instance (Simulation): L'istanza della simulazione principale.
        """
        self.simulation: 'Simulation' = simulation_instance

    def update_npc_lod(self, npc: 'Character', player_position: Tuple[float, float]):
        """Aggiorna il livello di dettaglio di un singolo NPC."""
        if not npc:
            return
        
        # Assumiamo che npc.position sia (npc.logical_x, npc.logical_y)
        # Se hai un attributo npc.position dedicato, usa quello.
        npc_pos = (float(npc.logical_x), float(npc.logical_y))
        distance = calculate_distance(player_position, npc_pos)

        new_lod = LODLevel.LOW # Default a LOW se lontano
        if distance < npc_config.LOD_DISTANCE_HIGH:
            new_lod = LODLevel.HIGH
        elif distance < npc_config.LOD_DISTANCE_MEDIUM:
            new_lod = LODLevel.MEDIUM
        
        if npc.lod != new_lod:
            npc.lod = new_lod
            # Potresti voler aggiungere un log qui se DEBUG_MODE è attivo
            print(f"  [LODManager] NPC {npc.name} LOD impostato a {new_lod.name}")

    def update_all_npcs_lod(self, player_position: Optional[Tuple[float, float]]):
        """
        Aggiorna il livello di dettaglio per tutti gli NPC nella simulazione
        in base alla posizione del giocatore (o di un focus point).

        Args:
            player_position (Optional[Tuple[float, float]]): La posizione (x, y) del giocatore o
                                                            del punto di focus. Se None, non fa nulla.
        """
        if player_position is None:
            # Se non c'è una posizione del giocatore, potresti voler impostare tutti a un LOD di default
            # o mantenere il loro stato attuale. Per ora, non facciamo nulla.
            return

        # Accedi agli NPC tramite l'istanza di simulazione salvata
        for npc_instance in self.simulation.npcs.values():
            # Il giocatore stesso viene escluso o gestito qui, se necessario
            if npc_instance.is_player_character:
                npc_instance.lod = LODLevel.HIGH
                continue
            self.update_npc_lod(npc_instance, player_position)
