```markdown
# 🚀 SimAI — Prompt di migrazione (stato: FASE 5 in corso, al 5.4c)

Stai assistendo lo sviluppo di **SimAI**: simulazione di vita ad agenti ambientata nel mondo di **Anthalys**. Python 3.13+, SQLAlchemy 2.0, Pydantic v2, Alembic, Typer + Rich, Loguru, FastAPI + Jinja2 opzionale. DB SQLite (PostgreSQL opzionale). Nessun bundler, nessun npm/node, nessuna CDN. UI offline-first (bootstrap, htmx, alpine, d3, chart.js in `simai/ui/static/`).

---

## 🏛️ REGOLE ARCHITETTURALI (TASSATIVE)

1. **Python 3.13+** — `match/case`, PEP 604 (`X | None`), `Self`, `StrEnum`, `Final`, generics PEP 695.
2. **Modularità rigorosa**: ogni feature in un package dedicato (`core/`, `npc/`, `world/`, `sim/`, `db/`, `config/`, `cli/`, `ui/`, `utils/`, `economy/`, `city/`).
   - **Eccezioni `core/`**: `Character`, `Location`, `GameObject`, `TimeManager`, `SimulationLoop`, `EventBus`, `SaveManager`, `DecisionSystem`. `core/` **non si tocca** senza esplicito via libera.
3. **Migrazioni Alembic**: formato `NNNN_SS_slug.py`. Range assegnati:
   | Range | Modulo |
   |---|---|
   | 5000–5099 | Core Simulation |
   | 5100–5199 | Anthalys Time |
   | 5200–5299 | NPC |
   | 5300–5399 | World |
   | 5400–5499 | Economy (STORICO, occupato) |
   | 5500–5599 | Politics (pianificato) |
   | 5600–5699 | SoNet (pianificato) |
   | 5700–5799 | Networking (MP) |
   | **6000–6099** | **Economy esteso (DECISIONE PRESA: deviazione dal TODO, documentata)** |
   La catena `down_revision` segue l'ordine numerico. Sotto-range 6000:
   - `6000_01` — Ledger core
   - `6000_02` — drop `transaction` legacy
   - `6000_03` — Banking core
   - `6000_04` — Companies core
   - `6000_05` — AION core
   - `6000_06` — AION shipments
   - `6000_07` — AION multivendor
4. **Attori**: `current_actor()` citato nel TODO ma **non implementato**. Tutto il codice usa dependency injection esplicita (`session`, `character`, `current_dt`). Nessun contextvar.
5. **Asset locali**, mai CDN. `simai/ui/static/`.
6. **File integrali** quando mostri Python o Jinja2. Mai troncare. Se troppo lungo, spezza in più messaggi.
7. **Zero stub / placeholder**: mai `pass`, `...`, `NotImplementedError`, `# TODO`. Solo codice funzionante.
8. **uv** come dep manager (non Poetry). `pyproject.toml` + `uv.lock`.
9. **Timezone**: `datetime` naive UTC o `AnthalysDateTime` (432gg/anno, 18 mesi × 24gg, 28h/giorno, 60min/h). `SECONDS_PER_DAY = 100800`, `SECONDS_PER_YEAR = 43_545_600`. Costanti in `simai/config/anthalys.py`.
10. **Random**: mai `random` globale. `random.Random(seed)` iniettato.
11. **Conventional Commits** + SemVer 2.0.0.
12. **Niente Vite/npm/node, niente CDN**.

---

## 🧠 CONVENZIONI DI RISPOSTA (personalizzate, concordate)

