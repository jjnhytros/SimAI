# 📋 TODO SimAI — Simulazione di Anthalys (Python 3.13)

## Legenda

- `[ ]` = voce non completata / stato azzerato
- `[x]` = voce completata (non usata in questa versione azzerata)

**Versione corrente**: `0.1.0.dev0`
**Runtime**: Python 3.13, SQLAlchemy 2.0, Pydantic v2, SQLite
**Stato dichiarato**: FASE 0–4 sviluppate nella versione precedente; il TODO è stato azzerato per la nuova ricostruzione. Le caselle `[ ]` indicano quindi lo stato del lavoro nella ricostruzione corrente, non dimostrano che il codice precedente sia assente.


## 🧭 DIREZIONE ESECUTIVA — LEGGERE PRIMA DI IMPLEMENTARE

### Obiettivo

Costruire prima un **motore di simulazione deterministico, osservabile e verificabile**; poi far emergere da esso individui, società e sistemi economici. La UI deve osservare e comandare il motore, non contenerne la logica. L'integrazione LLM è un'estensione futura e non deve essere necessaria per far avanzare il mondo.

- **SimAI**: motore, runtime, servizi e strumenti di simulazione.
- **Anthalys**: mondo simulato, regole, calendario, cultura e contenuti.
- **ClaireOS**: progetto distinto ma integrabile, dedicato all'assistente personale, alla continuità d'identità e alla memoria relazionale. Evitare dipendenze circolari: SimAI non deve importare logica specifica di ClaireOS.
- **Principio guida**: ogni Sim deve poter vivere una storia coerente anche senza osservatori; la simulazione deve poter essere messa in pausa, salvata, ripresa e verificata.

### Priorità consigliata

1. **P0 — Baseline affidabile**: recuperare il codice reale, creare un branch/tag di riferimento, verificare installazione, migrazioni, CLI e test. Non dedurre lo stato del codice dal TODO.
2. **P1 — Vertical slice end-to-end**: mondo demo + NPC + bisogni/decisioni + tempo + persistenza + statistiche. Deve funzionare da CLI senza UI.
3. **P2 — Validazione di lungo periodo**: simulazione accelerata riproducibile, invarianti, report e test di bilanciamento a 1, 10 e 60 anni simulati.
4. **P3 — Mondo interattivo**: UI, lotti, costruzione, inventario, trasporti e città, mantenendo il backend indipendente.
5. **P4 — Sistemi economici e sociali avanzati**: introdurli solo quando i sistemi precedenti superano i test di regressione e bilanciamento.
6. **P5 — LLM, multiplayer e scalabilità**: non anticiparli. Prima definire contratti, confini di processo e requisiti misurati.

### Regole di esecuzione

- Ogni task deve avere: **risultato verificabile**, test associato, dipendenze e criterio di completamento.
- Non iniziare una fase solo perché la precedente “sembra finita”: passare il relativo **gate di uscita**.
- Non introdurre nuove dipendenze senza motivazione, alternativa valutata e costo di manutenzione esplicito.
- Preferire piccoli incrementi verticali e migrazioni reversibili rispetto a grandi batch di moduli.
- Prima di rifattorizzare, verificare gli usi reali con ricerca nel repository e test; il TODO è una mappa, non una specifica infallibile.
- Mantenere un `CHANGELOG.md` o registro decisioni per scelte architetturali, cambi di schema e modifiche al bilanciamento.

### Decisioni architetturali da fissare presto

- **Test automatici obbligatori in CI**: unitari, integrazione DB/migrazioni e smoke test CLI. Il precedente “no test job” va rimosso.
- **RNG riproducibile**: seed master + stream RNG separati per sottosistema/entità; registrare seed e versione delle regole nei report e nei salvataggi.
- **Tick atomico**: definire ordine dei sistemi, confini transazionali, gestione degli errori e comportamento al riavvio. Un tick fallito non deve lasciare metà mondo aggiornato.
- **Tempo canonico**: un'unica rappresentazione interna e conversioni testate; niente calcoli temporali duplicati nei singoli servizi.
- **Eventi**: distinguere eventi di dominio persistenti, notifiche runtime e semplici log. Definire se gli eventi sono sincroni, ordinati e idempotenti.
- **Persistenza**: SQLite per la prima versione single-player; repository/servizi non devono dipendere da dettagli SQLite. PostgreSQL solo quando un requisito reale lo giustifica.
- **UI/API**: validazione agli ingressi, autorizzazione dove necessaria, nessuna logica di simulazione nei route handler.
- **Dati e salvataggi**: versionare lo schema del payload `.sav`, verificare integrità prima del caricamento e testare migrazioni/backup/restore.
- **Configurazione**: distinguere configurazione di sistema, configurazione di simulazione e dati del mondo; definire precedenza e validazione, evitando hot-reload impliciti di parametri che cambiano le regole a metà tick.
- **Osservabilità**: log strutturati, contatori per tick, durata per sistema, errori e report di bilanciamento; evitare di loggare dati personali non necessari.

### Invarianti di sicurezza e coerenza per NPC

- Ogni azione deve essere valida rispetto a età, stato, posizione, risorse e prerequisiti; l'AI può proporre un'azione, ma il servizio di dominio deve validarla.
- Le interazioni sessuali/intime di natura sessuale sono **solo tra personaggi adulti**. I personaggi minorenni possono avere dinamiche sociali e affettive non sessuali; nessun parametro di consenso o comando `force` deve aggirare il controllo d'età o il rifiuto.
- Il consenso è un requisito esplicito, non una semplice probabilità di successo. Un punteggio di disponibilità può modellare l'incertezza della decisione, ma non deve autorizzare coercizione, incapacità o bypass.
- Evitare che salute, identità, orientamento o altri attributi sensibili siano esposti automaticamente nella UI, nei log o nei report.
- Le morti, le nascite, le eredità, le transazioni e gli spostamenti devono essere idempotenti: ripetere un job dopo un crash non deve duplicare effetti.

### Gate di uscita per fase

- **Fase 0**: installazione pulita riproducibile; lint, typecheck e test passano in CI; migrazione vuota e upgrade funzionano.
- **Fase 1–2**: calendario coperto da test ai confini; tick riproducibili con seed; salvataggio/caricamento produce lo stesso stato logico.
- **Fase 3**: invarianti NPC, età, famiglia e relazioni testate; run accelerati senza errori; report di bilanciamento archiviati.
- **Fase 4**: geometria e pathfinding coperti da test; acquisti e costruzione sono atomici; UI non può creare stati invalidi.
- **Fase 5–7**: transazioni economiche riconciliate; imposte e stipendi non duplicabili; servizi pubblici e leggi hanno regole versionate.
- **Fase 8**: definire protocollo, autorità server e modello di concorrenza prima di implementare il multiplayer.
- **Fase 9**: profiling basato su benchmark e colli di bottiglia misurati, non ottimizzazioni speculative.

---

## 🗺️ ROADMAP

| FASE | Stato | Range migrazione | Note |
| ------ | ------- | ------------------ | ------ |
| 0 — Setup | [ ] | — | pyproject, alembic, CLI, CI, py.typed |
| 1 — Core Simulation | [ ] | 5000–5099, 5200_07 | TimeManager, Loop, SaveManager, Location, Stats |
| 2 — Anthalys Time | [ ] | 5100 (riservato) | Moons, Holidays, Seasons, Astro, Clock |
| 3 — Character/NPC | [ ] ~95% | 5200–5299 | 19 task §3.2/3.4/3.5 UI-driven sospesi |
| 4 — World | [ ] ~90% | 5300–5399 | 4.0→4.10c completati; debiti aperti |
| 5 — Economy | [ ] ~40% | 5400–5499 | Job/Market/Payday [ ], Banche/AION [ ] |
| 6 — Politics | [ ] 0% | 5500–5599 | — |
| 7 — SoNet | [ ] 0% | 5600–5699 | — |
| 8 — Multiplayer | [ ] 0% | 5700–5799 | — |
| 9 — Hardening | [ ] 0% | — | — |

---

## FASE 0 — SETUP [ ]

