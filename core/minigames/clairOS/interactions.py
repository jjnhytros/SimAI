# simai/core/minigames/clairOS/interactions.py
from .behavior import handle_sensitive_zones_effect
import random
from .constants import INTERACTION_SETS

def user_interaction() -> str:
    """Gestisce l'interazione con l'utente"""
    chosen_set = random.choice(INTERACTION_SETS)  # Accedi alla costante dal modulo constants
    print("Cosa scegli di fare?")
    
    for i, option in enumerate(chosen_set):
        print(f"[{i+1}] {option['prompt']}")
    
    while True:
        try:
            choice_num = int(input("Scelta (1, 2, o 3): "))
            if 1 <= choice_num <= 3:
                return chosen_set[choice_num - 1]['tag']
            print("Scelta non valida.")
        except ValueError:
            print("Input non valido.")

def perform_action_by_tag(tag):
    if tag == "share_creative_input":
        response = ("Claire sorride e condivide una sua creazione.")
    elif tag == "discuss_obsession":
        response = ("Claire parla di un'ossessione di cui è appassionata.")
    elif tag == "secret":
        response = ("Claire rivela un suo segreto personale.")
    elif tag == "sensitive_zones":
        response = handle_sensitive_zones_effect()
    else:
        response = "Azione non riconosciuta."
    return response
