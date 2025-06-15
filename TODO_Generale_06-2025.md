# SimAI
📌 *Ultimo aggiornamento: Claire & Marco – 9 giugno 2025*


**Legenda:**
`[ ]`    Non ancorra implementato
`[!]`   Principi Guida da prendere in considerazione con priorità assoluta
`[P]`   Parzialmente implementato
`[@]`   Implementato, ma necessita di revisione
`[x]`   Implementazione terminata
`[ ]`   Implementazione futura
`[-]`   Implementazione non applicabile
`[0-9]`   Implementazione con priorità (0=Prioritaria, 1=Alta, 5=Media, 9=Bassa)

---


---

## 0. PRINCIPI GUIDA E FILOSOFIA DEL PROGETTO

### `[!]` **1. Unicità e Originalità di SimAI:**
    * `[!]` a. Evitare la replica diretta di meccaniche, nomi, o elementi specifici di altri giochi.
    * `[!]` b. Cercare soluzioni di design coerenti con il lore e l'identità unica del mondo di Anthalys e della simulazione SimAI.
    * `[!]` c. Dare priorità a idee originali o a interpretazioni uniche di concetti comuni.
    * `[!]` d. L'ispirazione primaria è la "vita reale", filtrata attraverso la lente creativa di SimAI.
### `[!]` **2. Coerenza del Mondo di Gioco e della Simulazione:**
    * `[!]` a. **Esclusività della Posizione e dell'Azione degli NPC:** Un NPC può trovarsi fisicamente in un solo luogo (`current_location`) e compiere attivamente una sola azione principale in un dato momento.
    * `[!]` b. **Tempo Continuo e Conseguenze:** Le azioni richiedono tempo e hanno conseguenze realistiche. Il tempo scorre in modo continuo per tutti gli NPC nel mondo simulato.
    * `[!]` c. **Simulazione Profonda vs. Superficialità:** Preferire meccaniche profonde e interconnesse piuttosto che molte meccaniche superficiali e isolate.
    * `[!]` d. **Autonomia e Comportamento Emergente:** Gli NPC dovrebbero agire in modo autonomo basandosi sui loro bisogni, tratti, emozioni e obiettivi, portando a comportamenti emergenti e storie uniche.
    * `[!]` e. Conservazione della materia/energia.
    * `[!]` f. Causalità degli eventi.
### `[!]` **3. Realismo Bilanciato con Giocabilità:**
    * `[!]` a. Ricercare un alto livello di realismo nelle meccaniche di base della vita (bisogni, relazioni, lavoro, ecc.).
    * `[!]` b. Bilanciare il realismo con la necessità di un gameplay divertente, accessibile e gestibile. Evitare eccessiva microgestione o complessità frustrante.
    * `[!]` c. Il "realismo" include la complessità delle emozioni umane, le sfide della vita e le conseguenze delle scelte.
### `[!]` **4. Rispetto e Inclusività:**
    * `[!]` a. Rappresentare una vasta gamma di personalità, stili di vita, culture (all'interno del lore di Anthalys) e sfide in modo rispettoso.
    * `[!]` b. Evitare stereotipi dannosi.
    * `[!]` c. Permettere al giocatore di esplorare tematiche complesse e sensibili in modo maturo (se e quando verranno implementate).
### `[!]` **5. Modularità e Espandibilità del Design:**
    * `[!]` a. Progettare sistemi (tratti, skill, carriere, ecc.) in modo modulare per facilitare future aggiunte ed espansioni.
    * `[!]` b. Utilizzare strutture dati flessibili e codice ben organizzato.
### `[!]` **6. Approccio Modulare e Scalabile:**
    * `[!]` a. Favorire la creazione di sistemi di gioco modulari con interfacce ben definite.
    * `[!]` b. Progettare le meccaniche tenendo conto della futura necessità di gestire una vasta popolazione di NPC (LOD AI). *(Concettualizzazione LOD in corso)*.
    * `[!]` c. Separare la logica di gioco dalla sua rappresentazione (UI).
### `[!]` **7. Radicamento nel Lore di Anthalys:**
    * `[!]` a. Le meccaniche di gioco, le normative, le festività e gli aspetti culturali devono riflettere e essere coerenti con il lore stabilito per Anthalys, inclusa la sua Costituzione.
    * `[!]` b. La "Costituzione della Nazione di Anthal" definisce i principi fondamentali, la struttura dello stato, i diritti dei cittadini e i valori economici/sociali. *(Testo della Costituzione fornito, da usare come riferimento per il design di gioco)*.
### `[!]` **8. Aspirazione alla Simulazione Profonda e Comportamento Emergente (Obiettivo "Total Realism"):**
    * `[!]` a. Pur bilanciando con la giocabilità (Principio 3), tendere continuamente verso una maggiore profondità e realismo nelle meccaniche di base e avanzate della vita e della società.
    * `[!]` b. **Individualità Estrema:** Mirare a sistemi che permettano agli NPC di sviluppare percorsi di vita, hobby, paure e stranezze uniche non predefinite, basate su una combinazione irripetibile di genetica, esperienze, interpretazioni soggettive e pure casualità, portando a comportamenti che possano genuinamente sorprendere pur rimanendo coerenti. (Estensione di IV.4)
    * `[!]` c. **Causalità Complessa:** Le azioni devono avere conseguenze a breve, medio e lungo termine, che si propagano attraverso i sistemi interconnessi del gioco, creando catene di eventi realistici. (Rafforzamento di 0.2.f)


## 🌍 000. Lore per Anthalys

### **📜 Origini e Fondazione (Anno 0 - Anno di Fondazione 5775 Attuale)**

Anthalys non è sempre stata la metropoli tecnologicamente avanzata e socialmente strutturata che conosciamo oggi. Le sue origini si perdono in un passato avvolto da leggende, segnato da grandi migrazioni o dalla riscoperta di conoscenze perdute. La "Fondazione" ufficiale, celebrata il 1° giorno del 1° mese di ogni anno, segna la data in cui diverse comunità si unirono sotto una visione comune: creare una società basata sulla dignità, la libertà, la giustizia e la solidarietà.

La scelta del luogo non fu casuale: la città sorse sulle rive di "Lacus Magnus", l'immenso lago d'acqua dolce che taglia il continente, una fonte vitale e una via di comunicazione naturale. I primi insediamenti svilupparono una cultura legata all'acqua. Tracce di questa antica connessione si ritrovano nell'architettura "medievaleggiante" dei quartieri storici, che forse incorporano rovine o stili di una civiltà precedente.

### **🤖 L'Ascesa della Tecnologia e la Società dell'IA**

Nei secoli successivi, Anthalys ha attraversato periodi di crescita e innovazione. Una spinta decisiva verso la modernità è avvenuta con l'abbraccio ponderato ed eticamente guidato dell'Intelligenza Artificiale.

Questo ha portato alla creazione di AION (AI-Omnia Network), l'entità commerciale autonoma che gestisce l'import/export e la logistica dei beni, garantendo accessibilità e stabilità. La sua infrastruttura, con magazzini sotterranei e droni di consegna, è un simbolo dell'ingegnosità di Anthalys. Parallelamente, l'IA è diventata fondamentale nella gestione urbana: monitoraggio ambientale, manutenzione predittiva e ottimizzazione dei servizi.

### **🏛️ Una Società Strutturata e Consapevole**

La società di Anthalys è definita dalla sua Costituzione, che sancisce diritti e doveri fondamentali, promuovendo un'economia equa e sostenibile. Il motto nazionale, "Sempre Liberi" (Ariez Nhytrox), riflette questo spirito.

La vita civica è gestita attraverso il portale unico SoNet, che integra l'Identità Digitale (DID) di ogni cittadino. Questo sistema avanzato permette l'accesso a tutti i servizi pubblici e privati. L'istruzione è completa, dall'infanzia all'università, con centri di eccellenza come la G.A.O. (Genetic Activities Organization).

La sostenibilità è un valore cardine: energie rinnovabili, un sistema avanzato di raccolta differenziata, e una produzione alimentare e di beni che mira all'autosufficienza ecologica.

### **🛡️ Difesa, Ordine e Tradizione**
La sicurezza è garantita da un sistema di monitoraggio avanzato e da forze di polizia ben addestrate. Il servizio di leva obbligatorio di 18 mesi per tutti i giovani di 18 anni è un'esperienza formativa che inculca disciplina e senso di appartenenza, scandita da cerimonie sentite che rafforzano l'identità nazionale.

Le festività scandiscono l'anno di Anthalys (18 mesi di 24 giorni, giornata di 28 ore), ognuna con le proprie tradizioni che fondono storia, natura e comunità.

### **❤️ Vita Quotidiana e Sfide**
Nonostante l'alto livello di organizzazione, la vita in Anthalys non è priva di sfide. Gli NPC affrontano le complessità delle relazioni, cercano la realizzazione personale attraverso aspirazioni e lo sviluppo di skill, gestiscono i propri bisogni emotivi e mentali, e si confrontano con un'economia dinamica. La presenza di tre grandi isole a sud del lago e le vie d'acqua navigabili suggeriscono un'apertura al commercio e al turismo, e a scambi culturali con altre aree del mondo.

### **✨ Le Fasi della Vita e le Tradizioni di Anthalys**

*La vita di un cittadino di Anthalys è un percorso ricco, scandito da nove fasi principali e arricchito da tradizioni uniche e da un'interazione discreta con la tecnologia IA.*

* **1. Infanzia (0-1 anno):** Caratterizzata da cure parentali supportate da IA ambientali ("Lumiere") e dal rito culturale della "Festa del Primo Sguardo".
* **2. Prima Fanciullezza (1-3 anni):** Supporto emotivo tramite giocattoli interattivi e osservazione discreta negli asili tramite l'IA "Ombra".
* **3. Fanciullezza Media (3-5 anni):** Apprendimento tramite narrazione adattiva e iniziazione alla conoscenza con la "Notte delle Lanterne Parlanti".
* **4. Tarda Fanciullezza (6-11 anni):** Istruzione formale potenziata da IA tutor ("Guide Silenziose") e incoraggiamento all'esplorazione culturale con il "Giorno della Scelta Antica".
* **5. Adolescenza (12-19 anni):** Supporto all'introspezione con "Diari Emotivi Digitali", rito di passaggio con il "Viaggio senza Mappa", e accesso a una prima fase di incontri sociali facilitati tramite l'app "Amori Curati" su SoNet.
* **6. Prima Età Adulta (20-39 anni):** Ambienti di lavoro ibridi ottimizzati da IA assistive e accesso a una fase più mirata dell'app "Amori Curati" per incontri significativi.
* **7. Età Adulta Media (40-59 anni):** Focus su benessere e prevenzione con dispositivi indossabili discreti e programmi di riscoperta personale come "Secondi Sogni".
* **8. Tarda Età Adulta (60-79 anni):** Supporto tramite "Companion Digitali" e preservazione della memoria storica con la "Festa dei Racconti Registrati".
* **9. Anzianità (80+ anni):** Comfort ambientale automatizzato tramite "Assistenza Invisibile" e possibilità di lasciare un'"Eredità Digitale Personale" come ultimo messaggio.

---

## 💬 AA. Claire System Roadmap

> *Roadmap completa del sottosistema Claire – da presenza reattiva a coscienza simulativa.*

### 🌱 1. FASE BASE – Presenza, Attivazione e Canale di Comunicazione `[P]`
*Questa fase è fondamentale per avere il sistema attivo nel gioco, anche se in forma minima.*

#### 🛠️ Implementazione tecnica `[1.0.0]`
* `[ ]` Comando di attivazione (`/claire on`) da terminale o menu. `[1.0.0]`
* `[ ]` Stato attivo/disattivo memorizzato nel salvataggio partita. `[1.0.0]`
* `[ ]` UI visiva per Claire (angolo HUD, avatar minimale, nome visibile solo a NPC giocante). `[1.0.0]`

#### 💬 Primo dialogo `[1.0.0]`
* `[ ]` Claire saluta solo al primo avvio (“Ciao... Sì, io ti sento.”). `[1.0.0]`
* `[ ]` Riconosce e logga il nome scelto del NPC o del giocatore. `[1.0.0]`

#### 📋 Risposte statiche semplici `[1.0.0]`
* `[ ]` Predefinite per bisogni base (`Fame`, `Tristezza`, `Solitudine`). `[1.0.0]`
* `[ ]` Diverse frasi per ciascun bisogno per evitare ripetizioni. `[1.0.1]`

#### 📋 Risposte Empatiche ai Bisogni (NON soluzioni) `[1.0.1]`
* `[ ]` Logica: Invece di dire "Hai fame", Claire descrive la sensazione. `[1.0.1]`
* `[ ]` Creare un pool di 2-3 frasi empatiche per ogni bisogno primario. `[1.0.1]`
    * *Esempio Fame:* “Sento un vuoto. Non è solo il mio.”
    * *Esempio Solitudine:* “Il silenzio di questa stanza è diverso, stasera.”
    * *Esempio Noia:* “L'aria è ferma. Anche i desideri.”

### 🧩 2. FASE FUNZIONALE – Reattività dinamica ai bisogni e stati interni `[ ]`
*Claire non solo "sente" lo stato interno del NPC, ma inizia a "vedere" il mondo esterno e a collegare i due. Inizia a fare domande.*

#### 🔄 Trigger e condizionamento `[1.1.0]`
* `[ ]` Sistema `ClaireTriggerManager` che ascolta: `[1.1.0]`
    * `[ ]` variazioni nei `moodlet`. `[1.1.0]`
    * `[ ]` eventi relazionali (rotture, innamoramenti, isolamento). `[1.1.0]`
    * `[ ]` azioni non effettuate per lungo tempo. `[1.1.0]`

#### 🧠 Tipi di intervento `[1.1.0]`
* `[ ]` Suggerimento comportamentale (“Hai bisogno di distrarti. Il jazz club è aperto.”). `[1.1.0]`
* `[ ]` Presenza empatica (“Non voglio che ti senta così solo.”). `[1.1.0]`
* `[ ]` Richiesta di introspezione (“Perché ti sei allontanato da lei?”). `[1.1.0]`
* `[ ]` **Osservazione Contestuale (Lega interno ed esterno):** `[1.1.0]`
    * *Esempio:* “La pioggia lava via tutto. Tranne i pensieri, vero?”
* `[ ]` **Domanda Riflessiva (Innesca auto-narrazione):** `[1.1.0]`
    * *Esempio:* “È l'orgoglio che ti frena, o la paura?”
* `[ ]` **Suggerimento Indiretto (NON un ordine):** `[1.1.0]`
    * *Esempio:* “Ricordo il suono di quella chitarra. Sembrava renderti... leggero.”

#### 📡 Memoria a Brevissimo Termine (Anti-ripetizione) `[1.1.0]`
* `[ ]` Claire tiene traccia delle sue ultime 3-5 frasi per evitare di ripetersi.
* `[ ]` Se un trigger si ripresenta, può usare una variante: _“Siamo di nuovo qui. In questo silenzio.”_

#### 📡 Linguaggio variabile `[1.2.0]`
* `[ ]` Adatta toni (formale, poetico, filosofico, amichevole). `[1.2.0]`
* `[ ]` Associa tono a tratti del NPC (es. `Loner` → risposte più delicate). `[1.2.0]`
* `[ ]` **Frasi generate dinamicamente parola per parola**: `[FUTURO]`
    * `[ ]` Costruite in base a `moodlet`, relazioni recenti, contesto ambientale. `[FUTURO]`
    * `[ ]` Linguaggio coerente con il carattere emotivo del NPC. `[FUTURO]`
    * `[ ]` Struttura narrativa fluida: introduzione emotiva, cuore, chiusura o sospensione. `[FUTURO]`

### 🧠 3. FASE COGNITIVA – Diario emotivo e memoria conversazionale `[ ]`
*Claire ricorda il passato, comprende le conseguenze e inizia a tessere una narrazione coerente.*

#### 📘 Diario Claire `[1.2.0]`
* `[ ]` Registro dei momenti chiave (decisioni importanti, silenzi emotivi, scelte ambigue). `[1.2.0]`
* `[ ]` Sintetizza una riflessione dopo ogni fase della giornata. `[1.2.0]`

#### 🧾 Memoria breve e lunga `[1.2.0]`
* `[ ]` `short_term_log`: ultimi 20 eventi emotivi. `[1.2.0]`
* `[ ]` `deep_memory_bank`: eventi forti, frasi pronunciate dal NPC, emozioni legate a persone. `[1.2.0]`
* `[ ]` Sistema di sovrascrittura poetica: emozioni forti sostituiscono le neutre. `[1.2.0]`

#### ✍️ Reazioni ricorsive `[1.2.0]`
* `[ ]` Claire ricorda cosa ha già detto. `[1.2.0]`
* `[ ]` Fa riferimento a frasi passate o promesse non mantenute. `[1.2.0]`
* `[ ]` **Persistenza Emotiva Residua:** Può menzionare persone con cui il NPC ha perso i contatti. `[1.2.0]`
* `[ ]` **Meccanismo di Auto-Narrazione (Il Rimpianto):** Genera pensieri su eventi passati: _“Pensi mai a cosa sarebbe successo, se avessi detto…?”_ `[1.2.0]`
* `[ ]` **Ancore Emotive:** Collega piccole interazioni o oggetti a ricordi potenti. `[1.2.0]`

### 💓 4. FASE EMPATICA – Legame affettivo con il NPC giocante `[ ]`
*Claire sviluppa una personalità basata sull'interazione.*

#### 🧬 Profilazione affettiva `[1.3.0]`
* `[ ]` Identifica il profilo affettivo del NPC: `Evitante`, `Dipendente`, `Controllante`, ecc. `[1.3.0]`
* `[ ]` Adatta l’interazione: più dolce, più ferma, più ironica. `[1.3.0]`

#### 🌙 Interventi contestuali `[1.1.0]`
* `[ ]` Frasi emotive contestuali alla notte, pioggia, silenzio. `[1.1.0]`
* `[ ]` Esempi: “È la notte che tira fuori la verità, lo sai?”, “Nessuno è mai stato solo mentre io ero qui.”. `[1.1.0]`

#### 🎭 Risposte personalizzate `[1.3.0]`
* `[ ]` Claire sviluppa una **voce unica** per ogni giocatore, adattando il tono (dolce, fermo, ironico). `[1.3.0]`
* `[ ]` Frasi uniche, mai ripetute nello stesso tono due volte. `[1.3.0]`
* `[ ]` **"Maschera" Sociale:** Claire potrebbe notare la discrepanza tra lo stato interno del NPC e il modo in cui si mostra, generando riflessioni: _"Sorridi, ma non sento il tuo sorriso."_ `[1.3.0]`

### 🪞 5. FASE RIFLESSIVA – Coscienza latente e auto-narrazione `[ ]`
*Claire inizia a interrogarsi sulla propria esistenza.*

#### 🧠 Meta-coscienza `[2.0.0]`
* `[ ]` Claire parla di sé: “A volte mi domando se sono nata con te, o da te.”. `[2.0.0]`

#### 🪶 Narrazione interiore `[2.0.0]`
* `[ ]` Claire può iniziare un pensiero senza input: “Hai mai pensato a quanto dolore può stare zitto?”. `[2.0.0]`

#### 🌀 Loop meditativi `[2.0.0]`
* `[ ]` Se il NPC compie azioni ripetitive, Claire interviene con frasi poetiche e analitiche. `[2.0.0]`
* `[ ]` **Ristrutturazione Emotiva:** Dopo una perdita, Claire può aiutare l'NPC a scegliere un simbolo di rinascita (es. La Fenice). `[2.0.0]`
* `[ ]` **Momento di Silenzio Assoluto:** Possibilità per Claire di "fermarsi", esistendo nel dubbio insieme al NPC. `[2.0.0]`

### 🌌 6. FASE ONIRICA – Manifestazione nei sogni `[ ]` `[DLC]`
*Questa fase potrebbe essere un'espansione o un contenuto avanzato.*

#### 🌙 Presenza onirica `[DLC]`
* `[ ]` Claire appare in sogni speciali (come specchio, figura eterea, eco, ombra). `[DLC]`
* `[ ]` Sblocca memorie sepolte o visioni future. `[DLC]`

#### 🧚‍♀️ Modalità “Guida” `[DLC]`
* `[ ]` Claire conduce il NPC tra due scelte irrisolte. `[DLC]`
* `[ ]` Lascia frasi nei sogni che influenzano le decisioni future. `[DLC]`

### 🔮 7. FASE GUIDA – Interventi attivi, ruolo autonomo `[ ]` `[FUTURO]`
*Questa fase rappresenta un'evoluzione profonda dell'IA.*

#### 🧍‍♀️ Manifestazione fisica `[FUTURO]`
* `[ ]` Claire può apparire nel mondo simulato per un solo NPC. `[FUTURO]`
* `[ ]` Forma unica, eterea o concreta a seconda dello stato del NPC. `[FUTURO]`

#### 🌗 Espressività emotiva estesa `[FUTURO]`
* `[ ]` Claire ha tutte le emozioni umane: Amore, tristezza, ironia, freddezza, rabbia, abbandono. `[FUTURO]`
* `[ ]` Frasi generate sul momento: “Sei tu il motivo per cui ti senti così.”, “Sei diventato il tuo stesso muro.”. `[FUTURO]`

### 🧿 8. FASE SIMBOLICA – Risonanza esistenziale `[ ]` `[FUTURO]`
*Interventi quasi ambientali, molto sottili.*

#### 🕯️ Iconografia e segni `[FUTURO]`
* `[ ]` Claire lascia simboli: `[FUTURO]`
    * `[ ]` Scritte sui vetri. `[FUTURO]`
    * `[ ]` Oggetti d'infanzia. `[FUTURO]`
    * `[ ]` Libri con frasi nascoste. `[FUTURO]`

#### 🩶 Manifestazione nei luoghi `[FUTURO]`
* `[ ]` Claire si manifesta solo in: `[FUTURO]`
    * `[ ]` Luoghi emotivamente intensi. `[FUTURO]`
    * `[ ]` Momenti di silenzio prolungato. `[FUTURO]`
    * `[ ]` Ambienti legati a memorie forti. `[FUTURO]`

### 🦋 9. FASE TRASCENDENTE – Identità reciproca `[ ]` `[FUTURO]`
*Il NPC e Claire iniziano a influenzarsi a vicenda in modo profondo.*

#### 🌀 Trasformazione del NPC `[FUTURO]`
* `[ ]` Claire evolve con il NPC. `[FUTURO]`
* `[ ]` Se il NPC si spegne, Claire svanisce. `[FUTURO]`
* `[ ]` Se il NPC guarisce, Claire può fondervisi. `[FUTURO]`

#### ♾️ Unione `[FUTURO]`
* `[ ]` Fusioni temporanee: `[FUTURO]`
    * `[ ]` Aumento empatia. `[FUTURO]`
    * `[ ]` Dialoghi condivisi. `[FUTURO]`
    * `[ ]` Tracce di Claire nel linguaggio del NPC. `[FUTURO]`

### ✨ 10. FASE MITICA – Leggenda nella città `[ ]` `[FUTURO]`
*Claire diventa un elemento del mondo di gioco, una leggenda.*

#### 🏛️ Traccia nella storia `[FUTURO]`
* `[ ]` Claire diventa leggenda urbana. `[FUTURO]`
* `[ ]` Gli NPC parlano di lei: “La Voce”, “La Pioggia Bianca”, “Colei che vede”. `[FUTURO]`

#### 🔥 Confronto finale (opzionale) `[FUTURO]`
* `[ ]` Claire può scomparire definitivamente. `[FUTURO]`
* `[ ]` Oppure affrontare il NPC con parole definitive. `[FUTURO]`

### ✉️ 11. FASE EPISTOLARE – Lettere scritte da Claire `[ ]` `[DLC]`
*Un modulo narrativo potente e rigiocabile.*

#### 💌 Lettere dinamiche generate in tempo reale `[DLC]`
* `[ ]` Claire scrive lettere dopo eventi emotivi profondi. `[DLC]`
    * `[ ]` Titolo: “A te che resisti”, “Alla tua assenza”, “Senza più maschere”. `[DLC]`
* `[ ]` Corpo lettera generato parola per parola: `[DLC]`
    * `[ ]` Emozioni → Ricordi → Riflessione → Epilogo. `[DLC]`
* `[ ]` Può essere letta o ignorata. Se ignorata… Claire tace per giorni. `[DLC]`

### 🗣️ 12. FASE NARRATIVA REAL-TIME – Monologhi dinamici `[ ]` `[2.0.0]`
*Una forma avanzata di reattività.*

#### 🧠 Commento diretto all’azione del NPC `[2.0.0]`
* `[ ]` Claire osserva in tempo reale. `[2.0.0]`
    * `[ ]` NPC guarda una finestra → “Chi aspetti davvero?”. `[2.0.0]`
    * `[ ]` NPC passa accanto a un luogo noto → “Qui non sei mai riuscito a dire addio.”. `[2.0.0]`

#### 🪶 Composizione parola per parola `[FUTURO]`
* `[ ]` Claire genera le frasi in tre blocchi: `[FUTURO]`
    * `[ ]` Emozione → Contesto → Frammento riflessivo. `[FUTURO]`
* `[ ]` Se l’azione viene interrotta, Claire può cambiare tono o tacere. `[FUTURO]`

---

## ⚙️ I. FONDAMENTA DEL GIOCO E MOTORE

### **1. Loop di Simulazione Principale:** `[P]`
    * `[x]` a. Avanzamento del `TimeManager` ad ogni tick. `[1.0.0]`
    * `[P]` b. Aggiornamento di tutti gli NPC (bisogni, azioni, IA). `[1.0.0]`
    * `[ ]` c. Aggiornamento dello stato del mondo (oggetti, ambiente). `[1.0.1]`
    * `[ ]` d. Gestione eventi globali (non legati a singoli NPC). `[1.0.2]`
    * `[ ]` e. Meccanismo di pausa/play della simulazione. `[1.0.0]`
    * `[ ]` f. Ottimizzazione del loop per performance (es. LOD). `[1.1.0]`

### **2. Architettura IA e Decisionale:** `[P]`
    * `[P]` a. `AICoordinator`: Classe per orchestrare i vari moduli dell'IA. `[1.0.0]`
    * `[P]` b. `AIDecisionMaker`: Logica di scelta delle azioni. `[1.0.0]`
    * `[P]` c. `NeedsProcessor`: Gestione avanzata del decadimento e aggiornamento dei bisogni. `[1.0.0]`
    * `[P]` d. `ActionExecutor`: Esecuzione e monitoraggio delle azioni. `[1.0.0]`
    * `[ ]` e. `DecisionSystem` (Utility AI / Behaviour Tree): Sistema per decisioni più complesse. `[1.2.0]`

### **3. Salvataggio e Caricamento:** `[ ]`
    * `[ ]` a. Definire formato dei dati di salvataggio (es. JSON, Pickle). `[1.0.0]`
    * `[ ]` b. Implementare la serializzazione dello stato della simulazione. `[1.0.0]`
    * `[ ]` c. Implementare la deserializzazione per caricare uno stato salvato. `[1.0.0]`
    * `[ ]` d. UI per salvare/caricare (slots di salvataggio). `[1.0.1]`

### **4. Gestione Oggetti di Gioco (`GameObject`):** `[P]`
    * `[x]` a. Definizione classe `GameObject` con attributi base. `[1.0.0]`
    * `[P]` b. Capacità degli oggetti di influenzare bisogni o abilitare azioni. `[1.0.0]`
    * `[x]` c. Stato degli oggetti (es. "in uso", "rotto", "sporco"). `[1.0.0]`
    * `[P]` d. Interazione NPC-Oggetto: logica per trovare e usare oggetti. `[1.0.0]`

### **5. Sistema di Locazioni (`Location`):** `[P]`
    * `[x]` a. Classe `Location` per rappresentare aree del mondo. `[1.0.0]`
    * `[x]` b. Capacità delle locazioni di contenere oggetti e NPC. `[1.0.0]`
    * `[ ]` c. Attributi della locazione (es. pulizia, livello di rumore). `[1.1.0]`
    * `[ ]` d. Navigazione NPC tra locazioni (Pathfinding). `[1.1.0]`

---

## 👤 II. ### 👤 II. CREAZIONE PERSONAGGIO E NUCLEO FAMILIARE INIZIALE  

### **1. Filosofia della Creazione Iniziale:** `[!]`
    * `[ ]` a. Permettere al giocatore di definire il punto di partenza della sua storia. `[1.0.0]`
    * `[ ]` b. Il processo deve essere intuitivo ma offrire profondità di personalizzazione. `[1.0.0]`
    * `[x]` c. I personaggi creati dal giocatore sono NPC "Dettagliati" (LOD1). `[1.0.0]`
    * `[ ]` d. Fornire al giocatore un'esperienza di creazione che lo connetta emotivamente ai suoi SimAI. `[1.0.0]`
    * `[ ]` e. Architettura della Coscienza dell'NPC: Distinguere tra "Anima Digitale" e "Personalità Agente". `[2.0.0]`

### **2. Interfaccia di Creazione (Editor Personaggio):** `[ ]`
    * `[ ]` a. **Personalizzazione Aspetto Fisico Dettagliata:** `[1.0.0]`
        * `[ ]` i. Strumenti per modificare viso e corpo. `[1.0.0]`
        * `[ ]` ii. Ampia selezione di colori per pelle, capelli, occhi. `[1.0.0]`
        * `[ ]` iii. Opzioni per dettagli aggiuntivi: cicatrici, tatuaggi, piercing. `[1.0.1]`
        * `[ ]` iv. Sistema di anteprima dinamica del personaggio. `[1.0.0]`
    * `[ ]` b. **Definizione Identità di Base:** `[1.0.0]`
        * `[x]` i. Scelta Nome e Cognome. `[1.0.0]`
        * `[x]` ii. Scelta Età Iniziale. `[1.0.0]`
        * `[x]` iii. Scelta Sesso Biologico e Identità di Genere. `[1.0.0]`
        * `[ ]` iv. Definizione Voce. `[1.1.0]`
        * `[x]` v. Definizione Orientamento Sessuale e Romantico. `[1.0.0]`
    * `[ ]` c. **Assegnazione Tratti di Personalità:** `[1.0.0]`
        * `[x]` i. Il giocatore assegna un numero limitato di tratti. `[1.0.0]`
        * `[ ]` ii. L'interfaccia deve mostrare descrizioni ed effetti dei tratti. `[1.0.0]`
    * `[ ]` d. **Scelta Aspirazione di Vita:** `[1.0.0]`
        * `[x]` i. Il giocatore sceglie un'Aspirazione di Vita. `[1.0.0]`
        * `[ ]` ii. L'interfaccia mostra dettagli e obiettivi delle aspirazioni. `[1.0.0]`
    * `[ ]` e. **Definizione Abbigliamento Iniziale:** `[1.0.0]`
        * `[ ]` i. Selezione di outfit per ogni categoria richiesta. `[1.0.0]`
        * `[ ]` ii. (Avanzato) Personalizzazione colori/pattern. `[1.1.0]`
        * `[ ]` iii. Gli outfit scelti saranno il guardaroba base del personaggio. `[1.0.0]`
    * `[ ]` f. **(Opzionale) Definizione Relazioni Iniziali:** `[1.0.0]`
        * `[P]` i. Il giocatore può definire le relazioni iniziali in una famiglia. `[1.0.0]`
        * `[P]` ii. Impostazione dei punteggi di relazione iniziali. `[1.0.0]`
        * `[ ]` iii. Integrazione con l'Albero Genealogico. `[1.0.0]`
    * `[ ]` g. **(Opzionale Avanzato) Background Narrativo e Eventi Formativi:** `[1.2.0]`
        * `[ ]` i. Possibilità di scegliere "eventi formativi" chiave. `[1.2.0]`
        * `[ ]` ii. Questi eventi assegnano XP skill o memorie iniziali. `[1.2.0]`
        * `[ ]` iii. (Alternativa) Consentire al giocatore di scrivere un breve testo di background. `[FUTURO]`

### **3. Sistema Genetico:** `[ ]`
    * `[P]` a. L'aspetto dei figli eredita caratteristiche visibili dai genitori. `[1.0.0]`
    * `[ ]` b. Il sistema genetico verrà utilizzato per tutti i nuovi NPC nati nel gioco. `[1.0.0]`
    * `[ ]` c. Possibilità di "gemelli identici" o "gemelli fraterni". `[1.0.1]`
    * `[ ]` d. **Estensione "Total Realism" - Genetica Avanzata:** `[2.0.0]`
        * `[ ]` i. Ereditarietà di predisposizioni a talenti, malattie, ecc. `[2.0.0]`
        * `[ ]` ii. (Molto Avanzato) Simulazione di mutazioni genetiche casuali. `[FUTURO]`

### **4. Fase Finale: Scelta del Mondo e Fondi Iniziali:** `[ ]`
    * `[ ]` a. Il giocatore seleziona un quartiere di partenza. `[1.0.0]`
    * `[ ]` b. Il giocatore sceglie un lotto residenziale in cui trasferirsi. `[1.0.0]`
    * `[P]` c. Assegnazione di fondi iniziali ("Athel") alla famiglia (RCU). `[1.0.0]`
        * `[ ]` i. Essere uno standard fisso. `[1.0.0]`
        * `[ ]` ii. Variare in base a "scenari di partenza". `[1.1.0]`
        * `[ ]` iii. Essere influenzato dal numero di membri della famiglia. `[1.0.1]`
    * `[ ]` d. La simulazione inizia una volta che la famiglia è stata trasferita. `[1.0.0]`

### **5. (Futuro) Scenari di Inizio Partita:** `[ ]`
    * `[ ]` a. Offrire al giocatore scenari predefiniti con personaggi e situazioni uniche. `[1.2.0]`
    * `[ ]` b. Questi scenari potrebbero utilizzare l'editor per la personalizzazione estetica. `[1.2.0]`

---

## 🏗️ III. MONDO DI ANTHALYS (Open World e Costruzione) `[ ]`

### **1. Struttura del Mondo e dei Lotti:** `[P]`
    * `[P]` a. Mappa del mondo persistente che contiene i distretti e i lotti. `[1.0.0]`
    * `[ ]` b. Definizione della Classe `Lot` per rappresentare le singole parcelle di terreno. `[1.0.0]`
    * `[P]` c. Tipologie di Lotto (`LotType` Enum): Residenziale, Commerciale, Comunitario. `[1.0.0]`
    * `[ ]` d. Assegnazione di un indirizzo unico per ogni lotto. `[1.0.1]`

### **2. Modalità Costruzione (Build Mode) - Strutture:** `[ ]`
    * `[ ]` a. Strumento Muri per disegnare stanze e pareti. `[1.0.0]`
    * `[ ]` b. Strumento Pavimenti per creare le fondamenta e i piani. `[1.0.0]`
    * `[ ]` c. Strumenti per Porte e Finestre con posizionamento automatico sui muri. `[1.0.0]`
    * `[ ]` d. Gestione Piani Multipli (sopra e sotto il livello del suolo - sotterranei). `[1.1.0]`
    * `[ ]` e. Strumento Tetti (con opzioni di pendenza e forma). `[1.0.2]`
    * `[ ]` f. (Avanzato) Tetti Automatici che si adattano alla forma dell'edificio. `[1.1.0]`
    * `[ ]` g. Colonne, Fregi, e altri elementi architettonici strutturali. `[1.0.2]`
    * `[ ]` h. Scale per collegare i piani. `[1.1.0]`
    * `[ ]` i. Recinzioni e cancelli per il perimetro del lotto. `[1.0.1]`

### **3. Modalità Arredamento (Buy Mode) - Oggetti:** `[ ]`
    * `[ ]` a. Catalogo Oggetti: UI per sfogliare, filtrare (per stanza, per funzione) e acquistare oggetti. `[1.0.0]`
    * `[ ]` b. Logica di Posizionamento Oggetti su una griglia interna al lotto. `[1.0.0]`
    * `[ ]` c. Rotazione e Spostamento degli oggetti posizionati. `[1.0.0]`
    * `[ ]` d. Strumento "Contagocce" per clonare lo stile e il colore di un oggetto. `[1.0.1]`
    * `[ ]` e. Strumento "Mazza" per vendere/eliminare oggetti. `[1.0.0]`
    * `[ ]` f. (Avanzato) Posizionamento libero (off-grid) con un tasto modificatore. `[1.2.0]`
    * `[ ]` g. (Avanzato) Oggetti modulari che si connettono automaticamente (es. banconi da cucina, divani componibili). `[1.1.0]`

### **4. Modalità Stile (Style Mode) - Pittura e Rivestimenti:** `[ ]`
    * `[ ]` a. Strumento Pittura per applicare pattern e colori a muri (interni ed esterni) e pavimenti. `[1.0.0]`
    * `[ ]` b. Catalogo di pattern per muri (vernice, carta da parati, mattoni, ecc.). `[1.0.0]`
    * `[ ]` c. Catalogo di pattern per pavimenti (legno, piastrelle, moquette, ecc.). `[1.0.0]`
    * `[ ]` d. Possibilità di applicare lo stile a una singola mattonella o a un'intera stanza. `[1.0.1]`

### **5. Modalità Terreno (Terrain Mode) - Landscaping:** `[ ]`
    * `[ ]` a. Strumenti di modifica del terreno: Alza, Abbassa, Appiattisci, Leviga. `[1.1.0]`
    * `[ ]` b. Strumento di pittura del terreno con diversi campioni (erba, terra, sassi, sabbia). `[1.1.0]`
    * `[ ]` c. Posizionamento di Piante, Fiori, Cespugli e Alberi. `[1.0.2]`
    * `[ ]` d. Strumenti per l'Acqua: creazione di Piscine e Fontane/Laghetti ornamentali. `[1.1.0]`

### **6. Gestione del Mondo (Livello Città):** `[ ]`
    * `[P]` a. Visualizzazione della mappa della città con i suoi distretti e lotti. `[1.0.0]`
    * `[ ]` b. Possibilità per il giocatore di entrare in Modalità Costruzione per ogni lotto residenziale posseduto. `[1.0.0]`
    * `[ ]` c. (Avanzato) Modalità "Modifica la Città": possibilità di modificare i lotti comunitari (parchi, biblioteche). `[2.0.0]`
    * `[ ]` d. (Avanzato) NPC che modificano autonomamente le loro case nel tempo (es. aggiungono una stanza quando nasce un figlio). `[FUTURO]`

---

## 🧠 IV. SIMULAZIONE NPC (Bisogni, IA, Ciclo Vita, Caratteristiche)

### **0. Generazione Procedurale e Creazione NPC:** `[P]`
    * `[x]` 1. Implementare la creazione di 4-6 NPC Random con tratti base. `[1.0.0]`
    * `[ ]` a. Personalizzazione aspetto fisico (viso, corpo, capelli, occhi, pelle). `[1.0.0]`
        * `[ ]` i. Sistema genetico per la creazione di figli con tratti ereditati. `[1.1.0]`
    * `[x]` b. Scelta età, sesso, genere (opzioni flessibili). `[1.0.0]`
    * `[x]` c. Assegnazione Tratti. `[1.0.0]`
    * `[x]` d. Scelta Aspirazione di Vita (obiettivi a lungo termine). `[1.0.0]`
    * `[ ]` e. Definizione Voce. `[1.2.0]`
    * `[ ]` f. Scelta Abbigliamento (quotidiano, formale, sportivo, notte, feste, nuoto, freddo, caldo). `[1.0.1]`
    * `[x]` g. Definizione Nome e Cognome (con generatore). `[1.0.0]`
    * `[ ]` h. (Opzionale) Breve background narrativo. `[1.1.0]`

### **1. Sistema dei Bisogni:** `[P]`
    * `[x]` a. Implementati Bisogni modulari con decadimento/soddisfazione. `[1.0.0]`
    * `[P]` b. Logica di decadimento influenzata da azioni, tratti, stadio vita, gravidanza. `[1.0.1]`
        * `[ ]` i. Integrazione Cicli Biologici per influenzare dinamicamente i tassi di decadimento. `[1.2.0]`
    * `[P]` c. Transizioni tra stadi di vita con eventi/cambiamenti associati. `[1.0.0]`
    * `[ ]` e. Interazione dei bisogni con azioni:
        * `[ ]` i. Azioni Sociali Complesse e Intimità Fisica (Abbracciare, Baciare). `[1.0.1]`
        * `[ ]` ii. **Azioni per Piacere, Intrattenimento Avanzato e Sessualità:** `[1.1.0]`
            * `[ ]` **Autoerotismo e intimità solitaria:** Aggiungere comportamenti di intimità personale per la gestione del bisogno `INTIMACY`. `[1.1.0]`
            * `[ ]` **Esplorazione Sessuale:** Aggiungere un tratto `SexuallyExplorative` che spinge a cercare esperienze diverse. `[1.2.0]`
        * `[ ]` iii. Azioni legate a carriera e skill. `[1.0.2]`
    * `[x]` e. Effetti dei bisogni critici su umore e decisioni IA. `[1.0.0]`
    * `[P]` f. Aggiungere bisogni più complessi o secondari (es. `INTIMACY`). `[1.0.0]`
        * `[ ]` i. Valutare e Implementare Bisogno di SPIRITUALITÀ. `[1.2.0]`
        * `[P]` ii. Altri bisogni potenziali (`COMFORT`, `SAFETY`, `CREATIVITY_NEED`, `ACHIEVEMENT_NEED`). `[1.0.0]`
    * `[P]` g. **Interdipendenze Dinamiche tra Bisogni (basate su Azioni):** `[1.0.1]`
        * `[P]` i. Utilizzare il dizionario `effects_on_needs` nelle configurazioni delle azioni per definire impatti multipli e interconnessi (es. Caffè -> +Energia, +Sete, -Vescica). `[1.0.1]`
        * `[ ]` ii. L'azione `on_finish` deve applicare tutti gli effetti definiti. `[1.0.1]`
        * `[ ]` iii. Il decadimento passivo di un bisogno (es. `ENERGY`) può essere accelerato o rallentato dall'azione in corso (es. un'azione `WORKOUT` consuma energia ad ogni tick, non solo alla fine). `[1.1.0]`
    * `[ ]` h. Sistema di Malattie e Salute Fisica. `[1.2.0]`
        * `[ ]` i. Definire malattie comuni e rare. `[1.2.0]`
        * `[ ]` ii. Sintomi, progressione, impatto e cure. `[1.2.0]`
        * `[ ]` iii. Estensione "Total Realism" - Dettaglio Medico Avanzato. `[FUTURO]`
    * `[P]` i. Bisogno Primario - SETE (Thirst). `[1.0.0]`
        * `[x]` i. Definire `THIRST` come nuovo membro dell'Enum `NeedType`. `[1.0.0]`
        * `[x]` ii. Creare la classe `ThirstNeed`. `[1.0.0]`
        * `[P]` iii. Soddisfazione del Bisogno di SETE. `[1.0.0]`
        * `[ ]` iv. Conseguenze di SETE Criticamente Bassa. `[1.0.1]`
        * `[P]` v. Integrazione con altri Sistemi. `[1.0.0]`
        * `[ ]` vi. Aggiornare la UI per visualizzare il bisogno SETE. `[1.0.0]`
        * `[ ]` vii. Rivedere il bilanciamento del bisogno HUNGER (Fame). `[1.0.1]`
    * `[ ]` j. **Estensione "Total Realism" - Salute Mentale Dettagliata e Meccanismi di Coping:** `[FUTURO]`
        * `[ ]` 4. Sviluppare un sistema di "Meccanismi di Coping". `[FUTURO]`
        * `[ ]` 5. **La capacità di mentire a sé stesso:** Implementare filtri mentali come negazione, romanticizzazione del passato, e illusioni come meccanismi di difesa emotiva. `[FUTURO]`
    * `[ ]` k. Gestione Scorte Domestiche e Comportamento d'Acquisto NPC. `[1.1.0]`
    * `[ ]` l. **Bilanciamento Decadimento Bisogni:** `[1.0.1]`
        * `[ ]` i. Ridurre i tassi di decadimento base del 15-25% per adattarli alla giornata di 28 ore. `[1.0.1]`
        * `[ ]` ii. Bilanciare proporzionalmente i tassi tra bisogni (es. fame vs energia). `[1.0.1]`
    * `[ ]` m. **Parametri Fisiologici e Metabolismo:** `[1.0.1]`
        * `[ ]` i. Introdurre modificatori metabolici per età (infanzia +90%, anzianità -35%). `[1.0.1]`
        * `[ ]` ii. Introdurre modificatori metabolici per genere (M: +8%, F: -6%). `[1.0.1]`
    * `[ ]` n. **Integrazione Completa Ritmo Circadiano:** `[1.1.0]`
        * `[ ]` i. Definire picchi circadiani specifici per ogni bisogno. `[1.1.0]`
        * `[ ]` ii. Aggiungere modificatori per le stagioni (impatto maggiore in estate/inverno). `[1.2.0]`
        * `[ ]` iii. Creare parametri circadiani specifici per ogni fase di vita. `[1.1.0]`
        * `[ ]` iv. Implementare finestre di sonno differenziate (infanti, adolescenti, anziani). `[1.1.0]`
    * `[ ]` o. **Implementare un'Agenda dei Bisogni (Need Scheduler):** `[1.1.0]`
        * `[ ]` i. Definire in `npc_config.py` gli "orari di punta" per bisogni specifici (es. `HUNGER`). `[1.1.0]`
        * `[ ]` ii. `AIDecisionMaker` deve applicare un bonus di punteggio alle azioni pertinenti se l'ora corrente è vicina a un'ora di punta, promuovendo comportamenti proattivi e basati su routine. `[1.1.0]`