- [ ] `[00.0001]` Struttura progetto Python (`simai/`, `alembic/`, `docs/`, `scripts/`, `.github/workflows/`)
- [ ] `[00.0002]` `pyproject.toml` (uv, `requires-python = ">=3.13"`, classifier 3.13)
- [ ] `[00.0003]` Dipendenze core: SQLAlchemy 2.0, Alembic 1.13, Pydantic 2.7, pydantic-settings, Typer 0.12, Rich 13.7, Loguru 0.7, PyYAML 6.0; dev: ruff 0.6, mypy 1.13, pyright 1.1.390, types-PyYAML
- [ ] `[00.0004]` Config `[tool.ruff]` (line-length 100, py313, RUF001/002/003 disattivate, `extend-immutable-calls` per Typer+FastAPI, `**/*.md` esclusi), `[tool.mypy]` strict py313, `[tool.pyright]` strict py313
- [ ] `[00.0005]` `.env.example` completo
- [ ] `[00.0006]` `simai/config/settings.py` (Settings pydantic: db_url, log_level, debug, master_seed, tick_minutes, data_dir, starting_year/month/day, saves_dir, logs_dir, exports_dir, ui_enabled/host/port, save_encryption_key)
- [ ] `[00.0007]` `simai/config/anthalys.py` (432/18/24/28/60/60, WEEKDAYS 7, MONTHS 18, STARTING_YEAR 5775, SEASONS 4, SEASON_LENGTH_DAYS 108, DAY_PHASE_BOUNDARIES 7 fasi)
- [ ] `[00.0008]` `simai/config/logging.py` (Loguru: stderr in debug, file `data/logs/simai.log` con rotation daily + retention 30gg)
- [ ] `[00.0009]` `simai/db/base.py` (`Base` DeclarativeBase, `IdMixin` con `BigInteger().with_variant(Integer, "sqlite")`, `TimestampMixin`)
- [ ] `[00.0009b]` `simai/db/session.py` (`get_engine()` con PRAGMA SQLite, `get_session_factory()`, `session_scope()`, `sqlite_path_from_url()`)
- [ ] `[00.0010]` Alembic init: `alembic.ini` (file_template `%%(rev)s_%%(slug)s`), `env.py` (legge SIMAI_DB_URL da settings, importa `simai.db.registry.ensure_all_models_loaded()`, `compare_type=True`, `render_as_batch=True`), `script.py.mako` (typing `str | Sequence[str] | None`)
- [ ] `[00.0011]` `.gitignore` (Python, venv, db, data/, .env, cache, IDE)
- [ ] `[00.0012]` `.editorconfig` (UTF-8, LF, indent 4, trim trailing whitespace)
- [ ] `[00.0013]` `simai/__main__.py` (entrypoint Typer)
- [ ] `[00.0014]` `simai/cli/app.py` (poi splittato in Chunk 1.4)
- [ ] `[00.0015]` `simai/__version__.py` (`0.1.0.dev0`)
- [ ] `[00.0016]` Hook commit-msg + `scripts/install-hooks.sh`
- [ ] `[00.0017]` `docs/simai/README.md`, `docs/simai/lore/README.md`
- [ ] `[00.0018]` CI GitHub Actions (`lint`, `typecheck`, `pytest`: unitari + integrazione + smoke test)
- [ ] `[00.0019]` `.env.example`
- [ ] `[00.0020]` `python -m simai version` funziona
- [ ] `simai/py.typed` (marker PEP 561) + `[tool.hatch.build.targets.wheel.force-include]`
- [ ] `scripts/check.sh` (ruff --fix + format + check + mypy)
- [ ] `scripts/download_assets.sh` (bootstrap, htmx, alpine, d3, chart)
- [ ] `simai/utils/coerce.py` (`coerce_int/float/str/optional_int/optional_str`) + `git.py` (`get_git_sha`)
- [ ] `simai/db/registry.py` (`ensure_all_models_loaded()` idempotente con `configure_mappers()`)
- [ ] `simai/ui/routes/__init__.py` con import espliciti dei submodule

---

## FASE 1 — CORE SIMULATION [ ]

### §1.0 — Time Manager (range 5000)

- [ ] `[01.0001]` `core/anthalys_datetime.py` (`AnthalysDateTime` frozen, order, slots, `to_total_seconds`, `from_total_seconds`, `add_minutes/seconds`, `to_iso_string/from_iso_string`)
- [ ] `[01.0002]` `core/anthalys_calendar.py` (`AnthalysCalendar`: `to_total_days`, `day_of_year`, `weekday_of`, `month_name`, `season_of` 4×108gg, `phase_of` 7 fasi, `to_gregorian`/`from_gregorian` epoch `1-1-1 Anthalys ↔ 1 gen 1000 d.C.`)
- [ ] `[01.0003]` `core/time_manager.py` (`TimeManager` iniettato: `current`, `tick_minutes`, `advance_tick/ticks`, `subscribe_to_*_change`, eventi `time.tick/houredit/day/month/year/season/phase.changed`)
- [ ] `[01.0004]` `core/time_enums.py` (`DayPhase` 7, `Season` 4)
- [ ] `[01.0005]` Stagioni 4×108gg (inverno inizia doy 424)
- [ ] `[01.0006]` Cicli lunari (→ FASE 2)
- [ ] `[01.0007-0008]` Festività (→ FASE 2)
- [ ] `[01.0009]` CLI `sim time show` / `sim time advance N`
- [ ] `[01.0010]` Test manuale in `docs/simai/testing-manuale.md`

### §1.1 — Loop di Simulazione + EventBus + LOD

- [ ] `[01.0020]` `core/simulation_loop.py` (`SimulationLoop` con `TickReport`, pausa/resume/speed, `NPCManagerLike`/`WorldManagerLike` Protocol)
- [ ] `[01.0021]` `core/lod.py` (`LODLevel` IntEnum BACKGROUND/REDUCED/FULL, `lod_from_distance`, `FULL_DISTANCE_THRESHOLD=1`, `REDUCED_DISTANCE_THRESHOLD=3`)
- [ ] `[01.0022]` Metrica tick con `perf_threshold_ms` warning
- [ ] `[01.0023]` CLI `sim start --max-ticks N --perf-threshold-ms X`

### §1.2 — SaveManager (range 5000)

- [ ] `[01.0040]` SQLite come DB primario
- [ ] `[01.0041]` Formato `.sav` (`magic + uint16 + uint32 + JSON header + payload zstd + Fernet opzionale`). Fix bug offset: `f.seek(12)` per `header_len`, `f.seek(16+header_len)` per payload.
- [ ] `[01.0042]` `core/save_manager.py` (`SaveManager`, `SaveInfo`, `SimulationState`, `SaveError`/`SaveNotFoundError`/`SaveFormatError`, `create_save`/`load_save`/`list_saves`/`delete_save`)
- [ ] `[01.0043]` CLI `save list/create/load/delete/gen-key`
- [ ] `[00.0010b]` Migrazione `5000_01_core_version` (tabella `core_version` + seed versione)
- [ ] `[01.0044]` CLI `db upgrade/status`

### §1.3 — Location + GameObject + pathfinding (range 5300)

- [ ] `[01.0050]` `world/models.py` (`GameObject` con state enum, condition, container, interactions, metadata)
- [ ] `[01.0051]` Capacità oggetti (`container_capacity`, `container_contents_json`)
- [ ] `[01.0052]` Usura e rottura (`apply_wear` → BROKEN a 0)
- [ ] `[01.0053]` `repair()` (ripristina a 0.9)
- [ ] `[01.0054]` `list_objects_in(location_id)` per percezione
- [ ] `[01.0055]` Total Realism (fisica, fluidi, polvere) → FASE 9/debito
- [ ] `[01.0060]` `world/models.py` (`Location` con bounds, capacity, attributi dinamici)
- [ ] `[01.0061]` Capacità location + relationship oggetti
- [ ] `[01.0062]` Attributi dinamici (`cleanliness_level`, `noise_level`, `crowd_level`, `safety_rating`, `aesthetic_score`) + `update_dynamic_attribute`
- [ ] `[01.0063]` `world/pathfinding.py` (`LocationGraph` + A* euristica euclidea)
- [ ] `[01.0064]` `update_dynamic_attribute` con clamp
- [ ] `[5300_01]` Migrazione `locations_objects`
- [ ] `[world/seed.py]` `seed_demo_world` (casa demo 6 location, 5 edge, 11 oggetti)
- [ ] CLI `world seed/list/show/objects/path`

### §1.4 — CLI refactor + YAML config + db reset

- [ ] `[01.0080]` `config/simulation.yaml`, `config/loader.py` (`SimulationConfig` con hot-reload via mtime)
- [ ] CLI splittata: `cli/_console.py`, `_helpers.py`, `cmd_sim.py`, `cmd_db.py`, `cmd_save.py`, `cmd_world.py`, `cmd_economy.py`, `cmd_npc.py`, `cmd_stats.py`, `cmd_ui.py`, `cmd_city.py`, `cmd_transport.py`
- [ ] CLI `db reset [--yes] [--seed]` (cancella file + `alembic upgrade head` + `world_seed` + `seed_npc_data` + `economy_seed`)

### §1.6 — Population Statistics

- [ ] `[01.0070]` `npc/stats/models.py` (`PopulationCensus` unique `(year, month)`)
- [ ] `[01.0071]` `npc/stats/service.py` (`live_stats`, `snapshot` upsert, `census_history`) + hook in `LifecycleManager`
- [ ] `[5200_07]` Migrazione `population_census`
- [ ] CLI `stats population/snapshot/census/year-summary`