1. **Non generare test.** No-test policy attiva.
2. **File integrali**, mai parziali. Se un file è >~400 righe, spezza in più messaggi ma **mai troncare**.
3. **Niente CDN.**
4. **API esplicita**, mai global mutabili.
5. **Type hints FQCN** e `Mapped[...]` SQLAlchemy ovunque. mypy strict + ruff strict.
6. **Usa `coerce_int/coerce_float/coerce_str`** (in `simai/utils/coerce.py`) invece di `# type: ignore`. Esiste anche `coerce_optional_int/str`.
7. **Non toccare `core/`** senza esplicito via libera.
8. **Niente stub/placeholder.**
9. **Nome file completo** quando mostri codice.
10. **Checklist finale** con tabella task + `▶️ Comandi` di verifica + `📌 Note operative`.
11. Rispondi in **italiano**, conciso ma completo.
12. Nel **checkup**: verdetto 🔴/🟠/🟡/🟢 + tabella + domande di conferma.
13. **Se manca contesto, chiedi prima** di scrivere codice.
14. **Niente documentazione** durante lo sviluppo: `docs/simai/README.md` e `CHANGELOG.md` **solo se richiesto esplicitamente** (regola appresa in questa sessione).
15. **`./scripts/check.sh`** è il gate di qualità: `ruff check --fix .`, `ruff format .`, `ruff check .`, `ruff format --check .`, `mypy simai/`. **Va sempre eseguito** prima di dichiarare un chunk completato.
16. **Ruff**: line-length 100, `select = E,W,F,I,N,UP,B,C4,SIM,TID,RUF`. Evita `int(round(x))` (RUF046), ternari invece di if/else corti (SIM108), no `if/else` identici (RUF034).
17. **Batch mode Alembic** (`with op.batch_alter_table(...)`) obbligatorio per aggiungere FK a tabelle SQLite esistenti.
18. **`drop_index` con `if_exists=True`** se il nome non è garantito (lezione da `6000_02`).
19. **No mutable default in dataclass** — usa `field(default_factory=list)`. Niente `frozen=True` se poi muti i campi.
20. **Ledger double-entry è la sorgente di verità**: ogni movimento Athel posta una `JournalEntry` con ≥2 `Posting` bilanciati. `signed_amount` è **flow-based** (DEBIT `+`, CREDIT `-`), non account-based. `natural_balance` è helper di lettura separato.
21. **`Character.athel_balance` / `Company.athel_balance` / `BankAccount.balance` / `Loan.remaining_principal`** sono **cache materializzate**, riconciliabili con `WealthService.reconcile`, `CompanyService.reconcile`, `BankService.reconcile_bank`.
22. **Niente più `Transaction` legacy** (droppata in `6000_02`). Solo `JournalEntry` + eventuali tabelle di audit specifiche (`CompanyTransaction`, `LoanPayment`, `InterestAccrual`, `TaxPayment`).

---

## 🧩 STATO ATTUALE DEL PROGETTO

**FASI COMPLETATE**: 0, 1, 2, 3, 4.
**FASE 5 (Economy) IN CORSO**, chunks completati:

| Chunk | Nome | Stato |
|---|---|---|
| **5.1a** | Ledger double-entry core (Account, JournalEntry, Posting, LedgerService) | ✅ mig `6000_01` |
| **5.1b** | `WealthService` su ledger | ✅ |
| **5.1c** | Aggiornamento call-sites (market, payday, property, city/tax, city/infra, city/transport, city/transit, lifecycl/manager, inheritance) + CLI `economy reconcile` | ✅ |
| **5.1d** | Rimozione `Transaction` legacy + migrazione `6000_02` | ✅ |
| **5.2a** | Banking core (`Bank`, `BankAccount`, `Loan`, `LoanPayment`, `InterestAccrual`, `BankService`) | ✅ mig `6000_03` |
| **5.2b** | Integrazione `LifecycleManager` (`monthly_tick` banking) + CLI `economy bank [list\|show\|open\|accounts\|deposit\|withdraw\|loans\|issue-loan\|pay-loan\|monthly-tick\|reconcile]` | ✅ |
| **5.2c** | UI banking (`/economy/banks`, `/economy/banks/{code}`) | ✅ |
| **5.3a** | Companies core (`Company`, `CompanyEmployee`, `CompanyTransaction`, `CompanyService`) | ✅ mig `6000_04` |
| **5.3b** | `BusinessAI` + tick `LifecycleManager` + CLI `economy company [list\|show\|create\|hire\|fire\|tick\|seed\|reconcile]` + `seed_demo_companies` | ✅ |
| **5.3c** | UI companies (`/economy/companies`, `/economy/companies/{id}`) | ✅ |
| **5.4a** | AION core (`AionPlatform`, `AionWarehouse`, `AionListing`, `AionOrder` + escrow + commissioni differenziate) | ✅ mig `6000_05` |
| **5.4b** | AION shipments (`AionShipment`, `AionInventoryItem`, `ship_order`, `tick_shipments`, 3 modalità: `SELLER_DIRECT`/`AION_WAREHOUSE`/`DROP_SHIP`) | ✅ mig `6000_06` |
| **5.4c** | AION multivendor (`Company` come seller/buyer, `seller_company_id`, `buyer_company_id`, helper polimorfici `_actor_athel_account`/`_classify_seller`/`_classify_buyer`/`_seller_origin_location`) | ✅ mig `6000_07` |

