# Changelog

## [1.1.0] — 2026-10-20

### Aggiunto

- **Economia minima**: `Character.balance`, `Job` (1:1 con personaggio),
  `Transaction` (append-only con `from`/`to` nullable per "world").
  Migrazione `0010`.
- **Payday**: a fine giornata convenzionale (tick 23, 47, 71, ...),
  ogni personaggio con job riceve `daily_wage` e viene registrata una
  `Transaction` `SALARY`.
- **Costi per azione**: `ActionDef.cost`. EAT a caffè 3, DRINK a caffè 2,
  PLAY a caffè 4. EAT/DRINK/PLAY a casa e PLAY in piazza gratis.
  `DRINK` a casa (acqua) esiste: `amount=15, cost=0`.
- **Filtro affordabilità**: `choose_intent` e `do_action` escludono
  azioni con `cost > balance`. `balance` non scende mai sotto zero.
- **CLI `economy`**: `balance`, `ledger`, `jobs`.
- **`PlayerStatus.balance`**: mostrato in `player status`.
- **`sim tick` / `sim run`**: mostrano payday quando avvengono.
- **Benchmark**: colonna `balance` (mean/min/max), contatori
  `salary_transactions` e `purchase_transactions` nel report.

### Cambiato

- `CATALOG` ha più istanze per `ActionKind` (EAT casa vs caffè, DRINK
  casa vs caffè, PLAY piazza vs caffè). Il filtro per location in
  `actions_for_location` resta l'unico modo corretto di accedervi.
- `tests/test_utility.py::test_actions_for_residential` aggiornato:
  `{EAT, DRINK, PLAY}`.
- `tests/test_movement_in_tick.py`: il movimento NPC scatta da
  `piazza` (dove manca `DRINK`), non più da `casa`.

### Risultato misurato (87 tick, seed 42)

Da verificare con `sim benchmark` dopo merge. Atteso:

- tutti i `balance` finali > 0
- `salary_transactions = 3 × 5 = 15` (3 payday in 87 tick)
- `purchase_transactions ≥ 10`
- nessun invariante violato

### Limiti noti

- **Lavoro fisico non simulato**: gli NPC hanno un `Job` con location
  e orario, ma non si recano fisicamente al lavoro. Lo stipendio viene
  pagato ovunque si trovino.
- **Nessuna tassazione**: salario lordo, prezzi netti.
- **Nessun supporto familiare**: Erika e Max hanno wage 5
  ("paghetta"). Nessun trasferimento di denaro tra personaggi.
- **Nessun inventario**: il caffè vende "un drink" astratto, non merce.

## [1.0.1] — 2026-10-20

### Aggiunto

- **Movimento NPC**: gli NPC si spostano verso un'altra location quando
  un bisogno sotto soglia non è soddisfacibile dove si trovano. Utility
  AI estesa con `choose_intent` (azione locale vs. movimento). Costo
  distanza uniforme (5.0). Gli NPC non tornano a casa dopo.
- **Moodlet**: 3 eventi temporanei (`ATE_WELL`, `SOCIALIZED`, `LONELY`)
  con durata in tick, delta per tick e refresh (non somma). `LONELY`
  scatta dopo 3 tick consecutivi con `INTIMACY < 20`.
- **`Character.low_intimacy_streak`**: contatore persistente per il
  trigger di `LONELY`. Migrazione `0009`.
- **Tabella `moodlets`** con serializzazione in `.sav`.

### Cambiato

- `mood` include i moodlet attivi al tick corrente.
- `run_tick` esegue: decadimento → decisioni → azioni/movimenti →
  moodlet → mood → cleanup.

### Risultato misurato

- Benchmark 87 tick (seed 42), pre-1.0.1 → post-1.0.1:
  - Erika: mood 49.9 → **69.6**, thirst media 18.4 → **66.0**
  - Max: mood 56.0 → **68.7**, thirst media 18.4 → **66.0**
  - Giulia: mood 56.0 → **65.7**, thirst media 18.4 → **60.0**
  - Luca: mood 69.3 → 66.0, thirst media 66.0 → **54.0**

### Limiti noti

- Gli NPC non tornano a casa dopo essersi spostati. Un NPC che va al
  caffè per bere ci resta finché un altro bisogno critico non lo sposta
  altrove. "Routine" e "casa" sono 1.1.
- Luca peggiora leggermente su thirst perché si sposta via dal caffè
  per altri bisogni.

---

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
