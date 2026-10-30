# SimAI — Problemi noti e debiti aperti

Questo documento raccoglie difetti noti, limiti accettati e debiti aperti tra 1.0.0 e 1.6.0. Non sono bug bloccanti del percorso `avvia → simula → salva → ricarica`, ma descrivono dove il mondo è meno vivo di quanto dovrebbe.

## 1. Problemi noti 1.0.0

### 1.1 NPC senza routine

Gli NPC si spostano quando un bisogno critico non è soddisfacibile localmente, ma non hanno una casa né una routine. Chi si sposta al caffè per bere ci resta finché un altro bisogno critico non lo spinge altrove. Non esiste "torna a casa dopo".

**Roadmap 1.1:** routine (casa come punto di ancoraggio, cicli giornalieri, lavoro).

### 1.2 Player statico per default

Il player non subisce decisioni automatiche nel tick. Se non invocato, i suoi bisogni decadono fino a zero.

**Impatto:** dopo qualche ora simulata senza input, il player ha tutti i bisogni a 0 e mood minimo.

**Roadmap 1.1:** `include_player=True` di default in `sim run`, con opzione `--manual` per chi vuole controllarlo tick per tick.

### 1.3 Nessun moodlet

> **Risolto in 1.0.1**: moodlet `ATE_WELL`, `SOCIALIZED`, `LONELY`.

L’umore è solo una media pesata dei bisogni. Non ci sono eventi temporanei (“ha litigato con un amico”, “ha vinto alla lotteria”) che modificano l’umore indipendentemente dai bisogni.

**Roadmap 1.1:** sistema moodlet (durata, delta, sorgente) integrato con `run_tick` e con l’eventuale memoria.

### 1.4 Calendario approssimativo

`TICKS_PER_YEAR = 8760` è una convenzione gregoriana (365 × 24), non il calendario di Anthalys (432 giorni × 18 mesi). Non va usato per calcolare compleanni, stagioni o festività.

**Roadmap 1.1:** `sim/anthalys/time/` con calendario canonico e conversione testata.

### 1.5 NPC immobili (ex cooldown)

Il cooldown introdotto in 0.13b è stato **rimosso** in 0.13c: peggiorava le metriche. Al suo posto, ogni azione richiede che il bisogno che soddisfa sia sotto una soglia (mangi se hunger < 30, bevi se thirst < 40, ecc.). Questo elimina la monotonia ma non risolve il problema strutturale: chi vive in `casa` non ha `DRINK` disponibile, chi vive in `piazza` non ha `EAT`.

**Roadmap 1.1:** movimento NPC e catalogo espanso per location.

### Nota LONELY (1.0.1)

In 1.0.1 `LONELY` è dormiente in pratica. Gli NPC si spostano per `SOCIALIZE` prima che la streak scatti; il player ha mood clampato a 0 quando sarebbe solo. Il moodlet esiste, contribuisce al mood, ed è coperto da test. Diventerà visibile in 1.1 con tratti (`SOLITARY`), soglie per azione, o intenzioni automatiche del player.

---

## 2. Limiti dell’economia (1.1.0)

### 2.1 Lavoro fisico non simulato

> **Risolto in 1.2.0**: `WorkState`, priorità lavoro, payday con
> presenza fisica.

Gli NPC hanno un `Job` con `location_key` e `schedule_start/end_tick`, ma non si recano fisicamente al lavoro. Il salario viene pagato indipendentemente da dove sono. Un NPC che dorme in piazza riceve comunque lo stipendio.

**Roadmap 1.2:** `WorkAction` che richiede presenza fisica nella location al tick dello stipendio, o almeno "vai al lavoro prima del payday".

### 2.2 Nessuna tassazione

Il salario è lordo, i prezzi sono netti. Non c’è IVA, non c’è tassazione progressiva, non c’è tassa di successione.

**Roadmap 1.3+** (FASE 4 del TODO globale).

### 2.3 Nessun supporto familiare

Erika e Max hanno wage 5 (paghetta). Nessun trasferimento di denaro tra personaggi in 1.1.0. Se spendono tutto, bevono acqua gratis a casa e sopravvivono. Non c’è "mantenimento minori".

**Roadmap 1.2:** trasferimenti familiari (`SUPPORT` transaction kind), convivenza economica.

### 2.4 Nessun inventario

Il caffè vende "un drink" astratto: paghi 2, ricevi +30 thirst. Non esiste merce. Non esiste magazzino. Non esiste "comprare una bottiglia e portarla a casa".

**Roadmap 1.2:** oggetti e inventario.

### 2.5 Utility non penalizza il costo — **rimandato a 1.7.0**

`COST_PENALTY = 0.5` previsto in 1.6.0 non funziona: `DISTANCE_PENALTY
= 5.0` rende il move già penalizzato, e `COST_PENALTY` più piccolo non
sposta la decisione. `COST_PENALTY > 1.67` farebbe scattare il move,
ma ucciderebbe il caffè (`PLAY` a 4 Athel con penalty 8 perde contro
tutto).

Il problema è strutturale: la casa ha tutte le azioni gratis, quindi
il costo non è un segnale utile finché non c'è un'alternativa che la
casa non ha. Va a 1.7.0 con un design che discuta:

- moodlet `CAFFE` (bonus mood al caffè, non a casa),
- `DISTANCE_PENALTY` più basso + accettare la chiusura del caffè,
- nessuna delle tre.

### 2.6 Nessun motivo per risparmiare

L’economia non ha obiettivi a lungo termine (case, investimenti, pensioni). Il comportamento ottimale è spendere tutto.

**Roadmap 1.2+:** proprietà, mutui, investimenti. Solo allora il risparmio diventa razionale.

---

## 3. Debiti aperti e limiti noti post-1.1.1 / 1.2.0

### 3.1 Baseline 60 anni su 1.1.1 mancante

Il test 60 anni è stato eseguito su 1.1.0 (ha rivelato il bug del decadimento) ma non su 1.1.1. Il 1 anno è verde. Il 60 anni andava eseguito **prima di aprire 1.2.0** (lavoro fisico), perché il lavoro fisico aggiunge un vincolo (presenza al payday) che può interagire con derive non visibili su 12 mesi.