---

## FASE 2 — ANTHALYS TIME ESTESO [ ]

Package `simai/sim/anthalys/time/`:

- [ ] `[02.0001]` Package `time/`
- [ ] `[02.0002]` `clock.py` (`AnthalysClock` facade su `TimeManager`)
- [ ] `[02.0003]` `calendar.py` (`CalendarExt`: `add_days`, `days_between`, `start_of_*`, `end_of_*`)
- [ ] `[02.0004]` `holidays.py` (`Holiday`, `HolidayRegistry`, 12 fisse + 2 mobili)
- [ ] `[02.0005]` `moons.py` (`Moon`, `MoonPhase` 8, `MoonCycles` Aelith 27gg/Brumar 41gg/Cindral 89gg, `first_full_moon_of_month`)
- [ ] `[02.0006]` `seasons.py` (`SeasonInfo`, `season_info`, `days_until_next_season`, `next_season_start`)
- [ ] `[02.0007]` `DayPhase` (riesportato dal core)
- [ ] `[02.0008]` `astro.py` (`AstroEvent`, `AstroEventType`, `AstroEventsEngine`: eclissi, comete seed-based, meteore)
- [ ] `[02.0009]` `AnthalysClock` in `sim/anthalys/__init__.py`
- [ ] `[02.0010]` CLI `sim time moons/holidays/upcoming-holidays/season/astro`
- [ ] `[5100_xx]` Migrazioni (riservate, nessuna necessaria per ora)

---

## FASE 3 — CHARACTER / NPC (range 5200–5299)

### §3.0 — Character + NPC seed [ ]

- [ ] `[03.0001]` `npc/models.py` (`Character` con campi tipizzati + JSON)
- [ ] `[03.0002]` `npc/generator.py` (`CharacterGenerator`, `seed_characters`), `npc/name_generator.py` (M/F/cognomi)
- [ ] `[03.0003]` Seed Erika Lamborghetti (F 14y 24d), Max Volpi (M 14y 32d)
- [ ] `[03.0004]` Batch 4 NPC random
- [ ] `[E0.0500-0506]` `LIFESTAGE_*_THRESHOLDS`, `LifeStagePediatric`/`LifeStagePsychosocial`, `LifeStageService`
- [ ] `[5200_01]` Migrazione `characters` + `lifestage` + `name`
- [ ] CLI `npc list/show/seed/generate/stages/age`

### §3.1 — Genetica [ ]

- [ ] `[03.0030]` `npc/genetics/` (`GenomeCategory` 11+5 sub, `LOCI_LAYOUT` 1024 loci = 2048 alleli)
- [ ] `[03.0031]` Ereditarietà (`generate_from_parents` 1 allele/locus + mutazione 1%)
- [ ] `[03.0032]` Applicazione a nuovi NPC nati
- [ ] `[03.0033]` Gemelli (`generate_twins(identical=True/False)`, `roll_twins` 1.5%/30%)
- [ ] `[03.0034]` `phenotype_from_genome` (altezza, occhi, capelli, pelle, build, faccia)
- [ ] `[03.0035]` Total Realism genetica avanzata (malattie, talenti) → FASE 9

### §3.2 — Bisogni + AI [ ]

- [ ] `[03.0200]` 10 bisogni: HUNGER, THIRST, BLADDER, ENERGY, HYGIENE, SOCIAL, FUN, COMFORT, INTIMACY, SOLITUDE
- [ ] `[03.0201]` Decay + soglie CRITICAL(10)/LOW(30)/OK(70)/HIGH
- [ ] `[03.0202-0209]` Bisogni avanzati (solitudine, stress, desire, ecc.) → Chunk 3.7a/b, 3.9c
- [ ] `[03.0500]` `Action` (8 base + 4 training + 3 pratiche job + 4 addiction + BE_ALONE/SELF_CARE)
- [ ] `[03.0501]` `AIDecisionMaker` utility + tie-break RNG
- [ ] `[03.0502]` `ActionExecutor`, `BTActionExecutor`
- [ ] `[03.0503]` `MoodState` (happiness smoothed 2%/tick), `Moodlet` (duration 30-336 tick, delta −0.15..+0.12)
- [ ] `[03.0508]` `moodlet_for_need` (22 mapping need→state→moodlet)
- [ ] `[01.0030-0035]` `AICoordinator`, `NeedsProcessor`, `AIDecisionMaker`, `ActionExecutor`, `Moodlet`, `DecisionSystem` (utility pura, BT opzionale)
- [ ] `[5200_02]` Migrazione `needs/mood/current_action/last_ai_tick`
- [ ] CLI `npc needs/tick/autoplay`

### §3.2b — NPCManager [ ]

- [ ] `npc/events.py` (`EVENT_NPC_ACTION_STARTED`, `EVENT_NPC_NEED_CRITICAL`, `EVENT_NPC_MOOD_CHANGED`)
- [ ] `npc/manager.py` (`NPCManager`, `NPCState`, `SkillSnapshot`, `flush` batch)
- [ ] CLI `sim start --npcs --autosave-every N --npc-lod LEVEL`

### §3.2c — BT + Memoria + Intimità [ ]

- [ ] `npc/ai/bt/`: `status.py` (`BTStatus`), `base.py` (`BTNode`, `Blackboard`), `composites.py` (Sequence/Selector/Parallel), `decorators.py` (Inverter/Succeeder/Repeat/Cooldown), `leaves.py` (Condition/ActionLeaf/AlwaysSucceed/AlwaysFail/WaitLeaf), `render.py` (`render_tree`)
- [ ] `npc/memory/`: `enums.py` (`MemoryKind` SHORT/LONG/EMOTIONAL, `DECAY_RATES`), `models.py` (`Memory`), `saliency.py`, `service.py` (`record`/`recall`/`decay`)
- [ ] `npc/intimacy/`: `enums.py` (`IntimacyAction` 6, `IntimacyOutcome`), `actions.py` (`INTIMACY_CATALOG` 6 voci con level 0–5), `service.py` (`IntimacyService.perform`)
- [ ] `[5200_05]` Migrazione `memory`
- [ ] CLI `npc memory/intimate/bt-demo`

### §3.2d — BT in AI [ ]

- [ ] `ai/bt_templates.py` (`build_bt_for_action`), `ai/executor.py` (`BTActionExecutor`)
- [ ] CLI `npc bt-tree`, `--bt` su `npc tick/autoplay`

### §3.2e — BT in NPCManager [ ]

- [ ] `NPCManager(use_bt)`, `current_progress` astrae `executor.progress` vs `bt_executor.progress`, skip restore in BT mode
- [ ] CLI `sim start --bt`

### §3.3 — Relationships + Famiglia [ ]

- [ ] `[03.0400]` `npc/relationships/`: `enums.py` (`RelationshipKind` 11), `models.py` (`Relationship` unique `(from, to, kind)`), `service.py` (`create`/`delete`/`relationships_of`), `family_tree.py` (`parents_of`/`children_of`/`siblings_of`/`ancestors_of`/`descendants_of`), `kinship.py` (`relationship_coefficient` path-based, `kinship_coefficient`=r/2, `relationship_name` italiano)
- [ ] `[5200_03]` Migrazione `relationship` + 3 indici
- [ ] Seed Erika↔Max `FRIEND_OF`
- [ ] CLI `npc relate/unrelate/relationships/family/ancestors/descendants/kinship/relationship-kinds`
- [ ] `[03.0401-0415]` Dinamiche avanzate → Chunk 3.9b/c/d/e

### §3.4 — Lifecycle [ ]

- [ ] `[03.0300]` Aging (`AgingService.apply_aging`, transizioni)
- [ ] `[03.0301]` Transizioni con effetti (moodlet da `moodlet_for_need`)
- [ ] `[03.0302]` Invecchiamento progressivo (in `LifecycleManager`)
- [ ] `[03.0303]` Morte (`DeathService` mortalità baseline 1e-5, rampa cubica, max 1/30 a `exp_max`, `DeathCause` 6)
- [ ] `[03.0304]` Eredità e successione (`InheritanceService` 5 tier)
- [ ] `[03.0301b]` Gravidanza (`Pregnancy` 300gg, `PregnancyService`, gemelli 1.5%/30%)
- [ ] `[5200_04]` Migrazione `death_cause` + `pregnancy`
- [ ] CLI `npc conceive/pregnancies/deliver/kill/lifecycle-tick`

### §3.4b — Famiglia attiva [ ]

- [ ] `[03.0401]` `FamilyAI` (età/relazione/aspirazione/tratti/mood/needs/gap tra figli)
- [ ] `[03.0304]` `SuccessionService` (orfani < 25 con genitori morti + BFS tutore)
- [ ] CLI `npc couples/try-conceive/family-ai-tick/orphans/guardian`

### §3.4c — Eredità materiale [ ]

