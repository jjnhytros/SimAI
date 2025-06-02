# core/modules/time_manager.py
"""
Modulo TimeManager per la gestione del tempo di gioco, del calendario
e dei cicli temporali in SimAI.
Riferimento TODO: I.3, XXXII.8
"""
from core.world.ATHDateTime.ATHDateTime import ATHDateTime # Importa la classe concreta
# ATHDateTimeInterface potrebbe non essere necessaria qui se ATHDateTime la implementa
# from core.world.ATHDateTime.ATHDateTimeInterface import ATHDateTimeInterface

from typing import Optional # Per il type hinting
from core import settings     # Importiamo le costanti globali

class TimeManager:
    def __init__(self, 
                 start_year: int = settings.YEAR_REFERENCE,  # RY, Anno di riferimento da settings
                 start_month_num: int = 1, # Mese 1-based (es. 1 per Arejal)
                 start_day_num: int = 1,   # Giorno del mese 1-based
                 start_hour: int = 7,
                 start_minute: int = 0,
                 start_second: int = 0):
        """
        Inizializza il TimeManager usando ATHDateTime.
        L'ora di inizio di default è le 07:00:00 del primo giorno del primo mese dell'anno di riferimento.
        """
        if settings.DEBUG_MODE:
            print("  [TimeManager INIT] Inizializzazione TimeManager con ATHDateTime...")

        self.total_ticks_sim: int = 0
        # self.total_days_sim: int = 0 # Potremmo non averne più bisogno o calcolarlo diversamente

        # Crea la data/ora iniziale per ATHDateTime
        # Assumiamo che ATHDateTime possa essere inizializzato con questi componenti
        # o costruiamo una stringa ISO-like se necessario.
        # Dal codice di ATHDateTime, sembra che il costruttore prenda una stringa o un timestamp.
        # Costruiamo una stringa di data iniziale.
        initial_datetime_str = f"{start_year:04d}-{start_month_num:02d}-{start_day_num:02d}T{start_hour:02d}:{start_minute:02d}:{start_second:02d}"
        
        # Assumiamo che ATHDateTime carichi la sua configurazione di fuso orario internamente
        # o che tz_config=None sia accettabile per usare un default.
        self._sim_time: ATHDateTime = ATHDateTime(initial_datetime_str, tz_config=None) 
        
        # Memorizza la data di inizio della simulazione per calcolare total_days_sim se necessario
        self._simulation_start_ath_datetime: ATHDateTime = ATHDateTime(initial_datetime_str, tz_config=None)


        if settings.DEBUG_MODE:
            print(f"  [TimeManager INIT] Ora di inizio simulazione ATHDateTime: {self.get_formatted_datetime_string()}")
            print(f"  [TimeManager INIT] Costanti calendario usate (da settings, derivate da ATHDateTimeInterface):")
            print(f"    MINUTES_PER_HOUR: {settings.MINUTES_PER_HOUR}")
            print(f"    HOURS_PER_DAY: {settings.HOURS_PER_DAY}")
            print(f"    DAYS_PER_MONTH: {settings.DAYS_PER_MONTH}")
            print(f"    MONTHS_PER_YEAR: {settings.MONTHS_PER_YEAR}")
            print(f"    DAYS_PER_YEAR: {settings.DAYS_PER_YEAR}")
            print(f"    SECONDS_PER_MINUTE: {settings.SECONDS_PER_MINUTE}")


    def advance_tick(self):
        """
        Avanza il tempo di gioco di un singolo tick.
        1 tick = (SECONDS_PER_MINUTE / SIMULATION_TICKS_PER_MINUTE) secondi di gioco.
        Se SIMULATION_TICKS_PER_MINUTE è 1, allora 1 tick = 1 minuto di gioco.
        """
        self.total_ticks_sim += 1
        
        self._sim_time.add_seconds(settings.SECONDS_PER_SIMULATION_TICK)

        # Logica di stampa per nuova ora/giorno (opzionale, ATHDateTime ora gestisce il rollover)
        # Potremmo voler loggare solo quando l'ora o il giorno cambiano *effettivamente*
        # Questo richiede di confrontare con lo stato precedente o di usare i getter di _sim_time
        # per formattare un output solo quando necessario.
        # Per ora, la logica di debug print qui viene semplificata.
        if settings.DEBUG_MODE:
            if self._sim_time.get_minute() == 0 and self._sim_time.get_second() == 0: # Se è scattata una nuova ora
                 # Il log della GUI per SimTime in Simulation._update_simulation_state è già presente
                 pass # Non è necessario un print qui se Simulation lo fa
                 # print(f"    [TimeManager] Nuova ora: {self._sim_time.get_hour():02d}:00 (Tick: {self.total_ticks_sim})")
            # Potremmo aggiungere log per nuovo giorno/mese/anno se ATHDateTime non li fornisce o se vogliamo un formato specifico qui

    # --- Metodi Getter aggiornati per usare self._sim_time ---
    def get_current_tick(self) -> int:
        return self.total_ticks_sim

    def get_current_minute(self) -> int:
        return self._sim_time.get_minute()

    def get_current_hour(self) -> int:
        return self._sim_time.get_hour()

    def get_current_day_of_month(self) -> int: # ATHDateTime.get_day_of_month() è 1-based
        return self._sim_time.get_day_of_month()

    def get_current_month_index(self) -> int: # Per coerenza con l'uso di liste 0-based per nomi
        return self._sim_time.get_month_of_year() - 1 # ATHDateTime.get_month_of_year() è 1-based

    def get_current_month_name(self) -> str:
        return self._sim_time.get_month_name()

    def get_current_year(self) -> int:
        return self._sim_time.get_year()

    def get_current_day_of_week_index(self) -> int: # ATHDateTime.get_day_of_week_index() dovrebbe essere 0-based
        return self._sim_time.get_day_of_week_index() 

    def get_current_day_of_week_name(self) -> str:
        return self._sim_time.get_day_of_week_name()

    def get_total_days_sim_passed(self) -> int:
        """Restituisce il numero totale di giorni passati dall'inizio della simulazione."""
        # Calcola la differenza in giorni tra la data corrente e la data di inizio
        # Questo richiede che ATHDateTime supporti la sottrazione di date o il calcolo dei giorni totali
        # da un'epoca. Se ATHDateTime ha un metodo `diff_in_days(other_datetime)`, lo usiamo.
        # Altrimenti, questo contatore potrebbe dover essere gestito manualmente come prima
        # o calcolato in base al numero di tick e ai secondi/minuti/ore per giorno.
        
        # Metodo 1: Basato sui tick (più semplice se ATHDateTime.diff non è immediato)
        # return self.total_ticks_sim // (settings.SIMULATION_TICKS_PER_HOUR * settings.HOURS_PER_DAY)
        
        # Metodo 2: Usando ATHDateTime (se implementato)
        # return self._sim_time.diff(self._simulation_start_ath_datetime).days 
        # Per ora, manteniamo il calcolo basato sui tick se diff non è semplice
        
        # Calcolo semplificato basato su total_ticks_sim, minuti per ora e ore per giorno
        ticks_per_day = settings.MINUTES_PER_HOUR * settings.HOURS_PER_DAY * settings.SIMULATION_TICKS_PER_MINUTE
        if ticks_per_day > 0:
            return self.total_ticks_sim // ticks_per_day
        return 0


    def get_formatted_datetime_string(self) -> str:
        """Restituisce la data e l'ora correnti formattate usando ATHDateTime."""
        return self._sim_time.get_datetime_str() # ATHDateTime ha questo metodo

    def get_ath_detailed_datetime(self) -> dict:
        """
        Restituisce un dizionario con i componenti della data e ora
        per una formattazione personalizzata nella GUI, usando l'istanza interna _sim_time.
        """
        return {
            "year": self._sim_time.get_year(),
            "day_of_month": self._sim_time.get_day_of_month(),    # 1-based
            "month_of_year": self._sim_time.get_month_of_year(), # 1-based
            "hour": self._sim_time.get_hour(),
            "minute": self._sim_time.get_minute(),
            "second": self._sim_time.get_second(),
            "day_name": self._sim_time.get_day_of_week_name()
        }

    def is_weekend(self) -> bool:
        """Controlla se il giorno corrente è un weekend."""
        # ATHDateTime potrebbe avere un suo metodo is_weekend() che usa la sua configurazione interna
        # Se sì, preferisci self._sim_time.is_weekend()
        # Altrimenti, mantieni la logica basata su settings.WEEKEND_DAY_NUMBERS
        if hasattr(self._sim_time, 'is_weekend'):
            return self._sim_time.is_weekend()
        return self.get_current_day_of_week_index() in settings.WEEKEND_DAY_NUMBERS

    # TODO: Rivedere is_work_day, is_school_day per usare self._sim_time e ATHDateTime
    #       per controlli più robusti su orari e giorni specifici, considerando festività
    #       che potrebbero essere gestite da ATHDateTime o da un CalendarSystem.

# --- Blocco di Test (da adattare) ---
if __name__ == '__main__':
    # ... (Il blocco di test andrà adattato per istanziare ATHDateTime correttamente
    #      e per verificare i nuovi metodi basati su _sim_time.
    #      Le costanti temporali dovrebbero ora provenire da settings.MINUTES_PER_HOUR etc.
    #      che a loro volta derivano da ATHDateTimeInterface) ...
    print("--- Test diretto di core/modules/time_manager.py (adattato per ATHDateTime) ---")
    # ... (setup sys.path) ...
    # ... (import e mock di settings se necessario) ...
    # settings.RY ora si chiama settings.YEAR_REFERENCE
    tm = TimeManager(start_year=settings.RY, start_month_num=1, start_day_num=1, start_hour=27, start_minute=58)
    # ... (il resto del test) ...
