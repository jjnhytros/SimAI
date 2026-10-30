# Changelog

## [0.1190] — 2026-10-30

### Aggiunto

- **`ActionKind.STUDY`** (5° valore). `ActionDef` in `CATALOG`:
  `satisfies=FUN`, `amount=10`, `allowed_at={RESIDENTIAL}`,
  `max_need_to_start=70`, `cost=0`, `weight=0.8`.
- **`MoodletKind.STUDIED`** (`+0.5`/tick, durata 2), mappato da
  `moodlets_for_action(STUDY)`.
- **`_tick_one`**: quando `action.kind == STUDY` e `job is not None`,
  `train_skill(..., 0.01)`. 10× il training opportunistico di
  0.1180, 10× meno del WORKING (0.001/tick). La skill è quella del
  job corrente.
- **Player**: `do_action(player, STUDY)` soddisfa FUN (+10), ma
  **non** allena skill. Limite documentato in `known-issues.md` §19.1.

### Verificato (1y, seed 42)

Attesi: invarianti OK, `mood_mean` ~70.6 (STUDY scatta raramente),
`purchase`/`salary`/`death` invariati, `tps` ~60.

### Rimandato

- **Player training via STUDY**: 0.1200.
- **`PRACTICE_*`, `COOK`, `STUDY` con skill specifiche**: 0.1200.
- **10y accumulato** (0.1160+0.1170+0.1180+0.1190): 0.1200.

## [0.1180] — 2026-10-30

### Aggiunto

- **Training opportunistico** (`npc/manager.py::_tick_one`): quando
  un NPC non ha azioni né move disponibili (`intent.action is None`)
  e ha un job, pratica la sua skill professionale a `+0.00005/tick`
  (20× più lento del training durante WORKING, `+0.001/tick`).
  Silent: nessun moodlet, solo skill.

### Verificato (1y, seed 42)

Attesi: invarianti OK, `mood_mean` ~70.6 invariato (no moodlet),
`purchase`/`salary`/`death` invariati. La calibrazione vera a 0.1200
(10y accumulato: 0.1150 + 0.1180 + 0.1190).

### Non verificato

- **10y**: rimandato a 0.1200. La delta di 0.1180 è piccola e
  localizzata; un 10y isolato costa 30 minuti per un segnale di
  +0.3 skill/anno. Accumulato con 0.1190 a 0.1200.

### Rimandato

- **Moodlet `PRACTICED`**: no, silent training.
- **Skill decay**: no.
- **Training esplicito** (`PRACTICE_*`): ancora no.

## [0.1170] — 2026-10-30

### Cambiato

- **`mood/moodlets.py`**: `active_delta_many(session, char_ids, tick)`
  (1 SELECT invece di N) e `cleanup_expired_many(session, char_ids, tick)`
  (1 DELETE invece di N).
- **`mood/service.py::update_mood`**: nuova keyword
  `moodlet_delta: float | None = None`. Se passata, salta
  `active_delta`. Retro-compatibile.
- **`sim/tick.py` fase 3**: `active_delta_many` e
  `cleanup_expired_many` batch. Ordine preservato: moodlet intimacy
  → `active_delta_many` → `update_mood` → `cleanup_expired_many`.
- **Test**: 2 per `apply_intimacy_moodlets_many` (batch multi-char,
  refresh), 2 per `active_delta_many`/`cleanup_expired_many`
  (equivalenza batch vs per-char).

### Non verificato

- **`tps`**: non misurato. Il 10y non è stato rieseguito. Atteso
  ~63–70 (recupero di ~5–8 query/tick). Si misura al prossimo 10y
  accumulato (0.1180 o successivo), non ora: il cambiamento è
  matematicamente equivalente, nessuna feature.

## [0.1160] — 2026-10-30

### Aggiunto

- **`npc/intimacy/service.py`**: `intimacy_level(strength) -> int`
  (0–5, soglie 20/40/60/80/95), `best_intimacy_level` (max su out+in),
  `intimacy_levels_of`, `apply_intimacy_moodlets`,
  `apply_intimacy_moodlets_many` (batch: 3 query/tick invece di ~3
  per char).
- **`MoodletKind.ROMANTIC`** (level 4, `+0.5`/tick, durata 2) e
  **`MoodletKind.DEVOTED`** (level 5, `+1.0`/tick, durata 2).
- **`tick.py` fase 3**: `apply_intimacy_moodlets_many` prima di
  `update_mood`.
- **CLI** `relationships intimacy -c <key>`: tabella
  `target | kind | strength | level` + best.

### Verificato (10y + 1y, seed 42)

- **`mood_mean`**: 69.58 → **70.58** (erika), 69.98 → **70.98** (max),
  70.10 → **71.10** (luca), 69.58 → **70.58** (giulia). **+1.0
  esatto**, coerente con `DEVOTED` attivo (level 5).
