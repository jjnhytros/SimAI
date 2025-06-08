import re
import os
import argparse

def count_markers(file_path):
    """Conta i marker nel file, gestendo correttamente la legenda"""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        
        # Conta tutte le occorrenze dei marker rilevanti
        markers = {
            'x': len(re.findall(r'\[x\]', content, re.IGNORECASE)),
            'P': len(re.findall(r'\[P\]', content, re.IGNORECASE)),
            ' ': len(re.findall(r'\[\s\]', content, re.IGNORECASE)) + 
                 len(re.findall(r'\[\_\]', content, re.IGNORECASE)),  # Considera [ ] e [_]
            '@': len(re.findall(r'\[@\]', content, re.IGNORECASE)),
        }
        
        # Cerca la presenza di una legenda
        has_legenda = bool(re.search(r'#+\s*Legenda:', content, re.IGNORECASE))
        
        # Sottrai 1 per ogni tipo di marker se è presente una legenda
        if has_legenda:
            for marker in markers:
                markers[marker] = max(0, markers[marker] - 1)
        
        return markers

def calculate_versions(roadmap_path, general_path):
    # Conteggio marker
    roadmap = count_markers(roadmap_path)
    generale = count_markers(general_path)
    
    # Calcolo totali per la versione ufficiale
    ufficiale_completed = generale['x']
    ufficiale_partial = generale['P'] + generale['@']  # [P] e [@] sono considerati parziali
    ufficiale_total = ufficiale_completed + ufficiale_partial + generale[' ']
    
    # Calcolo totali per la versione starter
    starter_total = roadmap['x'] + roadmap['P'] + roadmap['@'] + roadmap[' ']
    starter_completed = roadmap['x']
    
    # Calcolo punti aggiuntivi oltre lo Starter
    additional_completed = max(0, ufficiale_completed - starter_completed)
    
    # 1. Versione STARTER
    if starter_completed == starter_total:
        starter_version = "1.0.0-starter"
    else:
        starter_version = f"0.{starter_completed}.0"
    
    # 2. Versione UFFICIALE con stato sviluppo
    # Calcolo progresso generale
    if ufficiale_total > 0:
        progress_percent = (ufficiale_completed + ufficiale_partial * 0.5) / ufficiale_total
    else:
        progress_percent = 0
    
    # Determinazione stato sviluppo
    if progress_percent >= 0.75:
        # Calcola numero di RC basato su punti mancanti
        remaining_points = ufficiale_total - (ufficiale_completed + ufficiale_partial)
        rc_number = min(5, (remaining_points // 100) + 1) if remaining_points > 0 else 1
        stage = f"rc{rc_number}"
    elif progress_percent >= 0.50:
        stage = f"beta.{starter_completed}"
    elif progress_percent >= 0.25:
        stage = f"alpha.{starter_completed}"
    else:
        stage = "pre-alpha"
    
    ufficiale_version = f"1.0.0-{stage}" if stage != "stable" else "1.0.0"
    
    # 3. Versione RELEASE
    release_version = "Non ancora pronta"
    if starter_completed == starter_total:
        release_version = "1.0.0-starter"
        if ufficiale_completed >= 79 and ufficiale_partial >= 116:
            release_version = "1.0.0"
    
    return {
        'starter': starter_version,
        'ufficiale': ufficiale_version,
        'release': release_version,
        'stats': {
            'roadmap': roadmap,
            'generale': generale
        },
        'totals': {
            'starter_completed': starter_completed,
            'starter_total': starter_total,
            'ufficiale_completed': ufficiale_completed,
            'ufficiale_partial': ufficiale_partial,
            'ufficiale_incomplete': generale[' '],
            'ufficiale_total': ufficiale_total
        }
    }

def main():
    parser = argparse.ArgumentParser(description='Generatore di versioni per progetto')
    parser.add_argument('--roadmap', default='TODO_Roadmap_v1.0.md', help='Percorso file roadmap')
    parser.add_argument('--generale', default='TODO_Generale.md', help='Percorso file generale')
    args = parser.parse_args()
    
    try:
        if not os.path.exists(args.roadmap):
            raise FileNotFoundError(f"File roadmap non trovato: {args.roadmap}")
        if not os.path.exists(args.generale):
            raise FileNotFoundError(f"File generale non trovato: {args.generale}")
            
        versions = calculate_versions(args.roadmap, args.generale)
    except FileNotFoundError as e:
        print(f"ERRORE: {str(e)}")
        print("Assicurati che i file esistano e che i percorsi siano corretti.")
        return
    except Exception as e:
        print(f"Errore durante l'elaborazione: {str(e)}")
        return
    
    # Stampa risultati
    print("\n" + "="*70)
    print(f"STARTER VERSION:    {versions['starter']}")
    print(f"UFFICIALE VERSION:  {versions['ufficiale']}")
    print(f"RELEASE VERSION:    {versions['release']}")
    print("="*70)
    
    # Statistiche dettagliate
    stats = versions['stats']
    totals = versions['totals']
    
    # Calcolo percentuali
    if totals['starter_total'] > 0:
        starter_percent = totals['starter_completed'] / totals['starter_total'] * 100
    else:
        starter_percent = 0
        
    if totals['ufficiale_total'] > 0:
        ufficiale_percent = (totals['ufficiale_completed'] + totals['ufficiale_partial'] * 0.5) / totals['ufficiale_total'] * 100
    else:
        ufficiale_percent = 0
    
    print("\n🚀 ROADMAP (1.0 STARTER):")
    print(f"• Completati [x]: {totals['starter_completed']}/{totals['starter_total']} ({starter_percent:.1f}%)")
    print(f"• Parziali [P]: {stats['roadmap']['P']} | [@]: {stats['roadmap']['@']} (da revisionare)")
    print(f"• Non iniziati [ ]: {stats['roadmap'][' ']}")
    
    print("\n🌍 GENERALE (1.0 UFFICIALE):")
    print(f"• Completati [x]: {totals['ufficiale_completed']}")
    print(f"• Parziali [P]: {stats['generale']['P']} | [@]: {stats['generale']['@']} (da revisionare)")
    print(f"• Non iniziati [ ]: {totals['ufficiale_incomplete']}")
    print(f"• Progresso complessivo: {ufficiale_percent:.1f}%")
    print("="*70)

if __name__ == "__main__":
    main()