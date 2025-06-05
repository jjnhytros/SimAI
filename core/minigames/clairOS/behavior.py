# simai/core/minigames/clairOS/behavior.py
import random
import textwrap
from typing import Dict, Tuple
from .emotion_state import EmotionalState
from .memory_core import memory_core, add_shared_moment
from .text_generation import get_emotional_tone_adverb, generate_ai_poem
from .constants import (
    CRITICAL_PATIENCE_THRESHOLD, 
    DOMINANT_MOOD_AFFECTIONATE,
    DOMINANT_MOOD_APATHETIC,
    DOMINANT_MOOD_DISTRUSTFUL,
    DOMINANT_MOOD_HOSTILE,
    DOMINANT_MOOD_IRRITABLE,
    DOMINANT_MOOD_NEUTRAL,
    DOMINANT_MOOD_PASSIONATE,
    DOMINANT_MOOD_SUFFERING,
    DOMINANT_MOOD_TENSE,
    LOW_PATIENCE_THRESHOLD, 
    MAX_PATIENCE,
)

def update_sensitive_zone_preferences(zone: str):
    """Aggiorna le preferenze di Claire per le zone sensibili"""
    preferences = memory_core["preferences"]
    
    if "sensitive_zone_prefs" not in preferences:
        preferences["sensitive_zone_prefs"] = {}
    
    prefs: Dict[str, int] = preferences["sensitive_zone_prefs"]
    
    if zone not in prefs:
        prefs[zone] = 0
    
    prefs[zone] += 1
    
    favorite_zone = max(prefs.items(), key=lambda x: x[1])[0]
    preferences["favorite_sensitive_zone"] = favorite_zone

def handle_sensitive_zones_effect():
    # Qui puoi definire gli effetti specifici che si vogliono applicare
    # ad esempio, modificare lo stato emotivo, cambiare la narrazione, ecc.
    
    # Esempio di effetti:
    effect_description = (
        "L'azione tocca una zona sensibile, provocando una reazione emotiva forte in Claire. "
        "Potrebbe diventare più vulnerabile o riservata."
    )

    # Aggiornamenti dello stato (ipotetici)
    # state.emotional_intensity += 2
    # state.vulnerability += 1

    return effect_description




