# game/src/entities/components/career_component.py
import logging
import random
from typing import Dict, Any, Optional, List, Tuple, TYPE_CHECKING

# Importa dal package 'game'
from game import config

if TYPE_CHECKING:
    from game.src.entities.character import Character
    from game.src.modules.game_state_module import GameState # Per accedere a GameTimeManager

logger = logging.getLogger(__name__)
DEBUG_CAREER = getattr(config, 'DEBUG_AI_ACTIVE', False)

# Esempio di struttura dati per le carriere (potrebbe essere in config.py o un JSON dedicato)
# Chiave: nome_carriera
# Valori: lista di livelli, ogni livello è un dict con "title", "salary_per_hour", "work_hours" (start, end),
#         "work_days" (lista di int, 0=Lun, 6=Dom), "promotion_threshold" (performance)
#         "required_skills" (dict: skill_name -> level)
DEFAULT_CAREER_TRACKS = {
    "Unemployed": [{
        "title": "Disoccupato", "level": 0, "salary_per_hour": 0,
        "work_hours": None, "work_days": [], "promotion_threshold": None
    }],
    "Cuoco": [
        {"title": "Lavapiatti", "level": 1, "salary_per_hour": 8, "work_hours": (9, 17), "work_days": [0,1,2,3,4], "promotion_threshold": 70, "required_skills": {"cucina": 1}},
        {"title": "Aiuto Cuoco", "level": 2, "salary_per_hour": 12, "work_hours": (10, 18), "work_days": [0,1,2,3,4], "promotion_threshold": 85, "required_skills": {"cucina": 3}},
        {"title": "Cuoco", "level": 3, "salary_per_hour": 20, "work_hours": (11, 19), "work_days": [0,1,2,3,4], "promotion_threshold": None, "required_skills": {"cucina": 5}},
    ],
    "Programmatore": [
        {"title": "Stagista Programmatore", "level": 1, "salary_per_hour": 10, "work_hours": (9,17,30), "work_days": [0,1,2,3,4], "promotion_threshold": 75, "required_skills": {"logica": 2}},
        {"title": "Programmatore Junior", "level": 2, "salary_per_hour": 18, "work_hours": (9,17,30), "work_days": [0,1,2,3,4], "promotion_threshold": 90, "required_skills": {"logica": 4}},
        {"title": "Programmatore Senior", "level": 3, "salary_per_hour": 30, "work_hours": (10,18), "work_days": [0,1,2,3,4], "promotion_threshold": None, "required_skills": {"logica": 6}},
    ]
    # Aggiungi altre carriere
}