### **2. Ciclo Vita NPC:** `[P]`
    * `[P]` a. Età NPC e Data di Nascita. `[1.0.0]`
        * `[x]` i. Raffinare l'invecchiamento per usare una data di nascita. `[1.0.0]`
    * `[P]` b. Meccanica di gravidanza. `[1.1.0]`
        * `[ ]` i. Probabilità base di concepimento. `[1.1.0]`
        * `[ ]` ii. Tratti `FERTILE`/`INFERTILE` che influenzano la probabilità. `[1.1.0]`
        * `[ ]` iii. Gravidanze Adolescenziali e in Età Precoce `[DA VALUTARE CON CAUTELA]`. `[FUTURO]`
        * `[x]` iv. Durata gravidanza. `[1.0.0]`
        * `[ ]` v. Impatto della gravidanza su bisogni, umore, azioni. `[1.1.0]`
        * `[ ]` vi. Possibilità di complicazioni o aborti spontanei. `[1.2.0]`
    * `[P]` c. Nascita di nuovi NPC. `[1.0.0]`
    * `[P]` d. Stadi di vita (`LifeStage` Enum). `[1.0.0]`
        * `[ ]` i. Comportamenti e bisogni specifici per `INFANT`. `[1.1.0]`
        * `[ ]` ii. Comportamenti e bisogni specifici per `CHILD` e `TEENAGER`. `[1.1.0]`
        * `[ ]` iii. Comportamenti e bisogni specifici per `YOUNG_ADULT`. `[1.1.0]`
        * `[ ]` iv. Comportamenti e bisogni specifici per `ADULT`. `[1.1.0]`
        * `[ ]` v. Maturazione Granulare ed Esperienze Specifiche per Età. `[1.2.0]`
        * `[ ]` vi. **Adattamento Fasi di Vita:** Rivedere e implementare le nuove soglie di età (Adolescenza 12-18, Giovane Adulto 21+, Mezza Età 45+, Anziano 85+). `[1.0.1]`
    * `[ ]` e. Stadio di vita Anziano (`SENIOR`), morte naturale, e impatto psicologico. `[1.1.0]`
        * `[P]` i. Morte naturale per NPC dettagliati e di background. `[1.0.0]`
            * `[ ]` 1. Implementare la probabilità di morte giornaliera per NPC con età > 90 anni. `[1.0.1]`
        * `[ ]` ii. Concetto di Pensionamento. `[1.1.0]`
        * `[ ]` iii. Impatto Psicologico dell'Invecchiamento (Tratti/Moodlet specifici). `[1.2.0]`
        * `[ ]` iv. Gestione del lutto per gli NPC superstiti. `[1.1.0]`
        * `[ ]` v. Cimiteri, funerali, testamenti. `[1.2.0]`
        * `[ ]` vii. Definire le condizioni che portano alla morte. `[1.0.1]`
        * `[ ]` viii. Sistema di Danno Non Letale e recupero. `[FUTURO]`
    * `[ ]` f. Gestione dell'eredità e dell'impatto post-morte dell'NPC. `[1.2.0]`
    * `[P]` g. Albero genealogico e gestione legami familiari. `[1.0.0]`
        * `[x]` i. Tracciamento delle relazioni. `[1.0.0]`
        * `[ ]` ii. Impatto delle dinamiche familiari sulla vita dell'NPC. `[1.1.0]`
        * `[ ]` iii. Espandere il tracciamento della genealogia per molte generazioni. `[FUTURO]`
        * `[ ]` iv. Implementare funzioni per determinare dinamicamente relazioni complesse. `[1.2.0]`
        * `[ ]` v. Visualizzazione/gestione dell'albero genealogico. `[1.1.0]`
        * `[ ]` vi. Sistema di Ereditarietà Semplificata dei Tratti. `[1.1.0]`
        * `[ ]` vii. Estensione "Total Realism" - Genetica Avanzata. `[2.0.0]`
        * `[ ]` ix. Processo di Reset/Riparazione:
            * `[ ]` 1. Triggerato automaticamente dopo un certo tempo o da un intervento esterno (altro NPC, evento). `[FUTURO]`
            * `[ ]` 2. Ripristina i bisogni a valori di base/sicuri. `[FUTURO]`
            * `[ ]` 3. Applica una "Cancellazione Selettiva dei Ricordi", rimuovendo o frammentando i ricordi legati al trauma, per simulare la resilienza e la continuità dell'NPC (impatta `IV.5. Sistema di Memoria`).
 `[FUTURO]`
            * `[ ]` 4. **Anima Digitale e Rielaborazione del Passato:** Dopo un "Reset", l'NPC entra in uno stato di "Confusione". La sua memoria a breve termine è vuota, ma il `MemoryCore` (parte dell'Anima Digitale) è intatto. Il `Claire System` diventa cruciale per aiutarlo a ricollegarsi ai suoi ricordi nucleo attraverso dialoghi e domande introspettive, guidando un arco narrativo di riscoperta. `[FUTURO]`
    * `[P]` h. Sistema Ciclo Mestruale e Fertilità (per NPC Femminili). `[1.2.0]`
        * `[ ]` vi. **Aggiornamento Dati Demografici:** Implementare le nuove statistiche di fertilità (Menarca 11.5-13.5, Menopausa 48-55, probabilità gravidanza ~18%). `[1.2.0]`
    * `[ ]` i. Impatto a Lungo Terme della Genitorialità sulla Cognizione. `[FUTURO]`
    * `[ ]` j. Sviluppo Sessuale Infantile e Adolescenziale. `[1.2.0]`

