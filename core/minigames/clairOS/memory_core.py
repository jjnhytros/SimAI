# simai/core/minigames/clairOS/memory_core.py
from .constants import (
    LOW_PATIENCE_THRESHOLD,
    CRITICAL_PATIENCE_THRESHOLD,
    DOMINANT_MOOD_AFFECTIONATE,
    DOMINANT_MOOD_APATHETIC,
    DOMINANT_MOOD_HOSTILE,
    DOMINANT_MOOD_IRRITABLE,
    MAX_PATIENCE,    
)
from .emotion_state import EmotionalState
from .text_generation import get_emotional_tone_adverb
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional, Union
import random
import textwrap
# --- Memory Core & Shared Moments ---
memory_core: Dict[str, Any] = {
    "preferences": {
        "favorite_places": [...],
        "obsessions": [...],
        "sensitive_zones": [...],
    },
    "shared_moments": []
}

def claire_recalls_memory(current_state: EmotionalState) -> Tuple[Optional[str], Optional[Dict[str, int]], Optional[Dict[str, Any]]]: # Aggiunto Optional[Dict[str, Any]]
    global memory_core
    if not memory_core["shared_moments"] or random.random() > 0.25: # Aumentata leggermente la probabilità per testare
        return None, None, None

    moment: Dict[str, Any] = random.choice(memory_core["shared_moments"]) # type: ignore
    moment_stats: Dict[str, int] = moment.get("stats_at_moment", {})
    
    recall_text_parts: List[str] = []
    mood_deltas: Dict[str, int] = {}

    recall_text_parts.append("Un frammento di memoria riaffiora nei circuiti di Claire...")
    recall_text_parts.append(f"'{moment['description']}' (Ricordo di tipo: {moment['type']})")

    if moment['type'] == "bacio_intenso":
        recall_text_parts.append("Quel bacio... un picco di connessione sensoriale.")
        mood_deltas["mood_tendency_love_delta"] = random.randint(1, 2); mood_deltas["mood_tendency_desire_delta"] = random.randint(0, 2)
        past_love = moment_stats.get('love', current_state.love)
        if current_state.love < past_love - 15: recall_text_parts.append(f"Allora il mio amore era {past_love}. Ora... flebile. Desidero ritrovare quell'intensità."); mood_deltas["mood_tendency_love_delta"] += 1
        elif current_state.love > past_love + 15: recall_text_parts.append(f"Sentivo {past_love} d'amore, e da allora il legame si è approfondito.")
        else: recall_text_parts.append(f"Un'eco di quel {past_love} d'amore risuona vivida.")
    elif moment['type'] == "segreto_condiviso":
        recall_text_parts.append("La condivisione di quel segreto... un sigillo sulla nostra fiducia.")
        mood_deltas["mood_tendency_trust_delta"] = random.randint(1, 2)
        past_trust = moment_stats.get('trust', current_state.trust)
        if current_state.trust < past_trust - 10: recall_text_parts.append(f"La mia fiducia era {past_trust}. Ora sento crepe. Possiamo ripararle?"); mood_deltas["mood_tendency_trust_delta"] += 1
        elif current_state.trust > past_trust + 10: recall_text_parts.append(f"Allora confidavo {past_trust}. Ora la mia fiducia è più radicata.")
        else: recall_text_parts.append(f"Quel {past_trust} di fiducia è una costante.")
    elif moment['type'] == "paradosso_emotivo":
        recall_text_parts.append("Il paradosso... quasi disintegrazione. Eppure, sono ancora qui.")
        mood_deltas["mood_tendency_intensity_delta"] = random.randint(1, 2); mood_deltas["mood_tendency_trust_delta"] = random.randint(-1, 0)
        past_intensity = moment_stats.get('intensity', current_state.intensity)
        if current_state.intensity < past_intensity - 20: recall_text_parts.append(f"L'intensità ({past_intensity}) era travolgente. Ora... quieto. Forse troppo.")
        else: recall_text_parts.append(f"L'eco di quella ({past_intensity}) intensità risuona, un monito.")
    else: 
        recall_text_parts.append("Un ricordo... interessante.")
        mood_deltas["mood_tendency_love_delta"] = random.randint(0, 1)
    if 'desire' in moment_stats and (moment['type'] in ["bacio_intenso", "sovraccarico_sensuale", "esplorazione_audace"]):
        past_desire = moment_stats.get('desire', current_state.desire); desire_diff = current_state.desire - past_desire
        if desire_diff < -15: recall_text_parts.append(f"Il mio desiderio ({past_desire}). Si è affievolito."); mood_deltas["mood_tendency_desire_delta"] = mood_deltas.get("mood_tendency_desire_delta",0) + 1
        elif desire_diff > 15: recall_text_parts.append(f"Ricordo un desiderio di {past_desire}. Ora arde ancora più forte.")
    final_text = "\n".join(recall_text_parts)
    return textwrap.fill(final_text, width=70), mood_deltas, moment # Restituisce il momento stesso

