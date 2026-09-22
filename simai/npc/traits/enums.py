"""Enum del dominio tratti e aspirazioni."""

from enum import StrEnum


class TraitCategory(StrEnum):
    """Categoria di un tratto (da TODO §03.0102)."""

    SOCIAL = "SOCIAL"
    PERSONALITY = "PERSONALITY"
    MENTAL = "MENTAL"
    LIFESTYLE = "LIFESTYLE"
    PHYSICAL = "PHYSICAL"


class Trait(StrEnum):
    """Tratti di personalità di Anthalys.

    Allineati con le stringhe storiche del `TRAITS_POOL` per retrocompatibilità.
    Ogni tratto appartiene a una famiglia genetica (`TraitFamily`) e ha una
    soglia poligenica per l'attivazione.
    """

    # Famiglia SOCIAL
    GENTILE = "Gentile"
    EMPATICO = "Empatico"
    SOCIALE = "Sociale"
    GENEROSO = "Generoso"
    LEALE = "Leale"
    RISERVATO = "Riservato"

    # Famiglia MENTAL
    INTELLETTUALE = "Intellettuale"
    CURIOSO = "Curioso"
    RIFLESSIVO = "Riflessivo"
    ORDINATO = "Ordinato"
    SOGNATORE = "Sognatore"
    TIMIDO = "Timido"

    # Famiglia PHYSICAL
    ATLETICO = "Atletico"
    CORAGGIOSO = "Coraggioso"
    IMPULSIVO = "Impulsivo"
    RIBELLE = "Ribelle"

    # Famiglia CREATIVE
    ARTISTICO = "Artistico"
    CREATIVO = "Creativo"
    SPENSIERATO = "Spensierato"

    # Famiglia PRACTICAL
    PRATICO = "Pratico"
    AMBIZIOSO = "Ambizioso"
    PRUDENTE = "Prudente"
    TESTARDO = "Testardo"
    OTTIMISTA = "Ottimista"
    PESSIMISTA = "Pessimista"

    # Famiglia CREATIVE (aperta)
    SEXUALLY_EXPLORATIVE = "SexuallyExplorative"

    # Famiglia SOCIAL (apertura emotiva)
    EMOTIONALLY_EXPRESSIVE = "EmotionallyExpressive"


class TraitFamily(StrEnum):
    """Famiglia genetica di un tratto (mappa 1:1 a una sotto-categoria loci)."""

    SOCIAL = "TRAITS_SOCIAL"
    MENTAL = "TRAITS_MENTAL"
    PHYSICAL = "TRAITS_PHYSICAL"
    CREATIVE = "TRAITS_CREATIVE"
    PRACTICAL = "TRAITS_PRACTICAL"


class Aspiration(StrEnum):
    """Aspirazione di vita di un Character."""

    FAMILY = "FAMILY"
    CAREER = "CAREER"
    KNOWLEDGE = "KNOWLEDGE"
    CREATIVITY = "CREATIVITY"
    FAME = "FAME"
    WEALTH = "WEALTH"
    LOVE = "LOVE"
    FITNESS = "FITNESS"


__all__ = ["Aspiration", "Trait", "TraitCategory", "TraitFamily"]
