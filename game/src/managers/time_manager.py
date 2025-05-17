# /home/nhytros/work/clair/simai/game/src/managers/time_manager.py
import pygame # Per pygame.time.get_ticks() se necessario per delta reali
import math
from typing import Optional, Tuple, List, Dict # Aggiungi per type hints

# Importa config per accedere alle costanti temporali
# Dato che time_manager.py è in game/src/managers/, e config.py è in game/,
# l'import corretto quando si esegue con 'python -m game.main' da 'simai/' è:
from game import config

class GameTimeManager:
    def __init__(self, 
                 game_hours_in_day: int = config.GAME_HOURS_IN_DAY, 
                 sky_keyframes: List[Tuple[float, Tuple[int, int, int]]] = config.SKY_KEYFRAMES,
                 time_speeds: Dict[int, Dict[str, Any]] = None, # Sarà preso da config se None
                 initial_hour: float = config.INITIAL_START_HOUR,
                 initial_day: int = 1,
                 initial_month: int = 1,
                 initial_year: int = 1,
                 default_speed_index: int = 1): # Velocità normale di default

        self.game_hours_in_day = game_hours_in_day
        self.seconds_in_game_hour = 3600  # Standard, ma potrebbe essere configurabile se un'ora di gioco != un'ora reale
        self.seconds_in_day = self.game_hours_in_day * self.seconds_in_game_hour

        self.sky_keyframes = sorted(sky_keyframes) # Assicura che siano ordinati per ora
        
        # TIME_SPEED_SETTINGS è una dict di dicts nel tuo config.py
        # { index: {"multiplier": X, "delta_override": Y, "name": Z}, ... }
        # Se il tuo config.TIME_SPEED_SETTINGS è {index: float_multiplier}, adattalo.
        # Assumiamo la struttura più semplice che avevi in config.py {index: real_seconds_per_game_hour}
        # e la convertiamo in moltiplicatori.
        
        self.time_speeds = {}
        # Il tuo config.TIME_SPEED_SETTINGS è {0: inf, 1: 240, ...} secondi reali per ora di GIOCO
        # Dobbiamo convertirlo in moltiplicatori di velocità rispetto al tempo reale.
        # Un'ora di gioco (3600 secondi di gioco) divisa per i secondi reali che ci vogliono per passarli.
        # Moltiplicatore = secondi_gioco_in_un_ora_gioco / secondi_reali_per_un_ora_gioco
        # Se TIME_SPEED_SETTINGS[1] = 240, significa che 3600 secondi di gioco passano in 240 secondi reali.
        # Moltiplicatore = 3600 / 240 = 15x. Cioè il tempo di gioco scorre 15 volte più veloce del reale.
        
        cfg_time_speeds = time_speeds if time_speeds is not None else config.TIME_SPEED_SETTINGS
        for speed_idx, real_seconds_per_game_hour in cfg_time_speeds.items():
            if speed_idx == 0: # Pausa
                multiplier = 0.0
                name = "Pause"
            elif real_seconds_per_game_hour == float('inf'): # Tecnicamente pausa, ma gestito come idx 0
                 multiplier = 0.0
                 name = f"Speed {speed_idx} (Paused)"
            else:
                multiplier = self.seconds_in_game_hour / real_seconds_per_game_hour
                name = f"{multiplier:.0f}x" if multiplier >=1 else f"1/{1/multiplier:.0f}x"

            self.time_speeds[speed_idx] = {
                "multiplier": multiplier, 
                "name": name, # Nome per la UI
                # "delta_override": None # Potresti usare questo per velocità fisse
            }
        
        self.default_speed_index = default_speed_index
        if self.default_speed_index not in self.time_speeds:
            self.default_speed_index = 1 # Fallback sicuro

        # Stato attuale del tempo
        self.total_game_seconds_elapsed: float = 0.0 # Secondi di gioco totali trascorsi dall'inizio
        self.year: int = initial_year
        self.month: int = initial_month
        self.day: int = initial_day
        self.hour: int = math.floor(initial_hour)
        self.minute: int = math.floor((initial_hour % 1) * 60)
        
        self.current_period_name: str = ""
        self.current_sky_color: Tuple[int, int, int] = self.sky_keyframes[0][1] # Colore iniziale
        self.current_sky_color_index: int = 0 # Per transizioni
        self.time_since_last_sky_update: float = 0.0

        self.reset_time_to_initial(initial_hour, initial_day, initial_month, initial_year)
        self.update_time(0) # Per inizializzare periodo e colore cielo

        if getattr(config, 'DEBUG_AI_ACTIVE', False):
            print(f"TIME_MANAGER: Initialized. Start: Y{self.year}-M{self.month}-D{self.day} H{self.hour:02d}:{self.minute:02d}")
            # print(f"TIME_MANAGER: Calculated speed multipliers: {self.time_speeds}")

    def reset_time_to_initial(self, initial_hour_float, initial_day, initial_month, initial_year):
        self.year = initial_year
        self.month = initial_month
        self.day = initial_day
        
        self.hour = math.floor(initial_hour_float)
        self.minute = math.floor((initial_hour_float % 1) * 60)
        
        # Calcola total_game_seconds_elapsed basandosi sulla data/ora iniziale
        # Questo è un calcolo approssimativo se non parti dall'anno 1, mese 1, giorno 1, ora 0
        # Per semplicità, lo resettiamo a zero se l'ora è quella iniziale del giorno.
        # Una logica più precisa richiederebbe di contare i giorni/mesi/anni passati.
        if self.day == 1 and self.month == 1 and self.year == 1 and self.hour == math.floor(config.INITIAL_START_HOUR):
            self.total_game_seconds_elapsed = (initial_hour_float - math.floor(config.INITIAL_START_HOUR)) * self.seconds_in_game_hour
        else:
            # Stima approssimativa (o dovresti avere un modo per salvare/caricare il total_game_seconds corretto)
            days_elapsed_approx = (self.year -1) * config.GAME_DAYS_PER_YEAR + \
                                  (self.month -1) * config.DAYS_PER_MONTH + \
                                  (self.day -1)
            self.total_game_seconds_elapsed = (days_elapsed_approx * self.game_hours_in_day * self.seconds_in_game_hour) + \
                                              (initial_hour_float * self.seconds_in_game_hour)
        
        self.update_time_representation()


    def update_time(self, dt_simulated_seconds: float):
        """Aggiorna il tempo di gioco basato sul delta time simulato (reale * moltiplicatore)."""
        if dt_simulated_seconds == 0: # Se il gioco è in pausa o velocità è 0
            self.update_time_representation() # Aggiorna comunque la rappresentazione (es. periodo)
            # Non aggiornare sky color se il tempo non passa, per evitare che cambi in pausa
            return

        self.total_game_seconds_elapsed += dt_simulated_seconds
        
        # Calcola la nuova data e ora
        current_total_hours = self.total_game_seconds_elapsed / self.seconds_in_game_hour
        
        self.hour = math.floor(current_total_hours % self.game_hours_in_day)
        self.minute = math.floor((current_total_hours * 60) % 60)
        
        total_game_days_elapsed = math.floor(current_total_hours / self.game_hours_in_day)
        
        # Calcolo anno, mese, giorno
        # Inizia dal giorno/mese/anno 1
        current_year_calc = 1 + math.floor(total_game_days_elapsed / config.GAME_DAYS_PER_YEAR)
        days_into_year = total_game_days_elapsed % config.GAME_DAYS_PER_YEAR
        
        current_month_calc = 1 + math.floor(days_into_year / config.DAYS_PER_MONTH)
        current_day_calc = 1 + (days_into_year % config.DAYS_PER_MONTH)
        
        self.year = current_year_calc
        self.month = current_month_calc
        self.day = current_day_calc
        
        self.update_time_representation()

    def update_time_representation(self):
        """Aggiorna il nome del periodo del giorno."""
        current_hour_float = self.get_hour_float()
        # Determina il periodo del giorno (usa config.PERIOD_DEFINITIONS)
        # Assumendo che config.PERIOD_DEFINITIONS sia una lista di tuple:
        # [(hour_start, name, icon_name), ...] ordinata per hour_start
        period_found = False
        for i in range(len(config.PERIOD_DEFINITIONS)):
            start_hour, period_name, _ = config.PERIOD_DEFINITIONS[i]
            next_start_hour = config.PERIOD_DEFINITIONS[i+1][0] if (i+1) < len(config.PERIOD_DEFINITIONS) else self.game_hours_in_day
            if start_hour <= current_hour_float < next_start_hour:
                self.current_period_name = period_name
                period_found = True
                break
        if not period_found: # Fallback se qualcosa va storto (es. ora fuori range)
             self.current_period_name = config.PERIOD_DEFINITIONS[-1][1] # Ultimo periodo

    def get_hour_float(self) -> float:
        """Restituisce l'ora corrente come float (es. 7.5 per le 7:30)."""
        return self.hour + (self.minute / 60.0)

    def update_sky_color(self, dt_real_seconds: float):
        """Aggiorna il colore del cielo con transizione graduale."""
        current_hour_float = self.get_hour_float()
        
        # Trova i due keyframe tra cui interpolare
        keyframe1 = self.sky_keyframes[0]
        keyframe2 = self.sky_keyframes[-1] # Default all'ultimo se non ne trova altri

        for i in range(len(self.sky_keyframes) -1):
            if self.sky_keyframes[i][0] <= current_hour_float < self.sky_keyframes[i+1][0]:
                keyframe1 = self.sky_keyframes[i]
                keyframe2 = self.sky_keyframes[i+1]
                break
            # Gestisci il caso in cui l'ora sia esattamente l'ultima keyframe o oltre (loop al primo)
            if i == len(self.sky_keyframes) - 2 and current_hour_float >= self.sky_keyframes[i+1][0]:
                keyframe1 = self.sky_keyframes[i+1]
                keyframe2 = self.sky_keyframes[0] # Loopa al primo colore (DEEP_NIGHT)
                # Aggiusta le ore per il calcolo del lerp se si fa il loop
                if keyframe2[0] < keyframe1[0]: # Indica che siamo passati alla "mezzanotte" del giorno dopo
                    keyframe2 = (keyframe2[0] + self.game_hours_in_day, keyframe2[1])
                break


        hour1, color1 = keyframe1
        hour2, color2 = keyframe2
        
        # Calcola il fattore di interpolazione (t)
        if hour2 == hour1: # Evita divisione per zero se i keyframe sono identici o si sovrappongono perfettamente
            t = 0.0
        else:
            t = (current_hour_float - hour1) / (hour2 - hour1)
        t = max(0.0, min(t, 1.0)) # Clamp t tra 0 e 1

        # Interpolazione lineare per ogni componente di colore
        r = int(color1[0] + (color2[0] - color1[0]) * t)
        g = int(color1[1] + (color2[1] - color1[1]) * t)
        b = int(color1[2] + (color2[2] - color1[2]) * t)
        
        self.current_sky_color = (r, g, b)
        
        # Per l'indice (non strettamente necessario se il colore è interpolato, ma può servire per UI)
        # Trova l'indice del keyframe più vicino o precedente
        self.current_sky_color_index = 0
        for i, (hour, _) in enumerate(self.sky_keyframes):
            if current_hour_float >= hour:
                self.current_sky_color_index = i
            else:
                break


    def get_time_display_text(self) -> str:
        """Restituisce una stringa formattata per la visualizzazione del tempo."""
        return f"Y{self.year}-M{self.month}-D{self.day}, {self.hour:02d}:{self.minute:02d} ({self.current_period_name})"

    def get_time_display_with_icon(self) -> Tuple[str, Optional[str]]:
        """Restituisce testo del tempo e percorso icona del periodo."""
        text = self.get_time_display_text()
        icon_path = None
        current_hour_float = self.get_hour_float()
        for start_hour, period_name, period_icon_name in config.PERIOD_DEFINITIONS:
            next_start_hour = self.game_hours_in_day # Default per l'ultimo periodo
            # Trova l'ora di inizio del periodo successivo per definire l'intervallo corrente
            current_period_index = -1
            for i, p_def in enumerate(config.PERIOD_DEFINITIONS):
                if p_def[1] == self.current_period_name:
                    current_period_index = i
                    break
            
            if current_period_index != -1 and (current_period_index + 1) < len(config.PERIOD_DEFINITIONS):
                next_start_hour = config.PERIOD_DEFINITIONS[current_period_index+1][0]

            if start_hour <= current_hour_float < next_start_hour and period_name == self.current_period_name:
                if period_icon_name:
                    icon_path = os.path.join(config.ICON_PATH, period_icon_name)
                break
        return text, icon_path

    def reset_time(self):
        """Resetta il tempo di gioco ai valori iniziali da config."""
        self.reset_time_to_initial(config.INITIAL_START_HOUR, 1, 1, 1)
        self.update_time(0) # Per aggiornare periodo e colore cielo

    # Potresti aggiungere un metodo per ottenere il moltiplicatore di velocità corrente se non è gestito altrove
    # def get_current_speed_multiplier(self, current_speed_index: int) -> float:
    #     return self.time_speeds.get(current_speed_index, {"multiplier": 1.0})["multiplier"]