- [ ] `[03.0304]` `npc/economy/`: `enums.py` (`InheritanceTier` 5), `models.py` (`CharacterOwnedLocation`), `service.py` (`WealthService`, `InventoryService`, `PropertyService`), `inheritance.py` (`InheritanceService.distribute` 5 tier: SPOUSE/CHILD/PARENT/SIBLING/OTHER, cash 50% spouse, locations primo erede, objects round-robin)
- [ ] `[5200_06]` Migrazione `athel_balance` + `owner_character_id` + `character_owned_location`
- [ ] CLI `npc wealth/give/inventory/own/unown/legacy/inherit`

### §3.5 — Tratti + Aspirazioni [ ]

- [ ] `[03.0100-0103]` `npc/traits/`: `enums.py` (`Trait` 25+1 `SEXUALLY_EXPLORATIVE`, `TraitCategory` 5, `TraitFamily` 5, `Aspiration` 8), `definitions.py` (`TraitDef`, `TRAIT_DEFS`, `ASPIRATION_WEIGHTS`), `derivation.py` (`derive_traits` con minimo 2 e max 6, `derive_mask_trait` 15%, `derive_aspiration`)
- [ ] `[03.0034]` Tratti ereditari (derivati da genoma)
- [ ] Integrato in `AIDecisionMaker` (utility modifiers)
- [ ] CLI `npc traits/traits-catalog`

### §3.6a-c — Skills [ ]

- [ ] `[03.0500]` `npc/skills/`: `enums.py` (`SkillType` 12, XP `1000+500L` = 115k totale, `DECAY_GRACE_DAYS=90`, `DECAY_RATE_PER_DAY=0.05`, `DEFAULT_TALENT=1.0`, `SKILL_TALENT_FAMILY`), `models.py` (`Skill`), `service.py` (`get_or_create`, `add_progress`, `compute_xp_application`, `compute_decay`, `apply_daily_decay`, `xp_to_next_level`, `level_penalty`, `xp_per_tick`)
- [ ] `[03.0502]` Training actions: `PRACTICE_COMBAT`, `STUDY`, `PRACTICE_ART`, `COOK`, `PRACTICE_CRAFT`, `PRACTICE_TRADE`, `PRACTICE_SERVICE` (FUN+55/60, boost 0.05)
- [ ] `[5200_08]` Migrazione `skill`
- [ ] CLI `npc skills/skill-train/skill-decay`
- [ ] `[03.0034]` `npc/skills/talent.py` (`talent_for_skill` z-score, `talent_map_for_genome`) + `TALENTS_PHYSICAL/MENTAL/SOCIAL/CREATIVE` in `LOCI_LAYOUT`
- [ ] `Job` esteso (`required_skill_type`, `min_skill_level`, `wage_skill_scale`, `promotion_skill_level`, `promoted_title`), `PaydayService` scala wage, promozioni in lifecycle
- [ ] `[5400_02]` Migrazione `job skill extensions`
- [ ] CLI `npc talents`, `economy job-assign --skill`

### §3.6d — Sviluppo dinamico personalità [ ]

- [ ] `[03.0106]` `npc/personality/`: `enums.py` (`ValueAxis` 6 Schwartz, `ACTION_TRAIT_EFFECTS`, `ACTION_VALUE_EFFECTS`, `EVENT_*_EFFECTS`, diminishing returns, `VALUE_MEAN_REVERSION=0.05`, `TRAIT_DECAY_PER_DAY=0.020`), `service.py` (`reinforce_inmemory`, `apply_event_inmemory`, `decay_inmemory`, `sync_from_state`)
- [ ] Integrazione in `BackgroundService.record_event`, `CrisisService.start/recovery`
- [ ] `NPCState.trait_strength`/`values` in-memory + `NPCManager._tick_one` decay ogni 336 tick
- [ ] CLI `npc personality/values/reinforce`

### §3.6e — Values in AI [ ]

- [ ] `utility._values_boost` = `1 + 0.6 × Σ(values-0.5) × alignment(action)`, `alignment = ACTION_VALUE_EFFECTS / ALIGNMENT_SCALE`, clamp `[0.70, 1.40]`
- [ ] `AICoordinator.tick(..., values=...)`, `NPCManager._tick_one` passa `state.values`

### §3.6f — Identità sessuale + SEP + Cultura [ ]

- [ ] `npc/identity/`: `enums.py` (`TabooReaction` 3, `CulturalTradition` 4, `TRADITION_RANGES`), `models.py` (`Sexuality` 4 dim `[0,1]`, `SEP` knowledge[0,100]/comfort/inhibition/received_at_age, `CulturalProfile` permissiveness/modesty/gender_role_strict/taboo, `IdentityProfile`), `service.py` (`initialize_sexuality` 70% standard/30% continuo, `initialize_sep` per età, `initialize_culture` con eredità genitori, `apply_sexuality_drift` mensile σ=0.03), `gender.py` (`GenderIdentity` 5, `is_cisgender`, `is_heterosexual`), `lgbtq.py` (`LGBTQService.is_lgbtq`, disclosure level, acceptance factor da cultura)
- [ ] Tratto `SEXUALLY_EXPLORATIVE`
- [ ] Fattori in `ConsentService`: `sep_factor = 0.5 + comfort×(1-inhibition)`, `cultural_factor` (modesty penalty, permissiveness bonus, taboo)
- [ ] CLI `npc identity/lgbtq/talents`

### §3.6g — Vizi e dipendenze [ ]

- [ ] `npc/addictions/`: `enums.py` (`AddictionKind` 5, `INITIAL_DEPENDENCE`, `DEPENDENCE_PER_USE`, `INITIATION_PROBABILITY`, `CRAVING_THRESHOLD_*`, `DECAY_GRACE_DAYS=90`, `DECAY_RATE_PER_DAY=0.10`, `MOODLET_*_DELTA`), `models.py` (`Addiction` unique `(char, kind)`), `service.py` (`use` con iniziazione probabilistica, `craving_factor`, `daily_tick` con `MILD`/`STRONG`/`WITHDRAWAL`, `start_addiction`)
- [ ] `[5200_09]` Migrazione `addiction`
- [ ] 4 azioni: `CONSUME_ALCOHOL`, `SMOKE`, `GAMBLE`, `DRINK_COFFEE`
- [ ] `AIDecisionMaker` boost `1 + craving × 0.4`
- [ ] Hook in `LifecycleManager` daily (craving moodlet + withdrawal + decay)
- [ ] Seed: **garantita almeno 1** addiction tra gli adulti + 2 uses iniziali
- [ ] CLI `npc addictions/addiction-start/addiction-use`

### §3.6h — Background narrativo [ ]

- [ ] `npc/background/`: `enums.py` (`FormativeEventKind` 10, `SEVERITY_RANGES`, `EVENT_VALENCE`, `MEMORY_THRESHOLD=0.5`, `BULLY_TIMID_THRESHOLD=0.6`), `models.py` (`FormativeEvent` unique `(char, kind, occurred_at_age)`), `service.py` (`record_event` + effetti identità + forza trait + memoria + personality, `generate_seed_events` per età, `persist_seed_events`)
- [ ] `[5200_10]` Migrazione `formative_event`
- [ ] Hook runtime: `PARENT_LOST` quando un character muore (figli < 25)
- [ ] CLI `npc background/background-add`

### §3.7 — Bisogni avanzati [ ]

- [ ] `[03.0202]` `SOLITUDE` + `BE_ALONE` (action + decay + utility)
- [ ] `[03.0204]` `DEEP_TALK` (intimità cognitiva)
- [ ] `[03.0205]` `StressService` (`STRESS_WEIGHTS` critici/mood/inhibition/rejection/poverty/fatigue, fattori da `Needs`/`Mood`/`Identity`/`Relationship.metadata_json["last_rejection_at"]`/`athel_balance`)
- [ ] `[03.0206]` `DesireService` (`baseline` da sexuality, `recompute` con age_peak/abstinence/stress/mood/refractory, `mark_satisfied`)
- [ ] `[03.0207]` Azioni sostitutive: `CUDDLE`, `HOLD_HANDS`, `DEEP_TALK`, `SHARE_MEAL`
- [ ] `[03.0208]` `SELF_CARE`
- [ ] `[03.0209]` `TEXT_MESSAGE`, `VIRTUAL_CALL`
- [ ] `ConsentService` integra `stress_factor` (−0.5×stress) e `desire_factor` (level≥3, `0.5+0.5×desire`)

### §3.9 — Famiglia e Relazioni avanzate [ ]

