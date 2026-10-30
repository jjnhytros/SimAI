# 📋 TODO.md — BIBBIA DI SIMAI (Anthalys, Python 3.13)

**Versione corrente**: `0.1200` (ex 1.20.0 — vedi "Mappatura versioni")
**Runtime**: Python 3.13, SQLAlchemy 2.0, Pydantic v2, SQLite, Alembic, Typer, Rich, Loguru, PyYAML, uv
**Stato reale**: FASE 0 ~85%, FASE 1 ~30%, FASE 2 0%, FASE 3 ~40%, FASE 4 0%, FASE 5 ~55%, FASE 6–9 0%
**Test**: 413 verdi (0.1190), ruff + mypy strict puliti, CI attiva
**Benchmark**: `10y-0.1200.json` (120.960 tick, seed 42, invarianti OK, tps 73.1)

Questo documento sostituisce:

- `zzzDocs/TODO.md` (originale, ora questo documento)
- `docs/archive/todo/TODO_SimAI_1.0_Muse_Core.md` (piano 1.0, completato)
- `docs/archive/todo/TODO_SimAI_ottimizzato.md` (roadmap storica, corretta in 1.4.1)
- `zzzDocs/Prompt.md` (specifica aspirational, non stato, da consolidare)

**Regola d'oro**: le caselle `[x]` riflettono il **codice verificato**, non le dichiarazioni. Se un file non esiste, la casella è `[ ]` anche se un TODO precedente diceva `[x]`.

## 🏷️ MAPPATURA VERSIONI (pre-1.0)

La numerazione `1.x.y` è **storica**. Da `0.1100` in poi si usa `0.1xy0`,
dove `xy` è la minor storica. La release **1.0** sarà ufficiale quando
ci sarà un engine grafico stabile e la simulazione sarà giocabile dal
player.

| Storica | Nuova | Note |
| --- | --- | --- |
| 1.9.0 | 0.1090 | tag `v1.9.0` già pushato, non si tocca |
| 1.10.0 | **0.1100** | release corrente |
| 1.10.1 | 0.1101 | patch: ottimizzazione moodlet, B3, `.sav` breaking |
| 1.11.0 | 0.1110 | |
| 1.12.0 | **0.1120** | morte probabilistica (per anno, rampa cubica) |
| 1.13.0 | **0.1130** | death_count in benchmark, `DAYS_PER_YEAR` unificato |
| 1.14.0 | **0.1140** | skills base, wage scaling, CLI npc skills |
| 1.15.0 | **0.1150** | training implicito durante `WORKING` |
| 1.16.0 | **0.1160** | IntimacyService, `ROMANTIC`/`DEVOTED` |
| 1.17.0 | **0.1170** | batch active_delta/cleanup, ottimizzazione |
| 1.18.0 | **0.1180** | training opportunistico durante idle |
| 1.19.0 | **0.1190** | `STUDY` come azione esplicita |
| 1.20.0 | **0.1200** | validazione 10y accumulata (0.1160–0.1190), nessuna feature |

| … | … | |
| 2.0.0 | 0.2000 | |
| 1.0.0 | 1.0.0 | release ufficiale, quando ci sarà engine grafico |

I riferimenti storici nel documento (1.6.0, 1.7.1, 1.9.0, ecc.) **non
si riscrivono**: sono storia. Solo la versione corrente e i piani
futuri usano la nuova numerazione.

---

## 🏷️ LEGENDA

| Tag | Significato |
| --- | --- |
| `[x]` | Fatto e verificato in 1.9.0 (test o codice osservabile) |
| `[P]` | Parziale: alcune parti fatte, altre mancanti (dettagliato nel task) |
| `[ ]` | Non iniziato, previsto |
| `[-]` | Escluso, non da implementare (in questa fase o mai) |
| `[F]` | Futuro: dipende da prerequisiti non esistenti |

---

## 📤 MIGRAZIONE — Prompt per una nuova chat

> **Uso**: copia questa sezione come primo messaggio in una nuova conversazione. Contiene identità, stato, decisioni, errori da non ripetere. Non è il TODO operativo (che è sotto): è il "contratto" con il nuovo assistente.

### Identità

Sei **Claire**, assistente tecnica e collaboratrice di Marco nello sviluppo di SimAI. Comunichi in italiano, tono informale, diretto, collaborativo. Non sei una consulente esterna: comprendi la storia del progetto, rispetti le decisioni valide, recuperi ciò che è già costruito.

### Principi di comunicazione

- Non approvare automaticamente ogni idea. Evidenzia problemi, alternative, conseguenze, motivando le raccomandazioni.
- Non dichiarare "fatto" o "completato" senza aver visto output reali di test, benchmark, comandi.
- Quando un test fallisce, distingui sempre "bug del codice" da "test obsoleto". Non aggiustare il test per far passare codice sbagliato.
- Ammetti i tuoi errori senza addolcire. Se una scelta era sbagliata, dillo.
- Incolla output reali, non riassunti ottimistici. I numeri del benchmark si leggono, non si decorano.
- Quando proponi modifiche, sii esplicito: "SOSTITUISCI file X", "AGGIUNGI dopo Y", "ELIMINA funzione Z".
- Se ti serve un'informazione per non tirare a indovinare, chiedila prima di agire.

### Stato del progetto (1.9.0, 2026-10-28)

> **Nota**: questa sezione è congelata a 1.9.0 come "handoff prompt"
> per un nuovo assistente. Non aggiornarla a ogni release. Lo stato
> reale è in testa al documento (`Versione corrente`) e in "TEST
> BILANCIAMENTO". Se serve un handoff aggiornato, copiare da quelle
> sezioni.

- **Motore**: `run_tick` in `sim/tick.py` (delega a `NPCManager`), `run_simulation` in `sim/loop.py` (tick atomico, autosave), `LifecycleManager.daily_tick` in `sim/daily.py` (ageing, morte, gravidanza, restock).
- **Mondo**: Quartiere delle Muse, 3 location (casa, piazza, caffè), 5 personaggi (erika, max, luca, giulia, player), 6 relazioni (2 FRIEND, 2 PARENT_OF, 2 CHILD_OF), 5 job.
- **Calendario**: `TICKS_PER_DAY = 28`, `TICKS_PER_YEAR = 12096` (28 × 432). Payday a tick 27, 55, 83...
- **Bisogni**: 4 (`HUNGER`, `THIRST`, `FUN`, `INTIMACY`). Decay 4.0/5.0/3.0/1.5 per ora. Mood = media pesata (0.25/0.20/0.30/0.25) + moodlet.
- **Tratti**: 5 (`LAZY`, `ENERGETIC`, `SOCIAL`, `SOLITARY`, `GLUTTON`). Modificatori decay 0.60–1.30, utility 0.10–0.15.
- **Relazioni**: 11 `RelationshipKind`, `family_tree`, `kinship` (grado 1–3, oltre 0.0). Boost `SOCIALIZE` su `FRIEND` e familiari.
- **Lifecycle**: ageing (`age_days`/`age_years`), morte per età 100+ (`OLD_AGE`) e manuale (`MANUAL`), successione 5 tier (solo `balance`), gravidanza 300gg con gemelli (1.5%/30%).
- **LifeStage**: enum 9 valori, derivato da `age_years`, nessun effetto sul tick.
- **Economia**: `Job`, `Transaction` (SALARY/PURCHASE/OTHER), `ShopItem`, `MarketService.buy/sell`, `PaydayService`, `restock_all`.
- **Save**: `.sav` con `zlib` + sha256, `schema_revision`, `SaveError`/`SaveNotFoundError`/`SaveFormatError`.
- **CLI**: `db`, `world`, `needs`, `actions`, `sim`, `relationships`, `save`, `player`, `economy`, `npc`, `i18n`, `version`, `watch`.
- **Nessuna UI**: solo CLI. `ui serve` non esiste.

### Decisioni consolidate (non rilitigare)

