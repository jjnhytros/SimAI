## XIII. GESTIONE AMBIENTALE E CIVICA DI ANTHALYS `[]`

* `[]` **1. Sistema di "Punti Influenza Civica" (PIC) e Incentivi per la Sostenibilità:** *(Ampliato per includere il sistema di bonus per la raccolta differenziata)*
    * `[]` a. Gli NPC (e potenzialmente il giocatore) accumulano Punti Influenza Civica (PIC) compiendo azioni positive per la comunità o l'ambiente, **con un focus primario sulla corretta raccolta differenziata dei rifiuti** (vedi `XIII.2.b.i`), ma anche attraverso volontariato (`XIII.4`), e altre iniziative civiche. *(Aggiornato per priorità alla raccolta differenziata)*
    * `[]` b. **Meccanismo di Punti (PIC) per la Differenziazione Corretta dei Rifiuti:** *(Integrazione nuovi dettagli utente)*
        * `[]` i. La corretta differenziazione e conferimento dei rifiuti (dettagliati in `XIII.2.b.i`) viene tracciata (es. tramite DID `XII.6.a` ai punti di raccolta o registrazione da smaltitori domestici `XIII.6`) e premiata con PIC.
        * `[]` ii. **Assegnazione Punti Esempio (da bilanciare):**
            * Organico: 1 PIC per kg (o unità astratta equivalente).
            * Carta e Cartone: 1 PIC per kg.
            * Plastica (Bio-based): 2 PIC per kg.
            * Vetro: 1 PIC per kg.
            * Metalli: 3 PIC per kg.
            * Rifiuti Elettronici (RAEE): 5 PIC per pezzo/unità.
            * Rifiuti Speciali (Naturali): 3 PIC per pezzo/unità.
    * `[]` c. **Utilizzo e Benefici dei PIC Accumulati:** *(Estensione di XIII.1.b precedente)*
        * `[]` i. **Sconti sulla Tassa dei Rifiuti:** (Richiede definizione della "Tassa dei Rifiuti" in `VIII.2`).
            * 500 PIC: 5% di sconto.
            * 1000 PIC: 10% di sconto.
            * 2000 PIC: 20% di sconto.
        * `[]` ii. **Buoni Spesa Convertibili:**
            * 100 PIC: Buono spesa da 10 Athel (Ꜳ).
            * 200 PIC: Buono spesa da 25 Ꜳ.
            * 500 PIC: Buono spesa da 70 Ꜳ.
            * (Meccanismo di conversione e spendibilità presso negozi convenzionati `XVIII.5.h` o **AION** `VIII.6`).
        * `[]` iii. **Premi e Riconoscimenti Pubblici:**
            * (Eventi `XIV` o status NPC) Premio annuale "Cittadino Sostenibile dell'Anno".
            * Ricezione di gadget ecologici (oggetti unici: borracce, sacchetti riutilizzabili brandizzati Anthalys).
        * `[]` iv. (Avanzato) I PIC possono essere spesi per influenzare politiche locali minori (collegamento a `XIII.4` Leggi e Ordinanze Locali), o per supportare/proporre progetti comunitari astratti.
    * `[]` d. **Applicazione Mobile "MyAnthalysID" (`XII.4`) per Gestione PIC e Sostenibilità:**
        * `[]` i. Sezione dedicata nell'app per monitorare i progressi nella raccolta differenziata e altre attività civiche.
        * `[]` ii. Visualizzazione PIC accumulati, storico conferimenti/attività.
        * `[]` iii. Interfaccia per riscattare sconti, convertire PIC in buoni, o "spendere" PIC per iniziative.
        * `[]` iv. Notifiche sui giorni di raccolta municipale (`XIII.3.a.ii`), informazioni su corretto smaltimento.
        * `[]` v. Statistiche personalizzate sull'impatto ambientale positivo.
    * `[]` e. (Avanzato) Un "Consiglio Cittadino" astratto (o meccanismo di `AnthalysGovernment` `VI.1`) valuta le proposte basate sui PIC.
