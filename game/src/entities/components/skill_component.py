# game/src/entities/components/skill_component.py
import logging
import math
import random
from typing import Dict, Any, Optional, List, TYPE_CHECKING

# Importa dal package 'game'
from game import config

if TYPE_CHECKING:
    from game.src.entities.character import Character

logger = logging.getLogger(__name__)
DEBUG_SKILL = getattr(config, 'DEBUG_AI_ACTIVE', False)

# Definizioni delle abilità (potrebbero essere in config.py o in un file JSON dedicato)
# Chiave: nome_abilità (stringa)
# Valori: dizionario con dettagli come "max_level", "xp_per_level_base", "xp_curve_factor"
DEFAULT_SKILL_DEFINITIONS = {
    "cucina": {"max_level": 10, "xp_per_level_base": 100, "xp_curve_factor": 1.2, "initial_level_range": (0,2)},
    "carisma": {"max_level": 10, "xp_per_level_base": 120, "xp_curve_factor": 1.25, "initial_level_range": (0,3)},
    "logica": {"max_level": 10, "xp_per_level_base": 100, "xp_curve_factor": 1.15, "initial_level_range": (0,2)},
    "meccanica": {"max_level": 10, "xp_per_level_base": 150, "xp_curve_factor": 1.3, "initial_level_range": (0,1)},
    "giardinaggio": {"max_level": 10, "xp_per_level_base": 90, "xp_curve_factor": 1.2, "initial_level_range": (0,1)},
    "pittura": {"max_level": 10, "xp_per_level_base": 110, "xp_curve_factor": 1.2, "initial_level_range": (0,1)},
    # Aggiungi altre abilità
}

class SkillInstance:
    """Rappresenta una singola abilità per un NPC."""
    def __init__(self, skill_name: str, definition: Dict[str, Any], initial_level: int = 0, initial_xp: float = 0.0):
        self.name: str = skill_name
        self.definition = definition # Riferimento alla definizione dell'abilità
        
        self.max_level: int = definition.get("max_level", 10)
        self.current_level: int = max(0, min(initial_level, self.max_level))
        
        # XP per il livello corrente (da 0 a xp_needed_for_next_level)
        self.current_xp: float = float(initial_xp) 
        self.xp_needed_for_next_level: float = self._calculate_xp_for_level(self.current_level + 1)

    def _calculate_xp_for_level(self, target_level: int) -> float:
        """Calcola l'XP totale necessario per raggiungere un certo livello."""
        if target_level <= 0: return 0
        if target_level > self.max_level +1 : target_level = self.max_level + 1 # XP per il cap
        
        base_xp = self.definition.get("xp_per_level_base", 100)
        curve_factor = self.definition.get("xp_curve_factor", 1.2) # Aumento XP per livello
        
        # Esempio di curva: XP = base * (fattore ^ (livello - 1))
        # Questa è l'XP per *quel singolo* livello.
        # Se vuoi XP totale, dovrai sommarla. Per ora, xp_needed è per il *prossimo* livello.
        if target_level == 1: return base_xp # XP per passare da 0 a 1
        return base_xp * (curve_factor ** (target_level - 1))


    def add_xp(self, amount: float, owner_name: str = "NPC") -> bool:
        """Aggiunge XP all'abilità e gestisce i level up."""
        if self.current_level >= self.max_level:
            self.current_xp = self.xp_needed_for_next_level # Riempi l'XP dell'ultimo livello
            return False # Già al massimo livello

        if amount <= 0:
            return False

        self.current_xp += amount
        leveled_up = False

        while self.current_xp >= self.xp_needed_for_next_level and self.current_level < self.max_level:
            leveled_up = True
            self.current_level += 1
            xp_overflow = self.current_xp - self.xp_needed_for_next_level
            self.current_xp = xp_overflow if xp_overflow > 0 else 0.0 # Porta l'eccesso al nuovo livello
            self.xp_needed_for_next_level = self._calculate_xp_for_level(self.current_level + 1)
            
            if DEBUG_SKILL or True: # Logga sempre i level up
                logger.info(f"Skill ({owner_name}): {self.name} è salita al livello {self.current_level}!")
            
            # TODO: Qui potresti triggerare eventi di gioco (es. sblocco nuove interazioni, boost umore)
            # if hasattr(owner, 'mood'): owner.mood.add_mood_modifier(config.MOOD_BOOST_SKILL_UP, f"Livellata {self.name}")

        if self.current_level == self.max_level: # Se ha raggiunto il cap
            self.current_xp = self.xp_needed_for_next_level # Riempi la barra XP

        if DEBUG_SKILL and not leveled_up and amount > 0: # Logga guadagno XP se non c'è stato level up
             logger.debug(f"Skill ({owner_name}): {self.name} ha guadagnato {amount:.2f} XP. Totale XP livello: {self.current_xp:.2f}/{self.xp_needed_for_next_level:.2f} (Liv. {self.current_level})")
        return leveled_up

    def get_level(self) -> int:
        return self.current_level

    def get_xp_progress_percentage(self) -> float:
        """Restituisce il progresso XP per il livello corrente come percentuale (0.0 a 1.0)."""
        if self.xp_needed_for_next_level == 0: # Es. al max livello o errore
            return 1.0 if self.current_level >= self.max_level else 0.0
        return min(self.current_xp / self.xp_needed_for_next_level, 1.0)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name, # Anche se la chiave esterna sarà il nome, è utile averlo qui
            "current_level": self.current_level,
            "current_xp": self.current_xp
        }

    @classmethod
    def from_dict(cls, skill_name: str, data: Dict[str, Any], definition: Dict[str, Any]) -> 'SkillInstance':
        level = data.get("current_level", 0)
        xp = data.get("current_xp", 0.0)
        return cls(skill_name, definition, initial_level=level, initial_xp=xp)


