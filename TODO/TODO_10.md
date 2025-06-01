## X. INTERESSI, HOBBY E ABILITÀ PRATICHE `[]` (Include azioni da vecchio `IX.3`)

* `[]` **1. Definizione e Gestione degli Interessi/Hobby:**
    * `[]` a. Identificare una lista di potenziali interessi/hobby (es. Lettura, Giardinaggio, Cucina/Pasticceria, Collezionismo, Scrittura, Pittura, Musica, Gaming, Moda, Fotografia, Mentoring, Attività Artigianali, ecc.). Molti sono impliciti o guidati dai tratti di personalità.
    * `[]` b. Ogni NPC (specialmente quelli dettagliati) potrebbe avere 1-3 interessi/hobby "attivi" o "preferiti".
    * `[]` c. L'IA (`AIDecisionMaker`) considera questi interessi/hobby nella scelta delle azioni quando i bisogni primari sono soddisfatti, specialmente per il bisogno `FUN`.
    * `[]` d. I tratti di personalità influenzano fortemente la scelta e la preferenza per determinati hobby/interessi. *(Molte classi tratto già implementano `get_action_choice_priority_modifier` per azioni correlate)*.
* `[]` **2. Impatto degli Hobby/Interessi:**
    * `[]` a. Praticare un hobby/interesse soddisfa primariamente il bisogno `FUN`. *(Molte classi tratto già implementano `get_fun_satisfaction_modifier` per azioni correlate)*.
    * `[]` b. Può contribuire a ridurre lo stress (futura meccanica di stress).
    * `[]` c. Porta allo sviluppo di `SkillType` specifiche correlate (es. Giardinaggio -> `GARDENING`, Scrittura -> `WRITING`, Cucinare -> `COOKING`/`BAKING`). *(Il sistema di classi Skill e `add_experience` gestirà questo)*.
    * `[]` d. (Avanzato) Può portare alla creazione di "opere" o oggetti (vedi X.4).
    * `[]` e. (Avanzato) Può sbloccare interazioni sociali uniche (es. "Discutere del proprio Hobby", "Mostrare la propria Collezione").
* `[]` **3. Abilità Pratiche (Non necessariamente Hobby):**
    * `[]` a. Alcune `SkillType` (es. `MANUAL_DEXTERITY`, `COOKING` base, (futura) `REPAIR`) rappresentano abilità pratiche utili nella vita quotidiana.
    * `[]` b. Gli NPC usano queste skill per azioni di routine (cucinare, pulire, riparare oggetti).
    * `[]` c. Il livello di queste skill influenza l'efficacia e la qualità dell'esito di tali azioni. *(Il tratto `StovesAndGrillsMaster` e `Artisan` ne sono un esempio)*.