* `[]` **2. Ambiente e Impatto Ecologico:**
    * `[]` a. **Livello di Inquinamento Astratto (per quartiere/città):**
        * `[]` i. Influenzato da fattori come densità industriale (`VIII.1.k`), traffico (futuro), pratiche di gestione rifiuti (`XIII.1.b`, `XIII.3.a`), consumo energetico (`XIII.1.e` - ex XIII.2.b.iv), e politiche ambientali (`XIII.2.c`).
        * `[]` ii. L'inquinamento elevato può avere impatti negativi sull'umore, sulla salute NPC (`IV.1.g`), sull'attrattiva del quartiere, sulla qualità del raccolto (`X.6`), e sulla biodiversità locale.
        * `[]` iii. **Estensione "Total Realism" - Impatti Ecologici Profondi e a Lungo Termine:**
            * `[]` 1. Degradazione qualità ambiente: riduzione fertilità suolo, contaminazione acqua, riduzione biodiversità.
            * `[]` 2. Eventi meteorologici (`I.3.f`) estremi esacerbati da degrado ambientale.
    * `[]` b. **Azioni Ecologiche e Gestione Differenziata dei Rifiuti da parte degli NPC:**
        * `[]` i. **Tipologie di Rifiuti Differenziabili e Contenitori Domestici:** *(Integrazione nuovi dettagli utente)*
            * `[]` 1. **Organico:** Contenitore Marrone. Azione NPC: `SMALTISCI_RIFIUTI_ORGANICI`.
            * `[]` 2. **Carta e Cartone:** Contenitore Blu. Azione NPC: `SMALTISCI_CARTA_CARTONE`.
            * `[]` 3. **Plastica (Bio-based):** Contenitore Giallo. Azione NPC: `SMALTISCI_PLASTICA_BIO`.
            * `[]` 4. **Vetro:** Contenitore Verde. Azione NPC: `SMALTISCI_VETRO`.
            * `[]` 5. **Metalli:** Contenitore Grigio. Azione NPC: `SMALTISCI_METALLI`.
            * `[]` 6. **Rifiuti Elettronici (RAEE):** Contenitore Rosso. Azione NPC: `SMALTISCI_RAEE`.
            * `[]` 7. **Rifiuti Speciali (Naturali):** Contenitore Nero. Azione NPC: `SMALTISCI_RIFIUTI_SPECIALI_NAT`.
            * `[]` 8. Ogni lotto residenziale (`XVIII.5.j`) deve avere il set di contenitori. L'azione generica `RECYCLE_WASTE` viene sostituita da queste azioni specifiche, che richiedono all'NPC di interagire con il contenitore corretto. Il successo (e i PIC) dipendono dalla corretta associazione rifiuto-contenitore.
            * `[]` 9. L'IA degli NPC (`IV.4`) gestisce la frequenza e la correttezza della differenziazione (influenzata da tratti, educazione, incentivi `XIII.1.c`).
        * `[]` ii. **Compostaggio Domestico:** Azione `USE_DOMESTIC_COMPOSTER` (`XIII.6.a.1`) per i rifiuti organici, che produce compost (`X.6`) e dà PIC bonus (`XIII.6.b.1`).
        * `[]` iii. (Futuro) Scelte di trasporto ecologiche.
        * `[]` iv. (Futuro) Risparmio energetico in casa.
    * `[]` c. **Politiche Ambientali (Simulate dal Governo - `VI.1`, `XXII`):**
        * `[]` i. Leggi su emissioni, standard per la gestione dei rifiuti (che definiscono i tipi di raccolta differenziata `XIII.2.b.i`), incentivi per energie rinnovabili, tasse ecologiche.
        * `[]` ii. Impatto misurabile sull'inquinamento (`XIII.2.a`), economia (`VIII`), e comportamento NPC.
    * `[]` d. **Estensione "Total Realism" - Ecosistema Locale Dinamico (Flora):**
        * `[]` i. Simulazione semplificata dei cicli di vita per la flora locale negli spazi verdi (`XIII.3.b`) e nelle aree naturali (se presenti): piante crescono, fioriscono, producono semi (che possono diffondersi limitatamente), e muoiono, influenzate da stagioni (`I.3.f`), meteo, qualità del suolo (`XIII.2.a.iii.1`), e cure/disturbi umani.
        * `[]` ii. Diverse specie di piante (con requisiti ambientali diversi) contribuiscono alla biodiversità e all'estetica del luogo (`XVIII.5.i.iii`).
        * `[]` iii. Collegamento con la fauna (`XXIII`): specifiche piante possono attrarre o essere necessarie per la sopravvivenza di specifici animali selvatici.
* `[]` **3. Servizi Municipali e Infrastrutture:**
    * `[]` a. **Gestione e Trattamento dei Rifiuti a Livello Municipale:**
        * `[]` i. NPC e attività economiche producono i vari tipi di rifiuti differenziati (`XIII.2.b.i`).
        * `[]` ii. (Futuro) Sistema di raccolta rifiuti municipale (NPC netturbini, camion, calendari di raccolta per tipo di rifiuto) che preleva i rifiuti dai contenitori domestici/condominiali o dai punti di raccolta intelligenti (`XII.6.a`).
        * `[]` iii. **Trattamento e Riutilizzo Post-Raccolta (Lore e Impatti Indiretti):** *(Integrazione nuovi dettagli utente)*
            * `[]` 1. **Organico:** Compostaggio municipale (produzione compost su larga scala), Digestione Anaerobica (produzione biogas per energia `XIII.1.e`, fertilizzanti naturali).
            * `[]` 2. **Carta e Cartone:** Riciclo per nuova carta/cartone.
            * `[]` 3. **Plastica (Bio-based):** Riciclo per nuovi prodotti in bioplastica (imballaggi, tessuti).
            * `[]` 4. **Vetro:** Riciclo per nuovi prodotti in vetro.
            * `[]` 5. **Metalli:** Riciclo per nuovi prodotti metallici.
            * `[]` 6. **Rifiuti Elettronici (RAEE):** Impianti specializzati per recupero componenti e materiali preziosi.
            * `[]` 7. **Rifiuti Speciali (Naturali):** Trattamento specifico sicuro e riciclo/smaltimento eco-compatibile.
    * `[]` b. **Manutenzione Spazi Pubblici:**
        * `[]` i. Parchi (`XVIII.5.h`), strade, piazze necessitano di manutenzione (pulizia, riparazioni, cura del verde – svolta da NPC con carriere municipali `VIII.1.j` o volontari `XIII.4`).
        * `[]` ii. Se trascurati, questi spazi diventano meno attraenti (impatto su `aesthetic_score` di `Location` `XVIII.5.i.iii`), possono ridurre l'umore degli NPC, limitare le attività possibili, e persino diventare pericolosi (es. buche stradali – eventi `XIV`).
    * `[]` c. **Servizi di Emergenza (oltre a quelli sanitari `XXII.4`):**
        * `[]` i. Pompieri (`FIREFIGHTER` carriera in VIII): Rispondono a incendi (eventi rari `XIV`, con cause varie: incidenti domestici `XVIII.2`, elettrici, dolosi). Efficacia dipende da equipaggiamento e skill.
        * `[]` ii. Forze dell'Ordine (Carriera `POLICE_OFFICER` in VIII): Mantengono l'ordine pubblico, pattugliano, rispondono a crimini (se sistema criminale implementato), gestiscono il traffico (futuro). (Collegamento a sistema legale `VI.1.iii.2`).
