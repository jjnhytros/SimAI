# core/utils/name_generator.py
"""
Funzioni di utilità per la generazione procedurale di nomi.
"""
import random
from core import settings
from core.config import npc_config # Importa la configurazione degli NPC

def gen_lastname():
    """
    Genera un cognome casuale combinando un prefisso e un suffisso,
    seguendo regole fonetiche specifiche.
    """
    prefixes = npc_config.LASTNAME_PREFIXES
    suffixes = npc_config.LASTNAME_SUFFIXES
    VOWELS = "aeiouàèéìòù"

    if not prefixes or not suffixes:
        return "CognomeDefault"

    # Aggiungiamo un meccanismo di tentativi per evitare loop infiniti
    # se un prefisso sfortunato non trovasse suffissi compatibili.
    max_retries = 24 
    for _ in range(max_retries):
        prefix = random.choice(prefixes)
        prefix_lower = prefix.lower()
        
        valid_suffixes = []
        prefix_to_use = prefix # Il prefisso da usare per la combinazione finale

        # --- APPLICAZIONE REGOLE ---

        # Regola per 'ch' e 'gh'
        if prefix_lower.endswith(('ch', 'gh')):
            # Scegli casualmente una delle due sotto-regole
            if random.random() < 0.5:
                # Sotto-regola A: Mantieni la 'h', il suffisso deve iniziare per 'e' o 'i'.
                valid_suffixes = [s for s in suffixes if s.lower().startswith(('e', 'i'))]
            else:
                # Sotto-regola B: Rimuovi la 'h' finale, il suffisso deve iniziare con una qualsiasi vocale.
                prefix_to_use = prefix[:-1] # Rimuove l'ultimo carattere ('h')
                valid_suffixes = [s for s in suffixes if s.lower().startswith(tuple(VOWELS))]
        
        # Regola per tutte le altre consonanti finali
        elif prefix_lower[-1] not in VOWELS:
            # Se il prefisso finisce per consonante (doppia o singola), il suffisso deve iniziare per vocale.
            valid_suffixes = [s for s in suffixes if s.lower().startswith(tuple(VOWELS))]
        
        # Se il prefisso termina con una vocale
        else:
            # Nessun filtro richiesto, tutti i suffissi sono potenzialmente validi
            valid_suffixes = suffixes

        # Se abbiamo trovato almeno un suffisso valido per il nostro prefisso
        if valid_suffixes:
            suffix = random.choice(valid_suffixes)
            
            # Regola finale: Fusione delle vocali identiche
            prefix_to_use_lower = prefix_to_use.lower()
            if prefix_to_use_lower[-1] in VOWELS and suffix.lower().startswith(prefix_to_use_lower[-1]):
                # Se l'ultima vocale del prefisso è uguale alla prima del suffisso, ne eliminiamo una.
                return prefix_to_use.capitalize() + suffix[1:]
            else:
                # Altrimenti, li uniamo semplicemente
                return prefix_to_use.capitalize() + suffix
    
    # Fallback se dopo N tentativi non si è trovata una combinazione valida
    if settings.DEBUG_MODE:
        print("[gen_lastname WARN] Non è stato possibile generare un cognome valido dopo diversi tentativi. Uso il fallback.")
    return "Rossi"