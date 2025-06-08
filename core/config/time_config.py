"""
Configurazione del tempo e calendario di Anthalys
"""
# --- IMPORTAZIONI DAL SISTEMA TEMPORALE DI ANTHALYS ---
from core.world.ATHDateTime.ATHDateTimeInterface import ATHDateTimeInterface
from core.enums import TimeOfDay

# Importa anche i nomi dei mesi/giorni se sono definiti altrove e ti servono qui
# Se sono definiti come attributi di ATHDateTimeInterface, accedi tramite la classe.
# Per ora, li lascio definiti manualmente sotto se non sono in ATHDateTimeInterface.
# from core.world.ATHDateTime.ATHDateTimeInterface import MONTH_NAMES, DAY_NAMES, MONTH_ABBR, DAY_ABBR # Se fossero a livello di modulo

# --- II. CALENDARIO E TEMPO DI ANTHALYS (Nomi variabili ESATTI come da config utente) ---
HXD = ATHDateTimeInterface.HXD_CALENDAR     # Ore per Giorno
DXM = ATHDateTimeInterface.DXM_CALENDAR     # Giorni per Mese
MXY = ATHDateTimeInterface.MXY_CALENDAR     # Mesi per Anno
DXW = ATHDateTimeInterface.DXW_CALENDAR     # Giorni per Settimana
DXY = ATHDateTimeInterface.DXY_CALENDAR     # Giorni per Anno (432)
IXH = ATHDateTimeInterface.IXH_CALENDAR     # mInuti per Ora
SXI = ATHDateTimeInterface.SXI_CALENDAR     # secondi per mInuto

# Costanti Derivate (Minuti)
IXD = IXH * HXD       # Minuti per Giorno
IXW = IXD * DXW       # Minuti per Settimana
IXM = IXD * DXM       # Minuti per Mese
IXY = IXD * DXY       # Minuti per Anno

# Costanti Derivate (Secondi)
SXH = SXI * IXH       # Secondi per Ora
SXD = SXH * HXD       # Secondi per Giorno
SXW = SXD * DXW       # Secondi per Settimana
SXM = SXD * DXM       # Secondi per Mese
SXY = SXD * DXY       # Secondi per Anno

# Costanti Lore e di Epoca
ATH_DATE_FORMAT = "Y, d/m G:i:s"
RDN = 951584400
RY = 5775
DXC = DXY * 100
ADN = RY * DXY

# Nomi Mesi e Giorni
MONTH_NAMES = ATHDateTimeInterface.MONTH_NAMES
DAY_NAMES = ATHDateTimeInterface.DAY_NAMES

MONTH_ABBR = ATHDateTimeInterface.MONTH_ABBR
DAY_ABBR = ATHDateTimeInterface.DAY_ABBR_ATH

WEEKEND_DAY_NUMBERS = [6, 0] # Indici per Ĝejahr (Sabato) e Nijahr (Domenica/Giorno 0)

# Costanti per la simulazione e i tick
TXH_SIMULATION = 1000 # Tick per Ora Simulazione

SXI_GAME = IXH * SXI # Es. 3600
SECONDS_PER_SIMULATION_TICK = SXI_GAME / TXH_SIMULATION # Es. 3600 / 1000 = 3.6

# Costanti necessarie per la simulazione
SIMULATION_START_YEAR = RY
SIMULATION_START_MONTH = 1
SIMULATION_START_DAY = 1
SIMULATION_START_HOUR = 27
SIMULATION_START_MINUTE = 0
SIMULATION_START_SECOND = 0

# Fuso orario di default per la simulazione, deve essere uno tra "ATZ", "ECT", "WCT"
DEFAULT_TIMEZONE = 'ATZ' 

NIGHT_START_HOUR = 22
NIGHT_END_HOUR = 6

# Ore di INIZIO per ogni fase del giorno (basato sul giorno di 28 ore)
TIME_OF_DAY_START_HOURS = {
    TimeOfDay.DAWN: 4,      # L'alba inizia alle 4:00
    TimeOfDay.MORNING: 6,   # La mattina alle 6:00
    TimeOfDay.AFTERNOON: 12,  # Il pomeriggio alle 12:00
    TimeOfDay.DUSK: 19,     # Il tramonto alle 19:00
    TimeOfDay.EVENING: 22,  # La sera alle 22:00
    TimeOfDay.NIGHT: 26,    # La notte alle 26:00 (o -2 rispetto al giorno dopo)
}
