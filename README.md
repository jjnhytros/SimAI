# SimAI 1.9.0

SimAI è il motore di simulazione della vita di Anthalys. La 1.0 ha
dimostrato che il nucleo funziona end-to-end (`avvia → simula → interagisci
→ salva → ricarica`); le release successive hanno aggiunto movimento NPC,
moodlet, economia, lavoro fisico, tratti, mercato, `NPCManager`, famiglia
e relazioni, e il giorno Anthalys di 28 ore.

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
# Inizializza il database (applica migrazioni, incl. 0014_job_break)
simai db upgrade

# Popola il Quartiere delle Muse (idempotente)
simai world seed

# Popola i negozi (idempotente)
simai economy seed

# Vedi lo stato del tuo Sim
simai player status

# Fai avanzare la simulazione di 28 tick (1 giorno Anthalys di 28 ore)
simai sim run --ticks 28

# Il tuo Sim ha fame? Mangia.
simai player do -a eat

# Controlla economia, lavoro, tratti, famiglia
simai economy jobs
simai economy ledger -c giulia
simai npc traits -c luca
simai relationships family -c erika

# Salva, esci, riprendi
simai save create -n partita1
simai save list
simai save load partita1 --yes
```

## Comandi principali

### Mondo e stato

```bash
simai world seed                  # popola il quartiere (idempotente)
simai economy seed                # popola i negozi (idempotente)
simai world list                  # elenca location e personaggi
simai player status               # pannello completo del tuo Sim (bisogni, lavoro, tratti, balance)
simai needs show -c <key>         # bisogni e umore di un personaggio
simai relationships show -c <key> # relazioni in uscita
simai relationships family -c <key>     # genitori, figli, fratelli
simai relationships ancestors -c <key>  # BFS antenati
simai relationships descendants -c <key> # BFS discendenti
simai relationships kinship -c <key> --with <other> # r, r/2, nome
simai npc traits -c <key>         # tratti dell'NPC
simai npc stages -c <key>         # età e LifeStage

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
simai economy jobs                  # stato corrente (al lavoro / in pausa / fuori orario)
simai economy shops                 # elenca ShopItem per location con stock
simai economy restock               # riporta lo stock ai valori di seed
```

Il salario viene pagato a fine turno (`schedule_end_tick - 1`)
**solo se il personaggio è fisicamente nella location del lavoro** al
tick del payday. `sim tick` / `sim run` mostrano
`💰 Payday: N pagati, M assenti (keys)`.

Orari attuali (seed 1.7.1):

| Personaggio | Job | Orario | Pausa |
|---|---|---|---|
| player | commesso | 10-19 | — |
| luca | barista | 14-21 | — |
| giulia | insegnante | 7-18 | 14-15 |
| erika | studente | 7-18 | 14-15 |
| max | studente | 7-18 | 14-15 |

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
simai sim benchmark --years 1  --output docs/release/benchmarks/1y.json
simai sim benchmark --years 10 --output docs/release/benchmarks/10y.json
```

Crea un DB temporaneo in `data/benchmark/` (da cancellare a mano, non
sono salvataggi) e stampa mood/bisogni/balance/attendance per NPC. Il
report JSON viene salvato solo se `--output` è specificato.

Convenzione Anthalys: `1 anno = 12096 tick` (432 giorni × 28 ore).
Un `--years 1` esegue 12096 tick, non 8760. Un `--years 10` esegue
120960 tick.

Riferimento attuale: `benchmarks/10y-1.7.1.json` (120.960 tick, ~1571s,
77.0 tick/s). Il 60y è un debito aperto e va eseguito su una release
stabile (vedi `known-issues.md`).

**Nota storica**: i 10y da 1.2.1 a 1.7.0 sono a 87.600 tick
(365 × 24, convenzione gregoriana). Non sono confrontabili con i
10y da 1.7.1 in poi (120.960 tick, calendario Anthalys).

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
  + `db upgrade` + `world seed` + `economy seed`. Funziona finché il DB
  contiene solo seed.

## Limiti noti della 1.7.1

Questa release è onesta su cosa non fa. I dettagli sono in
[`docs/release/known-issues.md`](docs/release/known-issues.md).

### Tempo e calendario

