"""Package `simai.npc.stats` — statistiche popolazione."""

from simai.npc.stats.models import PopulationCensus
from simai.npc.stats.service import LiveStats, PopulationStatsService

__all__ = ["LiveStats", "PopulationCensus", "PopulationStatsService"]