**PROSSIMI CHUNK FASE 5**:
| Chunk | Nome |
|---|---|
| **5.4d** | AION prodotti polimorfici (`SERVICE`, `LOT`, `VEHICLE`, `STOCK`) |
| **5.4e** | `AionAI` + tick `LifecycleManager` |
| **5.4f** | CLI + UI + seed AION |
| **5.5** | Mercato azionario (`Exchange`, `Ticker`, `Order`, `Trade`, `Portfolio`) — **NON aste, solo fixed price** (deciso in 5.4c) |
| **5.6** | Inflazione + prezzi dinamici |
| **5.7** | CLI + UI integration residuo |
| **5.8** | AI economica autonoma globale |

**FASI FUTURE**: 6 Politics, 7 SoNet, 8 Multiplayer, 9 Hardening.

---

## 📂 STRUTTURA PACKAGE ECONOMY (aggiornata)

```
simai/economy/
├── __init__.py, enums.py, models.py, jobs.py, market.py, payday.py,
│   property.py, seed.py
├── ledger/           # 5.1 — Account, JournalEntry, Posting, LedgerService
│   ├── __init__.py, enums.py, models.py, service.py
├── banking/          # 5.2 — Bank, BankAccount, Loan, LoanPayment, InterestAccrual
│   ├── __init__.py, enums.py, models.py, service.py
├── companies/        # 5.3 — Company, CompanyEmployee, CompanyTransaction
│   ├── __init__.py, enums.py, models.py, service.py, ai.py, seed.py
└── aion/             # 5.4 — AionPlatform, AionWarehouse, AionListing,
    ├── __init__.py   #        AionOrder, AionShipment, AionInventoryItem
    ├── enums.py
    ├── models.py
    └── service.py
```

Altri package rilevanti (invariati): `city/` (con `infrastructure/` e `transport/`), `npc/` (con tutti i sotto-package), `world/` (con `build/`, `buy/`, `style/`, `terrain/`), `ui/` (con `routes/` e `templates/`).

---

## 🔑 DECISIONI CHIAVE PRESE (da rispettare)

### Ledger
- **`signed_amount(kind, direction, amount)`** è **flow-based**: `DEBIT → +amount`, `CREDIT → -amount`. Serve per l'invariante `Σ signed_amount == 0`.
- **`natural_balance(kind, direction, amount)`** è l'helper **account-based** per display contabile. Vive in `ledger/enums.py`.
- Conti di sistema: `system:mint` (EQUITY), `system:consumption` (EXPENSE). Creati on-demand.
- Conti per character: `char:<id>:athel` (ASSET).
- Conti per bank: `bank:<code>:reserve` (ASSET), `bank:<code>:deposits` (LIABILITY), `bank:<code>:loans` (ASSET), `bank:<code>:interest_revenue` (REVENUE).
- Conti per char-bank: `char:<id>:bank:<bank_code>` (ASSET).
- Conti per char-loan: `char:<id>:loan:<bank_code>` (LIABILITY).
- Conti per company: `company:<id>:athel` (ASSET), `company:<id>:equity` (EQUITY, non usato in 5.3).
- Conti per AION: `aion:revenue` (REVENUE), `aion:escrow` (LIABILITY).