- **Il calendario Anthalys è approssimativo.** `1 anno = 12096 tick`
  (432 giorni × 28 ore) è usato per i benchmark, ma non ci sono ancora
  stagioni, festività, lune o giorni della settimana modellati. Il
  calendario completo arriverà in una release successiva.
- **Nessun ciclo sonno/veglia.** Gli NPC tornano a casa dopo il turno
  (se `INTIMACY >= 40` e `FUN >= 40`), ma restano svegli e continuano a
  fare EAT/DRINK/PLAY.

### NPC, tratti, famiglia

- **LONELY resta un moodlet del player.** Gli NPC fanno SOCIALIZE prima
  che la streak scatti, quindi LONELY non scatta mai per loro.
- **Effetto dei tratti piccolo.** I tratti modificano decadimento
  (0.60–1.30), utility (0.10–0.15) e movimento (−0.10 SOLITARY), ma
  l'effetto misurato sui 10 anni è < 1 punto su `fun_mean`/`intimacy_mean`.
  Progettati per spostare la decisione solo quando due opzioni sono vicine.
- **Relazioni familiari statiche.** `RelationshipKind` 11 kind,
  `family_tree`, `kinship` esistono, ma senza `LifecycleManager` il tick
  le usa solo per il boost `SOCIALIZE` (+5). Niente matrimonio,
  gravidanza, morte, eredità. Sono dati preparati, non comportamento.
- **`relationship_name` neutro.** "genitore", "figlio/a", ecc.
  `Character.gender` non esiste. `UNCLE_AUNT_OF` e `NEPHEW_NIECE_OF`
  sono kind neutri.
- **`relationship_coefficient` limitato a grado 3.** Oltre (cugini
  secondi, prozio, ...): 0.0.
- **Turni barista scoperti.** Luca è l'unico barista (14-21). I turni
  7-14 e 21-28 non sono coperti da nessun NPC.

### Economia

- **Nessuna tassazione.** Salario lordo, prezzi netti: niente IVA,
  tassazione progressiva o tassa di successione.
- **Nessun supporto familiare.** Nessun trasferimento di denaro tra
  personaggi, nessuna convivenza economica, nessun "mantenimento minori".
- **Nessun inventario.** Il caffè vende "un drink" astratto: paghi 2,
  ricevi +30 thirst. Non esiste merce, magazzino o "comprare una
  bottiglia e portarla a casa".
- **`COST_PENALTY` rimandato.** Il costo non è un segnale utile finché
  la casa ha tutte le azioni gratis. `COST_PENALTY = 0.5` è inerte
  (`DISTANCE_PENALTY = 5.0` domina). `COST_PENALTY = 2.0` ucciderebbe
  il caffè. Richiede design (moodlet `CAFFE`, `DISTANCE_PENALTY` più
  basso, o niente). Vedi `known-issues.md` §2.5.
- **Nessun motivo per risparmiare.** L'economia non ha obiettivi a
  lungo termine (case, investimenti, pensioni).
- **Stock finito non vincolante con 4 NPC.** `SHOP_ITEM_SPECS` ha
  stock 20/20/10/15, ma con 4 NPC e restock giornaliero lo stock non
  si esaurisce mai in pratica. Diventerà vincolante con > 10 NPC o
  stock più basso.

### Test e benchmark

- **Baseline 60 anni mancante.** L'ultimo 60y è su 1.1.0. Su 1.7.1 è
  stato eseguito solo 10y (`benchmarks/10y-1.7.1.json`). Il 60y è un
  debito aperto: va eseguito su una release stabile (2.0 o prima di
  multiplayer) per validazione estesa.
- **10y non confrontabile con i precedenti.** I 10y da 1.2.1 a 1.7.0
  sono a 87.600 tick. Da 1.7.1 sono a 120.960 tick. Il baseline
  riparte da `10y-1.7.1.json`. I vecchi report restano come archivio
  storico, non come riferimento.
- **Performance con DB > 50 MB non testata.** Il 10y produce ~15–20 MB
  e mostra performance stabile (77 tick/s), ma non dimostra che regga
  a ~200k transazioni (tipico di 60y).

### Infrastruttura

