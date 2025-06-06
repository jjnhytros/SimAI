# generate_version.py
"""
Script per calcolare e aggiornare automaticamente la versione del progetto SimAI.

Legge un file TODO, conta lo stato dei task, genera una nuova stringa di versione
e aggiorna sia il file TODO che il file settings.py.
"""
import os
import re
import argparse
from datetime import datetime

# Dizionario per tradurre i mesi in italiano, come da richiesta
MESI_ITALIANI = {
    1: "Gennaio", 2: "Febbraio", 3: "Marzo", 4: "Aprile",
    5: "Maggio", 6: "Giugno", 7: "Luglio", 8: "Agosto",
    9: "Settembre", 10: "Ottobre", 11: "Novembre", 12: "Dicembre"
}

DEFAULT_TODO_FILE_PATH = "TODO_Generale.md" # Nome del file TODO hardcodato

def count_tasks_in_file(file_path: str) -> tuple[int, int, int]:
    """
    Conta i task [x], [P], e [ ] in un file, ignorando la legenda iniziale
    e cercando i marker in qualsiasi punto della riga dopo la legenda.
    """
    x_count = 0
    p_count = 0
    empty_count = 0

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Errore: File non trovato a '{file_path}'")
        exit(1)

    content_started = False
    legend_marker_found = False
    for line_number, line in enumerate(lines):
        if line.strip() == '---':
            if not legend_marker_found:
                legend_marker_found = True
            content_started = True
            continue 
        
        if not content_started:
            continue
        
        # Ora cerchiamo i marker esatti all'interno della riga
        # Questo è più flessibile di startswith()
        # Assicurati che il formato nel tuo TODO sia esattamente '`[x]` ' (con spazio dopo)
        # o adattalo se necessario. Per ora, cerco il marker esatto con backtick.
        
        # Per evitare di contare più volte un marker se appare più volte in una riga
        # (improbabile per i task, ma per sicurezza), o di contare un marker
        # all'interno di un altro (es. [P] dentro una descrizione),
        # usiamo re.search per trovare la prima occorrenza e contiamo solo quella.
        # Una logica più semplice è cercare la sottostringa, che dovrebbe essere sufficiente
        # se i marker sono usati solo per indicare lo stato dei task.

        # Modifichiamo per cercare la stringa esatta, che include i backtick.
        # Il conteggio si basa sulla prima occorrenza trovata per evitare doppi conteggi
        # se una riga contenesse per errore più marker validi (molto improbabile).
        
        # Per evitare di contare un marker all'interno di un altro (es. se un task `[]` avesse
        # la descrizione "Implementare `[P]`"), cerchiamo specificamente il marker seguito da uno spazio
        # o che sia il pattern completo.
        # Una regex semplice potrebbe essere più robusta, ma proviamo con 'in' e controlli.

        line_to_check = line.strip() # Lavoriamo sulla riga trimmata

        # Per evitare doppi conteggi se una riga ha, per esempio, sia `[x]` che `[P]`
        # (improbabile per un singolo task), diamo priorità a `[x]`, poi `[P]`, poi `[]`.
        if '`[x]`' in line_to_check: # Cerchiamo la sottostringa esatta
            x_count += 1
        elif '`[P]`' in line_to_check: # Solo se non è stato trovato [x]
            p_count += 1
        elif '`[ ]`' in line_to_check:  # Solo se non sono stati trovati [x] o [P]
            empty_count += 1
            
    return x_count, p_count, empty_count

def update_todo_file(file_path: str, new_version: str):
    """
    Aggiorna la prima e la seconda riga del file TODO.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Formatta la data e l'ora correnti
    now = datetime.now()
    # Esempio: "02 Giugno 2025 12:40:32"
    timestamp = f"{now.day:02d} {MESI_ITALIANI[now.month]} {now.year} {now.strftime('%H:%M:%S')}"

    # Aggiorna le prime due righe
    lines[0] = f"# SimAI v{new_version}\n"
    lines[1] = f"# TODO List Generale (Aggiornato al {timestamp})\n"

    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"✅ File TODO '{file_path}' aggiornato con la nuova versione e timestamp.")

def update_settings_file(settings_path: str, new_version: str):
    """
    Aggiorna la variabile GAME_VERSION nel file settings.py.
    """
    if not os.path.exists(settings_path):
        print(f"⚠️ Attenzione: File settings non trovato a '{settings_path}'. Saltando l'aggiornamento.")
        return

    with open(settings_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    updated_lines = []
    found = False
    for line in lines:
        # Usa una regex per trovare e sostituire la riga della versione
        if re.match(r'^\s*GAME_VERSION\s*=\s*".*"', line):
            updated_lines.append(f'GAME_VERSION = "{new_version}"\n')
            found = True
        else:
            updated_lines.append(line)

    if not found:
        print(f"⚠️ Attenzione: Variabile GAME_VERSION non trovata in '{settings_path}'. Saltando l'aggiornamento.")
        return

    with open(settings_path, 'w', encoding='utf-8') as f:
        f.writelines(updated_lines)

    print(f"✅ File settings '{settings_path}' aggiornato con la nuova versione.")


def main():
    """Funzione principale dello script."""
    todo_path = DEFAULT_TODO_FILE_PATH # Nome file hardcodato

    if not os.path.exists(todo_path):
        print(f"Errore: Il file TODO '{todo_path}' non esiste. Controlla il percorso.")
        print("Lo script si aspetta di essere eseguito dalla directory principale del progetto.")
        exit(1)

    print(f"Analizzando il file: {todo_path}...")

    x_tasks, p_tasks, empty_tasks = count_tasks_in_file(todo_path)
    print("\n--- Conteggio Task Trovati ---")
    print(f"  Completati   [x]: {x_tasks}")
    print(f"  In corso     [P]: {p_tasks}")
    print(f"  Da iniziare   []: {empty_tasks}")
    print("----------------------------\n")

    major = 0 # Major version rimane 0 per ora
    
    # --- LOGICA DINAMICA PER LA MINOR VERSION ---
    # Definisci le tue soglie qui. Queste sono solo un esempio.
    # Le condizioni vengono valutate in ordine, quindi la prima che risulta vera determina la minor version.
    # È importante che le soglie siano crescenti e mutualmente esclusive nel modo in cui sono scritte.
    
    minor = 0 # Default se nessuna soglia viene raggiunta (progetto appena iniziato)
    if x_tasks >= 50 and p_tasks >= 100: # Traguardo molto avanzato
        minor = 5 
    elif x_tasks >= 40 and p_tasks >= 80: # Traguardo avanzato
        minor = 4
    elif x_tasks >= 30 and p_tasks >= 50: # Traguardo significativo (come la nostra attuale stima)
        minor = 3
    elif x_tasks >= 15 and p_tasks >= 30: # Sistemi core più robusti
        minor = 2
    elif x_tasks >= 5 and p_tasks >= 10:  # Fondamenta base gettate
        minor = 1
    # Se nessuna delle condizioni sopra è vera, minor rimane 0.
    # --- FINE LOGICA DINAMICA PER MINOR VERSION ---
    
    release = p_tasks # 'release' è il numero di task [P]
    alpha_value = (x_tasks * 2) + p_tasks # Alpha value come da tua formula
    
    new_version_string = f"{major}.{minor}.{release}-alpha_{alpha_value}"
    
    print(f"Nuova Versione Calcolata: {new_version_string}\n")
    
    settings_file_path = os.path.join('core', 'settings.py') 
    
    update_todo_file(todo_path, new_version_string)
    update_settings_file(settings_file_path, new_version_string)

    print("\nScript completato.")

if __name__ == "__main__":
    main()