* `[]` **4. Sistema di Creazione Oggetti/Opere (Crafting/Produzione):** *(Collegato a X.2.d)*
    * `[]` a. NPC con tratti/skill appropriate (es. `ARTISAN`, `AUTHOR`, `BAKER`, `STOVES_AND_GRILLS_MASTER`, `AESTHETIC_PERFECTIONIST`) possono creare oggetti o opere. *(Concetto base e modificatori di qualità/successo nei tratti definiti)*.
    * `[]` b. Implementare un sistema di "ricette" o "schemi" per il crafting (semplificato all'inizio).
    * `[]` c. Gli oggetti/opere prodotti hanno livelli di qualità (influenzati da skill, tratti, materiali - futuri, eventi casuali).
    * `[]` d. Gli oggetti/opere possono essere usati, esposti, regalati o venduti (legame con Economia VIII e tratto `Marketable`).
    * `[]` e. Completare un'opera significativa dà un forte moodlet positivo e soddisfazione (es. aspirazione).
* `[]` **5. Sistema di Cucina e Cibo:** `[SOTTOCATEGORIA DI X.4 e X.3]`
    * `[]` a. Definire ricette e tipi di cibo (es. "prodotto da forno", "pasto su fornelli", "cibo sano", "cibo spazzatura").
    * `[]` b. Implementare livelli di qualità per il cibo prodotto (da `POOR` a `IMPECCABLE`). *(Concettualizzato)*.
    * `[]` c. Azioni di cucina (`COOK_ON_STOVE`, `GRILL_FOOD`, `BAKE_GOODS`) producono cibo con qualità influenzata da skill e tratti. *(Concettualizzato, tratti `StovesAndGrillsMaster` e `Baker` definiti)*.
    * `[]` d. Mangiare cibo di alta qualità ha un impatto maggiore su `HUNGER` e umore. *(Concettualizzato, tratto `Baker` lo tocca)*.
    * `[]` e. (Futuro) Ingredienti e loro impatto sulla qualità/tipo di piatto.
* `[]` **6. Sistema di Giardinaggio:** `[SOTTOCATEGORIA DI X.4 e X.3]`
    * `[]` a. NPC con tratti `GREEN_THUMB` o `FARMER` si dedicano al giardinaggio. *(Tratti definiti)*.
    * `[]` b. Implementare azioni di giardinaggio (`PLANT_SEEDS`, `WATER_PLANTS`, `WEED_GARDEN`, `HARVEST_PLANTS`).
    * `[]` c. Le piante hanno stati di crescita e bisogno di cure.
    * `[]` d. Il raccolto può produrre "cibo" o ingredienti per la cucina/crafting, o essere venduto.
    * `[]` e. Qualità del raccolto influenzata da skill `GARDENING` e tratti (es. `Super Green Thumb`).
* `[]` **7. Sistema di Collezionismo:**
    * `[]` a. NPC con tratto `OBSESSIVE_COLLECTOR` (IV.3.b) sono spinti a collezionare oggetti.
    * `[]` b. Definire tipi di collezionabili (es. pietre, francobolli, action figure, arte) con rarità.
    * `[]` c. **Collezionismo di Athel Fisico Obsoleto:** `[NUOVO PUNTO]`
        * `[]` i. Le vecchie banconote e monete di Athel (`VIII.A.v`) sono considerate oggetti da collezione.
        * `[]` ii. NPC (specialmente con tratto `OBSESSIVE_COLLECTOR` o `OLD_SOUL` IV.3.b) possono cercare, acquistare, vendere o scambiare Athel fisico.
        * `[]` iii. Il valore collezionistico dipende dalla rarità, dalla conservazione e dal taglio della banconota/moneta.
    * `[]` d. Implementare azioni per trovare/acquistare/scambiare collezionabili.
    * `[]` e. Gli NPC necessitano di un `Inventario` (`XI.2.c.vi`) per conservare i collezionabili.
    * `[]` f. Completare una collezione dà un forte moodlet positivo/senso di realizzazione.
    * `[]` g. Azione `ADMIRE_COLLECTION`.
* `[]` **8. Estensione "Total Realism" - Profondità, Unicità e Impatto Culturale degli Hobby e delle Creazioni:** `[NUOVA SOTTOCATEGORIA]`
    * `[]` a. **Sviluppo Personale attraverso gli Hobby:**
        * `[]` i. Gli hobby non solo soddisfano `FUN` o sviluppano skill, ma possono diventare una parte centrale dell'identità di un NPC, influenzando le sue scelte di vita, relazioni e benessere a lungo termine (collegamento a `IV.3.a Aspirazioni`).
        * `[]` ii. NPC potrebbero sviluppare una vera "passione" per un hobby, dedicandovi tempo significativo e cercando attivamente di migliorare o esplorare nuove sfaccettature.
    * `[]` b. **Creazioni Uniche e di Rilievo:**
        * `[]` i. Oltre alla "qualità", le opere create (libri, dipinti, musica, software, invenzioni artigianali – collegamento a `IX.f.ii Maestria`) potrebbero avere attributi di "originalità", "stile" (se rilevante), o "contenuto tematico" (astratto).
        * `[]` ii. (Molto Avanzato) Generazione procedurale (semplificata) di "contenuti" unici per opere scritte o artistiche (es. titoli di libri, temi principali, descrizioni astratte dello stile di un dipinto o della melodia di una canzone).
    * `[]` c. **Impatto Culturale e Sociale delle Opere:**
        * `[]` i. Altri NPC possono interagire con le opere create: leggere libri, ammirare quadri, ascoltare musica, usare oggetti artigianali.
        * `[]` ii. Le reazioni degli altri NPC (moodlet, pensieri, argomenti di conversazione) dipendono dalla qualità/originalità dell'opera e dai loro tratti/preferenze (es. un NPC `BOOKWORM` potrebbe adorare un romanzo ben scritto, un NPC `SNOB` potrebbe criticare un'opera d'arte).
        * `[]` iii. Opere di particolare successo o impatto (vedi `IX.f.ii.2`) potrebbero generare discussioni nella comunità, influenzare mode (astratte), o addirittura ispirare altri NPC a intraprendere hobby simili o creare opere a loro volta (collegamento a futuro sistema di evoluzione culturale in `C. PROGETTI FUTURI E DLC`).
        * `[]` iv. Un NPC `PHILOSOPHER` (tratto) o con alta skill `WRITING` potrebbe scrivere saggi o manifesti che influenzano il dibattito politico o sociale (collegamento a `VI.2.e.ii Ecosistema dell'Informazione`).
    * `[]` d. **Consumo Critico di Media e Hobby:**
        * `[]` i. NPC non solo creano, ma consumano attivamente prodotti di hobby altrui (libri, musica, arte, videogiochi – skill `Video Gaming` IX.e).
        * `[]` ii. Le loro preferenze (influenzate da tratti, umore, esperienze) guidano le scelte di consumo e le reazioni (es. un NPC `MOVIE_BUFF` potrebbe avere opinioni forti sui film visti).
* **9. Elenco Azioni Generali (non prettamente sociali o di sviluppo skill):** (Precedentemente X.8)
    * `[]` a. NPC compiono azioni per soddisfare bisogni, whims, obiettivi, o per reazione all'ambiente. *(Logica base nelle classi azione)*
    * `[]` b. Le azioni hanno una durata, consumano/ripristinano bisogni, danno XP a skill, possono generare moodlet. *(Definito concettualmente per alcune azioni)*
    * `[]` Write Book (Scrivi un Libro) *(Classe implementata)*
    * `[]` Practice Musical Instrument (Esercitati con Strumento Musicale) *(Definita concettualmente)*
    * `[]` Read Book (Leggi un Libro) *(Definita concettualmente)*
    * `[]` Attend Concert/Show (Partecipa a Concerto/Spettacolo) *(Definita concettualmente)*
    * `[]` **Azioni per soddisfare la Sete (collegamento a `IV.1.h`):** `[NUOVA CATEGORIA AZIONI]`
        * `[]` i. `DRINK_WATER_TAP` (Bere Acqua dal Rubinetto) - Soddisfa Sete, costo nullo, disponibile in lotti con lavandini.
        * `[]` ii. `DRINK_WATER_BOTTLE` (Bere Acqua in Bottiglia) - Soddisfa Sete, richiede oggetto "Acqua in Bottiglia" (acquistabile o da frigo).
        * `[]` iii. `DRINK_JUICE` (Bere Succo) - Soddisfa Sete, piccolo bonus `FUN` o `ENERGY`, richiede oggetto "Succo".
        * `[]` iv. `DRINK_SODA` (Bere Bibita Gassata) - Soddisfa Sete, bonus `FUN`, possibile piccolo malus a `HUNGER` o `ENERGY` a lungo termine. Richiede oggetto "Bibita".
        * `[]` v. `DRINK_MILK` (Bere Latte) - Soddisfa Sete e un po' di `HUNGER`. Richiede oggetto "Latte".
        * `[]` vi. `DRINK_COFFEE_TEA` (Bere Caffè/Tè) - Soddisfa Sete (meno efficace dell'acqua), bonus temporaneo a `ENERGY` e concentrazione, possibile impatto su `BLADDER` e decadimento `ENERGY` a lungo termine. Richiede macchina caffè/bollitore e ingredienti.
        * `[]` vii. `ORDER_DRINK_AT_BAR` (Ordinare da Bere al Bar) - Soddisfa Sete e `FUN`/`SOCIAL`. Richiede `LocationType.BAR` e denaro. (Collegamento a `XIX`)
        * `[]` viii. `DRINK_FROM_FOUNTAIN` (Bere da Fontana Pubblica) - Soddisfa Sete, gratuito, disponibile in `LocationType.PARK` o altre aree pubbliche. Qualità dell'acqua potrebbe essere variabile.
        * `[]` ix. `QUENCH_THIRST_WITH_FRUIT` (Dissetarsi con Frutta) - Azione secondaria al mangiare frutta (`X.5`), soddisfa leggermente la Sete.
    * `[]` Molte altre azioni menzionate nei dettagli delle skill e dei tratti.

---

