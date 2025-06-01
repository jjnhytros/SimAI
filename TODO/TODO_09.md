## IX. ABILITÀ (SKILLS) `[]`

* `[P]` a. **Struttura Base per le Abilità:**
    * `[]` i. `SkillType` Enum definita e mantenuta. *(Considerare aggiunta futura di `SELF_CONTROL`)*. (Vecchio `IV.1.f` Suddivisione in categorie (es. Sociale, Mentale, Fisica, Creativa, Pratica, Bambini, Toddler). *(Struttura directory implementata)*)
    * `[P]` ii. Creare una classe `BaseSkill` in `modules/skills/base_skill.py` per gestire:
        * `[P]` 1. Livelli di abilità (es. da 1 a `settings.MAX_SKILL_LEVEL`). (Le abilità hanno livelli (es. 1-12, 1-6, 1-3 come da specifiche utente). *(Implementare con max_level variabile)*)
        * `[]` 2. Punti Esperienza (XP) per ogni abilità. *(Concetto base definito in `BaseSkill`)*. (Vecchio `IV.1.b` Si guadagna XP per le abilità compiendo azioni correlate. *(Logica base nelle classi Skill)*)
        * `[]` 3. Logica di progressione ai livelli successivi basata su XP accumulata. *(Metodo `add_experience` abbozzato in `BaseSkill`)*.
        * `[]` 4. Implementare la progressione di XP specifica per livello (es. 2, 3, 4, 6, 12, 24, 36 XP per avanzare) nel metodo `BaseSkill._calculate_xp_for_level`. *(Formula attuale in `BaseSkill` è un placeholder, da adattare alla progressione desiderata)*.
    * `[]` iii. Creare classi specifiche per ogni `SkillType` (es. `CharismaSkill`, `ProgrammingSkill`, `CraftingGeneralSkill`, ecc.) in sottocartella `modules/skills/`, che ereditano da `BaseSkill`. *(Iniziato concettualmente con `CharismaSkill`, `CraftingGeneralSkill`, `ResearchSkill`, ecc. Molte altre da creare)*.
        * `[]` 1. Ogni classe Skill specifica può sovrascrivere la curva XP o aggiungere benefici unici sbloccati a determinati livelli. (Vecchio `IV.1.c` Livelli più alti sbloccano nuove interazioni, ricette, oggetti creabili, o migliorano la qualità/velocità delle azioni. *(Implementato nelle classi Skill)*)
    * `[]` iv. Modificare `Character.skills` per contenere istanze di queste classi Skill (es. `Dict[SkillType, BaseSkill]`). *(Da implementare in `Character.__init__` e `constructors.py`)*.
    * `[]` v. Modificare la logica di guadagno skill (in Azioni e Tratti) per utilizzare il metodo `skill_obj.add_experience(punti_xp)` invece di incrementare direttamente un valore float. *(Da implementare, impatta molte classi Azione e Tratto)*.
    * `[]` vi. Alcune abilità potrebbero avere libri per apprenderle più velocemente. (Vecchio `IV.1.d`)
    * `[]` vii. Possibilità di "Mentoring" da NPC con abilità più alta. *(Incluso come sblocco Liv10/Max in molte skill)* (Vecchio `IV.1.e`)
