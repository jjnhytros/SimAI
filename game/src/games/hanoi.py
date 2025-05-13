import time
import os
import json

# Funzione per pulire l'output del terminale
def clear_output():
    """Pulisce l'output del terminale."""
    os.system('cls' if os.name == 'nt' else 'clear')

# Funzione per disegnare lo stato attuale delle torri
def draw_towers(disks, tower_a, tower_b, tower_c):
    """Disegna lo stato attuale delle torri."""
    max_height = disks
    for i in range(max_height - 1, -1, -1):
        a_disk = tower_a[i] if i < len(tower_a) else 0
        b_disk = tower_b[i] if i < len(tower_b) else 0
        c_disk = tower_c[i] if i < len(tower_c) else 0
        print(f"{' ' * (disks - a_disk)}{'-' * (2 * a_disk + 1)}{' ' * (disks - a_disk)}   "
              f"{' ' * (disks - b_disk)}{'-' * (2 * b_disk + 1)}{' ' * (disks - b_disk)}   "
              f"{' ' * (disks - c_disk)}{'-' * (2 * c_disk + 1)}{' ' * (disks - c_disk)}")
    print(" A ".center(2 * disks + 1), " B ".center(2 * disks + 1), " C ".center(2 * disks + 1))
    print("-" * (6 * disks + 9))

# Funzione per risolvere le Torri di Hanoi con simulazione
def hanoi(n, source, destination, auxiliary, towers, move_count, mode):
    """
    Risolve il problema delle Torri di Hanoi con simulazione.
    
    Args:
        n (int): Il numero di dischi da spostare.
        source (str): Il nome della torre sorgente ('A', 'B', o 'C').
        destination (str): Il nome della torre destinazione ('A', 'B', o 'C').
        auxiliary (str): Il nome della torre ausiliaria ('A', 'B', o 'C').
        towers (dict): Dizionario che rappresenta lo stato delle torri.
        move_count (list): Lista per tenere traccia del numero di mosse.
        mode (str): Modalità di gioco ("Normal" o "Fast").
    """
    if n == 1:
        disk = towers[source].pop()
        towers[destination].append(disk)
        move_count[0] += 1
        clear_output()
        print(f"Mossa {move_count[0]}: Sposta il disco {disk} da {source} a {destination}")
        draw_towers(len(towers['A']) + len(towers['B']) + len(towers['C']), towers['A'], towers['B'], towers['C'])
        time.sleep(0.2)
        return

    hanoi(n - 1, source, auxiliary, destination, towers, move_count, mode)

    disk = towers[source].pop()
    towers[destination].append(disk)
    move_count[0] += 1
    clear_output()
    print(f"Mossa {move_count[0]}: Sposta il disco {disk} da {source} a {destination}")
    draw_towers(len(towers['A']) + len(towers['B']) + len(towers['C']), towers['A'], towers['B'], towers['C'])
    time.sleep(0.2)

    hanoi(n - 1, auxiliary, destination, source, towers, move_count, mode)

# Funzione per chiedere se si desidera procedere con un numero maggiore di dischi
def ask_for_next_mode_and_disks():
    response = input("Vuoi passare al numero di dischi successivo (y/n)? ").strip().lower()
    if response == 'y' or response == '':
        return True
    return False

# Funzione principale
def main():
    statistics = {}
    
    # Carica le statistiche precedenti, se esistono
    if os.path.exists("hanoi_stats.json"):
        with open("hanoi_stats.json", "r") as f:
            statistics = json.load(f)

    while True:
        mode = input("Scegli la modalità (Normal/Fast): ").strip()
        num_disks = int(input("Inserisci il numero di dischi: "))
        
        # Verifica le statistiche per il numero di dischi scelto
        if str(num_disks) in statistics and mode in statistics[str(num_disks)]:
            print(f"Statistiche già presenti per {mode} con {num_disks} dischi.")
            print(f"Tempo: {statistics[str(num_disks)][mode]['time']} s, Mosse: {statistics[str(num_disks)][mode]['moves']}")
        else:
            # Inizializza le torri
            towers = {
                'A': list(range(num_disks, 0, -1)),
                'B': [],
                'C': []
            }
            move_count = [0]
            
            # Avvia il timer
            start_time = time.time()
            
            print(f"Completamento delle Torri di Hanoi con {num_disks} dischi in modalità {mode}...")
            hanoi(num_disks, 'A', 'C', 'B', towers, move_count, mode)
            
            end_time = time.time()
            elapsed_time = end_time - start_time
            
            # Aggiorna le statistiche
            if str(num_disks) not in statistics:
                statistics[str(num_disks)] = {}
            
            statistics[str(num_disks)][mode] = {
                'moves': move_count[0],
                'time': round(elapsed_time, 2)
            }

            # Salva le statistiche su file
            with open("hanoi_stats.json", "w") as f:
                json.dump(statistics, f, indent=4)
            
            # Mostra le statistiche
            print(f"\nNumero di mosse: {move_count[0]}")
            print(f"Tempo di esecuzione: {round(elapsed_time, 2)} secondi")
            
            # Chiedi se proseguire con un numero maggiore di dischi
            if not ask_for_next_mode_and_disks():
                break

if __name__ == "__main__":
    main()
