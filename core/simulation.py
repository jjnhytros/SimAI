# core/simulation.py
from typing import List, Dict, Any, Set, Optional # Aggiungi Optional e gli altri tipi generici
import random

# Importiamo le classi e le Enum necessarie
from core.character import Character
from core.enums import *
from core import settings
from core.modules.time_manager import TimeManager
from core.world.location import Location
from core.world.game_object import GameObject
from core.AI import AICoordinator
from core.AI.lod_manager import LODManager
from core.AI.social_manager import SocialManager
from core.world.weather_manager import WeatherManager

class Simulation:
    def __init__(self):
        if settings.DEBUG_MODE: print("  [Simulation INIT] Inizializzazione Simulation...")
        self.time_manager = TimeManager()
        if settings.DEBUG_MODE: print(f"  [Simulation INIT] TimeManager creato. Ora: {self.time_manager.get_formatted_datetime_string()}")

        self.current_tick: int = 0
        self.is_running: bool = False
        self.npcs: Dict[str, Character] = {}
        self.social_hubs: List[Dict] = []
        self.time_manager = TimeManager()
        self.weather_manager = WeatherManager()
        self.lod_manager = LODManager(self) # Istanzia LODManager qui

        self.locations: Dict[str, Location] = {}
        self.world_objects: Dict[str, GameObject] = {}
        self.game_speed: float = 1.0
        self.default_starting_location_id: Optional[str] = None
        self._initialize_world_data()
        self.ai_coordinator = AICoordinator(self)
        self.social_manager = SocialManager(self)
        self.ai_coordinator = AICoordinator(self)
        
        if settings.DEBUG_MODE: print("  [Simulation INIT] AICoordinator creato.")
        if settings.DEBUG_MODE: print("  [Simulation INIT] Simulation inizializzata.")

    def _initialize_world_data(self):
        self.social_hubs = [
            {"hub_id": "hub_bibli_club", "name": "Club Libro Biblio", "activity_type_descriptor": "Incontro Settimanale", "location_category": LocationType.PUBLIC_LIBRARY, "associated_interests": {Interest.READING, Interest.HISTORY}},
            {"hub_id": "hub_galleria_visioni", "name": "Galleria 'Visioni'", "activity_type_descriptor": "Esposizione", "location_category": LocationType.MUSEUM, "associated_interests": {Interest.VISUAL_ARTS, Interest.PHOTOGRAPHY}},
        ]
        if settings.DEBUG_MODE: print(f"  [Simulation INIT] Inizializzati {len(self.social_hubs)} social hub.")

        self._create_test_locations_and_objects()

    def _create_test_locations_and_objects(self):
        """Crea alcune locazioni e oggetti di esempio per il test."""
        cucina_max = Location(
            location_id="max_casa_cucina", 
            name="Cucina di Max", 
            location_type=LocationType.RESIDENTIAL_KITCHEN,
            logical_width=10, # Esempio: cucina 10x8 celle
            logical_height=8
        )
        # Assegna coordinate logiche agli oggetti (come prima, assicurati siano nei limiti)
        frigo = GameObject(object_id="frigo_max_01", name="Frigorifero", object_type=ObjectType.REFRIGERATOR, is_water_source=True, logical_x=1, logical_y=1)
        fornelli = GameObject(object_id="fornelli_max_01", name="Fornelli", object_type=ObjectType.STOVE, logical_x=3, logical_y=1)
        lavandino_cucina = GameObject(object_id="lavandino_cucina_max_01", name="Lavandino Cucina", object_type=ObjectType.SINK, is_water_source=True, logical_x=5, logical_y=1)
        
        cucina_max.add_object(frigo)
        cucina_max.add_object(fornelli)
        cucina_max.add_object(lavandino_cucina)
        self.add_location(cucina_max)
        self.world_objects[frigo.object_id] = frigo
        self.world_objects[fornelli.object_id] = fornelli
        self.world_objects[lavandino_cucina.object_id] = lavandino_cucina

        soggiorno_max = Location(
            location_id="max_casa_soggiorno", 
            name="Soggiorno di Max", 
            location_type=LocationType.RESIDENTIAL_LIVING_ROOM,
            logical_width=15, # Esempio: soggiorno 15x10 celle
            logical_height=10
        )
        tv_max = GameObject(object_id="tv_max_01", name="TV", object_type=ObjectType.TV, provides_fun_activities=[FunActivityType.WATCH_TV], logical_x=2, logical_y=3)
        divano_max = GameObject(object_id="divano_max_01", name="Divano", object_type=ObjectType.SOFA, comfort_value=7, logical_x=4, logical_y=3)
        libreria_max = GameObject(object_id="libreria_max_01", name="Libreria", object_type=ObjectType.BOOKSHELF, provides_fun_activities=[FunActivityType.READ_BOOK_FOR_FUN], logical_x=6, logical_y=3)
        
        soggiorno_max.add_object(tv_max)
        soggiorno_max.add_object(divano_max)
        soggiorno_max.add_object(libreria_max)
        self.add_location(soggiorno_max)
        self.world_objects[tv_max.object_id] = tv_max
        self.world_objects[divano_max.object_id] = divano_max
        self.world_objects[libreria_max.object_id] = libreria_max

        bagno_max = Location(
            location_id="max_casa_bagno", 
            name="Bagno di Max", 
            location_type=LocationType.RESIDENTIAL_BATHROOM,
            logical_width=8, # Esempio: bagno 8x6 celle
            logical_height=6
        )
        wc_max = GameObject(object_id="wc_max_01", name="WC", object_type=ObjectType.TOILET, logical_x=1, logical_y=5)
        doccia_max = GameObject(object_id="doccia_max_01", name="Doccia", object_type=ObjectType.SHOWER, logical_x=3, logical_y=5)
        
        bagno_max.add_object(wc_max)
        bagno_max.add_object(doccia_max)
        self.add_location(bagno_max)
        self.world_objects[wc_max.object_id] = wc_max
        self.world_objects[doccia_max.object_id] = doccia_max

        if settings.DEBUG_MODE: print(f"  [Simulation INIT] Create {len(self.locations)} locazioni di test con oggetti e coordinate logiche.")

    def add_location(self, location: Location):
        if location.location_id not in self.locations:
            self.locations[location.location_id] = location

    def get_location_by_id(self, location_id: str) -> Optional[Location]:
        return self.locations.get(location_id)

    def add_npc(self, new_npc: Character):
        if not isinstance(new_npc, Character):
            if settings.DEBUG_MODE: print(f"  [Simulation AddNPC WARN] Tentativo di aggiungere oggetto non Character: {type(new_npc)}")
            return
        if new_npc.npc_id in self.npcs:
            if settings.DEBUG_MODE: print(f"  [Simulation AddNPC WARN] NPC '{new_npc.name}' (ID: {new_npc.npc_id}) già presente nella simulazione.")
            return

        self.npcs[new_npc.npc_id] = new_npc

        loc_id_to_assign: Optional[str] = new_npc.current_location_id

        if not loc_id_to_assign:
            if self.default_starting_location_id and self.default_starting_location_id in self.locations:
                loc_id_to_assign = self.default_starting_location_id
                if settings.DEBUG_MODE: print(f"    [Simulation AddNPC] NPC '{new_npc.name}' userà la locazione di default della simulazione: '{loc_id_to_assign}'.")
            elif self.locations:
                loc_id_to_assign = list(self.locations.keys())[0]
                if settings.DEBUG_MODE: print(f"    [Simulation AddNPC WARN] Locazione di default non valida o non impostata. NPC '{new_npc.name}' aggiunto alla prima locazione disponibile: '{loc_id_to_assign}'.")
            else:
                if settings.DEBUG_MODE: print(f"    [Simulation AddNPC ERROR] Nessuna locazione definita nella simulazione. Impossibile piazzare '{new_npc.name}'.")

        if loc_id_to_assign and loc_id_to_assign in self.locations:
            new_npc.set_location(loc_id_to_assign, self)
        elif loc_id_to_assign:
             if settings.DEBUG_MODE: print(f"    [Simulation AddNPC ERROR] Locazione specificata '{loc_id_to_assign}' per '{new_npc.name}' non trovata.")
             new_npc.current_location_id = None

        if settings.DEBUG_MODE:
            final_loc_name = "Nessuna (Errore)"
            if new_npc.current_location_id:
                loc_instance = self.get_location_by_id(new_npc.current_location_id)
                if loc_instance:
                    final_loc_name = loc_instance.name

            print(f"  [Simulation] NPC '{new_npc.name}' (ID: {new_npc.npc_id}) aggiunto. Locazione Attuale: {final_loc_name}. Totale NPC: {len(self.npcs)}")

    def get_npc_by_id(self, npc_id_to_find: str) -> Optional[Character]: return self.npcs.get(npc_id_to_find)

    def set_player_character(self, npc_id: str):
        """Imposta l'NPC specificato come personaggio del giocatore."""
        if npc_id in self.npcs:
            self.player_character_id = npc_id
            if settings.DEBUG_MODE:
                print(f"  [Simulation] Personaggio del giocatore impostato su: {self.npcs[npc_id].name} (ID: {npc_id})")
        elif settings.DEBUG_MODE:
            print(f"  [Simulation WARN] Tentativo di impostare un player character non esistente: {npc_id}")

    def get_player_character(self) -> Optional[Character]:
        """Restituisce l'istanza del personaggio del giocatore, se impostata."""
        if self.player_character_id:
            return self.get_npc_by_id(self.player_character_id)
        return None

    def find_social_hubs(self, target_interests: Set[Interest]) -> list[dict]:
        if not target_interests: return []
        suggested = []
        for hub in self.social_hubs:
            if hub.get("associated_interests") and hub["associated_interests"].intersection(target_interests): suggested.append(hub)
        return suggested

    def get_eligible_dating_candidates(self, requesting_npc: Character, search_preferences: Optional[Dict[str, Any]] = None) -> list[Character]:
        if not requesting_npc: return []
        if requesting_npc.is_asexual() and requesting_npc.is_aromantic() and not (search_preferences and search_preferences.get("explicitly_seeking_qpr")): return []
        eligible_candidates: list[Character] = []
        req_npc_age_days = requesting_npc.get_age_in_days()
        min_cand_age_days = settings.DATING_CANDIDATE_MIN_AGE_DAYS
        max_age_diff_days = settings.DATING_CANDIDATE_MAX_AGE_DIFFERENCE_YEARS * settings.DXY
        genders_from_prefs: Optional[Set[Gender]] = None
        if search_preferences:
            genders_from_prefs_value = search_preferences.get("target_genders")
            if isinstance(genders_from_prefs_value, set): # Assicurati che sia un set se fornito
                genders_from_prefs = genders_from_prefs_value
            elif genders_from_prefs_value is not None and settings.DEBUG_MODE:
                # Logga un avviso se "target_genders" è fornito ma non è un set
                print(f"  [WARN - DatingCandidates] 'target_genders' in search_preferences per {requesting_npc.name} non è un set, ma {type(genders_from_prefs_value)}. Verrà ignorato.")
        if genders_from_prefs is not None:
            preferred_target_genders: Set[Gender] = genders_from_prefs
        else:
            preferred_target_genders: Set[Gender] = requesting_npc.get_sexual_attraction()

        preference_for_asexual_partner = search_preferences.get("partner_is_asexual") if search_preferences else None
        preference_for_aromantic_partner = search_preferences.get("partner_is_aromantic") if search_preferences else None

        for cand_npc in self.npcs.values():
            if cand_npc.npc_id == requesting_npc.npc_id: continue
            cand_age_days = cand_npc.get_age_in_days()
            if cand_age_days < min_cand_age_days: continue
            if cand_npc.life_stage not in {LifeStage.EARLY_ADULTHOOD, LifeStage.MIDDLE_ADULTHOOD, LifeStage.LATE_ADULTHOOD}: continue
            if abs(cand_age_days - req_npc_age_days) > max_age_diff_days: continue
            if cand_npc.get_relationship_status() not in {RelationshipStatus.SINGLE, RelationshipStatus.OPEN_RELATIONSHIP}: continue
            
            # Ora preferred_target_genders è garantito essere un Set[Gender]
            if not (cand_npc.gender in preferred_target_genders): continue
            
            if preference_for_asexual_partner is True and not cand_npc.is_asexual(): continue
            if preference_for_asexual_partner is False and cand_npc.is_asexual(): continue
            if not requesting_npc.is_aromantic() and (preference_for_aromantic_partner is True and not cand_npc.is_aromantic() or preference_for_aromantic_partner is False and cand_npc.is_aromantic()): continue
            
            compatible_orientation = False
            req_is_ace = requesting_npc.is_asexual()
            req_is_aro = requesting_npc.is_aromantic()
            cand_is_ace = cand_npc.is_asexual()
            cand_is_aro = cand_npc.is_aromantic()
            cand_sexual_attraction = cand_npc.get_sexual_attraction()
            cand_romantic_attraction = cand_npc.get_romantic_attraction()

            if not req_is_ace and not cand_is_ace:
                if requesting_npc.gender in cand_sexual_attraction: compatible_orientation = True
            elif not req_is_aro and not cand_is_aro: # Considera anche l'attrazione romantica se uno o entrambi sono asessuali
                if requesting_npc.gender in cand_romantic_attraction: compatible_orientation = True
            # Se entrambi sono sullo spettro ace E aro, la compatibilità potrebbe basarsi su altri fattori (QPR)
            # Questa logica potrebbe necessitare di ulteriore affinamento per QPR. Per ora, la escludiamo se non c'è attrazione sessuale/romantica.
            
            if not compatible_orientation: continue
            
            eligible_candidates.append(cand_npc)
        return eligible_candidates

    def get_potential_friend_candidates(self, requesting_npc: Character) -> list[Character]:
        if not requesting_npc: return []
        potential_friends: list[Character] = []; requesting_npc_age_days = requesting_npc.get_age_in_days()
        min_candidate_age_days = settings.FRIEND_CONNECT_MIN_ACCESS_AGE_DAYS
        max_age_diff_days = settings.FRIEND_MAX_AGE_DIFFERENCE_YEARS * settings.DXY
        for candidate_npc in self.npcs.values():
            if candidate_npc.npc_id == requesting_npc.npc_id: continue
            candidate_age_days = candidate_npc.get_age_in_days()
            if candidate_age_days < min_candidate_age_days: continue
            if abs(candidate_age_days - requesting_npc_age_days) > max_age_diff_days: continue
            potential_friends.append(candidate_npc)
        return potential_friends

    def find_available_social_target(self, requesting_npc: Character) -> Optional[Character]:
        if not self.npcs or len(self.npcs) <= 1 or not requesting_npc.current_location_id:
            return None

        requesting_npc_location = self.get_location_by_id(requesting_npc.current_location_id)
        if not requesting_npc_location: return None

        possible_targets = []
        for npc_id in requesting_npc_location.npcs_present_ids:
            if npc_id == requesting_npc.npc_id:
                continue

            npc = self.get_npc_by_id(npc_id)
            if not npc: continue

            if npc.current_action and npc.current_action.action_type_name == "ACTION_SLEEP": continue
            if npc.is_busy and npc.current_action and not npc.current_action.is_interruptible: continue

            possible_targets.append(npc)

        if not possible_targets:
            return None
        preferred_targets = []; other_targets = []
        for target in possible_targets:
            relationship_info = requesting_npc.get_relationship_with(target.npc_id)
            if relationship_info and relationship_info.score > 0 and relationship_info.type not in {RelationshipType.ENEMY_RIVAL, RelationshipType.ENEMY_DISLIKED}:
                preferred_targets.append({"npc": target, "score": relationship_info.score})
            elif not relationship_info or relationship_info.type not in {RelationshipType.ENEMY_RIVAL, RelationshipType.ENEMY_DISLIKED}:
                other_targets.append(target)
        if preferred_targets:
            preferred_targets.sort(key=lambda x: x["score"], reverse=True)
            chosen_target = preferred_targets[0]["npc"]
            if settings.DEBUG_MODE: print(f"    [Find Target - {requesting_npc.name}] Scelto target preferito (stessa locazione): {chosen_target.name}")
            return chosen_target
        elif other_targets:
            chosen_target = random.choice(other_targets)
            if settings.DEBUG_MODE: print(f"    [Find Target - {requesting_npc.name}] Scelto target casuale (stessa locazione): {chosen_target.name}")
            return chosen_target
        return None

    def _update_simulation_state(self):
        """
        Aggiorna lo stato di tutti gli elementi della simulazione per il tick corrente.
        Ora utilizza AICoordinator.
        """
        if not self.time_manager:
            if settings.DEBUG_MODE: print("    [Sim WARN] TimeManager non inizializzato!")
            self.current_tick += 1
            return

        self.time_manager.advance_time(self.game_speed) 
        self.weather_manager.update_weather()

        if settings.DEBUG_MODE and self.time_manager.get_current_minute() == 0 :
            print(f"      [SimTime] Ora: {self.time_manager.get_formatted_datetime_string()} (Tick Sim: {self.current_tick})")

        # Invece di ciclare sugli NPC e chiamare i loro metodi di update direttamente,
        # chiamiamo il metodo dell'AICoordinator.
        # Il 'time_delta' per update_all_npcs è il numero di tick trascorsi, che è 1 in questo caso.
        if self.ai_coordinator:
            self.ai_coordinator.update_all_npcs(time_delta=1) # Passiamo 1 perché questo metodo è chiamato per ogni tick
        else:
            # Fallback alla vecchia logica se ai_coordinator non fosse inizializzato (non dovrebbe succedere)
            if settings.DEBUG_MODE: print("    [Sim WARN] AICoordinator non disponibile! Uso logica di update NPC diretta.")
            is_new_day = (self.time_manager.get_current_hour() == 0 and
                            self.time_manager.get_current_minute() == 0 and
                            self.time_manager.total_ticks > 1)
            for npc in self.npcs.values():
                if npc:
                    npc.update_needs(self.time_manager, 1)
                    if is_new_day: npc._set_age_in_days(npc.get_age_in_days() + 1)
                    npc.update_action(self.time_manager, simulation_context=self)

        self.current_tick += 1

        # Ottieni la posizione del giocatore (questo è un esempio, adattalo)
        player_character = self.get_player_character() # Ipotetico metodo
        current_player_position = None
        if player_character:
            current_player_position = (float(player_character.logical_x), float(player_character.logical_y))

        # Aggiorna i LOD degli NPC
        if self.lod_manager:
            self.lod_manager.update_all_npcs_lod(current_player_position)

        # Aggiorna l'IA e le azioni degli NPC (l'IA potrebbe usare il LOD dell'NPC)
        if self.ai_coordinator:
            self.ai_coordinator.update_all_npcs(time_delta=1) # o i ticks effettivi

    def run(self, max_ticks: Optional[int] = None):
        if settings.DEBUG_MODE:
            print("  [Simulation RUN] Avvio del loop di simulazione...")
            if max_ticks:
                print(f"  [Simulation RUN] La simulazione girerà per un massimo di {max_ticks} tick.")
            else:
                print("  [Simulation RUN] La simulazione girerà indefinitamente (o fino a interruzione manuale Ctrl+C).")

        self.is_running = True

        try:
            while self.is_running:
                self._update_simulation_state()
                self._render_output()

                if max_ticks is not None and self.current_tick >= max_ticks:
                    if settings.DEBUG_MODE:
                        print(f"  [Simulation RUN] Raggiunto limite di {max_ticks} tick. Uscita elegante...")
                    self.is_running = False

                if settings.DEBUG_MODE and max_ticks:
                    import time
                    time.sleep(0.01)

        except KeyboardInterrupt:
            if settings.DEBUG_MODE:
                print("\n  [Simulation RUN] Loop interrotto da KeyboardInterrupt (Ctrl+C).")
            self.is_running = False
        finally:
            self._perform_cleanup()

    def _render_output(self):
        pass

    def _perform_cleanup(self):
        if settings.DEBUG_MODE:
            print("  [Simulation CLEANUP] Esecuzione pulizia finale...")
        print("------------------------------------")

