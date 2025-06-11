# simai/core/config/npc_config.py
"""
Configurazione NPC, tratti, bisogni e ciclo di vita
"""

from core.enums.trait_types import TraitType
from .time_config import DXY, DXM
from core.enums import NeedType

# --- Soglie e Valori generali dei Bisogni ---
NEED_MIN_VALUE: float = 0.0
NEED_MAX_VALUE: float = 100.0
NEED_DEFAULT_START_MIN: float = 50.0    # Valore minimo all'inizializzazione dell'NPC
NEED_DEFAULT_START_MAX: float = 80.0    # Valore massimo all'inizializzazione
NEED_LOW_THRESHOLD: float = 25.0        # Sotto questa soglia, l'NPC considera di agire
NEED_HIGH_THRESHOLD = 75.0              # non fare questa azione se il bisogno è già quasi pieno
NEED_CRITICAL_THRESHOLD: float = 10.0   # Sotto questa soglia, il bisogno è critico

# --- Soglie Comportamentali ---
SHY_NPC_CROWD_THRESHOLD: int = 3 # Un NPC timido si sente a disagio se ci sono più di 3 persone (incluso se stesso)

# --- Generazione NPC ---
MIN_TRAITS_PER_NPC = 3
MAX_TRAITS_PER_NPC = 5
MAX_NPC_ACTIVE_INTERESTS = 3

# --- Generazione Nomi Casuali ---
MALE_NAMES = ["Marco", "Alessandro", "Luca", "Davide", "Matteo", "Francesco", "Lorenzo", "Andrea"]
FEMALE_NAMES = ["Giulia", "Sofia", "Aurora", "Alice", "Ginevra", "Chiara", "Emma", "Sara"]
LAST_NAMES = ["Rossi", "Ferrari", "Russo", "Bianchi", "Romano", "Gallo", "Costa", "Fontana"]