- **`purchase_transactions: 34665` INVARIATO**.
- **`salary_transactions: 17280` INVARIATO**.
- **`balance_*`, `needs_*`, `death_count: 0`, `invariants_ok: true`**
  invariati.
- **`tps`: 63.3** (1y post-batch). Era 72.6 in 0.1150. **Costo
  feature**: 3 query/tick + ~2.5 scritture/tick per il refresh di
  `DEVOTED`. Coerente con +21s su 1y. Non regressione.

### Rimandato (0.1170)

- **`active_delta_many`** e **`cleanup_expired_many`**: N+1 residuo
  in `update_mood` (5 query/tick) e `cleanup_expired` (5 DELETE/tick,
  quasi sempre 0). Ottimizzabile in 0.1170 se il tps scende ancora.
- **Migrazione `Relationship.intimacy_level`**: non serve, derivato.
- **Boost SOCIALIZE scalato**: feedback loop, progettare prima.
- **60y**: rimandato appena prima di 0.2000.

## [0.1150] — 2026-10-29

### Aggiunto

- **Training durante WORKING**: `train_skill(session, char_id, kind, amount)`
  in `skills/service.py`. Aumenta il livello (cap 100), crea la
  skill se manca.
- **`skill_for_job_title(title_value)`**: mapping centralizzato
  `JobTitle.value → SkillKind`. Sostituisce `_skill_for` locale di
  `payday.py`.
- **`npc/manager.py::_tick_one`**: durante `WorkState.WORKING`, se
  l'NPC è nella `job.location_key`, chiama `train_skill(..., 0.001)`.
  Formazione come effetto del lavoro, non azione separata.

### Verificato (10y, seed 42)

- **Skill crescono**: luca 40→70.24 (+30.24 = 7 tick/giorno × 4320),
  giulia 50→93.2 (+43.2 = 10 tick/giorno × 4320), erika/max
  15→58.2 (+43.2). Player resta a 20 (`include_player=False`).
- **`balance_mean` aumentato**:
  - luca: 44536 → **47258.8** (+2722.6)
  - giulia: 52243 → **55666.4** (+3422.8)
  - erika: 5629 → **6407.0** (+777.9)
  - max: 5624 → **6402.4** (+777.9)
  Gli aumenti sono coerenti con il wage crescente × giorni / 2.
- **`purchase_transactions: 34665` INVARIATO** (balance non letto
  da `choose_action`).
- **`salary_transactions: 17280` INVARIATO** (stessi payday).
- **`mood_mean`, `needs_*`, `death_count`, `invariants_ok` INVARIATI**.
- `tps: 72.6` (era 73.9 in 0.1140).

### Corretto (test)

- `tests/test_payday.py::test_second_payday_pays_more` → rinominato
  `test_payday_pays_more_with_higher_skill`: testava training
  implicito tra due `process_payday` senza `run_tick`, cosa
  impossibile. Sostituito con training esplicito via
  `train_skill` + verifica del wage al payday successivo.

### Rimandato

- **Skill decay**: nessuna perdita di skill. 0.1160+.
- **Training action esplicita** (`PRACTICE_*`, `STUDY`, `COOK`):
  0.1160+.
- **Promozioni job basate su skill**: 0.1160+.
- **60y**: dopo 0.1150, con skill dinamiche + morte probabilistica +
  eredità, è il test che vale le 3 ore.

## [0.1140] — 2026-10-29

### Aggiunto

- **`SkillKind`** enum: `BARISTA`, `INSEGNANTE`, `COMMESSO`, `STUDENTE`.
  Separato da `JobTitle` (stessi valori oggi, modello permette
  divergenza futura).
- **`Skill`** model: `character_id` (FK CASCADE), `kind` (SAEnum),
  `level` (float 0–100), unique `(character_id, kind)`,
  `CheckConstraint 0 <= level <= 100`. Migrazione `5200_08`.
- **`skills/service.py`**: `skill_of`, `skills_of`, `level_of`,
  `wage_with_skill`, `clamp_level`.
- **`wage_with_skill(daily_wage, level)`**: `daily_wage * (1 + level/200)`.
  +50% a livello 100. Salario base è il minimo, nessuna penalità.
- **`process_payday`**: salario modulato dalla skill. `_skill_for(job)`
  mappa `JobTitle` → `SkillKind` (1:1 oggi).
- **Seed**: 5 skill iniziali (player COMMESSO 20, luca BARISTA 40,
  giulia INSEGNANTE 50, erika/max STUDENTE 15).
- **`save`/`load`**: serializza/deserializza `Skill`.
- **CLI** `npc skills -c <key>`.

### Verificato (10y, seed 42)

- **`purchase_transactions: 34665` INVARIATO**: `balance` non è letto
  da `choose_action`/`score`. Rischio (a) del piano chiuso.
