# core/simulation.py
from typing import TYPE_CHECKING, List, Dict, Any, Set, Optional # Aggiungi Optional e gli altri tipi generici
import random
import threading
import time

# Importiamo le classi e le Enum necessarie
from core.enums import *
from core import settings
from core.config import npc_config, time_config
from core.modules.time_manager import TimeManager
from core.world.location import Location
from core.world.game_object import GameObject
from core.AI import AICoordinator
from core.AI.lod_manager import LODManager
from core.AI.social_manager import SocialManager
from core.world.weather_manager import WeatherManager
from core.AI.consequence_analyzer import ConsequenceAnalyzer
from core.AI.claire.claire_system import ClaireSystem

if TYPE_CHECKING:
    from character import Character

class Simulation:
    def __init__(self):
        if settings.DEBUG_MODE: print("  [Simulation INIT] Inizializzazione Simulation...")
        self.time_manager = TimeManager(simulation_context=self)
        if settings.DEBUG_MODE: print(f"  [Simulation INIT] TimeManager creato. Ora: {self.time_manager.get_formatted_datetime_string()}")

        self.weather_manager = WeatherManager() # Assumendo che esista
        
        self.current_tick: int = 0
        self.is_running: bool = False
        self.npcs: Dict[str, 'Character'] = {}
        self.locations: Dict[str, Location] = {}
        self.world_objects: Dict[str, GameObject] = {}
        self.npcs: Dict[str, 'Character'] = {}

        self.game_speed: float = 1.0
        self.default_starting_location_id: Optional[str] = None
        
        # Inizializza l'attributo per l'ID del personaggio del giocatore a None.
        self.player_character_id: Optional[str] = None
        self.claire_system = ClaireSystem(self)

        self._initialize_world_data()

        # Istanzia i manager che richiedono il contesto della simulazione (self)
        self.lod_manager = LODManager(self)
        self.ai_coordinator = AICoordinator(self)
        self.is_paused: bool = False
        self.time_scale: float = 1.0
        self.social_manager = SocialManager(self)
        self.consequence_analyzer = ConsequenceAnalyzer()
        self.social_hubs: List[Dict] = []
        # self._simulation_thread: Optional[threading.Thread] = None
        # self._stop_event = threading.Event()
        # Il lock serve per evitare che il thread di rendering legga i dati
        # mentre il thread di simulazione li sta modificando.
        # self.state_lock = threading.Lock()
        if settings.DEBUG_MODE: print("  [Simulation INIT] AICoordinator creato.")
        if settings.DEBUG_MODE: print("  [Simulation INIT] Simulation inizializzata.")

    def _simulation_loop(self):
        """Il loop che gira in background e fa avanzare il mondo."""
        ns_per_tick = (time_config.TICK_RATE_DENOMINATOR * time_config.NANOSECONDS_PER_SECOND) // time_config.TICK_RATE_NUMERATOR
        last_update_ns = time.monotonic_ns()
        lag_accumulator_ns = 0

        while not self._stop_event.is_set():
            current_ns = time.monotonic_ns()
            elapsed_ns = current_ns - last_update_ns
            last_update_ns = current_ns
            lag_accumulator_ns += elapsed_ns * self.time_scale

            if not self.is_paused:
                while lag_accumulator_ns >= ns_per_tick:
                    with self.state_lock:
                        self._update_simulation_state(ticks_to_process=1)
                    
                    lag_accumulator_ns -= ns_per_tick
            else:
                # Se è in pausa, resetta l'accumulatore per evitare scatti alla ripresa
                lag_accumulator_ns = 0
            
            time.sleep(0.001)

    def start_simulation_thread(self):
        """Avvia il thread della simulazione."""
        if self._simulation_thread is None:
            self._stop_event.clear()
            self._simulation_thread = threading.Thread(target=self._simulation_loop, daemon=True)
            self._simulation_thread.start()
            if settings.DEBUG_MODE: print("  [Simulation] Thread di simulazione avviato.")

    def stop_simulation(self):
        """Ferma il thread della simulazione in modo pulito."""
        if self._simulation_thread and self._simulation_thread.is_alive():
            self._stop_event.set()
            self._simulation_thread.join() # Attende la fine del thread
            if settings.DEBUG_MODE: print("  [Simulation] Thread di simulazione fermato.")

    def set_time_scale(self, scale: float):
        """Imposta la velocità di scorrimento del tempo."""
        # Impostiamo dei limiti ragionevoli per evitare problemi
        # In questo modo, se premiamo un tasto di velocità, ci assicuriamo anche che il gioco non sia in pausa.
        self.is_paused = False
        self.time_scale = max(0.25, min(scale, 8.0))
        if settings.DEBUG_MODE:
            print(f"  [Simulation] Time scale impostato a: {self.time_scale}x")

    def toggle_pause(self):
        """Inverte lo stato di pausa della simulazione."""
        self.is_paused = not self.is_paused
        print(f"  [Simulation] Pausa {'ATTIVATA' if self.is_paused else 'DISATTIVATA'}.")

    def _initialize_world_data(self):
        """
        Carica tutte le locazioni e gli oggetti del mondo dai file di dati dei distretti.
        """
        from core.data.districts.muse_quarter_data import district_locations as muse_locations
        
        all_locations = muse_locations # + ...
        
        for loc in all_locations:
            self.locations[loc.location_id] = loc
            for obj_id, obj in loc.objects.items():
                self.world_objects[obj_id] = obj

        if settings.DEBUG_MODE:
            print(f"  [Simulation INIT] Caricate {len(self.locations)} locazioni e {len(self.world_objects)} oggetti dai file di dati.")

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
        tv_max = GameObject(object_id="tv_max_01", name="TV", object_type=ObjectType.TELEVISION, provides_fun_activities=[FunActivityType.WATCH_TV], logical_x=2, logical_y=3)
        divano_max = GameObject(object_id="divano_max_01", name="Divano", object_type=ObjectType.SOFA, comfort_value=7, logical_x=4, logical_y=3)
        libreria_max = GameObject(object_id="libreria_max_01", name="Libreria", object_type=ObjectType.BOOKCASE, provides_fun_activities=[FunActivityType.READ_BOOK_FOR_FUN], logical_x=6, logical_y=3)
        
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

    def add_npc(self, npc: 'Character'):
        """Aggiunge un NPC alla simulazione e lo posiziona nel mondo."""
        if npc.npc_id in self.npcs:
            if settings.DEBUG_MODE:
                print(f"[Simulation.add_npc WARN] NPC con ID {npc.npc_id} già presente. Sostituzione.")
        
        self.npcs[npc.npc_id] = npc
        
        # Calcola lo stadio di vita iniziale ora che abbiamo il contesto temporale
        if self.time_manager:
            npc._calculate_and_set_life_stage(self.time_manager.get_current_time())

        # Posiziona l'NPC nella sua locazione iniziale
        loc_id = npc.current_location_id
        if loc_id:
            location = self.get_location_by_id(loc_id)
            if location:
                location.add_npc(npc.npc_id)
            else:
                if settings.DEBUG_MODE:
                    print(f"[Simulation.add_npc ERROR] Locazione ID '{loc_id}' per {npc.name} non trovata!")
        elif settings.DEBUG_MODE:
            print(f"[Simulation.add_npc WARN] NPC '{npc.name}' aggiunto senza una locazione iniziale.")

    def get_npc_by_id(self, npc_id_to_find: str) -> Optional['Character']:
        return self.npcs.get(npc_id_to_find)

    def set_player_character(self, npc_id: str):
        """Imposta l'NPC specificato come personaggio del giocatore."""
        if npc_id in self.npcs:
            self.player_character_id = npc_id
            if settings.DEBUG_MODE:
                print(f"  [Simulation] Personaggio del giocatore impostato su: {self.npcs[npc_id].name} (ID: {npc_id})")
        elif settings.DEBUG_MODE:
            print(f"  [Simulation WARN] Tentativo di impostare un player character non esistente: {npc_id}")

    def get_player_character(self) -> Optional['Character']:
        """
        Restituisce l'oggetto Character del giocatore, se ne è stato impostato uno.
        Questo metodo non richiede argomenti.
        """
        # Controlla se abbiamo un ID del personaggio del giocatore salvato
        if self.player_character_id:
            # Usa un altro metodo della classe stessa per trovare e restituire l'NPC
            return self.get_npc_by_id(self.player_character_id)
        
        # Se non è stato impostato nessun personaggio, restituisce None
        return None

    def find_social_hubs(self, target_interests: Set[Interest]) -> list[dict]:
        if not target_interests: return []
        suggested = []
        for hub in self.social_hubs:
            if hub.get("associated_interests") and hub["associated_interests"].intersection(target_interests): suggested.append(hub)
        return suggested

    def get_eligible_dating_candidates(self, requesting_npc: 'Character', search_preferences: Optional[Dict[str, Any]] = None) -> List['Character']:
        if not requesting_npc: return []
        if not self.time_manager: return [] # Aggiunto controllo di sicurezza

        # Ottieni il tempo corrente una sola volta all'inizio
        current_time = self.time_manager.get_current_time()
        
        if requesting_npc.is_asexual() and requesting_npc.is_aromantic() and not (search_preferences and search_preferences.get("explicitly_seeking_qpr")):
            return []
            
        eligible_candidates: list['Character'] = []
        
        # Passa current_time alla chiamata del metodo
        req_npc_age_days = requesting_npc.get_age_in_days(current_time)
        
        min_cand_age_days = npc_config.DATING_CANDIDATE_MIN_AGE_DAYS
        max_age_diff_days = npc_config.DATING_CANDIDATE_MAX_AGE_DIFFERENCE_YEARS * settings.DXY
        
        # Logica per le preferenze di genere (già corretta)
        genders_from_prefs: Optional[Set[Gender]] = None
        if search_preferences:
            genders_from_prefs_value = search_preferences.get("target_genders")
            if isinstance(genders_from_prefs_value, set):
                genders_from_prefs = genders_from_prefs_value
        
        if genders_from_prefs is not None:
            preferred_target_genders: Set[Gender] = genders_from_prefs
        else:
            preferred_target_genders: Set[Gender] = requesting_npc.get_sexual_attraction()

        preference_for_asexual_partner = search_preferences.get("partner_is_asexual") if search_preferences else None
        preference_for_aromantic_partner = search_preferences.get("partner_is_aromantic") if search_preferences else None

        for cand_npc in self.npcs.values():
            if cand_npc.npc_id == requesting_npc.npc_id: continue
            
            # Passa current_time alle chiamate del metodo
            cand_age_days = cand_npc.get_age_in_days(current_time)
            
            if cand_age_days < min_cand_age_days: continue
            if abs(cand_age_days - req_npc_age_days) > max_age_diff_days: continue
            
            # Assicurati che anche qui venga passato il tempo corrente per il calcolo del LifeStage
            cand_npc._calculate_and_set_life_stage(current_time) 
            if cand_npc.life_stage not in {LifeStage.YOUNG_ADULT, LifeStage.ADULT, LifeStage.MIDDLE_AGED}: continue
            
            if cand_npc.get_relationship_status() not in {RelationshipStatus.SINGLE, RelationshipStatus.OPEN_RELATIONSHIP}: continue
            
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
            elif not req_is_aro and not cand_is_aro:
                if requesting_npc.gender in cand_romantic_attraction: compatible_orientation = True

            if not compatible_orientation: continue
            
            eligible_candidates.append(cand_npc)
            
        return eligible_candidates

    def get_potential_friend_candidates(self, requesting_npc: 'Character') -> List['Character']:
        """
        Restituisce una lista di NPC idonei per una nuova amicizia,
        filtrando principalmente per età.
        """
        eligible: List['Character'] = []
        if not self.time_manager:
            return eligible
            
        current_time = self.time_manager.get_current_time()
        req_age_days = requesting_npc.get_age_in_days(current_time)
        
        min_cand_age_days = npc_config.FRIEND_CONNECT_MIN_ACCESS_AGE_DAYS
        max_age_diff_days = npc_config.FRIEND_MAX_AGE_DIFFERENCE_YEARS * DXY

        for cand_npc in self.npcs.values():
            # Escludi il richiedente stesso e persone con cui ha già una relazione forte/negativa
            if cand_npc.npc_id == requesting_npc.npc_id:
                continue
            if requesting_npc.get_relationship_with(cand_npc.npc_id):
                # Potremmo aggiungere una logica più fine qui in futuro
                continue

            # Filtro: Età
            cand_age_days = cand_npc.get_age_in_days(current_time)
            if cand_age_days < min_cand_age_days:
                continue
            if abs(cand_age_days - req_age_days) > max_age_diff_days:
                continue
            
            eligible.append(cand_npc)
            
        return eligible

    def find_available_social_target(self, requesting_npc: 'Character') -> Optional['Character']:
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

    def _update_simulation_state(self, ticks_to_process: int = 1):
        """
        Avanza la logica della simulazione di un numero specifico di tick.
        """
        if self.is_paused:
            return
            
        ticks_to_process = 1

        if not self.is_running or ticks_to_process <= 0:
            return
            
        current_time = self.time_manager.get_current_time()

        # 1. Aggiorna il LOD
        player_character = self.get_player_character()
        if player_character and self.lod_manager:
            player_pos = (float(player_character.logical_x), float(player_character.logical_y))
            self.lod_manager.update_all_npcs_lod(player_position=player_pos)

        # 2. Aggiorna ogni NPC per il numero di tick richiesto
        if self.ai_coordinator:
            # Passiamo ticks_to_process che verrà usato in update_needs
            self.ai_coordinator.update_all_npcs(time_delta=ticks_to_process)

        # Aggiorna il sistema Claire
        if self.claire_system:
            self.claire_system.update()

        # 3. Avanza il tempo globale del numero di tick calcolato
        self.time_manager.advance_time(ticks=ticks_to_process)
        self.current_tick += ticks_to_process

    def run(self, max_ticks: Optional[int] = None):
        """Esegue la simulazione in modalità testuale (TUI) per un numero definito di tick."""
        if settings.DEBUG_MODE: print("  [Simulation TUI] Avvio del loop testuale...")

        self.is_running = True
        try:
            while self.is_running:
                # In TUI, l'update è sincrono, non in un thread
                self._update_simulation_state(ticks_to_process=1)
                
                # Potremmo stampare un output testuale qui, se volessimo
                # self._render_tui_output() 
                
                if max_ticks is not None and self.current_tick >= max_ticks:
                    self.is_running = False
        except KeyboardInterrupt:
            self.is_running = False
        finally:
            self._perform_cleanup()

    def _render_output(self):
        pass

    def _perform_cleanup(self):
        if settings.DEBUG_MODE:
            print("  [Simulation CLEANUP] Esecuzione pulizia finale...")
        print("------------------------------------")
