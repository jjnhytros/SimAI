## XXIV. SoNet - Portale Unico dei Servizi al Cittadino di Anthalys `[NUOVA SEZIONE]`

* `[]` a. **Definizione Concettuale e Architettura del Portale SoNet:**
    * `[]` i. SoNet è il portale web/app ufficiale del Governo di Anthalys (`VI.1`) che fornisce un punto di accesso unico e sicuro per i cittadini (`IV`) a una vasta gamma di servizi pubblici e informazioni personali. *(Concetto base definito nel documento myanthalysid_app_def e qui)*
    * `[]` ii. La sezione "Identità" di SoNet sostituisce ed espande le funzionalità precedentemente concettualizzate per "MyAnthalysID app" (vedi `XII.4` aggiornato).
* `[]` b. **Implementazione Tecnica dell'Interfaccia Utente (TUI o futura GUI) per SoNet:**
    * `[]` i. Design di un'interfaccia utente intuitiva, chiara e navigabile per accedere alle diverse sezioni e funzionalità di SoNet.
    * `[]` ii. Assicurare la coerenza visiva e funzionale tra le varie sezioni del portale.
* `[]` c. **Integrazione Funzionalità dei Servizi tramite SoNet:** *(Ogni punto qui richiederà un collegamento al backend del sistema corrispondente)*
    * `[]` i. **Sezione Identità (DID - Documento di Identità Digitale):** (Collegamento principale a `XII`)
        * `[]` 1. Visualizzazione dei dati anagrafici completi del cittadino memorizzati nel DID (`XII.1.a`).
        * `[]` 2. Funzionalità per la gestione del documento DID: richiesta rinnovo (se scade), segnalazione smarrimento/furto, blocco/sblocco temporaneo del certificato digitale (`XII.3.d.ii`).
        * `[]` 3. (Avanzato) Integrazione con servizi finanziari di base: visualizzazione saldo conto corrente principale associato al DID (`XII.5.a`, `XII.5.c.i`), storico transazioni con carta di pagamento integrata (`XII.5.b`), possibilità di trasferimenti P2P sicuri (`XII.5.c.ii`), gestione/riscatto Punti Influenza Civica (PIC) come buoni spesa (`XIII.1.c.ii`, `XXIV.c.vii.3`).
        * `[]` 4. Gestione dei consensi privacy per la condivisione di dati del DID (`XII.7.a`).
        * `[]` 5. Archivio digitale consultabile di licenze (patente di guida `IX.e Driving`, professionali `C.9`) e certificazioni (scolastiche `V.2`, formazione `V.4`) associate al DID (`XII.6.c`).
    * `[]` ii. **Sezione Tasse e Tributi:** (Collegamento a `XXII.3`)
        * `[]` 1. Visualizzazione dello stato fiscale del cittadino: imposte pagate, scadenze future, eventuali crediti/debiti (`XXII.3.c`).
        * `[]` 2. Funzionalità per il pagamento online sicuro delle imposte sul reddito e altre tasse municipali (es. Tassa sui Rifiuti, Tasse sulla Proprietà `XXII.2.b`).
    * `[]` iii. **Sezione Salute:** (Collegamento a `XXII.4`, `XXII.5`)
        * `[]` 1. Accesso a una cartella clinica elettronica riassuntiva e personale (dati rilevanti, allergie, farmaci attuali, vaccinazioni) gestita dal sistema sanitario di Anthalys.
        * `[]` 2. Sistema di prenotazione online per visite mediche presso strutture sanitarie pubbliche ("Istituti Fondine" `XXII.5.b`) o medici di base.
        * `[]` 3. Visualizzazione e gestione appuntamenti sanitari.
    * `[]` iv. **Sezione Istruzione e Formazione:** (Collegamento a `V`)
        * `[]` 1. Visualizzazione dello storico scolastico e universitario del cittadino (diplomi, qualifiche `V.2`, `V.3.h`).
        * `[]` 2. Funzionalità di iscrizione online a corsi di formazione continua, scuole pubbliche, o università statali di Anthalys.
    * `[]` v. **Sezione Partecipazione Civica:** (Collegamento a `VI.2`, `VI.4`)
        * `[]` 1. Registrazione alle liste elettorali e verifica del proprio status di elettore.
        * `[]` 2. Accesso a informazioni ufficiali su elezioni, candidati, programmi, e quesiti referendari.
        * `[]` 3. (Molto Futuro) Piattaforma sicura per il voto elettronico (richiede altissimi livelli di sicurezza `XXIV.f` e verifica identità DID `XII`).
        * `[]` 4. Accesso a consultazioni pubbliche o petizioni online promosse dal governo (`VI.1`).
    * `[]` vi. **Sezione Mobilità e Trasporti:** (Collegamento a futuro sistema trasporti `XIII.3` se dettagliato)
        * `[]` 1. Acquisto e gestione di abbonamenti digitali per i trasporti pubblici di Anthalys (se implementati).
        * `[]` 2. Visualizzazione orari, percorsi e informazioni in tempo reale sul servizio di trasporto pubblico.
        * `[]` 3. Pagamento di eventuali multe o pedaggi legati alla mobilità (se sistema veicoli privati implementato).
    * `[]` vii. **Sezione "La Mia Impronta Civica" (PIC - Punti Influenza Civica):** (Collegamento a `XIII.1`)
        * `[]` 1. Dashboard personale per il monitoraggio dei progressi nella raccolta differenziata (`XIII.1.b.iv.1`).
        * `[]` 2. Visualizzazione del saldo PIC accumulati e storico delle attività che li hanno generati (`XIII.1.b.iv.2`).
        * `[]` 3. Interfaccia per la riscossione di sconti sulla Tassa dei Rifiuti (`XIII.1.c.i`) o la conversione di PIC in buoni spesa (`XIII.1.c.ii`).
        * `[]` 4. Accesso a informazioni personalizzate, promemoria e guide sul corretto smaltimento dei rifiuti e sulla sostenibilità (`XIII.1.b.iv.4`).
    * `[]` viii. **Area Notifiche e Comunicazioni Ufficiali Personali:**
        * `[]` 1. Casella di posta sicura per ricevere comunicazioni ufficiali dal Governo di Anthalys (`VI.1`), scadenze fiscali (`XXII.3.d`), notifiche sanitarie (`XXII.4.c`), avvisi di servizio (es. interruzioni trasporti, allerte meteo `I.3.f`), risultati elettorali (`VI.3.e`).
        * `[]` 2. Storico delle comunicazioni consultabile.
    * `[]` ix. **Sezione Welfare e Supporto Sociale:** `[NUOVA SOTTOCATEGORIA]` (Collegamento a `VIII.3`, `XXII.4`, `XXII.5`)
        * `[]` 1. Consultazione dei propri diritti e delle prestazioni di welfare disponibili.
        * `[]` 2. Presentazione e monitoraggio (semplificato) di richieste per sussidi di disoccupazione (`XXII.4`).
        * `[]` 3. Visualizzazione dello stato dei propri contributi pensionistici e stima della pensione futura (`XXII.4.b`).
        * `[]` 4. Richiesta/gestione indennità di maternità/paternità (`XXII.4.c`).
        * `[]` 5. Informazioni e (eventuale) richiesta per supporti legati a invalidità o malattie a lungo termine (`XXII.4`).
        * `[]` 6. Accesso a programmi di supporto per famiglie a basso reddito (`XXII.4.d`) o per la copertura sanitaria tramite "Istituti Fondine" (`XXII.5`).
    * `[]` x. **Sezione Informazioni Legali e Normative per il Cittadino:** `[NUOVA SOTTOCATEGORIA]` (Collegamento a `XXII`)
        * `[]` 1. Accesso a un compendio semplificato e ricercabile dei diritti e doveri fondamentali del cittadino di Anthalys (`XXII.A`).
        * `[]` 2. Consultazione di normative chiave di interesse pubblico (es. sintesi del Regolamento Alimentare `XXII.8`, normative sul lavoro `XXII.1`, norme sulla privacy e uso del DID `XII.7`).
        * `[]` 3. FAQ e guide interattive su procedure amministrative comuni (es. come registrare un cambio di residenza, come richiedere un certificato).
        * `[]` 4. Contatti utili e link a enti governativi specifici o servizi di supporto al cittadino.
    * `[]` xi. **Sezione Commercio "AION":** (Dove i cittadini acquistano da AION `VIII.6`)
        * `[]` 1. Interfaccia per navigare/ricercare il catalogo prodotti completo di AION (importati e locali `VIII.6.1.b`).
        * `[]` 2. Funzionalità per aggiungere prodotti al carrello e completare ordini.
        * `[]` 3. Pagamento sicuro tramite il sistema finanziario integrato nel DID/SoNet (`XII.5`, `XXIV.c.i.3`).
        * `[]` 4. Gestione delle opzioni di consegna (a domicilio o ritiro presso Punti di Raccolta AION `VIII.6.3.b`).
        * `[]` 5. Accesso e gestione dei Programmi di Fidelizzazione AION (`VIII.6.3.c`).
        * `[]` 6. **Ordini Ricorrenti e Liste della Spesa Automatizzate (Abbonamenti AION):** `[NUOVO PUNTO]`
            * `[]` a. Gli NPC (tramite questa sezione di SoNet) possono impostare ordini ricorrenti (es. settimanali, mensili) per beni di consumo essenziali da AION.
            * `[]` b. Possibilità di creare "liste della spesa intelligenti" che AION può processare automaticamente o con conferma dell'NPC quando le scorte domestiche (`IV.1.j`) sono basse (se l'NPC acconsente alla condivisione di questi dati con l'IA di AION per questo servizio).
            * `[]` c. Sconti o vantaggi per chi aderisce a programmi di consegna regolare/abbonamento.
        * `[]` 7. Funzionalità per inviare feedback e valutazioni su prodotti e servizi AION (`VIII.6.12.a`).
        * `[]` 8. Storico ordini, gestione resi (se implementata), interfaccia per supporto clienti (gestito dall'IA di AION `VIII.6.1.c`).
* `[]` d. **Definizione e Implementazione delle `ActionType` Specifiche per SoNet:**
    * `[]` i. Esempi: `USA_PORTALE_SONET` (apre l'interfaccia), `CONTROLLA_SEZIONE_IDENTITA_SONET`, `PAGA_TASSE_VIA_SONET`, `PRENOTA_VISITA_MEDICA_SONET`, `VERIFICA_SALDO_PIC_SONET`, `RICHIEDI_SUSSIDIO_SONET`.
    * `[]` ii. Queste azioni saranno disponibili per gli NPC (e per il giocatore se gestisce un NPC) e avranno esiti specifici.
* `[]` e. **Logica Comportamentale (IA) per l'Utilizzo di SoNet da parte degli NPC (`IV.4`):**
    * `[]` i. Gli NPC utilizzeranno SoNet in modo autonomo per gestire i propri affari civici, finanziari e personali quando appropriato e necessario.
    * `[]` ii. L'utilizzo di SoNet sarà influenzato da: bisogni (`IV.1`), tratti di personalità (`IV.3.b` - es. `ORGANIZED`, `RESPONSIBLE`, o al contrario `PROCRASTINATOR`, `TECH_SAVVY` vs `TECHNOPHOBE`), scadenze imminenti (tasse, rinnovi), eventi di vita (nascita figlio, cambio lavoro), e livello di "alfabetizzazione digitale" (nuovo possibile attributo NPC o legato a `INTELLIGENCE` `IV.3.d`).
    * `[]` iii. Fallire nell'usare SoNet per compiti importanti (es. pagare tasse) porterà a conseguenze negative (`XXII.3.d`, `XXII.7.n`).
* `[]` f. **Sicurezza del Portale SoNet:**
    * `[]` i. Implementare robusti meccanismi di autenticazione per l'accesso al portale e alle sue sezioni sensibili (es. autenticazione a più fattori (MFA) che coinvolge il DID fisico/digitale `XII.1.c`, riconoscimento biometrico simulato via dispositivo personale).
    * `[]` ii. Crittografia dei dati in transito e a riposo.
    * `[]` iii. Misure contro frodi, phishing e accessi non autorizzati.
* `[]` g. **Accessibilità del Portale SoNet:**
    * `[]` i. Assicurare che il design dell'interfaccia (TUI o futura GUI) segua principi di accessibilità per permettere l'utilizzo da parte di NPC con diverse abilità (se simulate).
* `[]` h. **Sistema di Gestione Feedback e Valutazioni per SoNet e Servizi Governativi:** `[NUOVO PUNTO]`
    * `[]` i. **Canali di Raccolta Feedback Integrati:**
        * `[]` 1. Implementare funzionalità all'interno di ogni sezione di servizio di SoNet (`XXIV.c`) per permettere agli NPC di inviare feedback (es. valutazione a stelle, scelta multipla su aspetti specifici, campo di testo per commenti brevi e astratti).
        * `[]` 2. Possibilità di segnalare problemi tecnici o di usabilità relativi al portale SoNet stesso.
    * `[]` ii. **Processamento e Analisi del Feedback (Astratto):**
        * `[]` 1. Il feedback raccolto viene aggregato e analizzato (astrattamente) dall'ente governativo responsabile della gestione di SoNet e/o dai dipartimenti responsabili dei singoli servizi (`VI.1`).
        * `[]` 2. L'analisi mira a identificare pattern, aree di criticità ricorrenti, o suggerimenti utili.
    * `[]` iii. **Impatto del Feedback sulla Simulazione:**
        * `[]` 1. Feedback negativo consistente su una specifica funzionalità di SoNet potrebbe (nel lungo termine, o tramite eventi `XIV`) portare a un "progetto di aggiornamento SoNet" che ne migliora l'usabilità (`XXIV.b`).
        * `[]` 2. Feedback negativo sulla qualità o efficienza di un servizio pubblico (es. lunghe attese per appuntamenti sanitari `XXIV.c.iii`, difficoltà nell'ottenere sussidi `XXIV.c.ix`) potrebbe contribuire (insieme ad altri fattori come la reportistica governativa `VIII.2.d.vi`) a:
            * Decisioni politiche per aumentare i fondi o riformare quel servizio (`VI.1.ii.2`, `XXII.7.a`).
            * Generare malcontento pubblico se i problemi persistono (`VI.2.f`).
        * `[]` 3. Feedback positivo potrebbe portare a riconoscimenti (astratti) per i dipartimenti governativi efficienti.
    * `[]` iv. **Trasparenza (Opzionale Avanzato):**
        * `[]` 1. Il Governo di Anthalys potrebbe pubblicare periodicamente su SoNet (`XXIV.c.viii` o `XXIV.c.x`) report aggregati sul feedback dei cittadini e sulle azioni di miglioramento intraprese, per aumentare la fiducia e la trasparenza.

---