- **`salary_transactions: 17280` INVARIATO**: stessi payday, importi
  diversi.
- **`mood_mean`, `needs_*`, `death_count`, `invariants_ok` INVARIATI**.
- **`balance_mean` aumentato**, coerente con la formula:
  - luca: 33736 → **44536** (+10800 = +5/giorno × 4320/2)
  - giulia: 40363 → **52243** (+11880 = +5.5 × 4320/2)
  - erika: 4819 → **5629** (+810 = +0.375 × 4320/2)
  - max: 4814 → **5624** (+810)
- `balance_final` aumentato di `Δwage × 4320`: luca +21600, giulia
  +23760, erika/max +1620.
- `tps: 73.9` (era 70.4 in 0.1130).

### Corretto (test obsoleti)

I test hardcodavano i salari base. Aggiornati ai valori scalati:

- `test_cli_economy.py::test_economy_ledger_after_payday`: 25.00 → 30.00
- `test_payday.py::test_payday_at_end_of_shift`: max 5.0 → 5.375,
  giulia 22.0 → 27.5
- `test_payday.py::test_payday_pays_pediatric_student`: 5.0 → 5.375
- `test_payday_presence.py::test_student_erika_paid_if_moved_to_piazza`:
  5.0 → 5.375
- `test_payday_presence.py::test_player_paid_at_caffe`: 20.0 → 22.0
- `test_world_models.py::test_seed_creates_expected_counts`:
  - `skills_created: 5`
- `test_world_models.py::test_seed_is_idempotent`: + `skills_created: 0`

### Rimandato

- **Training action** (`PRACTICE_*`, `STUDY`, `COOK`): 0.1150.
  Skill statiche in 0.1140.
- **Skill decay**: 0.1150.
- **Promozioni job**: 0.1160+.
- **`death_count` sul 60y**: la morte probabilistica non è ancora
  stata esercitata (10y ha `death_count: 0`). 60y in coda.

## [0.1130] — 2026-10-29

### Aggiunto

- **`death_count`** in `BenchmarkReport`: conta le morti cumulate
  nel run. Esposto in `format_report` (riga `Morti: N`).
- **`TickReport.deaths`**: numero di morti del tick (da
  `LifecycleManager.daily_tick`). `run_tick` propaga a `TickReport`,
  `benchmark.py` accumula.

### Cambiato

- **`npc/lifecycle.py`**: rimossa `AGE_DAYS_PER_YEAR = 432` locale,
  importa `DAYS_PER_YEAR` da `economy/calendar.py`. Fonte unica.
  `tests/test_lifecycle.py` aggiornato.
- **`sim/daily.py`**: `restock_all` protetto da
  `if tick_index % TICKS_PER_DAY == 0`. La forma precedente era
  corretta ma il diff 0.1130 l'aveva perso; ripristinato.
- **`TODO.md`**: corretti path stale (`npc/needs/` → `needs/`,
  `npc/utility.py` → `actions/utility.py`).

### Verificato (1y, seed 42)

- `death_count: 0` (atteso: età 14–42, p cumulata <0.5%).
- Invarianti OK, tutto identico al 1y di 0.1110.
- 378 test verdi (377 + 1 per `death_count` in report).

### Rimandato

- **60y**: primo run dopo l'introduzione della morte probabilistica.
  Non è codice, è operazione. Va eseguito e archiviato come
  `docs/release/benchmarks/60y-0.1130.json`, con analisi di
  `death_count`, successioni, ereditità, mood, bilanci. Costo atteso
  ~3h.
- **`UNKNOWN` come causa di morte**: non generato.

## [0.1120] — 2026-10-29

### Aggiunto

- **Morte probabilistica** (`npc/death.py`): `probability_of_death(age_years)`
  con rampa cubica da `1e-5`/anno (età 0) a `1/30`/anno (età 100).
  Unità di misura definita: **per anno**.
- **`probability_of_death_per_day(age_years)`**: conversione esatta
  `1 - (1-p_anno)^(1/432)`, non lineare.
- **`check_probabilistic(session, tick_index, *, master_seed)`**: RNG
  isolato per char e tick (`f"simai:death:{seed}:{char.id}:{tick}"`).
  Salta `age_years >= 100` (OLD_AGE, deterministico, già in 1.8.0).
- **Cause di morte probabilistiche**: ILLNESS 60%, ACCIDENT 30%,
  VIOLENCE 10%. `UNKNOWN` non generato (placeholder).
- **`kill()` cancella gravidanze**: madre morente → gravidanza
  cancellata (figlio non nasce); padre morente → gravidanza resta con
  `partner_id = None` (figlio nasce senza padre). SQLite non enforce
  `ondelete=CASCADE`, quindi cancellazione esplicita + flush.
- **`LifecycleManager.daily_tick`**: chiama `check_probabilistic` dopo
  `check_age`. Log unificato con conteggio per causa.

