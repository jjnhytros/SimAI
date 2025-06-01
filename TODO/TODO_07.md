## VII. DINAMICHE SOCIALI E RELAZIONALI AVANZATE `[]` (Include vecchio `IX.1 Sistema di Interazioni`)

* **1. Interazioni Sociali:** `[]`
    * `[]` a. Interazioni base (`SOCIALIZING`, `BEING_INTIMATE`) implementate con classi Azione dedicate.
    * `[]` b. Espandere la varietà e la profondità delle interazioni sociali disponibili:
        * `[]` i. Implementare azioni sociali specifiche per i tratti (es. `SHARE_SPIRITUAL_INSIGHT` per `PastorTrait`, `TELL_ROMANTIC_PUN` per `PunnyRomantic`, `RILE_UP_NPC` per `HotHeaded`, `DEMAND_ATTENTION` per `Spoiled`, `BOAST_ABOUT_SELF` per `Pompous`/`DelusionalSelfImportance`, `GIVE_FINANCIAL_ADVICE` per `BornSalesperson`, `GIVE_GARDENING_ADVICE` per `GreenThumb`, `DISCUSS_FASHION_TRENDS` per `Fashionista`, `ASK_FOR_FEEDBACK` per `KeeperOfSharedKnowledge`).
        * `[]` ii. Azioni sociali più generiche ma contestuali (es. "Fare un Complimento Sincero", "Chiedere un Favore", "Offrire Aiuto", "Scusarsi", "Consolare", "Discutere di Hobby/Interessi"). (Precedentemente `[]` c. Interazioni contestuali basate su luogo, oggetti presenti, eventi in corso.)
        * `[]` iii. Azioni di Flirt più dettagliate (es. `FLIRT_GENTLE`, `FLIRT_BOLD`, `FLIRT_CHEESY_INAPPROPRIATE`).
        * `[]` iv. Interazioni legate a eventi specifici (es. "Fare le Condoglianze", "Congratularsi per un Successo").
        * `[]` v. **Interazioni Sociali legate all'Ospitalità:**
            * `[]` 1. Azioni `VISIT_NPC_AT_HOME`, `INVITE_NPC_HOME`.
            * `[]` 2. Comportamenti specifici per ospiti e ospitanti.
            * `[]` 3. Il tratto `AlwaysWelcome` influenza queste dinamiche (l'ospite si sente a casa, l'ospitante non si infastidisce).
        * `[]` vi. **Effetti dei Tratti dell'Iniziatore sul Target:** Implementare un meccanismo (es. nuovo metodo in `BaseTrait` come `get_moodlet_for_target_of_interaction`) per cui i tratti dell'NPC che inizia un'azione sociale possono influenzare direttamente l'umore o lo stato del target (es. `Beguiling` che rende il target `Flirty`).
    * `[]` c. Interazioni di gruppo.
    * `[]` d. **Reazioni alle Interruzioni Sociali e all'Attesa (per NPC Dettagliati).**
    * `[]` e. Il successo/fallimento delle interazioni dipende da skill, tratti, umore, relazione esistente.
    * `[]` f. Dialoghi dinamici (non solo animazioni, ma con testo che riflette la conversazione - molto ambizioso).
    * `[]` g. **Estensione "Total Realism" - Comunicazione Non Verbale e Sottigliezze Sociali:**
        * `[]` i. Simulazione astratta di "tono della voce" e "linguaggio del corpo" durante le interazioni, influenzati da umore, tratti (es. `Self-Assured` vs `Shy`), e relazione.
        * `[]` ii. Gli NPC che ricevono l'interazione potrebbero "percepire" questi segnali non verbali, influenzando la loro interpretazione dell'interazione e la loro risposta emotiva (moodlet) o comportamentale, al di là del semplice esito successo/fallimento.
        * `[]` iii. Skill come `EMPATHY` (IX.e) o `OBSERVANT` (IV.3.b) potrebbero migliorare la capacità di un NPC di interpretare correttamente questi segnali o di proiettarli efficacemente.
        * `[]` iv. Possibilità di "fraintendimenti" basati su segnali non verbali mal interpretati, aggiungendo complessità alle dinamiche sociali.