class SkillComponent:
    def __init__(self, character_owner: 'Character'):
        """
        Inizializza il componente delle abilità.

        Args:
            character_owner (Character): Il personaggio a cui questo componente appartiene.
        """
        self.owner: 'Character' = character_owner
        self.owner_name: str = character_owner.name if character_owner else "NPC Sconosciuto"

        self.skill_definitions: Dict[str, Dict[str, Any]] = getattr(config, 'SKILL_DEFINITIONS', DEFAULT_SKILL_DEFINITIONS)
        self.skills: Dict[str, SkillInstance] = {}

        self._initialize_skills()

        if DEBUG_SKILL:
            logger.debug(f"SkillComponent per {self.owner_name} inizializzato con {len(self.skills)} abilità.")

    def _initialize_skills(self):
        """Inizializza tutte le abilità definite con un livello iniziale casuale."""
        for skill_name, definition in self.skill_definitions.items():
            level_range = definition.get("initial_level_range", (0, 0))
            initial_level = random.randint(level_range[0], level_range[1])
            # L'XP iniziale per un livello > 0 potrebbe essere 0 o una frazione del necessario per il prossimo
            self.skills[skill_name] = SkillInstance(skill_name, definition, initial_level=initial_level)
            if DEBUG_SKILL and initial_level > 0:
                logger.debug(f"Skill ({self.owner_name}): {skill_name} inizializzata a livello {initial_level}")

    def add_skill_xp(self, skill_name: str, amount: float, source_action: Optional[str] = None) -> bool:
        """Aggiunge XP a un'abilità specifica. Restituisce True se l'abilità è salita di livello."""
        if skill_name not in self.skills:
            logger.warning(f"Skill ({self.owner_name}): Tentativo di aggiungere XP all'abilità non esistente '{skill_name}'.")
            return False
        
        if DEBUG_SKILL and source_action:
            logger.debug(f"Skill ({self.owner_name}): Aggiungo {amount:.2f} XP a '{skill_name}' da azione '{source_action}'.")
        
        return self.skills[skill_name].add_xp(amount, self.owner_name)

    def get_skill_level(self, skill_name: str) -> int:
        """Restituisce il livello di un'abilità specifica."""
        if skill_name in self.skills:
            return self.skills[skill_name].get_level()
        # logger.debug(f"Skill ({self.owner_name}): Abilità '{skill_name}' non trovata per get_skill_level.")
        return 0 # Livello 0 se l'abilità non esiste per questo NPC

    def get_skill_xp_percentage(self, skill_name: str) -> float:
        """Restituisce il progresso XP percentuale per l'abilità specificata."""
        if skill_name in self.skills:
            return self.skills[skill_name].get_xp_progress_percentage()
        return 0.0

    def get_all_skills_info(self) -> Dict[str, Dict[str, Any]]:
        """Restituisce un dizionario con informazioni su tutte le abilità."""
        info = {}
        for skill_name, skill_instance in self.skills.items():
            info[skill_name] = {
                "level": skill_instance.get_level(),
                "xp_percentage": skill_instance.get_xp_progress_percentage(),
                "xp_current": skill_instance.current_xp,
                "xp_needed_for_next": skill_instance.xp_needed_for_next_level
            }
        return info

    def update(self, game_hours_advanced: float, current_action: str, character_state: 'Character'):
        """
        Aggiorna le abilità. Potrebbe includere il decadimento delle abilità se non usate,
        o un lento apprendimento passivo per alcune abilità o tratti.
        Per ora, il guadagno di XP è principalmente guidato da azioni specifiche.
        """
        # Esempio: Se un'azione sta attivamente usando un'abilità, guadagna XP
        # Questa logica è meglio gestirla NEL MODULO DELL'AZIONE STESSA,
        # che poi chiama self.owner.skills.add_skill_xp(...)
        #
        # Ad esempio, in un'azione "cucinare_pasto.py":
        #   if successo:
        #       self.owner.skills.add_skill_xp("cucina", config.XP_GAIN_CUCINARE_PASTO)

        # Esempio di decadimento (opzionale, da configurare)
        # skill_decay_rate = getattr(config, "SKILL_DECAY_RATE_PER_HOUR", 0.001) # Molto lento
        # if game_hours_advanced > 0 and skill_decay_rate > 0:
        #     for skill_name, skill_instance in self.skills.items():
        #         if skill_instance.current_level > 0 and skill_instance.current_xp > 0:
        #             # Non far decadere sotto l'XP minimo per il livello corrente
        #             amount_to_decay = skill_decay_rate * game_hours_advanced
        #             skill_instance.current_xp = max(0, skill_instance.current_xp - amount_to_decay)
        pass

    def to_dict(self) -> Dict[str, Any]:
        """Serializza lo stato delle abilità."""
        skills_data = {}
        for skill_name, skill_instance in self.skills.items():
            skills_data[skill_name] = skill_instance.to_dict()
        return skills_data

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]], character_owner: 'Character') -> 'SkillComponent':
        """Crea un'istanza di SkillComponent da dati serializzati."""
        instance = cls(character_owner) # Crea un'istanza (che inizializza le abilità con livelli base)
        if data:
            # Sovrascrive le abilità con i dati salvati
            instance.skills.clear() # Rimuovi le abilità inizializzate di default
            for skill_name_saved, skill_data_saved in data.items():
                if skill_name_saved in instance.skill_definitions:
                    definition = instance.skill_definitions[skill_name_saved]
                    instance.skills[skill_name_saved] = SkillInstance.from_dict(skill_name_saved, skill_data_saved, definition)
                elif DEBUG_SKILL:
                    logger.warning(f"Skill ({character_owner.name}): Definizione per abilità salvata '{skill_name_saved}' non trovata. Skippata.")
        
        if DEBUG_SKILL and data:
            logger.debug(f"SkillComponent per {character_owner.name} caricato con {len(instance.skills)} abilità.")
        return instance