- [ ] `[03.0409]` `npc/reputation/`: `enums.py` (`GossipTopic` 8, `TOPIC_SENTIMENTS`, `CONSANGUINITY_THRESHOLD=0.125`), `models.py` (`Opinion`, `GossipEvent`), `service.py` (`get_opinion`, `update_opinion`, `spread` con credibility/confirmation/culture_mod, `broadcast`, `is_consanguineous`, `consanguinity_severity`, `witnesses_in_same_location`)
- [ ] `[03.0406]` Consanguineità taboo (in `ConsentService` come `consanguinity_factor` quando severity > 0)
- [ ] `[5200_11]` Migrazione `opinion + gossip_event`
- [ ] CLI `npc reputation/opinion/gossip/consanguinity`
- [ ] `[03.0412]` `BoredomService` (`DAILY_BOREDOM_GROWTH=0.005`, `NOVELTY_REDUCTION=0.05`, `STALE_THRESHOLD=0.90`, `register_action`)
- [ ] `[03.0407]` `BreakupService` (`DAILY_BREAKUP_PROBABILITY=0.01`, `breakup` rimuove relazione + `EX_PARTNER_OF` + moodlet + memoria + opinion negativa)
- [ ] `[03.0411]` `InfidelityService` (`should_consider` richiede partner + desire > 0.7 + opinion > 40 + boredom > 0.4, `resolve_discovery` con in-location 70% / witness 30% / rumor 5%)
- [ ] `[03.0410]` `CompatibilityService` (trait Jaccard 0.4, sexual fit 0.35, cultural 0.25)
- [ ] `[03.0413]` `ConnectionService` (`INITIAL_CONNECTION=0.10`, `BASE_GAIN=0.010+0.008×level`, `DAILY_DECAY=0.003`, `label`)
- [ ] `[03.0414]` `LibidoService` (`initialize_baseline`, `effective` per relazione con compat e conn, `asymmetry_factor` penalty fino a 0.4)
- [ ] `[03.0415]` Tratto `EMOTIONALLY_EXPRESSIVE` + `ConsentService` +0.10
- [ ] `ConsentService` integra `compatibility`, `connection`, `libido` (solo level ≥ 3)
- [ ] `[03.0401]` `MentorshipService` (`evaluate`, `register_session` con trait transfer 3%, culture shift, graduation 20 sessioni, boost talent +0.20), `MENTOR_OF`
- [ ] `[03.0408]` `IntergenerationalService` (`opinion_bonus` da gap età)
- [ ] `[03.0404]` `PolyamoryService` (`accepts_polyamory`, `current_partners`, `can_add_partner`)
- [ ] `[03.0405]` `LGBTQService` (già in 3.6f)
- [ ] `[03.0403]` `TeenDynamicsService` (`willingness_modifier` per teen, `parental_opposition_factor`)
- [ ] CLI `npc mentorships/mentor-eval/mentor-start/age-gap/polyamory-check/polyamory-add/teen-check/lgbtq/lgbtq`

### §3.11 — Consenso attivo intimità [ ]

- [ ] `intimacy/consent.py`: `ConsentService`, `ConsentResult`, `BASE_WILLINGNESS=0.50`, `ACTION_LEVEL_PENALTY=0.15`, `REJECTION_COOLDOWN_TICKS=100`, `NOVELTY_WINDOW_TICKS=30`, `REJECTION_PENALTY=0.30`, `NOVELTY_PENALTY=0.70`, `TRAIT_WILLINGNESS_MODIFIERS`
- [ ] Fattori: base × action × relationship × mood × needs × traits × SEP × culture × consanguinity × lgbtq × teen × parental × stress × desire × recency
- [ ] Rejection: moodlet "Rifiutato" −0.15/100t, bond −0.02, strength −0.01, memory −0.6, cooldown
- [ ] `IntimacyService.perform(force=False)` integra consenso
- [ ] CLI `npc consent`, `intimate --force`

### §3.12 — Consapevolezza sociale [ ]

- [ ] `npc/social_awareness/`: `enums.py` (`TraitVisibility` VISIBLE/MODERATE/HIDDEN, `DISCOVERY_PROBABILITY`, `CONFIDENCE_INCREMENT=0.20`, `INTENSITY_BY_LEVEL`, `FAMILY_INITIAL_CONFIDENCE=0.50`, `PARTIAL_THRESHOLD=0.30`, `OWN_CULTURE_AWARENESS=1.0`, `OTHER_CULTURE_AWARENESS=0.10`), `service.py` (`known_traits`, `partial_known_traits`, `cultural_awareness`, `initialize_for`, `initialize_family_knowledge`, `record_interaction` con `_maybe_learn_culture`)
- [ ] Hook in `IntimacyService._apply_success` (record_interaction dopo azione)
- [ ] Hook in `LifecycleManager` daily (passive discovery 15%/coppia/location)
- [ ] CLI `npc knows/discover/cultural-knowledge`

### §3.13-3.15 — Riflessione + Narrazione + Crisi [ ]

- [ ] `npc/reflection/`: `enums.py` (`ReflectionKind` 6, `CrisisPhase` 3, `REFLECTION_INTERVAL_DAYS=7`, `NEGATIVE_STREAK_FOR_CRISIS=3`, `STRESS_CRISIS_THRESHOLD=0.85`, `STRESS_DAYS_FOR_CRISIS=3`, `MIN_CRISIS_DURATION_DAYS=5`, `RECOVERY_*`), `models.py` (`ReflectionEntry`), `templates.py` (`compose_reflection` template-based: apertura+corpo+sentiment), `service.py` (`reflect` con auto-detect kind [CRISIS/REGRET/GRATITUDE/RESOLVE/OBSERVATION], mood effect, memory), `crisis.py` (`CrisisService.get_status/check_trigger/start_crisis/recovery_tick`), `narrative.py` (`LifeNarrativeService.compose` con capitoli da background/famiglia/skill/riflessioni/stato)
- [ ] `[5200_12]` Migrazione `reflection_entry`
- [ ] Hook settimanale + crisi in `LifecycleManager` daily
- [ ] CLI `npc reflections/reflect/narrative/crisis/crisis-start`

### §3.1 (architettura coscienza NPC) — SOSPESO

- [ ] `[03.0014]` Architettura `Anima Digitale` ↔ `Personalità Agente` → track separato LLM/ClaireOS, dopo la baseline single-player; non confonderlo con la FASE 8 (Multiplayer)

### §3.2 / 3.4 / 3.5 — SOSPESI (UI-driven)

- [ ] `[03.0020-0029]` Editor creazione personaggio (UI)
- [ ] `[03.0040-0043]` Fase finale creazione (quartiere/lotto/fondi) — parziale: `Athel_balance` già generato
- [ ] `[03.0050]` Scenari predefiniti (UI)

---

## FASE 4 — WORLD (range 5300–5399)

### §4.0 — UI MVP [ ]

- [ ] `simai/ui/` (FastAPI + Jinja2 + static bootstrap/htmx/alpine/d3/chart)
- [ ] `ui/app.py` (`create_app`, `templates` globale con `simai_version`)
- [ ] `ui/routes/`: `dashboard.py`, `npcs.py`, `world_routes.py` (rinominato da `world.py`), `economy_routes.py` (rinominato da `economy.py`), `live.py`, `api.py`, `build_routes.py`, `city_routes.py`, `transport_routes.py`
- [ ] Template: `base.html`, `dashboard.html`, `npcs_list.html`, `npc_detail.html`, `npc_tree.html` (D3), `world_list.html`, `world_detail.html`, `districts_list.html`, `district_detail.html`, `lots_list.html`, `economy.html`, `economy_lots.html`, `live.html`, `partials/live_fragment.html`, `build_editor.html`, `city.html`, `infrastructure.html`, `transport.html`, `transits.html`
- [ ] `ui/static/css/simai.css`, `ui/static/js/simai.js`
- [ ] CLI `ui serve --host/--port/--reload/--open`

### §4.1 — District + Lot [ ]

- [ ] `[04.0001]` `world/district.py` (`District` con bounds, tax_rate, safety_rating, aesthetic_score, `DistrictType` 5), `world/lot.py` (`Lot` con bounds, usage, base_price, location_id, current_value, `LotUsage` 6)
- [ ] `world/lot_service.py` (`create_district`, `create_lot`, `district_summaries`, `lot_summaries`, `attach_location`, `update_lot_usage`)
- [ ] `[5300_02]` Migrazione `districts, lots`
- [ ] CLI `world districts/district-create/lots/lot-create`
- [ ] UI `/world/districts`, `/world/lots`

### §4.2 — Property + Mortgage [ ]

- [ ] `economy/property.py`: `LotOwnership` unique `(char, lot)`, `Mortgage` (principal, remaining, rate, term, monthly, next_payment, status), `LotOwnershipService`, `MortgageService` (`compute_monthly_payment` formula francese, `pay_installment`, `foreclose`), `PropertyTaxService.monthly_tax_for` + `collect_all`, `LotPurchaseService.buy_cash/buy_with_mortgage/sell`
- [ ] `[5300_03]` Migrazione `lot_ownership, mortgage`
- [ ] CLI `economy lots-owned/lot-buy/lot-sell/mortgages/mortgage-pay/property-tax`
- [ ] UI `/economy/lots` + link da `/economy`