LASTNAME_PREFIXES = [
        "'Giacal", "Abatantu", "Abbatantu", "Acc", "Acciai", "Acciar", "Acco", 
        "Accorn", "Ad", "Adin", "Ador", "Ag", "Air", "Al", "Albergh", 
        "Albert", "Aldi", "Alf", "Alvar", "Alvi", "Amad", "Amazzon", "Ambros", 
        "Amend", "Anconet", "And", "Andre", "Antracen", "Anton", "Antonazz", 
        "Antu", "Ar", "Ard", "Ari", "Aric", "Arm", "Arrigh", "Art", "Ast", 
        "Aut", "Av", "B", "Ba", "Baboli", "Bacc", "Baccar", "Bacciag", 
        "Badal", "Bagn", "Balda", "Bald", "Ballari", "Banf", "Bar", "Barb", 
        "Barbag", "Barbar", "Barbo", "Barcar", "Barill", "Barnazz", "Baron", 
        "Barr", "Barz", "Bass", "Bassan", "Battist", "Battisto", "Baud", 
        "Bazz", "Begh", "Bel", "Bell", "Bella", "Bellin", "Bellol", "Ben", 
        "Benagl", "Benev", "Beni", "Ber", "Bergam", "Berl", "Berlusc", "Bern", 
        "Bernard", "Bert", "Bertev", "Bertol", "Béth", "Bi", "Bidd", "Bin", 
        "Bion", "Biss", "Bizz", "Bl", "Bocc", "Bod", "Boll", "Bolocc", "Bon", 
        "Boncompa", "Bonf", "Bor", "Bordigno", "Borl", "Borne", "Borr", 
        "Bort", "Bortol", "Borz", "Bott", "Bov", "Br", "Brad", "Bramb", 
        "Bressan", "Bri", "Brugn", "Brum", "Bug", "Bur", "Burr", "Bus", 
        "Busce", "C", "Cacciap", "Cafedd", "Calabr", "Calif", "Caligi", 
        "Calvanes", "Calzav", "Cam", "Camp", "Campagn", "Campit", "Cana", 
        "Cand", "Cangel", "Cann", "Cannal", "Cannavacci", "Cannavacciuol", 
        "Cannistr", "Cap", "Capann", "Car", "Carch", "Card", "Carl", 
        "Carlevar", "Carnev", "Cartasio", "Cas", "Casci", "Casir", "Cassiou", 
        "Cass", "Cast", "Cat", "Catal", "Cattapa", "Cav", "Cavacchi", 
        "Cavatto", "Cazz", "Cecc", "Cer", "Cerc", "Ceri", "Cerign", "Cerq", 
        "Cev", "Chabl", "Chiambr", "Chi", "Ci", "Ciarav", "Ciard", "Ciarr", 
        "Ciccol", "Circ", "Cirinn", "Co", "Coassi", "Cod", "Col", "Com", 
        "Cond", "Conde", "Contess", "Corb", "Corg", "Coron", "Corrid", 
        "Cortinov", "Corvi", "Coss", "Cost", "Covi", "Cr", "Cri", "Criser à", 
        "Crist", "Croci", "Cros", "Crosign", "Cul", "Cuné", "Curt", "Cusi", 
        "Cusm", "Custon", "Cut", "D", "D-'", "Dan", "De C", "De M", "Del Gr", 
        "Del", "Diémo", "Don", "Dor", "Dr", "Drom", "Du", "Ein", "F", "Fa", 
        "Fabi", "Fabr", "Falc", "Falcon", "Falconi", "Fall", "Fanti", "Farco", 
        "Fauss", "Fav", "Faz", "Fed", "Felic", "Feltr", "Fer", "Ferr", 
        "Ferrar", "Fi", "Fich", "Figi", "Figlio", "Fin", "Fiorin", "Fisc", 
        "Fl", "Fontan", "Form", "Formis", "Fr", "Frab", "Fracc", "Franc", 
        "Frattar", "Furla", "Fus", "G", "Gabb", "Gal", "Gale", "Gall", 
        "Gand", "Gar", "Gardell", "Gargi", "Garib", "Gasp", "Gast", "Gatt", 
        "Gaud", "Gazz", "Gen", "Ger", "Geron", "Gess", "Gi", "Giangregori", 
        "Giann", "Giard", "Giardini", "Giar", "Gif", "Gil", "Gilor", "Gioc", 
        "Giord", "Giorg", "Giovan", "Gir", "Girard", "Giss", "Giugli", "Go", 
        "Goll", "Gonzal", "Gorr", "Gr", "Grand", "Gregor", "Grett", "Grib", 
        "Grim", "Gris", "Grum", "Gu", "Guarn", "Guerr", "Guid", "Gum", 
        "Guzz", "I", "Iacov", "Iervol", "Interl", "Ior", "Jann", "L", 
        "Lagan", "Lamo", "Lampar", "Lamp", "Lampit", "Lanz", "Lav", 
        "Lazzar", "Lecc", "Lett", "Li", "Libr", "Libral", "Licc", "Licci", 
        "Livon", "Luc", "Luci", "Lucian", "Lucc", "Lur", "M", "Ma", 
        "Mabral", "Machiav", "Macr", "Mad", "Maddal", "Madril", "Madrin", 
        "Maff", "Mag", "Magg", "Mai", "Main", "Mal", "Malg", "Maln", 
        "Malp", "Malvolt", "Mammuc", "Man", "Manc", "Mand", "Mandr", 
        "Mangiav", "Mani", "Manz", "Mar", "Marang", "Marc", "Marco", 
        "March", "Marchigi", "Margherit", "Marguerett", "Mari", "Marigli", 
        "Martin", "Marr", "Martar", "Maruzz", "Marz", "Marzor", "Mas", 
        "Masc", "Masci", "Mass", "Massar", "Maso", "Matar", "Matal", 
        "Matt", "Matti", "Mazz", "Mazzol", "Mazzon", "Mel", "Melchi", 
        "Meneg", "Mi", "Mia", "Mic", "Mich", "Migliacci", "Migno", "Minch", 
        "Minerv", "Mir", "Modan", "Moden", "Mol", "Moli", "Molin", "Mom", 
        "Mon", "Monic", "Mont", "Montel", "Mor", "Mord", "Mostacciuol", 
        "Mull", "Munaf", "Muni", "Mur", "Mus", "Muzz", "N", "Nannar", 
        "Nard", "Nast", "Negl", "Nib", "Nic", "Nich", "Nicol", "Niedd", 
        "Nistic", "Nov", "Nunzi", "Nuzz", "Oli", "Oliv", "On", "Org", 
        "Orop", "Orr", "Ors", "Oz", "P", "Pac", "Pach", "Paci", "Padoa", 
        "Pag", "Pagn", "Pagli", "Pagliar", "Pal", "Palm", "Pan", "Pana", 
        "Panar", "Panariell", "Pand", "Pandi", "Pann", "Pani", "Papal", 
        "Par", "Parad", "Paradol", "Pari", "Parl", "Parol", "Passar", 
        "Pasqual", "Pasquett", "Pastor", "Pat", "Pav", "Pava", "Pazz", 
        "Pazzagli", "Pecor", "Pedr", "Pegli", "Pel", "Pell", "Penn", "Per", 
        "Peri", "Perre", "Perr", "Petacc", "Petracci", "Pezz", "Pi", "Pian", 
        "Pic", "Picc", "Piccir", "Pichl", "Pier", "Pieri", "Pilo", "Pin", 
        "Pineid", "Pint", "Pir", "Piscit", "Pol", "Polid", "Pom", "Porc", 
        "Porr", "Porz", "Pozz", "Pozzobo", "Pr", "Prattic", "Prestifilipp", 
        "Prestigiacom", "Pret", "Pri", "Proi", "Pronest", "Provenz", "Pugl", 
        "Pulz", "Puscion", "Puzz", "Quadr", "Quarantiell", "R", "Rache", 
        "Raddav", "Raff", "Rain", "Ramb", "Ramp", "Ran", "Rand", "Rav", 
        "Ravi", "Re", "Red", "Reg", "Regin", "Ren", "Resc", "Rib", "Ric", 
        "Ricc", "Ricciard", "Rid", "Rigam", "Rip", "Rizz", "Rom", "Romani", 
        "Ron", "Ronc", "Ronn", "Ros", "Ross", "Rossi", "Russ", "S", 
        "Saffir", "Sal", "Sang", "Sant", "Sar", "Sarto", "Sav", "Savar", 
        "Savi", "Savo", "Scaramuz", "Scaramuzz", "Scar", "Schiavo", "Schi", 
        "Schif", "Schirr", "Scilip", "Scim", "Scongliamigli", "Scud", "Se", 
        "Semer", "Serrai", "Serv", "Sever", "Sgarb", "Sgr", "Sid", "Simon", 
        "Simonc", "Sol", "Solin", "Sor", "Sov", "Spezz", "Spit", "Spital", 
        "St", "Stanzi", "Star", "Stor", "Stopp", "Strazz", "T", "Tab", 
        "Taglialat", "Tard", "Tart", "Tass", "Tauf", "Tav", "Tavol", "Ted", 
        "Terz", "Test", "Tib", "Tip", "Titomanl", "Toff", "Tomm", "Tr", 
        "Trab", "Trem", "Tremad", "Trevisa", "Trezz", "Trip", "Tro", "Tros", 
        "Trov", "Ub", "Urci", "V", "Vald", "Vallar", "Var", "Varri", 
        "Varricchi", "Varres", "Vass", "Vedov", "Ven", "Vend", "Vendra", 
        "Vendramin", "Venie", "Vent", "Ver", "Verc", "Verm", "Vern", 
        "Veron", "Verr", "Verrazz", "Verz", "Vetr", "Vezz", "Vi", "Vicer", 
        "Vida", "Vign", "Viol", "Vird", "Vis", "Visc", "Visch", "Visci", 
        "Viscia", "Visenti", "Visinti", "Viss", "Vit", "Volp", "Volpat", 
        "Vuillerm", "Wagn", "Z", "Zac", "Zacc", "Zaccar", "Zan", "Zangr", 
        "Zani", "Zano", "Zanon", "Zanonc", "Zanz", "Zanzar", "Zapp", "Zarl", 
        "Zen", "Zenn", "Zicc", "Zingal", "Zoin", "Zorz", "Zu'"
    ]
