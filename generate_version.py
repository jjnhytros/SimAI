# simai/generate_version.py
import re
import os
import argparse
from collections import defaultdict

def count_markers(file_path):
    """Conta i marker nel file, gestendo correttamente la legenda"""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        
        # Conta tutte le occorrenze dei marker rilevanti
        markers = {
            'x': len(re.findall(r'\[x\]', content, re.IGNORECASE)),
            'P': len(re.findall(r'\[P\]', content, re.IGNORECASE)),
            ' ': len(re.findall(r'\[\s\]', content, re.IGNORECASE)),
            '@': len(re.findall(r'\[@\]', content, re.IGNORECASE)),
            'version_tags': re.findall(r'\[\s*v?(\d+\.\d+\.\d+)\s*\]', content)
        }
        
        # Cerca la presenza di una legenda
        has_legenda = len(re.findall(r'#+\s*Legenda:', content, re.IGNORECASE)) > 0
        
        # Sottrai 1 per ogni tipo di marker se è presente una legenda
        if has_legenda:
            for marker in ['x', 'P', ' ', '@']:
                markers[marker] = max(0, markers[marker] - 1)
        
        return markers

def extract_version_tasks(content):
    """
    Estrae i task per ogni versione o categoria (DLC, FUTURO),
    usando i tag nelle intestazioni per determinare il contesto.
    """
    version_tasks = defaultdict(lambda: defaultdict(int))
    current_section = "1.0.0"  # Sezione di default

    for line in content.split('\n'):
        # Cerca i tag di sezione nelle intestazioni o a fine riga
        version_match = re.search(r'\[\s*v?(\d+\.\d+\.\d+)\s*\]', line)
        dlc_match = re.search(r'\[DLC\]', line, re.IGNORECASE)
        future_match = re.search(r'\[FUTURO\]', line, re.IGNORECASE)

        # Aggiorna la sezione corrente se viene trovato un tag
        if version_match:
            current_section = version_match.group(1)
        elif dlc_match:
            current_section = 'DLC'
        elif future_match:
            current_section = 'FUTURO'
        
        # Conta i marker solo sulle righe che sono effettivamente dei task
        if line.strip().startswith(('*', '-', '`[', '[')):
            if re.search(r'\[x\]', line, re.IGNORECASE):
                version_tasks[current_section]['x'] += 1
            elif re.search(r'\[P\]', line, re.IGNORECASE):
                version_tasks[current_section]['P'] += 1
            elif re.search(r'\[@\]', line, re.IGNORECASE):
                version_tasks[current_section]['@'] += 1
            elif re.search(r'\[\s\]', line, re.IGNORECASE) or re.search(r'\[\_\]', line, re.IGNORECASE):
                version_tasks[current_section][' '] += 1
                
    return version_tasks