**Stato:** 1.2.0 è stata aperta senza eseguire il test 60 anni su 1.1.1. Non c’è quindi una baseline 60y su 1.1.1.

**Rischio:** se 1.2.0 (lavoro fisico) rivela derive su 60 anni, non sapremo distinguere "colpa del lavoro fisico" da "deriva già presente in 1.1.1". Il debugging richiederà di eseguire 60y su 1.1.1 a posteriori, costando il doppio.

**Mitigazione:** appena disponibile una macchina libera, eseguire:

```bash
git checkout v1.1.1
uv run simai sim benchmark --years 60 \
  --output docs/release/benchmarks/60y-1.1.1.json \
  --sample-every 336
```

### 3.2 Attendance dipende dalla location di lavoro

> **Risolto in 1.2.1**: fontanella a piazza, panino 2 Athel, routine
> serale. Attendance 100% sui 4 NPC.

Chi lavora in una location senza `EAT`/`DRINK` (piazza) può perdere il payday se la salvaguardia fame scatta durante il turno. Giulia: 80% attendance; Erika/Max (piazza ma studenti, turno corto 8-13): 95-97%; Luca (caffè, tutto disponibile): 100%.

**Impatto:** ~20% di stipendi persi per chi lavora in piazza. Il mood non ne risente (stabile > 60) perché i soldi non mancano (Giulia accumula 1155 Athel in 1 anno).

**Roadmap 1.2.1:** fontanella/chiosco a piazza (EAT/DRINK gratis o a basso costo). Insieme a routine serale (tornare a casa dopo il lavoro).

### 3.3 Routine serale (1.2.1b)

Dopo il turno, gli NPC tornano a casa se hanno già soddisfatto i bisogni sociali (`INTIMACY >= 40`, `FUN >= 40`). Se non li hanno soddisfatti, restano dove possono socializzare (piazza, caffè).

Non c’è "sonno" né "notte" simulata: gli NPC tornano a casa e continuano a fare azioni (EAT/DRINK/PLAY) da svegli. Il ciclo sonno/veglia è 1.3 (con il calendario Anthalys).

### 3.4 Migrazioni SQLite fallite lasciano DB inconsistenti

Se una migrazione con `batch_alter_table` fallisce a metà, SQLite può lasciare il DB con la colonna aggiunta ma `alembic_version` invariata. Un successivo `db upgrade` fallisce con `duplicate column name`.

**Mitigazione:** reset del DB (`rm data/simai.db*` + `db upgrade` + `world seed`). Accettabile finché il DB contiene solo seed. Diventerà un problema serio quando ci saranno dati utente non ricreabili.

**Roadmap 1.3:** comando `simai db reset --yes` che gestisce questo caso. E test di migrazione `upgrade → downgrade → upgrade` in CI per catturare migrazioni che non sono reversibili.

### 3.5 60y rimandato, 10y eseguito

Il 60y su 1.2.1 non è stato eseguito. Al suo posto, 10y (`benchmarks/10y-1.2.1.json`, ~19 minuti, 75.5 tick/s).

**Confermato da 10y:**

- Balance lineare: giulia +3.713/anno, luca +2.657/anno, erika/max +691/anno. Nessuna accelerazione.
- Mood stabile (67.9–68.1 vs 68.4 a 3y).
- Attendance 100% per tutti i 4 NPC.
- Performance stabile (75.5 tick/s, identica a 3y).
- Salary deterministico (14.600 = 4 × 365 × 10).

**NON coperto da 10y:**

- Performance con DB > 50 MB (~200k transazioni, tipico di 60y). Il 10y produce ~15 MB e mostra performance stabile, ma non dimostra che regga a 50 MB.
- Derive oltre 10 anni. Non ci sono meccanismi noti che le causerebbero, ma non sono escluse.

**Roadmap:** 60y su una release stabile (2.0 o prima di multiplayer) come validazione estesa. 10y ad ogni release che tocca `run_tick` o `process_payday`.

### 3.6 LONELY resta un moodlet del player (non degli NPC)

1.2.1c ha aggiunto SOCIALIZE a casa, e i tratti (1.3.0) non cambiano questo fatto: un NPC con INTIMACY < 20 fa SOCIALIZE nella sua location corrente (tutte le location ora hanno SOCIALIZE), intimacy sale, streak si azzera. LONELY non scatta mai per gli NPC.

Il tratto SOLITARY rallenta il decadimento di INTIMACY (×0.60), ma non impedisce all’NPC di fare SOCIALIZE quando serve.

**Roadmap 1.3.1+:** perché LONELY scatti anche per gli NPC serve una location senza SOCIALIZE (es. un ufficio, una biblioteca), o una soglia di "troppo socializzato" oltre la quale l’NPC rifiuta SOCIALIZE (satolazione sociale). Entrambe sono 1.4+.

---

## 4. Tratti (1.3.0)

### 4.1 Effetto piccolo sui dati

I tratti modificano decadimento (0.60–1.30), utility (0.10–0.15) e
movimento (−0.10 SOLITARY), ma l'effetto **misurato** sui 10 anni è
piccolo:

- `fun_mean`: giulia (LAZY+GLUTTON) 79.9 vs 82+ degli altri;
- `intimacy_mean`: erika (SOLITARY) 81.3 vs 80.3–80.6 degli altri.

Le differenze sono < 1 punto. I tratti sono progettati per spostare
la decisione solo quando due opzioni sono vicine, non per dominare
l'utility. Se in futuro si vuole un effetto più visibile, va rivisto
il design (bonus più alti, o interazione fra tratti), non i numeri.

### 4.2 LAZY — ambiguità semantica

LAZY ha due effetti che spingono in direzioni opposte:

- `FUN` decade più veloce (× 1.30) → l'NPC sente prima il bisogno di
  divertirsi;
- `PLAY` ha utility +0.15 → l'NPC sceglie PLAY più spesso.

