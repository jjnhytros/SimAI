## IV. SIMULAZIONE NPC (Bisogni, IA, Ciclo Vita, Caratteristiche)

* `[]` **0. Generazione e Creazione NPC (CAS per NPC):** (`NPCFactory.h/.cpp` scheletro creato, riutilizza CAS da II).
    * `[]` a. Personalizzazione aspetto fisico (viso, corpo, capelli, occhi, pelle).
        * `[]` i. Sistema genetico per la creazione di figli con tratti ereditati. (Vedi anche `II.3` e `IV.2.f` per genetica avanzata). (`GeneticsSystem.h` creato).
    * `[]` b. Scelta età, sesso, genere (opzioni flessibili). (`character_enums.h`, `Identity` in `Character.h`).
    * `[]` c. Assegnazione Tratti (vedi IV.3.b). (`TraitManager` e logica in `NPCFactory` previsti).
    * `[]` d. Scelta Aspirazione di Vita (obiettivi a lungo termine) (vedi IV.3.a). (`AspirationManager` e logica in `NPCFactory` previsti).
    * `[]` e. Definizione Voce. (Attributo in `Identity`).
    * `[]` f. Scelta Abbigliamento (quotidiano, formale, sportivo, notte, feste, nuoto, freddo, caldo). (`ClothingManager` e logica in `NPCFactory` previsti).
    * `[]` g. Definizione Nome e Cognome. (Attributi in `Identity`).
    * `[]` h. (Opzionale) Breve background narrativo.
