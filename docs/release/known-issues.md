# SimAI 1.0.0 — Problemi noti

Questi sono difetti conosciuti e accettati per la release 1.0.0. Non sono
bug bloccanti del percorso `avvia → simula → salva → ricarica`, ma
descrivono dove il mondo è meno vivo di quanto dovrebbe.

## 1. NPC senza routine

Gli NPC si spostano quando un bisogno critico non è soddisfacibile
localmente, ma non hanno una casa né una routine. Chi si sposta al caffè
per bere ci resta finché un altro bisogno critico non lo spinge
altrove. Non esiste "torna a casa dopo".

**Roadmap 1.1:** routine (casa come punto di ancoraggio, cicli
giornalieri, lavoro).

## 2. Player statico per default

Il player non subisce decisioni automatiche nel tick. Se non invocato,
i suoi bisogni decadono fino a zero.

**Impatto:** dopo qualche ora simulata senza input, il player ha tutti i
bisogni a 0 e mood minimo.

**Roadmap 1.1:** `include_player=True` di default in `sim run`, con
opzione `--manual` per chi vuole controllarlo tick per tick.

## 3. Nessun moodlet

L’umore è solo una media pesata dei bisogni. Non ci sono eventi
temporanei (“ha litigato con un amico”, “ha vinto alla lotteria”) che
modificano l’umore indipendentemente dai bisogni.

**Roadmap 1.1:** sistema moodlet (durata, delta, sorgente) integrato
con `run_tick` e con l’eventuale memoria.

## 4. Calendario approssimativo

`TICKS_PER_YEAR = 8760` è una convenzione gregoriana (365 × 24), non il
calendario di Anthalys (432 giorni × 18 mesi). Non va usato per
calcolare compleanni, stagioni o festività.

**Roadmap 1.1:** `sim/anthalys/time/` con calendario canonico e
conversione testata.

## 5. NPC immobili (ex cooldown)

Il cooldown introdotto in 0.13b è stato **rimosso** in 0.13c: peggiorava
le metriche. Al suo posto, ogni azione richiede che il bisogno che
soddisfa sia sotto una soglia (mangi se hunger < 30, bevi se thirst < 40,
ecc.). Questo elimina la monotonia ma non risolve il problema strutturale:
chi vive in `casa` non ha `DRINK` disponibile, chi vive in `piazza` non
ha `EAT`.

**Roadmap 1.1:** movimento NPC e catalogo espanso per location.

---

**Nota:** in 1.0.1 `LONELY` è dormiente in pratica. Gli NPC si
spostano per `SOCIALIZE` prima che la streak scatti; il player ha
mood clampato a 0 quando sarebbe solo. Il moodlet esiste, contribuisce
al mood, ed è coperto da test. Diventerà visibile in 1.1 con tratti
(`SOLITARY`), soglie per azione, o intenzioni automatiche del player.

---

## 1.1.0 — Limiti dell'economia

### Lavoro fisico non simulato

Gli NPC hanno un `Job` con `location_key` e `schedule_start/end_tick`,
ma non si recano fisicamente al lavoro. Il salario viene pagato
indipendentemente da dove sono. Un NPC che dorme in piazza riceve
comunque lo stipendio.

**Roadmap 1.2:** `WorkAction` che richiede presenza fisica nella
location al tick dello stipendio, o almeno "vai al lavoro prima del
payday".

### Nessuna tassazione

Il salario è lordo, i prezzi sono netti. Non c'è IVA, non c'è
tassazione progressiva, non c'è tassa di successione.

**Roadmap 1.3+** (FASE 4 del TODO globale).

### Nessun supporto familiare

Erika e Max hanno wage 5 (paghetta). Nessun trasferimento di denaro
tra personaggi in 1.1.0. Se spendono tutto, bevono acqua gratis a casa
e sopravvivono. Non c'è "mantenimento minori".

**Roadmap 1.2:** trasferimenti familiari (`SUPPORT` transaction kind),
convivenza economica.

### Nessun inventario

Il caffè vende "un drink" astratto: paghi 2, ricevi +30 thirst. Non
esiste merce. Non esiste magazzino. Non esiste "comprare una bottiglia
e portarla a casa".

**Roadmap 1.2:** oggetti e inventario.

### Utility non penalizza il costo

Quando un NPC deve spostarsi per un bisogno, `choose_intent` confronta
casa (azione gratis) e caffè (azione a pagamento) con lo stesso score.
Risultato: metà delle volte spende quando potrebbe non spendere.

**Impatto:** studenti (paghetta 5) vivono al verde, adulti
paycheck-to-paycheck. Realistico ma non razionale.

**Roadmap 1.2:** `COST_PENALTY` in `choose_intent`. Non ora: rischia di
uccidere il caffè come location (mai visitato se gratis è sempre meglio).

### Nessun motivo per risparmiare

