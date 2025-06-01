## XIX. SISTEMA GIOCHI D'AZZARDO E SCOMMESSE DI ANTHALYS `[]`

* **1. Principi Generali e Regolamentazione di Base:** `[]`
    * `[!]` a. Legalità e regolamentazione di scommesse in denaro e giochi da casinò (piattaforme fisiche e online) per garantire trasparenza, equità e sicurezza.
    * `[!]` b. Accesso consentito solo ai maggiorenni (18+ anni come da input utente) – integrare con sistema età NPC (IV.2) e controlli di verifica.
    * `[]` c. Requisito di tutte le attività su piattaforme rintracciabili e regolamentate.
    * `[!]` d. Enfasi su gioco responsabile e protezione dei minori.

* **2. Sistema di Scommesse:** `[]`
    * `[]` a. **Tipologie di Scommesse Consentite:**
        * `[]` i. **Scommesse Sportive:**
            * `[]` 1. Su eventi sportivi nazionali/internazionali, competizioni ufficiali, tornei.
            * `[]` 2. Supporto per scommesse pre-partita e in tempo reale.
            * `[]` 3. Implementare sistema di aggiornamento continuo delle quote.
        * `[]` ii. **Scommesse Quotidiane:**
            * `[]` 1. Su eventi quotidiani imprevedibili e competizioni locali improvvisate.
            * `[]` 2. Meccaniche per coinvolgere la comunità tramite scommesse su attività giornaliere.
        * `[]` iii. **Scommesse di Intrattenimento:**
            * `[]` 1. Su gare e competizioni trasmesse in diretta (es. eventi canori, premiazioni cinematografiche).
            * `[]` 2. Requisito di trasmissione in diretta per evitare manipolazioni.
        * `[]` iv. **Scommesse Politiche:**
            * `[]` 1. Su esiti di elezioni, referendum, decisioni governative ufficiali (collegamento a Sistema Politico VI).
    * `[]` b. **Tipologie di Scommesse Non Consentite (da far rispettare):**
        * `[]` i. Divieto scommesse su programmi TV registrati (serie TV, film, ecc.).
        * `[]` ii. Divieto scommesse su eventi con risultati già conosciuti o facilmente manipolabili.
        * `[]` iii. Divieto scommesse su eventi personali con scambio di denaro al di fuori di piattaforme regolamentate (considerate illegali e da sanzionare se scoperte).
    * `[]` c. **Sistema di Piazzamento Scommesse per NPC:**
        * `[]` i. Definire azione `PLACE_BET` per NPC.
        * `[]` ii. Logica IA per NPC per decidere se, quando, su cosa e quanto scommettere (influenzata da tratti futuri come `GAMBLER`, `RISK_TAKER`, `IMPULSIVE`, `CALCULATING_STRATEGIST`; finanze; `KNOWLEDGE_SPORTS`/`KNOWLEDGE_POLITICS`; disponibilità e attrattiva eventi).
        * `[]` iii. Interfaccia (astratta o TUI) per piattaforme di scommesse (fisiche o online).
    * `[]` d. **Gestione Eventi Scommettibili:**
        * `[]` i. Sistema per generare/tracciare eventi sportivi, quotidiani, di intrattenimento e politici su cui scommettere, con quote variabili.
        * `[]` ii. Meccanismo per determinare e pubblicare esiti degli eventi in modo sicuro.

* **3. Tassazione sulle Scommesse (Importo Scommesso):** `[]`
    * `[]` a. Implementare tassazione progressiva sull'importo di ogni scommessa.
    * `[P]` b. Definire la struttura delle aliquote fiscali per gli importi delle scommesse in `settings.py` o `economy_config.py` (basata sulla tabella fornita dall'utente, da 0% per scommesse fino a 6000 Ꜳ, fino a 40% per scommesse oltre 90000 Ꜳ).
        * `[]` i. Costante per soglia di esenzione fiscale (6000 Ꜳ).
    * `[]` c. Logica per calcolare e detrarre la tassa immediatamente dall'importo scommesso (l'NPC paga la scommessa + la tassa).
    * `[]` d. Flusso delle tasse raccolte dalle scommesse verso `AnthalysGovernment.treasury` (collegamento a VIII.2.d).

