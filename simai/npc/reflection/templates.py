"""Template-based text generation per riflessioni.

Nessun LLM: compone frasi da elementi di stato + memorie recenti.
"""

from __future__ import annotations

import random
from typing import Final

from simai.npc.models import Character
from simai.npc.reflection.enums import ReflectionKind

#: Aperture per kind.
_OPENINGS: Final[dict[ReflectionKind, tuple[str, ...]]] = {
    ReflectionKind.GRATITUDE: (
        "Oggi mi sento grato",
        "Una giornata da ricordare",
        "Qualcosa di buono è successo",
        "Mi sento fortunato",
    ),
    ReflectionKind.REGRET: (
        "Avrei potuto fare meglio",
        "Ripenso a quello che è successo",
        "C'è qualcosa che mi pesa",
        "Non è andata come speravo",
    ),
    ReflectionKind.RESOLVE: (
        "Ho deciso di cambiare",
        "Da domani voglio",
        "Mi impegno a",
        "Voglio provare",
    ),
    ReflectionKind.OBSERVATION: (
        "Noto che",
        "Mi accorgo che",
        "Osservo in me",
        "Percepisco",
    ),
    ReflectionKind.CRISIS: (
        "Non so più chi sono",
        "Tutto sembra crollare",
        "Mi sento perso",
        "Sono in un pozzo profondo",
    ),
    ReflectionKind.RECOVERY: (
        "Riemergo lentamente",
        "Le cose iniziano a chiarirsi",
        "Torno a respirare",
        "Il peggio è passato",
    ),
}

#: Osservazioni su tratti.
_TRAIT_OBSERVATIONS: Final[dict[str, str]] = {
    "Gentile": "sono più gentile con chi mi sta intorno",
    "Curioso": "la curiosità mi guida sempre",
    "Timido": "faccio fatica ad aprirmi",
    "Atletico": "il corpo ha bisogno di muoversi",
    "Intellettuale": "la mente cerca risposte",
    "Artistico": "l'arte mi chiama",
    "Ribelle": "le regole mi stanno strette",
    "Empatico": "sento le emozioni degli altri",
    "Ambizioso": "voglio di più",
    "Riflessivo": "penso troppo",
    "Spensierato": "prendo la vita alla leggera",
    "Ordinato": "l'ordine mi dà pace",
    "Creativo": "nuove idee mi attraversano",
    "Leale": "non tradirò chi mi è caro",
    "Impulsivo": "agisco prima di pensare",
    "Ottimista": "vedo il buono ovunque",
    "Pessimista": "il peggio è sempre dietro l'angolo",
    "Sognatore": "immagino mondi migliori",
    "Pratico": "conto sui fatti, non sulle parole",
    "Sociale": "ho bisogno di stare con gli altri",
    "Riservato": "preferisco la mia solitudine",
    "Coraggioso": "non mi tiro indietro",
    "Prudente": "misuro ogni passo",
    "Testardo": "non cambio idea facilmente",
    "Generoso": "dare mi fa stare bene",
    "SexuallyExplorative": "cerco nuove esperienze",
    "EmotionallyExpressive": "dico ciò che sento",
}


def compose_reflection(
    character: Character,
    *,
    kind: ReflectionKind,
    rng: random.Random,
    context: dict[str, object] | None = None,
) -> tuple[str, float]:
    """Compone una frase di riflessione.

    Ritorna `(text, sentiment)` con sentiment in [-1, 1].
    """
    opening = rng.choice(_OPENINGS[kind])

    # Scegli un corpo tematico
    body_parts: list[str] = []

    # Tratto casuale
    traits = list(character.traits_json or [])
    if traits and rng.random() < 0.5:
        trait = rng.choice(traits)
        obs = _TRAIT_OBSERVATIONS.get(trait)
        if obs:
            body_parts.append(obs)

    # Contesto (memorie, eventi)
    if context:
        memory_text = context.get("memory_text")
        if isinstance(memory_text, str) and memory_text:
            body_parts.append(f"penso a {memory_text}")
        goal = context.get("goal")
        if isinstance(goal, str) and goal:
            body_parts.append(f"voglio {goal}")
        loss = context.get("loss")
        if isinstance(loss, str) and loss:
            body_parts.append(f"mi manca {loss}")

    if not body_parts:
        body_parts.append("il tempo scorre")

    body = rng.choice(body_parts)
    text = f"{opening}: {body}."

    sentiment = _sentiment_for(kind, rng)
    return text, sentiment


def _sentiment_for(kind: ReflectionKind, rng: random.Random) -> float:
    ranges: dict[ReflectionKind, tuple[float, float]] = {
        ReflectionKind.GRATITUDE: (0.4, 0.9),
        ReflectionKind.REGRET: (-0.8, -0.3),
        ReflectionKind.RESOLVE: (0.1, 0.5),
        ReflectionKind.OBSERVATION: (-0.2, 0.2),
        ReflectionKind.CRISIS: (-1.0, -0.7),
        ReflectionKind.RECOVERY: (0.3, 0.7),
    }
    lo, hi = ranges.get(kind, (-0.2, 0.2))
    return rng.uniform(lo, hi)


__all__ = ["compose_reflection"]
