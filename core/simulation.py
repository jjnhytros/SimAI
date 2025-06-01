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

class Simulation:
    def __init__(self):
        if settings.DEBUG_MODE: print("  [Simulation INIT] Inizializzazione Simulation...")
        self.time_manager = TimeManager() 
        if settings.DEBUG_MODE: print(f"  [Simulation INIT] TimeManager creato. Ora: {self.time_manager.get_formatted_datetime_string()}")
        
        self.current_tick: int = 0
        self.is_running: bool = False
        self.npcs: Dict[str, Character] = {}
        self.social_hubs: List[Dict] = [] # Come prima
        
        self.locations: Dict[str, Location] = {} # Dizionario per memorizzare le locazioni <location_id, Location_instance>
        self.world_objects: Dict[str, GameObject] = {} # Registro globale degli oggetti, se serve <object_id, GameObject_instance>
        
        self.default_starting_location_id: Optional[str] = None # Aggiungi questo attributo
        self._initialize_world_data()
        if settings.DEBUG_MODE: print("  [Simulation INIT] Simulation inizializzata.")

    def _initialize_world_data(self):
        # ... (inizializzazione social_hubs come prima) ...
        self.social_hubs = [ 
            {"hub_id": "hub_bibli_club", "name": "Club Libro Biblio", "activity_type_descriptor": "Incontro Settimanale", "location_category": LocationType.COMMUNITY_LOT_LIBRARY, "associated_interests": {Interest.READING, Interest.HISTORY}},
            {"hub_id": "hub_galleria_visioni", "name": "Galleria 'Visioni'", "activity_type_descriptor": "Esposizione", "location_category": LocationType.COMMUNITY_LOT_MUSEUM, "associated_interests": {Interest.VISUAL_ARTS, Interest.PHOTOGRAPHY}},
        ]
        if settings.DEBUG_MODE: print(f"  [Simulation INIT] Inizializzati {len(self.social_hubs)} social hub.")

        # Esempio di creazione di una locazione e oggetti di test
        # In un gioco reale, questo verrebbe caricato da file di dati del mondo.
        if settings.DEBUG_MODE:
            self._create_test_locations_and_objects()

    def _create_test_locations_and_objects(self):
        """Crea alcune locazioni e oggetti di esempio per il test."""
        # Cucina di Max
        cucina_max = Location(location_id="max_casa_cucina", name="Cucina di Max", location_type=LocationType.RESIDENTIAL_KITCHEN)
        frigo = GameObject(object_id="frigo_max_01", name="Frigorifero di Max", object_type=ObjectType.REFRIGERATOR)
        fornelli = GameObject(object_id="fornelli_max_01", name="Fornelli di Max", object_type=ObjectType.STOVE)
        cucina_max.add_object(frigo); cucina_max.add_object(fornelli)
        self.add_location(cucina_max)
        self.world_objects[frigo.object_id] = frigo # Aggiunge al registro globale
        self.world_objects[fornelli.object_id] = fornelli

        # Soggiorno di Max
        soggiorno_max = Location(location_id="max_casa_soggiorno", name="Soggiorno di Max", location_type=LocationType.RESIDENTIAL_LIVING_ROOM)
        tv_max = GameObject(object_id="tv_max_01", name="TV Grande di Max", object_type=ObjectType.TV, 
                             provides_fun_activities=[FunActivityType.WATCH_TV])
        divano_max = GameObject(object_id="divano_max_01", name="Divano Comodo di Max", object_type=ObjectType.SOFA, comfort_value=7)
        libreria_max = GameObject(object_id="libreria_max_01", name="Libreria di Max", object_type=ObjectType.BOOKSHELF,
                                   provides_fun_activities=[FunActivityType.READ_BOOK_FOR_FUN]) # La libreria abilita la lettura
        soggiorno_max.add_object(tv_max); soggiorno_max.add_object(divano_max); soggiorno_max.add_object(libreria_max)
        self.add_location(soggiorno_max)
        self.world_objects[tv_max.object_id] = tv_max
        self.world_objects[divano_max.object_id] = divano_max
        self.world_objects[libreria_max.object_id] = libreria_max
        
        # Bagno di Max
        bagno_max = Location(location_id="max_casa_bagno", name="Bagno di Max", location_type=LocationType.RESIDENTIAL_BATHROOM)
        wc_max = GameObject(object_id="wc_max_01", name="WC", object_type=ObjectType.TOILET)
        doccia_max = GameObject(object_id="doccia_max_01", name="Doccia", object_type=ObjectType.SHOWER)
        bagno_max.add_object(wc_max); bagno_max.add_object(doccia_max)
        self.add_location(bagno_max)
        self.world_objects[wc_max.object_id] = wc_max
        self.world_objects[doccia_max.object_id] = doccia_max

        if settings.DEBUG_MODE: print(f"  [Simulation INIT] Create {len(self.locations)} locazioni di test con oggetti.")

    def add_location(self, location: Location):
        """Aggiunge una locazione al mondo."""
        if location.location_id not in self.locations:
            self.locations[location.location_id] = location
            # if settings.DEBUG_MODE: print(f"  [Simulation] Locazione '{location.name}' aggiunta.")
        # else:
            # if settings.DEBUG_MODE: print(f"  [Simulation WARN] Locazione '{location.name}' già esistente.")

    def get_location_by_id(self, location_id: str) -> Optional[Location]:
        """Restituisce un'istanza di Location dato il suo ID."""
        return self.locations.get(location_id)

    def add_npc(self, new_npc: Character):
        """
        Aggiunge un NPC alla simulazione e lo piazza in una locazione.
        L'NPC dovrebbe avere il suo `initial_location_id` impostato nel suo __init__ se noto.
        Se `new_npc.current_location_id` è None, si usa `self.default_starting_location_id`.
        """
        if not isinstance(new_npc, Character):
            if settings.DEBUG_MODE: print(f"  [Simulation AddNPC WARN] Tentativo di aggiungere oggetto non Character: {type(new_npc)}")
            return
        if new_npc.npc_id in self.npcs:
            if settings.DEBUG_MODE: print(f"  [Simulation AddNPC WARN] NPC '{new_npc.name}' (ID: {new_npc.npc_id}) già presente nella simulazione.")
            return
        
        self.npcs[new_npc.npc_id] = new_npc
        
        # Determina la locazione di partenza
        loc_id_to_assign: Optional[str] = new_npc.current_location_id # Prende l'ID impostato da Character.__init__
        
        if not loc_id_to_assign: # Se l'NPC non ha una locazione iniziale specificata
            if self.default_starting_location_id and self.default_starting_location_id in self.locations:
                loc_id_to_assign = self.default_starting_location_id
                if settings.DEBUG_MODE: print(f"    [Simulation AddNPC] NPC '{new_npc.name}' userà la locazione di default della simulazione: '{loc_id_to_assign}'.")
            elif self.locations: # Fallback alla prima locazione definita se il default non è valido
                loc_id_to_assign = list(self.locations.keys())[0]
                if settings.DEBUG_MODE: print(f"    [Simulation AddNPC WARN] Locazione di default non valida o non impostata. NPC '{new_npc.name}' aggiunto alla prima locazione disponibile: '{loc_id_to_assign}'.")
            else: # Nessuna locazione disponibile
                if settings.DEBUG_MODE: print(f"    [Simulation AddNPC ERROR] Nessuna locazione definita nella simulazione. Impossibile piazzare '{new_npc.name}'.")
                # Lascia new_npc.current_location_id come None
        
        # Se abbiamo un ID di locazione valido, chiama set_location sull'NPC
        if loc_id_to_assign and loc_id_to_assign in self.locations:
            # Il metodo Character.set_location si occuperà di aggiornare self.current_location_id
            # e la lista npcs_present_ids della Location.
            new_npc.set_location(loc_id_to_assign, self)
        elif loc_id_to_assign: # L'ID era specificato ma la locazione non esiste
             if settings.DEBUG_MODE: print(f"    [Simulation AddNPC ERROR] Locazione specificata '{loc_id_to_assign}' per '{new_npc.name}' non trovata.")
             new_npc.current_location_id = None # Assicura che sia None se non valida
        
        # Log finale
        if settings.DEBUG_MODE: 
            final_loc_name = "Nessuna (Errore)"
            if new_npc.current_location_id:
                loc_instance = self.get_location_by_id(new_npc.current_location_id)
                if loc_instance:
                    final_loc_name = loc_instance.name
            
            print(f"  [Simulation] NPC '{new_npc.name}' (ID: {new_npc.npc_id}) aggiunto. Locazione Attuale: {final_loc_name}. Totale NPC: {len(self.npcs)}")

    def get_npc_by_id(self, npc_id_to_find: str) -> Optional[Character]: return self.npcs.get(npc_id_to_find)
    def find_social_hubs(self, target_interests: Set[Interest]) -> list[dict]:
        if not target_interests: return [] 
        suggested = []
        for hub in self.social_hubs:
            if hub.get("associated_interests") and hub["associated_interests"].intersection(target_interests): suggested.append(hub)
        return suggested
    def get_eligible_dating_candidates(self, requesting_npc: Character, search_preferences: Optional[Dict[str, Any]] = None) -> list[Character]: # Come prima
        if not requesting_npc: return []
        if requesting_npc.is_asexual() and requesting_npc.is_aromantic() and not (search_preferences and search_preferences.get("explicitly_seeking_qpr")): return []
        eligible_candidates: list[Character] = []; req_npc_age_days = requesting_npc.get_age_in_days()
        min_cand_age_days = settings.DATING_CANDIDATE_MIN_AGE_DAYS; max_age_diff_days = settings.DATING_CANDIDATE_MAX_AGE_DIFFERENCE_YEARS * settings.DXY
        preferred_target_genders = search_preferences.get("target_genders") if search_preferences and search_preferences.get("target_genders") else requesting_npc.get_sexual_attraction()
        preference_for_asexual_partner = search_preferences.get("partner_is_asexual") if search_preferences else None
        preference_for_aromantic_partner = search_preferences.get("partner_is_aromantic") if search_preferences else None
        for cand_npc in self.npcs.values():
            if cand_npc.npc_id == requesting_npc.npc_id: continue
            cand_age_days = cand_npc.get_age_in_days()
            if cand_age_days < min_cand_age_days: continue
            if cand_npc.life_stage not in {LifeStage.EARLY_ADULTHOOD, LifeStage.MIDDLE_ADULTHOOD, LifeStage.LATE_ADULTHOOD}: continue
            if abs(cand_age_days - req_npc_age_days) > max_age_diff_days: continue
            if cand_npc.get_relationship_status() not in {RelationshipStatus.SINGLE, RelationshipStatus.OPEN_RELATIONSHIP}: continue
            if not (cand_npc.gender in preferred_target_genders): continue
            if preference_for_asexual_partner is True and not cand_npc.is_asexual(): continue
            if preference_for_asexual_partner is False and cand_npc.is_asexual(): continue
            if not requesting_npc.is_aromantic() and (preference_for_aromantic_partner is True and not cand_npc.is_aromantic() or preference_for_aromantic_partner is False and cand_npc.is_aromantic()): continue
            compatible_orientation = False; req_is_ace = requesting_npc.is_asexual(); req_is_aro = requesting_npc.is_aromantic()
            cand_is_ace = cand_npc.is_asexual(); cand_is_aro = cand_npc.is_aromantic()
            cand_sexual_attraction = cand_npc.get_sexual_attraction(); cand_romantic_attraction = cand_npc.get_romantic_attraction()
            if not req_is_ace and not cand_is_ace:
                if requesting_npc.gender in cand_sexual_attraction: compatible_orientation = True
            elif not req_is_aro and not cand_is_aro:
                 if requesting_npc.gender in cand_romantic_attraction: compatible_orientation = True
            if not compatible_orientation: continue
            eligible_candidates.append(cand_npc)
        return eligible_candidates
    def get_potential_friend_candidates(self, requesting_npc: Character) -> list[Character]: # Come prima
        if not requesting_npc: return []
        potential_friends: list[Character] = []; requesting_npc_age_days = requesting_npc.get_age_in_days()
        min_candidate_age_days = settings.FRIEND_CONNECT_MIN_ACCESS_AGE_DAYS
        max_age_diff_days = settings.FRIEND_MAX_AGE_DIFFERENCE_YEARS * settings.DXY
        for candidate_npc in self.npcs.values():
            if candidate_npc.npc_id == requesting_npc.npc_id: continue
            candidate_age_days = candidate_npc.get_age_in_days()
            if candidate_age_days < min_candidate_age_days: continue
            if abs(candidate_age_days - requesting_npc_age_days) > max_age_diff_days: continue
            # TODO: Escludere nemici
            potential_friends.append(candidate_npc)
        return potential_friends

    def find_available_social_target(self, requesting_npc: Character) -> Optional[Character]:
        if not self.npcs or len(self.npcs) <= 1 or not requesting_npc.current_location_id: 
            return None
        
        requesting_npc_location = self.get_location_by_id(requesting_npc.current_location_id)
        if not requesting_npc_location: return None # Non dovrebbe succedere se l'NPC ha una locazione valida

        possible_targets = []
        for npc_id in requesting_npc_location.npcs_present_ids: # Cerca solo NPC nella stessa locazione
            if npc_id == requesting_npc.npc_id:
                continue
            
            npc = self.get_npc_by_id(npc_id)
            if not npc: continue

            if npc.current_action and npc.current_action.action_type_name == "ACTION_SLEEP": continue
            if npc.is_busy and npc.current_action and not npc.current_action.is_interruptible: continue
            
            possible_targets.append(npc)
        
        # ... (logica di scelta e preferenza come prima, ma ora da possible_targets filtrati per locazione) ...
        if not possible_targets:
            # if settings.DEBUG_MODE: print(f"    [Find Target - {requesting_npc.name}] Nessun NPC disponibile nella stessa locazione.")
            return None
        # (Logica di preferenza per relazione e scelta casuale come prima)
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
        """
        if not self.time_manager: # Check di sicurezza
            if settings.DEBUG_MODE: print("    [Sim WARN] TimeManager non inizializzato!")
            self.current_tick += 1
            return
            
        self.time_manager.advance_tick()
        
        if settings.DEBUG_MODE and self.time_manager.get_current_minute() == 0 : # Ogni ora piena
             print(f"      [SimTime] Ora: {self.time_manager.get_formatted_datetime_string()} (Tick Sim: {self.current_tick})")

        is_new_day = (self.time_manager.get_current_hour() == 0 and 
                        self.time_manager.get_current_minute() == 0 and
                        self.time_manager.total_ticks_sim > 1) 

        for npc in self.npcs.values():
            if npc:
                npc.update_needs(self.time_manager, 1) 
                if is_new_day: npc._set_age_in_days(npc.get_age_in_days() + 1) 
                npc.update_action(self.time_manager, simulation_context=self) 
        self.current_tick += 1

    # --- Loop Principale e Aggiornamenti ---
    def run(self, max_ticks: Optional[int] = None): # Accetta max_ticks
        """Avvia e gestisce il loop principale della simulazione."""
        if settings.DEBUG_MODE:
            print("  [Simulation RUN] Avvio del loop di simulazione...")
            if max_ticks:
                print(f"  [Simulation RUN] La simulazione girerà per un massimo di {max_ticks} tick.")
            else:
                print("  [Simulation RUN] La simulazione girerà indefinitamente (o fino a interruzione manuale Ctrl+C).")
        
        self.is_running = True
        # self.current_tick è già inizializzato a 0 in __init__ o dovrebbe esserlo se vogliamo più run()
        # Per ora, se run() viene chiamato più volte, current_tick continua da dove era.
        # Se vogliamo che ogni run() riparta da 0, resettare self.current_tick = 0 qui.
        
        try:
            while self.is_running:
                self._update_simulation_state() # Avanza il tempo e aggiorna gli NPC
                self._render_output()           # Stampa informazioni (placeholder)

                if max_ticks is not None and self.current_tick >= max_ticks:
                    if settings.DEBUG_MODE:
                        print(f"  [Simulation RUN] Raggiunto limite di {max_ticks} tick. Uscita elegante...")
                    self.is_running = False
                
                # Pausa per rendere l'output leggibile e non usare 100% CPU
                # In una vera TUI, questo potrebbe essere gestito diversamente.
                if settings.DEBUG_MODE and max_ticks: # Solo se c'è un limite, per non bloccare indefinitamente
                    import time
                    time.sleep(0.01) # Piccola pausa

        except KeyboardInterrupt:
            if settings.DEBUG_MODE:
                print("\n  [Simulation RUN] Loop interrotto da KeyboardInterrupt (Ctrl+C).")
            self.is_running = False # Assicura l'uscita
        finally:
            self._perform_cleanup()

    def _render_output(self):
        """Genera l'output della simulazione (es. per TUI o log testuale)."""
        # Per ora, questo metodo è un placeholder.
        # La stampa del tempo è già in _update_simulation_state per debug.
        pass

    def _perform_cleanup(self):
        if settings.DEBUG_MODE:
            print("  [Simulation CLEANUP] Esecuzione pulizia finale...")
        print("------------------------------------")