* **4. Sistema dei Casinò:** `[]`
    * `[]` a. **Tipologie di Casinò:**
        * `[]` i. **Casinò Fisici:**
            * `[]` 1. Creare nuovo `LocationType.CASINO` e definire lotti specifici in città.
            * `[]` 2. Implementare oggetti/azioni interagibili per giochi da casinò (slot machine, poker, roulette).
            * `[]` 3. Meccanismo di controllo età rigoroso all'ingresso (NPC < 18 anni non possono entrare/giocare).
        * `[]` ii. **Casinò Online:**
            * `[]` 1. Accesso tramite azione `USE_COMPUTER` -> `GAMBLE_ONLINE_CASINO` (o app mobile astratta).
            * `[]` 2. Meccanismi di verifica dell'età obbligatoria per l'accesso e la registrazione online.
            * `[]` 3. (Concettuale) Sicurezza tramite crittografia avanzata e registrazione delle transazioni.
    * `[]` b. **Giochi da Casinò Specifici (da implementare come azioni e oggetti):**
        * `[]` i. Slot Machine (azione `PLAY_SLOT_MACHINE`).
        * `[]` ii. Poker (azione `PLAY_POKER_TABLE_GAME`, potrebbe richiedere skill `LOGIC`, `BLUFFING` (futura), o `GAMBLING_SKILL` (futura), e interazioni sociali con altri NPC al tavolo).
        * `[]` iii. Roulette (azione `PLAY_ROULETTE_TABLE_GAME`).
        * `[]` iv. Definire meccaniche di gioco, regole e probabilità di vincita (RTP - Return To Player) e payout per ogni gioco, assicurando equità.
    * `[]` c. **Limiti delle Vincite nei Casinò:**
        * `[]` i. Implementare limite di vincita massima per singola giocata/scommessa al casinò a 10.000 Ꜳ (`MAX_CASINO_WIN_PER_PLAY`).
    * `[]` d. **IA per Comportamento al Casinò:**
        * `[]` i. NPC (specialmente con tratti rilevanti come futuro `GAMBLER`, `THRILL_SEEKER`, `ADDICTIVE_PERSONALITY`) decidono di visitare casinò fisici o giocare online.
        * `[]` ii. Logica IA per scelta dei giochi, importi da scommettere per giocata, e una gestione semplificata del "bankroll" per sessione di gioco.
        * `[]` iii. Rischio di sviluppare/peggiorare il tratto `ADDICTIVE_PERSONALITY` (IV.3.c) o un futuro `GAMBLING_ADDICTION` attraverso il gioco eccessivo.

* **5. Tassazione sulle Vincite dei Casinò:** `[]`
    * `[]` a. Implementare tassazione progressiva sulle vincite nette dei casinò per singola sessione o per vincita significativa.
    * `[P]` b. Definire la struttura delle aliquote fiscali per le vincite dei casinò in `settings.py` o `economy_config.py` (basata sulla tabella fornita dall'utente, da 0% per vincite fino a 600 Ꜳ, fino a 12% per vincite tra 6001-10000 Ꜳ).
        * `[]` i. Costante per soglia di esenzione fiscale (600 Ꜳ).
    * `[]` c. Logica per calcolare e detrarre la tassa automaticamente dalle vincite erogate all'NPC.
    * `[]` d. Flusso delle tasse raccolte dalle vincite dei casinò verso `AnthalysGovernment.treasury`.

* **6. Misure di Sicurezza e Gioco Responsabile:** `[]`
    * `[]` a. **Programmi di Gioco Responsabile (Simulati per NPC):**
        * `[]` i. Implementare meccanismi di "auto-limitazione" per NPC: se un NPC perde una soglia di denaro in un periodo, riceve moodlet negativi forti (es. `DEVASTATED_BY_LOSSES`, `GAMBLING_REGRET`) e l'IA evita di giocare per un periodo.
        * `[]` ii. (Avanzato) Opzioni di "autoesclusione": NPC con `ADDICTIVE_PERSONALITY` e perdite consistenti potrebbero autonomamente (o tramite intervento di familiari/eventi) cercare di "autoescludersi" (azione `REQUEST_GAMBLING_BAN`) per un periodo.
        * `[]` iii. Collegamento a futuri servizi di supporto per la dipendenza da gioco (terapie, gruppi di supporto – vedi sistema sanitario o sociale).
    * `[]` b. **Monitoraggio delle Attività di Gioco (Astratto dal "sistema regolatore"):**
        * `[]` i. Meccanismo simulato per cui il sistema regolatore (governo) identifica NPC con pattern di gioco eccessivi o "sospetti" (es. vincite enormi e frequenti che potrebbero indicare cheating se fosse possibile nel gioco).
        * `[]` ii. (Futuro) Conseguenze per NPC "segnalati": indagini (astratte), possibili sanzioni se collegate a attività illegali.
    * `[]` c. **Protezione dei Dati e Privacy (Piattaforme Online):** *(Principio generale già presente, qui specifico per transazioni finanziarie e dati di gioco)*.
        * `[]` i. Assicurare (concettualmente nel design) la sicurezza delle transazioni finanziarie per il gioco online.
        * `[]` ii. Accesso limitato ai dati personali per ridurre il rischio di violazioni (principio di design).

* **7. Impatto Economico e Sociale del Gioco d'Azzardo:** `[]`
    * `[]` a. I casinò e le piattaforme di scommesse generano reddito (tassato) per il governo.
    * `[]` b. Creazione di posti di lavoro (future carriere: Croupier, Gestore Casinò, Analista Quote).
    * `[]` c. Potenziale impatto negativo su NPC vulnerabili (debiti, problemi relazionali, dipendenza) – da simulare tramite moodlet, tratti, eventi e interazioni.

---