* `[]` b. **IA per Scelta Sviluppo Abilità:**
    * `[]` i. Gli NPC (specialmente quelli dettagliati) decidono attivamente quali abilità migliorare in base a:
        * Tratti di personalità (es. `EGGHEAD` preferisce skill mentali, `ARTISAN` quelle manuali).
        * Aspirazioni (se l'aspirazione richiede una certa skill).
        * Requisiti della carriera attuale o desiderata.
        * Interessi/Hobby (se implementati).
        * Opportunità di apprendimento disponibili (es. libri, corsi, mentoring).
* `[]` c. **Abilità influenzano azioni e loro esiti.**
    * `[]` i. Espandere il set di abilità e il loro impatto sulle azioni. *(Molti tratti ora definiscono modificatori al guadagno di specifiche skill; l'impatto effettivo delle skill sull'esito delle azioni è definito tratto per tratto e azione per azione).*.
    * `[]` ii. Definire azioni specifiche per l'apprendimento attivo di ciascuna skill (es. `STUDY_PROGRAMMING_BOOK`, `PRACTICE_INSTRUMENT`, `ATTEND_COOKING_CLASS`).
    * `[]` iii. Le skill sbloccano interazioni sociali o possibilità di azioni uniche (es. un alto livello di `CHARISMA` sblocca opzioni di dialogo persuasive, un alto livello di `CRAFTING_GENERAL` permette di creare oggetti più complessi o di qualità superiore).
    * `[]` iv. Il livello di una skill influenza la probabilità di successo, la qualità dell'esito, o la velocità di completamento di azioni correlate.
    * `[]` v. (Avanzato) Sistema di "decadimento skill" se un'abilità non viene usata per molto tempo (opzionale).
* `[]` d. **Gestione Skill per NPC di Background (LOD3):**
    * `[]` i. Gli NPC di background tracciano solo un numero limitato di `key_skills` (definite nel loro `BackgroundNPCState`). *(Concetto definito)*.
    * `[]` ii. La progressione di queste `key_skills` avviene lentamente e probabilisticamente durante gli "heartbeat" periodici (mensili/annuali), influenzata da lavoro/scuola astratti, performance astratta, e tratti/archetipo dominanti. *(Concettualizzazione in corso)*.
* `[]` e. **Elenco Abilità (da implementare o dettagliare):**
    *(Molte sono state dettagliate, contrassegnate con [] o [] se la classe base o i livelli sono stati definiti)*
    * `[]` Acting (Recitazione) (12)
    * `[]` Agility (Agilità) - (Horse Skill) `[F_DLC_C.5]` *(Dipende da Sistema Animali)*
    * `[]` Archaeology (Archeologia) (12)
    * `[]` Baking (Pasticceria) (12)
    * `[]` Battery Drum (Batteria) (12) *(Classe implementata)*
    * `[]` Bowling (6)
    * `[]` Cello (Violoncello) (12) *(Livelli dettagliati)*
    * `[]` Charisma (Carisma) (12)
    * `[]` Comedy (Commedia) (12)
    * `[]` Communication (Comunicazione) - (Toddler Skill) (6)
    * `[]` Cooking (Cucina) (12)
    * `[]` Creativity (Creatività) - (Child Skill) (12)
    * `[]` Cross-Stitch (Punto Croce) (6)
    * `[]` DJ Mixing (Mixaggio DJ) (12)
    * `[]` Dancing (Ballo) (6)
    * `[]` Driving (Guida) (12) *(Classe implementata)*
    * `[]` Endurance (Resistenza) - (Horse Skill) `[F_DLC_C.5]` *(Dipende da Sistema Animali)*
    * `[]` Entrepreneur (Imprenditore) (6)
    * `[]` Fabrication (Fabbricazione) (12)
    * `[]` Fishing (Pesca) (12)
    * `[]` Fitness (12)
    * `[]` Flower Arranging (Composizione Floreale) (12)
    * `[]` Gardening (Giardinaggio) (12) *(Classe implementata)*
    * `[]` Gemology (Gemmologia) (12)
    * `[]` Gourmet Cooking (Cucina Gourmet) (12)
    * `[]` Guitar (Chitarra) (12)
    * `[]` Handiness (Manualità) (12)
    * `[]` Herbalism (Erboristeria) (12)
    * `[]` Horse Riding (Equitazione) `[F_DLC_C.5]` *(Dipende da Sistema Animali)*
    * `[]` Imagination (Immaginazione) - (Toddler Skill) (6)
    * `[]` Juice Fizzing (Frizzaggio Succhi) (6)
    * `[]` Jumping (Salto) - (Horse Skill) `[F_DLC_C.5]` *(Dipende da Sistema Animali)*
    * `[]` Knitting (Lavoro a Maglia) (12)
    * `[]` Logic (Logica) (12)
    * `[]` Lute (Liuto) (12) *(Livelli dettagliati)*
    * `[]` Media Production (Produzione Media) (6)
    * `[]` Mental (Mentale) - (Child Skill) (12)
    * `[]` Mischief (Malizia) (12)
    * `[]` Mixology (Mixologia) (12)
    * `[]` Motor (Motorio) - (Child Skill) (12)
    * `[]` Movement (Movimento) - (Toddler Skill) (6)
    * `[]` Nectar Making (Produzione di Nettare) (6)
    * `[]` Negotiation (Negoziazione) (12) *(Classe implementata, max_level aggiornato)*
    * `[]` Painting (Pittura) (12)
    * `[]` Parenting (Genitorialità) (12)
    * `[] [F_DLC_C.5]` Pet Training (Addestramento Animali) (6) *(Dipende da Sistema Animali)*
    * `[]` Photography (Fotografia) (6)
    * `[]` Piano (Pianoforte) (12)
    * `[]` Pipe Organ (Organo a Canne) (12)
    * `[]` Pottery (Ceramica) (12)
    * `[]` Potty (Vasino) - (Toddler Skill) (3)
    * `[]` Potion Making (Preparazione Infusi/Decotti Alchemici/Erboristici) -> Crafting/Herbalism/Science *(Rimosso aspetto magico. Si concentra su preparati scientifici/naturali.)*
        * `[]` i. Definire scopo e meccanica: creazione di infusi, decotti, unguenti, o "elisir" non magici utilizzando erbe (`Herbalism`), ingredienti naturali, e tecniche di base di `Alchemy` (nuova potenziale sub-skill o set di ricette legate a `Science` o `Herbalism`).
        * `[]` ii. Esempi di creazioni:
            * `[]` 1. Infusi calmanti (temporaneo moodlet positivo per stress, aiuto per dormire).
            * `[]` 2. Decotti energizzanti (temporaneo piccolo boost a `ENERGY`, alternativa a caffè/tè).
            * `[]` 3. Unguenti lenitivi (per piccoli dolori muscolari da attività `FITNESS`, o irritazioni cutanee minori).
            * `[]` 4. "Tonico della Concentrazione" (temporaneo piccolo bonus a `skill_gain_modifier` per attività mentali).
            * `[]` 5. (Avanzato, con alta skill) Preparati che influenzano temporaneamente i bisogni (es. "Elisir Saziante" che riduce fame per un po', o "Bevanda Idratante Superiore").
        * `[]` iii. La qualità e l'efficacia dipendono dalla skill del creatore, dalla qualità degli ingredienti (se sistema ingredienti implementato), e dal successo nella "ricetta".
        * `[]` iv. Fallire la preparazione potrebbe risultare in un prodotto inefficace, con effetti collaterali negativi lievi, o semplicemente spreco di ingredienti.
    * `[]` Programming (Programmazione) (12)
    * `[]` Research & Debate (Ricerca e Dibattito) (12)
    * `[]` Robotics (Robotica) (12) *(Classe implementata)*
    * `[]` Rock Climbing (Arrampicata su Roccia) (12)
    * `[]` Rocket Science (Scienza Missilistica) (12)
    * `[]` Romance (Romanticismo) (12)
    * `[]` Anthalian Culture (Cultura Anthaliana) (6) *(Sostituito Selvadoradian)*
    * `[]` Saxophone (Sassofono) (12) *(Classe implementata)*
    * `[]` Singing (Canto) (12)
    * `[]` Skiing (Sci) (12)
    * `[]` Snowboarding (12)
    * `[]` Social (Sociale) - (Child Skill) (12)
    * `[]` Tattooing (Tatuaggi) (12)
    * `[] [F_DLC_C.5]` Temperament (Temperamento) - (Horse Skill) (12) *(Dipende da Sistema Animali)*
    * `[]` Thanatology (Tanatologia) (6)
    * `[]` Thinking (Pensiero) - (Toddler Skill) (6)
    * `[]` Tinker (Armeggiare/Smacchinare) (12) *(Classe implementata)*
    * `[]` Trumpet (Tromba) (12) *(Classe implementata)*
    * `[] [F_DLC_C.5]` Veterinarian (Veterinaria) (12) *(Dipende da Sistema Animali)*
    * `[]` Video Gaming (Videogiochi) (12)
    * `[]` Violin (Violino) (12)
    * `[]` Wellness (Benessere) (12)
    * `[]` Writing (Scrittura) (12)
    * `[]` Botany (Botanica) -> Mental/Cognitive o Practical
    * `[]` Charisma (Child) -> Social (Child)
    * `[] [F_DLC_C.5]` Charisma (Horse) -> Horse Skill *(Dipende da Sistema Animali)*
    * `[] [F_DLC_C.5]` Charisma (Pet) -> Pet Skill *(Dipende da Sistema Animali)*
    * `[]` Culture (Cultura - generica o per diverse culture di Anthalys) -> Mental/Cognitive
    * `[]` Deceive (Ingannare) -> Social
    * `[]` Discipline (Disciplina - per bambini/ragazzi o anche adulti) -> Mental/Cognitive
    * `[]` Diving (Immersione) -> Physical
    * `[] [F_DLC_C.5]` Dog Training (Addestramento Cani - più specifico di Pet Training) -> Practical/Pet Skill *(Dipende da Sistema Animali)*
    * `[]` Drama (Recitazione - forse un duplicato di Acting?) -> Creative
    * `[]` Education (Pedagogia - per insegnanti) -> Mental/Cognitive o Professional
    * `[]` Empathy (Empatia - diversa da Charisma) -> Social
    * `[]` Etiquette (Galateo) -> Social
    * `[]` Firemaking (Accendere Fuoco - sopravvivenza o campeggio) -> Practical/Outdoor
    * `[]` First Aid (Primo Soccorso) -> Practical/Medical
    * `[]` Fitness (Child) -> Physical (Child)
    * `[]` Flower Arranging (Child) -> Creative (Child)
    * `[]` Foraging (Raccolta Cibo Selvatico) -> Outdoor/Practical
    * `[]` Handiness (Child) -> Practical (Child)
    * `[]` History (Storia) -> Mental/Cognitive
    * `[]` Humor (Umorismo - diverso da Comedy, più la capacità di apprezzare/fare battute) -> Social
    * `[]` Hunting (Caccia - se il lore lo permette) -> Outdoor/Practical `[F_DLC_C.5]` *(Se per animali selvatici, dipende da Sistema Animali)*
    * `[]` Influence (Influenzare - capacità di cambiare opinioni altrui) -> Social
    * `[]` Investigation (Investigazione - per detective, giornalisti) -> Mental/Cognitive
    * `[]` Journalism (Giornalismo) -> Creative/Professional
    * `[]` Languages (Lingue Straniere - per diverse lingue di Anthalys) -> Mental/Cognitive
    * `[]` Law (Legge) -> Mental/Cognitive/Professional
    * `[]` Leadership (Child) -> Social (Child)
    * `[]` Lock-picking (Scassinare Serrature) -> Practical (potenzialmente illegale)
    * `[]` Martial Arts (Arti Marziali) -> Physical
    * `[]` Mechanics (Meccanica - per auto, macchinari) -> Practical/Technology
    * `[]` Medical (Medicina - più generica di Veterinarian) -> Mental/Cognitive/Medical
    * `[]` Meditation (Meditazione - parte di Wellness, ma potrebbe essere skill a sé) -> Mental/Wellness
    * `[]` Musicianship (Teoria Musicale/Musicalità) -> Creative/Mental
    * `[]` Natural Medicine (Medicina Naturale - legata a Herbalism) -> Practical/Medical
    * `[]` Painting (Child) -> Creative (Child)
    * `[]` Photography (Child) -> Creative (Child)
    * `[]` Pickpocketing (Borseggio) -> Practical (illegale)
    * `[]` Piloting (Pilotare - aerei, navi, droni avanzati) -> Technology/Professional
    * `[]` Politics (Politica) -> Social/Professional
    * `[]` Public Speaking (Parlare in Pubblico - parte di Charisma, ma potrebbe essere skill a sé) -> Social
    * `[]` Reading Comprehension (Comprensione del Testo) -> Mental/Cognitive
    * `[]` Repair (Riparare - più generico di Handiness, o Handiness è il nome giusto) -> Pratico
    * `[]` Riding (Cavalcare - generico, Horse Riding è specifico) `[F_DLC_C.5]` *(Dipende da Sistema Animali)*
    * `[]` Sailing (Vela) -> Outdoor/Physical
    * `[]` Scavenging (Recupero Oggetti Utili da Rifiuti/Rovine) -> Outdoor/Practical
    * `[]` Science (Scienza - generica, per carriere scientifiche) -> Mental/Cognitive
    * `[]` Sculpting (Child) -> Creative (Child)
    * `[]` Sculpting (Scultura - per adulti, diversa da Pottery?) -> Creative
    * `[]` Seduction (Seduzione - diversa da Romance, più manipolativa) -> Social
    * `[]` Self-Control (Autocontrollo - per gestire emozioni/impulsi) -> Mental/Cognitive
    * `[]` Sleight of Hand (Gioco di Prestigio/Destrezza Manuale) -> Creative/Practical
    * `[]` Social Media (Gestione Social Media - per influencer, marketing) -> Social/Technology
    * `[]` Stealth (Furtività) -> Physical/Practical
    * `[]` Storytelling (Narrazione - orale o scritta) -> Creative/Social
    * `[]` Street Smarts (Scaltrezza di Strada - intelligenza pratica urbana) -> Mental/Social
    * `[]` Surgery (Chirurgia - per medici) -> Medical/Practical
    * `[]` Survival (Sopravvivenza - in natura) -> Outdoor/Practical
    * `[]` Swimming (Nuoto) -> Physical
    * `[]` Teaching (Insegnamento - per insegnanti, mentori) -> Social/Professional
    * `[]` Trapping (Uso Trappole - per caccia o altro) -> Outdoor/Practical `[F_DLC_C.5]` *(Se per animali, dipende da Sistema Animali)*
    * `[]` Weather Forecasting (Previsioni Meteo) -> Mental/Cognitive
    * `[]` Woodworking (Lavorazione Legno - parte di Handiness, ma potrebbe essere più specifica) -> Crafting/Practical
    * `[]` Yoga (Yoga - parte di Wellness, ma potrebbe essere skill a sé) -> Physical/Wellness
    * `[F_DLC_C.9]` **Nuove Abilità legate al "Sistema di Produzione Sostenibile di Anthalys" (DLC C.9):** `[NUOVA SEZIONE SKILL]`
        * `[]` **Apiculture (Apicoltura):** `[NUOVA]`
            * Gestione arnie, raccolta miele (`C.9.d.xv`), cera d'api, propoli. Cura delle api.
            * Livelli alti sbloccano tipi di miele più rari o prodotti dell'alveare di maggiore qualità.
        * `[]` **Cheesemaking (Caseificazione):** `[NUOVA]`
            * Lavorazione del latte (`C.9.d.xii`) per produrre vari tipi di formaggi artigianali (freschi, stagionati).
            * Include la gestione di fermenti, caglio, tecniche di stagionatura.
        * `[]` **Charcuterie (Salumeria Artigianale):** `[NUOVA]`
            * Preparazione e stagionatura di salumi e insaccati naturali (`C.9.d.xiii`) da carni sostenibili.
            * Include la conoscenza di spezie, tecniche di conservazione naturale.
        * `[]` **Preserving (Tecniche di Conservazione Alimentare):** `[NUOVA]`
            * Creazione di conserve, marmellate, sottaceti, essiccati (`C.9.d.xi`).
            * Include sterilizzazione, pastorizzazione, gestione pH, tecniche di essiccazione.
        * `[]` **Mycology (Micologia Applicata):** `[NUOVA]`
            * Coltivazione di funghi commestibili (`C.9.d.xvi.1`).
            * Identificazione e raccolta sicura di funghi selvatici commestibili (se Foraging non è abbastanza specifico).
        * `[]` **Advanced Baking & Pastry (Alta Pasticceria e Panificazione Avanzata):** `[NUOVA O ESTENSIONE]` (Espande `Baking`)
            * Creazione di prodotti da forno complessi, pani speciali (`C.9.d.x`), dolci elaborati, uso di lievito madre.
        * `[]` **Artisanal Chocolate Making (Cioccolateria Artigianale):** `[NUOVA]`
            * Lavorazione fave di cacao importate, temperaggio cioccolato, creazione praline, tavolette aromatizzate (`C.9.d.xvii`).
        * `[]` **Herbal Cosmetics & Soapmaking (Cosmesi Naturale e Saponificazione):** `[NUOVA]`
            * Creazione di saponi (`C.9.f.ii.1`), creme, unguenti, oli essenziali (`C.9.f.ii.3`) con ingredienti naturali e erbe (`C.9.f.ii.2`). Collegata a `Herbalism`.
        * `[]` **Sustainable Textile Arts (Arti Tessili Sostenibili):** `[NUOVA O ESTENSIONE]` (Espande `Knitting`, `Cross-Stitch`)
            * Filatura di fibre naturali (`C.9.d.ix.3`), tessitura manuale/telaio (`C.9.d.ix.4`), tintura naturale (`C.9.d.ix.5`), creazione di capi complessi.
        * `[]` **Leatherworking (Lavorazione della Pelle Sostenibile):** `[NUOVA]`
            * Tecniche di taglio, cucitura, modellatura e finitura di pelli conciate vegetalmente (`C.9.d.viii`) per creare abbigliamento e accessori.
        * `[]` **Sustainable Forestry & Woodcrafting (Silvicoltura Sostenibile e Artigianato del Legno):** `[NUOVA O ESTENSIONE]` (Espande `Woodworking`)
            * Gestione sostenibile di piccole aree boschive (se NPC possiedono terreni), selezione e lavorazione di Legno Certificato di Anthalys (`C.9.f.i.3`) per mobili, intaglio, tornitura.
        * `[]` **Bio-composite Material Crafting (Lavorazione Materiali Bio-compositi):** `[NUOVA]`
            * Creazione e modellazione di materiali bio-compositi e a base di micelio (`C.9.f.i.1`, `C.9.f.i.2`) per oggetti di design o usi specifici.
        * `[]` **Local Stone & Mineral Crafting (Artigianato della Pietra e dei Minerali Locali):** `[NUOVA]`
            * Lavorazione di pietre e minerali locali (`C.9.f.i.4`) per scultura, edilizia decorativa, gioielleria.
        * `[]` **Artisanal Pottery & Clayworking (Ceramica Artistica e Lavorazione Argilla Avanzata):** `[NUOVA O ESTENSIONE]` (Espande `Pottery`)
            * Tecniche avanzate di lavorazione argille locali (`C.9.f.i.5`), smaltatura con pigmenti naturali (`C.9.f.i.4`), cottura in forni specifici.
        * `[]` **Basket Weaving & Fiber Arts (Intreccio Cesti e Arti delle Fibre Vegetali):** `[NUOVA]`
            * Creazione di cesti, stuoie, e altri oggetti intrecciati utilizzando fibre vegetali locali (`C.9.f.iii.4`).
        * `[]` **Artisanal Instrument Making (Liuteria Artigianale di Anthalys):** `[NUOVA]`
            * Costruzione di strumenti musicali tradizionali o unici di Anthalys utilizzando materiali locali (`C.9.f.iv`).
* `[]` f. **Estensione "Total Realism" - Apprendimento Contestuale, Maestria e Impatto Reale delle Abilità:** `[NUOVA SOTTOCATEGORIA]`
    * `[]` i. **Apprendimento Basato sull'Esperienza e la Sfida:**
        * `[]` 1. Oltre al guadagno di XP da azioni ripetitive, implementare un guadagno di XP significativamente maggiore (o sblocco di livelli/perk unici) quando le abilità vengono applicate con successo in situazioni complesse, rischiose, o per risolvere problemi reali per l'NPC (es. un NPC con alta skill `HANDINESS` che ripara un oggetto cruciale durante un'emergenza guadagna più di una semplice riparazione di routine).
        * `[]` 2. L'apprendimento potrebbe essere accelerato da "fallimenti costruttivi" dove l'NPC impara cosa non fare.
    * `[]` ii. **Maestria e Riconoscimento:**
        * `[]` 1. NPC con livelli di maestria eccezionali (es. livello massimo + "specializzazione") in certe skill (es. `PAINTING`, `WRITING`, `GUITAR`, `PROGRAMMING`, `GOURMET_COOKING`, `SCIENCE`) potrebbero produrre "opere maestre" o "innovazioni" di qualità eccezionale (collegamento a `X.4` Sistema di Creazione Oggetti/Opere).
        * `[]` 2. Queste opere/innovazioni potrebbero avere un impatto tangibile nel mondo:
            * Un libro "bestseller" (skill `WRITING`) potrebbe essere letto e discusso da altri NPC, generando moodlet o influenzando opinioni (collegamento a Ecosistema dell'Informazione `VI.2.e.ii`).
            * Un dipinto famoso (skill `PAINTING`) potrebbe essere esposto in un museo (`XVIII.5.h`) e ammirato.
            * Un software innovativo (skill `PROGRAMMING`) potrebbe sbloccare nuove interazioni o migliorare l'efficienza di certe attività per chi lo usa (molto avanzato, potrebbe toccare `C. Progetti Futuri`).
            * Un piatto gourmet eccezionale (skill `GOURMET_COOKING`) potrebbe dare moodlet potentissimi o diventare famoso in città.
        * `[]` 3. Gli NPC con tale maestria potrebbero guadagnare fama/reputazione (`XVI.5`), ricevere premi (eventi `XIV`), o diventare mentori (`VII.8`) molto ricercati.
    * `[]` iii. **Applicazione Interdisciplinare delle Abilità:**
        * `[]` 1. Creare situazioni o progetti complessi dove gli NPC necessitano di combinare diverse abilità per avere successo (es. organizzare un grande evento richiederebbe `SOCIAL`, `PARTY_PLANNER` (tratto), `COOKING`, `MUSIC_LOVER` (tratto) o skill musicali, `LOGIC` per la pianificazione).
    * `[]` iv. **Decadimento Realistico delle Abilità (Opzionale Avanzato):**
        * `[]` 1. Le abilità non utilizzate per lunghi periodi potrebbero decadere lentamente, specialmente quelle pratiche o altamente specialistiche, richiedendo "ripasso" o pratica continua per mantenerle al massimo livello (più realistico di un semplice non-decadimento). Tratti come `QUICK_LEARNER` / `SLOW_LEARNER` potrebbero influenzare anche la velocità di decadimento o recupero.

---

