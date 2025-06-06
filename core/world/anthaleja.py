import re
import random
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
from datetime import datetime
from typing import Optional

# -- CLASSE 1: SISTEMA NUMERICO --
class AnthalejaNumericalSystem:
    """Gestisce la rappresentazione dei numeri."""
    def __init__(self):
        self.numbers = {
            0: 'ne', 1: 'ma', 2: 'be', 3: 'ĉe', 4: 'dy', 5: 'fe', 6: 'ĝe',
            7: 'pla', 8: 'tye', 9: 'mo', 10: 'dek', 11: 'hel', 12: 'zen'
        }
        self.powers_of_ten_positive = {
            10**2: 'dune', 10**3: 'kise', 10**6: 'meĝe', 10**9: 'ĝede',
            10**12: 'teje', 10**15: 'peta', 10**18: 'exa', 10**21: 'zeta',
            10**24: 'yota', 10**27: 'rona', 10**30: 'keta'
        }
        self.powers_of_ten_negative = {
            10**-2: 'dunet', 10**-3: 'kiset', 10**-6: 'meĝet', 10**-9: 'ĝedet',
            10**-12: 'tejet', 10**-15: 'petat', 10**-18: 'exat', 10**-21: 'zetat',
            10**-24: 'yotat', 10**-27: 'ronat', 10**-30: 'ketat'
        }
        self.power_levels_positive = sorted(self.powers_of_ten_positive.keys(), reverse=True)

    def get_number(self, n):
        if not isinstance(n, (int, float)): return "input_non_numerico"
        if n < 0: return "ne " + self.get_number(abs(n))
        n_int = int(n)
        if n_int == n: # È un intero o un float che è un intero
            if n_int in self.numbers: return self.numbers[n_int]
            if 13 <= n_int <= 19: return self.numbers[10] + self.numbers[n_int - 10]
            if 20 <= n_int <= 99:
                tens = n_int // 10
                units = n_int % 10
                return self.get_number(tens) + self.numbers[10] + (self.numbers[units] if units > 0 else "")
            for power in self.power_levels_positive:
                if n_int >= power:
                    count = n_int // power
                    remainder = n_int % power
                    prefix = self.get_number(count) if count > 1 else ""
                    suffix = self.get_number(remainder) if remainder > 0 else ""
                    return prefix + self.powers_of_ten_positive[power] + suffix
        # Gestione base per float non interi (può essere espansa)
        return str(n) if isinstance(n, float) else "numero_non_supportato"


    def format_large_number(self, n, unit=""):
        sign = "ne " if n < 0 else ""
        n_abs = abs(n)
        for power in self.power_levels_positive:
            if n_abs >= power:
                value = n_abs / power
                value_str = f"{value:.1f}".rstrip('0').rstrip('.')
                return f"{sign}{value_str} {self.powers_of_ten_positive[power]}{unit}"
        return f"{sign}{n_abs} {unit}".strip()

# -- CLASSE 2: SISTEMA DEI COLORI --
class AnthalejaColorSystem:
    """Definisce il sistema dei colori e i loro modificatori."""
    def __init__(self):
        self.colors = {
            'green': 'klem', 'red': 'lip', 'blue': 'nyik', 'yellow': 'eira',
            'black': 'ploke', 'white': 'viris', 'pink': 'kef', 'gray': 'klye',
            'sky-gray': 'kepoz', 'orange': 'lipeira', 'purple': 'lipnyk',
            'brown': 'liploke', 'gold': 'koro', 'silver': 'ziro',
            'cyan': 'nyikin', 'beige': 'pie', 'crimson': 'lipdok',
            'bronze': 'kortil', 'flesh_color': 'bemiĝ'
        }
        self.color_derivations = {
            'light': ('-let', 'suffix'), 
            'dark': ('-dok', 'suffix'),
            'bright': ('mabloan-', 'prefix'),
            'pale': ('-pe', 'suffix')
        }
    
    def get_color(self, color_name, modifier=None):
        base = self.colors.get(color_name.lower())
        if not base: return "colore_non_trovato"
        if modifier:
            mod_tuple = self.color_derivations.get(modifier.lower())
            if mod_tuple:
                mod_str, mod_type = mod_tuple
                return (mod_str + base) if mod_type == 'prefix' else (base + mod_str)
        return base

# -- CLASSE 3: SISTEMA VERBALE --
class VerbSystem:
    """Modella il sistema di coniugazione dei verbi (tempo, aspetto, modo)."""
    def __init__(self):
        self.tenses = {
            'present': '', 'past': 'pe', 'future': 'fe',
            'conditional': 'so', 'imperative': 'ko'
        }
        self.aspects = {
            'simple': '', 'progressive': 'xan', 'perfect': 'tol'
        }
        self.moods = {
            'indicative': '', 'subjunctive': 'ne', 'imperative': 'ko'
        }
    
    def conjugate(self, root, tense='present', mood='indicative', aspect='simple'): # Ordine cambiato per coerenza
        # NB: La tua logica originale aveva mood -> tense -> root -> aspect.
        # La mia ultima generazione del generate_sentence aveva accidentalmente invertito mood e aspect
        # Ripristino la tua logica: TENSE + ROOT, poi ASPECT, poi MOOD
        
        # 1. Applica il tempo alla radice
        conjugated_verb = self.tenses.get(tense, '') + root
        
        # 2. Aggiungi l'aspetto
        if aspect != 'simple':
            conjugated_verb += self.aspects.get(aspect, '')
        
        # 3. Prefiggi il modo (se non indicativo)
        if mood != 'indicative':
            conjugated_verb = self.moods.get(mood, '') + conjugated_verb
            
        return conjugated_verb