Netto: giulia ha `fun_mean` più bassa degli altri (79.9 vs 82+), ma
questo è compatibile sia con "LAZY gioca meno" (utility bonus
insufficiente a compensare il decay) sia con "LAZY gioca di più ma
il decadimento è più forte". **La semantica voluta non è documentata.**
Va chiarito con Marco prima di 1.4: se l'intenzione è "il pigro gioca
meno", il bonus va rimosso o invertito di segno.

### 4.3 LONELY resta player-only

Confermato in 1.3.0. Gli NPC hanno SOCIALIZE in tutte le location e
azzerano la streak prima che scatti. Il tratto SOLITARY rallenta
INTIMACY (× 0.60) ma non impedisce SOCIALIZE. LONELY è raggiungibile
solo dal player.

---

## 5. Igiene operativa

### 5.1 `scripts/check.sh` cancella `data/` alla fine

Lo script termina con:

```bash
unset VIRTUAL_ENV
rm -rf data/
uv run simai db upgrade
uv run simai world seed
```

`set -euo pipefail` garantisce che il `rm -rf data/` parta solo se
tutti i gate sono passati, quindi non è un bug logico. Ma è
**distruttivo, non documentato, non gated da flag**. Chi lancia
`./scripts/check.sh` a metà lavoro perde DB locale e `data/saves/`
silenziosamente.

**Roadmap 1.4**: `--reset-data` esplicito, oppure sostituire con
`simai db reset --yes` (già in roadmap §3.4). Per 1.3.1 la mitigazione
è documentare qui.

---

## 6. Mercato (1.4.0)

### 6.1 `available_moves` non considera lo stock — **risolto in 1.6.0**

`available_moves` ora accetta `offers_by_key` e non propone move
verso location con stock 0 per l'azione target. `NPCManager.update_all`
calcola `offers_by_key` una volta per tick (una query), non una per
NPC. Test in `test_reachability.py` e `test_npc_manager.py`.

### 6.2 Un solo entry point per l'acquisto

`player do -a <action>` è l'unico comando per comprare. Non esiste
`simai economy buy`. Decisione: meno superficie, meno test, e
`player do` già mostra costo e `balance_after`. Se in futuro serve
un comando "compra per un NPC", si aggiunge con un nome esplicito
(`economy buy --for <npc>`), non come alias ambiguo.

### 6.3 `ShopItem.price` vs `ActionDef.cost`

Coerenti per costruzione, garantiti da
`test_shop_item_price_matches_catalog`. Se il test viene rimosso o
indebolito, i due numeri possono divergere silenziosamente
(`filter_by_affordability` usa `cost`, `market_buy` usa `price`).

### 6.4 Stock finito non attivo in 1.4.0

`SHOP_ITEM_SPECS` ha `stock = -1` (infinito). Il campo `stock` è
implementato, testato (`test_buy_with_infinite_stock_keeps_minus_one`,
`test_buy_decrements_stock_and_balance`), ma il consumo reale non è
attivo perché non esiste ancora un `restock` da `LifecycleManager`.

1.5.0: `stock` finito (20/20/10/15), `restock_all` chiamato da
`LifecycleManager.daily_tick`, test di integrazione esaurimento +
restock.

### 6.5 Stock finito non vincolante con 4 NPC (1.6.0)

`SHOP_ITEM_SPECS` ha stock 20/20/10/15. Con 4 NPC che comprano ~6
volte al giorno complessivamente, lo stock si esaurirebbe in ~3
giorni, ma `daily_tick` fa restock ogni 24 tick (tick 0, 24, 48, ...).
Risultato: `filter_by_stock` non filtra mai nella simulazione reale.
Il 10y di 1.6.0 ha `purchase_transactions: 22402` e `balance_final`
identici a 1.5.0: lo stock finito non ha effetto osservabile.

Il meccanismo è implementato e testato
(`test_stock_exhaustion_and_restock_via_tick`), ma non vincolante
alla scala attuale. Diventerà vincolante quando:

- gli NPC saranno > 10 (più domanda), o
- lo stock scenderà sotto 10 (meno offerta), o
- il restock sarà meno frequente (es. ogni 7 giorni, non ogni giorno).

Nessuna delle tre è in 1.6.0. Va documentato, non corretto con
stock artificialmente bassi.

---

## 7. NPCManager (1.5.0)

### 7.1 `NPCState` in-memory, non persistito

`NPCState` è ricostruito da DB a ogni `NPCManager.load()`. Il save
continua a serializzare lo stato da DB (Character, Need, Job,
ShopItem, ecc.), non `NPCState`. Se `state` divergesse da DB,
`load` lo correggerebbe al tick successivo.

`_tick_one` mantiene `state.location_id` e `state.balance`
sincronizzati con il DB dopo move e acquisti. `state.needs` è
aggiornato dopo `apply_effect`. I campi non sincronizzati (`traits`,
`home_location_id`) non sono mai scritti da `_tick_one`.

### 7.2 N+1 su `needs_of` in `load`

`load` fa una query per personaggio per `needs_of`. Su 4 NPC è
~4 query in più per tick rispetto al loop inline precedente (che
caricava `needs_by_char` una volta sola per tutti i personaggi).

