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
