## V. SISTEMA SCOLASTICO DI ANTHALYS `[]`

* **1. Struttura e Calendario Scolastico Complessivo:** `[]`
    * `[P]` a. Definire Livelli Scolastici con fasce d'età. (Costanti per età di inizio (`SCHOOL_AGE_START_..._DAYS`) e durate (`DURATION_..._YEARS`) dei livelli scolastici definite in `settings.py`)
        * `[]` i. Implementare gli 8 livelli scolastici dettagliati con le relative fasce d'età come da specifiche. *(Enum `SchoolLevel` aggiornata per riflettere gli 8 livelli + NONE. Costanti di età e durata definite concettualmente in `settings.py` per Infanzia (1-3 anni), Elementari Inferiori (3/4-6 anni), Elementari Superiori (6/7-9 anni), Medie Inferiori (9/10-12 anni), Medie Superiori (12/13-15 anni), Superiori (15/16-18 anni, obbligatorio), Superior Facoltativo (18/19-21 anni, preparazione pre-universitaria), Università (21+ anni, specializzazione universitaria). Logica di assegnazione in `Character` e `BackgroundNPCState` da aggiornare/verificare con queste nuove costanti).*.
    * `[P]` b. Implementare Calendario Scolastico Annuale (basato su 18 mesi). (Costanti per i mesi di inizio/fine dei periodi scolastici (`SCHOOL_MONTHS_PERIOD_...`) definite in `settings.py`)
    * `[]` c. (Obsoleto, integrato in V.1.b) Implementare Pause Scolastiche definite (Primaverile 12gg, Estiva 72gg). *(Le pause sono ora definite dalla struttura 6 mesi scuola / 3 mesi pausa)*.
    * `[]` d. Integrare il calendario scolastico (periodi di lezione, pause) nella logica di frequenza degli NPC (`TimeManager.is_school_day()`). *(Metodo in `TimeManager` concettualizzato)*.
    * `[]` e. **Gestione Iscrizioni e Percorsi Formativi tramite SoNet:** `[NUOVO PUNTO]`
        * `[]` i. Le procedure di iscrizione ai cicli scolastici obbligatori sono gestite centralmente con il DID (`XII`).
        * `[]` ii. L'iscrizione a livelli facoltativi (es. Superior Facoltativo `V.2.g`, Università `V.2.h`), corsi di formazione continua (`V.2.h` implicitamente), o la scelta di istituti specifici (se meccanica implementata) avverrà tramite la **Sezione Istruzione e Formazione del portale SoNet (`XXIV.c.iv.2`)**.
        * `[]` iii. SoNet fornirà informazioni sull'offerta formativa disponibile (corsi, requisiti di accesso).

