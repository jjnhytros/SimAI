# 📋 TODO SimAI — Simulazione di Anthalys (Python)

**Simulazione di vita ad agenti** — PHP sostituito da Python 3.12+.
Progetto autonomo ma integrato con ClaireCMS/ScienzaViva a livello di lore e (opzionalmente) di storage.

**Versione corrente**: `0.1.0-dev`
**Ultimo aggiornamento**: aggiorna manualmente ad ogni modifica sostanziale.

---

## PARTE I — RIFERIMENTI E CONVENZIONI

---

### 📄 Prompt di sistema per l'assistente — SimAI

Copia **integralmente** il blocco qui sotto in una nuova conversazione come **primo messaggio**.

---

## 🤝 SIMAI — PROMPT DI SISTEMA PER L'ASSISTENTE

Stai assistendo lo sviluppo di **SimAI**: una simulazione di vita ad agenti
ambientata nel mondo di **Anthalys**. La simulazione è scritta in **Python**
e gira su database **SQLite** (con predisposizione per PostgreSQL).

Il tuo ruolo è quello di implementare, verificare, correggere e documentare
seguendo rigorosamente le regole architetturali e le convenzioni stabilite.
Ogni violazione è già stata commessa in passato e **non va ripetuta**.

---

### 🏛️ REGOLE ARCHITETTURALI — TASSATIVE

#### 1. Linguaggio e runtime
- **Python 3.12+** — sfrutta `match/case`, type hints PEP 604, `Self`, ecc.
- **SQLAlchemy 2.0** (ORM dichiarativo con `Mapped[]` e `mapped_column`)
- **Pydantic v2** — validazione e serializzazione
- **Alembic** — migrazioni database
- **Typer** — comandi CLI
- **Rich** — output CLI
- **Loguru** o **structlog** — logging
- **Pytest** — test (dipende da regola 9, vedi sotto)

#### 2. Modularità rigorosa
Ogni feature significativa vive in un **package Python** dedicato:

```
simai/
├── core/             # Simulation engine (loop, tempo, eventi, save)
├── npc/              # NPC, genetica, bisogni, AI
├── world/            # Locazioni, economia, politica, meteo
├── sim/              # Lore-specific: Anthalys, calendario, festività
├── db/               # SQLAlchemy models + Alembic
├── config/           # Settings (pydantic-settings) + costanti Anthalys
├── cli/              # Comandi Typer
├── ui/               # Web UI (FastAPI + Jinja2) opzionale
└── utils/            # Helper generici
```

**Eccezioni legittime (Core)**: `Character`, `Location`, `GameObject`,
`TimeManager`, `SimulationLoop`, `EventBus`, `SaveManager`, `DecisionSystem`.

**TUTTO IL RESTO** deve essere package.

### 3. Naming migrazioni (Alembic, range-based)
Formato file: `NNNN_SS_descrizione.py` con `NNNN` = range modulo, `SS` = sequenza.

| Range     | Modulo SimAI                |
| --------- | --------------------------- |
| 5000–5099 | SimAI/Core Simulation       |
| 5100–5199 | SimAI/Anthalys Time         |
| 5200–5299 | SimAI/NPC                   |
| 5300–5399 | SimAI/World                 |
| 5400–5499 | SimAI/Economy               |
| 5500–5599 | SimAI/Politics              |
| 5600–5699 | SimAI/SoNet                 |
| 5700–5799 | SimAI/Networking (MP)       |
| 5800+     | (libero)                    |

**Convenzione Alembic**: `<revision_id>_<slug>.py` dove `revision_id` segue
`NNNN_SS`. La catena `down_revision` deve rispettare l'ordine numerico.

#### 4. Accesso all'attore corrente (analogo di `Auth::`)
La simulazione non ha "utenti" come un CMS. Ha **attori**:
- `Player` — se simulazione con input umano
- `NPC` — agenti autonomi
- `System` — eventi interni (tick, meteo, ecc.)

Usa **sempre** l'API esplicita:
```python
from simai.core.context import current_actor

actor = current_actor()  # Player | NPC | None
```
**Mai** variabili globali mutabili, mai importare istanze a livello di modulo.

#### 5. Asset locali — MAI CDN
Tutto in `simai/ui/static/`:
- `bootstrap.min.css`, `bootstrap.bundle.min.js`
- `bootstrap-icons.css`, `fonts/bootstrap-icons.woff2`
- `chart.umd.min.js`
- `Sortable.min.js`
- `d3.min.js` (alberi genealogici)
- `simai.css`, `simai.js` (custom)

Eccezione ammessa: nessuna. SimAI è **completamente offline-first**.

#### 6. View integrali
Quando mostri un template Jinja2 o un file Python "di vista",
**mostralo integralmente**. Se troppo lungo, spezza in più messaggi
ma **non troncare mai**.

#### 7. Zero stub / placeholder
**Mai** codice di esempio. **Mai** `pass  # TODO`, `...`, `NotImplementedError`.
Solo codice reale, completo, funzionante.

#### 8. Dipendenze
- **Poetry** o **uv** per la gestione dipendenze
- File `pyproject.toml` con `[project.dependencies]`
- **Vietato pip install manuale** a runtime
- Lock file `poetry.lock` o `uv.lock` sempre versionato

#### 9. Test
⚠️ **POLITICA ATTUALE: NON generare test.**
Rispecchia la no-test policy di ClaireCMS. La cartella `tests/` è
**eliminata** o vuota. Non creare file di test, non suggerire `pytest`,
non menzionare coverage.

#### 10. Warning mypy / pyright
- Tipo non inferibile → annotazione esplicita o `cast(T, x)` da `typing`
- Metodi su SQLAlchemy model → `Mapped[T]` e `mapped_column(...)`
- Warning fantasma → `# type: ignore[specific-code]` con codice specifico
- **Non indebolire i type hints** per fixare warning: preferisci cast mirati

#### 11. Pattern di integrazione difensiva
Per integrazioni opzionali con altri package:
```python
try:
    from simai.pkg.optional import Service

    svc = Service()
    svc.run()
except (ImportError, RuntimeError):
    pass
```
Config boot-safe: controlla l'esistenza del file/DB prima di aprirlo.
Preferire hook applicativi (`EventBus.emit("domain.entity.event", ...)`)
per disaccoppiare i package.

#### 12. Timezone e calendario
- **Internamente** usa sempre `datetime` **naive in UTC** o un custom
  `AnthalysDateTime`. **Mai** `datetime.now()` senza timezone.
- **Anthalys** ha il suo calendario: 432 giorni, 18 mesi × 24 giorni,
  28 ore/giorno. Vedi `config/anthalys.py`.
- Per conversioni, usa `simai.sim.AnthalysCalendar`.

#### 13. Random e riproducibilità
- **Mai** `random` globale. Usa `random.Random(seed)` iniettato.
- Il seed di simulazione è salvato e riproducibile.
- Per simulazioni parallele (multi-NPC), usa istanze separate con seed
  derivati: `master_seed + npc_id`.

