# core/enums/service_types.py
from enum import Enum

class ServiceType(Enum):
    """Definisce i tipi di servizi SoNet a cui un NPC può accedere."""
    AMORI_CURATI_PHASE1 = "Amori Curati Fase 1"
    AMORI_CURATI_PHASE2 = "Amori Curati Fase 2"
    FRIEND_CONNECT = "Trova Amici"