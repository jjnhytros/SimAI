## VIII. SISTEMA ECONOMICO, LAVORO E WELFARE DI ANTHALYS `[]` (Include vecchio `VIII. CARRIERE E LAVORO` e `I.1.d`)

* `[P]` **A. Valuta Ufficiale di Anthalys: L'Athel (Ꜳ) Digitale**
    * `[]` i. L’Athel (simbolo: **Ꜳ**) è la valuta ufficiale unica della nazione di Anthalys e svolge un ruolo centrale in tutte le transazioni economiche. (Costanti `CURRENCY_NAME` e `CURRENCY_SYMBOL` definite in `settings.py`)
        * `[NOTA UNICODE]` Il simbolo **Ꜳ** corrisponde al carattere Unicode U+A732 (LATIN CAPITAL LETTER AA). Per riferimento: [https://www.compart.com/en/unicode/U+A732](https://www.compart.com/en/unicode/U+A732)
    * `[]` ii. **Transizione al Digitale Completo:** Originariamente esistente anche in forma fisica (banconote e monete), l'Athel fisico è attualmente in disuso e ha cessato di avere corso legale in favore di una gestione monetaria esclusivamente digitale.
    * `[]` iii. Tutte le transazioni finanziarie correnti (acquisti, stipendi, tasse, ecc.) sono gestite attraverso sistemi elettronici sicuri, principalmente tramite il Documento di Identità Digitale (DID `XII.5`) e il portale SoNet (`XXIV.c.i.3`, `XXIV.c.ii.2`).
    * `[]` iv. Benefici della transizione al digitale: significativa riduzione dei costi di gestione della moneta, aumento della trasparenza fiscale e finanziaria, e maggiore sicurezza contro falsificazioni e illeciti finanziari.
    * `[]` v. **Athel Fisico Obsoleto (Valore Storico/Collezionistico):**
        * `[]` 1. (Lore) Descrizione delle vecchie banconote di Athel: stampate su un tessuto composto all’85% di cotone e al 15% di fibre di lino, presentavano disegni che celebravano simboli, monumenti (`XXV.2.d`) e figure storiche di Anthalys.
        * `[]` 2. (Lore) Tagli delle banconote fisiche obsolete: 1, 2, 6, 12, 24, 48, 96, 144, e 288 **Ꜳ**. (Eventuali monete metalliche avevano tagli inferiori).
        * `[]` 3. Molti NPC, specialmente i più anziani o i collezionisti (`X.7`), potrebbero ancora conservare esemplari di Athel fisico come ricordo, cimelio di famiglia o per valore numismatico. Questi oggetti non hanno valore legale ma potrebbero essere scambiati tra collezionisti.

* `[]` **B. Sistema Bancario e Finanziario di Anthalys** `[SOTTOCATEGORIA PRINCIPALE AGGIORNATA]`
    * `[!]` i. Il sistema bancario di Anthalys è solido, tecnologicamente avanzato (basato su Athel digitale `VIII.A`) e ben regolamentato per garantire stabilità e integrità.
    * `[]` ii. **Banca Centrale di Anthalys (BCA):**
        * `[]` 1. Definire la Banca Centrale di Anthalys come l'autorità monetaria e di vigilanza principale. (Potrebbe essere un'entità governativa (`VI.1`) o semi-indipendente). La sua sede è un `LocationType` specifico nel Distretto Amministrativo (`XXV.1.e`).
        * `[]` 2. **Funzioni della BCA:** `[PUNTO AMPLIATO]`
            * `[]` a. Conduzione della politica monetaria per mantenere la stabilità economica, controllare l'inflazione e sostenere la crescita sostenibile.
                * `[]` i. Utilizzo di strumenti come la definizione dei tassi di interesse di riferimento (che influenzano i tassi delle banche commerciali `VIII.5.d.iii`).
                * `[]` ii. Gestione delle riserve obbligatorie per le banche commerciali.
                * `[]` iii. (Avanzato) Conduzione di operazioni di mercato aperto (astrattamente simulate) per influenzare la liquidità del sistema.
            * `[]` b. Mantenimento della stabilità finanziaria del sistema bancario e dei mercati (se presenti `VIII.5.d.ii`).
            * `[]` c. Regolamentazione e supervisione delle banche commerciali (`VIII.B.iii`) e di altri istituti finanziari.
            * `[]` d. Emissione e gestione dell'Athel digitale (`VIII.A`).
            * `[]` e. Gestione delle riserve nazionali (valutarie o di altre risorse strategiche, se rilevante per il lore).
            * `[]` f. Monitoraggio e supervisione del sistema dei pagamenti digitali (transazioni via DID/SoNet `XII.5`, `XXIV.c.i.3`).
    * `[]` iii. **Banche Commerciali di Anthalys:**
        * `[]` 1. Definire 2-4 principali brand di Banche Commerciali operanti in Anthalys, con filiali (`LocationType.BANK_BRANCH` in `XVIII.5.h`) distribuite nei vari distretti (`XXV.1`).
        * `[]` 2. Operano sotto la supervisione e secondo le regolamentazioni della Banca Centrale di Anthalys (`VIII.B.ii.2.c`).
        * `[]` 3. **Servizi Finanziari Offerti ai Cittadini e alle Imprese NPC:**
            * `[]` a. **Conti Correnti Digitali:** Ogni cittadino adulto (`IV.2.d`) e impresa (`VIII.1.k`) possiede almeno un conto corrente in **Ꜳ** presso una banca commerciale, collegato al proprio DID (`XII`) e gestibile tramite **SoNet (`XXIV.c.i.3`)**. Su questo conto vengono accreditati stipendi (`VIII.1.c`), pensioni (`VIII.3.a`), e da cui partono pagamenti per tasse (`VIII.2.b`), acquisti (`VIII.6`), ecc.
            * `[]` b. **Conti di Risparmio:** Offerta di conti di risparmio con tassi di interesse variabili (influenzati dalla politica della BCA `VIII.B.ii.2.a`), accessibili e gestibili via SoNet.
            * `[]` c. **Prestiti Personali e Mutui Immobiliari:** Gli NPC possono richiedere prestiti (per spese importanti, emergenze) o mutui (per acquisto proprietà `XVIII.5.j`). La concessione dipende da reddito, affidabilità creditizia (nuovo attributo NPC), garanzie. Tassi di interesse variabili.
            * `[]` d. **Finanziamenti alle Imprese:** Le aziende NPC (`VIII.1.k`) possono richiedere prestiti per investimenti o capitale circolante.
            * `[]` e. **Servizi di Investimento:** (Semplificati o più dettagliati) Offerta di prodotti di investimento (es. fondi comuni, obbligazioni governative/corporate, azioni di aziende quotate se `VIII.5.d.ii` implementato). Gli NPC con surplus di **Ꜳ** e propensione al rischio (`IV.3.b`) possono investire.
            * `[]` f. **Distribuzione dell'Athel Digitale:** Le banche commerciali sono il canale principale per la distribuzione e la circolazione dell'Athel digitale attraverso i conti e i portafogli elettronici integrati nel DID/SoNet.
        * `[]` 4. **Carriere Bancarie:** Definire carriere specifiche nel settore bancario (impiegato, consulente finanziario, analista prestiti, dirigente di banca – espansione `VIII.1.j`).
    * `[]` iv. **Altri Istituti Finanziari (Opzionale):**
        * `[]` 1. (Futuro) Compagnie di assicurazione (per salute integrativa `XXII.5.c`, proprietà, vita).
        * `[]` 2. (Futuro) Società di gestione del risparmio o fondi pensione privati.


