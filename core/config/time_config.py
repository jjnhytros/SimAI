"""
Configurazione del tempo e calendario di Anthalys
"""

# --- Costanti Temporali di Base ---
HXD = 28        # Ore per Giorno
DXM = 24        # Giorni per Mese
MXY = 18        # Mesi per Anno
DXW = 7         # Giorni per Settimana
DXY = MXY * DXM # Giorni per Anno (432)
IXH = 60        # Minuti per Ora
SXI = 60        # Secondi per Minuto

# --- Costanti Derivate ---
IXD = IXH * HXD       # Minuti per Giorno
IXW = IXD * DXW       # Minuti per Settimana
IXM = IXD * DXM       # Minuti per Mese
IXY = IXD * DXY       # Minuti per Anno

SXH = SXI * IXH       # Secondi per Ora
SXD = SXH * HXD       # Secondi per Giorno
SXW = SXD * DXW       # Secondi per Settimana
SXM = SXD * DXM       # Secondi per Mese
SXY = SXD * DXY       # Secondi per Anno

# --- Calendario Anthalys ---
ATH_DATE_FORMAT = "Y, d/m G:i:s"
RDN = 951584400
RY = 5775
DXC = DXY * 100
ADN = RY * DXY

MONTH_NAMES = [
    'Arejal', 'Brukom', 'Ĉelal', 'Kebor', 'Duvol', 'Elumag',
    'Fydrin', 'Ĝinuril', 'Itrekos', 'Jebrax', 'Letranat', 'Mulfus',
    'Nylumer', 'Otlevat', 'Prax', 'Retlixen', 'Sajep', 'Xetul'
]

DAY_NAMES = ['Nijahr', 'Majahr', 'Bejahr', 'Ĉejahr', 'Dyjahr', 'Fejahr', 'Ĝejahr']

MONTH_ABBR = {name: (name[:2] + 'x' if name == "Prax" else name[:3]) for name in MONTH_NAMES}
DAY_ABBR = {name: name[:2] for name in DAY_NAMES}

WEEKEND_DAY_NUMBERS = [6, 0]  # Ĝejahr e Nijahr
SIMULATION_TICKS_PER_HOUR = IXH  # 1 tick = 1 minuto di gioco