- **Migrazioni SQLite non sempre reversibili.** Un `batch_alter_table`
  fallito può lasciare il DB con la colonna aggiunta ma
  `alembic_version` invariata; il successivo `db upgrade` fallisce con
  `duplicate column name`. Mitigazione: reset del DB. Comando
  `simai db reset --yes` e test `upgrade → downgrade → upgrade` in CI
  sono in roadmap.
- **`scripts/check.sh` cancella `data/` alla fine.** `set -euo pipefail`
  garantisce che il `rm -rf data/` parta solo se tutti i gate sono
  passati, ma è distruttivo e non gated da flag. Roadmap: `--reset-data`
  esplicito.

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
  `GLUTTON`), seed, migrazione, CLI `npc traits`. Modificatori su
  decadimento, utility e movimento. 10y verde.
- **1.3.1** — Release documentale: piano retroattivo 1.3.0, CHANGELOG
  e README allineati al codice, limiti dei tratti in `known-issues.md`.
- **1.4.0** — Mercato e negozi: `ShopItem`, `MarketService`, seed
  economia, `player do` con stock/prezzo autoritativi. CI attiva.
- **1.4.1** — Pulizia test e documentazione: migrations count, ROADMAP
  allineata al codice reale, README tassazione a 1.5+.
- **1.5.0** — `NPCManager` (`npc/manager.py`): astrazione sopra il tick,
  `NPCState` in-memory, `NPCManagerLike` per test di contract.
  Comportamento invariato (10y identico a 1.4.0).
- **1.6.0** — Stock finito + restock giornaliero (`daily_tick`),
  `needs_of_many`, `available_moves` esclude stock esaurito.
  `COST_PENALTY` rimandato (richiede design, non costante).
- **1.7.0** — Famiglia e relazioni: `RelationshipKind` 11 kind,
  `family_tree`, `kinship`, seed famiglia (giulia→erika, luca→max),
  boost `SOCIALIZE` familiare. Relazioni statiche senza lifecycle.
- **1.7.1** — Giorno di 28 ore (`TICKS_PER_DAY=28`,
  `TICKS_PER_YEAR=12096`), pausa pranzo (`Job.break_*`,
  `WorkState.ON_BREAK`), nuovi orari job Anthalys. 10y a 120.960 tick,
  baseline non confrontabile con i precedenti.
- **1.8.0** — `LifecycleManager`: ageing (`age_days`), morte per età
  (100+), successione (5 tier, solo `balance`), gravidanza (300gg
  Anthalys, gemelli). Morte manuale via CLI. Morte probabilistica e
  `LIFESTAGE` rimandati. 317 test verdi. 10y identico a 1.7.1
  (`death_count=0`).
- **1.9.0** — `LifeStage` (9 valori, tassonomia Anthalys 0–60+),
  `life_stage_for`, `is_pediatric`/`is_psychosocial`, CLI
  `npc stages`. Nessun effetto sul comportamento (dato derivato).
  340 test verdi. 10y identico a 1.8.0.

- **1.10+** — Morte probabilistica (richiede unità di misura),
  moodlet di transizione (`BIRTHDAY`, `PUBERTY`, `ADULTHOOD`,
  `SENIORITY`) con `moodlet_for_need` (22 mapping), `COST_PENALTY`
  (richiede design), `InventoryService`, calendario Anthalys completo (stagioni, festività, lune), supporto familiare, `db reset`.
  Tassazione in 1.8+ **solo previa decisione esplicita**. Vedi `TODO_SimAI_ottimizzato.md` per la roadmap globale.

## Documenti

- [`CHANGELOG.md`](CHANGELOG.md) — cosa è cambiato
- [`docs/release/known-issues.md`](docs/release/known-issues.md) — difetti noti e debiti aperti
- [`docs/release/1.0-baseline.md`](docs/release/1.0-baseline.md) — cronaca degli incrementi
- [`docs/release/1.5.0-plan.md`](docs/release/1.5.0-plan.md), [`1.6.0-plan.md`](docs/release/1.6.0-plan.md), [`1.7.0-plan.md`](docs/release/1.7.0-plan.md), [`1.7.1-plan.md`](docs/release/1.7.1-plan.md) — piani delle release recenti
- [`TODO_SimAI_1.0_Muse_Core.md`](TODO_SimAI_1.0_Muse_Core.md) — piano 1.0
- [`TODO_SimAI_ottimizzato.md`](TODO_SimAI_ottimizzato.md) — roadmap globale