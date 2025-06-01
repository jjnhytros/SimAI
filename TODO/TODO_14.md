## XIV. EVENTI CASUALI E SCENARI GUIDATI `[]`

* `[]` a. Registrazione eventi significativi della simulazione (nascite, morti, cambi di stadio di vita, matrimoni, promozioni, ecc.) per i report testuali e il log dell'interfaccia utente. (Include vecchio `I.2.e`)
* `[]` b. **Sistema di Eventi Casuali Dinamici:**
    * `[]` i. Definire una libreria di eventi casuali di piccola e media portata (positivi, negativi, neutri) con diverse probabilità di accadimento e condizioni di trigger.
        * *Esempi: trovare soldi per terra, perdere il portafoglio, guasto domestico minore, ricevere una telefonata inaspettata, incontro fortuito, piccolo infortunio, vincita minore a una lotteria istantanea.*
    * `[]` ii. Gli eventi possono influenzare direttamente l'umore, i bisogni, le relazioni o le finanze di uno o più NPC coinvolti.
    * `[]` iii. Gli eventi possono sbloccare opportunità (es. un nuovo contatto sociale, un'idea per un hobby, un oggetto raro trovato) o piccole sfide.
    * `[]` iv. (Avanzato) La probabilità o l'esito degli eventi casuali può essere influenzato da:
        * Tratti degli NPC (es. un `Clumsy` ha più probabilità di inciampare, un `Lucky` - tratto futuro - di trovare soldi o vincere piccole somme).
        * Umore attuale dell'NPC.
        * Stagione o condizioni meteorologiche (`I.3.f`).
        * Stato generale del "mondo" o della `Location` (es. più possibilità di guasti in una casa vecchia/maltenuta `XVIII.2`, o piccoli incidenti in un lotto con `safety_rating` basso `XVIII.5.i.ii`).
        * ***Nota: Cruciale anche per "dare vita" agli NPC di background (LOD Fascia 3) senza una simulazione completa.***
        * Livello di `Alfabetizzazione Mediatica` (`VI.2.e`) di un NPC potrebbe influenzare la sua reazione a eventi basati su "notizie" o informazioni.
    * `[]` v. **Estensione "Total Realism" - Eventi Guidati dall'Ecosistema Informativo:**
        * `[]` 1. Eventi casuali potrebbero essere scatenati dalla diffusione di notizie (vere o false – vedi `VI.2.e.ii`) nel mondo di gioco. Ad esempio, una "notizia" su una carenza di un certo bene potrebbe spingere gli NPC a fare scorte (azione `STOCKPILE_GOODS`), o una "notizia" su un'opportunità di investimento potrebbe portare a scelte finanziarie.
        * `[]` 2. La reazione degli NPC a tali eventi-notizia dipende dalla loro fiducia nella fonte (se simulata), dai loro tratti, e dalla loro skill di `Alfabetizzazione Mediatica`.
* `[]` c. **Eventi Contestuali basati sull'Ambiente e sui Tratti degli NPC:** *(La definizione di tratti reattivi è in corso; la generazione degli eventi specifici è da implementare)*
    * `[]` i. Implementare la generazione di eventi specifici basati sull'ambiente o su stimoli (es. `EVENT_SAW_CREEPY_CRAWLIES` in un luogo specifico, `EVENT_LOCATION_BECAME_VERY_DIRTY`, `EVENT_SUDDEN_LOUD_NOISE`, `EVENT_WITNESSED_VOMIT`).
    * `[]` ii. I tratti degli NPC (es. `Squeamish`, `Cowardly`, `Curious`, `HayFever`, `HatesHeat`, `CantStandCold`, `AgeInsecure` in reazione a complimenti/critiche) reagiscono a questi eventi specifici o a condizioni ambientali con moodlet, pensieri, o scelte di azione prioritarie. *(Molte classi tratto sono già state definite con metodi `get_associated_moodlet_on_event` e `get_periodic_moodlet` per questo scopo).*.
    * `[]` iii. (Avanzato) Eventi di "scoperta" o interazione con oggetti specifici nell'ambiente che triggerano reazioni basate sui tratti (es. un `AestheticPerfectionist` che trova un oggetto d'arte di cattivo gusto).
