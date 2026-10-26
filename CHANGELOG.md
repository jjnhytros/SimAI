# Changelog

## [1.3.1] — 2026-10-26

### Corretto (documentale)

- Aggiunto `docs/release/1.3.0-plan.md` retroattivo: il tag v1.3.0
  era stato creato senza piano scritto. Il piano è ricostruito da
  CHANGELOG, diff del codice e benchmark.
- CHANGELOG `[1.3.0]`: la sezione "Prossimi passi (A2)" diceva che i
  modificatori dei tratti andavano ancora applicati in `decay_value`
  e `score`. Erano già applicati. Sostituita con i numeri del 10y.
- README "Stato del progetto": stessa incoerenza su A2. Allineato al
  codice.
- `known-issues.md`: aggiunte §4 (limiti dei tratti) e §5
  (`check.sh` cancella `data/` senza flag).
- `pyproject.toml` e `__version__.py` bumpati a 1.3.1.

### Non incluso

- Nessuna modifica al codice del motore. La 1.3.1 è puramente
  documentale.

## [1.3.0] — 2026-10-26

### Aggiunto

- **Tratti**: `Character.traits` (JSON list). 5 tratti:
  LAZY, ENERGETIC, SOCIAL, SOLITARY, GLUTTON.
- Modificatori di decadimento (`trait_decay_multiplier`) e di utility
  (`trait_utility_bonus`), `trait_move_penalty`.
- Seed: erika=SOLITARY, max=ENERGETIC, luca=SOCIAL,
  giulia=LAZY+GLUTTON, player=nessuno.
- Migrazione `0012_traits`.
- CLI `simai npc traits -c <key>`.
- `player status` mostra `Tratti:`.
- `save`/`load` preserva `traits`.

### Verificato (10y, seed 42)

- Modificatori **applicati** in `decay_value`, `score`, `_move_score`
  (non solo definiti).
- Benchmark `10y-1.3.0.json` archiviato: 77.3 tick/s, invarianti OK,
  `job_attendance_rate 1.0` su tutti gli NPC.
- Mood medio: erika 68.06, max 68.26, luca 68.14, giulia 67.75
  (stabile vs 1.2.1: 67.87 / 68.02 / 68.13 / 67.97).
- Effetto dei tratti sui dati: < 1 punto su `fun_mean`/`intimacy_mean`.
Accettato, documentato in `known-issues.md` §4.1.
---

## [1.2.1] — 2026-10-26

### Aggiunto

- **Fontanella e panino a piazza**: `DRINK` gratis (fontanella,
  amount 15), `EAT` a 2 Athel (panino). Giulia passa da 80% a
  100% di attendance.
- **Routine serale**: `Character.home_location_id`. Dopo il turno,
  se `INTIMACY >= 40` e `FUN >= 40`, l'NPC torna a casa. Se no,
  resta dove può socializzare. Evita il crollo delle relazioni
  dopo il lavoro.
- Migrazione `0011_home_location`.

### Risultato misurato (3 anni, seed 42)

- Attendance 100% per tutti i 4 NPC.
- Mood: erika 68.4, max 68.1, luca 71.3, giulia 68.1.
- Salary: 4380 (esattamente 4 × 365 × 3).

### Limiti noti

- Nessun ciclo sonno/veglia. Gli NPC tornano a casa ma restano
  svegli. 1.3 con calendario Anthalys.

---

## [1.2.0] — 2026-10-25

### Aggiunto

- **Lavoro fisico**: `WorkState` (BEFORE_WORK, WORKING, AFTER_WORK,
  NO_JOB). `should_prioritize_work` con `PRIORITY_WINDOW=2` e
  salvaguardia `HUNGER < 10`.
- **Priorità lavoro in `run_tick`**: se mancano ≤2 tick all'inizio
  del turno e hunger ≥ 10, l'NPC si muove verso `job.location_key`.
  Se già lì, nessun move.
- **Payday con presenza fisica**: `process_payday` paga solo chi è
  nella location del lavoro al tick di payday. `PaydayReport` con
  `paid`, `absent`, `absent_keys`.
- **Osservabilità**:
  - `sim tick` / `sim run`: `💰 Payday: N pagati, M assenti (keys)`.
  - `economy jobs`: stato corrente (al lavoro / in attesa / fuori orario).
  - `player status`: `Lavoro: barista (al lavoro)`.
  - `BenchmarkReport`: `CharacterMetrics.job_attendance_rate`.

### Cambiato

- `TickReport.payday_count` → `TickReport.payday` (`PaydayReport`).
- `RunReport.total_paydays` = somma di `payday.paid`.

### Risultato misurato (1 anno, seed 42)

Da eseguire post-A2. Atteso: `job_attendance_rate > 0.80` per tutti
gli NPC con wage > 0. Player a casa di default: 0%.

### Limiti noti

- Gli NPC non tornano a casa dopo il lavoro. Se al lavoro possono
  soddisfare i bisogni, restano lì. Routine serale in 1.2.1.
- Il player deve gestire il lavoro attivamente. Nessun auto-work.

---

## [1.1.1] — 2026-10-21

### Corretto

- **Decadimento bisogni ridotto** da 20.0 a 13.5 per ora simulata
  (HUNGER 4.0, THIRST 5.0, FUN 3.0, INTIMACY 1.5). Il 60 anni su 1.1.0
  mostrava deficit strutturale: Erika e Max con mood medio 23.6/23.8,
  bisogni cronicamente sotto 30. Dopo il fix, su 1 anno: mood medio
  65.6/67.7, nessun bisogno medio sotto 49.
- **Movimento inutile filtrato**: `run_tick` non offre più un move per
  un bisogno già soddisfacibile nella location corrente. Prima un NPC a
  casa poteva spostarsi al caffè per mangiare, pagando, quando poteva
  mangiare gratis sul posto. Il filtro `local_satisfies` chiude il caso.
- **Player escluso dal report benchmark** se `include_player=False`.
  Prima il player inattivo con mood 3.5 e balance accumulato confondeva
  le metriche degli NPC. Ora `sim benchmark --include-player` è
  necessario per vederlo.

### Note

- Il test 60 anni su 1.1.1 non è stato eseguito prima del tag. Il
  1 anno è verde. Da eseguire prima di 1.2.0 (lavoro fisico).
- Il bilancio degli NPC è paycheck-to-paycheck: spendono quello che
  guadagnano perché non c'è motivo di risparmiare. Vedi
  `known-issues.md`.

---

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

---

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
