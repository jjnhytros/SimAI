# Changelog

## [1.0.0] — 2026-10-20

### Aggiunto

- **Motore**: `run_tick` con ordine canonico
  `decadimento → mood → decisione → effetto`. Tick transazionale nel loop
  (`run_simulation`), con rollback su errore e autosave best-effort.
- **Tempo**: `SimState` persistente con `tick_index` e `master_seed`.
  Convenzione provvisoria `1 anno = 8760 tick` per i benchmark.
- **Mondo**: `Location` (casa, piazza, caffè), `Character` (5 personaggi,
  1 giocabile), `seed_muse_core` idempotente.
- **Bisogni**: `HUNGER`, `THIRST`, `FUN`, `INTIMACY` con decadimento per
  ora simulata e clamp 0–100.
- **Umore**: media pesata dei bisogni (HUNGER 0.25, THIRST 0.20,
  FUN 0.30, INTIMACY 0.25), ricalcolato a ogni tick.
- **Azioni**: EAT, DRINK, PLAY, SOCIALIZE con catalogo per location e
  soglie di bisogno (`max_need_to_start`).
- **Utility AI**: `choose_action` con scoring deterministico e jitter
  basato su seed + `character_id` + `tick_index`.
- **Relazioni**: `Relationship` direzionale FRIEND con strength 0–100.
  Seed Erika ↔ Max amici, `SOCIALIZE` con boost bilaterale.
- **Giocatore**: `player status`, `player do`, `player move`. Il player
  subisce decadimento ma non agisce automaticamente.
- **Persistenza**: SQLite + Alembic (migrazioni `0001`–`0008`),
  formato `.sav` binario con magic, versione, checksum sha256 e
  compressione zlib.
- **CLI**: `db`, `world`, `needs`, `actions`, `sim`, `player`,
  `relationships`, `save`, `i18n`, `version`.
- **Qualità**: 127 test veloci (unitari, integrazione DB, smoke CLI),
  1 test slow di 1 anno simulato, `ruff` + `mypy --strict` in CI,
  benchmark configurabile.
- **Errori comprensibili**: `require_schema` blocca i comandi su DB non
  inizializzato o non aggiornato con messaggio azionabile. Nessun
  traceback esposto all'utente.

### Note

- Il cooldown temporale introdotto in una fase intermedia è stato
  rimosso: le metriche peggioravano. Sostituito da soglie di bisogno.
- I limiti noti della 1.0 sono documentati in `docs/release/known-issues.md`.
