## XV. SISTEMI TECNICI `[]`

* `[]` **1. Salvataggio e Caricamento Partita (JSON).**
    * `[]` a. Salvare lo stato completo della simulazione (NPC, tempo, meteo, relazioni, tratti, skill, finanze, ecc.) in un file JSON.
    * `[]` b. Caricare uno stato di gioco da un file JSON.
    * `[]` c. (Da I.5.c) **Salvataggi Multipli / Slot di Salvataggio:** Gestire più file di salvataggio, permettendo all'utente di scegliere quale caricare/sovrascrivere.
    * `[]` d. (Da I.5.d) (Futuro) Gestione errori e versioning dei salvataggi per retrocompatibilità.
* `[]` **2. Opzioni di Gioco e Impostazioni (tramite `settings.json` e menu `curses` base).**
    * `[]` a. File `settings.py` per costanti di gioco non modificabili a runtime.
    * `[]` b. File `settings.json` (o simile) per impostazioni utente modificabili (es. velocità di gioco, opzioni di report). *(Menu curses base implementato per modificare alcuni settings)*.
    * `[]` c. (Da I.7.b) **Refactoring Architetturale - Configurazioni Modulari:** *(Concettualizzato, da implementare)*.
        * `[]` i. Spostare costanti specifiche di sistema in file `_config.py` dedicati (es. `modules/school_system/school_config.py`, `modules/careers/careers_config.py`).
        * `[]` ii. Obiettivo: `settings.py` più snello, migliore modularità.
* `[]` **3. Ottimizzazione Performance e Gestione Popolazione Vasta:** `[NUOVO PUNTO AGGIORNATO]`
    * `[]` a. Architettura per supportare diversi Livelli di Dettaglio (LOD) per l'IA e la simulazione degli NPC. *(Design LOD e simulazione "Off-Screen" per NPC di background ulteriormente dettagliata - vedi IV.4.h).*.
    * `[]` b. Implementazione di Time Slicing / Staggered Updates per gli NPC attivi (LOD Fascia 1 e 2) per distribuire il carico della CPU.
    * `[]` c. Tecniche di caching per calcoli ripetitivi e costosi (se necessario).
    * `[]` d. Profiling periodico delle performance e ottimizzazione continua del motore di simulazione.
    * `[]` e. Valutare strutture dati efficienti per la gestione di grandi numeri di NPC, relazioni e memorie.

---

