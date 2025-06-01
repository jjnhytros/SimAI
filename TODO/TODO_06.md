## VI. SISTEMA POLITICO, GOVERNANCE E PARTECIPAZIONE CIVICA IN ANTHALYS `[]`

* **1. Struttura Politica e di Governance di Anthalys:** `[]`
    * `[]` a. Definire il tipo di governo di Anthalys come stato sovrano e indipendente, fondato su dignità umana, libertà, giustizia e solidarietà. *(Art. 1 Costituzione)*.
        * `[]` i. **Governatore:** Potere esecutivo, eletto democraticamente. Può scegliere il nome con cui farsi chiamare (tre nomi + cognome ereditato). *(Art. 4 Costituzione)*.
            * `[]` 1. Implementare meccanica di elezione democratica del Governatore.
            * `[]` 2. Logica per la scelta del nome e la gestione della successione (erede designato con nuovo nome e cognome del predecessore, Art. 5 Costituzione).
        * `[]` ii. **Parlamento Bicamerale (Camera dei Rappresentanti e Senato):** Potere legislativo. *(Art. 6 Costituzione)*.
            * `[]` 1. Definire composizione, elezione/nomina e funzioni delle due camere.
            * `[]` 2. **Estensione "Total Realism" - Processo Legislativo Dettagliato:**
                * `[]` a. Simulazione (astratta o dettagliata) del processo di proposta, dibattito, emendamento e votazione delle leggi all'interno del Parlamento.
                * `[]` b. NPC politici (membri del parlamento) con proprie ideologie (`VI.1.d.ii`), tratti (`IV.3.b`), e livelli di influenza (`IX.e` skill `Politics` o `Influence`) che partecipano attivamente.
                * `[]` c. Possibilità di lobbying (astratto) o influenza dell'opinione pubblica (espressa anche tramite consultazioni/petizioni su **SoNet `XXIV.c.v.4`**) sul processo legislativo.
        * `[]` iii. **Potere Giudiziario:** Indipendente, garante di giustizia e legalità. *(Art. 7 Costituzione)*.
            * `[]` 1. Definire la struttura del sistema giudiziario (tribunali, giudici).
            * `[]` 2. **Estensione "Total Realism" - Sistema Giudiziario Approfondito:**
                * `[]` a. Implementare `LocationType.COURTHOUSE` (Tribunale).
                * `[]` b. Nuova Carriera: `LAWYER` (Avvocato) e `JUDGE` (Giudice) (Estensione di VIII.1.j).
                * `[]` c. NPC possono intentare cause civili.
                * `[]` d. (Se implementato sistema criminale) Processi penali.
                * `[]` e. Sentenze variabili.
                * `[]` f. Possibilità di appelli e revisioni processuali.
            * `[]` 3. I cittadini possono accedere a informazioni sui propri diritti e sul funzionamento base del sistema giudiziario tramite la **Sezione Informazioni Legali di SoNet (`XXIV.c.x`)**.
    * `[]` c. Cicli elettorali o periodi di mandato per le cariche. *(Anno di fondazione 5775 stabilito, Art. 1 Costituzione)*.
    * `[]` d. Partiti Politici e Ideologie.
        * `[]` i. Definire 2-4 principali correnti ideologiche o partiti politici in Anthalys con piattaforme distinte (es. Progressisti Verdi, Conservatori Economici, Centristi Sociali, Libertari Civici).
        * `[]` ii. Gli NPC possono avere un'affiliazione o una preferenza per un partito/ideologia (attributo `political_leaning` o `party_affiliation` in `Character` / `BackgroundNPCState`).
        * `[]` iii. Tratti come `FEMINIST`, `SEXIST`, (futuri) `CONSERVATIVE`, `LIBERAL`, `ACTIVIST` influenzano l'affiliazione e le scelte politiche.
        * `[]` iv. I partiti possono avere un "indice di popolarità" che fluttua in base a eventi e performance dei loro membri eletti.

