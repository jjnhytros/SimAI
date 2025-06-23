# core/data/world_map_data.py
from dataclasses import dataclass
from typing import List, Dict
from enum import Enum, auto

# Enum per i diversi tipi di trasporto tra distretti
class TransportType(Enum):
    WALK = auto()
    METRO_LINE_A = auto()
    METRO_LINE_B = auto()
    BUS_ROUTE_1 = auto()
    FERRY = auto()

# Dataclass per rappresentare un percorso
@dataclass
class Route:
    destination_id: str
    travel_time_minutes: int
    transport_type: TransportType

# Il nostro grafo del mondo. Le chiavi sono gli ID dei distretti/nodi.
# I valori sono una lista di percorsi che partono da quel nodo.
WORLD_GRAPH: Dict[str, List[Route]] = {
    # --- QUARTIERE DELLE MUSE ---
    "dist_muse_quarter": [
        Route("dist_central_hub", 15, TransportType.METRO_LINE_A),
        Route("dist_lakeshore_park", 20, TransportType.BUS_ROUTE_1),
    ],

    # --- DISTRETTO RESIDENZIALE DOSINVELOS ---
    "dist_dosinvelos": [
        Route("dist_central_hub", 10, TransportType.METRO_LINE_B),
        Route("dist_commercial", 15, TransportType.WALK),
    ],

    # --- HUB CENTRALE (Stazione Principale) ---
    "dist_central_hub": [
        Route("dist_muse_quarter", 15, TransportType.METRO_LINE_A),
        Route("dist_dosinvelos", 10, TransportType.METRO_LINE_B),
        Route("dist_financial_district", 5, TransportType.WALK),
    ],

    # --- PARCO RIVA DEL LAGO ---
    "dist_lakeshore_park": [
        Route("dist_muse_quarter", 20, TransportType.BUS_ROUTE_1),
        Route("dist_south_island_1", 30, TransportType.FERRY),
    ],
    
    # Esempi di altri distretti
    "dist_commercial": [
        Route("dist_dosinvelos", 15, TransportType.WALK),
    ],
    "dist_financial_district": [
        Route("dist_central_hub", 5, TransportType.WALK),
    ],
    "dist_south_island_1": [
        Route("dist_lakeshore_park", 30, TransportType.FERRY),
    ]
}

# Dizionario per i metadati dei distretti (nomi, descrizioni, etc.)
DISTRICT_METADATA = {
    "dist_muse_quarter": {"name": "Quartiere delle Muse", "description": "Il cuore artistico e bohémien di Anthalys."},
    "dist_dosinvelos": {"name": "Distretto Dosinvelos", "description": "Una zona residenziale tranquilla."},
    "dist_central_hub": {"name": "Hub Centrale", "description": "La principale stazione di interscambio di Anthalys."},
    "dist_lakeshore_park": {"name": "Parco Riva del Lago", "description": "Il polmone verde della città, affacciato sul Lacus Magnus."},
    # ...
}