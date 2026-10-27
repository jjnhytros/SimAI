# SimAI 1.3.0

SimAI è il motore di simulazione della vita di Anthalys. La 1.0 ha
dimostrato che il nucleo funziona end-to-end (`avvia → simula → interagisci
→ salva → ricarica`); le release successive hanno aggiunto movimento NPC,
moodlet, economia, lavoro fisico e tratti.

Il mondo iniziale è il **Quartiere delle Muse**: 3 location (casa,
piazza, caffè), 5 personaggi (4 NPC autonomi + 1 Sim giocabile).

## Requisiti

- Python 3.13
- [`uv`](https://docs.astral.sh/uv/) (consigliato) oppure `pip`

## Installazione

Con `uv`:

```bash
git clone <repo-url> SimAI
cd SimAI
uv sync --all-extras
```

Senza `uv`:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Avvio rapido

```bash
# Inizializza il database
simai db upgrade

# Popola il Quartiere delle Muse (idempotente)
simai world seed

# Vedi lo stato del tuo Sim
simai player status

# Fai avanzare la simulazione di 24 tick (24 ore simulate)
simai sim run --ticks 24

# Il tuo Sim ha fame? Mangia.
simai player do -a eat

# Controlla economia, lavoro e tratti
simai economy jobs
simai economy ledger -c giulia
simai npc traits -c luca

# Salva, esci, riprendi
simai save create -n partita1
simai save list
simai save load partita1 --yes
```

## Comandi principali

### Mondo e stato

```bash
simai world seed                  # popola il quartiere (idempotente)
simai world list                  # elenca location e personaggi
simai player status               # pannello completo del tuo Sim (bisogni, lavoro, tratti)
simai needs show -c <key>         # bisogni e umore di un personaggio
simai relationships show -c <key> # relazioni in uscita
simai npc traits -c <key>         # tratti dell'NPC
```

### Simulazione

```bash
simai sim tick [-m MINUTI]                          # un tick
simai sim run --ticks N [-m MINUTI]                 # N tick
simai sim run --ticks N --autosave-every K          # con autosave
simai sim state                                     # tick e seed correnti
simai sim reset [--seed N]                          # azzera lo stato
simai sim benchmark --years N [--output FILE]       # simulazione accelerata
```

### Giocatore

```bash
simai player do -a <eat|drink|play|socialize>
simai player move -l <location>
```

Le azioni sono disponibili solo se il bisogno che soddisfano è sotto
soglia:

- `eat` — `hunger < 30`
- `drink` — `thirst < 40`
- `play` — `fun < 70`
- `socialize` — `intimacy < 70`

Se il bisogno è già alto, l'azione viene rifiutata con un messaggio
chiaro: `Azione 'eat' non necessaria: hunger=94.0 (soglia 30)`.

Il player **non** ha auto-work né auto-play: se non invochi `player do`,
i suoi bisogni decadono fino a zero.

### Economia

```bash
simai economy balance [-c KEY]      # saldo e storico
simai economy ledger  [-c KEY]      # transazioni (SALARY, PURCHASE, ...)
simai economy jobs                  # stato corrente (al lavoro / in attesa / fuori orario)
```

Il salario viene pagato a fine giornata convenzionale (tick 23, 47, 71, ...)
**solo se il personaggio è fisicamente nella location del lavoro** al tick
del payday. `sim tick` / `sim run` mostrano `💰 Payday: N pagati, M assenti (keys)`.

### Salvataggi

```bash
simai save create [-n NOME]     # crea un .sav (default: timestamp)
simai save list                 # elenca
simai save load <nome> [--yes]  # carica
simai save inspect <nome>       # metadati senza caricare
simai save delete <nome> [--yes]
```

I file `.sav` finiscono in `data/saves/`. Il formato è binario con
magic, versione, header JSON, payload compresso `zlib` e checksum
`sha256`. Un file corrotto viene rifiutato al load, non caricato
silenziosamente.

### Benchmark

```bash
simai sim benchmark --years 1 --output docs/release/benchmarks/1y.json
simai sim benchmark --years 10 --output docs/release/benchmarks/10y.json
```

Crea un DB temporaneo in `data/benchmark/` (da cancellare a mano, non
sono salvataggi) e stampa mood/bisogni/balance/attendance per NPC. Il
report JSON viene salvato solo se `--output` è specificato.

Convenzione provvisoria: `1 anno = 8760 tick` (365 giorni × 24 ore).
Non è il calendario di Anthalys e non va usato per compleanni o
stagioni.

Riferimento attuale: `benchmarks/10y-1.2.1.json` (~19 minuti, 75.5
tick/s). Il 60y è un debito aperto e va eseguito su una release stabile
(vedi `known-issues.md`).

## Qualità

```bash
./scripts/check.sh --with-tests    # lint + typecheck + test veloci
uv run pytest -m slow -v           # test slow (1 anno simulato)
```

La CI esegue solo i test veloci. I test slow sono esclusi via
`addopts = "-m 'not slow'"` in `pyproject.toml`.

## Backup e ripristino

Il database SQLite è in `data/simai.db` (con `-wal` e `-shm`). I
salvataggi sono file `.sav` indipendenti in `data/saves/`.

- **Backup**: copia `data/simai.db` e `data/saves/` da qualche parte.
- **Ripristino**: ripristina i file sopra e verifica con `simai db status`.
- **Ripresa da `.sav`**: `simai save load <nome> --yes`. Il caricamento
  **sostituisce** lo stato corrente: non è un merge.
- **Migrazione fallita**: se un `db upgrade` si blocca a metà e lascia il
  DB in stato inconsistente, la mitigazione attuale è `rm data/simai.db*`
  + `db upgrade` + `world seed`. Funziona finché il DB contiene solo seed.

## Limiti noti della 1.3.0

Questa release è onesta su cosa non fa. I dettagli sono in
[`docs/release/known-issues.md`](docs/release/known-issues.md).

### Tempo e calendario

- **Il calendario è approssimativo.** `1 anno = 8760 tick` (365 giorni
  × 24 ore) è ancora una convenzione per i benchmark, non il calendario
  di Anthalys (432 giorni × 18 mesi). Non va usato per compleanni,
  stagioni o festività.
- **Nessun ciclo sonno/veglia.** Dalla 1.2.1b gli NPC tornano a casa
  dopo il turno (se `INTIMACY >= 40` e `FUN >= 40`), ma restano svegli
  e continuano a fare EAT/DRINK/PLAY. Il ciclo sonno/veglia arriverà con
  il calendario Anthalys.

### NPC e moodlet

- **LONELY resta un moodlet del player.** Gli NPC fanno SOCIALIZE prima
  che la streak scatti, quindi LONELY non scatta mai per loro. Il tratto
  SOLITARY (1.3.0) rallenta il decadimento di INTIMACY (×0.60) ma non
  impedisce il SOCIALIZE.
- **Tratti in stato A2.** In 1.3.0 i tratti sono seedati e persistiti
  (`Character.traits`), ma i modificatori non sono ancora applicati in
  `decay_value` e `score`. Test comportamentali e benchmark 10y in
  arrivo (A2).

### Economia

- **Nessuna tassazione.** Salario lordo, prezzi netti: niente IVA,
  tassazione progressiva o tassa di successione (roadmap 1.3+).
- **Nessun supporto familiare.** Erika e Max hanno wage 5 (paghetta).
  Nessun trasferimento di denaro tra personaggi, nessuna convivenza
  economica, nessun "mantenimento minori" (roadmap 1.2).
- **Nessun inventario.** Il caffè vende "un drink" astratto: paghi 2,
  ricevi +30 thirst. Non esiste merce, magazzino o "comprare una
  bottiglia e portarla a casa" (roadmap 1.2).
- **Utility non penalizza il costo.** Quando un NPC deve spostarsi per
  un bisogno, casa (gratis) e caffè (a pagamento) hanno lo stesso score:
  metà delle volte spende quando potrebbe non spendere. `COST_PENALTY` in
  `choose_intent` è rimandato (rischia di uccidere il caffè come
  location).
- **Nessun motivo per risparmiare.** L'economia non ha obiettivi a
  lungo termine (case, investimenti, pensioni): il comportamento
  ottimale è spendere tutto.

### Test e benchmark

- **Baseline 60 anni mancante.** L'ultimo 60y è su 1.1.0 (ha rivelato il
  bug del decadimento). Su 1.1.1 e successive è stato eseguito solo 10y
  (`benchmarks/10y-1.2.1.json`). Il 60y è un debito aperto: va eseguito
  su una release stabile (2.0 o prima di multiplayer) per validazione
  estesa.
