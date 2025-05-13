# TODO List: Simulatore di Vita "SimAI" (Città di Anthalys)

**Legenda:**
* `[]`: Non iniziato
* `[P]`: Parzialmente completato / In corso
* `[x]`: Completato (per la sua implementazione base/attuale)
* `[+]`: Funzioni aggiuntive possibili/idee (generalmente per dopo o di complessità maggiore)
* `[ELEC]`: Punto ispirato/adattato dalla TODO List di `simai/election`
* `[NUOVO_USER]`: Punto aggiunto su specifica richiesta dell'utente in questa iterazione (usato nelle iterazioni precedenti, mantenuto per coerenza se presente nel file originale)
* `[ESPANSIONE]`: Punto che espande significativamente una funzionalità esistente o pianificata (usato nelle iterazioni precedenti)

---

**I. FONDAMENTA DEL GIOCO E MOTORE**
    * 1. **Core Pygame:** `[x]`
        * a. Creare il file principale del gioco (`main.py`). `[x]`
        * b. Implementare la finestra di gioco base di Pygame. `[x]`
        * c. Creare il loop di gioco principale. `[x]`
        * d. Gestire l'evento di chiusura della finestra. `[x]`
        * e. Impostare un clock per il framerate (FPS). `[x]`
    * 2. **Struttura Modulare del Codice:** `[x]`
        * a. Organizzazione cartelle base (`assets`, `src`, `modules/needs`). `[x]`
        * b. Creazione file principali (`config.py`, `game_utils.py`, `ai_system.py`). `[x]`
        * c. Definizione classe `Character` base in `src/entities/character.py`. `[x]`
        * d. Implementazione `__init__.py` per packages. `[x]`
    * 3. **Sistema di Tempo di Gioco Avanzato:** `[x]`
        * a. Ciclo giorno/notte di 28 ore con colori cielo graduali e nome del periodo con icona. `[x]`
        * b. 6 Velocità di gioco controllabili (0-5) con impostazioni personalizzate e pulsanti UI. `[x]`
        * c. Calcolo e visualizzazione data estesa: Giorno (1-24), Mese (1-18), Anno. `[x]`
        * d. Età degli NPC che progredisce in base al tempo di gioco. `[x]`
        * e. `[+]` Calendario con eventi unici (festività stagionali, compleanni NPC con possibili celebrazioni/moodlet).
        * f. `[+]` Meteo dinamico (sole, pioggia, nuvole, neve, vento) e stagioni, con impatto visivo e su gameplay (umore NPC, scelta attività, crescita piante se presenti, ecc.).
    * 4. **Sistema di Pathfinding NPC:** `[x]`
        * a. Integrazione libreria Pathfinding A*. `[x]`
        * b. Creazione griglia di navigazione basata su `TILE_SIZE`. `[x]`
        * c. Marcatura ostacoli fissi (oggetti) sulla griglia. `[x]`
        * d. Implementazione movimento diagonale per NPC. `[x]`
        * e. Logica IA per far puntare NPC a celle adiacenti camminabili per oggetti grandi. `[x]`
        * f. `[+]` Pathfinding per target mobili (altri NPC) più sofisticato (es. predizione o ricalcolo frequente).
        * g. `[+]` Gestione ostacoli dinamici (altri NPC che bloccano il percorso).
        * h. `[+]` Algoritmi di evitamento collisioni più fluidi tra NPC.
        * i. `[+]` Costi di attraversamento diversi per differenti tipi di terreno/superfici (se implementati).