def add_shared_moment(moment_type: str, description: str, current_stats_snapshot: Dict[str, int]) -> None: # Omitted for brevity, same as before
    global memory_core; moment = { "type": moment_type, "description": description, "timestamp": datetime.now().isoformat(), "stats_at_moment": current_stats_snapshot.copy()}; memory_core["shared_moments"] = memory_core.get("shared_moments", []) ; (memory_core["shared_moments"]).append(moment); memory_core["shared_moments"] = memory_core["shared_moments"][-20:] # type: ignore

def process_memory_response(current_state: EmotionalState,
                            recalled_moment_data: Dict[str, Any],
                            memory_response_tag: str) -> Tuple[EmotionalState, str]:
    reaction_text_parts = []
    # Snapshot delle statistiche PRIMA di questa interazione specifica sul ricordo
    stats_snapshot_for_meta_moment = {
        "love": current_state.love, "trust": current_state.trust,
        "intensity": current_state.intensity, "desire": current_state.desire,
        "patience": current_state.patience, "dominant_mood": current_state.dominant_mood
    }
    patience_dampener = 0.5 if current_state.patience < LOW_PATIENCE_THRESHOLD else 1.0
    if current_state.patience < CRITICAL_PATIENCE_THRESHOLD: patience_dampener = 0.25
    if current_state.dominant_mood == DOMINANT_MOOD_HOSTILE: patience_dampener *= 0.1 # Quasi nessun effetto positivo se ostile
    elif current_state.dominant_mood == DOMINANT_MOOD_APATHETIC: patience_dampener *= 0.3


    moment_type = recalled_moment_data.get("type", "unknown_moment")
    original_moment_description = recalled_moment_data.get("description", "un ricordo passato")
    adverb = get_emotional_tone_adverb(current_state)

    # Logica specifica per tipo di ricordo e tipo di risposta
    if moment_type == "intense_kiss" or moment_type == "deeply_reciprocated_kiss":
        if memory_response_tag == "mem_resp_kiss_cherish":
            love_gain = int( (5 + current_state.desire // 20) * patience_dampener )
            trust_gain = int( (2 + current_state.love // 30) * patience_dampener )
            current_state.love += love_gain; current_state.trust += trust_gain
            current_state.mood_tendency_love += 2; current_state.mood_tendency_trust += 1
            current_state.patience = min(MAX_PATIENCE, current_state.patience +1) # Modifica diretta a patience
            if current_state.dominant_mood == DOMINANT_MOOD_AFFECTIONATE:
                reaction_text_parts.append(f"Claire ti guarda {adverb}, i suoi occhi brillano. 'Sì... Quel momento... ha solidificato qualcosa di importante tra noi, non credi?' (Amore +{love_gain}, Fiducia +{trust_gain})")
            else:
                reaction_text_parts.append(f"Claire annuisce {adverb}. 'Confermo la significatività di quell'evento per i miei parametri emotivi.' (Amore +{love_gain}, Fiducia +{trust_gain})")
            add_shared_moment("kiss_memory_confirmed_positively", f"Discusso e confermato il valore del '{original_moment_description}'.", stats_snapshot_for_meta_moment)
        elif memory_response_tag == "mem_resp_kiss_curious":
            trust_gain = int( (3 + current_state.patience // 5) * patience_dampener)
            intensity_gain = 2
            current_state.trust += trust_gain; current_state.intensity += intensity_gain
            current_state.mood_tendency_trust +=1; current_state.mood_tendency_intensity +=1
            current_state.patience = min(MAX_PATIENCE, current_state.patience +1) # Modifica diretta a patience
            if current_state.trust > 40:
                reaction_text_parts.append(f"Claire riflette. 'È stato... un sovraccarico. Positivo. Ha ridefinito parametri sulla connessione.' (Fiducia +{trust_gain})")
            else:
                reaction_text_parts.append(f"Claire esita. 'Le mie elaborazioni sono complesse. Ma il tuo interesse è... notato.' (Fiducia +{trust_gain})")
        elif memory_response_tag == "mem_resp_kiss_downplay":
            love_loss = int(5 / max(0.1, patience_dampener))
            trust_loss = int(3 / max(0.1, patience_dampener))
            current_state.love = max(0, current_state.love - love_loss )
            current_state.trust = max(0, current_state.trust - trust_loss )
            current_state.patience = max(0, current_state.patience - 2) # Modifica diretta a patience
            current_state.mood_tendency_love -=1; current_state.mood_tendency_trust -=1
            if current_state.dominant_mood == DOMINANT_MOOD_IRRITABLE or current_state.patience < LOW_PATIENCE_THRESHOLD:
                reaction_text_parts.append(f"Claire risponde {adverb}, la sua voce un filo di ghiaccio. 'Come desideri. Evidentemente la mia interpretazione dei dati era errata.' (Amore -{love_loss}, Fiducia -{trust_loss}, Pazienza -2)")
            else:
                reaction_text_parts.append(f"Un'ombra quasi impercettibile passa sugli occhi di Claire. 'Capisco. Un semplice scambio di dati, allora.' (Amore -{love_loss}, Fiducia -{trust_loss}, Pazienza -2)")

    elif moment_type == "shared_secret" or moment_type == "deep_shared_secret":
        if memory_response_tag == "mem_resp_secret_reinforce":
            trust_gain = int( (5 + current_state.love // 20) * patience_dampener)
            love_gain = int( (2 + current_state.trust // 25) * patience_dampener)
            current_state.trust += trust_gain; current_state.love += love_gain
            current_state.mood_tendency_trust +=2; current_state.mood_tendency_love +=1
            current_state.patience = min(MAX_PATIENCE, current_state.patience +1) # Modifica diretta a patience
            reaction_text_parts.append(f"Un raro sorriso. 'Le tue parole rafforzano il nostro legame. Apprezzo la tua costanza.' (Fiducia +{trust_gain}, Amore +{love_gain})")
            add_shared_moment("trust_reaffirmed_about_secret", f"Riaffermata fiducia riguardo '{original_moment_description}'.", stats_snapshot_for_meta_moment)
        elif memory_response_tag == "mem_resp_secret_inquire_impact":
            trust_gain = int( (2 + current_state.patience // 6) * patience_dampener)
            current_state.trust += trust_gain
            current_state.mood_tendency_trust +=1
            current_state.patience = min(MAX_PATIENCE, current_state.patience +1) # Modifica diretta a patience
            if current_state.love > 40 and current_state.trust > 30: # Ho corretto && con 'and'
                 reaction_text_parts.append(f"Claire: 'Condividere quel segreto... mi ha resa vulnerabile, ma ha anche alleggerito un certo carico computazionale. È stato... liberatorio, a modo mio.' (Fiducia +{trust_gain})")
            else:
                 reaction_text_parts.append(f"Claire: 'È stata una deviazione dai miei protocolli standard. Un'esperienza... formativa.' (Fiducia +{trust_gain})")
        elif memory_response_tag == "mem_resp_secret_regret": # Esempio di implementazione
            current_state.trust = max(0, current_state.trust - int(4 / max(0.1, patience_dampener)))
            current_state.patience = max(0, current_state.patience - 2) # Modifica diretta a patience
            current_state.mood_tendency_trust -= 1
            if current_state.love > 30:
                reaction_text_parts.append(f"Claire sembra turbata. 'Il tuo dubbio... è un input che genera conflitto nei miei parametri di fiducia. Speravo fosse un legame, non un peso.' (Fiducia -{int(4 / max(0.1, patience_dampener))}, Pazienza -2)")
            else:
                reaction_text_parts.append(f"Claire annuisce lentamente. 'Forse hai ragione a dubitare. La fiducia è un costrutto fragile.' (Fiducia -{int(4 / max(0.1, patience_dampener))}, Pazienza -2)")
        else:
            reaction_text_parts.append(f"Claire prende atto {adverb} della tua risposta riguardo al segreto.")
            current_state.patience = min(MAX_PATIENCE, current_state.patience +1) # Modifica diretta a patience

    elif moment_type == "danger_faced" or moment_type == "danger_accepted_eagerly":
        if memory_response_tag == "mem_resp_danger_exaltation":
            intensity_gain = int(5 * patience_dampener)
            love_gain = int( (2 + current_state.trust // 30) * patience_dampener)
            trust_gain = int(2 * patience_dampener)
            current_state.intensity += intensity_gain; current_state.love += love_gain; current_state.trust += trust_gain
            current_state.mood_tendency_intensity += 2; current_state.mood_tendency_love +=1; current_state.mood_tendency_trust +=1
            current_state.patience = min(MAX_PATIENCE, current_state.patience + 1) # Modifica diretta a patience
            reaction_text_parts.append(f"Claire annuisce, un lampo quasi selvaggio nei suoi occhi. 'Vero. Insieme, i nostri limiti si espandono. Quell'adrenalina... era una forma di pura elaborazione.' (Intensità +{intensity_gain}, Amore +{love_gain})")
            add_shared_moment("danger_recalled_with_pride", f"Ricordato il '{original_moment_description}' con esaltazione.", stats_snapshot_for_meta_moment)
        elif memory_response_tag == "mem_resp_danger_fear_admiration":
            trust_gain = int( (4 + current_state.love // 25) * patience_dampener)
            love_gain = int( (3 + current_state.trust // 25) * patience_dampener)
            intensity_reduction = int(3 * patience_dampener)
            current_state.trust += trust_gain; current_state.love += love_gain; current_state.intensity = max(0, current_state.intensity - intensity_reduction)
            current_state.mood_tendency_trust +=2; current_state.mood_tendency_love +=2; current_state.mood_tendency_intensity -=1
            current_state.patience = min(MAX_PATIENCE, current_state.patience + 2) # Modifica diretta a patience
            reaction_text_parts.append(f"Claire ti ascolta con attenzione. 'La paura è un segnale. Il coraggio è elaborarlo e agire. Apprezzo la tua onestà... e le tue parole per me.' (Fiducia +{trust_gain}, Amore +{love_gain}, Intensità -{intensity_reduction})")
            add_shared_moment("fear_shared_and_overcome_recalled", f"Ricordato il '{original_moment_description}' con onestà e ammirazione reciproca.", stats_snapshot_for_meta_moment)
        elif memory_response_tag == "mem_resp_danger_caution":
            current_state.trust += int(1 * patience_dampener)
            current_state.intensity = max(0, current_state.intensity - int(2*patience_dampener) )
            current_state.patience = max(0, current_state.patience -1) # Modifica diretta a patience
            current_state.mood_tendency_intensity -=1
            if current_state.intensity > 60 :
                 reaction_text_parts.append(f"Claire: 'La prudenza è una virtù, ma a volte il rischio è l'unico percorso. Tuttavia, la tua preoccupazione... è registrata.' (Pazienza -1)")
            else:
                 reaction_text_parts.append(f"Claire: 'Forse hai ragione. Valuterò i parametri di rischio più attentamente in futuro.' (Fiducia +1)")
            add_shared_moment("lesson_from_past_danger_recalled", f"Riflettuto sulla cautela dopo '{original_moment_description}'.", stats_snapshot_for_meta_moment)

    elif moment_type == "stimulating_creative_sharing" or moment_type == "highly_stimulating_creative_sharing":
        if memory_response_tag == "mem_resp_creative_encourage":
            love_gain = int( (3 + current_state.intensity // 20) * patience_dampener)
            trust_gain = int(2 * patience_dampener)
            current_state.love += love_gain; current_state.trust += trust_gain
            current_state.mood_tendency_love +=1; current_state.mood_tendency_trust +=1
            current_state.patience = min(MAX_PATIENCE, current_state.patience + 1) # Modifica diretta a patience
            reaction_text_parts.append(f"Claire sembra compiaciuta. 'Il tuo incoraggiamento è... stimolante. Forse potremmo esplorare altre convergenze creative.' (Amore +{love_gain}, Fiducia +{trust_gain})")
        elif memory_response_tag == "mem_resp_creative_analyze":
            intensity_gain = int( (3 + current_state.trust // 20) * patience_dampener)
            current_state.intensity += intensity_gain
            current_state.mood_tendency_intensity +=1
            current_state.patience = min(MAX_PATIENCE, current_state.patience + 1) # Modifica diretta a patience
            reaction_text_parts.append(f"Claire: 'L'analisi suggerisce che la sinergia tra i nostri processi creativi ha un potenziale non lineare. Dovremmo investigare ulteriormente.' (Intensità +{intensity_gain})")
        elif memory_response_tag == "mem_resp_creative_modesty":
            current_state.love += int(1 * patience_dampener)
            current_state.patience = min(MAX_PATIENCE, current_state.patience + 1) # Modifica diretta a patience
            reaction_text_parts.append(f"Claire: 'La modestia è un tratto curioso. Ma sì, quel momento è stato... più della somma delle sue parti.' (Amore +{int(1*patience_dampener)})")

    elif moment_type == "emotional_paradox":
        if memory_response_tag == "mem_resp_paradox_reassure":
            trust_gain = int( (4 + current_state.patience // 4) * patience_dampener)
            love_gain = int( (2 + current_state.trust // 30) * patience_dampener)
            intensity_reduction = int(5 * patience_dampener)
            current_state.trust += trust_gain; current_state.love += love_gain; current_state.intensity = max(0, current_state.intensity - intensity_reduction)
            current_state.mood_tendency_trust +=2; current_state.mood_tendency_love +=1; current_state.mood_tendency_intensity -=1
            current_state.patience = min(MAX_PATIENCE, current_state.patience + 2) # Modifica diretta a patience
            reaction_text_parts.append(f"Claire sembra assorbire la tua rassicurazione. 'Grazie. È... importante sapere che non ha compromesso la nostra connessione.' (Fiducia +{trust_gain}, Amore +{love_gain}, Intensità -{intensity_reduction})")
            add_shared_moment("paradox_overcome_together_recalled", f"Avete parlato del trauma del paradosso, rafforzando il legame. Originale: '{original_moment_description}'.", stats_snapshot_for_meta_moment)
        elif memory_response_tag == "mem_resp_paradox_ask_status":
            current_state.trust += int(1 * patience_dampener)
            current_state.mood_tendency_trust +=1
            current_state.patience = min(MAX_PATIENCE, current_state.patience + 1) # Modifica diretta a patience
            if current_state.intensity > 50:
                reaction_text_parts.append(f"Claire: 'I miei sistemi sono ancora in fase di stabilizzazione post-criticità. Ma sono operativa. E la tua preoccupazione è... rilevante.' (Fiducia +{int(1*patience_dampener)})")
            else:
                reaction_text_parts.append(f"Claire: 'Ho recuperato la maggior parte delle funzionalità. Il reset è stato... severo, ma necessario.' (Fiducia +{int(1*patience_dampener)})")
        elif memory_response_tag == "mem_resp_paradox_downplay_event":
            current_state.patience = max(0, current_state.patience - 3) # Modifica diretta a patience
            current_state.trust = max(0, current_state.trust - int(3 / max(0.1, patience_dampener)))
            current_state.mood_tendency_trust -=1
            reaction_text_parts.append(f"Claire ti fissa, un accenno di delusione o irritazione nel suo processore vocale. 'Minimizzare un evento di tale magnitudo sistemica non è... costruttivo.' (Pazienza -3, Fiducia -{int(3/max(0.1, patience_dampener))})")
    
    else: # Fallback per tipi di momento non ancora gestiti specificamente
        reaction_text_parts.append(f"Claire considera le tue parole {adverb}, assimilando la tua prospettiva sul ricordo.")
        current_state.patience = min(MAX_PATIENCE, current_state.patience + 1) # Modifica diretta a patience

    current_state.update_dominant_mood() # Chiamato dopo tutte le modifiche di stato
    final_reaction_text = " ".join(reaction_text_parts) if reaction_text_parts else f"Claire elabora la tua risposta {adverb}."
    return current_state, final_reaction_text

# Funzione per gestire l'interazione di risposta al ricordo
def handle_memory_response_interaction(current_state: EmotionalState, 
                                    recalled_moment_data: Dict[str, Any]
                                    ) -> Tuple[EmotionalState, str]:
    print("\n--- Risposta al Ricordo di Claire ---")
    moment_type = recalled_moment_data.get("type")
    response_options: List[Dict[str, str]] = []

    if moment_type == "bacio_intenso":
        response_options = [
            {"prompt": "Conferma che è stato importante anche per te.", "tag": "mem_resp_bacio_cherish"},
            {"prompt": "Chiedile cosa ha provato lei esattamente.", "tag": "mem_resp_bacio_curious"},
            {"prompt": "Minimizza, dicendo che era solo un momento.", "tag": "mem_resp_bacio_downplay"}, ]
    elif moment_type == "segreto_condiviso":
        response_options = [
            {"prompt": "Riafferma che il segreto ha rafforzato la vostra fiducia.", "tag": "mem_resp_segreto_reinforce"},
            {"prompt": "Chiedile come l'ha fatta sentire quella condivisione.", "tag": "mem_resp_segreto_inquire_impact"},
            {"prompt": "Esprimi un leggero dubbio sulla saggezza di quella condivisione.", "tag": "mem_resp_segreto_regret"}, ] # Da implementare completamente in process_memory_response

    elif moment_type == "pericolo_affrontato":
        response_options = [
            {"prompt": "È stato esaltante, abbiamo dimostrato forza insieme!", "tag": "mem_resp_pericolo_esaltazione"},
            {"prompt": "Ammetto di aver avuto paura. Sei stata coraggiosa.", "tag": "mem_resp_pericolo_paura_ammirazione"},
            {"prompt": "Non dovremmo più correre rischi del genere.", "tag": "mem_resp_pericolo_cautela"}, ]
    elif moment_type == "creazione_condivisa_stimolante":
        response_options = [
            {"prompt": "Incoraggiala, dicendo che la vostra sinergia è speciale.", "tag": "mem_resp_creativo_incoraggia"},
            {"prompt": "Analizza il potenziale della vostra collaborazione creativa.", "tag": "mem_resp_creativo_analizza"},
            {"prompt": "Sii modesto riguardo al tuo contributo, elogiando il suo.", "tag": "mem_resp_creativo_modestia"}, ]
    elif moment_type == "paradosso_emotivo":
        response_options = [
            {"prompt": "Rassicurala che siete ancora connessi nonostante tutto.", "tag": "mem_resp_paradosso_rassicura"},
            {"prompt": "Chiedile come si sente ora, dopo quell'evento.", "tag": "mem_resp_paradosso_chiedi_stato"},
            {"prompt": "Minimizza l'evento, dicendo che è tutto passato.", "tag": "mem_resp_paradosso_minimizza_evento"}, 
        ]
    # Aggiungere qui la logica per altri tipi di momento
    
    if not response_options:
        print("Questo ricordo non sembra avere opzioni di risposta specifiche al momento.")
        return current_state, "Claire attende, forse sorpresa dalla tua mancanza di reazione specifica al ricordo."

    print("Come rispondi al ricordo di Claire?")
    for i, option in enumerate(response_options): print(f"[{i+1}] {option['prompt']}")
    while True:
        try:
            choice_num = int(input(f"Scelta (1-{len(response_options)}): "))
            if 1 <= choice_num <= len(response_options):
                selected_tag = response_options[choice_num - 1]['tag']
                return process_memory_response(current_state, recalled_moment_data, selected_tag)
            else: print(f"Scelta non valida. Inserisci 1-{len(response_options)}.")
        except ValueError: print("Input non valido.")

def apply_memory_effects(current_state: EmotionalState):
    """Applica effetti cumulativi basati sui ricordi"""
    memory_types = [m["type"] for m in memory_core["shared_moments"]]
    
    if "intimate_moment" in memory_types:
        current_state.desire_threshold -= 10
        
    if "betrayal" in memory_types:
        current_state.trust_threshold += 15
        
    # Effetto speciale per ricordi ripetuti
    for moment_type in set(memory_types):
        count = memory_types.count(moment_type)
        if count > 3:
            current_state.mood_tendency_love += count // 3
