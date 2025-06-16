# core/utils/pathfinding.py
import heapq
from typing import List, Tuple, Optional

def astar_pathfind(
    walkable_grid: List[List[bool]], 
    start: Tuple[int, int], 
    end: Tuple[int, int]
) -> Optional[List[Tuple[int, int]]]:
    """
    Algoritmo A* per trovare il percorso più breve su una griglia.
    Usa (riga, colonna) -> (y, x) per le coordinate.

    Args:
        walkable_grid: Una lista di liste di booleani. True se la cella è calpestabile.
        start: Una tupla (y, x) per la posizione di partenza.
        end: Una tupla (y, x) per la posizione di arrivo.

    Returns:
        Una lista di tuple (y, x) che rappresentano il percorso, o None se non trovato.
    """
    rows = len(walkable_grid)
    if rows == 0: return None
    cols = len(walkable_grid[0])
    
    open_set = []
    # L'heapq contiene (punteggio_f, posizione)
    heapq.heappush(open_set, (0, start))
    
    came_from = {}
    g_score = { (r, c): float('inf') for r in range(rows) for c in range(cols) }
    g_score[start] = 0
    f_score = { (r, c): float('inf') for r in range(rows) for c in range(cols) }
    # Funzione euristica (distanza di Manhattan)
    f_score[start] = abs(start[0] - end[0]) + abs(start[1] - end[1])

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == end:
            # Ricostruisci il percorso a ritroso
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            # Il percorso è al contrario, lo invertiamo
            # Nota: la posizione di partenza non è inclusa nel path finale
            return path[::-1]

        # Controlla i vicini (su, giù, sinistra, destra)
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            neighbor = (current[0] + dr, current[1] + dc)

            # Controlla che il vicino sia nei limiti della griglia e calpestabile
            if not (0 <= neighbor[0] < rows and 0 <= neighbor[1] < cols) or not walkable_grid[neighbor[0]][neighbor[1]]:
                continue

            tentative_g_score = g_score[current] + 1
            if tentative_g_score < g_score.get(neighbor, float('inf')):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + (abs(neighbor[0] - end[0]) + abs(neighbor[1] - end[1]))
                if neighbor not in [i[1] for i in open_set]:
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
                
    return None # Nessun percorso trovato