if __name__ == '__main__':
    print("--- Test diretto di core/simulation.py ---")
    import sys
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    original_sys_path = list(sys.path)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    settings_imported_successfully = False
    try:
        from core import settings
        settings_imported_successfully = True
    except ImportError:
        print("  [Test Setup - simulation.py] WARN: Impossibile importare 'core.settings'. Uso un mock di emergenza.")
        class EmergencySettingsMock:
            DEBUG_MODE: bool = True
            DXY: int = 432
            MAX_NPC_ACTIVE_INTERESTS: int = 3
            LIFE_STAGE_AGE_THRESHOLDS_DAYS: dict = {
                "INFANCY": 0, "TODDLERHOOD": 1 * DXY, "EARLY_CHILDHOOD": 3 * DXY,
                "MIDDLE_CHILDHOOD": 6 * DXY, "ADOLESCENCE": 12 * DXY,
                "EARLY_ADULTHOOD": 20 * DXY, "MIDDLE_ADULTHOOD": 40 * DXY,
                "LATE_ADULTHOOD": 60 * DXY, "ELDERLY": 80 * DXY
            }
            AMORI_CURATI_PHASE1_ACCESS_MIN_AGE_YEARS: int = 18
            AMORI_CURATI_PHASE1_ACCESS_MIN_AGE_DAYS: int = AMORI_CURATI_PHASE1_ACCESS_MIN_AGE_YEARS * DXY
            AMORI_CURATI_PHASE2_ACCESS_MIN_AGE_YEARS: int = 25
            AMORI_CURATI_PHASE2_ACCESS_MIN_AGE_DAYS: int = AMORI_CURATI_PHASE2_ACCESS_MIN_AGE_YEARS * DXY
            DATING_CANDIDATE_MIN_AGE_YEARS: int = 18
            DATING_CANDIDATE_MIN_AGE_DAYS: int = DATING_CANDIDATE_MIN_AGE_YEARS * DXY
            DATING_CANDIDATE_MAX_AGE_DIFFERENCE_YEARS: int = 15
            FRIEND_CONNECT_MIN_ACCESS_AGE_YEARS: int = 14
            FRIEND_CONNECT_MIN_ACCESS_AGE_DAYS: int = FRIEND_CONNECT_MIN_ACCESS_AGE_YEARS * DXY
            FRIEND_MAX_AGE_DIFFERENCE_YEARS: int = 10
            MAX_MATCHMAKING_SUGGESTIONS: int = 3
            # Aggiungi qui altre costanti minime necessarie per il test di Character e Simulation
            NEED_MIN_VALUE: float = 0.0
            NEED_MAX_VALUE: float = 100.0
            NEED_DEFAULT_START_MIN: float = 50.0
            NEED_DEFAULT_START_MAX: float = 80.0
            NEED_CRITICAL_THRESHOLD: float = 10.0
            NEED_LOW_THRESHOLD: float = 25.0
            IXH = 60 # Minuti per ora, necessario per `update_needs`
            NEED_DECAY_RATES: dict = {} # Deve esistere, anche se vuoto per il mock

        settings = EmergencySettingsMock()

    settings.DEBUG_MODE = True
    if not hasattr(settings, 'DXY') or settings.DXY != 432:
        if settings.DEBUG_MODE: print(f"  [Test Setup - simulation.py] WARN: settings.DXY non corretto ({getattr(settings, 'DXY', 'Mancante')}). Imposto 432.")
        settings.DXY = 432
    if project_root not in original_sys_path and settings.DEBUG_MODE:
        print(f"  [Test Setup - simulation.py] Aggiunto al sys.path: {project_root}")
    if settings.DEBUG_MODE: print(f"  [Test Setup - simulation.py] Utilizzo DXY = {settings.DXY}")

    _critical_constants_defaults_for_test = {
        "MAX_NPC_ACTIVE_INTERESTS": 3,
        "LIFE_STAGE_AGE_THRESHOLDS_DAYS": {
            "INFANCY": 0, "TODDLERHOOD": 1*settings.DXY, "EARLY_CHILDHOOD": 3*settings.DXY,
            "MIDDLE_CHILDHOOD": 6*settings.DXY, "ADOLESCENCE": 12*settings.DXY,
            "EARLY_ADULTHOOD": 20*settings.DXY, "MIDDLE_ADULTHOOD": 40*settings.DXY,
            "LATE_ADULTHOOD": 60*settings.DXY, "ELDERLY": 80*settings.DXY
        },
        "AMORI_CURATI_PHASE1_ACCESS_MIN_AGE_YEARS": 18,
        "AMORI_CURATI_PHASE2_ACCESS_MIN_AGE_YEARS": 25,
        "DATING_CANDIDATE_MIN_AGE_YEARS": 18,
        "DATING_CANDIDATE_MAX_AGE_DIFFERENCE_YEARS": 15,
        "FRIEND_CONNECT_MIN_ACCESS_AGE_YEARS": 14,
        "FRIEND_MAX_AGE_DIFFERENCE_YEARS": 10,
        "MAX_MATCHMAKING_SUGGESTIONS": 3,
        "NEED_MIN_VALUE": 0.0, "NEED_MAX_VALUE": 100.0,
        "NEED_DEFAULT_START_MIN": 50.0, "NEED_DEFAULT_START_MAX": 80.0,
        "NEED_CRITICAL_THRESHOLD": 10.0, "NEED_LOW_THRESHOLD": 25.0, "IXH": 60,
        "NEED_DECAY_RATES": {nt.name: -1.0 for nt in NeedType} # Aggiungi default per tutti i bisogni
    }
    for const_name, default_value in _critical_constants_defaults_for_test.items():
        if not hasattr(settings, const_name):
            if settings.DEBUG_MODE: print(f"  [Test Setup - simulation.py] WARN: settings.{const_name} non trovato. Uso default.")
            if isinstance(default_value, dict) and "TODDLERHOOD" in default_value:
                 setattr(settings, const_name, {k: (v if k=="INFANCY" else v * settings.DXY // settings.DXY) for k,v in default_value.items()})
            else:
                setattr(settings, const_name, default_value)
    if hasattr(settings, 'DXY'):
        _dependent_day_constants_map = {
            "AMORI_CURATI_PHASE1_ACCESS_MIN_AGE_DAYS": "AMORI_CURATI_PHASE1_ACCESS_MIN_AGE_YEARS",
            "AMORI_CURATI_PHASE2_ACCESS_MIN_AGE_DAYS": "AMORI_CURATI_PHASE2_ACCESS_MIN_AGE_YEARS",
            "DATING_CANDIDATE_MIN_AGE_DAYS": "DATING_CANDIDATE_MIN_AGE_YEARS",
            "FRIEND_CONNECT_MIN_ACCESS_AGE_DAYS": "FRIEND_CONNECT_MIN_ACCESS_AGE_YEARS",
        }
        for days_const, years_const_name in _dependent_day_constants_map.items():
            if not hasattr(settings, days_const) and hasattr(settings, years_const_name):
                setattr(settings, days_const, getattr(settings, years_const_name) * settings.DXY)
    try:
        from core.character import Character
        from core.enums import Interest, Gender, LifeStage, RelationshipStatus, AspirationType, LocationType, NeedType
        from core.AI import AICoordinator # Assicurati che sia importabile
        from core.AI.needs_processor import NeedsProcessor # Per testare l'integrazione
        from core.AI.decision_system import DecisionSystem
        from core.AI.action_executor import ActionExecutor
    except Exception as e:
        print(f"ERRORE CRITICO NELL'IMPORT DELLE CLASSI DI TEST in simulation.py: {e}")
        sys.exit(1)

    sim_test_instance = Simulation()
    try:
        sara_richiedente = Character(
            npc_id="sara_req01", name="Sara Richiedente (Test Sim)", initial_gender=Gender.FEMALE,
            initial_age_days=25 * settings.DXY,
            initial_interests={Interest.READING, Interest.TRAVEL, Interest.PHILOSOPHY_DEBATE},
            initial_sexually_attracted_to_genders={Gender.MALE, Gender.FEMALE},
            initial_romantically_attracted_to_genders={Gender.MALE, Gender.FEMALE},
            initial_relationship_status=RelationshipStatus.SINGLE,
            initial_aspiration=AspirationType.WORLD_EXPLORER
        )
        sim_test_instance.add_npc(sara_richiedente)

        print("\nAvvio simulazione di test per pochi tick...")
        sim_test_instance.run(max_ticks=10) # Esegui per 10 tick per vedere l'output

    except NameError as e:
        print(f"ERRORE NEL TEST (NameError in simulation.py test block): {e}. ")
    except Exception as e:
        print(f"ERRORE IMPREVISTO NEL TEST (simulation.py test block): {e.__class__.__name__} - {e}")

    print("\n--- Fine test diretto di core/simulation.py (con setup settings corretto) ---")