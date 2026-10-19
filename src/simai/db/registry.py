def ensure_all_models_loaded() -> None:
    """Importa tutti i moduli che dichiarano modelli ORM.

    Va chiamato prima di leggere `Base.metadata`, così Alembic e
    autogenerate vedono l'intero schema.
    """
    from simai.world import models as _world_models  # noqa: F401