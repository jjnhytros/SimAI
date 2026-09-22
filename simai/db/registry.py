"""Registro centralizzato dei modelli SQLAlchemy di SimAI.

Garantisce che **tutti** i modelli (db, npc, world, economy, ...) siano caricati
in `Base.metadata` prima di qualsiasi query SQLAlchemy.

Il problema: se un chiamante fa `from simai.npc import NPCManager` senza
mai importare `simai.world`, SQLAlchemy non conosce la tabella `location`,
e `character.location_id -> location.id` resta irrisolvibile.

Soluzione: `ensure_all_models_loaded()` importa (side-effect) tutti i moduli
di modelli e chiama `configure_mappers()`. Idempotente e sicuro da chiamare
più volte.

Viene invocato automaticamente in `simai.db.session._build_engine()`.
"""

from __future__ import annotations

#: Flag di idempotenza. Privato ma globale a livello di modulo: `global _loaded`
#: dentro la funzione lo modifica.
_loaded: bool = False


def ensure_all_models_loaded() -> None:
    """Importa tutti i modelli SimAI e configura i mapper. Idempotente."""
    global _loaded
    if _loaded:
        return

    # Import side-effect: popolano Base.metadata.
    from sqlalchemy.orm import configure_mappers

    from simai.city import models as _city_models  # noqa: F401
    from simai.city.infrastructure import models as _infra_models  # noqa: F401
    from simai.city.transport import models as _transport_models  # noqa: F401
    from simai.city.transport import transit as _transit_models  # noqa: F401
    from simai.db import models as _db_models  # noqa: F401
    from simai.economy import models as _eco_models  # noqa: F401
    from simai.economy import property as _prop_models  # noqa: F401
    from simai.economy.aion import models as _aion_models  # noqa: F401
    from simai.economy.banking import models as _bank_models  # noqa: F401
    from simai.economy.companies import models as _company_models  # noqa: F401
    from simai.economy.ledger import models as _ledger_models  # noqa: F401
    from simai.npc import models as _npc_models  # noqa: F401
    from simai.npc.addictions import models as _add_models  # noqa: F401
    from simai.npc.background import models as _bg_models  # noqa: F401
    from simai.npc.economy import models as _npc_eco_models  # noqa: F401
    from simai.npc.lifecycle import pregnancy as _preg_models  # noqa: F401
    from simai.npc.memory import models as _mem_models  # noqa: F401
    from simai.npc.reflection import models as _refl_models  # noqa: F401
    from simai.npc.relationships import models as _rel_models  # noqa: F401
    from simai.npc.reputation import models as _rep_models  # noqa: F401
    from simai.npc.skills import models as _skills_models  # noqa: F401
    from simai.npc.stats import models as _stats_models  # noqa: F401
    from simai.world import district as _district_models  # noqa: F401
    from simai.world import lot as _lot_models  # noqa: F401
    from simai.world import models as _world_models  # noqa: F401
    from simai.world.build import models as _build_models  # noqa: F401
    from simai.world.buy import models as _buy_models  # noqa: F401
    from simai.world.style import models as _style_models  # noqa: F401
    from simai.world.terrain import models as _terrain_models  # noqa: F401

    configure_mappers()
    _loaded = True


__all__ = ["ensure_all_models_loaded"]
