# SimAI 1.0.0 — Muse Core

SimAI è il motore di simulazione della vita di Anthalys. La 1.0
dimostra che il nucleo della simulazione funziona end-to-end:
avvio, simulazione autonoma, interazione, salvataggio e ripresa.

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
simai player status               # pannello completo del tuo Sim
simai needs show -c <key>         # bisogni e umore di un personaggio
simai relationships show -c <key> # relazioni in uscita
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
```

Crea un DB temporaneo in `data/benchmark/` (da cancellare a mano, non
sono salvataggi) e stampa mood/bisogni medi, min e max per NPC. Il
report JSON viene salvato solo se `--output` è specificato.

Convenzione provvisoria: `1 anno = 8760 tick` (365 giorni × 24 ore).
Non è il calendario di Anthalys e non va usato per compleanni o
stagioni.

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

## Limiti noti della 1.0

Questa release è onesta su cosa non fa. I dettagli sono in
[`docs/release/known-issues.md`](docs/release/known-issues.md).

- **Gli NPC non si spostano.** Un NPC nato in `casa` non può bere (non
  c'è `DRINK` in casa), quindi la sua sete scende fino a 0 e ci resta.
  Il mood ne risente. In 1.1 il movimento NPC risolverà questo.
- **Il player non agisce automaticamente.** Se non invochi `simai
  player do`, i suoi bisogni decadono fino a zero e il mood crolla.
- **L'umore è una media pesata dei bisogni.** Non ci sono moodlet
  temporanei ("ha litigato con un amico").
- **Il calendario è approssimativo.** `1 anno = 8760 tick` (365 giorni
  × 24 ore) è una convenzione per i benchmark, non il calendario di
  Anthalys. Non va usato per compleanni o stagioni.
- **Nessuna UI grafica.** Tutto avviene via CLI. L'interfaccia web è
  rimandata a 1.1.
- **Nessuna pausa/ripresa.** Il tempo avanza solo quando invochi
  `simai sim tick` o `simai sim run`.
- **Nessuna cifratura dei salvataggi.** I file `.sav` hanno checksum
  per l'integrità, ma non sono cifrati.

## Stato del progetto

- **1.0.0** — Muse Core: percorso `avvia → simula → interagisci → salva
  → ricarica` completo, con test automatici, benchmark e CLI.
- **1.1** — Movimento NPC, moodlet, calendario Anthalys, UI minima.
- **1.2+** — Economia, politica, SoNet, genetica avanzata, LLM.
  Vedi `TODO_SimAI_ottimizzato.md` per la roadmap globale.

## Documenti

- [`CHANGELOG.md`](CHANGELOG.md) — cosa è cambiato
- [`docs/release/known-issues.md`](docs/release/known-issues.md) — difetti noti
- [`docs/release/1.0-baseline.md`](docs/release/1.0-baseline.md) — cronaca degli incrementi
- [`TODO_SimAI_1.0_Muse_Core.md`](TODO_SimAI_1.0_Muse_Core.md) — piano 1.0
- [`TODO_SimAI_ottimizzato.md`](TODO_SimAI_ottimizzato.md) — roadmap globale