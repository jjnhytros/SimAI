## II. CREAZIONE DEL PERSONAGGIO GIOCABILE (SimAI Iniziale) `[]`

* `[!]` **1. Filosofia della Creazione Iniziale:**
    * `[]` a. Permettere al giocatore di definire il punto di partenza della sua storia nella simulazione attraverso la creazione di uno o più personaggi giocabili iniziali (es. un single, una coppia, una famiglia).
    * `[]` b. Il processo deve essere intuitivo ma offrire profondità di personalizzazione coerente con i sistemi di gioco (tratti, aspirazioni, aspetto).
    * `[]` c. I personaggi creati dal giocatore sono NPC "Dettagliati" (LOD1) fin dall'inizio, con pieno accesso ai sistemi di bisogni, emozioni, IA decisionale, etc. (`Character` class è LOD1).
    * `[]` d. Fornire al giocatore un'esperienza di creazione che lo connetta emotivamente ai suoi SimAI iniziali.

* `[]` **2. Interfaccia di Creazione del Personaggio/Famiglia (CAS - Create-A-Sim/Family):** (`CASManager.h/.cpp` creato)
    * `[]` a. **Personalizzazione Aspetto Fisico Dettagliata:** (Utilizza gli stessi asset e logiche di `IV.0.a` per la generazione NPC, ma con interfaccia per il giocatore) (`AppearanceData.h` creato).
        * `[]` i. Strumenti per modificare parti del viso (occhi, naso, bocca, forma viso, mascella, etc.) e del corpo (altezza, corporatura, percentuale muscoli/grasso).
        * `[]` ii. Ampia selezione di colori per pelle (con tonalità realistiche e fantasy se previste dal lore), capelli (acconciature e colori naturali e non), occhi (inclusa eterocromia opzionale).
        * `[]` iii. Opzioni per dettagli aggiuntivi: cicatrici, nei, vitiligine, efelidi, tatuaggi (collegamento a Skill Tatuaggi IX.e e carriera Tatuatore VIII.1.j), piercing.
        * `[]` iv. Sistema di anteprima dinamica del personaggio durante la personalizzazione.
    * `[]` b. **Definizione Identità di Base:** (Utilizza gli stessi attributi di `IV.0.b, IV.0.g` e `IV.3.j`) (`Identity` struct in `Character.h` e `character_enums.h` creati).
        * `[]` i. Scelta Nome e Cognome (con suggerimenti opzionali basati sul lore di Anthalys).
        * `[]` ii. Scelta Età Iniziale (generalmente limitata a certi stadi di vita per i fondatori, es. `YOUNG_ADULT`, `ADULT`, o `CHILD`/`TEENAGER` se creati come parte di una famiglia con adulti) (Attributi in `Identity` e `LifeStage` enum).
        * `[]` iii. Scelta Sesso Biologico e Identità di Genere (opzioni flessibili e inclusive come da `IV.3.b.viii.11` e `IV.3.j`, con pronomi personalizzabili) (Enums e attributi creati).
        * `[]` iv. Definizione Voce (selezione da preset con pitch e modulazione regolabili) (Attributo `voiceId` in `Identity`).
        * `[]` v. Definizione Orientamento Sessuale e Romantico (come da `IV.3.j`, con opzione per "esplorazione" per personaggi più giovani) (Enums e attributi creati).
    * `[]` c. **Assegnazione Tratti di Personalità:** (Selezione dalla lista definita in `IV.3.b`) (`TraitManager` e `Character::addTrait` previsti).
        * `[]` i. Il giocatore assegna un numero limitato di tratti (es. 3-5, come da `IV.3.b.i`) scelti dalla lista completa e categorizzata dei tratti disponibili.
        * `[]` ii. L'interfaccia CAS deve mostrare chiaramente le descrizioni dei tratti, i loro effetti principali e le eventuali incompatibilità o conflitti tra tratti selezionati (come da `IV.3.b.ix` e `IV.3.b.x.1`).
    * `[]` d. **Scelta Aspirazione di Vita:** (Selezione dalle aspirazioni definite in `IV.3.a`) (`AspirationManager` e `Character::setAspiration` previsti).
        * `[]` i. Il giocatore sceglie un'Aspirazione di Vita a lungo termine per ogni personaggio giocabile creato.
        * `[]` ii. L'interfaccia CAS mostra le diverse categorie di aspirazioni e le aspirazioni specifiche disponibili, con una descrizione dei loro obiettivi generali e delle ricompense (tratti bonus, soddisfazione).
    * `[]` e. **Definizione Abbigliamento Iniziale:** (Utilizza il sistema di abbigliamento di `IV.0.f`) (`ClothingManager.h`, `Outfit.h`, `ClothingItem.h` creati; `Character` ha `wardrobe_`).
        * `[]` i. Selezione di outfit per ogni categoria richiesta (quotidiano, formale, sportivo, notte, feste, nuoto, freddo, caldo) da un guardaroba iniziale fornito.
        * `[]` ii. (Avanzato) Possibilità di personalizzare i colori/pattern di alcuni capi di vestiario base.
        * `[]` iii. Gli outfit scelti saranno il guardaroba base del personaggio all'inizio del gioco.
    * `[]` f. **(Opzionale) Definizione Relazioni Iniziali (se si crea una famiglia/gruppo):** (`RelationshipManager.h`, `relationship_types.h` creati).
        * `[]` i. Se il giocatore crea più personaggi contemporaneamente (es. una famiglia, coinquilini), deve poter definire le loro relazioni iniziali (es. coniugi, partner, genitori-figli, fratelli, amici intimi).
        * `[]` ii. Impostazione dei punteggi di relazione iniziali (default positivi per familiari stretti, neutri o leggermente positivi per amici/coinquilini).
        * `[]` iii. Integrazione con l'Albero Genealogico (`IV.2.f`) per i membri della famiglia creati.
    * `[]` g. **(Opzionale Avanzato) Background Narrativo e Eventi Formativi:** (Espansione di `IV.0.h`)
        * `[]` i. Possibilità per il giocatore di scegliere alcuni "eventi formativi" chiave o un "archetipo di background" per i propri personaggi (es. "infanzia difficile", "talento artistico precoce", "background accademico brillante", "sopravvissuto a una tragedia").
        * `[]` ii. Questi potrebbero assegnare piccole quantità di XP skill iniziali, influenzare la probabilità di certi tratti nascosti o acquisibili, o fornire memorie iniziali uniche (IV.5).
        * `[]` iii. (Alternativa) Consentire al giocatore di scrivere un breve testo di background che il gioco potrebbe (opzionalmente) analizzare in modo astratto per questi effetti.