* **2. Livelli Scolastici, Curriculum e Sviluppo Abilità Specifiche:** `[]` *(Tutti i sotto-punti per curriculum/impatto per livello rimangono `[]` finché non implementati nel dettaglio, ma le fasce d'età sono state definite)*
    * `[]` a. **Infanzia (1-3 anni):**
        * `[]` i. Obiettivo: Sviluppo motorio, sociale, linguistico.
        * `[]` ii. Curriculum: Gioco, attività fisica, introduzione colori/numeri/lettere, socializzazione, Anthaliano moderno base.
        * `[]` iii. Impatto: Sviluppo skill base (es. `MOVEMENT`, `COMMUNICATION`, `SOCIAL`).
    * `[]` b. **Elementari Inferiori (3/4-6 anni):**
        * `[]` i. Obiettivo: Basi per alfabetizzazione e numerazione.
        * `[]` ii. Curriculum: Lettura/scrittura base, matematica base, scienze naturali intro, attività artistiche, Anthaliano moderno, Inglese.
        * `[]` iii. Impatto: Sviluppo skill (es. `LEARNING`, `LOGIC` base, `CREATIVITY` base, `LANGUAGE_ANTHALIAN`, `LANGUAGE_ENGLISH`).
    * `[]` c. **Elementari Superiori (6/7-9 anni):**
        * `[]` i. Obiettivo: Consolidare competenze base, introdurre nuovi concetti.
        * `[]` ii. Curriculum: Lettura/scrittura avanzate, matematica (x,/,frazioni), scienze naturali/sociali, arti visive/musica, ed. fisica, Anthaliano moderno/antico base, Inglese.
        * `[]` iii. Impatto: Sviluppo skill ulteriori.
    * `[]` d. **Medie Inferiori (9/10-12 anni):**
        * `[]` i. Obiettivo: Sviluppare competenze intermedie, pensiero critico.
        * `[]` ii. Curriculum: Letteratura/grammatica, matematica (algebra/geometria base), scienze (bio/chim/fis intro), storia/geografia, ed. tecnologica/informatica base, ed. fisica, Anthaliano moderno/antico base, Inglese.
        * `[]` iii. Impatto: Sviluppo skill.
    * `[]` e. **Medie Superiori (12/13-15 anni):**
        * `[]` i. Obiettivo: Preparazione avanzata.
        * `[]` ii. Curriculum: Letteratura/composizione, matematica avanzata, scienze avanzate, studi sociali, lingue straniere avanzate, ed. tecnologica/informatica avanzata, ed. fisica, arti/musica avanzate.
        * `[]` iii. Impatto: Sviluppo skill.
    * `[]` f. **Superiori (15/16-18 anni, obbligatorio):**
        * `[]` i. Obiettivo: Preparazione università/lavoro.
        * `[]` ii. Curriculum: Materie accademiche avanzate, progetti di ricerca, preparazione carriera/orientamento.
        * `[]` iii. Impatto: Sviluppo skill avanzate, possibile influenza su opportunità di carriera/universitarie.
    * `[]` g. **Superior Facoltativo (18/19-21 anni, preparazione pre-universitaria):**
        * `[]` i. Obiettivo: Specializzazione per accesso università.
        * `[]` ii. Curriculum: Materie di specializzazione, ricerca, stage, orientamento.
        * `[]` iii. Impatto: Forte influenza su accesso/successo universitario.
    * `[]` h. **Università (21+ anni, specializzazione universitaria):**
        * `[]` i. Obiettivo: Educazione approfondita e specialistica.
        * `[]` ii. Struttura: Laurea Triennale, Magistrale, Dottorato.
        * `[]` iii. Facoltà e Materie Esempio (Scienze/Tecnologia, Arti/Lettere, Economia/Gestione, Ingegneria, Medicina/Scienze Salute).
        * `[]` iv. Programmi di Scambio.
        * `[]` v. Impatto: Acquisizione skill altamente specializzate, percorsi di carriera di alto livello.
    * `[]` i. **Registrazione Ufficiale Titoli di Studio e Carriera Accademica:** `[NUOVO PUNTO]`
        * `[]` 1. I diplomi, le lauree e le altre certificazioni ufficiali ottenute al completamento dei cicli di studio sono registrate digitalmente e associate al DID (`XII`) del cittadino.
        * `[]` 2. Questi documenti sono consultabili dal titolare come parte del proprio storico accademico e nell'archivio certificazioni all'interno del portale **SoNet (rispettivamente `XXIV.c.iv.1` e `XXIV.c.i.5`)**.

* **3. Meccaniche Scolastiche per NPC:** `[]`
    * `[]` a. NPC frequentano scuola (simulazione presenza tramite azione `ATTENDING_SCHOOL`).
        * `[]` i. Integrare la frequenza con il nuovo calendario scolastico dettagliato. *(Il metodo `TimeManager.is_school_day()` ora include questa logica).*.
    * `[P]` b. Performance scolastica (`school_performance`, compiti) influenzata da NPC. (Molte costanti relative a performance scolastica, compiti, e loro impatto definite in `settings.py`)
        * `[]` i. Introdurre un sistema di "voti" formali.
        * `[]` ii. Espandere i fattori che influenzano la performance.
    * `[P]` c. Impatto performance su sviluppo abilità (attualmente skill "learning"). (Costanti per guadagno skill e moltiplicatori da performance definite in `settings.py`)
        * `[]` i. La performance influenza lo sviluppo di **abilità specifiche**.
        * `[]` ii. La performance scolastica complessiva influenza **aspirazioni** e **opportunità future**.
    * `[]` d. "Saltare la scuola" con conseguenze.
    * `[]` e. Attività extracurriculari.
    * `[]` f. Viaggi educativi.
    * `[]` g. Supporto agli Studenti.
    * `[]` h. Report Scolastici in TUI (come da tuo file TODO) *(Rappresentano la documentazione corrente/annuale, mentre lo storico ufficiale è su SoNet)*.
    * `[]` i. **Nuovo - Dinamiche di "Bocciatura" e Ripetizione Anno:** *(Da TODO interno che hai menzionato)*.
        * `[]` 1. Definire criteri per la bocciatura (es. `school_performance` troppo bassa per troppo tempo, troppe assenze ingiustificate).
        * `[]` 2. Se un NPC viene "bocciato", ripete l'anno scolastico corrente (o un segmento di esso).
        * `[]` 3. Limite di età per la ripetizione (es. fino ai 18 anni come da tua nota).
        * `[]` 4. Impatto sull'umore, sulle relazioni (con genitori/coetanei) e sulle aspirazioni future.
    * `[]` j. **Accesso a Informazioni e Servizi Scolastici tramite SoNet:** `[NUOVO PUNTO]`
        * `[]` i. Gli NPC studenti (o i loro tutori) possono utilizzare SoNet per visualizzare comunicazioni dalla scuola (es. calendario eventi, circolari - via `XXIV.c.viii`), consultare (astrattamente) materiale didattico online fornito dalla scuola, o interagire con alcuni servizi amministrativi scolastici (se implementati).

---

