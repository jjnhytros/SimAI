# core/character.py
"""
Definizione della classe Character, il nucleo per gli NPC in SimAI.
"""
from dataclasses import dataclass, field
from typing import Dict, Set, Optional, Tuple, List 
import collections
import random

from core.enums import (
    Interest, LifeStage, Gender, RelationshipStatus, RelationshipType,
    SchoolLevel, AspirationType, NeedType, FunActivityType, SocialInteractionType
)
from core.modules.actions import BaseAction 
from core.modules.actions import (
    EatAction, SleepAction, UseBathroomAction, HaveFunAction, SocializeAction, 
    EngageIntimacyAction,
)

from core import settings
from core.modules.time_manager import TimeManager
# Import per la nuova struttura dei bisogni
from core.modules.needs import BaseNeed 
from core.modules.needs import (
    HungerNeed, EnergyNeed, SocialNeed, FunNeed, HygieneNeed, BladderNeed, IntimacyNeed,
    ComfortNeed, EnvironmentNeed, SafetyNeed, CreativityNeed, LearningNeed, 
    SpiritualityNeed, AutonomyNeed, AchievementNeed
)
from core.AI.ai_decision_maker import AIDecisionMaker
# È necessario importare Simulation per il type hinting, ma questo crea dipendenza circolare
# se Simulation importa Character. Useremo una stringa per il type hint.
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.simulation import Simulation # Solo per type hinting
    # from core.world.location import Location

# Struttura per le informazioni di relazione
@dataclass
class RelationshipInfo: # Manteniamo questa definizione
    target_npc_id: str; type: RelationshipType; score: int = 0
    def __str__(self): return f"({self.type.display_name_it() if self.type else 'N/D'} con {self.target_npc_id}, Score: {self.score})"

