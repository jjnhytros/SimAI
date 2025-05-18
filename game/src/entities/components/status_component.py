# game/src/entities/components/status_component.py
import logging
import random # Per l'età iniziale
from typing import Dict, Any, Optional, TYPE_CHECKING

# Importa dal package 'game'
from game import config

if TYPE_CHECKING:
    from game.src.entities.character import Character # Per il type hint di character_owner
    # from game.src.modules.game_state_module import GameState # Non sembra necessario qui direttamente

logger = logging.getLogger(__name__)
DEBUG_STATUS = getattr(config, 'DEBUG_AI_ACTIVE', False)

# Valori di default per lo stato
DEFAULT_INITIAL_AGE_DAYS_MIN = getattr(config, 'NPC_INITIAL_AGE_YEARS_MIN', 20) * getattr(config, 'GAME_DAYS_PER_YEAR', 432)
DEFAULT_INITIAL_AGE_DAYS_MAX = getattr(config, 'NPC_INITIAL_AGE_YEARS_MAX', 40) * getattr(config, 'GAME_DAYS_PER_YEAR', 432)
DEFAULT_PREGNANCY_TERM_DAYS = getattr(config, 'PREGNANCY_TERM_GAME_DAYS', 24)

class StatusComponent:
    def __init__(self, character_owner: 'Character', initial_age_days: Optional[float] = None):
        """
        Inizializza il componente dello stato fisico e demografico.

        Args:
            character_owner (Character): Il personaggio a cui questo componente appartiene.
            initial_age_days (Optional[float]): L'età iniziale in giorni totali di gioco.
                                                Se None, viene generata casualmente.
        """
        self.owner: 'Character' = character_owner
        self.owner_name: str = character_owner.name if character_owner else "NPC Sconosciuto"

        if initial_age_days is None:
            self.age_in_total_game_days: float = random.uniform(
                DEFAULT_INITIAL_AGE_DAYS_MIN,
                DEFAULT_INITIAL_AGE_DAYS_MAX
            )
        else:
            self.age_in_total_game_days: float = float(initial_age_days)

        # Stato Gravidanza
        self.is_pregnant: bool = False
        self.pregnancy_progress_days: float = 0.0
        self.pregnancy_term_days: float = float(DEFAULT_PREGNANCY_TERM_DAYS)
        self.pregnancy_partner_uuid: Optional[str] = None # UUID del padre (o altro genitore)

        # Stato Salute (placeholder per futuro)
        # self.health_value: float = 100.0 # Es. 0-100
        # self.sicknesses: List[str] = []
        # self.injuries: List[str] = []

        if DEBUG_STATUS:
            logger.debug(f"StatusComponent per {self.owner_name} inizializzato. Età giorni: {self.age_in_total_game_days:.2f}")

    def update(self, game_hours_advanced: float):
        """
        Aggiorna lo stato demografico e fisico nel tempo.

        Args:
            game_hours_advanced (float): Ore di gioco trascorse in questo tick.
        """
        if game_hours_advanced <= 0:
            return

        days_advanced = game_hours_advanced / getattr(config, 'GAME_HOURS_IN_DAY', 28) # Assicura che GAME_HOURS_IN_DAY sia definito
        
        # Aggiornamento Età
        self.age_in_total_game_days += days_advanced

        # Aggiornamento Gravidanza
        if self.is_pregnant:
            self.pregnancy_progress_days += days_advanced
            if self.pregnancy_progress_days >= self.pregnancy_term_days:
                self._give_birth()
        
        # Aggiornamento Salute (futuro)
        # ...

    def _give_birth(self):
        """Gestisce l'evento del parto."""
        if not self.is_pregnant: return

        if DEBUG_STATUS:
            logger.info(f"STATUS ({self.owner_name}): È il momento del parto! Progresso: {self.pregnancy_progress_days:.2f}/{self.pregnancy_term_days:.2f}")
        
        # Logica per creare il neonato
        # Questa chiamata dovrebbe avvenire nel CharacterManager per centralizzare la creazione degli NPC
        if hasattr(self.owner, 'game_state_ref') and self.owner.game_state_ref and \
           hasattr(self.owner.game_state_ref, 'character_manager_instance') and \
           self.owner.game_state_ref.character_manager_instance:
            
            # Trova il partner della gravidanza per passarlo a spawn_newborn_npc
            partner_for_birth = None
            if self.pregnancy_partner_uuid and hasattr(self.owner.game_state_ref, 'get_npc_by_uuid'):
                partner_for_birth = self.owner.game_state_ref.get_npc_by_uuid(self.pregnancy_partner_uuid)

            newborn_npc = self.owner.game_state_ref.character_manager_instance.spawn_newborn_npc(
                parent1=self.owner, 
                parent2=partner_for_birth # Passa il partner se conosciuto
            )
            if newborn_npc:
                logger.info(f"STATUS ({self.owner_name}): Ha partorito {newborn_npc.name}!")
                # Qui potresti aggiungere un mood boost, ecc.
                if hasattr(self.owner, 'mood') and self.owner.mood:
                     self.owner.mood.add_mood_modifier(getattr(config, "MOOD_BOOST_BIRTH", 75.0), f"Nascita di {newborn_npc.name}")

            else:
                logger.error(f"STATUS ({self.owner_name}): Parto avvenuto, ma CharacterManager non è riuscito a creare il neonato.")
        else:
            logger.error(f"STATUS ({self.owner_name}): Parto avvenuto, ma CharacterManager non accessibile per creare il neonato.")
            
        # Resetta lo stato di gravidanza
        self.is_pregnant = False
        self.pregnancy_progress_days = 0.0
        self.pregnancy_partner_uuid = None


    def set_pregnant(self, partner_uuid: Optional[str] = None) -> bool:
        """
        Imposta lo stato di gravidanza dell'NPC.
        Restituisce True se l'NPC può e diventa incinta, False altrimenti.
        """
        if self.owner.gender != "female": # Assumendo solo femmine per gravidanza biologica
            if DEBUG_STATUS: logger.debug(f"Status ({self.owner_name}): Tentativo di gravidanza fallito (non è femmina).")
            return False
        if self.is_pregnant:
            if DEBUG_STATUS: logger.debug(f"Status ({self.owner_name}): Tentativo di gravidanza fallito (già incinta).")
            return False
        
        # (Opzionale) Controlla età fertile, numero massimo di figli, ecc.
        min_preg_age_days = getattr(config, 'MIN_PREGNANCY_AGE_YEARS', 18) * getattr(config, 'GAME_DAYS_PER_YEAR', 432)
        max_preg_age_days = getattr(config, 'MAX_PREGNANCY_AGE_YEARS', 45) * getattr(config, 'GAME_DAYS_PER_YEAR', 432)
        if not (min_preg_age_days <= self.age_in_total_game_days <= max_preg_age_days):
            if DEBUG_STATUS: logger.debug(f"Status ({self.owner_name}): Tentativo di gravidanza fallito (età non fertile: {self.age_in_total_game_days / config.GAME_DAYS_PER_YEAR:.1f} anni).")
            return False

        self.is_pregnant = True
        self.pregnancy_progress_days = 0.0
        self.pregnancy_partner_uuid = partner_uuid
        if DEBUG_STATUS: 
            partner_log = f" con partner {partner_uuid[-6:]}" if partner_uuid else ""
            logger.info(f"Status ({self.owner_name}): È incinta!{partner_log}")
        
        # Mood boost per la gravidanza
        if hasattr(self.owner, 'mood') and self.owner.mood:
            self.owner.mood.add_mood_modifier(getattr(config, "MOOD_BOOST_PREGNANT", 20.0), "Incinta")
        return True

    def get_formatted_age_string(self) -> str:
        """Restituisce una stringa formattata per l'età (Anni, Mesi, Giorni)."""
        days_per_year = getattr(config, 'GAME_DAYS_PER_YEAR', 432)
        days_per_month = getattr(config, 'DAYS_PER_MONTH', 24) # Assumendo che tutti i mesi abbiano la stessa durata
        
        if days_per_year == 0 or days_per_month == 0: 
            logger.warning("GAME_DAYS_PER_YEAR o DAYS_PER_MONTH non definiti o zero in config.")
            return "Età N/D"
        
        total_days_int = int(self.age_in_total_game_days)
        
        years = total_days_int // days_per_year
        remaining_days_after_years = total_days_int % days_per_year
        
        months = remaining_days_after_years // days_per_month
        days = remaining_days_after_years % days_per_month
        
        return f"{years}a, {months}m, {days}g"

    def to_dict(self) -> Dict[str, Any]:
        """Serializza lo stato fisico e demografico."""
        return {
            "age_in_total_game_days": self.age_in_total_game_days,
            "is_pregnant": self.is_pregnant,
            "pregnancy_progress_days": self.pregnancy_progress_days,
            "pregnancy_term_days": self.pregnancy_term_days, # Salva anche il termine se può variare
            "pregnancy_partner_uuid": self.pregnancy_partner_uuid
            # "health_value": self.health_value,
            # "sicknesses": self.sicknesses,
            # "injuries": self.injuries
        }

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]], character_owner: 'Character') -> 'StatusComponent':
        """Crea un'istanza di StatusComponent da dati serializzati."""
        initial_age = None
        if data and "age_in_total_game_days" in data:
            initial_age = float(data["age_in_total_game_days"])
            
        instance = cls(character_owner, initial_age_days=initial_age) # Il costruttore gestisce initial_age None
        
        if data:
            instance.is_pregnant = data.get("is_pregnant", False)
            instance.pregnancy_progress_days = float(data.get("pregnancy_progress_days", 0.0))
            instance.pregnancy_term_days = float(data.get("pregnancy_term_days", DEFAULT_PREGNANCY_TERM_DAYS))
            instance.pregnancy_partner_uuid = data.get("pregnancy_partner_uuid")
            # instance.health_value = float(data.get("health_value", 100.0))
            # instance.sicknesses = list(data.get("sicknesses", []))
            # instance.injuries = list(data.get("injuries", []))

        if DEBUG_STATUS and data:
            logger.debug(f"StatusComponent per {character_owner.name} caricato. Età giorni: {instance.age_in_total_game_days:.2f}, Incinta: {instance.is_pregnant}")
        return instance