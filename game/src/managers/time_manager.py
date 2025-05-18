# game/src/managers/time_manager.py
import pygame # Non strettamente necessario qui, ma spesso i manager interagiscono con Pygame
import math
import os # Usato se config.ICON_PATH viene costruito con os.path.join
import logging # Aggiunto per il logging
from typing import Optional, Tuple, List, Dict, Any # Tipizzazioni

# Importa dal package 'game'
from game import config

logger = logging.getLogger(__name__) # Logger specifico per questo modulo
DEBUG_TIME = getattr(config, 'DEBUG_AI_ACTIVE', False) # Puoi usare un flag di debug specifico per il tempo se preferisci

class GameTimeManager:
    def __init__(self,
                 game_hours_in_day: int = config.GAME_HOURS_IN_DAY,
                 sky_keyframes: List[Tuple[float, Tuple[int, int, int]]] = config.SKY_KEYFRAMES,
                 time_speeds: Optional[Dict[int, float]] = None, # Ora è secondi reali per ora di gioco
                 initial_hour: float = config.INITIAL_START_HOUR,
                 initial_day: int = 1,
                 initial_month: int = 1,
                 initial_year: int = 1,
                 default_speed_index: int = getattr(config, 'TIME_SPEED_NORMAL_INDEX', 1)
                 ):

        self.game_hours_in_day: int = game_hours_in_day
        self.seconds_in_game_hour: int = 3600  # Secondi di gioco in un'ora di gioco
        # self.seconds_in_day: int = self.game_hours_in_day * self.seconds_in_game_hour # Non usato direttamente

        self.sky_keyframes: List[Tuple[float, Tuple[int, int, int]]] = sorted(sky_keyframes) # Assicura ordine per ora
        
        # time_speeds ora mappa l'indice di velocità a un dizionario con "multiplier" e "name"
        self.time_speeds: Dict[int, Dict[str, Any]] = {}
        cfg_time_speeds_input = time_speeds if time_speeds is not None else config.TIME_SPEED_SETTINGS
        
        for speed_idx, real_seconds_per_game_hour in cfg_time_speeds_input.items():
            multiplier = 0.0
            name = f"Speed {speed_idx}" # Nome di fallback
            if speed_idx == 0 or real_seconds_per_game_hour == float('inf'):
                multiplier = 0.0 # Pausa
                name = "Pause" if speed_idx == 0 else f"Speed {speed_idx} (Paused)"
            elif real_seconds_per_game_hour > 0:
                # Moltiplicatore = (secondi di gioco in un'ora di gioco) / (secondi reali per far passare un'ora di gioco)
                multiplier = self.seconds_in_game_hour / real_seconds_per_game_hour
                name = f"{multiplier:.0f}x" if multiplier >=1 else f"1/{1/multiplier:.0f}x (Slow)"
            
            self.time_speeds[speed_idx] = {"multiplier": multiplier, "name": name, "real_secs_per_game_hour": real_seconds_per_game_hour}

        self.default_speed_index: int = default_speed_index
        if self.default_speed_index not in self.time_speeds:
            logger.warning(f"Indice di velocità di default {self.default_speed_index} non trovato. Uso l'indice 1.")
            self.default_speed_index = 1 
            if 1 not in self.time_speeds: # Fallback estremo
                 self.time_speeds[1] = {"multiplier": 15.0, "name": "15x (Fallback)", "real_secs_per_game_hour": 240.0}


        # Stato attuale del tempo
        self.total_game_seconds_elapsed: float = 0.0 # Secondi TOTALI di GIOCO trascorsi dall'epoca (01/01/Y1 00:00)
        
        self.year: int = initial_year
        self.month: int = initial_month
        self.day: int = initial_day
        self.hour: int = math.floor(initial_hour) # Ora intera (0-27)
        self.minute: int = math.floor((initial_hour % 1) * 60) # Minuto (0-59)
        
        self.current_period_name: str = "" # Es. "Mattina", "Notte"
        self.current_sky_color: Tuple[int, int, int] = self.sky_keyframes[0][1] # Colore cielo attuale
        self.ui_text_color: Tuple[int, int, int] = getattr(config, 'TEXT_COLOR_DARK', (0,0,0)) # Colore testo UI

        self.reset_time_to_initial(initial_hour, initial_day, initial_month, initial_year)
        self.update_time_display_elements(0.0) # Chiamata iniziale per impostare periodo, colore cielo e testo UI

        if DEBUG_TIME:
            logger.debug(f"GameTimeManager Initialized. Start: Y{self.year}-M{self.month}-D{self.day} H{self.hour:02d}:{self.minute:02d}")
            logger.debug(f"Calculated speed settings: {self.time_speeds}")

    def reset_time_to_initial(self, initial_hour_float: float, 
                              initial_day: int, initial_month: int, initial_year: int):
        """Resetta il tempo ai valori iniziali specificati."""
        self.year = initial_year
        self.month = initial_month
        self.day = initial_day
        
        self.hour = math.floor(initial_hour_float)
        self.minute = math.floor((initial_hour_float % 1) * 60)
        
        # Calcola total_game_seconds_elapsed basandosi sulla data/ora iniziale rispetto all'epoca Y1/M1/D1 H0
        days_from_epoch = (self.year - 1) * config.GAME_DAYS_PER_YEAR + \
                          (self.month - 1) * config.DAYS_PER_MONTH + \
                          (self.day - 1)
        hours_from_epoch_start_of_day = self.hour + (self.minute / 60.0)
        
        self.total_game_seconds_elapsed = (days_from_epoch * self.game_hours_in_day * self.seconds_in_game_hour) + \
                                          (hours_from_epoch_start_of_day * self.seconds_in_game_hour)
        
        if DEBUG_TIME:
            logger.debug(f"Time reset. New total_game_seconds_elapsed: {self.total_game_seconds_elapsed:.2f}")
        self.update_time_display_elements(0.0) # Aggiorna tutti gli elementi derivati dal tempo

    def update_time(self, game_seconds_advanced_this_tick: float):
        """
        Aggiorna il tempo di gioco basato sui secondi di GIOCO avanzati in questo tick.
        Questo metodo viene chiamato da game_loop_updater.
        """
        if game_seconds_advanced_this_tick < 0: # Non dovrebbe accadere
            logger.warning("update_time chiamato con game_seconds_advanced_this_tick negativo.")
            return

        self.total_game_seconds_elapsed += game_seconds_advanced_this_tick
        
        # Calcola la nuova data e ora dal totale dei secondi di gioco trascorsi
        current_total_game_hours_float = self.total_game_seconds_elapsed / self.seconds_in_game_hour
        
        total_game_days_from_epoch = math.floor(current_total_game_hours_float / self.game_hours_in_day)
        
        self.year = 1 + math.floor(total_game_days_from_epoch / config.GAME_DAYS_PER_YEAR)
        days_into_current_year = total_game_days_from_epoch % config.GAME_DAYS_PER_YEAR
        
        self.month = 1 + math.floor(days_into_current_year / config.DAYS_PER_MONTH)
        self.day = 1 + (days_into_current_year % config.DAYS_PER_MONTH)
        
        hour_float_in_day = current_total_game_hours_float % self.game_hours_in_day
        self.hour = math.floor(hour_float_in_day)
        self.minute = math.floor((hour_float_in_day % 1) * 60)
        
        # Aggiorna anche gli elementi dipendenti come nome del periodo e colori
        # dt_real_seconds non è direttamente disponibile qui, ma update_sky_color ora
        # si basa principalmente sull'ora corrente per il colore base.
        # La fluidità della transizione del colore del cielo è meglio gestirla con un dt reale,
        # ma il colore del testo UI può essere aggiornato qui.
        self.update_time_display_elements(0.0) # Passiamo 0.0 per dt se non lo usiamo per interpolazione qui

    def update_time_display_elements(self, dt_real_seconds_for_interpolation: float):
        """Aggiorna il nome del periodo, il colore del cielo e il colore del testo UI."""
        current_hour_float = self.get_hour_float()
        
        # Determina il periodo del giorno
        period_found = False
        for i in range(len(config.PERIOD_DEFINITIONS)):
            start_hour, period_name, _icon_name = config.PERIOD_DEFINITIONS[i]
            # Determina l'ora di fine del periodo corrente
            next_start_hour = config.PERIOD_DEFINITIONS[i+1][0] if (i+1) < len(config.PERIOD_DEFINITIONS) else self.game_hours_in_day
            
            if start_hour <= current_hour_float < next_start_hour:
                self.current_period_name = period_name
                period_found = True
                break
        if not period_found: # Fallback se l'ora è esattamente game_hours_in_day o un po' oltre per errori di float
             self.current_period_name = config.PERIOD_DEFINITIONS[-1][1] 

        # Aggiorna colore cielo e testo UI
        self._update_sky_and_ui_text_color(current_hour_float)


    def get_hour_float(self) -> float:
        """Restituisce l'ora corrente come float (es. 7.5 per le 7:30)."""
        return self.hour + (self.minute / 60.0)

    def _interpolate_color(self, color1: Tuple[int,int,int], color2: Tuple[int,int,int], factor: float) -> Tuple[int,int,int]:
        """Helper per interpolare linearmente tra due colori RGB."""
        factor = max(0.0, min(1.0, factor)) # Clamp factor
        r = int(color1[0] * (1.0 - factor) + color2[0] * factor)
        g = int(color1[1] * (1.0 - factor) + color2[1] * factor)
        b = int(color1[2] * (1.0 - factor) + color2[2] * factor)
        return (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))

    def _update_sky_and_ui_text_color(self, current_hour_float: float):
        """Aggiorna self.current_sky_color e self.ui_text_color."""
        keyframe1 = self.sky_keyframes[0]
        keyframe2 = self.sky_keyframes[-1] # Default all'ultimo

        for i in range(len(self.sky_keyframes) - 1):
            h1_kf, _ = self.sky_keyframes[i]
            h2_kf, _ = self.sky_keyframes[i+1]
            if h1_kf <= current_hour_float < h2_kf:
                keyframe1 = self.sky_keyframes[i]
                keyframe2 = self.sky_keyframes[i+1]
                break
            # Gestione del loop dalla fine della giornata all'inizio della successiva
            if i == len(self.sky_keyframes) - 2 and current_hour_float >= h2_kf: # Se siamo nell'ultimo intervallo o oltre
                keyframe1 = self.sky_keyframes[i+1] # L'ultimo keyframe
                keyframe2 = self.sky_keyframes[0]   # Il primo keyframe (inizio del giorno)
                # Aggiusta l'ora del secondo keyframe se si passa alla "mezzanotte" per l'interpolazione
                if keyframe2[0] < keyframe1[0]: # Es. keyframe1 è 25:00, keyframe2 è 00:00 (diventa 28:00)
                    keyframe2 = (keyframe2[0] + self.game_hours_in_day, keyframe2[1])
                break
        
        hour1, color1 = keyframe1
        hour2, color2 = keyframe2
        
        t = 0.0
        if hour2 - hour1 != 0: # Evita divisione per zero
            t = (current_hour_float - hour1) / (hour2 - hour1)
        t = max(0.0, min(t, 1.0))
        
        self.current_sky_color = self._interpolate_color(color1, color2, t)
        
        # Calcola e imposta il colore del testo UI
        brightness = (self.current_sky_color[0] * 0.299 + 
                      self.current_sky_color[1] * 0.587 + 
                      self.current_sky_color[2] * 0.114)
        
        # Soglia di luminosità (aggiustabile)
        brightness_threshold = getattr(config, 'UI_TEXT_BRIGHTNESS_THRESHOLD', 140) 
        if brightness > brightness_threshold:
            self.ui_text_color = getattr(config, 'TEXT_COLOR_DARK', (30,30,50))
        else:
            self.ui_text_color = getattr(config, 'TEXT_COLOR_LIGHT', (220,220,220))

        # Aggiorna current_sky_color_index (usato per il salvataggio/caricamento dello stato del cielo)
        self.current_sky_color_index = 0
        for i, (hour_kf, _) in enumerate(self.sky_keyframes):
            if current_hour_float >= hour_kf:
                self.current_sky_color_index = i
            else:
                break # Trovato l'intervallo corretto

    def get_time_display_text(self) -> str:
        """Restituisce una stringa formattata per la visualizzazione del tempo."""
        return f"Y{self.year}-M{self.month}-D{self.day}, {self.hour:02d}:{self.minute:02d} ({self.current_period_name})"

    def get_period_icon_name(self) -> Optional[str]:
        """Restituisce il nome del file dell'icona per il periodo corrente."""
        current_hour_float = self.get_hour_float()
        for start_hour, period_name, icon_name in config.PERIOD_DEFINITIONS:
            next_start_hour = self.game_hours_in_day
            # Trova l'indice del periodo corrente per determinare l'ora di fine
            current_period_idx = -1
            for i, p_def in enumerate(config.PERIOD_DEFINITIONS):
                if p_def[1] == self.current_period_name:
                    current_period_idx = i
                    break
            if current_period_idx != -1 and (current_period_idx + 1) < len(config.PERIOD_DEFINITIONS):
                 next_start_hour = config.PERIOD_DEFINITIONS[current_period_idx+1][0]

            if start_hour <= current_hour_float < next_start_hour and period_name == self.current_period_name:
                return icon_name # Es. "dawn.svg"
        return config.PERIOD_DEFINITIONS[-1][2] # Fallback all'icona dell'ultimo periodo

    def get_current_speed_multiplier(self, current_speed_idx: int) -> float:
        """Restituisce il moltiplicatore di velocità per l'indice dato."""
        return self.time_speeds.get(current_speed_idx, {"multiplier": 1.0})["multiplier"]

    def get_current_speed_name(self, current_speed_idx: int) -> str:
        """Restituisce il nome della velocità per l'indice dato."""
        return self.time_speeds.get(current_speed_idx, {"name": "Unknown"})["name"]

    def get_real_seconds_per_game_hour(self, current_speed_idx: int) -> float:
        """Restituisce i secondi reali necessari per far passare un'ora di gioco all'indice di velocità dato."""
        return self.time_speeds.get(current_speed_idx, {"real_secs_per_game_hour": float('inf')})["real_secs_per_game_hour"]

    def to_dict(self) -> Dict[str, Any]:
        """Serializza lo stato del time manager per il salvataggio."""
        return {
            "total_game_seconds_elapsed": self.total_game_seconds_elapsed,
            "year": self.year,
            "month": self.month,
            "day": self.day,
            "hour": self.hour, # Ora intera
            "minute": self.minute, # Minuto intero
            # current_sky_color_index è utile se vuoi un modo semplice per ripristinare il colore cielo
            # senza dover ricalcolare completamente l'interpolazione al caricamento.
            # Ma _update_sky_and_ui_text_color lo ricalcola comunque.
            # "current_sky_color_index": self.current_sky_color_index 
        }

    def from_dict(self, data: Dict[str, Any]):
        """Ripristina lo stato del time manager da dati caricati."""
        self.total_game_seconds_elapsed = data.get("total_game_seconds_elapsed", 0.0)
        
        # Ricalcola data e ora dal total_game_seconds_elapsed
        self.update_time(0) # Passa 0 per non avanzare ulteriormente il tempo, solo per ricalcolare

        # Anche se potremmo caricare anno/mese/giorno/ora/minuto direttamente,
        # ricalcolarli da total_game_seconds_elapsed assicura coerenza.
        # Se preferisci caricarli direttamente:
        # self.year = data.get("year", config.INITIAL_START_YEAR) # Assumi costanti iniziali in config
        # self.month = data.get("month", config.INITIAL_START_MONTH)
        # self.day = data.get("day", config.INITIAL_START_DAY)
        # self.hour = data.get("hour", math.floor(config.INITIAL_START_HOUR))
        # self.minute = data.get("minute", math.floor((config.INITIAL_START_HOUR % 1) * 60))

        # Assicura che periodo e colori siano aggiornati
        self.update_time_display_elements(0.0)
        if DEBUG_TIME:
            logger.debug(f"GameTimeManager stato ripristinato da dict. Ora: Y{self.year}-M{self.month}-D{self.day} H{self.hour:02d}:{self.minute:02d}")