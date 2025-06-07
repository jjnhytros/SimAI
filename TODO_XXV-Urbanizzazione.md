### Mini-TODO: Concettualizzazione dei Distretti di Anthalys

#### Obiettivo: Definire la struttura, l'identità e le opportunità di gioco per ciascuno dei 12 distretti di Anthalys.

#### Fase 1: Analisi Individuale dei Distretti
* `[x]` **1.a: Concetto Base e Identità**
    * `[x]` **Nome: La Cittadella**
    * `[x]` **Funzione Principale:** Amministrativo / Governativo
    * `[x]` **Descrizione e Atmosfera:** 
    > _La Cittadella è il cuore pulsante della vita civica e governativa di Anthalys. L'architettura è monumentale e solenne, con edifici imponenti che simboleggiano la stabilità e la giustizia (il Tribunale Supremo, il Parlamento). Tuttavia, non è un luogo freddo e distante. Le sue ampie piazze e i suoi viali alberati sono progettati per essere vissuti dalla comunità, ospitando cerimonie pubbliche (come il congedo militare), festività nazionali e mercati speciali. Si crea così un contrasto unico tra la formalità del potere e la vitalità della partecipazione civica. La sicurezza è sempre presente, ma discreta, per proteggere le istituzioni senza soffocare lo spirito comunitario._

* `[x]` **1.b: Location e Oggetti**
    * **LocationType Ospitate:**
        * `GOVERNOR_PALACE` (Palazzo del Governatore)
        * `PARLIAMENT_BUILDING` (Sede del Parlamento Bicamerale)
        * `COURTHOUSE` (Tribunale Supremo)
        * `CENTRAL_BANK_HQ` (Sede della Banca Centrale di Anthalys)
        * `GOVERNMENT_OFFICE` (Uffici dei vari dipartimenti/ministeri)
        * `NATIONAL_ARCHIVE` (Archivio Nazionale)
        * `CIVIC_AUDITORIUM` (Auditorium Civico per conferenze e udienze pubbliche)
    * **Oggetti Unici e Iconici del Distretto:**
        * Statue dei fondatori di Anthalys e di altre figure storiche rilevanti.
        * Un imponente "Monumento alla Costituzione" situato in una delle piazze principali.
    * Chioschi informativi SoNet dal design istituzionale, per l'accesso rapido ai servizi per il cittadino.
        * La "Fiamma Eterna della Libertà", un monumento simbolico perennemente acceso.

* `[x]` **1.c: Gameplay e Connessioni**
    * **Opportunità di Gameplay - Carriere:**
        * È il distretto d'elezione per tutte le carriere nel settore **Politico**, **Legale** (Avvocato, Giudice), e **Amministrativo/Servizio Civile**.
        * Ospita carriere specialistiche come **Archivista/Curatore** presso l'Archivio Nazionale.
    * **Opportunità di Gameplay - Azioni Specifiche:**
    * `RESEARCH_HISTORICAL_RECORDS`: Azione presso il `NATIONAL_ARCHIVE`, che potrebbe aumentare la skill `RESEARCH_DEBATE` o essere un obiettivo per un'aspirazione.
        * `ATTEND_PUBLIC_HEARING`: Azione disponibile al `CIVIC_AUDITORIUM`, per NPC con tratti come `ACTIVIST` o interessi politici, che influenza l'umore e la conoscenza civica.
        * `PROTEST_OUTSIDE_PARLIAMENT`: Azione per NPC con tratti come `ACTIVIST`, `REBELLIOUS` o con un forte malcontento verso le politiche attuali.
        * `PAY_RESPECTS_AT_MONUMENT`: Azione presso la "Fiamma Eterna" o il "Monumento alla Costituzione", che potrebbe soddisfare il bisogno `SPIRITUALITY` o `SOCIAL` (senso di appartenenza) e dare un moodlet positivo.
    * **Opportunità di Gameplay - Eventi:**
        * Luogo principale per **Eventi di Stato** (feste nazionali, parate, ecc.).
        * Teatro di **processi di alto profilo** al `COURTHOUSE`, con impatto mediatico.
        * Sede dei **discorsi del Governatore**, che attirano folle di NPC.
    * **Influenza sui Bisogni:**
        * L'atmosfera ordinata e sorvegliata potrebbe dare un **boost passivo al bisogno `SAFETY`**.
        * Generalmente **poco stimolante per il bisogno `FUN`**, a meno di eventi specifici.
    * **Connessioni:**
        * **Trasporti (XXV.3):** Ospita un **importante snodo della metropolitana** ("Piazza della  Fondazione") dove tutte e tre le linee (A, B, K) si incrociano, rendendolo il punto più accessibile della città.
        * **Flusso di NPC:** Altissima densità di **lavoratori "pendolari" durante il giorno**. Di **notte**, il distretto si svuota quasi completamente, diventando molto quieto, quasi surreale. La presenza delle forze dell'ordine diventa più visibile.
* `[x]` Discutere le **opportunità di gameplay uniche**.
* `[x]` Definire come il distretto si **collega** agli altri.
---

* `[x]` **2.a: Concetto Base e Identità**
    * `[x]` **Nome: Quartiere delle Muse**
    * `[x]` **Funzione Principale:** Culturale / Storico
    * `[x]` **Descrizione e Atmosfera:** 
        > *Un labirinto di vie acciottolate e piazze nascoste, dove il passato storico di Anthalys incontra la sua vibrante scena artistica contemporanea. Gli edifici sono un mix eclettico di facciate antiche restaurate e gallerie moderne con ampie vetrate. L'atmosfera è bohémien, intellettuale e costantemente animata: di giorno dal viavai di turisti e studenti d'arte, di sera dalla musica che fuoriesce dai piccoli locali jazz e dalle discussioni animate ai tavolini dei caffè letterari. È il rifugio per artisti, musicisti, scrittori e sognatori.*

