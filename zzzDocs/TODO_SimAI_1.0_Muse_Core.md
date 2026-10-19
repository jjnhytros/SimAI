# SimAI 1.0 — Muse Core
## TODO operativo per una prima versione funzionante e rilasciabile

**Obiettivo:** pubblicare una versione 1.0 di SimAI che permetta di avviare, osservare e influenzare una piccola simulazione autonoma di Anthalys, salvarla e riprenderla in modo affidabile.

**Ambito:** una sola area — *Quartiere delle Muse* — con 4–6 NPC autonomi e un personaggio controllabile dal giocatore.

**Principio di conservazione:** questo documento è un piano di rilascio, non una sostituzione del TODO globale. I sistemi già scritti non vengono cancellati. Le funzionalità non incluse nella 1.0 restano nel backlog globale e saranno integrate in seguito.

**Stato iniziale:** tutte le caselle qui sotto sono da verificare rispetto al repository reale. Non assumere che un task sia assente o presente solo perché il TODO globale lo segna in un certo modo.

---

## 1. Definizione di “Done” per la 1.0

SimAI 1.0 è rilasciabile quando un utente può:

1. Installare il progetto seguendo la documentazione, senza modificare il codice.
2. Inizializzare o aggiornare il database con un comando documentato.
3. Avviare una nuova partita nel Quartiere delle Muse.
4. Osservare il tempo che scorre e gli NPC che prendono decisioni autonome.
5. Controllare un Sim, consultare i suoi bisogni e scegliere azioni.
6. Vedere cambiamenti coerenti in bisogni, umore e relazioni dopo le azioni e il passare del tempo.
7. Salvare la partita, chiudere SimAI, ricaricare il salvataggio e continuare.
8. Ricevere messaggi d'errore comprensibili in caso di input non valido o dati corrotti, senza danneggiare silenziosamente la partita.
9. Eseguire i test automatici e i controlli di qualità previsti dal progetto.
10. Leggere una guida rapida per installazione, avvio, comandi e risoluzione dei problemi comuni.

### Fuori ambito per la 1.0

Queste funzioni non vengono eliminate: sono rinviate a release successive, a meno che il repository non dimostri che una di esse sia già stabile e indispensabile al percorso minimo.

- Economia completa: lavoro, mercato, banche, mutui, investimenti, fiscalità avanzata e AION.
- Politica, elezioni, leggi e partecipazione civica.
- SoNet e servizi digitali.
- Multiplayer, networking distribuito, anti-cheat e PostgreSQL cluster.
- Genetica avanzata, ereditarietà complessa, gravidanza, successione e simulazione di intere genealogie.
- Sistema completo di costruzione/arredamento, editor avanzato, rendering isometrico/3D.
- Rete di trasporto completa, orari di bus/metro e simulazione dettagliata del traffico.
- LLM obbligatorio per le decisioni degli NPC.
- Plugin utente e ottimizzazioni speculative prima di aver misurato le prestazioni.

---

## 2. P0 — Audit e baseline del repository

- [ ] **P0.1** Verificare la struttura reale del repository, gli entry point, i modelli, i servizi, le migrazioni e i test già esistenti.
- [ ] **P0.2** Confrontare il codice con il TODO globale e classificare i task: `riutilizzabile`, `da completare`, `da correggere`, `non necessario per 1.0`.
- [ ] **P0.3** Creare un branch di rilascio dedicato e registrare il commit di partenza.
- [ ] **P0.4** Verificare l'installazione pulita con la versione Python dichiarata dal progetto.
- [ ] **P0.5** Verificare `pyproject.toml`, dipendenze, configurazione, logging e comandi CLI effettivi.
- [ ] **P0.6** Verificare che le migrazioni Alembic funzionino su un database vuoto e su un database già inizializzato.
- [ ] **P0.7** Eseguire lint, typecheck e test disponibili; registrare i problemi preesistenti prima di modificarli.
- [ ] **P0.8** Scrivere un breve `docs/release/1.0-baseline.md` con lo stato verificato e i blocchi reali.

**Gate P0:** è possibile installare il progetto, identificare ciò che funziona davvero e ripetere i controlli iniziali.

---

## 3. P1 — Motore minimo affidabile

### Tempo e tick

- [ ] **P1.1** Verificare o completare il tempo canonico di Anthalys e il suo calendario.
- [ ] **P1.2** Implementare o consolidare il ciclo giorno/notte; le altre fasi della giornata possono essere mantenute se già disponibili.
- [ ] **P1.3** Definire un unico ordine dei sistemi eseguiti a ogni tick.
- [ ] **P1.4** Rendere espliciti pausa, ripresa e avanzamento controllato del tempo.
- [ ] **P1.5** Garantire che un tick fallito non lasci uno stato parzialmente aggiornato senza segnalazione e recupero definiti.
- [ ] **P1.6** Rendere le decisioni riproducibili con seed configurabile; registrare seed e versione delle regole nei report di debug.

### Persistenza

