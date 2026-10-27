# SimAI — Problemi noti e debiti aperti

Questo documento raccoglie difetti noti, limiti accettati e debiti aperti tra 1.0.0 e 1.2.1. Non sono bug bloccanti del percorso `avvia → simula → salva → ricarica`, ma descrivono dove il mondo è meno vivo di quanto dovrebbe.

## 1. Problemi noti 1.0.0

### 1.1 NPC senza routine

Gli NPC si spostano quando un bisogno critico non è soddisfacibile localmente, ma non hanno una casa né una routine. Chi si sposta al caffè per bere ci resta finché un altro bisogno critico non lo spinge altrove. Non esiste "torna a casa dopo".

**Roadmap 1.1:** routine (casa come punto di ancoraggio, cicli giornalieri, lavoro).

### 1.2 Player statico per default

Il player non subisce decisioni automatiche nel tick. Se non invocato, i suoi bisogni decadono fino a zero.

**Impatto:** dopo qualche ora simulata senza input, il player ha tutti i bisogni a 0 e mood minimo.

**Roadmap 1.1:** `include_player=True` di default in `sim run`, con opzione `--manual` per chi vuole controllarlo tick per tick.

### 1.3 Nessun moodlet

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