- **Performance con DB > 50 MB non testata.** Il 10y produce ~15 MB e
  mostra performance stabile (75.5 tick/s, identica a 3y), ma non
  dimostra che regga a ~200k transazioni (tipico di 60y).

### Infrastruttura

- **Migrazioni SQLite non sempre reversibili.** Un `batch_alter_table`
  fallito può lasciare il DB con la colonna aggiunta ma
  `alembic_version` invariata; il successivo `db upgrade` fallisce con
  `duplicate column name`. Comando `simai db reset --yes` e test
  `upgrade → downgrade → upgrade` in CI sono in roadmap 1.3.

### UI e persistenza

- **Nessuna UI grafica.** Tutto avviene via CLI. L'interfaccia web è
  rimandata.
- **Nessuna pausa/ripresa.** Il tempo avanza solo quando invochi
  `simai sim tick` o `simai sim run`.
- **Nessuna cifratura dei salvataggi.** I file `.sav` hanno checksum
  per l'integrità, ma non sono cifrati.

## Stato del progetto

- **1.0.0** — Muse Core: percorso `avvia → simula → interagisci → salva
  → ricarica` completo, con test automatici, benchmark e CLI.
- **1.0.1** — Movimento NPC e moodlet (`ATE_WELL`, `SOCIALIZED`, `LONELY`).
- **1.1.0** — Economia minima: balance, job, transazioni, payday, costi
  per azione, filtro affordabilità.
