# core/enums/social_interaction_types.py
from enum import Enum, auto
"""
Definizione dell'Enum SocialInteractionType per le interazioni sociali tra NPC.
Riferimento TODO: VII.1.b
"""

class SocialInteractionType(Enum):
    """Enum per i diversi tipi di interazioni sociali che un NPC può avviare."""
    
    DEEP_CONVERSATION = auto()
    COMPLIMENT = auto()
    
    # ================= CATEGORIA 1: INTERAZIONI QUOTIDIANE E AMICHEVOLI (50) =================
    ASK_ABOUT_DAY = auto()
    ASK_FOR_FAVOR = auto()
    ASK_FOR_HELP = auto()
    BORROW_ITEM = auto()
    CHAT_CASUAL = auto()
    COMPLIMENT_ACHIEVEMENT = auto()
    COMPLIMENT_SKILL = auto()
    DISCUSS_BOOK = auto()
    DISCUSS_CURRENT_EVENTS = auto()
    DISCUSS_HOBBIES = auto()
    EXCHANGE_GIFTS = auto()
    EXPRESS_GRATITUDE = auto()
    GIVE_ADVICE = auto()
    GIVE_DIRECTIONS = auto()
    INVITE_TO_GATHERING = auto()
    LEND_ITEM = auto()
    OFFER_COMFORT = auto()
    OFFER_FOOD = auto()
    OFFER_HELP = auto()
    PLAN_ACTIVITY = auto()
    PLAY_GAME = auto()
    RECOMMEND_BOOK = auto()
    RECOMMEND_MOVIE = auto()
    REMINISCE = auto()
    REQUEST_OPINION = auto()
    SHARE_FOOD = auto()
    SHARE_INTEREST = auto()
    SHARE_NEWS = auto()
    SHARE_SECRET = auto()
    SHOW_PHOTOS = auto()
    SMALL_TALK = auto()
    SMILE = auto()
    TELL_JOKE = auto()
    TELL_STORY = auto()
    WAVE_HELLO = auto()
    WISH_GOOD_LUCK = auto()
    WISH_WELL = auto()
    # Nuove interazioni
    COMPARE_EXPERIENCES = auto()
    DISCUSS_DREAMS = auto()
    EXCHANGE_RECIPES = auto()
    INTRODUCE_TO_GROUP = auto()
    INVITE_FOR_COFFEE = auto()
    OFFER_RIDE = auto()
    PLAN_TRIP = auto()
    PRAISE_WORK = auto()
    RECOMMEND_MUSIC = auto()
    SHARE_MEMORY = auto()
    SHARE_PERSONAL_GOAL = auto()
    SUGGEST_HOBBY = auto()
    TALK_ABOUT_PETS = auto()
    TALK_ABOUT_TRAVEL = auto()
    
    # ================= CATEGORIA 2: INTERAZIONI ROMANTICHE E SENSUALI (50) =================
    BLIND_DATE_SETUP = auto()
    COMPLIMENT_APPEARANCE = auto()
    CONFESS_ATTRACTION = auto()
    CONFESS_LOVE = auto()
    DANCE_TOGETHER = auto()
    EXCHANGE_LOVE_LETTERS = auto()
    FLIRT = auto()
    GIVE_ROMANTIC_GIFT = auto()
    HOLD_HANDS = auto()
    KISS = auto()
    MAKE_EYE_CONTACT = auto()
    PLAN_ROMANTIC_GETAWAY = auto()
    PROPOSE_COMMITMENT = auto()
    PROPOSE_DATE = auto()
    PROPOSE_INTIMACY = auto()
    PROPOSE_MARRIAGE = auto()
    ROMANTIC_DINNER = auto()
    SEND_FLOWERS = auto()
    SHARE_FANTASY = auto()
    SHARE_FUTURE_PLANS = auto()
    STARE_ROMANTICALLY = auto()
    SURPRISE_VISIT = auto()
    WHISPER_SWEET_NOTHINGS = auto()
    # Nuove interazioni
    ARRANGE_CANDLELIGHT_DINNER = auto()
    ASK_FOR_DANCE = auto()
    COMPLIMENT_SCENT = auto()
    CONFESS_DESIRE = auto()
    DISCUSS_RELATIONSHIP_FUTURE = auto()
    EXCHANGE_PROMISES = auto()
    FLIRTATIOUS_TEASING = auto()
    GENTLE_TOUCH = auto()
    INITIATE_PHYSICAL_CONTACT = auto()
    INVITE_TO_PRIVATE_SPACE = auto()
    MASSAGE_PARTNER = auto()
    PLAYFUL_BANTER = auto()
    PROPOSE_STAYCATION = auto()
    RECITE_POETRY = auto()
    SEND_LOVE_TEXT = auto()
    SHARE_INTIMATE_SECRET = auto()
    SUGGEST_COUPLE_ACTIVITY = auto()
    WALK_ARM_IN_ARM = auto()
    WATCH_SUNSET_TOGETHER = auto()
    WRITE_LOVE_SONG = auto()
    # Interazioni sensuali
    DISCUSS_BOUNDARIES = auto()
    EXPLORE_FANTASIES = auto()
    EXPRESS_SENSUAL_DESIRES = auto()
    INITIATE_AFFECTION = auto()
    PLAYFUL_WHISPERING = auto()
    PROPOSE_ADVENTURE = auto()
    SENSUAL_COMPLIMENT = auto()
    SHARE_EROTIC_DREAM = auto()
    SUGGEST_INTIMATE_GAME = auto()
    TALK_ABOUT_KINKS = auto()
    
    # ================= CATEGORIA 3: INTERAZIONI FAMILIARI E DI GRUPPO (50) =================
    APOLOGIZE_TO_FAMILY = auto()
    ASK_FOR_FAMILY_ADVICE = auto()
    ASK_FOR_HELP_HOMEWORK = auto()
    BABYSIT = auto()
    CELEBRATE_ANNIVERSARY = auto()
    DISCUSS_FAMILY_HISTORY = auto()
    FAMILY_DINNER = auto()
    FAMILY_GAME_NIGHT = auto()
    GIVE_FAMILY_GIFT = auto()
    GRIEVE_TOGETHER = auto()
    HELP_WITH_CHORES = auto()
    MEDIATE_FAMILY_DISPUTE = auto()
    PARENTAL_ADVICE = auto()
    PARENTAL_PRAISE = auto()
    PLAY_WITH_CHILD = auto()
    READ_TO_CHILD = auto()
    SEEK_BLESSING = auto()
    SEEK_PARENTAL_APPROVAL = auto()
    SIBLING_BONDING = auto()
    SIBLING_RIVALRY = auto()
    SIBLING_TEASING = auto()
    TEACH_CHILD_SKILL = auto()
    # Nuove interazioni
    ADOPT_PET_TOGETHER = auto()
    CELEBRATE_GRADUATION = auto()
    DISCUSS_PARENTING = auto()
    FAMILY_PHOTO_SESSION = auto()
    FAMILY_VACATION_PLAN = auto()
    GIVE_ELDERLY_CARE = auto()
    HELP_WITH_HOMEWORK = auto()
    HOST_FAMILY_GATHERING = auto()
    INCLUDE_IN_FAMILY_TRADITION = auto()
    INTRODUCE_PARTNER_TO_FAMILY = auto()
    ORGANIZE_REUNION = auto()
    PASS_DOWN_HEIRLOOM = auto()
    PLAN_GENERATIONAL_MEAL = auto()
    PREPARE_FAMILY_RECIPE = auto()
    SHARE_ANCESTRY_STORIES = auto()
    SUPPORT_FAMILY_MEMBER = auto()
    TEACH_FAMILY_TRADITION = auto()
    # Interazioni di gruppo
    COLLABORATE_ON_PROJECT = auto()
    DEBATE_GROUP_TOPIC = auto()
    FORM_STUDY_GROUP = auto()
    GROUP_CRAFTING = auto()
    GROUP_EXERCISE = auto()
    GROUP_GARDENING = auto()
    INITIATE_GROUP_HUG = auto()
    ORGANIZE_COMMUNITY_EVENT = auto()
    PLAN_GROUP_OUTING = auto()
    SHARE_GROUP_EXPERIENCE = auto()
    START_GROUP_CHANT = auto()
    TEAM_BUILDING_EXERCISE = auto()
    
    # ================= CATEGORIA 4: INTERAZIONI CONFLITTUALI E COMPETITIVE (50) =================
    ARGUE = auto()
    BETRAY_TRUST = auto()
    CHALLENGE_TO_COMPETITION = auto()
    COMPLAIN_ABOUT_BEHAVIOR = auto()
    CRITICIZE = auto()
    DEMAND_APOLOGY = auto()
    END_FRIENDSHIP = auto()
    EXPRESS_DISAPPOINTMENT = auto()
    GIVE_ULTIMATUM = auto()
    GOSSIP_ABOUT_ANOTHER_NPC = auto()
    GUILT_TRIP = auto()
    HUMILIATE = auto()
    IGNORE = auto()
    INSULT = auto()
    INTERRUPT_RUDELY = auto()
    ISSUE_WARNING = auto()
    JEALOUS_OUTBURST = auto()
    MAKE_THREAT = auto()
    MOCK = auto()
    REFUSE_REQUEST = auto()
    REJECT_ADVICE = auto()
    SPREAD_RUMOR = auto()
    STEAL_CREDIT = auto()
    TAUNT = auto()
    YELL_AT = auto()
    # Nuove interazioni
    ACCUSE_OF_CHEATING = auto()
    ARGUE_ABOUT_MONEY = auto()
    BELITTLE_ACHIEVEMENT = auto()
    BREAK_PROMISE = auto()
    CHALLENGE_AUTHORITY = auto()
    COMPARE_UNFAVORABLY = auto()
    DEMAND_EXPLANATION = auto()
    DISMISS_OPINION = auto()
    DISRESPECT_BOUNDARIES = auto()
    EXCLUDE_FROM_GROUP = auto()
    EXPRESS_CONTEMPT = auto()
    GASLIGHT = auto()
    GIVE_SILENT_TREATMENT = auto()
    HOLD_GRUDGE = auto()
    INITIATE_POWER_STRUGGLE = auto()
    INSULT_FAMILY = auto()
    INVADE_PERSONAL_SPACE = auto()
    MAKE_SARCASTIC_REMARK = auto()
    MANIPULATE_EMOTIONS = auto()
    PASSIVE_AGGRESSIVE_COMMENT = auto()
    QUESTION_CHARACTER = auto()
    REJECT_COMPROMISE = auto()
    RIDICULE_BELIEFS = auto()
    SABOTAGE_EFFORTS = auto()
    SET_UP_FOR_FAILURE = auto()
    SHOW_DISDAIN = auto()
    TAKE_CREDIT = auto()
    THREATEN_RELATIONSHIP = auto()
    UNDERCUT_AUTHORITY = auto()
    USE_EMOTIONAL_BLACKMAIL = auto()
    WITHDRAW_AFFECTION = auto()
    
    def display_name_it(self) -> str:
        """Restituisce un nome leggibile in italiano per il tipo di interazione."""
        mapping = {
            # ================= INTERAZIONI QUOTIDIANE E AMICHEVOLI =================
            SocialInteractionType.ASK_ABOUT_DAY: "Chiedere della Giornata",
            SocialInteractionType.ASK_FOR_FAVOR: "Chiedere un Favore",
            SocialInteractionType.ASK_FOR_HELP: "Chiedere Aiuto",
            SocialInteractionType.BORROW_ITEM: "Chiedere in Prestito",
            SocialInteractionType.CHAT_CASUAL: "Chiacchierata Informale",
            SocialInteractionType.COMPLIMENT_ACHIEVEMENT: "Complimentarsi per un Successo",
            SocialInteractionType.COMPLIMENT_SKILL: "Complimentarsi per un'Abilità",
            SocialInteractionType.DISCUSS_BOOK: "Discutere un Libro",
            SocialInteractionType.DISCUSS_CURRENT_EVENTS: "Discutere Attualità",
            SocialInteractionType.DISCUSS_HOBBIES: "Discutere Hobby",
            SocialInteractionType.EXCHANGE_GIFTS: "Scambiarsi Regali",
            SocialInteractionType.EXPRESS_GRATITUDE: "Esprimere Gratitudine",
            SocialInteractionType.GIVE_ADVICE: "Dare un Consiglio",
            SocialInteractionType.GIVE_DIRECTIONS: "Dare Indicazioni",
            SocialInteractionType.INVITE_TO_GATHERING: "Invitare a un Raduno",
            SocialInteractionType.LEND_ITEM: "Prestare un Oggetto",
            SocialInteractionType.OFFER_COMFORT: "Offrire Conforto",
            SocialInteractionType.OFFER_FOOD: "Offrire Cibo",
            SocialInteractionType.OFFER_HELP: "Offrire Aiuto",
            SocialInteractionType.PLAN_ACTIVITY: "Pianificare Attività",
            SocialInteractionType.PLAY_GAME: "Giocare Insieme",
            SocialInteractionType.RECOMMEND_BOOK: "Consigliare un Libro",
            SocialInteractionType.RECOMMEND_MOVIE: "Consigliare un Film",
            SocialInteractionType.REMINISCE: "Rimembrare il Passato",
            SocialInteractionType.REQUEST_OPINION: "Chiedere un'Opinione",
            SocialInteractionType.SHARE_FOOD: "Condividere Cibo",
            SocialInteractionType.SHARE_INTEREST: "Condividere un Interesse",
            SocialInteractionType.SHARE_NEWS: "Condividere Notizie",
            SocialInteractionType.SHARE_SECRET: "Condividere un Segreto",
            SocialInteractionType.SHOW_PHOTOS: "Mostrare Foto",
            SocialInteractionType.SMALL_TALK: "Conversazione Leggera",
            SocialInteractionType.SMILE: "Sorridere",
            SocialInteractionType.TELL_JOKE: "Raccontare una Barzelletta",
            SocialInteractionType.TELL_STORY: "Raccontare una Storia",
            SocialInteractionType.WAVE_HELLO: "Salutare con la Mano",
            SocialInteractionType.WISH_GOOD_LUCK: "Augurare Buona Fortuna",
            SocialInteractionType.WISH_WELL: "Augurare Buona Salute",
            SocialInteractionType.COMPARE_EXPERIENCES: "Confrontare Esperienze",
            SocialInteractionType.DISCUSS_DREAMS: "Discutere Sogni",
            SocialInteractionType.EXCHANGE_RECIPES: "Scambiarsi Ricette",
            SocialInteractionType.INTRODUCE_TO_GROUP: "Presentare al Gruppo",
            SocialInteractionType.INVITE_FOR_COFFEE: "Invitare per un Caffè",
            SocialInteractionType.OFFER_RIDE: "Offrire un Passaggio",
            SocialInteractionType.PLAN_TRIP: "Pianificare un Viaggio",
            SocialInteractionType.PRAISE_WORK: "Lodare il Lavoro",
            SocialInteractionType.RECOMMEND_MUSIC: "Consigliare Musica",
            SocialInteractionType.SHARE_MEMORY: "Condividere un Ricordo",
            SocialInteractionType.SHARE_PERSONAL_GOAL: "Condividere un Obiettivo",
            SocialInteractionType.SUGGEST_HOBBY: "Suggerire un Hobby",
            SocialInteractionType.TALK_ABOUT_PETS: "Parlare di Animali",
            SocialInteractionType.TALK_ABOUT_TRAVEL: "Parlare di Viaggi",
            
            # ================= INTERAZIONI ROMANTICHE E SENSUALI =================
            SocialInteractionType.BLIND_DATE_SETUP: "Organizzare Appuntamento al Buio",
            SocialInteractionType.COMPLIMENT_APPEARANCE: "Complimentarsi sull'Aspetto",
            SocialInteractionType.CONFESS_ATTRACTION: "Confessare Attrazione",
            SocialInteractionType.CONFESS_LOVE: "Confessare Amore",
            SocialInteractionType.DANCE_TOGETHER: "Ballare Insieme",
            SocialInteractionType.EXCHANGE_LOVE_LETTERS: "Scambiarsi Lettere d'Amore",
            SocialInteractionType.FLIRT: "Flirtare",
            SocialInteractionType.GIVE_ROMANTIC_GIFT: "Fare un Regalo Romantico",
            SocialInteractionType.HOLD_HANDS: "Tenersi per Mano",
            SocialInteractionType.KISS: "Baciare",
            SocialInteractionType.MAKE_EYE_CONTACT: "Stabilire Contatto Visivo",
            SocialInteractionType.PLAN_ROMANTIC_GETAWAY: "Pianificare Fuga Romantica",
            SocialInteractionType.PROPOSE_COMMITMENT: "Proporre Impegno",
            SocialInteractionType.PROPOSE_DATE: "Chiedere un Appuntamento",
            SocialInteractionType.PROPOSE_INTIMACY: "Proporre Intimità",
            SocialInteractionType.PROPOSE_MARRIAGE: "Proporre Matrimonio",
            SocialInteractionType.ROMANTIC_DINNER: "Cena Romantica",
            SocialInteractionType.SEND_FLOWERS: "Inviare Fiori",
            SocialInteractionType.SHARE_FANTASY: "Condividere una Fantasia",
            SocialInteractionType.SHARE_FUTURE_PLANS: "Condividere Progetti Futuri",
            SocialInteractionType.STARE_ROMANTICALLY: "Ammirare con Sguardo",
            SocialInteractionType.SURPRISE_VISIT: "Visita a Sorpresa",
            SocialInteractionType.WHISPER_SWEET_NOTHINGS: "Sussurrare Dolcezze",
            SocialInteractionType.ARRANGE_CANDLELIGHT_DINNER: "Organizzare Cena a Lume di Candela",
            SocialInteractionType.ASK_FOR_DANCE: "Chiedere di Ballare",
            SocialInteractionType.COMPLIMENT_SCENT: "Complimentarsi per il Profumo",
            SocialInteractionType.CONFESS_DESIRE: "Confessare Desiderio",
            SocialInteractionType.DISCUSS_RELATIONSHIP_FUTURE: "Discutere Futuro della Relazione",
            SocialInteractionType.EXCHANGE_PROMISES: "Scambiarsi Promesse",
            SocialInteractionType.FLIRTATIOUS_TEASING: "Stuzzicare Flirtando",
            SocialInteractionType.GENTLE_TOUCH: "Tocco Gentile",
            SocialInteractionType.INITIATE_PHYSICAL_CONTACT: "Iniziare Contatto Fisico",
            SocialInteractionType.INVITE_TO_PRIVATE_SPACE: "Invitare in Spazio Privato",
            SocialInteractionType.MASSAGE_PARTNER: "Massaggiare il Partner",
            SocialInteractionType.PLAYFUL_BANTER: "Scherzare Giocosamente",
            SocialInteractionType.PROPOSE_STAYCATION: "Proporre Staycation",
            SocialInteractionType.RECITE_POETRY: "Recitare Poesia",
            SocialInteractionType.SEND_LOVE_TEXT: "Inviare Messaggio d'Amore",
            SocialInteractionType.SHARE_INTIMATE_SECRET: "Condividere Segreto Intimo",
            SocialInteractionType.SUGGEST_COUPLE_ACTIVITY: "Suggerire Attività di Coppia",
            SocialInteractionType.WALK_ARM_IN_ARM: "Camminare a Braccetto",
            SocialInteractionType.WATCH_SUNSET_TOGETHER: "Guardare il Tramonto Insieme",
            SocialInteractionType.WRITE_LOVE_SONG: "Scrivere Canzone d'Amore",
            SocialInteractionType.DISCUSS_BOUNDARIES: "Discutere Confini",
            SocialInteractionType.EXPLORE_FANTASIES: "Esplorare Fantasie",
            SocialInteractionType.EXPRESS_SENSUAL_DESIRES: "Esprimere Desideri Sensuali",
            SocialInteractionType.INITIATE_AFFECTION: "Iniziare Affetto",
            SocialInteractionType.PLAYFUL_WHISPERING: "Sussurri Giocosi",
            SocialInteractionType.PROPOSE_ADVENTURE: "Proporre Avventura",
            SocialInteractionType.SENSUAL_COMPLIMENT: "Complimento Sensuale",
            SocialInteractionType.SHARE_EROTIC_DREAM: "Condividere Sogno Erotico",
            SocialInteractionType.SUGGEST_INTIMATE_GAME: "Suggerire Gioco Intimo",
            SocialInteractionType.TALK_ABOUT_KINKS: "Parlare di Preferenze",
            
            # ================= INTERAZIONI FAMILIARI E DI GRUPPO =================
            SocialInteractionType.APOLOGIZE_TO_FAMILY: "Chiedere Scusa alla Famiglia",
            SocialInteractionType.ASK_FOR_FAMILY_ADVICE: "Chiedere Consiglio Familiare",
            SocialInteractionType.ASK_FOR_HELP_HOMEWORK: "Chiedere Aiuto per i Compiti",
            SocialInteractionType.BABYSIT: "Fare da Babysitter",
            SocialInteractionType.CELEBRATE_ANNIVERSARY: "Celebrare Anniversario",
            SocialInteractionType.DISCUSS_FAMILY_HISTORY: "Discutere Storia Familiare",
            SocialInteractionType.FAMILY_DINNER: "Cena Famigliare",
            SocialInteractionType.FAMILY_GAME_NIGHT: "Serata Giochi in Famiglia",
            SocialInteractionType.GIVE_FAMILY_GIFT: "Fare Regalo Famigliare",
            SocialInteractionType.GRIEVE_TOGETHER: "Elaborare Lutto Insieme",
            SocialInteractionType.HELP_WITH_CHORES: "Aiutare nelle Faccende",
            SocialInteractionType.MEDIATE_FAMILY_DISPUTE: "Mediare Disputa Famigliare",
            SocialInteractionType.PARENTAL_ADVICE: "Consiglio Genitoriale",
            SocialInteractionType.PARENTAL_PRAISE: "Lode Genitoriale",
            SocialInteractionType.PLAY_WITH_CHILD: "Giocare con Bambino",
            SocialInteractionType.READ_TO_CHILD: "Leggere a un Bambino",
            SocialInteractionType.SEEK_BLESSING: "Chiedere Benedizione",
            SocialInteractionType.SEEK_PARENTAL_APPROVAL: "Chiedere Approvazione Genitoriale",
            SocialInteractionType.SIBLING_BONDING: "Legame Fraterno",
            SocialInteractionType.SIBLING_RIVALRY: "Rivalità Fraterna",
            SocialInteractionType.SIBLING_TEASING: "Prendere in Giro un Fratello",
            SocialInteractionType.TEACH_CHILD_SKILL: "Insegnare Abilità a Bambino",
            SocialInteractionType.ADOPT_PET_TOGETHER: "Adottare Animale Insieme",
            SocialInteractionType.CELEBRATE_GRADUATION: "Celebrare Laurea",
            SocialInteractionType.DISCUSS_PARENTING: "Discutere Genitorialità",
            SocialInteractionType.FAMILY_PHOTO_SESSION: "Sessione Foto Famigliare",
            SocialInteractionType.FAMILY_VACATION_PLAN: "Pianificare Vacanza Famigliare",
            SocialInteractionType.GIVE_ELDERLY_CARE: "Assistere Anziano",
            SocialInteractionType.HELP_WITH_HOMEWORK: "Aiutare con i Compiti",
            SocialInteractionType.HOST_FAMILY_GATHERING: "Ospitare Raduno Famigliare",
            SocialInteractionType.INCLUDE_IN_FAMILY_TRADITION: "Includere in Tradizione Famigliare",
            SocialInteractionType.INTRODUCE_PARTNER_TO_FAMILY: "Presentare Partner alla Famiglia",
            SocialInteractionType.ORGANIZE_REUNION: "Organizzare Riunione",
            SocialInteractionType.PASS_DOWN_HEIRLOOM: "Tramandare Cimelio",
            SocialInteractionType.PLAN_GENERATIONAL_MEAL: "Pianificare Pasto Intergenerazionale",
            SocialInteractionType.PREPARE_FAMILY_RECIPE: "Preparare Ricetta Famigliare",
            SocialInteractionType.SHARE_ANCESTRY_STORIES: "Condividere Storie Antenati",
            SocialInteractionType.SUPPORT_FAMILY_MEMBER: "Sostenere Membro Famiglia",
            SocialInteractionType.TEACH_FAMILY_TRADITION: "Insegnare Tradizione Famigliare",
            SocialInteractionType.COLLABORATE_ON_PROJECT: "Collaborare a Progetto",
            SocialInteractionType.DEBATE_GROUP_TOPIC: "Dibattere Tema di Gruppo",
            SocialInteractionType.FORM_STUDY_GROUP: "Formare Gruppo di Studio",
            SocialInteractionType.GROUP_CRAFTING: "Creare in Gruppo",
            SocialInteractionType.GROUP_EXERCISE: "Esercitarsi in Gruppo",
            SocialInteractionType.GROUP_GARDENING: "Fare Giardinaggio in Gruppo",
            SocialInteractionType.INITIATE_GROUP_HUG: "Iniziare Abbraccio di Gruppo",
            SocialInteractionType.ORGANIZE_COMMUNITY_EVENT: "Organizzare Evento Comunitario",
            SocialInteractionType.PLAN_GROUP_OUTING: "Pianificare Uscita di Gruppo",
            SocialInteractionType.SHARE_GROUP_EXPERIENCE: "Condividere Esperienza di Gruppo",
            SocialInteractionType.START_GROUP_CHANT: "Iniziare Coro di Gruppo",
            SocialInteractionType.TEAM_BUILDING_EXERCISE: "Esercizio di Team Building",
            
            # ================= INTERAZIONI CONFLITTUALI E COMPETITIVE =================
            SocialInteractionType.ARGUE: "Litigare",
            SocialInteractionType.BETRAY_TRUST: "Tradire Fiducia",
            SocialInteractionType.CHALLENGE_TO_COMPETITION: "Sfidare a Competizione",
            SocialInteractionType.COMPLAIN_ABOUT_BEHAVIOR: "Lamentarsi del Comportamento",
            SocialInteractionType.CRITICIZE: "Criticare",
            SocialInteractionType.DEMAND_APOLOGY: "Esigere Scuse",
            SocialInteractionType.END_FRIENDSHIP: "Terminare Amicizia",
            SocialInteractionType.EXPRESS_DISAPPOINTMENT: "Esprimere Delusione",
            SocialInteractionType.GIVE_ULTIMATUM: "Dare Ultimatum",
            SocialInteractionType.GOSSIP_ABOUT_ANOTHER_NPC: "Spettegolare su Altri",
            SocialInteractionType.GUILT_TRIP: "Fare Sentire in Colpa",
            SocialInteractionType.HUMILIATE: "Umiliare",
            SocialInteractionType.IGNORE: "Ignorare",
            SocialInteractionType.INSULT: "Insultare",
            SocialInteractionType.INTERRUPT_RUDELY: "Interrompere Maleducatamente",
            SocialInteractionType.ISSUE_WARNING: "Rilasciare Avvertimento",
            SocialInteractionType.JEALOUS_OUTBURST: "Sfogo di Gelosia",
            SocialInteractionType.MAKE_THREAT: "Fare Minaccia",
            SocialInteractionType.MOCK: "Deridere",
            SocialInteractionType.REFUSE_REQUEST: "Rifiutare Richiesta",
            SocialInteractionType.REJECT_ADVICE: "Rifiutare Consiglio",
            SocialInteractionType.SPREAD_RUMOR: "Diffondere Diceria",
            SocialInteractionType.STEAL_CREDIT: "Rubare Merito",
            SocialInteractionType.TAUNT: "Sfottere",
            SocialInteractionType.YELL_AT: "Urlare Contro",
            SocialInteractionType.ACCUSE_OF_CHEATING: "Accusare di Imbroglio",
            SocialInteractionType.ARGUE_ABOUT_MONEY: "Litigare per Soldi",
            SocialInteractionType.BELITTLE_ACHIEVEMENT: "Sminuire Successo",
            SocialInteractionType.BREAK_PROMISE: "Rompere Promessa",
            SocialInteractionType.CHALLENGE_AUTHORITY: "Sfidare Autorità",
            SocialInteractionType.COMPARE_UNFAVORABLY: "Confrontare Sfavorevolmente",
            SocialInteractionType.DEMAND_EXPLANATION: "Esigere Spiegazioni",
            SocialInteractionType.DISMISS_OPINION: "Respingere Opinione",
            SocialInteractionType.DISRESPECT_BOUNDARIES: "Disrispettare Confini",
            SocialInteractionType.EXCLUDE_FROM_GROUP: "Escludere dal Gruppo",
            SocialInteractionType.EXPRESS_CONTEMPT: "Esprimere Disprezzo",
            SocialInteractionType.GASLIGHT: "Fare Gaslighting",
            SocialInteractionType.GIVE_SILENT_TREATMENT: "Fare Trattamento del Silenzio",
            SocialInteractionType.HOLD_GRUDGE: "Serbare Rancore",
            SocialInteractionType.INITIATE_POWER_STRUGGLE: "Iniziare Lotta di Potere",
            SocialInteractionType.INSULT_FAMILY: "Insultare la Famiglia",
            SocialInteractionType.INVADE_PERSONAL_SPACE: "Invadere Spazio Personale",
            SocialInteractionType.MAKE_SARCASTIC_REMARK: "Fare Commento Sarcastico",
            SocialInteractionType.MANIPULATE_EMOTIONS: "Manipolare Emozioni",
            SocialInteractionType.PASSIVE_AGGRESSIVE_COMMENT: "Commento Passivo-Aggressivo",
            SocialInteractionType.QUESTION_CHARACTER: "Mettere in Dubbio il Carattere",
            SocialInteractionType.REJECT_COMPROMISE: "Rifiutare Compromesso",
            SocialInteractionType.RIDICULE_BELIEFS: "Deridere Credenze",
            SocialInteractionType.SABOTAGE_EFFORTS: "Sabotare Sforzi",
            SocialInteractionType.SET_UP_FOR_FAILURE: "Preparare al Fallimento",
            SocialInteractionType.SHOW_DISDAIN: "Mostrare Disprezzo",
            SocialInteractionType.TAKE_CREDIT: "Prendersi il Merito",
            SocialInteractionType.THREATEN_RELATIONSHIP: "Minacciare Relazione",
            SocialInteractionType.UNDERCUT_AUTHORITY: "Minare Autorità",
            SocialInteractionType.USE_EMOTIONAL_BLACKMAIL: "Usare Ricatto Emotivo",
            SocialInteractionType.WITHDRAW_AFFECTION: "Ritirare Affetto",
        }
        return mapping.get(self, self.name.replace("_", " ").title())