### Banking
- **Banca primaria** `anthal_primary` / "Banca di Anthal" creata idempotente da `BankService.ensure_primary_bank`.
- **Capitalizzazione iniziale**: 100_000 Athel via MINT (`PRIMARY_BANK_INITIAL_CAPITAL`), solo se `reserve == 0` (idempotente).
- **Mutui immobiliari** (`MortgageService` in `property.py`) sono **separati** dal banking. Passano per `WealthService.add`, non per `BankService`. Debito tecnico: unificarli in FASE 9.
- **Prestiti bancari** (`Loan`) sono separati dai mutui: no collateral obbligatorio, possono averlo opzionale.
- **Tick mensile**: interessi sui SAVINGS (creating money — modello banca che emette liquidità) + pagamento rate + write-off dopo `MAX_LOAN_MISSED_PAYMENTS * 2`.

### Companies
- **Owner è anche dipendente** con `role=OWNER`, `daily_wage=0`.
- **Tick giornaliero** in ordine: revenue → operating cost → salaries → dividend (se `balance > DIVIDEND_THRESHOLD`).
- **BusinessAI**: hire se `balance > MIN_RESERVE_FOR_HIRING` e sotto `TARGET_HEADCOUNT[kind]`; fire se `balance < FIRE_THRESHOLD`; scioglimento dopo `DAYS_TO_DISSOLVE=5` giorni a saldo ≤ 0.
- **Pool candidati**: exclude character con `Job` attivo **e** già dipendenti.
- **Bancarotta** quando `balance ≤ 0` **e** almeno uno stipendio è fallito.
- **Seed tollerante**: bastano 1+ adulti (prefer senza Job, fallback con Job).

### AION
- **`AION` = Artificial Intelligence Online Network**. Marketplace multivendor stile Amazon+AliExpress+eBay+Vinted.
- **Owner**: Governo di Anthalys (FASE 6). Gestita da AI.
- **Magazzino globale sotterraneo** a −200 m (`GLOBAL_WAREHOUSE_DEPTH_METERS`), `code = "aion:warehouse:global"`, cap 100_000.
- **Niente aste** (differenza da eBay). Solo fixed price.
- **Escrow** per gli ordini: `aion:escrow` (LIABILITY), rilascio a consegna.
- **Commissioni differenziate**: `commission_rate[seller_type][product_type]` in `AionPlatform.metadata_json`, fallback a `default_commission_rate`. Default: Character 7% GOODS, Company 5%, Government 2%, System 0%.
- **3 modalità fulfillment**: `SELLER_DIRECT`, `AION_WAREHOUSE`, `DROP_SHIP`. **3 modalità spedizione** (fisica/astratta/immediata) scelte automaticamente in base a distanza.
- **Consegna immediata** se `distance <= SHIPPING_DELIVERY_RADIUS_CELLS` (3 celle) o stessa location.
- **`ProductType`** già dichiarato: `GOODS`, `SERVICE`, `LOT`, `VEHICLE`, `STOCK`. Solo `GOODS` supportato in 5.4a–5.4c.
- **Seller/Buyer** possono essere `Character` **o** `Company` (5.4c). `Government` arriverà in FASE 6.

### UI
- **Read-only**: nessuna azione di scrittura dalla UI. Le mutazioni via CLI.
- Dashboard economia: `/economy` con pulsanti "Mercato immobiliare", "Banche", "Aziende".
- `/economy/lots`, `/economy/banks`, `/economy/banks/{code}`, `/economy/companies`, `/economy/companies/{id}`.

### Convenzioni cross-package
- **Import lazy** in `LifecycleManager.tick()` per tutti i blocco `2e-*` (evita cicli).
- **Try/except attorno ai tick secondari** (banking, companies, AION) per non far crashare il loop principale.
- **`LifecycleReport`** esteso con campi banking e companies (`bank_interest_paid`, `loan_payments_succeeded`, `loan_payments_missed`, `loans_defaulted`, `loans_written_off`, `companies_evaluated`, `company_hires`, `company_fires`, `company_dissolutions`, `company_tick_reports`).

---

## ⚙️ STACK TECNICO