- [ ] **P1.7** Verificare schema DB, migrazioni e relazioni essenziali per una partita.
- [ ] **P1.8** Implementare o consolidare `new game`, `save`, `load` e `list saves`.
- [ ] **P1.9** Versionare i dati di salvataggio e gestire file mancanti, corrotti o incompatibili con errori comprensibili.
- [ ] **P1.10** Testare che un salvataggio ricaricato mantenga il medesimo stato logico: tempo, personaggi, bisogni, relazioni, posizioni e azioni in corso.
- [ ] **P1.11** Definire un comportamento sicuro per autosalvataggio e interruzioni; nessuna doppia applicazione di effetti dopo il riavvio.

**Gate P1:** una partita può avanzare, essere salvata, chiusa e ripresa senza perdita o duplicazione di stato.

---

## 4. P2 — Un quartiere, pochi personaggi, vita autonoma

### Mondo iniziale

- [ ] **P2.1** Creare o verificare il seed del *Quartiere delle Muse*.
- [ ] **P2.2** Predisporre almeno 3 location funzionali, per esempio: abitazione, piazza/luogo sociale e caffè o luogo ricreativo.
- [ ] **P2.3** Verificare che le location abbiano identificativi stabili, capacità/posizioni coerenti e collegamenti percorribili.
- [ ] **P2.4** Popolare il mondo con 4–6 NPC iniziali dotati di nome, età, tratti essenziali, bisogni e relazioni iniziali plausibili.
- [ ] **P2.5** Garantire che il seed sia ripetibile e non crei duplicati se eseguito più volte.

### Bisogni e decisioni

- [ ] **P2.6** Attivare i quattro bisogni essenziali della prima release: `HUNGER`, `THIRST`, `FUN`, `INTIMACY`.
- [ ] **P2.7** Definire intervalli, decadimento, soglie e conseguenze osservabili per ogni bisogno.
- [ ] **P2.8** Implementare un insieme ristretto di azioni utilizzabili: mangiare, bere, riposare/recuperare, divertirsi, parlare e stare in compagnia.
- [ ] **P2.9** Fare scegliere agli NPC le azioni con una utility AI deterministica a parità di seed e stato.
- [ ] **P2.10** Validare le azioni nel servizio di dominio prima di eseguirle: posizione, risorse, stato e prerequisiti devono essere validi.
- [ ] **P2.11** Evitare che gli NPC restino bloccati senza azioni valide; prevedere fallback e log diagnostici.
- [ ] **P2.12** Consentire agli NPC di continuare a vivere quando il giocatore non li controlla.

### Personalità, umore e relazioni

- [ ] **P2.13** Attivare un catalogo piccolo e documentato di tratti con effetti comprensibili sulle decisioni.
- [ ] **P2.14** Attivare mood e pochi moodlet con durata e modificatori verificabili.
- [ ] **P2.15** Implementare relazioni essenziali tra personaggi: conoscenza/amicizia e variazione del legame tramite interazioni.
- [ ] **P2.16** Implementare almeno 2–3 interazioni sociali con effetti persistenti su relazione e umore.
- [ ] **P2.17** Conservare una memoria essenziale degli eventi significativi, se il sistema già disponibile è abbastanza stabile; altrimenti rinviarla senza bloccare la 1.0.
- [ ] **P2.18** Verificare che personalità, bisogni e relazioni influenzino davvero le scelte, anziché essere soltanto dati visualizzati.

**Nota su `INTIMACY`:** nella 1.0 può essere soddisfatto tramite vicinanza, affetto e connessione sociale. Qualunque interazione sessuale deve essere esclusa per i personaggi minorenni; il consenso non può essere aggirato da comandi forzati.

**Gate P2:** avviando una partita demo e lasciandola avanzare, gli NPC compiono azioni sensate, i bisogni cambiano, le relazioni evolvono e il mondo non richiede input continuo per funzionare.

---

## 5. P3 — Il giocatore può intervenire

- [ ] **P3.1** Selezionare il Sim controllabile e visualizzarne stato, bisogni, umore, relazioni e posizione.
- [ ] **P3.2** Mostrare le location disponibili e consentire di spostarsi fra quelle raggiungibili.
- [ ] **P3.3** Consentire di scegliere un'azione valida e mostrarne esito e costo in tempo/risorse.
- [ ] **P3.4** Mostrare il tempo corrente di Anthalys e un comando di pausa/ripresa.
- [ ] **P3.5** Mostrare un riepilogo delle attività recenti degli NPC, senza richiedere di leggere i log tecnici.
- [ ] **P3.6** Fornire messaggi chiari per azioni non disponibili e spiegare il motivo.
- [ ] **P3.7** Scegliere **una sola interfaccia minima** per la 1.0: CLI/TUI se già adeguata, oppure UI web essenziale se il backend e le route sono già stabili.
- [ ] **P3.8** Mantenere tutta la logica di simulazione nei servizi/core: l'interfaccia invia comandi e visualizza risultati, non implementa regole di dominio.
- [ ] **P3.9** Verificare che la partita sia utilizzabile senza accedere direttamente al DB o modificare file a mano.

