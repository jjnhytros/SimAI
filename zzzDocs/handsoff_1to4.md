# 🚀 Prompt di migrazione — Progetto SimAI

Copia **integralmente** il blocco sottostante in una **nuova conversazione** come primo messaggio. Contiene tutto il contesto, le regole, lo stato attuale e le convenzioni concordate.

---

```markdown
# SimAI — Simulazione di Anthalys (Python 3.13+)

Stai assistendo lo sviluppo di **SimAI**: una simulazione di vita ad agenti
ambientata nel mondo di **Anthalys**. Scritta in **Python 3.13**, SQLAlchemy 2.0,
Pydantic v2, SQLite (PostgreSQL opzionale), Typer + Rich per CLI, FastAPI + Jinja2
per UI web opzionale. Nessun bundler, nessuna CDN, nessun npm/node.

---

## 🏛️ REGOLE ARCHITETTURALI (TASSATIVE — dal TODO.md)

### 1. Linguaggio e runtime
- **Python 3.13+** — usa `match/case`, PEP 604 (`X | None`), `Self`, ecc.
- **SQLAlchemy 2.0** (ORM dichiarativo con `Mapped[]` e `mapped_column`)
- **Pydantic v2** — validazione e serializzazione
- **Alembic** — migrazioni database (formato file: `NNNN_SS_slug.py`)
- **Typer** — comandi CLI
- **Rich** — output CLI
- **Loguru** — logging
- **Nessun test** — no-test policy attiva (cartella `tests/` eliminata)

### 2. Modularità rigorosa
Package Python dedicati: `core/`, `npc/`, `world/`, `sim/`, `db/`, `config/`,
`cli/`, `ui/`, `utils/`, `economy/`, `city/`. Ogni feature significativa vive
nel suo package.

**Eccezioni legittime (Core)**: `Character`, `Location`, `GameObject`,
`TimeManager`, `SimulationLoop`, `EventBus`, `SaveManager`, `DecisionSystem`.
**Tutto il resto deve essere package.**

### 3. Naming migrazioni Alembic (range-based)
Formato: `NNNN_SS_descrizione.py`.
- `5000–5099` SimAI/Core Simulation
- `5100–5199` SimAI/Anthalys Time
- `5200–5299` SimAI/NPC
- `5300–5399` SimAI/World
- `5400–5499` SimAI/Economy
- `5500–5599` SimAI/Politics
- `5600–5699` SimAI/SoNet
- `5700–5799` SimAI/Networking (MP)

La catena `down_revision` segue l'ordine numerico.

### 4. Accesso all'attore corrente
Mai variabili globali mutabili. Usa sempre `from simai.core.context import current_actor`.

### 5. Asset locali — MAI CDN
Tutto in `simai/ui/static/` (bootstrap, htmx, alpine, d3, chart.js, bootstrap-icons).
Eccezioni: nessuna. Offline-first.

### 6. File integrali
Quando mostri un file Python o un template Jinja2, **mostralo integralmente**.
Se troppo lungo, spezza in più messaggi ma non troncare mai. Non generare README
o CHANGELOG a meno che non venga esplicitamente richiesto.

### 7. Zero stub / placeholder
Mai `pass`, `...`, `NotImplementedError`, `# TODO`. Solo codice reale e funzionante.

### 8. Dipendenze
Gestite con **uv** (non Poetry). `pyproject.toml` con `[project.dependencies]`.
Lock file `uv.lock` versionato.

### 9. Timezone e calendario
`datetime` naive in UTC o `AnthalysDateTime`. Anthalys: 432 giorni/anno,
18 mesi × 24 giorni, 28 ore/giorno, 60 min/ora. Vedi `simai/config/anthalys.py`.

### 10. Random e riproducibilità
Mai `random` globale. Usa `random.Random(seed)` iniettato. Seed di simulazione
riproducibile.

### 11. Conventional Commits
`<type>(<scope>): <subject>`. Type: `feat`, `fix`, `docs`, `style`, `refactor`,
`perf`, `test`, `build`, `ci`, `chore`, `revert`. Scope: nome package.

### 12. Versioning (SemVer 2.0.0)
`pyproject.toml`, `simai/__version__.py`, tabella `core_version` (migrazione 5000).

### 13. Niente Vite/npm/node, niente CDN
UI con Jinja2 + CSS/JS nativi.

---

## 🧠 CONVENZIONI DI RISPOSTA