**Misurato (10y, seed 42)**: la stima originale ("irrilevante,
< 1ms") era sbagliata. Il N+1 costa ~11 secondi su 87600 tick
(0.9%). Non è la causa della differenza di tps tra 1.4.0 e 1.5.0:
il baseline `76.5 tps` di 1.4.0 (misura del 2026-10-25) non era
valido. Rimisurato 1.4.0 lo stesso giorno di 1.5.1:
`72.27 tps`. La differenza reale è **2.2%**, non 7.7%.

**Risolto in 1.6.0** con `needs_of_many` batch in
`needs/service.py`: `load` fa una query per i bisogni di tutti gli
NPC, non N. Guadagno misurato: +0.9% (70.6 → 71.3 tps su 10y).
Piccolo, ma chiude il N+1 e prepara il terreno per quando gli NPC
saranno più di 4.

### 7.3 Nessun LOD

`NPCManager` carica tutti gli NPC, non solo quelli vicini al
player. Nessuna distinzione `BACKGROUND`/`REDUCED`/`FULL`. LOD è
FASE 1.1, non 1.5.0.

### 7.4 Nessun `SkillSnapshot`

Il TODO §3.2b prevede `SkillSnapshot` in `NPCState`. Non c'è skill
in 1.5.0. Sarà aggiunto in 3.6a-c, quando `Skill` esisterà.

### 7.5 Nessun lifecycle

`NPCManager` gestisce solo "decisione + esecuzione". Decay, mood,
moodlet, cleanup restano in `tick.py`. `LifecycleManager` (ageing,
morte, gravidanza) non esiste ancora. Sarà FASE 3.4, dopo A2.

---

## 8. Famiglia (1.7.0)

### 8.1 Relazioni familiari statiche

Le relazioni familiari (`PARENT_OF`, `CHILD_OF`, ecc.) sono create
dal seed e lette da `family_tree`. Il tick le usa solo per il boost
`SOCIALIZE` (`strength` +5). Non ci sono decisioni basate su di
esse: niente matrimonio, gravidanza, morte, eredità.

Senza `LifecycleManager` (C), le relazioni familiari sono **dati
preparati**, non comportamento. Il 10y di 1.7.0 ha `mood_mean` e
`balance` identici a 1.6.0: A2 non cambia il comportamento
osservabile. Va detto, non nascosto.

**Roadmap C**: `LifecycleManager` (ageing, morte, gravidanza,
successione) userà `family_tree` e `kinship` per decidere chi eredita,
chi è tutore, chi si sposa. Allora le relazioni familiari avranno
effetti.

### 8.2 `relationship_name` neutro

`Character.gender` non esiste. `relationship_name` restituisce forme
neutre: "genitore" (non "madre"/"padre"), "figlio/a", "fratello/sorella",
"nonno/a", "zio/a", "nipote (di nonno)"/"nipote (di zio)", "cugino/a".

`RelationshipKind` ha `UNCLE_AUNT_OF` e `NEPHEW_NIECE_OF` (11 kind
totali, non 13) proprio per non richiedere `gender`. Aggiungerlo è
`Character.gender` + migrazione + refactor di `relationship_name`:
1.7.1+.

### 8.3 `relationship_coefficient` limitato a grado 3

`relationship_coefficient` copre grado 1 (genitore/figlio/fratello),
grado 2 (nonno/zio/nipote), grado 3 (cugino primo). Oltre: `0.0`.
BFS multi-livello in 1.8.0 se serve.

`kinship_coefficient = r/2` è convenzione semplificata (TODO §3.3).
Il coefficiente genetico vero è `r`; `r/2` è la probabilità di allele
condiviso in modelli semplificati.

### 8.4 `player status` non mostra famiglia

`PlayerStatus` è frozen con campi fissi; aggiungere `family` richiede
toccare `build_player_status`, `cmd_player.py`, e tutti i test del
pannello. Rischio sproporzionato per "una riga". `npc relationships
family -c <key>` copre l'uso. Va in C o 1.7.1.

---

## 9. Giorno di 28 ore (1.7.1)

### 9.1 Decadimento +16.7%, acquisti +11.7%

`DECAY_PER_HOUR` non è cambiato (HUNGER 4.0, THIRST 5.0, FUN 3.0,
INTIMACY 1.5). Con 28 ore/giorno, il decadimento giornaliero passa
da 324 a 378 punti (+16.7%). Gli NPC fanno più azioni, quindi più
acquisti.

**Misurato (10y, seed 42):**

- `purchase_transactions`: 22402 (1.7.0, 87600 tick) → 34665
  (1.7.1, 120960 tick). Per tick: 0.256 → 0.286 (+11.7%).
- `balance_mean` per erika: 13922 (1.7.0) → 9590 (1.7.1).
  Il calo è dovuto al consumo reale, non a un bug.
- `mood_mean`: 67.7–68.1 (1.7.0) → 67.5–68.1 (1.7.1). Stabile.

Il +11.7% è inferiore al +16.7% del decadimento perché le azioni
gratuite (casa, piazza) assorbono parte dell'aumento. Coerente.

### 9.2 Turni barista scoperti

Il seed ha un solo barista (luca, turno 14-21). I turni "barista 1"
(7-14) e "barista 3" (21-28) restano scoperti. Il mondo non ha 3
baristi, non c'è modo di coprirli senza aggiungere 2 NPC.

**Roadmap 1.8.0+**: 2 NPC baristi in più (7 NPC totali) o sistema
di turni condivisi. Fuori scope 1.7.1.

### 9.3 Pausa 14-15 e attendance

Con `WorkState.ON_BREAK` (14-15 per giulia/erika/max), l'NPC è
libero di lasciare la location. Se al tick 17 (`schedule_end_tick - 1`) non è in location, non viene pagato.

**Misurato:** `job_attendance_rate: 1.0` per tutti i 4 NPC su
120960 tick. La pausa non ha ridotto l'attenzione. `PRIORITY_WINDOW = 2` è sufficiente per far rientrare l'NPC in tempo.

### 9.4 Baseline non confrontabile

I 10y da 1.2.1 a 1.7.0 sono a 87.600 tick (365 × 24). Il nuovo
10y è 120.960 tick (432 × 28). **Non confrontabili.** Il baseline
riparte da `10y-1.7.1.json`. I 10y precedenti restano come
archivio storico, non come riferimento.

### 9.5 `TICKS_PER_YEAR` non è più 8760

`sim/benchmark.py` ha `TICKS_PER_YEAR = 12096` (28 × 432), non
8760. Il comando `simai sim benchmark --years N` esegue `N × 12096`
tick. Un `--years 1` fa 12096 tick, non 8760.

---

## 10. Lifecycle (1.8.0)

### 10.1 Morte probabilistica non implementata

Il TODO §3.4 prevede `DeathService` con "mortalità baseline `1e-5`,
rampa cubica, max 1/30 a `exp_max`". **Non è implementata.** Serve
un'unità di misura (per tick? per anno? per giorno?) che il TODO non
specifica. Le tre interpretazioni plausibili danno risultati
incompatibili (morte in 200 tick, in 200 anni, in 100.000 anni).

In 1.8.0: solo morte per età (`age_years >= 100`) e morte manuale
(`kill()`). **1.9.0+**: morte probabilistica, con unità definita e
`exp_max` calibrato.

### 10.2 `DeathCause` 4 inutilizzati

`DeathCause` ha 6 valori: `OLD_AGE`, `ILLNESS`, `ACCIDENT`, `VIOLENCE`,
`UNKNOWN`, `MANUAL`. In 1.8.0 solo `OLD_AGE` (automatico) e `MANUAL`
(CLI) sono generati. Gli altri 4 esistono per il futuro, mai generati.
Documentato, non nascosto.

### 10.3 `LIFESTAGE` assente

Nessuna transizione pediatrica/psicosociale. `AgingService` fa solo
`age_days += 1` e `age_years += 1` a 432 giorni. Nessun moodlet di
compleanno, nessuna soglia (`MINOR`, `ADULT`, `SENIOR`). 1.9.0+.

### 10.4 Gravidanza senza sesso modellato

`conceive()` non valida il sesso: `Character.gender` non esiste.
Qualsiasi coppia adulta può concepire. Documentato. `gender` in
1.9.0+ (con migrazione).

### 10.5 Gemelli identici vs fraterni

`roll_twins()` ritorna `(n, identical)` con 1.5% identici e 30%
fraterni. Ma senza genetica, `traits=[]` per tutti i nuovi nati.
La distinzione è calcolata ma non osservabile. Diventerà visibile
quando ci sarà ereditarietà dei tratti.

### 10.6 `death_cause` campo inutilizzato

`Character.death_cause` (String(16), nullable) esiste in migrazione
`5200_04` ma non è usato: `kill()` **rimuove** il `Character`, non
lo marca come morto. Il campo è per il futuro (`is_alive` flag +
storia). Se in 1.9.0+ si passa a `is_alive`, va usato.

### 10.7 Nessuna `Transaction` per nascita

Il parto non registra una `Transaction`. Solo la successione ne
registra una (`OTHER`, `note="succession"`). Se serve tracciare le
nascite, va aggiunto in 1.9.0+.

### 10.8 Ritardo parto

`LifecycleManager.daily_tick` gira a tick 28, 56, ... Una gravidanza
con `due_at_tick=100` viene consegnata a tick 112, non 100. Ritardo
max 27 tick. `due_at_tick <= tick_index` recupera le gravidanze
scadute, non si perdono.

---

## 11. LIFESTAGE (1.9.0)

### 11.1 `LifeStagePediatric`/`LifeStagePsychosocial` come predicati

Il TODO §3.0 elenca `LifeStagePediatric` e `LifeStagePsychosocial`
come due classi/enum. **Non sono enum separate in 1.9.0.** La
tassonomia Anthalys è una sequenza (0–6, 6–12, 12–15, 15–20, 20–25,
25–40, 40–50, 50–60, 60+), non due assi paralleli.

`LifeStage` è una enum unica con 9 valori. I due concetti del TODO
sono diventati predicati: `is_pediatric(stage)` (True per 0–20) e
`is_psychosocial(stage)` (True per 20+). Se in futuro servono due
assi indipendenti (es. sviluppo cognitivo e sviluppo sociale
separati), si aggiungono enum separate. Per ora, la sequenza è
sufficiente.

### 11.2 `LifeStageService` assente

`life_stage_for(age_years)` è una funzione pura: nessuno stato da
salvare, nessuna transizione da gestire. Un `LifeStageService` con
`on_transition` sarebbe un wrapper vuoto. Se in 1.10.0+ serviranno
effetti (moodlet di compleanno, `PUBERTY`, `ADULTHOOD`,
`SENIORITY`), allora il servizio avrà senso.

### 11.3 Nessun effetto sul comportamento

`LifeStage` è **derivato** da `age_years`, non persistito, non letto
dal tick. `erika`/`max` (14) continuano a lavorare come studenti,
`giulia` (37) e `luca` (42) come adulti. Nessun divieto di lavoro
per minori o anziani. Il 10y di 1.9.0 è identico a 1.8.0.

### 11.4 `moodlet_for_need` (22 mapping) rimandato

TODO §3.0508 elenca `moodlet_for_need` (22 mapping need→state→
moodlet). Non implementato. Necessario per moodlet di transizione
complessi. 1.10.0+.

### 11.5 Moodlet di transizione rimandati

`BIRTHDAY`, `PUBERTY`, `ADULTHOOD`, `SENIORITY`: nessun moodlet.
Il compleanno incrementa `age_years` (1.8.0) ma non genera moodlet.
Se in 1.10.0+ i moodlet di transizione serviranno, richiedono
`moodlet_for_need` (11.4).

### 11.6 Confine all'anno

`life_stage_for(age_years)` ignora `age_days`. `erika` a 14 anni
e 431 giorni è `EARLY_ADOLESCENCE`, non `LATE_ADOLESCENCE`. Il
confine è all'anno. Documentato. Se in futuro serve il confine
esatto al giorno, `life_stage_for` accetta `age_years` e `age_days`.

### 11.7 `LifeStage` in `PlayerStatus` assente

`player status` non mostra `LifeStage`. `PlayerStatus` è frozen con
campi fissi; aggiungere `life_stage` richiede toccare
`build_player_status`, `cmd_player.py`, e i test del pannello.
`npc stages -c <key>` copre l'uso. Va in 1.10.0+ se serve.

---

## 12. Moodlet stato-dipendenti e ottimizzazione (0.1100 → 0.1101)

### 12.1 Doppio conteggio mood (0.1100, corretto in 0.1101)

In 0.1100 i moodlet stato-dipendenti avevano Δ positivi in linea con
la base pesata (+2/+3/+4/+5). Risultato: `mood_mean` 10y passa da
67.85 a 80.73 (+12.88). I need contribuiscono **due volte** al mood:
una nella media pesata (`MOOD_WEIGHTS`), una nei moodlet attivi.

In 0.1101 (B3) i 13 Δ positivi scendono a **+0.5**. I 6 Δ negativi
(`STARVING`, `HUNGRY`, `DEHYDRATED`, `THIRSTY`, `MISERABLE`, `BORED`)
restano invariati: sono segnali di stato critico, non premi.

**Conseguenza**: i moodlet need-based non sono più "varietà di umore"
ma "allarme + rifinitura". Il mood torna in 67.5–70.5 sul 10y.

### 12.2 Performance −5.42% in 0.1100 (ottimizzato in 0.1101)

`refresh_need_moodlets` in 0.1100 faceva:

- 5 SELECT/tick (uno per char) — 604.800 query su 10y
- DELETE+INSERT per transizione (~240k su 10y → 480k scritture)

`tps` 10y: 71.44 → 67.57 (−5.42%).

In 0.1101:

- `refresh_need_moodlets_many`: 1 SELECT per tutti i char, UPDATE
  invece di DELETE+INSERT (grazie a `Moodlet.need`)
- `update_mood(needs=...)`: salta la query interna
- `needs_of_many`: una query per i bisogni di tutti i char

**Misurato (rerun 1y, stesso giorno)**:

- 0.1110 = 148.0s CPU (71.8 tps)
- 0.1101 = 155.4s CPU (70.1 tps)

0.1110 usa **−4.8% CPU** rispetto a 0.1101. Il `79.7` tps del
`10y-0.1101.json` era anomalo (vedi §13.5). La baseline vera è
**~70 tps**, non 79.7.

### 12.3 Breaking change `.sav` (0.1101)

`Moodlet.need` è una colonna nuova. La migrazione `0015` cambia lo
`schema_revision` da `5200_04` a `0015`. `load_save` rifiuta i `.sav`
con schema diverso:

```python
if header.schema_revision != current_rev:
    raise SaveFormatError(...)
```

**Conseguenza**: i `.sav` creati con 0.1100 **non caricano** in
0.1101+. Non c'è backfill: il progetto è pre-1.0, i `.sav` sono
usa-e-getta. Se servisse, si aggiunge un lettore che tollera
`schema_revision="5200_04"` e mappa `need=None`.

**Mitigazione**: ricreare i save dopo 0.1101. Documentato in
CHANGELOG 0.1101.

### 12.4 `Moodlet.need` nullable, non indice

Colonna `String(16)` nullable, `SAEnum(native_enum=False)`.

- Moodlet need-based: `need = <kind>`
- `ATE_WELL`, `SOCIALIZED`, `LONELY`, `BECAME_*`: `need = None`

Non c'è indice dedicato: le query batch filtrano per `character_id`
(indice esistente da `0009`) e `expires_at_tick > tick`.

Se `EXPLAIN QUERY PLAN` in 0.1102 mostrasse un full scan su
`moodlets` in `refresh_need_moodlets_many`, si aggiunge
`ix_moodlets_need` o `ix_moodlets_character_expires`.

### 12.5 `TICKS_PER_YEAR` duplicato (risolto in 0.1100)

`sim/benchmark.py` ridefiniva `TICKS_PER_YEAR = 12096`. Ora importa
da `economy/calendar.py`, che è la fonte canonica:

```python
TICKS_PER_DAY = 28
DAYS_PER_YEAR = 432
TICKS_PER_YEAR = TICKS_PER_DAY * DAYS_PER_YEAR  # 12096
```

`npc/lifecycle.py` ha ancora `AGE_DAYS_PER_YEAR = 432` in locale.
Stesso valore, ma **due fonti**. Da unificare in una release
documentale (0.1120+): importare `DAYS_PER_YEAR` da `economy/calendar.py`.

---

## 13. Divieto lavoro pediatrico (0.1110)

### 13.1 Divieto "soft", non "hard"

`can_work(job, age_years)` ritorna False per pediatrici (0–20) con
job non-`STUDENTE`. Il `Job` **resta in DB**: non viene cancellato,
non viene riassegnato. Al compleanno che porta `age_years` a 20,
`is_pediatric(life_stage_for(20))` diventa False e il divieto si
revoca automaticamente al tick successivo.

**Conseguenza**: chi è pediatrico non-STUDENTE non si muove verso
il lavoro (`should_prioritize_work` False) e non viene pagato
(`process_payday` salta). Non finisce in `absent_keys`: non è
assente, è sospeso. Il `PaydayReport` non lo conta.

Se in futuro serve distinguere "sospeso" da "assente" in
`PaydayReport`, va aggiunto un campo. Non ora: nessun NPC del seed
è pediatrico non-STUDENTE, quindi il caso non è osservabile in
produzione.

### 13.2 `STUDENTE` esente

`JobTitle.STUDENTE` (wage 5, Erika/Max) è esente dal divieto. La
motivazione è semantica: la paghetta non è salario. Il divieto
protegge i minori dal lavoro, non toglie la paghetta.

Se in futuro il design vorrà che gli studenti non ricevano la
paghetta, sarà una release dedicata (e il 10y cambierà su
`balance`/`purchase`/`salary`). Non in 0.1110.

### 13.3 `SENIORITY` non coperto

Il TODO §3.4 parla di "divieti lavoro per minori/anziani". 0.1110
copre solo i minori. Nessun NPC del seed ha 60+ (`SENIORITY`):
Erika/Max 14, Player 30, Giulia 37, Luca 42. Il divieto per
anziani non è implementato, non è testato, non è esercitato.
Va in una release futura, quando ci sarà un NPC anziano o quando
l'ageing del 10y produrrà qualcuno a 60+ (con morte a 100 e
seed attuale, 10y non basta: nessuno invecchia di 60 anni).

