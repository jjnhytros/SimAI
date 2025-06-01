## XVIII. INTERAZIONI AMBIENTALI, OGGETTI E LUOGHI `[]` (Include vecchio `XVIII. LOCATIONS (Luoghi/Lotti)`)

* **1. Interazione con Oggetti Specifici:**
* **1. Interazione con Oggetti Specifici:**
    * `[]` a. NPC possono interagire con oggetti specifici nelle `Location` (es. TV, letto, frigorifero, computer, libri, specchio, strumenti musicali, attrezzatura sportiva, giochi da tavolo, lavandini/rubinetti, fontane pubbliche, macchine del caffè/bollitori, distributori automatici di bevande).
    * `[]` b. Le interazioni soddisfano bisogni, danno moodlet, o sviluppano skill (es. leggere un libro (`READ_BOOK` `X.9`) aumenta `KNOWLEDGE_GENERAL` (futura skill `IX.e`) e soddisfa `FUN` `IV.1.e`; usare un computer può sviluppare skill `PROGRAMMING` `IX.e` o `VIDEOGAMING` `IX.e`, o permettere accesso alla Sezione Commercio "AION" di SoNet `XXIV.c.xi`; usare un rubinetto per `DRINK_WATER_TAP` soddisfa `THIRST` `IV.1.h`).
    * `[]` c. Qualità e stato degli oggetti possono influenzare l'efficacia dell'interazione (es. un letto comodo dà un moodlet migliore `COMFORT` `IV.1.e`; un frigorifero ben fornito offre più opzioni per placare fame e sete e riflette le scorte domestiche `IV.1.j`).
    * `[]` d. **Oggetti Contenitori per Scorte Domestiche:** `[NUOVO PUNTO]`
        * `[]` i. Oggetti come Frigoriferi, Dispense, Armadietti del bagno (`XVIII.1.a`) non solo permettono l'interazione (es. `PRENDI_CIBO_DAL_FRIGO`) ma rappresentano visivamente (astrattamente) la capacità e il livello delle scorte domestiche (`IV.1.j`).
        * `[]` ii. La "capacità" di questi contenitori potrebbe essere un fattore (es. una famiglia numerosa necessita di un frigo più grande o di fare la spesa più spesso). Potrebbe essere un attributo dell'oggetto (es. `storage_capacity`).
* **2. Usura, Manutenzione e Dinamica degli Oggetti:** `[]` (Revisione di "Usura e Manutenzione Oggetti")
    * `[]` a. Oggetti possono "usurarsi" o "rompersi" con l'uso frequente o a causa di eventi (es. un NPC `CLUMSY` `IV.3.b` che lo usa, sbalzi di tensione per oggetti elettronici). *(Logica base di rottura implementata per alcuni oggetti)*
    * `[]` b. NPC (specialmente con skill `HANDINESS` `IX.e` o tratti come `HANDY` `IV.3.b`) possono tentare di riparare oggetti rotti (azione `REPAIR_OBJECT`).
        * `[]` i. La riparazione richiede tempo e, a volte, "pezzi di ricambio" (astratti o acquistabili).
        * `[]` ii. Il successo della riparazione dipende dalla skill `HANDINESS` e dalla complessità dell'oggetto. Un fallimento potrebbe peggiorare l'oggetto, danneggiarlo permanentemente, o dare un piccolo shock elettrico all'NPC (moodlet negativo).
    * `[]` c. Oggetti possono richiedere manutenzione periodica per prevenire guasti (es. pulire filtri, oliare meccanismi – azioni specifiche).
    * `[]` d. **Estensione "Total Realism" - Fisica degli Oggetti Semplificata e Interazioni Dinamiche:**
        * `[]` i. Possibilità per NPC (specialmente con tratti `STRONG` `IV.3.b` o durante azioni specifiche) di spostare alcuni oggetti di arredamento (sedie, tavolini).
        * `[]` ii. (Avanzato) Oggetti possono cadere e rompersi in modo più dinamico se urtati con forza (es. un vaso fragile).
        * `[]` iii. (Avanzato, se non TUI) Gli oggetti potrebbero accumulare polvere o sporcizia visibile nel tempo, richiedendo l'azione `CLEAN_OBJECT`.
        * `[]` iv. (Molto Avanzato) Simulazione semplificata di fluidi per interazioni specifiche:
            * `[]` 1. Riempire/svuotare contenitori d'acqua (bicchieri, vasche da bagno).
            * `[]` 2. Possibilità di "allagamenti" minori da tubi rotti (`XVIII.2.a`) o vasche straripanti, con NPC che devono pulire (`CLEAN_MESS` azione) per evitare danni o moodlet negativi.
            * `[]` 3. Diffusione di fumo da incendi (`XIII.3.c.i`) in aree chiuse.
