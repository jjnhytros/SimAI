def ensure_all_models_loaded() -> None:
    """Importa tutti i moduli che dichiarano modelli ORM."""
    from simai.needs import models as _needs_models  # noqa: F401
    from simai.sim import models as _sim_models  # noqa: F401
    from simai.world import models as _world_models  # noqa: F401