* `[]` **3. Sistema Genetico per Famiglie Iniziali e Discendenti:** (Stesso sistema di `IV.0.a.i`, `IV.2.c`, `IV.2.f`) (`GeneticsSystem.h/.cpp`, `Genome.h` creati).
    * `[]` a. Durante la creazione di una famiglia in CAS, se si creano personaggi imparentati (es. genitori e figli, fratelli), l'aspetto dei figli (o la somiglianza tra fratelli) dovrebbe poter ereditare caratteristiche visibili dai genitori (o condividerle) in modo plausibile.
        * `[]` i. Interfaccia per "generare" figli da due genitori in CAS, con possibilità di randomizzazione e ritocco.
    * `[]` b. Questo stesso sistema genetico (aspetto fisico e potenziale ereditarietà dei tratti di personalità `IV.2.f.vi`) verrà utilizzato per tutti i nuovi NPC nati nel corso della simulazione (`IV.2.c`).
    * `[]` c. Possibilità di "gemelli identici" o "gemelli fraterni" se si creano figli multipli contemporaneamente.
    * `[]` d. **Estensione "Total Realism" - Genetica Avanzata:** (Collegamento a `IV.2.f.vii` e `IV.1.g`) (`Genome.h` è un inizio).
        * `[]` i. Ereditarietà di un range più ampio di caratteristiche fisiche (oltre l'aspetto base) e predisposizioni (es. talenti innati per certe skill `IV.3.f`, suscettibilità a malattie specifiche `IV.1.g`). *(Aggiornato stato a [] per la definizione di `Genome.h` e placeholder per malattie genetiche)*
            * `[]` 1. Definire meccanismo per come i "tratti recessivi (potenzialmente negativi per la salute `IV.1.g` o altre caratteristiche `IV.3.b`)" sono rappresentati nel genoma astratto di un NPC.
            * `[]` 2. Implementare la logica di ereditarietà che aumenta la probabilità di espressione di questi tratti recessivi in caso di relazioni consanguinee (`VII.2.d.vi`), basata sul grado di parentela.
        * `[]` ii. (Molto Avanzato) Simulazione di mutazioni genetiche casuali (rare) con effetti variabili (positivi, negativi, neutri) che possono introdurre nuovi tratti o modificare quelli esistenti.

* `[]` **4. Fase Finale: Scelta del Mondo/Lotto Iniziale e Fondi:** (`WorldManager.h`, `LotManager.h`, `PlayerHousehold.h` creati).
    * `[]` a. Dopo la creazione della famiglia/personaggio giocabile, il giocatore seleziona un mondo o quartiere di partenza (se più di uno disponibile).
    * `[]` b. Il giocatore sceglie un lotto residenziale vuoto o una casa pre-costruita disponibile in cui trasferirsi (collegamento a `XVIII.5.j` Proprietà Immobiliari e `I. MONDO DI ANTHALYS E SIMULAZIONE GENERALE` per la struttura del mondo).
    * `[]` c. Assegnazione di fondi iniziali ("Athel") alla famiglia/personaggio giocabile. L'ammontare potrebbe: (`PlayerHousehold` ha `currentFunds_`).
        * `[]` i. Essere uno standard fisso.
        * `[]` ii. Variare in base a "scenari di partenza" o difficoltà scelte dal giocatore.
        * `[]` iii. Essere influenzato dal numero di membri della famiglia o dal background scelto (II.2.g).
    * `[]` d. La simulazione inizia una volta che la famiglia è stata trasferita in un lotto.

* `[F]` **5. (Futuro) Scenari di Inizio Partita ("Story Mode Starters"):**
    * `[F]` a. Oltre alla creazione libera, offrire al giocatore scenari predefiniti con personaggi, relazioni, e situazioni iniziali uniche che presentano sfide o obiettivi specifici (es. "Single al verde in città nuova", "Famiglia con troppi figli e pochi soldi", "Erede di una fortuna misteriosa").
    * `[F]` b. Questi scenari potrebbero utilizzare il CAS per la personalizzazione estetica dei personaggi predefiniti.

---

