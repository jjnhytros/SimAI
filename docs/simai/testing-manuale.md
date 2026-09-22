# Test manuale — SimAI

**No-test policy**: nessun test automatico. Verifica manuale documentata.

## Convenzioni di calcolo

- 1 tick = `SIMAI_TICK_MINUTES` minuti Anthalys (default: 5)
- 1 ora Anthalys = 60 minuti = 12 tick (default)
- 1 giorno Anthalys = 28 ore = 1680 minuti = **336 tick** (default)
- 1 mese Anthalys = 24 giorni = 8064 tick
- 1 anno Anthalys = 432 giorni = 145152 tick

## Verifica Chunk 1.0 — Time Manager

### 1. Avanzamento base

```bash
uv run python -m simai sim time show
uv run python -m simai sim time advance 100
uv run python -m simai sim time advance 400
uv run python -m simai sim time advance 10000
uv run python -m simai sim time advance 150000