### §4.2b — Housing AI [ ]

- [ ] `npc/housing/`: `enums.py` (`HousingAction` 6, `MIN_AGE_BUY=18`, `MIN_AGE_BUY_SHOP=22`, `MIN_SKILL_FOR_SHOP=5`, `MIN_RESERVE=200`, `BROKE_THRESHOLD=100`, `SENIOR_AGE=65`, `BUY_HOME_PROBABILITY=0.03`, `BUY_SHOP_PROBABILITY=0.01`, `SELL_PROBABILITY=0.10`, `MAX_PURCHASES_PER_DAY=2`), `ai.py` (`RealEstateAI.daily_tick`, `_maybe_buy_home/shop`, `_maybe_sell` broke/senior, `_execute_purchase` cash/mutuo, `_move_into_lot`)
- [ ] Hook in `LifecycleManager` daily
- [ ] CLI `economy real-estate-tick`

### §4.3 — Build mode [ ]

- [ ] `world/build/`: `enums.py` (`WallOrientation` H/V, `OpeningKind` DOOR/WINDOW, `WallMaterial` 4, `MAX_GRID_SIZE=50`, `MIN_ROOM_SIDE=1`, `MIN_ROOM_AREA=2`), `models.py` (`Wall` unique `(lot, x, y, orientation)`, `Opening` unique `wall_id`), `room_detector.py` (`DetectedRoom`, `detect_rooms` con flood fill e edge blocking), `service.py` (`BuildService.add_wall/remove_wall/clear_walls/set_opening/remove_opening/recompute_rooms`)
- [ ] `[5300_04]` Migrazione `wall, opening`
- [ ] CLI `world build-show/build-wall/build-clear`
- [ ] UI `/world/lots/{id}/build` (canvas 2D con tool wall/door/window/delete, auto-rooms on/off, ricalcola stanze)

### §4.4 — Buy mode [ ]

- [ ] `world/buy/`: `enums.py` (`ObjectCategory` 8, `ALLOWED_ROTATIONS` 4, `MAX_OBJECTS_PER_LOT=200`), `models.py` (`ObjectCatalog` con footprint, `is_container`, `icon`), `service.py` (`BuyService.list_catalog/place_object/move_object/remove_object`, `_check_bounds`, `_check_object_overlap`, `_find_room_for_cell`)
- [ ] `GameObject` esteso (`catalog_type_id`, `lot_id`, `position_x/y`, `rotation`)
- [ ] `[5300_05]` Migrazione `object_catalog` + 5 colonne su `game_object`
- [ ] `world/buy/seed.py` (`CATALOG_ENTRIES` 32 voci)
- [ ] CLI `world catalog/place-object/objects-on-lot`
- [ ] UI build editor con catalogo (selezione + tool place)

### §4.4b — Acquisto con pagamento [ ]

- [ ] `world/buy/supplier.py` (`SupplierService.offers_of/find_supplier/get_offer/decrement_stock/restock_all`, `RESTOCK_PER_TYPE=5`, `MAX_STOCK_PER_TYPE=30`)
- [ ] `place_object` accetta `buyer` + `supplier_location_id`, scala cash + stock, `current_dt` per Transaction
- [ ] Seed fornitore "Forniture del Quartiere" (12 `ShopItem` risorse) + "Emporio dell'Arredo" (32 `ShopItem` arredi)
- [ ] Hook restock in `LifecycleManager` daily
- [ ] CLI `economy suppliers/restock`, `world place-object --buyer --supplier`

### §4.4c — UI buyer [ ]

- [ ] `api_catalog` ritorna `supplier_price`, `supplier_stock`, `sales_tax_rate`
- [ ] `api_place_object` accetta `buyer_id`, `supplier_location_id`, ritorna `cost_paid`, `item_price`, `tax_paid`
- [ ] UI: `<select id="buyer-select">` con localStorage per-lotto, opacity inaffordabili, badge stock, prezzo `X+Y`
- [ ] Toast con breakdown "Acquistato: X + Y (tax) = Z"

### §4.5 — Style mode [ ]

- [ ] `world/style/`: `enums.py` (`StyleKind` FLOOR/WALL, `WallSide` INTERIOR/EXTERIOR), `models.py` (`StyleCatalog` con color/pattern/icon, `FloorTile` unique `(lot, x, y)`, `WallCovering` unique `(wall, side)`), `service.py` (`StyleService.set_floor/set_wall_style/clear_floor/clear_wall_style/clear_all`), `seed.py` (`STYLE_ENTRIES` 21 voci: 11 floor + 10 wall, pattern solid/wood/tile/stripes/floral/dots/brick/marble/stone)
- [ ] `[5300_06]` Migrazione `style_catalog, floor_tile, wall_covering`
- [ ] CLI `world styles --kind/set-floor/set-wall-style`
- [ ] UI build editor con tool FLOOR/WALLSTYLE + `<select id="style-kind">`

### §4.6 — Terrain mode [ ]

- [ ] `world/terrain/`: `enums.py` (`TerrainType` 8, `MAX_HEIGHT=3`, `FLAT_ONLY`, `BLOCKING_TERRAINS`), `models.py` (`TerrainTile` unique `(lot, x, y)`), `service.py` (`TerrainService.set_terrain/clear_tile/clear_all`, costo `TERRAIN_BASE_COST=3` + `TERRAIN_ELEVATION_COST=5`/livello, `FLAT_ONLY` validation), `palette.py` (`TERRAIN_COLORS`, `TERRAIN_LABELS`, `lighten_hex` per elevazione)
- [ ] `[5300_07]` Migrazione `terrain_tile`
- [ ] CLI `world terrain-types/set-terrain/terrain-show`
- [ ] UI build editor con tool TERRAIN + slider elevation 0–3

### §4.7 — Città [ ]

- [ ] `city/`: `enums.py` (`PublicServiceType` 6, `TaxKind` 3, `INCOME_TAX_RATE=0.10`, `SALES_TAX_RATE=0.05`, `DEFAULT_DAILY_COST`, `DEFAULT_QUALITY=0.6`, `DEFAULT_COVERAGE_RADIUS=40`), `models.py` (`PublicService` unique `(district, type)`, `CityBudget` singleton, `TaxPayment`), `service.py` (`CityService.get_budget/add_revenue/add_expense/register_service/all_services/services_of_district/daily_tick` con quality degradation −0.02/giorno se non pagato), `tax.py` (`TaxService.preview_sales_tax/total_with_tax/collect_income_tax/collect_sales_tax/collect_property_tax/payments_of`), `satisfaction.py` (`SERVICE_TO_AREA`, `SATISFACTION_WEIGHTS` safety 0.20/health 0.18/education 0.18/cleanliness 0.17/wellbeing 0.15/infrastructure 0.12, `SatisfactionService.compute_district/compute_all`), `seed.py` (`seed_demo_city`: police/hospital/school/garbage/park)
- [ ] `[5300_08]` Migrazione `public_service, city_budget, tax_payment`
- [ ] Hook in `PaydayService.process` (income tax), `PropertyTaxService.collect_all` (property → CityBudget), `LifecycleManager` daily (city tick)
- [ ] CLI `city services/register-service/budget/tick/taxes/satisfaction`
- [ ] UI `/city` (bilancio, servizi, soddisfazione, tasse)

### §4.7b — Soddisfazione→mood [ ]

- [ ] `city/mood.py` (`CityMoodService.daily_tick` con cache per distretto, moodlet "Servizi buoni/scadenti/eccellenti/in rovina" + aree specifiche sotto soglia, `CITY_MOODLET_DURATION=336`)
- [ ] Hook in `LifecycleManager` daily
- [ ] CLI `city citizens-mood/mood-tick`
- [ ] UI `/city` con tabella moodlet auto-refresh (htmx + JSON parse)

### §4.7c — Sales tax su acquisti [ ]

- [ ] `TaxService.preview_sales_tax/total_with_tax`
- [ ] `MarketService.buy` e `BuyService.place_object` applicano 5% tax, `item_price`/`tax_paid`/`cost_paid` in result
- [ ] Transaction con `metadata_json["sales_tax"]`
- [ ] UI mostra `X+Y` e toast con breakdown
- [ ] CLI `economy buy` mostra breakdown
- [ ] IVA/accise/successione → FASE 5

### §4.8 — Crafting [ ]

