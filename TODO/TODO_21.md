## XXI. STRUMENTI DEVELOPER `[]`

* `[]` **1. Debugging Avanzato:**
    * `[]` a. Implementare un sistema di logging più robusto e configurabile (diversi livelli di log, output su file e/o console).
    * `[]` b. Possibilità di attivare/disattivare il logging per moduli specifici.
    * `[]` c. Visualizzazione TUI migliorata per variabili interne degli NPC e dello stato della simulazione (oltre alle schede NPC attuali, magari una "debug view"). *(Le schede NPC attuali sono un inizio)*.
    * `[]` d. (Futuro) Integrazione con debugger Python (es. `pdb` o debugger di IDE) facilitata.
    * `[]` e. Funzionalità di "dump state" per un NPC specifico o per l'intera simulazione in un formato leggibile per analisi.

* `[]` **2. Profiling delle Performance:**
    * `[]` a. Integrare strumenti di profiling (es. `cProfile`, `line_profiler`) per identificare colli di bottiglia nelle performance.
    * `[]` b. Stabilire benchmark per misurare l'impatto delle modifiche al codice sulle performance.
    * `[]` c. Check periodici delle performance, specialmente con l'aumento del numero di NPC e della complessità dei sistemi.

* `[]` **3. Comandi Cheat-Code per Sviluppo e Testing:** `[NUOVO SOTTOPUNTO]`
    * `[]` a. Implementare un meccanismo per inserire comandi cheat (es. tramite una console di debug nella TUI o comandi specifici da tastiera in una "modalità developer").
    * `[]` b. **Comandi di Manipolazione NPC:**
        * `[]` i. Modificare bisogni di un NPC selezionato (es. `cheat_need <need_type> <value>`).
        * `[]` ii. Aggiungere/Rimuovere moodlet (es. `cheat_add_moodlet <moodlet_id> <duration>`).
        * `[]` iii. Aggiungere/Rimuovere tratti (es. `cheat_add_trait <trait_enum_name>`).
        * `[]` iv. Modificare livelli di skill (es. `cheat_skill <skill_type> <level>`).
        * `[]` v. Modificare punteggi di relazione (es. `cheat_relationship <npc_id_target> <value>`).
        * `[]` vi. Aggiungere/Rimuovere denaro (es. `cheat_money <amount>`).
        * `[]` vii. Triggerare una gravidanza / terminare una gravidanza.
        * `[]` viii. Cambiare `LifeStage` o età.
        * `[]` ix. Teletrasportare un NPC in una `Location`.
    * `[]` c. **Comandi di Manipolazione Mondo/Simulazione:**
        * `[]` i. Avanzare rapidamente il tempo di X giorni/mesi/anni.
        * `[]` ii. Cambiare stagione/meteo istantaneamente.
        * `[]` iii. Triggerare un evento specifico (da XIV).
        * `[]` iv. Generare un nuovo NPC con caratteristiche specifiche.
        * `[]` v. Salvare/Caricare la partita da console.
    * `[]` d. **Comandi di Visualizzazione/Debug:**
        * `[]` i. Mostrare informazioni di debug nascoste (es. pathfinding AI, variabili interne).
        * `[]` ii. Attivare/disattivare log specifici a runtime.
    * `[!]` e. Assicurarsi che i comandi cheat siano accessibili solo in una modalità di sviluppo/debug e non influenzino il gameplay normale per l'utente finale (a meno che non sia una scelta esplicita).

* `[]` **4. Utility Scripts per la Gestione del Progetto:**
    * `[]` a. Script per generare automaticamente le classi tratto base da una lista di nomi.
    * `[]` b. Script per validare la coerenza dei file di configurazione (es. `settings.py`, futuri `_config.py`).
    * `[]` c. Script per aiutare nel refactoring (es. trovare tutte le stringhe hardcoded per l'internalizzazione).

---