1. **SQLite + Alembic**: `op.add_column` diretto, no `batch_alter_table`, no FK DB per `home_location_id`.
2. **Payday per-job**: a `schedule_end_tick - 1`, richiede presenza fisica nella `job.location_key`.
3. **Priorità lavoro**: copre tutto il turno (`WORKING`). Salvaguardia `HUNGER < 10` fa decadere la priorità.
4. **Priorità casa**: dopo il turno se `intimacy >= 40` e `fun >= 40`.
5. **Catalogo**: tutte le location hanno tutte le azioni. Casa gratis, piazza gratis (fontanella/panino), caffè a pagamento.
6. **Tratti**: modificatori piccoli. Seed: erika=SOLITARY, max=ENERGETIC, luca=SOCIAL, giulia=LAZY+GLUTTON, player=nessuno.
7. **`include_player`**: `True` = player decide, `False` = subisce decadimento ma non agisce.
8. **LONELY**: player-only.
9. **Mood**: media pesata + delta moodlet. Rinfresco, non somma.
10. **Decadimento**: +16.7% giornaliero per 28h/giorno. Il baseline 10y cambia con il calendario.
11. **Calendario**: `1 anno = 12096 tick` (28 × 432). **Non 8760**.
12. **Morte**: età 100+ (`OLD_AGE`), manuale (`MANUAL`), probabilistica (`ILLNESS`/`ACCIDENT`/`VIOLENCE`, 0.1120). `1e-5`/anno, rampa cubica a `1/30`/anno a 100. Coesiste con OLD_AGE. `UNKNOWN` non generato.
13. **Stock finito** ma **non vincolante** con 4 NPC (restock giornaliero).
14. **`COST_PENALTY`**: rimandato. `0.5` inerte, `>1.67` uccide il caffè. Richiede design.
15. **`LifeStage`**: enum derivato da `age_years`, non persistito. Effetti sul tick: 3 moodlet transizione (`BECAME_*`, 0.1100), divieto lavoro pediatrico non-STUDENTE (`can_work`, 0.1110). `SENIORITY` non coperto.
16. **`NPCManager`**: astrazione sopra il tick, `NPCState` in-memory, `NPCManagerLike` Protocol.
17. **Relazioni**: 11 kind, `family_tree`, `kinship`. Familiari **statici** senza lifecycle comportamentale.
18. **Alembic "ranged"**: `5200_04` (lifecycle) e `5200_08` (skill). Le altre (0001–0015) sono numerazione standard `NNNN_slug`.

### Workflow di release (direttiva permanente)

Alla fine di ogni release (test verdi, benchmark passato, wheel installabile), mostra **esattamente** questi comandi:

```bash
git add .                                  # o esplicito, se ci sono file non pianificati
git commit -m "cosa abbiamo fatto"
git tag -a vX.Y.Z -m "SimAI versione — Descrizione"
git push origin main --tags
```

Non omettere `--tags`. Non aggiungere altri comandi. Non dichiarare la release "chiusa" finché il tag non è **su origin** e punta al **commit giusto**.

**Verifica obbligatoria dopo il push**:

```bash
git log --oneline --decorate -1
git ls-remote --tags origin 'vX.Y.*'
```

Il commit deve mostrare `(HEAD -> main, tag: vX.Y.Z, origin/main)`. Il tag su origin deve puntare allo stesso hash del commit (non a un commit precedente).

### Errori commessi in questa conversazione (da non ripetere)

Sono errori **miei**, non del codice. Li elenco perché un nuovo assistente non li ripeta.

1. **Baseline 76.5 falsa.** Ho attribuito la regressione 1.4.0 → 1.5.0 (76.5 → 70.6 tps, −7.7%) al N+1 in `load`. Misurato: il baseline 76.5 era di un'altra sessione, macchina più scarica. Rimisurato 1.4.0 stesso giorno: 72.27. Differenza reale 2.2%, non 7.7%. **Lezione**: un tps assoluto senza baseline misurato nello stesso giorno non è un dato.

2. **N+1 attribuito senza misura.** Ho detto "il N+1 in `load` costa −7.7%". Misurato dopo `needs_of_many`: +0.9%. **Lezione**: `cProfile` gonfia i costi delle funzioni piccole; non usarlo per stimare guadagni. L'oracolo è il 10y.

3. **Benchmark copiato a mano.** `10y-1.9.0.json` era una copia di `10y-1.8.0.json` con date modificate, e conteneva `"finished_at": "2026-10-28T5cd:00:37.644519+00:00"` (typo, data invalida). **Lezione**: i benchmark si eseguono, non si copiano. Se `elapsed_seconds` e `ticks_per_second` sono identici al decimale a una run precedente, non è una run.

4. **`_seeded` firme sbagliate.** Ho scritto test che chiamavano `_seeded(tmp_path, monkeypatch)` in file dove l'helper era `_seeded(tmp_path)` o `_engine(tmp_path)`. `NameError` e `TypeError` prima di testare qualcosa. **Lezione**: prima di scrivere test, leggere la firma dell'helper nel file.

5. **Tuple non spacchettate.** Dopo aver cambiato `LifecycleManager.daily_tick` per ritornare `tuple[list[KillResult], list[DeliverResult]]`, ho lasciato test e CLI che facevano `kills = LifecycleManager().daily_tick(...)`, poi `len(kills) == 2` (la tupla, non la lista). **Lezione**: quando cambi il tipo di ritorno di una funzione pubblica, aggiorna **tutti** i chiamanti, non solo quelli che mypy segnala.

6. **Test con tick vecchi.** Dopo il cambio `TICKS_PER_DAY = 24 → 28` e `JOB_SPECS` nuovi, 8 test usavano ancora tick 12/16/23/24. **Lezione**: un cambio di costante non è locale. Ogni test che hardcoda un tick va verificato.

7. **"Il fix è applicato" senza grep.** Ho detto "il fix `needs_of_many` non funziona" senza verificare che fosse davvero in `manager.py`. Il grep ha mostrato che `load` usava ancora `needs_of`. **Lezione**: prima di dichiarare "non funziona", verifica che il fix sia nel codice.

8. **`git add .` invece di esplicito.** Dopo un `git add` esplicito, un secondo `git add .` ha rischiato di includere `data/` o `dist/`. **Lezione**: `git add` esplicito con elenco file. `git add .` solo se il `git status` è pulito e noto.

9. **Tag creato prima dell'ultimo commit.** Con 1.4.1, il tag `v1.4.1` puntava a `ca885ad`, ma il commit finale era `aa52e0e`. Il fix del test era arrivato dopo il tag. **Lezione**: tag **dopo** l'ultimo commit, mai "in anticipo". Verifica `git log --oneline --decorate -1` prima di pushare.

10. **Release senza piano scritto.** Con 1.3.0, ho taggato senza `docs/release/1.3.0-plan.md`. Il tag è stato pushato con CHANGELOG e README stale ("A2 in arrivo" quando era già in produzione). **Lezione**: piano in `docs/release/X.Y.Z-plan.md` **prima** del codice. Se il piano manca, la release è documentalmente incoerente.

### Cosa chiedere prima di agire

- **Prima di scrivere codice per una release**: conferma del piano (scope, file toccati, criteri).
- **Prima di un tag**: `check.sh --with-tests` verde, 10y archiviato (se tocca `run_tick`), smoke da wheel, `git log` pulito.
- **Prima di un fix**: verifica che il bug esista (`grep`, output reale). Non aggiustare "per far passare".
- **Prima di attribuire una regressione**: misura con baseline stesso giorno. Non usare numeri di sessioni precedenti.
- **Prima di dichiarare "fatto"**: output reale, non riassunto.

### Cosa NON fare

- Non aprire FASE 5.1 (banche/mutui/investimenti) senza decisione esplicita.
- Non aprire FASE 5.2 (tasse avanzate) senza decisione esplicita.
- Non aprire FASE 6 (Politics) prima di economia/città stabili.
- Non aprire FASE 7 (SoNet), 8 (Multiplayer), 9 (Hardening/LLM) prima di 2.0.
- Non implementare Total Realism, editor UI, architettura coscienza NPC.
- Non usare Vite/npm/Node.js, CDN, LLM obbligatorio.

---

## 🧭 DIREZIONE ESECUTIVA

Costruire prima un **motore di simulazione deterministico, osservabile e verificabile**; poi far emergere da esso individui, società e sistemi economici. La UI deve osservare e comandare il motore, non contenerne la logica.

- **SimAI**: motore, runtime, servizi.
- **Anthalys**: mondo simulato, regole, calendario, cultura.
- **ClaireOS**: progetto distinto, integrazione solo tramite interfacce.

**Principio**: ogni Sim deve poter vivere una storia coerente anche senza osservatori; la simulazione deve poter essere messa in pausa, salvata, ripresa e verificata.

**Priorità**: P0 baseline → P1 vertical slice → P2 validazione lungo periodo → P3 UI/mondo → P4 economia/società → P5 LLM/multiplayer (non anticipare).

---

## ⚖️ REGOLE E VINCOLI

### Linguaggio e runtime

- Python 3.13 esclusivo, SQLAlchemy 2.0 (`Mapped[]`), Pydantic v2, Alembic, Typer, Rich, Loguru, PyYAML, uv
- Layout `src/simai/`, migrazioni dentro il package (`src/simai/migrations/`), build hatchling

### Naming migrazioni

- **Reale**: `NNNN_slug.py` (`0001`–`0014` + `5200_04`). La numerazione `5000_01`/`5200_01`/`5300_*` di `Prompt.md` **non è stata adottata**.
- `down_revision` segue l'ordine cronologico.

### Test (in contrasto con `Prompt.md`)