LASTNAME_SUFFIXES = [
        "a", "acchi", "acchio", "acci", "ace", "aci", "adi", "ago", "aghi", "aglia", 
        "aglio", "ai", "al", "ala", "ale", "ali", "aldi", "aldo", "ale", "alfi", 
        "ali", "alli", "allo", "aloro", "aloru", "ana", "andi", "ando", "ani", "ante", 
        "anti", "anzi", "ao", "ara", "ardi", "ari", "aro", "arri", "as", "aschi", 
        "asco", "asi", "asio", "aso", "assa", "assi", "asso", "astro", "ata", "ate", 
        "ati", "ato", "atti", "atto", "au", "audi", "audo", "auri", "auro", "auti", 
        "avi", "az", "azzi", "azzo", "à", "e", "ecchi", "ecchio", "ecci", "edda", 
        "edi", "ego", "eggi", "egli", "ei", "ela", "ele", "elfi", "eli", "ella", 
        "elle", "elli", "ello", "enghi", "engo", "eni", "enti", "enzi", "eo", "er", 
        "era", "erli", "erlo", "ero", "erri", "es", "eschi", "ese", "esi", "esio", 
        "essa", "essi", "esso", "etta", "etti", "evi", "ez", "ezzi", "è", "gni", 
        "i", "ia", "icchi", "icchio", "icci", "iccio", "idi", "ieri", "iero", "iello", 
        "iella", "iggi", "igli", "igo", "illa", "illi", "illo", "ina", "inghi", "ingo", 
        "ini", "ino", "inzi", "io", "is", "ise", "isi", "issa", "issi", "isso", 
        "ita", "iti", "ito", "itti", "iuoli", "izzi", "izio", "ì", "meni", "mi", 
        "n", "o", "occhi", "occhio", "occi", "oci", "odi", "oggi", "ogli", "oi", 
        "ola", "oldi", "oldo", "olfi", "olfo", "oli", "olla", "olli", "ollo", "olo", 
        "ona", "ondi", "ondo", "one", "oni", "ono", "onti", "onzi", "ora", "ordi", 
        "ori", "orri", "oschi", "osi", "ossa", "ossi", "osso", "ota", "oti", "otta", 
        "otti", "otto", "ou", "ovi", "oz", "ozzi", "ò", "r", "t", "u", "ucchi", 
        "ucci", "ucco", "udi", "ulfo", "uli", "ulla", "ulli", "ullo", "ulo", "uni", 
        "unti", "uolo", "uoli", "uoti", "uoto", "uozzi", "uozzo", "uri", "us", "uso", 
        "ussa", "ussi", "usso", "ut", "uta", "uti", "uto", "utta", "utti", "uzzi", 
        "uzzo", "y", "z"
    ]