#### 14. Git e commit (Conventional Commits)
```text
<type>(<scope>): <subject>

[body]

[footer]
```
**Type**: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`,
`build`, `ci`, `chore`, `revert`
**Scope**: nome package (`core`, `npc`, `world`, `economy`, `sim`, ...)

#### 15. Versioning (SemVer 2.0.0)
- **MAJOR** — breaking changes
- **MINOR** — feature retrocompatibili
- **PATCH** — bug fix
Ogni versione → tag git annotato + entry in `CHANGELOG.md`.

#### 16. Changelog
Formato **Keep a Changelog**.
Sezioni: `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`.

#### 17. Niente Vite, niente npm/node
La UI è **Jinja2 + CSS/JS nativi**. Nessun bundler, nessun transpiler,
nessun `package.json`, nessun `node_modules/`.

---

### 🧠 CONVENZIONI PERSONALI DI RISPOSTA

1. **Non generare test.**
2. **File integrali**, mai parziali.
3. **Niente CDN**.
4. **API esplicita** (`current_actor()`), mai global mutabili.
5. **Type hints FQCN** e `Mapped[...]` SQLAlchemy ovunque.
6. **Annotazioni di tipo esplicite** dove mypy non arriva.
7. **Non toccare `core/`** senza esplicito via libera.
8. **Niente stub o placeholder**: solo codice funzionante.
9. **Nome file completo** quando mostri codice.
10. **Checklist finale** con tabella task + `▶️ Comandi` + `Note operative`.
11. Se manca contesto, **chiedi** prima di scrivere codice.
12. Rispondi in **italiano**, conciso ma completo.
13. Risposte lunghe accettabili.
14. Nel **checkup**: verdetto 🔴/🟠/🟡/🟢 + tabella + domande di conferma.
15. **Ad ogni fix/fine sezione aggiorna `docs/simai/README.md`**.
16. **Niente Vite, niente npm/node.**

---

### 🧩 STATO DEL PROGETTO

#### Fasi
Vedi PARTE III.

#### Cicli di vita Anthalys
Vedi PARTE II.

---

### 📌 STATO AMBIENTE

- **Python** 3.12+
- **SQLAlchemy** 2.0.x, **Pydantic** 2.x, **Alembic** 1.13+
- **Typer** ≥ 0.12, **Rich** ≥ 13
- **SQLite** come default; PostgreSQL opzionale via `SIMAI_DB_URL`
- **UI**: FastAPI + Jinja2 (opzionale, non in FASE 0)
- **Lore**: `docs/simai/lore/` (Costituzione di Anthal, festività, ecc.)
- **Nessuna CDN, nessun npm**

---

### 🎯 COSA FARE ORA

1. **Conferma ricezione** del contesto in una riga.
2. **Chiedi all'utente** da dove partire:
   - **A)** FASE 0 — Setup progetto Python
   - **B)** FASE 1 — Core Simulation
   - **C)** FASE 2 — Anthalys Time
   - **D)** FASE 3 — Character / NPC
   - **E)** FASE 4 — World
   - **F)** Altra fase / debito tecnico
3. **Aspetta la scelta** prima di scrivere codice.

Struttura verdetto: 🔴 critici / 🟠 alti / 🟡 medi / 🟢 bassi + tabella + conferme.

---

### 📖 Legenda

| Simbolo | Stato                                    |
| ------- | ---------------------------------------- |
| `[ ]`   | Da implementare                          |
| `[x]`   | Implementato                             |
| `[P]`   | Parzialmente implementato                |
| `[?]`   | Indecisione sull'implementazione         |
| `[@]`   | Implementato, ma necessita revisione     |
| `[#]`   | Implementato, ma da rifare completamente |
| `[!]`   | Principio Guida prioritario              |
| `[F]`   | Implementazione futura                   |
| `[-]`   | Implementazione non applicabile          |

**Priorità**: `[0.001 – 9.999]` (valore basso = maggiore priorità).

**Convenzione priorità**:

| Range               | Ambito                            |
| ------------------- | --------------------------------- |
| `E0.xxxx`–`E9.xxxx` | SimAI — core simulation           |
| `F0.xxxx`–`F9.xxxx` | SimAI — NPC & AI                  |
| `G0.xxxx`–`G9.xxxx` | SimAI — world & infrastructure    |
| `H0.xxxx`–`H9.xxxx` | SimAI — economy & politics        |
| `I0.xxxx`–`I9.xxxx` | SimAI — SoNet & networking        |

---

### 🧱 Stack Python — riepilogo

| Componente     | Libreria / Tool                              |
| -------------- | -------------------------------------------- |
| Runtime        | CPython 3.12+                                |
| CLI            | Typer 0.12+                                  |
| Output CLI     | Rich 13+                                     |
| ORM            | SQLAlchemy 2.0 (async opzionale)             |
| Migrations     | Alembic 1.13+                                |
| Validation     | Pydantic v2                                  |
| Settings       | pydantic-settings                            |
| Logging        | Loguru                                       |
| Web UI (opz.)  | FastAPI + Jinja2 + Uvicorn                   |
| Test (opz.)    | Pytest (no-test policy attuale)              |
| Type check     | mypy --strict, pyright                       |
| Lint / format  | Ruff (lint + format), Black compat           |
| Dep manager    | Poetry (o uv)                                |
| DB dev         | SQLite                                       |
| DB prod (opz.) | PostgreSQL                                   |

---

### 📚 Sistema di versioning e changelog

#### Versioni attese

| Versione | Stato | Contenuto                                  |
| -------- | ----- | ------------------------------------------ |
| `0.1.0`  | `[ ]` | FASE 0–1 (Setup + Core Simulation)         |
| `0.2.0`  | `[ ]` | FASE 2 (Anthalys Time)                     |
| `0.3.0`  | `[ ]` | FASE 3 (Character/NPC, genetica)           |
| `0.4.0`  | `[ ]` | FASE 4 (World, locazioni, trasporti)       |
| `0.5.0`  | `[ ]` | FASE 5 (Economia, AION)                    |
| `0.6.0`  | `[ ]` | FASE 6 (Politica, governance)              |
| `0.7.0`  | `[ ]` | FASE 7 (SoNet — portale servizi)           |
| `0.8.0`  | `[ ]` | FASE 8 (Multiplayer MMO)                   |
| `0.9.0`  | `[ ]` | Debito tecnico, hardening                  |
| `1.0.0`  | `[ ]` | Prima release stabile pubblica             |

#### File `CHANGELOG.md`

Formato **Keep a Changelog** (sezioni `Added`, `Changed`, `Deprecated`,
`Removed`, `Fixed`, `Security`).

#### Tracciamento versione runtime

1. `pyproject.toml` → `[project] version = "0.1.0.dev0"` (PEP 440)
2. `simai/__version__.py` → `__version__ = "0.1.0.dev0"`
3. Tabella `core_version` (SQLAlchemy model + migration range 5000)

#### Comandi CLI da implementare

- `python -m simai version` — versione corrente + moduli caricati
- `python -m simai db upgrade` — applica migrazioni Alembic
- `python -m simai db status` — stato migrazioni
- `python -m simai sim start` — avvia simulazione
- `python -m simai sim tick N` — avanza N tick
- `python -m simai save create/list/load` — gestione salvataggi
- `python -m simai changelog add <type> <message>` — entry automatica

---

## PARTE II — CICLI DI VITA DI ANTHALYS

**Riferimento**: `docs/simai/lore/cicli-vita.md`

Nel calendario di Anthalys, un anno è composto da **432 giorni**
(18 mesi da 24 giorni) e un giorno dura **28 ore**. Le fasce d'età
tradizionalmente usate per gli umani vengono mantenute con gli stessi
valori numerici, ma interpretate secondo il nuovo calendario.

### 🍼 II.1 Prima scala (pediatrica e adolescenziale)

| Fascia                    | Età (anni/mesi/giorni Anthaliani) |
| ------------------------- | --------------------------------- |
| **Neonato**               | 0 – 28 giorni                     |
| **Lattante**              | 28 giorni – 1 anno                |
| **Prima infanzia**        | 1 – 2 anni (24 mesi)              |
| **Seconda infanzia**      | 2 – 6 anni                        |
| **Terza infanzia**        | 6 anni – inizio pubertà (10–13)   |
| **Pubertà e adolescenza** | pubertà – 18/20 anni              |

### 🌱 II.2 Seconda scala (psicosociale)

| Fascia               | Età (anni Anthaliani)      |
| -------------------- | -------------------------- |
| **Fase prenatale**   | dal concepimento ai 2 anni |
| **Infanzia (prima)** | 2 – 3 anni                 |
| **Infanzia**         | 3 – 5 anni                 |
| **Mezza infanzia**   | 6 – 12 anni                |
| **Adolescenza**      | 12 – 18 anni               |
| **Giovinezza**       | 18 – 25 anni               |
| **Età adulta**       | 25 – 60 anni               |
| · giovane adulto     | 25 – 40 anni               |
| · media adultità     | 40 – 50 anni               |
| · tarda adultità     | 50 – 60 anni               |
| **Vecchiaia**        | 60 anni fino alla morte    |

### ⏳ II.3 Nota sulla durata della vita

- **Maschi**: 144–156 anni Anthaliani
- **Femmine**: 156–168 anni Anthaliani

### 📋 II.4 TODO — Task di integrazione

- `[ E0.0500 ]` `[ ]` Costanti `LIFESTAGE_THRESHOLDS` in `config/anthalys.py`
- `[ E0.0501 ]` `[ ]` Costanti `PSYCHOSOCIAL_THRESHOLDS`
- `[ E0.0502 ]` `[ ]` Enum `LifeStagePediatric`
- `[ E0.0503 ]` `[ ]` Enum `LifeStagePsychosocial`
- `[ E0.0504 ]` `[ ]` `LifeStageService.get_pediatric_stage(character)`
- `[ E0.0505 ]` `[ ]` `LifeStageService.get_psychosocial_stage(character)`
- `[ E0.0506 ]` `[ ]` `LifeStageService.get_life_expectancy(character)` (144–156 M, 156–168 F)
- `[ E0.0507 ]` `[ ]` `AnthalysCalendar.to_gregorian(anth_date)` e inverso
- `[ E0.0508 ]` `[ ]` Integrazione con `TimeManager`
- `[ E0.0509 ]` `[ ]` Documentazione `docs/simai/cicli-vita.md`
- `[ E0.0510 ]` `[ ]` Riferimento incrociato con §4.2 Ciclo Vita NPC

---

## PARTE III — FASI DI SVILUPPO SimAI

### 🟢 FASE 0 — Setup iniziale progetto Python

- `[ 00.0001 ]` `[ ]` Creare struttura progetto Python:

  ```text
  simai/
  ├── pyproject.toml
  ├── README.md
  ├── .gitignore
  ├── .editorconfig
  ├── simai/
  │   ├── __init__.py
  │   ├── __main__.py
  │   ├── __version__.py
  │   ├── cli/                # Typer commands
  │   ├── config/             # pydantic-settings + anthalys constants
  │   ├── core/               # Simulation engine
  │   ├── db/                 # SQLAlchemy models + Alembic
  │   ├── npc/                # NPC, genetica, AI
  │   ├── world/              # Locazioni, economia, meteo
  │   ├── sim/                # Lore-specific (Anthalys)
  │   ├── ui/                 # FastAPI + Jinja2 (opzionale)
  │   └── utils/
  ├── alembic.ini
  ├── alembic/
  │   ├── env.py
  │   ├── script.py.mako
  │   └── versions/
  └── docs/
  ```

- `[ 00.0002 ]` `[ ]` Inizializzare progetto con `poetry init` (o `uv init`)
  - Python ≥ 3.12
  - Nome pacchetto: `simai`
  - Autori, licenza MIT
- `[ 00.0003 ]` `[ ]` Aggiungere dipendenze core in `pyproject.toml`:
  - `sqlalchemy >= 2.0`
  - `alembic >= 1.13`
  - `pydantic >= 2.7`
  - `pydantic-settings >= 2.3`
  - `typer >= 0.12`
  - `rich >= 13.7`
  - `loguru >= 0.7`
  - Dipendenze dev: `ruff`, `mypy`, `pyright`, `pytest` (opzionale)
- `[ 00.0004 ]` `[ ]` Configurare `pyproject.toml`:
  - `[tool.ruff]` line-length 100, target-version "py312"
  - `[tool.mypy]` strict mode, `disallow_untyped_defs = true`
  - `[tool.pytest.ini_options]` (se test abilitati) `testpaths = []`
- `[ 00.0005 ]` `[ ]` Configurare `.env.example` completo (vedi sotto)
- `[ 00.0006 ]` `[ ]` Configurare `simai/config/settings.py` con `pydantic_settings.BaseSettings`:
  - `db_url: str = "sqlite:///./simai.db"`
  - `log_level: str = "INFO"`
  - `debug: bool = False`
  - `master_seed: int = 0`
  - `tick_minutes: int = 5` (minuti Anthaliani per tick)
  - `data_dir: Path = Path("./data")`
  - Lettura da `.env` + variabili d'ambiente + defaults
- `[ 00.0007 ]` `[ ]` Configurare `simai/config/anthalys.py` con costanti del calendario:
  - `DAYS_PER_YEAR = 432`
  - `MONTHS_PER_YEAR = 18`
  - `DAYS_PER_MONTH = 24`
  - `HOURS_PER_DAY = 28`
  - `MINUTES_PER_HOUR = 60`
  - `SECONDS_PER_MINUTE = 60`
  - `WEEKDAYS = ["Nijahr", "Majahr", "Bejahr", "Ĉejahr", "Dyjahr", "Fejahr", "Ĝejahr"]`
  - `MONTHS = ["Arejal", "Brukom", "Ĉelal", "Kebor", "Duvol", "Elumag", "Fydrin", "Ĝinuril", "Itrekos", "Jebrax", "Letranat", "Mulfus", "Nylumer", "Otlevat", "Prax", "Retlixen", "Sajep", "Xetul"]`
  - `STARTING_YEAR = 5775`
  - `SEASONS` (6 stagioni × 3 mesi)
- `[ 00.0008 ]` `[ ]` Configurare `simai/config/logging.py` con Loguru
  - Sink su `data/logs/simai.log` (rotazione giornaliera, retention 30 gg)
  - Sink stderr in debug mode
- `[ 00.0009 ]` `[ ]` Configurare `simai/db/base.py`:
  - `DeclarativeBase` SQLAlchemy 2.0
  - Mixin comuni: `TimestampMixin`, `IdMixin` (bigint PK)
- `[ 00.0009b ]` `[ ]` Configurare `simai/db/session.py`:
  - Engine SQLite con `check_same_thread=False` e PRAGMA `foreign_keys=ON`
  - `SessionLocal` factory
  - Helper `with session_scope() as session:` context manager
- `[ 00.0010 ]` `[ ]` Inizializzare Alembic:
  - `alembic init alembic`
  - Modificare `alembic/env.py` per leggere `SIMAI_DB_URL` da settings
  - Importare `simai.db.base.Base.metadata` per autogenerate
  - Modificare `script.py.mako` per il formato `NNNN_SS_slug.py`
- `[ 00.0011 ]` `[ ]` Configurare `.gitignore`:
  - `__pycache__/`, `*.pyc`, `.venv/`, `venv/`
  - `*.db`, `*.sqlite`, `*.sqlite-journal`
  - `data/logs/`, `data/saves/`, `data/exports/`
  - `.env`, `.env.local`, `.env.*.local`
  - `.mypy_cache/`, `.ruff_cache/`, `.pytest_cache/`
  - `dist/`, `build/`, `*.egg-info/`
  - `.DS_Store`, `.idea/`, `.vscode/`
- `[ 00.0012 ]` `[ ]` Configurare `.editorconfig` (indent 4 spazi, LF, UTF-8)
- `[ 00.0013 ]` `[ ]` Creare entrypoint CLI `simai/__main__.py`:

  ```python
  from simai.cli.app import app

  if __name__ == "__main__":
      app()
  ```

- `[ 00.0014 ]` `[ ]` Creare `simai/cli/app.py` con Typer e comandi base:
  - `version` — mostra versione + python version + db status
  - `info` — info ambiente (path db, log dir, tick rate)
- `[ 00.0015 ]` `[ ]` Creare `simai/__version__.py` con `__version__ = "0.1.0.dev0"`
- `[ 00.0016 ]` `[ ]` Primo commit git con hook commit-msg (Conventional Commits)
- `[ 00.0017 ]` `[ ]` Creare `docs/simai/README.md` + `docs/simai/lore/README.md` (scheletri)
- `[ 00.0018 ]` `[ ]` Configurare CI GitHub Actions (`.github/workflows/ci.yml`):
  - Job lint: `ruff check .`, `ruff format --check .`
  - Job type: `mypy simai/`
  - Job test: **rimosso** (no-test policy)
- `[ 00.0019 ]` `[ ]` Popolare `.env.example` (vedi sotto)
- `[ 00.0020 ]` `[ ]` Verificare che `python -m simai version` funzioni

#### `.env.example` iniziale

```dotenv
# =============================================================================
# SimAI — .env.example
# =============================================================================
# --- Applicazione ---
SIMAI_ENV=development
SIMAI_DEBUG=true
SIMAI_LOG_LEVEL=INFO
SIMAI_MASTER_SEED=42

# --- Database ---
SIMAI_DB_URL=sqlite:///./simai.db
# SIMAI_DB_URL=postgresql+psycopg://user:pass@localhost:5432/simai

# --- Simulazione ---
SIMAI_TICK_MINUTES=5
SIMAI_STARTING_YEAR=5775
SIMAI_STARTING_DAY=1
SIMAI_STARTING_MONTH=1

# --- Data dir ---
SIMAI_DATA_DIR=./data
SIMAI_SAVES_DIR=./data/saves
SIMAI_LOGS_DIR=./data/logs
SIMAI_EXPORTS_DIR=./data/exports

# --- UI (opzionale, non in FASE 0) ---
SIMAI_UI_ENABLED=false
SIMAI_UI_HOST=127.0.0.1
SIMAI_UI_PORT=8000

# --- Save encryption (opzionale) ---
SIMAI_SAVE_ENCRYPTION_KEY=
```

---

### 🎯 FASE 1 — Core Simulation (range 5000–5099)

#### 1.0 — Time Manager e calendario Anthalys `[0.200]`

Vedi **§1.0 del TODO originale** per l'elenco completo dei task
(gestione calendario 432/18/24, festività, stagioni, fasi giorno/notte,
motore astronomico, API helper). Tutti riportati di seguito.

- `[ 01.0001 ]` `[ ]` Classe `AnthalysDateTime` (immutabile, naive)
  - Campi: `year`, `month`, `day`, `hour`, `minute`, `second`
  - Validazione range (0–431 giorni, 0–17 mesi, 0–23 giorni del mese,
    0–27 ore, 0–59 minuti, 0–59 secondi)
  - Metodi: `add_timedelta`, `compare`, `to_iso_string`, `from_iso_string`
- `[ 01.0002 ]` `[ ]` Classe `AnthalysCalendar`
  - Conversioni Anthalys ↔ giorni totali (analogo "epoch days")
  - Conversioni Anthalys ↔ Gregoriano (approssimazione documentata)
  - Costanti importate da `config/anthalys.py`
- `[ 01.0003 ]` `[ ]` Classe `TimeManager` (singleton per simulazione)
  - `current: AnthalysDateTime`
  - `tick_minutes: int` (default 5 min Anthaliani per tick)
  - `advance_tick()` — avanza di `tick_minutes`
  - `register_listener(event_type, callback, priority)` — pattern observer
  - `subscribe_to_hour_change`, `subscribe_to_day_change`, `subscribe_to_month_change`
- `[ 01.0004 ]` `[ ]` Fasi della giornata
  - Enum `DayPhase`: `DAWN`, `MORNING`, `NOON`, `AFTERNOON`, `EVENING`, `NIGHT`, `DEEP_NIGHT`
  - `TimeManager.current_phase` derivato dall'ora
- `[ 01.0005 ]` `[ ]` Gestione stagioni (6 stagioni × 3 mesi)
  - Enum `Season`: nomi da lore (es. `VERDANT`, `BRIGHT`, `HARVEST`, ...)
  - `TimeManager.current_season`
- `[ 01.0006 ]` `[ ]` Ciclo lunare
  - Classe `MoonPhase` (enum + nome)
  - Lista lune con periodo orbitale (in giorni Anthaliani)
  - `TimeManager.current_moon_phase(moon_id)`
- `[ 01.0007 ]` `[ ]` Festività fisse
  - Registry `HolidayRegistry` con decoratore `@fixed_holiday(month, day)`
  - Almeno 6 festività nel seeding iniziale
- `[ 01.0008 ]` `[ ]` Festività mobili
  - Regole basate su luna o su offset da festività fisse
  - Es. `Eclipse Festival = primo giorno della luna piena del mese X`
- `[ 01.0009 ]` `[ ]` Comandi CLI:
  - `python -m simai sim time` — mostra data/ora corrente
  - `python -m simai sim time advance N` — avanza N tick
- `[ 01.0010 ]` `[ ]` Test manuale documentato (no-test automatico):
  - Avanza di 100 tick, verifica cambio giorno
  - Avanza di 10_000 tick, verifica cambio mese
  - Avanza di 100_000 tick, verifica cambio anno

#### 1.1 — Loop di Simulazione Principale `[0.001]`

- `[ 01.0020 ]` `[ ]` Classe `SimulationLoop`
  - Attributi: `time_manager`, `npc_manager`, `world_manager`, `event_bus`
  - Metodo `tick()` che esegue la sequenza:
    1. `time_manager.advance_tick()`
    2. `world_manager.update_environment()`
    3. `npc_manager.update_all_npcs()`
    4. `event_bus.process_queue()`
    5. `world_manager.update_state()`
  - Metodo `run_for(num_ticks: int)` — esegue N tick in sequenza
  - Supporto pausa / ripresa / velocità di gioco
  - Reset simulazione (ricarica stato iniziale)
- `[ 01.0021 ]` `[ ]` Sistema di "LOD AI" per performance
  - Enum `LODLevel`: `FULL`, `REDUCED`, `BACKGROUND`
  - Ogni NPC ha un LOD, cambia dinamicamente in base a distanza
    dall'azione "calda" del giocatore / eventi rilevanti
  - `npc_manager.update_all_npcs()` salta NPC con LOD `BACKGROUND`
- `[ 01.0022 ]` `[ ]` Metrica tick
  - Misura durata di ogni fase in `data/logs/tick_perf.log`
  - Allarme se `tick > threshold_ms` (default 100)
- `[ 01.0023 ]` `[ ]` Comando CLI:
  - `python -m simai sim start [--headless] [--max-ticks=N]`

#### 1.2 — Architettura AI e Decisionale `[0.002]`

- `[ 01.0030 ]` `[ ]` Classe `AICoordinator` (per-NPC)
  - Orchestra i sotto-sistemi AI
  - Chiamato da `SimulationLoop` per ogni NPC FULL
- `[ 01.0031 ]` `[ ]` Classe `NeedsProcessor`
  - Decadimento dei bisogni per tick
  - Emette eventi quando un bisogno supera soglie critiche
- `[ 01.0032 ]` `[ ]` Classe `AIDecisionMaker`
  - Utility AI: ogni azione candidata ha `utility(npc, context) -> float`
  - Scegli l'azione con utility massima (con tie-break casuale seed)
  - Priorità modificabili da tratti, moodlets, obiettivi
- `[ 01.0033 ]` `[ ]` Classe `ActionExecutor`
  - Esegue l'azione scelta, gestisce stato "in corso"
  - Chiama `is_valid()` prima di iniziare
  - Emette eventi di inizio/fine azione
- `[ 01.0034 ]` `[ ]` Classe `DecisionSystem` (utility + behaviour tree)
  - Supporta due modalità: utility pura, behaviour tree
  - Modalità scelta per azione complessa (es. "cucinare cena")
- `[ 01.0035 ]` `[ ]` Sistema moodlets
  - Classe `Moodlet` (nome, durata, effetto su utility, effetto su umore)
  - Rimozione automatica alla scadenza
  - Effetti cumulativi su `mood_happiness`

#### 1.3 — Sistema di Salvataggio e Persistenza `[0.003]`

- `[ 01.0040 ]` `[ ]` Salvataggio SQLite come DB primario
- `[ 01.0041 ]` `[ ]` Formato `.sav` criptato + compresso
  - Serializzazione completa dello stato su SQLite
  - Compressione `zstandard`
  - Cifratura opzionale `cryptography.fernet` se `SIMAI_SAVE_ENCRYPTION_KEY` presente
- `[ 01.0042 ]` `[ ]` Classe `SaveManager`
  - `create_save(name: str) -> SaveInfo`
  - `load_save(save_id: int) -> SimulationState`
  - `list_saves() -> list[SaveInfo]`
  - `delete_save(save_id: int)`
  - Slot infiniti
- `[ 01.0043 ]` `[ ]` UI CLI per save/load
  - `python -m simai save list`
  - `python -m simai save create <name>`
  - `python -m simai save load <id>`
  - `python -m simai save delete <id>`

#### 1.4 — Gestione Oggetti di Gioco (GameObject) `[0.004]`

- `[ 01.0050 ]` `[ ]` Classe `GameObject` (SQLAlchemy model)
  - Campi: `id`, `type`, `location_id`, `state`, `condition`, `metadata`
  - `state` enum: `CLEAN`, `DIRTY`, `BROKEN`, `IN_USE`, `NEW`, ...
- `[ 01.0051 ]` `[ ]` Capacità degli oggetti
  - `objects.interactions`: lista di `Interaction` (verbo + effetti)
  - `objects.containers`: capacità, contenuto attuale
- `[ 01.0052 ]` `[ ]` Usura e rottura
  - `condition` decresce con uso (rate dipende da oggetto)
  - A `condition == 0` → `state = BROKEN`
  - Manutenzione periodica (NPC autonomo)
- `[ 01.0053 ]` `[ ]` Azione `REPAIR_OBJECT`
  - Richiede skill, tool, tempo
  - Ripristina `condition` a soglia (90% se successo pieno)
- `[ 01.0054 ]` `[ ]` Percezione oggetti nei metodi `is_valid()`
  - NPC vede solo oggetti nella sua location o adiacenti
- `[ 01.0055 ]` `[ ]` Estensione "Total Realism" — Fisica semplificata
  - Possibilità di spostare arredi
  - Oggetti che cadono e si rompono dinamicamente
  - Accumulo di polvere/sporcizia
  - Simulazione semplificata di fluidi (es. acqua versata)

#### 1.5 — Sistema di Locazioni (Location) `[0.006]`

- `[ 01.0060 ]` `[ ]` Classe `Location` (SQLAlchemy model)
  - Campi: `id`, `name`, `type`, `lot_id`, `parent_id`, `bounds`, `attributes`
- `[ 01.0061 ]` `[ ]` Capacità di contenere oggetti e NPC
- `[ 01.0062 ]` `[ ]` Attributi dinamici:
  - `cleanliness_level` (0.0–1.0)
  - `noise_level` (0.0–1.0)
  - `crowd_level` (0–N persone)
  - `safety_rating` (0.0–1.0)
  - `aesthetic_score` (0.0–1.0)
  - Aggiornati ad ogni tick da eventi (rumore, sporco, accessi)
- `[ 01.0063 ]` `[ ]` Navigazione NPC (pathfinding A*)
  - Grafo `Location` ↔ `Location` via edges (porta, corridoio, esterno)
  - Costo movimento basato su distanza + ostacoli
- `[ 01.0064 ]` `[ ]` Stato ambientale (pulizia, disordine)
  - `accumulate_dirt()` chiamato ad ogni azione sporcante
  - Azione `CLEAN_LOCATION` (NPC con tratto `Neat`)
  - Impatto su mood del NPC dentro

#### 1.6 — Statistiche e Tracking `[0.004]`

- `[ 01.0070 ]` `[ ]` Statistiche di popolazione
  - Contatori: vivi, morti, nati, emigrati, immigrati
  - Tracciati per anno/sesso/razza
- `[ 01.0071 ]` `[ ]` Tracking demografico
  - Storico censimenti mensili (tabella `population_census`)
  - Query CLI: `python -m simai stats population --year=5775`

#### 1.7 — Configurazione Globale `[0.010]`

- `[ 01.0080 ]` `[?]` Sistema configurazione globale via YAML
  - `config/simulation.yaml` (parametri economici, demografici, AI)
  - Override via `.env` per variabili sensibili
  - Hot-reload in development

---

### 🌍 FASE 2 — Anthalys Time (range 5100–5199)

Espande §1.0 della FASE 1 in un package dedicato.

- `[ 02.0001 ]` `[ ]` Package `simai/sim/anthalys/time/`
- `[ 02.0002 ]` `[ ]` `AnthalysClock` (wrapper di `AnthalysDateTime` + tick)
- `[ 02.0003 ]` `[ ]` `Calendar` (conversioni e lookup)
- `[ 02.0004 ]` `[ ]` `Holidays` (registry + 12 festività fisse iniziali)
- `[ 02.0005 ]` `[ ]` `MoonCycles` (3 lune con periodi orbitali)
- `[ 02.0006 ]` `[ ]` `Seasons` (6 stagioni, transizioni graduali)
- `[ 02.0007 ]` `[ ]` `DayPhase` (fasi giorno/notte)
- `[ 02.0008 ]` `[ ]` `AstroEvents` (eclissi, comete, eventi cosmici rari)
- `[ 02.0009 ]` `[ ]` `TimeManager` integration test
- `[ 02.0010 ]` `[ ]` Comandi CLI completi (status, jump, set-speed, dump)

---

### 👤 FASE 3 — Character / NPC (range 5200–5299)

#### 3.0 — Generazione NPC `[0.100]`

- `[ 03.0001 ]` `[ ]` Classe `Character` (SQLAlchemy model)
- `[ 03.0002 ]` `[ ]` Generatore procedurale `CharacterGenerator`
  - Nome + cognome (da `NameGenerator` con dizionari lore)
  - Sesso biologico, genere, orientamento
  - Età, data di nascita, luogo
  - Aspetto fisico (colori, altezze, forme)
  - Tratti e aspirazioni
  - Voce (tono, timbro)
  - Background narrativo breve
- `[ 03.0003 ]` `[ ]` Seed di default: Erika Lamborghetti (F, 14.24),
  Max Volpi (M, 14.32)
- `[ 03.0004 ]` `[ ]` Generazione batch 4–6 NPC random

#### 3.1 — Filosofia creazione iniziale `[!]`

- `[ 03.0010 ]` `[!]` Il giocatore definisce il punto di partenza
- `[ 03.0011 ]` `[!]` Processo intuitivo ma profondo
- `[ 03.0012 ]` `[!]` Personaggi giocatore = NPC `LOD1` (dettagliati)
- `[ 03.0013 ]` `[!]` Esperienza emotivamente coinvolgente
- `[ 03.0014 ]` `[ ]` Architettura Coscienza NPC: distinzione
  "Anima Digitale" ↔ "Personalità Agente" `[2.000]`

#### 3.2 — Interfaccia di Creazione `[1.500]`

- `[ 03.0020 ]` `[ ]` Editor personaggio (UI web o CLI interattiva)
- `[ 03.0021 ]` `[ ]` Personalizzazione aspetto fisico
- `[ 03.0022 ]` `[ ]` Identità di base
- `[ 03.0023 ]` `[ ]` Tratti di personalità
- `[ 03.0024 ]` `[ ]` Aspirazione di vita
- `[ 03.0025 ]` `[?]` Sistema punti creazione `[1.540]`
- `[ 03.0026 ]` `[?]` Salvataggio template personalità `[1.560]`
- `[ 03.0027 ]` `[ ]` Definizione abbigliamento iniziale
- `[ 03.0028 ]` `[P]` Definizione relazioni iniziali
- `[ 03.0029 ]` `[ ]` Background narrativo ed eventi formativi

#### 3.3 — Sistema Genetico `[0.101]`

- `[ 03.0030 ]` `[ ]` DNA simulato: 2048 alleli distribuiti in categorie
- `[ 03.0031 ]` `[ ]` Ereditarietà aspetto fisico dai genitori
- `[ 03.0032 ]` `[ ]` Applicazione a tutti i nuovi NPC nati in sim
- `[ 03.0033 ]` `[ ]` Gemelli identici / fraterni
- `[ 03.0034 ]` `[ ]` Tratti ereditari `[2.400]`
- `[ 03.0035 ]` `[ ]` Total Realism — genetica avanzata:
  - Predisposizioni a talenti/malattie
  - `[F]` Mutazioni genetiche casuali

#### 3.4 — Fase finale creazione

- `[ 03.0040 ]` `[ ]` Selezione quartiere di partenza
- `[ 03.0041 ]` `[ ]` Selezione lotto residenziale
- `[ 03.0042 ]` `[ ]` Fondi iniziali (Athel)
- `[ 03.0043 ]` `[ ]` Avvio sim dopo il trasferimento

#### 3.5 — Scenari di inizio partita

- `[ 03.0050 ]` `[ ]` Scenari predefiniti (es. "Giovane coppia in città",
  "Erede di famiglia nobile", "Emigrante")

#### 3.6 — Caratteristiche personaggio `[0.400]`

Vedi TODO originale §4.4 (invariato). Riepilogo:

- `[ 03.0100 ]` `[ ]` Sogni/aspirazioni `[0.600]`
- `[ 03.0101 ]` `[ ]` Tratti di personalità `[0.400]`
- `[ 03.0102 ]` `[ ]` Categorie tratti (Sociale, Personalità, Lifestyle,
  Mentale, Fisico, Economico, Lavoro)
- `[ 03.0103 ]` `[ ]` Tratto "Maschera" `[0.420]`
- `[ 03.0104 ]` `[ ]` Orientamento sessuale dinamico e fluidità temporanea `[1.820]`
- `[ 03.0105 ]` `[ ]` Vizi e dipendenze `[0.420]`
- `[ 03.0106 ]` `[ ]` Sviluppo dinamico personalità/valori
- `[ 03.0107 ]` `[ ]` Background e storia pregressa `[0.440]`
- `[ 03.0108 ]` `[ ]` Tratto `SexuallyExplorative` `[2.140]`
- `[ 03.0109 ]` `[ ]` Predisposizione a intimità mentale/emotiva
- `[ 03.0110 ]` `[ ]` Sexual Education Profile (SEP) `[0.230]`
- `[ 03.0111 ]` `[ ]` Esplorazione intimità e novità relazionale `[1.480]`
- `[ 03.0112 ]` `[ ]` Orientamento sessuale dinamico e fasi esplorazione `[1.260]`
- `[ 03.0113 ]` `[ ]` `CulturalProfile` — norme, inibizioni, reazioni `[0.520]`

#### 3.7 — Bisogni `[0.010]`

- `[ 03.0200 ]` `[ ]` Sistema bisogni: `hunger`, `thirst`, `bladder`,
  `energy`, `hygiene`, `social`, `fun`, `comfort`, `intimacy`, ...
- `[ 03.0201 ]` `[ ]` Decadimento e soglie critiche
- `[ 03.0202 ]` `[ ]` Intimità personale (solitudine) `[0.180]`
- `[ 03.0203 ]` `[ ]` Reazioni emotive a rifiuto/insuccesso intimo `[0.220]`
- `[ 03.0204 ]` `[ ]` Erotismo non fisico e intimità cognitiva `[0.260]`
- `[ 03.0205 ]` `[ ]` Fattori di stress inibenti `[0.140]`
- `[ 03.0206 ]` `[ ]` Curva dinamica del desiderio `[0.120]`
- `[ 03.0207 ]` `[ ]` Intimità non sessuale (azioni sostitutive) `[0.150]`
- `[ 03.0208 ]` `[ ]` Regolazione intima autonoma `[0.180]`
- `[ 03.0209 ]` `[ ]` Intimità digitale e virtuale `[0.210]`

#### 3.8 — Ciclo vita NPC `[0.100]`

- `[ 03.0300 ]` `[ ]` Fasi vita integrate con Anthalys (PARTE II)
- `[ 03.0301 ]` `[ ]` Transizioni di fase con effetti (pubertà, età adulta, ecc.)
- `[ 03.0302 ]` `[ ]` Invecchiamento progressivo
- `[ 03.0303 ]` `[ ]` Morte e cause
- `[ 03.0304 ]` `[ ]` Eredità e successione

#### 3.9 — Famiglia e Relazioni `[0.200]`

Vedi TODO originale §4.3 (invariato). Riepilogo:

- `[ 03.0400 ]` `[ ]` Sistema famiglia e albero genealogico
- `[ 03.0401 ]` `[ ]` Dinamiche familiari intergenerazionali `[0.250]`
- `[ 03.0402 ]` `[ ]` Dinamiche sociali avanzate `[0.250]`
- `[ 03.0403 ]` `[ ]` Dinamiche di coppia adolescenti `[0.255]`
- `[ 03.0404 ]` `[ ]` Poliamorosità `[2.500]`
- `[ 03.0405 ]` `[ ]` Dinamiche LGBTQ+ `[1.500]`
- `[ 03.0406 ]` `[ ]` Consanguineità culturale `[1.800]`
- `[ 03.0407 ]` `[ ]` Eventi sociali drastici/rotture `[0.850]`
- `[ 03.0408 ]` `[ ]` Mentoring intergenerazionale `[1.250]`
- `[ 03.0409 ]` `[ ]` Pettegolezzo e reputazione `[2.100]`
- `[ 03.0410 ]` `[ ]` Preferenze intime e compatibilità `[2.240]`
- `[ 03.0411 ]` `[ ]` Infedeltà con sfumature `[1.980]`
- `[ 03.0412 ]` `[ ]` Noia relazionale/routine `[1.760]`
- `[ 03.0413 ]` `[ ]` Intesa erotica e complicità `[0.980]`
- `[ 03.0414 ]` `[ ]` Libido asimmetrica e negoziazione `[1.340]`
- `[ 03.0415 ]` `[ ]` Intimità come comunicazione emotiva `[1.360]`

#### 3.10 — AI NPC `[0.010]`

Vedi TODO originale §4.5 (invariato). Riepilogo:

- `[ 03.0500 ]` `[ ]` Sistema base azioni
- `[ 03.0501 ]` `[ ]` Logica decisionale (utility + behaviour tree)
- `[ 03.0502 ]` `[ ]` Implementazione azioni specifiche
- `[ 03.0503 ]` `[ ]` Sistema stati umore e influenza `[0.500]`
- `[ 03.0504 ]` `[ ]` Cure infantili e genitorialità `[0.800]`
- `[ 03.0505 ]` `[ ]` Obiettivi e aspirazioni
- `[ 03.0506 ]` `[ ]` Pianificazione AI avanzata e apprendimento
- `[ 03.0507 ]` `[ ]` Simulazione off-screen e LOD
- `[ 03.0508 ]` `[ ]` Sistema moodlet ed espressioni
- `[ 03.0509 ]` `[ ]` Sistema relazioni sociali `[0.700]`
- `[ 03.0510 ]` `[ ]` Caratteristiche avanzate
- `[ 03.0511 ]` `[ ]` Coping intimo disfunzionale `[1.420]`
- `[ 03.0512 ]` `[ ]` Esiti negativi intimità `[0.620]`

#### 3.11 — Memoria NPC `[1.300]`

- `[ 03.0600 ]` `[ ]` Struttura base memoria
- `[ 03.0601 ]` `[ ]` Architettura a livelli (short/long/emotional)
- `[ 03.0602 ]` `[ ]` Processi gestione memoria (decay, consolidamento)
- `[ 03.0603 ]` `[ ]` Integrazione con altri sistemi
- `[ 03.0604 ]` `[ ]` Persistenza emotiva residua `[1.320]`
- `[ 03.0605 ]` `[ ]` Micro-ancore emotive `[2.120]`
- `[ 03.0606 ]` `[ ]` Conflitto relazionale latente
- `[ 03.0607 ]` `[ ]` `FantasyProfile` — vita fantasmatica interiore `[2.420]`
- `[ 03.0608 ]` `[ ]` Memoria emotiva intima `[1.520]`

#### 3.12 — Consapevolezza sociale `[0.710]`

- `[ 03.0700 ]` `[ ]` Scoperta tratti tramite interazione
- `[ 03.0701 ]` `[ ]` Norme culturali su intimità e sessualità `[1.620]`

#### 3.13 — Storyline generate AI `[2.000]`

- `[ 03.0800 ]` `[ ]` Auto-narrazione `[2.120]`
- `[ 03.0801 ]` `[ ]` Crollo cosciente e ricostruzione identitaria `[2.180]`

#### 3.14 — Comportamenti emergenti e "Riverie" `[2.100]`

- `[ 03.0900 ]` `[ ]` Recupero intimità post-trauma `[1.900]`

#### 3.15 — Autoanalisi, riflessività, cambiamento `[2.200]`

- `[ 03.1000 ]` `[ ]` Self-Reflection
- `[ 03.1001 ]` `[ ]` Impatto su comportamento e personalità
- `[ 03.1002 ]` `[ ]` Diario o voce interiore

---

### 🌐 FASE 4 — World (range 5300–5399)

Vedi TODO originale §3 (invariato). Riepilogo:

#### 4.1 — Struttura mondo e lotti `[0.025]`

- `[ 04.0001 ]` `[ ]` Quartieri, lotti, edifici
- `[ 04.0002 ]` `[ ]` Sistema coordinate (griglia 2D)

#### 4.2 — Proprietà e gestione lotti `[2.000]`

- `[ 04.0010 ]` `[ ]` Acquisto, vendita, affitto, mutui

#### 4.3 — Build Mode (strutture) `[1.400]`

- `[ 04.0020 ]` `[ ]` Pareti, porte, finestre, tetti
- `[ 04.0021 ]` `[ ]` Anteprima 3D con Three.js `[F]`

#### 4.4 — Buy Mode (oggetti) `[0.027]`

- `[ 04.0030 ]` `[ ]` Catalogo oggetti per categoria

#### 4.5 — Style Mode (pittura, rivestimenti) `[1.400]`

#### 4.6 — Terrain Mode (landscaping)

#### 4.7 — Gestione mondo (livello città) `[2.200]`

#### 4.8 — Sistema oggetti e crafting `[1.000]`

#### 4.9 — Infrastrutture e urbanistica `[1.400]`

#### 4.10 — Trasporti (auto, bus, metro, traghetti, aerei)

- `[ 04.0100 ]` `[ ]` `TransportService` (pathfinding multi-tratta)
- `[ 04.0101 ]` `[ ]` Veicoli privati NPC (carburante, parcheggi)
- `[ 04.0102 ]` `[ ]` Accessibilità (NPC con disabilità)

---

### 💰 FASE 5 — Economy (range 5400–5499)

Vedi TODO originale §9 + §10 (invariato). Riepilogo:

- `[ 05.0000 ]` `[ ]` Sistema economico base (Athel, offerta, domanda)
- `[ 05.0010 ]` `[ ]` Banche, mutui, investimenti
- `[ 05.0020 ]` `[ ]` Tasse e fisco
- `[ 05.0030 ]` `[ ]` **AION** — piattaforma commerciale centralizzata `[3.500]`
- `[ 05.0040 ]` `[ ]` AION spedizioni cargo
- `[ 05.0050 ]` `[ ]` Mercato azionario locale

---

### 🏛️ FASE 6 — Politics (range 5500–5599)

Vedi TODO originale §6 + §21 (invariato). Riepilogo:

- `[ 06.0000 ]` `[ ]` Governo, elezioni, partiti
- `[ 06.0010 ]` `[ ]` Leggi e regolamenti
- `[ 06.0020 ]` `[ ]` Servizi pubblici (sanità, scuola, sicurezza)
- `[ 06.0030 ]` `[ ]` Costituzione di Anthal — framework legale
- `[ 06.0040 ]` `[ ]` Partecipazione civica e proteste

---

### 🌐 FASE 7 — SoNet (range 5600–5699)

Vedi TODO originale §16 (invariato). Portale unico dei servizi al cittadino.

- `[ 07.0000 ]` `[ ]` Identità digitale del cittadino
- `[ 07.0010 ]` `[ ]` Servizi online (documenti, prenotazioni, pagamenti)
- `[ 07.0020 ]` `[ ]` Fascicolo sanitario elettronico
- `[ 07.0030 ]` `[ ]` Fascicolo scolastico
- `[ 07.0040 ]` `[ ]` Dichiarazione dei redditi
- `[ 07.0050 ]` `[ ]` Votazioni digitali

---

### 🌍 FASE 8 — Multiplayer (range 5700–5799)

Vedi TODO originale §28 (invariato). Tempo reale accelerato.

- `[ 08.0000 ]` `[!]` Architettura client-server
- `[ 08.0010 ]` `[ ]` Sincronizzazione stato (WebSocket / UDP)
- `[ 08.0020 ]` `[ ]` Server authority su NPC e mondo
- `[ 08.0030 ]` `[ ]` Scaling (sharding per quartiere/regione)
- `[ 08.0040 ]` `[ ]` Persistenza multiplayer (PostgreSQL cluster)
- `[ 08.0050 ]` `[ ]` Anti-cheat
- `[ 08.0060 ]` `[ ]` Chat globale e vocale
- `[ 08.0070 ]` `[ ]` Economia persistente cross-server
- `[ 08.0080 ]` `[ ]` Sistema di "istanze" per eventi

---

### 🎁 FASE 9 — Bonus / Debito tecnico

- `[ 09.0000 ]` `[ ]` Refactor e hardening generale
- `[ 09.0010 ]` `[ ]` Ottimizzazione performance (profilazione, cache)
- `[ 09.0020 ]` `[ ]` Documentazione tecnica completa
- `[ 09.0030 ]` `[ ]` Sistema di plugin/estensioni utente
- `[ 09.0040 ]` `[ ]` Analizzatore statico + fix mypy/pyright
- `[ 09.0050 ]` `[ ]` Setup deploy e distribuzione

---

## PARTE IV — DETTAGLI FASI RIMANENTI

Le seguenti sezioni sono **mantenute dall'originale** ma riassunte.
Per il contenuto integrale, vedi il TODO originale SimAI.

### Sistema scolastico (§5)

### Sistema mediatico (§8)

### Sistema abilità (§11)

### Interfaccia e UI (§12)

### Database e performance (§13)

### Feature avanzate (§14)

### Bilanciamento e gameplay (§15)

### Localizzazione e multilingua (§17)

### Giochi d'azzardo e scommesse (§18)

### Atteggiamenti culturali/familiari (§19)

### Strumenti developer (§20)

### Sistema sanitario approfondito (§22)

### Clima e eventi atmosferici (§23)

### Flora di Anthalys (§24)

### Fauna di Anthalys (§25)

### Vita militare e difesa (§26)

### Lore per Anthalys (§27)

---

## PARTE V — ARCHITETTURA TECNICA PYTHON

### V.1 Diagramma moduli

```mermaid
graph TD
    subgraph Core["Core (5000-5099)"]
        A1[SimulationLoop]
        A2[TimeManager]
        A3[EventBus]
        A4[SaveManager]
    end

    subgraph Time["Anthalys Time (5100-5199)"]
        T1[AnthalysDateTime]
        T2[AnthalysCalendar]
        T3[Holidays]
        T4[MoonCycles]
    end

    subgraph NPC["NPC (5200-5299)"]
        N1[Character]
        N2[NeedsProcessor]
        N3[AIDecisionMaker]
        N4[ActionExecutor]
        N5[Genetics]
        N6[Relationships]
        N7[Memory]
    end

    subgraph World["World (5300-5399)"]
        W1[Location]
        W2[GameObject]
        W3[Transport]
        W4[Climate]
    end

    subgraph Economy["Economy (5400-5499)"]
        E1[Market]
        E2[AION]
        E3[Banking]
    end

    subgraph Politics["Politics (5500-5599)"]
        P1[Government]
        P2[Laws]
        P3[Elections]
    end

    subgraph SoNet["SoNet (5600-5699)"]
        S1[CitizenPortal]
        S2[Services]
    end

    subgraph Networking["Networking (5700-5799)"]
        M1[MultiplayerServer]
        M2[Sync]
    end

    Core --> Time
    Core --> NPC
    Core --> World
    World --> Economy
    Economy --> Politics
    Politics --> SoNet
    SoNet --> Networking

    NPC -.-> Time
    World -.-> NPC
    Economy -.-> NPC
```

### V.2 Flusso di un tick

```
1. SimulationLoop.tick() riceve il segnale
2. TimeManager.advance_tick()
   → emette "time.hour.changed" (se ora cambiata)
   → emette "time.day.changed" (se giorno cambiato)
   → emette "time.month.changed", "time.year.changed", ...
3. EventBus.process_queue()
   → esegue listener registrati in ordine di priorità
4. WorldManager.update_environment()
   → aggiorna meteo, temperatura, stagione
   → aggiorna attributi location (cleanliness, noise, ...)
5. NPСManager.update_all_npcs()  # per LOD FULL e REDUCED
   → per ogni NPC: NeedsProcessor.update()
   → AIDecisionMaker.decide()
   → ActionExecutor.execute()
6. WorldManager.update_state()
   → accumula sporcizia, rumore, cambiamenti infrastrutturali
7. SaveManager.maybe_autosave()  # ogni N tick
8. PerformanceMonitor.record_tick_duration()
```

### V.3 Modello di concorrenza

- **Single-thread** di default (semplicità, debug, riproducibilità).
- **Async** opzionale per I/O (salvataggi, chiamate LLM future).
- **Multiprocessing** per lotti di NPC `BACKGROUND` (opzionale, se profilo mostra bottleneck).

### V.4 Database

- **SQLite** primario con PRAGMA:
  - `journal_mode=WAL`
  - `foreign_keys=ON`
  - `synchronous=NORMAL`
- **PostgreSQL** opzionale via `SIMAI_DB_URL`.
- **Alembic** per migrazioni (formato `NNNN_SS_slug.py`).

### V.5 Storage

- **SQLite** → dati simulazione
- **File JSON** → config e save esportabili
- **Formato `.sav`** → dump compresso (zstd) e opzionalmente cifrato (Fernet)
- **Directory `data/`**:
  - `data/saves/` — salvataggi
  - `data/logs/` — log applicativi
  - `data/exports/` — CSV/JSON esportati
  - `data/lore/` — contenuti lore (accessibili runtime)

---

## PARTE VI — DEBITO TECNICO

### VI.1 Miglioramenti futuri abbigliamento

- `[ ]` Override colore/pattern per singolo capo
- `[ ]` Influenza ambientale su tratti/abilità (non solo genetica)
- `[ ]` Tratti poligenici (più alleli per tratto)
- `[ ]` Dominanza/recessività

### VI.2 Build Mode enhancements

- `[ ]` Anteprima 3D con Three.js
- `[ ]` Undo/redo
- `[ ]` Snap automatico a muri
- `[ ]` Stili tetto selezionabili
- `[ ]` Collision detection scale

### VI.3 Regolamenti ambientali

- `[ ]` Impatto su umore NPC (inquinamento)
- `[ ]` Eventi casuali (ispezioni, multe)
- `[ ]` Conseguenze economiche

### VI.4 Lavoro e trasporti NPC

- `[ ]` Viaggio verso location appropriata
- `[ ]` Stipendio periodico
- `[ ]` Skill influenzano performance/promozioni

### VI.5 AION e spedizioni cargo

- `[ ]` Collegamento a inventario AION

### VI.6 Pathfinding multi-tratta

- `[ ]` `TravelAction` generica

### VI.7 Veicoli privati NPC

- `[ ]` Uso auto privata
- `[ ]` Consumo carburante

### VI.8 Accessibilità trasporti

- `[ ]` Filtro rotte accessibili

### VI.9 Crisi di mezza età

- `[ ]` Effetti aggiuntivi (`apply_midlife_crisis_effects`)

### VI.10 Albero genealogico — d3.js

- `[ ]` Integrazione d3.js in `ui/static/js/d3.min.js`

### VI.11 Analisi errori (dal TODO originale)

- `[ ]` **Variabili non definite**: `target_location`, `partner`
  in azioni e NeedsProcessor
- `[ ]` **Metodi mancanti**: `Character.is_parent_of()`,
  `NameGenerator.generate_last_name()` (statico)
- `[ ]` **Service duplicati**: `NPCAIService` vs `AIDecisionMaker`
- `[ ]` **Relazioni duplicate**: `family_relationships` e `relatives`
- `[ ]` **Enum `LifeStage` duplicato**
- `[ ]` **Firme incoerenti** in `ActionExecutor.execute_action()`
- `[ ]` **N+1 query** in `SimulationService.update_npcs()`
- `[ ]` **Cache in-memory** per `WorldState.get()/set()`
- `[ ]` **Indici mancanti** su FK

### Tabella riepilogo critici

| Issue                                       | Severità | File                    |
| ------------------------------------------- | -------- | ----------------------- |
| `target_location` non definita              | Alta     | MoveAction, TakeMetroAction, UseBusAction, UseFerryAction, UseMetroAction |
| `partner` in `NeedsProcessor`               | Alta     | NeedsProcessor          |
| `is_parent_of()` mancante                   | Media    | Character               |
| Metodo statico chiamato come istanza        | Media    | NameGenerator           |
| Service duplicato `NPCAIService`            | Bassa    | NPCAIService            |

### VI.12 Note architetturali aperte

- `[ ]` Decidere dove collocare l'evento `WorkflowTransition`
  (attualmente in `WorkflowEmail` in ClaireCMS, non rilevante per SimAI)
- `[ ]` Definire schema URL per UI web (se abilitata) — no CDN
- `[ ]` Decidere se abilitare test in futuro (richiederebbe override
  della no-test policy)

---

## 📅 ROADMAP DI RILASCIO

| Versione | Contenuto                              | Stato   |
| -------- | -------------------------------------- | ------- |
| `0.1.0`  | FASE 0–1 (Setup + Core Simulation)     | `[ ]`   |
| `0.2.0`  | FASE 2 (Anthalys Time)                 | `[ ]`   |
| `0.3.0`  | FASE 3 (Character/NPC)                 | `[ ]`   |
| `0.4.0`  | FASE 4 (World)                         | `[ ]`   |
| `0.5.0`  | FASE 5 (Economia, AION)                | `[ ]`   |
| `0.6.0`  | FASE 6 (Politica)                      | `[ ]`   |
| `0.7.0`  | FASE 7 (SoNet)                         | `[ ]`   |
| `0.8.0`  | FASE 8 (Multiplayer)                   | `[ ]`   |
| `0.9.0`  | FASE 9 (Hardening)                     | `[ ]`   |
| `1.0.0`  | Prima release stabile pubblica         | `[ ]`   |

---

### 📝 Note operative finali

1. **Convenzione priorità**: a parità di priorità, vale l'ordine di lettura.
2. **Ogni task chiuso** deve avere:
   - Commit Conventional Commit
   - Entry in `CHANGELOG.md` (sezione `[Unreleased]` → poi spostata)
   - Bump di versione (PATCH fix, MINOR feature)
3. **Ogni package nuovo** deve avere:
   - `__init__.py` che esporta l'API pubblica
   - `README.md` nel package (se ≥ 5 moduli interni)
   - Migrazioni Alembic nel range corretto
4. **Prima di taggare una release**:

   ```bash
   ruff check .
   ruff format --check .
   mypy simai/
   python -m simai db upgrade
   python -m simai version
   ```

5. **Compatibilità retroattiva**: da `1.0.0` in poi, ogni breaking
   change richiede MAJOR bump.
6. **Deprecazioni**: annunciare in `CHANGELOG.md` sotto `Deprecated`
   almeno una minor version prima della rimozione.
7. **SimAI — istruzioni specifiche**:
   - Linguaggio principale **Python 3.12+**
   - DB **SQLite** (PostgreSQL opzionale)
   - UI web in **Jinja2 + CSS/JS nativi** (nessun bundler)
   - Rispetto rigoroso dei **Principi Guida** (§VI.0 → mantenuti
     dall'originale: Unicità, Coerenza, Realismo bilanciato,
     Rispetto, Modularità, Approccio modulare, Lore, Deep simulation)
   - Coerenza con il lore di Anthalys e la Costituzione
   - Sistema tempo personalizzato (432 giorni / 18 mesi / 24 giorni / 28 ore)
   - Fasce di età Anthaliane (PARTE II di questo TODO)
   - Nessun test (no-test policy)
8. **Niente Vite / npm / Node.js** — tassativo, come per ClaireCMS.
9. **Niente CDN** — tutto offline-first.

---

### 📌 Note sull'output

1. **Il TODO completo fa riferimento al TODO SimAI originale** per le sezioni 4.1–4.10, 5, 6, 8–27. Quelle sezioni sono **riassunte** per evitare di generare un documento enorme; il TODO originale le contiene integralmente. Se vuoi che le espanda una per una, fammelo sapere.

2. **Le regole della PARTE I** sono adattate da PHP/Laravel a Python:
   - `Auth::` → `current_actor()`
   - Migration `NNNN_SS_slug.php` → Alembic `NNNN_SS_slug.py`
   - Composer → Poetry/uv
   - Blade → Jinja2
   - Artisan → Typer
   - Eloquent → SQLAlchemy 2.0
   - Spatie packages → custom implementations

3. **Nessuna dipendenza da ClaireCMS/ScienzaViva** è richiesta a livello di codice: SimAI è autonomo. Il lore (Anthalys, Costituzione) è condiviso a livello di contenuto.

4. **La no-test policy** è mantenuta per coerenza con ClaireCMS. Per una simulazione di questa complessità, potrebbe essere rivalutata in futuro — ho lasciato il debito tecnico come `[ ]` decidere.

5. **Il file è pronto per essere salvato** come `TODO_SimAI.md` alla root di un nuovo progetto Python separato.