* `[]` **3. Stato Ambientale (Pulizia, Disordine):**
    * `[]` a. `Location` (specialmente lotti residenziali) e alcuni Oggetti (es. fornelli, bagni) possono accumulare un livello di "sporcizia" o "disordine" a causa di attività quotidiane (cucinare `X.5`, mangiare, usare il bagno, bambini che giocano, feste, malattie `IV.1.g`).
    * `[]` b. Azioni che sporcano (es. cucinare, dipingere `IX.e`) e azioni che puliscono (`CLEAN_HOUSE`, `WASH_DISHES`, `MOP_FLOOR`, `WIPE_SURFACES` – nuove azioni specifiche).
    * `[]` c. Impatto sull'umore degli NPC (specialmente per tratti come `SQUEAMISH`, `NEAT` (IV.3.b), `SLOB` (IV.3.b), `AESTHETIC_PERFECTIONIST` (IV.3.b)). Un ambiente sporco può dare moodlet negativi, ridurre il `COMFORT` (`IV.1.e`), e persino aumentare il rischio di malattie (molto lieve, `IV.1.g`).
* `[]` **4. Eventi Ambientali Minori (Insetti, Odori):**
    * `[]` a. Possibilità di eventi come "vista di insetti" (scarafaggi, formiche, ragni – specialmente in lotti sporchi `XVIII.3` o con determinate caratteristiche ambientali) o "cattivi odori" (da spazzatura non raccolta `XIII.3.a`, cibi avariati, problemi idraulici).
    * `[]` b. Impatto sull'umore, specialmente per NPC `SQUEAMISH` (IV.3.b) (nausea, disgusto) o `NEAT` (IV.3.b) (stress, urgenza di pulire). Altri tratti potrebbero reagire diversamente (es. `SLOB` potrebbe ignorarli).
* `[]` **5. Proprietà e Tipi di Location:** (Include vecchio `XVIII.1 Sistema dei Luoghi` e `XVIII.2 Elenco Luoghi Comunitari` e `XVIII.5 Proprietà dei Luoghi`)
    * ... (considerare che gli attributi come `cleanliness_level` `XVIII.5.i.iv` sono ora dinamicamente influenzati da `XVIII.3`) ...
    * `[]` a. Diversi tipi di lotti (Residenziale, Comunitario, Commerciale). *(Implicitamente gestito da LocationType)*
    * `[]` b. Definizione di un Enum `LocationType` (o `LotType`). *(Definito e aggiornato)*. (Precedentemente anche `[]` a. Definite `Location` Enum base (`HOME`, `HOSPITAL`, `PARK`, `SCHOOL`, `WORK`, `BASEMENT`)).
    * `[]` c. Ogni lotto ha un indirizzo, dimensione, valore, oggetti specifici.
    * `[]` d. NPC visitano lotti comunitari per attività o lavoro. *(Definito concettualmente)*
    * `[]` e. Generazione procedurale o design di quartieri/città con lotti residenziali e comunitari. (Da vecchio `I.1.a`)
    * `[]` f. Sistema di "proprietà" dei lotti (acquistabili, affittabili). (Da vecchio `I.1.b`)
    * `[]` g. (Futuro) Introdurre sotto-luoghi specifici o "lotti" con caratteristiche uniche (es. `HOME` con `BASEMENT` per `ParanoidTrait`, `PARK` con aree affollate/isolate).
    * `[]` h. **Elenco Luoghi Comunitari (Esempi da implementare):**
        * `[]` Parco (Park) *(Enum base)*
        * `[]` Biblioteca (Library) *(Definita concettualmente e Enum)*
        * `[]` Palestra (Gym)
        * `[]` Museo (Museum)
        * `[]` Cinema (Cinema Plex) *(Enum base, azione AttendConcertShow)*
        * `[]` Ristorante / Caffè / Bar
        * `[]` Discoteca / Locale Notturno (Nightclub) *(Definita concettualmente e Enum)*
        * `[]` Negozi Vari (abbigliamento, alimentari, elettronica, ecc.)
        * `[]` Ospedale (Hospital) *(Enum base, carriera Doctor)*
        * `[]` Scuola (School) *(Enum base, carriera Teacher)*
        * `[]` Orto Comunitario (Community Garden) *(Definita concettualmente e Enum)*
        * `[]` Teatro / Sala Concerti (Theater Venue / Arena) *(Enum base, azione AttendConcertShow)*
    * `[]` i. **Attributi della Location che influenzano gli NPC:**
        * `[]` i. `crowd_level` (livello di affollamento) *(Definito concettualmente per le location create)*
        * `[]` ii. `safety_rating` (livello di sicurezza) *(Definito concettualmente per le location create)*
        * `[]` iii. `aesthetic_score` (punteggio estetico) *(Definito concettualmente per le location create)*
        * `[]` iv. `cleanliness_level` (livello di pulizia) *(Definito concettualmente per le location create)*
        * `[]` v. `noise_level` (livello di rumore) *(Definito concettualmente per le location create)*
        * `[]` vi. Questi attributi possono cambiare dinamicamente (es. `crowd_level` in un parco, `cleanliness_level` in una casa).
        * `[]` vii. I tratti degli NPC (es. `PARANOID`, `SQUEAMISH`, `AESTHETIC_PERFECTIONIST`, `MINIMALIST`) reagiscono a questi livelli con moodlet o preferenze di azione. *(Tratti definiti per reagire)*.
    * `[]` j. (Futuro) Sistema di "proprietà immobiliari": NPC possono acquistare/affittare/ereditare case, con impatto su finanze e benessere.
    * `[]` k. (Futuro) Miglioramento/Decorazione delle case (legato a tratti come `AESTHETIC_PERFECTIONIST`, `MINIMALIST`, `FASHIONISTA` per lo stile, e skill come `DESIGN_INTERIOR`).

---