- [ ] `npc/crafting/`: `enums.py` (`CraftingQuality` POOR/COMMON/GOOD/EXCELLENT, `QUALITY_PRICE_MULTIPLIER` 0.6/1.0/1.5/2.5, `SKILL_LEVEL_COMMON=3/GOOD=8/EXCELLENT=14`, `QUALITY_JITTER_SIGMA=0.05`), `recipes.py` (`Recipe` 10, `RECIPES`, `RESOURCE_NAMES` 12, `RESOURCE_PRICES`), `service.py` (`CraftingService.craft` con skill check + input consume + quality `base + skill_bonus×(lvl/20) + gauss`, +15 XP, `CraftResult`, `missing_inputs`, `inventory_count`)
- [ ] `[5300_05]` (già coperto) — usati `GameObject` esistenti
- [ ] CLI `npc recipes/resources/craft`

### §4.8b — Crafting AI + quality pricing [ ]

- [ ] `npc/crafting/ai.py` (`CraftingAI.maybe_craft` con `BASE_TICK_PROBABILITY=0.0015`, `SKILL_LEVEL_BONUS=0.10`, `MAX_CRAFTS_PER_DAY_PER_NPC=3`, `CraftingTickReport`)
- [ ] `NPCState.crafts_today`/`last_craft_day_index`, contatore resettato a cambio giorno
- [ ] `MarketService.sell` legge `metadata_json["quality_label"]` e applica multiplier
- [ ] `SaleResult` esteso (`quality_label`, `base_price`)
- [ ] CLI `economy sell` mostra breakdown

### §4.8c — UI inventario + vendita [ ]

- [ ] Endpoint `/api/npcs/{id}/inventory.json` (con `crafted`, `quality_label`, `quality_value`)
- [ ] Endpoint `/api/items/{type}/buyers.json`
- [ ] Endpoint `POST /api/npcs/{id}/sell` (usa `MarketService.sell` con quality pricing)
- [ ] Tab "Inventario" in `/npcs/{id}` con badge qualità colorati (POOR rosso, COMMON grigio, GOOD azzurro, EXCELLENT verde)
- [ ] Modal Bootstrap per scelta negozio + conferma vendita

### §4.9 — Infrastructure [ ]

- [ ] `city/infrastructure/`: `enums.py` (`RoadType` 4, `RoadCondition` 5, `LightType` 3, `ROAD_COSTS`, `LIGHT_COSTS`, `LIGHT_RADII`, `ROAD_DAILY_DEGRADATION=0.001`, `LIGHT_DAILY_DEGRADATION=0.0005`, `LIGHT_OFF_CONDITION=0.20`), `models.py` (`RoadTile`, `StreetLight`), `service.py` (`InfrastructureService.place_road/place_light/remove_road/remove_light/lighting_coverage_at/district_roads_coverage/district_lighting_coverage/daily_tick/clear_all`, `MAX_COORD=199`)
- [ ] `[5300_09]` Migrazione `road_tile, street_light`
- [ ] `SatisfactionService` esteso: area `infrastructure` peso 0.12 + safety bonus da illuminazione (+0.10 max)
- [ ] Hook degrado in `LifecycleManager` daily
- [ ] CLI `city infra-costs/road-place/light-place/road-remove/light-remove/infra-list/infra-tick/coverage`
- [ ] UI `/world/infrastructure` (canvas con griglia, strade, lampioni, raggi)

### §4.9b — Upkeep + riparazione [ ]

- [ ] Costo giornaliero 1 Athel/lampione dal CityBudget
- [ ] `repair_road`, `repair_light` (azione + costo)
- [ ] Auto-degradation acceleration se inquinato
- [ ] Illuminazione notturna dinamica (ON 19-7)

### §4.10 — Transport [ ]

- [ ] `city/transport/`: `enums.py` (`TransportMode` 5, `VehicleType` 2, `RouteType` 2, velocità 0.5/1.9/5.0/3.0/7.5, `BUS_FARE=2`, `METRO_FARE=3`, `CAR_FUEL_PER_CELL=1.5`, `CAR_FUEL_COST_PER_CELL=0.15`, `VEHICLE_PRICES` CAR=2500/BIKE=150), `models.py` (`Vehicle` unique `(owner, type)`, `TransportRoute`, `RouteStop` unique `(route, seq)` e `(route, loc)`), `service.py` (`TransportService.vehicle_of/vehicles_of/buy_vehicle/refuel_car/all_routes/stops_of/routes_serving_location/create_route/plan/plan_all/travel/home_location_id/work_location_id/daily_commute`), `seed.py` (`seed_demo_routes`: bus + metro)
- [ ] `[5300_10]` Migrazione `vehicle, transport_route, route_stop`
- [ ] Hook `daily_commute` in `LifecycleManager` daily
- [ ] CLI `transport vehicles/buy-vehicle/refuel/routes/route-stops/plan/travel`
- [ ] UI `/transport` (linee + veicoli)

### §4.10b — Pathfinding + transito [ ]

- [ ] `city/transport/pathfinding.py` (`RoadGraph`, `RoadPath`, A* 4-direzionale con penalty condition, `_CONDITION_PENALTY_WEIGHT=2.0`)
- [ ] `city/transport/transit.py` (`TransitJob` con `legs` metadata, `TransitService.start/tick/compute_progress/active_job_ids/is_in_transit/cancel`, `TransitStatus` 3)
- [ ] `EVENT_NPC_ARRIVED`
- [ ] `NPCManager.update_all_npcs` salta `report.in_transit_ids`
- [ ] `TransitService.tick` in `LifecycleManager.tick` ad ogni tick
- [ ] `TransitService.plan_all` usa `RoadGraph` se disponibile, altrimenti geometrico
- [ ] `[5300_11]` Migrazione `transit_job`
- [ ] CLI `transport travel --instant`, `transit-list`, `transit-status`

### §4.10c — Multi-tratta + UI live [ ]

- [ ] `city/transport/multi_leg.py` (`TravelLeg`, `MultiLegPlan`, `MultiLegPlanner.plan_all` walk+bus/metro+walk, `MAX_WALK_TO_STOP=25`, `MAX_TOTAL_WALK=50`, `TRANSFER_PENALTY_TICKS=3`, dedup + cap 20)
- [ ] `TransitService.start` accetta `MultiLegPlan`, `compute_progress` per UI
- [ ] CLI `transport plan-multi/travel-multi`
- [ ] UI `/transport/transits` (canvas 200×200, linee+stop+transiti interpolati), endpoint `/api/transport/transits.json` con `from_xy`/`to_xy`/`progress`/`legs`
- [ ] Refresh ogni 3s

### §4.10d — Miglioramenti futuri [ ]

- [ ] Percorso su polyline (non solo interpolazione lineare from→to)
- [ ] Timing bus/metro reali (orari)
- [ ] Tracking preciso per-leg

---

## FASE 5 — ECONOMY (range 5400–5499)

### §5.0 — Economia base [ ]

- [ ] `[05.0000]` `economy/enums.py` (`JobType` 10, `TransactionKind` 9, `MortgageStatus` 4, `DEFAULT_WAGES`, `SHOP_RESALE_MARGIN=0.20`), `models.py` (`Job` unique `(char)` esteso, `ShopItem`, `Transaction`), `jobs.py` (`JobService.assign/quit/job_of/all_active_jobs` con skill validation + wage scaling), `market.py` (`MarketService.items_in/find_item/buy/sell` con quality-based pricing + sales tax), `payday.py` (`PaydayService.is_payday/process` con income tax), `seed.py` (`seed_demo_economy`)
- [ ] `[5400_01]` Migrazione `job, shop_item, transaction`
- [ ] `[5400_02]` Migrazione `job skill extensions`
- [ ] `[00.0014b]` CLI `economy seed/jobs/job-assign/job-quit/wages/shops/shop/buy/sell/payday/transactions/stats`
- [ ] UI `/economy`

### §5.1 — Banche, mutui, investimenti [ ]

- [ ] `[05.0010]` `Bank`, `BankAccount`, `Deposit`, `Loan` (mutui già in 5300_03 ma mancano banca + interessi attivi)
- [ ] Tassi variabili, banche multiple
- [ ] Investimenti azionari
- [ ] Conti correnti + interessi passivi

### §5.2 — Tasse avanzate [ ]

- [ ] `[05.0020]` IVA/accise (oltre sales tax base)
- [ ] Tassa di successione
- [ ] Esenzioni e detrazioni
- [ ] Fisco progressivo

### §5.3 — AION (piattaforma commerciale) [ ]

- [ ] `[05.0030]` AION marketplace (acquisto/vendita NPC↔NPC)
- [ ] `[05.0040]` Spedizioni cargo (multi-location, tracking)
- [ ] `[05.0050]` Mercato azionario locale

---

## FASE 6 — POLITICS (range 5500–5599)

- [ ] `[06.0000]` Governo, elezioni, partiti
- [ ] `[06.0010]` Leggi e regolamenti
- [ ] `[06.0020]` Servizi pubblici politici (sanità, scuola, sicurezza già in city, ma mancano leggi)
- [ ] `[06.0030]` Costituzione di Anthal — framework legale
- [ ] `[06.0040]` Partecipazione civica, proteste

---

## FASE 7 — SONET (range 5600–5699)

