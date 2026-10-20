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