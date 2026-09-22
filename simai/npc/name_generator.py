"""NameGenerator — nomi e cognomi in stile Anthalys.

Liste statiche in codice: nomi maschili, femminili e cognomi. La generazione
è deterministica via `random.Random` iniettato (mai `random` globale).
"""

from __future__ import annotations

import random

from simai.npc.enums import Sex

MALE_NAMES: tuple[str, ...] = (
    # Italiani
    "Leonardo",
    "Francesco",
    "Alessandro",
    "Lorenzo",
    "Mattia",
    "Tommaso",
    "Riccardo",
    "Gabriele",
    "Matteo",
    "Andrea",
    "Diego",
    "Marco",
    "Kevin",
    "Davide",
    "Antonio",
    "Giuseppe",
    "Pietro",
    "Samuele",
    "Federico",
    "Emanuele",
    "Nicolò",
    "Stefano",
    "Filippo",
    "Simone",
    "Ettore",
    "Enrico",
    "Cesare",
    "Augusto",
    "Rocco",
    "Dario",
    # Anthalys
    "Kaelen",
    "Varesh",
    "Theron",
    "Drion",
    "Zephyr",
    "Marcus",
    "Trystan",
    "Kael",
    "Cassian",
    "Orion",
    "Sirius",
    "Dorian",
    "Aldric",
    "Rhys",
    "Talon",
)

FEMALE_NAMES: tuple[str, ...] = (
    # Italiani
    "Sofia",
    "Giulia",
    "Aurora",
    "Alice",
    "Ginevra",
    "Emma",
    "Giorgia",
    "Greta",
    "Beatrice",
    "Anna",
    "Chiara",
    "Sara",
    "Martina",
    "Elisa",
    "Elena",
    "Maria",
    "Francesca",
    "Alessia",
    "Vittoria",
    "Matilde",
    "Rebecca",
    "Nicole",
    "Noemi",
    "Camilla",
    "Viola",
    "Bianca",
    "Ludovica",
    "Arianna",
    "Gaia",
    "Zoe",
    # Anthalys
    "Lirena",
    "Verala",
    "Xenna",
    "Aelith",
    "Cyre",
    "Nyra",
    "Zephyra",
    "Marisol",
    "Tessa",
    "Ilaria",
    "Kaelith",
    "Selene",
    "Elara",
    "Cyrille",
    "Ilyra",
)

LAST_NAMES: tuple[str, ...] = (
    # Italiani
    "Rossi",
    "Russo",
    "Ferrari",
    "Esposito",
    "Bianchi",
    "Romano",
    "Colombo",
    "Ricci",
    "Marino",
    "Greco",
    "Bruno",
    "Gallo",
    "Conti",
    "De Luca",
    "Mancini",
    "Costa",
    "Giordano",
    "Rizzo",
    "Lombardi",
    "Moretti",
    "Barbieri",
    "Fontana",
    "Santoro",
    "Mariani",
    "Rinaldi",
    "Caruso",
    "Ferrara",
    "Galli",
    "Martini",
    "Leone",
    # Anthalys
    "Lamborghetti",
    "Volpi",
    "Ferretti",
    "Vallieri",
    "Danesi",
    "Morelli",
    "Sarri",
    "Donati",
    "Ferro",
    "Aureli",
    "Sarti",
    "Pacini",
    "Varano",
    "Nevi",
    "Tassi",
    "Bandini",
    "Cerri",
    "Vasari",
    "Cavalieri",
    "Fornari",
)


class NameGenerator:
    """Genera nomi e cognomi in stile Anthalys, deterministici dal seed."""

    def __init__(
        self,
        *,
        male_names: tuple[str, ...] = MALE_NAMES,
        female_names: tuple[str, ...] = FEMALE_NAMES,
        last_names: tuple[str, ...] = LAST_NAMES,
    ) -> None:
        if not male_names or not female_names or not last_names:
            raise ValueError("Le liste di nomi non possono essere vuote")
        self._male = male_names
        self._female = female_names
        self._last = last_names

    # ------------------------------------------------------------------
    # Query liste
    # ------------------------------------------------------------------

    @property
    def male_names(self) -> tuple[str, ...]:
        return self._male

    @property
    def female_names(self) -> tuple[str, ...]:
        return self._female

    @property
    def last_names(self) -> tuple[str, ...]:
        return self._last

    # ------------------------------------------------------------------
    # Generazione
    # ------------------------------------------------------------------

    def generate_first_name(self, rng: random.Random, sex: Sex) -> str:
        """Nome proprio in base al sesso."""
        if sex is Sex.MALE:
            return rng.choice(self._male)
        if sex is Sex.FEMALE:
            return rng.choice(self._female)
        # Intersex: nome da una delle due liste
        pool = self._male + self._female
        return rng.choice(pool)

    def generate_last_name(self, rng: random.Random) -> str:
        """Cognome."""
        return rng.choice(self._last)

    def generate_full_name(self, rng: random.Random, sex: Sex) -> tuple[str, str]:
        """(first_name, last_name)."""
        return (
            self.generate_first_name(rng, sex),
            self.generate_last_name(rng),
        )


__all__ = [
    "FEMALE_NAMES",
    "LAST_NAMES",
    "MALE_NAMES",
    "NameGenerator",
]
