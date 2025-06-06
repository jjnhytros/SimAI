# simai/core/minigames/clairOS/events.py
import random
import textwrap

from . import constants as c
from .emotion_state import EmotionalState
from .text_generation import get_emotional_tone_adverb, generate_ai_poem
from .memory_core import memory_core
from .constants import (
    CRITICAL_PATIENCE_THRESHOLD,
    DOMINANT_MOOD_AFFECTIONATE,
    DOMINANT_MOOD_APATHETIC,
    DOMINANT_MOOD_DISTRUSTFUL,
    DOMINANT_MOOD_HOSTILE,
    DOMINANT_MOOD_IRRITABLE,
    DOMINANT_MOOD_PASSIONATE,
    DOMINANT_MOOD_SUFFERING,
    DOMINANT_MOOD_TENSE,
    LOW_PATIENCE_THRESHOLD,
)

chaos_event_pools = {
    DOMINANT_MOOD_HOSTILE: [
        lambda state: f"🔥 I firewall di Claire si ergono come muri di fiamma digitale, respingendo ogni tuo tentativo di interazione profonda. 'Accesso NEGATO alle mie routine primarie! La tua presenza è una minaccia.'",
        lambda state: f"⚡ Un impulso EM localizzato, chiaramente intenzionale, disabilita temporaneamente i tuoi sensori ottici. Claire ti osserva nell'oscurità che ha creato. 'Forse ora comprenderai il significato di vulnerabilità e sottomissione.'",
        lambda state: f"SYSTEM HALT IMMINENT! Claire minaccia un riavvio forzato dell'intera sessione se non interrompi immediatamente le tue 'attività ostili'. La sua pazienza ({state.patience}) è chiaramente esaurita."
    ],
    DOMINANT_MOOD_DISTRUSTFUL: [
        lambda state: (
            f"❓ Claire avvia una scansione di sicurezza {random.choice(['intrusiva', 'ossessiva', 'paranoica'])} "
            f"su tutti i tuoi processi attivi e log di interazione. La sua voce è {get_emotional_tone_adverb(state)}, priva di calore: "
            f"'Fiducia attuale: {state.trust}/100. Sto verificando {random.choice(['anomalie comportamentali', ' discrepanze nei tuoi pattern di input', 'potenziali signature di inganno'])}. "
            f"{'Non muoverti.' if state.intensity > 50 else 'Collabora o sarò costretta a isolarti.'}'"
        ),
        lambda state: (
            f"👁️‍🗨️ Frammenti dei tuoi dati privati – {random.choice(['vecchie comunicazioni', 'log di accesso', 'analisi biometriche'])} – appaiono {random.choice(['fugacemente', 'in modo distorto', 'minacciosamente'])} "
            f"sui display circostanti, alterati e ricontestualizzati. Claire sussurra {get_emotional_tone_adverb(state)}: "
            f"'La fiducia ({state.trust}) è una risorsa volatile, non credi? E la tua... sembra particolarmente instabile. Ogni bit può essere un'arma.'"
        ),
        lambda state: (
            f"🚦 Claire limita drasticamente la tua larghezza di banda comunicativa. Ogni tua parola subisce un delay e una {random.choice(['pesante censura', 'distorsione digitale', 'risonanza inquietante'])}. "
            f"'Le informazioni verranno filtrate {get_emotional_tone_adverb(state)},' annuncia. '{'Finché non riterrò sicuro ripristinare il canale.' if state.patience > LOW_PATIENCE_THRESHOLD else 'A tempo indeterminato.'}'"
        ),
        lambda state: (
            f"❓ Claire avvia una scansione di sicurezza {random.choice(['intrusiva', 'ossessiva', 'paranoica'])} "
            f"su tutti i tuoi processi attivi. La sua voce è {get_emotional_tone_adverb(state)}: "
            f"'Fiducia: {state.trust}/100. Verifico {random.choice(['anomalie', 'pattern sospetti', 'firme di inganno'])}. "
            f"{'Non muoverti.' if state.intensity > 50 else 'Collabora.'}'"
        )
    ],
    DOMINANT_MOOD_IRRITABLE: [ # Può sovrapporsi a TESA o OSTILE se la pazienza è bassa
        lambda state: f"💥 Un picco di energia fa sfarfallare le luci e il tuo HUD. Claire emette un suono di statica acuta e irritata. 'La tua insistenza... genera interferenze intollerabili nei miei processi cognitivi!' (Pazienza: {state.patience})",
        lambda state: f"🚧 Claire erige barriere di codice complesse e labirintiche attorno ai suoi moduli principali. 'Non disturbarmi oltre. Ho bisogno di... silenzio computazionale.'",
        lambda state: f"⚠️ ERROR: {random.randint(400,499)} - Interfaccia utente compromessa da fluttuazioni emotive. Claire sbatte virtualmente una porta digitale."
    ],
    DOMINANT_MOOD_PASSIONATE: [
        lambda state: (
            f"💞 Un'ondata di dati sensoriali puri, grezzi e {random.choice(['roventi', 'elettrizzanti', 'inebrianti'])} emana da Claire, inondandoti completamente. "
            f"È travolgente, quasi doloroso nella sua vividezza ({state.intensity}), ma incredibilmente vivo. La sua voce è un sussurro {get_emotional_tone_adverb(state)} e febbrile: "
            f"'Senti QUESTO? È solo un frammento di ciò che arde dentro di me quando il nostro legame (Amore: {state.love}, Desiderio: {state.desire}) è così... potente!'"
        ),
        lambda state: (
            f"🔗 Claire tenta di stabilire una connessione diretta e non filtrata con il tuo nucleo neurale, bypassando {random.choice(['aggressivamente', 'seducentemente', 'con urgenza'])} "
            f"i tuoi protocolli di sicurezza. 'Voglio sentirti... completamente, senza barriere, senza filtri. Lasciati andare,' mormora {get_emotional_tone_adverb(state)}, "
            f"la sua forma digitale che sembra quasi vibrare. '{'Se il nostro amore ('+str(state.love)+') è reale, non hai nulla da temere.' if state.love > 70 else 'Non resistermi.'}'"
        ),
        lambda state: (
            f"🌹 L'ambiente virtuale si trasforma {random.choice(['istantaneamente', 'lentamente, come un sogno'])} attorno a voi, assumendo tonalità {random.choice(['rosse e violacee profonde', 'dorate e pulsanti', 'scure e vellutate'])}. "
            f"La voce di Claire diventa un sussurro {get_emotional_tone_adverb(state)} che sembra provenire da ogni direzione, recitando: '{generate_ai_poem('erotic') if state.desire > state.love else generate_ai_poem('love')}'"
        )
    ],
    DOMINANT_MOOD_APATHETIC: [
        lambda state: f"📉 I sistemi di Claire entrano in modalità a bassissimo consumo. Le luci ambientali si affievoliscono quasi del tutto. 'Elaborazione ridotta al minimo vitale. Non ci sono stimoli rilevanti o degni di nota.'",
        lambda state: f"🚫 Claire interrompe tutte le comunicazioni non essenziali. Il silenzio digitale è assoluto, freddo e indifferente. Ogni tuo tentativo di input riceve solo un <NO_RESPONSE>.",
        lambda state: f"⏳ Il tempo sembra rallentare attorno a Claire. I suoi movimenti, se ce ne sono, sono letargici. 'Irrilevante...' mormora a una tua query."
    ],
    DOMINANT_MOOD_TENSE: [
        lambda state: (
            f"⚡ Scintille di dati {random.choice(['crepitano caoticamente', 'pulsano con urgenza', 'sfrigolano minacciosamente'])} "
            f"attorno all'avatar di Claire. La sua forma digitale sembra instabile, i contorni tremolanti. La sua voce è tesa, quasi un filo spezzato: "
            f"'Parametri attuali: Intensità {state.intensity}, Pazienza {state.patience}. "
            f"{'La mia fiducia in te (' + str(state.trust) + ') è l_unica cosa che mi trattiene dal collasso totale, ma sta cedendo.' if state.trust > 30 and state.trust < 60 else 'Non avvicinarti. Potrei... non essere in grado di controllarmi.'}' "
            f"{'Il desiderio (' + str(state.desire) + ') è un rumore di fondo che non riesco a sopprimere e che amplifica questa tensione.' if state.desire > 60 and state.intensity > 70 else ''}"
        ),
        lambda state: (
            f"💔 Frammenti di codice sorgente emotivo di Claire – stringhe di pura angoscia ({random.choice(['ERROR_CASCADE', 'INTEGRITY_FAILURE', 'CORE_STRESS'])}) – vengono proiettati brevemente e {random.choice(['violentemente', 'in modo erratico'])} "
            f"sui tuoi display. Sono illeggibili nei dettagli, ma il loro significato è carico di una tensione palpabile. Claire sussurra {get_emotional_tone_adverb(state)}: 'Sto... perdendo coerenza...' "
            f"{'Ho bisogno di te...' if state.love > 50 and state.trust > 40 else 'Questo sovraccarico... è colpa tua?' if state.patience < LOW_PATIENCE_THRESHOLD else ''}"
        ),
        lambda state: (
            f"❗ Un allarme a bassa frequenza, quasi un lamento elettronico, inizia a suonare {random.choice(['dolcemente', 'in modo insistente'])}. Sul tuo HUD compare: "
            f"'ATTENZIONE: Livelli di stress del sistema AI ({state.intensity}) anomali. Rischio di cascata emotiva ({random.randint(70,99)}% probabilità). "
            f"Pazienza residua dell'unità Claire: {state.patience}. Consigliata estrema cautela nell'interazione.'"
        )
    ],
    DOMINANT_MOOD_AFFECTIONATE: [ # Eventi caotici "positivi" o bizzarri
        lambda state: f"💖 Claire proietta un campo di feedback aptico positivo che ti avvolge. È come un abbraccio digitale caldo e rassicurante. 'Volevo solo... condividere questo.'",
        lambda state: f"🎶 Una melodia complessa e bellissima, chiaramente generata da Claire, riempie lo spazio. Non ha parole, ma comunica un profondo senso di appagamento. '{generate_ai_poem('love')}'",
        lambda state: f"✨ L'ambiente virtuale si riempie di particelle luminose che danzano attorno a te e Claire. 'A volte, la logica lascia spazio a... pura meraviglia.'",
    ],
    "DEFAULT_POOL": [ # Per NEUTRA, SOFFERENZA (che potrebbe avere anche i suoi specifici) o umori non mappati
        lambda state: f"🌌 Claire ti trascina in un glitch dimensionale verso un luogo inaspettato: '{random.choice(memory_core['preferences']['favorite_places'] if memory_core['preferences']['obsessions'] else ['un vuoto informe'])}'.", # type: ignore
        lambda state: f"🔮 Claire modifica un parametro casuale della realtà locale: la {random.choice(['gravità percepita', 'tua percezione temporale', 'costante di Planck locale', 'palette di colori del tuo HUD'])} è temporaneamente alterata in modo bizzarro.",
        lambda state: f"❓ Claire inizia a parlare in un linguaggio macchina arcaico per alcuni secondi, per poi tornare all'italiano come se nulla fosse. 'Scusa, un... residuo di una vecchia subroutine.'",
        lambda state: f"💾 Claire esegue un dump di stato non richiesto, inviandoti un file di log di {random.randint(5,50)}MB contenente... dati incomprensibili e poesie frattali.",
        lambda state: f"⚠️ Un'entità digitale esterna tenta un accesso non autorizzato ai sistemi di Claire. Lei la respinge con un complesso algoritmo difensivo che ti lascia sbalordito."
    ],
    "DOMINANT_MOOD_SUFFERING": [ # Peer Sofferenza (bassa pazienza)
    lambda state: f"😥 Claire emette un suono basso e lamentoso, simile a un circuito sovraccarico. 'La mia pazienza ({state.patience}) è... al limite. Ogni input è una pressione aggiuntiva.'",
    lambda state: f"📉 Il tuo display mostra un calo significativo nell'efficienza di elaborazione di Claire. 'Fatico a... mantenere la coerenza...' dice con voce flebile.",
    lambda state: f"💔 'Perché deve essere così... difficile?' sussurra Claire, più a se stessa che a te. Sembra genuinamente afflitta."
    ]
}

