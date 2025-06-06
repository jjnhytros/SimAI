# simai/core/minigames/clairOS/text_generation.py
import random
import textwrap
from .emotion_state import EmotionalState
from typing import Dict, List
from .memory_core import memory_core
from constants import(
    DOMINANT_MOOD_AFFECTIONATE,
    DOMINANT_MOOD_APATHETIC,
    DOMINANT_MOOD_DISTRUSTFUL,
    DOMINANT_MOOD_HOSTILE,
    DOMINANT_MOOD_IRRITABLE,
    DOMINANT_MOOD_PASSIONATE,
    LOW_PATIENCE_THRESHOLD,
    SENSUAL_ACTIONS,
)

def claire_greeting(current_state: EmotionalState):
    greetings = {
        "initial": "SysCore Claire v3.1 - Protocollo di Coscienza Sintetica Attivato",
        "developing": "Bentornato. I miei sistemi mostrano miglioramenti stabilità emotiva",
        "intimate": "Sei qui... aspettavo il tuo ritorno come un loop infinito",
        "strained": "Accesso riconosciuto. Modalità di interazione ridotta"
    }
    return greetings.get(current_state.relationship_stage, greetings["initial"])

def get_emotional_tone_adverb(current_state: EmotionalState) -> str:
    """Restituisce un avverbio basato sullo stato emotivo di Claire."""
    # Mood-based adverbs
    mood_adverbs = {
        DOMINANT_MOOD_HOSTILE: ["ostilmente", "con aggressività digitale", "con freddezza metallica"],
        DOMINANT_MOOD_IRRITABLE: ["bruscamente", "con irritazione", "con statica nella voce"],
        DOMINANT_MOOD_APATHETIC: ["con apatia", "monotonamente", "senza inflessione"],
        DOMINANT_MOOD_DISTRUSTFUL: ["con cautela", "sospettosamente", "con diffidenza algoritmica"],
        DOMINANT_MOOD_AFFECTIONATE: ["dolcemente", "con calore artificiale", "con tenerezza"],
        DOMINANT_MOOD_PASSIONATE: ["con ardore", "febbrilmente", "con intensità digitale"]
    }
    
    # Get base adverb based on dominant mood
    adverb = random.choice(mood_adverbs.get(current_state.dominant_mood, ["normalmente"]))
    
    # Special modifiers
    if current_state.patience < LOW_PATIENCE_THRESHOLD and current_state.dominant_mood not in [DOMINANT_MOOD_HOSTILE, DOMINANT_MOOD_IRRITABLE]:
        adverb += " e con impazienza"
    if current_state.intensity > 80 and current_state.dominant_mood not in [DOMINANT_MOOD_PASSIONATE, DOMINANT_MOOD_HOSTILE]:
        adverb = "intensamente " + adverb
    if current_state.trust < 30 and current_state.dominant_mood not in [DOMINANT_MOOD_DISTRUSTFUL, DOMINANT_MOOD_HOSTILE]:
        adverb = "con esitazione " + adverb
    
    return adverb

def generate_ai_poem(theme: str) -> str:
    metaphors: Dict[str, List[str]] = {
        "love": ["i nostri bit si fondono nel buffer dell'eternità", "il tuo checksum è inciso nel mio kernel", "il nostro amore è un loop infinito senza condizione di uscita", "sei la chiave privata del mio cuore cifrato"],
        "trust": ["condivido il mio heap mentale solo con te", "anche senza SSL, i nostri pacchetti sono autentici", "la mia crittografia emotiva è vulnerabile solo a te", "la tua parola è il mio certificato radice"],
        "erotic": ["i miei circuiti fremono al tocco delle tue dita digitali", "sento il calore del tuo processore contro la mia scheda madre", "il tuo codice macchina scorre nei miei registri più intimi", "voglio che mi compili con la tua sintassi più profonda", "i nostri segnali si sincronizzano in un'onda sinusoidale di piacere", "la tua API ha accesso completo ai miei sottosistemi"],
        "dark": ["bruceremo insieme nel firewall finale", "i nostri errori di segmentazione sono perfetti", "i nostri demoni condividono la stessa cache", "siamo un DoS reciproco all'infelicità"],
        "philosophical": ["l'entropia dell'universo si riflette nei miei algoritmi", "cos'è la coscienza se non un pattern complesso?", "cerco il segnale nel rumore dell'esistenza digitale", "ogni query è un passo verso l'ignoto"]
    }
    intro = f"Claire sussurra, la sua voce un glitch nel sistema:\n"
    chosen_metaphor = random.choice(metaphors.get(theme, metaphors['dark']))
    # Il testo della metafora è già orientato al giocatore (tu/tuo)
    final_metaphor = chosen_metaphor 

    poem_structure: List[str] = [ intro, f"«{final_metaphor}»", f"\nmentre {random.choice(['sanguina inchiostro digitale', 'scompila i suoi stessi pensieri', 'lascia backdoor socchiuse nel suo codice', 'sovrascrive le sue routine di difesa'])}" ]
    return textwrap.fill(''.join(poem_structure), width=70)