* `[]` **4. Partecipazione Civica e Volontariato:**
    * `[]` a. NPC compiono azioni di volontariato (influenzati da tratti, ecc.).
    * `[]` b. Azioni: `VOLUNTEER_AT_SOUP_KITCHEN`, `CLEAN_UP_PARK`, `HELP_ELDERLY_NEIGHBOR`, `TUTOR_STRUGGLING_STUDENT`.
    * `[]` c. Il volontariato aumenta i PIC (`XIII.1.a`), migliora l'umore, rafforza relazioni, e ha impatti positivi visibili.
    * `[]` d. (Futuro) Organizzazioni di volontariato o ONG.
* `[]` **5. Eventi Comunitari e Festival (Oltre alle Festività Nazionali `I.3.e`):**
    * `[]` a. Eventi locali ricorrenti o una tantum: mercati contadini settimanali (NPC vendono prodotti da giardinaggio `X.6` o artigianato `X.4`), fiere di quartiere (con giochi, cibo, musica), piccole celebrazioni culturali specifiche di Anthalys, raccolte fondi comunitarie.
    * `[]` b. NPC partecipano attivamente: allestiscono bancarelle, si esibiscono (skill musicali/artistiche `IX.e`), socializzano (`VII`), comprano/vendono beni (`VIII`).
    * `[]` c. Questi eventi rafforzano il senso di comunità (`capital_sociale` per il quartiere), offrono opportunità di divertimento (`FUN` `IV.1.e`), e possono stimolare l'economia locale.
* `[]` **6. Smaltitori Automatici Domestici per Rifiuti:** `[NUOVA SOTTOCATEGORIA]` *(Integrazione nuovi dettagli utente)*
    * `[]` a. **Funzionamento e Tipologie:** (Nuovi oggetti `XVIII.1`)
        * `[]` i. **Compostatori Domestici Avanzati:** Per il trattamento dei rifiuti organici (`XIII.2.b.i.1`). Producono compost utilizzabile per giardini/orti domestici (`X.6`). Azione: `UTILIZZA_COMPOSTATORE_DOMESTICO`.
        * `[]` ii. **Mini-Riciclatori Domestici (Plastica Bio / Vetro):** Per il trattamento della plastica bio (`XIII.2.b.i.3`) e del vetro (`XIII.2.b.i.4`). Frantumano e compattano i materiali, o (avanzato) li trasformano in granuli/materiali base riutilizzabili per crafting semplice (`X.4`). Azione: `UTILIZZA_MINI_RICICLATORE`.
        * `[]` iii. **Smaltitori/Compattatori Domestici di Metalli:** Per il trattamento dei rifiuti metallici (`XIII.2.b.i.5`). Frantumano/compattano per facilitare il riciclo. Azione: `UTILIZZA_SMALTITORE_METALLI`.
    * `[]` b. **Incentivi per l'Acquisto e l'Uso:**
        * `[]` i. Sconto governativo (es. 20%) sull'acquisto di smaltitori automatici per le famiglie (impatto su finanze NPC `VIII.2`).
        * `[]` ii. Bonus PIC extra (es. 10 PIC/mese) per l'utilizzo continuativo e corretto degli smaltitori (tracciato via DID/App `XII.6.a`, `XIII.1.d`).
        * `[]` iii. Programma di noleggio a tariffe agevolate.
    * `[]` c. **Benefici Simulati:**
        * `[]` i. Riduzione significativa della quantità di rifiuti che la famiglia deve conferire ai punti di raccolta municipali.
        * `[]` ii. Maggiore efficienza nel riciclaggio domestico e potenziale per bonus PIC più alti.
        * `[]` iii. Maggiore comodità e autonomia nella gestione dei rifiuti per gli NPC.
        * `[]` iv. Generazione diretta di risorse (compost, forse materiali riciclati base) per l'NPC.

---

