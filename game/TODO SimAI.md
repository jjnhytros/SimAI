# TODO List: Simulatore di Vita "SimAI" (Città di Anthalys)

**Legenda:**
* `[]`: Non iniziato
* `[P]`: Parzialmente completato / In corso
* `[x]`: Completato (per la sua implementazione base/attuale)
* `[+]`: Funzioni aggiuntive possibili/idee (generalmente per dopo o di complessità maggiore)
* `[ELEC]`: Punto ispirato/adattato dalla TODO List di `simai/election`

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
        * a. Ciclo giorno/notte di 28 ore con colori cielo graduali e nome del periodo. `[x]`
        * b. 6 Velocità di gioco controllabili (0-5) con impostazioni personalizzate. `[x]`
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
            * iii.`[]` Luoghi di lavoro (uffici, negozi, ecc. - vedi Sezione Lavoro).
            * iv. `[]` Servizi pubblici: Stazione di polizia, Caserma dei vigili del fuoco, Ospedale (edifici e interazioni base).
            * v.  `[]` Luoghi di svago/cultura: Parchi, Cinema (placeholder), Ristoranti (placeholder), Palestre, Biblioteche.
        * e. `[+]` Sistema di trasporti pubblici (es. fermate autobus, NPC li usano).
    * 4. `[+]` **Ambiente Dinamico e Interattivo:**
        * a. `[+]` (Spostato da I.3.e) Impatto visivo e su NPC di Meteo e Stagioni.
        * b. `[+]` (Molto Avanzato) Modalità "Costruisci/Compra" per modificare lotti (per osservatore/debug o per IA NPC avanzata).
        * c. `[+]` Sistema di tracciabilità e incentivi per l'uso responsabile dei servizi di raccolta rifiuti (collegato al Documento d'Identità).