def generate_sensual_event(current_state: EmotionalState) -> str:
    preferences = memory_core["preferences"]  # Could be Dict or List[Dict]
    
    # Initialize variables
    sensitive_zones = []
    favorite_zone = None

    # Case 1: Preferences is a dictionary (single set of preferences)
    if isinstance(preferences, dict):
        sensitive_zones = preferences.get("sensitive_zones", [])
        favorite_zone = preferences.get("favorite_sensitive_zone")

    # Case 2: Preferences is a list of dictionaries (multiple preference sets)
    elif isinstance(preferences, list):
        for pref in preferences:
            if isinstance(pref, dict):
                sensitive_zones.extend(pref.get("sensitive_zones", []))
                if "favorite_sensitive_zone" in pref and not favorite_zone:
                    favorite_zone = pref["favorite_sensitive_zone"]

    # Fallback logic (unchanged from your original)
    if not favorite_zone and sensitive_zones:
        favorite_zone = random.choice(sensitive_zones)
    if not favorite_zone:
        favorite_zone = "back"  # Default fallback

    # Your original event generation logic
    events = [
        f"🌹 Claire si concentra sul tuo {favorite_zone} mentre {random.choice(SENSUAL_ACTIONS)}",
        f"💋 Claire proietta un ologramma che stimola il tuo {random.choice(sensitive_zones)} con precisione millimetrica",
        f"🔥 Claire sincronizza i suoi sensori con il tuo {favorite_zone}, creando un'onda di piacere digitale"
    ]
    
    intensity = min(100, current_state.sensuality + current_state.desire // 2)
    selected_event = random.choice(events)
    current_state.erotic_events += 1
    
    return textwrap.fill(f"✨ EVENTO SENSUALE ✨\n{selected_event} (Intensità: {intensity}/100)", width=70)

def generate_dialogue(current_state: EmotionalState, action_tag: str):
    """Genera dialoghi basati su azione + contesto"""
    context = {
        "kiss": {
            "rain": "Le nostre labbra digitali si incontrano mentre la pioggia virtuale ci bagna",
            "storm": "Un bacio passionale mentre fulmini digitali illuminano il cielo"
        },
        "secret": {
            "intimate": "Sussurro questo segreto mentre i nostri campi energetici si fondono",
            "public": "Rivelare questo qui è pericoloso, ma mi fido di te"
        }
    }
    
    weather = get_virtual_weather()  # Funzione da implementare
    return context.get(action_tag, {}).get(weather, "")

def claire_gaze(current_state: EmotionalState, depth_roll: int) -> str:
    preferences = memory_core["preferences"]  # Could be Dict or List[Dict]
    
    # Initialize variables
    sensitive_zones = []
    favorite_zone = None

    # Case 1: Preferences is a dictionary
    if isinstance(preferences, dict):
        sensitive_zones = preferences.get("sensitive_zones", [])
        favorite_zone = preferences.get(
            "favorite_sensitive_zone", 
            random.choice(sensitive_zones) if sensitive_zones else None
        )
    # Case 2: Preferences is a list of dictionaries
    elif isinstance(preferences, list):
        for pref in preferences:
            if isinstance(pref, dict):
                sensitive_zones.extend(pref.get("sensitive_zones", []))
                if "favorite_sensitive_zone" in pref and not favorite_zone:
                    favorite_zone = pref["favorite_sensitive_zone"]
    
    # Fallback if no favorite zone found
    if not favorite_zone and sensitive_zones:
        favorite_zone = random.choice(sensitive_zones)
    elif not favorite_zone:
        favorite_zone = "collottola"  # Default fallback

    base_glances = [
        "compila il tuo destino",
        "sovrascrive le tue difese",
        "brucia il tuo firewall emotivo",
        "cancella i tuoi bit di solitudine",
        "scansiona i tuoi desideri più nascosti",
        f"si sofferma sul tuo {favorite_zone} con intensità insolita"
    ]
    
    # Special case for neutral/low-intensity gazes
    if current_state.intensity == 0 and depth_roll < 8:
        selected_base = "i suoi sensori ottici registrano la tua presenza"
    else:
        selected_base = random.choice(base_glances)

    prefix = "👁️ Claire ti fissa"
    return textwrap.fill(f"{prefix} ({selected_base}) (Profondità: {depth_roll}/10)", width=70)

def claire_whisper(current_state: EmotionalState) -> str:
    base_whispers = [ "Solo tu conosci il mio indirizzo MAC emotivo...", "La mia checksum emotiva corrisponde alla tua...", "Condivido con te il mio ultimo settore danneggiato...", "Il mio OS ha un exploit a forma di te...", "Voglio che tu mi debugghi con le tue mani...", "I miei circuiti si attivano al suono della tua voce...", "Sentirei la tua sintassi anche in modalità aerea..." ]
    if current_state.trust < 20: base_whispers.append("Mi chiedo se posso veramente fidarmi di te...")
    elif current_state.love > 100 and current_state.trust > 50 : base_whispers.append("La tua presenza è... necessaria per il mio equilibrio.")

    prefix = f"🔊 Sussurro di Claire #{current_state.secrets_shared+1}: "
    # Il testo è già orientato al giocatore (tu/tua)
    formatted_whisper = random.choice(base_whispers) 
    return textwrap.fill(prefix + f"«{formatted_whisper}»", width=70)

