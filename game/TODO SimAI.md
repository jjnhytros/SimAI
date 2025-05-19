# TODO List: Simulatore di Vita "SimAI" (Città di Anthalys)

**Legenda:**
* `[]`: Non iniziato
* `[P]`: Parzialmente completato / In corso
* `[x]`: Completato (per la sua implementazione base/attuale)
* `[]`: Funzioni aggiuntive possibili/idee (generalmente per dopo o di complessità maggiore)
* `[ELEC]`: Punto ispirato/adattato dalla TODO List di `simai/election`
* `[NUOVO_USER]`: Punto aggiunto su specifica richiesta dell'utente in questa iterazione (usato nelle iterazioni precedenti, mantenuto per coerenza se presente nel file originale)
* `[ESPANSIONE]`: Punto che espande significativamente una funzionalità esistente o pianificata (usato nelle iterazioni precedenti)

---
**Data Ultimo Aggiornamento TODO:** 19 Maggio 2025
---

**I. FONDAMENTA DEL GIOCO E MOTORE**
    * 1. **Core Pygame:** `[x]`
        * a. Creare il file principale del gioco (`main.py`). `[x]`
        * b. Implementare la finestra di gioco base di Pygame. `[x]`
        * c. Creare il loop di gioco principale. `[x]`
        * d. Gestire l'evento di chiusura della finestra. `[x]`
        * e. Impostare un clock per il framerate (FPS). `[x]`
    * 2. **Struttura Modulare del Codice:** `[x]`
        * a. Organizzazione cartelle base (`assets`, `src`, `modules/needs`, `entities/components`, `ai/actions`). `[x]`
        * b. Creazione file principali (`config.py`, `game_utils.py`). `[x]`
        * c. `[x]` Definizione classe `Character` (refactorizzata con componenti) in `src/entities/character.py`.
        * d. Implementazione `__init__.py` per packages. `[x]`
    * 3. **Sistema di Tempo di Gioco Avanzato:** `[P]`
        * a. Ciclo giorno/notte di 28 ore con colori cielo graduali e nome del periodo con icona. `[P]` (Logica in `TimeManager`)
        * b. 6 Velocità di gioco controllabili (0-5) con impostazioni personalizzate e pulsanti UI. `[P]` (Logica in `TimeManager` e `EventHandler`)
        * c. Calcolo e visualizzazione data estesa: Giorno (1-24), Mese (1-18), Anno. `[P]` (In `TimeManager`)
        * d. Età degli NPC che progredisce in base al tempo di gioco. `[P]` (In `StatusComponent`)
        * e. `[]` Calendario con eventi unici (festività stagionali, compleanni NPC con possibili celebrazioni/moodlet).
        * f. `[]` Meteo dinamico (sole, pioggia, nuvole, neve, vento) e stagioni, con impatto visivo e su gameplay.
        * g. `[P]` **Accelerazione Automatica del Tempo**:
            * i. `[P]` Se tutti gli NPC attivi sono a letto (`resting_on_bed`), la velocità del gioco passa automaticamente a quella massima.
              * 1. Non hai ancora testato a fondo tutti i casi limite (es. cosa succede se un nuovo NPC spawna mentre altri dormono? Cosa succede se un NPC viene rimosso?).
              * 2.La definizione di "NPC attivi" potrebbe necessitare di ulteriori rifiniture (es. ignora i neonati o NPC "fuori lotto" in futuro).
              * 3. La velocità "massima" (5) è hardcoded; potresti volerla prendere da `config.py` (`TIME_SPEED_SLEEP_ACCELERATED_INDEX`) come avevamo discusso come opzione. La nostra implementazione attuale usa `5` direttamente.
            * ii.`[P]` Memorizzare la velocità precedente per ripristinarla quando almeno un NPC si sveglia.
              * 1. Il test completo di tutti gli scenari di risveglio e interruzione potrebbe essere ancora in corso.
              * 2. La gestione del ripristino in concomitanza con il cambio manuale della velocità da parte dell'utente (vedi punto iii) è interconnessa e deve funzionare perfettamente.
            * iii.`[P]` L'intervento manuale dell'utente sulla velocità del tempo deve interrompere l'accelerazione automatica e avere la priorità.
              * 1. La robustezza di questa interazione (utente che cambia velocità mentre l'accelerazione è attiva, o mentre sta per attivarsi/disattivarsi) necessita di test approfonditi per assicurarsi che non ci siano condizioni di gara o comportamenti imprevisti.
              * 2. cosa succede se l'utente mette in pausa (velocità 0) mentre l'accelerazione era attiva? Al risveglio di un NPC, il gioco dovrebbe rimanere in pausa (come impostato dall'utente) o tornare alla velocità che c'era prima dell'accelerazione? La nostra logica attuale dovrebbe ripristinare la velocità precedente all'accelerazione, ma l'utente potrebbe aspettarsi che la sua ultima azione manuale (pausa) persista. Questo potrebbe richiedere una riflessione o una specifica di design più precisa. La nostra implementazione attuale fa sì che se l'utente cambia velocità, `is_sleep_fast_forward_active` diventa `False`, quindi al risveglio di un NPC, il blocco `if game_state.is_sleep_fast_forward_active`: non si attiva, e la velocità rimane quella impostata dall'utente. Questo sembra corretto, ma testare tutte le sequenze è importante.
    * 4. **Sistema di Pathfinding NPC:** `[P]`
        * a. Integrazione libreria Pathfinding A*. `[x]` (Logica A* base in `game_utils.py`)
        * b. Creazione griglia di navigazione basata su `TILE_SIZE`. `[x]`
        * c. Marcatura ostacoli fissi (oggetti) sulla griglia. `[P]` (Logica in `setup_pathfinding_grid`, **debugging attivo per correggere errori di mappatura**)
        * d. Implementazione movimento diagonale per NPC. `[x]`
        * e. Logica IA per far puntare NPC a celle adiacenti camminabili per oggetti grandi. `[P]` (Nei moduli azione e con punti di interazione, **da verificare con pathfinding corretto**)
        * f. `[]` Pathfinding per target mobili (altri NPC) più sofisticato.
        * g. `[]` Gestione ostacoli dinamici (altri NPC che bloccano il percorso).
        * h. `[]` Algoritmi di evitamento collisioni più fluidi tra NPC.
        * i. `[]` Costi di attraversamento diversi per differenti tipi di terreno/superfici.

**II. CREAZIONE DEL PERSONAGGIO GIOCABILE** `[NUOVO_USER]`
    * 1. `[]` **Interfaccia di Creazione Personaggio (ICP):**
        * a. `[]` Scelta del nome e cognome.
        * b. `[]` Scelta del genere.
        * c. `[]` Personalizzazione aspetto fisico (viso, corpo, capelli, vestiti base).
        * d. `[]` Scelta età iniziale (es. giovane adulto).
        * e. `[]` Selezione aspirazione iniziale.
        * f. `[]` Selezione tratti di personalità iniziali.
    * 2. `[]` **Impostazione Background Familiare (Opzionale):**
        * a. `[]` Creare/selezionare genitori e fratelli (con impatto su relazioni iniziali e albero genealogico).
    * 3. `[]` **Assegnazione Residenza Iniziale:**
        * a. `[]` Scelta o assegnazione di un lotto residenziale di partenza.
    * 4. `[]` **Introduzione/Tutorial al Gioco:**
        * a. `[]` Breve tutorial che guida il giocatore attraverso le meccaniche base dopo la creazione.

**III. MONDO DI ANTHALYS (Open World e Costruzione)**
    * 1. `[]` **Funzionalità Open World di Base:**
        * a. `[]` Transizione da lotto singolo a mappa open-world per la città di Anthalys.
        * b. `[]` Sistema di coordinate globali per la città e gestione caricamento/streaming di aree (chunk).
        * c. `[]` Pathfinding su larga scala per navigazione cittadina tra lotti e quartieri.
    * 2. `[]` **Creazione della Città di Anthalys:**
        * a. `[]` Progettazione mappa base: layout stradale, zone principali.
        * b. `[]` Definizione e creazione di quartieri distinti.
    * 3. `[]` **Infrastrutture e Lotti Cittadini:**
        * a. `[]` Sistema stradale dettagliato e marciapiedi.
        * b. `[]` Sistema di indirizzi.
        * c. `[]` Implementazione lotti residenziali.
        * d. `[]` Implementazione lotti comunitari/commerciali.
        * e. `[]` Sistema di trasporti pubblici base.
    * 4. `[]` **Ambiente Dinamico e Interattivo:**
        * a. `[]` Impatto visivo e su NPC di Meteo e Stagioni.
        * b. `[]` (Molto Avanzato) Strumenti di costruzione e arredo lotti.

**IV. SIMULAZIONE NPC (Bisogni, IA, Ciclo Vita, Caratteristiche)**
    * 1. **Sistema dei Bisogni:** `[x]` (Componente `NeedsComponent` e classi `BaseNeed` implementati)
        * a. `[x]` 7 Bisogni modulari implementati.
        * b. `[x]` Logica di decay/increase e soddisfazione per ogni bisogno.
        * c. `[P]` Interazione dei bisogni con azioni e ambiente (da testare/implementare nelle azioni IA).
        * d. `[P]` Effetti dei bisogni critici su umore e decisioni IA (da integrare con `MoodComponent` e `idle.py`).
        * e. `[]` Aggiungere bisogni più complessi o secondari.
        * f. `[]` Interdipendenze più profonde tra bisogni.
        * g. `[]` Modificatori di bisogno a lungo termine.
        * h. `[]` Bisogni emergenti specifici per stadi di vita o situazioni.
        * i. `[]` **Sistema di Malattie e Salute**. `[NUOVO_USER]`
        * j. `[P]` **Migliorare Interazione Cibo per NPC**: (Necessita `InventoryComponent` e oggetti cibo)
        * k. `[P]` **Migliorare Interazione Bagno per NPC**: (Testare con pathfinding corretto)
    * 2. **Ciclo Vita NPC:** `[P]` (Gestito da `StatusComponent`)
        * a. `[x]` Età NPC che progredisce e visualizzazione base.
        * b. `[P]` Meccanica di gravidanza base.
        * c. `[P]` Nascita di nuovi NPC (chiamata a `CharacterManager.spawn_newborn_npc`).
        * d. `[]` Implementare stadi di vita successivi e **Sistema Scolastico di Anthalys**. `[ESPANSIONE]`
        * e. `[]` Stadio di vita Anziano, morte naturale.
        * f. `[P]` Albero genealogico e gestione legami familiari (`RelationshipComponent` base, genealogia N-generazioni da espandere).
        * g. `[]` Congedo retribuito per maternità/paternità. `[NUOVO_USER]`
    * 3. **Caratteristiche Personaggio Approfondite:** `[P]` (Componenti base creati: `Aspiration`, `Mood`, `Career`, `Skill`)
        * a. `[P]` Sogni/Aspirazioni principali NPC (`AspirationComponent`). `[ELEC]` `[NUOVO_USER]`
        * b. `[]` Tratti di Personalità (`PersonalityComponent` futuro). `[ELEC]`
        * c. `[]` Vizi e Dipendenze. `[NUOVO_USER]`
        * d. `[]` Manie e Fissazioni. `[NUOVO_USER]`
        * e. `[]` Paure e Fobie. `[NUOVO_USER]`
        * f. `[]` Talenti Innati / Inclinazioni Naturali per abilità.
        * g. `[]` Valori Fondamentali/Etica.
        * h. `[]` Stile di Comunicazione Unico.
        * i. `[]` Segreti NPC.
    * 4. **Intelligenza Artificiale NPC (Comportamento e Decisioni):** `[P]`
        * a. `[P]` Soddisfa i 7 bisogni attuali tramite oggetti/azioni (azioni refactorizzate, testare a fondo).
        * b. `[x]` Logica decisionale base (`idle.py`).
        * c. `[P]` Sistema di Umore (`MoodComponent` base).
        * d. `[P]` Influenza Umore sulle Decisioni (da implementare in `idle.py`).
        * e. `[P]` Obiettivi a Breve e Lungo Termine/Aspirazioni (guidati da `AspirationComponent`, IA da integrare).
        * f. `[]` Pianificazione AI Avanzata, Routine, Apprendimento.
        * g. `[]` IA per scelta **vestiario**. `[NUOVO_USER]`
        * h. `[]` Simulazione "Off-Screen".
        * i. `[]` IA per interagire con servizi cittadini.
        * j. `[P]` **Riattivare e Migliorare Azione "Phoning"**.
        * k. `[P]` **Migliorare Interazione Letto** (pathfinding, gestione slot, animazioni).
        * l. `[x]` **Refactor `npc_behavior.py` per Modularità**: (Completato con i moduli azione).

**V. SISTEMA SCOLASTICO DI ANTHALYS** `[]` `[NUOVO_USER]`
    * 1. `[]` **Struttura e Calendario Scolastico:**
        * a. `[]` Definire 8 Livelli Scolastici (Infanzia -> Università) con fasce d'età.
        * b. `[]` Implementare Anno Scolastico (18 mesi, 324gg didattica, Inizio 13/13, Fine 12/9).
        * c. `[]` Implementare Pause Scolastiche (Primaverile 12gg, Estiva 72gg).
    * 2. `[]` **Curriculum e Materie per Livello:**
        * a. `[]` Infanzia (1-3 anni): Sviluppo motorio/sociale/linguistico, **Anthaliano** moderno base.
        * b. `[]` Elementari Inferiori (4-6 anni): Alfabetizzazione base, matematica base, scienze intro, arti, **Anthaliano** moderno, **Inglese**.
        * c. `[]` Elementari Superiori (7-9 anni): Lettura/scrittura avanzate, matematica (x,/,frazioni), scienze, arti/musica, ed. fisica, **Anthaliano** moderno/antico base, **Inglese**.
        * d. `[]` Medie Inferiori (10-12 anni): Letteratura/grammatica, matematica (algebra/geometria base), scienze (bio/chim/fis intro), storia/geografia, ed. tecnologica/informatica base, ed. fisica, **Anthaliano** moderno/antico base, **Inglese**.
        * e. `[]` Medie Superiori (13-15 anni): Letteratura/composizione, matematica avanzata, scienze avanzate, studi sociali, lingue straniere avanzate (**Anthaliano** antico, **Inglese**), ed. tecnologica/informatica avanzata, ed. fisica, arti/musica avanzate.
        * f. `[]` Superiori (16-18 anni, obbligatorio): Materie accademiche avanzate, progetti di ricerca, preparazione carriera/orientamento, **Anthaliano** moderno/antico avanzato, **Inglese**.
        * g. `[]` Superior Facoltativo (19-21 anni, pre-universitaria): Specializzazione, ricerca, stage, orientamento universitario.
        * h. `[]` Università (21+ anni): Struttura (Triennale, Magistrale, Dottorato), Facoltà (Scienze/Tecnologia, Arti/Lettere, Economia/Gestione, Ingegneria, Medicina/Scienze Salute), materie esempio, programmi scambio.
    * 3. `[]` **Meccaniche Scolastiche per NPC:**
        * a. `[]` NPC frequentano scuola (simulazione presenza/lotto scuola).
        * b. `[]` Performance scolastica (voti, compiti) influenzata da NPC.
        * c. `[]` Impatto performance su sviluppo abilità, aspirazioni, opportunità.
        * d. `[]` "Saltare la scuola" con conseguenze.
        * e. `[]` Attività extracurriculari, viaggi educativi, supporto studenti.

**VI. INTEGRAZIONE FUNZIONALITÀ E CONCETTI DA `simai/election`** `[P]` `[ELEC]`
    * 1. **Modelli Comportamentali NPC Avanzati:**
        * a. `[P]` Personalità Complesse e Tratti NPC.
        * b. `[]` Implementazione di **Bias Cognitivi**.
        * c. `[]` Decisioni NPC Basate su **Valori/Identità Personale vs. Bisogni Immediati/Logica Situazionale**.
        * d. `[P]` Influenza **Reti Sociali Esplicite** (`RelationshipComponent`).
        * e. `[]` **"Alfabetizzazione" Sociale/Emotiva e Pensiero Critico NPC**.
        * f. `[]` **Apprendimento e Adattamento Comportamentale Avanzato NPC**.
    * 2. `[]` **Miglioramenti alla Simulazione del "Mondo Vivo"**.
        * a. `[]` NPC perseguono **"Progetti Personali"** con gestione risorse e fasi (vedi IV.4.h).
        * b. `[]` **Eventi Casuali Dinamici** influenzati da "stato del mondo" e "argomenti caldi" in Anthalys (vedi XI.b).
        * c. `[]` Modellare **"Fonti di Informazione" fittizie** in Anthalys (media locali, social media simulati) con bias, che influenzano NPC (vedi XI.c).
        * d. `[]` **Sistemi di "Scelta Collettiva"** o influenza di gruppo per NPC (per attività comunitarie, mode).
        * e. `[]` **Generazione NPC Più Profonda e Unica**, con background e relazioni iniziali.
    * 3. `[]` **Strategie Comportamentali Dinamiche NPC**.
        * a. `[]` NPC definiscono strategie per raggiungere obiettivi personali (sociali, carriera, abilità) adattandole e gestendo risorse (vedi IV.4.s).
    * 4. `[]` **Generazione di Contenuti Testuali (NLG) per SimAI**.
        * a. `[]` "Pensieri" o "voci di diario" testuali più variati per gli NPC.
        * b. `[]` Generazione di "notizie" fittizie o "post social media" all'interno del mondo di Anthalys.
        * c. `[]` Migliorare la varietà del linguaggio **Anthaliano** parlato (se testuale o con più suoni).
    * 5. `[]` **Principi di Progettazione e Validazione per SimAI**.
        * a. `[]` Basare alcuni parametri NPC su concetti reali semplificati.
        * b. `[]` Calibrazione attenta dei parametri di gioco per bilanciamento.
        * c. `[]` Validazione comportamento emergente.
    * 6. `[]` **IA e LLM (Obiettivi a Lungo Termine per SimAI)**.
        * a. `[]` (Ricerca Estrema) Agenti NPC potenziati da LLM.
        * b. `[]` (Ricerca) Approccio Ibrido LLM/Regole.
    * 7. `[P]` **Persistenza Dati Avanzata con SQLite (Evoluzione di XV.1):** `[ELEC]` (Attualmente JSON, SQLite è futuro)
        * a. `[]` **Migrazione da JSON a SQLite:** Pianificare e implementare la transizione dal sistema di salvataggio basato su JSON (implementato in XV.1) a un database SQLite.
        * b. `[]` Progettare lo schema del database SQLite per `GameState`, `Character` (con UUID univoco come da VI.7.b originale, ora fuso qui), oggetti del mondo dinamici, relazioni, e altre entità persistenti.
        * c. `[]` Implementare la logica di mapping tra oggetti Python e tabelle SQLite (valutare ORM come SQLAlchemy a lungo termine).
        * d. `[]` Garantire la retrocompatibilità o un percorso di migrazione per i salvataggi JSON esistenti, se fattibile e desiderato.
        * e. `[]` Sfruttare le transazioni SQLite per garantire l'atomicità e l'integrità dei salvataggi.
        * f. `[x]` Il salvataggio/caricamento dei dati dei componenti è stato impostato nei rispettivi metodi `to_dict`/`from_dict`.
        * g. `[]` Memorizzare statistiche aggregate di vita per ogni NPC e per la città di Anthalys (come da VI.7.d originale, ora fuso qui).

**VII. DINAMICHE SOCIALI E RELAZIONALI AVANZATE** (`RelationshipComponent`)
    * 1. **Interazioni Sociali:** `[P]`
        * a. `[P]` Interazione "Intimità" base, Telefonare (azioni refactorizzate).
        * b. `[]` Interazioni sociali più varie.
        * c. `[]` Interazioni di gruppo.
    * 2. **Sistema di Relazioni:** `[P]`
        * a. `[x]` I punteggi di relazione sono in `RelationshipComponent`.
        * b. `[P]` Grafo sociale esplicito (base con UUID, influenza da implementare). `[ELEC]`
    * 3. `[]` Dinamiche di Gruppo e Comunità.
    * 4. `[]` **Vacanze e Viaggi NPC.** `[NUOVO_USER]`

**VIII. SISTEMA ECONOMICO, LAVORO E WELFARE DI ANTHALYS** (`CareerComponent`, `FinanceComponent`)
    * 1. **Lavoro e Carriere per NPC:** `[P]` `[NUOVO_USER]`
        * a. `[P]` Definire tipi di lavoro e percorsi di carriera (`CareerComponent` con `CAREER_DEFINITIONS`).
        * b. `[P]` Implementare **Orario di Lavoro**.
        * c. `[P]` **Stipendi**.
        * d. `[P]` IA NPC per cercare/ottenere/mantenere lavoro, promozioni.
        * e. `[]` Luoghi di lavoro fisici in Anthalys.
        * f. `[P]` Performance lavorativa.
        * g. `[P]` Licenziamento/dimissioni.
    * 2. `[]` **Sistema Fiscale di Anthalys.** `[NUOVO_USER]`
        * a. `[]` Tasse sul Reddito con scaglioni progressivi.
        * b. `[]` Esenzione fiscale per redditi < 3,000 AA.
        * c. `[]` Dichiarazione e raccolta tasse ogni 9 mesi di gioco.
    * 3. `[]` **Benefici e Sicurezza Sociale.** `[NUOVO_USER]`
        * a. `[]` **Assicurazione Sanitaria** (lavoratori, copertura basso reddito < 6,000 AA via **Istituti Fondine**).
        * b. `[]` **Sistema Pensionistico**.
        * c. `[]` **Indennità di Maternità/Paternità**.
        * d. `[]` **Sicurezza sul Lavoro**.
    * 4. `[]` **Vacanze e Permessi Lavorativi.** `[NUOVO_USER]`
        * a. `[]` Vacanze Annuali pagate (24 giorni/anno lavorativo di Anthalys).
        * b. `[]` IA NPC per richiedere/usare vacanze.
        * c. `[]` Permessi per Malattia e Emergenze Familiari.
    * 5. `[]` **Tassa sui Rifiuti e Incentivi Economici.** `[NUOVO_USER]`

**IX. ABILITÀ (SKILLS) (`SkillComponent`)** `[P]`
    * a. `[P]` Le definizioni delle abilità e `SkillComponent` base sono pronti.
    * b. `[P]` IA per scelta sviluppo abilità (da collegare ad aspirazioni, carriera, tratti).
    * c. `[P]` Abilità influenzano successo azioni, carriera (da implementare nelle logiche specifiche).

**X. GRAFICA E AUDIO**
    * 1. **Grafica:** `[P]`
        * a. `[x]` Sprite NPC adulti (idle/walk), immagine letto, icone PNG base.
        * b. `[]` Spritesheets per altri stadi di vita/stati NPC.
        * c. `[P]` Sprites/immagini per oggetti del mondo e UI.
        * d. `[]` **Sistema di Vestiario Multiplo per NPC**. `[NUOVO_USER]`
        * e. `[P]` Animazioni più dettagliate (logica di animazione base presente in `Character`).
        * f. `[]` Effetti visivi.
    * 2. `[]` **Audio e Espressività Vocale NPC (Linguaggio Anthaliano)**.
        * a. `[]` Sistema Audio Base (`pygame.mixer`), clip audio base in **Anthaliano**.
        * b. `[]` Voci "Uniche" per Personaggio.
        * c. `[]` Vocabolario Personalizzato (**Anthaliano**).
        * d. `[]` Tono di Voce / Espressione Emotiva Vocale.
        * e. `[]` Sincronizzazione Audio.
        * f. `[]` Effetti Sonori Ambientali e UI.

**XI. INTERFACCIA UTENTE (UI)**
    * 1. Elementi GUI Esistenti: `[P]` (Pannello inferiore, label ora, stato NPC base, pulsanti velocità, barre bisogni base).
    * 2. `[]` Miglioramenti GUI Ispirati da `simai/election`. `[ELEC]`
    * 3. `[P]` Miglioramenti Generali UI (layout barra di stato inferiore proposto con sezioni sinistra/centro/destra).
    * 4. `[]` **Interfaccia per Documento d'Identità e Servizi Correlati**.

**XII. DOCUMENTO DI IDENTITÀ DI ANTHALYS E SERVIZI INTEGRATI** `[]` `[NUOVO_USER]`
    * a. `[]` Dati Documento, generazione **CIP** univoco.
    * b. `[]` Integrazione nel Personaggio.
    * c. `[]` Funzionalità Codice QR (Simulazione Accesso Base/Completo).
    * d. `[]` Caratteristiche di Sicurezza (Lore).
    * e. `[]` **Carta di Pagamento Integrata** (collegata a VII).
    * f. `[]` Accesso Dati per Titolare (Simulazione/UI Debug).
    * g. `[]` Utilizzo per Punti Raccolta Rifiuti (vedi XIII.2).

**XIII. GESTIONE AMBIENTALE E CIVICA DI ANTHALYS** `[]` `[NUOVO_USER]`
    * 1. **Sistema di Raccolta Differenziata Individuale.**
    * 2. **Sistema di Punti e Bonus per Raccolta Differenziata.**
    * 3. `[]` Trattamento e Riutilizzo dei Rifiuti (Narrativa).
    * 4. **Smaltitori Automatici Domestici.**

**XIV. EVENTI CASUALI E SCENARI GUIDATI** `[]`
    * a. `[]` Eventi casuali.
    * b. `[]` IA NPC per reazione credibile, influenzata da bias/pensiero critico. `[ELEC]`
    * c. `[]` Piccoli scenari o storie emergenti.
    * d. `[]` Eventi legati a rifiuti, sostenibilità, scuola, lavoro.

**XV. SISTEMI TECNICI** `[P]`
    * 1. Salvataggio e Caricamento Partita `[]` (**Priorità Alta**) (Includere tutti i nuovi sistemi). `[ELEC]`
    * 2. Opzioni di Gioco e Impostazioni `[]`.

**XVI. SISTEMI UNICI E AVANZATI (Idee Speciali per SimAI)** `[]`
    * `[]` (Riflessione Interna, Cultura Emergente, Linguaggio Anthaliano Dinamico, IA Regista, Eredità, Sogni)

**XVII. LOCALIZZAZIONE E MULTILINGUA** `[]`
    * a. `[]` **Analisi e Scelta Sistema di Localizzazione**.
        * i. `[]` Valutare librerie Python per i18n/l10n (es. `gettext`, `fluent`, `polyglot`) o un sistema custom basato su file JSON/YAML.
        * ii.`[]` Strutturare i file di lingua (es. un file per lingua con coppie chiave-valore).
    * b. `[]` **Esternalizzare Stringhe dalla UI**.
        * i. `[]` Identificare tutte le stringhe visibili all'utente nella UI (etichette `pygame_gui`, testo disegnato manualmente, messaggi di debug che potrebbero diventare notifiche).
        * ii.`[]` Sostituire le stringhe hardcoded con chiavi di traduzione (es. `traduzione.get("UI_BTN_PAUSE")`).
    * c. `[]` **Creare File di Lingua Iniziali**.
        * i. `[]` File per l'Italiano (lingua di sviluppo attuale).
        * ii.`[]` File per l'Inglese (come prima lingua target per la traduzione).
    * d. `[]` **Implementare Logica di Caricamento Lingua**.
        * i. `[]` Funzione per caricare il file di lingua appropriato all'avvio o tramite opzioni.
        * ii.`[]` Aggiungere opzione di gioco per cambiare lingua (vedi XV.2).
    * e. `[]` **Gestione Testo Dinamico e Pluralizzazione**.
        * i. `[]` Considerare come gestire stringhe che includono variabili (es. `f"NPC {nome} è {azione}"`) e la pluralizzazione (es. "1 giorno" vs "2 giorni").
    * f. `[]` **Font Support**.
    * g. `[]` **Adattamento Layout UI**.

---