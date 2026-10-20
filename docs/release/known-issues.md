# SimAI 1.0.0 — Problemi noti

Questi sono difetti conosciuti e accettati per la release 1.0.0. Non sono
bug bloccanti del percorso `avvia → simula → salva → ricarica`, ma
descrivono dove il mondo è meno vivo di quanto dovrebbe.

## 1. NPC immobili

Gli NPC non si spostano mai dalla loro location iniziale. Se il bisogno
critico non è soddisfacibile localmente (es. sete per chi vive in `casa`,
dove `DRINK` non è disponibile), resta a zero per sempre.

**Impatto:** Erika e Giulia hanno `thirst` a 0 in modo stabile. Il loro
mood ne risente.

**Roadmap 1.1:** azione `MOVE` e utility AI che considera anche la
soddisfacibilità altrove (movimento come effetto collaterale di una
decisione, non come azione esplicita).

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

## 5. Cooldown satura in casi limite

Con `PLAY` in `casa`, un NPC con `FUN` già alto può comunque raggiungere
100 dopo ogni esecuzione. Il cooldown attenua ma non elimina la
saturazione.

**Impatto:** limitato. Il test di bilanciamento mostra `hunger` oscillante
e non più fisso a 100.

**Roadmap 1.1:** diminishing returns (guadagno decrescente su azioni
ripetute) e soglie di utilità minima sotto le quali l’NPC salta il turno
anche senza cooldown.