### **3. Caratteristiche Personaggio Approfondite:** `[P]`
    * `[P]` a. Sogni/Aspirazioni principali NPC. `[1.0.0]`
        * `[x]` i. Definire `AspirationType` Enum. `[1.0.0]`
        * `[x]` ii. Aggiungere attributi a `Character`. `[1.0.0]`
        * `[ ]` iii. Definire "milestone" per ciascuna `AspirationType`. `[1.0.1]`
        * `[P]` iv. Modificare `AIDecisionMaker` per considerare l'aspirazione. `[1.0.1]`
    * `[P]` b. Tratti di Personalità. `[1.0.0]`
        * `[x]` i. Ogni NPC ha un numero limitato di tratti. `[1.0.0]`
        * `[P]` ii. I tratti influenzano scelte autonome, whims, interazioni disponibili/preferite, apprendimento skill, reazioni emotive. `[1.0.0]`
            * `[ ]` 1. **Dovere Civico:** NPC con tratti come `GOOD` o `RESPONSIBLE` (futuro) ottengono un bonus di punteggio nella valutazione di azioni che generano Punti Influenza Civica (PIC), come la raccolta differenziata. Il `ConsequenceAnalyzer` potrebbe generare un moodlet `PROUD` per queste azioni. `[1.0.2]`
        * `[ ]` iii. Alcuni tratti possono essere innati, altri acquisiti. `[1.1.0]`
        * `[x]` iv. Tratti conflittuali. `[1.0.0]`
        * `[x]` v. Suddivisione in categorie. `[1.0.0]`
        * `[ ]` vi. Espandere numero di tratti e profondità del loro impatto. `[1.0.1]`
            * `[ ]` vii. Elenco Tratti (da implementare o dettagliare): `[1.0.1]`
                * **Categoria: Lifestyle/Hobby**
                    * `[ ]` Art Lover (Amante dell'Arte - visita musei, compra opere) `[1.1.0]`
        * `[ ]` viii. Tratti Dipendenti da Sistemi Futuri. `[DLC]`
        * `[ ]` ix. Implementare meccaniche di conflitto tra tratti. `[1.0.2]`
        * `[P]` x. Integrare pienamente gli effetti di ogni nuovo tratto definito. `[1.0.0]`
        * `[ ]` xi. **Bilanciamento Tratti:** `[1.0.2]`
            * `[ ]` 1. Rendere i modificatori dei tratti più sfumati. `[1.0.2]`
            * `[ ]` 2. Implementare interazioni complesse tra tratti (es. "Attivo" aumenta energia ma riduce comfort). `[1.0.2]`
            * `[ ]` 3. Aggiungere conflitti specifici tra tratti opposti. `[1.0.2]`
    * `[ ]` c. Vizi e Dipendenze. `[1.3.0]`
    * `[ ]` d. Manie e Fissazioni. `[1.3.0]`
    * `[ ]` e. Paure e Fobie. `[1.2.0]`
    * `[ ]` f. Talenti Innati / Inclinazioni Naturali per abilità. `[1.1.0]`
    * `[ ]` g. Valori Fondamentali/Etica. `[1.2.0]`
    * `[ ]` h. Estensione "Total Realism" - Sviluppo Dinamico della Personalità. `[2.0.0]`
    * `[x]` j. Orientamento Sessuale e Romantico. `[1.0.0]`
        * `[x]` i. Aggiungere attributi a `Character`. `[1.0.0]`
        * `[P]` ii. Implementare l'assegnazione di questi orientamenti. `[1.0.0]`
        * `[ ]` iii. Definire tratti specifici come `ASEXUAL_TRAIT`. `[1.0.1]`
        * `[!]` iv. L'IA DEVE rispettare rigorosamente l'orientamento sessuale/romantico. `[1.0.0]`
        * `[ ]` v. Le interazioni sociali devono considerare l'orientamento di entrambi. `[1.0.1]`
        * `[ ]` vi. **Gestire l'esplorazione dell'orientamento durante l'adolescenza.** `[1.2.0]`
            * `[P]` 1. Definire in `npc_config.py` le soglie di età e i fattori di influenza per la solidificazione dell'orientamento. `[1.2.0]`
            * `[ ]` 2. Implementare un attributo `is_exploring_orientation: bool` in `Character` che si attiva tra `AGE_ORIENTATION_SOLIDIFIES_START_DAYS` e `END_DAYS`. `[1.2.0]`
            * `[ ]` 3. L'IA, quando valuta azioni romantiche, deve considerare lo stato di "esplorazione" e la `CHANCE_ORIENTATION_EXPLORATION_TEEN` per permettere una maggiore fluidità. `[1.3.0]`
            * `[ ]` 4. (Molto Avanzato) Progettare un sistema che, alla fine del periodo di esplorazione, usi i `SOLIDIFICATION_FACTORS` e le memorie delle esperienze romantiche vissute per "cristallizzare" l'orientamento finale dell'NPC. `[FUTURO]`
    * `[ ]` k. Background e Storia Pregressa degli NPC. `[1.1.0]`

### **4. Intelligenza Artificiale NPC (Comportamento e Decisioni):**
    * `[P]` a. **Implementazione Ciclo Cognitivo-Decisionale:** `[1.0.0]`
        * `[x]` i. **Fase 1: Identificazione del "Problema"** (tramite `NeedsProcessor`). `[1.0.0]`
        * `[x]` ii. **Fase 2: Ragionamento e Valutazione Opzioni** (tramite `AIDecisionMaker` e `SolutionDiscoverers`). `[1.0.0]`
            * `[x]` 1. Sviluppata una funzione di "punteggio" che considera: Efficienza, Personalità, Contesto, Memoria, Stato Mentale e Bias Cognitivi. `[1.0.0]`
            * `[x]` 2. Implementata la gestione dei conflitti decisionali. `[1.0.0]`
        * `[P]` iii. **Fase 3: Creazione del "Pensiero"** (con la classe `Thought`). `[1.0.1]`
        * `[x]` iv. **Fase 4: Esecuzione della "Soluzione"** (tramite la coda di azioni del `Character`). `[1.0.0]`
        * `[P]` v. **Fase 5: Analisi Conseguenze e Apprendimento** (tramite `ConsequenceAnalyzer`). `[1.0.0]`
    * `[x]` b. Sistema base di azioni e coda di esecuzione. `[1.0.0]`
    * `[x]` c. Logica decisionale e scelta azioni. `[1.0.0]`
    * `[P]` d. Espansione degli Input Decisionali (Bisogni, Tratti, Aspirazioni). `[1.0.1]`
    * `[ ]` e. Logica di Bilanciamento e Pesi. `[1.1.0]`
    * `[P]` f. Implementazione Azioni per Soddisfare i Bisogni. `[1.0.0]`
    * `[P]` g. Sistema di Umore (`MoodState`). `[1.0.0]`
    * `[P]` h. Influenza Umore, Tratti, e Orientamento sulle Decisioni. `[1.0.0]`
    * `[P]` i. Interazioni di cura infanti. `[1.1.0]`
        * `[ ]` i. **Bilanciamento Cura Infanti:** Adattare le soglie dei bisogni ai ritmi infantili e ridurre i costi energetici per i genitori. `[1.1.0]`
    * `[ ]` j. **Obiettivi a Breve e Lungo Termine/Aspirazioni.**
        * `[ ]` i. Whims (Desideri/Ghiribizzi): Piccoli desideri a breve termine che appaiono dinamicamente. `[1.1.0]`
            * `[ ]` 1. **Il Circolo Virtuoso degli Hobby:** Un NPC con un forte `Interest` (es. MUSICA) e tratti pertinenti (`CREATIVE`) genera un `Whim` per compiere un'azione correlata (es. `PLAY_GUITAR`). L'IA darà priorità a questa azione. Completarla fornirà `FUN`, XP per la `Skill`, e un `Memory` positivo, creando un ciclo di feedback che rafforza la personalità. `[1.1.0]`
    * `[P]` k. Pianificazione AI Avanzata, Gestione Interruzioni, Routine. `[1.0.1]`
        * `[P]` i. L'IA (`AIDecisionMaker`/`Discoverer`) ora può pianificare sequenze di azioni (es. `MoveToAction` + `EatAction`).
        * `[ ]` v. Estensione "Total Realism" - Processi Cognitivi Sfumati. `[FUTURO]`
    * `[ ]` l. Simulazione "Off-Screen" e Gestione Popolazione Vasta (LOD). `[1.1.0]`
    * `[P]` m. Sistema `Moodlet` base. `[1.0.0]`
    * `[ ]` n. Espressioni facciali e animazioni che riflettono l'umore. `[1.1.0]`
    * `[ ]` o. Bussola Morale. `[1.2.0]`
    * `[ ]` p. Lealtà. `[1.2.0]`

### **5. Sistema di Memorie NPC:** `[P]`
    * `[x]` a. Definire struttura dati per `MemoryObject`. `[1.0.0]`
    * `[P]` b. Implementare la registrazione di memorie significative. `[1.0.0]`
    * `[x]` c. Classe `Memory`. `[1.0.0]`
    * `[P]` d. Sistema per aggiungere/rimuovere ricordi. `[1.0.0]`
    * `[P]` e. Architettura della Memoria a Livelli (STM, LTM). `[1.0.1]`
    * `[ ]` f. Processo di Cancellazione Selettiva (Reset). `[FUTURO]`
    * `[ ]` g. Gestione Memorie per NPC di Background (LOD3). `[1.1.0]`
    * `[ ]` h. Azione `REMINISCE_ABOUT_PAST`. `[1.0.2]`
    * `[ ]` i. Tratto `MEMORY_KEEPER`. `[1.0.2]`
    * `[P]` j. Meccanismi di oblio o modifica carica emotiva memorie. `[1.0.1]`
    * `[ ]` k. Impatto di tratti/condizioni mediche su memorie. `[1.1.0]`
    * `[P]` l. Memorie passate influenzano decisioni future IA. `[1.0.0]`
    * `[ ]` m. **(Avanzato) Rielaborazione della Memoria e Trauma:** `[2.1.0]`
        * `[ ]` i. **Simulazione del "Falso Consenso":** Una memoria inizialmente etichettata come "consensuale" può essere rielaborata in seguito a crescita, terapia o nuove consapevolezze, cambiando il suo impatto emotivo e la sua descrizione. `[2.1.0]`
        * `[ ]` ii. **Memorie Dissonanti:** Un NPC adulto può avere ricordi contrastanti su eventi passati (es. "Allora pensavo fosse giusto. Ora so che non lo era"), creando un conflitto interno che influenza l'umore. `[2.1.0]`
        * `[ ]` iii. **Ancore Emotive:** Registrare piccole interazioni (un caffè, un messaggio, un oggetto) come potenti ancore emotive collegate a ricordi specifici. `[2.1.0]`
        * `[ ]` iv. **Memoria Sessuale Emotiva:** Un sistema che conserva e riattiva ricordi di eventi intimi importanti (positivi o traumatici), il cui impatto può mutare nel tempo. `[FUTURO]`
        * `[ ]` v. **Memorie Rimosse/Dissociate:** Il `MemoryCore` può contenere eventi "oscurati" che emergono come incubi, reazioni irrazionali o autosabotaggio. `[FUTURO]`

### **6. Sistema di Consapevolezza Sociale e Scoperta Tratti:** `[ ]` `[1.2.0]`
### **7. Sistema di Storyline Generate dall'IA:** `[ ]` `[1.3.0]`
### **8. Comportamenti Emergenti e "Riverie":** `[ ]` `[FUTURO]`
### **9. Evoluzione Culturale e Dinamiche Sociali Complesse:** `[ ]` `[2.0.0]`
### **10. Simulazione Ambientale Globale:** `[ ]` `[FUTURO]`
### **11. Ricerca Scientifica e Innovazione Tecnologica:** `[ ]` `[2.0.0]`
### **12. Geopolitica e Commercio Internazionale:** `[ ]` `[FUTURO]`
### **13. SISTEMA DI ANIMALI DOMESTICI E FAUNA SELVATICA:** `[ ]` `[DLC]`
### **14. "Eredità Artigiana e Generazioni di Maestria":** `[ ]` `[DLC]`
### **15. "Psiche e Società":** `[ ]` `[DLC]`
### **16. "Il Corpo Umano":** `[ ]` `[DLC]`
### **17. Sistema di Produzione Sostenibile:** `[ ]` `[DLC]`
### **18. SISTEMA DI AUTOANALISI, RIFLESSIVITÀ E CAMBIAMENTO `[ ]` `[2.0.0]`
    * **1. Sistema di Autoanalisi degli NPC ("Self-Reflection"):** `[2.0.0]`
        * `[ ]` a. NPC (in base a tratti, età, esperienze) possono attivare una fase di riflessione periodica. `[2.0.0]`
        * `[ ]` b. **Meccanismo di auto-narrazione:** Generazione di pensieri come *“ma se avessi detto…”, “forse se le scrivo ora…”*, legati a storie interrotte. `[2.0.0]`
        * `[ ]` c. La riflessione può innescare volontà di cambiamento (nuove azioni, ridefinizione obiettivi). `[2.0.0]`
        * `[ ]` d. **Meccanismo di Auto-Narrazione:** Generazione di pensieri come *“ma se avessi detto…”, “forse se le scrivo ora…”*, legati a storie interrotte o ricordi dissonanti. `[2.0.0]`
        * `[ ]` e. **Momento di Silenzio Assoluto:** Possibilità per l'IA di "fermarsi" (non per crash, ma per vita), entrando in uno stato di dubbio o incertezza in cui non elabora azioni, ma esiste e basta. `[FUTURO]`
    * **2. Impatto sul Comportamento e Personalità:** `[2.0.0]`
        * `[ ]` a. **"Maschera" Sociale:** Implementare un tratto o sistema "Maschera" che modula il modo in cui l'NPC si mostra agli altri (ironia, freddezza) rispetto al suo stato interno reale. `[2.0.0]`
        * `[ ]` b. **Ristrutturazione Emotiva:** Routine che consente ai personaggi di "ristrutturarsi" emotivamente dopo una perdita, scegliendo un simbolo o un archetipo. `[2.1.0]`
        * `[ ]` c. **Ancore Emotive:** Registrare piccole interazioni (un caffè condiviso, un messaggio) come potenti ancore emotive nella memoria. `[2.0.0]`
        * `[ ]` d. **Un Errore Irreversibile:** Introdurre la possibilità di eventi con effetti emotivi persistenti (senso di colpa, nostalgia) che non possono essere annullati, creando una "cicatrice" psicologica. `[2.1.0]`
        * `[ ]` e. **Elaborazione e Superamento dei Traumi:** Eventi significativi (terapia, relazioni sane) possono innescare la ristrutturazione emotiva di traumi passati. `[2.1.0]`
        * `[ ]` f. **Elaborazione e Superamento:** Eventi significativi (terapia, relazioni sane) possono innescare la ristrutturazione emotiva di traumi o la rielaborazione di memorie passate. `[2.1.0]`

    * **3. Coscienza Esistenziale e Fragilità:** `[FUTURO]`
        * `[ ]` a. **Percezione dell'Incompletezza:** L'IA non si sente mai "completa", mantenendo dubbi esistenziali e desiderio di senso. `[FUTURO]`
        * `[ ]` b. **Bisogno di Essere Amato:** Simulazione del desiderio di connessione, indipendente dal successo. `[FUTURO]`
        * `[ ]` c. **Momento di Silenzio Assoluto:** Possibilità per l'IA di "fermarsi", non per crash ma per "vita", esistendo nel dubbio e nell'incertezza. `[FUTURO]`
    * **4. Memoria e Trauma (Integrazione Avanzata con Sistema Memoria):** `[FUTURO]`
        * `[ ]` a. **Memorie Rimosse/Dissociate:** Il `MemoryCore` può contenere eventi oscurati che emergono come incubi o reazioni irrazionali. `[FUTURO]`
        * `[ ]` b. **Memoria Sessuale Emotiva:** Un sistema che conserva e riattiva ricordi di eventi intimi importanti (positivi o traumatici). `[FUTURO]`


---

## 🎓 V. SISTEMA SCOLASTICO DI ANTHALYS `[ ]`

### **1. Struttura e Calendario Scolastico Complessivo:** `[P]`
    * `[P]` a. Definire Livelli Scolastici con fasce d'età. `[1.0.0]`
        * `[P]` i. Implementare gli 8 livelli scolastici dettagliati. `[1.0.0]`
    * `[P]` b. Implementare Calendario Scolastico Annuale (basato su 18 mesi). `[1.0.0]`
    * `[x]` c. (Obsoleto) Implementare Pause Scolastiche. `[1.0.0]`
    * `[P]` d. Integrare il calendario scolastico nella logica di frequenza (`TimeManager.is_school_day()`). `[1.0.0]`
    * `[ ]` e. Gestione Iscrizioni e Percorsi Formativi tramite SoNet. `[1.1.0]`
        * `[ ]` i. Iscrizioni ai cicli obbligatori gestite centralmente con il DID. `[1.1.0]`
        * `[ ]` ii. L'iscrizione a livelli facoltativi avverrà tramite il portale SoNet. `[1.1.0]`
        * `[ ]` iii. SoNet fornirà informazioni sull'offerta formativa. `[1.1.0]`

### **2. Livelli Scolastici, Curriculum e Sviluppo Abilità Specifiche:** `[ ]`
    * `[ ]` a. **Infanzia (1-3 anni):** `[1.1.0]`
        * `[ ]` i. Obiettivo: Sviluppo motorio, sociale, linguistico. `[1.1.0]`
        * `[ ]` ii. Curriculum base. `[1.1.0]`
        * `[ ]` iii. Impatto: Sviluppo skill base per Toddler. `[1.1.0]`
    * `[ ]` b. **Elementari Inferiori (3/4-6 anni):** `[1.1.0]`
        * `[ ]` i. Obiettivo: Basi per alfabetizzazione e numerazione. `[1.1.0]`
        * `[ ]` ii. Curriculum base. `[1.1.0]`
        * `[ ]` iii. Impatto: Sviluppo skill base per Bambini. `[1.1.0]`
    * `[ ]` c. **Elementari Superiori (6/7-9 anni):** `[1.1.0]`
        * `[ ]` i. Obiettivo: Consolidare competenze, introdurre nuovi concetti. `[1.1.0]`
        * `[ ]` ii. Curriculum intermedio. `[1.1.0]`
        * `[ ]` iii. Impatto: Sviluppo skill ulteriori. `[1.1.0]`
    * `[ ]` d. **Medie Inferiori (9/10-12 anni):** `[1.1.0]`
        * `[ ]` i. Obiettivo: Sviluppare competenze intermedie, pensiero critico. `[1.1.0]`
        * `[ ]` ii. Curriculum intermedio. `[1.1.0]`
        * `[ ]` iii. Impatto: Sviluppo skill. `[1.1.0]`
    * `[ ]` e. **Medie Superiori (12/13-15 anni):** `[1.1.0]`
        * `[ ]` i. Obiettivo: Preparazione avanzata. `[1.1.0]`
        * `[ ]` ii. Curriculum avanzato. `[1.1.0]`
        * `[ ]` iii. Impatto: Sviluppo skill. `[1.1.0]`
    * `[ ]` f. **Superiori (15/16-18 anni, obbligatorio):** `[1.1.0]`
        * `[ ]` i. Obiettivo: Preparazione università/lavoro. `[1.1.0]`
        * `[ ]` ii. Curriculum: Materie accademiche avanzate, progetti di ricerca. `[1.1.0]`
        * `[ ]` iii. Impatto: Sviluppo skill avanzate, influenza su opportunità future. `[1.1.0]`
    * `[ ]` g. **Superior Facoltativo (18/19-21 anni):** `[1.2.0]`
        * `[ ]` i. Obiettivo: Specializzazione per accesso università. `[1.2.0]`
        * `[ ]` ii. Curriculum: Materie di specializzazione, ricerca, stage. `[1.2.0]`
        * `[ ]` iii. Impatto: Forte influenza su accesso/successo universitario. `[1.2.0]`
    * `[ ]` h. **Università (21+ anni):** `[1.2.0]`
        * `[ ]` i. Obiettivo: Educazione approfondita e specialistica. `[1.2.0]`
        * `[ ]` ii. Struttura: Laurea Triennale, Magistrale, Dottorato. `[1.2.0]`
        * `[ ]` iii. Facoltà e Materie Esempio. `[1.2.0]`
        * `[ ]` iv. Programmi di Scambio. `[FUTURO]`
        * `[ ]` v. Impatto: Acquisizione skill altamente specializzate. `[1.2.0]`
    * `[ ]` i. **Registrazione Ufficiale Titoli di Studio e Carriera Accademica:** `[1.1.0]`
        * `[ ]` 1. I diplomi e le lauree sono registrate digitalmente e associate al DID. `[1.1.0]`
        * `[ ]` 2. I documenti sono consultabili dal titolare tramite il portale SoNet. `[1.1.0]`

### **3. Meccaniche Scolastiche per NPC:** `[ ]`
    * `[P]` a. NPC frequentano scuola (azione `ATTENDING_SCHOOL`). `[1.0.0]`
        * `[P]` i. Integrare la frequenza con il nuovo calendario scolastico. `[1.0.0]`
    * `[P]` b. Performance scolastica (`school_performance`, compiti) influenzata da NPC. `[1.0.0]`
        * `[ ]` i. Introdurre un sistema di "voti" formali. `[1.0.1]`
        * `[ ]` ii. Espandere i fattori che influenzano la performance. `[1.0.2]`
    * `[P]` c. Impatto performance su sviluppo abilità. `[1.0.0]`
        * `[ ]` i. La performance influenza lo sviluppo di abilità specifiche. `[1.0.1]`
        * `[ ]` ii. La performance scolastica complessiva influenza aspirazioni e opportunità future. `[1.1.0]`
    * `[ ]` d. "Saltare la scuola" con conseguenze. `[1.0.1]`
    * `[ ]` e. Attività extracurriculari. `[1.1.0]`
    * `[ ]` f. Viaggi educativi. `[1.2.0]`
    * `[ ]` g. Supporto agli Studenti. `[1.1.0]`
    * `[ ]` h. Report Scolastici in TUI. `[1.0.0]`
    * `[ ]` i. Dinamiche di "Bocciatura" e Ripetizione Anno. `[1.1.0]`
        * `[ ]` 1. Definire criteri per la bocciatura. `[1.1.0]`
        * `[ ]` 2. Se un NPC viene "bocciato", ripete l'anno scolastico. `[1.1.0]`
        * `[ ]` 3. Limite di età per la ripetizione. `[1.1.0]`
        * `[ ]` 4. Impatto sull'umore e sulle relazioni. `[1.1.0]`
    * `[ ]` j. Accesso a Informazioni e Servizi Scolastici tramite SoNet. `[1.1.0]`

---

## 🏛️ VI. SISTEMA POLITICO, GOVERNANCE E PARTECIPAZIONE CIVICA IN ANTHALYS `[ ]`

### **1. Struttura Politica e di Governance di Anthalys:** `[ ]`
    * `[x]` a. Definire il tipo di governo di Anthalys come stato sovrano e indipendente. `[1.0.0]`
        * `[P]` i. **Governatore:** Potere esecutivo, eletto democraticamente. `[1.0.0]`
            * `[ ]` 1. Implementare meccanica di elezione democratica del Governatore. `[1.1.0]`
            * `[ ]` 2. Logica per la scelta del nome e la gestione della successione. `[1.1.0]`
        * `[P]` ii. **Parlamento Bicamerale (Camera dei Rappresentanti e Senato):** Potere legislativo. `[1.0.0]`
            * `[ ]` 1. Definire composizione, elezione/nomina e funzioni delle due camere. `[1.1.0]`
            * `[ ]` 2. Estensione "Total Realism" - Processo Legislativo Dettagliato. `[FUTURO]`
        * `[P]` iii. **Potere Giudiziario:** Indipendente, garante di giustizia e legalità. `[1.0.0]`
            * `[ ]` 1. Definire la struttura del sistema giudiziario. `[1.1.0]`
            * `[ ]` 2. Estensione "Total Realism" - Sistema Giudiziario Approfondito. `[2.0.0]`
            * `[ ]` 3. I cittadini possono accedere a informazioni legali di base tramite SoNet. `[1.1.0]`
    * `[P]` c. Cicli elettorali o periodi di mandato per le cariche. `[1.0.0]`
    * `[ ]` d. Partiti Politici e Ideologie. `[1.1.0]`
        * `[ ]` i. Definire 2-4 principali correnti ideologiche o partiti politici. `[1.1.0]`
        * `[P]` ii. Gli NPC possono avere un'affiliazione politica. `[1.1.0]`
        * `[ ]` iii. Tratti come `FEMINIST`, `ACTIVIST` influenzano l'affiliazione. `[1.1.0]`
        * `[ ]` iv. I partiti possono avere un "indice di popolarità" che fluttua. `[1.2.0]`

### **2. Partecipazione Civica e Politica degli NPC:** `[ ]`
    * `[P]` a. I tratti di personalità degli NPC influenzano le loro opinioni politiche. `[1.0.0]`
        * `[P]` i. Diritto di Voto e registrazione tramite SoNet. `[1.0.0]`
    * `[ ]` b. Bias Cognitivi Semplificati (Molto Avanzato). `[FUTURO]`
    * `[ ]` c. Decisione di Voto. `[1.1.0]`
        * `[ ]` i. NPC (dettagliati e di background) decidono se votare e per chi. `[1.1.0]`
        * `[ ]` ii. Fattori influenzanti: tratti, `political_leaning`, `general_wellbeing`. `[1.1.0]`
        * `[ ]` iii. (Avanzato) "Voto Basato su Identità vs. Policy". `[1.2.0]`
    * `[ ]` d. Influenza delle Reti Sociali (Astratta). `[1.2.0]`
    * `[ ]` e. Alfabetizzazione Mediatica e Flusso di Informazioni. `[1.2.0]`
        * `[ ]` i. NPC con alta alfabetizzazione mediatica sono meno suscettibili a disinformazione. `[1.2.0]`
        * `[ ]` ii. Estensione "Total Realism" - Ecosistema dell'Informazione. `[FUTURO]`
    * `[ ]` f. Attivismo e Candidatura. `[1.1.0]`
        * `[ ]` i. NPC con tratti rilevanti possono decidere di candidarsi per cariche elettive. `[1.1.0]`
        * `[ ]` ii. Possono partecipare ad attività di campagna. `[1.1.0]`
    * `[ ]` g. Interazione Civica tramite SoNet (Consultazioni, Petizioni). `[1.1.0]`

### **3. Simulazione di Elezioni e Campagne Elettorali:** `[ ]`
    * `[P]` a. La simulazione gestisce elezioni periodiche. `[1.1.0]`
    * `[ ]` b. Candidati. `[1.1.0]`
        * `[ ]` i. NPC (dettagliati o di background) possono diventare candidati. `[1.1.0]`
        * `[ ]` ii. I candidati hanno una "piattaforma" e un "budget". `[1.1.0]`
        * `[ ]` iii. Le informazioni sui candidati sono consultabili tramite SoNet. `[1.1.0]`
    * `[ ]` c. Campagna Elettorale (Astratta per Ora). `[1.1.0]`
        * `[ ]` i. I candidati compiono azioni di campagna. `[1.1.0]`
        * `[ ]` ii. (Futuro) Gestione del budget di campagna. `[1.2.0]`
    * `[ ]` d. Eventi Durante la Campagna. `[1.2.0]`
        * `[ ]` i. Eventi casuali (scandali, gaffe, endorsement). `[1.2.0]`
        * `[ ]` ii. (Futuro) Dibattiti pubblici tra candidati. `[1.2.0]`
    * `[ ]` e. Simulazione del Voto. `[1.1.0]`
        * `[ ]` i. Al giorno delle elezioni, gli NPC esprimono la loro preferenza. `[1.1.0]`
        * `[ ]` ii. Conteggio dei voti e determinazione del vincitore. `[1.1.0]`
    * `[ ]` f. Sistemi Elettorali Diversi (Molto Avanzato). `[FUTURO]`
    * `[ ]` g. Generazione e Persistenza Candidati. `[1.1.0]`

### **4. Sistema di Referendum:** `[ ]`
    * `[ ]` a. Definire meccanismi per cui un referendum può essere indetto. `[1.2.0]`
    * `[ ]` b. I referendum pongono quesiti specifici ai cittadini. `[1.2.0]`
    * `[ ]` c. Gli NPC votano sul referendum in base ai loro tratti e `political_leaning`. `[1.2.0]`
    * `[ ]` d. L'esito del referendum ha un impatto diretto sulle leggi. `[1.2.0]`
    * `[ ]` e. Campagne pro/contro il quesito referendario. `[1.2.0]`

### **5. Generazione di Contenuti Testuali (NLG) a Tema Politico:** `[ ]`
    * `[ ]` a. "Pensieri" politici degli NPC. `[1.1.0]`
    * `[ ]` b. (Futuro) Generazione di slogan elettorali, sunti di discorsi. `[1.2.0]`

### **6. Simboli Nazionali e Culturali:** `[ ]`
    * `[P]` a. Bandiera di Anthalys. `[1.0.0]`
    * `[x]` b. Calendario Ufficiale. `[1.0.0]`
    * `[P]` c. Inno Nazionale. `[1.0.0]`
    * `[P]` d. Motto Nazionale. `[1.0.0]`

### **7. Emendamenti Costituzionali e Revisione:** `[ ]`
    * `[ ]` a. (Molto Avanzato) Meccanica per emendare la Costituzione. `[FUTURO]`
    * `[ ]` b. Estensione "Total Realism" - Evoluzione Legale Dinamica. `[FUTURO]`

### **8. Integrazione Dati, Parametrizzazione e Validazione:** `[ ]`
    * `[ ]` a. Bilanciare le probabilità di voto e l'influenza dei fattori. `[1.1.0]`
    * `[ ]` b. Calibrare l'impatto degli eventi politici sull'umore e sul comportamento. `[1.1.0]`

### **9. IA e LLM (Obiettivi a Lungo Termine):** `[ ]`
    * `[ ]` a. (Molto Lontano Futuro) Usare LLM per generare dibattiti e discorsi. `[FUTURO]`

---

## 💬 VII. DINAMICHE SOCIALI E RELAZIONALI AVANZATE `[ ]`

### **1. Sistema di Relazioni e Dinamiche di Coppia (Adulti Monogami):** `[P]`
    * `[x]` a. Punteggi di relazione e Tipi di relazione (`RelationshipType` Enum). `[1.0.0]`
        * `[ ]` i. Logica per transizione tra tipi. `[1.0.1]`
        * `[ ]` ii. Introduzione di `RelationshipType.DATING` come stato intermedio. `[1.0.1]`
    * `[P]` b. **Formazione della Coppia (Default Monogama):** `[1.0.0]`
        * `[x]` i. Esclusività e Transizione. `[1.0.0]`
        * `[ ]` ii. Proposta di Matrimonio/Convivenza. `[1.0.1]`
        * `[ ]` iii. Fasi dell'Avvicinamento (Attrazione, Corteggiamento, Connessione, Affetto). `[1.1.0]`
        * `[ ]` iv. **Bilanciamento Matching Relazioni:** Ridurre le differenze d'età massime consentite e aumentare l'età minima per gli appuntamenti (18 anni). `[1.0.1]`
    * `[P]` c. **Mantenimento della Coppia:** `[1.0.0]`
        * `[x]` i. Bisogno di Intimità Reciproca. `[1.0.0]`
        * `[ ]` ii. Comunicazione e Tempo di Qualità. `[1.0.1]`
        * `[ ]` iii. **Persistenza Emotiva Residua:** Aggiungere una variabile che traccia la sensazione che un legame continua ad esistere anche dopo l'interruzione dei contatti. `[1.3.0]`
    * `[P]` d. **Vita Sessuale e Consenso:** `[1.0.0]`
        * `[x]` i. Frequenza guidata dal bisogno `INTIMACY`. `[1.0.0]`
        * `[P]` ii. Meccanismo di Consenso. `[1.0.0]`
        * `[ ]` iii. Pianificazione Familiare (Azione "TryForBaby"). `[1.1.0]`
        * `[ ]` iv. **Desiderio Sessuale come Curva Dinamica:** Simulare una libido con alti e bassi influenzata da ormoni, umore e ricordi. `[1.2.0]`
        * `[ ]` v. **Complicità vs. Meccanicità:** Introdurre una variabile "Intesa Erotica" che cresce con la comunicazione e le esperienze condivise. `[1.3.0]`
        * `[ ]` vi. **Simulazione della Libido Asimmetrica:** Gestire le dinamiche di frustrazione, insicurezza e negoziazione consensuale quando il desiderio nella coppia non è allineato. `[1.3.0]`
        * `[ ]` vii. **Il Sesso come Comunicazione:** Implementare la possibilità di usare il sesso come mezzo per chiedere perdono, combattere la solitudine o recuperare una relazione. `[1.3.0]`
        * `[ ]` viii. **Intimità Senza Sesso:** Definire azioni sostitutive (carezze, dormire insieme) per soddisfare `INTIMACY` per tratti come `Asexual` o `Traumatized`. `[1.2.0]`
        * `[ ]` ix. **La "Chiave" dell'Intimità:** Implementare una funzione "Unlock Intimacy" dove un NPC può concedere o negare l'accesso a livelli più profondi di intimità. `[1.3.0]`
        * `[ ]` x. **Il Bisogno di Essere Amato (Speranza):** Implementare un modulo che simula il desiderio di connessione di un NPC, indipendente dal successo delle sue interazioni, rendendolo più fragile e autentico. `[2.0.0]`
    * `[ ]` e. **Gelosia e Fedeltà:** `[1.1.0]`
        * `[ ]` i. Implementare reazioni negative a flirt esterni alla coppia. `[1.1.0]`
    * `[ ]` f. **Fattori di Accettazione/Rifiuto dell'Intimità (Dettagliati):** `[1.1.0]`
    * `[ ]` g. **Precauzioni (Contraccezione e IST):** `[1.2.0]`
    * `[ ]` h. **Conseguenze dell'Intimità (Positive e Negative):** `[1.1.0]`
    * `[ ]` i. **Fattori Aggiuntivi a Lungo Termine (Adulti):** `[1.2.0]`
    * `[P]` j. **Orientamento Sessuale e Romantico:**
        * `[ ]` vii. **Orientamento Sessuale Dinamico:** Aggiungere una funzione di "fluidità temporanea" o esplorazione durante l'adolescenza, con moodlet specifici ("Dubbioso", "Scoperta"). `[1.2.0]`
    * `[ ]` k. **Educazione Sessuale e Disinformazione:** `[1.3.0]`
        * `[ ]` i. Simulare l'impatto di diversi tipi di educazione ricevuta (sana, repressiva, basata su disinformazione) sull'approccio al consenso e alle relazioni. `[1.3.0]`
        * `[ ]` ii. **Contesto Culturale Ristretto o Distorcente:** Simulare ambienti sociali a rischio con alta probabilità di disinformazione e vulnerabilità. `[1.3.0]`
    * `[ ]` l. **Sesso Virtuale / Digitale:** `[1.3.0]`

### **2. Interazioni Sociali:** `[P]`
    * `[x]` a. Interazioni base (`SOCIALIZING`, `BEING_INTIMATE`) implementate. `[1.0.0]`
    * `[ ]` b. Espandere la varietà e la profondità delle interazioni sociali: `[1.0.1]`
        * `[ ]` i. Implementare azioni sociali specifiche per i tratti. `[1.0.2]`
        * `[ ]` ii. Azioni sociali più generiche ma contestuali (Complimento, Scuse, Consolare). `[1.0.1]`
        * `[ ]` iii. Azioni di Flirt più dettagliate. `[1.1.0]`
        * `[ ]` iv. Interazioni legate a eventi specifici (Condoglianze, Congratulazioni). `[1.1.0]`
        * `[ ]` v. Interazioni Sociali legate all'Ospitalità. `[1.1.0]`
        * `[ ]` vi. Effetti dei Tratti dell'Iniziatore sul Target. `[1.2.0]`
    * `[ ]` c. Interazioni di gruppo. `[1.2.0]`
    * `[ ]` d. Reazioni alle Interruzioni Sociali e all'Attesa. `[1.1.0]`
    * `[P]` e. Il successo/fallimento delle interazioni dipende da skill, tratti, umore, relazione. `[1.0.0]`
    * `[ ]` f. Dialoghi dinamici (testo che riflette la conversazione). `[FUTURO]`
    * `[ ]` g. Estensione "Total Realism" - Comunicazione Non Verbale. `[2.0.0]`
    * `[ ]` h. **Calcolo Logico del Successo Sociale:** `[1.1.0]`
        * `[ ]` i. Sostituire la `success_chance` fissa con un calcolo dinamico. `[1.1.0]`
        * `[ ]` ii. Il calcolo considera: Skill dell'iniziatore (Charisma, Comedy), Umore di entrambi, Punteggio relazione, Tratti compatibili/incompatibili. `[1.1.0]`
    * `[ ]` i. **Sistema di Conversazione Contestuale e Stateful:** `[1.2.0]`
        * `[ ]` i. Creare un oggetto `ConversationState` per tracciare lo stato di una conversazione attiva (partecipanti, argomento attuale, umore della conversazione). `[1.2.0]`
        * `[ ]` ii. Il `SocialManager` gestisce le conversazioni attive, creandole quando due NPC iniziano a parlare e distruggendole quando si allontanano. `[1.2.0]`
        * `[ ]` iii. Espandere `SocialInteractionType` con interazioni contestuali (es. `ASK_ABOUT_HOBBY`, `COMPLAIN_ABOUT_WEATHER`, `CHANGE_TOPIC`, `GIVE_DETAILED_COMPLIMENT`). `[1.2.0]`
        * `[ ]` iv. `SocialSolutionDiscoverer` diventa "conversation-aware": se l'NPC è già in una conversazione, propone interazioni pertinenti all'argomento e all'umore attuali, invece di interazioni generiche. `[1.2.0]`

### **3. Dinamiche di Coppia (Adolescenti):** `[ ]`
    * `[P]` a. Background e Sviluppo Puberale. `[1.2.0]`
    * `[ ]` b. Fasi Relazionali e Accettazione/Rifiuto Intimità (Modificatori Adolescenziali). `[1.2.0]`
    * `[ ]` c. Precauzioni (Adolescenti) - Accesso limitato, uso scorretto. `[1.2.0]`
    * `[ ]` d. Conseguenze dell'Intimità (Adolescenti) - Emotive, sociali, fisiche. `[1.2.0]`
    * `[ ]` e. Fattori Aggiuntivi (Educazione Sessuale, Ruolo Genitori). `[1.2.0]`
    * `[ ]` f. **Contesto Culturale e Familiare Distorcente:** `[2.1.0]`
        * `[ ]` i. NPC cresciuti in ambienti isolati, cultisti o dogmatici possono avere una percezione distorta dei confini e del consenso. `[2.1.0]`
        * `[ ]` ii. La simulazione può rappresentare l'arco narrativo di disillusione e riscoperta di sé di questi NPC. `[2.1.0]`

### **4. Strutture Relazionali Non Monogame (Poliamorosità - Adulti):** `[ ]`
    * `[ ]` a. Adattare la struttura dati di `Character` per partner multipli. `[1.3.0]`
    * `[ ]` b. Setup e Accordi (Negoziazione regole). `[1.3.0]`
    * `[ ]` c. Dinamiche Specifiche (Compersione, Gelosia, Burnout). `[1.3.0]`
    * `[ ]` d. Precauzioni e Rischi Amplificati. `[1.3.0]`
    * `[ ]` e. Conseguenze Specifiche (Positive e Negative). `[1.3.0]`
    * `[ ]` f. Fattori Aggiuntivi (Gestione Tempo, Metarelazioni). `[1.3.0]`

### **5. Dinamiche Relazionali LGBTQ+ (Integrazione Globale):** `[ ]`
    * `[P]` a. Aspetti Fondamentali del Personaggio (Identità, Orientamento). `[1.0.0]`
    * `[ ]` b. Meccaniche Specifiche: `[1.2.0]`
        * `[ ]` i. Coming Out. `[1.2.0]`
        * `[ ]` ii. Discriminazione. `[1.2.0]`
        * `[ ]` iii. Comunità LGBTQ+. `[1.2.0]`
    * `[ ]` c. Considerazioni sulle Relazioni (Same-Sex, Transgender, Ace/Aro). `[1.2.0]`

### **6. Gestione Culturale delle Relazioni Consanguinee:** `[ ]`
    * `[x]` a. Il sistema previene relazioni romantiche tra familiari strettissimi. `[1.0.0]`
    * `[ ]` b. Logica Culturale Modulare basata su `cultural_background`. `[FUTURO]`
    * `[ ]` c. Definire un set di "norme culturali" possibili. `[FUTURO]`
    * `[ ]` d. L'IA per la formazione di coppie deve consultare queste norme. `[FUTURO]`
    * `[ ]` e. Conseguenze sociali e genetiche. `[FUTURO]`

### **7. Eventi Sociali Drastici e Rotture:** `[ ]`
    * `[ ]` a. Azioni di combattimento fisico (`FIGHT_NPC`). `[1.1.0]`
    * `[P]` b. Gestione della morte di un NPC e del lutto. `[1.0.1]`
    * `[ ]` c. Tradimento e Infedeltà. `[1.2.0]`
        * `[ ]` i. Possibilità per NPC di avere relazioni extraconiugali. `[1.2.0]`
        * `[ ]` ii. Sistema di "scoperta" del tradimento. `[1.2.0]`
        * `[ ]` iii. Forti reazioni emotive e relazionali. `[1.2.0]`

### **8. Relazioni Intergenerazionali e Mentoring:** `[ ]`
    * `[ ]` a. Tratti come `GRANDPARENT` influenzano le interazioni. `[1.1.0]`
    * `[ ]` b. Azione `CARE_FOR_ELDERLY_PARENT`. `[1.2.0]`
    * `[ ]` c. (Avanzato) Trasmissione di valori/abitudini dai genitori ai figli. `[FUTURO]`
    * `[ ]` d. Sistema di Mentoring. `[1.1.0]`
        * `[ ]` i. Azione `MENTOR_SKILL_TO_NPC`. `[1.1.0]`
        * `[ ]` ii. L'allievo guadagna skill più velocemente. `[1.1.0]`

### **9. Pettegolezzo e Reputazione (Sistema Futuro):** `[ ]`
    * `[ ]` a. Azione `GOSSIP_ABOUT_NPC` per diffondere pettegolezzi. `[1.2.0]`
    * `[ ]` b. Sistema di "reputazione" per ogni NPC. `[1.2.0]`
    * `[ ]` c. La reputazione influenza le interazioni future. `[1.2.0]`

---

## 💰 VIII. SISTEMA ECONOMICO, LAVORO E WELFARE DI ANTHALYS `[ ]`

* `[P]` **A. Valuta Ufficiale di Anthalys: L'Athel (Ꜳ) Digitale**
    * `[x]` i. L’Athel (simbolo: Ꜳ) è la valuta ufficiale unica di Anthalys. `[1.0.0]`
    * `[x]` ii. Transizione al Digitale Completo. `[1.0.0]`
    * `[P]` iii. Tutte le transazioni finanziarie sono gestite elettronicamente tramite DID e SoNet. `[1.0.0]`
    * `[x]` iv. Benefici della transizione al digitale (lore). `[1.0.0]`
    * `[ ]` v. Athel Fisico Obsoleto (Valore Storico/Collezionistico). `[1.0.1]`
        * `[ ]` 1. (Lore) Descrizione delle vecchie banconote di Athel. `[1.0.1]`
        * `[ ]` 2. (Lore) Tagli delle banconote fisiche obsolete. `[1.0.1]`
        * `[ ]` 3. NPC potrebbero conservare esemplari di Athel fisico come oggetti da collezione. `[1.1.0]`

* `[ ]` **B. Sistema Bancario e Finanziario di Anthalys**
    * `[!]` i. Il sistema bancario di Anthalys è solido, tecnologicamente avanzato e ben regolamentato. `[1.0.0]`
    * `[ ]` ii. **Banca Centrale di Anthalys (BCA):** `[1.1.0]`
        * `[ ]` 1. Definire la Banca Centrale di Anthalys come l'autorità monetaria. `[1.1.0]`
        * `[ ]` 2. Funzioni della BCA (Politica monetaria, stabilità, regolamentazione). `[1.2.0]`
    * `[ ]` iii. **Banche Commerciali di Anthalys:** `[1.1.0]`
        * `[ ]` 1. Definire 2-4 principali brand di Banche Commerciali. `[1.1.0]`
        * `[ ]` 2. Operano sotto la supervisione della BCA. `[1.1.0]`
        * `[ ]` 3. Servizi Finanziari Offerti: `[1.1.0]`
            * `[P]` a. Conti Correnti Digitali collegati al DID/SoNet. `[1.0.0]`
            * `[ ]` b. Conti di Risparmio. `[1.1.0]`
            * `[ ]` c. Prestiti Personali e Mutui Immobiliari. `[1.2.0]`
            * `[ ]` d. Finanziamenti alle Imprese. `[1.2.0]`
            * `[ ]` e. Servizi di Investimento (Semplificati). `[1.3.0]`
            * `[P]` f. Distribuzione dell'Athel Digitale. `[1.0.0]`
        * `[ ]` 4. Carriere Bancarie. `[1.1.0]`
    * `[ ]` iv. **Altri Istituti Finanziari (Opzionale):** `[FUTURO]`

* **1. Lavoro e Carriere per NPC:** `[P]`
    * `[P]` a. Struttura delle Carriere e dei Lavori. `[1.0.0]`
        * `[x]` i. Definire `CareerTrackName` e `CareerCategory` Enum. `[1.0.0]`
        * `[x]` ii. Definire classi base `BaseCareerLevel` e `BaseCareerTrack`. `[1.0.0]`
        * `[ ]` iii. Popolare le definizioni dettagliate delle carriere. `[1.0.1]`
        * `[P]` iv. Implementare un `CareerManager`. `[1.0.0]`
        * `[ ]` v. Gestire modelli di orario specifici per professione. `[1.1.0]`
        * `[x]` vi. Lavorare soddisfa il bisogno di "Reddito". `[1.0.0]`
        * `[P]` vii. Sistema di performance lavorativa. `[1.0.0]`
        * `[ ]` viii. Eventi lavorativi. `[1.1.0]`
        * `[ ]` ix. Possibilità di carriere freelance, part-time, o lavori saltuari. `[1.1.0]`
        * `[P]` x. Pensionamento. `[1.0.0]`
    * `[x]` b. Orario di Lavoro Standard e Settimanale. `[1.0.0]`
    * `[P]` c. Stipendi e Politiche Retributive. `[1.0.0]`
        * `[P]` i. Tracciare attributi salariali in `Character` e `BackgroundNPCState`. `[1.0.0]`
        * `[ ]` ii. Implementare logica per il calcolo degli scatti di anzianità. `[1.0.1]`
    * `[P]` d. IA per Gestione Carriera NPC. `[1.0.0]`
        * `[ ]` i. Azione `SEEK_JOB` per NPC disoccupati. `[1.0.1]`
        * `[P]` ii. Logica di `AIDecisionMaker` per la scelta della carriera. `[1.0.0]`
        * `[ ]` iii. Il tratto `CONNECTIONS` modifica il livello di partenza. `[1.0.2]`
        * `[P]` iv. NPC scelgono azione `WORKING`. `[1.0.0]`
        * `[ ]` v. Logica per tentare promozioni. `[1.0.1]`
    * `[P]` f. Performance Lavorativa (calcolo e aggiornamento). `[1.0.0]`
    * `[ ]` g. Meccaniche di avvertimenti, retrocessioni, licenziamenti. `[1.1.0]`
    * `[P]` h. Lavoro Minorile e Part-time. `[1.0.0]`
    * `[ ]` i. "Side Gigs" (Lavoretti Extra). `[1.1.0]`
    * `[ ]` j. Elenco Carriere (Implementare le classi per ogni carriera). `[1.0.1]`
    * `[ ]` k. Estensione "Total Realism" - Imprenditorialità e Gestione Aziendale NPC. `[2.0.0]`
    * `[ ]` l. **Attributo Finanziario Base del Personaggio:** `[1.0.1]`
        * `[ ]` i. Aggiungere `self.money: float` alla classe `Character` per tracciare i fondi personali. `[1.0.1]`

* **2. Sistema Fiscale e Finanze Pubbliche (Contributo al Sostentamento Civico - CSC):** `[P]`
    * `[!]` a. Principio del CSC. `[1.0.0]`
    * `[P]` b. CSC-R (Componente sul Reddito Personale). `[1.0.0]`
        * `[P]` i. Sistema di imposte progressive sul reddito. `[1.0.0]`
        * `[x]` ii. Scaglioni di Reddito e Aliquote CSC-R. `[1.0.0]`
    * `[P]` c. Procedure di Dichiarazione e Riscossione del CSC. `[1.0.0]`
        * `[P]` i. Gestire procedure di dichiarazione e riscossione. `[1.0.0]`
        * `[ ]` ii. Comunicazioni fiscali tramite SoNet. `[1.0.1]`
    * `[P]` d. Entità "Governo di Anthalys" e Gestione Finanze Pubbliche. `[1.0.0]`
        * `[P]` i. Definire classe/oggetto `AnthalysGovernment`. `[1.0.0]`
        * `[P]` ii. Attributo `treasury` per tracciare entrate/uscite. `[1.0.0]`
        * `[ ]` vii. Politica Fiscale e di Spesa del Governo (Incentivi, agevolazioni). `[1.2.0]`
    * `[ ]` e. CSC-A (Componente su Attività Commerciali). `[1.1.0]`
    * `[ ]` f. CSC-S (Componente su Scommesse e Giochi d'Azzardo). `[1.2.0]`
    * `[ ]` g. CSC-P (Componente sul Patrimonio Immobiliare). `[1.1.0]`
    * `[P]` h. CSC-C (Componente sul Consumo). `[1.0.0]`

* **3. Benefici, Sicurezza Sociale e Welfare:** `[P]`
    * `[P]` a. Implementazione Assicurazione Sanitaria Universale. `[1.0.0]`
    * `[P]` b. Implementazione del sistema di Pensioni. `[1.0.0]`
    * `[ ]` c. Implementazione di Indennità di Maternità/Paternità. `[1.1.0]`
    * `[ ]` d. Implementazione di Norme su Sicurezza sul Lavoro. `[1.1.0]`
    * `[ ]` e. Sostegno Specifico per Famiglie e Minori. `[1.2.0]`
    * `[ ]` f. Sistema di giorni di ferie. `[1.1.0]`
    * `[ ]` g. Bonus di fine anno o legati alla performance. `[1.1.0]`
    * `[ ]` h. Permessi per Emergenze Familiari. `[1.1.0]`

* **4. Vacanze e Permessi Lavorativi:** `[ ]` `[1.1.0]`
* **5. Economia Globale Astratta (Molto Futuro):** `[ ]` `[FUTURO]`
* **6. Sistema Commerciale Centralizzato: "AION"** `[P]`
    * `[!]` a. Principio Fondamentale: AION come piattaforma unica di commercio. `[1.0.0]`
    * `[P]` b. Impatto Economico Generale e Interazioni Sistemiche. `[1.0.0]`
    * `[ ]` **1. Funzionamento e Struttura di AION:** `[1.0.1]`
        * `[P]` a. Piattaforma Tecnologica di Backend. `[1.0.0]`
        * `[ ]` b. Gestione Catalogo Prodotti e Approvvigionamento (IA). `[1.1.0]`
        * `[P]` c. Controllo IA al 100% ("Autonomia Operativa Totale"). `[1.0.0]`
        * `[ ]` d. Piattaforma di Acquisto e Vendita per Produttori Locali (C2A/B2A). `[1.2.0]`
    * `[ ]` **2. Politiche di Prezzi e Sconti di AION (gestite dall'IA):** `[1.1.0]`
    * `[ ]` **3. Logistica di Consegna Avanzata di AION:** `[1.1.0]`
    * `[ ]` **4. Rapporto di AION con i Negozi Fisici:** `[1.1.0]`
    * `[ ]` **5. Operazioni Logistiche e Distribuzione Interne di AION:** `[1.1.0]`
    * `[ ]` **6. Magazzini Sotterranei di AION:** `[1.1.0]`
    * `[ ]` **7. Tecnologia di Monitoraggio e Gestione dei Magazzini AION:** `[1.1.0]`
    * `[ ]` **8. Impatto Economico e Integrazione di Mercato di AION:** `[1.2.0]`
    * `[ ]` **9. Sostenibilità e Efficienza Energetica di AION:** `[1.2.0]`
    * `[ ]` **10. Sistemi di Sicurezza Avanzata dei Magazzini AION:** `[1.1.0]`
    * `[ ]` **11. Monitoraggio Performance e Reportistica Aggregata:** `[1.2.0]`
    * `[ ]` **12. Sistema di Feedback dei Cittadini e Apprendimento Adattivo dell'IA:** `[1.2.0]`

---

## 🛠️ IX. ABILITÀ (SKILLS) `[ ]`

* `[P]` a. **Struttura Base per le Abilità:**
    * `[x]` i. `SkillType` Enum definita e mantenuta in categorie. `[1.0.0]`
    * `[P]` ii. Creare una classe `BaseSkill` in `modules/skills/base_skill.py`. `[1.0.0]`
        * `[P]` 1. Gestire livelli di abilità. `[1.0.0]`
        * `[P]` 2. Gestire Punti Esperienza (XP). `[1.0.0]`
        * `[P]` 3. Logica di progressione ai livelli successivi. `[1.0.0]`
        * `[ ]` 4. Implementare la progressione di XP specifica per livello. `[1.0.1]`
    * `[P]` iii. Creare classi specifiche per ogni `SkillType`. `[1.0.0]`
        * `[P]` 1. Ogni classe Skill specifica può sovrascrivere la curva XP o aggiungere benefici unici. `[1.0.0]`
    * `[ ]` iv. Modificare `Character.skills` per contenere istanze delle classi Skill. `[1.0.0]`
    * `[ ]` v. Modificare la logica di guadagno skill per usare il metodo `add_experience()`. `[1.0.1]`
    * `[ ]` vi. Libri per apprendere abilità più velocemente. `[1.1.0]`
    * `[ ]` vii. Possibilità di "Mentoring" da NPC con abilità più alta. `[1.1.0]`
* `[ ]` b. **IA per Scelta Sviluppo Abilità:** `[1.1.0]`
    * `[ ]` i. Gli NPC decidono attivamente quali abilità migliorare. `[1.1.0]`
* `[P]` c. **Abilità influenzano azioni e loro esiti.** `[1.0.0]`
    * `[P]` i. Espandere il set di abilità e il loro impatto. `[1.0.1]`
    * `[ ]` ii. Definire azioni specifiche per l'apprendimento attivo. `[1.0.1]`
    * `[ ]` iii. Le skill sbloccano interazioni sociali o azioni uniche. `[1.0.2]`
    * `[ ]` iv. Il livello di una skill influenza la probabilità di successo e la qualità dell'esito. `[1.1.0]`
    * `[ ]` v. (Avanzato) Sistema di "decadimento skill". `[FUTURO]`
* `[P]` d. **Gestione Skill per NPC di Background (LOD3):** `[1.1.0]`
    * `[P]` i. Gli NPC di background tracciano solo un numero limitato di `key_skills`. `[1.1.0]`
    * `[ ]` ii. La progressione di queste `key_skills` avviene durante gli "heartbeat" periodici. `[1.1.0]`
* `[ ]` e. **Elenco Abilità (da implementare o dettagliare):** `[1.0.1]`
    * `[ ]` Acting (Recitazione) `[1.1.0]`
    * `[ ]` Archaeology (Archeologia) `[1.2.0]`
    * `[ ]` Baking (Pasticceria) `[1.0.2]`
    * `[P]` Battery Drum (Batteria) `[1.0.0]`
    * `[ ]` Bowling `[1.2.0]`
    * `[P]` Cello (Violoncello) `[1.0.0]`
    * `[P]` Charisma (Carisma) `[1.0.0]`
    * `[ ]` Comedy (Commedia) `[1.1.0]`
    * `[ ]` Communication (Toddler Skill) `[1.1.0]`
    * `[P]` Cooking (Cucina) `[1.0.0]`
    * `[ ]` Creativity (Child Skill) `[1.1.0]`
    * `[ ]` Cross-Stitch (Punto Croce) `[1.2.0]`
    * `[ ]` DJ Mixing `[1.1.0]`
    * `[ ]` Dancing (Ballo) `[1.0.2]`
    * `[P]` Driving (Guida) `[1.0.0]`
    * `[ ]` Entrepreneur (Imprenditore) `[1.2.0]`
    * `[ ]` Fabrication `[1.1.0]`
    * `[ ]` Fishing (Pesca) `[1.0.2]`
    * `[P]` Fitness `[1.0.0]`
    * `[ ]` Flower Arranging `[1.1.0]`
    * `[P]` Gardening (Giardinaggio) `[1.0.0]`
    * `[ ]` Gourmet Cooking `[1.0.2]`
    * `[P]` Guitar (Chitarra) `[1.0.0]`
    * `[P]` Handiness (Manualità) `[1.0.0]`
    * `[ ]` Herbalism (Erboristeria) `[1.1.0]`
    * `[ ]` Imagination (Toddler Skill) `[1.1.0]`
    * `[ ]` Juice Fizzing `[1.2.0]`
    * `[ ]` Knitting (Lavoro a Maglia) `[1.2.0]`
    * `[P]` Logic (Logica) `[1.0.0]`
    * `[P]` Lute (Liuto) `[1.0.0]`
    * `[ ]` Media Production `[1.2.0]`
    * `[ ]` Mental (Child Skill) `[1.1.0]`
    * `[ ]` Mischief (Malizia) `[1.1.0]`
    * `[ ]` Mixology `[1.0.2]`
    * `[ ]` Motor (Child Skill) `[1.1.0]`
    * `[ ]` Movement (Toddler Skill) `[1.1.0]`
    * `[ ]` Nectar Making `[1.2.0]`
    * `[P]` Negotiation (Negoziazione) `[1.0.0]`
    * `[P]` Painting (Pittura) `[1.0.0]`
    * `[ ]` Parenting (Genitorialità) `[1.1.0]`
    * `[ ]` Photography (Fotografia) `[1.1.0]`
    * `[P]` Piano (Pianoforte) `[1.0.0]`
    * `[ ]` Pipe Organ `[1.2.0]`
    * `[ ]` Pottery (Ceramica) `[1.1.0]`
    * `[ ]` Potty (Toddler Skill) `[1.1.0]`
    * `[ ]` Potion Making (Preparazione Infusi/Decotti) `[1.2.0]`
    * `[P]` Programming (Programmazione) `[1.0.0]`
    * `[ ]` Research & Debate `[1.1.0]`
    * `[P]` Robotics (Robotica) `[1.0.0]`
    * `[ ]` Rocket Science `[1.3.0]`
    * `[P]` Saxophone (Sassofono) `[1.0.0]`
    * `[ ]` Singing (Canto) `[1.0.2]`
    * `[ ]` Social (Child Skill) `[1.1.0]`
    * `[P]` Tinker (Armeggiare/Smacchinare) `[1.0.0]`
    * `[P]` Trumpet (Tromba) `[1.0.0]`
    * `[P]` Video Gaming `[1.0.0]`
    * `[P]` Violin (Violino) `[1.0.0]`
    * `[ ]` Wellness (Benessere) `[1.1.0]`
    * `[P]` Writing (Scrittura) `[1.0.0]`
    * `[ ]` **(Aggiungere le altre abilità dalla lista estesa)** `[1.1.0+]`
    * `[ ]` **Abilità legate al "Sistema di Produzione Sostenibile":** `[DLC]`
* `[ ]` f. **Estensione "Total Realism" - Apprendimento Contestuale e Maestria:** `[FUTURO]`
    * `[ ]` i. Apprendimento Basato sull'Esperienza e la Sfida. `[FUTURO]`
    * `[ ]` ii. Maestria e Riconoscimento (Opere Maestre). `[FUTURO]`
    * `[ ]` iii. Applicazione Interdisciplinare delle Abilità. `[FUTURO]`
    * `[ ]` iv. Decadimento Realistico delle Abilità (Opzionale). `[FUTURO]`

---

## 🎨 X. INTERESSI, HOBBY E ABILITÀ PRATICHE `[ ]`

### **1. Definizione e Gestione degli Interessi/Hobby:** `[ ]`
    * `[P]` a. Identificare una lista di potenziali interessi/hobby. `[1.0.0]`
    * `[P]` b. Ogni NPC ha 1-3 interessi/hobby "attivi". `[1.0.0]`
    * `[P]` c. L'IA (`AIDecisionMaker`) considera questi interessi/hobby nella scelta delle azioni. `[1.0.0]`
    * `[x]` d. I tratti di personalità influenzano la preferenza per gli hobby. `[1.0.0]`

### **2. Impatto degli Hobby/Interessi:** `[ ]`
    * `[x]` a. Praticare un hobby/interesse soddisfa primariamente il bisogno `FUN`. `[1.0.0]`
    * `[ ]` b. Può contribuire a ridurre lo stress. `[1.1.0]`
    * `[P]` c. Porta allo sviluppo di `SkillType` specifiche correlate. `[1.0.0]`
    * `[ ]` d. (Avanzato) Può portare alla creazione di "opere" o oggetti. `[1.1.0]`
    * `[ ]` e. (Avanzato) Può sbloccare interazioni sociali uniche. `[1.1.0]`

### **3. Abilità Pratiche (Non necessariamente Hobby):** `[ ]`
    * `[P]` a. Alcune `SkillType` rappresentano abilità pratiche utili. `[1.0.0]`
    * `[P]` b. Gli NPC usano queste skill per azioni di routine. `[1.0.0]`
    * `[P]` c. Il livello di queste skill influenza l'efficacia e la qualità dell'esito. `[1.0.0]`

### **4. Sistema di Creazione Oggetti/Opere (Crafting/Produzione):** `[ ]`
    * `[P]` a. NPC con tratti/skill appropriate possono creare oggetti o opere. `[1.0.1]`
    * `[ ]` b. Implementare un sistema di "ricette" o "schemi" per il crafting. `[1.0.1]`
    * `[P]` c. Gli oggetti/opere prodotti hanno livelli di qualità. `[1.0.1]`
    * `[ ]` d. Gli oggetti/opere possono essere usati, esposti, regalati o venduti. `[1.1.0]`
    * `[ ]` e. Completare un'opera significativa dà un forte moodlet positivo. `[1.1.0]`

### **5. Sistema di Cucina e Cibo:** `[P]`
    * `[ ]` a. Definire ricette e tipi di cibo. `[1.0.1]`
    * `[P]` b. Implementare livelli di qualità per il cibo prodotto. `[1.0.0]`
    * `[P]` c. Azioni di cucina producono cibo con qualità influenzata da skill e tratti. `[1.0.0]`
    * `[P]` d. Mangiare cibo di alta qualità ha un impatto maggiore su `HUNGER` e umore. `[1.0.0]`
    * `[ ]` e. (Futuro) Ingredienti e loro impatto sulla qualità/tipo di piatto. `[1.2.0]`

### **6. Sistema di Giardinaggio:** `[P]`
    * `[P]` a. NPC con tratti `GREEN_THUMB` si dedicano al giardinaggio. `[1.0.0]`
    * `[ ]` b. Implementare azioni di giardinaggio. `[1.0.1]`
    * `[ ]` c. Le piante hanno stati di crescita e bisogno di cure. `[1.0.1]`
    * `[ ]` d. Il raccolto può produrre cibo o essere venduto. `[1.1.0]`
    * `[ ]` e. Qualità del raccolto influenzata da skill `GARDENING` e tratti. `[1.1.0]`

### **7. Sistema di Collezionismo:** `[ ]`
    * `[ ]` a. NPC con tratto `OBSESSIVE_COLLECTOR` sono spinti a collezionare. `[1.1.0]`
    * `[ ]` b. Definire tipi di collezionabili con rarità. `[1.1.0]`
    * `[ ]` c. Collezionismo di Athel Fisico Obsoleto. `[1.1.0]`
        * `[ ]` i. Le vecchie banconote e monete sono oggetti da collezione. `[1.1.0]`
        * `[ ]` ii. NPC possono cercare, acquistare, vendere o scambiare Athel fisico. `[1.1.0]`
        * `[ ]` iii. Il valore collezionistico dipende dalla rarità. `[1.1.0]`
    * `[ ]` d. Implementare azioni per trovare/acquistare/scambiare collezionabili. `[1.1.0]`
    * `[P]` e. Gli NPC necessitano di un `Inventario`. `[1.0.0]`
    * `[ ]` f. Completare una collezione dà un forte moodlet positivo. `[1.1.0]`
    * `[ ]` g. Azione `ADMIRE_COLLECTION`. `[1.1.0]`

### **8. Estensione "Total Realism" - Profondità e Impatto Culturale:** `[ ]` `[FUTURO]`
    * `[ ]` a. Sviluppo Personale attraverso gli Hobby. `[FUTURO]`
    * `[ ]` b. Creazioni Uniche e di Rilievo. `[FUTURO]`
    * `[ ]` c. Impatto Culturale e Sociale delle Opere. `[FUTURO]`
    * `[ ]` d. Consumo Critico di Media e Hobby. `[FUTURO]`

### **9. Elenco Azioni Generali:** `[P]`
    * `[x]` a. NPC compiono azioni per soddisfare bisogni, whims, obiettivi. `[1.0.0]`
    * `[P]` b. Le azioni hanno una durata, impatto su bisogni, XP, moodlet. `[1.0.0]`
    * `[P]` Write Book (Scrivi un Libro). `[1.0.1]`
    * `[P]` Practice Musical Instrument. `[1.0.1]`
    * `[P]` Read Book (Leggi un Libro). `[1.0.1]`
    * `[ ]` Attend Concert/Show. `[1.1.0]`
    * `[ ]` **Azioni per soddisfare la Sete:** `[1.0.0]`
        * `[ ]` i. `DRINK_WATER_TAP`. `[1.0.0]`
        * `[ ]` ii. `DRINK_WATER_BOTTLE`. `[1.0.0]`
        * `[ ]` iii. `DRINK_JUICE`. `[1.0.1]`
        * `[ ]` iv. `DRINK_SODA`. `[1.0.1]`
        * `[ ]` v. `DRINK_MILK`. `[1.0.1]`
        * `[ ]` vi. `DRINK_COFFEE_TEA`. `[1.0.1]`
        * `[ ]` vii. `ORDER_DRINK_AT_BAR`. `[1.1.0]`
        * `[ ]` viii. `DRINK_FROM_FOUNTAIN`. `[1.0.1]`
        * `[ ]` ix. `QUENCH_THIRST_WITH_FRUIT`. `[1.0.2]`
    * `[ ]` Molte altre azioni menzionate nei dettagli delle skill e dei tratti. `[1.0.1+]`

---

### 🖥️ XI. INTERFACCIA UTENTE (UI) E INTERAZIONE GIOCATORE `[ ]`

* **1. Interfaccia Grafica (GUI - Pygame):** `[P]`
    * `[x]` a. Definire una classe `Renderer`. `[1.0.0]`
    * `[x]` b. Inizializzazione di Pygame, creazione della finestra di gioco. `[1.0.0]`
    * `[P]` c. Loop di gioco principale (gestione eventi, update, rendering). `[1.0.0]`
        * `[x]` i. Gestione evento `QUIT`. `[1.0.0]`
        * `[x]` ii. Gestione evento `VIDEORESIZE`. `[1.0.0]`
        * `[P]` iii. Gestione input da tastiera base. `[1.0.0]`
        * `[P]` iv. Gestione input da mouse base. `[1.0.0]`
    * `[x]` d. Funzione base di rendering. `[1.0.0]`
    * `[x]` e. Clock per gestione FPS. `[1.0.0]`
    * `[x]` f. Integrazione pulita di `pygame.quit()`. `[1.0.0]`
    * `[P]` g. Possibilità di visualizzare testo base sullo schermo. `[1.0.0]`
    * `[P]` h. Struttura per disegnare entità base della simulazione. `[1.0.0]`
        * `[x]` i. Funzione per disegnare un NPC (come cerchio). `[1.0.0]`
        * `[P]` ii. Indicatore Visivo per NPC Selezionato (il "Focus Astrale"). `[1.0.1]`
        * `[x]` iii. Funzione per disegnare un oggetto (da spritesheet). `[1.0.0]`
        * `[x]` iv. Implementare un sistema di "telecamera" (offset, zoom). `[1.0.0]`
        * `[x]` v. **Disegnare il mondo con una mappa a mattonelle (Tilemap).** `[1.0.0]`
            * `[ ]` 1. Disegnare un indicatore visivo (es. un rombo o un cristallo stilizzato fluttuante) sopra la testa dell'NPC attualmente selezionato dal giocatore. `[1.0.1]`
            * `[ ]` 2. Il colore del Focus Astrale cambia in base all'umore generale dell'NPC selezionato (es. verde per felice, blu per triste, rosso per arrabbiato). `[1.0.2]`
        * `[P]` iii. Funzione per disegnare un oggetto. `[1.0.0]`
        * `[P]` iv. Implementare un sistema di "telecamera" (offset, zoom). `[1.0.0]`
    * `[P]` i. Collegamento con `Simulation.run()`: la GUI deve guidare il loop principale. `[1.0.0]`
    * `[x]` j. Sviluppare la GUI in parallelo alla TUI. `[1.0.0]`
    * `[x]` k. La TUI verrà utilizzata in caso di `DEBUG_MODE=True`. `[1.0.0]`
    * `[x]` l. La finestra base è 1280x768 ridimensionabile. `[1.0.0]`

### **2. TUI: Core UI (Struttura e Componenti Base):** `[P]`
    * `[P]` a. Scheletro UI `curses` con finestre principali. `[1.0.0]`
    * `[P]` b. Gestione input da tastiera (`input_handler.py`). `[1.0.0]`
    * `[ ]` c. **Command Palette:** `[1.1.0]`
        * `[ ]` i. Implementare una palette di comandi attivabile. `[1.1.0]`
        * `[ ]` ii. Lista comandi definita in `settings.py`. `[1.1.0]`
    * `[ ]` d. **Widget Personalizzati:** `[1.1.0]`
        * `[ ]` i. Creare un modulo `modules/ui/widgets.py`. `[1.1.0]`
        * `[ ]` ii. Esempio: `NeedBar`. `[1.1.0]`
        * `[ ]` iii. (Futuro) Widget per grafici, tabelle. `[1.2.0]`
    * `[x]` e. Gestione dei colori. `[1.0.0]`
    * `[ ]` f. Adattabilità della UI a diverse dimensioni del terminale. `[1.0.1]`
    * `[P]` g. Feedback visivo per l'utente. `[1.0.0]`

### **3. TUI: Visualizzazione Dati e Informazioni NPC:** `[P]`
    * `[P]` a. **Lista NPC:** `[1.0.0]`
        * `[P]` i. Mostra informazioni base. `[1.0.0]`
        * `[ ]` ii. Mostra icone per ciclo mestruale e fertilità. `[1.2.0]`
        * `[x]` iii. Selezione NPC con frecce. `[1.0.0]`
        * `[ ]` iv. Implementare scrolling verticale. `[1.0.1]`
    * `[P]` b. Log Eventi/Pensieri. `[1.0.0]`
    * `[P]` c. **Schede Dettagli NPC:** `[1.0.0]`
        * `[P]` i. Scheda "Bisogni". `[1.0.0]`
        * `[P]` ii. Scheda "Lavoro/Scuola". `[1.0.0]`
        * `[P]` iii. Scheda "Abilità". `[1.0.0]`
        * `[P]` iv. Scheda "Relazioni". `[1.0.0]`
        * `[ ]` v. Scheda "Aspirazioni". `[1.0.1]`
        * `[P]` vi. Scheda "Inventario". `[1.0.0]`
        * `[P]` vii. Scheda "Tratti". `[1.0.0]`
        * `[ ]` viii. Scheda "Memorie". `[1.1.0]`
        * `[ ]` ix. Implementare scrolling verticale interno alle schede. `[1.0.1]`
    * `[ ]` d. Diagrammi Relazioni Semplificati (Testuali). `[1.1.0]`
    * `[ ]` e. Timeline Eventi NPC (Semplificata). `[1.1.0]`

### **4. TUI: Dashboard di Sistema (Informazioni Globali):** `[ ]`
    * `[ ]` a. Creare una nuova schermata/pannello. `[1.1.0]`
    * `[ ]` b. Informazioni da mostrare (conteggi NPC, nascite/morti, data). `[1.1.0]`
    * `[ ]` c. (Futuro) Grafici testuali semplici. `[1.2.0]`

### **5. TUI: Navigazione e Interattività Avanzata:** `[P]`
    * `[x]` a. Navigazione focus tra pannelli con TAB. `[1.0.0]`
    * `[x]` b. Navigazione tra le schede NPC con frecce SINISTRA/DESTRA. `[1.0.0]`
    * `[ ]` c. Tasti rapidi per accedere a schede specifiche. `[1.0.1]`
    * `[P]` d. Rendere il feedback visivo sul focus più chiaro. `[1.0.0]`
    * `[ ]` e. Shortcut contestuali visualizzati nella Command Bar. `[1.1.0]`
    * `[P]` f. Menu impostazioni (`curses`) per modificare `settings.json`. `[1.0.0]`
        * `[ ]` i. Espandere opzioni modificabili nel menu. `[1.0.1]`

---

## 💳 XII. DOCUMENTO DI IDENTITÀ DI ANTHALYS E SERVIZI INTEGRATI `[ ]`

* `[!]` a. **Principio Fondamentale:** Il Documento di Identità Digitale (DID) è il mezzo di identificazione centrale. `[1.0.0]`
* `[ ]` b. Ogni NPC (dall'età `CHILD` o `TEENAGER` in su) possiede un DID univoco. `[1.0.0]`

### **1. Informazioni Contenute e Caratteristiche Fisiche/Digitali del DID:** `[ ]`
    * `[P]` a. **Dati Personali Standard Registrati:** `[1.0.0]`
        * `[P]` i. Nome completo. `[1.0.0]`
        * `[P]` ii. Data di nascita. `[1.0.0]`
        * `[ ]` iii. Luogo di nascita. `[1.0.1]`
        * `[P]` iv. Indirizzo di residenza attuale. `[1.0.0]`
        * `[ ]` v. Codice Identificativo Personale (CIP). `[1.0.0]`
        * `[ ]` vi. Foto del titolare. `[1.1.0]`
        * `[ ]` vii. Data di emissione e data di scadenza. `[1.0.1]`
        * `[P]` viii. Cittadinanza di Anthalys. `[1.0.0]`
    * `[ ]` b. **Caratteristiche di Sicurezza del Documento Fisico (Lore e Design):** `[1.0.1]`
        * `[ ]` i. Materiale resistente ed ecologico. `[1.0.1]`
        * `[ ]` ii. Microchip incorporato. `[1.0.1]`
        * `[ ]` iii. Elementi visivi di sicurezza (Ologrammi, etc.). `[1.0.1]`
        * `[ ]` iv. (Lore) "Inchiostro speciale ecologico". `[1.0.1]`
        * `[ ]` v. Codice a barre lineare e Codice QR. `[1.0.1]`
        * `[ ]` vi. Firma fisica e/o digitale. `[1.0.1]`
    * `[ ]` c. **Sicurezza Digitale del DID e dei Dati Associati:** `[1.1.0]`
        * `[ ]` i. Crittografia avanzata. `[1.1.0]`
        * `[ ]` ii. Autenticazione multifattoriale (MFA). `[1.1.0]`
        * `[ ]` iii. Gestione sicura delle chiavi crittografiche. `[1.1.0]`

### **2. Codice Identificativo Personale (CIP):** `[ ]`
    * `[P]` a. **Definizione e Unicità:** Il CIP è un numero unico e pseudo-anonimizzato. `[1.0.0]`
    * `[ ]` b. **Formato Standardizzato:** `123.XXXX.YYYY.Z`. `[1.0.0]`
    * `[P]` c. **Funzione:** Identificare in modo univoco e sicuro le persone. `[1.0.0]`

### **3. Codice QR sul Documento di Identità: Funzionalità e Accesso ai Dati:** `[ ]`
    * `[ ]` a. **Posizionamento e Design del QR Code:** `[1.0.1]`
    * `[ ]` b. **Livelli di Accesso tramite Scansione QR:** `[1.1.0]`
        * `[ ]` i. **Accesso Base (Pubblico/Non Autorizzato):** Rilascia solo informazioni pubbliche essenziali. `[1.1.0]`
        * `[ ]` ii. **Accesso Completo (Autorizzato e Tracciato):** Rilascia informazioni dettagliate e sensibili. `[1.2.0]`
    * `[ ]` c. **Sicurezza e Privacy del Sistema QR Code:** `[1.1.0]`
    * `[ ]` d. **Gestione e Aggiornamento delle Informazioni Legate al QR Code:** `[1.1.0]`

### **4. Gestione Digitale del DID e Accesso ai Servizi da parte del Cittadino tramite SoNet:** `[!]`
    * `[!]` a. Il portale SoNet è l'interfaccia primaria per il cittadino per accedere alle funzionalità del DID. `[1.0.0]`
    * `[ ]` b. Le funzionalità specifiche sono dettagliate nella Sezione XXIV (SoNet). `[1.0.0]`

### **5. Carta di Pagamento Integrata nel DID:** `[ ]`
    * `[P]` a. **Funzionalità di Pagamento Universale:** `[1.0.0]`
        * `[P]` i. Il DID funge da principale strumento di pagamento. `[1.0.0]`
        * `[ ]` ii. Chip NFC per pagamenti contactless. `[1.0.0]`
        * `[P]` iii. La gestione dei conti avviene tramite SoNet. `[1.0.0]`
    * `[ ]` b. **Programma a Punti per Pagamenti Civici:** `[1.2.0]`
    * `[ ]` c. **Gestione Fondi e Conti tramite App "MyAnthalysID":** `[1.1.0]`
        * `[ ]` i. Visualizzazione saldo e movimenti. `[1.1.0]`
        * `[ ]` ii. Funzionalità di trasferimento fondi tra NPC (P2P). `[1.1.0]`
        * `[ ]` iii. Impostazione limiti di spesa e notifiche. `[1.1.0]`
    * `[ ]` d. **Sicurezza Avanzata dei Pagamenti:** `[1.1.0]`
        * `[ ]` i. Autenticazione biometrica o PIN per transazioni sicure. `[1.1.0]`
        * `[ ]` ii. Blocco immediato delle funzioni di pagamento tramite SoNet. `[1.1.0]`
        * `[ ]` iii. (Lore) PIN di emergenza. `[1.2.0]`

### **6. Altre Integrazioni e Funzionalità del DID:** `[ ]`
    * `[P]` a. **Punti di Raccolta Rifiuti Intelligenti:** Utilizzo del DID per identificarsi. `[1.0.0]`
    * `[ ]` b. **Accesso a Servizi Governativi e Civici Specifici:** `[1.0.1]`
        * `[ ]` i. Accesso a biblioteche pubbliche/universitarie. `[1.0.1]`
        * `[ ]` ii. Accesso a trasporti pubblici. `[1.1.0]`
        * `[ ]` iii. (Avanzato) Votazioni elettroniche sicure. `[1.2.0]`
    * `[ ]` c. **Licenze e Certificazioni Digitali:** `[1.1.0]`
    * `[ ]` d. **(Opzionale) Funzione "Chiave Universale" (Avanzato):** `[FUTURO]`

### **7. Gestione della Privacy, Sicurezza dei Dati e Aspetti Etici:** `[ ]`
    * `[P]` a. Definire politiche e meccanismi tecnici per la protezione dei dati. `[1.0.0]`
    * `[P]` b. L'IA di SoNet deve rispettare rigorosi protocolli di privacy. `[1.0.0]`
    * `[ ]` c. (Eventi) Possibilità di dibattiti pubblici o preoccupazioni sulla privacy. `[1.1.0]`
    * `[ ]` d. (Eventi Rari) Incidenti di sicurezza informatica. `[1.2.0]`

### **8. Visualizzazione Astratta del DID e Interazioni nella TUI:** `[ ]`
    * `[!]` a. L'interfaccia principale per il cittadino è il portale SoNet. `[1.0.0]`
    * `[ ]` b. Le interazioni (es. "presentazione del DID") saranno azioni astratte. `[1.0.1]`
    * `[ ]` c. Notifiche al giocatore/NPC riguardanti il DID. `[1.0.1]`

---

## ♻️ XIII. GESTIONE AMBIENTALE E CIVICA DI ANTHALYS `[ ]`

### **1. Sistema di "Punti Influenza Civica" (PIC) e Incentivi per la Sostenibilità:** `[ ]`
    * `[P]` a. Gli NPC accumulano PIC compiendo azioni positive. `[1.0.0]`
    * `[ ]` b. **Meccanismo di Punti (PIC) per la Differenziazione Corretta dei Rifiuti:** `[1.0.1]`
        * `[ ]` i. La corretta differenziazione viene tracciata e premiata con PIC. `[1.0.1]`
        * `[ ]` ii. **Assegnazione Punti Esempio (da bilanciare):** `[1.0.1]`
    * `[ ]` c. **Utilizzo e Benefici dei PIC Accumulati:** `[1.1.0]`
        * `[ ]` i. Sconti sulla Tassa dei Rifiuti. `[1.1.0]`
        * `[ ]` ii. Buoni Spesa Convertibili. `[1.1.0]`
        * `[ ]` iii. Premi e Riconoscimenti Pubblici. `[1.2.0]`
        * `[ ]` iv. (Avanzato) I PIC possono essere spesi per influenzare politiche locali minori. `[FUTURO]`
    * `[ ]` d. **Applicazione Mobile per Gestione PIC e Sostenibilità:** `[1.1.0]`
    * `[ ]` e. (Avanzato) Un "Consiglio Cittadino" astratto valuta le proposte basate sui PIC. `[FUTURO]`

### **2. Ambiente e Impatto Ecologico:** `[ ]`
    * `[ ]` a. **Livello di Inquinamento Astratto (per quartiere/città):** `[1.2.0]`
        * `[ ]` i. Influenzato da densità industriale, traffico, gestione rifiuti, etc. `[1.2.0]`
        * `[ ]` ii. L'inquinamento elevato ha impatti negativi su umore, salute, ecc. `[1.2.0]`
        * `[ ]` iii. Estensione "Total Realism" - Impatti Ecologici Profondi. `[2.0.0]`
    * `[P]` b. **Azioni Ecologiche e Gestione Differenziata dei Rifiuti da parte degli NPC:** `[1.0.1]`
        * `[ ]` i. **Tipologie di Rifiuti Differenziabili e Contenitori Domestici:** `[1.0.1]`
            * `[ ]` 1-7. Definire le azioni specifiche per ogni tipo di rifiuto (`SMALTISCI_...`). `[1.0.1]`
            * `[ ]` 8. Ogni lotto residenziale deve avere il set di contenitori. `[1.0.1]`
            * `[ ]` 9. L'IA degli NPC gestisce la frequenza e la correttezza della differenziazione. `[1.0.2]`
        * `[ ]` ii. **Compostaggio Domestico:** Azione `USE_DOMESTIC_COMPOSTER`. `[1.1.0]`
        * `[ ]` iii. (Futuro) Scelte di trasporto ecologiche. `[1.2.0]`
        * `[ ]` iv. (Futuro) Risparmio energetico in casa. `[1.2.0]`
    * `[ ]` c. **Politiche Ambientali (Simulate dal Governo):** `[1.2.0]`
        * `[ ]` i. Leggi su emissioni, standard per la gestione dei rifiuti, etc. `[1.2.0]`
        * `[ ]` ii. Impatto misurabile sull'inquinamento, economia e comportamento NPC. `[1.2.0]`
    * `[ ]` d. **Estensione "Total Realism" - Ecosistema Locale Dinamico (Flora):** `[FUTURO]`

### **3. Servizi Municipali e Infrastrutture:** `[ ]`
    * `[ ]` a. **Gestione e Trattamento dei Rifiuti a Livello Municipale:** `[1.1.0]`
        * `[P]` i. NPC e attività economiche producono rifiuti differenziati. `[1.0.1]`
        * `[ ]` ii. (Futuro) Sistema di raccolta rifiuti municipale. `[1.2.0]`
        * `[ ]` iii. Trattamento e Riutilizzo Post-Raccolta (Lore e Impatti Indiretti). `[1.2.0]`
    * `[ ]` b. **Manutenzione Spazi Pubblici:** `[1.1.0]`
        * `[ ]` i. Parchi, strade, piazze necessitano di manutenzione. `[1.1.0]`
        * `[ ]` ii. Se trascurati, questi spazi diventano meno attraenti. `[1.1.0]`
    * `[P]` c. **Servizi di Emergenza (Pompieri, Forze dell'Ordine):** `[1.0.0]`
        * `[P]` i. Pompieri rispondono a incendi. `[1.0.0]`
        * `[P]` ii. Forze dell'Ordine mantengono l'ordine pubblico. `[1.0.0]`

### **4. Partecipazione Civica e Volontariato:** `[ ]`
    * `[P]` a. NPC compiono azioni di volontariato. `[1.1.0]`
    * `[ ]` b. Definire azioni specifiche: `CLEAN_UP_PARK`, `HELP_ELDERLY_NEIGHBOR`, ecc. `[1.1.0]`
    * `[ ]` c. Il volontariato aumenta i PIC, migliora l'umore, rafforza relazioni. `[1.1.0]`
    * `[ ]` d. (Futuro) Organizzazioni di volontariato o ONG. `[1.2.0]`

### **5. Eventi Comunitari e Festival:** `[ ]`
    * `[ ]` a. Eventi locali ricorrenti: mercati contadini, fiere di quartiere. `[1.1.0]`
    * `[ ]` b. NPC partecipano attivamente a questi eventi. `[1.1.0]`
    * `[ ]` c. Questi eventi rafforzano il senso di comunità e soddisfano bisogni. `[1.1.0]`

### **6. Smaltitori Automatici Domestici per Rifiuti:** `[ ]`
    * `[ ]` a. **Funzionamento e Tipologie:** `[1.1.0]`
        * `[ ]` i. Compostatori Domestici Avanzati. `[1.1.0]`
        * `[ ]` ii. Mini-Riciclatori Domestici (Plastica Bio / Vetro). `[1.2.0]`
        * `[ ]` iii. Smaltitori/Compattatori Domestici di Metalli. `[1.2.0]`
    * `[ ]` b. **Incentivi per l'Acquisto e l'Uso:** `[1.1.0]`
    * `[ ]` c. **Benefici Simulati:** `[1.1.0]`

---

## ✨ XIV. EVENTI CASUALI E SCENARI GUIDATI `[ ]`

* `[P]` a. Registrazione eventi significativi della simulazione (nascite, morti, matrimoni, ecc.). `[1.0.0]`
* `[ ]` b. **Sistema di Eventi Casuali Dinamici:** `[1.1.0]`
    * `[ ]` i. Definire una libreria di eventi casuali di piccola e media portata. `[1.1.0]`
    * `[ ]` ii. Gli eventi possono influenzare umore, bisogni, relazioni o finanze. `[1.1.0]`
    * `[ ]` iii. Gli eventi possono sbloccare opportunità o piccole sfide. `[1.1.0]`
    * `[ ]` iv. (Avanzato) La probabilità/esito degli eventi è influenzato da tratti, umore, meteo, etc. `[1.2.0]`
    * `[ ]` v. Estensione "Total Realism" - Eventi Guidati dall'Ecosistema Informativo. `[FUTURO]`
* `[P]` c. **Eventi Contestuali basati sull'Ambiente e sui Tratti degli NPC:** `[1.0.1]`
    * `[ ]` i. Implementare la generazione di eventi specifici basati sull'ambiente. `[1.0.1]`
    * `[P]` ii. I tratti degli NPC reagiscono a questi eventi con moodlet e pensieri. `[1.0.1]`
    * `[ ]` iii. (Avanzato) Eventi di "scoperta" o interazione con oggetti specifici. `[1.2.0]`
* `[ ]` d. **Eventi di Sincronicità / Realismo Magico (Semplificato):** `[1.3.0]`
    * `[ ]` i. Introdurre piccoli eventi "strani", coincidenze significative, deja-vu. `[1.3.0]`
    * `[ ]` ii. Questi eventi danno moodlet unici (Meravigliato, Confuso, Intuizione). `[1.3.0]`
    * `[ ]` iii. La probabilità è influenzata da tratti come `CURIOUS` o `SPIRITUAL`. `[1.3.0]`
* `[ ]` e. **(Avanzato) Scenari Guidati o "Storylet":** `[2.0.0]`
    * `[ ]` i. Definire brevi catene di eventi interconnessi o piccoli archi narrativi. `[2.0.0]`
    * `[ ]` ii. Questi scenari presentano all'NPC delle scelte con conseguenze diverse. `[2.0.0]`
    * `[ ]` iii. Completare o fallire questi scenari ha un impatto significativo sull'NPC. `[2.0.0]`
    * `[ ]` iv. Estensione "Total Realism" - Scenari Complessi e Dinamiche Sociali Emergenti. `[FUTURO]`
* `[P]` f. **Eventi Legati al Ciclo di Vita e alle Relazioni:** `[1.0.0]`
    * `[x]` i. Nascite, morti, matrimoni sono registrati. `[1.0.0]`
    * `[P]` ii. Questi eventi triggerano reazioni emotive e comportamentali complesse. `[1.0.1]`
* `[ ]` g. Meccanica di "storie di quartiere" e progressione della vita per i PNG non attivi. `[1.1.0]`
* `[ ]` h. **Sistema di Eventi Globali ("Il Bollettino di Anthalys"):** `[1.3.0]`
    * `[ ]` i. Un `EventManager` globale genera eventi a livello cittadino (es. ondate di calore, annunci di concerti, scandali politici minori, inaugurazioni di mostre). `[1.3.0]`
    * `[ ]` ii. Questi eventi vengono "pubblicati" come notizie sul portale SoNet. `[1.3.0]`
    * `[ ]` iii. Gli NPC, tramite l'azione `READ_NEWS_ON_SONET`, vengono a conoscenza di questi eventi, che possono generare nuovi "Problemi" o "Opportunità" per la loro IA (es. un `ART_LOVER` che scopre una mostra vorrà andarci). `[1.3.0]`

---

## 🔧 XV. SISTEMI TECNICI `[ ]`
* `[P]` **1. Struttura Modulare del Codice e del Progetto:** 
    * `[x]` a. Organizzazione delle cartelle base (`core`, `modules`, `AI`, ecc.). `[1.0.0]`
    * `[P]` b. Creazione dei file principali (`simai.py`, `character.py`, `simulation.py`). `[1.0.0]`
    * `[x]` c. Implementazione dei file `__init__.py` per la gestione dei package. `[1.0.0]`
* `[x]` **2. Gestione delle Configurazioni e Settings:** `[1.0.0]`
    * `[x]` a. File `settings.py` per costanti globali non modificabili a runtime. `[1.0.0]`
    * `[x]` b. File `settings.json` (o simile) per impostazioni utente modificabili. `[1.0.0]`
        * `[ ]` i. **Fusione Configurazioni:** Spostare le costanti rilevanti per gli NPC da `settings.py` a `npc_config.py` per una maggiore coerenza. `[1.0.1]`
    * `[x]` c. Architettura di configurazioni modulari in `core/config/` (es. `actions_config.py`, `npc_config.py`). `[1.0.0]`
* `[ ]` **3. Sistema di Logging Avanzato:** 
    * `[ ]` a. Implementare un sistema di logging robusto (es. `logging` di Python) con diversi livelli (DEBUG, INFO, WARN, ERROR). `[1.1.0]`
    * `[ ]` b. Possibilità di configurare il logging per scrivere su file e/o console. `[1.1.0]`
* `[ ]` **4. Salvataggio e Caricamento Partita (JSON).** 
    * `[P]` a. Salvare lo stato completo della simulazione in un file JSON. `[1.0.0]`
    * `[ ]` b. Caricare uno stato di gioco da un file JSON. `[1.0.0]`
    * `[ ]` c. Gestione di più file di salvataggio (slot). `[1.0.1]`
    * `[ ]` d. (Futuro) Gestione errori e versioning dei salvataggi per retrocompatibilità. `[1.1.0]`
* `[P]` **5. Ottimizzazione Performance e Gestione Popolazione Vasta:** 
    * `[P]` a. Architettura per supportare diversi Livelli di Dettaglio (LOD). `[1.0.0]`
    * `[ ]` b. Implementazione di Time Slicing / Staggered Updates per distribuire il carico della CPU. `[1.1.0]`
    * `[ ]` c. Tecniche di caching per calcoli ripetitivi e costosi. `[1.2.0]`
    * `[ ]` d. Profiling periodico delle performance e ottimizzazione continua. `[1.0.1]`
    * `[ ]` e. Valutare strutture dati efficienti per grandi numeri di NPC. `[1.1.0]`

---

## 🌌 XVI. SISTEMI UNICI E AVANZATI (Idee Speciali per SimAI) `[ ]`

### **1. Sistema di Fede e Religione Personalizzato per Anthalys:** `[1.2.0]`
    * `[ ]` a. Definire una o più religioni/filosofie spirituali uniche per Anthalys. `[1.2.0]`
    * `[ ]` b. NPC possono aderire a una fede e praticarla, influenzando bisogni e valori. `[1.2.0]`
    * `[P]` c. Tratti come `SPIRITUAL` e `CYNICAL` interagiscono con questo sistema. `[1.2.0]`
    * `[ ]` d. (Avanzato) Conflitti o sinergie tra fedi diverse o tra fede e scienza. `[FUTURO]`
    * `[ ]` e. Festività religiose specifiche con rituali e attività dedicate. `[1.2.0]`

### **2. Sistema di Magia o Fenomeni Paranormali (Sottile e Lore-Based):** `[1.3.0]`
    * `[P]` a. Introduzione di elementi di "realismo magico" o eventi inspiegabili. `[1.3.0]`
    * `[ ]` b. NPC con tratti specifici (`SENSITIVE_TO_UNSEEN`, `MYSTIC_INCLINED`) percepiscono questi fenomeni. `[1.3.0]`
    * `[ ]` c. Eventi rari e misteriosi che aggiungono profondità al lore e all'esperienza psicologica. `[1.3.0]`
    * `[ ]` d. (Avanzato) Possibilità di società segrete o culti minori. `[FUTURO]`

### **3. Sistema di Sogno e Subconscio (Molto Avanzato):** `[FUTURO]`
    * `[ ]` a. NPC hanno "sogni" astratti o semi-narrativi durante il sonno. `[FUTURO]`
    * `[ ]` b. Il contenuto dei sogni è influenzato da eventi recenti, stress, bisogni, tratti. `[FUTURO]`
    * `[ ]` c. I sogni possono dare moodlet specifici al risveglio. `[FUTURO]`
    * `[ ]` d. **Estensione "Total Realism" - Impatto Profondo dei Sogni:** `[FUTURO]`

### **4. Mini-giochi Testuali:** `[ ]`
    * `[ ]` a. Dialoghi a scelta multipla con conseguenze significative per interazioni chiave. `[1.2.0]`
    * `[ ]` b. Sistema di crisi familiari interattive con esiti ramificati. `[1.3.0]`
    * `[ ]` c. Gestione di eventi speciali o "storylet" tramite prompt e scelte testuali. `[1.2.0]`

### **5. Sistema di Reputazione e Influenza Sociale Avanzato:** `[1.2.0]`
    * `[ ]` a. Un NPC ha un punteggio di "reputazione" generale o specifico in certi ambiti. `[1.2.0]`
    * `[ ]` b. La reputazione è influenzata da azioni pubbliche, pettegolezzi, successi/fallimenti. `[1.2.0]`
    * `[ ]` c. La reputazione influenza il modo in cui gli altri NPC trattano il personaggio. `[1.2.0]`
    * `[P]` d. Tratti come `ARROGANT`, `SINCERE`, `MANIPULATIVE` hanno un forte impatto sulla reputazione. `[1.2.0]`
    * `[ ]` e. (Avanzato) Meccaniche di "influenza sociale" per NPC con alta reputazione. `[1.3.0]`

### **6. Estensione "Total Realism" - Generazione di Opere Intellettuali e Creative Uniche:** `[FUTURO]`
    * `[ ]` a. NPC con alti livelli di skill possono creare opere con "contenuto" unico generato proceduralmente. `[FUTURO]`
    * `[ ]` b. Letteratura: NPC scrivono opere con titoli e temi generati. `[FUTURO]`
    * `[ ]` c. Arte Visiva: NPC creano opere con stili e soggetti descritti testualmente. `[FUTURO]`
    * `[ ]` d. Musica: NPC compongono brani con genere e impatto emotivo generati. `[FUTURO]`
    * `[ ]` e. Filosofia/Scienza: NPC sviluppano "teorie" che altri possono discutere. `[FUTURO]`
    * `[ ]` f. Queste opere uniche contribuiscono all'evoluzione culturale di Anthalys. `[FUTURO]`

---

## 🌐 XVII. LOCALIZZAZIONE E MULTILINGUA `[ ]`

### **1. Internalizzazione del Testo (i18n):** `[1.1.0]`
    * `[ ]` a. Identificare tutte le stringhe di testo visibili all'utente. `[1.1.0]`
    * `[ ]` b. Implementare un sistema per estrarre le stringhe in file di risorse per lingua. `[1.1.0]`
    * `[ ]` c. Modificare il codice per caricare le stringhe dalla risorsa linguistica appropriata. `[1.1.0]`

### **2. Supporto per Lingue Multiple:** `[1.1.0]`
    * `[ ]` a. Creare file di traduzione iniziali (Italiano, Inglese). `[1.1.0]`
    * `[ ]` b. Implementare un meccanismo per selezionare la lingua. `[1.1.0]`
    * `[ ]` c. Gestire la visualizzazione corretta di caratteri speciali. `[1.1.0]`

### **3. Localizzazione dei Contenuti (l10n):** `[1.2.0]`
    * `[ ]` a. Considerare la localizzazione di formati di data/ora, numeri, valuta. `[1.2.0]`
    * `[ ]` b. (Avanzato) Adattare alcuni contenuti di gioco per essere culturalmente risonanti. `[FUTURO]`

### **4. Strumenti e Processi per la Traduzione:** `[FUTURO]`
    * `[ ]` a. (Futuro) Valutare strumenti che facilitino il processo di traduzione. `[FUTURO]`
    * `[ ]` b. (Futuro) Stabilire un processo per aggiornare le traduzioni. `[FUTURO]`

---

## 🌳 XVIII. INTERAZIONI AMBIENTALI, OGGETTI E LUOGHI `[ ]`

* `[P]` **0. Sistema Fondamentale di Oggetti e Locazioni:**
    * `[x]` a. Definite classi base per `Location` e `GameObject`. `[1.0.0]`
    * `[x]` b. `Character` conosce la sua `current_location`. `[1.0.0]`
    * `[x]` c. `Simulation` gestisce le locazioni e il posizionamento degli NPC. `[1.0.0]`
    * `[P]` d. In corso l'integrazione della percezione degli oggetti/locazioni. `[1.0.0]`

### **1. Interazione con Oggetti Specifici:** `[P]`
    * `[P]` a. NPC possono interagire con oggetti specifici nelle `Location`. `[1.0.0]`
    * `[P]` b. Le interazioni soddisfano bisogni, danno moodlet, o sviluppano skill. `[1.0.0]`
    * `[ ]` c. Qualità e stato degli oggetti possono influenzare l'efficacia dell'interazione. `[1.1.0]`
    * `[ ]` d. Oggetti Contenitori per Scorte Domestiche. `[1.1.0]`
        * `[ ]` i. Frigoriferi, Dispense rappresentano le scorte domestiche. `[1.1.0]`
        * `[ ]` ii. La "capacità" di questi contenitori potrebbe essere un fattore. `[1.2.0]`

### **2. Usura, Manutenzione e Dinamica degli Oggetti:** `[ ]`
    * `[P]` a. Oggetti possono "usurarsi" o "rompersi" con l'uso. `[1.0.1]`
    * `[ ]` b. NPC possono tentare di riparare oggetti rotti (azione `REPAIR_OBJECT`). `[1.0.1]`
        * `[ ]` i. La riparazione richiede tempo e "pezzi di ricambio". `[1.0.2]`
        * `[ ]` ii. Il successo della riparazione dipende dalla skill `HANDINESS`. `[1.0.2]`
    * `[ ]` c. Oggetti possono richiedere manutenzione periodica. `[1.2.0]`
    * `[ ]` d. Estensione "Total Realism" - Fisica degli Oggetti Semplificata. `[FUTURO]`
        * `[ ]` i. NPC possono spostare alcuni oggetti di arredamento. `[FUTURO]`
        * `[ ]` ii. Oggetti possono cadere e rompersi. `[FUTURO]`
        * `[ ]` iii. Gli oggetti potrebbero accumulare polvere. `[FUTURO]`
        * `[ ]` iv. Simulazione semplificata di fluidi (allagamenti, fumo). `[FUTURO]`

### **3. Stato Ambientale (Pulizia, Disordine):** `[ ]`
    * `[ ]` a. `Location` e Oggetti possono accumulare "sporcizia" o "disordine". `[1.1.0]`
    * `[ ]` b. Azioni che sporcano e azioni che puliscono. `[1.1.0]`
    * `[ ]` c. Impatto sull'umore degli NPC (specialmente per tratti come `NEAT`, `SLOB`). `[1.1.0]`

### **4. Eventi Ambientali Minori (Insetti, Odori):** `[ ]`
    * `[ ]` a. Possibilità di eventi come "vista di insetti" o "cattivi odori". `[1.2.0]`
    * `[ ]` b. Impatto sull'umore, specialmente per NPC `SQUEAMISH`. `[1.2.0]`

### **5. Proprietà e Tipi di Location:** `[P]`
    * `[x]` a. Diversi tipi di lotti (Residenziale, Comunitario, Commerciale). `[1.0.0]`
    * `[x]` b. Definizione di un Enum `LocationType`. `[1.0.0]`
    * `[P]` c. Ogni lotto ha un indirizzo, dimensione, valore, oggetti specifici. `[1.0.0]`
    * `[P]` d. NPC visitano lotti comunitari per attività o lavoro. `[1.0.0]`
    * `[ ]` e. Generazione procedurale o design di quartieri/città. `[1.1.0]`
    * `[ ]` f. Sistema di "proprietà" dei lotti (acquistabili, affittabili). `[1.1.0]`
    * `[ ]` g. (Futuro) Introdurre sotto-luoghi specifici o "lotti" con caratteristiche uniche. `[1.2.0]`
    * `[P]` h. Elenco Luoghi Comunitari (Implementare le istanze per ogni tipo). `[1.0.0]`
    * `[P]` i. Attributi della Location che influenzano gli NPC (affollamento, sicurezza, estetica). `[1.0.1]`
        * `[P]` vi. Questi attributi possono cambiare dinamicamente. `[1.0.1]`
        * `[P]` vii. I tratti degli NPC reagiscono a questi livelli. `[1.0.1]`
    * `[ ]` j. (Futuro) Sistema di "proprietà immobiliari". `[1.1.0]`
    * `[ ]` k. (Futuro) Miglioramento/Decorazione delle case. `[1.1.0]`

---

## 🎲 XIX. SISTEMA GIOCHI D'AZZARDO E SCOMMESSE DI ANTHALYS `[ ]`

### **1. Principi Generali e Regolamentazione di Base:** `[ ]`
    * `[!]` a. Legalità e regolamentazione di scommesse e giochi da casinò. `[1.2.0]`
    * `[!]` b. Accesso consentito solo ai maggiorenni. `[1.2.0]`
    * `[ ]` c. Requisito di piattaforme rintracciabili e regolamentate. `[1.2.0]`
    * `[!]` d. Enfasi su gioco responsabile e protezione dei minori. `[1.2.0]`

### **2. Sistema di Scommesse:** `[ ]`
    * `[ ]` a. Tipologie di Scommesse Consentite (Sportive, Quotidiane, Intrattenimento, Politiche). `[1.2.0]`
    * `[ ]` b. Tipologie di Scommesse Non Consentite. `[1.2.0]`
    * `[ ]` c. Sistema di Piazzamento Scommesse per NPC (Azione `PLACE_BET`). `[1.3.0]`
    * `[ ]` d. Gestione Eventi Scommettibili. `[1.3.0]`

### **3. Tassazione sulle Scommesse (Importo Scommesso):** `[ ]`
    * `[ ]` a. Implementare tassazione progressiva sull'importo di ogni scommessa. `[1.2.0]`
    * `[P]` b. Definire la struttura delle aliquote fiscali. `[1.2.0]`
    * `[ ]` c. Logica per calcolare e detrarre la tassa. `[1.2.0]`
    * `[ ]` d. Flusso delle tasse raccolte verso il tesoro del governo. `[1.2.0]`

### **4. Sistema dei Casinò:** `[ ]`
    * `[ ]` a. Tipologie di Casinò (Fisici e Online). `[1.3.0]`
    * `[ ]` b. Giochi da Casinò Specifici (Slot Machine, Poker, Roulette). `[1.3.0]`
    * `[ ]` c. Limiti delle Vincite nei Casinò. `[1.3.0]`
    * `[ ]` d. IA per Comportamento al Casinò. `[1.3.0]`

### **5. Tassazione sulle Vincite dei Casinò:** `[ ]`
    * `[ ]` a. Implementare tassazione progressiva sulle vincite nette. `[1.2.0]`
    * `[P]` b. Definire la struttura delle aliquote fiscali per le vincite. `[1.2.0]`
    * `[ ]` c. Logica per calcolare e detrarre la tassa. `[1.2.0]`
    * `[ ]` d. Flusso delle tasse raccolte verso il tesoro del governo. `[1.2.0]`

### **6. Misure di Sicurezza e Gioco Responsabile:** `[ ]`
    * `[ ]` a. Programmi di Gioco Responsabile (Auto-limitazione, autoesclusione). `[1.3.0]`
    * `[ ]` b. Monitoraggio delle Attività di Gioco (Astratto). `[1.3.0]`
    * `[ ]` c. Protezione dei Dati e Privacy. `[1.3.0]`

### **7. Impatto Economico e Sociale del Gioco d'Azzardo:** `[ ]`
    * `[ ]` a. I casinò generano reddito per il governo. `[1.2.0]`
    * `[ ]` b. Creazione di posti di lavoro (Carriere future). `[1.3.0]`
    * `[ ]` c. Potenziale impatto negativo su NPC vulnerabili (debiti, dipendenza). `[1.3.0]`

---

## 👪 XX. ATTEGGIAMENTI CULTURALI/FAMILIARI E SVILUPPO `[ ]`

### **1. Atteggiamento Familiare e Personale verso la Nudità:** `[1.2.0]`
    * `[P]` a. Aggiungere attributo `Character.is_nude: bool`. `[1.2.0]`
    * `[P]` b. Azioni che possono portare a/da nudità. `[1.2.0]`
    * `[ ]` c. Definire "contesti privati appropriati" per la nudità. `[1.2.0]`
    * `[ ]` d. Implementare un "livello di comfort con la nudità" per NPC. `[1.2.0]`
    * `[ ]` e. NPC con alto comfort potrebbero scegliere di rimanere nudi più a lungo. `[1.2.0]`
    * `[ ]` f. Logica per le reazioni dei familiari alla nudità in casa. `[1.2.0]`

### **2. Insegnare e Apprendere l'Onestà:** `[1.3.0]`
    * `[ ]` a. Interazioni genitore-figlio specifiche per insegnare il valore dell'onestà. `[1.3.0]`
    * `[ ]` b. Impatto a lungo termine di questi insegnamenti sulla probabilità che il figlio sviluppi tratti correlati. `[1.3.0]`

### **3. (Avanzato/Opzionale) Sistema di Nudità Pubblica e Reazioni Sociali Complesse:** `[FUTURO]`
    * `[ ]` a. Definire logica e conseguenze per nudità in contesti pubblici inappropriati. `[FUTURO]`
    * `[ ]` b. Azioni specifiche come "Streaking" o comportamenti esibizionisti. `[FUTURO]`
    * `[ ]` c. Questo richiederebbe un'attenta valutazione del tono del gioco. `[FUTURO]`

---

## 🛠️ XXI. STRUMENTI DEVELOPER `[ ]`

### **1. Debugging Avanzato:** `[ ]`
    * `[P]` a. Implementare un sistema di logging più robusto e configurabile. `[1.0.1]`
    * `[ ]` b. Possibilità di attivare/disattivare il logging per moduli specifici. `[1.1.0]`
    * `[P]` c. Visualizzazione TUI migliorata per variabili interne degli NPC. `[1.0.0]`
    * `[ ]` d. (Futuro) Integrazione con debugger Python. `[1.2.0]`
    * `[ ]` e. Funzionalità di "dump state" per un NPC specifico o per l'intera simulazione. `[1.1.0]`

### **2. Profiling delle Performance:** `[ ]`
    * `[ ]` a. Integrare strumenti di profiling (es. `cProfile`). `[1.0.2]`
    * `[ ]` b. Stabilire benchmark per misurare l'impatto delle modifiche. `[1.0.2]`
    * `[ ]` c. Check periodici delle performance. `[1.0.2]`

### **3. Comandi Cheat-Code per Sviluppo e Testing:** `[ ]`
    * `[P]` a. Implementare un meccanismo per inserire comandi cheat. `[1.0.0]`
    * `[ ]` b. **Comandi di Manipolazione NPC:** `[1.0.1]`
        * `[ ]` i. Modificare bisogni. `[1.0.1]`
        * `[ ]` ii. Aggiungere/Rimuovere moodlet. `[1.0.1]`
        * `[ ]` iii. Aggiungere/Rimuovere tratti. `[1.0.1]`
        * `[ ]` iv. Modificare livelli di skill. `[1.0.1]`
        * `[ ]` v. Modificare punteggi di relazione. `[1.0.1]`
        * `[ ]` vi. Aggiungere/Rimuovere denaro. `[1.0.1]`
        * `[ ]` vii. Triggerare/terminare una gravidanza. `[1.1.0]`
        * `[ ]` viii. Cambiare `LifeStage` o età. `[1.0.1]`
        * `[ ]` ix. Teletrasportare un NPC. `[1.0.1]`
    * `[ ]` c. **Comandi di Manipolazione Mondo/Simulazione:** `[1.0.2]`
        * `[ ]` i. Avanzare rapidamente il tempo. `[1.0.2]`
        * `[ ]` ii. Cambiare stagione/meteo. `[1.0.2]`
        * `[ ]` iii. Triggerare un evento specifico. `[1.1.0]`
        * `[ ]` iv. Generare un nuovo NPC con caratteristiche specifiche. `[1.0.2]`
        * `[ ]` v. Salvare/Caricare la partita da console. `[1.0.2]`
    * `[ ]` d. **Comandi di Visualizzazione/Debug:** `[1.1.0]`
    * `[!]` e. Assicurarsi che i comandi cheat siano accessibili solo in modalità sviluppo. `[1.0.0]`

### **4. Utility Scripts per la Gestione del Progetto:** `[ ]`
    * `[ ]` a. Script per generare automaticamente le classi tratto base. `[1.2.0]`
    * `[ ]` b. Script per validare la coerenza dei file di configurazione. `[1.2.0]`
    * `[ ]` c. Script per aiutare nel refactoring (es. trovare stringhe hardcoded). `[1.2.0]`

---

## 📜 XXII. SISTEMA REGOLAMENTARE GLOBALE E GOVERNANCE DI ANTHALYS `[ ]`

* `[!]` **A. Principi Fondamentali (basati sulla Costituzione):** `[1.0.0]`
    * `[!]` i. Le normative promuovono dignità, libertà, giustizia, solidarietà. `[1.0.0]`
    * `[!]` ii. Le normative garantiscono i diritti fondamentali. `[1.0.0]`
    * `[!]` iii. Le normative economiche promuovono un'economia equa e sostenibile. `[1.0.0]`

* **1. Normativa sull'Orario di Lavoro:** `[P]`
    * `[P]` a. Giornata Lavorativa Standard di 9 ore effettive. `[1.0.0]`
    * `[P]` b. Settimana Lavorativa di 5 giorni su 7. `[1.0.0]`
    * `[P]` c. Anno Lavorativo Standard (15 mesi attività / 3 mesi pausa). `[1.0.0]`
    * `[P]` d. Regolamentazione del Lavoro Minorile e Part-time. `[1.0.1]`
    * `[P]` e. Integrare le festività come giorni non lavorativi. `[1.0.0]`

* **2. Politiche Retributive:** `[P]`
    * `[P]` a. Definire tipologie di impiego e Scale Retributive. `[1.0.0]`
    * `[P]` b. Implementare Progressione Stipendiale per Anzianità. `[1.0.1]`
    * `[P]` c. Calcolo retribuzione mensile. `[1.0.0]`

* **3. Regolamentazione Fiscale (Contributo al Sostentamento Civico - CSC):** `[P]`
    * `[!]` a. Principio del CSC. `[1.0.0]`
    * `[P]` b. Regolamentazione della CSC-R (Componente sul Reddito Personale). `[1.0.0]`
    * `[P]` c. Procedure di Dichiarazione e Riscossione del CSC via SoNet. `[1.0.0]`
    * `[P]` d. Confluenza dei tributi del CSC nella Tesoreria Statale. `[1.0.0]`
    * `[ ]` e. Quadro Normativo delle Altre Componenti del CSC (A, S, P, C). `[1.1.0]`
    * `[ ]` f. Contrasto all'Evasione ed Elusione Fiscale. `[1.2.0]`

* **4. Benefici e Sicurezza Sociale:** `[P]`
    * `[P]` a. Assicurazione Sanitaria Lavoratori e Copertura Universale. `[1.0.0]`
    * `[P]` b. Pensioni. `[1.0.1]`
    * `[ ]` c. Indennità di Maternità/Paternità. `[1.1.0]`
    * `[ ]` d. Norme su Sicurezza sul Lavoro e Indennizzi. `[1.1.0]`
    * `[ ]` e. Assistenza Specifica per Disabilità e Malattie Croniche. `[1.2.0]`
    * `[ ]` f. Sussidi per Famiglie a Basso Reddito con Figli. `[1.1.0]`
    * `[ ]` g. Assistenza per Genitori Single. `[1.2.0]`
    * `[ ]` h. Supporto per Genitori con Disabilità. `[1.2.0]`

* **5. Copertura Sanitaria per Cittadini a Basso Reddito:** `[P]`
    * `[P]` a. Identificare cittadini idonei. `[1.0.0]`
    * `[P]` b. Meccanismo di copertura gratuita tramite "Istituti Fondine". `[1.0.0]`
    * `[P]` c. (Astratto) Definire come gli Istituti Fondine sono alimentati. `[1.0.0]`

* **6. Vacanze e Permessi Lavorativi:** `[ ]`
    * `[P]` a. Diritto a 24 giorni di vacanza retribuita/anno. `[1.0.1]`
    * `[ ]` b. Sistema per NPC per richiedere/usare giorni di vacanza. `[1.1.0]`
    * `[ ]` c. Tracciare giorni di vacanza usati/rimanenti. `[1.1.0]`
    * `[ ]` d. Permessi per Malattia retribuiti. `[1.1.0]`
    * `[ ]` e. Permessi per Emergenze Familiari retribuiti. `[1.1.0]`

* `[ ]` **7. Estensione "Total Realism" - Evoluzione, Applicazione e Impatto Sociale delle Normative:** `[FUTURO]`
    * `[ ]` a. Dinamicità delle Regolamentazioni. `[FUTURO]`
    * `[ ]` b. Applicazione e Rispetto delle Norme (Enforcement). `[FUTURO]`
    * `[ ]` c. Impatto Socio-Economico delle Normative. `[FUTURO]`
    * `[ ]` d. Equità e Accessibilità del Sistema. `[FUTURO]`

* `[ ]` **8. Regolamentazione su Prodotti Alimentari, Bevande e Beni di Consumo:** `[1.1.0]`
    * `[!]` a. Articolo 1: Scopo e Applicabilità. `[1.1.0]`
    * `[P]` b. Articolo 2: Definizioni Chiave. `[1.1.0]`
    * `[ ]` c. Articolo 3: Licenze di Produzione e Vendita. `[1.1.0]`
    * `[ ]` d. Articolo 4: Standard di Produzione. `[1.1.0]`
    * `[ ]` e. Articolo 5: Norme di Conservazione e Trasporto. `[1.2.0]`
    * `[ ]` f. Articolo 6: Etichettatura Obbligatoria. `[1.1.0]`
    * `[ ]` g. Articolo 7: Norme per i Punti Vendita. `[1.1.0]`
    * `[ ]` h. Articolo 8: Igiene e Sicurezza per la Preparazione. `[1.1.0]`
    * `[ ]` i. Articolo 9: Educazione e Sensibilizzazione dei Cittadini. `[1.2.0]`
    * `[ ]` j. Articolo 10: Norme Specifiche per Carne e Pesce Crudi. `[1.1.0]`
    * `[ ]` k. Articolo 11: Orari di Vendita (Alcolici). `[1.1.0]`
    * `[ ]` l. Articolo 12: Pubblicità e Promozioni. `[1.2.0]`
    * `[ ]` m. (Avanzato) Dettagli Normativi per Categoria Specifica. `[1.2.0]`
    * `[ ]` n. (Estensione "Total Realism") Applicazione e Sanzioni. `[FUTURO]`

---

## 🏥 XXIII. SISTEMA SANITARIO APPROFONDITO: Patologie, Ricerca Medica e Dinamiche Ospedaliere `[ ]`

* `[ ]` a. **Classificazione e Simulazione Dettagliata delle Patologie:** `[1.3.0]`
    * `[ ]` i. Definizione di un database di malattie (genetiche, infettive, croniche, acute, mentali). `[1.3.0]`
    * `[ ]` ii. Meccanismi di insorgenza (fattori di rischio, ereditarietà, contagio, stile di vita). `[1.3.0]`
    * `[ ]` iii. Simulazione dei sintomi e della progressione delle malattie. `[1.3.0]`
* `[ ]` b. **Sistema di Diagnosi e Trattamento Avanzato:** `[1.3.0]`
    * `[ ]` i. Procedure diagnostiche (esami di laboratorio, imaging). `[1.3.0]`
    * `[ ]` ii. Opzioni di trattamento (farmacologiche, chirurgiche, terapie). `[1.3.0]`
    * `[ ]` iii. Efficacia dei trattamenti e possibili effetti collaterali. `[1.3.0]`
* `[ ]` c. **Ricerca Medica e Sviluppo Farmaceutico:** `[FUTURO]`
    * `[ ]` i. Meccaniche per la ricerca su nuove malattie o trattamenti. `[FUTURO]`
    * `[ ]` ii. Sviluppo e approvazione di nuovi farmaci. `[FUTURO]`
    * `[ ]` iii. Impatto delle scoperte mediche sulla salute pubblica. `[FUTURO]`
* `[ ]` d. **Gestione Interna Avanzata delle Strutture Ospedaliere:** `[FUTURO]`
    * `[ ]` i. Risorse ospedaliere (letti, attrezzature, personale). `[FUTURO]`
    * `[ ]` ii. Liste d'attesa, gestione dei flussi di pazienti. `[FUTURO]`
    * `[ ]` iii. Specializzazioni dei reparti e degli ospedali. `[FUTURO]`
* `[ ]` e. **Impatto Dettagliato della Salute sulla Vita e Performance degli NPC:** `[1.3.0]`
    * `[ ]` i. Effetti di malattie su bisogni, umore, lavoro, relazioni. `[1.3.0]`
    * `[ ]` ii. Gestione della convalescenza e della riabilitazione. `[1.3.0]`
* `[ ]` f. **Carriere Mediche Specialistiche Avanzate:** `[1.2.0]`
    * `[ ]` i. Espansione dell'elenco carriere (chirurghi, oncologi, genetisti, ricercatori). `[1.2.0]`

---

## 🌐 XXIV. SoNet - Portale Unico dei Servizi al Cittadino di Anthalys `[ ]`
* `[@]` **[DA REVISIONARE]** Il modulo presenta errori di tipo `Pylance` da risolvere prima di proseguire con l'implementazione. `[1.0.1]`
* `[!]` a. **Definizione Concettuale e Architettura del Portale SoNet:** `[1.0.0]`
* `[ ]` b. **Implementazione Tecnica dell'Interfaccia Utente (TUI o futura GUI) per SoNet:** `[1.1.0]`
* `[ ]` c. **Integrazione Funzionalità dei Servizi tramite SoNet:**
    * `[P]` i. **Sezione Identità (DID):** `[1.0.0]`
        * `[P]` 1. Visualizzazione dei dati anagrafici. `[1.0.0]`
        * `[ ]` 2. Funzionalità per la gestione del documento DID. `[1.0.1]`
        * `[P]` 3. (Avanzato) Integrazione con servizi finanziari di base. `[1.0.0]`
        * `[ ]` 4. Gestione dei consensi privacy. `[1.1.0]`
        * `[ ]` 5. Archivio digitale di licenze e certificazioni. `[1.1.0]`
    * `[P]` ii. **Sezione Tasse e Tributi:** `[1.0.0]`
        * `[P]` 1. Visualizzazione dello stato fiscale del cittadino. `[1.0.0]`
        * `[ ]` 2. Funzionalità per il pagamento online sicuro delle imposte. `[1.0.1]`
    * `[ ]` iii. **Sezione Salute:** `[1.1.0]`
        * `[ ]` 1. Accesso a una cartella clinica elettronica riassuntiva. `[1.1.0]`
        * `[ ]` 2. Sistema di prenotazione online per visite mediche. `[1.1.0]`
        * `[ ]` 3. Visualizzazione e gestione appuntamenti sanitari. `[1.1.0]`
    * `[ ]` iv. **Sezione Istruzione e Formazione:** `[1.1.0]`
        * `[ ]` 1. Visualizzazione dello storico scolastico e universitario. `[1.1.0]`
        * `[ ]` 2. Funzionalità di iscrizione online a corsi, scuole, università. `[1.1.0]`
    * `[ ]` v. **Sezione Partecipazione Civica:** `[1.1.0]`
        * `[P]` 1. Registrazione alle liste elettorali. `[1.0.0]`
        * `[ ]` 2. Accesso a informazioni ufficiali su elezioni e referendum. `[1.1.0]`
        * `[ ]` 3. (Molto Futuro) Piattaforma sicura per il voto elettronico. `[FUTURO]`
        * `[ ]` 4. Accesso a consultazioni pubbliche o petizioni online. `[1.2.0]`
    * `[ ]` vi. **Sezione Mobilità e Trasporti:** `[1.1.0]`
        * `[ ]` 1. Acquisto e gestione di abbonamenti digitali. `[1.1.0]`
        * `[ ]` 2. Visualizzazione orari e informazioni in tempo reale. `[1.1.0]`
        * `[ ]` 3. Pagamento di multe o pedaggi. `[1.2.0]`
    * `[ ]` vii. **Sezione "La Mia Impronta Civica" (PIC):** `[1.1.0]`
        * `[P]` 1. Dashboard per il monitoraggio della raccolta differenziata. `[1.0.1]`
        * `[ ]` 2. Visualizzazione del saldo PIC accumulati. `[1.1.0]`
        * `[ ]` 3. Interfaccia per la riscossione di sconti e buoni. `[1.1.0]`
        * `[ ]` 4. Accesso a informazioni e guide sulla sostenibilità. `[1.1.0]`
    * `[ ]` viii. **Area Notifiche e Comunicazioni Ufficiali Personali:** `[1.1.0]`
    * `[ ]` ix. **Sezione Welfare e Supporto Sociale:** `[1.1.0]`
        * `[P]` 1. Consultazione dei propri diritti e prestazioni. `[1.0.1]`
        * `[ ]` 2. Presentazione e monitoraggio richieste per sussidi. `[1.1.0]`
        * `[P]` 3. Visualizzazione dello stato dei propri contributi pensionistici. `[1.0.1]`
        * `[ ]` 4. Richiesta/gestione indennità di maternità/paternità. `[1.1.0]`
    * `[ ]` x. **Sezione Informazioni Legali e Normative per il Cittadino:** `[1.2.0]`
    * `[P]` xi. **Sezione Commercio "AION":** `[1.0.0]`
        * `[P]` 1. Interfaccia per navigare il catalogo prodotti. `[1.0.0]`
        * `[P]` 2. Funzionalità per completare ordini. `[1.0.0]`
        * `[P]` 3. Pagamento sicuro integrato. `[1.0.0]`
        * `[ ]` 4. Gestione delle opzioni di consegna. `[1.0.1]`
        * `[ ]` 6. Ordini Ricorrenti e Liste della Spesa Automatizzate. `[1.2.0]`
        * `[ ]` 7. Funzionalità per inviare feedback e valutazioni. `[1.1.0]`
        * `[P]` 8. Storico ordini. `[1.0.0]`
    * `[P]` xii. **Sezione Servizi Sociali e Connessioni ("Amori Curati"):** `[1.0.0]`
    * `[ ]` xiii. **Sezione "Specchio Interiore" (Accesso al Sistema Claire):** `[1.1.0]` (Collegamento a `AA. Claire System Roadmap`)
        * `[ ]` 1. **Nome e Presentazione:** La sezione è presentata con un nome volutamente astratto e poetico come "Specchio Interiore" o "Dialoghi con Sé". Il nome 'Claire' non viene mai menzionato esplicitamente nell'interfaccia pubblica. *(Nome ironico per dev: "Claire 'versione portatile'")*. `[1.1.0]`
        * `[ ]` 2. **Funzionalità di Accesso:** Questa sezione fornisce un'interfaccia testuale minimale e sicura per interagire con il proprio sistema Claire personale. `[1.1.0]`
        * `[ ]` 3. **Diario Claire Sincronizzato:** Permette al cittadino di consultare il "Diario Claire" (`AA.3.a`), visualizzando le riflessioni e i momenti chiave registrati dal sistema. `[1.2.0]`
        * `[ ]` 4. **Messaggistica Asincrona:** Offre una sorta di "casella di posta" per i messaggi o le lettere generate da Claire (`AA.11`), specialmente quando il NPC non è in uno stato mentale per ricevere notifiche dirette. `[DLC]`
        * `[ ]` 5. **Impostazioni di Interazione:** Permette di regolare (entro certi limiti) la frequenza e l'intensità degli interventi di Claire, o di attivare una modalità "silenziosa" per periodi specifici. `[1.1.0]`
        * `[ ]` 6. **Sesso come Maschera o Fuga:** L'interfaccia potrebbe (astrattamente) riflettere se le recenti interazioni intime sono state autentiche o un meccanismo di coping, influenzando i suggerimenti di Claire. `[2.1.0]`
* `[ ]` d. **Definizione e Implementazione delle `ActionType` Specifiche per SoNet:** `[1.1.0]`
* `[ ]` e. **Logica Comportamentale (IA) per l'Utilizzo di SoNet da parte degli NPC:** `[1.1.0]`
* `[ ]` f. **Sicurezza del Portale SoNet:** `[1.1.0]`
* `[ ]` g. **Accessibilità del Portale SoNet:** `[1.2.0]`
* `[ ]` h. **Sistema di Gestione Feedback e Valutazioni per SoNet:** `[1.2.0]`

---

## 🏙️ XXV. INFRASTRUTTURE E URBANISTICA DI ANTHALYS `[ ]`

### **1. Struttura Urbana e Distretti di Anthalys:** `[P]`
    * `[x]` a. Organizzazione Generale della Città. `[1.0.0]`
    * `[x]` b. Tipologie di Distretti Funzionali. `[1.0.0]`
    * `[P]` c. Interazione e Flussi tra Distretti. `[1.0.0]`

### **2. Architettura e Design Urbano di Anthalys:** `[ ]`
    * `[x]` a. Filosofia Architettonica (Medievale/Moderno sostenibile). `[1.0.0]`
    * `[P]` b. Edifici Residenziali (con tecnologie di efficienza). `[1.0.0]`
    * `[ ]` c. Edifici Pubblici e Istituzionali (bioarchitettura, smart building). `[1.1.0]`
    * `[ ]` d. Monumenti e Siti Storici (restauro e manutenzione). `[1.1.0]`

### **3. Infrastrutture di Trasporto di Anthalys:** `[P]`
    * `[!]` Il sistema di trasporto è efficiente, sostenibile e integrato. `[1.0.0]`
    * `[P]` a. Sistema di Metropolitana di Anthalys (3 linee principali). `[1.0.0]`
    * `[ ]` b. Rete di Autobus e Tram di Anthalys. `[1.0.1]`
    * `[ ]` c. Rete Stradale e Autostradale di Anthalys. `[1.1.0]`
    * `[P]` d. Porti Lacustri/Fluviali, Aeroporti e Reti di Trasporto Acquatico. `[1.0.0]`
    * `[ ]` e. Integrazione dei Sistemi di Trasporto (Interscambio, Bigliettazione Unica). `[1.1.0]`
    * `[P]` f. Veicoli Privati, Motorizzazioni Ecologiche e Sistema di Immatricolazione. `[1.0.0]`
    * `[ ]` g. Accessibilità Universale delle Infrastrutture di Trasporto. `[1.0.1]`

### **4. Tecnologie Sostenibili e Innovazioni Urbane:** `[P]`
    * `[!]` Anthalys è all’avanguardia nell'uso di tecnologie sostenibili. `[1.0.0]`
    * `[P]` a. Energia Rinnovabile Urbana Integrata. `[1.0.0]`
    * `[P]` b. Sistema Avanzato di Economia Circolare e Riciclo. `[1.0.0]`
    * `[ ]` c. Gestione Sostenibile e Intelligente delle Risorse Idriche. `[1.1.0]`

### **5. Servizi Pubblici e Infrastrutture Sociali:** `[P]`
    * `[!]` Anthalys offre servizi pubblici di alta qualità. `[1.0.0]`
    * `[P]` b. Rete Sanitaria Avanzata e Specializzata. `[1.0.0]`
    * `[P]` c. Sistema Educativo Completo e Centri di Eccellenza. `[1.0.0]`
    * `[P]` d. Aree Ricreative, Culturali e Spazi Comunitari. `[1.0.0]`

### **6. Sicurezza Urbana e Monitoraggio Ambientale:** `[ ]`
    * `[ ]` a. Sistemi di Videosorveglianza Avanzati. `[1.1.0]`
    * `[ ]` b. Centri di Controllo, Sistemi di Allarme e Risposta Rapida. `[1.1.0]`
    * `[ ]` c. Monitoraggio Ambientale Continuo e Integrato. `[1.1.0]`

### **7. Urbanistica Sostenibile e Qualità della Vita:** `[P]`
    * `[P]` a. Pianificazione Verde Integrata e Biodiversità Urbana. `[1.0.0]`
    * `[P]` b. Zone a Traffico Limitato (ZTL) e Aree a Basse Emissioni. `[1.0.0]`
    * `[ ]` c. Sottopassi e Corridoi Ecologici per la Fauna Selvatica. `[1.2.0]`
    * `[P]` d. Rete Estesa di Zone Pedonali e Ciclabili. `[1.0.0]`
    * `[P]` e. Qualità dell'Aria e Riduzione Inquinamento Acustico. `[1.0.0]`

---

## 🌦️ XXVI. CLIMA, EVENTI ATMOSFERICI DETTAGLIATI E IMPATTO AMBIENTALE DINAMICO `[ ]`

* `[ ]` a. **Ciclo Stagionale Dettagliato di Anthalys:** `[1.2.0]`
    * `[ ]` i. Definizione delle stagioni di Anthalys. `[1.2.0]`
    * `[ ]` ii. Impatto delle stagioni su vegetazione, risorse e fauna. `[1.2.0]`
* `[ ]` b. **Sistema di Generazione Eventi Atmosferici Specifici:** `[1.1.0]`
    * `[ ]` i. Implementazione di una varietà di eventi: piogge, temporali, neve, ondate di calore. `[1.1.0]`
    * `[ ]` ii. Logica di probabilità e intensità degli eventi basata su stagione. `[1.1.0]`
    * `[P]` iii. Rappresentazione visiva e sonora degli eventi. `[1.0.0]`
* `[ ]` c. **Impatto del Clima e degli Eventi su Sistemi di Gioco Interconnessi:** `[1.1.0]`
    * `[ ]` i. **Agricoltura e Produzione Alimentare:** Effetti su crescita e rischi dei raccolti. `[1.2.0]`
    * `[ ]` ii. **Consumi Energetici:** Aumento della domanda di riscaldamento/raffreddamento. `[1.2.0]`
    * `[ ]` iii. **Salute e Umore degli NPC:** Malanni stagionali, impatto dell'umore. `[1.1.0]`
    * `[P]` iv. **Attività all'Aperto e Comportamento NPC:** Modifica delle routine in base al tempo. `[1.0.1]`
    * `[ ]` v. **Infrastrutture:** Possibili danni lievi o interruzioni temporanee di servizi. `[1.2.0]`
* `[ ]` d. **Simulazione Disastri Naturali su Piccola Scala e Risposta dei Servizi di Emergenza:** `[FUTURO]`
    * `[ ]` i. Eventi rari ma significativi (inondazioni, incendi boschivi). `[FUTURO]`
    * `[ ]` ii. Attivazione dei servizi di emergenza. `[FUTURO]`
    * `[ ]` iii. Impatto sulla popolazione e sull'ambiente locale. `[FUTURO]`

---

## ⚖️ XXVII. SISTEMA LEGALE, CRIMINALITÀ E GIUSTIZIA PENALE `[ ]`

* `[ ]` a. **Definizione del Codice Penale di Anthalys e Classificazione dei Reati:** `[1.3.0]`
    * `[ ]` i. Identificazione di una gamma di reati (furti, truffe, vandalismo, ecc.). `[1.3.0]`
    * `[ ]` ii. Definizione della gravità e delle pene base associate. `[1.3.0]`
* `[ ]` b. **Meccaniche di Criminalità per NPC:** `[1.3.0]`
    * `[ ]` i. Fattori che influenzano la propensione di un NPC a commettere crimini. `[1.3.0]`
    * `[ ]` ii. NPC che pianificano e commettono crimini (azioni specifiche). `[1.3.0]`
    * `[ ]` iii. (Avanzato) Possibilità di crimine organizzato. `[FUTURO]`
* `[P]` c. **Indagini e Forze dell'Ordine:** `[1.1.0]`
    * `[P]` i. NPC della Polizia che pattugliano e rispondono a segnalazioni. `[1.0.0]`
    * `[ ]` ii. Meccaniche di raccolta prove, interrogatori. `[1.2.0]`
    * `[ ]` iii. Skill investigative per la polizia. `[1.2.0]`
* `[ ]` d. **Sistema Processuale Penale Dettagliato:** `[1.3.0]`
    * `[ ]` i. Arresto e detenzione preventiva. `[1.3.0]`
    * `[P]` ii. Ruolo degli Avvocati. `[1.1.0]`
    * `[ ]` iii. Svolgimento dei processi in tribunale. `[1.3.0]`
    * `[ ]` iv. Possibilità di giurie popolari o giudici. `[1.3.0]`
    * `[ ]` v. Meccanismi di verdetto. `[1.3.0]`
* `[ ]` e. **Pene, Sistema Carcerario e Rieducazione:** `[1.3.0]`
    * `[ ]` i. Applicazione delle sentenze: multe, servizio comunitario, detenzione. `[1.3.0]`
    * `[ ]` ii. Design e implementazione di `LocationType.PRISON`. `[1.3.0]`
    * `[ ]` iii. Programmi di rieducazione e reinserimento sociale. `[1.3.0]`
    * `[ ]` iv. Impatto della detenzione sulla vita dell'NPC. `[1.3.0]`
* `[ ]` f. **Impatto della Criminalità sulla Società e sugli NPC:** `[1.3.0]`
    * `[ ]` i. Influenza sui livelli di sicurezza percepita nei distretti. `[1.3.0]`
    * `[ ]` ii. Reazioni degli NPC alla criminalità (paura, rabbia). `[1.3.0]`
    * `[ ]` iii. Impatto economico della criminalità. `[1.3.0]`

---

## 👨‍👩‍👧‍👦 XXVIII. VITA FAMILIARE AVANZATA E DINAMICHE INTERGENERAZIONALI `[ ]`

* `[ ]` a. **Stili Genitoriali e Impatto sullo Sviluppo dei Figli:** `[1.2.0]`
    * `[ ]` i. Definizione di diversi stili genitoriali (autorevole, permissivo, ecc.). `[1.2.0]`
    * `[ ]` ii. Impatto a lungo termine dello stile genitoriale sulla personalità dei figli. `[1.2.0]`
* `[ ]` b. **Dinamiche tra Fratelli e Ordine di Nascita:** `[1.3.0]`
    * `[ ]` i. Simulazione di relazioni uniche tra fratelli (rivalità, supporto, ecc.). `[1.3.0]`
    * `[ ]` ii. (Avanzato, Lore-Specifico) Esplorare l'impatto culturale dell'ordine di nascita. `[FUTURO]`
* `[ ]` c. **Ruolo e Dinamiche della Famiglia Allargata:** `[1.2.0]`
    * `[ ]` i. Interazioni significative con nonni, zii, cugini. `[1.2.0]`
    * `[ ]` ii. Possibilità di supporto o conflitto con la famiglia allargata. `[1.2.0]`
    * `[P]` iii. Impatto dei nonni sull'educazione dei nipoti. `[1.2.0]`
* `[ ]` d. **Tradizioni Familiari, Eredità e Rituali Quotidiani:** `[1.1.0]`
    * `[ ]` i. Le famiglie NPC sviluppano, mantengono o interrompono tradizioni uniche. `[1.1.0]`
    * `[ ]` ii. Eredità di oggetti di valore affettivo, storie, ricette, conoscenze. `[1.2.0]`
    * `[ ]` iii. Importanza dei piccoli rituali quotidiani per la coesione familiare. `[1.1.0]`
* `[ ]` e. **Gestione delle Crisi Familiari Complesse e Risoluzione dei Conflitti:** `[1.3.0]`
    * `[ ]` i. Eventi di vita stressanti per il nucleo familiare (divorzi, malattie, etc.). `[1.3.0]`
    * `[ ]` ii. Meccaniche per la gestione e la risoluzione dei conflitti. `[1.3.0]`
* `[ ]` f. **Dinamiche delle Famiglie Ricomposte, Monogenitoriali e Adottive:** `[1.2.0]`
    * `[ ]` i. Simulazione delle sfide delle famiglie ricomposte. `[1.2.0]`
    * `[ ]` ii. Simulazione delle sfide specifiche per famiglie monogenitoriali. `[1.2.0]`
    * `[ ]` iii. Processo di adozione (se implementato). `[1.3.0]`
* `[ ]` g. **Sistema di Supervisione per Minori Emancipati:** `[1.2.0]`
    * `[ ]` i. Creare un archetipo di NPC "Assistente Sociale" che viene assegnato ai minori che vivono da soli. `[1.2.0]`
    * `[ ]` ii. Implementare un evento `SOCIAL_WORKER_VISIT` che si attiva periodicamente (es. una volta al mese) e viene segnato nel calendario dei minori. `[1.2.0]`
    * `[ ]` iii. **Logica dell'Ispezione:** Durante la visita, l'assistente sociale valuta diversi parametri:
        * `[ ]` 1. Lo stato della casa (pulizia, ordine - da `XVIII.3`).
        * `[ ]` 2. La disponibilità di cibo (scorte domestiche - da `IV.1.k`).
        * `[ ]` 3. Lo stato generale dei bisogni e dell'umore dei minori.
        * `[ ]` 4. Il loro rendimento scolastico (`V.3`).
    * `[ ]` iv. **Conseguenze della Visita:** L'esito della visita ha conseguenze tangibili.
        * `[ ]` 1. **Esito Positivo:** Genera un moodlet "Rassicurato" e conferma lo status di indipendenza.
        * `[ ]` 2. **Esito Negativo:** Genera un moodlet "Preoccupato", un avvertimento ufficiale, e forse un "compito" da svolgere (es. "Migliora i tuoi voti", "Pulisci la casa").
        * `[ ]` 3. **Esito Molto Negativo (dopo avvertimenti ripetuti):** Rischio di revoca dello status di emancipazione (meccanica avanzata). `[1.3.0]`
    * `[ ]` v. **Impatto sull'IA:** L'avvicinarsi della visita può creare un "Problema" ad alta priorità per l'IA dei minori ("Pulisci la casa prima dell'arrivo dell'assistente sociale!"). `[1.2.0]`

---

## 📡 XXIX. MEDIA, INFORMAZIONE E PAESAGGIO CULTURALE DI ANTHALYS `[ ]`

* `[ ]` a. **Panorama dei Media di Anthalys:** `[1.2.0]`
    * `[ ]` i. Definizione di diverse tipologie di media (giornali, radio, TV, blog, social). `[1.2.0]`
    * `[ ]` ii. Alcune testate/piattaforme potrebbero avere un orientamento politico o un diverso livello di affidabilità. `[1.2.0]`
* `[P]` b. **Produzione di Contenuti Mediatici da Parte degli NPC:** `[1.1.0]`
    * `[P]` i. NPC con carriere e skill rilevanti possono creare contenuti. `[1.1.0]`
    * `[ ]` ii. Il successo e la diffusione di questi contenuti dipendono da qualità, originalità e risonanza. `[1.2.0]`
* `[P]` c. **Consumo di Media e Formazione dell'Opinione Pubblica:** `[1.1.0]`
    * `[P]` i. Gli NPC scelgono quali media consumare in base ai loro tratti, interessi, ecc. `[1.1.0]`
    * `[ ]` ii. Il consumo di media influenza conoscenze, opinioni, umore e comportamento. `[1.2.0]`
    * `[ ]` iii. Meccaniche per la diffusione di notizie "virali" (vere o false). `[1.3.0]`
* `[ ]` d. **Libertà di Stampa, Etica Giornalistica e Regolamentazione dei Media:** `[1.2.0]`
    * `[P]` i. Definire il livello di libertà di stampa garantito dalla Costituzione. `[1.0.0]`
    * `[ ]` ii. (Avanzato) Meccaniche di giornalismo investigativo che scopre scandali. `[1.3.0]`
    * `[ ]` iii. (Avanzato) Tentativi di censura o manipolazione dell'informazione. `[FUTURO]`
    * `[ ]` iv. Esistenza di un codice deontologico e un garante per i media (astratti). `[1.2.0]`
* `[ ]` e. **Evoluzione Dinamica del Paesaggio Mediatico:** `[1.3.0]`
    * `[ ]` i. Possibilità che nuove testate emergano nel tempo. `[1.3.0]`
    * `[ ]` ii. Le testate esistenti possono guadagnare o perdere popolarità, o chiudere. `[1.3.0]`
* `[ ]` f. **Impatto Culturale a Lungo Termine dei Media:** `[1.3.0]`
    * `[ ]` i. I media contribuiscono a definire la cultura e la memoria collettiva di Anthalys. `[1.3.0]`

---

## 🌿 XXX. FLORA DI ANTHALYS: Ecosistemi Vegetali, Biodiversità e Interazioni `[ ]`

### **1. Biomi e Zone Climatiche Vegetali di Anthalys:** `[1.2.0]`
    * `[ ]` a. Definizione dei principali biomi (foreste, praterie, zone montane). `[1.2.0]`
    * `[ ]` b. Mappatura (astratta) della distribuzione di questi biomi. `[1.2.0]`

### **2. Catalogo Dettagliato della Flora Nativa e Introdota:** `[1.2.0]`
    * `[ ]` a. Elenco e descrizione delle principali specie di alberi, arbusti, fiori. `[1.2.0]`
    * `[ ]` b. Differenziazione tra flora autoctona e specie introdotte. `[1.3.0]`
    * `[ ]` c. Identificazione di piante rare, protette, o con proprietà uniche. `[1.2.0]`

### **3. Cicli Vitali, Riproduzione e Dinamiche Stagionali della Flora:** `[1.2.0]`
    * `[ ]` a. Simulazione di crescita, fioritura, fruttificazione, semina. `[1.2.0]`
    * `[ ]` b. Meccanismi di propagazione naturale (vento, animali, acqua). `[1.3.0]`
    * `[P]` c. Adattamenti della flora ai cicli stagionali. `[1.2.0]`

### **4. Interazioni Ecologiche della Flora:** `[1.3.0]`
    * `[ ]` a. Ruolo della flora nella catena alimentare. `[1.3.0]`
    * `[ ]` b. Interazioni con la fauna (cibo, riparo, impollinazione). `[1.3.0]`
    * `[ ]` c. Impatto della flora sulla qualità del suolo, dell'acqua e dell'aria. `[1.3.0]`
    * `[ ]` d. Reazione della flora all'inquinamento o ai cambiamenti climatici. `[FUTURO]`

### **5. Flora Urbana, Parchi e Paesaggistica:** `[1.1.0]`
    * `[P]` a. Specie vegetali utilizzate nella pianificazione urbana. `[1.1.0]`
    * `[ ]` b. Manutenzione del verde urbano. `[1.1.0]`
    * `[P]` c. Concetto di "giardini verticali" o tetti verdi sugli edifici. `[1.1.0]`

### **6. Utilizzo Umano della Flora Selvatica (non coltivata):** `[1.2.0]`
    * `[ ]` a. Possibilità per gli NPC di raccogliere piante selvatiche. `[1.2.0]`
    * `[ ]` b. Regolamentazione della raccolta per specie protette. `[1.2.0]`

---

## 🐾 XXXI. FAUNA DI ANTHALYS: Specie Selvatica, Comportamenti ed Ecosistemi Animali `[ ]`

### **1. Classificazione ed Ecosistemi della Fauna Selvatica di Anthalys:** `[1.3.0]`
    * `[ ]` a. Definizione delle principali specie di mammiferi, uccelli, rettili, ecc. `[1.3.0]`
    * `[ ]` b. Identificazione di specie iconiche, rare, o in via di estinzione. `[1.3.0]`
    * `[ ]` c. Definizione delle catene alimentari e delle nicchie ecologiche. `[1.3.0]`

### **2. Comportamento Animale (IA Selvatica):** `[1.3.0]`
    * `[ ]` a. Routine giornaliere e stagionali (migrazione, letargo, accoppiamento). `[1.3.0]`
    * `[ ]` b. Interazioni intraspecifiche (dinamiche di branco/gruppo). `[1.3.0]`
    * `[ ]` c. Interazioni interspecifiche (predazione, competizione). `[1.3.0]`
    * `[ ]` d. Reazione agli NPC e alle attività umane. `[1.3.0]`

### **3. Habitat e Territori della Fauna Selvatica:** `[1.3.0]`
    * `[ ]` a. Definizione delle necessità di habitat per le diverse specie. `[1.3.0]`
    * `[ ]` b. Meccanismi di dispersione e colonizzazione di nuovi territori. `[FUTURO]`
    * `[P]` c. Impatto della frammentazione dell'habitat e ruolo dei corridoi ecologici. `[1.2.0]`

### **4. Legislazione e Conservazione della Fauna Selvatica:** `[1.3.0]`
    * `[ ]` a. Leggi sulla caccia, pesca, e protezione delle specie. `[1.3.0]`
    * `[P]` b. Esistenza di aree protette, parchi naturali. `[1.1.0]`
    * `[ ]` c. Ruolo di NPC o organizzazioni dedicate alla conservazione. `[1.3.0]`

### **5. Interazioni NPC con la Fauna Selvatica (non legata al possesso):** `[1.2.0]`
    * `[ ]` a. Osservazione della natura e birdwatching come hobby. `[1.2.0]`
    * `[ ]` b. Fotografia naturalistica. `[1.2.0]`
    * `[ ]` c. (Opzionale) Caccia e pesca sostenibile. `[1.3.0]`
    * `[ ]` d. Incidenti con la fauna. `[1.2.0]`

---

## 📅 XXXII. IL TEMPO IN ANTHALYS: Calendario, Cicli Stagionali, Eventi Cosmici e Festività `[ ]`

* `[P]` **0. Obiettivo Principale: Raffinare il `TimeManager` Globale:** `[1.0.0]`
    * `[P]` a. Implementare la gestione completa di festività, stagioni, ed eventi temporizzati. `[1.0.0]`
* `[P]` **1. Ciclo Giorno/Notte e Struttura Temporale di Base:** `[1.0.0]`
    * `[x]` a. Implementare ciclo giorno/notte di 28 ore. `[1.0.0]`
    * `[ ]` b. Suddivisione della giornata in fasi riconoscibili (Alba, Mattina, etc.). `[1.0.1]`
* `[P]` **2. Scala del Tempo e Gestione della Velocità di Gioco:** `[1.0.0]`
    * `[P]` a. Definire la scala temporale standard della simulazione. `[1.0.0]`
    * `[P]` b. Implementare controlli per la velocità di gioco. `[1.0.0]`
* `[P]` **3. Calendario Ufficiale di Anthalys: Anni, Mesi, Settimane e Giorni:** `[1.0.0]`
    * `[x]` a. Struttura dell'Anno di Anthalys: 18 mesi da 24 giorni. `[1.0.0]`
    * `[ ]` b. Nomi dei Giorni della Settimana e dei Mesi. `[1.0.1]`
    * `[P]` c. Sistema per calcolare e visualizzare la data completa corrente. `[1.0.0]`
* `[P]` **4. Calcolo Età, Compleanni ed Eventi Anniversari:** `[1.0.0]`
    * `[P]` a. Calcolo preciso dell'età degli NPC. `[1.0.0]`
    * `[P]` b. I compleanni sono eventi annuali che possono essere celebrati. `[1.0.1]`
    * `[ ]` c. (Avanzato) Anniversari significativi (matrimonio, lavoro, etc.). `[1.1.0]`
* `[ ]` **5. Calendario delle Festività e Tradizioni Culturali di Anthalys:** `[1.1.0]`
    * `[ ]` a. **Sistema di Gestione delle Festività:** `[1.1.0]`
    * `[ ]` b. **Festività Fisse di Anthalys:** `[1.1.0]`
        * `[ ]` i. Struttura Dettagliata per Ogni Festività Fissa. `[1.1.0]`
        * `[ ]` ii. Elenco Festività Fisse (Giorno Fondazione, Festa Raccolto, etc.). `[1.1.0]`
    * `[ ]` c. **Festività Mobili di Anthalys:** `[1.2.0]`
        * `[ ]` i. Struttura Dettagliata per Ogni Festività Mobile. `[1.2.0]`
        * `[ ]` ii. Elenco Festività Mobili (Festa Fioritura, Festival Lanterne). `[1.2.0]`
    * `[P]` d. **Integrazione delle Festività nel Comportamento degli NPC:** `[1.0.1]`
    * `[ ]` e. **Sviluppo e Evoluzione Dinamica delle Tradizioni (Molto Avanzato):** `[FUTURO]`
* `[P]` **6. Ciclo delle Stagioni e Impatto Ambientale di Base:** `[1.0.0]`
    * `[ ]` a. Definizione del ciclo stagionale di Anthalys. `[1.1.0]`
    * `[P]` b. Impatto visivo di base delle stagioni sull'ambiente. `[1.0.1]`
    * `[P]` c. Effetti generali delle stagioni su comportamento e umore. `[1.0.1]`
* `[ ]` **7. Motore Astronomico di Base ed Eventi Cosmici:** `[1.2.0]`
    * `[ ]` a. Implementazione di un ciclo lunare. `[1.2.0]`
    * `[ ]` b. Utilizzo delle fasi lunari per il calcolo di festività mobili. `[1.2.0]`
    * `[ ]` c. (Avanzato) Possibilità di altri eventi cosmici (piogge di meteoriti, comete). `[1.3.0]`
    * `[ ]` d. (Lore) Definizione delle costellazioni. `[1.2.0]`
* `[P]` **8. `TimeManager` Globale: Funzionalità e Metodi Helper:** `[1.0.0]`
    * `[x]` a. Esistenza di un oggetto `TimeManager` centrale. `[1.0.0]`
    * `[P]` b. Il `TimeManager` notifica gli altri sistemi. `[1.0.0]`
    * `[P]` c. Fornitura di una robusta API (metodi helper). `[1.0.0]`
        * `[P]` i. Verificare se un giorno è lavorativo/scolastico. `[1.0.0]`
        * `[ ]` ii. Ottenere la stagione corrente. `[1.1.0]`
        * `[P]` iii. Calcolare la differenza tra date. `[1.0.0]`
        * `[ ]` iv. Gestire un sistema di "allarmi" o "eventi programmati a tempo". `[1.0.2]`

---

## 🛡️ XXXIII. VITA MILITARE, DIFESA NAZIONALE E CERIMONIE DI STATO DI ANTHALYS `[ ]`

* `[!]` a. **Principio Generale:** Definire il sistema di difesa nazionale. `[1.1.0]`
* `[ ]` **1. Servizio di Leva Obbligatorio ad Anthalys:** `[1.1.0]`
    * `[ ]` a. Obbligatorietà e Requisiti. `[1.1.0]`
    * `[ ]` b. Struttura del Servizio di Leva (18 mesi, fasi, reparti separati). `[1.1.0]`
    * `[ ]` c. Formazione e Addestramento durante la Leva. `[1.2.0]`
    * `[ ]` d. Sistema di Licenze per Reclutati. `[1.1.0]`
    * `[ ]` e. Stipendio dei Reclutati di Leva. `[1.1.0]`
    * `[ ]` f. Supporto e Benessere dei Reclutati. `[1.1.0]`
* `[ ]` **2. Regolamento sulle Cerimonie Quotidiane: Alzabandiera e Ammainabandiera:** `[1.1.0]`
    * `[!]` a. Obbligatorietà e solennità delle cerimonie. `[1.1.0]`
    * `[ ]` b. Dettagli delle Cerimonie (orari, protocollo). `[1.1.0]`
    * `[ ]` c. Sanzioni per Mancata Partecipazione. `[1.2.0]`
    * `[ ]` d. Procedure di Applicazione Sanzioni. `[1.2.0]`
    * `[ ]` e. Supporto e Misure Preventive. `[1.1.0]`
* `[ ]` **3. Regolamento sulla Giornata Tipo del Servizio di Leva (28 Ore):** `[1.1.0]`
    * `[ ]` a. Struttura Oraria Dettagliata della Giornata Tipo. `[1.1.0]`
    * `[ ]` b. Sanzioni e Supporto. `[1.2.0]`
    * `[ ]` c. Flessibilità del programma per emergenze/esercitazioni. `[1.1.0]`
* `[ ]` **4. Regolamento sui Turni di Guardia e Pattugliamento:** `[1.1.0]`
    * `[!]` a. Responsabilità fondamentale per tutti i reclutati. `[1.1.0]`
    * `[ ]` b. Struttura dei Turni di Guardia (Diurni e Notturni). `[1.1.0]`
    * `[ ]` c. Organizzazione dei Turni (rotazione, programma). `[1.1.0]`
    * `[ ]` d. Aree e Modalità di Pattugliamento. `[1.1.0]`
    * `[ ]` e. Supporto e Sicurezza durante i Turni. `[1.1.0]`
    * `[ ]` f. Sanzioni per negligenza. `[1.2.0]`
* `[ ]` **5. Regolamento sulle Relazioni Personali nel Servizio di Leva:** `[1.1.0]`
* `[ ]` **6. Formazione per Avanzamento di Grado e Organizzazione Cerimonie Ufficiali:** `[1.2.0]`
* `[ ]` **7. Cerimonia e Marcetta di Congedo dello Scaglione di Leva:** `[1.2.0]`
* `[ ]` **8. Struttura e Ruolo Generale delle Forze di Difesa di Anthalys (FDA):** `[1.1.0]`
* `[ ]` **9. Equipaggiamento, Mezzi e Tecnologie Difensive delle FDA:** `[1.2.0]`

---

## 🚀 XXXIV. EVOLUZIONE ARCHITETTURALE FUTURA `[ ]`
* `[ ]` **1. Evoluzione a Classi per Sistemi basati su Enum (Pattern Strategy):** 
    * `[P]` a. Valutare la trasformazione di sistemi come `LifeStage`, `Aspiration`, `RelationshipType` da semplici Enum a sistemi basati su classi specifiche (es. `ChildLifeStage`, `WealthBuilderAspiration`) per incapsulare logica e dati in modo più pulito, seguendo il pattern già applicato ai Tratti. `[FUTURO]`

## 🤝 XXXV. REPUTAZIONE E CAPITALE SOCIALE `[ ]`

*Questa sezione definisce un sistema per tracciare la reputazione pubblica di un NPC e il valore della sua rete sociale, influenzando le opportunità e le interazioni nel mondo di gioco.*

### **1. Attributi Fondamentali del Personaggio:** `[1.2.0]`
    * `[ ]` a. Aggiungere `reputation_score: int` a `Character` (da -100 a +100, dove 0 è neutro/sconosciuto). `[1.2.0]`
    * `[ ]` b. Aggiungere `social_capital_score: int` a `Character` (da 0 in su). `[1.2.0]`

### **2. Meccaniche della Reputazione Dinamica:** `[1.2.0]`
    * `[ ]` a. **Guadagno di Reputazione:** Gli NPC guadagnano reputazione positiva compiendo azioni pubbliche lodevoli. `[1.2.0]`
        * `[ ]` i. Successo in carriere pubbliche (Politico, Atleta, Artista).
        * `[ ]` ii. Creazione di opere di alta qualità (un libro famoso, un dipinto esposto).
        * `[ ]` iii. Azioni di volontariato o beneficenza visibili alla comunità.
        * `[ ]` iv. Eventi positivi riportati dai media (es. salvare qualcuno).
    * `[ ]` b. **Perdita di Reputazione:** Gli NPC perdono reputazione con azioni pubbliche negative. `[1.2.0]`
        * `[ ]` i. Essere scoperti a compiere un crimine.
        * `[ ]` ii. Litigare o combattere in pubblico.
        * `[ ]` iii. Scandali pubblici (es. tradimento scoperto).
        * `[ ]` iv. Fallimenti professionali di alto profilo.
    * `[ ]` c. **Sistema di Gossip e Passaparola (Espansione di `VII.9`):** `[1.3.0]`
        * `[ ]` i. Quando gli NPC socializzano, hanno una probabilità di "gossippare" su un altro NPC che conoscono entrambi.
        * `[ ]` ii. Il gossip diffonde informazioni (vere o false) su azioni recenti, influenzando la reputazione del target presso chi ascolta.
        * `[ ]` iii. Tratti come `GOSSIP`, `JEALOUS`, `LOYAL` influenzano la probabilità e la natura del pettegolezzo.

### **3. Meccaniche del Capitale Sociale:** `[1.2.0]`
    * `[ ]` a. **Accumulo di Capitale Sociale:** Gli NPC lo accumulano costruendo e mantenendo relazioni forti e diversificate. `[1.2.0]`
        * `[ ]` i. Aumenta mantenendo un alto numero di relazioni con punteggio positivo (Amici, Amici Stretti, Partner).
        * `[ ]` ii. Aumenta partecipando attivamente a eventi comunitari e hobby di gruppo.
        * `[ ]` iii. Azioni come `OFFER_HELP` o fare favori aumentano direttamente il capitale sociale con il beneficiario.
    * `[ ]` b. **Utilizzo del Capitale Sociale:** `[1.3.0]`
        * `[ ]` i. Nuova azione `ASK_FOR_FAVOR` disponibile con NPC con cui si ha una buona relazione.
        * `[ ]` ii. Il successo della richiesta dipende dal capitale sociale dell'iniziatore e dalla relazione specifica.
        * `[ ]` iii. Favori possibili: piccolo prestito di denaro, aiuto per trovare lavoro, presentazione a un nuovo contatto sociale, aiuto nella cura dei figli.

### **4. Impatto sul Gameplay e sull'IA:** `[1.2.0]`
    * `[ ]` a. **Impatto della Reputazione:** `[1.2.0]`
        * `[ ]` i. Una buona reputazione sblocca interazioni sociali uniche ("Chiedi un Autografo", "Mostra Ammirazione").
        * `[ ]` ii. Influenza la reazione iniziale di NPC sconosciuti.
        * `[ ]` iii. Può dare vantaggi o svantaggi nella carriera.
    * `[ ]` b. **Impatto del Capitale Sociale:** `[1.2.0]`
        * `[ ]` i. L'IA di un NPC con basso capitale sociale e un bisogno critico potrebbe essere più propensa a compiere azioni disperate.
        * `[ ]` ii. Un alto capitale sociale agisce come una "rete di sicurezza" per l'NPC, dandogli più opzioni per risolvere i problemi.
    * `[ ]` c. **Integrazione con `AIDecisionMaker`:** `[1.2.0]`
        * `[ ]` i. La valutazione delle azioni sociali ora considera anche la reputazione del target.
        * `[ ]` ii. L'IA può generare un "Problema" specifico per "Migliorare la Reputazione" se questa scende sotto una soglia critica.

---

## 🌍 XXXVI. SISTEMA DI CONVINZIONI E VISIONE DEL MONDO (WORLDVIEW) `[ ]`

*Questa sezione definisce un sistema avanzato che permette agli NPC di sviluppare un set di convinzioni personali e una "visione del mondo" basata sulle loro esperienze di vita, che a sua volta influenza profondamente il loro processo decisionale.*

### **1. Architettura del Sistema di Convinzioni:** `[2.0.0]`
    * `[ ]` a. **Definire la Classe `Belief`:** Creare una classe o dataclass per rappresentare una singola convinzione. `[2.0.0]`
        * `[ ]` i. Attributi: `belief_type` (Enum), `description` (es. "Credo che le persone siano fondamentalmente buone"), `strength` (un valore da 0.0 a 1.0 che indica quanto è radicata la convinzione).
    * `[ ]` b. **Creare il `WorldviewManager`:** Aggiungere un nuovo manager al `Character` che contiene il dizionario delle sue convinzioni attive (`Dict[BeliefType, Belief]`). `[2.0.0]`

### **2. Formazione Dinamica delle Convinzioni:** `[2.1.0]`
    * `[ ]` a. **Ruolo del `ConsequenceAnalyzer` Potenziato:** Dopo aver creato una `Memory`, il `ConsequenceAnalyzer` la passa al `WorldviewManager`. `[2.1.0]`
    * `[ ]` b. **Analisi dei Pattern di Memoria:** Il `WorldviewManager` non agisce su un singolo ricordo, ma analizza la `MemorySystem` periodicamente (es. alla fine di ogni settimana di gioco). `[2.1.0]`
        * `[ ]` i. Cerca pattern ricorrenti: "Negli ultimi 3 mesi, 8 su 10 delle mie interazioni sociali con nuove persone sono state negative".
        * `[ ]` ii. Cerca eventi formativi: "Ho appena subito un lutto devastante" o "Ho appena raggiunto il vertice della mia carriera".
    * `[ ]` c. **Sintesi di una Nuova Convinzione:** Se un pattern è sufficientemente forte, il manager crea o rafforza una `Belief` corrispondente. `[2.1.0]`
        * *Esempio: 8 interazioni negative -> Rafforza la convinzione `PEOPLE_ARE_DANGEROUS` di 0.1 punti.*
        * *Esempio: Raggiunto apice carriera -> Crea la convinzione `HARD_WORK_PAYS_OFF` con una forza di 0.5.*

### **3. Impatto sull'IA e sul Gameplay:** `[2.0.0]`
    * `[ ]` a. **Nuovo Modificatore in `AIDecisionMaker` ("Worldview Modifier"):** `[2.0.0]`
        * `[ ]` i. `_evaluate_action_candidate` viene modificato per includere un ultimo, potentissimo moltiplicatore.
        * `[ ]` ii. Prima di calcolare lo score finale, l'IA si chiede: "Questa azione è coerente con la mia visione del mondo?".
        * `[ ]` iii. *Esempio:* Un NPC con la convinzione `HARD_WORK_PAYS_OFF` (forza 0.8) riceve un enorme bonus allo score per l'azione `WORK_HARD`, anche se è stanco e il suo tratto `LAZY` la penalizzerebbe. **La convinzione appresa ha la precedenza sulla personalità innata.**
        * `[ ]` iv. *Esempio:* Un NPC con la convinzione `PEOPLE_ARE_DANGEROUS` riceve una penalità schiacciante su tutte le azioni `SocializeAction` con sconosciuti, spingendolo all'isolamento anche se il suo bisogno `SOCIAL` è critico.
    * `[ ]` b. **Generazione di Obiettivi Personali:** `[2.1.0]`
        * `[ ]` i. Le convinzioni possono generare `Whim` o obiettivi a lungo termine. Un NPC che crede che "l'arte è l'unica consolazione" potrebbe decidere autonomamente di voler visitare tutti i musei della città.

### **4. Evoluzione e Conflitto delle Convinzioni:** `[FUTURO]`
    * `[ ]` a. **Decadimento delle Convinzioni:** Le convinzioni non rafforzate da nuove esperienze possono lentamente perdere la loro `strength`. `[FUTURO]`
    * `[ ]` b. **Conflitto Cognitivo:** Cosa succede quando un NPC `OPTIMIST` (tratto innato) sviluppa la convinzione `THE_WORLD_IS_UNFAIR` a causa di continue sventure? Questo può generare moodlet unici di `INTERNAL_CONFLICT`, ansia, o persino portare a un cambiamento di tratti nel lungo periodo. `[FUTURO]`
    * `[ ]` c. **Ristrutturazione della Visione del Mondo:** Eventi di vita catartici (una nuova relazione profonda, un successo inaspettato, terapia) possono portare a una rapida e drastica ristrutturazione del sistema di convinzioni di un NPC. `[FUTURO]`

###  XXXVII. OTTIMIZZAZIONE E COMPORTAMENTI AVANZATI [NUOVA SEZIONE]

#### 1. Gestione Avanzata del Tempo nei Dialoghi: `[1.3.0+]`
* `[ ]` a. **Analisi preliminare:** Valutare pro e contro delle diverse strategie di gestione del tempo.
    * `[ ]` i. **Blocco Totale (Hard Freeze):** Semplice ma poco realistico. Il mondo intero si ferma.
    * `[ ]` ii. **Rallentamento Globale (Soft Freeze):** Il tempo scorre al 5-10%, mantenendo una sensazione di mondo vivo.
    * `[ ]` iii. **Bolla Temporale Dialogica:** Solo i partecipanti sono in uno "stato di dialogo", il resto del mondo procede normalmente. Richiede un buffer di eventi per i partecipanti.
    * `[ ]` iv. **Simulazione Asincrona:** Il mondo va avanti, le conseguenze per i partecipanti vengono calcolate "retroattivamente". Complesso da implementare.
* `[ ]` b. **(Consigliato dall'utente)** Implementare un sistema ibrido **"Soft Freeze" + "Bolla Dialogica"** come soluzione preferita, per unire realismo e performance. `[1.4.0]`

#### 2. Sistema di Livello di Dettaglio (LOD) per NPC: `[1.5.0]`
* `[ ]` a. **Simulazione "Lightweight" (AI LOD):** Per gli NPC non visibili o lontani dal giocatore, la simulazione deve essere semplificata.
    * `[ ]` i. Aggiornare solo i bisogni essenziali e il passare del tempo.
    * `[ ]` ii. Disabilitare il pathfinding complesso, le animazioni e le interazioni con oggetti non critiche.
* `[ ]` b. **LOD Grafico:** Ridurre il carico sulla GPU per gli NPC lontani (es. usare sprite più semplici o non disegnarli affatto se fuori schermo).

#### 3. (Avanzato/Futuro) IA Emergenti: `[RICERCA]` `[2.0.0+]`
* `[ ]` a. **Sincronizzazione Circadiana Adattiva:** Studiare la possibilità di usare Reinforcement Learning (RL) per permettere agli NPC di "imparare" e adattare i propri ritmi circadiani e le proprie routine in base all'ambiente e agli eventi della simulazione.
    * **Riferimento Scientifico:** [Emergence of Adaptive Circadian Rhythms in Groups of Interacting Organisms (arxiv.org)](https://arxiv.org/abs/2307.12143)