### 13.4 Firma breaking di `should_prioritize_work`

`should_prioritize_work` ora richiede `*, age_years: int`. I
chiamanti sono: `npc/manager.py` (uno), e i test in `test_work.py`,
`test_routine.py`, `test_jobs.py` (da verificare). MyPy strict
segnala ogni chiamata senza `age_years`. Nei test esistenti va
aggiunto `age_years=30` (adulto), **non** cambiato il codice.

### 13.5 Baseline tps anomala in `10y-0.1101.json`

Il `10y-0.1101.json` riporta `tps: 79.7` (1517.9s wall). Il rerun
1y dello stesso commit (0.1101) dà 70.1 tps (155.4s CPU, 173.3s
wall). Il `10y-0.1110.json` dà 69.8 tps (148.0s CPU, 169.3s wall
su 1y), coerente col proprio 1y (71.8).

**Conclusione**: il `79.7` del 10y di 0.1101 era anomalo, non
riproducibile. Il tps vero è ~70 per 0.1101 e 0.1110. La differenza
di CPU tra le due release su 1y è −4.8% per 0.1110 (148.0s vs
155.4s), compatibile con rumore di misurazione.

**Causa probabile**: condizioni macchina diverse (carico, cache DB,
throttling termico). Non investigata.

**Regola operativa**: d'ora in poi, ogni benchmark che "batte il
target" va verificato con CPU time (`user` + `sys`) e, se
possibile, con un rerun 1y dello stesso commit. Un `tps` assoluto
senza CPU time e senza baseline stesso-giorno non è un dato
(lezione #1 della lista errori).

---

## 14. Morte probabilistica (0.1120)

### 14.1 Unità di misura: per anno

Il TODO §3.4 dice "mortalità baseline 1e-5, rampa cubica, max 1/30 a
`exp_max`". L'unità di misura non era specificata. 0.1120 la
definisce: **per anno**.

Formula: `p_anno(x) = 1e-5 + (1/30 - 1e-5) * (min(x,100)/100)^3`.

`p_anno` a età tipiche: 14y → 0.01%, 30y → 0.09%, 42y → 0.25%,
60y → 0.72%, 80y → 1.7%, 99y → 3.2%. `p_giorno = 1 - (1-p_anno)^(1/432)`.

Se in futuro servisse una mortalità più alta (es. per un mondo con
guerre o pestilenze), la costante `MORTALITY_BASE` va alzata, non
l'unità cambiata.

### 14.2 Coesiste con OLD_AGE

`check_age` (deterministico, età >= 100) e `check_probabilistic`
(probabilistico, età < 100) sono chiamati in sequenza in
`LifecycleManager.daily_tick`. Chi ha 100+ anni muore di OLD_AGE
certo; chi ha < 100 rischia ILLNESS/ACCIDENT/VIOLENCE con p_anno.
Nessuna sovrapposizione, nessun doppio conteggio.

`check_probabilistic` salta esplicitamente `age_years >= EXP_MAX_YEARS`
(100), ridondante con `check_age` ma difensivo: se in futuro
`check_age` cambia soglia, `check_probabilistic` non uccide due volte.

### 14.3 Gravidanza e morte

In 0.1120 `kill()` cancella esplicitamente le gravidanze in cui il
morente è madre (`character_id`) e azzera `partner_id` in quelle in
cui è padre. SQLite non enforce `ondelete=CASCADE` di default, quindi
la cancellazione esplicita + `session.flush()` prima di
`session.delete(char)` è necessaria per evitare errori di FK.

**Semantica**: madre morente → figlio non nasce (gravidanza cancellata).
Padre morente → figlio nasce senza padre (`partner_id = None`).

Se in futuro si vorrà che il figlio nasca comunque (parto postumo),
va cambiato il design: `Pregnancy` con `character_id` nullable e stato
`ORPHANED`. Non in 0.1120.

### 14.4 RNG deterministico

`f"simai:death:{master_seed}:{char.id}:{tick_index}"`. Isolato da
altri RNG (moodlet, utility, gravidanza). Stesso seed + stesso char +
stesso tick → stesso esito, sempre. Test
`test_check_probabilistic_deterministic` copre.

Se in futuro `master_seed` cambia durante il run (non succede oggi,
`SimState.master_seed` è fisso), il determinismo si rompe. Non
gestito.

### 14.5 10y non esercita la feature

Con età 14–42 e seed 42, `death_count: 0` sul 10y. La feature è
inerte sul seed attuale. Diventa significativa:

- sul 60y (luca arriverebbe a 102, giulia a 97, erika/max a 74,
  player a 90 — con p_anno cumulata ~25-40% per luca/giulia),
- su scenari con NPC anziani (test dedicato),
- quando l'ageing produrrà NPC 60+ in run lunghe.

`death_count` non è nel `BenchmarkReport`: verifica implicita
(character assente dal report = morto). Da aggiungere in 0.1130.

---

## 15. `death_count` nel benchmark (0.1130)

### 15.1 `death_count` in `BenchmarkReport`

Aggiunto in 0.1130. Conta le morti cumulate nel run. È la somma di
`TickReport.deaths` su tutti i tick, dove `deaths` è `len(kills)`
da `LifecycleManager.daily_tick` (OLD_AGE + probabilistiche).

`format_report` lo stampa come `Morti: N`.

### 15.2 `TickReport.deaths` default 0

`deaths: int = 0` in `TickReport`. I test che costruiscono
`TickReport` senza `deaths` continuano a funzionare. I chiamanti
reali (`run_tick`) lo popolano.

### 15.3 1y non esercita la morte

Con età 14–42 e seed 42, `death_count: 0` sul 1y. La feature è
inerte sul seed attuale. Diventa significativa sul 60y o su scenari
con NPC anziani.

### 15.4 60y rimandato

Il 60y su 0.1150 non è stato eseguito. Con 725.760 tick (432 × 28 ×
60) e `tps` ~70, costa ~3h di CPU. Incompatibile con lo sviluppo
attivo.

**Decisione**: rimandato appena prima di 0.2000, quando il codice
si ferma per una milestone. Non è una release: è validazione.
Archivia `60y-0.2000.json` (o la versione al momento del run).

**Atteso** (con seed 42 e stato 0.1150):

- `death_count`: 1–3. Luca a 102 (OLD_AGE certo), giulia a 97
  (~25% cumulata), player a 90 (~15%), erika/max a 74 (~3–5%).
- Eredità visibile: max eredita da luca (CHILD_OF), erika da
  giulia (CHILD_OF). `balance_final` con salti.
- Skill a 100 per tutti entro i primi 20 anni.
- `mood_mean` stabile in 67.5–70.5.
- `purchase_transactions` ~208k (3467/anno × 60).

**Se il 60y mostra `death_count` fuori da 1–3**: la calibrazione
morte (0.1120) va rivista prima di 0.2000. Se mostra `death_count:
0`: bug (luca a 102 deve morire). Se 5+: formula troppo
aggressiva.

**Nota**: il 60y non è mai stato eseguito con skill dinamiche
(0.1150). L'unico 60y esistente è su 1.1.0, 525.600 tick (365 ×
24, calendario gregoriano). Non confrontabile.

