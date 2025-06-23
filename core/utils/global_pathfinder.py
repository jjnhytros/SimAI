# core/utils/global_pathfinder.py

import sys
import os

# "Trucco" per aggiungere la cartella radice del progetto al percorso di Python
# In questo modo, lo script può trovare il pacchetto 'core'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Ora gli import funzioneranno correttamente
import heapq
from typing import List, Optional, Dict
from core.data.world_map_data import WORLD_GRAPH, Route, TransportType

def find_best_route_plan(start_district_id: str, end_district_id: str) -> Optional[List[Route]]:
    """
    Trova il percorso più breve (in termini di tempo) tra due distretti
    usando l'algoritmo di Dijkstra.

    Args:
        start_district_id: L'ID del distretto di partenza.
        end_district_id: L'ID del distretto di arrivo.

    Returns:
        Una lista di oggetti Route che rappresentano il piano di viaggio,
        o None se non esiste un percorso.
    """
    # La coda di priorità conterrà tuple di (tempo_totale, distretto_attuale)
    priority_queue = [(0, start_district_id)]
    
    # Dizionari per tenere traccia dei costi e del percorso
    # 'came_from' memorizza {nodo: (nodo_precedente, rotta_percorsa)}
    came_from: Dict[str, Tuple[str, Route]] = {}
    time_so_far: Dict[str, float] = {district: float('inf') for district in WORLD_GRAPH}
    time_so_far[start_district_id] = 0

    while priority_queue:
        current_time, current_district_id = heapq.heappop(priority_queue)

        # Se abbiamo raggiunto la destinazione, ricostruiamo il percorso
        if current_district_id == end_district_id:
            path: List[Route] = []
            step = current_district_id
            while step in came_from:
                previous_step, route_taken = came_from[step]
                path.append(route_taken)
                step = previous_step
            return path[::-1] # Restituisce il percorso nell'ordine corretto

        # Se abbiamo trovato un percorso più lungo di uno già noto, lo ignoriamo
        if current_time > time_so_far[current_district_id]:
            continue

        # Esplora i vicini (le rotte che partono dal distretto corrente)
        for route in WORLD_GRAPH.get(current_district_id, []):
            new_time = current_time + route.travel_time_minutes
            
            # Se troviamo un percorso più veloce per il vicino, lo aggiorniamo
            if new_time < time_so_far[route.destination_id]:
                time_so_far[route.destination_id] = new_time
                priority = new_time # Per Dijkstra, la priorità è solo il costo
                heapq.heappush(priority_queue, (priority, route.destination_id))
                came_from[route.destination_id] = (current_district_id, route)

    return None # Nessun percorso trovato

# --- Esempio di Utilizzo (per testare lo script) ---
if __name__ == "__main__":
    start = "dist_dosinvelos"
    end = "dist_muse_quarter"
    
    print(f"Calcolo percorso da {start} a {end}...")
    plan = find_best_route_plan(start, end)
    
    if plan:
        print("Piano di viaggio trovato:")
        total_time = 0
        for i, route in enumerate(plan):
            print(f"  {i+1}. Vai a '{route.destination_id}' via {route.transport_type.name} ({route.travel_time_minutes} min)")
            total_time += route.travel_time_minutes
        print(f"Tempo di viaggio totale stimato: {total_time} minuti.")
    else:
        print("Nessun percorso trovato.")