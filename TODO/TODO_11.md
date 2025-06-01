## XI. INTERFACCIA UTENTE (TUI) `[]` *(UI `curses`)*

* **1. Core UI (Struttura e Componenti Base):** `[]`
    * `[]` a. Scheletro UI `curses` con finestre principali: Header (Info Gioco/Tempo), Log Eventi/Pensieri, Pannello Inferiore (Lista NPC, Dettagli NPC), Command Bar.
    * `[]` b. Gestione input da tastiera (`input_handler.py`) per navigazione e comandi base. *(Funzionalità base implementata, da espandere)*.
    * `[]` c. **Command Palette (Nuova Feature):** (Precedentemente `I.6.1.g`)
        * `[]` i. Implementare una palette di comandi attivabile (es. con `Ctrl+P` o simile) per accesso rapido a funzioni (es. "velocità X", "cerca NPC Y", "salva", "esci").
        * `[]` ii. Lista comandi definita in `settings.py` o dinamicamente.
    * `[]` d. **Widget Personalizzati (Nuova Feature):** (Precedentemente `I.6.1.h`)
        * `[]` i. Creare un modulo `modules/ui/widgets.py` per componenti UI riutilizzabili.
        * `[]` ii. Esempio: `NeedBar` per visualizzare i bisogni. *(Concettualmente già presente con le barre di progressione attuali, ma potrebbe essere formalizzata come widget)*.
        * `[]` iii. (Futuro) Widget per grafici semplici, tabelle formattate.
    * `[P]` e. Gestione dei colori tramite `settings.ANSIColors` (o equivalenti `curses.color_pair`). (Classe `ANSIColors` definita in `settings.py`)
    * `[]` f. Adattabilità della UI a diverse dimensioni del terminale (entro limiti ragionevoli).
    * `[]` g. Feedback visivo per l'utente (es. evidenziazione elemento selezionato, messaggi di stato/errore nella command bar).

* **2. Visualizzazione Dati e Informazioni NPC:** `[]` (Precedentemente anche `I.6.2`)
    * `[]` a. **Lista NPC (Pannello Sinistro Inferiore):**
        * `[]` i. Mostra nome, genere (icona), stadio vita (abbrev.), azione corrente (abbrev.), umore (icona).
        * `[]` ii. Mostra icone per ciclo mestruale e fertilità (se attivi).
        * `[]` iii. Selezione NPC con frecce SU/GIÙ.
        * `[]` iv. Implementare scrolling verticale per la lista NPC se il numero di NPC supera l'altezza della finestra.
        * `[]` v. (Opzionale) Aggiungere una piccola scrollbar visiva.
        * `[]` vi. (Futuro) Filtri o opzioni di ordinamento per la lista NPC.
    * `[]` b. **Log Eventi/Pensieri (Pannello Centrale):** Visualizzazione dinamica con auto-scrolling e scrollbar manuale.
    * `[]` c. **Schede Dettagli NPC (Pannello Destro Inferiore):** (Precedentemente `I.6.5 Struttura Finestre Esistente`)
        * `[]` i. Scheda "Bisogni" (😊) con icone, valori percentuali e barre di progressione.
        * `[]` ii. Scheda "Lavoro/Scuola" (💼) con informazioni su lavoro/livello e status/performance scolastica. *(Da espandere con dettagli carriera e report scolastici)*.
        * `[]` iii. Scheda "Abilità" (🛠️) con visualizzazione delle skill e dei loro livelli (e XP se si decide di mostrarla). *(Da aggiornare per il sistema di classi Skill e per mostrare più skill)*.
        * `[]` iv. Scheda "Relazioni" (❤️) con visualizzazione delle relazioni significative e dei loro punteggi/tipi. *(Da migliorare per chiarezza e più informazioni)*.
        * `[]` v. Scheda "Aspirazioni" (🎯): Visualizzare l'aspirazione corrente dell'NPC, le milestone e il progresso. *(Placeholder attuale)*.
        * `[]` vi. Scheda "Inventario" (🎒): Visualizzare l'inventario dell'NPC (oggetti, collezionabili - placeholder attuale, meccanica non implementata).
        * `[]` vii. Scheda "Tratti" (🧠): Elencare i tratti dell'NPC con le loro icone e brevi descrizioni.
        * `[]` viii. Scheda "Memorie" (📜): Visualizzare memorie significative dell'NPC (se il sistema di memorie è implementato).
        * `[]` ix. Implementare scrolling verticale *all'interno* delle singole schede se il contenuto è troppo lungo. *(Precedentemente XI.6.d)*.
    * `[]` d. **Nuovo - Diagrammi Relazioni Semplificati (Testuali):** (Precedentemente `I.6.2.a`)
        * `[]` i. Visualizzare una rappresentazione testuale semplice delle relazioni dirette dell'NPC selezionato (es. partner, figli, genitori).
    * `[]` e. **Nuovo - Timeline Eventi NPC (Semplificata):** (Precedentemente `I.6.2.b`)
        * `[]` i. Scheda o visualizzazione che mostra gli eventi di vita più significativi (memorie) dell'NPC selezionato in ordine cronologico.

* **3. Dashboard di Sistema (Informazioni Globali):** `[]` (Precedentemente `I.6.3`)
    * `[]` a. Creare una nuova schermata/pannello accessibile per visualizzare statistiche globali della simulazione.
    * `[]` b. Informazioni da mostrare: Numero totale NPC, numero famiglie, NPC occupati/studenti, nascite/morti del giorno, stato dell'economia (futuro), anno/mese/giorno corrente.
    * `[]` c. (Futuro) Grafici testuali semplici per l'evoluzione di alcune statistiche.

* **4. Navigazione e Interattività Avanzata:** `[]` (Precedentemente `I.6.4` e `I.6.7 Migliorare Interattività`)
    * `[]` a. Navigazione focus tra pannelli principali (Lista NPC, Log, Schede NPC) con TAB. *(Implementata base)*.
    * `[]` b. Navigazione tra le schede NPC con frecce SINISTRA/DESTRA. *(Implementata base)*.
    * `[]` c. Tasti rapidi per accedere a schede specifiche (es. 'B' per Bisogni).
    * `[]` d. Rendere il feedback visivo sul focus del pannello/elemento più chiaro ed evidente. *(Base presente, da migliorare)*.
    * `[]` e. Shortcut contestuali visualizzati nella Command Bar.
    * `[]` f. Menu impostazioni (`curses`) per modificare `settings.json`. *(Implementato base, da espandere)*. (Precedentemente `I.6.6 Menu Impostazioni`)
        * `[]` i. Espandere opzioni modificabili nel menu (più tassi di decadimento, soglie, opzioni di debug).

---