* `[x]` **2.b: Location e Oggetti**
    * **LocationType Ospitate:**
        * `MUSEUM` (es. "Museo di Storia Naturale di Anthalys")
        * `ART_GALLERY` (Gallerie d'arte moderna e contemporanea)
        * `THEATER_VENUE` (Teatri per opere classiche e spettacoli d'avanguardia)
        * `CONCERT_HALL` (Per musica classica o artisti famosi)
        * `JAZZ_CLUB` / `MUSIC_VENUE_SMALL` (Locali piccoli per musica dal vivo)
        * `INDEPENDENT_CINEMA` (Cinema d'essai)
        * `ANTIQUE_BOOKSTORE` (Librerie antiquarie)
        * `ART_SUPPLY_STORE` (Negozi di forniture per artisti)
        * `CONSERVATORY` (Conservatorio Musicale, per la formazione)
        * `CAFE` (Caffè letterari)
    * **Oggetti Unici e Iconici del Distretto:**
        * **Murales Artistici:** Intere facciate di edifici coperte da opere di street art che cambiano periodicamente.
        * **Sculture Pubbliche:** Installazioni moderne e interattive nelle piazze.
        * **"L'Albero dei Poeti":** Un grande albero antico in una piazzetta, dove gli NPC possono compiere l'azione `AFFIGGI_POESIA`, lasciando un pensiero e leggendo quelli degli altri.
        * **Bancarelle di Artisti di Strada:** Oggetti con cui gli NPC artisti possono interagire per l'azione `VENDI_OPERE_D_ARTE`.

* `[x]` **2.c: Gameplay e Connessioni**
    * **Opportunità di Gameplay - Carriere:**
        * Il distretto principale per le carriere artistiche: `ARTIST` (Pittore), `MUSICIAN`, `WRITER`, `COMEDIAN`, `ACTOR`, `DJ`.
        * Carriere di supporto come **Curatore di Museo/Galleria**, **Critico d'Arte/Musicale** (legato al Giornalismo).
    * **Opportunità di Gameplay - Azioni Specifiche:**
        * `VISIT_MUSEUM`, `ATTEND_CONCERT`, `WATCH_PLAY`.
        * `PERFORM_ON_STREET`: Azione per musicisti/artisti per guadagnare denaro e fama.
        * `SKETCH_IN_NOTEBOOK`: Azione contestuale per NPC con tratto `ARTISTIC`, che aumenta il divertimento e la skill `PAINTING`.
        * `DISCUSS_ART`: Interazione sociale speciale disponibile solo in questo distretto.
    * **Opportunità di Gameplay - Eventi:**
        * **Festival del Cinema Indipendente**, **Inaugurazioni di Mostre d'Arte (Vernissage)**, **Festival di Musica di Strada**, **Poetry Slam**.
    * **Influenza sui Bisogni:**
        * **Alto guadagno passivo/opportunità** per i bisogni `FUN` e `CREATIVITY`.
        * Potenzialmente **rumoroso e affollato la sera** (impatto negativo su `ENERGY` o per NPC `LONER`).
    * **Connessioni:**
        * **Geografica:** Potrebbe essere **adiacente a "La Loggia del Sapere" (Distretto Universitario)**, creando un flusso naturale di studenti e professori.
        * **Trasporti:** Ben collegato dalla metropolitana (magari con una stazione decorata da artisti locali), ma con molte **Zone a Traffico Limitato (ZTL)** e vicoli stretti che incentivano l'esplorazione a piedi.
* `[x]` Discutere le **opportunità di gameplay uniche**.
* `[x]` Definire come il distretto si **collega** agli altri.
---

* `[x]` **3.a: Concetto Base e Identità**
    * `[x]` **Nome: Via Aeterna**
    * `[x]` **Funzione Principale:** Commerciale (Lusso e Mainstream) / Finanziario
    * `[x]` **Descrizione e Atmosfera:** 
        > *Via Aeterna è la vetrina scintillante del potere economico e del consumismo di Anthalys. È un canyon di grattacieli corporativi di vetro e acciaio le cui facciate sono coperte da giganteschi schermi olografici pubblicitari. Il ritmo qui è frenetico: i viali sono affollati di NPC in carriera, sempre di fretta, e di facoltosi cittadini a caccia dell'ultimo prodotto di lusso. L'atmosfera è moderna, costosa, energica ma anche leggermente impersonale e competitiva. È il simbolo del successo materiale in Anthalys.*

* `[x]` **3.b: Location e Oggetti**
    * **LocationType Ospitate:**
        * `DEPARTMENT_STORE` (Grandi Magazzini su più piani)
        * `LUXURY_SHOP` (Boutique di alta moda e gioiellerie)
        * `CORPORATE_HQ_TOWER` (Quartier Generale di grandi aziende)
        * `STOCK_EXCHANGE` (La Borsa di Anthalys, se implementata come da TODO `VIII.5.d.ii`)
        * `BANK_BRANCH` (Le filiali di punta delle principali banche commerciali)
        * `FANCY_RESTAURANT` e `ROOFTOP_BAR` (Ristoranti e bar esclusivi in cima ai grattacieli)
    * **Oggetti Unici e Iconici del Distretto:**
        * **Ologrammi Pubblicitari Giganti:** Schermi interattivi sulle facciate che mostrano pubblicità dinamiche.
        * **La Sfera di AION:** Una grande scultura cinetica o un ologramma fluttuante (magari davanti alla sede di AION, se si trova qui) che mostra flussi di dati economici globali in tempo reale (astrattamente).
        * **"Portali dei Negozi Elaborati":** Ingressi monumentali e artistici per i negozi di lusso

* `[x]` **3.c: Gameplay e Connessioni**
    * **Opportunità di Gameplay - Carriere:**
        * Il distretto principale per le carriere nel Business e nella Finanza (`BUSINESS_EXECUTIVE`, `FINANCIAL_ANALYST`).
        * Carriere nel **Marketing** e nel settore **Retail** di alto livello (`STORE_MANAGER`).
    * **Opportunità di Gameplay - Azioni Specifiche:**
        * `WINDOW_SHOPPING`: Azione a basso costo che soddisfa poco `FUN` ma potrebbe generare un moodlet "Desideroso".
        * `GO_ON_SHOPPING_SPREE`: Azione molto costosa che soddisfa molto `FUN` (specialmente per NPC `MATERIALISTIC`) ma impatta negativamente le finanze.
        * `ATTEND_BUSINESS_MEETING` e `NETWORK_AT_BAR`: Azioni specifiche per far progredire le carriere nel business.
    * **Opportunità di Gameplay - Eventi:**
        * **Lanci di nuovi prodotti** high-tech o di moda.
        * **Settimana della Moda di Anthalys (Anthalys Fashion Week).**
        * Eventi di networking esclusivi nei rooftop bar.
    * **Influenza sui Bisogni:**
        * L'ambiente frenetico e competitivo potrebbe **aumentare lo Stress** (se implementato).
        * Grandi opportunità per soddisfare `FUN` (tramite shopping e intrattenimento), ma quasi sempre a un **costo economico elevato**.
        * Potrebbe generare `Moodlet` contrastanti a seconda dei tratti: un NPC `FRUGAL` si sentirebbe a disagio, un `MATERIALISTIC` o `SPENDER` si sentirebbe euforico.
    * **Connessioni:**
        * **Geografica:** Potrebbe essere **adiacente a "La Cittadella"** (per simboleggiare la vicinanza tra potere economico e politico) e al **"Porto di Levante"** (da cui arrivano le merci).
        * **Trasporti:** Attraversato da una delle linee principali della metropolitana (es. Linea B Est-Ovest), con stazioni moderne e piene di schermi pubblicitari. Le strade principali sono larghe ma trafficate.
* `[x]` Discutere le **opportunità di gameplay uniche**.
* `[x]` Definire come il distretto si **collega** agli altri.
---

* `[x]` **4.a: Concetto Base e Identità**
    * `[x]` **Nome: Complesso della Quercia Bianca**
    * `[x]` **Funzione Principale:** Sanitario / Ricerca Medica
    * `[x]` **Descrizione e Atmosfera:** 
        > *L'antitesi del caos di Via Aeterna. Il Complesso della Quercia Bianca è un'oasi di tranquillità e speranza, interamente dedicata alla cura e alla ricerca. L'architettura è moderna, funzionale e progettata per essere rassicurante, con ampie vetrate, materiali naturali come legno e pietra, e una perfetta integrazione con la natura. Ogni edificio è circondato da giardini terapeutici e percorsi accessibili per la convalescenza. L'atmosfera è quieta, pulita e ordinata, con un traffico veicolare limitato a navette elettriche silenziose.*

* `[x]` **4.b: Location e Oggetti**
    * **LocationType Ospitate:**
        * `HOSPITAL` (Ospedale Centrale di Anthalys)
        * `CHILDREN_HOSPITAL` (Ospedale Pediatrico specializzato)
        * `ONCOLOGY_HOSPITAL` (Centro Oncologico di Eccellenza)
        * `GERIATRIC_HOSPITAL` (Ospedale Geriatrico)
        * `MENTAL_HEALTH_CLINIC` (Clinica per la Salute Mentale, con uffici per Psicologi/Terapeuti)
        * `REHABILITATION_CENTER` (Centro di Riabilitazione Fisioterapica)
        * `VETERINARY_CLINIC` (Grande Clinica Veterinaria centrale, se si implementa il DLC Animali)
        * `PHARMACY` (Una grande farmacia centrale aperta 28h)
        * `BLOOD_DONATION_CENTER` (Centro Donazioni Sangue)
    * **LocationType Ospitate (Divisione Campus G.A.O.):**
        * `GAO_RESEARCH_INSTITUTE`: Il cuore del campus, con i laboratori di ricerca più avanzati.
        * `UNIVERSITY_LECTURE_HALL_SCIENCE`: Aule specializzate per le materie scientifiche.
        * `UNIVERSITY_LIBRARY_SCIENCE`: Biblioteca specializzata in testi medici e scientifici.
        * `SCIENCE_LAB`, `ENGINEERING_LAB` (Biomedical/Robotics).
        * `UNIVERSITY_DORMITORY_GAO`: Dormitori per gli studenti e i ricercatori della G.A.O.
    * **Oggetti Unici e Iconici del Distretto:**
        * **Giardini Terapeutici:** Aree verdi con piante specifiche che potrebbero dare un piccolo moodlet positivo ("Rilassato") agli NPC che vi passeggiano.
        * **"Monumento al Personale Sanitario":** Una scultura che celebra il lavoro di medici e infermieri.
        * **Navette Elettriche Autonome:** Veicoli a bassa velocità che trasportano silenziosamente personale e pazienti tra i vari edifici del complesso.
        * **Stazioni di Disinfezione:** Oggetti interattivi sparsi per il distretto con cui gli NPC possono usare l'azione `DISINFECT_HANDS` per un piccolo boost all'igiene.

* `[x]` **4.c: Gameplay e Connessioni**
    * **Opportunità di Gameplay - Carriere:**
        * È il distretto per tutte le carriere mediche: `DOCTOR`, `SURGEON`, `PSYCHOLOGIST`, `MEDICAL_RESEARCHER`, `GENETICIST`, `VETERINARIAN`.
    * **Opportunità di Gameplay - Azioni Specifiche:**
        * Tutti gli NPC malati verranno qui per le azioni `GET_TREATMENT` o `BE_HOSPITALIZED`.
        * `VISIT_SICK_NPC`: Azione per NPC che vanno a trovare amici o familiari ricoverati.
        * `ATTEND_THERAPY_SESSION`: Azione per NPC che seguono un percorso di salute mentale.
        * `DONATE_BLOOD`: Azione civica che dà un forte moodlet positivo ("Orgoglioso di Aver Aiutato").
    * **Opportunità di Gameplay - Eventi:**
        * Eventuali (rari) focolai di malattie che aumentano drasticamente l'attività e lo stress nel distretto.
        * Campagne di sensibilizzazione sanitaria, di vaccinazione o di donazione del sangue.
        * Annunci di importanti scoperte mediche dalla G.A.O. che generano notizie e discussioni in tutta la città.
    * **Influenza sui Bisogni:**
        * Generalmente un luogo tranquillo, ma può generare `STRESS` o tristezza per chi è malato o in visita.
        * Non è un luogo per il bisogno `FUN`. Un NPC sano che si trova qui senza un motivo specifico (lavoro, visita) potrebbe annoiarsi rapidamente.
    * **Connessioni:**
        * **Geografica:** Potrebbe essere situato in una **zona leggermente periferica ma facilmente accessibile**, per garantire quiete ma anche un rapido accesso in caso di emergenza.
        * **Trasporti:** Deve avere una **fermata della metropolitana dedicata** ("Ospedale Centrale") e un'eccellente connessione con le principali arterie stradali per le ambulanze. Il traffico interno di veicoli privati è quasi assente.
        * **Flusso di NPC:** Un flusso costante ma ordinato di personale medico, pazienti e visitatori.
* `[x]` Discutere le **opportunità di gameplay uniche**.
* `[x]` Definire come il distretto si **collega** agli altri.
---

* `[x]` **5.a: Concetto Base e Identità**
    * `[x]` **Nome: La Loggia del Sapere**
    * `[x]` **Funzione Principale:** Educativo / Universitario
    * `[x]` **Descrizione e Atmosfera:** 
        > *Situato su una suggestiva penisola che si affaccia sul grande lago, questo vasto e verdeggiante campus è leggermente isolato dal trambusto della città, favorendo un'atmosfera di studio e contemplazione. L'architettura è un affascinante mix di antiche aule ricoperte d'edera e modernissimi laboratori di vetro e metallo. Il distretto brulica di NPC `YOUNG_ADULT`, pieni di energia intellettuale e aspirazioni. Il sottofondo sonoro è un misto di chiacchiericcio vivace proveniente dai caffè, il rintocco di una torre campanaria e il silenzio concentrato delle biblioteche.*

* `[x]` **5.b: Location e Oggetti**
    * **LocationType Ospitate:**
        * `UNIVERSITY_FACULTY_LAW` (Facoltà di Giurisprudenza)
        * `UNIVERSITY_FACULTY_ARTS` (Facoltà di Lettere e Filosofia)
        * `UNIVERSITY_FACULTY_ECONOMICS` (Facoltà di Economia e Scienze Sociali)
        * `LECTURE_HALL` (Aule Magne per lezioni importanti)
        * `SCIENCE_LAB` (Laboratori Scientifici)
        * `ENGINEERING_LAB` (Laboratori di Ingegneria/Robotica)
        * `DORMITORY` (Dormitori Studenteschi)
        * `UNIVERSITY_LIBRARY` (Grande Biblioteca Universitaria)
        * `STUDENT_UNION_BUILDING` (Edificio dell'Unione Studentesca, con bar e aree comuni)
        * `PERFORMING_ARTS_STUDIO` (Studi per teatro, danza e musica)
        * `UNIVERSITY_LIBRARY_HUMANITIES` (Grande Biblioteca Umanistica)
        * `STUDENT_UNION_BUILDING`
        * `SPORTS_FIELD_UNIVERSITY` (Campi sportivi universitari)
        * `CAMPUS_CAFE` / `UNIVERSITY_BOOKSTORE`
    * **Oggetti Unici e Iconici del Distretto:**
        * **"La Statua del Pensatore"** o un monumento a un grande filosofo/giurista di Anthalys.
        * **Bacheche Digitali Interattive:** Oggetti pieni di annunci per club studenteschi, eventi accademici, e lavoretti part-time.
        * **Aule Olografiche:** Oggetti speciali per lezioni avanzate o interattive.
        * **Distributori automatici di caffè e "smart food"** per gli studenti che tirano tardi.
        * **"Il Muro del Dibattito":** Una grande lavagna pubblica dove gli NPC possono lasciare messaggi e argomentazioni (azione `POST_OPINION`), stimolando interazioni.
        * **Angoli Studio all'Aperto:** Aree tranquille con panchine e tavoli con vista sul lago.

    * `[x]` **5.c: Gameplay e Connessioni**
        * **Opportunità di Gameplay - Carriere:**
        * La sede per le carriere accademiche in ambito non-scientifico: **Professori** di legge, storia, arte, ecc.
        * Gli studenti qui si preparano per carriere come `LAWYER`, `POLITICIAN`, `ARTIST`, `WRITER`, `JOURNALIST`, `ECONOMIST`.

    * **Opportunità di Gameplay - Azioni Specifiche:**
        * `ATTEND_DEBATE` (Partecipa a Dibattito)
        * `PRACTICE_INSTRUMENT` negli studi musicali.
        * `WRITE_ESSAY` (Scrivi Saggio) nelle biblioteche o caffè.
    * **Opportunità di Gameplay - Eventi:**
        * **Inizio dell'Anno Accademico**, **Sessioni d'Esame** (periodo di stress per gli studenti NPC), **Cerimonie di Laurea**, **Conferenze Accademiche**, **Feste dei Dormitori**.
    * **Influenza sui Bisogni:**
        * **Alto stimolo per il bisogno `LEARNING`** (se implementato).
        * Potrebbe essere **stressante durante gli esami**.
        * Molte opportunità per il bisogno `SOCIAL`, ma anche per attività solitarie (studio).

    * **Connessioni:**
        * **Geografica:** Adiacente al **"Quartiere delle Muse" (Distretto 2)**, il collegamento naturale per gli studenti di arte e spettacolo.
        * **Trasporti:** Fermata della metropolitana "Università" e servizio di traghetti che lo collega sia a "Via Aeterna" (per gli studenti di economia) sia alla "Cittadella" (per gli studenti di legge).
* `[x]` Discutere le **opportunità di gameplay uniche**.
* `[x]` Definire come il distretto si **collega** agli altri.
---

* `[x]` **6.a: Concetto Base e Identità**
    * `[x]` **Nome: Porto di Levante**
    * `[x]` **Funzione Principale:** Industriale / Logistico / Portuale
    * `[x]` **Descrizione e Atmosfera:** 
        > *Il motore instancabile dell'economia di Anthalys, attivo 28 ore su 28. Il Porto di Levante è un distretto prettamente funzionale, situato lungo la costa est del grande lago. Il paesaggio è dominato da imponenti gru che caricano e scaricano navi cargo, dalle file ordinate di container di AION e da moderni stabilimenti industriali non inquinanti. L'atmosfera è operosa e rumorosa, un sottofondo costante di macchinari, sirene di navi e veicoli automatizzati. Non è un luogo per turisti, ma il centro vitale da cui le merci entrano ed escono dalla città.*

* `[x]` **6.b: Location e Oggetti**
    * **LocationType Ospitate:**
        * `AION_WAREHOUSE` (Punto di accesso ai magazzini sotterranei di AION)
        * `CARGO_DOCKS` (Banchine di carico/scarico merci)
        * `FACTORY` (Fabbriche di vario tipo, es. tessili, elettroniche, assemblaggio)
        * `SPECIAL_ECONOMIC_ZONE` (ZES, un'area speciale all'interno del distretto)
        * `CUSTOMS_OFFICE` (Ufficio Doganale)
        * `LOGISTICS_HUB` (Centri di smistamento merci)
        * `SHIPYARD` (Cantiere Navale per costruzione e riparazione)
        * `WORKERS_CANTEEN` (Mensa per i lavoratori del porto)

    * **Oggetti Unici e Iconici del Distretto:**
        * **Bracci di Carico Automatizzati:** Oggetti animati di grandi dimensioni che si muovono lungo le banchine.
        * **Container AION:** Oggetti statici impilati con il logo di AION.
        * **Pannelli Olografici Portuali:** Mostrano informazioni (simulate) su arrivi, partenze e stato delle merci.
        * **Sistemi di Filtraggio dell'Acqua:** Grandi impianti visibili lungo le banchine, che purificano l'acqua usata nei processi industriali/portuali prima di reimmetterla nel lago.

* `[x]` **6.c: Gameplay e Connessioni**
    * **Opportunità di Gameplay - Carriere:**
        * Il distretto per le carriere industriali e logistiche: `INDUSTRIAL_WORKER`, `LOGISTICS_MANAGER`, `DOCK_WORKER` (Operaio Portuale), `SHIP_CAPTAIN`, `CUSTOMS_OFFICER` (Doganiere).
        * Carriere tecniche come `MECHANICAL_ENGINEER`.

    * **Opportunità di Gameplay - Azioni Specifiche:**
        * `OPERATE_CRANE` (Manovra Gru), `LOAD_CARGO`, `MANAGE_INVENTORY`.
        * `REPAIR_SHIP` (presso lo `SHIPYARD`).
        * `INSPECT_CONTAINER` (per i doganieri).

    * **Opportunità di Gameplay - Eventi:**
        * Arrivo di una nave cargo speciale con merci rare o esotiche.
        * Un (raro) incidente industriale che richiede l'intervento dei servizi di emergenza.
        * Scioperi o manifestazioni dei lavoratori (se implementato).
        * Annuncio dell'apertura di una nuova fabbrica o dell'espansione della ZES.

    * **Influenza sui Bisogni:**
        * **Impatto negativo sull'attributo** `ENVIRONMENT` di un lotto o sull'umore di un NPC sensibile (nonostante le tecnologie eco-compatibili, è pur sempre un'area industriale).
        * **Quasi nessuna opportunità per il bisogno** `FUN`.
        * Il lavoro qui potrebbe **ridurre il bisogno** `ENERGY` **più velocemente** a causa della natura fisica o stressante.

    * **Connessioni:**
        * **Geografica:** Situato sulla **costa est** della città. Potrebbe essere collegato tramite **autostrade dirette per il trasporto merci** alla **"Via Aeterna"** per rifornire i negozi.
        * **Trasporti:** Una **linea della metropolitana dedicata ai lavoratori** con una o più fermate ("Porto di Levante", "Zona Industriale"). Il trasporto principale è via acqua o su rotaia/gomma per le merci.
        * **Flusso di NPC:** Quasi esclusivamente **lavoratori**, con turni che coprono tutte le 28 ore. Praticamente quasi nessun turista o residente di altri quartieri, a meno che non lavorino qui.

* `[x]` Discutere le **opportunità di gameplay uniche**.
* `[x]` Definire come il distretto si **collega** agli altri.
---

* `[x]` **7.a: Concetto Base e Identità**
    * `[x]` **Nome: Giardini Sospesi**
    * `[x]` **Funzione Principale:** Ricreativo / Verde Pubblico
    * `[x]` **Descrizione e Atmosfera:** 
        > *Il polmone verde e il cuore ricreativo di Anthalys. I "Giardini Sospesi" non sono solo un parco, ma un capolavoro di ingegneria paesaggistica, con colline artificiali, percorsi che si snodano su più livelli e terrazze panoramiche. È un'oasi di tranquillità dove il ronzio della metropoli è sostituito dal canto degli uccelli. È il luogo preferito dai cittadini per rilassarsi, fare sport, socializzare e riconnettersi con la natura, **offrendo ampi spazi sia all'aperto che al coperto per essere vissuto con qualsiasi condizione meteorologica.*

* `[x]` **7.b: Location e Oggetti**
    * **LocationType Ospitate:** _Nota: Queste sono "micro-locazioni" all'interno del distretto-parco_
        * `CENTRAL_PARK` (L'area generica del parco)
        * `BOTANICAL_GARDEN` (Giardino Botanico con una grande serra per piante esotiche)
        * `AMPHITHEATER` (Un anfiteatro all'aperto per concerti ed eventi estivi)
        * `COMMUNITY_GARDEN` (Orti Comunitari gestiti dai cittadini)
        * `LAKE_CAFE` (Un caffè con tavolini sulla riva del lago interno al parco)
        * `PLAYGROUND_LARGE` (Una grande e moderna area giochi per bambini)
        * `DOG_PARK` (Area recintata e attrezzata per cani)
        * `SKATE_PARK`

    * **Oggetti Unici e Iconici del Distretto:**
        * **Lago Noleggiabile:** Un lago centrale con un molo dove gli NPC possono usare l'azione `RENT_A_ROWBOAT` (Noleggia una barca a remi).
        * **Grande Serra Pubblica:** All'interno del `BOTANICAL_GARDEN`, non solo ospita piante esotiche ma funge da **grande spazio pubblico al coperto**, con panchine, piccole fontane e forse un caffè interno. È una destinazione popolare durante le giornate di pioggia o freddo.
        * **Padiglioni e Gazebo:** Strutture eleganti con tettoia, sparse per il parco. Offrono riparo dalla pioggia o dal sole e sono luoghi ideali per picnic o per musicisti di strada.
        * **Anfiteatro con Copertura Parziale:** L'anfiteatro ha una grande e iconica copertura a "conchiglia" che protegge il palco e parte delle sedute, permettendo lo svolgimento di eventi anche con tempo incerto.
        * **Aree Picnic Attrezzate:** Oggetti "griglia pubblica" e "tavolo da picnic" con cui gli NPC possono interagire.
        * **Labirinto di Siepi:** Un classico labirinto vegetale esplorabile.
        * **Punti Panoramici:** "Telescopi" o piattaforme specifiche sulle colline più alte del parco.

* `[x]` **7.c: Gameplay e Connessioni**
    * **Opportunità di Gameplay - Carriere:**
        * `GARDENER` (Giardiniere del parco, responsabile della manutenzione)
        * `BOTANIST` (Botanico, che lavora al `BOTANICAL_GARDEN`)
        * `PARK_RANGER` (Guardia del parco, garantisce sicurezza e rispetto delle regole)
        * Possibili lavori part-time durante gli eventi (venditori ambulanti, staff).

    * **Opportunità di Gameplay - Azioni Specifiche:**
        * `GO_FOR_A_JOG`, `HAVE_A_PICNIC`, `DO_YOGA_IN_THE_PARK`.
        * `TEND_COMMUNITY_GARDEN_PLOT` (Azione per chi ha un lotto negli orti comunitari, aumenta skill `GARDENING`).
        * `WATCH_OUTDOOR_CONCERT` (Azione disponibile durante gli eventi all'anfiteatro).
        * `SHELTER_FROM_RAIN`: Azione reattiva dove gli NPC nel parco, all'inizio di una pioggia, cercheranno automaticamente riparo sotto i padiglioni, nella serra o nel caffè sul lago, continuando a socializzare lì.

    * **Opportunità di Gameplay - Eventi:**
        * **Concerti** e **Spettacoli Teatrali** all'anfiteatro.
        * **Festival Stagionali** (es. "Festa della Fioritura").
        * **Maratona di Anthalys**, il cui percorso attraversa il parco.

    * **Influenza sui Bisogni:**
        * **Il luogo migliore per soddisfare il bisogno** FUN **in modo gratuito o a basso costo.**
        * Molte opportunità per il bisogno `SOCIAL` (picnic, incontri casuali, aree giochi).
        * Alto potenziale per `FUN` e `SOCIAL` in ogni condizione meteo, grazie alle aree coperte.
        * **Ottimo per ridurre lo Stress** e aumentare il `COMFORT` (se il meteo è favorevole), dando moodlet come "Rinvigorito" o "A Contatto con la Natura".
        * Ottimo per ridurre lo Stress.

    * **Connessioni:**
        * **Geografica:** Posizionato **centralmente**, per fungere da cuscinetto e punto di collegamento tra diversi distretti (es. La Cittadella, Quartiere delle Muse, Via Aeterna, e un distretto residenziale).
        * **Trasporti:** Circondato da **fermate della metropolitana su più lati** per un facile accesso da tutta la città. Al suo interno, il traffico veicolare è assente, dominato da una fitta rete di percorsi pedonali e ciclabili.
        * **Flusso di NPC:** Molto affollato durante i giorni di riposo e le ore pomeridiane/serali se il tempo è bello. Il tipo di NPC varia a seconda dell'area (famiglie vicino al `PLAYGROUND`, giovani allo `SKATE_PARK`, NPC `ACTIVE` sui percorsi da jogging, ecc.). **L'uso delle aree coperte aumenta drasticamente durante il maltempo**, creando scene di socializzazione più concentrate e intime.

* `[x]` Discutere le **opportunità di gameplay uniche**.
* `[x]` Definire come il distretto si **collega** agli altri.
---

* `[x]` **8.a: Concetto Base e Identità**
    * `[x]` **Nome: Borgo Antico / Le Terrazze**
    * `[x]` **Funzione Principale:** Residenziale Esclusivo (Storico e Moderno)
    * `[x]` **Descrizione e Atmosfera:** 
        > *Arroccato su una collina panoramica che domina il lago e parte della città, il Borgo Antico è il quartiere del prestigio e della ricchezza di Anthalys. È diviso in due aree distinte: il **Borgo Antico** vero e proprio, un dedalo di vie strette e tortuose dove ville storiche sono celate da alte mura e giardini secolari, emanando un'atmosfera di privacy assoluta e "vecchia ricchezza"; e **Le Terrazze**, un sottoborgo aggrappato ai pendii più scoscesi, caratterizzato da un'architettura più moderna, con lussuosi appartamenti dotati di immense vetrate e piscine a sfioro che si affacciano sulla città. L'intero distretto è estremamente quieto, esclusivo e privato.*

* `[x]` **8.b: Location e Oggetti**
    * **LocationType (Borgo Antico - area storica):**
        * `RESIDENTIAL_VILLA` (Ville storiche e appartate)
        * `RESIDENTIAL_LUXURY_CONDO_SMALL` (Un condominio storico esclusivo con pochi appartamenti di lusso, in un palazzo restaurato).
        * `EXCLUSIVE_HEALTH_CLUB` (Un club privato e discreto per i residenti)
        * `ANTIQUE_BOOKSTORE` (Una piccola e preziosa libreria antiquaria)

    * **LocationType (Le Terrazze - area moderna):**
        * `RESIDENTIAL_LUXURY_APT` (Moderni complessi di appartamenti di lusso)
        * `PRIVATE_ART_GALLERY` (Piccole gallerie d'arte contemporanea, su appuntamento)
        * `GOURMET_FOOD_STORE` (Un negozio di specialità alimentari internazionali)
        * `ROOFTOP_BAR` (Un bar esclusivo con vista panoramica)

    * **Oggetti Unici e Iconici del Distretto:**
        * **Funicolare Panoramica:** Un oggetto-veicolo che collega le diverse altitudini del distretto, con una fermata intermedia per "Le Terrazze".
        * Cancelli in ferro battuto elaborati (nel Borgo Antico).
        * Infinity pools e pareti di vetro (a Le Terrazze).
        * Placche storiche sugli edifici.
        * Auto di lusso d'epoca e moderne.

* `[x]` **8.c: Gameplay e Connessioni**
    * **Opportunità di Gameplay - Carriere:**
        * Dimora per gli NPC al vertice della loro carriera.
        * Carriere di servizio di lusso: `BUTLER`, `PERSONAL_CHEF`, `LANDSCAPE_DESIGNER`, `GALLERY_OWNER`.

    * **Opportunità di Gameplay - Dinamiche Sociali:**
        * Questa divisione crea una potenziale **dinamica sociale tra "vecchia" e "nuova" ricchezza**. Gli NPC del Borgo Antico potrebbero essere più `SNOB` e tradizionalisti, mentre quelli de Le Terrazze più `MATERIALISTIC` e moderni.
        * Eventi e feste nelle due zone potrebbero avere "temi" e liste di invitati molto diversi, creando circoli sociali distinti.

    * **Opportunità di Gameplay - Azioni Specifiche:**
        * `HOST_EXCLUSIVE_DINNER_PARTY`: Azione per NPC residenti per aumentare lo status sociale e le relazioni.
        * `ADMIRE_THE_VIEW`: Azione disponibile presso i punti panoramici (`SCENIC_LOOKOUT_POINT`) e dalle terrazze delle abitazioni, che soddisfa `FUN` e riduce lo stress.
        * `GO_FOR_A_SCENIC_DRIVE`: Azione che un NPC potrebbe compiere con la sua auto di lusso per divertimento.
        * Azioni legate alla gestione del patrimonio e degli investimenti (interazione con SoNet da una `Location` domestica).

    * **Opportunità di Gameplay - Eventi:**
        * **Feste Private Esclusive:** Eventi su invito nelle ville o negli attici, difficilmente accessibili per NPC esterni a quella cerchia sociale.
        * **Raccolte Fondi di Beneficenza:** Eventi di gala organizzati dai residenti più influenti.
        * **Tour dei Giardini Storici:** Evento stagionale raro e su prenotazione.

* **Influenza sui Bisogni:**
    * **Altissimo** `ENVIRONMENT` e `SAFETY` percepiti, che potrebbero rallentare il decadimento di alcuni bisogni legati allo stress.
    * Per i residenti, fornisce un alto livello di `COMFORT` e soddisfazione.
    * Per i visitatori (se riescono ad entrare), potrebbe generare `Moodlet` contrastanti a seconda dei loro tratti: "Ammirato", "Invidioso" (per NPC `JEALOUS` o `MATERIALISTIC`), o "Fuori Posto" (per NPC `SHY` o con poche finanze).

    * **Dinamiche Sociali:**
        * La divisione tra **Borgo Antico** (_"vecchia ricchezza"_) e **Le Terrazze** (_"nuova ricchezza"_) può generare dinamiche di snobismo, rivalità o alleanza tra le famiglie residenti.

    * **Connessioni:**
        * La **Funicolare** diventa un elemento di connessione interna cruciale tra le due sotto-zone e il resto della città ai piedi della collina.
        * Il flusso di NPC rimane basso, ma ora è anche segmentato tra i residenti delle due aree.

* `[x]` Discutere le **opportunità di gameplay uniche**.
* `[x]` Definire come il distretto si **collega** agli altri.
---

* `[x]` **9.a: Concetto Base e Identità**
    * `[x]` **Nome: Solara**
    * `[x]` **Funzione Principale:** Residenziale (Moderno / Eco-sostenibile / Comunitario)
    * `[x]` **Descrizione e Atmosfera:** 
        > *Solara è l'esperimento di vita urbana sostenibile di Anthalys diventato realtà. È un quartiere dove la tecnologia e la natura coesistono in armonia. L'architettura è all'avanguardia, con edifici a basso impatto energetico adornati da pareti verdi verticali e tetti giardino. L'energia è prodotta localmente da pannelli solari e micro-turbine eoliche silenziose. L'atmosfera è infusa da un forte senso di comunità: gli spazi sono progettati per incoraggiare l'interazione, con cortili condivisi, orti urbani e laboratori di quartiere. Il traffico privato è quasi inesistente, sostituito da un silenzioso ronzio di biciclette e navette elettriche.*

* `[x]` **9.b: Location e Oggetti**
    * **LocationType Ospitate:**
        * `RESIDENTIAL_ECO_HOUSE` (Case unifamiliari intelligenti)
        * `RESIDENTIAL_ECO_CONDO_MEDIUM` (Edifici di medie dimensioni con 10-20 unità abitative, tetti giardino e servizi condivisi).
        * `RESIDENTIAL_ECO_CONDO_LARGE` (Un grande complesso residenziale con decine di unità, che potrebbe integrare al suo interno una fattoria verticale e un `COMMUNITY_HUB`).
        * `COMMUNITY_HUB` (Un edificio centrale con un laboratorio "makerspace", una biblioteca di quartiere e sale riunioni)
        * `ORGANIC_CAFE` (Un caffè che serve prodotti a km 0, magari dagli orti del distretto)
        * `ZERO_WASTE_STORE` (Un negozio "alla spina" dove i prodotti vengono venduti senza imballaggi)
        * `URBAN_FARM` (Fattorie verticali integrate negli edifici per la produzione alimentare locale)
        * `CAR_SHARING_STATION` (Stazioni per il car sharing elettrico)

    * **Oggetti Unici e Iconici del Distretto:**
        * **Pannelli Solari** e **Tetti Verdi:** Visibili su quasi ogni edificio.
        * **Compostatori Comunitari:** Oggetti interattivi dove i residenti portano i loro rifiuti organici.
        * **"Smart Bins":** Cestini intelligenti che ottimizzano la raccolta e dannp Punti Influenza Civica (PIC).
        * **Stazioni di Ricarica per Veicoli Elettrici:** Oggetti dal design moderno e integrato.
        * **Makerspace Tools:** Oggetti come stampanti 3D o banchi da lavoro nel `COMMUNITY_HUB` con cui gli NPC possono interagire.

* `[x]` **9.c: Gameplay e Connessioni**
    * **Opportunità di Gameplay - Carriere:**
        * Attrae NPC che lavorano in settori high-tech e sostenibili: `SOFTWARE_DEVELOPER`, `ENGINEER` (specialmente ambientale/energetico), `URBAN_PLANNER`, e molte carriere **freelance** o con **lavoro da remoto**.

    * **Opportunità di Gameplay - Azioni Specifiche:**
        * `ATTEND_COMMUNITY_WORKSHOP`: Partecipare a laboratori su riciclo, giardinaggio, riparazioni, ecc. nel `COMMUNITY_HUB`.
        * `BUY_BULK_GOODS`: Fare la spesa allo `ZERO_WASTE_STORE`.
        * Aumenta la propensione degli NPC residenti a compiere azioni come `RECYCLE_WASTE` e `TEND_COMMUNITY_GARDEN`.

    * **Opportunità di Gameplay - Eventi:**
        * **Mercato dei Produttori Locali (Farmer's Market)** settimanale.
        * **"Repair Café":** Evento comunitario dove gli NPC si aiutano a vicenda a riparare oggetti rotti (aumenta skill `HANDINESS`).
        * **Feste di Quartiere** nei cortili e spazi comuni.

    * **Influenza sui Bisogni:**
        * Altissimo `ENVIRONMENT` score.
        * Forte potenziale per il bisogno `SOCIAL` grazie agli spazi e alle attività comunitarie.
        * Potrebbe generare `Moodlet` unici come "Fiero della mia Comunità" o "Vivere Sostenibile".

    * **Connessioni:**
        * **Geografica:** Potrebbe essere situato vicino alla **"Loggia del Sapere" (Distretto 5)** per ospitare professori e ricercatori, e al **"Porto di Levante" (Distretto 6)** per i lavoratori del settore tecnologico delle ZES.
        * **Trasporti:** Il traffico di veicoli privati è fortemente disincentivato o vietato. È servito da una **linea di tram e metropolitana** leggera efficiente. Al suo interno, il movimento primario è a piedi, in bicicletta o con navette elettriche a chiamata.
        * **Flusso di NPC:** Principalmente residenti. Pochi turisti, a meno che non sia un "modello" di quartiere da visitare in tour guidati. Il flusso di persone è costante ma rilassato, con molta attività nelle aree comuni.

* `[x]` Discutere le **opportunità di gameplay uniche**.
* `[x]` Definire come il distretto si **collega** agli altri.
---

* `[x]` **10.a: Concetto Base e Identità**
    * `[x]` **Nome: Nido del Fiume**
    * `[x]` **Funzione Principale:** Residenziale (Familiare / Suburbano)
    * `[x]` **Descrizione e Atmosfera:** 
        > *Il "Nido del Fiume" è il volto della tranquilla vita suburbana di Anthalys. È un ampio quartiere periferico, sviluppato attorno alle anse di un fiume minore, che offre un ambiente sicuro e ideale per crescere una famiglia. L'architettura è piacevole e uniforme, composta da un mix di case unifamiliari, villette a schiera e piccole palazzine residenziali, quasi tutte con piccoli giardini privati o spazi verdi comuni. L'atmosfera è rilassata e amichevole; le strade sono piene di bambini che giocano dopo la scuola e vicini che chiacchierano oltre le staccionate. Il suono predominante è quello della vita quotidiana, mescolato al dolce scorrere del fiume.*

* `[x]` **10.b: Location e Oggetti**
    * **LocationType Ospitate:**
        * `RESIDENTIAL_HOUSE_MEDIUM` (Casa unifamiliare di medie dimensioni con giardino)
        * `RESIDENTIAL_HOUSE_LARGE` (Casa unifamiliare più grande, per famiglie numerose)
        * **Unità Abitative a Schiera:**
            * `RESIDENTIAL_TOWNHOUSE` (Villette a schiera, una soluzione comune per le famiglie)
        * **Unità Abitative Plurifamiliari:**
            * `RESIDENTIAL_APARTMENT_BUILDING_SMALL` (Una piccola palazzina di 2-3 piani con 6-8 appartamenti, situata vicino ai servizi principali del quartiere).
        * **Servizi di Quartiere:**
            * `SCHOOL` (Scuola Elementare/Media del quartiere)
            * `PLAYGROUND_LARGE` (Grandi parchi giochi attrezzati)
            * `SUPERMARKET` (Un supermercato di quartiere per la spesa settimanale)
            * `COMMUNITY_POOL` (Piscina comunale estiva)
            * `DAYCARE_CENTER` (Asilo nido)
            * `PEDIATRICIAN_OFFICE` (Ambulatorio pediatrico locale)

    * **Oggetti Unici e Iconici del Distretto:**
        * **Passeggiata Lungofiume:** Un percorso pedonale e ciclabile che segue il corso del fiume, con panchine e aree di sosta.
        * **Moli per la Pesca:** Piccoli moli di legno sul fiume dove gli NPC possono usare l'azione `GO_FISHING_IN_RIVER`.
        * **Fermate dello Scuolabus:** Oggetti riconoscibili dove i bambini si radunano la mattina e tornano il pomeriggio.
        * **Griglie per Barbecue:** Oggetti comuni nei giardini privati delle case e nelle aree parco.
        * **Canestri da Basket** e **Porte da Calcio** nei cortili e nei piccoli parchi.

* `[x]` **10.c: Gameplay e Connessioni**
    * **Opportunità di Gameplay - Carriere:**
        * È il quartiere **dove vivono** molti NPC che lavorano come pendolari negli altri distretti.
        * Le carriere **interne** al distretto sono legate ai servizi di prossimità: `TEACHER`, `SUPERMARKET_CLERK`, `LIFEGUARD` (bagnino alla piscina), `COACH` (allenatore delle squadre sportive giovanili).

    * **Opportunità di Gameplay - Azioni Specifiche:**
        * `HOST_NEIGHBORHOOD_BBQ` (Organizza un barbecue con i vicini).
        * `TAKE_KIDS_TO_PLAYGROUND`.
        * `WAIT_FOR_SCHOOLBUS` (Azione per i bambini).
        * `CHAT_WITH_NEIGHBOR_OVER_FENCE` (Interazione sociale contestuale).
        * Questa è la location principale per il gameplay legato alla `Parenting Skill`.

    * **Opportunità di Gameplay - Eventi:**
        * **Feste di compleanno dei bambini** nei giardini o nelle aree gioco.
        * **Partite sportive giovanili** durante il weekend.
        * **Mercatino dell'usato** di quartiere.
        * **Festa annuale del "Nido del Fiume"** con giochi e cibo per tutti i residenti.

    * **Influenza sui Bisogni:**
        * Un ambiente molto **bilanciato e sicuro (alto `SAFETY`)**.
        * Molte opportunità per il **bisogno `SOCIAL` a livello di vicinato e famiglia**.
        * Potrebbe risultare **"noioso" e poco stimolante per `FUN`** per NPC con tratti come `PARTY_ANIMAL`, `ADVENTUROUS` o adolescenti in cerca di stimoli diversi.

    * **Connessioni:**
        * **Geografica:** Situato in una **zona periferica** della città, ma non isolato. Il fiume che lo attraversa potrebbe collegarsi al lago più a valle.
        * **Trasporti:** Ben collegato ai distretti centrali da una **linea di metropolitana** per i pendolari. All'interno, le strade sono a bassa percorrenza e il servizio di **scuolabus** è un mezzo di trasporto chiave.
        * **Flusso di NPC:** Principalmente **residenti**. Il quartiere si svuota durante le ore lavorative e si riempie di vita nel tardo pomeriggio, sera e weekend. È il distretto con la più alta concentrazione di NPC `CHILD` e `TEENAGER`.

* `[x]` Discutere le **opportunità di gameplay uniche**.
* `[x]` Definire come il distretto si **collega** agli altri.
---

* `[x]` **11.a: Concetto Base e Identità**
    * `[x]` **Nome: Il Crocevia dei Mercanti**
    * `[x]` **Funzione Principale:** Commerciale (Mercati) / Artigianale / Residenziale Popolare
    * `[x]` **Descrizione e Atmosfera:** 
        > *Il vero melting pot di Anthalys. Il Crocevia dei Mercanti è un distretto vibrante, caotico e multiculturale, famoso per il suo enorme mercato all'aperto e per le strette vie fiancheggiate da botteghe artigiane. L'architettura è un mix eclettico di stili diversi, con edifici bassi che spesso ospitano un negozio al piano terra e unità abitative ai piani superiori. L'aria è un assalto sensoriale: odori di spezie esotiche e cibo di strada si mescolano al suono di martelli, al brusio del mercato e a musiche provenienti da tutto il mondo. È il distretto più "terreno" e vivo della città.*

* `[x]` **11.b: Location e Oggetti**
    * **LocationType Ospitate:**
        * `OPEN_AIR_MARKET` (Il grande mercato centrale, una location composta da tante micro-aree)
        * `ARTISAN_SHOP` (Botteghe di vario tipo: vasaio, sarto, orafo, falegname...)
        * `ETHNIC_RESTAURANT` (Ristoranti specializzati in cucine di diverse culture)
        * `FOOD_STALL` (Bancarelle di cibo di strada)
        * `SPICE_SHOP` (Negozi di spezie) / `FABRIC_STORE` (Negozi di tessuti)
        * `HOSTEL` (Ostello economico per viaggiatori e nuovi arrivati)
        * **Unità Abitative Plurifamiliari (Popolari):**
            * `RESIDENTIAL_APT_ABOVE_SHOP_SMALL`: Piccoli appartamenti sopra i negozi, spesso abitati dagli stessi negozianti.
            * `RESIDENTIAL_APARTMENT_BUILDING_MEDIUM`: Palazzine residenziali di medie dimensioni, leggermente più appartate rispetto al mercato, con affitti più accessibili.

    * **Oggetti Unici e Iconici del Distretto:**
        * **Bancarelle del Mercato:** Oggetti interattivi per l'azione `BROWSE_MARKET_STALLS` e per comprare ingredienti unici, spezie, o oggetti artigianali.
        * **Tavoli da Lavoro per Artigiani:** Oggetti visibili nelle botteghe (es. tornio da vasaio, banco da orafo) che sono postazioni di lavoro per le carriere artigiane.
        * **Lanterne Culturali:** Illuminazione stradale con lanterne di stili diversi che creano un'atmosfera unica di notte.
        * **Fontana del Mercato:** Una grande fontana, usurata dal tempo, al centro della piazza del mercato, che funge da punto di incontro informale.

* `[x]` **11.c: Gameplay e Connessioni**
    * **Opportunità di Gameplay - Carriere:**
        * **Carriere principali:** `ARTISAN` (Vasaio, Sarto, Orafo, etc.), `STREET_VENDOR` (Venditore Ambulante), `CHEF` (specializzato in cucina etnica), `SHOPKEEPER` (Negoziante).

    * **Opportunità di Gameplay - Azioni Specifiche:**
        * `HAGGLE_PRICE`: Interazione speciale per tentare di ottenere uno sconto al mercato, basata sulla skill `CHARISMA`.
        * `BROWSE_MARKET_STALLS`, `TRY_STREET_FOOD`.
        * `CRAFT_ITEM`: Azione principale per le carriere artigiane nelle loro botteghe.

    * **Opportunità di Gameplay - Eventi:**
        * **Mercato Settimanale** (con merci e affluenza che variano).
        * **Festival Culturali** di una delle comunità presenti nel quartiere (es. "Festa delle Lanterne", "Festival delle Spezie").
        * **Fiere dell'Artigianato**.

    * **Influenza sui Bisogni:**
        * **Altissimo potenziale per** `FUN` (scoperta, cibo, shopping).
        * **Molto** `SOCIAL`, ma in un contesto caotico e affollato.
        * Potrebbe avere un `ENVIRONMENT` **score basso** a causa del disordine e della folla (un tipo di "inquinamento" diverso da quello industriale), potendo infastidire NPC con il tratto `NEAT`.

    * **Connessioni:**
        * **Geografica:** Potrebbe essere situato vicino al **"Porto di Levante" (Distretto 6)**, da cui riceve merci e nuovi immigrati/viaggiatori. Potrebbe anche confinare con un quartiere residenziale più popolare come **"Nido del Fiume" (Distretto 10)**.
        * **Trasporti:** Una **fermata della metropolitana molto trafficata** ("Mercato Centrale"). Le strade interne sono strette, affollate e in gran parte pedonali.
        * **Flusso di NPC:** Il distretto più **eterogeneo** della città. Un mix di residenti, lavoratori e visitatori da ogni altro distretto. Molto affollato di giorno, più tranquillo ma ancora vivo di notte grazie ai ristoranti e bar.

* `[x]` Discutere le **opportunità di gameplay uniche**.
* `[x]` Definire come il distretto si **collega** agli altri.
---

* `[x]` **12.a: Concetto Base e Identità**
    * `[x]` **Nome: L'Arena**
    * `[x]` **Funzione Principale:** Intrattenimento di Massa / Sportivo
    * `[x]` **Descrizione e Atmosfera:** 
        > *Questo distretto è un tempio moderno dedicato alla passione collettiva e allo spettacolo. Dominato dall'imponente Stadio Polifunzionale di Anthalys e da altre strutture per eventi, "L'Arena" è un'area che vive a due velocità. Durante i giorni feriali, è un luogo quasi surreale per la sua quiete, popolato solo da atleti in allenamento, tecnici e staff. Ma durante le partite o i grandi concerti, il distretto esplode di vita, trasformandosi nel luogo più rumoroso e affollato della città, un mare di NPC festanti. L'architettura è grandiosa, funzionale e progettata per gestire enormi folle in sicurezza. L'atmosfera nei giorni degli eventi è semplicemente elettrica.*

* `[x]` **12.b: Location e Oggetti**
    * **LocationType Ospitate:**
        * `STADIUM` (Il grande stadio polifunzionale per sport e mega-concerti)
        * `INDOOR_ARENA` (Un'arena al coperto più piccola, per concerti, basket, o altri eventi)
        * `SPORTS_MUSEUM` (Museo dello Sport di Anthalys)
        * `SPORTS_BAR` (Grandi bar a tema sportivo con maxi-schermi, affollatissimi prima e dopo le partite)
        * `TEAM_MERCHANDISE_STORE` (Negozi ufficiali delle squadre della città)
        * `TRAINING_FACILITY` (Strutture di allenamento ad uso esclusivo degli atleti professionisti)
        * `LARGE_EVENT_HOTEL` (Un grande hotel per ospitare squadre, artisti e fan in trasferta)

    * **Oggetti Unici e Iconici del Distretto:**
        * **Statue di Atleti Famosi:** Monumenti in bronzo o olografici dedicati alle leggende sportive di Anthalys.
        * **Maxi-schermi Esterni:** Enormi schermi sulle facciate dello stadio che mostrano i momenti salienti degli eventi in corso.
        * **Tornelli e Cancelli d'Accesso:** Oggetti interattivi con cui gli NPC formano code e che devono attraversare per entrare allo stadio (`ATTEND_EVENT`).
        * **Chioschi di Cibo e Bevande:** Oggetti che sono "chiusi" nei giorni normali e si "attivano" durante gli eventi, diventando fonti di cibo e bevande per gli NPC.

* `[x]` **12.c: Gameplay e Connessioni**
    * **Opportunità di Gameplay - Carriere:**
        * `PROFESSIONAL_ATHLETE` (Atleta Professionista)
        * `SPORTS_MANAGER` / `COACH`
        * Carriere nel mondo dello spettacolo: `MUSICIAN` (per i tour negli stadi).
        * Lavori di supporto legati agli eventi: `EVENT_STAFF`, `SECURITY_GUARD`, `FOOD_VENDOR`.

    * **Opportunità di Gameplay - Azioni Specifiche:**
        * `ATTEND_SPORTS_MATCH`: Azione principale, soddisfa moltissimo `FUN` e `SOCIAL`.
        * `ATTEND_CONCERT`.
        * `TRAIN_PROFESSIONALLY`: Azione per gli atleti nelle strutture dedicate, che aumenta la skill `FITNESS` e la performance lavorativa.
        * `BUY_TEAM_MERCHANDISE`.
        * `CELEBRATE_VICTORY` / `MOURN_DEFEAT`: Azioni sociali specifiche che avvengono nei `SPORTS_BAR` dopo la partita, con un forte impatto sull'umore.

    * **Opportunità di Gameplay - Eventi:**`
        * Il gameplay di questo distretto **è** l'evento.
        * **Campionati Sportivi:** Stagioni regolari con partite ogni settimana di riposo, che culminano in **Finali/Playoff** ad altissima partecipazione.`
        * **Tour di Grandi Star della Musica**.

    * **Influenza sui Bisogni:**
        * **Potenziale di** `FUN` e `SOCIAL` **altissimo**, ma quasi esclusivamente durante gli eventi.
        * L'affollamento estremo durante gli eventi potrebbe essere **negativo per NPC** `LONER` **o con tratti simili**.
        * L'esito di una partita può generare moodlet molto forti (positivi o negativi) per gli NPC tifosi.

    * **Connessioni:**
        * **Geografica:** Situato in una **zona dedicata e periferica**, con ampi spazi attorno per la gestione delle folle e dei parcheggi.
        * **Trasporti:** Deve avere una **stazione della metropolitana dedicata e sovradimensionata** ("Stazione Arena") e accesso diretto alle autostrade. Le strade circostanti sono progettate per diventare pedonali durante gli eventi.
        * **Flusso di NPC:** Il flusso più "a ondate" di tutta la città. Quasi deserto nei giorni normali, vive un picco di densità estremo per poche ore durante i giorni degli eventi, con NPC che arrivano da tutti gli altri distretti.

* `[x]` Discutere le **opportunità di gameplay uniche**.
* `[x]` Definire come il distretto si **collega** agli altri.
---

* `[x]` **13.a: Concetto Base e Identità**
    * `[x]` **Nome: Il Vecchio Castello di Anthalys** _(o più semplicemente Il Castello Antico)_
**
    * `[x]` **Funzione Principale:** Storico / Museale / Simbolico
    * `[x]` **Descrizione e Atmosfera:** 
        > *Il luogo dove è nata la leggenda di Anthalys. Il Vecchio Castello è una fortezza antica, le cui mura di pietra hanno visto secoli di storia. Oggi non è più un centro di potere attivo, ma il custode della memoria della città. In parte restaurato e trasformato in un museo, emana un'atmosfera di riverenza, mistero e un po' di malinconia. È la principale meta turistica per chi vuole comprendere il passato della città e un luogo di pellegrinaggio simbolico per i cittadini più legati alle tradizioni.*

* `[x]` **13.b: Location e Oggetti**
    * **LocationType Ospitate:** La location principale è `HISTORICAL_CASTLE`, che al suo interno contiene varie "stanze" o aree:
        * `THRONE_ROOM` (La Sala del Trono, con il trono di _Re Kaleb_ esposto)
        * `ROYAL_APARTMENTS` (Gli appartamenti reali, conservati come un'esposizione)
        * `CASTLE_DUNGEONS` (Le prigioni sotterranee, ora visitabili)
        * `ARMORY` (L'armeria con le armature e le armi della vecchia guardia reale)
        * `CASTLE_GARDENS` (I giardini interni del castello, magari con piante rare e antiche)

    * **Oggetti Unici e Iconici del Distretto:**
        * **I Medaglioni del Potere:** L'oggetto più importante, esposto in una sala di massima sicurezza all'interno del castello. Un'attrazione centrale.
        * **Il Trono di _Re Kaleb Nhytros_:** L'oggetto iconico della Sala del Trono.
        * **Galleria dei Ritratti Reali:** Una serie di ritratti che raccontano la storia della dinastia Nhytros.
        * **L'Antico Libro degli Ospiti:** Un oggetto con cui i visitatori possono interagire per "firmare".

* `[x]` **13.c: Gameplay e Connessioni**
    * **Opportunità di Gameplay - Carriere:**
        * **Carriere:** `HISTORIAN`, `MUSEUM_CURATOR` (specializzato nel castello), `TOUR_GUIDE`.
        * **Azioni Specifiche:** `TAKE_CASTLE_TOUR`, `VIEW_MEDALLIONS_OF_POWER`, `LEARN_CITY_HISTORY`, `SEARCH_FOR_SECRET_PASSAGES` (un'azione rara, che potrebbe dare il via a una piccola storia o scoperta).
        * **Eventi:** Anniversario della Fondazione, mostre speciali, eventi di stato estremamente formali.
        * **Bisogni:** Alto potenziale per il bisogno `LEARNING` e per moodlet legati alla storia e all'ispirazione.

    * **Opportunità di Gameplay - Azioni Specifiche:**
        * `TAKE_CASTLE_TOUR`: L'azione base per i visitatori.
        * `VIEW_MEDALLIONS_OF_POWER`: Azione specifica che potrebbe dare un moodlet di "Meraviglia".
        * `LEARN_CITY_HISTORY`: Azione che aumenta la conoscenza del lore del gioco.
        * `SEARCH_FOR_SECRET_PASSAGES`: Un'azione rara con una bassa probabilità di successo, che potrebbe dare il via a una piccola storia o scoperta nascosta.

    * **Opportunità di Gameplay - Eventi:**
        * **Anniversario della Fondazione di Anthalys:** Un evento di stato solenne che si tiene qui.
        * **Mostre Speciali Temporanee:** Ad esempio, "Gli Gioielli della Dinastia Nhytros" o "Le Mappe Antiche del Regno".
        * Potrebbe essere usato per **eventi di stato estremamente formali**, come l'accoglienza di un dignitario straniero, in un contesto più storico rispetto alla Cittadella.

    * **Influenza sui Bisogni:**
        * **Alto potenziale per il bisogno** `LEARNING` (se implementato).
        * Potrebbe dare un forte **moodlet "Ispirazione Storica"** o un senso di `SOCIAL` (appartenenza alla comunità/storia).
        * Generalmente un luogo tranquillo, non adatto a soddisfare il bisogno `FUN` in modo convenzionale.

    * **Connessioni:**
        * **Geografica:** Il Vecchio Castello sorge sulla cima della collina del "Borgo Antico" (Distretto 8). Il suo lato "terrestre" si affaccia e si collega al lussuoso quartiere storico, mentre il suo lato opposto si erge su un'imponente scogliera a picco sul grande lago.
        * **Impatto Visivo:** Questa posizione lo rende sia il pinnacolo del prestigio del Borgo Antico, sia un landmark drammatico e iconico visibile da tutta la città e dal lago.
        * **Trasporti:** Raggiungibile principalmente attraverso il Borgo Antico, a piedi o tramite la funicolare panoramica che ha una fermata dedicata "Castello".

* `[x]` Discutere le **opportunità di gameplay uniche**.
* `[x]` Definire come il distretto si **collega** agli altri.
---

* `[x]` **14.a: Concetto Base e Identità**
    * `[x]` **Nome: Il Grande Albero** _(conosciuto anche come "L'Albero dei Sogni")_
    * `[x]` **Funzione Principale:** Luogo Simbolico, Romantico e Storico
    * `[x]` **Descrizione e Atmosfera:** 
        > *Un albero imponente e antichissimo, piantato dai primi coloni di Anthalys quasi 6000 anni prima. Si erge solitario sulla cima di una collinetta scoscesa all'interno dei Giardini Sospesi, in una posizione panoramica che si affaccia sul Grande Lago. L'atmosfera è intima, quasi magica e carica di storia. È un luogo di pellegrinaggio per gli innamorati, un rifugio per amici intimi e un simbolo della longevità e delle radici della città.*

* `[x]` **14.b: Location e Oggetti**
    * **LocationType Ospitate:**
        * `GREAT_TREE_HILL`: Un micro-lotto unico all'interno del parco, che rappresenta la collina stessa.

    * **Oggetti Unici e Iconici del Distretto:**
        * `GREAT_DREAM_TREE`: L'albero stesso, un oggetto interagibile unico nel gioco.
        * `CARVED_BENCHES`: Panchine ricavate direttamente dalle radici affioranti dell'albero.
        * `HISTORICAL_PLAQUE`: Una piccola targa di bronzo che ne racconta brevemente la storia.
        * La corteccia dell'albero è essa stessa un "oggetto" con cui interagire.

* `[x]` **14.c: Gameplay e Connessioni**
    * **Opportunità di Gameplay - Carriere:**
        * Nessuna carriera è basata qui, essendo un luogo puramente sociale e contemplativo. Tuttavia, NPC con carriere come `BOTANIST` o `HISTORIAN` potrebbero avere interazioni uniche con l'albero.

    * **Opportunità di Gameplay - Azioni Specifiche:**
        * `ACTION_CARVE_INITIALS_ON_TREE`: Azione romantica per coppie con una relazione stabile, che crea una memoria condivisa potente.
        * `ACTION_CONFIDE_AT_GREAT_TREE`: Interazione sociale profonda tra amici intimi per rafforzare il loro legame.
        * `ACTION_HAVE_FIRST_KISS_AT_GREAT_TREE`: Un'interazione speciale e memorabile per le prime cotte adolescenziali.
        * `ACTION_MAKE_A_WISH_AT_GREAT_TREE`: Un'azione individuale che può dare un moodlet di speranza.
        * `ACTION_REMINISCE_ABOUT_PAST`: Un'azione per NPC anziani che visitano l'albero per ricordare il passato.

    * **Opportunità di Gameplay - Eventi:**
        * Non è un luogo per eventi pubblici su larga scala, ma un catalizzatore per **eventi personali emergenti e significativi** (primi baci, proposte di matrimonio, confessioni).
        * Potrebbe essere associato a un evento stagionale minore, come la "Fioritura del Grande Albero".

    * **Influenza sui Bisogni:**
        * Fornisce un forte guadagno ai bisogni `SOCIAL` e `FUN` (inteso come appagamento emotivo profondo, non come divertimento caotico).
        * Potrebbe soddisfare il bisogno `SPIRITUALITY` per alcuni NPC.
        * Genera `Moodlet` unici e potenti legati a romanticismo, amicizia, nostalgia e meraviglia.

    * **Connessioni:**
        * **Geografica:** Si trova all'interno del **Distretto 7: Giardini Sospesi**, sulla sua sommità collinare più a nord, affacciandosi direttamente sul Grande Lago.
        * **Trasporti:** Raggiungibile tramite i percorsi pedonali e ciclabili dei Giardini Sospesi. La fermata della metropolitana più vicina sarebbe una di quelle che servono i Giardini Sospesi.

* `[x]` Discutere le **opportunità di gameplay uniche**.
* `[x]` Definire come il distretto si **collega** agli altri.
---

**Fase 2: Visione d'Insieme**
* `[ ]` **2.a: Revisione Finale e Mappa Concettuale**
    * `[ ]` Creare una mappa concettuale di come i distretti sono disposti geograficamente (es. quali sono vicini, quali si affacciano sul lago, ecc.) per garantire la coerenza del mondo.

Partiamo dalle caratteristiche geografiche principali che abbiamo stabilito:
* **Il Grande Lago:** L'elemento dominante.
* **La Costa:** Dove la città incontra il lago.
* **La Collina del Borgo Antico:** Che termina con una scogliera a picco sul lago.
* **La Penisola della Loggia del Sapere.**
* **Il Fiume Minore** del "Nido del Fiume".

**Layout Geografico:**

1.  **Il Fronte Lago (da Ovest a Est):**
    * Nell'estremo ovest, una verdeggiante **penisola** si protende nel lago, ospitando **La Loggia del Sapere (5)**.
    * Immediatamente a est della penisola, la costa si innalza per formare la collina del **Borgo Antico (8)**, con il **Vecchio Castello (13)** sulla sua sommità, a picco sull'acqua.
    * Al centro esatto della costa cittadina si estendono i magnifici **Giardini Sospesi (7)**, che fungono da cuore verde e da snodo centrale, con una propria riva sul lago.
    * A est dei Giardini, la costa diventa industriale e ospita il grande **Porto di Levante (6)**.

2.  **Il Nucleo Centrale (immediatamente dietro il fronte lago):**
    * Dietro i Giardini Sospesi si trova il centro del potere e del commercio.
    * **La Cittadella (1)** potrebbe essere direttamente dietro la parte centrale/ovest dei Giardini.
    * **Via Aeterna (3)** potrebbe essere direttamente dietro la parte centrale/est dei Giardini, adiacente sia alla Cittadella che al Porto.
    * Il **Quartiere delle Muse (2)** si inserisce perfettamente tra il Borgo Antico, La Loggia del Sapere e il centro città, creando una continuità logica tra l'élite storica, gli studenti e la vita culturale.

3.  **La Cintura Intermedia e Periferica:**
    * Ancora più all'interno, troviamo i quartieri residenziali e le grandi infrastrutture.
    * **Il Crocevia dei Mercanti (11)** potrebbe trovarsi tra il Porto di Levante e i quartieri residenziali, un luogo naturale per lo smistamento delle merci e l'incontro di persone.
    * Il **Nido del Fiume (10)**, quartiere suburbano, si sviluppa più nell'entroterra, con il suo fiume che scorre verso il lago, magari passando vicino ai Giardini Sospesi.
    * **Solara (9)**, il quartiere eco-tecnologico, potrebbe essere vicino alla Loggia del Sapere e al Complesso della Quercia Bianca, per attrarre i ricercatori e i professionisti di quei settori.
    * Il **Complesso della Quercia Bianca (4)** e **L'Arena (12)**, essendo strutture molto grandi che richiedono spazio e una certa quiete (per l'ospedale) o una buona gestione della folla (per lo stadio), si troverebbero nelle zone più esterne della città, ma ben collegate dalle autostrade e dalla metropolitana.


### Mappa Concettuale a Griglia di Anthalys (Versione 2 - Lago a NORD)

#### Legenda dei Distretti:

* `LK` = Grande Lago
* `~~` = Fiume Minore
---
* `[13] CA` = Vecchio Castello (sulla cima del Borgo Antico)
* `[ 8] BA` = Borgo Antico (Residenziale Storico/Benestante)
* `[ 5] LS` = Loggia del Sapere (Università Umanistica, su una penisola)
---
* `[ 2] QM` = Quartiere delle Muse (Culturale/Storico)
* `[ 7] GS` = Giardini Sospesi (Parco Centrale)
* `[ 1] CI` = La Cittadella (Amministrativo)
* `[ 3] VE` = Via Aeterna (Commerciale/Finanziario)
---
* `[ 6] PL` = Porto di Levante (Industriale/Logistico)
* `[11] CM` = Il Crocevia dei Mercanti (Mercati/Artigianale)
---
* `[ 9] SO` = Solara (Residenziale Eco-sostenibile)
* `[10] NF` = Nido del Fiume (Residenziale Familiare)
* `[ 4] QB` = Complesso della Quercia Bianca (Sanitario/Ricerca Scientifica)
* `[12] AR` = L'Arena (Sport/Intrattenimento di Massa)

---
#### Mappa Schematica (Vista dall'alto, NORD in alto):

+-------------------------------------------------------------------------------------------+
|                                IL   GRANDE   LAGO   (NORD)                                |
|  LK   LK   LK   LK   LK   LK   LK   LK   LK   LK   LK   LK   LK   LK   LK   LK   LK   LK  |
+-------------------------------------------------------------------------------------------+
|      [FRONTE LAGO - OVEST]       |     [FRONTE LAGO - CENTRO]      | [FRONTE LAGO - EST]  |
|                                  |                                 |                      |
|   LS   LS   BA   BA   BA   CA    |   GS   GS   GS   GS   GS   GS   |   PL   PL   PL   PL  |
|   LS   LS   BA   BA   BA   BA    |   GS   GS   GS   GS   GS   GS   |   PL   PL   PL   PL  |
|   LS   LS   BA   BA   BA   BA    |   GS   GS   GS   GS   GS   GS   |   PL   PL   PL   PL  |
+----------------------------------+---------------------------------+----------------------+
|          [ENTROTERRA OVEST]      |        [NUCLEO CENTRALE]        |  [ENTROTERRA EST]    |
|                                  |                                 |                      |
|   QM   QM   QM   CI   CI   CI    |   CI   CI   CI   VE   VE   VE   |   CM   CM   CM       |
|   QM   QM   QM   CI   CI   CI    |   CI   CI   CI   VE   VE   VE   |   CM   CM   CM       |
|   SO   SO   SO   CI   CI   CI    |   VE   VE   VE   VE   VE   VE   |   CM   CM   CM       |
+----------------------------------+---------------------------------+----------------------+
|      [PERIFERIA SUD-OVEST]       |          [PERIFERIA SUD]        | [PERIFERIA SUD-EST]  |
|                                  |                                 |                      |
|   QB   QB   QB   QB   SO   SO    |   NF   NF   NF   NF~~ NF~~ NF   |   AR   AR   AR   AR  |
|   QB   QB   QB   QB   QB   QB    |   NF   NF   NF   NF~~ NF~~ NF   |   AR   AR   AR   AR  |
|   QB   QB   QB   QB   QB   QB    |   NF   NF   NF   NF~~ NF~~ NF   |   AR   AR   AR   AR  |
+-------------------------------------------------------------------------------------------+


---

* `[x]` **X.a: Concetto Base e Identità**
    * `[x]` **Nome: **
    * `[x]` **Funzione Principale:** 
    * `[x]` **Descrizione e Atmosfera:** 
        > **

* `[x]` **X.b: Location e Oggetti**
    * **LocationType Ospitate:**

    * **Oggetti Unici e Iconici del Distretto:**

* `[x]` **X.c: Gameplay e Connessioni**
    * **Opportunità di Gameplay - Carriere:**

    * **Opportunità di Gameplay - Azioni Specifiche:**

    * **Opportunità di Gameplay - Eventi:**

    * **Influenza sui Bisogni:**

    * **Connessioni:**

* `[x]` Discutere le **opportunità di gameplay uniche**.
* `[x]` Definire come il distretto si **collega** agli altri.
---
