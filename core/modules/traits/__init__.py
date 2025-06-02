# core/modules/traits/__init__.py
"""
Modulo per la gestione dei Tratti di Personalità degli NPC.
"""
from .base_trait import BaseTrait
from core.settings import DEBUG_MODE

from .active_trait import ActiveTrait
from .glutton_trait import GluttonTrait
from .loner_trait import LonerTrait
from .bookworm_trait import BookwormTrait

if DEBUG_MODE: print("  [modules/traits/__init__] Modulo Tratti caricato.")