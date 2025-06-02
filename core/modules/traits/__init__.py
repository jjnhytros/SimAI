# core/modules/traits/__init__.py
"""
Modulo per la gestione dei Tratti di Personalità degli NPC.
"""
from .base_trait import BaseTrait
from core.settings import DEBUG_MODE
# Quando avremo tratti concreti, li importeremo qui per renderli disponibili
# Esempio:
# from .ambitious_trait import AmbitiousTrait
# from .lazy_trait import LazyTrait

if DEBUG_MODE: print("  [modules/traits/__init__] Modulo Tratti caricato.")