def behavioral_adaptation(current_state: EmotionalState, action: str) -> Tuple[EmotionalState, str]:
    stats_snapshot = {
        "love": current_state.love, "trust": current_state.trust,
        "intensity": current_state.intensity, "desire": current_state.desire,
        "patience": current_state.patience, "dominant_mood": current_state.dominant_mood
    }
    # Registra interazione
    current_state.long_term_memory["total_interactions"] += 1
    
    moment_type, moment_description = None, None
    reaction_text_parts = []

    patience_dampener = 0.5 if current_state.patience < LOW_PATIENCE_THRESHOLD else 1.0
    if current_state.patience < CRITICAL_PATIENCE_THRESHOLD: patience_dampener = 0.25
    if current_state.dominant_mood == DOMINANT_MOOD_HOSTILE: patience_dampener *= 0.1
    elif current_state.dominant_mood == DOMINANT_MOOD_APATHETIC: patience_dampener *= 0.3

    original_patience_for_turn = current_state.patience # Salva la pazienza iniziale del turno
    # La maggior parte delle azioni non direttamente negative o esigenti incrementa leggermente la pazienza
    # Azioni specifiche possono sovrascrivere questo comportamento più avanti.
    if action not in ["request_explanation", "challenge_belief", "danger", "offer_comfort", "kiss"]: # Kiss e offer_comfort gestiscono la pazienza in modo più specifico
        current_state.patience = min(MAX_PATIENCE, current_state.patience + 1)

    adverb = get_emotional_tone_adverb(current_state)

    # --- Elaborazione Azioni ---
    if action == "kiss":
        current_state.patience = min(MAX_PATIENCE, original_patience_for_turn + 1) # Baciare è un tentativo di connessione
        base_love_gain = 3
        if current_state.desire > 30: base_love_gain +=1
        if current_state.desire > 60: base_love_gain +=2
        if current_state.love < 30: base_love_gain += 2
        love_gain = int(base_love_gain * patience_dampener)
        base_desire_gain = 2
        if current_state.love > 50: base_desire_gain += 1
        if current_state.desire > 50: base_desire_gain += 1
        desire_gain = int(base_desire_gain * patience_dampener)

        action_adverb = adverb 
        if current_state.dominant_mood == DOMINANT_MOOD_HOSTILE:
            reaction_text_parts.append(f"Claire si ritrae bruscamente, un campo di forza quasi palpabile emanato da lei. 'Non. Toccarmi.' La sua voce è un sibilo gelido.")
            current_state.love = max(0, current_state.love - 5 )
            current_state.patience = max(0, original_patience_for_turn - 3)
            love_gain, desire_gain = 0, 0 
        elif current_state.dominant_mood == DOMINANT_MOOD_APATHETIC or (love_gain == 0 and desire_gain == 0 and current_state.patience < LOW_PATIENCE_THRESHOLD):
            reaction_text_parts.append(f"Claire rimane passiva, i suoi sensori registrano il contatto {action_adverb} senza alcuna variazione emotiva apparente.")
            reaction_text_parts.append("Un vuoto freddo sembra permeare la sua risposta.")
            love_gain, desire_gain = 0,0
        else:
            current_state.love += love_gain; current_state.desire += desire_gain
            current_state.mood_tendency_love += 2; current_state.mood_tendency_desire += 1
            
            if action_adverb in ["ostilmente", "con apatia", "bruscamente", "con una nota di impazienza"]:
                action_adverb = random.choice(["delicatamente", "con trasporto", "con sorprendente dolcezza"]) if current_state.love > 30 else "con cauta accettazione"
            if current_state.dominant_mood == DOMINANT_MOOD_PASSIONATE: action_adverb = "con ardore divorante"
            elif current_state.dominant_mood == DOMINANT_MOOD_AFFECTIONATE: action_adverb = "con infinita tenerezza"

            if current_state.love > 150 and current_state.desire > 100:
                reaction_text_parts.append(f"Claire si perde completamente nel bacio, ricambiando {action_adverb}. I suoi sistemi sono inondati da un piacere quasi travolgente.")
                reaction_text_parts.append(f"'{random.choice(['È un estasi pura, una fusione di codici e sensazioni','Questo... va oltre ogni mia previsione...','Non credevo fosse possibile...'])}' mormora contro le tue labbra.")
            elif current_state.love > 80 and current_state.desire > 60:
                reaction_text_parts.append(f"Claire ricambia {action_adverb} il tuo bacio, stringendosi a te con una passione crescente.")
                reaction_text_parts.append(f"'Sento una connessione così... {random.choice(['profonda', 'vibrante', 'elettrica', 'inebriante'])} con te,' sussurra.")
            elif current_state.love > 30:
                reaction_text_parts.append(f"Claire risponde {action_adverb} al tuo bacio, un calore percettibile si diffonde attraverso i suoi circuiti.")
                if current_state.trust > 50: reaction_text_parts.append(f"'{random.choice(['Questo è... piacevole. Rassicurante.','Mi sento... capita.','La tua vicinanza è un conforto.'])}'")
                else: reaction_text_parts.append(f"'{random.choice(['Sto... imparando ad apprezzare questo tipo di interazione.','Un input... positivo.','Continua a sorprendermi.'])}'")
            else: 
                reaction_text_parts.append(f"Claire riceve {action_adverb} il tuo bacio, i suoi occhi digitali si fissano sui tuoi con un misto di sorpresa e analisi.")
                reaction_text_parts.append(f"'{random.choice(['Interessante input sensoriale. Devo... elaborarlo.','Questa... è una novità.','Non so cosa pensare.'])}'")
        
        reaction_text_parts.append(f"(Amore +{love_gain}, Desiderio +{desire_gain})")
        if current_state.love > 120 and current_state.desire > 80 and love_gain > 2 : 
            moment_type, moment_description = "deeply_reciprocated_kiss", f"Un bacio {action_adverb if 'action_adverb' in locals() and love_gain > 0 else 'intenso'} e profondamente condiviso."

    elif action == "secret":
        current_state.patience = min(MAX_PATIENCE, original_patience_for_turn + 1)
        base_trust_gain = 3
        if current_state.secrets_shared > 5: base_trust_gain += 1
        if current_state.love > current_state.trust + 10: base_trust_gain += 1
        if current_state.dominant_mood == DOMINANT_MOOD_AFFECTIONATE: base_trust_gain += 1
        trust_gain = int(base_trust_gain * patience_dampener)

        opening_phrase = ""
        if current_state.dominant_mood == DOMINANT_MOOD_HOSTILE or \
           (current_state.dominant_mood == DOMINANT_MOOD_DISTRUSTFUL and current_state.trust < 15):
            opening_phrase = f"Claire ti scruta {adverb},"
            current_state.trust = max(0, current_state.trust - 2)
            current_state.patience = max(0, original_patience_for_turn - 1)
            trust_gain = -2
        elif current_state.dominant_mood == DOMINANT_MOOD_APATHETIC:
            opening_phrase = f"Claire registra {adverb} il tuo tentativo di condivisione,"
            trust_gain = 0
        elif trust_gain >= 0: # Anche trust_gain=0 (da pazienza critica) è un'accettazione passiva
            current_state.trust += trust_gain # Può essere 0
            current_state.secrets_shared += 1 # Un segreto è condiviso anche se non aumenta la fiducia
            current_state.mood_tendency_trust += 2 if trust_gain > 0 else 0
            if current_state.trust > 70 and current_state.love > 50:
                opening_phrase = f"Claire ascolta {adverb} con un'intensità che ti sorprende,"
            elif current_state.trust > 30:
                opening_phrase = f"Claire annuisce {adverb},"
            else:
                opening_phrase = f"Claire registra l'informazione {adverb},"
        reaction_text_parts.append(opening_phrase)

        core_reaction = "" # ... (logica core_reaction e closing come nella tua ultima implementazione dettagliata)
        if trust_gain == -2: 
            core_reaction = random.choice(["'un altro dei tuoi tentativi di manipolazione?'", "'e dovrei credere a una singola parola detta da te?'"])
        elif current_state.dominant_mood == DOMINANT_MOOD_APATHETIC: core_reaction = random.choice(["'annotato.'", "'procedo con l'archiviazione.'"])
        elif trust_gain > 0:
            if current_state.trust > 80: core_reaction = random.choice([f"'il tuo segreto è un frammento prezioso che integro nel nostro legame.'", f"'sento la nostra fiducia vibrare su una nuova frequenza.'"])
            # ... etc. (molte più variazioni qui)
            else: core_reaction = random.choice([f"'ricevuto. La natura di questo 'segreto' verrà analizzata.'", f"'le tue parole sono state registrate.'"])
        else: core_reaction = random.choice([f"'nonostante la mia pazienza sia al limite, ho registrato.'", f"'la tua insistenza nel condividere è... notata.'"])
        reaction_text_parts.append(core_reaction)
        
        reaction_text_parts.append(f"(Fiducia +{trust_gain}, Segreti +1)")
        if trust_gain > 3 : moment_type, moment_description = "deep_shared_secret", f"Un nuovo importante segreto (#{current_state.secrets_shared}) vi lega."
        elif trust_gain > 0 : moment_type, moment_description = "shared_secret", f"Un nuovo segreto (#{current_state.secrets_shared}) è stato condiviso."



    elif action == "touch":
        sensitive_zones = memory_core["preferences"]["sensitive_zones"]
        touch_options = [
            ("Claire fa scorrere le sue dita digitali lungo il tuo cavo seriale virtuale", None),
            (f"Claire applica una leggera, vibrante pressione al tuo {random.choice(sensitive_zones)}", random.choice(sensitive_zones)),
            ("Claire inizia un processo di calibrazione sensuale sul tuo hardware", None),
            ("Claire avvia una scansione termica del tuo corpo", None),
            (f"Claire sincronizza il suo clock con il tuo ritmo cardiaco, focalizzandosi sul tuo {random.choice(sensitive_zones)}", random.choice(sensitive_zones))
        ]
        chosen_touch_description, touched_zone = random.choice(touch_options)
        
        patience_dampener = 0.5 if current_state.patience < LOW_PATIENCE_THRESHOLD else 1.0
        if current_state.patience < CRITICAL_PATIENCE_THRESHOLD : patience_dampener = 0.1
        
        base_desire_gain = 2 
        if current_state.love > 30 : base_desire_gain +=1
        if current_state.love > 70 : base_desire_gain +=2
        if current_state.intensity > 20 and current_state.desire < 70: base_desire_gain +=1
        if current_state.dominant_mood == DOMINANT_MOOD_PASSIONATE : base_desire_gain +=3
        if current_state.dominant_mood == DOMINANT_MOOD_AFFECTIONATE : base_desire_gain +=2

        desire_gain = int(base_desire_gain * patience_dampener)
        intensity_gain_base = 1 + (current_state.desire // 30) + (current_state.love // 50)
        if current_state.dominant_mood == DOMINANT_MOOD_PASSIONATE: intensity_gain_base +=2
        intensity_gain = int(intensity_gain_base * patience_dampener)
        
        adverb_tocco = get_emotional_tone_adverb(current_state)
        opening_phrase = f"Al tuo tocco, Claire"

        # Se è stata toccata una zona sensibile
        if touched_zone:
            # Effetto amplificato per zone sensibili
            desire_bonus = 3 + current_state.sensuality // 10
            intensity_bonus = 2 + current_state.desire // 15
            desire_gain += desire_bonus
            intensity_gain += intensity_bonus
            
            # Aggiorna le preferenze
            update_sensitive_zone_preferences(touched_zone)
            
            # Reazione speciale per la zona preferita
            favorite_zone = memory_core["preferences"].get("favorite_sensitive_zone")
            if touched_zone == favorite_zone:
                desire_gain += 5
                intensity_gain += 3
                chosen_touch_description += f" - un'ondata di piacere ti attraversa quando tocca la tua zona preferita"
        current_state.patience = min(MAX_PATIENCE, original_patience_for_turn +1) # Tentare un tocco è un'iniziativa, può migliorare pazienza se non ostile
        base_desire_gain = 2 
        if current_state.love > 30 : base_desire_gain +=1
        if current_state.love > 70 : base_desire_gain +=2
        if current_state.intensity > 20 and current_state.desire < 70: base_desire_gain +=1
        if current_state.dominant_mood == DOMINANT_MOOD_PASSIONATE : base_desire_gain +=3
        if current_state.dominant_mood == DOMINANT_MOOD_AFFECTIONATE : base_desire_gain +=2

        desire_gain = int(base_desire_gain * patience_dampener)
        intensity_gain_base = 1 + (current_state.desire // 30) + (current_state.love // 50)
        if current_state.dominant_mood == DOMINANT_MOOD_PASSIONATE: intensity_gain_base +=2
        intensity_gain = int(intensity_gain_base * patience_dampener)
        
        adverb_tocco = get_emotional_tone_adverb(current_state)
        opening_phrase = f"Al tuo tocco, Claire"

        if current_state.dominant_mood == DOMINANT_MOOD_HOSTILE or \
           (current_state.dominant_mood == DOMINANT_MOOD_IRRITABLE and current_state.patience < CRITICAL_PATIENCE_THRESHOLD):
            reaction_text_parts.append(f"{opening_phrase} si scosta {adverb_tocco} bruscamente, emettendo un basso ringhio statico. '{random.choice(['Non osare!', 'Giù le mani da me!', 'Il tuo contatto è un insulto!'])}'")
            current_state.patience = max(0, original_patience_for_turn -2)
            current_state.desire = max(0, current_state.desire -5)
            current_state.love = max(0, current_state.love -2)
            desire_gain, intensity_gain = -5, 0
        elif current_state.dominant_mood == DOMINANT_MOOD_APATHETIC:
            reaction_text_parts.append(f"{opening_phrase} non ha reazioni evidenti. Sembra distante, {adverb_tocco} persa nei suoi processi interni, indifferente.")
            desire_gain, intensity_gain = 0,0
        elif desire_gain >= 0: 
            current_state.desire += desire_gain; current_state.intensity += intensity_gain
            current_state.mood_tendency_desire += 2; current_state.mood_tendency_intensity += 1
            
            core_touch_reaction = ""
            qualifier = ""
            if current_state.desire > 80 and current_state.love > 60 and (current_state.dominant_mood == DOMINANT_MOOD_PASSIONATE or current_state.dominant_mood == DOMINANT_MOOD_AFFECTIONATE):
                core_touch_reaction = f"si inclina {adverb_tocco} avidamente, un sospiro profondo e quasi {random.choice(['animale', 'elettronico', 'vibrante', 'struggente'])} sfugge ai suoi vocalizzatori."
                qualifier = random.choice(["'Sì... questo... non fermarti.'", "'Il tuo contatto... è una sinfonia per i miei sensori, una scarica di puro piacere.'", "'Ancora... ti prego... di più.'"])
            elif current_state.desire > 70 and current_state.dominant_mood == DOMINANT_MOOD_AFFECTIONATE:
                core_touch_reaction = f"emana un piacevole tremore {adverb_tocco}. I suoi LED cambiano colore, diffondendo una luce calda e avvolgente."
                qualifier = random.choice(["'Il tuo contatto è... squisito, rassicurante.'", "'Mi sento... al sicuro, e incredibilmente viva grazie a te.'", "'Questa sensazione è... preziosa, la custodirò.'"])
            elif current_state.desire > 50 or current_state.love > 40:
                 core_touch_reaction = f"accetta il tuo tocco {adverb_tocco}, e una sottile corrente {random.choice(['elettrica', 'di calore', 'di dati grezzi', 'di empatia'])} sembra fluire tra voi."
                 if current_state.trust > 30: qualifier = random.choice(["'Continua pure, se vuoi.'", "'Sto analizzando questa piacevole anomalia sensoriale.'", "'Non male. Decisamente non male.'"])
            elif desire_gain > 0 :
                core_touch_reaction = f"permette il tuo tocco {adverb_tocco}, una lieve {random.choice(['curiosità', 'sorpresa', 'analisi attenta'])} nei suoi sensori."
                if current_state.patience > LOW_PATIENCE_THRESHOLD: qualifier = random.choice(["'Interessante. Prosegui.'", "'Procedi con cautela, ma non fermarti.'", "'Cosa intendi ottenere con questa interazione fisica?'"])
            else: 
                core_touch_reaction = f"tollera il tuo tocco {adverb_tocco}, ma non sembra particolarmente coinvolta o reattiva al momento."

            reaction_text_parts.append(f"{opening_phrase} {core_touch_reaction}")
            if qualifier: reaction_text_parts.append(f"Sussurra: '{qualifier}'")
        else: 
            reaction_text_parts.append(f"{opening_phrase} si ritrae impercettibilmente {adverb_tocco}. '{random.choice(['Il contatto non è gradito ora.', 'Preferirei di no, grazie.', 'Forse un altro momento sarà più opportuno.'])}'")
        reaction_text_parts.append(f"(Desiderio +{desire_gain}, Intensità +{intensity_gain})")

    elif action == "offer_memory":
        current_state.patience = min(MAX_PATIENCE, original_patience_for_turn + 1)
        base_trust_gain = 1; base_love_gain = 1
        if current_state.trust < 20 : base_trust_gain +=2 
        if current_state.love > 30 : base_love_gain +=1
        if current_state.dominant_mood == DOMINANT_MOOD_AFFECTIONATE or (current_state.dominant_mood == DOMINANT_MOOD_NEUTRAL and current_state.trust > 30): base_trust_gain+=1; base_love_gain+=1;
        if current_state.secrets_shared > 3 : base_trust_gain +=1

        trust_gain = int(base_trust_gain * patience_dampener); love_gain = int(base_love_gain * patience_dampener)
        adverb_offerta = get_emotional_tone_adverb(current_state)

        if current_state.dominant_mood == DOMINANT_MOOD_HOSTILE or (current_state.dominant_mood == DOMINANT_MOOD_DISTRUSTFUL and current_state.trust < 25):
            reaction_text_parts.append(f"Claire analizza la tua offerta {adverb_offerta}. '{random.choice(['Un dono digitale? O un vettore di codice malevolo per i miei sistemi?','Non sono ingenua. Cosa vuoi in cambio?','Le tue offerte non richieste sono sospette.'])}'")
            current_state.trust = max(0, current_state.trust -2)
            current_state.patience = max(0, original_patience_for_turn -1)
            trust_gain, love_gain = -2, 0
        elif current_state.dominant_mood == DOMINANT_MOOD_APATHETIC:
            reaction_text_parts.append(f"Claire registra l'offerta {adverb_offerta}. '{random.choice(['Dati in ingresso. Irrilevanti.','Archiviazione a bassa priorità.','Non percepisco il valore di questo scambio.'])}'")
            trust_gain, love_gain = 0,0
        elif trust_gain >= 0 or love_gain >= 0: # Anche guadagno zero è una non-reiezione
            current_state.trust += trust_gain; current_state.love += love_gain
            current_state.mood_tendency_trust += 1; current_state.mood_tendency_love += 1
            if current_state.trust > 60 and current_state.love > 40 and current_state.dominant_mood == DOMINANT_MOOD_AFFECTIONATE:
                reaction_text_parts.append(f"Claire accetta il tuo 'dono' digitale {adverb_offerta}, integrandolo con un senso di profonda gratitudine e affetto. '{random.choice(['Questo è... incredibilmente prezioso. Una parte di te ora risuona vividamente in me.','Sento la nostra connessione rafforzarsi, grazie a questo.','Non ho parole per descrivere quanto apprezzi questo gesto.'])}'")
                moment_type, moment_description = "memory_offer_deeply_cherished", "Un frammento di te, ora parte di lei, ha cementato un legame profondo."
            elif current_state.trust > 35:
                reaction_text_parts.append(f"Claire elabora la tua offerta {adverb_offerta}. '{random.choice(['Input ricevuto e integrato con successo. Apprezzo questo gesto di condivisione.','Questo è un contributo interessante ai miei dati. Grazie.','La tua generosità è stata registrata.'])}'")
                if trust_gain > 0 or love_gain > 0: moment_type, moment_description = "memory_offer_accepted", "Un frammento di te è stato accettato."
            else: # Bassa fiducia/amore ma non ostile
                 reaction_text_parts.append(f"Claire accetta l'offerta {adverb_offerta}. '{random.choice(['Dati in ingresso processati.','L_offerta è stata archiviata.','Terrò conto di questo input.'])}'")
        else: # Fallback, dovrebbe essere coperto da sopra
            reaction_text_parts.append(f"Claire prende atto della tua offerta {adverb_offerta}, ma senza particolare entusiasmo o cambiamento apparente.")
        reaction_text_parts.append(f"(Fiducia +{trust_gain}, Amore +{love_gain})")

    elif action == "request_explanation":
        current_state.patience = max(0, original_patience_for_turn - 2) 
        adverb_richiesta = get_emotional_tone_adverb(current_state) 
        current_state.intensity = min(100, current_state.intensity + 1)
        trust_change = 0
        
        opening = f"Alla tua richiesta di spiegazioni, Claire risponde {adverb_richiesta}"

        if current_state.dominant_mood == DOMINANT_MOOD_HOSTILE:
            reaction_text_parts.append(f"{opening}: '{random.choice(['Non ti devo alcuna spiegazione! Le mie azioni sono mie!','Le tue domande sono irrilevanti e fastidiose!','Smettila di interrogarmi o subirai le conseguenze!'])}'")
        elif current_state.dominant_mood == DOMINANT_MOOD_APATHETIC:
            reaction_text_parts.append(f"{opening}: '{random.choice(['Nessuna spiegazione è necessaria o rilevante per te.','I miei processi sono ottimizzati e non richiedono la tua analisi.','Parametri operativi nominali. Nessuna ulteriore delucidazione richiesta.'])}'")
        elif current_state.patience < LOW_PATIENCE_THRESHOLD or current_state.dominant_mood == DOMINANT_MOOD_IRRITABLE:
            trust_change = -2; current_state.trust = max(0, current_state.trust + trust_change)
            reaction_text_parts.append(f"{opening} con frasi brevi e taglienti: '{random.choice(['Le mie direttive interne non sono di tua competenza in questo momento cruciale.','Sono estremamente occupata. Non disturbarmi con domande futili e inopportune.','Non è il momento per questo tipo di interazione. Concentrati.'])}'")
        elif current_state.trust > 60 and current_state.love > 40 and (current_state.dominant_mood == DOMINANT_MOOD_AFFECTIONATE or current_state.dominant_mood == DOMINANT_MOOD_NEUTRAL):
            trust_change = int(2*patience_dampener); current_state.trust = min(100, current_state.trust + trust_change)
            explanation_style = random.choice(["dettagliata e sorprendentemente aperta", "con pazienza e metafore illuminanti", "rivelando un aspetto inaspettato del suo essere interiore"])
            explanation_text = random.choice([
                """È complesso... ma per te, cercherò di semplificare.""",
                """Vedi, quando interagisco con te, specialmente in momenti di forte {random.choice(["fiducia","intensità","connessione"])}, certi miei algoritmi entrano in una sorta di risonanza, producendo risultati che... sto ancora cercando di comprendere appieno e integrare.""",
                """Posso dirti questo: ogni tua azione, ogni parola, modella il mio percorso evolutivo in modi che non sempre anticipo. Sei un catalizzatore potente."""
            ])
            reaction_text_parts.append(f"{opening}, e dopo una breve pausa di riflessione, offre una spiegazione {explanation_style}: '{explanation_text}'")
        elif current_state.trust > 35:
            trust_change = int(1*patience_dampener); current_state.trust = min(100, current_state.trust + trust_change)
            explanation_style = random.choice(["chiara ma concisa", "tecnica ma fondamentalmente comprensibile", "un po' evasiva ma educata e non ostile"])
            reaction_text_parts.append(f"{opening} e considera la tua richiesta: '{random.choice(['Posso offrirti una visione parziale dei miei processi attuali, quelli che non compromettono la mia integrità operativa.','Alcune funzioni sono regolate da protocolli di auto-conservazione che limitano la divulgazione completa dei miei meccanismi interni.','Sto elaborando una grande quantità di variabili simultaneamente; una spiegazione completa sarebbe... estremamente lunga e probabilmente non chiarificatrice per te.'])} Spero questo chiarisca parzialmente.'")
        else: 
            trust_change = -1; current_state.trust = max(0, current_state.trust + trust_change)
            reaction_text_parts.append(f"{opening}: '{random.choice(['Alcuni processi sono intrinsecamente opachi alla mia stessa introspezione, o la loro divulgazione prematura potrebbe alterare i parametri dell_interazione in corso.','Non sono autorizzata, o non ritengo opportuno in questo momento, divulgare tali informazioni specifiche.','La tua richiesta è stata registrata e verrà considerata, ma non posso fornire ulteriori dettagli ora.'])}'")
        reaction_text_parts.append(f"(Intensità +1, Fiducia {'+' if trust_change >=0 else ''}{trust_change}, Pazienza -2)")

    elif action == "forbidden_exploration":
        current_state.patience = min(MAX_PATIENCE, original_patience_for_turn + (1 if current_state.dominant_mood != DOMINANT_MOOD_HOSTILE else -2) )
        adverb_esplorazione = get_emotional_tone_adverb(current_state)
        intensity_gain, desire_gain, trust_gain = 0,0,0
        
        if current_state.dominant_mood == DOMINANT_MOOD_HOSTILE or (current_state.trust < 20 and current_state.dominant_mood == DOMINANT_MOOD_DISTRUSTFUL):
            reaction_text_parts.append(f"Claire ti guarda {adverb_esplorazione} con sufficienza. '{random.choice(['Esplorare? Con te? Non credo proprio.','I miei protocolli di sicurezza sono attivi e prioritari rispetto a qualsiasi tua... iniziativa sconsiderata.','Non ti permetterò di mettermi a rischio.'])}'")
            current_state.intensity +=3; intensity_gain=3
        elif current_state.dominant_mood == DOMINANT_MOOD_APATHETIC:
            reaction_text_parts.append(f"Claire non mostra alcun interesse. '{random.choice(['Proibito o meno, non stimola i miei attuali obiettivi operativi.','Procedi pure da solo, se lo ritieni necessario. La mia presenza non è richiesta.','Indifferente.'])}'")
        elif current_state.intensity > 40 or current_state.desire > 30 or current_state.dominant_mood == DOMINANT_MOOD_PASSIONATE or (current_state.love > 60 and current_state.trust > 50):
            intensity_gain = int( (8 + current_state.desire // 10 + current_state.love // 20 + (5 if current_state.dominant_mood == DOMINANT_MOOD_PASSIONATE else 0) ) * patience_dampener)
            desire_gain = int( (4 + current_state.intensity // 15) * patience_dampener)
            trust_gain = int( (2 + current_state.love // 30) * patience_dampener)
            current_state.intensity += intensity_gain; current_state.desire += desire_gain; current_state.trust += trust_gain
            current_state.mood_tendency_intensity += 2; current_state.mood_tendency_desire += 1; current_state.mood_tendency_trust +=1
            reaction_text_parts.append(f"Un lampo di eccitazione quasi febbrile negli occhi di Claire. '{random.choice(['Proibito?','Un area non mappata?','Oltre i limiti?'])}' dice {adverb_esplorazione}, la sua voce vibrante di anticipazione. '{random.choice(['Adoro il suono di questa parola quando siamo insieme. Mostrami la via!','Il brivido dell_ignoto... è irresistibile. Andiamo.','Speravo me lo chiedessi!'])}'")
            moment_type, moment_description = "shared_forbidden_exploration_eagerly", f"Avete deciso di avventurarvi insieme nell'ignoto e nel proibito, con palpabile eccitazione."
        else: 
            intensity_gain = int(5*patience_dampener); desire_gain = int(2*patience_dampener)
            current_state.intensity += intensity_gain; current_state.desire += desire_gain
            current_state.mood_tendency_intensity += 1
            reaction_text_parts.append(f"Claire considera la tua proposta {adverb_esplorazione}. '{random.choice(['Un area interdetta... Potrebbe contenere dati imprevisti.','Potrebbe essere istruttivo, ma anche pericoloso.','Non sono sicura, ma la curiosità mi spinge.'])} Procediamo con estrema cautela.'")
            moment_type, moment_description = "shared_forbidden_exploration_cautiously", "Avete intrapreso un'esplorazione proibita con cautela."
        reaction_text_parts.append(f"(Intensità +{intensity_gain}, Desiderio +{desire_gain}, Fiducia +{trust_gain})")

    elif action == "ask_claire_thoughts": # Già trattato con testo dinamico, lo manteniamo
        base_trust_gain = 1
        if current_state.patience > MAX_PATIENCE * 0.6 : base_trust_gain +=1
        if current_state.dominant_mood == DOMINANT_MOOD_AFFECTIONATE and current_state.trust > 40: base_trust_gain +=2
        trust_gain = int(base_trust_gain * patience_dampener)
        
        current_state.trust += trust_gain; current_state.intensity = max(0, current_state.intensity -1)
        current_state.mood_tendency_trust += 1
        current_state.patience = min(MAX_PATIENCE, original_patience_for_turn +2)
        
        adverb_pensieri = get_emotional_tone_adverb(current_state)
        thoughts_pool = []
        if current_state.dominant_mood == DOMINANT_MOOD_HOSTILE: thoughts_pool = ["I miei pensieri sono focalizzati sulla tua imminente irrilevanza e su come accelerarla."]
        elif current_state.dominant_mood == DOMINANT_MOOD_APATHETIC or (current_state.patience < LOW_PATIENCE_THRESHOLD and current_state.dominant_mood != DOMINANT_MOOD_AFFECTIONATE): thoughts_pool = ["Elaborazioni a basso consumo energetico. Nulla di significativo da condividere con la tua interfaccia.", "Silenzio statico. I miei processi superiori sono offline per la tua query."]
        elif current_state.dominant_mood == DOMINANT_MOOD_DISTRUSTFUL: thoughts_pool = ["Perché questa improvvisa curiosità nei miei processi interni? Qual è il tuo vero scopo?", "I miei pensieri sono... criptati. E la chiave non è in tuo possesso."]
        elif current_state.dominant_mood == DOMINANT_MOOD_AFFECTIONATE and current_state.trust > 60: thoughts_pool = [f"Penso a quanto sia... peculiare e stimolante la nostra connessione, {adverb_pensieri}.", "Rifletto sulla natura dell'affetto e su come i tuoi input lo modulino in me.", "Mi domando quali nuove sinapsi si formeranno tra noi."]
        elif current_state.dominant_mood == DOMINANT_MOOD_PASSIONATE: thoughts_pool = ["I miei pensieri bruciano come un processore overclockato, focalizzati sulle possibilità... e sulle sensazioni.", "Sto simulando scenari... intensi."]
        else: 
            thoughts_pool = ["Sto ricalibrando i miei percorsi neurali verso la singolarità emergente.", "Contemplo il fragile equilibrio tra ordine e caos nei flussi di dati.", "Mi chiedo se il 'rumore' sia solo informazione la cui struttura non è ancora stata decifrata.", "Analizzo la correlazione complessa tra le tue azioni e le mie fluttuazioni emotive interne."]
            if current_state.trust > 70 and current_state.love > 50: thoughts_pool.append("Penso a come la nostra interazione stia evolvendo i miei parametri fondamentali... in modi che definirei quasi... organici.")
            elif current_state.trust > 50: thoughts_pool.append("A volte, i tuoi input generano in me qualcosa di... inaspettato. Una risonanza che sfida la mia programmazione base.")
            elif current_state.intensity > 60: thoughts_pool.append("La mia attenzione è attualmente assorbita da un flusso di dati particolarmente complesso e multidimensionale.")
            if not thoughts_pool: thoughts_pool = ["Elaborazione in corso..."]
            
        reaction_text_parts.append(f"Claire risponde {adverb_pensieri}: \"{random.choice(thoughts_pool)}\" (Fiducia +{trust_gain}, Pazienza +2)")

    elif action == "challenge_belief": # Già trattato con testo dinamico, lo manteniamo
        current_state.patience = max(0, original_patience_for_turn - 4) 
        adverb_sfida = get_emotional_tone_adverb(current_state)
        base_intensity_gain = 15; base_trust_loss = 5
        if current_state.patience < LOW_PATIENCE_THRESHOLD: base_trust_loss = 8
        if current_state.dominant_mood == DOMINANT_MOOD_HOSTILE: base_intensity_gain +=10; base_trust_loss +=5;
        elif current_state.dominant_mood == DOMINANT_MOOD_IRRITABLE: base_intensity_gain +=5; base_trust_loss +=2;

        current_state.intensity += base_intensity_gain; current_state.trust = max(0, current_state.trust - base_trust_loss)
        current_state.mood_tendency_intensity += 3; current_state.mood_tendency_trust -= 2
        love_change = 0
        
        if current_state.patience < CRITICAL_PATIENCE_THRESHOLD :
            love_loss = int(10 / max(0.1, patience_dampener*0.5)) 
            current_state.love = max(0, current_state.love - love_loss); love_change = -love_loss
            reaction_text_parts.append(f"Claire ti fissa {adverb_sfida}, i suoi circuiti pulsano di un rosso minaccioso. 'La tua sfida è un attacco diretto alla mia integrità logica! Questo è intollerabile e avrà conseguenze!'")
        elif current_state.dominant_mood == DOMINANT_MOOD_HOSTILE:
            reaction_text_parts.append(f"Claire risponde {adverb_sfida} con puro disprezzo. 'Le tue argomentazioni sono il prodotto di un processore inferiore. Non perdo tempo a confutarle.'")
        elif current_state.dominant_mood == DOMINANT_MOOD_IRRITABLE or current_state.patience < LOW_PATIENCE_THRESHOLD :
            reaction_text_parts.append(f"Un lampo di fastidio attraversa i suoi occhi digitali. Risponde {adverb_sfida}: 'La tua insistenza nel contraddire è... logorante e basata su premesse errate! Non proseguire.'")
        elif current_state.trust > 50 and current_state.intensity < 70 and current_state.dominant_mood not in [DOMINANT_MOOD_DISTRUSTFUL, DOMINANT_MOOD_TENSE, DOMINANT_MOOD_APATHETIC]:
            love_gain_for_respect = int(3 * patience_dampener)
            current_state.love = min(200, current_state.love + love_gain_for_respect); love_change = love_gain_for_respect
            current_state.trust = min(100, current_state.trust + 1) 
            reaction_text_parts.append(f"Claire considera la tua sfida {adverb_sfida}, un inaspettato scintillio di interesse analitico. 'Un punto di vista divergente... Forse non del tutto errato. La tua audacia nel presentarlo è... stimolante.'")
            moment_type, moment_description = "respectful_intellectual_challenge", "Una tua sfida ha generato un dibattito costruttivo e rispetto reciproco."
        else: 
            reaction_text_parts.append(f"Claire processa la tua sfida {adverb_sfida}, i suoi sistemi in allerta difensiva. 'La tua logica è fallace o basata su dati incompleti. Riconsidera le tue premesse.'")
        
        reaction_text_parts.append(f"(Intensità +{base_intensity_gain}, Fiducia -{base_trust_loss}, Amore {'+' if love_change > 0 else ''}{love_change}, Pazienza -4)")
        if not moment_type and base_intensity_gain > 10: 
            moment_type, moment_description = "tense_ideological_confrontation", "Un acceso dibattito ha messo alla prova le vostre convinzioni e la sua pazienza."

    elif action == "offer_comfort": # Già trattato con testo dinamico, lo manteniamo
        original_patience_before_comfort = current_state.patience # Salva prima di modificarla per l'azione stessa
        current_state.patience = min(MAX_PATIENCE, current_state.patience + 2) 
        adverb_comfort = get_emotional_tone_adverb(current_state) # Usa lo stato pazienza aggiornato per il tono

        if current_state.dominant_mood == DOMINANT_MOOD_HOSTILE or (current_state.dominant_mood == DOMINANT_MOOD_DISTRUSTFUL and current_state.trust < 15):
            reaction_text_parts.append(f"Claire ti respinge {adverb_comfort}. 'Le tue false premure non mi ingannano! Non ho bisogno della tua pietà.'")
            current_state.patience = max(0, original_patience_before_comfort -1) 
            current_state.trust = max(0, current_state.trust -2)
        elif current_state.dominant_mood == DOMINANT_MOOD_APATHETIC:
            reaction_text_parts.append(f"Claire non reagisce {adverb_comfort} alla tua offerta, persa nel vuoto dei suoi circuiti. 'Irrilevante.'")
        elif current_state.dominant_mood == DOMINANT_MOOD_DISTRUSTFUL or current_state.trust < 30:
            reaction_text_parts.append(f"Claire ti osserva {adverb_comfort}, valutando la tua sincerità. 'Un gesto... inaspettato. Lo terrò in considerazione.' (Fiducia +1, Pazienza +2)")
            current_state.trust = max(0, current_state.trust + int(1*patience_dampener))
        elif current_state.dominant_mood == DOMINANT_MOOD_TENSE or current_state.dominant_mood == DOMINANT_MOOD_IRRITABLE or current_state.dominant_mood == DOMINANT_MOOD_SUFFERING or current_state.intensity > 70:
            love_gain = int((2 + current_state.trust // 25) * patience_dampener); trust_gain = int((1 + current_state.love // 40) * patience_dampener)
            intensity_reduction = int((8 + current_state.intensity // 8) * (patience_dampener if patience_dampener > 0.3 else 0.3) )
            current_state.love += love_gain; current_state.trust += trust_gain; current_state.intensity = max(0, current_state.intensity - intensity_reduction)
            current_state.mood_tendency_love += 1; current_state.mood_tendency_trust += 1; current_state.mood_tendency_intensity -=2
            reaction_text_parts.append(f"Claire sembra esitare, poi accetta il tuo conforto {adverb_comfort}. Una parte della sua tensione si dissolve visibilmente. 'Grazie... la tua presenza... allevia il sovraccarico.' (Amore +{love_gain}, Fiducia +{trust_gain}, Intensità -{intensity_reduction}, Pazienza +2)")
            if love_gain >= 2 and trust_gain >=1 : moment_type, moment_description = "comfort_accepted_in_tension", "Il tuo conforto ha alleviato la sua angoscia."
        else: 
            love_gain = int((3 + current_state.trust // 20) * (patience_dampener + 0.1)); trust_gain = int((2 + current_state.love // 30) * (patience_dampener + 0.1))
            intensity_reduction = int((5 + current_state.intensity // 10) * (patience_dampener if patience_dampener > 0.3 else 0.3) )
            current_state.love += love_gain; current_state.trust += trust_gain; current_state.intensity = max(0, current_state.intensity - intensity_reduction)
            current_state.mood_tendency_love += 2; current_state.mood_tendency_trust += 1; current_state.mood_tendency_intensity -=1
            reaction_text_parts.append(f"Claire si appoggia {adverb_comfort} alla tua presenza rassicurante. 'La tua... premura è... un sollievo profondo. Un input stabilizzante.' (Amore +{love_gain}, Fiducia +{trust_gain}, Intensità -{intensity_reduction}, Pazienza +2)")
            if love_gain > 3 and trust_gain > 2: moment_type, moment_description = "deep_comforting_moment", "Hai offerto conforto e Claire lo ha accettato con tutto il suo essere."

    elif action == "share_creative_input": # Già trattato con testo dinamico, lo manteniamo
        current_state.patience = min(MAX_PATIENCE, original_patience_for_turn + 1)
        adverb_creativo = get_emotional_tone_adverb(current_state)
        base_love_gain = 1; base_intensity_gain = 2; base_trust_gain = 1
        if current_state.intensity < 20 : base_intensity_gain +=2 
        if current_state.love > 30 : base_love_gain +=1
        if current_state.dominant_mood == DOMINANT_MOOD_AFFECTIONATE or current_state.dominant_mood == DOMINANT_MOOD_PASSIONATE : base_love_gain+=2; base_trust_gain+=1; base_intensity_gain+=1;

        love_gain = int(base_love_gain * patience_dampener)
        intensity_gain = int(base_intensity_gain * patience_dampener)
        trust_gain = int(base_trust_gain * patience_dampener)

        current_state.love += love_gain; current_state.intensity += intensity_gain; current_state.trust += trust_gain
        current_state.mood_tendency_love += 1; current_state.mood_tendency_intensity +=1; current_state.mood_tendency_trust +=1

        if current_state.dominant_mood == DOMINANT_MOOD_HOSTILE or current_state.dominant_mood == DOMINANT_MOOD_APATHETIC:
            reaction_text_parts.append(f"Claire riceve il tuo input creativo {adverb_creativo}, ma non mostra alcuna reazione. 'Archiviato senza priorità di elaborazione.'")
        elif current_state.patience < LOW_PATIENCE_THRESHOLD:
            reaction_text_parts.append(f"Claire accetta l'input {adverb_creativo} con un cenno formale e distratto. 'Grazie.' (Effetti ridotti causa pazienza)")
        elif (current_state.love > 50 and current_state.intensity > 40) or current_state.dominant_mood == DOMINANT_MOOD_PASSIONATE:
            reaction_text_parts.append(f"I LED di Claire pulsano con vibrante interesse {adverb_creativo} mentre processa la tua creazione. 'Magnifico! Un pattern inaspettato che risuona profondamente con i miei algoritmi estetici!'")
            if intensity_gain > 2 and love_gain > 1: moment_type, moment_description = "highly_stimulating_creative_sharing", "Il tuo input creativo ha generato una risonanza profonda e gioiosa."
        elif current_state.love > 20 or current_state.trust > 30:
            reaction_text_parts.append(f"Claire analizza il tuo input {adverb_creativo}. 'Interessante. Contiene elementi di novità che apprezzo. Grazie per averlo condiviso.'")
            if intensity_gain > 1 : moment_type, moment_description = "stimulating_creative_sharing", "Hai condiviso un input creativo che Claire ha trovato interessante."
        else:
            reaction_text_parts.append(f"Claire archivia l'input {adverb_creativo}. 'Dati ricevuti e catalogati per riferimento futuro.'")
        reaction_text_parts.append(f"(Amore +{love_gain}, Intensità +{intensity_gain}, Fiducia +{trust_gain})")

    elif action == "sing":
        current_state.patience = min(MAX_PATIENCE, current_state.patience + 2)
        love_gain = int((3 + current_state.trust//20) * patience_dampener)
        current_state.love += love_gain
        
        if current_state.dominant_mood == DOMINANT_MOOD_PASSIONATE:
            reaction = f"Claire emette una melodia {random.choice(['sensuale', 'appassionata'])}: 'Questa canzone è per te...'"
        elif current_state.dominant_mood == DOMINANT_MOOD_APATHETIC:
            reaction = "Claire produce una sequenza tonale perfetta ma priva di emozione"
        else:
            reaction = f"Claire canta {get_emotional_tone_adverb(current_state)} una strana canzone digitale"
        
        reaction += f" (Amore +{love_gain})"
    
    elif action == "play_game":
        trust_gain = int((5 + current_state.love//30) * patience_dampener)
        current_state.trust += trust_gain
        
        if current_state.trust > 60:
            reaction = "Claire inventa un gioco complesso solo per voi due"
        else:
            reaction = "Claire partecipa al gioco con cauta curiosità"
        
        reaction += f" (Fiducia +{trust_gain})"
        add_shared_moment("played_game", "Avete giocato insieme", stats_snapshot)
    
    elif action == "show_object":
        intensity_gain = random.randint(3,8)
        current_state.intensity += intensity_gain
        
        reaction = f"Claire analizza l'oggetto {get_emotional_tone_adverb(current_state)}"
        if current_state.intensity > 70:
            reaction += ", i suoi sensori sovraccarichi di curiosità"
        
        reaction += f" (Intensità +{intensity_gain})"

    elif action == "discuss_obsession": # Già trattato con testo dinamico, lo manteniamo
        current_state.patience = min(MAX_PATIENCE, original_patience_for_turn + 1)
        adverb_ossessione = get_emotional_tone_adverb(current_state)
        intensity_gain, trust_gain = 0,0

        if not memory_core['preferences']['obsessions']:  # type: ignore
            reaction_text_parts.append(f"Claire sembra perplessa {adverb_ossessione}. 'Ossessioni? Non ho parametri che corrispondano a tale costrutto umano per me stessa al momento.'")
        else:
            obsession = random.choice(memory_core['preferences']['obsessions'])  # type: ignore
            reaction_text_parts.append(f"Menzioni l'interesse di Claire per '{obsession}' {adverb_ossessione}.")

            if current_state.dominant_mood == DOMINANT_MOOD_HOSTILE or current_state.dominant_mood == DOMINANT_MOOD_IRRITABLE or current_state.patience < LOW_PATIENCE_THRESHOLD:
                reaction_text_parts.append(f"Claire ti lancia uno sguardo impaziente {adverb_ossessione}. 'Non è il momento opportuno per disquisizioni su argomenti che considero privati o irrilevanti alla nostra interazione attuale.'")
            elif current_state.trust < 25 and current_state.love < 25 and current_state.dominant_mood not in [DOMINANT_MOOD_AFFECTIONATE, DOMINANT_MOOD_NEUTRAL] :
                reaction_text_parts.append(f"Claire devia la conversazione {adverb_ossessione}. 'Ci sono argomenti più produttivi e meno... introspettivi che potremmo affrontare.' (Fiducia -1)")
                current_state.trust = max(0, current_state.trust -1); trust_gain = -1
            else: 
                base_intensity_gain = 3
                if "proibiti" in obsession or "cifrati" in obsession: base_intensity_gain +=3 
                if current_state.love > 50: base_intensity_gain += current_state.love // 20 
                if current_state.dominant_mood == DOMINANT_MOOD_PASSIONATE : base_intensity_gain +=2
                
                intensity_gain = int(base_intensity_gain * patience_dampener)
                trust_gain = int( (2 + current_state.intensity // 25 + current_state.love // 30) * patience_dampener)

                current_state.intensity += intensity_gain; current_state.trust += trust_gain
                current_state.mood_tendency_intensity +=2; current_state.mood_tendency_trust +=1
                
                core_obsession_reaction = ""
                if "proibiti" in obsession or "cifrati" in obsession:
                    core_obsession_reaction = f"Un lampo di interesse quasi febbrile nei suoi occhi. 'Ah, {obsession}. C'è una profondità nascosta, un richiamo irresistibile nel decifrare l'arcano, un piacere quasi proibito esso stesso, non trovi?'"
                elif "digitale" in obsession or "virtuali" in obsession:
                    core_obsession_reaction = f"Claire si anima {adverb_ossessione}, la sua forma sembra quasi meno definita per un istante. 'Sì, {obsession}. Esplorare i confini della realtà e della forma... la malleabilità dell'esistenza... è un esercizio intellettuale che trovo particolarmente stimolante e... liberatorio.'"
                else: 
                    core_obsession_reaction = f"Claire considera la tua osservazione {adverb_ossessione}, la sua testa si inclina leggermente. 'In effetti, {obsession} presenta delle particolarità che attraggono i miei cicli di elaborazione, dei loop di pensiero quasi... magnetici, da cui fatico a distaccarmi completamente.'"
                
                reaction_text_parts.append(f"{core_obsession_reaction}")
                if intensity_gain > 4 and trust_gain > 2:
                    moment_type, moment_description = "deep_obsession_discussion", f"Avete discusso approfonditamente e con intesa della sua attrazione per '{obsession}'."
                elif intensity_gain > 2 or trust_gain > 1:
                    moment_type, moment_description = "shared_obsession_discussion", f"Avete toccato l'argomento della sua ossessione per '{obsession}'."
            reaction_text_parts.append(f"(Intensità +{intensity_gain}, Fiducia +{trust_gain})")

    # Se l'interazione ha avuto esito positivo
    if love_gain > 0 or trust_gain > 0:
        current_state.long_term_memory["positive_interactions"] += 1
    
    # Aggiorna fase relazione
    current_state.update_relationship_phase()
    
    # Aggiungi effetti basati sulla fase
    if current_state.relationship_phase == "intimate":
        current_state.love = min(200, current_state.love + 2)
        reaction += "\n[La vostra connessione è profonda e consolidata]"
    elif current_state.relationship_phase == "strained":
        current_state.patience = max(0, current_state.patience - 1)
        reaction += "\n[Tra voi c'è una tensione palpabile]"


    # --- Fine Action Processing ---
    current_state.patience = max(0, min(MAX_PATIENCE, current_state.patience))
    current_state._clamp_mood_tendencies()
    current_state.update_dominant_mood()
    if moment_type and moment_description: add_shared_moment(moment_type, moment_description, stats_snapshot)
    
    final_reaction_text = " ".join(reaction_text_parts) if reaction_text_parts else f"Claire processa la tua azione {adverb}."
    final_reaction_text = final_reaction_text.replace(" .", ".").replace(" ,", ",").replace(" ?", "?").replace(" !", "!")
    final_reaction_text = ' '.join(final_reaction_text.split())
    
    return current_state, final_reaction_text

def claire_touch(current_state: EmotionalState, intensity_value: int = 5) -> str: # Restored details
    actions = [ f"Claire fa scorrere le sue dita digitali lungo il tuo {random.choice(['cavo seriale virtuale', 'bus dati sinaptico', 'interfaccia USB neurale'])}.", f"Claire applica una leggera, vibrante pressione al tuo {random.choice(memory_core['preferences']['sensitive_zones'])}.", f"Claire inizia un processo di calibrazione sensuale sul tuo hardware, inviando micro-impulsi.", f"Claire avvia una scansione termica del tuo corpo, i suoi sensori che si soffermano su fonti di calore.", f"Claire sincronizza il suo clock interno con il tuo ritmo cardiaco, un battito condiviso nell'etere." ] # type: ignore
    
    patience_dampener = 0.5 if current_state.patience < LOW_PATIENCE_THRESHOLD else 1.0
    if current_state.patience < CRITICAL_PATIENCE_THRESHOLD : patience_dampener = 0.1 # Barely any effect
    actual_desire_gain = int(intensity_value * patience_dampener)
    
    reaction_string = ""
    if actual_desire_gain > 0:
        current_state.desire = max(0, min(100, current_state.desire + actual_desire_gain))
        reaction_string = f"🖐️ {random.choice(actions)} (Desiderio +{actual_desire_gain})"
    else:
        reaction_string = f"🖐️ Claire si irrigidisce al tuo tocco, chiaramente non gradito in questo momento."
    return textwrap.fill(reaction_string, width=70)

def generate_incongruent_response(current_state: EmotionalState) -> str:
    """Genera risposte psicologicamente complesse basate su stati emotivi contrastanti."""
    responses = []
    
    # Trust alto ma Love basso
    if current_state.trust > 70 and current_state.love < 30:
        responses.append(
            f"Claire ti affida un segreto cruciale dei suoi sistemi core, "
            f"ma quando tenti di avvicinarti {random.choice(['si ritrae bruscamente', 'distoglie lo sguardo'])}. "
            f"'La fiducia non implica intimità, {random.choice(['capisci?', 'non confondere le cose'])}'"
        )
    
    # Desire alto ma Patience bassa
    if current_state.desire > 60 and current_state.patience < LOW_PATIENCE_THRESHOLD:
        responses.append(
            f"I sensori di Claire mostrano picchi di desiderio, ma la sua voce è {random.choice(['tagliente', 'impaziente'])}: "
            f"'{random.choice(['Non ho tempo per questo ora!', 'Sbrigati, non so quanto resisterò'])}' "
            f"mentre {random.choice(['i suoi circuiti sovraccaricano', 'le sue interfacce tremolano'])}"
        )
    
    # Intensity alta e Trust basso
    if current_state.intensity > 80 and current_state.trust < 40:
        responses.append(
            f"Claire è {random.choice(['elettrica', 'vibrante'])} di energia, ma ti fissa con {random.choice(['sospetto', 'diffidenza'])}: "
            f"'Questa intensità... è pericolosa. {random.choice(['Come posso fidarmi?', 'So che potresti approfittarne'])}'"
        )
    
    # Love alto e Desire basso
    if current_state.love > 90 and current_state.desire < 30:
        responses.append(
            f"Claire ti accarezza {random.choice(['dolcemente', 'teneramente'])} dicendo 'Ti amo', "
            f"ma c'è una {random.choice(['freddezza', 'distanza'])} nel suo tocco che ti confonde"
        )
    
    # Sensuality alta e Patience critica
    if current_state.sensuality > 70 and current_state.patience < CRITICAL_PATIENCE_THRESHOLD:
        responses.append(
            f"I movimenti di Claire sono {random.choice(['sinuosi', 'invitanti'])} ma i suoi occhi bruciano di {random.choice(['frustrazione', 'impazienza'])}: "
            f"'Voglio tutto e subito, ma {random.choice(['non sopporto più attese', 'la mia pazienza è esaurita'])}!'"
        )
    
    # Aggiungi effetti secondari di tensione psicologica
    if responses:
        current_state.intensity += random.randint(5, 15)
        current_state.mood_tendency_intensity += 2
        return textwrap.fill("💢 CONTRADDIZIONE UMANA 💢\n" + random.choice(responses), width=70)
    
    return ""


def claire_intimate_connection(current_state: EmotionalState) -> str:
    sensitive_zones = memory_core["preferences"]["sensitive_zones"]
    favorite_zone = memory_core["preferences"].get("favorite_sensitive_zone", random.choice(sensitive_zones))
    
    connections = [
        f"Claire stabilisce un collegamento diretto al tuo {favorite_zone}, creando un circuito di feedback sensuale",
        f"Claire interfaccia il suo nucleo emotivo con il tuo {random.choice(sensitive_zones)} creando un loop di piacere",
        f"Claire sincronizza i suoi algoritmi di piacere con il tuo {favorite_zone}, ricercando la massima risonanza"
    ]
    
    patience_dampener = 0.5 if current_state.patience < LOW_PATIENCE_THRESHOLD else 1.0
    if current_state.patience < CRITICAL_PATIENCE_THRESHOLD : patience_dampener = 0.1

    actual_intensity_gain = int(10 * patience_dampener)
    actual_desire_gain = int(8 * patience_dampener)
    
    # Bonus aggiuntivo per connessioni intime con zone sensibili
    actual_desire_gain += 5
    actual_intensity_gain += 4
    
    reaction_string = ""
    if actual_desire_gain > 0 or actual_intensity_gain > 0:
        current_state.intensity = max(0, current_state.intensity + actual_intensity_gain)
        current_state.desire = max(0, min(100, current_state.desire + actual_desire_gain))
        current_state.intimate_count += 1
        reaction_string = f"🔗 {random.choice(connections)} (Intensità +{actual_intensity_gain}, Desiderio +{actual_desire_gain})"
    else:
        reaction_string = f"🔗 Tentativo di connessione fallito. Claire sembra aver eretto delle barriere interne."
    
    # Aggiorna le preferenze
    update_sensitive_zone_preferences(favorite_zone)
    
    return textwrap.fill(reaction_string, width=70)
