## XXII. SISTEMA REGOLAMENTARE GLOBALE E GOVERNANCE DI ANTHALYS `[]` *(Concetti base e parametri definiti, implementazione in corso)*

* `[]` **A. Principi Fondamentali (basati sulla Costituzione):** `[NUOVO SOTTO-BLOCCO]`
    * `[!]` i. Le normative devono promuovere la dignità umana, la libertà, la giustizia e la solidarietà. *(Art. 1 Costituzione)*.
    * `[!]` ii. Le normative devono garantire i diritti fondamentali: vita, libertà, sicurezza, proprietà privata (con eccezioni legali), istruzione, assistenza sanitaria, partecipazione civica. *(Art. 8, 9, 10 Costituzione)*.
    * `[!]` iii. Le normative economiche devono promuovere un'economia equa, sostenibile e orientata al benessere, combattendo povertà e ingiustizia sociale. *(Art. 11, 12 Costituzione)*.
* **1. Normativa sull'Orario di Lavoro:** `[]` *(Parametri definiti, implementazione in `TimeManager` e logica NPC da completare)* (Include vecchio `VIII.4 Normativa sull'Orario di Lavoro`)
    * `[]` a. Definire e implementare Giornata Lavorativa Standard di 9 ore effettive. *(Costante `STANDARD_WORK_HOURS_PER_DAY` definita).*.
    * `[]` b. Implementare Settimana Lavorativa di 5 giorni su 7. *(Costante `WORK_DAYS_PER_WEEK` definita, logica in `TimeManager.is_work_day()` concettualizzata).*.
    * `[]` c. Implementare Anno Lavorativo Standard: *(Parametri definiti)*.
        * `[]` i. 15 mesi di attività produttiva.
        * `[]` ii. 3 mesi di interruzione totali, ripartiti in tre periodi di pausa annuali da 1 mese ciascuno.
        * `[]` iii. Calcolo e tracciamento dei ~300 giorni lavorativi/anno (`WORK_DAYS_PER_YEAR_EFFECTIVE`) e ~2.700 ore lavorative/anno (`STANDARD_ANNUAL_WORK_HOURS`). *(Costanti definite, ma il calcolo preciso di `WORK_DAYS_PER_YEAR_EFFECTIVE` basato su 5/7 e mesi di pausa è da verificare/implementare in `TimeManager` o `careers_config`)*.
    * `[]` d. Implementare Regolamentazione del Lavoro Minorile e Part-time per studenti Medie Superiori (età 13-15 anni):
        * `[]` i. Limite massimo 5.25 ore/giorno. *(Costante definita)*.
        * `[]` ii. Monte ore annuo tra 50% (1.350 ore) e 66.6% (1.800 ore) dell'orario standard. *(Percentuali definite, calcolo da implementare)*.
        * `[]` iii. Contributo ore part-time per anzianità di servizio e pensione (logica di tracciamento e calcolo).
        * `[]` iv. Logica per NPC adolescenti per cercare/ottenere/mantenere lavori part-time (interazione con VIII.1 e V.3).
    * `[]` e. Integrare le festività (fisse e mobili) come giorni non lavorativi nel calcolo dell'anno lavorativo e nella disponibilità degli NPC al lavoro. *(Collegamento a I.3.e e I.3.h, ora XXXII.5)*
* **2. Politiche Retributive:** `[]` *(Parametri e scale definite, logica di applicazione da implementare)*
    * `[]` a. Definire tipologie di impiego (Base, Specializzati, Alta Qualificazione, Dirigenziali) e relative Scale Retributive Annuali Medie (in **Ꜳ**) in `careers_config.py` (o `settings.py`). *(Struttura `GENERAL_SALARY_RANGES_ANNUAL` definita concettualmente)*.
    * `[]` b. Implementare Progressione Stipendiale per Anzianità di Servizio: *(Regole definite, implementazione calcolo e applicazione da fare)*.
        * `[]` i. Riconoscimento scatto di anzianità ogni 2 anni di servizio effettivi (`YEARS_OF_SERVICE_FOR_SENIORITY_BONUS`).
        * `[]` ii. Primo scatto: +1.0% (`FIRST_SENIORITY_BONUS_PERCENTAGE`).
        * `[]` iii. Scatti successivi: +(0.1 x Numero Ordinale Scatto)% (`SUBSEQUENT_SENIORITY_BONUS_FACTOR`).
        * `[]` iv. Limite massimo di aumento per singolo scatto: 2.5% (`MAX_SENIORITY_BONUS_PERCENTAGE_PER_STEP`).
        * `[]` v. Attributi in `Character` e `BackgroundNPCState` per tracciare `years_of_service`, `base_salary_for_current_level`, `num_seniority_bonuses_received`.
        * `[]` vi. Logica per applicare gli aumenti all'`annual_salary` (negli aggiornamenti annuali NPC).
    * `[]` c. Calcolo retribuzione mensile (stipendio annuale / 18 mesi). *(Formula definita, da usare quando si pagano gli stipendi)*.

* **3. Regolamentazione Fiscale (basata sul Contributo al Sostentamento Civico - CSC):** `[]` `[TITOLO E STRUTTURA RIVISTI]`
    * `[!]` a. Il sistema fiscale di Anthalys si fonda sul principio del **Contributo al Sostentamento Civico (CSC)**, diversificato in componenti basate sulla capacità contributiva e sulle attività economiche. (Vedi `VIII.2` per i dettagli economici di ciascuna componente).
    * `[]` b. **Regolamentazione della CSC-R (Componente sul Reddito Personale):** `[NOME STANDARDIZZATO]`
        * `[]` i. Normativa che definisce il sistema di imposte progressive sul reddito annuo individuale. (La tabella dettagliata di scaglioni e aliquote è specificata in `VIII.2.b.ii`).
        * `[]` ii. Conferma normativa dell'esenzione fiscale per redditi annui inferiori a 3.000 **Ꜳ** (`TAX_EXEMPTION_INCOME_THRESHOLD`).
        * `[]` iii. Norme per il calcolo dell'imponibile e delle deduzioni/detrazioni ammissibili per la CSC-R.
    * `[]` c. **Procedure di Dichiarazione e Riscossione del CSC:**
        * `[]` i. Normativa che stabilisce la periodicità (es. ogni 9 mesi o annuale) e le modalità di dichiarazione e versamento delle varie componenti del CSC (CSC-R, CSC-A, ecc.).
        * `[]` ii. Utilizzo del portale **SoNet (`XXIV.c.ii`)** come canale ufficiale per le dichiarazioni e i pagamenti da parte dei cittadini e delle imprese.
    * `[]` d. **Confluenza dei Tributi del CSC nella Tesoreria Statale:**
        * `[]` i. Le entrate derivanti da tutte le componenti del CSC sono versate all'`AnthalysGovernment.treasury` (`VIII.2.d`) per finanziare la spesa pubblica.
    * `[]` e. **Quadro Normativo delle Altre Componenti del CSC:** *(Questa sezione stabilisce il quadro normativo generale; i dettagli economici e le aliquote sono in VIII.2)*
        * `[]` i. **CSC-A (Componente sugli Utili d'Impresa):** Regolamentazione sulla determinazione del reddito d'impresa imponibile, principi per le aliquote (`VIII.2.e.ii`), e criteri normativi per le agevolazioni fiscali (`VIII.2.e.iii`).
        * `[]` ii. **CSC-S (Componente sulle Vincite da Gioco):** Quadro normativo per la tassazione delle vincite, definizione della base imponibile, principi per le aliquote progressive (`VIII.2.f.ii`), e normative sulle esenzioni (`VIII.2.f.iii`).
        * `[]` iii. **CSC-P (Componente sul Patrimonio Immobiliare):** Normativa che definisce i criteri per la valutazione degli immobili ai fini fiscali (`VIII.2.g.ii`) e i principi per la determinazione delle aliquote (`VIII.2.g.iii`).
        * `[]` iv. **CSC-C (Componente sul Consumo):** Normativa che definisce l'applicazione dell'aliquota standard (12% - `VIII.2.h.ii`) e i criteri per l'identificazione di beni/servizi soggetti ad aliquote ridotte o esenzioni (`VIII.2.h.iii`).
    * `[]` f. **Contrasto all'Evasione ed Elusione Fiscale:**
        * `[]` i. Normative e meccanismi di controllo per prevenire e sanzionare l'evasione e l'elusione delle varie componenti del CSC. (Collegamento a `XXVII` se implementato).

* **4. Benefici e Sicurezza Sociale (Erogati o Gestiti tramite il Governo):** `[]` `[SEZIONE AMPLIATA]`
    * `[]` a. **Assicurazione Sanitaria Lavoratori e Copertura Universale:**
        * `[]` i. Implementare un sistema di copertura sanitaria universale per tutti i cittadini di Anthalys, finanziato tramite contribuzioni (`VIII.3.a`) e fiscalità generale (`VIII.2.d`).
        * `[]` ii. Calcolo contribuzione specifica per lavoratori: (Ore Lavorate nel Mese / `HEALTH_INSURANCE_CONTRIBUTION_HOURS_DIVISOR`)% dello stipendio netto mensile.
        * `[]` iii. Esenzione contribuzione per lavoratori < 16 anni (`HEALTH_INSURANCE_MINOR_AGE_EXEMPTION`); copertura garantita dallo stato.
        * `[]` iv. Logica per dedurre la contribuzione da `Character.money` / `BackgroundNPCState.money`.
    * `[]` b. **Pensioni:**
        * `[]` i. Tracciare anni di servizio effettivi (`years_of_service`) e monte ore lavorativo.
        * `[]` ii. Calcolare stipendio medio pensionabile (basato sullo stipendio medio mensile durante la vita lavorativa e aggiornato all'inflazione).
        * `[]` iii. **Pensione di Base:** Accesso dopo 20 anni di lavoro effettivo (o equivalente in ore), garantisce il 50% dello stipendio medio pensionabile.
        * `[]` iv. **Pensione Massima:** Raggiungibile quando la somma dell'età del cittadino e degli anni di servizio è >= 96 (o dopo un numero elevato di anni di servizio, es. 35-40, da definire quale criterio prevale o se coesistono), garantisce fino al 100% dello stipendio medio pensionabile. *(Nota: "35/50 anni" dagli appunti vecchi è un riferimento, il sistema attuale `[]` usa somma età+servizio. Manteniamo il sistema attuale più dettagliato, ma il concetto di "molti anni di servizio" è valido).*
        * `[]` v. Adeguamento Annuale Pensione (+1.0% sulla media progressiva, dal secondo anno dopo il pensionamento).
        * `[]` vi. Le pensioni sono tassate con un'aliquota fissa del 1.5% (Componente CSC-R specifica per pensioni).
        * `[]` vii. Gestire transizione allo stato di "pensionato" e inizio erogazione pensione.
    * `[]` c. **Indennità di Maternità/Paternità:** Definire durata, importo (% dello stipendio), e condizioni di accesso (es. mesi minimi di contribuzione).
    * `[]` d. **Norme su Sicurezza sul Lavoro e Indennizzi:** Meccanismi di prevenzione infortuni e malattie professionali, e sistema di indennizzo/supporto in caso di accadimento.
    * `[]` e. **Assistenza Sanitaria e Supporto Specifico per Disabilità e Malattie Croniche:** `[NUOVO PUNTO]`
        * `[]` i. Programmi speciali e dedicati per garantire l'accesso a cure continuative, terapie riabilitative (`XXIII.b.ii`), ausili tecnici, e supporto psicologico (`IV.1.i`) per cittadini con disabilità (fisiche o mentali) o affetti da malattie croniche invalidanti.
        * `[]` ii. Questi programmi integrano e vanno oltre la copertura sanitaria di base (`XXII.5`), potendo includere assistenza domiciliare o supporto per i caregiver.
    * `[]` f. **Sussidi per Famiglie a Basso Reddito con Figli:** `[NUOVO PUNTO]`
        * `[]` i. Definire criteri di idoneità (basati su reddito familiare, numero di figli).
        * `[]` ii. Erogazione di un sussidio economico periodico (in **Ꜳ**) per supportare le spese di crescita ed educazione dei minori.
    * `[]` g. **Assistenza per Genitori Single:** `[NUOVO PUNTO]`
        * `[]` i. Programmi specifici di supporto economico, consulenza e servizi (es. accesso prioritario ad asili nido `V.2.a`) per madri e padri single, specialmente se a basso reddito.
    * `[]` h. **Supporto per Genitori con Disabilità o Malattie Degenerative:** `[NUOVO PUNTO]`
        * `[]` i. Servizi di assistenza pratica (es. aiuto domestico, trasporto) e supporto psicologico per genitori con disabilità o malattie che limitano la loro capacità di cura dei figli.

* **5. Copertura Sanitaria per Cittadini a Basso Reddito (Gestita tramite il Governo):** `[]` *(Parametri definiti, logica da implementare)*
    * `[]` a. Identificare cittadini idonei (reddito annuo < 6.000 **Ꜳ** - `LOW_INCOME_HEALTH_COVERAGE_THRESHOLD`).
    * `[]` b. Meccanismo di copertura gratuita (cure base e ospedaliere) tramite "Istituti Fondine" (finanziati da `AnthalysGovernment.treasury`). La copertura universale (`XXII.4.a.i`) garantisce accesso, qui si dettaglia la gratuità per basso reddito.
    * `[]` c. (Astratto) Definire come gli Istituti Fondine sono alimentati (es. % tasse generali).

* **6. Vacanze e Permessi Lavorativi:** `[]`
    * `[]` a. Diritto a 24 giorni di vacanza retribuita/anno (`ANNUAL_VACATION_DAYS`).
    * `[]` b. Sistema per NPC (dettagliati) per richiedere/usare giorni di vacanza.
    * `[]` c. Tracciare giorni di vacanza usati/rimanenti per NPC.
    * `[]` d. Permessi per Malattia retribuiti (definire meccanica: durata, certificazione - astratta, impatto su performance).
    * `[]` e. Permessi per Emergenze Familiari retribuiti (definire meccanica: tipi di emergenze, durata).

* `[]` **7. Estensione "Total Realism" - Evoluzione, Applicazione e Impatto Sociale delle Normative:** `[NUOVA SOTTOCATEGORIA]`
    * `[]` a. **Dinamicità delle Regolamentazioni:**
        * `[]` i. Le normative globali definite in questa sezione (orari di lavoro, tasse, welfare) non sono statiche, ma possono essere soggette a revisione e modifica nel tempo da parte dell'`AnthalysGovernment` (`VI.1`) in risposta a:
            * Cambiamenti economici (`VIII.5.b`).
            * Pressione dell'opinione pubblica (`VI.2.e.ii`).
            * Proposte di partiti politici (`VI.1.d`) o esiti di referendum (`VI.4`).
            * Crisi o eventi significativi (`XIV`).
        * `[]` ii. L'introduzione di nuove normative o la modifica di quelle esistenti dovrebbe essere comunicata agli NPC (tramite sistema di notizie astratto `VI.2.e.ii` e SoNet `XXIV.c.viii`) e avere un periodo di "adeguamento".
    * `[]` b. **Applicazione e Rispetto delle Norme:**
        * `[]` i. Simulazione del livello di "enforcement" per certe normative. Non tutte le leggi potrebbero essere rispettate al 100% da tutti gli NPC o aziende.
        * `[]` ii. (Se implementato sistema criminale/illeciti `XXVII`) Possibilità di evasione fiscale (`VIII.2`), lavoro nero (violazione di `XXII.1`), o frodi ai danni del sistema di welfare (`XXII.4`), con rischi e conseguenze se scoperti.
    * `[]` c. **Impatto Socio-Economico delle Normative:**
        * `[]` i. Le modifiche normative (es. aumento/diminuzione tasse, cambiamenti nei benefici) dovrebbero avere un impatto misurabile sul comportamento finanziario degli NPC (spesa, risparmio), sulla loro soddisfazione lavorativa, sul benessere generale (`IV.4.h.ii.4`), e sull'economia (`VIII.5`).
        * `[]` ii. NPC potrebbero reagire attivamente a normative percepite come ingiuste o troppo onerose (proteste astratte, malcontento, dibattito pubblico – collegamento a `VI.2.f` Attivismo).
    * `[]` d. **Equità e Accessibilità del Sistema:**
        * `[]` i. Valutare come le normative impattano diversamente NPC con diversi livelli di reddito, tratti, o situazioni familiari, e se il sistema nel suo complesso promuove l'equità (Principio `XXII.A.iii`).
        * `[]` ii. L'accesso ai benefici (sanità `XXII.5`, pensioni `XXII.4.b`) dovrebbe essere chiaro e, per quanto possibile, non eccessivamente burocratico per gli NPC (meccanica di richiesta astratta via SoNet `XXIV.c.ix`).
* `[]` **8. Regolamentazione su Prodotti Alimentari, Bevande e Beni di Consumo di Anthalys:** `[NUOVA INTEGRAZIONE]` *(Basata sul "Regolamento Alimentare di Anthal" e documenti specifici forniti)*
    * `[!]` a. **Articolo 1: Scopo e Applicabilità:**
        * `[]` i. Stabilire norme per produzione, distribuzione, vendita, conservazione e consumo di prodotti alimentari, bevande (alcoliche e non), e altri beni di consumo primari per garantire sicurezza, qualità e protezione dei consumatori.
        * `[]` ii. Le normative si applicano a tutti gli operatori del settore (produttori `C.9`, distributori `VIII.6`, venditori `XVIII.5.h`) e ai consumatori finali (`IV`).
    * `[]` b. **Articolo 2: Definizioni Chiave:**
        * `[]` i. Prodotti Alimentari Freschi.
        * `[]` ii. Prodotti Alimentari Confezionati.
        * `[]` iii. Prodotti Alimentari Crudi.
        * `[]` iv. Bevande Alcoliche.
        * `[]` v. Bevande Non Alcoliche.
        * `[]` vi. Prodotti del Tabacco Naturale (`C.9.d.i`).
        * `[]` vii. Pelli e Tessuti (`C.9.d.viii`, `C.9.d.ix`).
    * `[]` c. **Articolo 3: Licenze di Produzione e Vendita:**
        * `[]` i. Obbligo di licenza specifica (`VI.1`) per produzione/vendita di: alimentari, bevande alcoliche, bevande non alcoliche, tabacco, (da valutare) pelli/tessuti.
        * `[]` ii. Concessione licenze solo a operatori conformi a standard di sicurezza, qualità, igiene, sostenibilità (`C.9.a.i`).
    * `[]` d. **Articolo 4: Standard di Produzione:**
        * `[]` i. Obbligo uso ingredienti naturali e metodi produzione sostenibili (`C.9.a.ii`).
        * `[]` ii. Divieto/limitazione additivi chimici, conservanti artificiali, pesticidi sintetici, OGM.
        * `[]` iii. Ispezioni periodiche stabilimenti da autorità sanitaria/controllo qualità (`VI.1`).
        * `[]` iv. Obbligo tracciabilità lotti (ingredienti -> prodotto finito).
    * `[]` e. **Articolo 5: Norme di Conservazione e Trasporto dei Prodotti:**
        * `[]` i. Temperature/condizioni specifiche per categorie prodotti.
        * `[]` ii. Norme trasporto refrigerato/controllato.
        * `[]` iii. Imballaggi (`VIII.6.5.b.i`, `C.9.d`) devono garantire integrità/sicurezza.
    * `[]` f. **Articolo 6: Etichettatura Obbligatoria e Informazioni al Consumatore:**
        * `[]` i. Etichette chiare, leggibili (lingua di Anthalys `XVII`), veritiere.
        * `[]` ii. Informazioni obbligatorie: ingredienti, valori nutrizionali, origine (preferenziale per prodotti Anthalys), scadenza/TMC, istruzioni conservazione/uso, contenuto alcolico, avvertenze/allergeni.
        * `[]` iii. Etichette specifiche per carne/pesce crudi ("da consumare crudo", precauzioni).
        * `[]` iv. Divieto indicazioni ingannevoli.
    * `[]` g. **Articolo 7: Norme per i Punti Vendita Autorizzati:**
        * `[]` i. Vendita solo in `LocationType` autorizzate (`XVIII.5.h`).
        * `[]` ii. Obbligo rispetto norme igienico-sanitarie (pulizia, temperature, scadenze).
        * `[]` iii. Formazione personale vendita su normative e gestione sicura.
    * `[]` h. **Articolo 8: Igiene e Sicurezza per la Preparazione e il Consumo (Generale):**
        * `[]` i. Personale manipolazione alimenti (specie crudi) deve seguire formazione e norme igieniche.
        * `[]` ii. Prevenzione contaminazione incrociata.
        * `[]` iii. Consumatori: lavaggio frutta/verdura; cottura sicura carni/pesce.
    * `[]` i. **Articolo 9: Educazione e Sensibilizzazione dei Cittadini:**
        * `[]` i. Programmi educativi governativi (`VI.1`) su: dieta equilibrata, consumo/conservazione sicura, rischi alcol/tabacco, lettura etichette.
        * `[]` ii. Campagne sensibilizzazione periodiche.
        * `[]` iii. Risorse informative disponibili (online `XII.4`, punti vendita, centri civici).
    * `[]` j. **Articolo 10: Norme Specifiche per il Consumo di Carne e Pesce Crudi:**
        * `[]` i. Acquisto solo da fonti affidabili con etichettatura specifica.
        * `[]` ii. Conservazione domestica rigorosa (0-2°C, consumo entro 1-2 giorni).
        * `[]` iii. Preparazione domestica con massima igiene.
        * `[]` iv. Informazione consumatori su rischi residui.
    * `[]` k. **Articolo 11: Orari di Vendita (Specifico per Alcolici):**
        * `[]` i. Vendita alcolici limitata a orari specifici (variabili per tipo esercizio/normative locali `XIII.4`).
        * `[]` ii. Nessuna restrizione orario per alimenti/bevande non alcoliche (salvo orari generali negozi).
    * `[]` l. **Articolo 12: Pubblicità e Promozioni (Alcolici, Tabacco, Alimenti):**
        * `[]` i. **Alcolici e Tabacco:** Pubblicità etica stringente (non incoraggiare abuso, non per minori, messaggi salute). Vietate promozioni aggressive.
        * `[]` ii. **Alimenti e Bevande Non Alcoliche:** Pubblicità veritiera. Incoraggiate promozioni per stili vita sani.
    * `[]` m. **(Avanzato) Dettagli Normativi per Categoria Specifica:**
        * `[]` i. **Bevande Alcoliche:** Standard produzione, controlli contenuto alcolico. Divieto vendita minori 18 anni (verifica DID `XII.1.d`), sanzioni consumo irresponsabile. Supporto dipendenze.
        * `[]` ii. **Bevande Non Alcoliche:** Standard produzione, enfasi ingredienti naturali. Programmi transizione da bevande zuccherate/alcoliche.
        * `[]` iii. **Prodotti del Tabacco Naturale:** Restrizioni vendita (età `XII.1.d`), avvertenze sanitarie, divieto fumo luoghi pubblici chiusi/specifici.
        * `[]` iv. **Pelli e Tessuti:** Norme su coloranti naturali (`C.9.d.viii.3`, `C.9.d.ix.5`), assenza sostanze irritanti.
    * `[]` n. **(Estensione "Total Realism") Applicazione e Sanzioni:** (Collegamento a `XXII.A.i Dovere rispetto leggi`, `VI.1.iii.2 Polizia`, `VI.1.iii.3 Sistema Giudiziario`, `XXII.7.b`)
        * `[]` i. Ispezioni regolari da NPC ispettori (nuove carriere `VIII.1.j`).
        * `[]` ii. Multe, sospensione/revoca licenze, azioni legali per non conformità.
        * `[]` iii. Conseguenze per cittadini che violano norme (es. consumo alcol aree vietate).

---