**III. SIMULAZIONE NPC (Bisogni, IA, Ciclo Vita)**
    * 1. **Sistema dei Bisogni:** `[x]`
        * a. `[x]` 7 Bisogni modulari implementati (`Vescica`, `Fame`, `Energia`, `Divertimento`, `Socialità`, `Igiene`, `Intimità`) con meccaniche di variazione (tassi base, moltiplicatori periodo), inizializzazione casuale.
        * b. `[+]` Aggiungere bisogni più complessi o secondari (es. Comfort, Ambiente, Sete, Stress, Sicurezza).
        * c. `[+]` Interdipendenze più profonde tra bisogni (es. energia bassa peggiora umore e capacità di socializzare, stress aumenta decadimento altri bisogni).
        * d. `[+]` Modificatori di bisogno a lungo termine (tratti, età, salute, oggetti posseduti, qualità dell'ambiente).
        * e. `[+]` Bisogni emergenti specifici per stadi di vita (es. "gioco" per bambini) o situazioni.
        * f. `[]` **Sistema di Malattie e Salute:** NPC possono ammalarsi (casualmente, per scarsa igiene/energia/cibo, o per eventi specifici) con impatto su bisogni, umore, capacità lavorative/sociali. `[]` NPC cercano cure (riposo, medicine - se disponibili, interazione con Ospedale/Medico).
    * 2. **Ciclo Vita NPC:** `[P]`
        * a. `[x]` Età NPC che progredisce (giorni, mesi, anni) e visualizzazione base.
        * b. `[P]` Meccanica di gravidanza base (probabilità, durata, reset stato, no re-gravidanza durante).
        * c. `[]` Nascita di nuovi NPC (bambini, uso di `bundles.png`), gestione visiva e comportamentale di base per neonati (bisogni specifici, interazioni con genitori/tutori).
        * d. `[]` Implementare stadi di vita successivi (bambino `child.png`, adolescente `teen.png`, giovane adulto, adulto, anziano) con bisogni, comportamenti, abilità e sprite differenziati.
        * e. `[+]` Invecchiamento visivo (cambio sprite/texture, postura) e morte naturale per NPC anziani.
        * f. `[+]` Albero genealogico e gestione legami familiari (genitori, figli, fratelli, coniugi).
        * g. `[+]` Congedo retribuito per maternità/paternità (collegato a Lavoro e Nascita).
    * 3. **Intelligenza Artificiale NPC (Comportamento e Decisioni):** `[P]`
        * a. `[P]` Soddisfa i 7 bisogni attuali tramite oggetti/azioni esistenti.
        * b. `[x]` Logica decisionale base con priorità sui bisogni.
        * c. `[x]` Comportamento "Wandering" per stato idle.
        * d. `[]` IA per usare i nuovi oggetti per Divertimento (es. TV) e Igiene (es. Doccia) e Oggetti Scolastici.
        * e. `[]` **Sistema di Umore (Mood):** Implementare un sistema di umore (es. Felice, Neutro, Triste, Arrabbiato, Stressato, Annoiato, Ispirato, Innamorato, Imbarazzato) derivato dai livelli dei bisogni, tratti, eventi recenti, relazioni, ambiente.
        * f. `[+]` Influenza dell'Umore sulle Decisioni IA: cambia priorità bisogni, scelta azioni, interazioni sociali, performance lavorativa/abilità.
        * g. `[+]` Sistema di "Moodlet/Buff": Modificatori temporanei (positivi/negativi) all'umore e/o ai tassi dei bisogni basati su azioni specifiche, eventi, oggetti, relazioni.
        * h. `[P]` Obiettivi a Breve e Lungo Termine/Aspirazioni NPC (collegato a "Caratteristiche Personaggio").
        * i. `[+]` Pianificazione AI Avanzata (es. Goal-Oriented Action Planning - GOAP, Behavior Trees) per comportamenti multi-step complessi.
        * j. `[+]` Routine Giornaliere/Settimanali personalizzate (lavoro, sonno, tempo libero, pasti) e apprese dagli NPC, influenzate da orari lotti comunitari.
        * k. `[+]` Apprendimento e Adattamento NPC: Sviluppo preferenze (oggetti, attività, cibo, altri NPC), adattamento a routine o a cambiamenti ambientali, modifica pesi decisionali. `[ELEC]`
        * l. `[+]` Migliore Percezione Ambientale: NPC "notano" e reagiscono a oggetti nuovi/rilevanti, stato di pulizia del lotto, azioni di altri NPC, cambiamenti di luce/meteo.
        * m. `[+]` Gestione Fallimenti Azioni e Ripianificazione: Cosa fa un NPC se un'azione fallisce? (es. riprova, sceglie alternativa, si frustra).
        * n. `[]` IA per la scelta del **vestiario** in base a contesto (meteo, ora, luogo, attività, evento sociale – vedi VI.1.d).
        * o. `[+]` Simulazione "Off-Screen" (Level of Detail - LoD) per NPC non visibili.
        * p. `[+]` Implementazione di **Bias Cognitivi** (es. conferma, ragionamento motivato, bandwagon) nell'IA. `[ELEC]`
        * q. `[+]` Decisioni NPC bilanciano **valori/identità vs. bisogni/logica situazionale**. `[ELEC]`
        * r. `[+]` Comportamento Strategico NPC per obiettivi a lungo termine. `[ELEC]`
        * s. `[+]` IA NPC per la "Gestione della Propria Vita": definire strategie per obiettivi personali. `[ELEC]`
        * t. `[]` IA per interagire con i servizi cittadini (usare Documento d'Identità, punti raccolta rifiuti).
        * u. `[]` IA per interagire con i servizi cittadini (es. usare Documento d'Identità, usare punti raccolta rifiuti, gestire finanze su app governativa). `[ESPANSIONE]`
        * v. `[]` IA per la gestione dei rifiuti domestici (usare contenitori corretti, usare smaltitori automatici). `[NUOVO]`

**IV. INTERAZIONI E DINAMICHE SOCIALI**
    * 1. **Interazioni Sociali:** `[P]`
        * a. `[x]` Interazione "Intimità" base (ricerca partner, Fiki Fiki/Flirt, durata, soddisfazione reciproca).
        * b. `[x]` Azione "Telefonare" per Socialità.
        * c. `[]` Aggiungere interazioni sociali dirette più varie tra NPC (es. "parlare" in linguaggio **Anthaliano**, "scherzare", "litigare", "confortare", "fare complimenti") con impatto su bisogni e relazioni.
        * d. `[+]` Interazioni di gruppo (più NPC conversano, partecipano ad attività insieme).
    * 2. **Sistema di Relazioni:** `[]`
        * a. `[]` Implementare punteggi di relazione (amicizia, romanticismo, inimicizia, famiglia, professionale) tra NPC.
        * b. `[]` Interazioni sociali e azioni (positive/negative) influenzano i punteggi di relazione.
        * c. `[+]` Relazioni influenzano la disponibilità/probabilità e il tipo di interazioni sociali e intime.
        * d. `[+]` Grafo sociale esplicito con meccanismi di influenza (diffusione umore, opinioni, abitudini, linguaggio **Anthaliano**). `[ELEC]`
    * 3. **Caratteristiche Personaggio Approfondite:** `[P]`
        * a. `[P]` Sogni/Aspirazioni principali che guidano obiettivi (concetto base).
        * b. `[]` Tratti di Personalità (Timido, Ambizioso, Creativo, Pigro, Ordinato, Estroverso, Introverso, Irritabile, Allegro, **Partigiano Forte** `[ELEC]`, ecc.) che influenzano comportamento, bisogni, abilità, relazioni e scelta carriera/hobby.
        * c. `[+]` Vizi e Dipendenze (con meccaniche di craving e conseguenze).
        * d. `[+]` Manie e Fissazioni (collezionismo, ossessioni, routine rigide).
        * e. `[+]` Paure e Fobie (con impatto su umore e comportamento).
        * f. `[+]` Talenti Innati / Inclinazioni Naturali per abilità.
        * g. `[+]` Valori Fondamentali/Etica (Onestà, Lealtà, Potere, ecc.) che guidano decisioni "morali".
        * h. `[+]` Stile di Comunicazione Unico (legato a tratti/umore).
        * i. `[+]` Segreti NPC (scopribili, con impatto su relazioni).
        * j. `[]` **"Alfabetizzazione" Sociale/Emotiva e Pensiero Critico NPC** (come NPC interpretano interazioni complesse, pettegolezzi, "notizie" – vedi V.1.e). `[ELEC]`
    * 4. `[+]` Dinamiche di Gruppo e Comunità: Reputazione pubblica, formazione di "cricche" o gruppi di interesse, eventi sociali organizzati dagli NPC (feste, cene).
    * 5. `[]` **Vacanze e Viaggi:** NPC possono andare in vacanza (scompaiono per un po', tornano con umore/bisogni alterati) o viaggiare in altri lotti/quartieri di Anthalys per scopi specifici.

**V. INTEGRAZIONE FUNZIONALITÀ ISPIRATE DA `simai/election`**
    * *(Questa sezione adatta e integra le idee dalla TODO list di `simai/election` nel contesto della simulazione di vita SimAI. Molti punti sono già stati fusi nelle sezioni precedenti.)*
    * 1. **Modelli Comportamentali NPC Avanzati:** (Molti già integrati in III.3 e IV.3) `[P]` `[ELEC]`
    * 2. **Miglioramenti alla Simulazione del "Mondo Vivo":** `[P]` `[ELEC]`
        * a. `[]` "Progetti Personali" NPC con gestione risorse e temi (vedi III.3.h). `[ELEC]`
        * b. `[+]` Eventi Casuali e Dinamiche del Mondo di Anthalys influenzati da "stato del mondo" / "argomento caldo" (vedi X.b). `[ELEC]`
        * c. `[+]` Modellare "fonti di informazione" fittizie in Anthalys (vedi X.c). `[ELEC]`
        * d. `[+]` Generazione NPC Più Profonda e Unica (vedi III.2, IV.3). `[ELEC]`
    * 3. **Strategie Comportamentali Dinamiche NPC:** `[P]` (vedi III.3.s). `[ELEC]`
    * 4. **Generazione di Contenuti Testuali (NLG) per SimAI:** `[]` `[ELEC]`
        * a. `[]` "Pensieri" o "voci di diario" testuali più variati per gli NPC.
        * b. `[+]` Generazione di "notizie" fittizie o "post social media" all'interno del mondo di Anthalys.
        * c. `[+]` Migliorare la varietà del linguaggio **Anthaliano** parlato.
    * 5. **Principi di Progettazione e Validazione per SimAI:** `[]` `[ELEC]`
        * a. `[+]` Basare alcuni parametri NPC su concetti reali semplificati.
        * b. `[]` Calibrazione attenta dei parametri di gioco per bilanciamento.
        * c. `[]` Validazione comportamento emergente.
    * 6. **IA e LLM (Obiettivi a Lungo Termine per SimAI):** `[+]` `[ELEC]`
        * a. `[+]` Esplorare uso di LLM per arricchire dialoghi, pensieri NPC, generazione eventi.
    * 7. **Persistenza Dati NPC Avanzata (Database):** `[P]` (vedi VIII.1). `[ELEC]`

**VI. GRAFICA E AUDIO**
    * 1. **Grafica:** `[P]`
        * a. `[P]` Sprite NPC adulti (idle/walk), immagine letto, icone PNG.
        * b. `[]` Integrare spritesheets per altri stadi di vita/stati NPC.
        * c. `[]` Sprites/immagini per tutti oggetti interattivi e edifici di Anthalys.
        * d. `[]` **Sistema di Vestiario Multiplo per NPC** (cambio per contesto).
        * e. `[+]` Animazioni più dettagliate.
        * f. `[+]` Effetti visivi per meteo, interazioni.
        * g. `[]` Sprite/immagini per i diversi tipi di contenitori rifiuti e smaltitori automatici. `[NUOVO]`

    * 2. **Audio e Espressività Vocale NPC (Linguaggio Anthaliano):** `[]`
        * a. `[]` Sistema Audio Base (`pygame.mixer`), clip audio base in **Anthaliano**.
        * b. `[]` Voci "Uniche" per Personaggio.
        * c. `[]` Vocabolario Personalizzato (**Anthaliano**).
        * d. `[]` Tono di Voce / Espressione Emotiva Vocale (legata a umore).
        * e. `[+]` Sincronizzazione Audio.
        * f. `[]` Effetti Sonori Ambientali e UI.

**VII. INTERFACCIA UTENTE (UI)**
    * 1. Elementi GUI Esistenti: `[P]`
        * a. `[x]` `pygame_gui` panel, etichette (tempo, NPC, azione, età, gravidanza), pulsanti velocità (icone), barre bisogni manuali (7, 3 colonne, icone, gradienti), UI switch.
        * b. `[x]` Toggle per griglia debug e info NPC on-screen.
    * 2. Miglioramenti GUI Ispirati da `simai/election`: `[]` `[ELEC]`
        * a. `[+]` Visualizzazione statistiche avanzate con barre/grafici.
        * b. `[+]` Visualizzazione Info NPC più dettagliata.
        * c. `[+]` (Sandbox/Debug) Dashboard Interattivo "What-If".
        * d. `[+]` Visualizzazione Reti Sociali (grafo relazioni).
    * 3. `[+]` Miglioramenti Generali UI (Ritratti NPC, Notifiche, Tema personalizzato per **Anthalys**).
    * 4. `[]` **Interfaccia per Documento d'Identità e Servizi Correlati:** `[ESPANSIONE]`
        * a. `[]` Visualizzazione informazioni Documento d'Identità NPC selezionato.
        * b. `[+]` (Molto Avanzato) Simulazione "app ufficiale" per il titolare per accedere a dati completi (per osservazione/debug).
        * c. `[]` Sezione UI nell'app (o in una UI cittadino) per monitorare punti raccolta differenziata, riscattare bonus/sconti. `[NUOVO]`
        * d. `[+]` UI per gestire conti bancari associati al Documento d'Identità (se implementata economia dettagliata). `[NUOVO]`

**VIII. SISTEMA ECONOMICO, LAVORO E WELFARE DI ANTHALYS** (Nuova numerazione, ex Sezione VII)
    * 1. **Lavoro e Carriere per NPC:** `[]`
        * a. `[]` Definire tipi di lavoro e percorsi di carriera.
        * b. `[]` Implementare **Orario di Lavoro** (9h/giorno, 5gg/sett, 15 mesi lavoro/anno + 3 mesi pausa).
        * c. `[]` **Stipendi** (valuta "Athel" - AA, scale di stipendio). NPC ricevono stipendio.
        * d. `[]` IA NPC per cercare/ottenere/mantenere lavoro, promozioni.
        * e. `[]` Luoghi di lavoro fisici in Anthalys.
        * f. `[+]` Performance lavorativa.
        * g. `[+]` Licenziamento/dimissioni.
    * 2. **Sistema Fiscale di Anthalys:** `[]`
        * a. `[]` Tasse sul Reddito con scaglioni progressivi (max 24%-26%).
        * b. `[]` Esenzione fiscale per redditi < 3,000 AA.
        * c. `[]` Dichiarazione e raccolta tasse ogni 9 mesi di gioco.
    * 3. **Benefici e Sicurezza Sociale:** `[]`
        * a. `[]` **Assicurazione Sanitaria** (lavoratori, copertura basso reddito < 6,000 AA via **Istituti Fondine**).
        * b. `[]` **Sistema Pensionistico** (Base dopo 20 anni, Massima dopo 35 anni, tassazione pensione).
        * c. `[]` **Indennità di Maternità/Paternità**.
        * d. `[+]` **Sicurezza sul Lavoro** (narrativo o eventi).
    * 4. **Vacanze e Permessi Lavorativi:** `[]`
        * a. `[]` Vacanze Annuali pagate (24 giorni/anno lavorativo di Anthalys).
        * b. `[]` IA NPC per richiedere/usare vacanze.
        * c. `[]` Permessi per Malattia e Emergenze Familiari retribuiti.
    * 5. **Tassa sui Rifiuti e Incentivi Economici:** `[]` `[NUOVO]`
        * a. `[]` Implementare una tassa sui rifiuti per gli NPC/nuclei familiari.
        * b. `[]` Sconti sulla tassa dei rifiuti basati sui punti accumulati con la raccolta differenziata (500pt=5%, 1000pt=10%, 2000pt=20%).
        * c. `[]` Punti raccolta differenziata convertibili in buoni spesa (100pt=10AA, 200pt=25AA, 500pt=70AA).
        * d. `[+]` Incentivi per l'acquisto/noleggio di smaltitori automatici domestici.

**IX. ABILITÀ (SKILLS)** `[]` (Nuova numerazione, ex Sezione VIII)
    * a. `[]` NPC sviluppano abilità (Cucina, Manualità, Logica, Carisma, Pensiero Critico, ecc.).
    * b. `[+]` IA per scelta sviluppo abilità.
    * c. `[]` Abilità influenzano successo azioni, carriera, interazioni.

**X. EVENTI CASUALI E SCENARI GUIDATI** `[]` (Nuova numerazione, ex Sezione X)
    * a. `[]` Eventi casuali (positivi/negativi).
    * b. `[+]` IA NPC per reazione credibile agli eventi.
    * c. `[+]` Piccoli scenari o storie emergenti.
    * d. `[+]` Eventi legati alla gestione dei rifiuti o alla sostenibilità (es. "giornata ecologica", multe per errata differenziazione). `[NUOVO]`

**XI. DOCUMENTO DI IDENTITÀ DI ANTHALYS E SERVIZI INTEGRATI** `[]`
    * a. `[]` **Definizione Dati Documento:**
        * i.  `[]` Struttura dati per informazioni personali (Nome, data/luogo nascita, indirizzo, foto placeholder, CIP).
        * ii. `[]` Generazione **Codice Identificativo Personale (CIP)** univoco (`123.XXXX.YYYY.Z`).
    * b. `[]` **Integrazione nel Personaggio:** Ogni NPC riceve un CIP.
    * c. `[]` **Funzionalità Codice QR sul Documento (Simulazione):** `[ESPANSIONE]` `[ELEC]`
        * i.  `[]` **Accesso Base** (Scansione da dispositivi pubblici/non autorizzati): Nome, cognome, data/luogo nascita, CIP, date documento. Per verifiche di routine.
        * ii. `[]` **Accesso Completo** (Scansione da dispositivi autorizzati - es. Forze dell'Ordine, Sanitari): Dati biometrici (placeholder), indirizzo, stato civile, professione, dati medici rilevanti (placeholder), storico viaggi (placeholder), informazioni bancarie (placeholder). Per verifiche approfondite/emergenze.
    * d. `[+]` **Caratteristiche di Sicurezza del Documento (Simulazione Narrativa):** Microchip, ologrammi, inchiostro speciale, firma digitale, crittografia, autenticazione multifattoriale. `[ESPANSIONE]`
    * e. `[]` **Carta di Pagamento Integrata:** (Collegata a VIII) `[ESPANSIONE]` `[ELEC]`
        * i.  `[]` Documento come strumento per transazioni finanziarie.
        * ii. `[]` Pagamenti contactless (simulati).
        * iii.`[]` Programma a punti per pagamenti servizi pubblici (trasporti, bollette) con sconti/benefici.
        * iv. `[+]` Sicurezza pagamenti (autenticazione placeholder, PIN emergenza, blocco carta).
    * f. `[+]` **Accesso ai Dati Completi per il Titolare (Simulazione via "App Ufficiale"):** `[ESPANSIONE]` `[ELEC]`
        * i. `[+]` NPC (via IA) "usa" l'app per consultare/aggiornare (se possibile) alcuni dati (indirizzo, stato civile), visualizzare storico transazioni, gestire conti, monitorare punti raccolta differenziata, riscattare bonus.
        * ii.`[+]` UI per giocatore/osservatore per visualizzare questi dati completi per l'NPC selezionato.
    * g. `[]` **Utilizzo per Punti Raccolta Rifiuti:** Documento scansionato per tracciare conferimenti e accumulare punti (vedi XII.2). `[NUOVO]`

**XII. GESTIONE AMBIENTALE E CIVICA DI ANTHALYS** `[]` (**NUOVA SEZIONE**)
    * 1. **Sistema di Raccolta Differenziata Individuale:** `[]`
        * a. `[]` Definire **Tipi di Rifiuti** (Organico, Carta/Cartone, Plastica Bio, Vetro, Metalli, Elettronici, Speciali Naturali).
        * b. `[]` Implementare **Contenitori** specifici (con colori: Marrone, Blu, Giallo, Verde, Grigio, Rosso, Nero) per ogni tipo di rifiuto, disponibili per ogni nucleo familiare/lotto.
        * c. `[]` NPC generano tipi di rifiuti appropriati in base alle loro attività (es. scarti di cibo dopo aver mangiato, imballaggi dopo acquisti, vecchi gadget).
        * d. `[]` IA NPC per differenziare correttamente i rifiuti nei contenitori appositi.
        * e. `[+]` Conseguenze per errata differenziazione (mancato ritiro, multe, impatto sull'ambiente del lotto).
    * 2. **Sistema di Punti e Bonus per la Raccolta Differenziata:** `[]`
        * a. `[]` Assegnazione punti per corretta differenziazione (Organico/Carta/Vetro: 1pt/kg; Plastica: 2pt/kg; Metalli: 3pt/kg; Elettronici: 5pt/pezzo; Speciali: 3pt/pezzo). (Richiede simulazione "peso" o "quantità" rifiuti).
        * b. `[]` Implementazione Bonus e Incentivi (Sconti Tassa Rifiuti, Buoni Spesa, Premi Annuali "Cittadino Sostenibile", Gadget ecologici – vedi VIII.5).
        * c. `[]` (Spostato da VII.6.c) "Applicazione Mobile" (simulata tramite UI) per monitorare punti, riscattare bonus, notifiche raccolta.
    * 3. **Trattamento e Riutilizzo dei Rifiuti (Simulazione Alto Livello/Narrativa):** `[+]`
        * a. `[+]` Compostaggio da organico per agricoltura urbana/giardini.
        * b. `[+]` Digestione anaerobica per biogas.
        * c. `[+]` Riciclo effettivo di Carta, Plastica Bio, Vetro, Metalli, Elettronici.
        * d. `[+]` Trattamento specifico per rifiuti speciali.
        * e. `[+]` Impatto visibile o statistico del livello di riciclo della città di Anthalys.
    * 4. **Smaltitori Automatici Domestici:** `[]`
        * a. `[]` Definire tipi di smaltitori acquistabili/noleggiabili dagli NPC (Compostatori, Mini-Riciclatori Plastica/Vetro, Smaltitori Metalli).
        * b. `[]` Funzionamento: trasformano rifiuti in materiali riutilizzabili o compost a livello domestico.
        * c. `[]` Incentivi per acquisto/noleggio e uso (sconti, punti extra).
        * d. `[+]` Impatto sulla quantità di rifiuti prodotti dal nucleo familiare e sulla frequenza di uso dei punti di raccolta pubblici.

**XIII. SISTEMI TECNICI** `[P]`
    * 1. Salvataggio e Caricamento Partita: `[]` (**Priorità Alta**) (Dettagli come prima, includere dati Documento Identità e sistema rifiuti/punti). `[ELEC]`
    * 2. Opzioni di Gioco e Impostazioni: `[]` (Dettagli come prima).

**XIII. SISTEMI UNICI E AVANZATI (Idee Speciali per SimAI)** `[]` (Nuova numerazione, ex Sezione XIV)
    * a. `[+]` Riflessione Interna e "Filosofia di Vita" NPC.
    * b. `[+]` Cultura Emergente e Tradizioni di Anthalys.
    * c. `[+]` Linguaggio **Anthaliano** Dinamico/Evolutivo.
    * d. `[+]` IA "Regista di Storie" (Narrativa Emergente Guidata).
    * e. `[+]` Impatto Generazionale e Eredità NPC.
    * f. `[+]` Sogni e Subconscio NPC.

**XIV. INTEGRAZIONE FUNZIONALITÀ ISPIRATE DA `simai/election` (Ex Punto 5)** `[P]`
    * *(Questa sezione adatta e integra le idee dalla TODO list di `simai/election` nel contesto della simulazione di vita SimAI)*
    * **1. Modelli Comportamentali NPC Avanzati (Adattamento da "Modelli di Votanti"):** `[P]`
        * a. `[P]` Personalità Complesse e Tratti NPC (vedi III.3.d e IV.3). `[ELEC]`
        * b. `[]` **Bias Cognitivi nell'IA NPC:** `[ELEC]`
            * i.  `[]` Effetto Gregge/Controtendenza (NPC influenzati da popolarità di attività/luoghi).
            * ii. `[]` Bias di Conferma (NPC cercano informazioni/interazioni che confermano le loro "convinzioni" o preferenze).
            * iii.`[]` Ragionamento Motivato (NPC interpretano eventi o azioni altrui in modo da proteggere relazioni esistenti o autostima).
            * iv. `[+]` Altri Bias (es. Hindsight Bias nelle riflessioni su eventi passati).
        * c. `[]` **Decisioni Basate su Identità/Valori vs. Bisogni Immediati** (vedi III.3.e). `[ELEC]`
        * d. `[P]` **Influenza delle Reti Sociali Esplicite** (vedi IV.2.b - il grafo sociale e la diffusione di umore/opinioni/linguaggio sono una forma di questo). `[ELEC]`
        * e. `[]` **"Alfabetizzazione" Sociale/Emotiva e Pensiero Critico NPC:** (Adattamento di Alfabetizzazione Mediatica) `[ELEC]`
            * i.  `[]` Attributo che influenza come un NPC interpreta interazioni sociali complesse, pettegolezzi, o "notizie" del mondo di gioco (se implementate).
            * ii. `[]` Influenza la suscettibilità a manipolazioni sociali o a fraintendimenti.
        * f. `[+]` **Apprendimento e Adattamento Comportamentale Avanzato:** (Adattamento di Apprendimento Agenti Elettori - vedi III.3.j) `[ELEC]`
            * i. `[+]` NPC modificano l'importanza relativa dei loro bisogni, obiettivi, o preferenze di interazione in base a esperienze positive/negative.
    * **2. Miglioramenti alla Simulazione del "Mondo Vivo":** `[P]`
        * a. `[]` **Interazioni NPC-Oggetto più Complesse e Tematiche:** (Adattamento da "Simulazione Campagna") `[ELEC]`
            * i. `[]` Introduzione di "progetti personali" o attività a lungo termine che richiedono budget di tempo/energia/denaro (se implementato) e hanno "temi" (es. imparare un'abilità, scrivere un libro, organizzare una festa).
            * ii.`[+]` Eventi specifici generati dagli NPC (es. organizzare un raduno, una mostra d'arte amatoriale).
        * b. `[]` **Eventi Casuali e Dinamiche del Mondo di Anthalys:** (Adattamento da "Eventi Casuali" e "Generazione Dinamica Eventi/Notizie") `[ELEC]`
            * i. `[P]` Eventi casuali base (già in TODO SimAI).
            * ii.`[+]` Eventi influenzati da uno "stato del mondo" o "argomento caldo" in Anthalys (es. una nuova moda, un problema cittadino).
            * iii.`[+]` Modellare "fonti di informazione" fittizie in Anthalys (giornali locali, social media simulati) con possibili bias, che influenzano la conoscenza e l'umore degli NPC in base al loro Pensiero Critico.
        * c. `[+]` **Sistemi di "Voto" o Scelta Collettiva per NPC (Molto Avanzato):** (Adattamento da "Sistemi Elettorali") `[ELEC]`
            * i. `[+]` Se si formano gruppi, potrebbero "votare" per attività di gruppo o decisioni comunitarie minori.
        * d. `[+]` **Generazione NPC Più Profonda:** (Adattamento da "Generazione Candidati Migliorata") `[ELEC]`
            * i. `[+]` NPC generati con background, relazioni iniziali, e un set di tratti/valori più coerenti e unici.
    * **3. Strategie Comportamentali Dinamiche NPC (Adattamento da "Strategie di Campagna"):** `[P]` (vedi anche III.3.e) `[ELEC]`
        * a. `[+]` NPC "targettizzano" specifici altri NPC per interazioni sociali/romantiche basate su relazioni, tratti, e obiettivi.
        * b. `[+]` NPC scelgono temi di conversazione o attività di gruppo in modo strategico.
        * c. `[+]` NPC adattano le loro strategie sociali/obiettivo se incontrano fallimenti o successi ripetuti.
    * **4. Generazione di Contenuti Testuali (NLG) per SimAI:** `[]` `[ELEC]`
        * a. `[]` "Pensieri" o "voci di diario" testuali più variati per gli NPC.
        * b. `[+]` Generazione di "notizie" fittizie o "post social media" all'interno del mondo di Anthalys (se implementate fonti media).
        * c. `[+]` Migliorare la varietà del linguaggio **Anthaliano** parlato (se rappresentato testualmente o con più suoni).
    * **5. Principi di Progettazione e Validazione per SimAI:** `[]` (Adattamento da "Integrazione Dati, Parametrizzazione e Validazione") `[ELEC]`
        * a. `[+]` Basare alcuni parametri NPC (es. distribuzione tratti, tassi bisogni medi) su concetti psicologici/sociologici semplificati.
        * b. `[]` Calibrazione attenta dei parametri di gioco per bilanciamento.
        * c. `[]` Validazione multi-sfaccettata del comportamento emergente degli NPC.
    * **6. IA e LLM (Obiettivi a Lungo Termine per SimAI):** `[+]` (Adattamento da "IA e LLM") `[ELEC]`
        * a. `[+]` Esplorare uso di LLM per arricchire dialoghi, pensieri NPC, generazione eventi.
    * **7. Persistenza Dati NPC Avanzata (Database):** `[P]` (Vedi anche VIII.1) `[ELEC]`
        * a. `[]` Utilizzare SQLite (o simile) per una persistenza robusta degli NPC e del mondo di gioco.
        * b. `[]` Ogni NPC (generato o nato nel gioco) ha un UUID.
        * c. `[]` Memorizzare tratti, valori, abilità, relazioni, età, stato gravidanza, storia personale significativa.
        * d. `[+]` Memorizzare statistiche aggregate per la vita di ogni NPC.

**XV. SISTEMA SCOLASTICO DI ANTHALYS** `[]` (**NUOVA SEZIONE DETTAGLIATA**)
    * 1. **Struttura e Calendario Scolastico:** `[]`
        * a. `[]` Definire 8 Livelli Scolastici (Infanzia, Elementari Inf/Sup, Medie Inf/Sup, Superiori Obbligatorie, Superior Facoltativo, Università) con fasce d'età corrispondenti.
        * b. `[]` Implementare Anno Scolastico (18 mesi di gioco totali):
            * i.  `[]` Inizio Anno: giorno 13/mese 13.
            * ii. `[]` Fine Anno: giorno 12/mese 9.
            * iii.`[]` Durata: 324 giorni di attività didattica.
        * c. `[]` Implementare Pause Scolastiche:
            * i.  `[]` Pausa Primaverile: 12 giorni (01/5 - 12/5).
            * ii. `[]` Pausa Estiva: 72 giorni (13/9 - 12/13).
    * 2. **Curriculum e Materie per Livello:** `[]`
        * a. `[]` **Infanzia (1-3 anni):** Sviluppo motorio/sociale/linguistico, gioco, introduzione colori/numeri/lettere, socializzazione, **Anthaliano** moderno base.
        * b. `[]` **Elementari Inferiori (4-6 anni):** Alfabetizzazione base, matematica base, scienze naturali intro, attività artistiche, **Anthaliano** moderno, **Inglese**.
        * c. `[]` **Elementari Superiori (7-9 anni):** Lettura/scrittura avanzate, matematica (x, /, frazioni), scienze naturali/sociali (storia/geografia intro), arti/musica, ed. fisica, **Anthaliano** moderno/antico base, **Inglese**.
        * d. `[]` **Medie Inferiori (10-12 anni):** Letteratura/grammatica, matematica (algebra/geometria base), scienze (bio/chim/fis intro), storia/geografia, ed. tecnologica/informatica base, ed. fisica, **Anthaliano** moderno/antico base, **Inglese**.
        * e. `[]` **Medie Superiori (13-15 anni):** Letteratura/composizione, matematica avanzata (algebra/trigo/calcolo intro), scienze avanzate, studi sociali (storia mod/cont, economia, diritto), lingue straniere avanzate (**Anthaliano** antico, **Inglese**), ed. tecnologica/informatica avanzata, ed. fisica, arti/musica avanzate.
        * f. `[]` **Superiori (16-18 anni, obbligatorio):** Letteratura/scrittura avanzata, matematica superiore, scienze avanzate, scienze sociali avanzate, ed. civica/diritto, ed. tecnologica/informatica avanzata, progetti di ricerca obbligatori, preparazione carriera/orientamento, **Anthaliano** moderno/antico avanzato, **Inglese**.
        * g. `[]` **Superior Facoltativo (19-21 anni, pre-universitaria):** Materie di specializzazione, ricerca avanzata, stage/tirocini, orientamento universitario, perfezionamento lingue.
        * h. `[]` **Università (21+ anni):**
            * i.  `[]` Definire struttura (Laurea Triennale 3 anni, Magistrale 5 anni, Dottorato 7 anni).
            * ii. `[]` Definire esempi di Facoltà e Specializzazioni (Scienze/Tecnologia, Arti/Lettere, Economia/Gestione, Ingegneria, Medicina/Scienze Salute con relative materie).
            * iii.`[+]` Programmi di scambio e collaborazione internazionale (narrativo o eventi).
            * iv. `[]` Lingue di istruzione: **Anthaliano** moderno/antico, **Inglese**.
    * 3. **Meccaniche Scolastiche per NPC:** `[]`
        * a. `[]` NPC bambini/adolescenti frequentano automaticamente la scuola appropriata durante l'orario scolastico (escono di casa, "vanno" al lotto scuola - se esiste - o scompaiono per la durata delle lezioni).
        * b. `[]` Performance scolastica (voti, compiti a casa placeholder) influenzata da umore, bisogni, tratti, abilità.
        * c. `[+]` Impatto della performance scolastica su sviluppo abilità, aspirazioni, opportunità future (lavoro, università).
        * d. `[+]` Possibilità di "saltare la scuola" con conseguenze.
        * e. `[+]` Attività extracurriculari e viaggi educativi durante le pause.
        * f. `[+]` Supporto studenti (orientamento, tutoraggio - simulato tramite IA o eventi).

---