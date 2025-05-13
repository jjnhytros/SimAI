import time
import os

def clear_output():
    """Pulisce l'output del terminale."""
    os.system('cls' if os.name == 'nt' else 'clear')

def draw_grid(n, grid, elapsed_time=None):
    """Disegna la griglia corrente e il tempo trascorso."""
    if elapsed_time is not None:
        days = int(elapsed_time // (24 * 3600))
        elapsed_time %= (24 * 3600)
        hours = int(elapsed_time // 3600)
        elapsed_time %= 3600
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        time_str = f"Tempo: {days}g {hours}:{minutes:02d}:{seconds:02d}"
        print(time_str.center(n * 6 - 1))  # Centra la stringa del tempo

    for i in range(n):
        row_str = ""
        for j in range(n):
            if grid[i][j] == 0:
                row_str += "[   ]"
            else:
                row_str += f"[{grid[i][j]:>3}]"
        print(row_str)

def format_time(elapsed_time):
    """Formatta il tempo in D giorni, H:M:S."""
    days = int(elapsed_time // (24 * 3600))
    elapsed_time %= (24 * 3600)
    hours = int(elapsed_time // 3600)
    elapsed_time %= 3600
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)
    return f"{days}g {hours}:{minutes:02d}:{seconds:02d}"

def is_safe(r, c, n, grid):
    """Verifica se una casella (r, c) è valida all'interno della griglia e non ancora occupata."""
    return 0 <= r < n and 0 <= c < n and grid[r][c] == 0

def find_solution(n, grid, r, c, num, start_time):
    """Funzione ricorsiva per trovare una soluzione, aggiornando la griglia e il tempo."""
    current_time = time.time()
    elapsed_time = current_time - start_time

    if num > n * n:
        clear_output()
        print("Griglia completata!")
        draw_grid(n, grid, elapsed_time)
        return True  # Griglia completamente riempita

    if not is_safe(r, c, n, grid):
        return False  # Casella non valida o già occupata

    grid[r][c] = num
    clear_output()
    print(f"Tentativo di posizionare {num} in ({r}, {c}):")
    draw_grid(n, grid, elapsed_time)
    time.sleep(0.1)  # Piccolo ritardo per visualizzare il processo

    # Prova tutte le possibili mosse dalla casella corrente
    moves = get_valid_moves(r, c, n, grid)
    for next_r, next_c in moves:
        if find_solution(n, grid, next_r, next_c, num + 1, start_time):
            return True

    # Backtrack: se nessuna mossa porta a una soluzione, resetta la casella
    grid[r][c] = 0
    clear_output()
    print(f"Backtracking da ({r}, {c}):")
    draw_grid(n, grid, elapsed_time)
    time.sleep(0.1)
    return False

def get_valid_moves(r, c, n, grid):
    """Restituisce una lista di mosse valide dalla casella (r, c)."""
    valid_moves = []

    # Mosse orizzontali/verticali (lasciando 2 spazi)
    possible_hv = [(r, c + 3), (r, c - 3), (r + 3, c), (r - 3, c)]
    for nr, nc in possible_hv:
        if is_safe(nr, nc, n, grid):
            valid_moves.append((nr, nc))

    # Mosse diagonali (lasciando 1 spazio)
    possible_diag = [(r + 2, c + 2), (r + 2, c - 2), (r - 2, c + 2), (r - 2, c - 2)]
    for nr, nc in possible_diag:
        if is_safe(nr, nc, n, grid):
            valid_moves.append((nr, nc))

    return valid_moves

def solve_grid_filling(n):
    """Risolve il problema del riempimento della griglia nxn e memorizza i tempi."""
    start_time_total = time.time()
    attempt_times = {}
    solution_found = False

    # Prova a partire da ogni casella della griglia
    for start_r in range(n):
        for start_c in range(n):
            clear_output()
            print(f"Tentativo di soluzione partendo da ({start_r}, {start_c})...")
            grid = [[0 for _ in range(n)] for _ in range(n)]  # Reset della griglia per ogni tentativo
            draw_grid(n, grid)
            time.sleep(0.2)

            start_time_attempt = time.time()
            if find_solution(n, grid, start_r, start_c, 1, start_time_attempt):
                time_end_attempt = time.time()
                elapsed_time_attempt = time_end_attempt - start_time_attempt
                attempt_times[(start_r, start_c)] = elapsed_time_attempt
                solution_found = True
                break  # Ferma alla prima soluzione trovata
            else:
                time_end_attempt = time.time()
                elapsed_time_attempt = time_end_attempt - start_time_attempt
                attempt_times[(start_r, start_c)] = elapsed_time_attempt

        if solution_found:
            break

    end_time_total = time.time()
    elapsed_time_total = end_time_total - start_time_total

    clear_output()
    if solution_found:
        print("Soluzione trovata:")
        # La griglia della soluzione è già stata stampata all'interno del loop
    else:
        print(f"Nessuna soluzione trovata per una griglia {n}x{n}.")

    print("\nTempi per ogni tentativo:")
    for (r, c), time_taken in attempt_times.items():
        print(f"Partenza da ({r}, {c}): {format_time(time_taken)}")

    print(f"\nTempo totale di esecuzione: {format_time(elapsed_time_total)}")

if __name__ == "__main__":
    dimensione_griglia = int(input("Inserisci la dimensione della griglia (es. 3 o 4): "))
    solve_grid_filling(dimensione_griglia)