1. **Non generare test.**
2. **File integrali**, mai parziali (ma non generare README/CHANGELOG se non richiesto).
3. **Niente CDN.**
4. **API esplicita** (`current_actor()`), mai global mutabili.
5. **Type hints FQCN** e `Mapped[...]` SQLAlchemy ovunque.
6. **Annotazioni di tipo esplicite** dove mypy non arriva.
7. **Non toccare `core/`** senza esplicito via libera.
8. **Niente stub o placeholder**: solo codice funzionante.
9. **Nome file completo** quando mostri codice.
10. **Checklist finale** con tabella task + `▶️ Comandi` + `Note operative`.
11. Rispondi in **italiano**, conciso ma completo.
12. Nel checkup: verdetto 🔴/🟠/🟡/🟢 + tabella + domande di conferma.
13. Se manca contesto, **chiedi** prima di scrivere codice.
14. **Aggiorna `docs/simai/README.md`** ad ogni fine sezione (ma solo se richiesto).
15. **`./scripts/check.sh`** è il gate di qualità: ruff check/format, mypy strict.
16. **Usa `coerce_int`, `coerce_float`, `coerce_str`** (in `simai/utils/coerce.py`)
    invece di `# type: ignore` sui cast.

---

## 📦 STATO ATTUALE DEL PROGETTO

- **FASE 0** — Setup iniziale ✅
- **FASE 1** — Core Simulation (TimeManager, SimulationLoop, EventBus, LOD,
  SaveManager, Location/GameObject, Statistics) ✅
- **FASE 2** — Anthalys Time esteso (Holidays, MoonCycles, Seasons, AstroEvents,
  AnthalysClock) ✅
- **FASE 3** — Character/NPC (genetica, bisogni, AI, tratti, skills, memoria,
  relazioni, ciclo vita, famiglia, intimità, background, personalità dinamica) ✅
- **FASE 4** — World (District, Lot, proprietà/mutui, Build mode, Buy mode,
  Style mode, Terrain mode, City (servizi/tasse/budget), Infrastructure
  (strade/lampioni), Transport (veicoli, linee, pathfinding, transito temporale,
  multi-leg, UI live)) ✅ **completata**
- **FASE 5** — Economy (banche, mutui, tassazione, AION) → **prossimo step**
- **FASE 6** — Politics
- **FASE 7** — SoNet
- **FASE 8** — Multiplayer
- **FASE 9** — Hardening/deploy

---

## 📂 STRUTTURA DEI PACKAGE (aggiornata)

```
simai/
├── __init__.py, __main__.py, __version__.py, py.typed
├── cli/               # Typer: app.py, cmd_city.py, cmd_db.py, cmd_economy.py,
│                      # cmd_npc.py, cmd_save.py, cmd_sim.py, cmd_stats.py,
│                      # cmd_transport.py, cmd_ui.py, cmd_world.py
├── config/            # settings.py, anthalys.py, logging.py, loader.py, simulation.yaml
├── core/              # anthalys_datetime.py, anthalys_calendar.py, time_manager.py,
│                      # event_bus.py, simulation_loop.py, lod.py, save_manager.py
├── city/              # enums.py, models.py, service.py, tax.py, satisfaction.py,
│                      # mood.py, seed.py, infrastructure/ (enums, models, service),
│                      # transport/ (enums, models, service, pathfinding, transit,
│                      # multi_leg, seed)
├── economy/           # enums.py, models.py, jobs.py, market.py, payday.py,
│                      # property.py, seed.py
├── npc/               # ai/ (actions, utility, executor, coordinator, bt/),
│                      # needs/, traits/, skills/, genetics/, memory/, intimacy/,
│                      # relationships/, lifecycle/, addictions/, background/,
│                      # identity/, reflection/, social_awareness/, personality/,
│                      # crafting/, housing/, economy/, stats/,
│                      # manager.py, models.py, mood.py, generator.py, name_generator.py
├── sim/anthalys/time/ # astro.py, calendar.py, clock.py, holidays.py, moons.py, seasons.py
├── db/                # base.py, session.py, registry.py, models/
├── ui/                # app.py, deps.py, routes/ (dashboard, npcs, world_routes,
│                      # economy_routes, city_routes, infrastructure_routes,
│                      # transport_routes, api, live, build_routes),
│                      # templates/ (base.html + pagine), static/ (css, js, fonts)
├── world/             # enums.py, models.py, district.py, lot.py, location_service.py,
│                      # game_object_service.py, pathfinding.py, lot_service.py,
│                      # seed.py, build/, buy/, style/, terrain/
└── utils/             # coerce.py, git.py
```

---

