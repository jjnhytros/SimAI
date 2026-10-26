# Changelog

## [1.5.0] — 2026-10-26

### Aggiunto

- **`NPCManager`** (`src/simai/npc/manager.py`): astrazione sopra il
  loop di decisione del tick. `NPCState` (in-memory), `NPCManager`
  (`load`, `update_all`, `_tick_one`), `NPCManagerLike` Protocol.
  `run_tick` accetta `npc_manager=` per iniezione.
- **`sim/reports.py`**: `TickDecision` e `TickReport` spostati da
  `sim/tick.py` per evitare il ciclo `tick → manager → tick`. Re-
  esportati da `tick.py`, nessun test esistente si rompe.
- Test `tests/test_npc_manager.py` (10 test): load, update_all
  ordinato, sync `state.location_id`, priorità lavoro, salvaguardia
  fame, `NPCManagerLike` strutturale.
- Test `tests/test_tick_with_fake_manager.py` (3 test): `run_tick`
  usa il manager iniettato, propaga `include_player`, manager di
  default produce 4 decisioni.

### Cambiato

- `sim/tick.py` delega a `NPCManager`. Il loop inline sparisce.
  Ordine, effetti, `TickDecision`, `TickReport` invariati. `tick.py`
  scende da ~250 a ~110 righe.
- `npc/__init__.py` resta vuoto (era vuoto prima di B1, doveva
  restarlo). `npc.traits` è importato da `actions.utility`:
  re-esportare `NPCManager` innescherebbe un ciclo.

### Verificato (10y, seed 42)

- `10y-1.5.0.json` identico a `10y-1.4.0.json` su `mood_mean`,
  `balance_mean`, `purchase_transactions`, `salary_transactions`,
  `job_attendance_rate`.
- `invariants_ok: true`.

### Limitato (documentato in `known-issues.md` §7)

- `NPCState` in-memory, ricostruito da DB a ogni `load()`. Non
  persistito.
- `load` fa N+1 su `needs_of` (una query per NPC). Irrilevante su
  4 NPC, da correggere in 1.6.0 quando si scala.
- Nessun LOD, nessun `SkillSnapshot`, nessun lifecycle. Quelli sono
  A2 e FASE 3.
- `NPCManagerLike` esiste per test di contract, non ancora usato da
  implementazioni alternative.

## [1.4.1] — 2026-10-26

### Corretto (documentale e test)

- `tests/test_db_migrations.py`: `assert len(versions) >= 8` → `>= 13`
  (migrazione `0013_shop_item` inclusa). Il test passava, il commento
  era stale.
- `tests/test_market.py::test_save_load_preserves_shop_items`:
  variabile `offer` riusata due volte nella stessa sessione. Funzionava
  per `expire_on_commit=False`, ma era fragile. Ora `offer` e
  `offer_after_buy` sono distinte.
- `TODO_SimAI_ottimizzato.md`: ROADMAP allineata al codice reale
  (FASE 3 ~25%, FASE 4 0%, FASE 5 ~55%) + nota che le caselle `[ ]`
  non sono la fonte di verità.
- `README.md`: rimosso "tassazione" dalla riga `1.4+`; spostata a
  `1.5+`, previa decisione esplicita. Coerente con Prompt.md (economia
  avanzata non si apre senza decisione).

### Non incluso

- Nessuna modifica al comportamento del motore. La 1.4.1 è pulizia
  di test e documentazione.

## [1.4.0] — 2026-10-26

### Aggiunto

- **Mercato e negozi**: `ShopItem` (stock, price, location, action),
  `MarketService.buy/sell/filter_by_stock`, `seed_demo_economy`,
  `restock_all`.
- Migrazione `0013_shop_item`.
- `player do -a <action>` usa `MarketService.buy` quando c'è uno
  `ShopItem`: prezzo e stock autoritativi, `Transaction PURCHASE`
  registrata, `stock` scalato.
- `sim/tick.py` filtra azioni con `stock == 0` (via `filter_by_stock`).
- `save`/`load` serializza `ShopItem`.
- CLI `economy seed / shops / restock`.
- CI GitHub Actions (`.github/workflows/ci.yml`) con
  `check.sh --with-tests`.

### Cambiato

- `do_action` refactor: `MarketService.buy` se `ShopItem` esiste,
  fallback legacy se non esiste (test esistenti invariati).
- `sim/benchmark.py` semina l'economia (`seed_demo_economy`) prima di
  `reset_state`. Prima il benchmark non aveva `ShopItem` e
  `purchase_transactions` era 0: il benchmark non misurava il
  comportamento di produzione.

### Verificato (10y, seed 42)

- `invariants_ok: true`
- `purchase_transactions: 22402` (vs 22402 in 1.3.0 — le decisioni
  non cambiano, cambia il meccanismo)
- `mood_mean`: erika 68.1, max 68.1, luca 67.9, giulia 67.7
- `job_attendance_rate: 1.0`
- `balance_mean`: erika 6987, max 6987, luca 26416, giulia 36454
  (non più lineare: gli acquisti scalano il saldo)

### Limitato (documentato in `known-issues.md` §6)

- `stock = -1` (infinito) in 1.4.0. Consumo scorte reale + restock
  in 1.5.0 (con `LifecycleManager`).
- `available_moves` non considera lo stock: un NPC può muoversi per
  un'azione esaurita. Non raggiungibile in 1.4.0 (stock infinito).
- Un solo entry point per l'acquisto (`player do`). Niente
  `economy buy`.

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
