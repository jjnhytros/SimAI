## XVII. LOCALIZZAZIONE E MULTILINGUA `[]`

* `[]` **1. Internalizzazione del Testo (i18n):**
    * `[]` a. Identificare tutte le stringhe di testo visibili all'utente nel gioco (nomi di azioni, descrizioni di tratti/moodlet/skill, messaggi di log, etichette UI, pensieri NPC, nomi di oggetti/location generici, ecc.).
    * `[]` b. Implementare un sistema per estrarre queste stringhe dal codice e memorizzarle in file di risorse per lingua (es. file `.po` con `gettext`, o file JSON/YAML per lingua).
    * `[]` c. Modificare il codice per caricare e utilizzare le stringhe dalla risorsa linguistica appropriata invece di usare stringhe hardcoded.
* `[]` **2. Supporto per Lingue Multiple:**
    * `[]` a. Creare file di traduzione iniziali per le lingue target (es. Italiano come default, Inglese come prima lingua aggiuntiva).
    * `[]` b. Implementare un meccanismo per permettere all'utente (o al gioco) di selezionare la lingua desiderata all'avvio o dalle opzioni.
    * `[]` c. Gestire la visualizzazione corretta di caratteri speciali e set di caratteri diversi per ogni lingua supportata (assicurarsi che `curses` e il font del terminale possano gestirli, o considerare alternative per la GUI futura).
* `[]` **3. Localizzazione dei Contenuti (l10n):**
    * `[]` a. Oltre alla traduzione testuale, considerare la localizzazione di formati di data/ora, numeri, valuta (se Anthalys avesse diverse regioni con convenzioni diverse – meno probabile per ora).
    * `[]` b. (Avanzato) Adattare alcuni contenuti di gioco (es. nomi propri di NPC generati casualmente, nomi di luoghi specifici, riferimenti culturali nei dialoghi o eventi) per essere più appropriati o culturalmente risonanti per le diverse localizzazioni, se si mira a un alto grado di immersione.
* `[]` **4. Strumenti e Processi per la Traduzione:**
    * `[]` a. (Futuro) Valutare strumenti che facilitino il processo di traduzione e la gestione dei file di lingua.
    * `[]` b. (Futuro) Stabilire un processo per aggiornare le traduzioni quando nuovo testo viene aggiunto al gioco.

---