---

## 16. Skills base (0.1140)

### 16.1 Skill dinamiche (training durante WORKING, 0.1150)

Da 0.1150 le skill crescono durante `WorkState.WORKING` (se l'NPC
è nella `job.location_key`): `+0.001/tick`, lineare, cap a 100.
Nessuna azione dedicata: il training è effetto collaterale del
lavorare.

**Misurato (10y, seed 42)**:

- luca: 40 → 70.24 (7 ore/giorno × 4320 giorni, 0.001/tick)
- giulia: 50 → 93.2 (10 ore/giorno, pausa 14-15 esclusa)
- erika/max: 15 → 58.2 (10 ore/giorno, pausa 14-15 esclusa)

In 60 anni tutti cappano a 100 entro i primi 20 anni. In 10y le
differenze sono visibili e il salario scala di conseguenza.

**Non c'è ancora** training esplicito (`STUDY`, `PRACTICE_*`),
skill decay, o promozioni. Quelli sono 0.1160+.

### 16.2 Mapping `JobTitle` → `SkillKind`

Oggi 1:1 (`BARISTA` → `BARISTA`, ecc.), implementato da
`_skill_for(job)` in `payday.py`. Se in futuro un job richiederà
più skill (es. `CUOCO` che richiede `COOKING` e `BARISTA`), va
cambiato il design: `SkillRequirement` con peso, o `Job.skills`
JSON.

