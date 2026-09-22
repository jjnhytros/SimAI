# SimAI — Documentazione

Panoramica del progetto **SimAI**, simulazione di vita ad agenti
ambientata nel mondo di **Anthalys**.

## Indice

- [`lore/`](./lore/) — lore di Anthalys (Costituzione, festività, cicli di vita)
- `cicli-vita.md` — fasce di età Anthaliane (in preparazione, FASE 1)
- `architettura.md` — architettura tecnica (in preparazione)

## Stato attuale

**FASE 0 — Setup iniziale** ✅

- [x] Struttura progetto Python
- [x] Configurazione `pydantic-settings`
- [x] Costanti calendario Anthalys
- [x] Logging Loguru
- [x] Base SQLAlchemy 2.0 + session factory
- [x] CLI Typer con comandi `version` e `info`
- [x] Alembic inizializzato
- [x] CI GitHub Actions (lint + typecheck)

## Prossimo step

**FASE 1 — Core Simulation** (range migrazioni 5000–5099):

- `AnthalysDateTime`, `AnthalysCalendar`, `TimeManager`
- `SimulationLoop`, `EventBus`, `SaveManager`
- Primitive `DayPhase`, `Season`

## Convenzioni

- **Naming migrazioni**: `NNNN_SS_slug.py` (vedi `TODO.md` §3)
- **Commit**: Conventional Commits (hook in `scripts/hooks/commit-msg`)
- **Versioning**: SemVer 2.0.0
- **Changelog**: Keep a Changelog
- **No-test policy**: attiva