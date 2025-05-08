# TODO List: Simulatore di Vita "simai/game"

**Legenda:**
* `[]`: Non iniziato
* `[P]`: Parzialmente completato
* `[x]`: Completato
* `[+]`: Funzioni aggiuntive possibili/idee

---

1.  **Core di Pygame (in `simai/game`)**
    * a. [x] Creare il file principale del gioco (es. `main.py` in `simai/game`).
    * b. [x] Implementare la finestra di gioco base di Pygame (inizializzazione, dimensioni, titolo).
    * c. [x] Creare il loop di gioco principale (gestione eventi, aggiornamento logica, rendering).
    * d. [x] Gestire l'evento di chiusura della finestra.
    * e. [x] Impostare un clock per controllare il framerate (FPS).

2.  **Struttura Iniziale del Codice di Gioco (in `simai/game`)**
    * a. [] Creare sottocartelle per l'organizzazione del codice (es. `assets`, `src` o direttamente `engine`, `entities`, `world`, `ai`, `ui`).
        * i. [] `simai/game/assets/`: per immagini, suoni, font.
        * ii. [] `simai/game/src/` (o direttamente le altre cartelle):
            * [] `simai/game/src/engine/`: per il gestore di gioco, grafica di basso livello.
            * [] `simai/game/src/entities/`: per le classi dei personaggi.
            * [] `simai/game/src/world/`: per la mappa e gli oggetti ambientali.
            * [] `simai/game/src/ai/`: per la logica dell'IA.
            * [] `simai/game/src/ui/`: per l'interfaccia utente.
    * b. [] Definire la classe base per un'entità/personaggio (es. `Character` in `simai/game/src/entities/character.py`) con attributi minimi (posizione x, y).
    * c. [] Implementare un metodo `draw()` base per l'entità (es. disegnare un cerchio/rettangolo).
    * d. [] Istanziare e disegnare una singola entità sullo schermo.

3.  **Movimento e Interazione Base**
    * a. [] Implementare il movimento base del personaggio (se controllato dal giocatore) tramite input da tastiera.
    * b. [] Definire i confini della finestra per evitare che l'entità esca dallo schermo.
    * c. [] (Opzionale) Implementare il movimento base per un NPC (es. movimento casuale semplice o verso un punto). [+]

4.  **Sistema dei Bisogni (Super Semplice Inizialmente)**
    * a. [] Aggiungere un attributo "fame" alla classe `Character`.
    * b. [] Far aumentare la fame lentamente nel tempo.
    * c. [] Visualizzare il valore della fame sullo schermo (testo semplice o una barra).
    * d. [] Creare un oggetto "cibo" (grafica semplice) nel mondo.
    * e. [] Implementare una semplice interazione: se il personaggio è vicino al cibo e preme un tasto, la fame diminuisce.

5.  **Pianificazione Integrazione con `simai/election`**
    * a. [] Definire concettualmente quali dati o eventi dal simulatore di vita (`game`) potrebbero influenzare il simulatore di elezioni (`election`) (es. felicità della popolazione, numero di cittadini, leader carismatici).
    * b. [] Definire concettualmente quali dati o eventi da `election` potrebbero influenzare `game` (es. nuove leggi, tasse, disordini civili).
    * c. [] Valutare i meccanismi di comunicazione tra i due moduli (es. file JSON condivisi, API interne se eseguiti come processi separati, o chiamate dirette di funzioni se parte di un unico eseguibile più grande). *Questo è per una fase molto successiva, ma è bene iniziare a pensarci.* [+]

6.  **Prossimi Passi (Sviluppo Iterativo)**
    * a. [] Implementare un sistema di tempo (ciclo giorno/notte).
    * b. [] Aggiungere più bisogni (sonno, socialità, ecc.). [+]
    * c. [] Creare oggetti interattivi per soddisfare i bisogni (letto, telefono).
    * d. [] Iniziare a implementare l'IA decisionale per gli NPC (es. una FSM semplice: se affamato, cerca cibo). [+]
    * e. [] Sviluppare un sistema di pathfinding base (se il mondo diventa più complesso). [+]
    * f. [] Migliorare la grafica e l'UI.
    * g. [] Aggiungere più NPC e interazioni sociali rudimentali. [+]