class Character:
    def __init__(self, 
                npc_id: str, name: str, initial_gender: Gender,
                initial_age_days: int = 0, initial_interests: Optional[Set[Interest]] = None,
                initial_sexually_attracted_to_genders: Optional[Set[Gender]] = None,
                initial_romantically_attracted_to_genders: Optional[Set[Gender]] = None,
                initial_is_on_asexual_spectrum: bool = False, initial_is_on_aromantic_spectrum: bool = False,
                initial_relationship_status: RelationshipStatus = RelationshipStatus.SINGLE,
                initial_school_level: SchoolLevel = SchoolLevel.NONE,
                initial_location_id: Optional[str] = None,
                initial_aspiration: Optional[AspirationType] = None):

        self.npc_id: str = npc_id; self.name: str = name
        if not isinstance(initial_gender, Gender): raise ValueError(f"initial_gender per {name} non valido")
        self.gender: Gender = initial_gender
        self._age_in_days: int = initial_age_days
        self.life_stage: Optional[LifeStage] = None 
        self._interests: Set[Interest] = {i for i in (initial_interests or set()) if isinstance(i, Interest)}
        self.sexually_attracted_to_genders: Set[Gender] = {g for g in (initial_sexually_attracted_to_genders or set()) if isinstance(g, Gender)}
        self.romantically_attracted_to_genders: Set[Gender] = {g for g in (initial_romantically_attracted_to_genders or set()) if isinstance(g, Gender)}
        self.is_on_asexual_spectrum: bool = initial_is_on_asexual_spectrum
        self.is_on_aromantic_spectrum: bool = initial_is_on_aromantic_spectrum
        if not isinstance(initial_relationship_status, RelationshipStatus): raise ValueError("initial_relationship_status non valido")
        self.relationship_status: RelationshipStatus = initial_relationship_status
        if not isinstance(initial_school_level, SchoolLevel): raise ValueError("initial_school_level non valido")
        self.current_school_level: SchoolLevel = initial_school_level
        self.highest_school_level_completed: SchoolLevel = SchoolLevel.NONE
        self.relationships: Dict[str, RelationshipInfo] = {} 
        if initial_aspiration is not None and not isinstance(initial_aspiration, AspirationType): raise ValueError("initial_aspiration non valida")
        self.aspiration: Optional[AspirationType] = initial_aspiration
        self.aspiration_progress: float = 0.0
        self.needs: Dict[NeedType, BaseNeed] = {}
        self._initialize_needs()
        self._calculate_and_set_life_stage() 
        self.action_queue: collections.deque[BaseAction] = collections.deque()
        self.current_action: Optional[BaseAction] = None
        self.is_busy: bool = False
        self.current_location_id: Optional[str] = initial_location_id

        # Attributi per la gestione delle proposte di intimità
        self.pending_intimacy_proposal_from: Optional[str] = None # ID dell'NPC che mi ha fatto una proposta
        self.pending_intimacy_target_accepted: Optional[str] = None # ID del target che ha accettato la MIA proposta
        self.last_intimacy_proposal_tick: int = -99999 # Per cooldown proposte fatte (inizializzato a un valore molto basso)
        # last_intimacy_proposal_received_tick: int = -99999 # Potrebbe servire per cooldown risposte

        self.ai_decision_maker = AIDecisionMaker(npc=self) # <-- CREA ISTANZA AI

        if settings.DEBUG_MODE: print(f"  [Character CREATED] {self!s}")

    def set_location(self, new_location_id: str, simulation: 'Simulation'):
        """Sposta l'NPC in una nuova locazione."""
        old_location_id = self.current_location_id
        
        # Rimuovi l'NPC dalla vecchia locazione (se esiste)
        if old_location_id:
            old_loc_instance = simulation.get_location_by_id(old_location_id)
            if old_loc_instance:
                old_loc_instance.remove_npc(self.npc_id)
        
        # Aggiungi l'NPC alla nuova locazione
        self.current_location_id = new_location_id
        new_loc_instance = simulation.get_location_by_id(new_location_id)
        if new_loc_instance:
            new_loc_instance.add_npc(self.npc_id)
            if settings.DEBUG_MODE: print(f"  [Character Location - {self.name}] Spostato a '{new_loc_instance.name}' (ID: {new_location_id})")
        elif settings.DEBUG_MODE:
            print(f"  [Character Location WARN - {self.name}] Tentativo di spostare a locazione non esistente: {new_location_id}")

    def get_current_location(self, simulation: 'Simulation') -> Optional['Location']:
        if self.current_location_id:
            return simulation.get_location_by_id(self.current_location_id)
        return None

    def _initialize_needs(self):
        need_class_map: Dict[NeedType, type[BaseNeed]] = {
            NeedType.HUNGER: HungerNeed, NeedType.ENERGY: EnergyNeed, NeedType.SOCIAL: SocialNeed, NeedType.FUN: FunNeed,
            NeedType.HYGIENE: HygieneNeed, NeedType.BLADDER: BladderNeed, NeedType.INTIMACY: IntimacyNeed,
            NeedType.COMFORT: ComfortNeed, NeedType.ENVIRONMENT: EnvironmentNeed, NeedType.SAFETY: SafetyNeed,
            NeedType.CREATIVITY: CreativityNeed, NeedType.LEARNING: LearningNeed, NeedType.SPIRITUALITY: SpiritualityNeed,
            NeedType.AUTONOMY: AutonomyNeed, NeedType.ACHIEVEMENT: AchievementNeed
        }
        for need_type_enum in NeedType:
            if need_type_enum in need_class_map: self.needs[need_type_enum] = need_class_map[need_type_enum]() 
            elif settings.DEBUG_MODE: print(f"  [Char Needs Init WARN - {self.name}] Classe per NeedType.{need_type_enum.name} non in map.")
        if settings.DEBUG_MODE: print(f"    [Char Needs Init OOP - {self.name}] Bisogni oggetti inizializzati.")

    def _calculate_and_set_life_stage(self): # Assicurati che la formattazione età nei log sia quella voluta
        age_days = self._age_in_days; new_calculated_stage = None
        sorted_thresholds = sorted(settings.LIFE_STAGE_AGE_THRESHOLDS_DAYS.items(), key=lambda item: item[1])
        for stage_key_str, threshold_days in reversed(sorted_thresholds):
            if age_days >= threshold_days:
                try: new_calculated_stage = LifeStage[stage_key_str.upper()] 
                except KeyError: pass
                break 
        if not new_calculated_stage and sorted_thresholds:
            try: new_calculated_stage = LifeStage[sorted_thresholds[0][0].upper()]
            except KeyError: pass 
        current_life_stage_exists = hasattr(self, 'life_stage') and self.life_stage is not None
        if new_calculated_stage is not None:
            if not current_life_stage_exists or self.life_stage != new_calculated_stage:
                old_stage_name_for_log = self.life_stage.name if current_life_stage_exists else "Nessuno"
                self.life_stage = new_calculated_stage
                if settings.DEBUG_MODE:
                    age_in_years_for_log = self.get_age_in_years_float() 
                    current_life_stage_display_name = self.life_stage.display_name_it() if self.life_stage else "N/D"
                    old_life_stage_display_name = "Nessuno"
                    if old_stage_name_for_log != "Nessuno":
                        try: old_life_stage_display_name = LifeStage[old_stage_name_for_log].display_name_it()
                        except KeyError: old_life_stage_display_name = old_stage_name_for_log
                    print(f"  [Character LIFE STAGE] {self.name} (età {age_in_years_for_log:.1f} anni) è ora {current_life_stage_display_name} (precedente: {old_life_stage_display_name}).")
        elif settings.DEBUG_MODE: print(f"  [Character ERROR] Impossibile determinare LifeStage per {self.name} (età {age_days}gg).")

    def get_age_in_days(self) -> int: return self._age_in_days

    def get_age_in_years_float(self) -> float:
        if settings.DXY == 0: return 0.0
        return self._age_in_days / settings.DXY

    def _set_age_in_days(self, new_age_days: int): 
        if new_age_days != self._age_in_days:
            self._age_in_days = new_age_days
            if settings.DEBUG_MODE: print(f"  [Character AGE UPDATE] L'età di {self.name} è ora {self.get_age_in_years_float():.1f} anni.")
            self._calculate_and_set_life_stage() 

    def get_interests(self) -> Set[Interest]: return self._interests.copy()

    def add_interest(self, i: Interest) -> bool:
        if not isinstance(i, Interest): return False
        if len(self._interests) < settings.MAX_NPC_ACTIVE_INTERESTS and i not in self._interests: self._interests.add(i); return True
        return False

    def remove_interest(self, i: Interest) -> bool:
        if not isinstance(i, Interest): return False
        try: self._interests.remove(i); return True
        except KeyError: return False

    def get_sexual_attraction(self) -> Set[Gender]: return self.sexually_attracted_to_genders.copy()

    def get_romantic_attraction(self) -> Set[Gender]: return self.romantically_attracted_to_genders.copy()

    def is_asexual(self) -> bool: return self.is_on_asexual_spectrum

    def is_aromantic(self) -> bool: return self.is_on_aromantic_spectrum

    def get_relationship_status(self) -> RelationshipStatus: return self.relationship_status

    def set_relationship_status(self, new_status: RelationshipStatus):
        if not isinstance(new_status, RelationshipStatus): return
        if self.relationship_status != new_status:
            if settings.DEBUG_MODE: print(f"  [Character RELATIONSHIP] Stato di {self.name}: {self.relationship_status.display_name_it()} -> {new_status.display_name_it()}.")
            self.relationship_status = new_status

    def get_current_school_level(self) -> SchoolLevel: return self.current_school_level

    def set_current_school_level(self, level: SchoolLevel):
        if not isinstance(level, SchoolLevel): return
        if self.current_school_level != level: self.current_school_level = level

    def get_highest_school_level_completed(self) -> SchoolLevel: return self.highest_school_level_completed

    def set_highest_school_level_completed(self, level: SchoolLevel):
        if not isinstance(level, SchoolLevel): return
        if self.highest_school_level_completed != level: self.highest_school_level_completed = level

    def get_relationships(self) -> Dict[str, RelationshipInfo]: return self.relationships.copy()

    def get_relationship_with(self, target_npc_id: str) -> Optional[RelationshipInfo]: return self.relationships.get(target_npc_id)

    def update_relationship(self, target_npc_id: str, new_type: RelationshipType, score_change: int = 0, new_score: Optional[int] = None):
        if not isinstance(new_type, RelationshipType): return
        if target_npc_id not in self.relationships: self.relationships[target_npc_id] = RelationshipInfo(target_npc_id=target_npc_id, type=new_type, score=0)
        rel_info = self.relationships[target_npc_id]; rel_info.type = new_type
        if new_score is not None: rel_info.score = max(-100, min(100, new_score))
        else: rel_info.score = max(-100, min(100, rel_info.score + score_change))

    def get_aspiration(self) -> Optional[AspirationType]: return self.aspiration

    def set_aspiration(self, aspiration: AspirationType, progress: float = 0.0):
        if not isinstance(aspiration, AspirationType): return
        if self.aspiration != aspiration: self.aspiration = aspiration; self.aspiration_progress = max(0.0, min(1.0, progress))

    def get_aspiration_progress(self) -> float: return self.aspiration_progress

    def update_aspiration_progress(self, change: float):
        if self.aspiration:
            old_progress = self.aspiration_progress; self.aspiration_progress = max(0.0, min(1.0, self.aspiration_progress + change))
            if settings.DEBUG_MODE and old_progress != self.aspiration_progress and self.aspiration_progress >= 1.0:
                print(f"  [Character ASPIRATION] {self.name} HA COMPLETATO: {self.aspiration.display_name_it()}!")

    def get_need_value(self, need_type: NeedType) -> Optional[float]:
        """Restituisce il valore corrente di un bisogno specifico, accedendo all'oggetto BaseNeed."""
        if not isinstance(need_type, NeedType):
            if settings.DEBUG_MODE: print(f"  [Character Needs WARN - {self.name}] Tentativo di get NeedType non valido: {need_type}")
            return None
        need_object = self.needs.get(need_type)
        if need_object:
            return need_object.get_value()
        else:
            if settings.DEBUG_MODE: print(f"  [Character Needs WARN - {self.name}] Bisogno {need_type.name} non trovato nell'istanza Character.")
            return None # O un valore di default appropriato se preferito

    def change_need_value(self, need_type: NeedType, amount: float, is_decay_event: bool = False) -> bool:
        """
        Modifica il valore di un bisogno specifico chiamando il metodo sull'oggetto BaseNeed corrispondente.
        """
        if not isinstance(need_type, NeedType):
            if settings.DEBUG_MODE: print(f"  [Character Needs WARN - {self.name}] Tentativo di modificare NeedType non valido: {need_type}")
            return False
        need_object = self.needs.get(need_type)
        if need_object:
            # Passiamo il nome del Character per i log interni a BaseNeed.change_value
            need_object.change_value(amount, is_decay_event=is_decay_event, character_name_for_log=self.name)
            return True
        else:
            if settings.DEBUG_MODE: print(f"  [Character Needs WARN - {self.name}] Bisogno {need_type.name} non trovato durante change_need_value.")
            return False

    def update_needs(self, time_manager: TimeManager, ticks_elapsed_since_last_update: int):
        """
        Aggiorna (fa decadere) tutti i bisogni dell'NPC chiamando il metodo 'decay'
        su ciascun oggetto BaseNeed.
        """
        fraction_of_hour_elapsed = ticks_elapsed_since_last_update / settings.IXH

        for need_type_enum_member in self.needs:
            need_object = self.needs[need_type_enum_member] # Prendiamo l'oggetto bisogno
            
            # Gestione condizionale per INTIMACY
            if need_type_enum_member == NeedType.INTIMACY and isinstance(need_object, IntimacyNeed):
                # Passiamo l'età e il nome per i log interni a IntimacyNeed.decay (se presenti)
                need_object.decay(fraction_of_hour_elapsed, 
                                character_age_days=self.get_age_in_days(), 
                                character_name_for_log=self.name)
            else:
                need_object.decay(fraction_of_hour_elapsed, 
                                character_name_for_log=self.name)

            # I log di debug DETTAGLIATI per ogni bisogno ad ogni tick sono stati rimossi da qui.
            # Il logging principale del cambiamento del valore del bisogno ora avviene in BaseNeed.change_value(),
            # principalmente per soddisfazioni o quando si superano le soglie LOW/CRITICAL.
            # Manteniamo un avviso se un tasso di decadimento non è definito in settings.py.
            if settings.DEBUG_MODE:
                need_name_str = need_type_enum_member.name
                if need_name_str not in settings.NEED_DECAY_RATES:
                    # Questo log è importante perché indica un problema di configurazione
                    print(f"    [NEEDS UPDATE WARN - {self.name}] Tasso di decadimento per '{need_name_str}' NON DEFINITO in settings.NEED_DECAY_RATES! (Userà 0.0)")

    def get_lowest_need(self) -> Optional[Tuple[NeedType, float]]:
        if not self.needs: return None
        
        lowest_value = float('inf')
        lowest_need_type: Optional[NeedType] = None
        
        for need_type, need_object in self.needs.items():
            current_value = need_object.get_value()
            if current_value < lowest_value:
                lowest_value = current_value
                lowest_need_type = need_type
        
        if lowest_need_type is not None:
            return lowest_need_type, lowest_value
        return None

    def add_action_to_queue(self, action: BaseAction):
        """Aggiunge un'azione alla fine della coda dell'NPC."""
        if not isinstance(action, BaseAction):
            if settings.DEBUG_MODE: print(f"  [Character Action WARN - {self.name}] Tentativo di accodare oggetto non BaseAction: {action}")
            return
        self.action_queue.append(action)
        if settings.DEBUG_MODE: 
            print(f"  [Character Action - {self.name}] Azione '{action.action_type_name}' AGGIUNTA alla coda. Coda: {len(self.action_queue)}.")

    def print_needs_summary(self): # Per i test in simai.py
        if hasattr(self, 'needs') and self.needs:
            print(f"Bisogni di {self.name}:")
            for need_type, need_object in sorted(self.needs.items(), key=lambda item: item[0].name):
                critical_status = ""; value = need_object.get_value()
                critical_thresh = getattr(settings, "NEED_CRITICAL_THRESHOLD", 15.0)
                low_thresh = getattr(settings, "NEED_LOW_THRESHOLD", 30.0)
                if value <= critical_thresh: critical_status = " [!!! CRITICO !!!]"
                elif value <= low_thresh: critical_status = " [! Basso !]"
                print(f"  - {need_object.display_name()}: {value:.1f}{critical_status}")

    def decide_on_intimacy_proposal(self, initiator_npc: 'Character', simulation_context: 'Simulation') -> bool:
        if not initiator_npc: return False
        import random # Import locale se non è a livello di modulo
        relationship = self.get_relationship_with(initiator_npc.npc_id)
        min_rel_score_for_acceptance = getattr(settings, "MIN_REL_SCORE_FOR_INTIMACY_ACCEPTANCE", 20)
        if not relationship or relationship.type not in {RelationshipType.ROMANTIC_PARTNER, RelationshipType.SPOUSE, RelationshipType.CRUSH} or relationship.score < min_rel_score_for_acceptance:
            if settings.DEBUG_MODE: print(f"    [Intimacy Decision - {self.name}] Rifiuto proposta da {initiator_npc.name}: relazione non idonea.")
            return False
        my_intimacy_need = self.get_need_value(NeedType.INTIMACY)
        my_acceptance_threshold = getattr(settings, "MY_INTIMACY_ACCEPTANCE_THRESHOLD", 75.0)
        if my_intimacy_need is None or my_intimacy_need >= my_acceptance_threshold:
            if settings.DEBUG_MODE: print(f"    [Intimacy Decision - {self.name}] Rifiuto proposta da {initiator_npc.name}: bisogno intimità personale alto.")
            return False
        acceptance_chance = 0.80; 
        if my_intimacy_need < settings.NEED_LOW_THRESHOLD: acceptance_chance += 0.15
        acceptance_chance = min(0.95, max(0.10, acceptance_chance))
        accepted = random.random() < acceptance_chance
        if settings.DEBUG_MODE: print(f"    [Intimacy Decision - {self.name}] Proposta da {initiator_npc.name}. Accettata: {accepted} (Chance: {acceptance_chance:.2f})")
        return accepted

    def update_action(self, time_manager: TimeManager, simulation_context: 'Simulation'): # Aggiunto simulation_context
        if self.current_action:
            if self.current_action.is_started and \
               not self.current_action.is_finished and \
               not self.current_action.is_interrupted:
                self.current_action.execute_tick() # Le azioni potrebbero aver bisogno di simulation_context in futuro
            
            if self.current_action.is_finished or self.current_action.is_interrupted:
                action_name_log = self.current_action.action_type_name
                was_interrupted = self.current_action.is_interrupted
                self.current_action = None; self.is_busy = False
                if settings.DEBUG_MODE:
                    status_log = "INTERROTTA" if was_interrupted else "COMPLETATA"
                    print(f"  [Character Action - {self.name}] Azione '{action_name_log}' {status_log}. NPC libero.")
        
        if not self.is_busy and self.action_queue:
            next_action_from_queue = self.action_queue.popleft()
            if settings.DEBUG_MODE:
                print(f"  [Character Action - {self.name}] Tento avvio da coda: '{next_action_from_queue.action_type_name}'. Coda: {len(self.action_queue)}")
            # _start_action potrebbe aver bisogno di simulation_context se action.is_valid() lo richiede
            self._start_action(next_action_from_queue, simulation_context) # Passa sim_context a _start_action
        
        if not self.is_busy and not self.action_queue:
            self.ai_decision_maker.decide_next_action(time_manager, simulation_context)

    def _start_action(self, action: BaseAction, simulation_context: 'Simulation') -> bool:
        # Le azioni ora possono richiedere simulation_context nel loro __init__
        # e is_valid() potrebbe dipendere da esso, anche se non lo passiamo esplicitamente qui
        # (ma viene passato quando si crea l'azione in decide_next_action)
        if action.is_valid(): # is_valid() potrebbe usare self.simulation_context memorizzato nell'azione
            self.current_action = action
            self.current_action.on_start()
            self.is_busy = True
            if settings.DEBUG_MODE: print(f"  [Character Action - {self.name}] INIZIATA azione: '{action.action_type_name}' (Durata: {action.duration_ticks}t). NPC occupato.")
            return True
        else:
            if settings.DEBUG_MODE: print(f"  [Character Action - {self.name}] Azione '{action.action_type_name}' non valida. Non avviata.")
            self.action_queue.appendleft(action) # Rimetti in coda se non valida? O scartala? Per ora scartiamola non rimettendola.

    def __str__(self) -> str: # Come prima, con info azione
        interest_names = sorted([i.name for i in self._interests]); life_stage_name = self.life_stage.display_name_it() if self.life_stage else "N/D"
        gender_name = self.gender.display_name_it() if self.gender else "N/D"; age_in_years_str = f"{self.get_age_in_years_float():.1f}"
        sexual_attraction_str = ", ".join(sorted([g.name for g in self.sexually_attracted_to_genders])) or "N/S"
        if self.is_on_asexual_spectrum: sexual_attraction_str = "Spettro Asessuale"
        romantic_attraction_str = ", ".join(sorted([g.name for g in self.romantically_attracted_to_genders])) or "N/S"
        if self.is_on_aromantic_spectrum: romantic_attraction_str = "Spettro Aromantico"
        relationship_status_name = self.relationship_status.display_name_it(); school_level_name = self.current_school_level.display_name_it()
        aspiration_name = self.aspiration.display_name_it() if self.aspiration else "Nessuna"
        needs_summary = "; ".join([f"{nobj.display_name()}: {nobj.get_value():.0f}" for nobj in sorted(self.needs.values(), key=lambda x: x.get_value())[:3]]) if self.needs else "N/D"
        current_action_str = self.current_action.action_type_name if self.current_action else "Nessuna"
        current_action_progress = f"({self.current_action.get_progress_percentage():.0%})" if self.current_action and self.current_action.is_started else ""
        queue_size = len(self.action_queue)
        return (f"Character(ID: {self.npc_id}, Nome: \"{self.name}\", Genere: {gender_name}, Età: {age_in_years_str} anni ({life_stage_name})\n"
                f"  Scuola: {school_level_name}, Aspirazione: {aspiration_name} ({self.aspiration_progress:.0%})\n"
                f"  Stato Sent.: {relationship_status_name}, Interessi: {interest_names}\n"
                f"  Attr. Sessuale: {sexual_attraction_str}, Attr. Romantica: {romantic_attraction_str}\n"
                f"  Bisogni (Top Bassi): [{needs_summary}]\n"
                f"  Azione: {current_action_str} {current_action_progress}, Coda: {queue_size}, Occupato: {self.is_busy})")