**II. MONDO DI ANTHALYS (Open World e Costruzione)**
    * 1. `[]` **Funzionalità Open World di Base:**
        * a. `[]` Transizione da lotto singolo a mappa open-world per la città di Anthalys.
        * b. `[]` Sistema di coordinate globali per la città e gestione caricamento/streaming di aree (chunk).
        * c. `[+]` Pathfinding su larga scala per navigazione cittadina tra lotti e quartieri.
    * 2. `[]` **Creazione della Città di Anthalys:**
        * a. `[]` Progettazione mappa base: layout stradale, zone principali.
        * b. `[]` Definizione e creazione di quartieri distinti (es. residenziale, commerciale, parchi, industriale, governativo) con estetica e lotti tipici.
    * 3. `[]` **Infrastrutture e Lotti Cittadini:**
        * a. `[]` Sistema stradale dettagliato e marciapiedi.
        * b. `[]` Sistema di indirizzi: nomi per strade e numeri civici per edifici.
        * c. `[]` Implementazione lotti residenziali (case per NPC, inizialmente placeholder, poi con interni base).
        * d. `[]` Implementazione lotti comunitari/commerciali con funzionalità base:
            * i.  `[]` Negozi generici (per acquisto oggetti base).
            * ii. `[]` Supermercati/Mercati per acquisto cibo.
            * iii.`[]` Luoghi di lavoro (uffici, negozi, ecc. - vedi Sezione VI).
            * iv. `[]` Servizi pubblici: Stazione di polizia, Caserma dei vigili del fuoco, Ospedale (edifici e interazioni base).
            * v.  `[]` Luoghi di svago/cultura: Parchi, cinema, ristoranti, palestre, biblioteche, musei.
        * e. `[+]` Sistema di trasporti pubblici base (es. fermate autobus, NPC li usano).
    * 4. `[+]` **Ambiente Dinamico e Interattivo:**
        * a. `[+]` Impatto visivo e su NPC di Meteo e Stagioni.
        * b. `[+]` (Molto Avanzato) Modalità "Costruisci/Compra" per modificare lotti.

