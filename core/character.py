# core/character.py
import collections
from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, Set, Type

# Import Enum
from core.enums import *

# Import Config e Settings
from core.config import time_config, npc_config
from core import settings

# --- IMPORT PER L'ESECUZIONE (FUORI DA TYPE_CHECKING) ---
from core.modules.lifestages.child_life_stage import ChildLifeStage
from core.modules.memory.memory_system import MemorySystem
from core.modules.moodlets.moodlet_manager import MoodletManager
from core.modules.skills.skill_system import SkillManager
from core.world.ATHDateTime.ATHDateTime import ATHDateTime
from core.utils.anthalys_circadian_model import AnthalysCircadianModel

# --- IMPORT SOLO PER IL TYPE CHECKING (PER ROMPERE I CICLI) ---
if TYPE_CHECKING:
    from core.simulation import Simulation
    from core.world.location import Location
    from core.modules.time_manager import TimeManager
    from core.modules.actions.action_base import BaseAction
    from core.AI.ai_decision_maker import AIDecisionMaker
    from core.modules.memory.memory_definitions import Problem
    from core.modules.lifestages.base_life_stage import BaseLifeStage
    from core.modules.traits.base_trait import BaseTrait
    from core.modules.needs.need_base import BaseNeed

# Dataclass per le relazioni
@dataclass
class RelationshipInfo:
    target_npc_id: str
    type: RelationshipType
    score: int = 0
    # Nota: display_name_it richiede gender, usiamo un default o lo rimuoviamo da qui
    def __str__(self): return f"({self.type.name} con {self.target_npc_id}, Score: {self.score})"

# --- MAPPE DI CLASSI ---
# Importiamo le classi specifiche prima di usarle nelle mappe
from core.modules.traits import *
TRAIT_TYPE_TO_CLASS_MAP: Dict[TraitType, Type['BaseTrait']] = {
    TraitType.ACTIVE: ActiveTrait, TraitType.BOOKWORM: BookwormTrait, TraitType.GLUTTON: GluttonTrait,
    TraitType.LONER: LonerTrait, TraitType.AMBITIOUS: AmbitiousTrait, TraitType.LAZY: LazyTrait,
    TraitType.SOCIAL: SocialTrait, TraitType.CREATIVE: CreativeTrait, TraitType.CHILDISH: ChildishTrait,
    TraitType.PLAYFUL: PlayfulTrait, TraitType.PARTY_ANIMAL: PartyAnimalTrait, 
    TraitType.UNINHIBITED: UninhibitedTrait, TraitType.GOOD: GoodTrait, 
    TraitType.ARTISTIC: ArtisticTrait, TraitType.CHARMER: CharmerTrait, TraitType.SHY: ShyTrait,
}

from core.modules.needs.common_needs import *
NEED_TYPE_TO_CLASS_MAP: Dict[NeedType, Type['BaseNeed']] = {
    NeedType.HUNGER: HungerNeed, NeedType.ENERGY: EnergyNeed, NeedType.SOCIAL: SocialNeed, NeedType.FUN: FunNeed,
    NeedType.HYGIENE: HygieneNeed, NeedType.BLADDER: BladderNeed, NeedType.INTIMACY: IntimacyNeed,
    NeedType.COMFORT: ComfortNeed, NeedType.ENVIRONMENT: EnvironmentNeed, NeedType.SAFETY: SafetyNeed,
    NeedType.CREATIVITY: CreativityNeed, NeedType.LEARNING: LearningNeed, NeedType.SPIRITUALITY: SpiritualityNeed,
    NeedType.AUTONOMY: AutonomyNeed, NeedType.ACHIEVEMENT: AchievementNeed, NeedType.THIRST: ThirstNeed,
    NeedType.STRESS: StressNeed,
}