* **2. Partecipazione Civica e Politica degli NPC:** `[]`
    * `[]` a. **Personalità Complesse e Tratti (IV.3.b):** I tratti di personalità degli NPC influenzano le loro opinioni politiche, la propensione al voto e all'attivismo.
        * `[]` i. Diritto di Voto: NPC acquisiscono il diritto di voto (collegato a Diritti Fondamentali, Art. 10 Costituzione). La registrazione alle liste elettorali e la verifica dello status di elettore avvengono tramite la **Sezione Partecipazione Civica di SoNet (`XXIV.c.v.1`)**.
    * `[]` b. **Bias Cognitivi Semplificati (Molto Avanzato):**
        * `[]` i. (Futuro) Considerare un leggero "Effetto Bandwagon" (tendenza a supportare chi è percepito come vincente) o "Underdog" nelle preferenze di voto.
        * `[]` ii. (Futuro) "Bias di Conferma Politico": NPC tendono a interpretare notizie/eventi in modo da confermare le proprie convinzioni politiche preesistenti.
    * `[]` c. **Decisione di Voto:**
        * `[]` i. NPC (dettagliati e di background, se hanno diritto di voto) decidono se votare e per chi/cosa (candidato, partito, opzione referendaria).
        * `[]` ii. Fattori influenzanti: tratti, `political_leaning`, `general_wellbeing`, importanza percepita dell'elezione/referendum (informazioni ottenibili tramite **SoNet `XXIV.c.v.2`**), (futura) "Alfabetizzazione Mediatica".
        * `[]` iii. (Avanzato) "Voto Basato su Identità vs. Policy": NPC potrebbero dare più peso all'appartenenza a un gruppo/identità o alle proposte specifiche.
    * `[]` d. **Influenza delle Reti Sociali (Astratta):** L'opinione degli amici e familiari (relazioni con alto punteggio) può influenzare le preferenze politiche di un NPC. *(Concetto base, da dettagliare come la "media pesata" del tuo esempio originale possa applicarsi)*.
    * `[]` e. **Alfabetizzazione Mediatica e Flusso di Informazioni (Attributo/Skill Futura):**
        * `[]` i. NPC con alta alfabetizzazione mediatica sono meno suscettibili a disinformazione (eventi futuri) e analizzano le proposte politiche più criticamente.
        * `[]` ii. **Estensione "Total Realism" - Ecosistema dell'Informazione:**
            * `[]` 1. Simulazione di diverse fonti di informazione (giornali, TV, radio, portali online – astratti o legati a oggetti/azioni `X.8`, skill `Media Production` `IX.e`).
            * `[]` 2. Le fonti possono avere un orientamento politico o un livello di affidabilità variabile.
            * `[]` 3. NPC scelgono quali fonti consultare in base ai loro tratti, `political_leaning`, e `media_literacy_skill`.
            * `[]` 4. L'ecosistema informativo di Anthalys include la potenziale diffusione di notizie da varie fonti, alcune delle quali potrebbero essere inaffidabili o diffondere "fake news" (meccanica da definire in `XIV` - Eventi Casuali, o legata a media non ufficiali). Queste informazioni (vere o false) hanno un impatto sull'opinione pubblica, sulle campagne elettorali (`VI.3`), e sul comportamento degli NPC (incluso il voto). Il portale **SoNet (`XXIV.c.viii`)**, in quanto canale ufficiale del governo, fornisce informazioni verificate e comunicazioni istituzionali, agendo come punto di riferimento autorevole e potenziale contrasto alla disinformazione circolante altrove. *(Corretto per chiarire il ruolo di SoNet)*
    * `[]` f. **Attivismo e Candidatura:**
        * `[]` i. NPC con tratti rilevanti (`AMBITIOUS`, `CAREER_ORIENTED` con focus politico, `CUNNING`, `FEMINIST`, futuri `ACTIVIST`) possono decidere di candidarsi per cariche elettive (azione `RUN_FOR_OFFICE`).
        * `[]` ii. Possono partecipare ad attività di campagna (azioni `ATTEND_RALLY`, `VOLUNTEER_FOR_CAMPAIGN`).
    * `[]` g. **Interazione Civica tramite SoNet:**
        * `[]` i. Gli NPC possono utilizzare la **Sezione Partecipazione Civica di SoNet (`XXIV.c.v.4`)** per partecipare a consultazioni pubbliche indette dal governo o per aderire/promuovere petizioni online su temi specifici.
        * `[]` ii. L'esito di petizioni con ampia partecipazione potrebbe influenzare l'agenda politica (`VI.1.ii.2.c`) o portare a referendum (`VI.4`).

* **3. Simulazione di Elezioni e Campagne Elettorali:** `[]` *(Adattato da "Miglioramenti alla Simulazione" e "Strategie di Campagna")*
    * `[]` a. **Ciclo Elettorale:** La simulazione gestisce elezioni periodiche per le cariche definite. *(Concetto base)*.
    * `[]` b. **Candidati:**
        * `[]` i. NPC (dettagliati o di background con profilo adatto) possono diventare candidati. *(La generazione di candidati migliorata come da tuo punto 3.g è rilevante)*.
        * `[]` ii. I candidati hanno una "piattaforma" (temi chiave) e un (futuro) "budget di campagna".
        * `[]` iii. Le piattaforme dei candidati e le informazioni ufficiali sulle elezioni sono consultabili tramite **SoNet (`XXIV.c.v.2`)**.
    * `[]` c. **Campagna Elettorale (Astratta per Ora):**
        * `[]` i. I candidati compiono azioni di campagna (dibattiti, rally, pubblicità – azioni future) che influenzano la loro popolarità e le intenzioni di voto.
        * `[]` ii. (Futuro) Gestione del budget di campagna e sua allocazione strategica (come da tuoi punti 3.a.i-iii e 4.d).
    * `[]` d. **Eventi Durante la Campagna.** *(Questi eventi possono includere la diffusione di disinformazione da fonti esterne a SoNet, che influenza la campagna).*
        * `[]` i. Eventi casuali (scandali, gaffe, endorsement positivi/negativi) possono influenzare la campagna. *(Logica base implementata per eventi generici, da specializzare)*.
        * `[]` ii. (Futuro) Dibattiti pubblici tra candidati con impatto sulla percezione.
    * `[]` e. **Simulazione del Voto:**
        * `[]` i. Al giorno delle elezioni, gli NPC votanti esprimono la loro preferenza. (Futura possibilità di voto elettronico tramite **SoNet `XXIV.c.v.3`**).
        * `[]` ii. Conteggio dei voti e determinazione del vincitore.
    * `[]` f. **Sistemi Elettorali Diversi (Molto Avanzato):** Considerare diversi modi di contare i voti o strutturare le elezioni, se rilevante per il lore.
    * `[]` g. **Generazione e Persistenza Candidati:** *(Adattato dal tuo punto 9 sul DB SQLite)*.
        * `[]` i. Implementare un sistema per tracciare i candidati, i loro attributi politici chiave, e la loro storia elettorale (vittorie, sconfitte, budget usati). (Potrebbe essere parte degli attributi estesi di `Character` o `BackgroundNPCState`, o un registro separato).