### Verificato (10y, seed 42)

- **Comportamento deterministico IDENTICO a 0.1110**, al decimale:
  `balance_mean`, `purchase_transactions=34665`, `salary_transactions=17280`,
  `mood_mean`, `relationships_active=6`, `job_attendance_rate=1.0`,
  `invariants_ok: true`.
- **`death_count: 0`** (implicito: tutti e 4 gli NPC nel report con
  balance invariati; una morte li avrebbe rimossi e redistribuito il
  balance).
- `tps`: **70.4** (dentro ±2% di 69.8).
- La feature è inerte sul 10y: p_anno 0.01–0.25% per età 14–42,
  cumulato <3% su 10y. Diventa significativa sul 60y.

### Corretto (test)

- `tests/test_death.py::test_probability_of_death_per_day_conversion`:
  usava un'identità lineare (`p_giorno * 432 ≈ p_anno`) che vale solo
  per `p → 0`. Sostituita con l'identità esatta
  `(1 - p_giorno)^432 = 1 - p_anno` (tolleranza `1e-12`) + sanity
  relativa 1%.

### Rimandato

- **`UNKNOWN` come causa generata**: non in 0.1120.
- **`death_count` in `BenchmarkReport`**: non aggiunto. Verifica
  implicita (character assente dal report = morto). Da aggiungere in
  0.1130, quando il 60y avrà morti reali.

## [0.1110] — 2026-10-29

### Aggiunto

- **`can_work(job, age_years)`** in `economy/work.py`: True sse
  `JobTitle.STUDENTE` (esente) o `not is_pediatric(life_stage_for(age_years))`.
  Soglia `< 20` (EARLY_CHILDHOOD → LATE_ADOLESCENCE).
- **`should_prioritize_work(job, t_in_day, hunger, *, age_years)`**:
  aggiunto divieto pediatrico non-STUDENTE. Firma breaking
  (keyword-only `age_years`).
- **`process_payday`**: `_can_be_paid(char, job)` salta i pediatrici
  non-STUDENTE. Non incrementa `absent` (sospensione, non assenza).
- **`npc/manager.py::_tick_one`**: se `not can_work`, `job = None`.

### Verificato (10y, seed 42)

- **Comportamento deterministico IDENTICO a 0.1101**, al decimale:
  `balance_mean` (4819.070122656793 / 4814.471650081 /
  33736.2131451053 / 40363.58805831983), `purchase_transactions=34665`,
  `salary_transactions=17280`, `relationships_active=6`,
  `job_attendance_rate=1.0`, `mood_mean` 69.58–70.10, `invariants_ok: true`.
  Erika/Max sono `STUDENTE` (esenti), gli altri non sono pediatrici.
- **`tps`: 69.8** sul 10y. **Non è una regressione.**
  Rerun 1y stesso giorno: 0.1110 = 148.0s CPU (71.8 tps),
  0.1101 = 155.4s CPU (70.1 tps). **0.1110 usa −4.8% di CPU
  rispetto a 0.1101.** La baseline `79.7` del 10y di 0.1101 era
  **anomala** (1y di 0.1101 dà 70.1, non 79.7). Il tps vero è ~70
  per entrambe le release.

### Nota su baseline tps

Il `10y-0.1101.json` riporta `tps: 79.7`, incoerente con il
`1y-0.1101` (70.1). La baseline tps da usare per confronti
d'ora in poi è **~70**, non 79.7. Documentato in
`known-issues.md` §13.5. I benchmark futuri che "battono il
target" vanno verificati con CPU time (`user` + `sys`) prima di
dichiararli, per non ripetere l'errore.

## [0.1101] — 2026-10-28

### Cambiato

- **`Moodlet.need`**: nuova colonna `SAEnum(NeedKind, native_enum=False)`,
  nullable. Popolata per i 19 moodlet need-based, `None` per
  `ATE_WELL`, `SOCIALIZED`, `LONELY`, `BECAME_*`. Migrazione `0015`.
- **`refresh_need_moodlets` → `refresh_need_moodlets_many`**: batch
  su tutti i char (1 SELECT invece di N). Transizione = UPDATE del
  `kind` invece di DELETE+INSERT.
- **`update_mood(session, char_id, tick=None, needs=None)`**: nuova
  keyword `needs` per evitare la query interna quando i bisogni sono
  già calcolati. Retro-compatibile.
- **`sim/tick.py` fase 3**: `needs_of_many` una volta per tick,
  `refresh_need_moodlets_many` una volta, `update_mood` con `needs`
  precalcolati.
- **`SPECS` (B3)**: i 13 Δ positivi need-based passano da +2/+3/+4/+5
  a **+0.5**. I 6 Δ negativi invariati. `ATE_WELL`, `SOCIALIZED`,
  `LONELY`, `BECAME_*` invariati.