from core.modules.lifestages import *
LIFESTAGE_TYPE_TO_CLASS_MAP: Dict[LifeStage, Type['BaseLifeStage']] = {
    LifeStage.CHILD: ChildLifeStage,
    # Aggiungi qui le altre classi LifeStage quando le crei
}

    
class Character:
    def __init__(self,
                npc_id: str, name: str, initial_gender: Gender,
                initial_birth_date: 'ATHDateTime',
                is_player_character: bool = False,
                initial_aspiration: Optional[AspirationType] = None,
                initial_interests: Optional[Set[Interest]] = None,
                initial_is_on_asexual_spectrum: bool = False, 
                initial_is_on_aromantic_spectrum: bool = False,
                initial_location_id: Optional[str] = None,
                initial_lod: LODLevel = LODLevel.HIGH,
                initial_logical_x: int = 0, 
                initial_logical_y: int = 0,
                initial_relationship_status: RelationshipStatus = RelationshipStatus.SINGLE,
                initial_romantically_attracted_to_genders: Optional[Set[Gender]] = None,
                initial_school_level: SchoolLevel = SchoolLevel.NONE,
                initial_sexually_attracted_to_genders: Optional[Set[Gender]] = None,
                initial_traits: Optional[Set[TraitType]] = None,
            ):

        # Validazioni
        if initial_aspiration is not None and not isinstance(initial_aspiration, AspirationType): raise ValueError("initial_aspiration non valida")
        if not isinstance(initial_gender, Gender): raise ValueError(f"initial_gender per {name} non valido")
        if not isinstance(initial_relationship_status, RelationshipStatus): raise ValueError("initial_relationship_status non valido")
        if not isinstance(initial_school_level, SchoolLevel): raise ValueError("initial_school_level non valido")

        # Attributi Base e di Stato
        self.npc_id: str = npc_id; 
        self.name: str = name
        self.gender: Gender = initial_gender; 
        self.birth_date: 'ATHDateTime' = initial_birth_date
        self.is_player_character: bool = is_player_character

        # --- CORREZIONE ARCHITETTURALE ---
        # Contenitori e Sistemi Interni
        self.traits: Dict[TraitType, BaseTrait] = {}
        self.needs: Dict[NeedType, BaseNeed] = {}
        self.action_queue: collections.deque['BaseAction'] = collections.deque()
        self.current_action: Optional['BaseAction'] = None
        self.current_problem: Optional['Problem'] = None
        self.life_stage_obj: Optional[BaseLifeStage] = None 
        self.life_stage: Optional[LifeStage] = None; 

        # L'IA viene assegnata dall'esterno, dopo la creazione.
        self.ai_decision_maker: Optional['AIDecisionMaker'] = None
        self.memory_system: MemorySystem = MemorySystem(self)
        self.moodlet_manager: MoodletManager = MoodletManager(self)
        self.skill_manager: 'SkillManager' = SkillManager(self)

        # Esecuzione dei Metodi di Inizializzazione
        self._initialize_traits(initial_traits or set())
        self._initialize_needs()


        self.is_busy: bool = False
        self.cognitive_load: float = 0.0; 
        self.lod: LODLevel = initial_lod

        # Personalità e Relazioni
        self.aspiration: Optional[AspirationType] = initial_aspiration
        self.aspiration_progress: float = 0.0
        self._interests: Set[Interest] = {i for i in (initial_interests or set()) if isinstance(i, Interest)}
        self.sexually_attracted_to_genders: Set[Gender] = {g for g in (initial_sexually_attracted_to_genders or set()) if isinstance(g, Gender)}
        self.romantically_attracted_to_genders: Set[Gender] = {g for g in (initial_romantically_attracted_to_genders or set()) if isinstance(g, Gender)}
        self.is_on_asexual_spectrum: bool = initial_is_on_asexual_spectrum
        self.is_on_aromantic_spectrum: bool = initial_is_on_aromantic_spectrum
        self.relationship_status: RelationshipStatus = initial_relationship_status
        self.relationships: Dict[str, RelationshipInfo] = {}

        # Mondo e Posizione
        self.current_location_id: Optional[str] = initial_location_id
        self.logical_x: int = initial_logical_x; self.logical_y: int = initial_logical_y
        
        # Scuola e Lavoro
        self.current_school_level: SchoolLevel = initial_school_level
        self.highest_school_level_completed: SchoolLevel = SchoolLevel.NONE

        # Stato Interazioni
        self.pending_intimacy_proposal_from: Optional[str] = None
        self.pending_intimacy_target_accepted: Optional[str] = None
        self.last_intimacy_proposal_tick: int = -99999

        # Ogni personaggio ha il suo modello di ritmo biologico
        self.circadian_model = AnthalysCircadianModel()

        if settings.DEBUG_MODE: print(f"  [Character CREATED] {self!s}")

    def _initialize_traits(self, initial_trait_types: Set[TraitType]):
        for trait_type_enum in initial_trait_types:
            trait_class = TRAIT_TYPE_TO_CLASS_MAP.get(trait_type_enum)
            if trait_class:
                trait_instance = trait_class(
                    character_owner=self,
                    trait_type=trait_type_enum
                )
                self.traits[trait_type_enum] = trait_instance
            elif settings.DEBUG_MODE:
                print(f"    [Character Traits WARN - {self.name}] Classe non trovata per {trait_type_enum.name}")

    def _initialize_needs(self):
        """Inizializza gli oggetti bisogno dell'NPC."""
        # Itera sulla mappa delle classi dei bisogni, è più efficiente
        for need_type, need_class in NEED_TYPE_TO_CLASS_MAP.items():
            # Ora usiamo 'need_type' e 'need_class' che sono definite nel loop
            self.needs[need_type] = need_class(
                character_owner=self,
                p_need_type=need_type
            )

    def _calculate_and_set_life_stage(self, current_time: 'ATHDateTime'):
        age_days = self.get_age_in_days(current_time)
        new_stage_enum = None
        sorted_thresholds = sorted(npc_config.LIFE_STAGE_AGE_THRESHOLDS_DAYS.items(), key=lambda item: item[1])
        for stage_key, threshold in reversed(sorted_thresholds):
            if age_days >= threshold:
                try:
                    new_stage_enum = LifeStage[stage_key]
                    break
                except KeyError: continue
        
        if new_stage_enum and self.life_stage != new_stage_enum:
            self.life_stage = new_stage_enum
            life_stage_class = LIFESTAGE_TYPE_TO_CLASS_MAP.get(new_stage_enum)
            if life_stage_class:
                self.life_stage_obj = life_stage_class(self)
                if hasattr(self.life_stage_obj, 'on_enter_stage'):
                    self.life_stage_obj.on_enter_stage()
                if settings.DEBUG_MODE:
                    print(f"  [Character LIFE STAGE] {self.name} è ora {self.life_stage_obj.display_name}.")

    def set_location(self, new_location_id: str, simulation: 'Simulation'):
        if self.current_location_id:
            old_loc = simulation.get_location_by_id(self.current_location_id)
            if old_loc: old_loc.remove_npc(self.npc_id)
        self.current_location_id = new_location_id
        new_loc = simulation.get_location_by_id(new_location_id)
        if new_loc:
            new_loc.add_npc(self.npc_id)
            if settings.DEBUG_MODE: print(f"  [Character Location - {self.name}] Spostato a '{new_loc.name}'")
        elif settings.DEBUG_MODE: print(f"  [Character Location WARN - {self.name}] Locazione non esistente: {new_location_id}")

    def get_current_location(self, simulation: 'Simulation') -> Optional['Location']:
        return simulation.get_location_by_id(self.current_location_id) if self.current_location_id else None

    def has_trait(self, trait_type: TraitType) -> bool:
        return trait_type in self.traits

    def get_trait(self, trait_type: TraitType) -> Optional['BaseTrait']:
        return self.traits.get(trait_type)

    def get_trait_types(self) -> Set[TraitType]:
        return set(self.traits.keys())

    def get_age_in_days(self, current_time: 'ATHDateTime') -> int:
        """Calcola l'età dell'NPC in giorni basandosi sulla data corrente."""
        age_interval = current_time.diff(self.birth_date)
        
        # Usa getattr per essere sicuro, nel caso il nome nella tua libreria sia .days
        # Prova prima 'total_days', se non esiste usa 'days'.
        total_days = getattr(age_interval, 'total_days', None)
        if total_days is not None:
            return total_days
        
        return getattr(age_interval, 'days', 0)

    def get_age_in_years_float(self, current_time: 'ATHDateTime') -> float:
        age_in_days = self.get_age_in_days(current_time)
        return age_in_days / time_config.DXY if time_config.DXY > 0 else 0.0

    def get_interests(self) -> Set[Interest]: return self._interests.copy()
    def add_interest(self, i: Interest) -> bool:
        if isinstance(i, Interest) and len(self._interests) < npc_config.MAX_NPC_ACTIVE_INTERESTS and i not in self._interests:
            self._interests.add(i); return True
        return False
    def remove_interest(self, i: Interest) -> bool:
        try: self._interests.remove(i); return True
        except KeyError: return False

    def get_sexual_attraction(self) -> Set[Gender]: return self.sexually_attracted_to_genders.copy()
    def get_romantic_attraction(self) -> Set[Gender]: return self.romantically_attracted_to_genders.copy()
    def is_asexual(self) -> bool: return self.is_on_asexual_spectrum
    def is_aromantic(self) -> bool: return self.is_on_aromantic_spectrum
    def get_relationship_status(self) -> RelationshipStatus: return self.relationship_status
    def set_relationship_status(self, new_status: RelationshipStatus):
        if isinstance(new_status, RelationshipStatus): self.relationship_status = new_status

    def get_relationships(self) -> Dict[str, RelationshipInfo]: return self.relationships.copy()
    def get_relationship_with(self, target_npc_id: str) -> Optional[RelationshipInfo]: return self.relationships.get(target_npc_id)

    def update_relationship(self, target_npc_id: str, new_type: RelationshipType, score_change: int = 0, new_score: Optional[int] = None):
        if not isinstance(new_type, RelationshipType): return
        if target_npc_id not in self.relationships:
            self.relationships[target_npc_id] = RelationshipInfo(target_npc_id, new_type, 0)
        rel_info = self.relationships[target_npc_id]
        rel_info.type = new_type
        if new_score is not None:
            rel_info.score = max(-100, min(100, new_score))
        else:
            rel_info.score = max(-100, min(100, rel_info.score + score_change))
            
    def get_need_value(self, need_type: NeedType) -> Optional[float]:
        need_object = self.needs.get(need_type)
        return need_object.get_value() if need_object else None

    def change_need_value(self, need_type: NeedType, amount: float, is_decay_event: bool = False):
        need_object = self.needs.get(need_type)
        if need_object:
            need_object.change_value(amount, is_decay_event)

    @property
    def overall_mood(self) -> int:
        return self.moodlet_manager.get_total_emotional_impact() if self.moodlet_manager else 0

    def update_needs(self, time_manager: 'TimeManager', elapsed_ticks: int):
        """
        Aggiorna tutti i bisogni dell'NPC in base ai tassi di decadimento,
        ai modificatori di età/genere e al ritmo circadiano.
        """
        if not self.needs or elapsed_ticks <= 0:
            return

        # Otteniamo i dati temporali e i modificatori una sola volta
        current_hour_float = time_manager.get_current_hour_float()
        lifestage_modifiers = self.life_stage_obj.get_need_decay_modifiers() if self.life_stage_obj else {}

        current_action = self.current_action

        # Itera su ogni bisogno che l'NPC possiede
        for need_type, need_obj in self.needs.items():
            # Se c'è un'azione in corso che sta già gestendo questo bisogno,
            # SALTA il suo decadimento passivo per questo tick.
            if current_action and current_action.manages_need == need_type:
                continue

            # 1. Prende il tasso di decadimento base PER TICK dalla configurazione
            decay_per_tick = npc_config.NEED_DECAY_RATES_PER_TICK.get(need_type, 0.0)
            
            # 2. Applica i modificatori
            lifestage_modifier = lifestage_modifiers.get(need_type, 1.0)
            
            circadian_modifier = 1.0
            if need_type == NeedType.ENERGY:
                # Ottieni il valore del ritmo circadiano (-1 a +1) dal nostro adattatore
                rhythm_value = self.circadian_model.get_rhythm_value(current_hour_float)
                
                # Convertiamo il ritmo in un modificatore di decadimento:
                # Se il ritmo è alto (+1, massima veglia), il modificatore è 1.5 (calo veloce)
                # Se il ritmo è basso (-1, massima sonnolenza), il modificatore è 0.1 (calo lento/quasi nullo)
                circadian_modifier = ((rhythm_value + 1) / 2) * 1.4 + 0.1 # Scala il range a [0.1, 1.5]
            
            # 3. Il calcolo finale del cambiamento
            change_amount = (decay_per_tick * circadian_modifier) * elapsed_ticks
            
            if change_amount != 0:
                need_obj.change_value(change_amount, is_decay_event=True)

        # 4. Logica per il carico cognitivo (stress) - invariata
        needs_to_average = [n.get_value() for t, n in self.needs.items() if t != NeedType.STRESS]
        avg_need_level = sum(needs_to_average) / len(needs_to_average) if needs_to_average else 100.0
        
        if avg_need_level < npc_config.COGNITIVE_LOAD_THRESHOLD:
             self.cognitive_load += npc_config.COGNITIVE_LOAD_GAIN_RATE * elapsed_ticks
        else:
             self.cognitive_load -= npc_config.COGNITIVE_LOAD_DECAY_RATE * elapsed_ticks
        
        self.cognitive_load = max(0.0, min(1.0, self.cognitive_load))
        
        # Logica Moodlet
        # ... (logica moodlet come da tua implementazione) ...

    def add_action_to_queue(self, action: 'BaseAction'):
        from core.modules.actions.action_base import BaseAction
        if not isinstance(action, BaseAction): return
        self.action_queue.append(action)
        if settings.DEBUG_MODE: 
            print(f"  [Character Action - {self.name}] Azione '{action.action_type_name}' AGGIUNTA. Coda: {len(self.action_queue)}.")

    def _start_action(self, action: 'BaseAction', simulation_context: 'Simulation') -> bool:
        if action.is_valid():
            self.current_action = action
            self.current_action.on_start()
            self.is_busy = True
            return True
        return False

    def update_action(self, time_manager: 'TimeManager', simulation_context: 'Simulation'):
        if self.current_action:
            if self.current_action.is_started and not self.current_action.is_finished and not self.current_action.is_interrupted:
                self.current_action.execute_tick()
            if self.current_action.is_finished or self.current_action.is_interrupted:
                completed_action = self.current_action
                self.current_action = None; self.is_busy = False
                if simulation_context.consequence_analyzer:
                    simulation_context.consequence_analyzer.analyze_action_and_create_memory(self, completed_action)
                if settings.DEBUG_MODE:
                    status_log = "INTERROTTA" if completed_action.is_interrupted else "COMPLETATA"
                    print(f"  [Character Action - {self.name}] Azione '{completed_action.action_type_name}' {status_log}. NPC libero.")

        if not self.is_busy and self.action_queue:
            next_action_from_queue = self.action_queue.popleft()
            self._start_action(next_action_from_queue, simulation_context)

        if not self.is_busy and not self.action_queue and self.ai_decision_maker:
            self.ai_decision_maker.decide_next_action(time_manager, simulation_context)

    def __str__(self) -> str:
        """Restituisce una rappresentazione testuale dell'oggetto Character."""
        # Formattiamo la data di nascita invece di tentare di calcolare l'età
        birth_date_str = self.birth_date.format("d F Y") # Usa il formato che preferisci
        
        return (f"Character(ID: {self.npc_id}, Nome: \"{self.name}\", Nato/a il: {birth_date_str})")
