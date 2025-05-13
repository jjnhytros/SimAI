import time

def is_safe(x, y, n, board):
    """Verifica se una casella (x, y) è valida all'interno di una griglia nxn e non ancora visitata."""
    return 0 <= x < n and 0 <= y < n and board[x][y] == -1

def solve_knight_tour(n):
    """Risolve il problema del tour del cavallo su una griglia nxn e misura il tempo."""
    start_time = time.time()
    board = [[-1 for _ in range(n)] for _ in range(n)]
    move_x = [2, 1, -1, -2, -2, -1, 1, 2]
    move_y = [1, 2, 2, 1, -1, -2, -2, -1]
    found_tour = False

    def find_tour(x, y, move_count):
        """Funzione ricorsiva per trovare il tour."""
        board[x][y] = move_count

        if move_count == n * n:
            return True

        for i in range(8):
            next_x = x + move_x[i]
            next_y = y + move_y[i]

            if is_safe(next_x, next_y, n, board):
                if find_tour(next_x, next_y, move_count + 1):
                    return True

        # Backtrack: se non si trova un percorso valido da questa casella, resetta e torna indietro
        board[x][y] = -1
        return False

    # Prova a partire da ogni casella della griglia
    for start_x in range(n):
        for start_y in range(n):
            # Inizializza la scacchiera per ogni tentativo
            board = [[-1 for _ in range(n)] for _ in range(n)]
            if find_tour(start_x, start_y, 1):
                end_time = time.time()
                elapsed_time = end_time - start_time
                days = int(elapsed_time // 86400)
                elapsed_time %= 86400
                hours = int(elapsed_time // 3600)
                elapsed_time %= 3600
                minutes = int(elapsed_time // 60)
                seconds = int(elapsed_time % 60)

                print(f"Tour trovato per una griglia {n}x{n} partendo dalla casella ({start_x}, {start_y}):")
                for row in board:
                    print(row)
                print(f"Tempo di soluzione: {days} giorni, {hours}:{minutes:02d}:{seconds:02d}")
                return True  # Trovata una soluzione, possiamo fermarci
            found_tour = True # Imposta a True anche se non si trova subito, per il messaggio finale

    if found_tour:
        end_time = time.time()
        elapsed_time = end_time - start_time
        days = int(elapsed_time // 84600)
        elapsed_time %= 84600
        hours = int(elapsed_time // 3600)
        elapsed_time %= 3600
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        print(f"Nessun tour completo trovato per una griglia {n}x{n}.")
        print(f"Tempo totale di ricerca: {days} giorni, {hours}:{minutes:02d}:{seconds:02d}")
    else:
        print(f"Nessun tour trovato per una griglia {n}x{n}.")

if __name__ == "__main__":
    dimensione_griglia = int(input("Inserisci la dimensione della griglia (es. 5 per una 5x5): "))
    solve_knight_tour(dimensione_griglia)