IMPLEMENTED_TRAITS = [
    TraitType.ACTIVE, TraitType.BOOKWORM, TraitType.GLUTTON, TraitType.LONER,
    TraitType.AMBITIOUS, TraitType.LAZY, TraitType.SOCIAL, TraitType.CREATIVE,
    TraitType.ARTISTIC, TraitType.CHARMER, TraitType.SHY, TraitType.PLAYFUL,
    TraitType.CHILDISH, TraitType.UNINHIBITED, TraitType.GOOD,
    # Aggiungi qui altri tratti man mano che crei le loro classi
]



# --- PESI PER L'IA ---
# Pesi per i bisogni usati da AIDecisionMaker e NeedsProcessor
NEED_WEIGHTS: dict[NeedType, float] = {
    NeedType.HUNGER: 1.5,
    NeedType.THIRST: 1.6, 
    NeedType.ENERGY: 1.4,
    NeedType.BLADDER: 1.3,
    NeedType.HYGIENE: 1.0,
    NeedType.FUN: 0.8,
    NeedType.SOCIAL: 0.7,
    NeedType.INTIMACY: 0.6,
    # Aggiungere pesi per altri NeedType quando implementati
}

# Modificatore di urgenza per bisogni critici
CRITICAL_NEED_THRESHOLD_MODIFIER: float = 1.5

# --- Ciclo di Vita ---
LIFE_STAGE_AGE_THRESHOLDS_DAYS = {
    # Chiavi come stringhe dei membri dell'Enum LifeStage
    "NEWBORN": 0,                     # Dalla nascita
    "INFANT": round(DXM * 2),         # Da circa 2 mesi
    "TODDLER": DXY * 1,               # Da 1 anno
    "PRESCHOOLER": DXY * 3,           # Da 3 anni
    "CHILD": DXY * 6,                 # Da 6 anni
    "PRE_TEEN": DXY * 9,              # Da 9 anni
    "EARLY_ADOLESCENCE": DXY * 12,    # Da 12 anni
    "MID_ADOLESCENCE": DXY * 15,      # Da 15 anni
    "LATE_ADOLESCENCE": DXY * 18,     # Da 18 anni
    "YOUNG_ADULT": DXY * 20,          # Da 20 anni
    "ADULT": DXY * 30,                # Da 30 anni
    "MIDDLE_AGED": DXY * 40,          # Da 40 anni
    "MATURE_ADULT": DXY * 60,         # Da 60 anni
    "SENIOR": DXY * 75,               # Da 75 anni
    "ELDERLY": DXY * 90,              # Da 90 anni
}