* **1. Lavoro e Carriere per NPC:** `[]` (Vecchio `VIII.1. Sistema delle Carriere`)
    * `[]` a. **Struttura delle Carriere e dei Lavori:** *(Concettualizzazione dettagliata e struttura file in corso)*. (Vecchio `VIII.1.a` Percorsi di carriera multipli con livelli di promozione.)
        * `[]` i. Definire `CareerTrackName` Enum e `CareerCategory` Enum in `modules/careers/career_enums.py`. *(Definite, con icone)*. (Vecchio `VIII.1.a.i` Ogni livello ha stipendio in **Ꜳ**, orario, compiti, requisiti di promozione (skill, performance). *(Definito nelle classi)*)
        * `[]` ii. Definire classi base `BaseCareerLevel` e `BaseCareerTrack` in `modules/careers/base/`. *(Classi base definite concettualmente)*. (Vecchio `VIII.1.a.ii` Struttura directory: `modules/careers/base/base_career_track.py` e `base_career_level.py`. *(Confermato e implementato)*)
        * `[]` iii. Popolare le definizioni dettagliate delle carriere... *(Eventuali licenze professionali o certificazioni di qualifica richieste per alcune carriere potrebbero essere registrate e visualizzabili dal cittadino nella Sezione Identità di SoNet `XXIV.c.i.5`)*.
        * `[]` iv. Implementare un `CareerManager` (in `modules/careers/career_manager.py`) per caricare e gestire le definizioni delle carriere. *(Concettualizzato)*.
        * `[]` v. Gestire modelli di orario specifici per professione (turni, weekend, stagionalità, freelance) come eccezioni allo standard definito in XXII.1. *(Concetto annotato, da implementare la variabilità negli attributi di `BaseCareerLevel` e nella logica del `CareerManager`)*.
        * `[]` vi. Lavorare soddisfa il bisogno di "Reddito" e può influenzare altri bisogni/umore. (Vecchio `VIII.1.b`)
        * `[]` vii. Sistema di performance lavorativa. (Vecchio `VIII.1.c`)
        * `[]` viii. Eventi lavorativi (es. progetti speciali, scadenze, incontri con il capo, colleghi difficili). (Vecchio `VIII.1.d`)
        * `[]` ix. Possibilità di carriere freelance, part-time, o lavori saltuari. (Vecchio `VIII.1.e`)
        * `[]` x. Pensionamento. (Vecchio `VIII.1.f`)
    * `[]` b. Orario di Lavoro Standard e Settimanale. *(Definito in `modules/careers/careers_config.py` e basato su XXII.1)*.
    * `[]` c. Stipendi e Politiche Retributive. *(Definite in `modules/careers/careers_config.py` e basate su XXII.2)*.
        * `[]` i. NPC `Character` e `BackgroundNPCState` tracciano `annual_salary` (in **Ꜳ**), `years_of_service`, `base_salary_for_current_level` (in **Ꜳ**), `num_seniority_bonuses_received`. *(Attributi definiti concettualmente)*.
        * `[]` ii. Implementare logica per il calcolo e l'applicazione degli scatti di anzianità (vedi XXII.2.c) sull'**Ꜳ** annuale.
    * `[]` d. **IA per Gestione Carriera NPC:** *(Concettualizzazione in corso)*.
        * `[]` i. Definire e implementare l'azione `SEEK_JOB` per NPC disoccupati.
        * `[]` ii. Logica di `AIDecisionMaker` per la scelta della carriera (influenzata da skill, tratti, aspirazioni, istruzione).
        * `[]` iii. Il tratto `CONNECTIONS` modifica il livello di partenza. *(Classe tratto definita, integrazione in `Character.assign_job()` in corso concettuale)*.
        * `[]` iv. NPC scelgono (o viene loro assegnata) un'azione `WORKING` durante l'orario di lavoro.
        * `[]` v. Logica per tentare promozioni (basata su performance, skill, tempo nel livello, tratti). *(Concettualizzata per NPC Background nell'aggiornamento annuale)*.
    * `[]` f. **Performance Lavorativa:** *(Concettualizzata, attributo `work_performance` in `Character` e `work_school_performance_score` in `BackgroundNPCState`)*.
        * `[]` i. Definire come la performance viene calcolata e aggiornata (giornalmente/settimanalmente/mensilmente) per NPC dettagliati e di background.
        * `[]` ii. Tratti e skill influenzano la performance. *(Molti tratti già definiscono `get_job_performance_modifier` o effetti sulla performance)*.
    * `[]` g. Meccaniche di avvertimenti, retrocessioni, licenziamenti e reazioni degli NPC (influenzate da tratti).
    * `[]` h. **Lavoro Minorile e Part-time:** *(Regole definite in XXII.1.d. Eventuali permessi o registrazioni ufficiali potrebbero essere gestiti o archiviati tramite SoNet, se previsto dalla normativa)*.
    * `[]` i. **"Side Gigs" (Lavoretti Extra):** *(Concettualizzato, richiesto da tratto `CareerOriented`)*.
        * `[]` 1. Definire `ActionType` `FIND_SIDE_GIG` e `DO_SIDE_GIG`.
        * `[]` 2. Sistema per generare/offrire "side gigs" disponibili (potrebbero essere legati a skill o opportunità casuali).
        * `[]` 3. NPC con tratti rilevanti li scelgono per guadagno extra (in **Ꜳ**) /soddisfazione.
    * `[]` j. **Elenco Carriere (da definire e implementare):** (Vecchio `VIII.2`)
        * `[]` Agente Immobiliare
        * `[]` Archeologo / Curatore Museale
        * `[]` Architetto / Designer d'Interni
        * `[]` Artigiano (Falegname, Sarto, ecc.) *(Ora potenziato da `C.9` con specializzazioni)*
            * `[F_DLC_C.9]` Specializzazione: Apicoltore (`C.9.d.xv`)
            * `[F_DLC_C.9]` Specializzazione: Artigiano del Legno Certificato (`IX.e Woodworking`, `C.9.f.i.3`, `C.9.f.iii.2`)
            * `[F_DLC_C.9]` Specializzazione: Artigiano Tessile (Filatura, Tessitura, Tintura Naturale `C.9.d.ix`)
            * `[F_DLC_C.9]` Specializzazione: Casaro Artigianale (Formaggi `C.9.d.xii`)
            * `[F_DLC_C.9]` Specializzazione: Ceramista / Vasaio Artistico (`IX.e Pottery`, `C.9.f.i.5`, `C.9.f.iii.3`)
            * `[F_DLC_C.9]` Specializzazione: Cestaio / Intrecciatore Fibre Naturali (`IX.e Basket Weaving`, `C.9.f.iii.4`)
            * `[F_DLC_C.9]` Specializzazione: Cioccolatiere Artigianale (`C.9.d.xvii`)
            * `[F_DLC_C.9]` Specializzazione: Conciatore di Pelli Sostenibili (`C.9.d.viii`)
            * `[F_DLC_C.9]` Specializzazione: Distillatore (Whisky, Bourbon, Sambuca, Liquori `C.9.d.iii-v, xxxii`)
            * `[F_DLC_C.9]` Specializzazione: Erborista Preparatore / Saponificatore (`IX.e Herbalism`, `C.9.f.ii`)
            * `[F_DLC_C.9]` Specializzazione: Liutaio Artigianale (`IX.e Instrument Making`, `C.9.f.iv`)
            * `[F_DLC_C.9]` Specializzazione: Mastro Birraio (`C.9.d.ii`)
            * `[F_DLC_C.9]` Specializzazione: Micologo Coltivatore/Raccoglitore (`C.9.d.xvi`)
            * `[F_DLC_C.9]` Specializzazione: Norcino / Produttore di Salumi (`C.9.d.xiii`)
            * `[F_DLC_C.9]` Specializzazione: Pastaio Artigianale (`C.9.d.xiv`)
        * `[]` Artista (Pittore, Scultore)
        * `[]` Atleta Professionista
        * `[]` Avvocato (collegamento a `VI.1.iii.2`)
        * `[]` Barista / Mixologist (potrebbe usare prodotti da `C.9.d` come Birre, Distillati, Sciroppi)
        * `[]` Chef / Cuoco
        * `[]` Comico
        * `[]` Contadino / Allevatore `[F_DLC_C.5]` *(Ora potenziato da `C.9` con specializzazioni)*
            * `[F_DLC_C.9]` Specializzazione: Agricoltore Biologico/Sinergico
            * `[F_DLC_C.9]` Specializzazione: Allevatore Etico (per carne, latte, pelli `C.9.e`, `C.9.d.viii`)
            * `[F_DLC_C.9]` Specializzazione: Gestore Serre / Fattorie Verticali
        * `[]` DJ
        * `[]` Forze dell'Ordine / Detective
        * `[]` Influencer / Creatore di Contenuti Digitali
        * `[]` Ispettore (Sanitario, Lavoro, Ambientale) (collegamento a `XXII.8.n.i`) `[NUOVA CARRIERA SUGGERITA]`
        * `[]` Insegnante (Teacher) *(Implementata)*
        * `[]` Medico (Doctor) *(Implementata)*
        * `[]` Musicista (vari strumenti/generi)
        * `[]` Netturbino / Operatore Ecologico (collegamento a `XIII.3.a.ii`) `[NUOVA CARRIERA SUGGERITA]`
        * `[]` Politico / Servizio Civile
        * `[]` Pompiere
        * `[]` Psicologo / Terapeuta
        * `[]` Scienziato / Ricercatore
        * `[]` Scrittore / Giornalista
        * `[]` Sviluppatore Software (Software Developer) *(Definita, file carriera specifico implementato)*
        * `[]` Tatuatore
        * `[]` Uomo/Donna d'Affari / Imprenditore
        * `[]` Veterinario `[F_DLC_C.5]` *(Dipende da Sistema Animali)*
    * `[]` k. **Estensione "Total Realism" - Imprenditorialità e Gestione Aziendale NPC:**
        * `[]` i. Possibilità per NPC di avviare e gestire la propria attività... *(La registrazione ufficiale dell'attività e le relative licenze potrebbero in futuro essere gestite tramite un portale governativo dedicato alle imprese, o una sezione specializzata di SoNet. Le certificazioni personali dell'imprenditore sono in SoNet `XXIV.c.i.5`)*.
        * `[]` ii. Meccaniche semplificate per la gestione aziendale: ... prezzi (con una certa autonomia rispetto ai prezzi di **AION**, ma influenzati da essi).
        * `[]` iii. Il successo dell'attività dipende da skill...
        * `[]` iv. Le aziende NPC contribuiscono all'economia...
        * `[]` v. Questo crea percorsi di carriera non lineari...
        * `[]` vi. **Gestione delle Scorte per Negozi NPC:**
            * `[]` 1. Implementare un sistema di monitoraggio delle scorte (semplificato) per i negozi gestiti da NPC.
            * `[]` 2. La mancanza di scorte per prodotti richiesti porterà a vendite mancate e insoddisfazione dei clienti (`IV.4.c` moodlet).
        * `[]` vii. **Reportistica Semplificata per Negozi NPC:**
            * `[]` 1. Fornire agli NPC imprenditori accesso a report astratti o semplificati su vendite (in **Ꜳ**), profitti (in **Ꜳ**), e livelli di scorta.
        * `[]` viii. **Automatizzazione del Rifornimento per Negozi NPC:**
            * `[]` 1. Possibilità per i negozi NPC di impostare livelli di scorta minimi per i prodotti chiave, che triggerano ordini di rifornimento automatici o semi-automatici da **AION** (`VIII.6.2.b`) o altri fornitori.
            * `[]` 2. L'IA dell'NPC imprenditore (`IV.4`) potrebbe gestire questi parametri di riordino.
        * `[]` ix. **Feedback dei Cittadini e Reputazione dei Negozi NPC:**
            * `[]` 1. Il feedback dei clienti influenza la reputazione (`VII.9`) e il successo commerciale del negozio NPC.
            * `[]` 2. NPC con tratti come `CUSTOMER_ORIENTED` (futuro) o alte skill sociali (`IX.e Charisma`) potrebbero gestire meglio il feedback.

* **2. Sistema Fiscale e Finanze Pubbliche (basato sul Contributo al Sostentamento Civico - CSC):** `[]` `[TITOLO E SEZIONE RIVISTI]`
    * `[!]` a. Il sistema fiscale di Anthalys è strutturato per essere equo e trasparente. Si basa sul principio del **Contributo al Sostentamento Civico (CSC)**, con una progressività delle aliquote che riflette la capacità contributiva dei cittadini e delle imprese, e con meccanismi di riscossione efficienti e digitalizzati.
    * `[P]` b. **CSC-R (Componente sul Reddito Personale):**
        * `[]` i. Sistema di imposte progressive sul reddito annuo individuale (espresso in **Ꜳ**). La visualizzazione dello stato fiscale personale e il pagamento online di questa componente del CSC avvengono tramite la **Sezione Tasse e Tributi di SoNet (`XXIV.c.ii`)**.
        * `[P]` ii. **Scaglioni di Reddito e Aliquote CSC-R:** (Lista `TAX_BRACKETS_CSC_R` e `CSC_R_INCOME_EXEMPTION_THRESHOLD` definite in `settings.py`)
            * 0 - 3.000 **Ꜳ** annui: **0%** (fascia di esenzione)
            * 3.001 - 6.000 **Ꜳ** annui: **1.5%**
            * 6.001 - 12.000 **Ꜳ** annui: **3%**
            * 12.001 - 24.000 **Ꜳ** annui: **6%**
            * 24.001 - 48.000 **Ꜳ** annui: **12%**
            * 48.001 - 96.000 **Ꜳ** annui: **18%**
            * 96.001 - 144.000 **Ꜳ** annui: **24%**
            * Oltre 144.000 **Ꜳ** annui: **24%** (aliquota massima).
    * `[P]` c. **Procedure di Dichiarazione e Riscossione del CSC:**
        * `[]` i. Gestire procedure di dichiarazione dei redditi (per la Componente CSC-R) e riscossione delle varie componenti del CSC ogni 9 mesi (216 giorni), o su base annuale simulata. (`TAX_COLLECTION_PERIOD_DAYS` definito in `settings.py`)
        * `[]` ii. Le comunicazioni relative a scadenze fiscali, pagamenti dovuti, e rimborsi per il cittadino avvengono tramite notifiche e la sezione dedicata su **SoNet (`XXIV.c.viii` e `XXIV.c.ii`)**.
    * `[]` d. **Entità "Governo di Anthalys" e Gestione Finanze Pubbliche:** `[SOTTOPUNTO AMPLIATO]`
        * `[]` i. Definire classe/oggetto `AnthalysGovernment`.
        * `[]` ii. Attributo `treasury: float` (tesoreria, in **Ꜳ**) per tracciare le entrate da tutte le componenti del CSC e le uscite per i servizi.
        * `[]` iii. Tutte le componenti del CSC raccolte dagli NPC e dalle imprese confluiscono in `AnthalysGovernment.treasury`.
        * `[]` iv. I sussidi e i costi dei servizi pubblici vengono detratti da `AnthalysGovernment.treasury`.
        * `[]` v. (Avanzato) Meccaniche di bilancio statale astratto.
        * `[]` vi. **Reportistica Governativa Avanzata e Indicatori Nazionali.**
        * `[]` vii. **Politica Fiscale e di Spesa del Governo (basata sul CSC):**
            * `[!]` 1. Il governo di Anthalys utilizza attivamente le varie componenti del CSC e la spesa pubblica (`VIII.2.d.ii`, `VIII.2.d.iv`) come strumenti di politica fiscale per influenzare l'economia, redistribuire ricchezza e finanziare i servizi pubblici.
            * `[]` 2. La Componente CSC-R è progressiva per garantire equità.
            * `[]` 3. **Politica di Spesa e Incentivi Governativi:** La politica di spesa pubblica del Governo favorisce:
                * `[]` a. Investimenti strategici in: infrastrutture (`XXV`), sanità (`XXII.5`, `XXIII`), istruzione (`V`), e welfare (`VIII.3`, `XXII.4`).
                * `[]` b. **Incentivi per l’Innovazione:** Erogazione di crediti d’imposta (sulla CSC-A `VIII.2.e.iii`) e sovvenzioni dirette per ricerca e sviluppo, tecnologie verdi (`XXV.4`), e progetti innovativi.
                * `[]` c. **Agevolazioni per le Energie Rinnovabili:** Concessione di esenzioni o riduzioni fiscali e/o sussidi per l'installazione di sistemi di energia rinnovabile.
                * `[]` d. **Agevolazioni e Sostegno per il Settore Agricolo:** Erogazione di sussidi diretti e supporto tecnico/logistico ai produttori agricoli (`C.9`), con particolare attenzione alla produzione sostenibile e all'accesso ai mercati di esportazione (`C.4.e.ii`).
            * `[]` 4. **Sviluppo Economico Internazionale:** `[NUOVO PUNTO]` Le politiche economiche del governo includono anche strategie attive per:
                * `[]` a. Promuovere il commercio internazionale attraverso la negoziazione di accordi commerciali vantaggiosi (`C.4.e.ii`).
                * `[]` b. Attrarre investimenti esteri diretti, ad esempio attraverso la creazione e la regolamentazione di Zone Economiche Speciali (ZES) (`C.4.e.iii`).
    * `[]` e. **CSC-A (Componente su Attività Commerciali):** `[NOME STANDARDIZZATO E PUNTO AMPLIATO]`
        * `[]` i. Le imprese (`VIII.1.k`) sono soggette a un contributo basato sul reddito imponibile (profitti).
        * `[]` ii. Aliquota media CSC-A: 12%.
        * `[]` iii. Prevedere agevolazioni fiscali (riduzione aliquota CSC-A, crediti d'imposta) per:
            * `[]` Startup nei primi anni di attività.
            * `[]` Imprese che dimostrano investimenti significativi in innovazione tecnologica, ricerca e sviluppo, e tecnologie verdi (`VIII.2.d.vii.3.b`).
            * `[]` Imprese che implementano pratiche di sostenibilità ambientale (`XIII.1`, `XXV.4`).
        * `[]` iv. Le entrate da questa componente del CSC confluiscono in `AnthalysGovernment.treasury`.
    * `[]` f. **CSC-S (Componente su Scommesse e Giochi d'Azzardo):** `[NOME STANDARDIZZATO]`
        * `[]` i. Le vincite derivanti da scommesse (`XIX.2`), e altri giochi d’azzardo (`XIX.4`) sono soggette a un contributo.
        * `[]` ii. Aliquote progressive in base all’importo della vincita (1% - 40%).
        * `[]` iii. Esenzione per vincite inferiori a 600 **Ꜳ**.
        * `[]` iv. La ritenuta avviene alla fonte.
    * `[]` g. **CSC-P (Componente sul Patrimonio Immobiliare):** `[NOME STANDARDIZZATO]`
        * `[]` i. È previsto un contributo annuale sul possesso di proprietà immobiliari (`XVIII.5.j`).
        * `[]` ii. Calcolato in base al valore catastale (zona `XXV.1`, dimensione, caratteristiche `XXV.2`).
        * `[]` iii. Aliquote differenziate (prima casa, seconde case, immobili commerciali/industriali).
        * `[]` iv. Pagamento annuale o rateizzato tramite **SoNet (`XXIV.c.ii`)**.
    * `[P]` h. **CSC-C (Componente sul Consumo):**
        * `[]` i. Applicazione di una Componente sul Consumo del CSC sulla maggior parte dei beni e servizi venduti (tramite AION `VIII.6` che negozi fisici `XVIII.5.h`).
        * `[P]` ii. Aliquota standard CSC-C: 12%. (`CSC_C_STANDARD_RATE` definita in `settings.py`)
        * `[]` iii. Possibili aliquote ridotte o esenzioni per beni/servizi essenziali.
        * `[]` iv. La Componente CSC-C è inclusa nel prezzo finale e versata dagli esercenti.

* **3. Benefici, Sicurezza Sociale e Welfare:** `[]` `[SEZIONE AMPLIATA]` *(Dettagli normativi in XXII.4 e XXII.5)*.
    * `[]` a. Implementazione delle meccaniche di **Assicurazione Sanitaria Universale** per lavoratori e cittadini (vedi `XXII.4.a`), con gestione delle contribuzioni e accesso ai servizi essenziali (`XXII.5`) facilitato tramite **SoNet (`XXIV.c.iii`, `XXIV.c.ix`)**. (`HEALTH_INSURANCE_CONTRIBUTION_HOURS_DIVISOR`, `HEALTH_INSURANCE_MINOR_AGE_EXEMPTION_YEARS` definite in `settings.py`)
        * `[]` i. Programmi speciali di assistenza sanitaria e supporto per cittadini con disabilità o malattie croniche, integrati nella copertura universale o come benefici aggiuntivi. (Dettagli in `XXII.4.e`).
    * `[]` b. Implementazione del sistema di **Pensioni** (`XXII.4.b`), calcolate in base a stipendio medio e anni di servizio, con tassazione specifica. Gli NPC possono consultare il proprio stato pensionistico e (futuro) richiederla tramite **SoNet (`XXIV.c.ix`)**. (Costanti per calcolo pensione definite in `settings.py`)
    * `[]` c. Implementazione di **Indennità di Maternità/Paternità** (`XXII.4.c`). Le richieste e la gestione dei benefici avvengono tramite **SoNet (`XXIV.c.ix`)**.
    * `[]` d. Implementazione di **Norme su Sicurezza sul Lavoro** (`XXII.4.d`) e meccanismi di indennizzo per infortuni.
    * `[]` e. **Sostegno Specifico per Famiglie e Minori:** (Dettagli normativi in `XXII.4.f, g, h`)
        * `[]` i. Meccaniche per l'erogazione di sussidi a famiglie a basso reddito con figli a carico.
        * `[]` ii. Programmi di assistenza e supporto per genitori single (madri e padri).
        * `[]` iii. Programmi di supporto dedicati a genitori con disabilità o affetti da malattie degenerative, per aiutarli nella cura dei figli.
        * `[]` iv. Accesso a questi programmi e sussidi gestito tramite la **Sezione Welfare di SoNet (`XXIV.c.ix`)**.
    * `[]` f. Sistema di giorni di ferie accumulati e utilizzabili (come da `VIII.4` e `XXII.6`). *(Generalmente gestito a livello di datore di lavoro)*.
    * `[]` g. Bonus di fine anno o legati alla performance (in **Ꜳ**). *(Specifico del datore di lavoro)*.
    * `[]` h. Permessi per Emergenze Familiari retribuiti (come da `VIII.4` e `XXII.6`). *(Se implicati benefici statali, gestione tramite SoNet `XXIV.c.ix`)*.

* **4. Vacanze e Permessi Lavorativi:** `[]` *(Dettagli in XXII.6)*.
    * `[]` a. Implementare il sistema di vacanze e permessi. *(L'interfaccia per la gestione di questi diritti da parte del cittadino verso enti statali o per consultazione dei propri diritti legali potrebbe essere SoNet, se XXII.6 lo prevede per aspetti centralizzati)*.

* **5. Economia Globale Astratta (Molto Futuro):** `[]`
    * `[]` a. Concetto di settori economici, domanda/offerta di lavoro (che influenza la disponibilità di carriere e la facilità di trovare lavoro per gli NPC).
    * `[]` b. Eventi economici (recessioni, boom) che influenzano stipendi, disoccupazione, prezzi, e fiducia dei consumatori (NPC propensi a spendere vs risparmiare).
    * `[]` c. (Avanzato) Sistema di prezzi dinamico per beni e servizi, influenzato da domanda/offerta e eventi economici.
    * `[]` d. **Estensione "Total Realism" - Dinamiche Economiche Complesse:**
        * `[]` i. Simulazione di catene di produzione e approvvigionamento semplificate: le aziende NPC (`VIII.1.k`) necessitano di input (materie prime astratte, componenti da altre aziende NPC) per produrre beni/servizi, creando interdipendenze economiche.
        * `[]` ii. (Molto Avanzato) Introduzione di un mercato azionario simulato dove le aziende NPC più grandi possono essere quotate, con NPC (e giocatore) che possono investire.
        * `[]` iii. (Molto Avanzato) Simulazione di inflazione, tassi di interesse bancari (se banche implementate), e politiche monetarie astratte gestite dall'`AnthalysGovernment` (`VIII.2.d`) con impatto sull'economia generale (es. costo prestiti, valore risparmi).

* `[]` **6. Sistema Commerciale Centralizzato: "AION" (AI-Omnia Network / Anthalys Integrated Omnia-network)** `[SOTTOCATEGORIA PRINCIPALE AGGIORNATA]`
    * `[!]` a. **Principio Fondamentale:** Definire e implementare **AION** come la singola grande entità di import/export e piattaforma commerciale di Anthalys, operante come infrastruttura logistica e commerciale basata su IA al 100%. Centralizza il flusso di beni importati e **facilita la vendita di prodotti di cittadini/piccole imprese locali**. L'interfaccia di acquisto *e vendita C2A/B2A (Citizen/Business-to-AION)* per i cittadini è integrata esclusivamente nel portale **SoNet (`XXIV.c`)**. *(Aggiornato per includere vendita da cittadini ad AION)*
    * `[]` b. **Impatto Economico Generale e Interazioni Sistemiche:** AION deve integrarsi profondamente con l'economia esistente (`VIII.2.a`), i negozi fisici (`XVIII.5.h`), il comportamento d'acquisto *e di vendita* degli NPC (che avviene tramite SoNet `XXIV.c` e influenza AION), e le politiche governative (`VI`, `XXII`).
    * `[]` **1. Funzionamento e Struttura di AION (Backend e Operatività IA):**
        * `[]` a. **Piattaforma Tecnologica di Backend:**
            * `[]` i. AION opera tramite una complessa infrastruttura tecnologica di backend, accessibile ai cittadini produttori e consumatori solo attraverso le API esposte a **SoNet (`XXIV`)**.
            * `[]` ii. Questa piattaforma gestisce l'intero catalogo prodotti (importati e locali), i livelli di inventario, la logistica, e le transazioni B2C (via SoNet), C2A/B2A (Citizen/Business-to-AION, via SoNet), e B2B (AION-to-Business).
        * `[]` b. **Gestione Catalogo Prodotti e Approvvigionamento (IA):**
            * `[]` i. L'IA di AION gestisce un vasto e diversificato catalogo prodotti, includendo sia beni importati globalmente sia prodotti forniti da cittadini e imprese di Anthalys (`C.9`, `VIII.1.k`).
            * `[]` ii. **Approvvigionamento Globale:** L'IA seleziona e gestisce (astrattamente) i rapporti con fornitori globali (per beni non prodotti localmente), valutando criteri di etica, sostenibilità, costo, qualità e affidabilità.
            * `[]` iii. **Approvvigionamento Locale (C2A/B2A):** L'IA di AION valuta e acquista/mette in consignazione prodotti da cittadini e imprese locali attraverso la piattaforma SoNet (vedi `VIII.6.1.d`).
            * `[]` iv. **Realismo (Gestione Dinamica Catalogo):** L'IA di AION aggiorna dinamicamente il catalogo, introduce nuovi prodotti (importati o locali) basati su analisi di trend e feedback da SoNet (`XXIV.c.xi`), e gestisce la disponibilità.
        * `[]` c. **Controllo IA al 100% ("Autonomia Operativa Totale"):**
            * `[]` i. Tutte le decisioni operative interne, logistiche (`VIII.6.5`), di pricing (sia di acquisto da produttori locali/globali che di vendita ai consumatori/negozi `VIII.6.2`), gestione dell'inventario (`VIII.6.7.b`), selezione dei fornitori (globali e locali), e strategie di mercato sono gestite autonomamente dall'IA di AION.
            * `[]` ii. Interazione umana limitata a:
                * `[]` 1. Supervisione etica e regolamentare esterna (`VI`, `XXII`).
                * `[]` 2. Manutenzione hardware critica o aggiornamenti architetturali IA da tecnici esterni specializzati (eventi rari).
                * `[]` 3. Mandato iniziale e obiettivi a lungo termine definiti alla creazione dell'IA.
            * `[]` iii. **Realismo (Comportamento IA):** Simulare possibili "derive algoritmiche" o interpretazioni sub-ottimali dell'IA, specialmente di fronte a crisi o dati anomali, con potenziali effetti collaterali che richiedono intervento correttivo dall'ente di supervisione o generano dibattito.
        * `[]` d. **Piattaforma di Acquisto e Vendita per Produttori Cittadini/Locali (C2A/B2A via SoNet):** `[NUOVO PUNTO INTEGRATO]`
            * `[]` i. **AION**, tramite una sezione dedicata su **SoNet (`XXIV.c.xi` o una nuova sezione "Vendi su AION")**, offre un'interfaccia attraverso cui i cittadini produttori (artigiani `C.9`, agricoltori `C.9`, piccole imprese `VIII.1.k`) possono proporre i propri prodotti per la vendita.
            * `[]` ii. L'IA di AION valuta i prodotti proposti in base a: qualità (verificabile astrattamente o tramite campioni/certificazioni `XXII.8`), potenziale domanda (stimata dai dati di SoNet), coerenza con standard etici/sostenibili di AION, prezzo richiesto dal produttore, capacità produttiva.
            * `[]` iii. Modelli di collaborazione: AION può acquistare direttamente dai produttori (definendo prezzi di acquisto all'ingrosso equi) e/o operare come marketplace prendendo una commissione sulla vendita, gestendo comunque la logistica e la presentazione su SoNet.
            * `[]` iv. I prodotti locali approvati vengono integrati nel catalogo AION visibile ai consumatori su SoNet, distinti o promossi come "Prodotto di Anthalys".
    * `[]` **2. Politiche di Prezzi e Sconti di AION (gestite dall'IA):**
        * `[]` a. **Definizione Prezzi al Consumo (visibili su SoNet, in Ꜳ):** L'IA di AION calcola i prezzi per i consumatori finali, mirando ad accessibilità e stabilità, considerando costi (inclusi quelli di acquisto da produttori locali) e dinamiche di mercato.
        * `[]` b. **Sconti e Condizioni per Negozi Fisici Rivenditori (B2B):**
            * `[]` i. L'IA di AION gestisce un sistema B2B per i negozi fisici.
        * `[]` c. **Definizione Prezzi di Acquisto da Produttori Locali (C2A/B2A, in Ꜳ):**
            * `[]` i. L'IA di AION stabilisce i prezzi di acquisto o i termini di commissione per i prodotti forniti dai cittadini/imprese locali, cercando un equilibrio tra sostenibilità per il produttore e accessibilità per il consumatore finale. (Questo è un punto critico per il concetto di "condivisione risorse" e l'equità `VIII.6.8.a.ii`).
        * `[]` d. **Realismo - Fattori di Pricing Complessi dell'IA:** L'IA considera: costi di importazione/logistici (in **Ꜳ**), elasticità della domanda (analizzata dai dati di acquisto su SoNet), cicli di vita prodotti, tasse di importazione (in **Ꜳ**), obiettivi di profitto (in **Ꜳ**, se presenti nel mandato) vs. accessibilità, prezzi di acquisto da produttori locali, e bilanciamento con parametri di sostenibilità (`VIII.6.9.c`).
    * `[]` **3. Logistica di Consegna Avanzata di AION (al servizio di SoNet):**
        * `[]` a. **Infrastruttura Logistica per Evasione Ordini da SoNet:**
            * `[]` i. AION gestisce il sistema di spedizioni estremamente rapide (es. entro 15-60 minuti di gioco per aree urbane) per gli ordini effettuati dai cittadini tramite **SoNet (`XXIV.c.xi`)**.
            * `[]` ii. Gestione delle opzioni di consegna a domicilio o ritiro presso "Punti di Raccolta AION" locali (integrati con la mappa cittadina e SoNet).
            * `[]` iii. **Tecnologia Droni-Cargo:** Utilizzo e gestione della flotta di droni-cargo per le consegne, con IA di sciame e invisibilità radar (lore).
            * `[]` iv. **Realismo (Limitazioni Logistiche):** Introdurre (raramente) lievi ritardi a causa di meteo avverso (`I.3.f`), manutenzione droni, o congestione.
    * `[]` **4. Rapporto di AION con i Negozi Fisici (gestito dall'IA secondo direttive):**
        * `[]` a. **Fornitura e Supporto Strategico (guidato da parametri IA per equilibrio di mercato):**
            * `[]` i. L'IA di AION può essere programmata per supportare un settore retail fisico vitale, modulando sconti B2B (`VIII.6.2.b.i`) o fornendo (anonimamente) dati di mercato aggregati ai negozianti registrati per aiutarli nelle loro strategie.
        * `[]` b. **Valorizzazione dell'Esperienza d'Acquisto Fisica.** I negozi fisici offrono esperienze (prova prodotti, consulenza) che l'e-commerce via SoNet non replica direttamente.
        * `[]` c. **Realismo (Dinamiche di Mercato):** Simulare possibili tensioni o negoziazioni tra AION e negozianti riguardo ai termini B2B, e ora anche riguardo alla competizione/collaborazione con i prodotti C2A venduti direttamente tramite AION/SoNet.
    * `[]` **5. Operazioni Logistiche e Distribuzione Interne di AION (completamente automatizzata):**
        * `[]` a. **Efficienza Logistica e Automazione Totale nel Backend.**
        * `[]` b. **Impegno per la Sostenibilità nelle Operazioni (gestito e ottimizzato dall'IA):**
            * `[]` i. Selezione ottimizzata di imballaggi ecologici.
            * `[]` ii. Ottimizzazione algoritmica delle rotte di consegna.
            * `[]` iii. Gestione e promozione di programmi di riciclaggio/riutilizzo.
            * `[]` iv. **Realismo (Impatto Droni):** I droni-cargo, pur ottimizzati, hanno un impatto ambientale minimo (rumore localizzato, consumo energetico) che contribuisce al bilancio di sostenibilità.
    * `[]` **6. Magazzini Sotterranei di AION:**
        * `[]` a. **Struttura e Profondità.**
        * `[]` b. **Sicurezza e Condizioni Ambientali Controllate.**
        * `[]` c. **Realismo:** Definire scenari rari ma possibili che richiedono "accesso umano limitato" (`VIII.6.1.c.ii.2`): es. guasti catastrofici a sistemi robotici non riparabili da altri robot, audit di sicurezza imposti dall'ente di supervisione, o indagini su anomalie inspiegabili nei sistemi IA.
    * `[]` **7. Tecnologia di Monitoraggio e Gestione dei Magazzini AION (automatizzata):**
        * `[]` a. **Automazione con Robot e Droni Interni:**
            * `[]` i. La gestione delle giacenze, raccolta, imballaggio e preparazione per spedizione sono completamente automatizzate da robot e droni interni ai magazzini.
            * `[]` ii. IA avanzata per navigazione autonoma e ottimizzazione dei percorsi interni.
        * `[]` b. **Sistema di Gestione del Magazzino (WMS) Centralizzato e Real-Time:** *(Stato aggiornato a [] se la concettualizzazione del monitoraggio in tempo reale è considerata iniziata)*
            * `[]` i. Un WMS avanzato basato su IA coordina tutte le attività logistiche, traccia ogni singolo articolo **in tempo reale** dalla ricezione alla spedizione, aggiornando automaticamente e istantaneamente le giacenze e gestendo dinamicamente gli ordini in arrivo e le priorità di picking.
            * `[]` ii. Il monitoraggio in tempo reale delle scorte permette all'IA di **AION** di prendere decisioni di rifornimento (`VIII.6.1.c.i`) altamente efficienti e di minimizzare le rotture di stock o l'overstocking.
    * `[]` **8. Impatto Economico e Integrazione di Mercato di AION:**
        * `[]` a. **Simulazione dell'Integrazione con il Mercato Locale (guidata dall'IA di AION e dalle politiche di Anthalys):**
            * `[]` i. **Ruolo di AION nel Commercio:**
                * `[]` 1. **AION come Fornitore Primario:** Per molti negozi fisici (`XVIII.5.h`, `VIII.1.k`) che si riforniscono prevalentemente da **AION** (importati o aggregati da altri produttori locali).
                * `[]` 2. **AION come Piattaforma di Vendita Diretta per Produttori Locali:** Cittadini e piccole imprese (`C.9`, `VIII.1.k`) utilizzano **AION** (tramite SoNet `XXIV.c.xi`) per vendere i propri beni a un mercato più ampio, beneficiando della logistica e della visibilità della piattaforma. Questo rappresenta una forma di "condivisione di risorse commerciali".
                * `[]` 3. **AION come Rivenditore Diretto ai Cittadini:** I cittadini acquistano beni (sia importati da **AION** sia forniti da produttori locali tramite **AION**) attraverso la **Sezione Commercio di SoNet (`XXIV.c.xi`)** a prezzi ottimizzati dall'IA.
            * `[]` ii. **Implicazioni della Piattaforma Centrale "AION":** *(Riformulato)*
                * `[]` 1. Analizzare le dinamiche di **AION** come piattaforma centrale che facilita la "condivisione di risorse commerciali" (logistica, portata di mercato, base clienti) per beni importati e locali.
                * `[]` 2. Definire meccanismi di controllo governativo (`VI`, `XXII`) o parametri etici stringenti per l'IA di **AION** (`VIII.6.1.c.ii.1`) per:
                    * Assicurare termini equi e trasparenti per i cittadini/imprese che vendono i loro prodotti tramite **AION** (es. commissioni, prezzi di acquisto da AION, visibilità sulla piattaforma SoNet).
                    * Prevenire pratiche che potrebbero soffocare ingiustamente la concorrenza dei negozi fisici (che possono essere sia clienti B2B di AION sia venditori indipendenti) o la diversità produttiva locale.
                    * Garantire che **AION** operi per il benessere economico generale di Anthalys, in linea con i principi costituzionali (`XXII.A.iii`).
            * `[]` iii. **Impatto dei Prezzi Ottimizzati dall'IA sui Cittadini e sul Consumo:**
                * `[]` 1. Simulare come i prezzi "standard ottimizzati" dall'IA (`VIII.6.2.a.i`) influenzano il potere d'acquisto degli NPC (`IV.1` Bisogni, `VIII.2` Finanze) e le loro decisioni di spesa (`IV.4` IA).
                * `[]` 2. Valutare l'impatto sull'inflazione/deflazione generale dei beni di consumo nel mondo di Anthalys.
                * `[]` 3. (Avanzato) L'IA di pricing di **AION** potrebbe implementare micro-dinamiche come "saldi" intelligenti, bundling di prodotti, o prezzi dinamici (limitati) in risposta a scorte/domanda, e come gli NPC (specialmente con tratti `SAVVY_SHOPPER`) reagiscono a ciò.
            * `[]` iv. **Dinamiche di Equilibrio tra Commercio tramite AION/SoNet e Negozi Fisici Indipendenti:**
                * `[]` 1. Definire e monitorare metriche chiave per tracciare la salute del settore retail fisico rispetto alla centralità di **AION** (es. quote di mercato, tassi di apertura/chiusura negozi fisici, livelli di soddisfazione NPC per entrambe le opzioni d'acquisto).
                * `[]` 2. Implementare meccanismi di feedback (astratti o attivi) per cui i parametri dell'IA di **AION** (`VIII.6.4.a.i`) o le politiche governative di Anthalys (`VI`, `XXII.7.a` o la numerazione corretta per l'evoluzione delle normative) potrebbero essere influenzati o mirare a mantenere un certo "equilibrio di mercato" desiderato, per esempio, proteggendo i piccoli negozianti o garantendo l'accesso ai beni in aree meno servite dalla logistica dei droni.
                * `[]` 3. Valutare come l'esistenza di **AION** influenzi la tipologia e la specializzazione dei negozi fisici che riescono a prosperare (es. negozi che offrono alta specializzazione, esperienza d'acquisto unica, o servizi personalizzati non replicabili online `VIII.6.4.b`).
    * `[]` **9. Sostenibilità e Efficienza Energetica di AION (ottimizzate dall'IA):**
        * `[]` a. **Fonti di Energia Rinnovabile:**
            * `[]` i. (Lore/Concetto) L'azienda utilizza prevalentemente energie rinnovabili.
            * `[]` ii. **Realismo:** L'enorme fabbisogno energetico dei magazzini sotterranei e della flotta di droni (`VIII.6.5.b.iv`), pur coperto da rinnovabili, rappresenta un fattore significativo nel bilancio energetico complessivo di Anthalys, con possibili impatti se la produzione di energia della nazione dovesse avere problemi o essere limitata.
        * `[]` b. **Gestione Ottimizzata dei Rifiuti.**
        * `[]` c. **Realismo - Bilanciamento Efficienza vs. Sostenibilità:** L'IA di **AION** deve bilanciare i suoi obiettivi di efficienza economica/logistica con parametri di sostenibilità imposti dall'ente di supervisione o dal suo mandato etico (es. limiti massimi di emissioni per consegna, percentuali minime di imballaggi riutilizzati, sourcing etico). Il mancato rispetto potrebbe portare a sanzioni o a un danno reputazionale (se l'IA è programmata per percepire e reagire a questo).
    * `[]` **10. Sistemi di Sicurezza Avanzata dei Magazzini Sotterranei AION (gestiti da IA di sicurezza dedicata):**
        * `[]` a. **Accesso e Barriere Fisiche.**
        * `[]` b. **Sistemi di Monitoraggio e Sorveglianza Continua (H28).**
        * `[]` c. **Tecnologie Anti-Intrusione Attive.**
        * `[]` d. **Protocolli di Sicurezza e Risposta alle Emergenze.**
        * `[]` e. **Protezione dei Dati e Sicurezza Informatica Robusta.**
        * `[]` f. **Realismo - Minacce Teoriche e Pressione Continua:** Nonostante l'inespugnabilità teorica, simulare (come eventi di lore estremamente rari, notizie di background, o minacce astratte) tentativi (sempre falliti o sventati) di spionaggio industriale o cyber-attacchi ad **AION** da parte di entità esterne (se `C.4 Geopolitica` implementato) o gruppi criminali altamente sofisticati. Questo serve a sottolineare la costante pressione sulla sua sicurezza e il valore dei dati e delle tecnologie che protegge, senza necessariamente farla fallire ma aggiungendo tensione al world-building.
    * `[]` **11. Monitoraggio Performance, Reportistica Aggregata e Trasparenza (Astratta) di AION:**
        * `[]` a. L'IA di **AION** genera internamente report analitici dettagliati (vendite tramite SoNet, transazioni B2B, logistica, includendo dati sulle vendite C2A/B2A, feedback clienti da SoNet `XXIV.c.xi`, impatto ambientale) per auto-apprendimento e ottimizzazione.
        * `[]` b. Versioni aggregate e anonimizzate di questi report potrebbero essere rese disponibili all'ente di supervisione governativo (`VIII.6.1.c.ii.1`) o al pubblico di Anthalys (tramite SoNet (`XXIV.c.viii` o `XXIV.c.x`)) come forma di trasparenza.
        * `[]` c. Questi report potrebbero influenzare le politiche governative (`VI`, `XXII`).
    * `[]` **12. Sistema di Feedback dei Cittadini (tramite SoNet) e Apprendimento Adattivo dell'IA di AION:**
        * `[]` a. **Raccolta Feedback (centralizzata su SoNet):** I cittadini forniscono feedback su prodotti/servizi acquistati tramite **AION** (sia importati che da produttori locali) attraverso la **Sezione Commercio "AION" di SoNet (`XXIV.c.xi`)**.
            * `[]` i. Qualità dei prodotti acquistati da **AION**.
            * `[]` ii. Esperienza di acquisto sulla piattaforma online (integrata in SoNet).
            * `[]` iii. Efficienza e qualità del servizio di consegna tramite droni.
            * `[]` iv. Politiche di sostenibilità dell'azienda (es. imballaggi).
        * `[]` b. **Analisi IA del Feedback:** L'IA di **AION** processa i dati di feedback ricevuti da SoNet.
        * `[]` c. **Apprendimento Adattivo e Azioni Correttive da parte di AION:**
            * `[]` i. In base all'analisi, l'IA di **AION** può:
                * Ottimizzare ulteriormente il catalogo prodotti (rimuovendo articoli con feedback costantemente negativo, promuovendo quelli apprezzati - collegamento a `VIII.6.1.b`).
                * Modificare la selezione dei fornitori (`VIII.6.1.b.ii`) se i problemi di qualità sono legati a essi.
                * Suggerire miglioramenti per l'interfaccia commerciale su SoNet (se ha un canale di feedback con gli sviluppatori di SoNet).
                * Ottimizzare le procedure logistiche o di imballaggio per rispondere a criticità emerse.
            * `[]` ii. Questo crea un ciclo di miglioramento continuo guidato non solo da metriche di efficienza interna ma anche dalla soddisfazione (o insoddisfazione) degli utenti finali.
        * `[]` d. Il feedback aggregato e le azioni correttive di **AION** potrebbero essere comunicate ai cittadini tramite la sezione notizie di SoNet (`XXIV.c.viii`).

---