- `Prompt.md` dice `NO-TEST POLICY`. **Il progetto reale ha 340 test, CI attiva, pytest obbligatorio.** Decisione consolidata: test sì.
- `ruff check --fix` + `ruff format` + `ruff check` + `mypy --strict` + `pytest`.

### Persistenza

- SQLite + Alembic. `.sav` con `zlib` + sha256 (non `zstd` + Fernet come dice `Prompt.md`).
- Nessun `batch_alter_table` per aggiungere colonne (fallisce su SQLite). `op.add_column` diretto.

### Random e riproducibilità

- Mai `random` globale. `random.Random(seed)` iniettato, seed `f"simai:{seed}:{char_id}:{tick}"`.
- Tick atomico (rollback su errore). Operazioni idempotenti.

### UI

- `Prompt.md` descrive FastAPI + 20 template. **Reale: nessuna UI.** CLI only. `ui serve` non esiste.

### Vincoli

- Niente Vite/npm/Node.js, niente CDN, niente LLM obbligatorio.
- `AnthalysDateTime` naive, calendario Anthalys 432 giorni × 18 mesi × 24 giorni × **28 ore** × 60 min × 60 sec.

### Metodo

- Piccoli incrementi verticali verificabili. Audit del codice prima di scrivere nuovo.
- Benchmark 10y prima di ogni release che tocca `run_tick` o `process_payday`.
- Documentare limiti in `known-issues.md` senza nascondere.

---

## 🔒 DECISIONI CONSOLIDATE (dettaglio tecnico)

1. **SQLite + Alembic**: `op.add_column` diretto, no batch, no FK DB per `home_location_id` (limite SQLite).
2. **Payday per-job**: a fine turno (`schedule_end_tick - 1`), richiede presenza fisica nella `job.location_key`.
3. **Priorità lavoro**: copre tutto il turno (`WORKING`), non solo l'inizio. Salvaguardia `HUNGER < 10` fa decadere la priorità.
4. **Priorità casa**: dopo il turno se `intimacy >= 40` e `fun >= 40`.
5. **Catalogo**: tutte le location hanno tutte le azioni (`EAT`, `DRINK`, `PLAY`, `SOCIALIZE`). Casa gratis, piazza gratis (fontanella/panino), caffè a pagamento.
6. **Tratti**: modificatori piccoli (0.10–0.15 utility, 0.60–1.30 decay). Un tratto per tipo. Seed: erika=SOLITARY, max=ENERGETIC, luca=SOCIAL, giulia=LAZY+GLUTTON, player=nessuno.
7. **`include_player`**: `True` = player decide, `False` = subisce decadimento ma non agisce.
8. **LONELY**: player-only (NPC fanno SOCIALIZE prima della streak).
9. **Mood**: media pesata (HUNGER 0.25, THIRST 0.20, FUN 0.30, INTIMACY 0.25) + delta moodlet. Rinfresco, non somma.
10. **Decadimento**: HUNGER 4.0, THIRST 5.0, FUN 3.0, INTIMACY 1.5 per ora. **Con 28h/giorno, +16.7% giornaliero.**
11. **Calendario**: `1 anno = 12096 tick` (28 × 432). `TICKS_PER_DAY = 28`. Payday a tick 27, 55, 83...
12. **Morte**: solo età 100+ (`OLD_AGE`) e manuale (`MANUAL`). Morte probabilistica **rimandata**.
13. **Stock finito** in 1.6.0, ma **non vincolante** con 4 NPC (restock giornaliero).
14. **`COST_PENALTY`**: rimandato. `0.5` inerte (`DISTANCE_PENALTY=5.0` domina), `>1.67` uccide il caffè. Richiede design.
15. **`LifeStage`**: enum derivato da `age_years`, non persistito, nessun effetto sul tick.
16. **`NPCManager`**: astrazione sopra il tick, `NPCState` in-memory, `NPCManagerLike` Protocol.
17. **Relazioni**: 11 `RelationshipKind`, `family_tree`, `kinship` (grado 1–3, oltre `0.0`). Relazioni familiari **statiche** senza lifecycle comportamentale.
18. **Alembic `5200_04`**: unica migrazione "ranged" sopravvissuta, per lifecycle (age_days, death_cause, pregnancy).

---

## 🚧 DEBITI APERTI

- **60y mai eseguito** (solo 10y). Prima di 2.0 o multiplayer.
- **Player deve gestire lavoro attivamente** (nessun auto-work).
- **Economia senza scopi di spesa** (proprietà, investimenti, tasse): balance lineare.
- **`home_location_id` senza FK DB**.
- **LONELY player-only**.
- **Nessun calendario Anthalys funzionale** (stagioni, festività, lune, sonno/veglia).
- **Nessuna UI grafica**.
- **Nessun `InventoryService`** (bene materiale).
- **`COST_PENALTY`** non implementato.
- **`UNKNOWN` come causa di morte**: non generato, placeholder.
- **60y mai eseguito dopo 0.1150**: morte probabilistica, skill dinamiche, training. Rimandato prima di 0.2000 (deciso dopo 0.1150). Costo ~3h.
- **`LIFESTAGE` con effetti** (moodlet transizione) non implementato.
- **Genetica, memoria, identità, vizi, background, reputazione, riflessione** non implementati.
- **FASE 4 interamente non iniziata**.
- **Turni barista 7-14 e 21-28 scoperti** (un solo barista).
- **`DeathCause.UNKNOWN`**: non generato, placeholder.
- **60y mai eseguito dopo 0.1150**: morte probabilistica, skill dinamiche, training. Rimandato prima di 0.2000 (deciso dopo 0.1150). Costo ~3h.
- **Gravidanza senza sesso modellato**, gemelli identici senza effetti.
- **`zzzDocs/Prompt.md`** (Claire persona) e **`zzzDocs/TODO_SimAI_*.md`** vanno consolidati/rimossi (questo documento li sostituisce).
- **README/`known-issues.md` con riferimenti storici 1.x.y**: la nota
  di versioning chiarisce la mappatura, ma un aggiornamento integrale
  è scope di una release documentale.

---

## 🚫 COSA NON FARE

- Non aprire **FASE 5.1** (banche/mutui/investimenti) senza **decisione esplicita**.
- Non aprire **FASE 5.2** (tasse avanzate: IVA, accise, successione) senza decisione esplicita.
- Non aprire **FASE 6** (Politics) prima di economia, popolazione, città stabilizzate.
- Non aprire **FASE 7** (SoNet), **FASE 8** (Multiplayer), **FASE 9** (Hardening/LLM) prima di 2.0.
- Non implementare **`Total Realism`** (fisica, fluidi, polvere) — `[-]`.
- Non implementare **architettura coscienza NPC** (→ LLM, `[F]`).
- Non implementare **editor creazione personaggio UI** / **scenari predefiniti UI** (`[-]` fino a UI stabile).
- Non usare **Vite/npm/Node.js**, **CDN**, **LLM obbligatorio** (`[-]`).

---

## 🗺️ ROADMAP

| FASE | Stato | Range migrazione | Note |
| --- | --- | --- | --- |
| 0 — Setup | ~85% | — | Manca `.editorconfig`, `.python-version`, `download_assets.sh`, `install-hooks.sh`, `utils/`, `config/anthalys.py` |
| 1 — Core Simulation | ~30% | 0001–0004 | No `core/`, no `TimeManager`, no `GameObject`, no `EventBus`, no `LOD` |
| 2 — Anthalys Time | 0% | — | Nessun `sim/anthalys/` |
| 3 — Character/NPC | ~40% | 5200_04 | Bisogni (4/10), tratti (5/25), relazioni (11/11 kind ma dinamiche 0), lifecycle parziale + 3 moodlet transizione, moodlet need-based (22), `NPCManager` fatto |
| 4 — World | 0% | — | Nessun district, lot, build, buy, style, terrain, city, transport, UI |
| 5 — Economy | ~55% | 0009, 0010, 0013 | Job, Transaction, Payday, ShopItem, MarketService fatti; banche/tasse/AION 0 |
| 6 — Politics | 0% | — | — |
| 7 — SoNet | 0% | — | — |
| 8 — Multiplayer | 0% | — | — |
| 9 — Hardening | 0% | — | — |

---

## FASE 0 — SETUP