# -- CLASSE 4: GESTIONE DATA E ORA --
class AnthalejaDatetime:
    """Gestisce la conversione e la manipolazione delle date nel calendario Anthalys."""
    HXD, DXM, MXY, DXW = 28, 24, 18, 7
    DXY = MXY * DXM
    SXD = HXD * 60 * 60 
    MONTH_NAMES = ['Arejal', 'Brukom', 'Ĉelal', 'Kebor', 'Duvol', 'Elumag', 'Fydrin', 
                    'Ĝinuril', 'Itrekos', 'Jebrax', 'Letranat', 'Mulfus', 'Nylumer', 
                    'Otlevat', 'Prax', 'Retlixen', 'Sajep', 'Xetul'
                ]
    DAY_NAMES = ['Nijahr', 'Majahr', 'Bejahr', 'Ĉejahr', 'Dyjahr', 'Fejahr', 'Ĝejahr']
    MONTH_ABBR = {name: (name[:2] + 'x' if name == "Prax" else name[:3]) for name in MONTH_NAMES}
    EPOCH = 951584400 - (5775 * DXY * SXD)

    def __init__(self, earth_date=None):
        if earth_date is None: earth_date = datetime.utcnow()
        earth_timestamp = earth_date.timestamp()
        
        seconds_since_epoch = earth_timestamp - self.EPOCH
        absolute_days = int(seconds_since_epoch // self.SXD)
        seconds_in_day = seconds_since_epoch % self.SXD
        day_of_year = absolute_days % self.DXY
        
        self.year = absolute_days // self.DXY
        self.month_index = day_of_year // self.DXM
        self.month_name = self.MONTH_NAMES[self.month_index]
        self.day = (day_of_year % self.DXM) + 1
        self.day_of_week_index = absolute_days % self.DXW
        self.day_of_week_name = self.DAY_NAMES[self.day_of_week_index]
        
        self.hour = int(seconds_in_day // (60 * 60))
        self.minute = int((seconds_in_day % (60 * 60)) // 60)
        self.second = int(seconds_in_day % 60)

    def format(self, format_str="Y, d/m G:i:s"):
        replacements = {
            'Y': str(self.year), 'm': self.MONTH_ABBR[self.month_name],
            'd': str(self.day), 'G': str(self.hour),
            'i': str(self.minute).zfill(2), 's': str(self.second).zfill(2),
            'MONTH': self.month_name, 'DAY': self.day_of_week_name
        }
        processed_format_str = format_str
        for code, value in replacements.items():
            processed_format_str = processed_format_str.replace(code, value)
        return processed_format_str
        
    def __str__(self):
        return self.format()

# -- CLASSE 5: MOTORE DELLA LINGUA ANTHALEJA --
class AnthalejaLang:
    """Definisce il nucleo della lingua: lessico, grammatica e morfologia."""
    def __init__(self):
        self.numbers = AnthalejaNumericalSystem()
        self.colors = AnthalejaColorSystem()
        self.verb_system = VerbSystem()
        
        self.pronouns_subject = {
            '1.SG': 'ja', '2.SG': 'rya', '3.SG.M': 'ĉa', '3.SG.F': 'ĝa', '3.SG.NT': 'ka',
            '1.PL': 'jya', '2.PL': 'rya', '3.PL': 'kya'
        }
        self.pronouns_possessive_pron = { # 'mio', 'tuo' (indipendenti E usati come aggettivi)
            '1.SG': 'mija', '2.SG': 'mirya', '3.SG.M': 'miĉa', '3.SG.F': 'miĝa', '3.SG.NT': 'mika',
            '1.PL': 'mijya', '2.PL': 'mirya', '3.PL': 'mikya'
        }
        
        self.articles = {'DEF': 'ol'}
        
        self.lexicon = {
            # Nomi
            'frekol':           {'pos': 'noun', 'meaning_it': 'pioggia', 'meaning_en': 'rain', 'pron': '/frekol/'},
            'freja':            {'pos': 'noun', 'meaning_it': 'acqua', 'meaning_en': 'water', 'pron': '/freʒa/'},
            'nijel':            {'pos': 'noun', 'meaning_it': 'sole', 'meaning_en': 'sun', 'pron': '/niʒel/'},
            'ding':             {'pos': 'noun', 'meaning_it': 'montagna', 'meaning_en': 'mountain', 'pron': '/ding/'},
            'frisik':           {'pos': 'noun', 'meaning_it': 'fuoco, fiamma', 'meaning_en': 'fire, flame', 'pron': '/frisik/'},
            'derzim':           {'pos': 'noun', 'meaning_it': 'bevanda', 'meaning_en': 'drink, beverage', 'pron': '/derzim/'},
            'kixo':             {'pos': 'noun', 'meaning_it': 'cibo', 'meaning_en': 'food, meal', 'pron': '/kiʃo/'},
            'bemno':            {'pos': 'noun', 'meaning_it': 'male, il male', 'meaning_en': 'evil, bad thing', 'pron': '/bemno/'},
            'jahr':             {'pos': 'noun', 'meaning_it': 'giorno', 'meaning_en': 'day', 'pron': '/jahr/'}, 
            'sahr':             {'pos': 'noun', 'meaning_it': 'sera', 'meaning_en': 'evening', 'pron': '/sahr/'}, # da tua lista originale, hai poi confermato 'san'
            'nahr':             {'pos': 'noun', 'meaning_it': 'notte', 'meaning_en': 'night', 'pron': '/nahr/'},
            'whato':            {'pos': 'noun', 'meaning_it': 'albero; legno', 'meaning_en': 'tree; wood', 'pron': '/uːato/'},
            'whedo':            {'pos': 'noun', 'meaning_it': 'mappa', 'meaning_en': 'map', 'pron': '/uːedo/'},
            'pame':             {'pos': 'noun', 'meaning_it': 'roccia; pietra', 'meaning_en': 'rock; stone', 'pron': '/pame/'},
            'kole':             {'pos': 'noun', 'meaning_it': 'cielo', 'meaning_en': 'sky', 'pron': '/kole/'},
            'koro':             {'pos': 'noun/adjective', 'meaning_it': 'oro; dorato', 'meaning_en': 'gold; golden', 'pron': '/koro/'},
            'ziro':             {'pos': 'noun/adjective', 'meaning_it': 'argento; argentato', 'meaning_en': 'silver; silvery', 'pron': '/ziro/'},
            'kortil':           {'pos': 'noun/adjective', 'meaning_it': 'bronzo; bronzeo', 'meaning_en': 'bronze; bronze-colored', 'pron': '/kortil/'},
            'lyoki':            {'pos': 'noun', 'meaning_it': 'parola', 'meaning_en': 'word', 'pron': '/liːoki/'},
            'ĝogi':             {'pos': 'noun', 'meaning_it': 'colore (concetto)', 'meaning_en': 'color (concept)', 'pron': '/ʤogi/'},
            'ĝeratid':          {'pos': 'noun', 'meaning_it': 'colore (tonalità)', 'meaning_en': 'hue, shade', 'pron': '/ʤeratid/'},
            'pylo':             {'pos': 'noun', 'meaning_it': 'occhio', 'meaning_en': 'eye', 'pron': '/piːlo/'},
            'ys':               {'pos': 'noun', 'meaning_it': 'città', 'meaning_en': 'city, town', 'pron': '/iːs/'},
            'Anthal':           {'pos': 'noun_proper', 'meaning_it': 'Anthal (nazione)', 'meaning_en': 'Anthal (nation)', 'pron': '/antal/'},
            'Anthaleja':        {'pos': 'noun', 'meaning_it': 'lingua Anthaleja; cittadino/a di Anthal', 'meaning_en': 'Anthaleja language; citizen of Anthal', 'pron': '/antaleʒa/'},
            'kuba':             {'pos': 'noun', 'meaning_it': 'cubo', 'meaning_en': 'cube', 'pron': '/kuba/'},
            'kwara':            {'pos': 'noun', 'meaning_it': 'quadrato', 'meaning_en': 'square', 'pron': '/kuara/'},
            'nesdol':           {'pos': 'noun', 'meaning_it': 'anno', 'meaning_en': 'year', 'pron': '/nesdol/'},
            'donesdol':         {'pos': 'noun', 'meaning_it': 'dozzennio (12 anni)', 'meaning_en': 'dozennio (12 years)', 'pron': '/donesdol/'},
            'venesdol':         {'pos': 'noun', 'meaning_it': 'mezzo secolo Anthalejano (72 anni)', 'meaning_en': 'Anthalejan half-century (72 years)', 'pron': '/venesdol/'},
            'zenkwaranesdol':   {'pos': 'noun', 'meaning_it': 'secolo Anthalejano (144 anni)', 'meaning_en': 'Anthalejan century (144 years)', 'pron': '/zenkuaranesdol/'},
            'zenkubanesdol':    {'pos': 'noun', 'meaning_it': 'millennio Anthalejano (1728 anni)', 'meaning_en': 'Anthalejan millennium (1728 years)', 'pron': '/zenkubanesdol/'},

            # Verbi
            'frekola':          {'pos': 'verb', 'meaning_it': 'piovere', 'meaning_en': 'to rain', 'pron': '/frekola/'},
            'jita':             {'pos': 'verb', 'meaning_it': 'essere (esistere, stato perm.)', 'meaning_en': 'to be (exist, state)', 'pron': '/jita/'},
            'kita':             {'pos': 'verb', 'meaning_it': 'avere, dovere, possedere', 'meaning_en': 'to have, must, possess', 'pron': '/kita/'},
            'yeta':             {'pos': 'verb', 'meaning_it': 'volere, desiderare, mancare', 'meaning_en': 'to want, desire, lack', 'pron': '/jeta/'},
            'dhaba':            {'pos': 'verb', 'meaning_it': 'amare', 'meaning_en': 'to love', 'pron': '/ðaba/'},
            'bomya':            {'pos': 'verb', 'meaning_it': 'odiare', 'meaning_en': 'to hate', 'pron': '/bomja/'},
            'ĉoterlia':         {'pos': 'verb', 'meaning_it': 'perdonare, scusare', 'meaning_en': 'to forgive, excuse', 'pron': '/ʧoterlia/'},
            'mabloa':           {'pos': 'verb', 'meaning_it': 'splendere, brillare', 'meaning_en': 'to shine, glitter', 'pron': '/mabloa/'},
            'bwka':             {'pos': 'verb', 'meaning_it': 'pensare; credere', 'meaning_en': 'to think; believe', 'pron': '/buːka/'},
            'dreha':            {'pos': 'verb', 'meaning_it': 'vedere; guardare', 'meaning_en': 'to see; look; watch', 'pron': '/dreːa/'},
            'pyha':             {'pos': 'verb', 'meaning_it': 'correre', 'meaning_en': 'to run', 'pron': '/piːa/'},
            'werla':            {'pos': 'verb', 'meaning_it': 'esplorare; cercare', 'meaning_en': 'to explore; seek', 'pron': '/uːerla/'},
            'mera':             {'pos': 'verb', 'meaning_it': 'mangiare', 'meaning_en': 'to eat', 'pron': '/mera/'},
            'jemba':            {'pos': 'verb', 'meaning_it': 'bere', 'meaning_en': 'to drink', 'pron': '/ʒemba/'},
            'medala':           {'pos': 'verb', 'meaning_it': 'dormire', 'meaning_en': 'to sleep', 'pron': '/medala/'},
            'eja':              {'pos': 'verb/suffix', 'meaning_it': 'parlare (lingua); lingua; cittadino di', 'meaning_en': 'to speak (language); language; citizen of', 'pron': '/eʒa/'},
            'ryja':             {'pos': 'verb', 'meaning_it': 'fare; produrre; costruire', 'meaning_en': 'do; make; produce', 'pron': '/riːʒa/'},
            'pidea':            {'pos': 'verb', 'meaning_it': 'cominciare, iniziare', 'meaning_en': 'to begin, to start', 'pron': '/pidea/'},
            
            # Aggiungo qui le parole dalla lista lunga che erano verbi
            'gaia':             {'pos': 'verb', 'meaning_it': 'acchiappare', 'meaning_en': 'to catch, to grab', 'pron': '/gaia/'},
            'maya':             {'pos': 'verb', 'meaning_it': 'aiutare', 'meaning_en': 'to help', 'pron': '/maiːa/'},
            'lidowa':           {'pos': 'verb', 'meaning_it': 'affittare', 'meaning_en': 'to rent', 'pron': '/lidouːa/'},
            'debira':           {'pos': 'verb', 'meaning_it': 'capire', 'meaning_en': 'to understand', 'pron': '/debira/'},
            'oĝela':            {'pos': 'verb', 'meaning_it': 'comperare', 'meaning_en': 'to buy', 'pron': '/oʤela/'},
            'media':            {'pos': 'verb', 'meaning_it': 'conoscere', 'meaning_en': 'to know (person/place)', 'pron': '/media/'},
            'lifora':           {'pos': 'verb', 'meaning_it': 'costruire', 'meaning_en': 'to build, construct', 'pron': '/lifora/'},
            'pida':             {'pos': 'verb', 'meaning_it': 'diventare', 'meaning_en': 'to become', 'pron': '/pida/'},
            'jekma':            {'pos': 'verb', 'meaning_it': 'firmare', 'meaning_en': 'to sign', 'pron': '/ʒekma/'},
            'vilex':            {'pos': 'verb', 'meaning_it': 'gelare', 'meaning_en': 'to freeze', 'pron': '/viːleks/'}, # x -> /ks/ o /ʃ/? Utente ha specificato /ʃ/
            'delova':           {'pos': 'verb', 'meaning_it': 'guidare', 'meaning_en': 'to drive, guide', 'pron': '/delova/'},
            'nida':             {'pos': 'verb', 'meaning_it': 'incontrare', 'meaning_en': 'to meet', 'pron': '/nida/'},
            'lidamya':          {'pos': 'verb', 'meaning_it': 'mordere', 'meaning_en': 'to bite', 'pron': '/lidamja/'},
            'xemada':           {'pos': 'verb', 'meaning_it': 'nevicare', 'meaning_en': 'to snow', 'pron': '/ʃemada/'},
            'inka':             {'pos': 'verb', 'meaning_it': 'parlare (generico)', 'meaning_en': 'to speak, talk', 'pron': '/inka/'},
            'rima':             {'pos': 'verb', 'meaning_it': 'partire', 'meaning_en': 'to leave, depart', 'pron': '/rima/'},
            'piĝea':            {'pos': 'verb', 'meaning_it': 'piegare', 'meaning_en': 'to bend, fold', 'pron': '/piʤea/'},
            'lyema':            {'pos': 'verb', 'meaning_it': 'piovere', 'meaning_en': 'to rain', 'pron': '/liːema/'}, # Conflitto con frekola
            'sevira':           {'pos': 'verb', 'meaning_it': 'portare', 'meaning_en': 'to bring, carry', 'pron': '/sevira/'},
            'rolya':            {'pos': 'verb', 'meaning_it': 'rapinare', 'meaning_en': 'to rob', 'pron': '/rolja/'},
            'relada':           {'pos': 'verb', 'meaning_it': 'rompere', 'meaning_en': 'to break', 'pron': '/relada/'},
            'lah':              {'pos': 'verb', 'meaning_it': 'sapere (fatto)', 'meaning_en': 'to know (a fact)', 'pron': '/lah/'},
            'mimeraĝa':         {'pos': 'verb', 'meaning_it': 'scegliere', 'meaning_en': 'to choose', 'pron': '/mimeraʤa/'},
            'noeda':            {'pos': 'verb', 'meaning_it': 'soffiare', 'meaning_en': 'to blow', 'pron': '/noeda/'},
            'vemita':           {'pos': 'verb', 'meaning_it': 'trovare', 'meaning_en': 'to find', 'pron': '/vemita/'},
            'janepa':           {'pos': 'verb', 'meaning_it': 'venire', 'meaning_en': 'to come', 'pron': '/ʒanepa/'},

            # Aggettivi, colori e dimostrativi
            'ylieva':           {'pos': 'adjective', 'meaning_it': 'buono/a', 'meaning_en': 'good', 'pron': '/iːlieva/'},
            'umpo':             {'pos': 'adjective', 'meaning_it': 'eccellente', 'meaning_en': 'excellent', 'pron': '/umpo/'},
            'eke':              {'pos': 'adjective', 'meaning_it': 'facile', 'meaning_en': 'easy', 'pron': '/eke/'}, # Sostituisce opo
            'dehvo':            {'pos': 'adjective', 'meaning_it': 'difficile', 'meaning_en': 'difficult', 'pron': '/dehvo/'},
            'lip':              {'pos': 'adjective', 'meaning_it': 'rosso', 'meaning_en': 'red', 'pron': '/lip/'},
            'eira':             {'pos': 'adjective', 'meaning_it': 'giallo', 'meaning_en': 'yellow', 'pron': '/eira/'},
            'nyik':             {'pos': 'adjective', 'meaning_it': 'blu', 'meaning_en': 'blue', 'pron': '/njik/'},
            'klem':             {'pos': 'adjective', 'meaning_it': 'verde', 'meaning_en': 'green', 'pron': '/klem/'},
            'ploke':            {'pos': 'adjective', 'meaning_it': 'nero', 'meaning_en': 'black', 'pron': '/ploke/'},
            'viris':            {'pos': 'adjective', 'meaning_it': 'bianco', 'meaning_en': 'white', 'pron': '/viris/'},
            'kef':              {'pos': 'adjective', 'meaning_it': 'rosa', 'meaning_en': 'pink', 'pron': '/kef/'},
            'klye':             {'pos': 'adjective', 'meaning_it': 'grigio (generale)', 'meaning_en': 'gray (general)', 'pron': '/kliːe/'},
            'kepoz':            {'pos': 'adjective', 'meaning_it': 'grigio (del cielo)', 'meaning_en': 'gray (sky)', 'pron': '/kepoz/'},
            'lipeira':          {'pos': 'adjective/verb', 'meaning_it': 'arancione; diventare arancione', 'meaning_en': 'orange; to become orange', 'pron': '/lipeira/'},
            'lipnyk':           {'pos': 'adjective', 'meaning_it': 'viola (colore principale)', 'meaning_en': 'purple (main color)', 'pron': '/lipniːk/'},
            'bapir':            {'pos': 'adjective/noun', 'meaning_it': 'tonalità/sfumatura di viola', 'meaning_en': 'shade/hue of purple', 'pron': '/bapir/'},
            'liploke':          {'pos': 'adjective', 'meaning_it': 'marrone (colore principale)', 'meaning_en': 'brown (main color)', 'pron': '/liploke/'},
            'plom':             {'pos': 'adjective/noun', 'meaning_it': 'tonalità/sfumatura di marrone', 'meaning_en': 'shade/hue of brown', 'pron': '/plom/'},
            'lipdok':           {'pos': 'adjective', 'meaning_it': 'cremisi, scarlatto', 'meaning_en': 'crimson, scarlet', 'pron': '/lipdok/'},
            'nyikin':           {'pos': 'adjective', 'meaning_it': 'ciano, turchese', 'meaning_en': 'cyan, turquoise', 'pron': '/njikin/'},
            'pie':              {'pos': 'adjective', 'meaning_it': 'beige', 'meaning_en': 'beige', 'pron': '/pie/'},
            'kortil':           {'pos': 'noun/adjective', 'meaning_it': 'bronzo; bronzeo', 'meaning_en': 'bronze; bronze-colored', 'pron': '/kortil/'}, # Già c'era, ora confermato come agg
            'bemiĝ':            {'pos': 'adjective', 'meaning_it': 'colore carnagione', 'meaning_en': 'flesh color', 'pron': '/bemiʤ/'},
            'tenji':            {'pos': 'demonstrative', 'meaning_it': 'questo/a', 'meaning_en': 'this', 'pron': '/tenʒi/'},
            'kenjo':            {'pos': 'demonstrative', 'meaning_it': 'quello/a', 'meaning_en': 'that', 'pron': '/kenʒo/'},
            'idon':             {'pos': 'determiner', 'meaning_it': 'quale?; che? (det.)', 'meaning_en': 'which?; what? (det.)', 'pron': '/idon/'},
            'milo':             {'pos': 'adverb/adjective', 'meaning_it': 'prossimo, dopo', 'meaning_en': 'next, after', 'pron': '/milo/'},
            'ymet':             {'pos': 'adverb/adjective/noun', 'meaning_it': 'ultimo, fine', 'meaning_en': 'last, end', 'pron': '/iːmet/'},
            'ika':              {'pos': 'noun', 'meaning_it': 'settimana (sing.)', 'meaning_en': 'week (sg.)', 'pron': '/ika/'},
            'ike':              {'pos': 'noun', 'meaning_it': 'settimane (pl.)', 'meaning_en': 'weeks (pl.)', 'pron': '/ike/'}, # Plurale irregolare
            'gadik':            {'pos': 'noun', 'meaning_it': 'quarto (frazione)', 'meaning_en': 'quarter (fraction)', 'pron': '/gadik/'},
            'vekia':            {'pos': 'noun', 'meaning_it': 'mezzora', 'meaning_en': 'half an hour', 'pron': '/vekia/'},
            'vedan':            {'pos': 'noun/adverb', 'meaning_it': 'mezzogiorno (14:00 ATH)', 'meaning_en': 'midday, noon (14:00 ATH)', 'pron': '/vedan/'},
            'venahr':           {'pos': 'noun/adverb', 'meaning_it': 'mezzanotte (00:00 ATH)', 'meaning_en': 'midnight (00:00 ATH)', 'pron': '/venahr/'},
            'nalmek':           {'pos': 'noun', 'meaning_it': 'mattino', 'meaning_en': 'morning', 'pron': '/nalmek/'},
            'daja':             {'pos': 'noun', 'meaning_it': 'pomeriggio', 'meaning_en': 'afternoon', 'pron': '/daʒa/'},
            'san':              {'pos': 'noun', 'meaning_it': 'sera', 'meaning_en': 'evening', 'pron': '/san/'}, # Conferma da tua lista lunga
            'maro':             {'pos': 'ordinal_numeral', 'meaning_it': 'primo', 'meaning_en': 'first', 'pron': '/maro/'},
            'bero':             {'pos': 'ordinal_numeral', 'meaning_it': 'secondo', 'meaning_en': 'second', 'pron': '/bero/'},
            'ĉero':             {'pos': 'ordinal_numeral', 'meaning_it': 'terzo', 'meaning_en': 'third', 'pron': '/ʧero/'},

            # Interrogativi
            'hon':              {'pos': 'pronoun', 'meaning_it': 'chi?', 'meaning_en': 'who?', 'pron': '/oːn/'},
            'oos':              {'pos': 'pronoun', 'meaning_it': 'cosa?', 'meaning_en': 'what?', 'pron': '/oːs/'},
            'edon':             {'pos': 'adverb', 'meaning_it': 'dove?', 'meaning_en': 'where?', 'pron': '/edon/'},
            'elos':             {'pos': 'adverb', 'meaning_it': 'quando?', 'meaning_en': 'when?', 'pron': '/elos/'},
            'Bojyke':           {'pos': 'adverb', 'meaning_it': 'perché?', 'meaning_en': 'why?', 'pron': '/boʒiːke/'},
            'enta':             {'pos': 'adverb', 'meaning_it': 'come?', 'meaning_en': 'how?', 'pron': '/enta/'},

            # Congiunzioni
            'ho':               {'pos': 'conjunction', 'meaning_it': 'perché, poiché', 'meaning_en': 'because, since', 'pron': '/ho/'},
            'ya':               {'pos': 'conjunction', 'meaning_it': 'e', 'meaning_en': 'and', 'pron': '/iːa/'},
            'yo':               {'pos': 'conjunction', 'meaning_it': 'o, oppure', 'meaning_en': 'or', 'pron': '/iːo/'},
            'ermi':             {'pos': 'conjunction', 'meaning_it': 'quando (cong.)', 'meaning_en': 'when (conj.)', 'pron': '/ermi/'},
            'en':               {'pos': 'conjunction', 'meaning_it': 'se', 'meaning_en': 'if', 'pron': '/en/'},
            'koyk':             {'pos': 'adverb/conjunction', 'meaning_it': 'altrimenti', 'meaning_en': 'else, otherwise', 'pron': '/koiːk/'},
            'jodgim':           {'pos': 'conjunction', 'meaning_it': 'mentre', 'meaning_en': 'while', 'pron': '/ʒodgim/'},
            'tho':              {'pos': 'adverb', 'meaning_it': 'anche; pure; così', 'meaning_en': 'also; too; so', 'pron': '/toː/'},
            
            # Interiezioni e Pragmatica
            'rompo':            {'pos': 'interjection', 'meaning_it': 'grazie', 'meaning_en': 'thank you', 'pron': '/rompo/'},
            'kehla':            {'pos': 'interjection', 'meaning_it': 'ciao', 'meaning_en': 'hello, hi', 'pron': '/kehla/'},
            'ylievamor':        {'pos': 'interjection', 'meaning_it': 'benvenuto', 'meaning_en': 'welcome', 'pron': '/iːlievamor/'},
            'ke':               {'pos': 'interjection', 'meaning_it': 'sì', 'meaning_en': 'yes', 'pron': '/ke/'},
            'misi':             {'pos': 'interjection', 'meaning_it': 'bene!', 'meaning_en': 'good!, well!', 'pron': '/misi/'},
            'nilmiet':          {'pos': 'adverb', 'meaning_it': 'per favore', 'meaning_en': 'please', 'pron': '/nilmiet/'},
            'ĉoko':             {'pos': 'preposition/adverb', 'meaning_it': 'vicino (sociale, supporto)', 'meaning_en': 'near (socially), to support', 'pron': '/ʧoko/'},
            'meoje':            {'pos': 'adverb/preposition', 'meaning_it': 'vicino (luogo)', 'meaning_en': 'near (place)', 'pron': '/meoʒe/'},
            
            # Aggiungo qui le parole dalla lista lunga che erano preposizioni o avverbi non interrogativi
            'ny':               {'pos': 'preposition', 'meaning_it': 'a (moto a luogo, stato in luogo)', 'meaning_en': 'to, at, in', 'pron': '/niː/'},
            'fo':               {'pos': 'particle_impersonal', 'meaning_it': 'si (impersonale/passivante)', 'meaning_en': 'one (impersonal), is X-ed', 'pron': '/fo/'},
            'ye':               {'pos': 'adverb/prefix', 'meaning_it': 'ancora; ri-, re-', 'meaning_en': 'again, still; re-', 'pron': '/iːe/'},
            'otis':             {'pos': 'adverb', 'meaning_it': 'adesso', 'meaning_en': 'now', 'pron': '/otis/'},
            'fyla':             {'pos': 'adverb/conjunction', 'meaning_it': 'allora, quindi', 'meaning_en': 'then, so', 'pron': '/fiːla/'},
            'enteno':           {'pos': 'adverb/conjunction', 'meaning_it': 'altrimenti', 'meaning_en': 'otherwise', 'pron': '/enteno/'},
            'lan':              {'pos': 'preposition', 'meaning_it': 'da (moto da luogo)', 'meaning_en': 'from', 'pron': '/lan/'},
            'otyrom':           {'pos': 'adverb/preposition', 'meaning_it': 'davanti', 'meaning_en': 'in front of, before', 'pron': '/otirom/'},
            'tidal':            {'pos': 'adverb/preposition', 'meaning_it': 'dietro', 'meaning_en': 'behind', 'pron': '/tidal/'},
            'embax':            {'pos': 'adverb/noun', 'meaning_it': 'domani', 'meaning_en': 'tomorrow', 'pron': '/embaks/'},   # UFFICIALE
            'sifan':            {'pos': 'adverb/preposition', 'meaning_it': 'dopo', 'meaning_en': 'after, then', 'pron': '/sifan/'},
            'bembax':           {'pos': 'adverb/noun', 'meaning_it': 'dopodomani', 'meaning_en': 'day after tomorrow', 'pron': '/bembaks/'},
            'embadyl':          {'pos': 'adverb/noun', 'meaning_it': 'ieri', 'meaning_en': 'yesterday', 'pron': '/embadiːl/'}, # UFFICIALE
            'entredija':        {'pos': 'adverb', 'meaning_it': 'immediatamente', 'meaning_en': 'immediately', 'pron': '/entrediʒa/'},
            'jedon':            {'pos': 'phrase_adverbial', 'meaning_it': 'in tempo', 'meaning_en': 'in time', 'pron': '/ʒedon/'},
            'je oer':           {'pos': 'phrase_adverbial', 'meaning_it': 'intanto', 'meaning_en': 'meanwhile', 'pron': '/ʒe oer/'},
            'bembadyl':         {'pos': 'adverb/noun', 'meaning_it': 'l’altroieri', 'meaning_en': 'day before yesterday', 'pron': '/bembadiːl/'}, # Duplicato, già inserito
            'voje':             {'pos': 'adverb/adjective', 'meaning_it': 'lontano', 'meaning_en': 'far', 'pron': '/voʒe/'},
            'mifil':            {'pos': 'adverb', 'meaning_it': 'mai', 'meaning_en': 'never', 'pron': '/mifil/'},
            'neaĝe':            {'pos': 'adverb', 'meaning_it': 'molto', 'meaning_en': 'very, much', 'pron': '/neaʤe/'},
            'embadan':          {'pos': 'adverb/noun', 'meaning_it': 'oggi', 'meaning_en': 'today', 'pron': '/embadan/'},     # UFFICIALE
            'kia':              {'pos': 'noun/adverb', 'meaning_it': 'ora (tempo); adesso', 'meaning_en': 'hour; now (time)', 'pron': '/kia/'}, # Conflitto con otis
            'tis':              {'pos': 'preposition', 'meaning_it': 'per (scopo, causa)', 'meaning_en': 'for (purpose), because of', 'pron': '/tis/'},
            'medar':            {'pos': 'adverb/adjective', 'meaning_it': 'poco', 'meaning_en': 'little, few', 'pron': '/medar/'},
            'ysed':             {'pos': 'adverb', 'meaning_it': 'poi', 'meaning_en': 'then, afterwards', 'pron': '/iːsed/'},
            'ynte':             {'pos': 'adverb', 'meaning_it': 'presto', 'meaning_en': 'soon, early', 'pron': '/iːnte/'},
            'pivol':            {'pos': 'adverb/preposition', 'meaning_it': 'prima', 'meaning_en': 'before, first', 'pron': '/pivol/'},
            'lolyr':            {'pos': 'adverb', 'meaning_it': 'raramente', 'meaning_en': 'rarely', 'pron': '/loliːr/'},
            'kiram':            {'pos': 'preposition', 'meaning_it': 'sopra (con contatto)', 'meaning_en': 'on, upon', 'pron': '/kiram/'},
            'wym':              {'pos': 'preposition', 'meaning_it': 'sotto', 'meaning_en': 'under, below', 'pron': '/uːiːm/'},
            'avym':             {'pos': 'adverb', 'meaning_it': 'spesso', 'meaning_en': 'often', 'pron': '/aviːm/'},
            'am':               {'pos': 'preposition', 'meaning_it': 'su (senza contatto)', 'meaning_en': 'on, up (no contact)', 'pron': '/am/'},
            'delye':            {'pos': 'adverb', 'meaning_it': 'subito', 'meaning_en': 'immediately', 'pron': '/delje/'}, # Conflitto con entredija
            'ondames':          {'pos': 'adverb', 'meaning_it': 'talvolta', 'meaning_en': 'sometimes', 'pron': '/ondames/'},
            'ries':             {'pos': 'adverb', 'meaning_it': 'tardi', 'meaning_en': 'late', 'pron': '/riːes/'},
            'dan':              {'pos': 'noun', 'meaning_it': 'giorno (concetto)', 'meaning_en': 'day (concept)', 'pron': '/dan/'}, 
        }

        self.derivation_graph = nx.DiGraph()
        self.vowels = "aeiouyw" # w è /uː/
        self.consonants = "bkĉdfgĝhjlmnprsxtvz" # x è /ʃ/

    def to_ordinal_numeral(self, cardinal_value: int) -> Optional[str]:
        """
        Converte un valore numerico cardinale nella sua forma ordinale Anthalejana.
        Restituisce None se il numero non è nel nostro sistema base per cardinali diretti.
        """
        # Ottiene la parola per il numero cardinale
        cardinal_word = self.numbers.numbers.get(cardinal_value) # self.numbers è AnthalejaNumericalSystem
        if cardinal_word:
            # Applica il suffisso -ro. Gestisce casi come 'mo' (9) -> 'moro'.
            # Se il cardinale finisce per 'o' e il suffisso è '-ro', potrebbe esserci elisione?
            # Per ora, semplice aggiunta. Mo + ro = Moro (nono)
            if cardinal_word.endswith('e'): # es. ĉe, ĝe, be
                return cardinal_word[:-1] + "ero" # bero, ĉero, ĝero (secondo, terzo, sesto) - più eufonico
            return cardinal_word + "ro"
        # Per numeri composti (es. 10+) la logica sarebbe più complessa
        # e potrebbe richiedere la forma scritta completa del cardinale.
        # Questa è una semplificazione per i numeri base.
        # Per ora, restituiamo None se non è un numero base semplice.
        return None 

    def generate_sentence(self):
        nouns = [word for word, data in self.lexicon.items() if data['pos'] == 'noun']
        verbs = [word for word, data in self.lexicon.items() if data['pos'] == 'verb']
        if not nouns or not verbs: return "Lessico insufficiente per generare una frase."
        
        pronoun_key = random.choice(list(self.pronouns_subject.keys()))
        pronoun = self.pronouns_subject[pronoun_key]
        
        noun = random.choice(nouns)
        verb_root = random.choice(verbs)
        
        rand_tense = random.choice(list(self.verb_system.tenses.keys()))
        rand_aspect = random.choice(list(self.verb_system.aspects.keys()))
        rand_mood = random.choice(list(self.verb_system.moods.keys()))
        if rand_mood == 'imperative': rand_tense = 'present' # L'imperativo ha una sua forma
        conjugated_verb = self.verb_system.conjugate(verb_root, rand_tense, rand_aspect, rand_mood)

        article_type = random.choice(['definite', 'zero', 'emphatic_indefinite'])
        article_str = ""
        if article_type == 'definite':
            article_str = self.articles['DEF'] + " "
        elif article_type == 'emphatic_indefinite':
            # Assicurati che 'ma' (numero 1) esista nel sistema numerico per essere usato qui
            if 1 in self.numbers.numbers:
                article_str = self.numbers.numbers[1] + " "
            else: # Fallback se 'ma' non è definito lì per qualche motivo
                article_str = "ma "

        base_sentence_core = f"{conjugated_verb} {article_str}{noun}"
        
        sentence_type = random.choice(['statement', 'negation', 'question'])
        final_sentence = ""

        if sentence_type == 'negation':
            final_sentence = f"{pronoun.capitalize()} ne {base_sentence_core}."
        elif sentence_type == 'question':
            # Scegliamo un interrogativo per domande aperte, o 'Ma' per sì/no
            wh_word_keys = [k for k,v in self.lexicon.items() if v['pos'] in ['pronoun/determiner','adverb'] and '?' in v['meaning_it']]
            if random.choice([True, False]) and wh_word_keys : # 50% probabilità di domanda aperta se possibile
                wh_word = random.choice(wh_word_keys)
                if self.lexicon[wh_word]['pos'] == 'pronoun/determiner' and 'cosa?' in self.lexicon[wh_word]['meaning_it']: # 'pa'
                    final_sentence = f"¿{wh_word.capitalize()} {pronoun} {conjugated_verb}?" # Es: ¿Pa ja yeta?
                else:
                    final_sentence = f"¿{wh_word.capitalize()} {pronoun} {base_sentence_core}?"
            else:
                final_sentence = f"¿Ma {pronoun} {base_sentence_core}?"
        else: # statement
            final_sentence = f"{pronoun.capitalize()} {base_sentence_core}."
        return final_sentence

    def negate_adjective(self, adjective):
        if adjective.startswith('ne'): return adjective[2:] 
        return 'ne' + adjective
        
    def negate_verb(self, verb):
        if verb.startswith('ne'): return verb[2:]
        return 'ne' + verb

    def verb_from_adjective_causative(self, adjective):
        if adjective and adjective[0] in self.vowels: return "ĉi" + adjective
        return "ĉy" + adjective

    def verb_from_adjective_inchoative(self, adjective):
        if adjective.endswith('a'): return adjective
        return adjective + "a"

    def verb_from_noun_instrumental(self, noun):
        return "e" + noun

    def verb_from_noun_action(self, noun):
        if noun.endswith('a'): return noun
        return noun + "a"
        
    def adjective_to_adverb(self, adj): return ("on" if adj and adj[0] in self.vowels else "oni") + adj
    def adjective_to_abstract_noun(self, adj): return adj + ("s" if adj and adj[0] in self.vowels else "os")
    def noun_to_adjective_quality(self, noun): return "e" + noun
    def noun_to_adjective_relation(self, noun): return "i" + noun
    def verb_to_adjective_result(self, verb): return verb + ("n" if verb and verb[-1] in self.vowels else "an")
    def verb_to_adjective_tending(self, verb): return verb + ("kine" if verb and verb[-1] in self.vowels else "ine")
    def verb_to_act_noun(self, verb): return verb + ("kai" if verb and verb[-1] in self.vowels else "akai")
    def verb_to_product_noun(self, verb): return "ty" + verb
    def verb_to_agent_noun(self, verb): return "e" + verb
    def noun_to_place(self, noun): return ("k" if noun and noun[0] in self.vowels else "ki") + noun
    def noun_to_diminutive(self, noun): return ("nik" if noun and noun[0] in self.vowels else "nike") + noun
    def noun_to_augmentative(self, noun): return ("mik" if noun and noun[0] in self.vowels else "mike") + noun
    
    def pluralize_noun(self, noun):
        if noun.endswith('eja'): return noun
        if noun and noun[-1].lower() in self.vowels: return noun + 'x'
        return noun + 'ox'

    def generate_demonym(self, city_name_original):
        stem = city_name_original
        if city_name_original.lower().endswith('ys'):
            stem = city_name_original[:-2]
        if stem and stem[-1].lower() in self.vowels:
            stem += 'n'
        return stem + "eja"

# -- CLASSE 6: FACCIATA PRINCIPALE DELL'ECOSISTEMA --
class Anthaleja:
    """Classe facciata per interagire con l'ecosistema Anthaleja."""
    def __init__(self):
        self.lang = AnthalejaLang()
        self.numbers = self.lang.numbers # Esposto per convenienza
        self.colors = self.lang.colors   # Esposto per convenienza
        self._initialize_vocab() # Vocabolario per esempi, non il lessico principale

    def _initialize_vocab(self):
        # Questo è per esempi specifici, non il lessico principale della lingua
        self.thematic_vocab = {
            'adventure': {'nouns': ['montagna', 'foresta', 'spada'], 'verbs': ['esplorare', 'scoprire', 'combattere']},
            'mystery': {'nouns': ['indizio', 'segreto', 'notte'], 'verbs': ['investigare', 'trovare', 'nascondere']}
        }
        self.translation_dict_it_to_ath = {
            'l\'eroe': 'ol erota', 'esplora': 'werla', 'una': 'ma', 'foresta': 'silva', 'oscura': 'maluma-inya'
        }

    def demonstrate_morphology(self, word, pos):
        # Assicurati che la parola esista nel lessico prima di derivare
        if word not in self.lang.lexicon and pos == 'adjective':
            # Prova a vedere se è un colore base non nel lessico principale ma in color system
            if word in self.lang.colors.colors.values():
                # OK, è un colore, possiamo procedere
                pass
            else:
                print(f"\n--- Parola '{word}' non trovata nel lessico per derivazioni ---")
                return

        print(f"\n--- Derivazioni per '{word}' ({pos}) ---")
        if pos == 'adjective':
            print(f"  > Avverbio: {self.lang.adjective_to_adverb(word)}")
            print(f"  > Nome Astratto: {self.lang.adjective_to_abstract_noun(word)}")
            print(f"  > Verbo Causativo (rendere {word}): {self.lang.verb_from_adjective_causative(word)}")
            print(f"  > Verbo Incoativo (diventare {word}): {self.lang.verb_from_adjective_inchoative(word)}")
            print(f"  > Contrario (ne{word}): {self.lang.negate_adjective(word)}")
        elif pos == 'noun':
            print(f"  > Plurale: {self.lang.pluralize_noun(word)}")
            print(f"  > Aggettivo (qualità di): {self.lang.noun_to_adjective_quality(word)}")
            print(f"  > Aggettivo (relativo a): {self.lang.noun_to_adjective_relation(word)}")
            print(f"  > Verbo (azione tipica di): {self.lang.verb_from_noun_action(word)}")
            print(f"  > Verbo (strumentale): {self.lang.verb_from_noun_instrumental(word)}")
            print(f"  > Luogo di: {self.lang.noun_to_place(word)}")
            print(f"  > Diminutivo: {self.lang.noun_to_diminutive(word)}")
            print(f"  > Accrescitivo: {self.lang.noun_to_augmentative(word)}")
        elif pos == 'verb':
            print(f"  > Contrario (ne{word}): {self.lang.negate_verb(word)}")
            print(f"  > Nome (l'atto di): {self.lang.verb_to_act_noun(word)}")
            print(f"  > Nome (prodotto di): {self.lang.verb_to_product_noun(word)}")
            print(f"  > Nome (agente): {self.lang.verb_to_agent_noun(word)}")
            print(f"  > Aggettivo (risultato di): {self.lang.verb_to_adjective_result(word)}")
            print(f"  > Aggettivo (tendente a): {self.lang.verb_to_adjective_tending(word)}")

    def demonstrate_verb_conjugation(self, verb_root):
        if verb_root not in [k for k,v in self.lang.lexicon.items() if v['pos'] == 'verb']:
            print(f"\n--- Radice verbale '{verb_root}' non trovata nel lessico ---")
            return
        print(f"\n--- Coniugazioni per la radice '{verb_root}' ---")
        vs = self.lang.verb_system
        print(f"  Presente Indicativo Semplice: {vs.conjugate(verb_root, 'present', 'simple', 'indicative')}")
        print(f"  Passato Indicativo Progressivo: {vs.conjugate(verb_root, 'past', 'progressive', 'indicative')}")
        print(f"  Futuro Indicativo Perfetto: {vs.conjugate(verb_root, 'future', 'perfect', 'indicative')}")
        print(f"  Condizionale Congiuntivo Semplice: {vs.conjugate(verb_root, 'conditional', 'simple', 'subjunctive')}")
        print(f"  Imperativo: {vs.conjugate(verb_root, tense='imperative', mood='imperative')}") # Tense can be 'present' here

    def generate_story(self, theme='adventure', length=3):
        print(f"\n--- Storia sul tema '{theme}' ---")
        # Logica per generare una storia, per ora semplificata
        for i in range(length):
            print(f"  [{i+1}] {self.lang.generate_sentence()}")

    def translate_to_anthaleja(self, italian_text):
        print(f"\n--- Traduzione di '{italian_text}' (Semplificata) ---")
        words = italian_text.lower().split()
        translated_words = [self.translation_dict_it_to_ath.get(w, f'[{w}]') for w in words] # Usa il dict per esempi
        print(f"  Risultato: {' '.join(translated_words)}.")

    def vocabulary_trainer(self):
        print("\n--- Sessione di Allenamento Vocabolario (Esempio) ---")
        # Esempio: scegli una parola dal lessico e chiedi la traduzione
        word_keys = [k for k,v in self.lang.lexicon.items() if 'meaning_it' in v]
        if not word_keys: 
            print("  Lessico vuoto per l'allenamento.")
            return
        
        random_word_key = random.choice(word_keys)
        random_word_data = self.lang.lexicon[random_word_key]
        print(f"  Traduci in Italiano: '{random_word_key}' (POS: {random_word_data['pos']})")
        print(f"  Risposta possibile: {random_word_data['meaning_it']}")

# -- BLOCCO DI ESECUZIONE PRINCIPALE --
if __name__ == "__main__":
    anthaleja = Anthaleja()
    
    print("="*60)
    print("ECOSISTEMA COMPLETO LINGUA ANTHALEJA".center(60))
    print("="*60)

    print("\n[1. SISTEMA NUMERICO E COLORI]")
    print(f"  Numero 12345: {anthaleja.numbers.get_number(12345)}")
    print(f"  Numero Formattato 2.5e6: {anthaleja.numbers.format_large_number(2.5e6, 'm')}")
    print(f"  Colore 'blu scuro': {anthaleja.colors.get_color('blue', 'dark')}")
    print(f"  Colore 'oro brillante': {anthaleja.colors.get_color('gold', 'bright')}")

    print("\n[2. DIMOSTRAZIONE MORFOLOGICA]")
    anthaleja.demonstrate_morphology('ylieva', 'adjective')
    anthaleja.demonstrate_morphology('ding', 'noun')
    anthaleja.demonstrate_morphology('dhaba', 'verb')

    print("\n[3. DIMOSTRAZIONE CONIUGAZIONE VERBALE]")
    anthaleja.demonstrate_verb_conjugation('mera') # Mangiare
    anthaleja.demonstrate_verb_conjugation('yeta') # Volere

    print("\n[4. GENERAZIONE LINGUISTICA]")
    print(f"  Frase Casuale 1: {anthaleja.lang.generate_sentence()}")
    print(f"  Frase Casuale 2: {anthaleja.lang.generate_sentence()}")
    anthaleja.generate_story('mystery', 2)

    print("\n[5. APPLICAZIONI LINGUISTICHE]")
    anthaleja.translate_to_anthaleja("L'eroe esplora una foresta oscura")
    anthaleja.vocabulary_trainer()

    print("\n[6. DIMOSTRAZIONE CALENDARIO]")
    now_anthaleja = AnthalejaDatetime()
    print(f"  Data e Ora Attuale Anthaleja: {now_anthaleja}")
    specific_date_earth = datetime(2024, 12, 25, 10, 30, 0)
    specific_date_anthaleja = AnthalejaDatetime(specific_date_earth)
    print(f"  Data Specifica (25/12/2024 10:30 Terra): {specific_date_anthaleja.format('DAY, d MONTH Y G:i:s')}")

    print("\n[7. DIMOSTRAZIONE DEMONIMI]")
    print(f"  Abitante di 'Roma (Romano)': {anthaleja.lang.generate_demonym('Roma')}")
    print(f"  Abitante di 'Parigi': {anthaleja.lang.generate_demonym('Parisys')}")
    print(f"  Plurale di 'Roma (Romani)': {anthaleja.lang.pluralize_noun(anthaleja.lang.generate_demonym('Roma'))}")
    print(f"  Plurale di 'ding': {anthaleja.lang.pluralize_noun('ding')}")
    print("="*60)
    
    