class CareerComponent:
    def __init__(self, character_owner: 'Character'):
        """
        Inizializza il componente della carriera.

        Args:
            character_owner (Character): Il personaggio a cui questo componente appartiene.
        """
        self.owner: 'Character' = character_owner
        self.owner_name: str = character_owner.name if character_owner else "NPC Sconosciuto"

        self.career_tracks_data: Dict[str, List[Dict[str, Any]]] = getattr(config, 'CAREER_DEFINITIONS', DEFAULT_CAREER_TRACKS)
        
        self.current_career_name: str = "Unemployed" # Nome della traccia di carriera
        self.current_job_level_index: int = 0 # Indice del livello corrente nella lista della carriera
        
        # Questi attributi vengono derivati dal livello corrente
        self.job_title: str = "Disoccupato"
        self.salary_per_hour: float = 0.0
        self.work_start_hour: Optional[float] = None # Ora di inizio lavoro (es. 9.0 per le 9:00)
        self.work_end_hour: Optional[float] = None   # Ora di fine lavoro (es. 17.5 per le 17:30)
        self.work_days: List[int] = [] # Lista di giorni della settimana (0=Lun, 1=Mar, ..., 6=Dom)
        self.required_skills_for_current_level: Dict[str, int] = {}

        self.performance_at_work: float = 50.0 # Da 0 a 100
        self.days_worked_consecutively: int = 0 # Per bonus/malus performance
        self.days_missed_work_consecutively: int = 0
        self.is_currently_at_work: bool = False # Se l'NPC è fisicamente "al lavoro" (potrebbe essere un rabbit hole)

        self._update_job_details_from_level() # Imposta i dettagli iniziali del lavoro

        if DEBUG_CAREER:
            logger.debug(f"CareerComponent per {self.owner_name} inizializzato. Lavoro: {self.job_title} (Livello {self.current_job_level_index})")

    def _update_job_details_from_level(self):
        """Aggiorna i dettagli del lavoro (titolo, stipendio, orari) in base al nome e al livello della carriera corrente."""
        if self.current_career_name in self.career_tracks_data and \
           0 <= self.current_job_level_index < len(self.career_tracks_data[self.current_career_name]):
            
            level_data = self.career_tracks_data[self.current_career_name][self.current_job_level_index]
            
            self.job_title = level_data.get("title", "Sconosciuto")
            self.salary_per_hour = float(level_data.get("salary_per_hour", 0.0))
            
            work_hours_tuple = level_data.get("work_hours") # Es. (9, 17) o (9, 17.5)
            if work_hours_tuple and len(work_hours_tuple) == 2:
                self.work_start_hour = float(work_hours_tuple[0])
                self.work_end_hour = float(work_hours_tuple[1])
            else:
                self.work_start_hour = None
                self.work_end_hour = None
                
            self.work_days = level_data.get("work_days", [])
            self.required_skills_for_current_level = level_data.get("required_skills", {})
            
            if DEBUG_CAREER:
                logger.debug(f"Career ({self.owner_name}): Dettagli lavoro aggiornati a '{self.job_title}'. Salario/ora: {self.salary_per_hour}. Orario: {self.work_start_hour}-{self.work_end_hour} su giorni {self.work_days}")
        else:
            # Fallback a disoccupato se la carriera/livello non sono validi
            self.current_career_name = "Unemployed"
            self.current_job_level_index = 0
            unemployed_data = self.career_tracks_data.get("Unemployed", [DEFAULT_CAREER_TRACKS["Unemployed"][0]])[0]
            self.job_title = unemployed_data.get("title", "Disoccupato")
            self.salary_per_hour = 0.0
            self.work_start_hour = None
            self.work_end_hour = None
            self.work_days = []
            self.required_skills_for_current_level = {}
            logger.warning(f"Career ({self.owner_name}): Carriera/livello non validi. Impostato a Disoccupato.")


    def set_career(self, career_name: str, level_index: int = 0) -> bool:
        """Imposta una nuova carriera e livello per l'NPC."""
        if career_name in self.career_tracks_data and \
           0 <= level_index < len(self.career_tracks_data[career_name]):
            self.current_career_name = career_name
            self.current_job_level_index = level_index
            self.performance_at_work = 50.0 # Resetta la performance con un nuovo lavoro/livello
            self.days_worked_consecutively = 0
            self.days_missed_work_consecutively = 0
            self._update_job_details_from_level()
            if DEBUG_CAREER:
                logger.info(f"Career ({self.owner_name}): Nuova carriera '{self.current_career_name}', Livello '{self.job_title}'.")
            return True
        else:
            logger.warning(f"Career ({self.owner_name}): Tentativo di impostare carriera non valida '{career_name}' o livello {level_index}.")
            return False

    def can_work_today(self, game_state: 'GameState') -> bool:
        """Verifica se oggi è un giorno lavorativo per l'NPC."""
        if not self.work_days or not game_state.game_time_handler:
            return False # Non ha un lavoro con giorni definiti o il time_manager non è disponibile
        
        # game_state.game_time_handler.day_of_week dovrebbe restituire 0 per Lun, ..., 6 per Dom
        # Se non hai day_of_week, puoi calcolarlo da total_days_elapsed % 7
        current_day_of_week = game_state.game_time_handler.get_day_of_week() # Assumendo che esista questo metodo
        return current_day_of_week in self.work_days

    def is_work_time(self, game_state: 'GameState') -> bool:
        """Verifica se è orario di lavoro per l'NPC."""
        if self.work_start_hour is None or self.work_end_hour is None or not game_state.game_time_handler:
            return False
        
        current_hour_float = game_state.game_time_handler.get_hour_float()
        return self.work_start_hour <= current_hour_float < self.work_end_hour

    def go_to_work(self):
        """Gestisce l'NPC che va al lavoro (potrebbe essere un rabbit hole)."""
        # Questa funzione verrebbe chiamata dall'IA (es. in idle.py)
        # quando è ora di andare al lavoro.
        if self.current_career_name == "Unemployed":
            return

        if DEBUG_CAREER:
            logger.info(f"Career ({self.owner_name}): {self.owner_name} sta 'andando al lavoro' ({self.job_title}).")
        self.is_currently_at_work = True
        # L'NPC potrebbe scomparire dalla mappa o andare in un lotto "lavoro" specifico.
        # Per ora, è solo un flag. L'IA non dovrebbe controllare altri bisogni mentre è a lavoro.

    def finish_work(self, hours_worked: float):
        """Gestisce il ritorno dal lavoro."""
        if not self.is_currently_at_work:
            return

        self.is_currently_at_work = False
        if DEBUG_CAREER:
            logger.info(f"Career ({self.owner_name}): {self.owner_name} ha finito di lavorare ({self.job_title}). Ore lavorate: {hours_worked:.2f}")

        # Calcola stipendio
        earned_this_shift = self.salary_per_hour * hours_worked
        if earned_this_shift > 0 and hasattr(self.owner, 'finances') and self.owner.finances:
            self.owner.finances.add_money(earned_this_shift, f"Stipendio: {self.job_title}")

        # Aggiorna performance (logica semplificata)
        performance_change = getattr(config, 'PERFORMANCE_CHANGE_PER_WORK_DAY', 5.0)
        # Potrebbe dipendere da umore, abilità, eventi casuali al lavoro
        # Esempio: if self.owner.mood.get_current_mood_value() < 0: performance_change /= 2
        self.performance_at_work += performance_change
        self.performance_at_work = max(0, min(100, self.performance_at_work)) # Clamp
        self.days_worked_consecutively += 1
        self.days_missed_work_consecutively = 0

        if DEBUG_CAREER:
            logger.debug(f"Career ({self.owner_name}): Performance aggiornata a {self.performance_at_work:.1f}/100.")
        
        self._check_for_promotion()

    def miss_work(self):
        """Gestisce un giorno di lavoro mancato."""
        if self.current_career_name == "Unemployed": return

        performance_penalty = getattr(config, 'PERFORMANCE_PENALTY_MISSED_WORK', -15.0)
        self.performance_at_work += performance_penalty
        self.performance_at_work = max(0, min(100, self.performance_at_work))
        self.days_worked_consecutively = 0
        self.days_missed_work_consecutively += 1
        if DEBUG_CAREER:
            logger.warning(f"Career ({self.owner_name}): {self.owner_name} ha saltato il lavoro! Performance: {self.performance_at_work:.1f}")
        
        # Potrebbe esserci un rischio di licenziamento dopo X giorni mancati
        if self.days_missed_work_consecutively >= getattr(config, 'DAYS_TO_GET_FIRED', 3):
            self.get_fired()

    def _check_for_promotion(self):
        """Controlla se l'NPC merita una promozione."""
        if self.current_career_name == "Unemployed" or not self.career_tracks_data[self.current_career_name]:
            return

        current_level_data = self.career_tracks_data[self.current_career_name][self.current_job_level_index]
        promotion_threshold = current_level_data.get("promotion_threshold")
        
        if promotion_threshold is None: # Ultimo livello della carriera
            return

        # Verifica se ha le abilità richieste per il prossimo livello (se definito)
        next_level_index = self.current_job_level_index + 1
        if next_level_index < len(self.career_tracks_data[self.current_career_name]):
            next_level_data = self.career_tracks_data[self.current_career_name][next_level_index]
            required_skills_next = next_level_data.get("required_skills", {})
            has_required_skills = True
            if hasattr(self.owner, 'skills') and self.owner.skills:
                for skill_name, req_level in required_skills_next.items():
                    if self.owner.skills.get_skill_level(skill_name) < req_level:
                        has_required_skills = False
                        break
            else: # Non ha un componente skill, non può verificare
                has_required_skills = not bool(required_skills_next) # Promuovi solo se non ci sono skill richieste

            if self.performance_at_work >= promotion_threshold and has_required_skills:
                self.current_job_level_index = next_level_index
                self._update_job_details_from_level()
                self.performance_at_work = 50.0 # Resetta performance al nuovo livello
                logger.info(f"Career ({self.owner_name}): PROMOZIONE! Nuovo ruolo: {self.job_title}")
                if hasattr(self.owner, 'mood') and self.owner.mood:
                    self.owner.mood.add_mood_modifier(getattr(config, "MOOD_BOOST_PROMOTION", 20.0), "Promozione")
        else: # Già al livello massimo di questa traccia
            pass


    def get_fired(self):
        """L'NPC viene licenziato."""
        logger.warning(f"Career ({self.owner_name}): {self.owner_name} è stato LICENZIATO da {self.job_title}!")
        self.set_career("Unemployed", 0) # Torna disoccupato
        if hasattr(self.owner, 'mood') and self.owner.mood:
            self.owner.mood.add_mood_modifier(getattr(config, "MOOD_PENALTY_FIRED", -50.0), "Licenziato")


    def update(self, game_hours_advanced: float, game_state: 'GameState'):
        """
        Aggiorna lo stato della carriera (es. controllo orario di lavoro).
        Questa funzione viene chiamata da Character.update() o da un sistema AI.
        """
        # Questa funzione potrebbe essere usata dall'IA per decidere se andare/tornare dal lavoro.
        # Esempio:
        # if self.current_career_name != "Unemployed" and self.can_work_today(game_state):
        #     is_time_to_go = self.is_work_time(game_state) and not self.is_currently_at_work
        #     is_time_to_return = not self.is_work_time(game_state) and self.is_currently_at_work
        # 
        #     if is_time_to_go:
        #         # L'IA dovrebbe impostare l'azione per andare al lavoro
        #         # self.owner.set_action_go_to_work(...)
        #         pass
        #     elif is_time_to_return:
        #         # L'IA (o questo update) dovrebbe gestire il ritorno dal lavoro
        #         # self.finish_work(ore_lavorate_effettive)
        #         pass
        pass # La logica principale di andare/tornare dal lavoro sarà guidata dall'IA in idle.py


    def get_job_title_and_level(self) -> str:
        if self.current_career_name == "Unemployed":
            return self.job_title
        return f"{self.job_title} (Liv. {self.current_job_level_index + 1})"


    def to_dict(self) -> Dict[str, Any]:
        return {
            "current_career_name": self.current_career_name,
            "current_job_level_index": self.current_job_level_index,
            "performance_at_work": self.performance_at_work,
            "days_worked_consecutively": self.days_worked_consecutively,
            "days_missed_work_consecutively": self.days_missed_work_consecutively,
            "is_currently_at_work": self.is_currently_at_work # Salva se è al lavoro
        }

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]], character_owner: 'Character') -> 'CareerComponent':
        instance = cls(character_owner) # Crea un'istanza con valori di default (Disoccupato)
        if data:
            career_name = data.get("current_career_name", "Unemployed")
            level_index = data.get("current_job_level_index", 0)
            
            # set_career aggiornerà anche job_title, salary, ecc.
            instance.set_career(career_name, level_index) 
            
            instance.performance_at_work = float(data.get("performance_at_work", 50.0))
            instance.days_worked_consecutively = int(data.get("days_worked_consecutively", 0))
            instance.days_missed_work_consecutively = int(data.get("days_missed_work_consecutively", 0))
            instance.is_currently_at_work = data.get("is_currently_at_work", False)

        if DEBUG_CAREER and data:
            logger.debug(f"CareerComponent per {character_owner.name} caricato. Lavoro: {instance.job_title}")
        return instance