### 16.3 Nessuna penalità per skill basse

Il salario base è il **minimo**: skill 0 → salario base, skill 100 →
+50%. Un NPC senza skill prende comunque il salario pieno. Se in
futuro si vorrà una penalità (es. skill 0 → -20%), va cambiato
`wage_with_skill`.

### 16.4 `SkillKind` e `JobTitle` separati

Duplicazione intenzionale: i due enum hanno gli stessi valori oggi,
ma concettualmente diversi. `JobTitle` è il ruolo (chi sei),
`SkillKind` è la competenza (cosa sai fare). In futuro:
`JobTitle.CUOCO` con skill `COOKING`, o `JobTitle.ARTISTA` con
skill `PAINTING`.

### 16.5 Check constraint su SQLite

`CHECK (level >= 0 AND level <= 100)` è enforced nativamente da
SQLite (non è una FK). Test `test_skill_check_constraint` copre.
Se in futuro si passa a PostgreSQL, il comportamento è identico.


---

## 17. IntimacyService (0.1160)

### 17.1 `intimacy_level` derivato, non persistito

`intimacy_level` è calcolato da `Relationship.strength`. Non è una
colonna. Se in futuro serve persistere il livello (es. per
`Relationship.intimacy_level` in una migrazione, per query più
rapide o per snapshot), va aggiunto. Oggi non serve.