# --- Blocco di Test per simulation.py ---
# In core/simulation.py, alla fine del file

if __name__ == '__main__':
    print("--- Test diretto di core/simulation.py ---")

    # === INIZIO BLOCCO PER RISOLVERE IMPORT E CONFIGURARE SETTINGS PER IL TEST ===
    import sys
    import os

    # Aggiungiamo la directory genitore (SimAI_Project/) al sys.path
    # per permettere l'import di 'core.settings', 'core.character', ecc.
    current_dir = os.path.dirname(os.path.abspath(__file__)) # Directory di simulation.py (core/)
    project_root = os.path.dirname(current_dir)             # Directory sopra core/ (SimAI_Project/)
    
    original_sys_path = list(sys.path) # Salva il sys.path originale
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
        # Il print di conferma del path lo faremo dopo aver caricato/mockato settings per DEBUG_MODE

    # Tentativo di importare il vero modulo settings
    settings_imported_successfully = False
    try:
        from core import settings
        settings_imported_successfully = True
        # print("  [Test Setup - simulation.py] Modulo 'core.settings' importato con successo.")
    except ImportError:
        print("  [Test Setup - simulation.py] WARN: Impossibile importare 'core.settings'. Uso un mock di emergenza.")
        class EmergencySettingsMock:
            # Costanti minime essenziali per i test
            DEBUG_MODE: bool = True # Deve essere True per i log di test
            DXY: int = 432
            
            # Costanti per Character e LifeStage
            MAX_NPC_ACTIVE_INTERESTS: int = 3
            LIFE_STAGE_AGE_THRESHOLDS_DAYS: dict = {
                "INFANCY": 0, "TODDLERHOOD": 1 * DXY, "EARLY_CHILDHOOD": 3 * DXY,
                "MIDDLE_CHILDHOOD": 6 * DXY, "ADOLESCENCE": 12 * DXY,
                "EARLY_ADULTHOOD": 20 * DXY, "MIDDLE_ADULTHOOD": 40 * DXY,
                "LATE_ADULTHOOD": 60 * DXY, "ELDERLY": 80 * DXY
            }
            
            # Costanti per Amori Curati e Dating (con DXY definito sopra)
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

        settings = EmergencySettingsMock()

    # Assicura che DEBUG_MODE sia True per i test e che DXY esista e sia corretto
    # Questo sovrascrive il DEBUG_MODE del file settings importato, solo per questo test.
    # if not hasattr(settings, 'DEBUG_MODE') or not settings.DEBUG_MODE:
    #     print("  [Test Setup - simulation.py] Forzo settings.DEBUG_MODE = True per il test.")
    settings.DEBUG_MODE = True # Sempre True per i test di questo blocco

    if not hasattr(settings, 'DXY') or settings.DXY != 432: # Verifica anche il valore se importato
        if settings.DEBUG_MODE: print(f"  [Test Setup - simulation.py] WARN: settings.DXY non corretto ({getattr(settings, 'DXY', 'Mancante')}). Imposto 432.")
        settings.DXY = 432
    
    # Stampa di conferma del path solo ora che DEBUG_MODE è sicuramente True
    if project_root not in original_sys_path and settings.DEBUG_MODE: # Stampa solo se è stato effettivamente aggiunto
        print(f"  [Test Setup - simulation.py] Aggiunto al sys.path: {project_root}")
    if settings.DEBUG_MODE: print(f"  [Test Setup - simulation.py] Utilizzo DXY = {settings.DXY}")

    # Definisci valori di fallback per costanti critiche se non presenti nell'oggetto 'settings'
    # (questo è utile se il file settings.py è incompleto o se si usa il mock)
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
    }
    for const_name, default_value in _critical_constants_defaults_for_test.items():
        if not hasattr(settings, const_name):
            if settings.DEBUG_MODE: print(f"  [Test Setup - simulation.py] WARN: settings.{const_name} non trovato. Uso default.")
            # Se il default_value è un dizionario (es. LIFE_STAGE_AGE_THRESHOLDS_DAYS), assicurati che usi il settings.DXY corretto
            if isinstance(default_value, dict) and "TODDLERHOOD" in default_value: # Check specifico per LIFE_STAGE
                 setattr(settings, const_name, {k: (v if k=="INFANCY" else v * settings.DXY // settings.DXY) for k,v in default_value.items()})
            else:
                setattr(settings, const_name, default_value)
    
    # Deriva le costanti in giorni DOPO che le _YEARS e DXY sono sicuramente sull'oggetto settings
    _dependent_day_constants_map = {
        "AMORI_CURATI_PHASE1_ACCESS_MIN_AGE_DAYS": "AMORI_CURATI_PHASE1_ACCESS_MIN_AGE_YEARS",
        "AMORI_CURATI_PHASE2_ACCESS_MIN_AGE_DAYS": "AMORI_CURATI_PHASE2_ACCESS_MIN_AGE_YEARS",
        "DATING_CANDIDATE_MIN_AGE_DAYS": "DATING_CANDIDATE_MIN_AGE_YEARS",
        "FRIEND_CONNECT_MIN_ACCESS_AGE_DAYS": "FRIEND_CONNECT_MIN_ACCESS_AGE_YEARS",
    }
    if hasattr(settings, 'DXY'):
        for days_const, years_const_name in _dependent_day_constants_map.items():
            if not hasattr(settings, days_const) and hasattr(settings, years_const_name):
                setattr(settings, days_const, getattr(settings, years_const_name) * settings.DXY)
    # === FINE BLOCCO PER RISOLVERE IMPORT E CONFIGURARE SETTINGS ===

    # Ora importa le classi che dipendono da settings e enums
    try:
        from core.character import Character 
        from core.enums import Interest, Gender, LifeStage, RelationshipStatus, AspirationType, LocationType
    except Exception as e:
        print(f"ERRORE CRITICO NELL'IMPORT DELLE CLASSI DI TEST in simulation.py: {e}")
        print("Controlla che i file Character ed Enum siano corretti e che 'settings' sia accessibile e completo.")
        sys.exit(1) # Esce se gli import fondamentali falliscono

    # --- Inizio Codice di Test Specifico per Simulation ---
    sim_test_instance = Simulation() 
    try:
        # NPC Richiedente per testare get_eligible_dating_candidates e get_potential_friend_candidates
        sara_richiedente = Character(
            npc_id="sara_req01", name="Sara Richiedente (Test Sim)", initial_gender=Gender.FEMALE,
            initial_age_days=25 * settings.DXY, # 25 anni
            initial_interests={Interest.READING, Interest.TRAVEL, Interest.PHILOSOPHY_DEBATE},
            initial_sexually_attracted_to_genders={Gender.MALE, Gender.FEMALE}, # Bisessuale
            initial_romantically_attracted_to_genders={Gender.MALE, Gender.FEMALE},
            initial_relationship_status=RelationshipStatus.SINGLE,
            initial_aspiration=AspirationType.WORLD_EXPLORER
        )
        sim_test_instance.add_npc(sara_richiedente)

        # Candidati per Dating e Amicizia
        marco_cand = Character(
            npc_id="marco_cand01", name="Marco Single (Test Sim)", initial_gender=Gender.MALE,
            initial_age_days=28 * settings.DXY, 
            initial_interests={Interest.TRAVEL, Interest.GAMING},
            initial_sexually_attracted_to_genders={Gender.FEMALE},
            initial_romantically_attracted_to_genders={Gender.FEMALE},
            initial_relationship_status=RelationshipStatus.SINGLE,
            initial_aspiration=AspirationType.WORLD_EXPLORER
        )
        sim_test_instance.add_npc(marco_cand)
        
        laura_cand = Character(
            npc_id="laura_cand02", name="Laura Artista (Test Sim)", initial_gender=Gender.FEMALE,
            initial_age_days=26 * settings.DXY, 
            initial_interests={Interest.VISUAL_ARTS, Interest.READING},
            initial_sexually_attracted_to_genders={Gender.MALE, Gender.FEMALE, Gender.NON_BINARY},
            initial_romantically_attracted_to_genders={Gender.MALE, Gender.FEMALE, Gender.NON_BINARY},
            initial_relationship_status=RelationshipStatus.SINGLE,
            initial_aspiration=AspirationType.CREATIVE_SOUL
        )
        sim_test_instance.add_npc(laura_cand)
        
        elena_amica = Character( # Per test amicizia
            npc_id="elena_amica01", name="Elena Amica (Test Sim)", initial_gender=Gender.FEMALE,
            initial_age_days=16 * settings.DXY, # 16 anni
            initial_interests={Interest.MUSIC_LISTENING, Interest.GAMING},
            initial_relationship_status=RelationshipStatus.SINGLE,
            initial_aspiration=AspirationType.SOCIAL_BUTTERFLY
        )
        sim_test_instance.add_npc(elena_amica)


        print(f"\n--- Test get_eligible_dating_candidates per {sara_richiedente.name} ---")
        candidati_dating_sara = sim_test_instance.get_eligible_dating_candidates(sara_richiedente)
        if candidati_dating_sara:
            print(f"Trovati {len(candidati_dating_sara)} candidati dating per {sara_richiedente.name}:")
            for candidato in candidati_dating_sara: print(f"  - {candidato.name}")
        else: print(f"Nessun candidato dating trovato per {sara_richiedente.name}.")

        print(f"\n--- Test get_potential_friend_candidates per {elena_amica.name} ---")
        candidati_amici_elena = sim_test_instance.get_potential_friend_candidates(elena_amica)
        if candidati_amici_elena:
            print(f"Trovati {len(candidati_amici_elena)} candidati amici per {elena_amica.name}:")
            for candidato in candidati_amici_elena: print(f"  - {candidato.name}")
        else: print(f"Nessun candidato amico trovato per {elena_amica.name}.")

        # Avvio della simulazione per qualche tick (opzionale per questo test specifico)
        # print("\nAvvio simulazione di test per pochi tick...")
        # sim_test_instance.run()

    except NameError as e: # Cattura NameError se un Enum o classe non è definito/importato
        print(f"ERRORE NEL TEST (NameError in simulation.py test block): {e}. "
              "Assicurati che tutte le Enum (Gender, LifeStage, RelationshipStatus, Interest, AspirationType, LocationType) "
              "siano definite in core.enums ed esportate correttamente in core/enums/__init__.py, "
              "e che la classe Character sia importata.")
    except Exception as e:
        print(f"ERRORE IMPREVISTO NEL TEST (simulation.py test block): {e.__class__.__name__} - {e}")

    print("\n--- Fine test diretto di core/simulation.py (con setup settings corretto) ---")
