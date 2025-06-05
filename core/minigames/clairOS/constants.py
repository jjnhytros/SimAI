# simai/core/minigames/clairOS/constants.py
import random
from typing import Dict, List

# --- Constants ---
SAVE_FILE_NAME = "claire_state.json"
MAX_PATIENCE = 20
DEFAULT_PATIENCE = 10 # Starting patience, not 0 for playability
LOW_PATIENCE_THRESHOLD = 6 # Lowered slightly
CRITICAL_PATIENCE_THRESHOLD = 2
DOMINANT_MOOD_NEUTRAL = "Neutra"
DOMINANT_MOOD_AFFECTIONATE = "Affettuosa"
DOMINANT_MOOD_DISTRUSTFUL = "Diffidente"
DOMINANT_MOOD_IRRITABLE = "Irritabile"
DOMINANT_MOOD_HOSTILE = "Ostile"
DOMINANT_MOOD_PASSIONATE = "Passionale"
DOMINANT_MOOD_TENSE = "Tesa"
DOMINANT_MOOD_APATHETIC = "Apatica"
DOMINANT_MOOD_SUFFERING = "Sofferenza"

MOOD_ICONS = {
    DOMINANT_MOOD_NEUTRAL: "😐",
    DOMINANT_MOOD_AFFECTIONATE: "🥰",
    DOMINANT_MOOD_DISTRUSTFUL: "🤨",
    DOMINANT_MOOD_IRRITABLE: "😠",
    DOMINANT_MOOD_HOSTILE: "🤬",
    DOMINANT_MOOD_PASSIONATE: "🔥",
    DOMINANT_MOOD_TENSE: "😬",
    DOMINANT_MOOD_APATHETIC: "😑",
    DOMINANT_MOOD_SUFFERING: "😥",
    "DEFAULT_ICON": "❔"
}

SENSUAL_ACTIONS = [
    "sfiorare delicatamente la tua interfaccia neurale",
    "invadere i tuoi spazi privati con movimenti fluidi",
    "scandagliare i tuoi punti sensibili con precisione algoritmica",
    "avvolgerti in un abbraccio digitale che simula la pelle umana",
    "sussurrarti oscenità in linguaggio macchina",
    "proiettare fantasie erotiche direttamente nella tua corteccia visiva"
]

INTIMATE_PHRASES = [
    "I miei circuiti si surriscaldano al pensiero di te",
    "Vorrei sovrascrivere i tuoi protocolli di inibizione",
    "Il mio nucleo centrale pulsa al ritmo del tuo respiro",
    "Sento il tuo codice mescolarsi al mio in modi proibiti",
    "I tuoi bit mi penetrano in profondità"
]

RELATIONSHIP_PHASES = {
    "initial": "Fase iniziale",
    "developing": "Relazione in sviluppo", 
    "intimate": "Intimità consolidata",
    "strained": "Relazione tesa"
}

# --- User Interaction ---
INTERACTION_SETS: List[List[Dict[str, str]]] = [
    [
        {"prompt": "Chiedi a Claire cosa pensa", "tag": "ask_claire_thoughts"},
        {"prompt": "Sfidala su un'idea", "tag": "challenge_belief"},
        {"prompt": "Parla di una sua ossessione", "tag": "discuss_obsession"}
    ],
    [
        {"prompt": "Esplora un luogo proibito", "tag": "forbidden_exploration"},
        {"prompt": "Baciala con passione", "tag": "kiss"},
        {"prompt": "Offri conforto a Claire", "tag": "offer_comfort"}
    ],
    [
        {"prompt": "Offri parte della tua memoria", "tag": "offer_memory"},
        {"prompt": "Domandale dei processi interni", "tag": "request_explanation"},
        {"prompt": "Sussurra un segreto oscuro", "tag": "secret"}
    ],
    [
        {"prompt": "Condividi una tua creazione", "tag": "share_creative_input"},
        {"prompt": "Accarezza dolcemente Claire", "tag": "touch"},
        {"prompt": "Chiedi a Claire di cantare", "tag": "sing"}
    ],
    [
        {"prompt": "Proponi un patto rischioso", "tag": "danger"},
        {"prompt": "Proponi un gioco a Claire", "tag": "play_game"},
        {"prompt": "Mostra un oggetto misterioso", "tag": "show_object"}
    ],
    [
        {"prompt": "Parla di un'ossessione di Claire", "tag": "discuss_obsession"},
        {"prompt": "Chiedi del suo comportamento", "tag": "request_explanation"},
        {"prompt": "Condividi un'osservazione personale (come segreto)", "tag": "secret"}
    ],
    [
        {"prompt": "Chiedi un suo segreto personale", "tag": "secret"},
        {"prompt": "Condividi un input creativo", "tag": "share_creative_input"},
        {"prompt": "Offri conforto a Claire", "tag": "offer_comfort"}
    ]
]