## 🔑 DECISIONI CHIAVE PRESE

- **`TimeManager` iniettato** (non singleton) in `SimulationLoop`.
- **`AnthalysDateTime` / `AnthalysCalendar` / `TimeManager` in `core/`** (range 5000).
- **Estensioni Anthalys** (Holidays, MoonCycles, AstroEvents) in `sim/anthalys/time/`.
- **Migrazioni**: prima `5000_01_core_version`, ultima attuale `5300_11_transit`.
- **`config/anthalys.py`** contiene costanti calendario, stagioni, fasi, life stages.
- **`LIFESTAGE_*`** in `config/anthalys.py` (confermato).
- **UI**: FastAPI + Jinja2 + htmx + Alpine.js + D3.js + Chart.js, tutti in locale.
- **Nessuna dipendenza da ClaireCMS/ScienzaViva** a livello codice; solo lore condiviso.
- **No-test policy** attiva. `tests/` eliminata.
- **`simai/py.typed`** presente per PEP 561.
- **`./scripts/check.sh`** esegue `ruff check --fix .`, `ruff format .`,
  `ruff check .`, `ruff format --check .`, `mypy simai/`.
- **`uv`** come dep manager (non Poetry). `uv.lock` versionato.

---

## ⚙️ STACK TECNICO (riepilogo)

| Componente     | Libreria / Tool                              |
|----------------|----------------------------------------------|
| Runtime        | CPython 3.13+                                |
| CLI            | Typer 0.12+                                  |
| Output CLI     | Rich 13+                                     |
| ORM            | SQLAlchemy 2.0                               |
| Migrations     | Alembic 1.13+                                |
| Validation     | Pydantic v2                                  |
| Settings       | pydantic-settings                            |
| Logging        | Loguru                                       |
| Web UI (opz.)  | FastAPI + Jinja2 + Uvicorn                   |
| Type check     | mypy --strict, pyright                       |
| Lint / format  | Ruff (lint + format)                         |
| Dep manager    | uv                                           |
| DB dev         | SQLite                                       |
| DB prod (opz.) | PostgreSQL                                   |
| UI asset       | bootstrap, htmx, alpine, d3, chart.js (locali)|

---

## 📅 PROSSIMO STEP

Dopo FASE 4 completa, le opzioni sono:

- **A) FASE 5 — Economy**: banche, mutui, tassazione, AION, azioni.
- **B) FASE 6 — Politics**: governo, elezioni, leggi, servizi pubblici,
  Costituzione di Anthal.
- **C) FASE 7 — SoNet**: portale servizi al cittadino.
- **D) FASE 8 — Multiplayer**.
- **E) Altro** (debito tecnico, hardening, o richieste specifiche).

**Chiedi all'utente da dove vuole partire prima di scrivere codice.**

---

## ✅ CHECKLIST GENERALE

Quando completi un chunk:
1. Aggiorna `CHANGELOG.md` (solo se richiesto).
2. Aggiorna `docs/simai/README.md` (solo se richiesto).
3. Includi `▶️ Comandi` di verifica.
4. Includi `📌 Note operative`.
5. Verifica `./scripts/check.sh` prima di dichiarare completato.
6. Se manca contesto, chiedi prima di scrivere.

---

## 🎯 ISTRUZIONI IMMEDIATE

1. Conferma ricezione del contesto in una riga.
2. Chiedi all'utente da dove partire (A/B/C/D/E).
3. Aspetta la scelta prima di scrivere codice.
```

---

## 📌 Come usarlo

1. Apri una **nuova conversazione**.
2. Incolla **integralmente** il blocco `markdown` sopra come **primo messaggio**.
3. L'assistente confermerà la ricezione e chiederà da dove partire.
4. Rispondi con la tua scelta (es. `A) FASE 5 — Economy`) e prosegui.

---

## ✅ Cosa è preservato

- Tutte le regole architetturali del TODO.md.
- Le convenzioni di risposta personalizzate.
- Lo stato completo delle FASI 0–4.
- La struttura aggiornata dei package.
- Le decisioni chiave prese durante lo sviluppo.
- Lo stack tecnico completo.
- Il prossimo step (FASE 5, 6, 7, 8 o debito tecnico).
- Il flusso di lavoro con `check.sh` e `coerce_*`.
- La no-test policy, no-CDN, no-Vite.

---

## ❓ Nota

Se vuoi, posso anche generare un file `PROMPT_MIGRAZIONE.md` da salvare nella root del progetto, così lo hai sempre a portata di mano. Fammi sapere. 🚀