- **1.1.1** — Fix decadimento (20.0 → 13.5/ora), filtro movimento
  inutile, player escluso dal benchmark se `include_player=False`.
- **1.2.0** — Lavoro fisico: `WorkState`, priorità lavoro, payday con
  presenza fisica.
- **1.2.1** — Fontanella e panino a piazza, routine serale
  (`home_location_id`), attendance 100% sui 4 NPC.
- **1.3.0** — Tratti (`LAZY`, `ENERGETIC`, `SOCIAL`, `SOLITARY`,
  `GLUTTON`), seed, migrazione, CLI `npc traits`. Modificatori attivi
  su decadimento, utility e movimento. 10y verde (mood 67.8–68.3,
  attendance 100%, invarianti OK). Documentazione retroattiva in
  `docs/release/1.3.0-plan.md`.
- **1.3.1** — Release documentale: piano retroattivo 1.3.0, CHANGELOG
  e README allineati al codice, limiti dei tratti in `known-issues.md`,
  nota su `check.sh --reset-data` rimandato a 1.4.
- **1.4.0** — Mercato e negozi: `ShopItem`, `MarketService`, seed
  economia, `player do` con stock/prezzo autoritativi. CI attiva.
  10y verde (`purchase_transactions 22402`). Stock infinito in 1.4.0,
  consumo reale + restock in 1.5.0.
- **1.5.0** — `NPCManager` (`npc/manager.py`): astrazione sopra il
  tick, `NPCState` in-memory, `NPCManagerLike` per test di contract.
  Comportamento invariato (10y identico a 1.4.0). 261 test verdi.
- **1.6.0** — Stock finito + restock giornaliero (`daily_tick`),
  `needs_of_many`, `available_moves` esclude stock esaurito.
  `COST_PENALTY` a 1.7.0 (richiede design, non costante). 274 test
  verdi.
- **1.7.0** — `RelationshipKind` 11 kind, `family_tree`, `kinship`,
  seed famiglia (giulia→erika, luca→max), boost `SOCIALIZE` familiare.
  Relazioni statiche senza lifecycle. 289 test verdi.

- **1.5+** — `RelationshipKind` 11 kind (A2), stock finito + restock +
  `COST_PENALTY` + inventario, `LifecycleManager`, skills, memoria,
  calendario Anthalys. Tassazione in 1.5+ **solo previa decisione
  esplicita**: non è nel perimetro 1.5.0.

## Documenti

- [`CHANGELOG.md`](CHANGELOG.md) — cosa è cambiato
- [`docs/release/known-issues.md`](docs/release/known-issues.md) — difetti noti e debiti aperti
- [`docs/release/1.0-baseline.md`](docs/release/1.0-baseline.md) — cronaca degli incrementi
- [`TODO_SimAI_1.0_Muse_Core.md`](TODO_SimAI_1.0_Muse_Core.md) — piano 1.0
- [`TODO_SimAI_ottimizzato.md`](TODO_SimAI_ottimizzato.md) — roadmap globale