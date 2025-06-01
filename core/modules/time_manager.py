# core/modules/time_manager.py
"""
Modulo TimeManager per la gestione del tempo di gioco, del calendario
e dei cicli temporali in SimAI.
Riferimento TODO: I.3, XXXII.8
"""
from typing import Optional # Per il type hinting
from core import settings     # Importiamo le costanti globali

class TimeManager:
    def __init__(self, 
                 start_year: int = settings.RY, 
                 start_month_idx: int = 0,  # 0 per 'Arejal'
                 start_day_idx: int = 0,    # 0 per 'Nijahr' (o il primo giorno del mese)
                 start_hour: int = 7,       # Es. le 7 del mattino
                 start_minute: int = 0):
        """
        Inizializza il TimeManager.
        L'ora di inizio di default è le 07:00 del primo giorno del primo mese dell'anno RY.
        Gli indici per mese e giorno sono 0-based.
        """
        if settings.DEBUG_MODE:
            print("  [TimeManager INIT] Inizializzazione TimeManager...")

        # Stato temporale corrente (1 tick = 1 minuto di gioco come da settings.SIMULATION_TICKS_PER_HOUR = settings.IXH)
        self.current_year: int = start_year
        self.current_month_idx: int = start_month_idx   # 0 a (settings.MXY - 1)
        self.current_day_in_month_idx: int = start_day_idx # 0 a (settings.DXM - 1)
        self.current_hour: int = start_hour             # 0 a (settings.HXD - 1)
        self.current_minute: int = start_minute           # 0 a (settings.IXH - 1)
        
        self.total_ticks_sim: int = 0      # Tick totali passati dall'inizio della simulazione
        self.total_days_sim: int = 0       # Giorni totali passati dall'inizio della simulazione
                                           # (calcolato considerando un giorno 0 come inizio)

        if settings.DEBUG_MODE:
            print(f"  [TimeManager INIT] Ora di inizio simulazione: {self.get_formatted_datetime_string()}")
            print(f"  [TimeManager INIT] Costanti usate: HXD={settings.HXD}, DXM={settings.DXM}, MXY={settings.MXY}, IXH={settings.IXH}")


    def advance_tick(self):
        """
        Avanza il tempo di gioco di un singolo tick (1 minuto di gioco).
        Gestisce il rollover di minuti, ore, giorni, mesi, anni.
        """
        self.total_ticks_sim += 1
        self.current_minute += 1

        if self.current_minute >= settings.IXH: # Se i minuti superano il massimo per ora (60)
            self.current_minute = 0
            self.current_hour += 1
            if settings.DEBUG_MODE and self.total_ticks_sim % (settings.IXH // 10) == 0 : # Log meno frequente
                print(f"    [TimeManager] Nuova ora: {self.current_hour:02d}:00 (Tick: {self.total_ticks_sim})")


            if self.current_hour >= settings.HXD: # Se le ore superano il massimo per giorno (28)
                self.current_hour = 0
                self.current_day_in_month_idx += 1
                self.total_days_sim += 1 # Incrementa il contatore totale dei giorni
                
                if settings.DEBUG_MODE:
                    print(f"    [TimeManager] NUOVO GIORNO! Giorno {self.get_current_day_of_month()} di "
                          f"{self.get_current_month_name()}, Anno {self.current_year}. "
                          f"({self.get_current_day_of_week_name()}) (Tot giorni sim: {self.total_days_sim})")

                if self.current_day_in_month_idx >= settings.DXM: # Se i giorni superano il massimo per mese (24)
                    self.current_day_in_month_idx = 0
                    self.current_month_idx += 1
                    if settings.DEBUG_MODE:
                        print(f"      [TimeManager] NUOVO MESE: {settings.MONTH_NAMES[self.current_month_idx]}!")
                    
                    if self.current_month_idx >= settings.MXY: # Se i mesi superano il massimo per anno (18)
                        self.current_month_idx = 0
                        self.current_year += 1
                        if settings.DEBUG_MODE:
                            print(f"        [TimeManager] NUOVO ANNO: {self.current_year}!!!")
        # Fine logica di rollover

    # --- Metodi Getter ---
    def get_current_tick(self) -> int:
        return self.total_ticks_sim

    def get_current_minute(self) -> int:
        return self.current_minute

    def get_current_hour(self) -> int:
        return self.current_hour

    def get_current_day_of_month(self) -> int: # Restituisce giorno 1-24
        return self.current_day_in_month_idx + 1

    def get_current_month_index(self) -> int: # Restituisce indice 0-17
        return self.current_month_idx

    def get_current_month_name(self) -> str:
        try:
            return settings.MONTH_NAMES[self.current_month_idx]
        except IndexError:
            return "Mese Sconosciuto" # Fallback

    def get_current_year(self) -> int:
        return self.current_year

    def get_current_day_of_week_index(self) -> int: # 0 per Nijahr, ..., 6 per Ĝejahr
        # Assumiamo che il giorno 0 della simulazione (total_days_sim = 0) sia Nijahr (indice 0).
        return self.total_days_sim % settings.DXW

    def get_current_day_of_week_name(self) -> str:
        try:
            return settings.DAY_NAMES[self.get_current_day_of_week_index()]
        except IndexError:
            return "Giorno Sconosciuto" # Fallback

    def get_total_days_sim_passed(self) -> int:
        """Restituisce il numero totale di giorni passati dall'inizio della simulazione."""
        return self.total_days_sim
        
    def get_formatted_datetime_string(self, date_format: Optional[str] = None) -> str:
        """
        Restituisce la data e l'ora correnti formattate come stringa.
        TODO: Implementare una formattazione flessibile basata su date_format.
        Per ora, usa una formattazione standard.
        """
        # Esempio di formattazione (da migliorare per usare settings.ATH_DATE_FORMAT)
        return (f"Anno {self.current_year}, {self.get_current_month_name()} "
                f"Giorno {self.get_current_day_of_month()} ({self.get_current_day_of_week_name()}), "
                f"Ore {self.current_hour:02d}:{self.current_minute:02d}")

    def is_weekend(self) -> bool:
        """Controlla se il giorno corrente è un weekend, basandosi su settings.WEEKEND_DAY_NUMBERS."""
        return self.get_current_day_of_week_index() in settings.WEEKEND_DAY_NUMBERS

    # TODO: is_work_day(self), is_school_day(self) (considerando festività, calendari specifici)

# --- Blocco di Test per time_manager.py ---
if __name__ == '__main__':
    print("--- Test diretto di core/modules/time_manager.py ---")
    # Setup sys.path (come negli altri test)
    import sys, os
    _current_dir = os.path.dirname(os.path.abspath(__file__))
    _core_dir = os.path.dirname(_current_dir)
    _project_root = os.path.dirname(_core_dir)
    if _project_root not in sys.path: sys.path.insert(0, _project_root)

    try:
        from core import settings # Importa il vero settings
        settings.DEBUG_MODE = True # Attiva i log per questo test
        # Assicurati che le costanti temporali siano definite in settings
        if not all(hasattr(settings, c) for c in ["RY", "HXD", "DXM", "MXY", "DXW", "IXH", "MONTH_NAMES", "DAY_NAMES", "WEEKEND_DAY_NUMBERS", "ATH_DATE_FORMAT", "SIMULATION_TICKS_PER_HOUR"]):
            print("WARN: Alcune costanti temporali mancano in settings.py! Uso mock.")
            raise ImportError("Costanti settings mancanti per il test di TimeManager")
    except ImportError:
        class MockSettingsTM: # Mock ultra-semplificato
            RY = 5775; HXD = 28; DXM = 24; MXY = 18; DXW = 7; IXH = 60
            MONTH_NAMES = [f"MTest{i+1}" for i in range(18)]; DAY_NAMES = [f"GTest{i}" for i in range(7)]
            WEEKEND_DAY_NUMBERS = [0, 6]; ATH_DATE_FORMAT = ""; DEBUG_MODE = True
            SIMULATION_TICKS_PER_HOUR = 60 # Necessaria se TimeManager la usa
        settings = MockSettingsTM()
        print("  [Test TimeManager] WARN: Usato MockSettingsTM.")

    # Test con ora di inizio specifica per vedere il rollover
    tm = TimeManager(start_year=settings.RY, start_month_idx=0, start_day_idx=0, start_hour=27, start_minute=58)
    print(f"\nOra Iniziale: {tm.get_formatted_datetime_string()}")
    print(f"Giorno settimana idx: {tm.get_current_day_of_week_index()}, Nome: {tm.get_current_day_of_week_name()}")
    print(f"Weekend? {tm.is_weekend()}")

    print("\nAvanzamento di 5 tick (5 minuti):")
    for i in range(5):
        tm.advance_tick()
        print(f"Tick {tm.total_ticks_sim}: {tm.get_formatted_datetime_string()} ({tm.get_current_day_of_week_name()})")

    print(f"\nTotale giorni passati: {tm.get_total_days_sim_passed()}")

    print("\nAvanzamento per far scattare un nuovo anno (molti tick):")
    # Avanziamo di (GiorniInUnAnno * OreAlGiorno * MinutiPerOra) + qualche minuto
    ticks_per_year = settings.DXY * settings.HXD * settings.IXH # DXY non è in settings, ma MXY*DXM
    ticks_per_year_calc = settings.MXY * settings.DXM * settings.HXD * settings.IXH
    
    print(f"Tick per passare all'anno successivo (circa): {ticks_per_year_calc - tm.total_ticks_sim % ticks_per_year_calc + 5}")
    # Per semplicità, avanziamo di un numero fisso di tick che copra più di un anno
    # (Es. 2 anni = 2 * 432 giorni * 28 ore * 60 minuti)
    ticks_for_2_years = 2 * (settings.MXY * settings.DXM * settings.HXD * settings.IXH)
    #current_total_ticks = tm.total_ticks_sim
    #for i in range(ticks_for_2_years - current_total_ticks + 5):
    #    tm.advance_tick()
    # Semplifichiamo il test di rollover anno per ora, facendolo manualmente per un giorno.
    # Per testare il rollover dell'anno, dovremmo far avanzare molti più tick.
    # Facciamo avanzare fino alla fine del mese corrente
    current_day_idx = tm.current_day_in_month_idx
    current_month_idx = tm.current_month_idx
    print(f"Avanzo fino alla fine del mese {settings.MONTH_NAMES[current_month_idx]}...")
    while tm.current_month_idx == current_month_idx:
        prev_day = tm.current_day_in_month_idx
        tm.advance_tick()
        if tm.current_day_in_month_idx != prev_day and settings.DEBUG_MODE:
             print(f"Tick {tm.total_ticks_sim}: {tm.get_formatted_datetime_string()}")

    print(f"\nData dopo aver fatto scattare il mese: {tm.get_formatted_datetime_string()}")
    print(f"Totale giorni passati: {tm.get_total_days_sim_passed()}")
    print(f"Giorno settimana: {tm.get_current_day_of_week_name()}")

    print("\n--- Fine test diretto di core/modules/time_manager.py ---")