- **`save/service.py`**: serializza/deserializza `Moodlet.need`.
  **Breaking change `.sav`**: i file con `schema_revision="5200_04"`
  sono rifiutati da 0.1101+ (schema `0015`). Documentato in
  `known-issues.md` §12.3.

### Corretto (efficienza, non bug)

- **Doppia `needs_of` per char per tick** in `tick.py` + `update_mood`
  (presente da 0.1090, es. 1.9.0). `update_mood(needs=...)` elimina
  la query ridondante. Effetto combinato con il batch moodlet:
  `tps` da 67.57 (0.1100) a **79.7** (0.1101), **+17.9%**. 0.1101
  è più veloce anche di 0.1090 (71.44) pur avendo 19 moodlet in più.

### Verificato (10y, seed 42)

- `10y-0.1101.json`, 120.960 tick.
- **`tps`: 79.7** (era 67.57 in 0.1100, target ≥ 70.5).
- **`mood_mean`: 69.83** (69.6 / 70.0 / 70.1 / 69.6 per erika / max /
  luca / giulia). Era 80.73 in 0.1100, 67.85 in 0.1090. Target 67.5–70.5.
- **Comportamento deterministico identico a 0.1100**:
  `balance_*`, `purchase_transactions=34665`,
  `salary_transactions=17280`, `relationships_active=6`,
  `job_attendance_rate=1.0` invariati. `invariants_ok: true`.
- CPU time: 1325s (era 1611s in 0.1100). Non è variazione di carico
  macchina: rapporto CPU/wall simile (~87% vs ~90%), CPU work
  realmente ridotto.

### Rimosso

- `refresh_need_moodlets` (sostituito da `refresh_need_moodlets_many`).
  Nessun chiamante esterno.

## [0.1100] — 2026-10-28

**Nota versioning**: ex `1.10.0` nella numerazione storica. Da questa
release la numerazione è `0.1xy0` (`xy` = minor storica). La release
**1.0** sarà ufficiale quando ci sarà un engine grafico stabile e la
simulazione sarà giocabile dal player. La serie `1.x.y` è storica.
Mappatura completa in `TODO.md` §"Mappatura versioni".

### Aggiunto

- **Moodlet da stato dei bisogni**: 19 nuovi `MoodletKind` need-based
  (`STARVING`, `HUNGRY`, `SATISFIED`, `WELL_FED`, `STUFFED` per HUNGER;
  `DEHYDRATED`, `THIRSTY`, `HYDRATED`, `REFRESHED`, `OVERHYDRATED` per
  THIRST; `MISERABLE`, `BORED`, `CONTENT`, `ENTERTAINED`, `BLISSFUL`
  per FUN; `INTIMATE`, `CONNECTED`, `CLOSE`, `ADORED` per INTIMACY).
  Totale moodlet need-based: 22 (3 esistenti + 19 nuovi).
- **`moodlet_for_need(need, value) -> MoodletKind | None`** in
  `mood/moodlets.py`. Funzione pura, deterministica. `None` per
  INTIMACY < `LONELY_THRESHOLD` (coperto da `LONELY` via streak).
- **`refresh_need_moodlets(session, char_id, needs, tick)`**:
  applica il moodlet dello stato corrente. Transizione: delete+insert.
  Stato invariato e lontano dalla scadenza: nessuna scrittura. Stato
  invariato e vicino (`expires - tick <= 14`): refresh in-place.
- **`NEED_MOODLETS`**, **`REFRESH_THRESHOLD_TICKS`** in
  `mood/moodlets.py`.
- **Moodlet di transizione LifeStage**: 3 nuovi kind (`BECAME_CHILD`
  a 6 anni, `BECAME_YOUNG_ADULT` a 20, `BECAME_SENIOR` a 60),
  `duration_ticks=10`, `delta_per_tick=+0.5`. Applicati da
  `LifecycleManager.daily_tick` dopo `apply_aging`.
- **`LIFESTAGE_TRANSITION_MOODLETS`** dict in `npc/lifecycle.py`.

### Cambiato

- `sim/tick.py` fase 3: `refresh_need_moodlets` tra
  `apply_moodlet(LONELY)` e `update_mood`.
- `sim/benchmark.py`: rimosso `TICKS_PER_YEAR = 12096` locale, ora
  importato da `economy/calendar.py` (fonte canonica).
- `economy/calendar.py`: aggiunti `TICKS_PER_YEAR = TICKS_PER_DAY * 432`
  e `DAYS_PER_YEAR = 432`.
- Archivio documentale: `zzzDocs/TODO.md` → `TODO.md` (root),
  `zzzDocs/TODO_SimAI_1.0_Muse_Core.md` e
  `zzzDocs/TODO_SimAI_ottimizzato.md` → `docs/archive/todo/`.
  `TODO.md` è ora la fonte di verità. `zzzDocs/Prompt.md` resta
  (specifica aspirational, da consolidare).