* **4. Sistema di Referendum:** `[]`
    * `[]` a. Definire meccanismi per cui un referendum può essere indetto.
    * `[]` b. I referendum pongono quesiti specifici ai cittadini. Informazioni dettagliate sui quesiti sono disponibili su **SoNet (`XXIV.c.v.2`)**.
    * `[]` c. Gli NPC votano sul referendum. (Futura possibilità di voto elettronico tramite **SoNet `XXIV.c.v.3`**).
    * `[]` c. Gli NPC votano sul referendum in base ai loro tratti, `political_leaning`, `general_wellbeing`, e (futura) comprensione del quesito (influenzata da `KNOWLEDGE_GENERAL` o `Alfabetizzazione Mediatica`).
    * `[]` d. L'esito del referendum ha un impatto diretto sulle leggi o politiche del mondo di Anthalys.
    * `[]` e. Campagne pro/contro il quesito referendario possono avvenire, con NPC che si schierano.

* **5. Generazione di Contenuti Testuali (NLG) a Tema Politico:** `[]`
    * `[]` a. "Pensieri" politici degli NPC.
    * `[]` b. (Futuro) Generazione di slogan elettorali, sunti di discorsi, o "notizie" simulate sugli esiti delle elezioni/referendum (questi ultimi potrebbero essere comunicati ufficialmente tramite **SoNet `XXIV.c.viii`**).

* **6. Simboli Nazionali e Culturali (Nuovo punto basato sulla Costituzione):** `[]`
    * `[]` a. **Bandiera di Anthal:** Tre bande verticali blu, azzurro, blu, con una "A" bianca al centro. *(Art. 2 Costituzione)*. (Da considerare per futura rappresentazione visiva o descrizioni).
    * `[]` b. **Calendario Ufficiale:** 432 giorni, 18 mesi, 24 giorni/mese, 28 ore/giorno, settimana di 7 giorni specifici. *(Art. 3 Costituzione)*.
    * `[]` c. **Inno Nazionale:** "Sempre Liberi". *(Art. 13 Costituzione)*. (Potrebbe dare moodlet se "ascoltato" in eventi).
    * `[]` d. **Motto Nazionale:** "Sempre Liberi" / "Ariez Nhytrox". *(Art. 14 Costituzione)*.

* **7. Emendamenti Costituzionali e Revisione:** `[]`
    * `[]` a. (Molto Avanzato) Meccanica per cui la Costituzione può essere emendata.
    * `[]` b. **Estensione "Total Realism" - Evoluzione Legale Dinamica:**
        * `[]` i. Le leggi (non solo la Costituzione) possono essere create, abrogate o modificate dal Parlamento (`VI.1.ii.2`) in risposta a bisogni sociali emergenti, pressione pubblica (espressa anche tramite **SoNet `XXIV.c.v.4`**), o eventi significativi (`XIV`).
        * `[]` ii. Questo crea un sistema legale che evolve. Le leggi e gli emendamenti approvati sono resi pubblici e consultabili tramite la **Sezione Informazioni Legali di SoNet (`XXIV.c.x.2`)**.

* **8. Integrazione Dati, Parametrizzazione e Validazione (Principi Generali):** `[]`
    * `[]` a. Bilanciare le probabilità di voto e l'influenza dei vari fattori per ottenere risultati plausibili.
    * `[]` b. Calibrare l'impatto degli eventi politici sull'umore e sul comportamento degli NPC.

* **9. IA e LLM (Obiettivi a Lungo Termine):** `[]` *(Adattato dal tuo punto 8)*
    * `[]` a. (Molto Lontano Futuro) Usare LLM per generare dibattiti più complessi, discorsi, o per NPC che argomentano le loro posizioni politiche.

---

