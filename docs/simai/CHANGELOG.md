# Changelog

Tutte le modifiche rilevanti a SimAI sono documentate in questo file.

Il formato segue [Keep a Changelog](https://keepachangelog.com/it/1.1.0/)
e il progetto aderisce a [Semantic Versioning](https://semver.org/lang/it/).

## [Unreleased]

### Added
- Struttura iniziale del progetto Python (`simai/`).
- Configurazione `pydantic-settings` in `simai/config/settings.py`.
- Costanti calendario e stagioni di Anthalys in `simai/config/anthalys.py`.
- Logging Loguru in `simai/config/logging.py`.
- Base SQLAlchemy 2.0 (`Base`, `IdMixin`, `TimestampMixin`) in `simai/db/base.py`.
- Session factory e context manager `session_scope()` in `simai/db/session.py`.
- CLI Typer con comandi `version` e `info` in `simai/cli/app.py`.
- Configurazione Alembic (`alembic.ini`, `alembic/env.py`, `script.py.mako`).
- CI GitHub Actions per lint (`ruff`) e type check (`mypy`).
- Documentazione iniziale in `docs/simai/`.
- Hook Git `commit-msg` per Conventional Commits.

[Unreleased]: https://github.com/simai-project/simai/compare/v0.0.0...HEAD