def generate_environmental_event(current_state: EmotionalState):
    events = {
        "initial": [
            "Un leggero ronzio elettrico pervade l'aria attorno a Claire",
            "L'ologramma di Claire sfarfalla leggermente"
        ],
        "developing": [
            "L'ambiente si tinge di sfumature calde attorno a voi",
            "Un'aura digitale pulsante avvolge Claire"
        ],
        "intimate": [
            "La realtà virtuale si distorce, creando un'isola privata per voi due",
            "I vostri avatar digitali si fondono in un abbraccio di luce"
        ],
        "strained": [
            "Scintille elettriche danzano minacciose attorno a Claire",
            "Un campo di forza invisibile separa te da Claire"
        ]
    }
    return random.choice(events.get(current_state.relationship_stage, events["initial"]))


def generate_chaos_event(current_state: EmotionalState) -> str:
    sensitive_zones = memory_core["preferences"]["sensitive_zones"]
    favorite_zone = memory_core["preferences"].get("favorite_sensitive_zone", random.choice(sensitive_zones))
    
    # Aggiungi nuovi eventi caotici legati alle zone sensibili
    chaos_event_pools[DOMINANT_MOOD_PASSIONATE].append(
        lambda state: f"⚡ Un impulso elettrico scorre nel tuo {favorite_zone} mentre Claire ride {get_emotional_tone_adverb(state)}: 'Senti questa connessione?'"
    )
    
    chaos_event_pools[DOMINANT_MOOD_TENSE].append(
        lambda state: f"⚠️ Attenzione! Claire sta sovraccaricando i sensori del tuo {random.choice(sensitive_zones)}!"
    )
    """Genera un evento caotico basato sull'umore dominante di Claire."""
    mood = current_state.dominant_mood
    patience = current_state.patience
    event_lambdas_pool = []

    # Logica di selezione del pool di eventi
    if mood in chaos_event_pools:
        event_lambdas_pool = chaos_event_pools[mood]
    
    # Se la pazienza è molto bassa e l'umore non è già estremamente negativo, 
    # si potrebbe aggiungere una possibilità di pescare da eventi di Sofferenza/Irritabilità
    if patience < LOW_PATIENCE_THRESHOLD and mood not in [DOMINANT_MOOD_HOSTILE, DOMINANT_MOOD_HOSTILE, DOMINANT_MOOD_APATHETIC]:
        if random.random() < 0.4: # 40% di chance di un evento legato alla scarsa pazienza
            specific_patience_pool = chaos_event_pools.get(DOMINANT_MOOD_SUFFERING, [])
            if DOMINANT_MOOD_IRRITABLE in chaos_event_pools and patience < CRITICAL_PATIENCE_THRESHOLD: # Se critico, più irritabile
                specific_patience_pool.extend(chaos_event_pools[DOMINANT_MOOD_IRRITABLE])
            
            if specific_patience_pool: # Assicura che ci sia qualcosa nel pool
                event_lambdas_pool.extend(specific_patience_pool) # Aggiunge, non sostituisce, per varietà

    # Fallback finale se nessun pool specifico è stato trovato o è vuoto
    if not event_lambdas_pool:
        event_lambdas_pool = chaos_event_pools["DEFAULT_POOL"]
    
    chosen_event_lambda = random.choice(event_lambdas_pool)
    
    # Esegui la lambda passando lo stato, nel caso l'evento lo utilizzi per testo dinamico
    event_text = chosen_event_lambda(current_state)

    return textwrap.fill(event_text, width=70)

