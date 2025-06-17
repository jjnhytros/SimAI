# core/AI/claire/claire_config.py
from core.enums import MoodletType

# Mappa un Moodlet a una o più possibili risposte di Claire
CLAIRE_MOODLET_RESPONSES = {
    MoodletType.BORED: [
        "L'aria è ferma qui dentro. Forse è il momento di farla muovere.",
        "Sento una quiete che non è pace. È attesa.",
        "C'è un mondo fuori da questa stanza. O dentro un libro."
    ],
    MoodletType.LONELY: [
        "Non sei solo in questo silenzio.",
        "Questa sensazione... la conosco. Ma passa, come le nuvole.",
        "A volte, la persona che più ci manca siamo noi stessi."
    ],
    MoodletType.STRESSED: [
        "Respira. Un momento alla volta. Solo questo.",
        "Il peso che senti non è solo tuo. Lascia che ne prenda un po'.",
    ],
    # Aggiungeremo qui altre reazioni...
}