L'economia non ha obiettivi a lungo termine (case, investimenti,
pensioni). Il comportamento ottimale è spendere tutto.

**Roadmap 1.2+:** proprietà, mutui, investimenti. Solo allora il
risparmio diventa razionale.

---

## Debiti aperti post-1.1.1

### Test 60 anni su 1.1.1 non eseguito

Il test 60 anni è stato eseguito su 1.1.0 (ha rivelato il bug del
decadimento) ma non su 1.1.1. Il 1 anno è verde. Il 60 anni va eseguito
**prima di aprire 1.2.0** (lavoro fisico), perché il lavoro fisico
aggiunge un vincolo (presenza al payday) che può interagire con derive
non visibili su 12 mesi.

Comando:

```bash
uv run simai sim benchmark --years 60 \
  --output docs/release/benchmarks/60y-1.1.1.json \
  --sample-every 336

---

## Debito aperto 1.2.0 — 60y su 1.1.1 non eseguito

**Stato**: 1.2.0 è stata aperta senza eseguire il test 60 anni su
1.1.1. Il 1 anno è verde, il 60y su 1.1.0 ha rivelato il bug del
decadimento, ma non c'è una baseline 60y su 1.1.1.

**Rischio**: se 1.2.0 (lavoro fisico) rivela derive su 60 anni, non
sapremo distinguere "colpa del lavoro fisico" da "deriva già presente
in 1.1.1". Il debugging richiederà di eseguire 60y su 1.1.1 a
posteriori, costando il doppio.

**Mitigazione**: appena disponibile una macchina libera,
eseguire:

```bash
git checkout v1.1.1
uv run simai sim benchmark --years 60 \
  --output docs/release/benchmarks/60y-1.1.1.json \
  --sample-every 336
```

### Attendance dipende dalla location di lavoro

Chi lavora in una location senza `EAT`/`DRINK` (piazza) può perdere
il payday se la salvaguardia fame scatta durante il turno. Giulia:
80% attendance; Erika/Max (piazza ma studenti, turno corto 8-13):
95-97%; Luca (caffè, tutto disponibile): 100%.

**Impatto:** ~20% di stipendi persi per chi lavora in piazza. Il
mood non ne risente (stabile > 60) perché i soldi non mancano
(Giulia accumula 1155 Athel in 1 anno).

**Roadmap 1.2.1:** fontanella/chiosco a piazza (EAT/DRINK gratis o
a basso costo). Insieme a routine serale (tornare a casa dopo il
lavoro).

### Routine serale (1.2.1b)

Dopo il turno, gli NPC tornano a casa se hanno già soddisfatto i
bisogni sociali (`INTIMACY >= 40`, `FUN >= 40`). Se non li hanno
soddisfatti, restano dove possono socializzare (piazza, caffè).

Non c'è "sonno" né "notte" simulata: gli NPC tornano a casa e
continuano a fare azioni (EAT/DRINK/PLAY) da svegli. Il ciclo
sonno/veglia è 1.3 (con il calendario Anthalys).

### Migrazioni SQLite fallite lasciano DB inconsistenti

Se una migrazione con `batch_alter_table` fallisce a metà, SQLite può
lasciare il DB con la colonna aggiunta ma `alembic_version` invariata.
Un successivo `db upgrade` fallisce con `duplicate column name`.

**Mitigazione:** reset del DB (`rm data/simai.db*` + `db upgrade` +
`world seed`). Accettabile finché il DB contiene solo seed. Diventerà
un problema serio quando ci saranno dati utente non ricreabili.

**Roadmap 1.3:** comando `simai db reset --yes` che gestisce questo
caso. E test di migrazione `upgrade → downgrade → upgrade` in CI per
catturare migrazioni che non sono reversibili.

### 60y rimandato, 10y eseguito

Il 60y su 1.2.1 non è stato eseguito. Al suo posto, 10y
(`benchmarks/10y-1.2.1.json`, ~19 minuti, 75.5 tick/s).

**Confermato da 10y**:

- Balance lineare: giulia +3.713/anno, luca +2.657/anno,
  erika/max +691/anno. Nessuna accelerazione.
- Mood stabile (67.9–68.1 vs 68.4 a 3y).
- Attendance 100% per tutti i 4 NPC.
- Performance stabile (75.5 tick/s, identica a 3y).
- Salary deterministico (14.600 = 4 × 365 × 10).

**NON coperto da 10y**:

- Performance con DB > 50 MB (~200k transazioni, tipico di 60y).
  Il 10y produce ~15 MB e mostra performance stabile, ma non
  dimostra che regga a 50 MB.
- Derive oltre 10 anni. Non ci sono meccanismi noti che le
  causerebbero, ma non sono escluse.

**Roadmap**: 60y su una release stabile (2.0 o prima di multiplayer)
come validazione estesa. 10y ad ogni release che tocca `run_tick` o
`process_payday`.