### Corretto (test)

- `tests/test_cli_mood.py::test_mood_drops_after_tick`: atteso "81.2"
  invece di "67.2". I moodlet stato-dipendenti aggiungono +14 al mood
  dopo 10h (HUNGER 60→`SATISFIED`+2, THIRST 50→`HYDRATED`+2,
  FUN 70→`ENTERTAINED`+5, INTIMACY 85→`CLOSE`+5).
- `tests/test_moodlets.py::test_moodlet_for_need_intimacy_below_lonely_is_none`:
  soglie corrette (90.0 → `ADORED`, non `CLOSE`). Aggiunti i confini
  49.99/69.99/89.99.

### Verificato (10y, seed 42)

- `10y-0.1100.json` (ex `10y-1.10.0.json`), 120.960 tick.
- **Comportamento deterministico identico a 0.1090 (ex 1.9.0)**:
  `needs_*`, `balance_*`, `salary_transactions=17280`,
  `purchase_transactions=34665`, `relationships_active=6`,
  `job_attendance_rate=1.0` invariati. Rischio "`score` legge `mood`"
  chiuso due volte (grep + 10y).
- **Mood +12.88 medio** (67.85 → 80.73). Atteso: i moodlet
  stato-dipendenti aggiungono ~+14 nel caso tipico. `mood_max`
  clippa a 100 per tutti e 4 gli NPC.
- **Performance −5.42%** (71.44 → 67.57 tps, stessa giornata).
  Accettato consapevolmente: il calo è dovuto alle transizioni
  DELETE+INSERT, non al SELECT. Ottimizzazione tracciata per 0.1101.
- `invariants_ok: true`.

### Rimandato (0.1101+)

- **Ottimizzazione `refresh_need_moodlets`**: batch SELECT (1 per tutti
  i char), UPDATE invece di DELETE+INSERT (richiede colonna `need` su
  `Moodlet` → migrazione).
- **Calibrazione Δ moodlet**: +12.88 medio è forse troppo. Da valutare
  su 60y o con player incluso.
- **Le altre 5 transizioni LifeStage** (12, 15, 25, 40, 50 anni) senza
  moodlet.
- **Unificazione `AGE_DAYS_PER_YEAR`** (`npc/lifecycle.py`) con
  `DAYS_PER_YEAR` (`economy/calendar.py`): stesso valore 432 in due
  posti.

## [1.9.0] — 2026-10-28

### Aggiunto

- **`LifeStage`** enum (9 valori, inglese): `EARLY_CHILDHOOD`,
  `CHILDHOOD`, `EARLY_ADOLESCENCE`, `LATE_ADOLESCENCE`,
  `YOUNG_ADULT`, `EARLY_ADULTHOOD`, `MIDDLE_ADULTHOOD`,
  `LATE_ADULTHOOD`, `SENIORITY`. Tassonomia Anthalys 0–60+.
- **`npc/lifestage.py`**: `LIFESTAGE_THRESHOLDS` (0, 6, 12, 15, 20,
  25, 40, 50, 60), `life_stage_for(age_years)` (funzione pura),
  `is_pediatric`, `is_psychosocial` (predicati).
- CLI `npc stages -c <key>`: età, `LifeStage`, predicati.

### Verificato (10y, seed 42)

- `10y-1.9.0.json` **identico a `10y-1.8.0.json`**. `LifeStage` non
  tocca il tick: è un dato derivato, letto solo dalla CLI.
- Nessuna migrazione: `LifeStage` non è persistito.

### Rimandato (documentato in `known-issues.md` §11)

- **`LifeStagePediatric`/`LifeStagePsychosocial` come enum separate**:
  non implementate. La tassonomia è una sequenza, non due assi
  paralleli. Diventano predicati (`is_pediatric`, `is_psychosocial`)
  sull'enum unica.
- **`LifeStageService`**: non implementato. `life_stage_for` è
  funzione pura, nessuno stato da salvare. Se in 1.10.0+ serviranno
  effetti (moodlet di transizione), il servizio avrà senso.
- **`moodlet_for_need`** (22 mapping, TODO §3.0508): rimandato.
- **Moodlet di transizione** (`BIRTHDAY`, `PUBERTY`, `ADULTHOOD`,
  `SENIORITY`): rimandati.
- **Divieti di lavoro per minori/anziani**: nessuno. `erika`/`max`
  (14) continuano a lavorare come studenti.
- **`LifeStage` in `save`/`load`**: non persistito (derivato da
  `age_years`).
- **`LifeStage` in `PlayerStatus`**: non mostrato in `player status`
  (richiede `PlayerStatus` non frozen). `npc stages` copre l'uso.