* `[]` d. **Eventi di Sincronicità / Realismo Magico (Semplificato):** *(Dalle idee originali)*
    * `[]` i. Introdurre piccoli eventi "strani", coincidenze significative, o momenti di "deja-vu" che non hanno una spiegazione logica immediata ma aggiungono sapore e mistero.
    * `[]` ii. Questi eventi potrebbero dare moodlet unici (es. "Meravigliato", "Confuso", "Intuizione Improvvisa") o sbloccare pensieri/interazioni speciali.
    * `[]` iii. La probabilità potrebbe essere influenzata da tratti come `CURIOUS`, `WHIMSICAL` o (futuro) `SPIRITUAL`.
* `[]` e. **(Avanzato) Scenari Guidati o "Storylet":**
    * `[]` i. Definire brevi catene di eventi interconnessi o piccoli archi narrativi che si attivano per specifici NPC in base a determinate condizioni (età, tratti, relazioni, carriera, aspirazioni, eventi passati, memorie `IV.5`).
    * `[]` ii. Questi scenari potrebbero presentare all'NPC (o al giocatore, se interattivo) delle scelte con conseguenze diverse, creando mini-storie personalizzate.
        * *Esempio: un NPC `Ambitious` con bassa performance lavorativa potrebbe ricevere un'offerta per un "progetto rischioso ma redditizio" che potrebbe portarlo a una promozione o a un fallimento.*
        * *Esempio: un NPC `LoveScorned` potrebbe incontrare qualcuno che assomiglia a un suo ex partner, portando a una catena di interazioni e decisioni.*
        * *Esempio: uno scenario legato a una crisi di mezza età per NPC `ADULT` con certi tratti, che porta a scelte di cambiamento di vita.*
    * `[]` iii. Completare o fallire questi scenari ha un impatto significativo sull'NPC (umore a lungo termine, acquisizione di nuovi tratti minori o memorie potenti, cambiamenti nelle relazioni o aspirazioni).
    * `[]` iv. **Estensione "Total Realism" - Scenari Complessi e Dinamiche Sociali Emergenti:**
        * `[]` 1. Sviluppare scenari che coinvolgono più NPC e le loro relazioni, con esiti che dipendono dalle azioni e interazioni di tutti i partecipanti (es. una faida familiare, la creazione di un'impresa di gruppo, una campagna politica locale).
        * `[]` 2. Alcuni scenari potrebbero essere attivati da dinamiche sociali più ampie (es. un periodo di difficoltà economica `VIII.5.b` che scatena scenari di perdita del lavoro o di ricerca di nuove opportunità per molti NPC).
* `[]` f. **Eventi Legati al Ciclo di Vita e alle Relazioni:** *(Parzialmente coperto dalla registrazione eventi, ma espandere per impatto attivo)*
    * `[]` i. Nascite, morti, matrimoni (futuri), divorzi (futuri) sono registrati.
    * `[]` ii. Questi eventi dovrebbero triggerare reazioni emotive e comportamentali complesse negli NPC coinvolti e nella loro cerchia sociale (amici, famiglia), influenzate dai loro tratti e dalla relazione con gli NPC al centro dell'evento. *(I moodlet base per compleanni, festività sono un inizio; i tratti come `LoveScorned`, `Lovebug`, `Heartbreaker` reagiranno a eventi relazionali)*.
* `[]` g. Meccanica di "storie di quartiere" e progressione della vita per i PNG non attivamente controllati.
    * `[]` i. Eventi specifici che simulano la "progressione della storia" per le famiglie e i singoli NPC nel quartiere non direttamente controllati dal giocatore, per dare la sensazione di un mondo vivo (es. matrimoni tra NPC di background, nascite, cambi di lavoro, trasferimenti, piccole faide o amicizie che si sviluppano "off-screen" ma di cui si può venire a conoscenza tramite pettegolezzi `VII.9` o osservazione).

---

