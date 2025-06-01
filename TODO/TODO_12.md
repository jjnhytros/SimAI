## XII. DOCUMENTO DI IDENTITÀ DI ANTHALYS E SERVIZI INTEGRATI `[]` *(Revisione completa della sezione)*

* `[!]` a. **Principio Fondamentale:** Il Documento di Identità Digitale (DID) di Anthalys è un mezzo di identificazione avanzato, multifunzionale (personale, amministrativo, finanziario), sicuro e centrale per la vita quotidiana dei cittadini e l'interazione con servizi pubblici e privati. L'accesso e la gestione delle funzionalità digitali del DID da parte del cittadino avvengono primariamente tramite il portale **SoNet (`XXIV`)**. *(Aggiornato con riferimento a SoNet)*
* `[]` b. Ogni NPC (dall'età `CHILD` o `TEENAGER` in su, da definire) possiede un DID univoco emesso dal governo di Anthalys.
* **1. Informazioni Contenute e Caratteristiche Fisiche/Digitali del DID:** `[]`
    * `[]` a. **Dati Personali Standard Registrati:**
        * `[]` i. Nome completo (Nome, Cognome)
        * `[]` ii. Data di nascita
        * `[]` iii. Luogo di nascita
        * `[]` iv. Indirizzo di residenza attuale (collegato a `XVIII.5.j`)
        * `[]` v. Codice Identificativo Personale (CIP) - Vedi `XII.2`.
        * `[]` vi. Foto del titolare.
        * `[]` vii. Data di emissione e data di scadenza.
        * `[]` viii. Cittadinanza di Anthalys (o status di residente).
    * `[]` b. **Caratteristiche di Sicurezza del Documento Fisico (Lore e Design):**
        * `[]` i. Materiale resistente ed ecologico.
        * `[]` ii. Microchip incorporato per memorizzare dati digitali critici e certificati di autenticazione.
        * `[]` iii. Elementi visivi di sicurezza: Ologrammi complessi, design guilloché, e altri elementi anti-contraffazione.
        * `[]` iv. (Lore) "Inchiostro speciale ecologico" visibile solo a dispositivi di verifica autorizzati, per informazioni ultra-riservate sul documento fisico.
        * `[]` v. Codice a barre lineare e Codice QR (`XII.3`) per accesso rapido a diversi livelli di informazione.
        * `[]` vi. Spazio per firma fisica (se ancora in uso) e/o memorizzazione della firma digitale nel chip.
    * `[]` c. **Sicurezza Digitale del DID e dei Dati Associati:**
        * `[]` i. Crittografia avanzata (end-to-end dove possibile) per tutti i dati memorizzati sul chip e trasmessi.
        * `[]` ii. Autenticazione multifattoriale (MFA) per accessi sensibili tramite l'app ufficiale (`XII.4`) o per modifiche ai dati.
        * `[]` iii. Gestione sicura delle chiavi crittografiche da parte dell'autorità emittente.
* **2. Codice Identificativo Personale (CIP):** `[]` *(Dettaglio dell'ID Univoco da XII.1.b precedente)*
    * `[]` a. **Definizione e Unicità:** Il CIP è un numero unico e pseudo-anonimizzato (non direttamente decifrabile senza accesso a database protetti) assegnato a vita a ogni individuo registrato in Anthalys.
    * `[]` b. **Formato Standardizzato:** `123.XXXX.YYYY.Z`
        * `[]` i. `123`: Parte fissa identificativa del sistema DID di Anthalys.
        * `[]` ii. `XXXX` e `YYYY`: Due serie di numeri (es. 4 cifre ciascuna) generate casualmente al momento dell'assegnazione per garantire l'unicità.
        * `[]` iii. `Z`: Lettera di controllo calcolata algoritmicamente sui numeri precedenti per verifica formale di correttezza.
    * `[]` c. **Funzione:** Identificare in modo univoco e sicuro le persone nei database governativi e per l'accesso ai servizi, mantenendo un livello di anonimato nelle transazioni pubbliche di base (dove non è richiesto il nome completo).
* **3. Codice QR sul Documento di Identità: Funzionalità e Accesso ai Dati:** `[]`
    * `[]` a. **Posizionamento e Design del QR Code:**
        * `[]` i. Posizionato sul retro del documento fisico, vicino a una possibile banda magnetica (se presente per retrocompatibilità con vecchi sistemi).
        * `[]` ii. Design standard monocromatico, protetto da usura.
    * `[]` b. **Livelli di Accesso tramite Scansione QR:** *(Meccanica centrale)*
        * `[]` i. **Accesso Base (Pubblico/Non Autorizzato):**
            * `[]` 1. Scansionabile da dispositivi comuni (es. smartphone NPC, chioschi informativi `XVIII.5.h`).
            * `[]` 2. Rilascia solo informazioni pubbliche essenziali: Nome e cognome, Data di nascita, Luogo di nascita (generico), CIP, Data di emissione/scadenza del documento.
            * `[]` 3. Utilizzo: Verifiche d'identità di routine, accesso a edifici pubblici non sensibili, registrazione a servizi non critici, conferma maggiore età per acquisti (`VIII.2.a`).
        * `[]` ii. **Accesso Completo (Autorizzato e Tracciato):**
            * `[]` 1. Scansionabile solo da dispositivi autorizzati e registrati (es. forze dell'ordine `VI.1.iii`, professionisti sanitari `XXII.5`, autorità governative specifiche `VI.1`).
            * `[]` 2. Richiede autenticazione del dispositivo/operatore autorizzato prima di rivelare i dati.
            * `[]` 3. Rilascia informazioni dettagliate e sensibili (memorizzate centralmente e accessibili tramite il CIP come chiave, non tutte nel QR stesso per sicurezza):
                * Dati biometrici (astratti, es. "corrispondenza impronta: sì/no").
                * Indirizzo di residenza attuale e storico.
                * Stato civile e composizione nucleo familiare (collegamento a `IV.2.f`).
                * Professione e datore di lavoro attuale (collegamento a `VIII.1`).
                * Dati medici rilevanti (gruppo sanguigno, allergie note, condizioni mediche critiche pre-autorizzate alla condivisione in emergenza – collegamento a `XXII.5`).
                * (Molto Avanzato/Opzionale) Storico viaggi internazionali (se `C.4` implementato).
                * (Molto Avanzato/Opzionale) Storico accessi a servizi governativi critici.
                * (Molto Avanzato/Opzionale) Informazioni bancarie e transazioni recenti (solo con consenso esplicito o mandato legale – vedi `XII.5`).
            * `[]` 4. Utilizzo: Situazioni che richiedono verifica approfondita, emergenze sanitarie, operazioni di sicurezza, indagini legali (con dovuti mandati `VI.1.iii.2`).
    * `[]` c. **Sicurezza e Privacy del Sistema QR Code:**
        * `[]` i. Il QR code stesso (o i dati a cui punta) utilizza protocolli di crittografia. Le chiavi di decrittazione per l'accesso completo sono gestite centralmente e distribuite solo a dispositivi/enti autorizzati.
        * `[]` ii. In caso di smarrimento/furto del DID fisico, il certificato digitale associato può essere disabilitato remotamente tramite **SoNet (`XXIV.c.i.2`)** o da un ufficio governativo. *(Aggiornato con riferimento a SoNet)*
    * `[]` d. **Gestione e Aggiornamento delle Informazioni Legate al QR Code:**
        * `[]` i. Le informazioni a cui punta il QR (specialmente quelle complete) sono aggiornate in tempo reale tramite il sistema centrale governativo. Il QR stesso potrebbe contenere solo il CIP e un token di sessione/puntatore sicuro.
        * `[]` ii. In caso di smarrimento/furto del DID fisico, il certificato digitale associato al QR (o al chip) può essere disabilitato remotamente dall'app ufficiale (`XII.4`) o da un ufficio governativo, rendendo il QR inservibile o limitato al solo Accesso Base non sensibile.
* **4. Gestione Digitale del DID e Accesso ai Servizi da parte del Cittadino tramite SoNet:**
    * `[!]` a. Il portale **SoNet (`XXIV`)** è l'interfaccia primaria fornita dal Governo di Anthalys (`VI.1`) attraverso cui i cittadini accedono alle informazioni del proprio DID, gestiscono aspetti del proprio documento e interagiscono con i servizi civici, finanziari e amministrativi associati.
    * `[]` b. Le funzionalità specifiche di visualizzazione dati DID, gestione documento, servizi finanziari, consensi privacy, archivio licenze, e altre interazioni sono dettagliate nella **Sezione XXIV.c.i (Sezione Identità di SoNet)** e nelle altre sezioni pertinenti di SoNet.
* **5. Carta di Pagamento Integrata nel DID:** `[]`
    * `[]` a. **Funzionalità di Pagamento Universale:**
        * `[]` i. Il DID funge da principale strumento di pagamento (contactless e online), collegato ai conti bancari dell'NPC (sistema bancario da dettagliare in `VIII.2`). Sostituisce o affianca carte di credito/debito tradizionali.
        * `[]` ii. Chip NFC (o tecnologia equivalente) per pagamenti contactless presso punti vendita fisici (`XVIII.5.h`).
        * `[]` iii. La gestione dei conti associati, visualizzazione saldo, cronologia transazioni, trasferimenti fondi e limiti di spesa avviene tramite la sezione Identità/Finanziaria del portale **SoNet (`XXIV.c.i.3`, `XII.5.c`)**. *(Aggiornato con riferimento a SoNet)*
    * `[]` b. **Programma a Punti per Pagamenti Civici:**
        * `[]` i. Accumulo punti fedeltà utilizzando il DID per pagamenti di servizi pubblici (es. trasporti `XIII.3` se con tariffe, bollette astratte, tasse `VIII.2`).
        * `[]` ii. I punti possono dare diritto a sconti su futuri servizi, accesso prioritario, o altri piccoli benefici civici.
    * `[]` c. **Gestione Fondi e Conti tramite App "MyAnthalysID":**
        * `[]` i. Visualizzazione saldo e movimenti dei conti bancari associati.
        * `[]` ii. Funzionalità di trasferimento fondi tra NPC (P2P).
        * `[]` iii. Impostazione limiti di spesa e notifiche di transazione.
    * `[]` d. **Sicurezza Avanzata dei Pagamenti:**
        * `[]` i. Ogni transazione (sopra una certa soglia o per acquisti online) richiede autenticazione biometrica (impronta/facciale tramite dispositivo personale) o PIN sicuro.
        * `[]` ii. Blocco immediato delle funzioni di pagamento tramite **SoNet (`XXIV.c.i.2`, `XXIV.c.i.3`)** in caso di smarrimento/furto.
        * `[]` iii. (Lore) PIN di emergenza che, se usato, blocca tutte le funzionalità del DID e allerta le autorità (in situazioni di coercizione).
* **6. Altre Integrazioni e Funzionalità del DID:** `[]`
    * `[]` a. **Punti di Raccolta Rifiuti Intelligenti:** (Collegamento a `XIII.1.b` e `XIII.4.c`)
        * `[]` i. Utilizzo del DID per identificarsi. *(Tracciamento e visualizzazione incentivi/PIC tramite SoNet `XXIV.c.vii`)*. *(Aggiunto riferimento a SoNet)*
        * `[]` ii. Sistema per tracciare il conferimento responsabile e accumulare punti/incentivi (PIC `XIII.1`) o ricevere feedback sulla qualità della differenziazione.
    * `[]` b. **Accesso a Servizi Governativi e Civici Specifici:** *(Rafforzamento di XII.2 precedente)*
        * `[]` i. Accesso a biblioteche pubbliche/universitarie (`V.2.h.iii`).
        * `[]` ii. Accesso a trasporti pubblici (abbonamenti, tariffe agevolate - `XIII.3` se implementato).
        * `[]` iii. (Avanzato) Votazioni elettroniche sicure (`VI.2.a.i`, `VI.4`).
    * `[]` c. **Licenze e Certificazioni Digitali:**
        * `[]` i. Il DID contiene o è collegato a versioni digitali di licenze e certificazioni, consultabili e gestibili (astrattamente) tramite la sezione Identità di **SoNet (`XXIV.c.i.5`)**. *(Aggiornato con riferimento a SoNet)*
    * `[]` d. **(Opzionale) Funzione "Chiave Universale" (Avanzato e Contestualizzato):**
        * `[]` i. Per alcuni NPC e in contesti specifici, il DID potrebbe (con autorizzazioni) funzionare come chiave di accesso per la propria abitazione (`XVIII.5.j`), veicolo, o posto di lavoro.
* **7. Gestione della Privacy, Sicurezza dei Dati e Aspetti Etici (Revisione di XII.3 precedente):** `[]`
    * `[]` a. Definire politiche e meccanismi tecnici robusti per la protezione dei dati personali degli NPC, in linea con la Costituzione di Anthalys (`XXII.A`). Crittografia forte, accesso limitato e tracciato (`XII.3.c.ii`).
    * `[]` b. L'IA di SoNet (`VIII.6`) e altri sistemi che interagiscono con il DID devono rispettare rigorosi protocolli di privacy per i dati dei cittadini.
    * `[]` c. (Eventi) Possibilità di dibattiti pubblici o preoccupazioni NPC riguardanti la privacy e la sorveglianza legati all'uso estensivo del DID, che potrebbero influenzare politiche governative (`VI`, `XXII`).
    * `[]` d. (Eventi Rari) Incidenti di sicurezza informatica (tentati o riusciti su piccola scala, non catastrofici) che mettono alla prova il sistema e generano conseguenze (es. indagini, aggiornamenti di sicurezza, perdita di fiducia temporanea da parte degli NPC).
* **8. Visualizzazione Astratta del DID e Interazioni nella TUI (Revisione di XII.4 precedente):** `[]`
    * `[!]` a. L'interfaccia principale per il cittadino per interagire con i dati e le funzionalità del proprio DID è il portale **SoNet (`XXIV`)**. La "scheda DID semplificata" menzionata precedentemente è ora una vista all'interno della sezione Identità di SoNet. *(Aggiornato)*
    * `[]` b. Nelle interazioni tra NPC, la "presentazione del DID" o la "scansione del QR" saranno azioni astratte con esiti dipendenti dal contesto e dal livello di accesso.
    * `[]` c. Notifiche al giocatore/NPC riguardanti aggiornamenti del DID, avvisi di sicurezza, o scadenze.

---