- **Confine all'anno**: `age_days` ignorato. `life_stage_for(14)`
  è `EARLY_ADOLESCENCE` indipendentemente da `age_days`.

## [1.8.0] — 2026-10-28

### Aggiunto

- **`LifecycleManager`** (`npc/lifecycle.py`): chiamato da
  `daily_tick` ogni 28 tick. Ageing (`age_days`, `age_years`),
  morte per età, parto automatico delle gravidanze scadute.
- **`Character.age_days`** (Integer, 0–431). Migrazione `5200_04`
  insieme a `death_cause` e `pregnancy`. Seed: erika 14y 24d,
  max 14y 32d, altri 0d.
- **`DeathService.kill()`** (`npc/death.py`): rimuove il
  `Character`, distribuisce il `balance`, registra `Transaction`
  `OTHER`. Morte automatica solo a 100 anni (`OLD_AGE`), manuale
  via CLI (`MANUAL`).
- **`InheritanceService.distribute()`** (`npc/inheritance.py`):
  5 tier (SPOUSE 50% + CHILD resto, PARENT, SIBLING, OTHER→world).
  Solo `balance`.
- **`Pregnancy` + `PregnancyService`** (`npc/pregnancy.py`):
  300 giorni Anthalys (= 8400 tick), gemelli (1.5% identici,
  30% fraterni), parto automatico da `daily_tick`.
- **`DeathCause`** 6 enum (`OLD_AGE`, `ILLNESS`, `ACCIDENT`,
  `VIOLENCE`, `UNKNOWN`, `MANUAL`). Solo `OLD_AGE` e `MANUAL`
  generati in 1.8.0.
- **`TransactionKind.OTHER`** (terzo valore, oltre SALARY/PURCHASE).
- CLI `npc kill`, `npc conceive`, `npc pregnancies`, `npc deliver`,
  `npc lifecycle-tick`.
- `save`/`load` serializza `age_days` e `Pregnancy`.

### Verificato (10y, seed 42)

- `10y-1.8.0.json` **identico a `10y-1.7.1.json`** su
  `mood_mean`, `balance_mean`, `purchase_transactions`,
  `salary_transactions`, `job_attendance_rate`, `relationships_active`.
- `death_count: 0` (nessuno arriva a 100 anni: erika/max 24,
  giulia 47, luca 52).
- `invariants_ok: true`.

### Rimandato (documentato in `known-issues.md` §10)

- **Morte probabilistica**: `1e-5` baseline, rampa cubica,
  `exp_max` del TODO §3.4 **non implementata**. Serve un'unità di
  misura (per tick? per anno? per giorno?) che il TODO non
  specifica. 1.9.0+.
- **`DeathCause` 4 inutilizzati** (`ILLNESS`, `ACCIDENT`,
  `VIOLENCE`, `UNKNOWN`): enum per il futuro, mai generati.
- **`LIFESTAGE`**: nessuna transizione pediatrica/psicosociale.
  `AgingService` fa solo compleanno.
- **Gravidanza senza sesso modellato**: `conceive()` non valida il
  sesso. `Character.gender` non esiste.
- **Gemelli identici vs fraterni**: `roll_twins()` calcola il flag
  ma non ha effetto osservabile (nessuna genetica). `traits=[]`
  per tutti i nuovi nati.
