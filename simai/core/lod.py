"""LOD (Level of Detail) per gli NPC.

Da TODO §1.1: ogni NPC ha un LOD che cambia dinamicamente in base alla
rilevanza. `npc_manager.update_all_npcs()` può saltare gli NPC in BACKGROUND.
"""

from enum import IntEnum


class LODLevel(IntEnum):
    """Livello di dettaglio simulativo di un NPC.

    Eredita da `IntEnum` per consentire ordinamento diretto:
    ``BACKGROUND < REDUCED < FULL``.
    """

    BACKGROUND = 0
    REDUCED = 1
    FULL = 2

    @property
    def is_simulated(self) -> bool:
        """``True`` se l'NPC richiede update ogni tick (FULL o REDUCED)."""
        return self is not LODLevel.BACKGROUND

    @property
    def is_full(self) -> bool:
        """``True`` solo se LOD è FULL."""
        return self is LODLevel.FULL


# ---------------------------------------------------------------------------
# Soglie di default (configurabili in futuro via config globale)
# ---------------------------------------------------------------------------

#: Distanza in hop entro cui un NPC è considerato "nel focus" -> FULL.
FULL_DISTANCE_THRESHOLD: int = 1

#: Distanza in hop entro cui un NPC è simulato a dettaglio ridotto -> REDUCED.
#: Oltre questa soglia -> BACKGROUND.
REDUCED_DISTANCE_THRESHOLD: int = 3


def lod_from_distance(distance_hops: int) -> LODLevel:
    """Calcola il LOD da una distanza in hop dal "focus" della simulazione.

    Regole:
      - ``distance <= FULL_DISTANCE_THRESHOLD``    -> FULL
      - ``distance <= REDUCED_DISTANCE_THRESHOLD`` -> REDUCED
      - altrimenti                                  -> BACKGROUND

    Se in futuro la logica diventa più complessa (priorità evento, mood,
    coinvolgimento in quest, ecc.), questa funzione rimane il punto di
    estensione unico.
    """
    if distance_hops < 0:
        raise ValueError(f"distance_hops deve essere >= 0, ricevuto {distance_hops}")
    if distance_hops <= FULL_DISTANCE_THRESHOLD:
        return LODLevel.FULL
    if distance_hops <= REDUCED_DISTANCE_THRESHOLD:
        return LODLevel.REDUCED
    return LODLevel.BACKGROUND