* **2. Sistema di Relazioni:** `[]`
    * `[]` a. Punteggi di relazione (numerici, es. da -100 a +100) tra coppie di NPC.
    * `[]` b. Tipi di relazione (`RelationshipType` Enum: es. `FAMILY`, `FRIEND`, `ROMANTIC_PARTNER`, `CRUSH`, `ENEMY`, `ACQUAINTANCE`).
        * `[]` i. Logica per la transizione tra tipi di relazione (es. da `ACQUAINTANCE` a `FRIEND`, da `FRIEND` a `ROMANTIC_PARTNER`). *(Concettualizzata, parzialmente influenzata da azioni e tratti)*.
        * `[]` ii. Definire un tipo di relazione "Cotta Infantile/Puppy Love" per `CHILD` e primi `TEENAGER`. *(Concettualizzato)*.
        * `[]` iii. Attributo `Character.childhood_crush_id: Optional[uuid.UUID]`.
        * `[]` iv. Azioni sociali specifiche per "Cotte Infantili".
        * `[]` v. Impatto sull'umore specifico per queste relazioni infantili.
    * `[]` c. Formazione e rottura di coppie romantiche. *(La logica DEVE ora considerare `sexually/romantically_attracted_to_genders` di entrambi gli NPC)*.
        * `[]` i. Il tratto `CONNECTIONS` non influenza direttamente la formazione di coppie, ma il successo nella carriera potrebbe indirettamente rendere un NPC più "desiderabile".
        * `[]` ii. Tratti come `LOVEBUG`, `LOVE_STRUCK`, `HEARTBREAKER`, `LOVE_CYNIC`, `LOVE_SCORNED`, `MONOGAMOUS`, `POLYAMOROUS`, `UNFLIRTY`, `INAPPROPRIATE_FLIRT`, `FAIRY_TALE_FANATIC`, `OVERLY_ANALYTICAL_AMORIST`, `COMPULSIVE_AFFECTION_SEEKER` influenzano fortemente la formazione, la stabilità e la rottura delle relazioni. *(Classi tratto definite concettualmente)*.
    * `[]` d. **Gestione Culturale delle Relazioni Consanguinee:** (Revisione del precedente controllo anti-incesto universale)
        * `[]` i. Il sistema attuale previene relazioni romantiche tra familiari più stretti (es. genitori-figli, fratelli diretti) come norma di base. *(Stato precedente: controllo anti-incesto universale implementato)*.
        * `[]` ii. **Logica Culturale Modulare:** Implementare un sistema dove la permissività di relazioni romantiche tra familiari (es. cugini di vario grado, o altri gradi di parentela a seconda della definizione culturale) dipende da un attributo `cultural_background` o `family_tradition` dell'NPC. (Collegamento a `XX. ATTEGGIAMENTI CULTURALI/FAMILIARI` e potenziale futuro sistema di Culture Dettagliate in `C. PROGETTI FUTURI E DLC`).
        * `[]` iii. Definire un set di "norme culturali sulla consanguineità" possibili nel lore di Anthalys (es. `STRICT_EXOGAMY` - divieto forte anche per cugini; `COUSIN_MARRIAGE_PERMITTED`; `DYNASTIC_CONSANGUINITY_TOLERATED` - per specifiche linee nobiliari/isolate; `NO_STRONG_TABOO_BEYOND_IMMEDIATE_FAMILY`). La norma di default di Anthalys potrebbe essere `STRICT_EXOGAMY`.
        * `[]` iv. L'IA per la formazione di coppie (`IV.4.d`, `VII.2.c`) e le reazioni degli NPC alle relazioni altrui devono consultare queste norme culturali. La scelta di un partner consanguineo da parte di un NPC dovrebbe essere fortemente influenzata dalla sua educazione culturale e dai suoi tratti (es. `REBELLIOUS`, `TRADITIONALIST` - futuri).
        * `[]` v. Le conseguenze sociali (reazioni di altri NPC, impatto sulla reputazione `VII.9`, pettegolezzi `VII.9`) per relazioni consanguinee varieranno drasticamente in base alla norma culturale prevalente nella comunità dell'NPC, ai tratti degli osservatori (`JUDGEMENTAL`, futuri `OPEN_MINDED`, `TRADITIONALIST`), e al grado di parentela.
        * `[!]` vi. **Implicazioni Genetiche:** Se tali relazioni sono permesse da una cultura e si verificano, il sistema genetico (`II.3.d`, `IV.2.f.vii`) deve simulare un aumento della probabilità di espressione di tratti recessivi (potenzialmente negativi per la salute `IV.1.g` o altre caratteristiche) nelle generazioni successive, se il sistema genetico è sufficientemente dettagliato per supportarlo.
    * `[]` e. **Decadimento Passivo delle Relazioni:**
        * `[]` i. Implementare un leggero decadimento giornaliero per le relazioni non coltivate.
        * `[]` ii. Il tratto `MEMORABLE` e `WARM_HEARTED` riducono questo decadimento. *(Classi tratto definite)*.
    * `[]` f. Implementare meccanica di Gelosia (`JEALOUS` tratto) e sue conseguenze. *(Classe tratto definita, eventi trigger e reazioni complesse da implementare)*.
    * `[]` g. Ottimizzazione per larga scala: NPC mantengono un numero limitato di relazioni significative; gestione astratta/statistica delle relazioni per NPC di background (LOD Fascia 3).
    * `[]` h. **Estensione "Total Realism" - Profondità dei Legami Relazionali:**
        * `[]` i. Oltre al punteggio numerico, implementare una "qualità" o "profondità" della relazione basata su:
            * Esperienze significative condivise (positive e negative – collegamento a Sistema Memorie `IV.5`).
            * Compatibilità di valori fondamentali (se implementati in `IV.3.g`) e tratti di personalità.
            * Livello di fiducia reciproca e vulnerabilità condivisa (potrebbe essere un nuovo attributo della relazione).
            * Comprensione reciproca (NPC con alta relazione e skill `EMPATHY` potrebbero anticipare i bisogni o le reazioni dell'altro).
        * `[]` ii. Relazioni profonde potrebbero sbloccare interazioni sociali uniche, offrire un maggiore supporto emotivo (moodlet di conforto più forti), o resistere meglio a conflitti minori.
        * `[]` iii. Rotture di relazioni profonde avrebbero un impatto emotivo (lutto, `LOVE_SCORNED`) più devastante e duraturo.
* **3. Meccaniche di Comunicazione Autentica e Onesta:** `[]` *(Concettualizzato, influenzato da tratti)*
    * `[]` a. Utilizzare/Espandere Tratti relativi (`SINCERE`, `DISHONEST`, `JADED`).
    * `[]` b. Nuove interazioni: `SHARE_HONEST_FEELING`, `CONFRONT_ISSUE_DIRECTLY`, `OFFER_CONSTRUCTIVE_CRITICISM`.
    * `[]` c. Effetti variabili (umore, relazione, sviluppo di un punteggio di "Autenticità/Fiducia della Relazione").
    * `[]` d. (Avanzato) Consenso nelle Interazioni Intime (oltre al semplice check di relazione).
    * `[]` e. (Avanzato) Benessere Emotivo Post-Intimità (legato alla qualità della connessione, non solo al soddisfacimento del bisogno).
* **4. Eventi Sociali Drastici (Violenza, Morte, Tradimento):** `[]` *(Parzialmente coperto da reazioni tratti)*
    * `[]` a. Azioni di combattimento fisico (`FIGHT_NPC`) tra NPC e loro conseguenze (ferite - future, relazioni danneggiate, moodlet).
    * `[]` b. NPC testimoni di violenza (`EVENT_NAME_WITNESSED_FIGHT`) reagiscono in base ai loro tratti (`SQUEAMISH` si nausea, `COWARDLY` fugge, `HOT_HEADED` potrebbe unirsi). *(Tratti definiti, evento da implementare)*.
    * `[]` c. Gestione della morte di NPC e reazioni degli altri (lutto - moodlet, azione `MOURN_NPC` futura, impatto diverso per `HEARTLESS`, `SURVIVOR_OF_LOSS`, `STOIC`). *(Tratti ed eventi concettualizzati)*.
    * `[]` d. **Tradimento e Infedeltà:**
        * `[]` i. NPC (specialmente con tratti come `HEARTBREAKER`, `FORBIDDEN_LOVER`, o `POOR_IMPULSE_CONTROL` in certe situazioni) potrebbero intraprendere relazioni romantiche/intime al di fuori della coppia principale.
        * `[]` ii. Sistema di "scoperta" del tradimento (casuale, investigazione da parte del partner, pettegolezzi).
        * `[]` iii. Forti reazioni emotive e relazionali per il partner tradito (influenzate da tratti come `MONOGAMOUS`, `JEALOUS`, `LOVE_SCORNED`).
        * `[]` iv. Conseguenze come rottura, litigio, moodlet di lunga durata.
* **5. Relazioni Intergenerazionali e Trasmissione Culturale/Valoriale:** `[]`
    * `[]` a. Il tratto `GRANDPARENT` influenza le interazioni con i nipoti.
    * `[]` b. (Sandwich Generation) Azione `CARE_FOR_ELDERLY_PARENT` (definire). *(Concetto annotato, rilevante per NPC Adulti)*.
    * `[]` c. (Avanzato) Trasmissione di "valori" o "abitudini" dai genitori ai figli (potrebbe influenzare la probabilità di sviluppare certi tratti o preferenze).
    * `[]` d. Impatto delle relazioni familiari sulla scelta delle aspirazioni o sul benessere a lungo termine.
* **6. Strutture Relazionali Non Monogame (Poliamore):** `[]` *(Tratto `POLYAMOROUS` definito concettualmente)*.
    * `[]` a. Adattare la struttura dati di `Character` e `BackgroundNPCState` per permettere partner romantici multipli (es. `romantic_partners_ids: List[uuid.UUID]`).
    * `[]` b. Logica per consenso e comunicazione in relazioni poliamorose (interazioni specifiche).
    * `[]` c. Impatto sull'umore e sulla stabilità relazionale in base alla gestione di relazioni multiple e alla compatibilità dei tratti dei partner.
* **7. Sfide Relazionali per Giovani Adulti Emergenti (`YOUNG_ADULT`):** `[]`
    * `[]` a. Maggiore enfasi sulla formazione di relazioni romantiche stabili e amicizie profonde.
    * `[]` b. Pressione sociale (astratta) per "sistemarsi" o raggiungere certi traguardi relazionali.
    * `[]` c. Eventi specifici o "crisi" legate alla transizione verso relazioni adulte (es. prima convivenza, discussioni su impegno a lungo termine).
* **8. Sistema di Mentoring tra NPC:** `[]` *(Tratto `SUPER_MENTOR` definito)*.
    * `[]` a. Definire azione `MENTOR_SKILL_TO_NPC` (e variante `OFFER_PAID_MENTORING_SESSION`).
    * `[]` b. **Regola di Gioco**: NPC può fare da mentore solo per skill in cui ha almeno il livello `settings.MIN_SKILL_LEVEL_FOR_MENTORING`.
    * `[]` c. L'allievo guadagna skill più velocemente se mentorato.
    * `[]` d. Tratto `SUPER_MENTOR` potenzia l'efficacia del mentoring e i guadagni.
    * `[]` e. Interfacciare con sistema di valuta "Athel" per mentoring a pagamento.
* **9. Pettegolezzo e Reputazione (Sistema Futuro):** `[]`
    * `[]` a. NPC possono iniziare e diffondere pettegolezzi (`GOSSIP_ABOUT_NPC` azione).
    * `[]` b. I pettegolezzi possono essere veri o falsi.
    * `[]` c. Un sistema di "reputazione" per ogni NPC (es. affidabile, donnaiolo, generoso, tirchio) influenzato dalle sue azioni e dai pettegolezzi.
    * `[]` d. La reputazione influenza come gli altri NPC percepiscono e interagiscono con un personaggio. Tratti come `JUDGMENTAL` o `NOSY` interagiscono fortemente.

---