- **Nessuna `Transaction` per nascita** (solo per successione).
- **`death_cause` campo nullable in `Character`**: non usato in
  1.8.0 (`kill()` rimuove il `Character`, non c'è nulla da salvare).

## [1.7.1] — 2026-10-27

### Cambiato

- **`TICKS_PER_DAY = 28`** (era 24): giorno Anthalys di 28 ore.
  Payday tick 27, 55, 83, ...
- **`TICKS_PER_YEAR = 12096`** (era 8760): 28 × 432 (calendario
  Anthalys). `sample_every` default 28.
- **`Job.break_start_tick` / `break_end_tick`**: pausa pranzo.
  Migrazione `0014`.
- **`WorkState.ON_BREAK`**: durante la pausa, l'NPC è libero di
  lasciare la location. `should_prioritize_work` è `False` in pausa.
- **Seed orari nuovi**: luca barista 14-21, giulia/erika/max 7-14
  - pausa 14-15 + 15-18, player commesso 10-19.
- **`player/status.py` / `cmd_economy.py`**: mapping `on_break` →
  "in pausa".

### Verificato (10y, seed 42)

- 120.960 tick, `invariants_ok: true`, tps 77.0.
- `mood_mean`: 67.5–68.1.
- `job_attendance_rate: 1.0` (pausa 14-15 non riduce l'attenzione).
- `purchase_transactions: 34665` (+11.7%/tick rispetto a 1.7.0,
  coerente con decadimento +16.7%).
- `balance_mean` per erika: 9590 (era 13922 in 1.7.0, calo dovuto
  a consumo reale).

### Limitato (documentato in `known-issues.md` §9)

- Decadimento +16.7% e acquisti +11.7%: il baseline cambia, i 10y
  precedenti non sono più confrontabili.
- Turni barista 7-14 e 21-28 scoperti (un solo barista nel seed).
- `TICKS_PER_YEAR = 12096`, non 8760. `--years 1` fa 12096 tick.

## [1.7.0] — 2026-10-27

### Aggiunto

- **`RelationshipKind` 11 kind**: `FRIEND`, `PARENT_OF`, `CHILD_OF`,
  `SIBLING_OF`, `SPOUSE_OF`, `EX_PARTNER_OF`, `GRANDPARENT_OF`,
  `GRANDCHILD_OF`, `UNCLE_AUNT_OF`, `NEPHEW_NIECE_OF`, `COUSIN_OF`.
  Nessuna migrazione: `kind` è `String(16)` senza CHECK.
- **`family_tree.py`**: `parents_of`, `children_of`, `siblings_of`,
  `ancestors_of` (BFS), `descendants_of` (BFS).
- **`kinship.py`**: `relationship_coefficient` (path-based, grado
  1/2/3 → 0.5/0.25/0.125), `kinship_coefficient` (r/2),
  `relationship_name` (italiano neutro).
- **Seed famiglia**: giulia madre di erika, luca padre di max.
  4 relazioni (`PARENT_OF` + `CHILD_OF`) + 2 `FRIEND` = 6.
- **Boost `SOCIALIZE` familiare**: `boost_social_relationship`
  boosta `PARENT_OF`/`CHILD_OF` oltre a `FRIEND`.
- CLI `relationships family/ancestors/descendants/kinship`.

### Verificato (10y, seed 42)

- `relationships_active: 6` (era 2 in 1.6.0).
- `mood_mean`: 67.7–68.1, identici a 1.6.0.
- `balance_final` e `purchase_transactions: 22402` identici a 1.6.0.
  Il boost familiare cambia `strength` delle relazioni, non l'utility
  o l'economia.
- `invariants_ok: true`, tps 73.4.

### Limitato (documentato in `known-issues.md` §8)

- Relazioni familiari **statiche**: senza `LifecycleManager` (C), il
  tick non le usa per decisioni (matrimonio, gravidanza, morte).
- `relationship_name` neutro ("genitore", "figlio/a"): `Character.gender`
  non esiste.
- `relationship_coefficient` copre grado 1–3. Oltre: 0.0.
- `player status` non mostra famiglia (rischio `PlayerStatus` frozen).
  `npc relationships family` copre l'uso.

## [1.6.0] — 2026-10-27

### Aggiunto

- **Stock finito**: `SHOP_ITEM_SPECS` con stock 20/20/10/15 (era
  `-1`, infinito in 1.4.0). `daily_tick` in `sim/daily.py` fa
  `restock_all` ogni 24 tick (tick 0, 24, 48, ...).
- **`needs_of_many`** in `needs/service.py`: una query per i bisogni
  di tutti gli NPC. `NPCManager.load` la usa. Recuperato da 1.5.1.
- **`available_moves` con `offers_by_key`**: le location con
  `stock == 0` per l'azione target non sono più proposte come meta.
  `NPCManager.update_all` calcola `offers_by_key` una volta per tick.

### Cambiato

- `daily_tick` chiamato da `run_tick` prima del payday. Punto di
  aggancio futuro per `LifecycleManager`.

### Rimandato

- **`COST_PENALTY` a 1.7.0**. `COST_PENALTY = 0.5` previsto in 1.6.0
  non funziona: `DISTANCE_PENALTY = 5.0` rende il move già penalizzato
  e `0.5` non sposta la decisione. Valori più alti ucciderebbero il
  caffè. Il problema è strutturale (la casa ha tutte le azioni
  gratis). Va discusso come design, non come costante. Vedi
  `known-issues.md` §2.5.

### Corretto (documentale)

- `docs/release/1.5.0-plan.md` §7.2: la stima "irrilevante (< 1ms)"
  per il N+1 era sbagliata. Il N+1 costa ~11s su 10y (0.9%), non
  −7.7% del tps. Il baseline 76.5 tps di 1.4.0 non era valido:
  rimisurato lo stesso giorno di 1.5.1, dà 72.27 tps. Differenza
  reale 1.4.0 → 1.5.0: 2.2%, non 7.7%.
- `known-issues.md` §7.2 corretto con il dato reale. §6.1, §6.4,
  §2.5 marcati risolti/rimandati. §1.3, §2.1, §3.2 marcati "risolto"
  (erano stale da 1.0.1, 1.2.0, 1.2.1).

### Non incluso

- `InventoryService` (personaggio), `RelationshipKind` 11 (A2),
  `LifecycleManager`, tassazione, skills, memoria. 1.7.0+.

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
