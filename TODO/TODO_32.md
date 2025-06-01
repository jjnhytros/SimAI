## XXXII. IL TEMPO IN ANTHALYS: Calendario, Cicli Stagionali, Eventi Cosmici e Festività `[]`

*Questa sezione centralizza tutte le meccaniche relative alla misurazione del tempo, al calendario ufficiale di Anthalys, all'alternarsi delle stagioni, agli eventi astronomici rilevanti e alla gestione delle festività, che influenzano profondamente la vita degli NPC e le dinamiche del mondo di gioco.*

* `[]` **1. Ciclo Giorno/Notte e Struttura Temporale di Base:**
    * `[]` a. Implementare ciclo giorno/notte di 28 ore terrestri standard (come definito nella Costituzione di Anthalys, `Art. 3`).
    * `[]` b. Suddivisione della giornata in fasi riconoscibili: Alba, Mattina, Mezzogiorno, Pomeriggio, Sera, Notte, Notte Profonda (con orari indicativi e impatto sulla luce ambientale e sulla routine degli NPC `IV.4.a`).
* `[]` **2. Scala del Tempo e Gestione della Velocità di Gioco:**
    * `[]` a. Definire la scala temporale standard della simulazione (es. 1 minuto di tempo reale = X minuti di tempo di gioco) per bilanciare il realismo con la giocabilità.
    * `[]` b. Implementare controlli per il giocatore per accelerare, rallentare, o mettere in pausa il tempo di gioco (interfaccia utente definita in `XI.2.c.i`).