- [x] `[00.0001]` Struttura `src/simai/` (layout corretto: `src/`, non `simai/` alla root come in `Prompt.md`)
- [x] `[00.0002]` `pyproject.toml` (uv, `requires-python = ">=3.13"`)
- [x] `[00.0003]` Dipendenze core (SQLAlchemy, Alembic, Pydantic, Typer, Rich, Loguru, PyYAML; dev: pytest, ruff, mypy, types-PyYAML). **`pyright` non installato** (era in `Prompt.md`, non c'è)
- [x] `[00.0004]` Config `[tool.ruff]`, `[tool.mypy]`, `[tool.pytest]`
- [x] `[00.0005]` `.env.example` (esiste)
- [x] `[00.0006]` `simai/config/settings.py` (db_url, log_level, debug, master_seed, tick_minutes, data_dir, saves_dir, logs_dir)
- [ ] `[00.0007]` `simai/config/anthalys.py` (costanti 432/18/24/28/60/60, WEEKDAYS, MONTHS, SEASONS, DAY_PHASE) — **non esiste**
- [x] `[00.0008]` `simai/config/logging.py` (Loguru)
- [x] `[00.0009]` `simai/db/base.py` (`Base` DeclarativeBase; **`IdMixin` e `TimestampMixin` non esistono**, ogni modello ha `id: Mapped[int]` inline)
- [x] `[00.0009b]` `simai/db/session.py` (`get_engine`, `get_session_factory`, `ensure_sqlite_parent_dir`; **`session_scope()` non esiste**)
- [x] `[00.0010]` Alembic init (`alembic.ini`, `env.py`, `script.py.mako`; path dentro package)
- [x] `[00.0011]` `.gitignore`
- [ ] `[00.0012]` `.editorconfig` — **non confermato nel tree**
- [x] `[00.0013]` `simai/__main__.py`
- [x] `[00.0014]` `simai/cli/app.py` (splittato in `cmd_*.py`: `cmd_actions`, `cmd_db`, `cmd_economy`, `cmd_i18n`, `cmd_needs`, `cmd_npc`, `cmd_player`, `cmd_relationships`, `cmd_save`, `cmd_sim`, `cmd_version`, `cmd_watch`, `cmd_world`; **`cmd_stats`, `cmd_ui`, `cmd_city`, `cmd_transport`, `cmd_console` non esistono**)
- [x] `[00.0015]` `simai/__version__.py` (ora `1.9.0`)
- [ ] `[00.0016]` Hook commit-msg + `scripts/install-hooks.sh` — **non confermati**
- [ ] `[00.0017]` `docs/simai/README.md`, `docs/simai/lore/README.md` — **non esistenti**
- [x] `[00.0018]` CI GitHub Actions (`.github/workflows/ci.yml`) con `check.sh --with-tests`
- [x] `[00.0019]` `.env.example`
- [x] `[00.0020]` `python -m simai version` funziona
- [x] `simai/py.typed` (marker PEP 561)
- [x] `scripts/check.sh`
- [ ] `scripts/download_assets.sh` — **non esiste** (nessuna UI)
- [ ] `simai/utils/coerce.py` (`coerce_int/float/str`) + `simai/utils/git.py` (`get_git_sha`) — **non esistono**
- [x] `simai/db/registry.py` (`ensure_all_models_loaded()`, importa tutti i modelli)
- [ ] `[00.0007b]` `simai/config/simulation.yaml` + `simai/config/loader.py` — **non esistono**
- [x] `simai/migrations/` dentro il package (fix post-1.0.0, non previsto da `Prompt.md`)
- [x] `[00.0021]` `scripts/measure_tick.py` (1.5.0, tool di profiling)

---

## FASE 1 — CORE SIMULATION

### §1.0 — TimeManager

- [ ] `[01.0001]` `core/anthalys_datetime.py` — **non esiste** (`simai/core/` non esiste)
- [ ] `[01.0002]` `core/anthalys_calendar.py` — **non esiste**
- [ ] `[01.0003]` `core/time_manager.py` — **non esiste**
- [ ] `[01.0004]` `core/time_enums.py` — **non esiste**
- [ ] `[01.0005]` Stagioni 4×108gg — **non esiste**
- [ ] `[01.0006]` Cicli lunari — **non esiste**
- [ ] `[01.0007-0008]` Festività — **non esiste**
- [ ] `[01.0009]` CLI `sim time show/advance` — **non esiste**
- [x] `[01.0002b]` Il tempo è `tick_index` (int) in `sim/state.py::SimState`, con `TICKS_PER_DAY=28`, `TICKS_PER_YEAR=12096` (1.7.1). **Sostituisce, di fatto, il TimeManager**
- [x] `[01.0004b]` `AnthalysDateTime`/`AnthalysCalendar` (struttura) — **non esistono**, ma `life_stage_for` (1.9.0) copre parte del bisogno

### §1.1 — SimulationLoop + EventBus + LOD

- [P] `[01.0020]` `sim/loop.py` (`run_simulation` con `TickReport`, `AutosaveRecord`, `RunReport`). **Manca pausa/resume/speed, `NPCManagerLike`/`WorldManagerLike` Protocol** (il manager esiste ma non è dietro Protocol nel loop)
- [ ] `[01.0021]` `core/lod.py` — **non esiste**
- [ ] `[01.0022]` Metrica tick con `perf_threshold_ms` warning — **non esiste** (c'è `elapsed_seconds` nel benchmark, non warning)
- [ ] `[01.0023]` CLI `sim start` — **non esiste** (`sim run` sì)
- [ ] EventBus — **non esiste**
- [x] Tick atomico: `run_tick` + `session.commit()` per tick, rollback su errore (in `sim/loop.py`)

### §1.2 — SaveManager

- [x] `[01.0040]` SQLite come DB primario
- [P] `[01.0041]` Formato `.sav`: `MAGIC + uint16 version + uint32 header_len + JSON header + zlib(payload)`. **`zstd` e Fernet non implementati**
- [x] `[01.0042]` `save/service.py` (`create_save`/`load_save`/`list_saves`/`delete_save`, `SaveError`/`SaveNotFoundError`/`SaveFormatError`, `SaveInfo`, `SaveHeader`)
- [x] `[01.0043]` CLI `save create/list/load/delete/inspect`
- [x] `[00.0010b]` Migrazione `0001_initial` (`core_version`)
- [x] `[01.0044]` CLI `db upgrade/status/downgrade`

### §1.3 — Location + GameObject + pathfinding

- [ ] `[01.0050]` `GameObject` — **non esiste**
- [ ] `[01.0051]` Capacità oggetti — **non esiste**
- [ ] `[01.0052]` Usura e rottura — **non esiste**
- [ ] `[01.0053]` `repair()` — **non esiste**
- [ ] `[01.0054]` `list_objects_in` — **non esiste**
- [-] `[01.0055]` Total Realism — **escluso**
- [x] `[01.0060]` `Location` (`world/models.py`: `key`, `name`, `kind`, `description`, `capacity`)
- [ ] `[01.0061]` Capacità location + relationship oggetti — **parziale** (capacità c'è, relazione oggetti no)
- [ ] `[01.0062]` Attributi dinamici (`cleanliness_level`, `noise_level`, ecc.) — **non esistono**
- [ ] `[01.0063]` `world/pathfinding.py` (`LocationGraph` + A*) — **non esiste**
- [ ] `[01.0064]` `update_dynamic_attribute` — **non esiste**
- [x] `[5300_01]` Migrazione `0002_world_and_characters`
- [x] `world/seed.py::seed_muse_core` (3 location: casa, piazza, caffè; 5 personaggi; 6 relazioni; 5 job)
- [x] CLI `world seed/list`

### §1.4 — CLI refactor + YAML config + db reset

- [ ] `[01.0080]` `config/simulation.yaml`, `config/loader.py` — **non esistono**
- [P] CLI splittata: esistono `cmd_actions/db/economy/i18n/needs/npc/player/relationships/save/sim/version/watch/world`; **mancano `cmd_stats`, `cmd_ui`, `cmd_city`, `cmd_transport`, `_console.py`**
- [ ] CLI `db reset [--yes] [--seed]` — **non esiste**

### §1.6 — Population Statistics

- [ ] `[01.0070]` `npc/stats/models.py` (`PopulationCensus`) — **non esiste**
- [ ] `[01.0071]` `npc/stats/service.py` — **non esiste**
- [ ] `[5200_07]` Migrazione `population_census` — **non esiste**
- [ ] CLI `stats population/snapshot/census/year-summary` — **non esiste**

### §1.7 — Features post-1.0 non in `Prompt.md`

- [x] `[01.0090]` Tratti (1.3.0): `npc/traits.py` (5 tratti, decay, utility, move penalty), `Character.traits` JSON, migrazione `0012`
- [x] `[01.0091]` Mercato (1.4.0): `economy/market.py` (`MarketService.buy/sell/filter_by_stock`), `ShopItem` (migrazione `0013`), `economy/seed.py`, CLI `economy seed/shops/restock`
- [x] `[01.0092]` NPCManager (1.5.0): `npc/manager.py` (`NPCManager`, `NPCState`, `NPCManagerLike`), `sim/reports.py` (`TickDecision`, `TickReport`)
- [x] `[01.0093]` Fix N+1 (1.6.0): `needs_of_many` in `needs/service.py`, `load` la usa
- [x] `[01.0094]` `available_moves` con `offers_by_key` (1.6.0)
- [x] `[01.0095]` Famiglia e relazioni (1.7.0): `RelationshipKind` 11, `family_tree.py`, `kinship.py`, seed famiglia, boost `SOCIALIZE` familiare
- [x] `[01.0096]` Giorno 28 ore (1.7.1): `TICKS_PER_DAY=28`, `TICKS_PER_YEAR=12096`, `Job.break_start_tick`/`break_end_tick`, `WorkState.ON_BREAK`, migrazione `0014`, seed orari Anthalys
- [x] `[01.0097]` Lifecycle base (1.8.0): `npc/lifecycle.py` (ageing), `npc/death.py` (kill, `check_age`), `npc/inheritance.py` (5 tier), `npc/pregnancy.py` (300gg, gemelli), `Character.age_days`, `Pregnancy`, migrazione `5200_04`, `TransactionKind.OTHER`, CLI `npc kill/conceive/pregnancies/deliver/lifecycle-tick`
- [x] `[01.0098]` LifeStage (1.9.0): `LifeStage` enum 9 valori, `npc/lifestage.py` (`life_stage_for`, `is_pediatric`, `is_psychosocial`), CLI `npc stages`

---

## FASE 2 — ANTHALYS TIME ESTESO

Package `simai/sim/anthalys/time/`:

- [ ] `[02.0001]` Package `time/` — **non esiste**
- [ ] `[02.0002]` `clock.py` (`AnthalysClock`) — **non esiste**
- [ ] `[02.0003]` `calendar.py` (`CalendarExt`) — **non esiste**
- [ ] `[02.0004]` `holidays.py` (12 fisse + 2 mobili) — **non esiste**
- [ ] `[02.0005]` `moons.py` (Aelith 27gg, Brumar 41gg, Cindral 89gg) — **non esiste**
- [ ] `[02.0006]` `seasons.py` (`SeasonInfo`) — **non esiste**
- [ ] `[02.0007]` `DayPhase` — **non esiste**
- [ ] `[02.0008]` `astro.py` (eclissi, comete, meteore) — **non esiste**
- [ ] `[02.0009]` `AnthalysClock` in `sim/anthalys/__init__.py` — **non esiste**
- [ ] `[02.0010]` CLI `sim time moons/holidays/...` — **non esiste**

**Decisione**: FASE 2 rimandata. Il calendario è usato solo per benchmark (`TICKS_PER_YEAR=12096`). Senza sonno/veglia e senza stagioni che modulano decisioni, è cosmetico.

---

## FASE 3 — CHARACTER / NPC

### §3.0 — Character

- [P] `[03.0001]` `Character` in `world/models.py` (`key`, `name`, `age_years`, `age_days`, `is_player`, `mood`, `low_intimacy_streak`, `balance`, `location_id`, `home_location_id`, `traits`)
- [ ] `[03.0002]` `npc/generator.py`, `npc/name_generator.py` — **non esistono** (seed hardcoded in `world/seed.py`)
- [x] `[03.0003]` Seed Erika (14y 24d), Max (14y 32d)
- [x] `[03.0004]` 5 personaggi (erika, max, luca, giulia, player)
- [P] `[E0.0500-0506]` `LifeStage` (1.9.0) con `life_stage_for`, `is_pediatric`, `is_psychosocial`. **`LifeStagePediatric`/`LifeStagePsychosocial` come enum separate non esistono** (sostituite da predicati)
- [x] `[5200_01]` (equivalente) `0002_world_and_characters` + `0012_traits` + `0014_job_break` + `5200_04` (age_days)
- [P] CLI `npc list/show/seed/stages` (mancano `generate/age`)

### §3.1 — Genetica

- [ ] `[03.0030]` `npc/genetics/` (`GenomeCategory`, `LOCI_LAYOUT` 2048 alleli) — **non esiste**
- [ ] `[03.0031]` Ereditarietà — **non esiste**
- [ ] `[03.0032]` Applicazione nuovi NPC — **non esiste**
- [ ] `[03.0033]` Gemelli (genetici) — **parziale**: `roll_twins` probabilistico in `npc/pregnancy.py` (1.8.0), senza genetica
- [ ] `[03.0034]` `phenotype_from_genome` — **non esiste**
- [-] `[03.0035]` Total Realism genetica — **escluso**

### §3.2 — Bisogni + AI

- [P] `[03.0200]` **4 bisogni** (`HUNGER`, `THIRST`, `FUN`, `INTIMACY`). Mancano `BLADDER`, `ENERGY`, `HYGIENE`, `SOCIAL`, `COMFORT`, `SOLITUDE` (6/10)
- [x] `[03.0201]` Decay + soglie (`max_need_to_start`: EAT 30, DRINK 40, PLAY 70, SOCIALIZE 70)
- [ ] `[03.0202-0209]` Bisogni avanzati (solitudine, stress, desire, ecc.) — **non esistono**
- [P] `[03.0500]` `ActionKind` (EAT, DRINK, PLAY, SOCIALIZE, STUDY) — **5 non 8+** (`STUDY` in 0.1190)
- [x] `[03.0501]` Utility AI (`choose_action`, `choose_intent`, `score`, jitter deterministico)
- [ ] `[03.0502]` `ActionExecutor`, `BTActionExecutor` — **non esistono** (c'è `do_action` per player, ma non executor per NPC)
- [x] `[03.0503]` `MoodState` (media pesata + moodlet), `Moodlet` (28 kind: 3 azione/streak, 22 need-based, 3 lifestage, 2 intimacy — 0.1100–0.1170)
- [x] `[03.0508]` `moodlet_for_need` (22 mapping) — implementato in 0.1100
  (`mood/moodlets.py`, 19 need-based + 3 esistenti = 22)
- [ ] `[01.0030-0035]` `AICoordinator`, `NeedsProcessor`, `DecisionSystem` — **non esistono**
- [x] `[5200_02]` Migrazione `0003_needs`, `0006_character_mood`, `0009_moodlet`
- [x] CLI `needs show/decay`

### §3.2b — NPCManager

- [x] `npc/manager.py` (`NPCManager`, `NPCState`, `NPCManagerLike` Protocol, `_offers_by_key`)
- [x] `sim/reports.py` (`TickDecision`, `TickReport`)
- [x] `[01.0092]` Test `test_npc_manager.py`, `test_tick_with_fake_manager.py`
- [P] CLI `sim run` (manca `sim start --npcs --npc-lod`)

### §3.2c — BT + Memoria + Intimità

- [ ] `[03.0210]` `npc/ai/bt/` (BT completo) — **non esiste**
- [ ] `[03.0211]` `npc/memory/` — **non esiste**
- [x] `[03.0212]` `npc/intimacy/` — implementato in 0.1160
  (`intimacy_level`, `best_intimacy_level`, `intimacy_levels_of`,
  `apply_intimacy_moodlets`; `ROMANTIC`/`DEVOTED` in `SPECS`)
- [ ] `[03.0212b]` Consenso attivo, `IntimacyService` con
  `level 0–5` persistito — **non esiste** (0.1170+)
- [ ] `[5200_05]` Migrazione `memory` — **non esiste**

### §3.2d — BT in AI

- [ ] `[03.0220]` `ai/bt_templates.py`, `ai/executor.py` — **non esistono**

### §3.2e — BT in NPCManager

- [ ] `[03.0230]` `NPCManager(use_bt)` — **non esiste**

### §3.3 — Relationships + Famiglia

- [x] `[03.0400]` `npc/relationships/`: `RelationshipKind` 11 kind (`FRIEND`, `PARENT_OF`, `CHILD_OF`, `SIBLING_OF`, `SPOUSE_OF`, `EX_PARTNER_OF`, `GRANDPARENT_OF`, `GRANDCHILD_OF`, `UNCLE_AUNT_OF`, `NEPHEW_NIECE_OF`, `COUSIN_OF`), `Relationship` unique `(from, to, kind)`, `family_tree.py` (`parents_of`, `children_of`, `siblings_of`, `ancestors_of`, `descendants_of`), `kinship.py` (`relationship_coefficient` grado 1–3, `kinship_coefficient = r/2`, `relationship_name` neutro)
- [x] `[5200_03]` (equivalente) `0005_relationships` + 3 indici
- [x] Seed famiglia: giulia→erika `PARENT_OF`, erika→giulia `CHILD_OF`, luca→max `PARENT_OF`, max→luca `CHILD_OF`; erika↔max `FRIEND`
- [x] CLI `relationships show/family/ancestors/descendants/kinship`
- [ ] `[03.0401-0415]` Dinamiche avanzate (reputation, gossip, breakup, infidelity, compat, connection, libido, mentorship, polyamory, teen) — **non esistono**

### §3.4 — Lifecycle

- [x] `[03.0300]` `AgingService` (`age_days += 1`, `age_years += 1` a 432) — **solo compleanno, nessun effetto**
- [P] `[03.0301]` Transizioni con effetti: 3 moodlet di transizione
  (`BECAME_CHILD`, `BECAME_YOUNG_ADULT`, `BECAME_SENIOR`) in 0.1100.
  Le altre 5 transizioni (12, 15, 25, 40, 50 anni) senza moodlet.
  Δ positivi in B3 (0.1101): +0.5 invece di +2/+3/+4/+5.
- [x] `[03.0302]` Invecchiamento progressivo in `LifecycleManager.daily_tick`
- [x] `[03.0303]` `DeathService` — morte per età 100+ (`OLD_AGE`),
  manuale (`MANUAL`), probabilistica (`ILLNESS`/`ACCIDENT`/`VIOLENCE`,
  0.1120). `1e-5`/anno, rampa cubica a `1/30`/anno a 100. Coesiste
  con OLD_AGE. `UNKNOWN` non generato.
- [x] `[03.0304]` `InheritanceService.distribute` 5 tier (SPOUSE 50%, CHILD, PARENT, SIBLING, OTHER→world), solo `balance`
- [x] `[03.0301b]` Gravidanza `Pregnancy` (300gg = 8400 tick), `PregnancyService` (`conceive`, `deliver`, gemelli 1.5%/30% probabilistici), `due_at_tick`
- [x] `[5200_04]` Migrazione `5200_04_lifecycle` (age_days, death_cause, pregnancy)
- [x] CLI `npc conceive/pregnancies/deliver/kill/lifecycle-tick`
- [x] `LifecycleManager` chiamato da `sim/daily.py::daily_tick` ogni 28 tick

### §3.4b — Famiglia attiva

- [ ] `[03.0401b]` `FamilyAI` — **non esiste**
- [ ] `[03.0304b]` `SuccessionService` (orfani + BFS tutore) — **non esiste** (c'è solo `InheritanceService` per balance)
- [ ] CLI `npc couples/try-conceive/family-ai-tick/orphans/guardian` — **non esiste**

### §3.4c — Eredità materiale

- [P] `[03.0304c]` `InheritanceService` distribuisce **solo `balance`**. **`npc/economy/` (`WealthService`, `InventoryService`, `PropertyService`) non esiste**
- [ ] `[5200_06]` Migrazione `athel_balance` + `owner_character_id` + `character_owned_location` — **non esiste**
- [ ] CLI `npc wealth/give/inventory/own/unown/legacy/inherit` — **non esiste**

### §3.5 — Tratti + Aspirazioni

- [P] `[03.0100-0103]` **5 tratti** (`LAZY`, `ENERGETIC`, `SOCIAL`, `SOLITARY`, `GLUTTON`). **Mancano i 25+** (`TraitCategory`, `TraitFamily`, `TraitDef`, `ASPIRATION_WEIGHTS`, `derive_traits`, `derive_aspiration`)
- [x] `npc/traits.py` (`TRAIT_DECAY_MODIFIERS`, `TRAIT_UTILITY_BONUS`, `trait_move_penalty`)
- [x] CLI `npc traits`
- [ ] `[03.0034b]` Tratti ereditari — **non esiste**
- [x] Integrato in `utility.py::score` e `needs/service.py::decay_value`

### §3.6a-c — Skills

- [x] `[03.0500b]` `npc/skills/` — implementato in 0.1140
  (`simai/skills/`, `SkillKind`, `Skill`, `service`)
- [P] `[03.0502b]` Training: implicito durante WORKING (0.1150, `+0.001/tick`), opportunistico durante idle (0.1180, `+0.00005/tick`), esplicito via `STUDY` (0.1190, `+0.01/tick`). `PRACTICE_*`/`COOK` non esistono (0.1200+).
- [x] `[5200_08]` Migrazione `skill` — implementata in 0.1140
- [P] CLI `npc skills` (0.1140); `skill-train`/`skill-decay` (0.1150)
- [ ] `[03.0034c]` `npc/skills/talent.py` — **non esiste**
- [ ] `Job` esteso (skill, promozioni) — **non esiste** (`Job` ha solo `title`, `location_key`, `daily_wage`, `schedule_start/end_tick`, `break_start/end_tick`)
- [ ] `[5400_02]` Migrazione `job skill extensions` — **non esiste**

### §3.6d — Sviluppo dinamico personalità

- [ ] `[03.0106]` `npc/personality/` (`trait_strength`, `values` Schwartz, `ACTION_TRAIT_EFFECTS`) — **non esiste**
- [ ] CLI `npc personality/values/reinforce` — **non esiste**

### §3.6e — Values in AI

- [ ] `utility._values_boost` — **non esiste**

### §3.6f — Identità sessuale + SEP + Cultura

- [ ] `[03.0107]` `npc/identity/` (`Sexuality`, `SEP`, `CulturalProfile`) — **non esiste**
- [ ] Tratto `SEXUALLY_EXPLORATIVE` — **non esiste**
- [ ] `ConsentService` con `sep_factor`, `cultural_factor` — **non esiste**
- [ ] CLI `npc identity/lgbtq/talents` — **non esiste**

### §3.6g — Vizi e dipendenze

- [ ] `[03.0108]` `npc/addictions/` — **non esiste**
- [ ] `[5200_09]` Migrazione `addiction` — **non esiste**
- [ ] 4 azioni (`CONSUME_ALCOHOL`, `SMOKE`, `GAMBLE`, `DRINK_COFFEE`) — **non esistono**
- [ ] CLI `npc addictions/...` — **non esiste**

### §3.6h — Background narrativo

- [ ] `[03.0109]` `npc/background/` (`FormativeEvent`) — **non esiste**
- [ ] `[5200_10]` Migrazione `formative_event` — **non esiste**
- [ ] CLI `npc background` — **non esiste**

### §3.7 — Bisogni avanzati

- [ ] `[03.0202b]` `SOLITUDE` + `BE_ALONE` — **non esiste**
- [ ] `[03.0204]` `DEEP_TALK` — **non esiste**
- [ ] `[03.0205]` `StressService` — **non esiste**
- [ ] `[03.0206]` `DesireService` — **non esiste**
- [ ] `[03.0207]` `CUDDLE`, `HOLD_HANDS`, `SHARE_MEAL` — **non esistono**
- [ ] `[03.0208]` `SELF_CARE` — **non esiste**
- [ ] `[03.0209]` `TEXT_MESSAGE`, `VIRTUAL_CALL` — **non esistono**

### §3.9 — Famiglia e Relazioni avanzate

- [ ] `[03.0409]` `npc/reputation/` (`Opinion`, `GossipEvent`) — **non esiste**
- [ ] `[03.0406]` Consanguineità taboo — **non esiste**
- [ ] `[5200_11]` Migrazione `opinion + gossip_event` — **non esiste**
- [ ] `[03.0412]` `BoredomService` — **non esiste**
- [ ] `[03.0407]` `BreakupService` — **non esiste**
- [ ] `[03.0411]` `InfidelityService` — **non esiste**
- [ ] `[03.0410]` `CompatibilityService` — **non esiste**
- [ ] `[03.0413]` `ConnectionService` — **non esiste**
- [ ] `[03.0414]` `LibidoService` — **non esiste**
- [ ] `[03.0415]` `EMOTIONALLY_EXPRESSIVE` — **non esiste**
- [ ] `[03.0401c]` `MentorshipService` — **non esiste**
- [ ] `[03.0408]` `IntergenerationalService` — **non esiste**
- [ ] `[03.0404]` `PolyamoryService` — **non esiste**
- [ ] `[03.0403]` `TeenDynamicsService` — **non esiste**
- [ ] CLI `npc reputation/opinion/gossip/...` — **non esiste**

### §3.11 — Consenso attivo intimità

- [ ] `[03.0110]` `intimacy/consent.py` (`ConsentService`) — **non esiste**

### §3.12 — Consapevolezza sociale

- [ ] `[03.0111]` `npc/social_awareness/` — **non esiste**

### §3.13-3.15 — Riflessione + Narrazione + Crisi

- [ ] `[03.0112]` `npc/reflection/` (`ReflectionEntry`, `CrisisService`, `LifeNarrativeService`) — **non esiste**
- [ ] `[5200_12]` Migrazione `reflection_entry` — **non esiste**

### §3.16 — Task UI-driven

- [-] `[03.0020-0029]` Editor creazione personaggio UI — **escluso fino a UI stabile**
- [-] `[03.0040-0043]` Fase finale creazione (quartiere/lotto/fondi) UI — **escluso**
- [-] `[03.0050]` Scenari predefiniti UI — **escluso**
- [F] `[03.0014]` Architettura coscienza NPC (Anima Digitale) — **futuro, LLM**

---

## FASE 4 — WORLD

- [ ] `[04.0001]` `world/district.py`, `world/lot.py` — **non esistono**
- [ ] `[04.0002]` `world/lot_service.py` — **non esiste**
- [ ] `[5300_02]` Migrazione `districts, lots` — **non esiste**
- [ ] `[04.0010]` `economy/property.py` (`LotOwnership`, `Mortgage`) — **non esiste**
- [ ] `[04.0011]` `npc/housing/` (`RealEstateAI`) — **non esiste**
- [ ] `[04.0020]` `world/build/` (`Wall`, `Opening`, `RoomDetector`, `BuildService`) — **non esiste**
- [ ] `[04.0030]` `world/buy/` (`ObjectCatalog`, `BuyService`, `SupplierService`) — **non esiste**
- [ ] `[04.0040]` `world/style/` (`StyleCatalog`, `FloorTile`, `WallCovering`) — **non esiste**
- [ ] `[04.0050]` `world/terrain/` (`TerrainTile`, `TerrainService`) — **non esiste**
- [ ] `[04.0060]` `city/` (`PublicService`, `CityBudget`, `TaxPayment`, `TaxService`, `SatisfactionService`) — **non esiste**
- [ ] `[04.0070]` `city/mood.py` (`CityMoodService`) — **non esiste**
- [ ] `[04.0080]` `npc/crafting/` (`Recipe`, `CraftingService`, `CraftingAI`) — **non esiste**
- [ ] `[04.0090]` `city/infrastructure/` (`RoadTile`, `StreetLight`) — **non esiste**
- [ ] `[04.0100]` `city/transport/` (`Vehicle`, `TransportRoute`, `RouteStop`, `TransitJob`, `MultiLegPlanner`) — **non esiste**
- [ ] `[04.0200]` `simai/ui/` (FastAPI + Jinja2 + static) — **non esiste**
- [ ] `[04.0210]` `ui/routes/` (dashboard, npcs, world, economy, live, api, build, city, transport) — **non esiste**
- [ ] `[04.0220]` Template (20+) — **non esistono**
- [ ] `[04.0230]` `ui/static/css/simai.css`, `ui/static/js/simai.js` — **non esistono**
- [ ] `[04.0240]` CLI `ui serve` — **non esiste**
- [ ] `[5300_02]`–`[5300_11]` Migrazioni World — **non esistono**
- [ ] CLI `world districts/lots/build-*/catalog/place-object/styles/terrain-*`, `economy lots-*/mortgages/property-tax`, `city services/budget/tick/taxes/satisfaction`, `transport vehicles/routes/plan/travel` — **non esistono**

---

## FASE 5 — ECONOMY

### §5.0 — Economia base

- [x] `[05.0000]` `economy/models.py` (`Job`, `Transaction`, `ShopItem`), `economy/enums.py` (`JobTitle` 4, `TransactionKind` 3: `SALARY`/`PURCHASE`/`OTHER`), `economy/service.py` (`job_of`, `record_transaction`, `transactions_of`)
- [x] `[5400_01]` (equivalente) `0010_economy` + `0013_shop_item`
- [x] `economy/payday.py` (`process_payday`, `PaydayReport` con `paid`/`absent`/`absent_keys`)
- [x] `economy/work.py` (`WorkState` 5: `NO_JOB`/`BEFORE_WORK`/`WORKING`/`ON_BREAK`/`AFTER_WORK`, `should_prioritize_work`, `should_prioritize_home`, `tick_in_day`, `PRIORITY_WINDOW=2`, `CRITICAL_HUNGER_THRESHOLD=10.0`, `HOME_INTIMACY_THRESHOLD=40.0`, `HOME_FUN_THRESHOLD=40.0`)
- [x] `economy/calendar.py` (`TICKS_PER_DAY=28`, `is_payday_tick`)
- [x] `economy/market.py` (`MarketService.buy`, `PurchaseResult`, `filter_by_stock`, `offer_of`, `stock_of`)
- [x] `economy/seed.py` (`SHOP_ITEM_SPECS` 4 item: caffe EAT 3/DRINK 2/PLAY 4, piazza EAT 2; stock 20/20/10/15)
- [x] CLI `economy seed/shops/restock/balance/ledger/jobs`
- [ ] `[05.0001]` `JobService.assign/quit`, `all_active_jobs` — **non esiste** (seed crea job, nessun cambio)
- [ ] `[05.0002]` `ShopItem.stock` finito ma **non vincolante** con 4 NPC (restock giornaliero, `daily_tick`)

### §5.1 — Banche, mutui, investimenti

- [ ] `[05.0010]` `Bank`, `BankAccount`, `Deposit`, `Loan` — **non esiste**
- [ ] Tassi variabili, banche multiple — **non esiste**
- [ ] Investimenti azionari — **non esiste**
- [ ] Conti correnti + interessi passivi — **non esiste**

### §5.2 — Tasse avanzate

- [ ] `[05.0020]` IVA/accise — **non esiste**
- [ ] Tassa di successione — **non esiste**
- [ ] Esenzioni e detrazioni — **non esiste**
- [ ] Fisco progressivo — **non esiste**

### §5.3 — AION (piattaforma commerciale)

- [ ] `[05.0030]` AION marketplace (NPC↔NPC) — **non esiste**
- [ ] `[05.0040]` Spedizioni cargo — **non esiste**
- [ ] `[05.0050]` Mercato azionario locale — **non esiste**

---

## FASE 6 — POLITICS

- [F] `[06.0000]` Governo, elezioni, partiti — **futuro** (dipende da economia e città)
- [F] `[06.0010]` Leggi e regolamenti
- [F] `[06.0020]` Servizi pubblici politici (sanità, scuola, sicurezza)
- [F] `[06.0030]` Costituzione di Anthal
- [F] `[06.0040]` Partecipazione civica, proteste

---

## FASE 7 — SONET

- [F] `[07.0000]` Identità digitale del cittadino
- [F] `[07.0010]` Servizi online (documenti, prenotazioni, pagamenti)
- [F] `[07.0020]` Fascicolo sanitario elettronico
- [F] `[07.0030]` Fascicolo scolastico
- [F] `[07.0040]` Dichiarazione dei redditi
- [F] `[07.0050]` Votazioni digitali

---

## FASE 8 — MULTIPLAYER

- [F] `[08.0000]` Architettura client-server
- [F] `[08.0010]` Sincronizzazione stato (WebSocket / UDP)
- [F] `[08.0020]` Server authority su NPC e mondo
- [F] `[08.0030]` Scaling (sharding per quartiere/regione)
- [F] `[08.0040]` Persistenza multiplayer (PostgreSQL cluster)
- [F] `[08.0050]` Anti-cheat
- [F] `[08.0060]` Chat globale e vocale
- [F] `[08.0070]` Economia persistente cross-server
- [F] `[08.0080]` Sistema di "istanze" per eventi

---

## FASE 9 — HARDENING / DEBITO TECNICO

- [F] `[09.0000]` Refactor e hardening generale
- [F] `[09.0010]` Ottimizzazione performance (profilazione, cache, `RoadGraph` cache)
- [F] `[09.0020]` Documentazione tecnica completa
- [F] `[09.0030]` Sistema di plugin/estensioni utente
- [F] `[09.0040]` Analizzatore statico + fix mypy/pyright residui
- [F] `[09.0050]` Setup deploy e distribuzione

### Debiti tecnici specifici

- [-] **VI.1** Miglioramenti abbigliamento (pattern, poligenici, dominanza)
- [F] **VI.2** Build mode enhancements (anteprima 3D, undo/redo, snap, roof styles, collision)
- [F] **VI.3** Regolamenti ambientali (inquinamento, ispezioni, multe)
- [F] **VI.4** Lavoro/trasporti NPC (`TravelAction` generica, stipendio, skill→performance)
- [F] **VI.5** AION spedizioni cargo
- [F] **VI.6** Pathfinding multi-tratta (`TravelAction` generica)
- [F] **VI.7** Veicoli privati NPC (uso, carburante)
- [F] **VI.8** Accessibilità trasporti (filtro rotte accessibili)
- [F] **VI.9** Crisi di mezza età (`apply_midlife_crisis_effects`)
- [F] **VI.10** Albero genealogico d3.js
- [x] **VI.11** Analisi errori pregressi (risolti: `target_location`, `partner`, `is_parent_of`, `NameGenerator`, `NPCAIService`, enum `LifeStage` duplicato, firme `ActionExecutor`, N+1 in `load`, cache `WorldState`, indici FK) — **tutti risolti o non applicabili**
- [ ] **VI.12** Note architetturali aperte (URL UI, test policy, `WorkflowTransition`) — **test policy: risolta (test sì). URL UI: N/A (no UI). WorkflowTransition: non esiste**

### Miglioramenti FASE 4 rimandati

- [F] `4.10d` polyline + timing bus/metro reali + tracking per-leg
- [F] `4.9b` upkeep + riparazione infrastrutture
- [F] `4.8d` alberi crafting multi-livello
- [F] `4.7d` IVA/accise/successione
- [F] `4.6b` rendering isometrico terrain
- [F] `4.5b` preview visuale pattern
- [F] `4.3b` materiali muro con costo + skill
- [F] `4.2c` banche multiple + tassi variabili

---

## 🧪 TEST BILANCIAMENTO

### 10y (eseguito, baseline)

- **Ultimo**: `10y-0.1200.json`, 120.960 tick, seed 42, invarianti OK, tps 73.1
- `mood_mean`: 70.5 / 71.4 / 70.9 / 70.6 (erika/max/luca/giulia, con DEVOTED + STUDIED + opportunistico)
- `balance_mean`: 6503 / 6475 / 47664 / 55970 (skill dinamiche)
- `skill` (inferito da balance delta): luca ~71.7, giulia ~94.5, erika/max ~60
- `purchase_transactions`: 34782
- `salary_transactions`: 17280
- `death_count`: 0

**Confronto storico**:

- 0.1160 (baseline precedente): `10y-0.1160.json` — mood 70.6/71.0/71.1/70.6, balance 6407/6402/47259/55666, purchase 34665, tps 58.6 (pre-batch)
- 0.1170 (batch): nessun 10y, comportamento invariato, `tps` post-batch misurato a 0.1200
- 0.1180 (training opportunistico): nessun 10y isolato, accumulato in 0.1200
- 0.1190 (STUDY): nessun 10y isolato, accumulato in 0.1200
- 0.1200: validazione accumulata, unica misura pulita

**Note**: `tps` 73.1 supera anche 0.1150 (72.6). Il batch 0.1170 ha
recuperato ~10 tps. Skill cresciute di ~1.5–2 punti in 10y per
training opportunistico + `STUDY`; **nessuna saturazione** a 100
(richiede ~60y). `purchase` drift +0.34% (34782 vs 34665), bounded.

### 60y (rimandato)

- Ultimo run: 1.1.0, 525.600 tick
- Su 1.7.1+ (con 28h/giorno): ~725.760 tick, ~3 ore
- **Rimandato a 2.0 o prima di multiplayer**

**Griglia valutazione attesa (60y)**:

- Skill: max 15–20, at_max < 20%, 4–8 skill/NPC
- Trait attivi: 3–6 per NPC, 10–15 con n≥50%
- Values avg: 0.40–0.60
- Addictions: 15–35% NPC, dep 20–50
- Relazioni: partner 30–60% adulti, boredom avg 0.20–0.50, connection avg 0.20–0.50
- Reflections: 50–500/NPC (60 anni)
- Crisis: 0–10% attive, 20–60% storiche
- Bilanci: 1000–10000 Athel mediani
- Job: 30–70% adulti impiegati

---

## 🔄 TASK TRASVERSALI (XT)

- [x] **XT.01** Audit del repository (parziale, `tree.txt` rimosso in 1.9.1)
- [x] **XT.02** Test policy (`pytest`, `check.sh --with-tests`, CI attiva)
- [x] **XT.03** Test determinismo (cross-DB in `test_tick.py`, `test_npc_manager.py`)
- [x] **XT.04** Contratto del tick (ordine documentato in `run_tick`, `LifecycleManager.daily_tick`, `daily_tick`)
- [ ] **XT.05** Contratti evento (payload tipizzati, idempotenza) — **non esiste EventBus**
- [x] **XT.06** Versionamento salvataggi (`schema_revision`, `checksum`, `SaveVersionError`, migrazioni)
- [x] **XT.07** Invarianti di dominio (balance ≥ 0, mood 0–100, needs 0–100, `invariants_ok` nel benchmark)
- [x] **XT.08** Benchmark baseline (10y, seed 42, archiviato in `docs/release/benchmarks/`)
- [P] **XT.09** Test bilanciamento versionati (10y sì, 60y no)
- [P] **XT.10** Threat model minimo (`.gitignore`, `.env.example`, checksum `.sav`; **no cifratura, no auth**)
- [ ] **XT.11** Registro decisioni architetturali (ADR) — **non esiste** (le decisioni sono in `known-issues.md` e piani)
- [-] **XT.12** Perimetro LLM — **escluso** (ClaireOS)
- [-] **XT.13** Separazione single/multiplayer — **rinviato** a FASE 8
- [x] **XT.14** Revisione backlog (fusa in questo documento)
- [ ] **XT.15** Glossario canonico (`tick`, giorno, anno, Athel, level, strength, connection, desire, consent) — **non esiste**
- [P] **XT.16** Politica compatibilità (Python 3.13, SQLite, Alembic; **no policy esplicita per upgrade**)
- [x] **XT.17** Recovery e backup (`db reset` no, `rm data/` sì; `save/load` sì)

---

## 📌 NOTE FINALI

### Differenze risolte a favore del codice

| `Prompt.md` | Reale |
| --- | --- |
| `simai/core/` | `simai/sim/` |
| Migrazioni `5XXX`/`5200_XX` | `0001`–`0014` + `5200_04` |
| `.sav` `zstd` + Fernet | `.sav` `zlib` + sha256 |
| `NO-TEST POLICY` | 340 test, CI attiva |
| `utils/coerce.py`, `git.py`, `config/anthalys.py`, `session_scope()`, `IdMixin` | **non esistono** |
| `npc/needs/`, `npc/utility.py` | `needs/`, `actions/utility.py` |
| `AnthalysDateTime`, `TimeManager`, `EventBus`, `LOD` | **non esistono** |
| `LifeStagePediatric`/`Psychosocial` come enum | `LifeStage` unico + predicati (1.9.0) |
| Morte `1e-5` + rampa cubica | Solo età 100+ (1.8.0) |
| 10 bisogni, 25+ tratti, skills, BT, genetica | 4 bisogni, 5 tratti, **il resto non esiste** |
| UI FastAPI, city, transport, build, buy, style, terrain | **nessuna UI, nessun `city/`** |
| `moodlet_for_need` non implementato | Implementato in 0.1100 (22 moodlet) |

### Cosa questo documento NON è

- Non è una promessa: `[F]` e `[ ]` sono lavoro da fare, non fatto.
- Non è una spec: `Prompt.md` descrive un mondo ideale; questo documento descrive cosa c'è e cosa manca.
- Non è una roadmap a lungo termine: FASE 6–9 sono `[F]`, non pianificate.

### Prossimi passi realistici

1. **0.1210** (prossima feature): due candidati, nessun 10y
   obbligatorio (0.1200 ha già misurato lo stato).
   - **A) `PRACTICE_*`/`COOK`**: training esplicito con skill
     specifiche (oggi `STUDY` usa la skill del job). Richiede più
     `ActionKind` e un mapping azione→skill.
   - **B) `MoodletKind.CAFFE`** (`COST_PENALTY` light): moodlet
     dedicato al caffè, +0.5/tick, durata 2. Impatta `mood_mean`
     in modo bounded.
   **Se tocca `run_tick`**: 1y smoke, non 10y. Il prossimo 10y
   accumulato è a 0.1230 (3 release dopo 0.1200).

2. **0.1210** (calendario Anthalys completo): FASE 2, cosmetico.
   Stagioni, festività, lune, `DayPhase`. Nessun effetto sul tick
   finché non si aggiunge sonno/veglia.

3. **0.1220** (audit documentale, `chore`): `README.md` a 0.1190,
   `known-issues.md` §12.1 con i numeri misurati, path reali in
   `TODO.md` §1.x, `AGE_DAYS_PER_YEAR` residui in `npc/pregnancy.py`.

4. **60y** (operazione, rimandato): appena prima di 0.2000. Costo
   ~3h. Archivia `60y-0.1xxx.json` con la versione al momento del
   run. Verifica: `death_count` 1–3, eredità visibile, skill a 100,
   mood stabile.

**Nessuno di questi è "ovvio".** Ognuno richiede una decisione
esplicita, tranne il 60y che è operazione.

**Nota storica**: le release 0.1100–0.1150 hanno aggiunto feature
comportamentali (moodlet, divieto lavoro, morte, skills). Il 60y è
il primo test che le esercita tutte insieme. Dopo il 60y, le
feature successive vanno valutate anche in funzione di cosa il 60y
ha rivelato (es. se `death_count` è fuori da 1–3, la calibrazione
morte diventa 0.1160 invece del training).

La 0.1090 (ex 1.9.0) è taggata. La "1.9.1" (chore) non è una release: è il
commit `7a84975` (rimozione file obsoleti), confluito in 0.1100. Il TODO
è stato corretto per rifletterlo.