def calculate_versions(roadmap_path, general_path, target_version):
    roadmap = count_markers(roadmap_path)
    
    with open(general_path, 'r', encoding='utf-8') as file:
        generale_content = file.read()
        generale = count_markers(general_path)
        version_tasks, global_counts = extract_version_tasks(generale_content)
    
    target_tasks = version_tasks.get(target_version, defaultdict(int))
    
    target_completed = target_tasks['x']
    target_partial = target_tasks['P'] + target_tasks['@']
    target_incomplete = target_tasks[' ']
    target_total = target_completed + target_partial + target_incomplete
    
    starter_completed = roadmap['x']
    starter_total = roadmap['x'] + roadmap['P'] + roadmap['@'] + roadmap[' ']
    
    starter_version = "1.0.0-starter" if starter_completed == starter_total else f"0.{starter_completed}.0"
    
    if target_total > 0:
        progress_percent = (target_completed + target_partial * 0.5) / target_total
    else:
        progress_percent = 0
    
    # Determinazione stato sviluppo
    if progress_percent < 0.25:
        stage = f"pre-alpha-b{starter_completed}_{target_total}_{target_completed}_{target_partial}"
    elif progress_percent < 0.50:
        stage = f"alpha.{starter_completed}"
    elif progress_percent < 0.75:
        stage = f"beta.{starter_completed}"
    elif progress_percent < 1.0:
        remaining_points = target_total - (target_completed + target_partial)
        rc_number = min(5, (remaining_points // 10) + 1) if remaining_points > 0 else 1
        stage = f"rc{rc_number}"
    else:
        stage = "stable"
    
    target_version_str = f"{target_version}-{stage}" if stage != "stable" else target_version
    
    release_version = "Non ancora pronta"
    if starter_completed == starter_total and target_completed == target_total and target_version == "1.0.0":
        release_version = "1.0.0"

    return {
        'starter': starter_version,
        'target': target_version_str,
        'release': release_version,
        'stats': {
            'roadmap': roadmap,
            'all_tasks': version_tasks, # Rinomino per chiarezza
        },
        'totals': {
            'starter_completed': starter_completed,
            'starter_total': starter_total,
            'target_completed': target_completed,
            'target_partial': target_partial,
            'target_incomplete': target_incomplete,
            'target_total': target_total,
        }
    }

def main():
    parser = argparse.ArgumentParser(description='Generatore di versioni per progetto')
    parser.add_argument('--roadmap', default='TODO_Roadmap_v1.0.md', help='Percorso file roadmap')
    parser.add_argument('--generale', default='TODO_Generale_06-2025.md', help='Percorso file generale')
    parser.add_argument('--target', default='1.0.0', help='Versione target (es. 1.0.1, 1.1.0)')
    args = parser.parse_args()
    
    try:
        if not os.path.exists(args.roadmap):
            raise FileNotFoundError(f"File roadmap non trovato: {args.roadmap}")
        if not os.path.exists(args.generale):
            raise FileNotFoundError(f"File generale non trovato: {args.generale}")
            
        versions = calculate_versions(args.roadmap, args.generale, args.target)
    except FileNotFoundError as e:
        print(f"ERRORE: {str(e)}")
        print("Assicurati che i file esistano e che i percorsi siano corretti.")
        return
    except Exception as e:
        print(f"Errore durante l'elaborazione: {str(e)}")
        return
    
    # --- LOGICA DI STAMPA AGGIORNATA ---
    stats = versions['stats']
    totals = versions['totals']

    # Separa le categorie speciali (DLC, FUTURO) dalle versioni numeriche
    all_tasks = stats['all_tasks']
    dlc_tasks = all_tasks.pop('DLC', defaultdict(int))
    future_tasks = all_tasks.pop('FUTURO', defaultdict(int))
    numerical_versions = all_tasks # Ciò che rimane sono le versioni numeriche

    # Calcola i totali globali per le categorie speciali
    total_dlc_tasks = sum(dlc_tasks.values())
    total_future_tasks = sum(future_tasks.values())
    
    print("\n" + "="*70)
    print(f"🚀 STARTER VERSION:  {versions['starter']}")
    print(f"🎯 TARGET VERSION:   {versions['target']}")
    print(f"✅ RELEASE STATUS:   {versions['release']}")
    print(f"🌌 FUTURE TASKS:     {total_future_tasks}")
    print(f"📦 DLC TASKS:        {total_dlc_tasks}")
    print("="*70)
    
    # Calcolo percentuali
    starter_percent = totals['starter_completed'] / totals['starter_total'] * 100 if totals['starter_total'] > 0 else 0
    
    if totals['target_total'] > 0:
        target_percent = (totals['target_completed'] + totals['target_partial'] * 0.5) / totals['target_total'] * 100
    else:
        target_percent = 0
    
    print("\n🚀 ROADMAP (1.0 STARTER):")
    print(f"• Completati [x]: {totals['starter_completed']}/{totals['starter_total']} ({starter_percent:.1f}%)")
    print(f"• Parziali [P]: {stats['roadmap']['P']} | [@]: {stats['roadmap']['@']} (da revisionare)")
    print(f"• Non iniziati [ ]: {stats['roadmap'][' ']}")
    
    print(f"\n🎯 TARGET VERSION ({args.target}):")
    print(f"• Completati [x]: {totals['target_completed']}")
    print(f"• Parziali [P]: {stats['target'].get('P', 0)} | [@]: {stats['target'].get('@', 0)} (da revisionare)")
    print(f"• Non iniziati [ ]: {totals['target_incomplete']}")
    print(f"• Progresso: {target_percent:.1f}%")
    
    # Stampa il breakdown delle versioni numeriche
    print("\n📊 ROADMAP DI SVILUPPO (Versioni):")
    version_keys = list(numerical_versions.keys())
    sorted_version_keys = sorted(version_keys, key=lambda v: tuple(map(int, v.split('.'))))
    
    for ver in sorted_version_keys:
        tasks = numerical_versions[ver]
        total = sum(tasks.values())
        if total > 0:
            completed = tasks.get('x', 0)
            print(f"• {ver}: {completed}/{total} completati ({completed/total*100:.1f}%)")
    
    # Stampa un riepilogo per le categorie speciali
    print("\n" + "-"*30)
    print("🗓️ CATEGORIE SPECIALI:")
    if total_dlc_tasks > 0:
        print(f"• [DLC]: {total_dlc_tasks} task totali ([x]:{dlc_tasks.get('x', 0)}, [P]:{dlc_tasks.get('P', 0)}, [ ]:{dlc_tasks.get(' ', 0)})")
    if total_future_tasks > 0:
        print(f"• [FUTURO]: {total_future_tasks} task totali ([x]:{future_tasks.get('x', 0)}, [P]:{future_tasks.get('P', 0)}, [ ]:{future_tasks.get(' ', 0)})")
        
    print("="*70)

if __name__ == "__main__":
    main()