* `[]` **3. Calendario Ufficiale di Anthalys: Anni, Mesi, Settimane e Giorni:**
    * `[]` a. Struttura dell'Anno di Anthalys: 18 mesi, ogni mese composto da 24 giorni (per un totale di 432 giorni all'anno, come da `Art. 3` della Costituzione e `VI.6.b`).
    * `[]` b. Nomi dei Giorni della Settimana e dei Mesi:
        * `[]` i. Definire i nomi ufficiali dei 7 giorni della settimana di Anthalys (come da `Art. 3` Costituzione).
        * `[]` ii. Definire i nomi ufficiali e il lore per ciascuno dei 18 mesi dell'anno di Anthalys.
    * `[]` c. Sistema per calcolare e visualizzare la data completa corrente: Giorno della settimana, Giorno del mese (1-24), Mese (1-18), Anno (a partire dall'Anno di Fondazione 5775, `VI.1.c`).
* `[]` **4. Calcolo Età, Compleanni ed Eventi Anniversari:**
    * `[]` a. Calcolo preciso dell'età degli NPC in anni di Anthalys, basato sulla loro data di nascita e sulla data corrente.
    * `[]` b. Gli NPC hanno una data di nascita specifica; i compleanni sono eventi annuali (`ANNUAL_BIRTHDAY_EVENT` `XIV.b`) che possono essere celebrati (astrattamente o con interazioni specifiche) e influenzare l'umore (`IV.4.i`).
    * `[]` c. (Avanzato) Anniversari significativi (es. matrimonio `IV.2.c`, data di assunzione in un lavoro importante, data di fondazione di un'azienda NPC `VIII.1.k`) possono essere tracciati e generare moodlet, interazioni speciali, o riflessioni per gli NPC.

* `[]` **5. Calendario delle Festività e Tradizioni Culturali di Anthalys:** `[PUNTO AMPLIATO]`
    * `[]` a. **Sistema di Gestione delle Festività:**
        * `[]` i. Meccanismo centrale per registrare e gestire tutte le festività (nome, tipo [fissa/mobile], data/regola di calcolo, lore, impatti di base).
        * `[]` ii. Integrazione con `TimeManager` (`XXXII.8`) per identificare correttamente i giorni festivi e attivare gli effetti associati.
        * `[]` iii. Impatto automatico di base delle festività riconosciute: giorno non lavorativo per la maggior parte delle carriere (`VIII.1.b`, `XXII.1.e`), chiusura scuole (`V.1.d`), potenziale chiusura o orari ridotti per alcuni negozi/servizi (impatto su `XVIII.5.h` e `VIII.6`).
    * `[]` b. **Festività Fisse di Anthalys:**
        * `[]` i. **Struttura Dettagliata per Ogni Festività Fissa:** *(Da replicare per ogni festività elencata sotto)*
            * `[]` 1. **Nome Ufficiale** (ed eventuali nomi popolari).
            * `[]` 2. **Data Esatta** nel calendario di Anthalys (Giorno/Mese).
            * `[]` 3. **Origine, Storia e Significato (Lore):** Contesto culturale, storico o mitologico della festività. (Collegamento generale a `XX. ATTEGGIAMENTI CULTURALI/FAMILIARI E SVILUPPO`).
            * `[]` 4. **Tradizioni Culturali Generali e Pubbliche:** Usanze comuni osservate dalla popolazione in generale, simboli ufficiali, decorazioni urbane (`XXV.2`), eventi pubblici organizzati (parate, discorsi, mercati speciali `XIII.5.a`). (Collegamento a `XX. ATTEGGIAMENTI CULTURALI`).
            * `[]` 5. **Attività Tipiche degli NPC:** Azioni specifiche che gli NPC sono più propensi a compiere durante la festività (es. `PARTECIPA_A_PARATA_FESTIVA`, `VISITA_PARENTI_PER_FESTA`, `PREPARA_CIBO_TRADIZIONALE_FESTIVO`, `SCAMBIA_DONI_FESTIVI`, `ACCENDI_LANTERNE_RITUALI`). (Richiede definizione di nuove `ActionType` in `X.9` o `VII.1`).
            * `[]` 6. **Cibi e Bevande Tradizionali:** Elenco di ricette o prodotti alimentari specifici (`C.9.d`) associati alla festività, che gli NPC potrebbero preparare (`X.5`) o acquistare.
            * `[]` 7. **Oggetti Specifici della Festività:** Decorazioni domestiche, abbigliamento tradizionale/cerimoniale, regali tipici, strumenti rituali (nuovi oggetti in `XVIII.1` e `II.2.e`).
            * `[]` 8. **Impatto Emotivo e Moodlet Specifici:** Moodlet (`IV.4.i`) caratteristici associati alla festività (es. "Euforia Festiva", "Nostalgia delle Feste", "Stress da Preparativi").
            * `[]` 9. **Impatto Economico:** Variazioni nella spesa dei consumatori (aumento acquisti per certi beni, riduzione per altri), impatto su specifici settori commerciali (`VIII.2.a`).
            * `[]` 10. **Tradizioni Familiari Specifiche:** Come le singole famiglie NPC (`IV.2.f`) personalizzano o interpretano le tradizioni generali, creando i propri rituali e memorie familiari. (Collegamento diretto a `XXVIII.d. Tradizioni Familiari, Eredità e Rituali Quotidiani`).
        * `[]` ii. **Elenco Festività Fisse (Esempi da Dettagliare con la struttura sopra):**
            * `[]` 1. **Giorno della Fondazione di Anthalys (1° Giorno del 1° Mese):** *(Già in `I.3.e.1`)* Cerimonie ufficiali, parate, discorsi del Governatore (`VI.1.i`), fuochi d'artificio (astratti o evento visivo). Enfasi sul patriottismo e sull'unità.
            * `[]` 2. **Festa del Raccolto Prospero (es. Metà 9° Mese, dopo il principale periodo di raccolta agricola `C.9`):** Ringraziamento per l'abbondanza, grandi banchetti familiari e comunitari, mercati agricoli speciali con prodotti di stagione, decorazioni rurali, giochi e competizioni a tema agricolo.
            * `[]` 3. **Notte delle Stelle Silenti (es. Giorno del Solstizio d'Inverno, se applicabile):** Celebrazione della quiete, della riflessione e della luce interiore durante il periodo più buio. Tradizioni: accensione di candele o luci speciali, racconti di storie, cibi caldi e confortanti, contemplazione del cielo stellato.
            * `[]` 4. **Giorno della Memoria e dell'Unità Civica (es. Data legata a un evento storico cruciale per l'unità di Anthalys):** Cerimonie solenni, commemorazioni di figure storiche importanti, attività di volontariato comunitario (`XIII.4`), riflessione sui valori fondanti della Costituzione (`XXII.A`).
            * `[]` 5. *(Aggiungere 2-3 altre festività fisse uniche per il lore e la cultura di Anthalys, con temi distinti, es. una legata alla tecnologia, una all'arte, una al ciclo dell'acqua/natura)*.
    * `[]` c. **Festività Mobili di Anthalys:**
        * `[]` i. **Struttura Dettagliata per Ogni Festività Mobile:** *(Struttura identica a `XXXII.5.b.i`, ma con aggiunta della regola di calcolo data)*
            * `[]` 1. Nome Ufficiale.
            * `[]` 2. **Regola di Calcolo della Data:** Basata su cicli lunari (`XXXII.7.b`), equinozi/solstizi (`XXXII.7.c`), o altri eventi astronomici/naturali ricorrenti ma non fissi. Il `TimeManager` (`XXXII.8`) calcolerà e annuncerà queste date con anticipo.
            * `[]` 3. Origine e Lore. (Collegamento a `XX. ATTEGGIAMENTI CULTURALI`).
            * ... (punti 4-10 come per le festività fisse, collegando a `XX` e `XXVIII.d`).
        * `[]` ii. **Elenco Festività Mobili (Esempi da Dettagliare con la struttura sopra):**
            * `[]` 1. **Festa della Fioritura (o della Rinascita Primaverile, es. calcolata sulla prima luna piena dopo un segno astronomico di inizio primavera):** Celebrazione del rinnovamento della natura (`XXX.c`), della fertilità e dei nuovi inizi. Tradizioni: fiere dei fiori e delle piante, picnic all'aperto, danze tradizionali, creazione di ghirlande.
            * `[]` 2. **Festival delle Lanterne dei Desideri (es. una notte specifica di una particolare fase lunare estiva, come da `I.3.e.1.iii`):** Desideri e speranze affidati a lanterne luminose (fluttuanti sull'acqua o luminarie speciali, considerando la sicurezza e la tecnologia di Anthalys). Atmosfera contemplativa, musica serale, riunioni tranquille.
            * `[]` 3. *(Aggiungere 1-2 altre festività mobili uniche, magari una legata a un evento astronomico specifico visibile solo in certi periodi, o una "festa dei venti" se il vento ha un ruolo nel lore)*.
    * `[]` d. **Integrazione delle Festività nel Comportamento degli NPC (`IV.4`):**
        * `[]` i. Gli NPC riconoscono attivamente le festività imminenti e in corso (es. tramite calendario personale, notizie su SoNet `XXIV.c.viii`).
        * `[]` ii. Modificano le loro routine: prendono giorni liberi dal lavoro/scuola (`XXXII.5.a.iii`), pianificano e partecipano attivamente alle attività festive (`XXXII.5.b.i.5`, `XXXII.5.c.i.5`), decorano le loro case (`XVIII.1`) con oggetti a tema (`XXXII.5.b.i.7`).
        * `[]` iii. Intraprendono interazioni sociali specifiche a tema festivo con familiari e amici (`VII.1`).
        * `[]` iv. Le loro scelte di acquisto (beni specifici, regali - `VIII.6`, `XVIII.5.h`) e di preparazione/consumo di cibo (`X.5`, `C.9.d`) sono fortemente influenzate dalle tradizioni della festività.
    * `[]` e. **Sviluppo e Evoluzione Dinamica delle Tradizioni (Molto Avanzato):**
        * `[]` i. Le tradizioni associate a una festività non sono completamente statiche. Nel corso di molte generazioni simulate, o in risposta a grandi eventi storici (`XIV`) o cambiamenti culturali (`C.1`), alcune usanze potrebbero evolvere, fondersi con altre, o cadere in disuso, mentre nuove potrebbero emergere organicamente dal comportamento aggregato degli NPC.
        * `[]` ii. Questo renderebbe il mondo di Anthalys ancora più vivo e credibile nel lungo periodo.

* `[]` **6. Ciclo delle Stagioni e Impatto Ambientale di Base:** *(Dettagli climatici ed eventi atmosferici specifici sono in Sezione XXVI)*
    * `[]` a. Definizione del ciclo stagionale di Anthalys, in linea con l'anno di 18 mesi (es. potrebbero esserci 6 stagioni da 3 mesi, o un altro schema logico per il lore, ognuna con un nome e caratteristiche base).
    * `[]` b. Impatto visivo di base delle stagioni sull'ambiente (colori della vegetazione `XXX.c`, durata della luce diurna `XXXII.1.b`, presenza di neve/ghiaccio di base).
    * `[]` c. Effetti generali delle stagioni sul comportamento e sull'umore degli NPC (es. preferenze per attività indoor/outdoor `X`, moodlet stagionali `IV.4.i`, scelta abbigliamento `II.2.e`).
* `[]` **7. Motore Astronomico di Base ed Eventi Cosmici:**
    * `[]` a. Implementazione di un ciclo lunare per la/le luna/e di Anthalys, con fasi visibili nel cielo notturno e impatto sulla luminosità ambientale.
    * `[]` b. Utilizzo delle fasi lunari per il calcolo di alcune festività mobili (`XXXII.5.c.i.2`).
    * `[]` c. (Avanzato) Possibilità di altri eventi cosmici periodici o rari (es. allineamenti planetari visibili, piogge di meteoriti annuali, passaggi di comete) che possono essere osservati dagli NPC, generare discussioni (`VII.1.c`), diventare parte del folklore, o avere un impatto culturale/psicologico minore (es. stupore, timore reverenziale). Questi eventi sarebbero annunciati dal `TimeManager` o da osservatori astronomici.
    * `[]` d. (Lore) Definizione delle costellazioni visibili nel cielo di Anthalys e loro eventuale significato culturale o astrologico (se presente e non considerato "paranormale").
* `[]` **8. `TimeManager` Globale: Funzionalità e Metodi Helper:**
    * `[]` a. Esistenza di un oggetto `TimeManager` centrale e autorevole che gestisce l'avanzamento del tempo (tick, minuti, ore, giorni, mesi, anni), la data e l'ora correnti.
    * `[]` b. Il `TimeManager` notifica gli altri sistemi della simulazione (NPC, ambiente, economia, ecc.) degli aggiornamenti temporali rilevanti.
    * `[]` c. Fornitura di una robusta API (metodi helper) in `TimeManager` per:
        * `[]` i. Verificare se un dato giorno è lavorativo o scolastico, considerando i giorni della settimana (`XXXII.3.b.i`), le festività (`XXXII.5.a.iii`), e i calendari specifici (`V.1.d`, `VIII.1.b`).
        * `[]` ii. Ottenere la stagione corrente (`XXXII.6.a`).
        * `[]` iii. Calcolare la differenza tra due date, aggiungere/sottrarre periodi di tempo a una data.
        * `[]` iv. Gestire un sistema di "allarmi" o "eventi programmati a tempo" che possono essere impostati da altri moduli per triggerare logiche specifiche a date/orari futuri (es. scadenza tasse `VIII.2.c`, inizio eventi festivi `XXXII.5`, promemoria personali NPC su SoNet `XXIV.c.viii`).

---