**III. SIMULAZIONE NPC (Bisogni, IA, Ciclo Vita, Caratteristiche)**
    * 1. **Sistema dei Bisogni:** `[x]`
        * a. `[x]` 7 Bisogni modulari implementati (`Vescica`, `Fame`, `Energia`, `Divertimento`, `Socialità`, `Igiene`, `Intimità`) con meccaniche di variazione (tassi base, moltiplicatori periodo), inizializzazione casuale.
        * b. `[+]` Aggiungere bisogni più complessi o secondari (es. Comfort, Ambiente, Sete, Stress, Sicurezza).
        * c. `[+]` Interdipendenze più profonde tra bisogni.
        * d. `[+]` Modificatori di bisogno a lungo termine (tratti, età, salute, oggetti posseduti, qualità dell'ambiente).
        * e. `[+]` Bisogni emergenti specifici per stadi di vita (es. "gioco" per bambini) o situazioni.
        * f. `[]` **Sistema di Malattie e Salute:** NPC possono ammalarsi (casualmente, per scarsa igiene/energia/cibo, o per eventi specifici) con impatto su bisogni, umore, capacità lavorative/sociali. `[]` NPC cercano cure (riposo, medicine - se disponibili, interazione con Ospedale/Medico). `[NUOVO_USER]`
    * 2. **Ciclo Vita NPC:** `[P]`
        * a. `[x]` Età NPC che progredisce (giorni, mesi, anni) e visualizzazione base.
        * b. `[P]` Meccanica di gravidanza base (probabilità, durata, reset stato, no re-gravidanza durante).
        * c. `[]` Nascita di nuovi NPC (bambini, uso di `bundles.png`), gestione visiva e comportamentale di base per neonati (bisogni specifici, interazioni con genitori/tutori).
        * d. `[]` Implementare stadi di vita successivi (Infanzia, Elementari Inf/Sup, Medie Inf/Sup, Superiori) con sprite (`child.png`, `teen.png`), bisogni, comportamenti e iscrizione al **Sistema Scolastico di Anthalys** (vedi IV). `[ESPANSIONE]`
        * e. `[+]` Stadio di vita Anziano, invecchiamento visivo, morte naturale.
        * f. `[+]` Albero genealogico e gestione legami familiari.
        * g. `[]` Congedo retribuito per maternità/paternità (collegato a VI.3.c). `[NUOVO_USER]`
    * 3. **Caratteristiche Personaggio Approfondite:** `[P]`
        * a. `[P]` Sogni/Aspirazioni principali NPC (concetto base). `[ELEC]` `[NUOVO_USER]`
        * b. `[]` Tratti di Personalità (Timido, Ambizioso, Creativo, Pigro, Ordinato, Estroverso, Introverso, Irritabile, Allegro, **Partigiano Forte** `[ELEC]`, ecc.). `[ELEC]`
        * c. `[+]` Vizi e Dipendenze (shopping compulsivo, dipendenza da "caffè di Anthalys", gioco d'azzardo fittizio) con meccaniche di craving e conseguenze. `[NUOVO_USER]`
        * d. `[+]` Manie e Fissazioni (collezionismo, ossessione per pulizia/hobby, parlare solo di un certo argomento). `[NUOVO_USER]`
        * e. `[+]` Paure e Fobie (buio, animali fittizi, impegno, fallimento) con impatto su umore/comportamento. `[NUOVO_USER]`
        * f. `[+]` Talenti Innati / Inclinazioni Naturali per abilità.
        * g. `[+]` Valori Fondamentali/Etica (Onestà, Lealtà, Potere, ecc.).
        * h. `[+]` Stile di Comunicazione Unico.
        * i. `[+]` Segreti NPC.
    * 4. **Intelligenza Artificiale NPC (Comportamento e Decisioni):** `[P]`
        * a. `[P]` Soddisfa i 7 bisogni attuali tramite oggetti/azioni esistenti. `[]` IA per usare nuovi oggetti (TV, Doccia, Oggetti Scolastici).
        * b. `[x]` Logica decisionale base (priorità bisogni, wandering).
        * c. `[]` Sistema di Umore (Mood) e "Moodlet/Buff".
        * d. `[+]` Influenza Umore sulle Decisioni.
        * e. `[P]` Obiettivi a Breve e Lungo Termine/Aspirazioni (guidati da III.3.a).
        * f. `[+]` Pianificazione AI Avanzata (GOAP, Behavior Trees), Routine, Apprendimento, Migliore Percezione Ambientale, Gestione Fallimenti.
        * g. `[]` IA per scelta **vestiario** (contesto: meteo, ora, luogo, attività, evento sociale, uniforme scolastica/lavorativa). `[NUOVO_USER]`
        * h. `[+]` Simulazione "Off-Screen" (LoD).
        * i. `[]` IA per interagire con servizi cittadini (Documento d'Identità, punti raccolta rifiuti, obblighi scolastici/lavorativi).

**IV. SISTEMA SCOLASTICO DI ANTHALYS** `[]` `[NUOVO_USER]`
    * 1. **Struttura e Calendario Scolastico:** `[]`
        * a. `[]` Definire 8 Livelli Scolastici (Infanzia -> Università) con fasce d'età.
        * b. `[]` Implementare Anno Scolastico (18 mesi, 324gg didattica, Inizio 13/13, Fine 12/9).
        * c. `[]` Implementare Pause Scolastiche (Primaverile 12gg, Estiva 72gg).
    * 2. **Curriculum e Materie per Livello:** `[]`
        * a. `[]` Infanzia (1-3 anni): Sviluppo motorio/sociale/linguistico, **Anthaliano** moderno base.
        * b. `[]` Elementari Inferiori (4-6 anni): Alfabetizzazione base, matematica base, scienze intro, arti, **Anthaliano** moderno, **Inglese**.
        * c. `[]` Elementari Superiori (7-9 anni): Lettura/scrittura avanzate, matematica (x,/,frazioni), scienze, arti/musica, ed. fisica, **Anthaliano** moderno/antico base, **Inglese**.
        * d. `[]` Medie Inferiori (10-12 anni): Letteratura/grammatica, matematica (algebra/geometria base), scienze (bio/chim/fis intro), storia/geografia, ed. tecnologica/informatica base, ed. fisica, **Anthaliano** moderno/antico base, **Inglese**.
        * e. `[]` Medie Superiori (13-15 anni): Letteratura/composizione, matematica avanzata, scienze avanzate, studi sociali, lingue straniere avanzate (**Anthaliano** antico, **Inglese**), ed. tecnologica/informatica avanzata, ed. fisica, arti/musica avanzate.
        * f. `[]` Superiori (16-18 anni, obbligatorio): Materie accademiche avanzate, progetti di ricerca, preparazione carriera/orientamento, **Anthaliano** moderno/antico avanzato, **Inglese**.
        * g. `[]` Superior Facoltativo (19-21 anni, pre-universitaria): Specializzazione, ricerca, stage, orientamento universitario.
        * h. `[]` Università (21+ anni): Struttura (Triennale, Magistrale, Dottorato), Facoltà (Scienze/Tecnologia, Arti/Lettere, Economia/Gestione, Ingegneria, Medicina/Scienze Salute), materie esempio, programmi scambio.
    * 3. **Meccaniche Scolastiche per NPC:** `[]`
        * a. `[]` NPC frequentano scuola (simulazione presenza/lotto scuola).
        * b. `[]` Performance scolastica (voti, compiti) influenzata da NPC.
        * c. `[+]` Impatto performance su sviluppo abilità, aspirazioni, opportunità.
        * d. `[+]` "Saltare la scuola" con conseguenze.
        * e. `[+]` Attività extracurriculari, viaggi educativi, supporto studenti.

**V. INTEGRAZIONE FUNZIONALITÀ E CONCETTI DA `simai/election`** `[P]` `[ELEC]`
    * *(Questa sezione adatta e integra le idee dalla TODO list di `simai/election` nel contesto della simulazione di vita SimAI, focalizzandosi su IA avanzata, dinamiche mondiali, e principi di sviluppo.)*
    * 1. **Modelli Comportamentali NPC Avanzati (Adattato da "Modelli di Votanti"):**
        * a. `[P]` Personalità Complesse e Tratti NPC (vedi III.3).
        * b. `[]` Implementazione di **Bias Cognitivi** (Effetto Bandwagon/Underdog, Bias di Conferma, Ragionamento Motivato, Hindsight Bias, ecc.) nell'IA decisionale e sociale.
        * c. `[+]` Decisioni NPC Basate su **Valori/Identità Personale vs. Bisogni Immediati/Logica Situazionale**.
        * d. `[P]` Influenza **Reti Sociali Esplicite** e Diffusione Idee/Umore (vedi IV.2.d).
        * e. `[]` **"Alfabetizzazione" Sociale/Emotiva e Pensiero Critico NPC** (vedi IV.3.j).
        * f. `[+]` **Apprendimento e Adattamento Comportamentale Avanzato NPC** (vedi III.4.k).
    * 2. **Miglioramenti alla Simulazione del "Mondo Vivo":**
        * a. `[]` NPC perseguono **"Progetti Personali"** con gestione risorse e fasi (vedi III.4.h).
        * b. `[+]` **Eventi Casuali Dinamici** influenzati da "stato del mondo" e "argomenti caldi" in Anthalys (vedi X.b).
        * c. `[+]` Modellare **"Fonti di Informazione" fittizie** in Anthalys (media locali, social media simulati) con bias, che influenzano NPC (vedi X.c).
        * d. `[+]` **Sistemi di "Scelta Collettiva"** o influenza di gruppo per NPC (per attività comunitarie, mode).
        * e. `[+]` **Generazione NPC Più Profonda e Unica**, con background e relazioni iniziali.
    * 3. **Strategie Comportamentali Dinamiche NPC (Adattato da "Strategie di Campagna"):**
        * a. `[+]` NPC definiscono strategie per raggiungere obiettivi personali (sociali, carriera, abilità) adattandole e gestendo risorse (vedi III.4.s).
    * 4. **Generazione di Contenuti Testuali (NLG) per SimAI:**
        * a. `[]` "Pensieri" o "voci di diario" testuali più variati per gli NPC.
        * b. `[+]` Generazione di "notizie" fittizie o "post social media" all'interno del mondo di Anthalys.
        * c. `[+]` Migliorare la varietà del linguaggio **Anthaliano** parlato (se testuale o con più suoni).
    * 5. **Principi di Progettazione e Validazione per SimAI:**
        * a. `[+]` Basare alcuni parametri NPC su concetti reali semplificati.
        * b. `[]` Calibrazione attenta dei parametri di gioco per bilanciamento.
        * c. `[]` Validazione comportamento emergente.
    * 6. **IA e LLM (Obiettivi a Lungo Termine per SimAI):**
        * a. `[+]` (Ricerca Estrema) Agenti NPC potenziati da LLM.
        * b. `[+]` (Ricerca) Approccio Ibrido LLM/Regole.
    * 7. **Persistenza Dati Avanzata (Ispirato da "Database SQLite"):** (vedi XIII.1)
        * a. `[]` Utilizzare un sistema robusto (es. SQLite) per persistenza NPC dettagliata e stato mondo.
        * b. `[]` Ogni NPC (e oggetti significativi) con UUID.
        * c. `[]` Salvare/caricare: tratti, valori, abilità, relazioni, età, gravidanza, storia personale, finanze, inventario, progressi lavorativi/scolastici.
        * d. `[+]` Memorizzare statistiche aggregate di vita per ogni NPC e per la città di Anthalys.

**VI. DINAMICHE SOCIALI E RELAZIONALI AVANZATE** (Ex Sezione IV, rinumerata per inserimento Scuola)
    * 1. **Interazioni Sociali:** `[P]`
        * a. `[x]` Interazione "Intimità" base, Telefonare.
        * b. `[]` Interazioni sociali più varie (parlare in **Anthaliano**, ecc.).
        * c. `[+]` Interazioni di gruppo.
    * 2. **Sistema di Relazioni:** `[]`
        * a. `[]` Punteggi di relazione (amicizia, romanticismo, inimicizia, famiglia, professionale).
        * b. `[+]` Grafo sociale esplicito con meccanismi di influenza. `[ELEC]`
    * 3. `[+]` Dinamiche di Gruppo e Comunità (reputazione pubblica, eventi sociali organizzati da NPC).
    * 4. `[]` **Vacanze e Viaggi NPC.** `[NUOVO_USER]`

**VII. SISTEMA ECONOMICO, LAVORO E WELFARE DI ANTHALYS** `[]` (Ex Sezione VI)
    * 1. **Lavoro e Carriere per NPC:** `[]` `[NUOVO_USER]`
        * a. `[]` Definire tipi di lavoro e percorsi di carriera.
        * b. `[]` Implementare **Orario di Lavoro** (9h/giorno, 5gg/sett, 15 mesi lavoro/anno + 3 mesi pausa).
        * c. `[]` **Stipendi** (valuta "Athel" - AA, scale di stipendio). NPC ricevono stipendio.
        * d. `[]` IA NPC per cercare/ottenere/mantenere lavoro, promozioni.
        * e. `[]` Luoghi di lavoro fisici in Anthalys.
        * f. `[+]` Performance lavorativa.
        * g. `[+]` Licenziamento/dimissioni.
    * 2. **Sistema Fiscale di Anthalys:** `[]` `[NUOVO_USER]`
        * a. `[]` Tasse sul Reddito con scaglioni progressivi.
        * b. `[]` Esenzione fiscale per redditi < 3,000 AA.
        * c. `[]` Dichiarazione e raccolta tasse ogni 9 mesi di gioco.
    * 3. **Benefici e Sicurezza Sociale:** `[]` `[NUOVO_USER]`
        * a. `[]` **Assicurazione Sanitaria** (lavoratori, copertura basso reddito < 6,000 AA via **Istituti Fondine**).
        * b. `[]` **Sistema Pensionistico**.
        * c. `[]` **Indennità di Maternità/Paternità**.
        * d. `[+]` **Sicurezza sul Lavoro**.
    * 4. **Vacanze e Permessi Lavorativi:** `[]` `[NUOVO_USER]`
        * a. `[]` Vacanze Annuali pagate (24 giorni/anno lavorativo di Anthalys).
        * b. `[]` IA NPC per richiedere/usare vacanze.
        * c. `[]` Permessi per Malattia e Emergenze Familiari.
    * 5. **Tassa sui Rifiuti e Incentivi Economici:** `[]` `[NUOVO_USER]` (vedi XII.2)

**VIII. ABILITÀ (SKILLS)** `[]`
    * a. `[]` NPC sviluppano abilità (Cucina, Manualità, Logica, Carisma, Pensiero Critico/Alfabetizzazione Mediatica, ecc.).
    * b. `[+]` IA per scelta sviluppo abilità (legate a carriera, aspirazioni, tratti, scuola).
    * c. `[]` Abilità influenzano successo azioni, carriera, interazioni, qualità oggetti creati/riparati.

**IX. GRAFICA E AUDIO** (Ex Sezione VI)
    * 1. **Grafica:** `[P]`
        * a. `[P]` Sprite NPC adulti (idle/walk), immagine letto, icone PNG.
        * b. `[]` Spritesheets per altri stadi di vita/stati NPC.
        * c. `[]` Sprites/immagini per tutti oggetti interattivi e edifici di Anthalys.
        * d. `[]` **Sistema di Vestiario Multiplo per NPC** e IA per cambio abiti. `[NUOVO_USER]`
        * e. `[+]` Animazioni più dettagliate.
        * f. `[+]` Effetti visivi.
    * 2. **Audio e Espressività Vocale NPC (Linguaggio Anthaliano):** `[]`
        * a. `[]` Sistema Audio Base (`pygame.mixer`), clip audio base in **Anthaliano**.
        * b. `[]` Voci "Uniche" per Personaggio.
        * c. `[]` Vocabolario Personalizzato (**Anthaliano**).
        * d. `[]` Tono di Voce / Espressione Emotiva Vocale.
        * e. `[+]` Sincronizzazione Audio.
        * f. `[]` Effetti Sonori Ambientali e UI.

**X. INTERFACCIA UTENTE (UI)** (Ex Sezione VII)
    * 1. Elementi GUI Esistenti: `[P]` `[x]`
    * 2. `[+]` Miglioramenti GUI Ispirati da `simai/election`. `[ELEC]`
    * 3. `[+]` Miglioramenti Generali UI.
    * 4. `[]` **Interfaccia per Documento d'Identità e Servizi Correlati** (vedi XI).

**XI. DOCUMENTO DI IDENTITÀ DI ANTHALYS E SERVIZI INTEGRATI** `[]` `[NUOVO_USER]`
    * a. `[]` Dati Documento, generazione **CIP** univoco.
    * b. `[]` Integrazione nel Personaggio.
    * c. `[]` Funzionalità Codice QR (Simulazione Accesso Base/Completo).
    * d. `[+]` Caratteristiche di Sicurezza (Lore).
    * e. `[]` **Carta di Pagamento Integrata** (collegata a VI).
    * f. `[+]` Accesso Dati per Titolare (Simulazione/UI Debug).
    * g. `[]` Utilizzo per Punti Raccolta Rifiuti (vedi XII.2).

**XII. GESTIONE AMBIENTALE E CIVICA DI ANTHALYS** `[]` `[NUOVO_USER]`
    * 1. **Sistema di Raccolta Differenziata Individuale.**
    * 2. **Sistema di Punti e Bonus per Raccolta Differenziata.**
    * 3. `[+]` Trattamento e Riutilizzo dei Rifiuti (Narrativa).
    * 4. **Smaltitori Automatici Domestici.**

**XIII. EVENTI CASUALI E SCENARI GUIDATI** `[]` (Ex Sezione X)
    * a. `[]` Eventi casuali.
    * b. `[+]` IA NPC per reazione credibile, influenzata da bias/pensiero critico. `[ELEC]`
    * c. `[+]` Piccoli scenari o storie emergenti.
    * d. `[+]` Eventi legati a rifiuti, sostenibilità, scuola, lavoro.

**XIV. SISTEMI TECNICI** `[P]` (Ex Sezione XIII)
    * 1. Salvataggio e Caricamento Partita `[]` (**Priorità Alta**) (Includere tutti i nuovi sistemi). `[ELEC]`
    * 2. Opzioni di Gioco e Impostazioni `[]`.

**XV. SISTEMI UNICI E AVANZATI (Idee Speciali per SimAI)** `[]` (Ex Sezione XIV)
    * `[+]` (Riflessione Interna, Cultura Emergente, Linguaggio Anthaliano Dinamico, IA Regista, Eredità, Sogni)

**XVI. LOCALIZZAZIONE E MULTILINGUA** `[]` (**NUOVA SEZIONE**)
    * a. `[]` **Analisi e Scelta Sistema di Localizzazione:**
        * i. `[]` Valutare librerie Python per i18n/l10n (es. `gettext`, `fluent`, `polyglot`) o un sistema custom basato su file JSON/YAML.
        * ii.`[]` Strutturare i file di lingua (es. un file per lingua con coppie chiave-valore).
    * b. `[]` **Esternalizzare Stringhe dalla UI:**
        * i. `[]` Identificare tutte le stringhe visibili all'utente nella UI (etichette `pygame_gui`, testo disegnato manualmente, messaggi di debug che potrebbero diventare notifiche).
        * ii.`[]` Sostituire le stringhe hardcoded con chiavi di traduzione (es. `traduzione.get("UI_BTN_PAUSE")`).
    * c. `[]` **Creare File di Lingua Iniziali:**
        * i. `[]` File per l'Italiano (lingua di sviluppo attuale).
        * ii.`[]` File per l'Inglese (come prima lingua target per la traduzione).
    * d. `[]` **Implementare Logica di Caricamento Lingua:**
        * i. `[]` Funzione per caricare il file di lingua appropriato all'avvio o tramite opzioni.
        * ii.`[+]` Aggiungere opzione di gioco per cambiare lingua (vedi XIII.2).
    * e. `[+]` **Gestione Testo Dinamico e Pluralizzazione:**
        * i. `[+]` Considerare come gestire stringhe che includono variabili (es. `f"NPC {nome} è {azione}"`) e la pluralizzazione (es. "1 giorno" vs "2 giorni").
    * f. `[+]` **Font Support:** Verificare che i font usati supportino i set di caratteri per le lingue target.
    * g. `[+]` **Adattamento Layout UI:** Alcune lingue richiedono più/meno spazio per lo stesso testo.

---