| Componente | Versione / Tool |
|---|---|
| Runtime | CPython 3.13+ |
| ORM | SQLAlchemy 2.0 (no async) |
| Migrations | Alembic 1.13+ |
| Validation | Pydantic v2 |
| Settings | pydantic-settings |
| CLI | Typer 0.12+ |
| Output | Rich 13+ |
| Logging | Loguru |
| Web UI | FastAPI + Jinja2 + Uvicorn (opzionale) |
| Type check | mypy --strict, pyright strict |
| Lint/format | Ruff (line-length 100, py313) |
| Dep manager | **uv** (non Poetry) |
| DB dev | SQLite (WAL, foreign_keys=ON) |
| DB prod (opz.) | PostgreSQL |
| UI assets | bootstrap, htmx, alpine, d3, chart.js (locali, no CDN) |

---

## 📅 PROSSIMO STEP

Il **Chunk 5.4c è appena stato completato** (migrazione `6000_07`). Il gate `./scripts/check.sh` deve passare pulito.

I prossimi passi possibili sono:

- **A)** Chunk **5.4d** — AION prodotti polimorfici (`SERVICE`, `LOT`, `VEHICLE`, `STOCK`)
- **B)** Chunk **5.4e** — `AionAI` + tick `LifecycleManager` (creazione automatica listing dagli NPC)
- **C)** Chunk **5.4f** — CLI `economy aion ...` + UI `/economy/aion` + seed demo
- **D)** Saltare a **5.5** — Mercato azionario (fixed price, no aste)
- **E)** Saltare a **5.6** — Inflazione + prezzi dinamici
- **F)** Altro

**Chiedi all'utente da dove vuole partire prima di scrivere codice.**

---

## ✅ CHECKLIST GENERALE

Quando completi un chunk:
1. Includi sempre **migrazione Alembic** con sotto-range corretto.
2. Aggiorna **`simai/db/registry.py`** se hai aggiunto nuovi models.
3. Aggiorna **`simai/economy/__init__.py`** con export pubblici.
4. Includi `▶️ Comandi` di verifica (test manuale via `uv run python -c "..."`).
5. Includi `📌 Note operative` con decisioni prese e debito tecnico.
6. Verifica `./scripts/check.sh` prima di dichiarare completato.
7. **Zero documentazione, zero test**, come da istruzioni.
8. **Se manca contesto, chiedi prima di scrivere.**

---

## 🎯 ISTRUZIONI IMMEDIATE

1. **Conferma ricezione** del contesto in una riga.
2. **Chiedi all'utente da dove partire** (A/B/C/D/E/F).
3. **Aspetta la scelta** prima di scrivere codice.

---

## ❓ NOTA FINALE

Se in questa conversazione l'utente ha allegato il **TODO.md** completo e l'**ultimo scambio della chat precedente**, usali come riferimento primario: il TODO contiene le specifiche ufficiali (regole architetturali, naming migrazioni, fasi, convenzioni) e lo scambio precedente contiene l'esito del chunk appena completato (5.4c) — utile per sapere esattamente dove eravamo rimasti.

L'utente ha confermato in precedenza: **"procedi con 5.4c"** come ultima richiesta soddisfatta. Ora attende indicazioni su cosa fare dopo (5.4d / 5.4e / 5.4f / 5.5 / 5.6 / altro).
```

---

## 📌 Come usarlo

1. Apri una **nuova conversazione**.
2. Incolla il blocco `markdown` sopra come **primo messaggio**.
3. Allega il **TODO.md** completo e l'**ultimo scambio della vecchia chat** (chunk 5.4c).
4. L'assistente confermerà la ricezione e chiederà da dove partire (A–F).

---

## ✅ Cosa è preservato

- Tutte le **regole architetturali** del TODO originale (adattate a Python/uv/Alembic).
- Le **convenzioni di risposta personalizzate** (incluso `coerce_*`, no-docs-fino-alla-fine, SIM108/RUF046/RUF034).
- Lo **stato completo** FASE 0–4 + FASE 5 fino a 5.4c.
- La **mappa migrazioni** con il range `6000–6099` e i sotto-range assegnati.
- Le **decisioni chiave** per ledger, banking, companies, AION, UI.
- Lo **stack tecnico** completo.
- Il **prossimo step** (A–F) con richiesta esplicita di attendere la scelta.
- Le **lezioni apprese** in questa sessione: ledger flow-based, drop_index con if_exists, batch_alter_table, no mutable default in dataclass, import lazy in LifecycleManager, ecc.