### 17.2 `best_intimacy_level` out+in

`best_intimacy_level` considera relazioni in uscita e in entrata.
Il seed è simmetrico, quindi oggi out basta. Se in futuro ci
saranno relazioni unidirezionali (es. amore non corrisposto), la
definizione "il mio miglior legame, da qualunque parte" è più
corretta di "solo out".

Costo: 2 SELECT per char per tick (out + in). Su 5 char, 10
query/tick. Accettabile. Se diventa un collo di bottiglia
(>10 NPC, 60y), ottimizzare con `UNION`.

### 17.3 Moodlet `ROMANTIC`/`DEVOTED` continui

Se `best_intimacy_level >= 4`, `apply_intimacy_moodlets` chiama
`apply_moodlet` ogni tick. Con `duration=2`, il moodlet è sempre
attivo finché il livello resta >= 4. Il delta (+0.5/+1.0) è
sostenuto, non one-shot.

**Conseguenza**: `mood_mean` è gonfiato di +0.5/+1.0 per chi ha
legami forti. Range atteso 69–72. Se sale oltre, i delta vanno
ridotti (0.1170).

### 17.4 Nessun boost SOCIALIZE scalato

`boost_social_relationship` dà +5 fisso per SOCIALIZE,
indipendentemente dal livello. Non scalare: creerebbe feedback
loop (strength → level → boost → strength) con convergenza a 100
in pochi anni, rendendo tutti `DEVOTED` e il moodlet inutile.

Se in futuro si vorrà un boost scalato, va progettato con cura:
es. boost = 5 * (1 - strength/100), così strength converge
asintoticamente a 100 senza saturare subito.

### 17.5 `ROMANTIC`/`DEVOTED` non sono need-based

Hanno `need=None` in `Moodlet`. `refresh_need_moodlets_many` li
ignora (filtra `need.isnot(None)`). Sono gestiti da
`apply_intimacy_moodlets` in `tick.py`.

### 17.6 CLI `relationships intimacy`

Mostra solo relazioni in uscita. Per out+in, oggi non c'è un
comando. Se serve, `npc intimacy -c <key>` in 0.1170+.

### 17.7 tps −12.8% (0.1160)

`apply_intimacy_moodlets_many` costa ~3 query/tick + ~2.5
scritture/tick. Su 1y: +21s (170s → 191s, tps 72.6 → 63.3). Su
10y pre-batch: 58.6 tps.

Il batch ha recuperato parzialmente (58.6 → 63.3 su 1y). Il residuo
è `active_delta` (5 query/tick in `update_mood`) e `cleanup_expired`
(5 DELETE/tick). Ottimizzabili in 0.1170 con `active_delta_many` e
`cleanup_expired_many`.

**Non è una regressione**: è il costo della feature, documentato e
bounded.
