# SimAI — Simulazione di Anthalys

**Simulazione di vita ad agenti** ambientata nel mondo di **Anthalys**.
Motore Python 3.13+, SQLAlchemy 2.0, FastAPI opzionale, UI offline-first.

[![CI](https://github.com/<TUO-USER>/<TUO-REPO>/actions/workflows/ci.yml/badge.svg)](https://github.com/<TUO-USER>/<TUO-REPO>/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

## Cosa è

SimAI è una **simulazione di vita multi-agente** dove NPC autonomi nascono, crescono, lavorano, si innamorano, commerciano, si ammalano e muoiono in un mondo persistente chiamato **Anthalys**. Il calendario è custom (432 giorni, 18 mesi, 28 ore/giorno), l'economia è double-entry (ledger SQL), i trasporti sono multi-modali, e la piattaforma di commercio **AION** è un marketplace multivendor gestito da AI.

## Stack

| Componente | Tool |
|---|---|
| Runtime | CPython 3.13+ |
| ORM | SQLAlchemy 2.0 |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| CLI | Typer + Rich |
| Web UI | FastAPI + Jinja2 |
| Logging | Loguru |
| Type check | mypy strict + ruff strict |
| Dep manager | **uv** |
| DB | SQLite (PostgreSQL opzionale) |

## Installazione

```bash
# 1. Clona
git clone https://github.com/<TUO-USER>/<TUO-REPO>.git
cd <TUO-REPO>

# 2. Installa uv (se non presente)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 3. Sincronizza dipendenze (incl. extra UI)
uv sync --extra ui

# 4. Copia .env.example → .env
cp .env.example .env

# 5. Migra il DB
uv run python -m simai db upgrade

# 6. Popola il mondo demo
uv run python -m simai world seed
uv run python -m simai npc seed
uv run python -m simai economy seed
uv run python -m simai economy company seed
uv run python -m simai economy aion seed

# 7. Verifica
uv run python -m simai version