- [ ] `[07.0000]` Identità digitale del cittadino
- [ ] `[07.0010]` Servizi online (documenti, prenotazioni, pagamenti)
- [ ] `[07.0020]` Fascicolo sanitario elettronico
- [ ] `[07.0030]` Fascicolo scolastico
- [ ] `[07.0040]` Dichiarazione dei redditi
- [ ] `[07.0050]` Votazioni digitali

---

## FASE 8 — MULTIPLAYER (range 5700–5799)

- [ ] `[08.0000]` Architettura client-server
- [ ] `[08.0010]` Sincronizzazione stato (WebSocket / UDP)
- [ ] `[08.0020]` Server authority su NPC e mondo
- [ ] `[08.0030]` Scaling (sharding per quartiere/regione)
- [ ] `[08.0040]` Persistenza multiplayer (PostgreSQL cluster)
- [ ] `[08.0050]` Anti-cheat
- [ ] `[08.0060]` Chat globale e vocale
- [ ] `[08.0070]` Economia persistente cross-server
- [ ] `[08.0080]` Sistema di "istanze" per eventi

---

## FASE 9 — HARDENING / DEBITO TECNICO

- [ ] `[09.0000]` Refactor e hardening generale
- [ ] `[09.0010]` Ottimizzazione performance (profilazione, cache, `RoadGraph` cache)
- [ ] `[09.0020]` Documentazione tecnica completa
- [ ] `[09.0030]` Sistema di plugin/estensioni utente
- [ ] `[09.0040]` Analizzatore statico + fix mypy/pyright residui
- [ ] `[09.0050]` Setup deploy e distribuzione

### Debiti tecnici specifici

- [ ] **VI.1** Miglioramenti abbigliamento (pattern, poligenici, dominanza)
- [ ] **VI.2** Build mode enhancements (anteprima 3D, undo/redo, snap, roof styles, collision)
- [ ] **VI.3** Regolamenti ambientali (inquinamento, ispezioni, multe)
- [ ] **VI.4** Lavoro/trasporti NPC (`TravelAction` generica, stipendio, skill→performance)
- [ ] **VI.5** AION spedizioni cargo
- [ ] **VI.6** Pathfinding multi-tratta (`TravelAction` generica)
- [ ] **VI.7** Veicoli privati NPC (uso, carburante)
- [ ] **VI.8** Accessibilità trasporti (filtro rotte accessibili)
- [ ] **VI.9** Crisi di mezza età (`apply_midlife_crisis_effects`)
- [ ] **VI.10** Albero genealogico d3.js
- [ ] **VI.11** Analisi errori pregressi (già risolti: `target_location`, `partner`, `is_parent_of`, `NameGenerator`, `NPCAIService`, enum `LifeStage` duplicato, firme `ActionExecutor`, N+1, cache `WorldState`, indici FK)
- [ ] **VI.12** Note architetturali aperte (URL UI, test policy, `WorkflowTransition`)

### Miglioramenti FASE 4 rimandati

- [ ] `4.10d` polyline + timing bus/metro reali + tracking per-leg
- [ ] `4.9b` upkeep + riparazione infrastrutture
- [ ] `4.8d` alberi crafting multi-livello
- [ ] `4.7d` IVA/accise/successione
- [ ] `4.6b` rendering isometrico terrain
- [ ] `4.5b` preview visuale pattern
- [ ] `4.3b` materiali muro con costo + skill
- [ ] `4.2c` banche multiple + tassi variabili

### Task FASE 3 sospesi

- [ ] `3.1.14` Architettura coscienza NPC (→ LLM)
- [ ] `3.2.20-0029` Editor creazione personaggio (UI)
- [ ] `3.4.40-0043` Fase finale creazione quartiere/lotto/fondi (UI) — parziale (`Athel_balance` già generato)
- [ ] `3.5.50` Scenari predefiniti (UI)

---

## TEST BILANCIAMENTO 60 ANNI (RIMANDATO)

Dopo fix di Chunk 3.x, non è stato ri-eseguito il run 60 anni. Ultimo run 1 anno: valori OK (values 0.5-0.6, traits non saturi, skill job > 0, relazioni > 0 dopo fix `location_id`, addictions 1+ dopo fix seed). Rifare per validare.

**Griglia valutazione attesa**:

- Skill: max 15-20, at_max < 20%, 4-8 skill/NPC
- Trait attivi: 3-6 per NPC, 10-15 con n≥50%
- Values avg: 0.40-0.60
- Addictions: 15-35% NPC, dep 20-50
- Relazioni: partner 30-60% adulti, boredom avg 0.20-0.50, connection avg 0.20-0.50
- Reflections: 50-500/NPC (60 anni)
- Crisis: 0-10% attive, 20-60% storiche
- Bilanci: 1000-10000 Athel mediani
- Job: 30-70% adulti impiegati

---

## 🧪 TASK TRASVERSALI DA AGGIUNGERE ALLA ROADMAP

Queste attività non sostituiscono i task esistenti: sono prerequisiti che impediscono al progetto di accumulare sistemi non verificabili.

- [ ] **XT.01 — Audit del repository**: mappare moduli esistenti, entry point, migrazioni, dipendenze e test; associare ogni task al codice effettivo.
- [ ] **XT.02 — Test policy**: `pytest`, fixture DB temporaneo, test dei servizi e delle migrazioni, smoke test CLI e copertura dei bug già risolti.
- [ ] **XT.03 — Test determinismo**: stesso seed + stessa configurazione + stessi comandi = stesso stato logico e stesso report, salvo campi esplicitamente non deterministici.
- [ ] **XT.04 — Contratto del tick**: ordine canonico dei sistemi, gestione errori, atomicità e recupero dopo interruzione.
- [ ] **XT.05 — Contratti evento**: payload tipizzati/versionati, ordinamento, idempotenza, distinzione fra eventi persistenti e notifiche runtime.
- [ ] **XT.06 — Versionamento dei salvataggi**: schema version, migrazioni del payload, checksum/integrità, test di file troncati/corrotti e restore.
- [ ] **XT.07 — Invarianti di dominio**: bilanci mai NaN/infiniti, nessun saldo negativo dove vietato, riferimenti FK validi, nessuna doppia nascita/morte/paga/transazione.
- [ ] **XT.08 — Benchmark baseline**: numero NPC, tick/s, tempo per tick, query DB, memoria e tempo di salvataggio per scenari standard.
- [ ] **XT.09 — Test di bilanciamento versionati**: run 1/10/60 anni con seed fissi, soglie motivabili e report confrontabili fra release.
- [ ] **XT.10 — Threat model minimo**: segreti fuori dal repository, validazione input CLI/API, protezione dei salvataggi, backup e log senza dati sensibili.
- [ ] **XT.11 — Registro decisioni architetturali (ADR)**: documentare decisioni non banali, alternative scartate e conseguenze.
- [ ] **XT.12 — Definizione del perimetro LLM**: API astratta, timeout, fallback, budget di risorse, isolamento e divieto di accesso diretto dell'LLM al DB.
- [ ] **XT.13 — Separazione single-player/multiplayer**: identificare le assunzioni non compatibili con concorrenza e autorità server prima della FASE 8.
- [ ] **XT.14 — Revisione del backlog**: deduplicare ID riutilizzati (es. `03.0304`, `03.0401`, `03.0500`), distinguere ID requisito da ID migrazione e assegnare ID univoci ai task.
- [ ] **XT.15 — Glossario canonico**: definire termini e unità (`tick`, giorno, anno, Athel, `level`, `strength`, `connection`, `desire`, `consent`) e indicare intervalli validi.
- [ ] **XT.16 — Politica di compatibilità**: versioni Python/dipendenze supportate, formato di configurazione, compatibilità DB e procedura di upgrade.
- [ ] **XT.17 — Recovery e backup**: test automatici di backup/restore del DB e dei `.sav`; documentare cosa è autorevole in caso di divergenza.

## 🚦 PROSSIMO BLOCCO CONSIGLIATO

Non partire direttamente da FASE 5 o FASE 6 solo perché la FASE 4 risulta “completata” nel riepilogo. Prima:

1. Eseguire **XT.01** e confrontare il TODO con il repository reale.
2. Chiudere **XT.02–XT.07** almeno per il percorso verticale principale.
3. Eseguire il test di bilanciamento di 1 anno e poi quello di 60 anni, salvando seed, configurazione, versione e report.
4. Correggere i difetti emersi e fissare una baseline/tag.
5. Solo allora scegliere il prossimo blocco: **Economy** se il ciclo lavoro–reddito–consumi è la priorità; **Politics** solo dopo aver stabilizzato economia, popolazione, città e regole di dominio.

La priorità non è completare il maggior numero di moduli: è ottenere un mondo piccolo che funzioni in modo coerente, autonomo e riproducibile, prima di renderlo enorme.