* `[]` **1. Sistema dei Bisogni:**
    * `[P]` a. Implementati Bisogni modulari con decadimento/soddisfazione. (Configurazione base dei tassi di decadimento, soglie e guadagni da azioni inserita in `settings.py`)
    * `[]` b. Logica di decadimento influenzata da azioni, tratti, stadio vita, gravidanza.
    * `[]` c. Interazione dei bisogni con azioni.
    * `[]` d. Effetti dei bisogni critici su umore e decisioni IA.
    * `[P]` e. Aggiungere bisogni più complessi o secondari (menzionato `INTIMACY_DECAY_RATE` e `INTIMACY_LOW_THRESHOLD`, `INTIMACY_ACTION_GAIN` in `settings.py` - parziale configurazione)
        * `[]` i. **Valutare e Implementare Bisogno di SPIRITUALITÀ:** `[PUNTO DI VALUTAZIONE]` (`SpiritualityNeed.h/.cpp` scheletro creato se opzione A).
            * **Opzione A (Approccio Sistemico come `NeedType`):**
                * `[]` 1. Definire `SPIRITUALITY` come nuovo membro dell'Enum `NeedType`.
                * `[]` 2. Definire tasso di decadimento base, valore iniziale, colore e icona.
                * `[]` 3. Creare la classe `SpiritualityNeed(BaseNeed)` con logica specifica.
                * `[]` 4. Integrare con `AIDecisionMaker`.
                * `[]` 5. Impatto sull'umore.
                * `[]` 6. Visualizzazione nella TUI.
            * **Opzione B (Approccio Guidato solo da Tratti/Moodlet):**
                * `[]` 1. "Spiritualità" non è un bisogno numerico tracciato.
                * `[]` 2. Tratti spirituali danno moodlet positivi da azioni spirituali.
                * `[]` 3. Assenza di pratiche spirituali per NPC con tratti spirituali può portare a moodlet negativi.
                * `[]` 4. Preferenze per azioni spirituali guidate da tratti e moodlet.
        * `[]` ii. Altri bisogni potenziali (es. `COMFORT`, `SICUREZZA`, `CREATIVITY_NEED`, `ACHIEVEMENT_NEED`). (Aggiunti a `NeedId` enum e `Character.cpp::initializeDefaultNeeds` come placeholder).
    * `[]` f. Interdipendenze più profonde tra bisogni.
    * `[]` g. **Sistema di Malattie e Salute Fisica:** (Vedi anche `IV.1.i` per Salute Mentale) (`Disease.h`, `HealthManager.h/.cpp`, `disease_enums.h` creati).
        * `[]` i. Definire malattie comuni e rare (infettive, croniche, legate all'età, incidenti).
        * `[]` ii. Sintomi, progressione, impatto su bisogni/umore/azioni, possibilità di cura (collegamento a Ospedale XVIII.5.h, Carriera Medico VIII.1.j, Skill Medical IX.e).
        * `[]` iii. **Estensione "Total Realism" - Dettaglio Medico Avanzato:** (`Genome.h` per malattie genetiche).
            * `[]` 1. Malattie specifiche con cause complesse (genetiche `IV.2.f.vii.1`, ambientali `XIII`, stile di vita), diagnosi (richiede skill `MEDICAL` avanzate, esami specifici), e percorsi di trattamento differenziati (farmaci specifici, terapie, chirurgia `IX.e`). *(Aggiornato stato a [] per definizione malattie genetiche in `Genome.h`)*
            * `[]` 2. (Molto Avanzato) Simulazione semplificata del sistema immunitario, efficacia di vaccini (se rilevanti per il lore), e potenziale sviluppo di resistenza a trattamenti.
            * `[]` 3. Impatto a lungo termine dello stile di vita (dieta – da sistema cibo `X.5`, esercizio – skill `FITNESS` `IX.e`, stress – da `IV.1.i`, vizi `IV.3.c`) sulla salute generale e sulla predisposizione a specifiche patologie.
    * `[]` h. **Nuovo Bisogno Primario - SETE (Thirst):** (Separato da Fame)
        * `[]` i. Definire `THIRST` come nuovo membro dell'Enum `NeedType` (o equivalente struttura per i bisogni). (`NeedId` aggiornato).
        * `[]` ii. Creare la classe `ThirstNeed(BaseNeed)` con logica specifica: (`ThirstNeed.h/.cpp` creato).
            * `[]` 1. Tasso di decadimento base (influenzato da attività fisica, meteo/temperatura (I.3.f), tratti come `Heatproof`, consumo di cibi salati/secchi).
            * `[]` 2. Valore iniziale alla creazione dell'NPC e al risveglio.
            * `[]` 3. Definire colore e icona (es. 💧) per la visualizzazione nella TUI (XI.2.c.i).
        * `[]` iii. **Soddisfazione del Bisogno di SETE:**
            * `[]` 1. Implementare azioni specifiche per bere: `DRINK_WATER` (da rubinetto, bottiglia, fontana), `DRINK_JUICE`, `DRINK_SODA`, `DRINK_MILK`, `DRINK_COFFEE_TEA` (potrebbero avere effetti diuretici lievi), `ORDER_DRINK_AT_BAR`, `QUENCH_THIRST_WITH_FRUIT`.
            * `[]` 2. Diverse bevande soddisfano la sete in misura variabile; alcune possono avere effetti secondari (es. bibite zuccherate danno breve boost di `FUN` o `ENERGY` ma possono far venire sete prima; caffè/tè possono ridurre `ENERGY` a lungo termine o influenzare `BLADDER`).
            * `[]` 3. Alcuni cibi (es. frutta fresca, zuppe) contribuiscono marginalmente a soddisfare la sete (meccanica minore).
            * `[]` 4. L'acqua dovrebbe essere la bevanda base più efficace e neutra.
        * `[]` iv. **Conseguenze di SETE Criticamente Bassa:**
            * `[]` 1. Moodlet negativi progressivamente più forti (es. `THIRSTY` (-1), `VERY_THIRSTY` (-2), `PARCHED` (-3), `DEHYDRATED` (-5 con impatti fisici)).
            * `[]` 2. Impatto su altre funzioni: riduzione significativa di `ENERGY` (il tratto `Never Weary` potrebbe mitigare ma non eliminare), riduzione concentrazione (impatto negativo su `skill_gain_modifier`, `job_performance`), riduzione efficacia in attività fisiche (`FITNESS` skill).
            * `[]` 3. (Avanzato) Se `DEHYDRATED` per periodi prolungati: rischio di svenimento, sviluppo di problemi di salute temporanei o permanenti (interazione con `IV.1.g Sistema di Malattie e Salute`).
        * `[]` v. **Integrazione con altri Sistemi:**
            * `[]` 1. `AIDecisionMaker` (IV.4) deve dare alta priorità alla soddisfazione della sete quando critica, cercando fonti d'acqua/bevande.
            * `[]` 2. Tratti NPC (IV.3.b): (Molti tratti relativi a sete e caldo creati o concettualizzati).
                * `[]` a. Valutare nuovi tratti specifici (es. `HARDLY_THIRSTY` - decade più lentamente, `DESERT_ADAPTED` - tollera meglio la sete, `ALWAYS_PARCHED` - decade più velocemente, `WATER_CONNOISSEUR` - ottiene moodlet extra da acqua di qualità/bevande specifiche, `CAMEL_LIKE` - può bere molto e resistere a lungo).
                * `[]` b. Adattare tratti esistenti: `Heatproof` potrebbe ridurre il tasso di aumento della sete in climi caldi. Tratti legati al metabolismo o all'attività fisica potrebbero influenzare la sete.
            * `[]` 3. Moodlet (IV.4.i): certi moodlet (es. da malattia, da attività fisica intensa) possono accelerare il decadimento della sete. (Sistema Moodlet creato).
            * `[]` 4. Impatto ambientale: Meteo caldo/secco (I.3.f) aumenta significativamente il decadimento della sete. Disponibilità e tipo di fonti d'acqua/bevande nelle `Location` (XVIII) (es. rubinetti, frigoriferi con bevande, bar, distributori automatici, fontane pubbliche). (`WeatherManager` scheletro creato).
            * `[]` 5. Economia (VIII): Costo delle bevande acquistabili nei negozi, bar, distributori.
            * `[]` 6. Il bisogno `BLADDER` (Vescica) sarà influenzato più frequentemente dalla necessità di bere. (`Bladder` need esiste).
        * `[]` vi. Aggiornare la UI (XI.2.c.i Scheda "Bisogni") per visualizzare distintamente e tracciare il nuovo bisogno `SETE`.
        * `[]` vii. Rivedere il bilanciamento del bisogno `HUNGER` (Fame) per assicurare che ora si concentri esclusivamente sull'assunzione di cibo solido e le sue meccaniche siano distinte da quelle della Sete.
    * `[]` i. **Estensione "Total Realism" - Salute Mentale Dettagliata e Meccanismi di Coping:** `[NUOVA SOTTOCATEGORIA]` (`MentalDisorder.h`, `MentalHealthManager.h`, `mental_disorder_enums.h` creati).
        * `[]` 1. Definire disturbi mentali specifici (es. depressione clinica, vari disturbi d'ansia, PTSD post-eventi traumatici `XIV`, disturbi ossessivo-compulsivi) oltre ai tratti di personalità.
        * `[]` 2. Ogni disturbo avrebbe criteri diagnostici (astratti), cicli di manifestazione (es. episodi depressivi), impatti comportamentali specifici, e interazioni con tratti/bisogni/moodlet.
        * `[]` 3. Possibilità di trattamento: terapia (con NPC Psicologo/Terapeuta `VIII.1.j`), farmaci (con effetti collaterali), tecniche di auto-aiuto (legate a skill `WELLNESS` `IX.e` o specifiche azioni).
        * `[]` 4. Sviluppare un sistema di "Meccanismi di Coping": come gli NPC gestiscono stress acuto e cronico, traumi, o forti emozioni negative (es. ricerca di supporto sociale, isolamento, indulgenza in vizi, attività creative, negazione, razionalizzazione). Influenzato da tratti e memorie. (`CopingMechanismId` enum creato).
    * `[]` j. **Gestione Scorte Domestiche e Comportamento d'Acquisto NPC:** `[NUOVO PUNTO]` (`HouseholdInventory.h/.cpp` creato).
        * `[]` i. Gli NPC (o l'unità familiare) mantengono una "scorta" astratta o semi-dettagliata dei beni di consumo essenziali (cibo `X.5`, bevande `IV.1.h`, prodotti per l'igiene `IV.1.a`, ecc.) e materiali per hobby/lavoro (`X`, `C.9`).
        * `[]` ii. L'IA dell'NPC (`IV.4`) monitora questi livelli di scorta. Quando un bene scende sotto una soglia critica (influenzata da tratti come `PREPARED` (futuro), `FRUGAL` `IV.3.b`, o da abitudini), l'NPC inserisce quel bene nella sua "lista della spesa" (mentale o digitale tramite la Sezione Commercio "AION" di SoNet `XXIV.c.xi`). (`HouseholdInventory` ha `shoppingList_`).
        * `[]` iii. L'azione di acquisto (online tramite SoNet/AION o presso negozi fisici `XVIII.5.h`) rifornisce queste scorte domestiche.
        * `[]` iv. La mancanza cronica di beni essenziali in casa a causa di cattiva gestione delle scorte (o difficoltà economiche `VIII.2`) porta a moodlet negativi (`IV.4.i`) e potenziale stress (`IV.1.i`).
        * `[]` v. Il sistema di "Inventario" del personaggio/famiglia (`XI.2.c.vi`) dovrebbe riflettere queste scorte di beni consumabili oltre agli oggetti unici.
* `[]` **2. Ciclo Vita NPC:** (Include vecchio `I.2.d`, `I.2.e`)
    * `[P]` a. Età NPC (`age` float e `age_in_days`...) (Le costanti per le soglie di età dei `LifeStage` sono ora in `settings.py`)
    * `[P]` b. Meccanica di gravidanza:
        * `[]` i. Probabilità base di concepimento influenzata da fertilità dei partner e azione `BEING_INTIMATE`.
        * `[]` ii. Tratti `FERTILE`/`INFERTILE`/`ERECTILE_DYSFUNCTION`/`BABY_MAKER` (e simili) influenzano la probabilità. (Tratti concettualizzati).
        * `[]` iii. **Gravidanze Adolescenziali e in Età Precoce:** `[DA VALUTARE CON ESTREMA CAUTELA]` *(Concetto e conseguenze significative delineate, implementazione richiede sensibilità e sistemi di supporto)*.
        * `[P]` iv. Durata gravidanza (`PREGNANCY_DURATION_DAYS_GAME`), tracciamento `pregnancy_timer`. (Costanti `PREGNANCY_DURATION_MONTHS_GAME`, `PREGNANCY_DURATION_DAYS_GAME`, `PREGNANCY_DURATION_TICKS` definite in `settings.py`)
        * `[]` v. Impatto della gravidanza su bisogni, umore, azioni della madre.
        * `[]` vi. Possibilità di complicazioni o aborti spontanei.
    * `[]` c. Nascita di nuovi NPC (creazione di istanze `Character` o `BackgroundNPCState` con legami familiari corretti). (Include parte di vecchio `I.2.e` Eventi della vita (nascite, morti, matrimoni, divorzi, trasferimenti).) (`NPCFactory` prevista).
    * `[P]` d. Stadi di vita (`LifeStage` Enum: `INFANT`, `CHILD`, `TEENAGER`, `YOUNG_ADULT`, `ADULT`, `SENIOR`) definiti con soglie di età in `settings.py`. (Nove stadi di vita dettagliati e le loro soglie in giorni (`LIFE_STAGE_AGE_THRESHOLDS_DAYS`) sono stati definiti in `settings.py`)
        * `[]` i. Comportamenti e bisogni specifici per `INFANT` (logica di cura da parte dei genitori).
        * `[]` ii. Comportamenti e bisogni specifici più dettagliati per `CHILD` e `TEENAGER` (scuola, amicizie, sviluppo identità).
        * `[]` iii. Comportamenti e bisogni specifici dettagliati per `YOUNG_ADULT` (inizio carriera, indipendenza, relazioni serie).
        * `[]` iv. Comportamenti e bisogni specifici dettagliati per `ADULT` (consolidamento carriera, famiglia, crisi di mezza età - tratto futuro).
        * `[]` v. **Maturazione Granulare ed Esperienze Specifiche per Età:** *(Concetto definito, da integrare con Sistema Memorie `MemoryObject.h` creato)*.
            * `[]` 1. Definire "età chiave" o "fasi di maturazione" interne ai `LifeStage`.
            * `[]` 2. Associare a queste età/fasi eventi di vita specifici, sfide o opportunità.
            * `[]` 3. Esperienze vissute a età specifiche registrate nel Sistema di Memorie (IV.5).
            * `[]` 4. Logica di trigger per eventi di maturazione.
            * `[]` 5. **Gestione della Pubertà e dei Cambiamenti Corporei Adolescenziali:**
                * `[]` a. Eventi di gioco astratti che segnalano l'inizio/progressione della pubertà per NPC `TEENAGER`.
                * `[]` b. Possibilità di moodlet specifici ("Consapevolezza del Proprio Corpo", "Insicurezza Adolescenziale", "Curiosità per i Cambiamenti") durante questo periodo. (Sistema Moodlet creato).
                * `[]` c. Il tratto `BodyConscious` (se presente) può avere effetti amplificati o manifestazioni specifiche durante l'adolescenza. (Tratto concettualizzato).
                * `[]` d. Interazioni sociali specifiche per adolescenti legate a questi temi (es. parlare con amici, chiedere consiglio ai genitori).
                * `[]` e. Impatto sull'approccio alle prime esperienze romantiche/intime.
    * `[]` e. Stadio di vita Anziano (`SENIOR`), morte naturale, e impatto psicologico dell'invecchiamento: (Include vecchio `II.3 Morte e Aldilà`) (Logica base in `Character.cpp`).
        * `[]` i. Morte naturale per NPC dettagliati e di background. *(Logica base e per BG NPC concettualizzata)*. (Precedentemente `[]` a. Cause di morte (vecchiaia, incidenti - rari, malattie - se implementate).)
        * `[]` ii. Concetto di Pensionamento e calcolo pensione (vedi VIII e XXII). *(Logica per BG NPC concettualizzata)*.
        * `[]` iii. Impatto Psicologico dell'Invecchiamento: (Tratti e Moodlet concettualizzati).
            * `[]` 1. Tratti/moodlet specifici per anziani (es. `RETIREE`, `WISE`, `ELEGANTLY_AGED` vs. `AGE_INSECURE`, `GRUMPY`).
            * `[]` 2. Declino cognitivo lieve e impatto su energia/salute.
            * `[]` 3. Importanza partecipazione sociale/hobby per benessere anziani.
        * `[]` iv. Gestione del lutto per gli NPC superstiti.
        * `[]` v. Cimiteri, funerali, testamenti.
        * `[]` vi. (Opzionale, lore-specifico) Concetto di "passaggio" o ricordo degli antenati.
    * `[]` f. Albero genealogico e gestione legami familiari. *(ID parenti/figli tracciati. `RelationshipType` Enum definita per relazioni vicine).*. (Include vecchio `II.2 Albero Genealogico e Relazioni Familiari`) (`RelationshipManager.h`, `relationship_types.h`, attributi in `Character.h` creati).
        * `[]` i. Tracciamento delle relazioni (genitori, figli, fratelli, coniugi, ecc.).
        * `[]` ii. Impatto delle dinamiche familiari sulla vita dell'NPC.
        * `[]` iii. Espandere il tracciamento della genealogia per supportare **un numero elevato di generazioni (es. fino a 12 o più)**, permettendo di risalire agli antenati e tracciare i discendenti su larga scala. *(Questo è un obiettivo a lungo termine per la profondità del database relazionale).*.
        * `[]` iv. Implementare funzioni per **determinare dinamicamente relazioni familiari complesse** (es. "trisavolo", "cugino di secondo grado") navigando l'albero genealogico, invece di avere un `RelationshipType` Enum per ogni singola possibilità remota.
        * `[]` v. Visualizzazione/gestione dell'albero genealogico (TUI o futura GUI) che permetta di esplorare queste connessioni estese.
        * `[]` vi. **Sistema di Ereditarietà Semplificata dei Tratti:** *(Concetto definito: probabilità di ereditare tratti dai genitori e nonni. L'ereditarietà da antenati più remoti sarebbe statisticamente irrilevante per la maggior parte dei tratti di personalità)*. (`GeneticsSystem` previsto).
        * `[]` vii. **Estensione "Total Realism" - Genetica Avanzata:** (Collegamento a `II.3.d`) (`Genome.h` creato).
            * `[]` 1. Oltre ai tratti di personalità, ereditarietà di predisposizioni a talenti specifici (skill `IX`), suscettibilità a malattie fisiche (`IV.1.g.iii.1`) e mentali (`IV.1.i`). *(Aggiornato stato a [] per `Genome.h` e placeholder per malattie)*
            * `[]` 2. (Molto Avanzato) Possibilità di mutazioni genetiche casuali (rare) alla nascita, che potrebbero introdurre nuovi piccoli modificatori comportamentali o fisici.
    * `[P]` g. **Sistema Ciclo Mestruale e Fertilità (per NPC Femminili):** (Costanti `MIN_AGE_PUBERTY_FERTILITY_DAYS`, `MIN_AGE_START_PREGNANCY_FEMALE_DAYS`, `MAX_AGE_FERTILE_FEMALE_DAYS`, `AGE_START_MENSTRUAL_CYCLE_DAYS_SET`, `AGE_MENOPAUSE_DAYS_SET` definite in `settings.py`)
        * `[]` i. Definizione Parametri del Ciclo e inizio pubertà/fertilità (allineato con `MIN_AGE_FOR_PREGNANCY`).
        * `[]` ii. Meccanica di Tracciamento del Ciclo.
        * `[]` iii. Impatto sulla Fertilità e probabilità di Gravidanza.
        * `[]` iv. Impatto su Umore e Bisogni durante le diverse fasi del ciclo.
        * `[]` v. Menopausa.
        * `[]` vi. Persistenza.
    * `[]` h. Impatto a Lungo Terme della Genitorialità sulla Cognizione.
    * `[]` i. Sviluppo Sessuale Infantile e Adolescenziale (Normativo e Limiti di Simulazione):
        * `[]` 1. Assicurare appropriatezza interazioni per `INFANT` e `CHILD`.
        * `[]` 2. Eventi astratti di "curiosità" o "domande ai genitori" per `CHILD`/`TEENAGER`.
        * `[]` 3. Introduzione di "Cotte Infantili/Puppy Love" per `CHILD` e primi `TEENAGER` (vedi VII.2.b.1-4).
        * `[]` 4. **Consapevolezza e Gestione dei Cambiamenti Corporei "Intimi" durante l'Adolescenza:**
            * `[]` a. NPC adolescenti (specialmente con tratti come `BodyConscious`, `Curious`, `Shy`) possono avere pensieri, moodlet o cercare informazioni (azioni future) riguardo ai cambiamenti del proprio corpo, inclusi gli aspetti più intimi. (Tratti e Moodlet concettualizzati).
            * `[]` b. Questo NON implica la simulazione di atti sessuali espliciti per minori, ma la rappresentazione delle loro insicurezze, curiosità e del processo di comprensione del proprio corpo in evoluzione.
        * `[]` 5. **Esplorazione dell'Identità di Genere e dell'Orientamento Sessuale/Romantico durante l'Adolescenza/Giovane Età Adulta:** (Attributi in `Character.h`).
            * `[]` a. NPC adolescenti/giovani adulti potrebbero attraversare una fase di "esplorazione" o "scoperta" del proprio orientamento (attributo `is_exploring_orientation`).
            * `[]` b. Eventi o interazioni che permettono di solidificare o cambiare (entro certi limiti realistici) il proprio orientamento durante questa fase.
* `[P]` **3. Caratteristiche Personaggio Approfondite:**
    * `[]` a. **Sogni/Aspirazioni principali NPC:** *(Focus di implementazione corrente o successivo)* (Include vecchio `VII.3 Aspirazioni di Vita`) (`BaseAspiration.h`, `AspirationManager.h`, `aspiration_enums.h` creati; attributi in `Character.h`).
        * `[]` i. Definire `AspirationType` Enum (es. `FAMILY_ORIENTED`, `WEALTH_BUILDER`). *(Nomi e concetti da rendere unici per SimAI)*.
        * `[]` ii. Aggiungere attributi `aspiration` e `aspiration_progress` a `Character` e `BackgroundNPCState`.
        * `[]` iii. Definire azioni/stati chiave ("milestone" semplificate) per ciascuna `AspirationType`. *(Definite milestone per FAMILY_ORIENTED e WEALTH_BUILDER)*.
        * `[]` iv. Modificare `AIDecisionMaker` per considerare l'aspirazione.
        * `[]` v. Implementare feedback per il progresso dell'aspirazione.
        * `[]` vi. Visualizzare aspirazione e progresso nella TUI.
        * `[]` vii. (Avanzato) Sotto-obiettivi o "questline" strutturate.
        * `[]` viii. (Avanzato) Permettere cambio aspirazione.
    * `[]` b. **Tratti di Personalità.** *(L'Enum `Trait` e le classi tratto verranno spostate in `modules/traits/` come da I.2.e.i)*. (Questa sezione ora include tutto il vecchio `III. TRATTI DEGLI NPC`) (`BaseTrait.h`, `TraitManager.h`, `trait_enums.h` creati; attributi in `Character.h`; esempi di tratti individuali creati).
        * `[]` i. Ogni NPC ha un numero limitato di tratti (es. 3-5) che definiscono la sua personalità e comportamento.
        * `[]` ii. I tratti influenzano scelte autonome, whims, interazioni disponibili/preferite, apprendimento skill, reazioni emotive. *(Logica base implementata nelle classi dei tratti)*
        * `[]` iii. Alcuni tratti possono essere innati, altri acquisiti durante la vita.
        * `[]` iv. Tratti conflittuali (es. "Timido" vs "Estroverso") creano dinamiche interessanti. *(Definito in alcuni tratti)*
        * `[]` v. Suddivisione in categorie (es. Personalità, Sociale, Lifestyle/Hobby, Mentale/Cognitivo, Fisico/Salute, Economico). *(Struttura directory implementata)*
        * `[]` vi. Espandere numero di tratti e profondità del loro impatto. *(Aggiunti concettualmente: ...Artisan, Jealous, Unflirty, Pompous, WarmHearted, Spoiled, HealthNut, SurvivorOfLoss, CompulsiveAffectionSeeker, AddictivePersonality).*.
        * `[]` vii. **Elenco Tratti (da implementare o dettagliare):** (L'enum `TraitId` è da popolare, ogni tratto è una classe da creare).
            * **Categoria: Sociale**
                * `[]` Always Welcome
                * `[]` Argumentative (Litigioso)
                * `[]` Beguiling
                * `[]` Charmer (Incantatore - diverso da Beguiling, più manipolativo)
                * `[]` Chatty
                * `[]` Good Friend (Buon Amico - leale, supportivo)
                * `[]` Hates Crowds (Odia le Folle)
                * `[]` Incredibly Friendly
                * `[]` Llamacrat & Plumbobican & NPCdipendant (Affiliazioni Politiche) -> Sociale/Personalità
                * `[]` Loner (Solitario - meno estremo di Needs No One)
                * `[]` Needs No One
                * `[]` Outgoing (Estroverso)
                * `[]` Party Animal (Animale da Festa)
                * `[]` People Person (Ama la Gente)
                * `[]` Persuasive (Persuasivo)
                * `[]` Romantic
                * `[]` Seductive (Seducente - diverso da Beguiling, più attivo e intenzionale)
                * `[]` Shy (Timido)
                * `[]` Socially Awkward (Socialmente Imbarazzante)
                * `[]` Soulmate (Anima Gemella - per relazioni) -> Sociale (speciale, forse acquisito)
                * `[]` Tender (Tenero - nelle relazioni)
            * **Categoria: Personalità**
                * `[]` Ambitious (Ambizioso) (Esempio di classe tratto creato)
                * `[]` Anxious (Ansioso)
                * `[]` Arrogant (Arrogante)
                * `[]` Artistic (Artistico - generico, ama l'arte)
                * `[]` Body Positive
                * `[]` Bookworm (Topo di Biblioteca)
                * `[]` Brave
                * `[]` Calm
                * `[]` Carefree
                * `[]` Childish (Infantile - per adulti)
                * `[]` Clumsy
                * `[]` Competitive
                * `[]` Cynical (Cinico)
                * `[]` Disciplined (Disciplinato)
                * `[]` Dramatic (Drammatico)
                * `[]` Eccentric (Eccentrico)
                * `[]` Emotional (Emotivo - sente le emozioni intensamente)
                * `[]` Empathetic (Empatico - diverso da Good Friend, sente le emozioni altrui)
                * `[]` Evil (Malvagio - se si vuole un sistema morale)
                * `[]` Forgetful (Smemorato)
                * `[]` Gloomy (Cupo/Malinconico) -> Personalità
                * `[]` Grumpy
                * `[]` Good (Buono - se si vuole un sistema morale)
                * `[]` High Maintenance (Richiede Molte Attenzioni) -> Personalità
                * `[]` Hot-Headed (Testa Calda)
                * `[]` Humble (Umile)
                * `[]` Impulsive (Impulsivo)
                * `[]` Insecure (Insicuro - diverso da Body Conscious, più generale)
                * `[]` Jealous (Geloso)
                * `[]` Kind (Gentile)
                * `[]` Lazy (Pigro) (Esempio di tratto concettualizzato)
                * `[]` Logical
                * `[]` Loyal (Leale)
                * `[]` Materialistic (Materialista)
                * `[]` Mean (Cattivo/Sgarbato)
                * `[]` Moody (Lunatico)
                * `[]` Muser (Contemplativo - simile a Philosopher?) -> Personalità
                * `[]` Naive (Ingenuo)
                * `[]` Natural Beauty
                * `[]` Neat (Ordinato)
                * `[]` Neurotic (Nevrotico - preoccupato, ossessivo)
                * `[]` Old Soul
                * `[]` Optimist (Ottimista)
                * `[]` Paranoid (Paranoico)
                * `[]` Passionate (Appassionato - per hobby o amore)
                * `[]` Patient (Paziente)
                * `[]` Peaceful
                * `[]` Perfectionist (Perfezionista)
                * `[]` Perky
                * `[]` Pessimist (Pessimista)
                * `[]` Philosopher
                * `[]` Proper (Formale/Contegnoso)
                * `[]` Rebellious (Ribelle)
                * `[]` Reserved (Riservato)
                * `[]` Self-Assured
                * `[]` Self-Sufficient (Autosufficiente) -> Personalità o Lifestyle
                * `[]` Selfish (Egoista)
                * `[]` Sense of Humor (Senso dell'Umorismo - es. Sarcastico, Sciocco, Intellettuale)
                * `[]` Serious (Serio)
                * `[]` Shameless
                * `[]` Sincere (Sincero) -> Personalità
                * `[]` Skeptic (Scettico)
                * `[]` Slob
                * `[]` Snob (Snob)
                * `[]` Spiritual (Spirituale - non necessariamente religioso)
                * `[]` Stoic (Stoico - non mostra emozioni)
                * `[]` Street Smart
                * `[]` Superstitious (Superstizioso) - Crede in portafortuna/sfortuna comuni (numeri, oggetti, azioni come rompere uno specchio), esegue piccoli rituali personali per "assicurarsi la buona sorte" o evitare la cattiva. Non legato a fenomeni paranormali ma a credenze popolari o idiosincrasie. Potrebbe provare ansia o disagio se i suoi rituali sono interrotti o se "sfida la sfortuna". (Esempio di tratto concettualizzato)
                * `[]` Technophobe (Tecnofobo) -> Personalità
                * `[]` Time-sensitive
                * `[]` Unemotional (Privo di Emozioni - diverso da Stoic?) -> Personalità
                * `[]` Unflirty (Non Ammiccante/Disinteressato al flirt)
                * `[]` Unlucky (Sfortunato)
                * `[]` Vain (Vanitoso)
                * `[]` Water Wary (Diffidente dell'Acqua) -> Personalità
                * `[]` Worldly
            * **Categoria: Lifestyle/Hobby**
                * `[] [F_DLC_C.5]` Animal Whisperer *(Interazioni avanzate con animali, dipende da Sistema Animali)*
                * `[]` Creative Visionary
                * `[]` Daredevil
                * `[]` Hairstyle Hobbyist
                * `[]` Home Chef
                * `[]` Horticulturist
                * `[]` Inspired Explorer
                * `[]` Morning NPC
                * `[]` Movie Buff
                * `[]` Night Owl
                * `[]` Speed Cleaner
                * `[]` Adventurous (Avventuroso - diverso da Daredevil, più esplorazione e novità)
                * `[]` Angler (Pescatore Appassionato)
                * `[]` Art Lover (Amante dell'Arte - visita musei, compra opere)
                * `[]` Beach Bum (Tipo da Spiaggia)
                * `[]` Born Salesperson (Venditore Nato)
                * `[F_DLC_C.5]` Cat Person (Gattofilo) *(Dipende da Sistema Animali)*
                * `[]` Child of the Mountains (Ama la Montagna) -> Lifestyle/Hobby
                * `[]` Child of the Ocean (Ama il Mare/Oceano) -> Lifestyle/Hobby
                * `[]` Clubber (Festaiolo da Club)
                * `[]` Collector (Collezionista - di qualsiasi cosa)
                * `[]` Computer Whiz (Mago del Computer - diverso da programmatore, più uso generico)
                * `[]` Couch Potato (Pantofolaio)
                * `[F_DLC_C.5]` Dog Person (Cinofilo) *(Dipende da Sistema Animali)*
                * `[]` Essence of Flavor (Essenza del Sapore - per cuochi?) -> Lifestyle/Hobby o Talento
                * `[]` Foodie (Buongustaio - ama mangiare, non necessariamente cucinare)
                * `[]` Gamer (Videogiocatore Appassionato)
                * `[]` Green Thumb (Pollice Verde - meno intenso di Horticulturist)
                * `[]` Handy (Tuttofare - meno intenso di Handiness skill alta)
                * `[]` Homebody (Pantofolaio/Casalingo)
                * `[]` Loves Outdoors (Ama la Vita all'Aperto)
                * `[]` Loves Spicy Food (Ama il Cibo Piccante) -> Lifestyle/Hobby
                * `[]` Music Lover (Melomane)
                * `[]` Nature Lover (Amante della Natura - generico)
                * `[]` Nightlife Enthusiast (Appassionato di Vita Notturna)
                * `[]` Party Planner (Organizzatore di Feste)
                * `[F_DLC_C.5]` Pet Lover (Amante degli Animali - generico) *(Dipende da Sistema Animali)*
                * `[]` Plant Parent (Genitore di Piante - meno intenso di Horticulturist) -> Lifestyle/Hobby
                * `[]` Savvy Shopper (Acquirente Esperto)
                * `[]` Scribe (Scriba/Amanuense - ama scrivere a mano, calligrafia)
                * `[]` Straight Edge (Contrario a droghe/alcol) -> Lifestyle/Hobby
                * `[]` Super Green Thumb (Super Pollice Verde - estremo di Green Thumb/Horticulturist) -> Lifestyle/Hobby
                * `[]` Sweet Tooth (Goloso di Dolci) -> Lifestyle/Hobby
                * `[]` Techie (Appassionato di Tecnologia)
                * `[]` Traveler (Viaggiatore - meno "ispirato" di Inspired Explorer, più turista)
                * `[]` Vegetarian (Vegetariano) -> Lifestyle/Hobby (Esempio di tratto concettualizzato)
                * `[]` Webmaster (Mago del Web - specifico per computer/internet) -> Lifestyle/Hobby o Skill-based
                * `[]` Winter Expert (Esperto d'Inverno - ama e gestisce bene il freddo/neve) -> Lifestyle/Hobby (sinergia con Cold Acclimation/Ice Proof)
            * **Categoria: Mentale/Cognitivo**
                * `[]` Absent-Minded (Distratto - diverso da Oblivious, più dimenticanze)
                * `[]` Genius (Genio - apprendimento skill molto veloce)
                * `[]` Oblivious
                * `[]` Observant (Osservatore) (`ObservantTrait.h/.cpp` potrebbe essere un esempio)
                * `[]` Quick Learner (Apprende Velocemente)
                * `[]` Savant (Savant - genio in un'area specifica, ma difficoltà in altre) -> Mentale/Cognitivo
                * `[]` Slow Learner (Apprende Lentamente)
            * **Categoria: Fisico/Salute**
                * `[]` Active (Attivo - ama muoversi, fare sport) (Athletic è simile)
                 * `[F_DLC_C.5]` Allergic to [] (Allergico a [] - es. polline, **gatti, cani** - la parte animali dipende da `C.5`)
                * `[]` Always Parched (Sempre Disidratato) - Il bisogno di Sete decade più rapidamente.
                * `[]` Antiseptic
                * `[]` Asthmatic
                * `[]` Camel-Like (Camelide) - Può bere grandi quantità d'acqua in una volta e resistere più a lungo alla disidratazione, ma potrebbe aver bisogno di urinare più frequentemente dopo aver bevuto molto.
                * `[]` Cold Acclimation
                * `[]` Delicate Stomach (Stomaco Delicato)
                * `[]` Fit (In Forma - bonus a fitness, energia)
                * `[]` Forever Fresh
                * `[]` Forever Full
                * `[]` Frail (Gracile/Debole Fisicamente) (Weak è simile)
                * `[]` Glutton (Ghiottone)
                * `[]` Hardly Hungry
                * `[]` Hardly Thirsty (Raramente Assetato) - Il bisogno di Sete decade più lentamente.
                * `[]` Heatproof
                * `[]` Heavy Sleeper (Sonno Pesante)
                * `[]` High Metabolism (Metabolismo Veloce)
                * `[]` Ice Proof
                * `[]` Insomniac (Insonne)
                * `[]` Light Sleeper (Sonno Leggero)
                * `[]` Never Weary
                * `[]` Quick Recovery (Recupero Rapido - da malattie/stanchezza) -> Fisico/Salute
                * `[]` Sickly (Malaticcio - si ammala facilmente)
                * `[]` Steel Bladder
                * `[]` Strong (Forte Fisicamente)
                * `[]` Water Connoisseur (Intenditore d'Acqua) - Ottiene moodlet positivi extra da acqua di alta qualità o bevande specifiche; potrebbe essere schizzinoso riguardo fonti d'acqua di bassa qualità.
                * `[]` Weak Bladder (Vescica Debole)
            * **Categoria: Economico**
                * `[]` Born Rich (Nato Ricco - inizia con più fondi)
                * `[]` Debt-Prone (Incline ai Debiti)
                * `[]` Free Services
                * `[]` Frugal (Thrifty è simile)
                * `[]` Marketable
                * `[]` Penny Pincher (Tirchio - estremo di Frugal)
                * `[]` Spender (Spendaccione)
            * **Categoria: Lavoro/Carriera (alcuni potrebbero essere Lifestyle)**
                * `[]` Ambitious (Ambizioso - già in Personalità, ma con forte impatto sul lavoro)
                * `[]` Dedicated Worker (Lavoratore Dedito)
                * `[]` Dislikes Work (Odia Lavorare)
                * `[]` Efficient (Efficiente)
                * `[]` Procrastinator (Procrastinatore)
                * `[]` Workaholic (Stacanovista)
        * `[]` viii. **Tratti Dipendenti da Sistemi Futuri o Tematiche Specifiche (da Valutare con Cautela):** *(come definito precedentemente, il tratto AddictivePersonality si legherà fortemente a un futuro sistema di dipendenze)*.
            * `[]` 1. Fame Jealous (richiede Sistema di Fama/Reputazione).
            * `[F_DLC_C.5]` 2. Allergic to Cats/Dogs (richiede Sistema di Animali Domestici/Selvatici `C.5`).
            * `[]` 3. Clubber (richiede Sistema di Droghe/Sostanze e Reputazione). *(Definita classe tratto base per aspetto "festaiolo")*.
            * `[]` 4. Straight Edge (richiede Sistema di Droghe/Sostanze).
            * `[]` 5. **Tratti Politici/Ideologici**: (richiede Sistema Politico/Attivismo). *(Nomi da definire per SimAI)*.
            * `[]` 6. **Self-Destructive Tendencies**: `[DA VALUTARE CON CAUTELA]`.
            * `[]` 7. (Opzionale Molto Futuro / Tematica Adulta) **Voyeur-like Behaviors**.
            * `[]` 8. **Tratti legati alla Nudità e al Pudore** (es. `NATURIST`, `PRUDE`, `EXHIBITIONIST`).
            * `[]` 9. **Nosy (Ficcanaso):** (richiede azioni di gossip/snooping).
            * `[]` 10. **Sistema di Dipendenze Comportamentali/da Sostanze:** Richiesto per il pieno funzionamento di `AddictivePersonalityTrait` e `Clubber`/`StraightEdge`. (`AddictionManager` scheletro creato).
            * `[]` 11. **Rappresentazione Approfondita dell'Identità di Genere `TRANSGENDER` e `NON_BINARY`:** Definire meccaniche specifiche (oltre alla semplice Enum `Gender`) per il vissuto e le possibili transizioni (sociali, mediche - astratte) di questi NPC, e come la società di Anthalys reagisce.
            * `[] [F_DLC_C.5]` 12. **Nuovo - Animal Whisperer:** Interazioni avanzate con animali (richiede Sistema di Animali Domestici/Selvatici `C.5`). *(Classe tratto definita concettualmente)*.
        * `[]` ix. Implementare meccaniche di conflitto tra tratti durante l'assegnazione.
        * `[]` x. Integrare pienamente gli effetti di ogni nuovo tratto definito (su IA, bisogni, skill, moodlet, interazioni).
            * `[]` 1. Definire esplicitamente set di tratti incompatibili in `settings.py`.
            * `[]` 2. Logica di assegnazione dei tratti (`constructors.assign_character_traits`) per prevenire conflitti. *(Concetto definito, implementazione da finalizzare)*.
            * `[]` 3. Valutare logica per tratti specifici dell'età o acquisibili dinamicamente.
            * `[]` 4. Sinergie tra tratti compatibili emergono da effetti combinati.
    * `[]` c. **Vizi e Dipendenze:** `[]` *(Questo punto esisteva, ora lo colleghiamo esplicitamente ad AddictivePersonalityTrait e al futuro sistema di dipendenze)*. (`Addiction.h`, `AddictionManager.h`, `addiction_enums.h` creati).
        * `[]` i. Sviluppare un sistema di progressione per dipendenze specifiche (es. gioco d'azzardo, shopping, lavoro, sostanze astratte).
        * `[]` ii. Azioni per indulgere, resistere, cercare aiuto.
        * `[]` iii. Impatto su salute, finanze, relazioni.
    * `[]` d. Manie e Fissazioni.
    * `[]` e. Paure e Fobie.
    * `[]` f. Talenti Innati / Inclinazioni Naturali per abilità.
    * `[]` g. Valori Fondamentali/Etica.
    * `[]` h. **Estensione "Total Realism" - Sviluppo Dinamico della Personalità e Valori:**
        * `[]` i. Oltre ai tratti assegnati alla nascita/CAS, NPC possono sviluppare o modificare leggermente sfaccettature della loro personalità o sistema di valori nel tempo in risposta a esperienze di vita significative (eventi `XIV`, relazioni `VII`, successi/fallimenti carriera `VIII`, traumi `IV.1.i`). (Collegamento a Sistema Memorie `IV.5` - `MemoryObject.h` creato).
        * `[]` ii. Questo non implica cambi drastici di tratti fondamentali, ma evoluzioni e maturazioni realistiche.
    * `[]` i. Propensione all'Onestà Radicale/Autenticità (Tratti definiti).
    * `[P]` j. Orientamento Sessuale e Romantico. (Costanti di probabilità per orientamenti e spettro asessuale/aromantico definite in `settings.py`)
        * `[]` i. Aggiungere attributi a `Character` e `BackgroundNPCState`: `sexually_attracted_to_genders: Set[Gender]`, `romantically_attracted_to_genders: Set[Gender]`, `is_asexual_romantic_spectrum: bool`, `is_aromantic_spectrum: bool`. *(Attributi definiti concettualmente in `Character.h`)*.
        * `[]` ii. Implementare l'assegnazione di questi orientamenti alla creazione dell'NPC (in `constructors.assign_character_orientations`) con una distribuzione probabilistica. *(Logica e probabilità base definite concettualmente, funzione da implementare)*.
            * `[]` 1. Definire chiaramente come l'orientamento "etero/omo" si applica a NPC `NON_BINARY` e `TRANSGENDER`.
        * `[]` iii. Definire e implementare tratti specifici come `ASEXUAL_TRAIT`, `AROMANTIC_TRAIT` con i loro effetti su bisogni e comportamento (se i flag booleani non sono sufficienti).
        * `[!]` iv. **L'IA (`AIDecisionMaker`) DEVE rispettare rigorosamente l'orientamento sessuale/romantico dell'NPC** nella scelta di target per azioni di flirt, `BEING_INTIMATE`, e formazione di coppie romantiche. *(Questo è un requisito fondamentale per l'IA)*.
        * `[]` v. Le interazioni sociali (es. ricevere flirt) devono considerare l'orientamento di entrambi gli NPC per determinare l'esito.
        * `[]` vi. (Futuro) Gestire l'esplorazione e la potenziale evoluzione (limitata) dell'orientamento durante l'adolescenza/giovane età adulta (vedi IV.2.i.5). (Attributo `is_exploring_orientation` previsto).
    * `[]` k. **Background e Storia Pregressa degli NPC:** (`NPCFactory` e `MemoryObject` previsti).
        * `[]` i. Generare storia pregressa astratta per NPC non neonati.
        * `[]` ii. Storia pregressa registrata come memorie iniziali (vedi IV.5).
        * `[]` iii. Il BG influenza skill iniziali, relazioni, probabilità tratti.
* `[P]` **4. Intelligenza Artificiale NPC (Comportamento e Decisioni):**
    * `[]` a. Soddisfa i bisogni attuali tramite azioni. (Vecchio `VII.1.a` Logica per la scelta autonoma delle azioni basata su bisogni, moodlet, whims, tratti, ora del giorno, ambiente, obiettivi.)
    * `[]` b. Logica decisionale rifattorizzata in `AIDecisionMaker` con priorità. (Vecchio `VII.1.b` Sistema di priorità per le azioni.)
    * `[]` c. Sistema di Umore (`MoodState`). (Vecchio `VI.a` Sistema di Umore (MoodState) che rappresenta lo stato emotivo generale dell'NPC (Felice, Triste, Arrabbiato, Stressato, ecc.). *(Enum MoodState parzialmente definito e usato)*)
    * `[]` d. Influenza Umore, Tratti, **e Orientamento Sessuale/Romantico** sulle Decisioni. (Vecchio `VI.c` Le emozioni influenzano le scelte dell'IA, le interazioni sociali, l'efficacia nelle skill e nel lavoro.)
    * `[P]` e. Interazioni di cura infanti. (Costanti per soglie bisogni infanti, mood trigger, energia genitore, costi e durate cura infanti definite in `settings.py`)
    * `[]` f. Obiettivi a Breve e Lungo Termine/Aspirazioni. (Include `VII.2 Whims` e `VII.3 Aspirazioni`)
        * `[]` i. Whims (Desideri/Ghiribizzi): Piccoli desideri a breve termine che appaiono dinamicamente. *(Definiti concettualmente: ShareGoodNews, LearnNewRecipe)*
        * `[]` ii. Soddisfare i whims dà piccole ricompense (moodlet positivi, punti soddisfazione).
        * `[]` iii. I whims sono influenzati da tratti, umore, skill, ambiente, eventi recenti.
    * `[]` g. **Pianificazione AI Avanzata, Gestione Interruzioni, Routine, Apprendimento:** *(Concettualizzazione gestione interruzioni e priorità stimoli per NPC dettagliati in corso)*. (Include `VII.1.c` Capacità di pianificare sequenze di azioni per raggiungere un obiettivo. e `VII.4 Routine Giornaliera`)
        * `[]` i. Meccanismo per gestione stimoli/eventi concorrenti per NPC Dettagliati (LOD1/2).
        * `[]` ii. L'IA (`AIDecisionMaker`) per NPC Dettagliati valuta se interrompere azione corrente.
        * `[]` iii. Gestire stati di azione "in pausa" per NPC Dettagliati.
        * `[]` iv. (Avanzato) Routine giornaliere/settimanali più flessibili per NPC Dettagliati. (NPC dovrebbero avere routine di base (dormire, mangiare, lavorare/scuola, tempo libero) influenzate da tratti e orari. Capacità di interrompere la routine per eventi imprevisti o bisogni urgenti.)
        * `[]` v. **Estensione "Total Realism" - Processi Cognitivi Sfumati e Apprendimento Profondo:**
            * `[]` 1. Capacità di ragionamento deduttivo/induttivo semplificato per risolvere problemi nuovi o raggiungere obiettivi complessi (es. "se A e B sono veri, allora C deve essere possibile").
            * `[]` 2. Pianificazione dinamica: NPC non solo seguono routine, ma creano piani multi-step per obiettivi a medio-lungo termine (aspirazioni `IV.3.a`, risoluzione problemi) e possono rivedere/adattare questi piani se le circostanze cambiano o emergono ostacoli/opportunità.
            * `[]` 3. Implementare bias cognitivi specifici (oltre a quelli politici `VI.2.b`, es. ancoraggio, bias di conferma, euristica della disponibilità, effetto Dunning-Kruger) che influenzano la percezione della realtà, la valutazione dei rischi/opportunità e le decisioni, portando a comportamenti talvolta irrazionali ma umanamente comprensibili.
            * `[]` 4. (Molto Avanzato) Meccaniche di apprendimento comportamentale che vanno oltre l'accumulo di XP per le skill: NPC "imparano" quali strategie funzionano meglio in certe situazioni o con certi altri NPC, adattando il loro comportamento nel tempo.
            * `[]` 5. Simulazione (astratta) di un "subconscio attivo": paure irrazionali (IV.3.e) potrebbero emergere dinamicamente da esperienze passate o da una combinazione di tratti e stress. I sogni (XVI.3) potrebbero avere un impatto più diretto sull'umore del giorno dopo o fornire "intuizioni" (molto rare) per NPC con tratti specifici.
        * `[!]` vi. L'IA deve mirare a generare comportamenti che rispettino il principio di "Individualità Estrema" (`⓪.8.b`), sorprendendo il giocatore con azioni uniche ma coerenti.
    * `[]` h. **Simulazione "Off-Screen" e Gestione Popolazione Vasta:**
        * `[]` i. Definizione dei Livelli di Dettaglio (LOD) per NPC.
        * `[]` ii. **NPC di Background (Fascia 3) - Simulazione Astratta/Narrativa:**
            * `[]` 1. Definire lo Stato Minimo da Tracciare (`BackgroundNPCState`). *(Classe base definita, attributi e metodi di transizione concettualizzati)*.
            * `[]` 2. **Implementare Aggiornamenti a Bassa Frequenza ("Heartbeats"):**
                * `[]` a. Logica per Aggiornamento Giornaliero. *(Concettualizzazione dettagliata completata)*.
                * `[]` b. Logica per Aggiornamento Mensile/Periodico. *(Concettualizzazione dettagliata dei componenti completata)*.
                * `[]` c. Logica per Aggiornamento Annuale (triggerato da compleanno). *(Concettualizzazione dettagliata dei componenti completata)*.
            * `[]` 3. Azioni ed Esistenza: Routine e ruoli, non `AIDecisionMaker` dettagliato.
            * `[]` 4. Bisogni e Umore: Astratti in "Benessere Generale".
            * `[]` 5. NPC non giocanti (PNG) che popolano il mondo con le loro vite e routine. (Da vecchio `I.1.c`)
                * `[]` i. Meccanica di "storie di quartiere" e progressione della vita per i PNG non attivamente controllati. (Da vecchio `I.1.c.i`)
        * `[]` iii. **NPC Prossimi (Fascia 2) - Simulazione Semplificata:** *(Concettualizzazione da approfondire)*.
        * `[]` iv. **Transizione tra Livelli di Dettaglio (LOD):**
        * `[]` v. **(Opzionale ma Consigliato) Sistema di Archetipi NPC:** *(Concettualizzato)*.
    * `[]` i. **Sistema di Moodlet:** (Da vecchio `VI.b`)
        * `[]` i. Ogni moodlet ha un'intensità (positiva/negativa) e una durata. *(Implementato nei tratti)*
        * `[]` ii. Moodlet possono accumularsi o annullarsi a vicenda.
    * `[]` j. Espressioni facciali e animazioni che riflettono l'umore attuale. (Da vecchio `VI.d`)
    * `[]` m. **Nuovo - Sistema di Osservazione (da file TODO utente):** (Come prima)
* **5. Sistema di Memorie NPC:** `[]` *(Concettualizzazione Iniziale, inclusa gestione per NPC background e legame con maturazione)*.
    * `[]` a. Definire struttura dati per `MemoryObject`.
    * `[]` b. Implementare la registrazione di memorie significative per NPC Dettagliati (LOD1/2):
        * `[]` i. Eventi di vita maggiori ed esperienze di maturazione legate all'età (vedi IV.2.d.iii) vengono salvati come `MemoryObject`.
        * `[]` ii. (Avanzato) Implementare `character.memories_short_term`.
    * `[]` c. **Gestione Memorie per NPC di Background (LOD3):**
        * `[]` i. Mantengono lista semplificata di memorie a lungo termine chiave.
        * `[]` ii. Memorie astratte influenzano probabilità negli "heartbeat" e `general_wellbeing`.
        * `[]` iii. Non tracciata memoria a breve termine dettagliata.
    * `[]` d. Definire e implementare azione `REMINISCE_ABOUT_PAST`.
    * `[]` e. Tratto `MEMORY_KEEPER` interagisce con questo sistema.
    * `[]` f. (Avanzato) Meccanismi di oblio o modifica carica emotiva memorie.
    * `[]` g. (Avanzato) Impatto di tratti (`ABSENT_MINDED`) o condizioni mediche su memorie.
    * `[]` h. (Avanzato) Memorie passate influenzano decisioni future IA per NPC dettagliati.
* **6. Sistema di Consapevolezza Sociale e Scoperta Tratti:** `[]` *(Concettualizzazione Iniziale)*.
    * `[]` a. Attributo `Character.known_npc_traits`. (Include save/load).
    * `[]` b. Logica base per NPC *non Osservatori* per scoprire tratti.
    * `[]` c. Tratto `OBSERVANT` permette scoperta immediata/accelerata. *(Classe tratto definita)*.
    * `[]` d. L'IA (`AIDecisionMaker`) utilizza `known_npc_traits`.
    * `[]` e. (Avanzato) NPC potrebbero "sbagliare" a interpretare tratti.

---