AGE_SENIOR_STARTS_CONSIDER_DEATH_YEARS = 75.0
AGE_SENIOR_STARTS_CONSIDER_DEATH_DAYS = round(AGE_SENIOR_STARTS_CONSIDER_DEATH_YEARS * DXY)
DAILY_DEATH_CHANCE_MULTIPLIER_SENIOR = 0.0005

# --- Riproduzione e Sessualità ---
MIN_AGE_PUBERTY_FERTILITY_YEARS = 13
MIN_AGE_PUBERTY_FERTILITY_DAYS = MIN_AGE_PUBERTY_FERTILITY_YEARS * DXY

MIN_AGE_FOR_INTIMACY_YEARS = 14
MIN_AGE_FOR_INTIMACY_DAYS = MIN_AGE_FOR_INTIMACY_YEARS * DXY
MAX_AGE_FOR_INTIMACY_YEARS = 70
MAX_AGE_FOR_INTIMACY_DAYS = MAX_AGE_FOR_INTIMACY_YEARS * DXY

PREGNANCY_CHANCE_FEMALE = 0.20
PREGNANCY_DURATION_MONTHS_GAME = 9
PREGNANCY_DURATION_DAYS_GAME = PREGNANCY_DURATION_MONTHS_GAME * DXM

MIN_AGE_START_PREGNANCY_FEMALE_YEARS = 14
MIN_AGE_START_PREGNANCY_FEMALE_DAYS = MIN_AGE_START_PREGNANCY_FEMALE_YEARS * DXY
MAX_AGE_FERTILE_FEMALE_YEARS = 48
MAX_AGE_FERTILE_FEMALE_DAYS = MAX_AGE_FERTILE_FEMALE_YEARS * DXY

AGE_START_MENSTRUAL_CYCLE_YEARS_SET = {11.0, 13.0}
AGE_START_MENSTRUAL_CYCLE_DAYS_SET = {round(year * DXY) for year in AGE_START_MENSTRUAL_CYCLE_YEARS_SET}
AGE_MENOPAUSE_YEARS_SET = {50.0, 60.0}
AGE_MENOPAUSE_DAYS_SET = {round(year * DXY) for year in AGE_MENOPAUSE_YEARS_SET}

CHANCE_NPC_IS_HETEROSEXUAL = 0.85
CHANCE_NPC_IS_HOMOSEXUAL = 0.07
CHANCE_NPC_IS_BISEXUAL = 0.05
CHANCE_NPC_IS_PANSEXUAL = 0.03
CHANCE_NPC_IS_ASEXUAL_SPECTRUM = 0.02
CHANCE_NPC_IS_AROMANTIC_SPECTRUM = 0.02
CHANCE_ROMANTIC_MATCHES_SEXUAL = 0.95

NEED_DECAY_RATES: dict[NeedType, float] = {
    NeedType.ACHIEVEMENT: -0.2,
    NeedType.AUTONOMY: -0.3,
    NeedType.BLADDER: -8.0,
    NeedType.COMFORT: -1.0,
    NeedType.CREATIVITY: -0.3,
    NeedType.ENERGY: -5.0,
    NeedType.ENVIRONMENT: -0.5,
    NeedType.FUN: -3.0,
    NeedType.HUNGER: -4.2,
    NeedType.HYGIENE: -2.0,
    NeedType.INTIMACY: -1.5,
    NeedType.LEARNING: -0.2,
    NeedType.SAFETY: -0.5,
    NeedType.SOCIAL: -2.5,
    NeedType.SPIRITUALITY: -0.4,
    NeedType.THIRST: -5.5, # Assicurati di avere THIRST qui
}

# Modificatore di urgenza per bisogni critici
CRITICAL_NEED_THRESHOLD_MODIFIER: float = 1.5

# Soglia di urgenza sopra la quale l'IA considera un problema per la decisione
AI_URGENT_PROBLEM_THRESHOLD: float = 0.5 # Esempio: considera problemi con urgenza > 50%