**Gate P3:** un utente può giocare una breve sessione completa attraverso l'interfaccia scelta.

---

## 6. P4 — Qualità minima di produzione

### Test e stabilità

- [ ] **P4.1** Aggiungere test automatici per calendario, tick, bisogni, decisioni, relazioni, movimento, seed e salvataggi.
- [ ] **P4.2** Aggiungere test d'integrazione con DB temporaneo e migrazioni.
- [ ] **P4.3** Aggiungere smoke test CLI per inizializzare, avviare, salvare, elencare e ricaricare una partita.
- [ ] **P4.4** Eseguire test con seed fissi per verificare la riproducibilità del percorso principale.
- [ ] **P4.5** Eseguire simulazioni accelerate di 1 anno e 10 anni simulati; correggere blocchi, valori fuori intervallo e accumuli anomali.
- [ ] **P4.6** Eseguire un test di 60 anni come validazione estesa prima del rilascio, se il costo è sostenibile; archiviare il report.
- [ ] **P4.7** Verificare che nessun NPC resti indefinitamente senza bisogni aggiornati o azioni valide.
- [ ] **P4.8** Verificare che non si duplicheranno pagamenti, eventi di vita o altri effetti se un'operazione viene ripetuta dopo un errore.

### Distribuzione e operatività

- [ ] **P4.9** Definire un comando documentato per inizializzare/aggiornare il DB e un comando per avviare SimAI.
- [ ] **P4.10** Rendere la configurazione iniziale utilizzabile con valori predefiniti sicuri ed esempio `.env.example`.
- [ ] **P4.11** Verificare log rotanti, livello di log configurabile e messaggi d'errore utili.
- [ ] **P4.12** Documentare backup e ripristino del DB e dei salvataggi.
- [ ] **P4.13** Preparare `README` con requisiti, installazione, avvio rapido, comandi, salvataggi e problemi noti.
- [ ] **P4.14** Aggiornare versione e changelog per `1.0.0`.
- [ ] **P4.15** Creare un pacchetto/tag di release riproducibile e fare una prova completa da installazione pulita.
- [ ] **P4.16** Pubblicare note di rilascio e lista esplicita delle funzionalità rinviate.

**Gate P4:** la build passa i controlli, si installa in ambiente pulito, la partita demo è completabile e i salvataggi sopravvivono a chiusura e riavvio.

---

## 7. Claire Mode — opzionale, non bloccante

- [ ] **C.1** Definire Claire Mode come guida/assistente opzionale all'esperienza, non come dipendenza del motore.
- [ ] **C.2** Permettere di chiedere spiegazioni sullo stato del mondo e sui personaggi usando dati esposti tramite API/servizi controllati.
- [ ] **C.3** Se non è già stabile, lasciare Claire Mode disattivato nella release base senza impedire il rilascio.
- [ ] **C.4** Non consentire all'eventuale componente LLM di modificare direttamente il DB o saltare le regole di dominio.

---

## 8. Checklist finale di rilascio

- [ ] Installazione pulita completata seguendo il README.
- [ ] Database inizializzato/aggiornato con i comandi documentati.
- [ ] Nuova partita nel Quartiere delle Muse avviata correttamente.
- [ ] 4–6 NPC presenti e autonomi.
- [ ] Almeno 3 location utilizzabili.
- [ ] Tempo giorno/notte funzionante.
- [ ] Bisogni, tratti, umore e relazioni con effetti osservabili.
- [ ] Sim controllabile dal giocatore tramite l'interfaccia scelta.
- [ ] Salvataggio, chiusura, caricamento e ripresa verificati.
- [ ] Test automatici, lint e typecheck superati.
- [ ] Test accelerato e report di bilanciamento archiviati.
- [ ] Backup/restore e gestione errori documentati.
- [ ] Versione `1.0.0`, changelog e note di rilascio preparati.
- [ ] Nessun bug bloccante noto nel percorso principale.

## 9. Ordine di lavoro raccomandato

1. **Audit del codice reale**: riutilizzare ciò che è già buono, non riscrivere per principio.
2. **Percorso verticale minimo**: nuova partita → tick → NPC autonomi → azione del giocatore → salvataggio → ricaricamento.
3. **Comportamento**: bisogni, utility AI, tratti, umore e relazioni.
4. **Interfaccia minima**: rendere osservabile e controllabile il percorso verticale.
5. **Stabilità**: test, simulazioni accelerate, backup, documentazione.
6. **Release candidate**: congelare le funzionalità, risolvere solo difetti e regressioni.
7. **Rilascio 1.0.0**: tag, pacchetto, note e backlog delle funzionalità successive.

### Regola di priorità

Se una funzionalità non è necessaria per il percorso completo **avvia → simula → interagisci → salva → ricarica**, non deve bloccare SimAI 1.0. Non significa eliminarla: significa proteggerne il futuro evitando di rendere infinita la prima release.
