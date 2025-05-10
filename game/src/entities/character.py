# simai/game/src/entities/character.py
import pygame
import math 
import random 
import os
from game import game_utils

try:
    # Importa config dal package 'game'
    from game import config as game_config 
except ImportError:
    print("ERRORE CRITICO (Character): Impossibile importare 'game.config'.")
    # NON usare FallbackConfig qui, l'errore deve essere bloccante se config non si trova
    import sys
    sys.exit("Uscita a causa di fallimento import config in Character.")

try:
    # Importa i bisogni dal package 'game.src.modules.needs'
    from game.src.modules.needs.hunger import Hunger
    from game.src.modules.needs.energy import Energy
    from game.src.modules.needs.social import Social
    from game.src.modules.needs.bladder import Bladder
    from game.src.modules.needs.fun import Fun
    from game.src.modules.needs.hygiene import Hygiene
    from game.src.modules.needs.intimacy import Intimacy
except ImportError as e_needs:
    print(f"ERRORE CRITICO (Character): Impossibile importare moduli dei bisogni: {e_needs}")
    import sys
    sys.exit()


def _character_grid_to_world_center(grid_x, grid_y, tile_size_ref):
    world_x = grid_x * tile_size_ref + tile_size_ref / 2
    world_y = grid_y * tile_size_ref + tile_size_ref / 2
    return world_x, world_y

class Character:
    def __init__(self, name, gender, x, y, color=(255, 0, 0), radius=15, speed=200, 
                spritesheet_filename=None, is_bundle=False): # Nuovi parametri per sprite
        self.name = name 
        self.gender = gender 
        self.x = float(x); self.y = float(y)
        self.color = color; self.radius = radius; self.speed = float(speed)
        self.target_partner = None 
        self.age_in_total_game_days = 0
        self.time_in_current_action = 0.0
        self.target_destination = None; self.is_player = False; self.current_action = "idle"
        self.current_path = None; self.current_path_index = 0; self.target_partner = None
        self.is_pregnant = False
        self.pregnancy_progress_days = 0.0

        # --- Gestione Sprite e Animazione ---
        self.spritesheet_image = None
        self.is_bundle = is_bundle # Per caricare lo spritesheet corretto e usare la logica bundle
        self.frame_width = 0
        self.frame_height = 0
        self.animations = {} # Dizionario che conterrà liste di frame (Surface)
        self.current_animation_key = "idle_down" # Esempio: inizia guardando in basso
        self.current_frame_idx_in_animation = 0
        self.animation_timer = 0.0
        self.animation_speed = getattr(game_config, 'DEFAULT_ANIMATION_SPEED', 0.15)
        self.current_facing_direction = "down" # "down", "left", "right", "up"

        if spritesheet_filename:
            char_sprite_base_path = getattr(game_config, 'CHARACTER_SPRITE_PATH', os.path.join(getattr(game_config, 'IMAGE_PATH', 'assets/images'), 'characters'))
            # print(f"DEBUG INIT ({self.name}): Loading spritesheet '{spritesheet_filename}' from base path '{char_sprite_base_path}'")
            self.spritesheet_image = game_utils.load_image(spritesheet_filename, base_path=char_sprite_base_path)
            
            if self.spritesheet_image:
                # print(f"DEBUG INIT ({self.name}): Spritesheet '{spritesheet_filename}' LOADED successfully.")
                if self.is_bundle:
                    self.frame_width = getattr(game_config, 'BUNDLE_FRAME_WIDTH', 32)
                    self.frame_height = getattr(game_config, 'BUNDLE_FRAME_HEIGHT', 32)
                    self._load_bundle_animations()
                else:
                    self.frame_width = getattr(game_config, 'SPRITE_FRAME_WIDTH', 32)
                    self.frame_height = getattr(game_config, 'SPRITE_FRAME_HEIGHT', 48)
                    self._load_standard_animations()
                
                # DEBUG: Controlla le animazioni caricate
                print(f"DEBUG INIT ({self.name}): Animations loaded: {list(self.animations.keys())}")
                for key, frames in self.animations.items():
                    print(f"  - Anim '{key}': {len(frames)} frames")
                    if not frames: print(f"    ATTENZIONE: Animazione '{key}' è vuota!")

                initial_anim_key = "idle_bundle" if self.is_bundle else "idle_" + self.current_facing_direction
                if initial_anim_key in self.animations and self.animations[initial_anim_key]:
                    self.current_animation_key = initial_anim_key
                elif self.animations: # Fallback alla prima animazione valida se quella di default non c'è
                    self.current_animation_key = list(self.animations.keys())[0]
                    print(f"ATTENZIONE: Animazione iniziale '{initial_anim_key}' non trovata o vuota. Fallback a '{self.current_animation_key}'.")
                else:
                    print(f"ERRORE CRITICO: Nessuna animazione valida caricata per {self.name} nonostante lo spritesheet sia presente.")
                    self.spritesheet_image = None # Forza il fallback al disegno del cerchio
                
                print(f"DEBUG INIT ({self.name}): Initial animation key: '{self.current_animation_key}'")

            else: # self.spritesheet_image è None
                print(f"ATTENZIONE (Character __init__): Spritesheet {spritesheet_filename} non caricato per {self.name} (load_image ha restituito None).")
        
        rect_w = self.frame_width if self.spritesheet_image and self.frame_width > 0 else radius * 2
        rect_h = self.frame_height if self.spritesheet_image and self.frame_height > 0 else radius * 2
        self.rect = pygame.Rect(0, 0, rect_w, rect_h)
        self.rect.center = (int(self.x), int(self.y))

        # --- Creazione Istanze Bisogni ---
        self.hunger = Hunger(self, 
                            getattr(game_config, 'HUNGER_MAX_VALUE', 100.0), 
                            getattr(game_config, 'HUNGER_INITIAL_MIN_PCT', 0.0), 
                            getattr(game_config, 'HUNGER_INITIAL_MAX_PCT', 0.6),
                            getattr(game_config, 'HUNGER_BASE_RATE', 2.0), 
                            getattr(game_config, 'HUNGER_RATE_MULTIPLIERS', {}))
        
        self.energy = Energy(self, 
                            getattr(game_config, 'ENERGY_MAX_VALUE', 100.0),
                            getattr(game_config, 'ENERGY_INITIAL_MIN_PCT', 0.4), 
                            getattr(game_config, 'ENERGY_INITIAL_MAX_PCT', 1.0),
                            getattr(game_config, 'ENERGY_BASE_DECAY_RATE', 5.5), 
                            getattr(game_config, 'ENERGY_DECAY_MULTIPLIERS', {}))
        
        self.social = Social(self, 
                            getattr(game_config, 'SOCIAL_MAX_VALUE', 100.0),
                            getattr(game_config, 'SOCIAL_INITIAL_MIN_PCT', 0.4),
                            getattr(game_config, 'SOCIAL_INITIAL_MAX_PCT', 1.0),
                            getattr(game_config, 'SOCIAL_BASE_DECAY_RATE', 1.4),
                            getattr(game_config, 'SOCIAL_DECAY_MULTIPLIERS', {}))

        self.bladder = Bladder(self, 
                            getattr(game_config, 'BLADDER_MAX_VALUE', 100.0),
                            getattr(game_config, 'BLADDER_INITIAL_MIN_PCT', 0.0),
                            getattr(game_config, 'BLADDER_INITIAL_MAX_PCT', 0.65),
                            getattr(game_config, 'BLADDER_BASE_FILL_RATE', 3.0),
                            getattr(game_config, 'BLADDER_FILL_MULTIPLIERS', {}))

        self.fun = Fun(self, 
                    getattr(game_config, 'FUN_MAX_VALUE', 100.0),
                    getattr(game_config, 'FUN_INITIAL_MIN_PCT', 0.3),
                    getattr(game_config, 'FUN_INITIAL_MAX_PCT', 1.0),
                    getattr(game_config, 'FUN_BASE_DECAY_RATE', 2.5),
                    getattr(game_config, 'FUN_DECAY_MULTIPLIERS', {}))

        self.hygiene = Hygiene(self, 
                            getattr(game_config, 'HYGIENE_MAX_VALUE', 100.0),
                            getattr(game_config, 'HYGIENE_INITIAL_MIN_PCT', 0.5),
                            getattr(game_config, 'HYGIENE_INITIAL_MAX_PCT', 1.0),
                            getattr(game_config, 'HYGIENE_BASE_DECAY_RATE', 1.8),
                            getattr(game_config, 'HYGIENE_DECAY_MULTIPLIERS', {}))
        
        self.intimacy = Intimacy(self, 
                                getattr(game_config, 'INTIMACY_MAX_VALUE', 100.0),
                                getattr(game_config, 'INTIMACY_INITIAL_MIN_PCT', 0.0),
                                getattr(game_config, 'INTIMACY_INITIAL_MAX_PCT', 0.3),
                                getattr(game_config, 'INTIMACY_BASE_INCREASE_RATE', 0.8), # Era intimacy_drive_increase_rate_per_game_hour
                                getattr(game_config, 'INTIMACY_INCREASE_RATE_MULTIPLIERS', {}))

        # Età
        days_in_year = getattr(game_config, 'GAME_DAYS_PER_YEAR', 432)
        min_age_y = getattr(game_config, 'NPC_INITIAL_AGE_YEARS_MIN', 20)
        max_age_y = getattr(game_config, 'NPC_INITIAL_AGE_YEARS_MAX', 40)
        min_age_days = min_age_y * days_in_year
        max_age_days = max_age_y * days_in_year
        self.age_in_total_game_days = random.uniform(min_age_days, max_age_days)
        
    def _get_sprite(self, x, y, width, height):
        """Estrae un singolo frame dallo spritesheet."""
        if not self.spritesheet_image:
            return pygame.Surface((width, height), pygame.SRCALPHA) # Frame vuoto trasparente
        
        sprite = pygame.Surface((width, height), pygame.SRCALPHA)
        sprite.blit(self.spritesheet_image, (0, 0), (x, y, width, height))
        return sprite

    def _load_animation_frames(self, sheet_row_index, num_frames, frame_width, frame_height):
        frames = []
        if not self.spritesheet_image or frame_width == 0 or frame_height == 0: # Controllo aggiunto
            print(f"ERRORE _load_animation_frames: spritesheet non caricato o dimensioni frame nulle per {self.name}, riga {sheet_row_index}")
            return frames # Restituisce lista vuota
            
        y_pos = sheet_row_index * frame_height
        # Controlla se la riga eccede l'altezza dello spritesheet
        if y_pos + frame_height > self.spritesheet_image.get_height():
            print(f"ERRORE _load_animation_frames: Riga {sheet_row_index} (y_pos {y_pos}) + altezza frame {frame_height} eccede altezza spritesheet {self.spritesheet_image.get_height()} per {self.name}")
            return frames

        for i in range(num_frames):
            x_pos = i * frame_width
            # Controlla se la colonna eccede la larghezza dello spritesheet
            if x_pos + frame_width > self.spritesheet_image.get_width():
                print(f"ERRORE _load_animation_frames: Colonna {i} (x_pos {x_pos}) + larghezza frame {frame_width} eccede larghezza spritesheet {self.spritesheet_image.get_width()} per {self.name}, animazione riga {sheet_row_index}")
                break # Interrompi caricamento frame per questa animazione
            frames.append(self._get_sprite(x_pos, y_pos, frame_width, frame_height))
        
        if not frames and num_frames > 0:
             print(f"ATTENZIONE _load_animation_frames: Nessun frame caricato per {self.name}, riga {sheet_row_index}, num_frames attesi {num_frames}")
        return frames

    # _load_standard_animations() e _load_bundle_animations() COME PRIMA, usano le costanti da game_config

    def _load_standard_animations(self):
        """Carica tutte le animazioni standard per personaggi non-bundle."""
        walk_frames = getattr(game_config, 'SPRITE_WALK_ANIM_FRAMES', 4)
        idle_frames = getattr(game_config, 'SPRITE_IDLE_ANIM_FRAMES', 1)

        self.animations["walk_up"]    = self._load_animation_frames(getattr(game_config, 'ANIM_ROW_WALK_UP', 8), walk_frames, self.frame_width, self.frame_height)
        self.animations["walk_left"]  = self._load_animation_frames(getattr(game_config, 'ANIM_ROW_WALK_LEFT', 9), walk_frames, self.frame_width, self.frame_height)
        self.animations["walk_down"]  = self._load_animation_frames(getattr(game_config, 'ANIM_ROW_WALK_DOWN', 10), walk_frames, self.frame_width, self.frame_height)
        self.animations["walk_right"] = self._load_animation_frames(getattr(game_config, 'ANIM_ROW_WALK_RIGHT', 11), walk_frames, self.frame_width, self.frame_height)
        
        self.animations["idle_up"]    = self._load_animation_frames(getattr(game_config, 'ANIM_ROW_IDLE_UP', 22), idle_frames, self.frame_width, self.frame_height)
        self.animations["idle_left"]  = self._load_animation_frames(getattr(game_config, 'ANIM_ROW_IDLE_LEFT', 23), idle_frames, self.frame_width, self.frame_height)
        self.animations["idle_down"]  = self._load_animation_frames(getattr(game_config, 'ANIM_ROW_IDLE_DOWN', 24), idle_frames, self.frame_width, self.frame_height)
        self.animations["idle_right"] = self._load_animation_frames(getattr(game_config, 'ANIM_ROW_IDLE_RIGHT', 25), idle_frames, self.frame_width, self.frame_height)
        # Aggiungi qui altre animazioni se necessario (es. phoning, fiki_fiki)

    def _load_bundle_animations(self):
        """Carica animazioni per i neonati (bundles)."""
        # Riga 4 (indice 0-based), 3 frame
        bundle_row = getattr(game_config, 'BUNDLE_ANIM_ROW', 4)
        num_bundle_frames = getattr(game_config, 'BUNDLE_ANIM_FRAMES', 3)
        self.animations["idle_bundle"] = self._load_animation_frames(bundle_row, num_bundle_frames, self.frame_width, self.frame_height)
        self.current_animation_key = "idle_bundle" # Default per bundle

    def get_formatted_age_string(self):
        days_per_m = getattr(game_config, 'DAYS_PER_MONTH', 24)
        months_per_y = getattr(game_config, 'MONTHS_PER_YEAR', 18)
        days_in_y = days_per_m * months_per_y
        if days_in_y == 0: return "Età N/D" 

        total_days_val = int(self.age_in_total_game_days)
        years = total_days_val // days_in_y
        remaining_days_after_years = total_days_val % days_in_y
        months = remaining_days_after_years // days_per_m
        days = remaining_days_after_years % days_per_m
        return f"{years}a, {months}m, {days}g"

    def update(self, dt_real, screen_width, screen_height, game_hours_advanced, 
            current_time_speed_index, is_char_actually_resting, tile_size, period_name):
        dx = 0.0
        dy = 0.0 
        is_moving = False
        
        is_in_blocking_action_for_movement = self.current_action in [
            "phoning", "resting_on_bed", 
            "fiki_fiki_action", "flirting_action",
            "using_toilet" # NUOVO
        ]
        
        can_move_actively = current_time_speed_index > 0 and \
                            not is_char_actually_resting and \
                            not is_in_blocking_action_for_movement

        # DEBUG: Stampa lo stato iniziale prima di tentare il movimento
        if not self.is_player: # Solo per NPC
           print(f"CHAR_UPDATE ({self.name} - Action: {self.current_action}): CanMove={can_move_actively}, TargetDest={self.target_destination}, PathLen={len(self.current_path) if self.current_path else 0}, PathIdx={self.current_path_index}")

        if can_move_actively:
            original_x, original_y = self.x, self.y # Per debug movimento effettivo

            # Logica Movimento NPC
            # 1. Aggiorna target_destination se seeking_partner (movimento diretto)
            if self.current_action == "seeking_partner" and self.target_partner:
                self.target_destination = (self.target_partner.x, self.target_partner.y)
                self.current_path = None # L'inseguimento diretto sovrascrive il path A*
                print(f"CHAR_UPDATE ({self.name}): Now chasing partner {self.target_partner.name} at {self.target_destination}")
            
            # 2. Se si ha un percorso A* e nessun target_destination corrente, imposta il prossimo nodo
            elif self.current_path and self.target_destination is None: 
                if self.current_path_index < len(self.current_path):
                    target_node = self.current_path[self.current_path_index]
                    try:
                        target_world_x, target_world_y = _character_grid_to_world_center(target_node.x, target_node.y, tile_size)
                        self.target_destination = (target_world_x, target_world_y)
                        print(f"CHAR_UPDATE ({self.name}): New A* node target: {self.target_destination} (idx {self.current_path_index} for action '{self.current_action}')")
                    except AttributeError: 
                        print(f"CHAR_UPDATE ({self.name}): Invalid A* node, clearing path.")
                        self.current_path = None; self.target_destination = None
                else: # Indice fuori dai limiti, il percorso dovrebbe essere finito
                    print(f"CHAR_UPDATE ({self.name}): Path index out of bounds, path should be completed.")
                    self.current_path = None; self.target_destination = None
            
            # 3. Se non c'è un percorso A* e non si sta cercando un partner, non ci dovrebbe essere una destinazione
            elif not self.current_path and self.current_action != "seeking_partner": 
                 if self.target_destination: # Se per qualche motivo c'era una destinazione, cancellala
                    print(f"CHAR_UPDATE ({self.name}): No path and not seeking partner, clearing target_destination {self.target_destination}")
                    self.target_destination = None

            # 4. Muoviti verso il target_destination (se impostato)
            if self.target_destination:
                target_x, target_y = self.target_destination
                dist_x = target_x - self.x
                dist_y = target_y - self.y
                distance_to_target = math.sqrt(dist_x**2 + dist_y**2)
                
                # Soglia per considerare un nodo del percorso A* "raggiunto"
                # Per seeking_partner, l'IA controllerà la distanza effettiva dal partner.
                reach_threshold_for_node = tile_size / 2.0 # Più generoso, circa mezza cella

                print(f"CHAR_UPDATE ({self.name}): Trying to move to {self.target_destination}. Dist: {distance_to_target:.1f}")

                if distance_to_target > self.radius * 0.5: # Muoviti solo se non sei estremamente vicino
                    angle = math.atan2(dist_y, dist_x)
                    move_this_frame = self.speed * dt_real
                    
                    # Se la distanza rimanente è minore di un passo completo, muoviti direttamente sul target
                    if distance_to_target <= move_this_frame: 
                        dx = dist_x
                        dy = dist_y
                    else: # Altrimenti, muoviti di un passo completo in quella direzione
                        dx = math.cos(angle) * move_this_frame
                        dy = math.sin(angle) * move_this_frame
                    
                    print(f"CHAR_UPDATE ({self.name}): Calculated dx={dx:.2f}, dy={dy:.2f}")
                
                # 5. Controlla se il nodo corrente del percorso A* è stato raggiunto
                # Questo è specifico per A* e non per "seeking_partner" (che è movimento diretto)
                if self.current_path and self.current_action != "seeking_partner":
                    if distance_to_target <= reach_threshold_for_node:
                        print(f"CHAR_UPDATE ({self.name}): Reached A* node {self.current_path_index} ({self.target_destination}). Advancing path.")
                        self.current_path_index += 1 
                        self.target_destination = None # Forza il ricalcolo del prossimo nodo nel prossimo update
                        if self.current_path_index >= len(self.current_path): 
                            print(f"CHAR_UPDATE ({self.name}): Path A* fully completed for action '{self.current_action}'.")
                            self.current_path = None # Segnala alla logica AI che il percorso è finito
                            # L'IA in run_npc_ai_logic gestirà la transizione da "wandering" a "idle"
            
            # Applica il movimento calcolato
            self.x += dx
            self.y += dy

            # Debug se effettivamente si è mosso
            if dx != 0 or dy != 0:
                print(f"CHAR_UPDATE ({self.name}): MOVED from ({original_x:.0f},{original_y:.0f}) to ({self.x:.0f},{self.y:.0f})")
            elif self.target_destination: # Se aveva un target ma dx,dy sono 0
                print(f"CHAR_UPDATE ({self.name}): Had target {self.target_destination}, but dx,dy are zero.")

            # Controllo Bordi
            if self.x - self.radius < 0: self.x = self.radius
            if self.x + self.radius > screen_width: self.x = screen_width - self.radius
            if self.y - self.radius < 0: self.y = self.radius
            if self.y + self.radius > screen_height: self.y = screen_height - self.radius
        
        else: # Se can_move_actively è False
            # Se non è in un'azione che implica un target (come seeking_partner o un path A*),
            # o se il movimento è bloccato, non dovrebbe avere un target_destination.
            if not (self.current_path or (self.current_action == "seeking_partner" and self.target_partner)) :
                self.target_destination = None 

        # --- Gestione Animazione ---
        if self.spritesheet_image: # Solo se abbiamo uno spritesheet
            new_animation_key = None
            if self.is_bundle:
                new_animation_key = "idle_bundle"
            elif is_moving: # Dovrai impostare 'is_moving = True' se dx o dy sono != 0 dalla logica di movimento
                new_animation_key = "walk_" + self.current_facing_direction
            else: # Fermo
                new_animation_key = "idle_" + self.current_facing_direction
            
            if new_animation_key and new_animation_key != self.current_animation_key:
                if new_animation_key in self.animations:
                    self.current_animation_key = new_animation_key
                    self.current_frame_idx_in_animation = 0
                    self.animation_timer = 0.0
                # else: print(f"WARN: Animazione '{new_animation_key}' non trovata per {self.name}")
            
            if abs(dx) > 0.01 or abs(dy) > 0.01: # Tolleranza minima per considerare movimento
                is_moving = True
                if abs(dx) > abs(dy): # Movimento più orizzontale
                    self.current_facing_direction = "right" if dx > 0 else "left"
                else: # Movimento più verticale (o uguale)
                    self.current_facing_direction = "down" if dy > 0 else "up"
            # else: is_moving rimane False, current_facing_direction non cambia se fermo

        # Gestione Animazione
        if self.spritesheet_image:
            new_anim_key_candidate = ""
            if self.is_bundle:
                new_anim_key_candidate = "idle_bundle"
            elif is_moving:
                new_anim_key_candidate = "walk_" + self.current_facing_direction
            else: # Fermo
                new_anim_key_candidate = "idle_" + self.current_facing_direction
            
            if new_anim_key_candidate and new_anim_key_candidate != self.current_animation_key:
                if new_anim_key_candidate in self.animations and self.animations[new_anim_key_candidate]:
                    self.current_animation_key = new_anim_key_candidate
                    self.current_frame_idx_in_animation = 0
                    self.animation_timer = 0.0
                # else: print(f"WARN ANIM ({self.name}): Richiesta animazione '{new_anim_key_candidate}' non trovata o vuota.")
            
            self.animation_timer += dt_real
            current_anim_speed = self.animation_speed 
            if self.current_animation_key in self.animations: # Verifica di nuovo prima di accedere
                anim_frames = self.animations[self.current_animation_key]
                if anim_frames and self.animation_timer >= current_anim_speed: # Solo se ci sono frame
                    self.animation_timer = 0.0
                    self.current_frame_idx_in_animation = (self.current_frame_idx_in_animation + 1) % len(anim_frames)

        # Aggiornamento Età
        ghid = getattr(game_config, 'GAME_HOURS_IN_DAY', 28)
        if game_hours_advanced > 0 and ghid > 0 :
            self.age_in_total_game_days += game_hours_advanced / ghid
            
            # Energia
            # (is_char_actually_resting viene da main/AI, is_in_blocking_action_for_movement è locale)
            if not is_char_actually_resting and not is_in_blocking_action_for_movement : 
                self.energy.update(game_hours_advanced, period_name, self.current_action, is_char_actually_resting)

            # Socialità
            self.social.update(game_hours_advanced, period_name, self.current_action, is_char_actually_resting)
            
            # Pulsione Intimità
            if self.current_action not in ["fiki_fiki_action", "flirting_action"]: 
                if self.intimacy.get_value() < self.intimacy.max_value: # Usa get_value()
                    # Assicurati che intimacy.base_rate_per_hour sia il tasso di AUMENTO
                    # e che intimacy.high_value_is_good sia False
                    self.intimacy.update(game_hours_advanced, period_name, self.current_action, is_char_actually_resting)

            # Vescica (decade normalmente, soddisfatta dall'azione "using_toilet")
            self.bladder.update(game_hours_advanced, period_name, self.current_action, is_char_actually_resting)
            
            # Incrementa timer per azioni con durata
            if self.current_action in ["fiki_fiki_action", "flirting_action", "using_toilet"]: # MODIFICATO
                self.time_in_current_action += game_hours_advanced

        # Aggiornamento Oggetti Bisogno
        self.hunger.update(game_hours_advanced, period_name, self.current_action, is_char_actually_resting)
        # self.energy.update(game_hours_advanced, period_name, self.current_action, is_char_actually_resting)
        # self.social.update(game_hours_advanced, period_name, self.current_action, is_char_actually_resting)
        self.bladder.update(game_hours_advanced, period_name, self.current_action, is_char_actually_resting)
        self.fun.update(game_hours_advanced, period_name, self.current_action, is_char_actually_resting)
        self.hygiene.update(game_hours_advanced, period_name, self.current_action, is_char_actually_resting)
        # self.intimacy.update(game_hours_advanced, period_name, self.current_action, is_char_actually_resting)

        if self.current_action == "phoning":
            if game_hours_advanced > 0 and hasattr(game_config, 'SOCIAL_RECOVERY_RATE_PER_HOUR_PHONE'):
                # Calcola quanto recuperare in questo frame
                recovery_this_frame = game_config.SOCIAL_RECOVERY_RATE_PER_HOUR_PHONE * game_hours_advanced
                self.social.satisfy(recovery_this_frame) # Usa il metodo satisfy del bisogno Social
                # La AI in ai_system.py gestirà l'uscita da "phoning" quando self.social è pieno
        else:
            # Se non sta telefonando (o in altre azioni sociali specifiche), la socialità decade (gestito da Social.update)
            self.social.update(game_hours_advanced, period_name, self.current_action, is_char_actually_resting)

        # Intimità (decade/aumenta secondo la sua logica in Intimacy.update)
        self.intimacy.update(game_hours_advanced, period_name, self.current_action, is_char_actually_resting)

    # --- METODO randomize_needs ---
    def randomize_needs(self):
        """Ri-randomizza i valori correnti di tutti i bisogni."""
        # Usa le stesse percentuali dell'inizializzazione in BaseNeed, o definisci nuovi range qui
        # Le percentuali sono min_pct, max_pct del *valore massimo* del bisogno.
        
        # Esempio: Fame (0=non affamato, 100=affamatissimo)
        # Usa le percentuali definite in config per l'inizializzazione, se disponibili
        self.hunger.randomize_value(
            getattr(game_config, 'HUNGER_INITIAL_MIN_PCT', 0.0), 
            getattr(game_config, 'HUNGER_INITIAL_MAX_PCT', 0.6)
        )
        # Energia (100=piena, 0=scarica)
        self.energy.randomize_value(
            getattr(game_config, 'ENERGY_INITIAL_MIN_PCT', 0.4), 
            getattr(game_config, 'ENERGY_INITIAL_MAX_PCT', 1.0)
        )
        # Socialità
        self.social.randomize_value(
            getattr(game_config, 'SOCIAL_INITIAL_MIN_PCT', 0.4), 
            getattr(game_config, 'SOCIAL_INITIAL_MAX_PCT', 1.0)
        )
        # Vescica
        self.bladder.randomize_value(
            getattr(game_config, 'BLADDER_INITIAL_MIN_PCT', 0.0), 
            getattr(game_config, 'BLADDER_INITIAL_MAX_PCT', 0.65)
        )
        # Divertimento
        self.fun.randomize_value(
            getattr(game_config, 'FUN_INITIAL_MIN_PCT', 0.3), 
            getattr(game_config, 'FUN_INITIAL_MAX_PCT', 1.0)
        )
        # Igiene
        self.hygiene.randomize_value(
            getattr(game_config, 'HYGIENE_INITIAL_MIN_PCT', 0.5), 
            getattr(game_config, 'HYGIENE_INITIAL_MAX_PCT', 1.0)
        )
        # Intimità
        self.intimacy.randomize_value(
            getattr(game_config, 'INTIMACY_INITIAL_MIN_PCT', 0.0), 
            getattr(game_config, 'INTIMACY_INITIAL_MAX_PCT', 0.3)
        )
        
        print(f"DEBUG: Needs RE-randomized for {self.name}")
        
    def draw(self, screen, font=None, text_color=(255,255,255)):
        # Calcola posizione topleft per blit
        draw_x = int(self.x - self.frame_width / 2)
        draw_y = int(self.y - self.frame_height / 2)
        # Aggiorna self.rect se necessario per collisioni o altro
        if hasattr(self, 'rect'):
            self.rect.topleft = (draw_x, draw_y)
            self.rect.size = (self.frame_width, self.frame_height)
        else: # Crea rect se non esiste
            self.rect = pygame.Rect(draw_x, draw_y, self.frame_width if self.frame_width>0 else 30, self.frame_height if self.frame_height>0 else 30)

        # --- DEBUG PRINT ALL'INIZIO DI DRAW ---
        print(f"DRAW ({self.name}): Action: {self.current_action}, AnimKey: '{self.current_animation_key}', FrameIdx: {self.current_frame_idx_in_animation}, SpritesheetLoaded: {self.spritesheet_image is not None}")
        if self.current_animation_key in self.animations:
            print(f"DRAW ({self.name}): Frames in '{self.current_animation_key}': {len(self.animations[self.current_animation_key])}")
        else:
            print(f"DRAW ({self.name}): AnimKey '{self.current_animation_key}' NOT IN self.animations")
        # --- FINE DEBUG PRINT ---

        image_to_draw_final = None
        if self.spritesheet_image and self.current_animation_key in self.animations:
            current_anim_frames = self.animations[self.current_animation_key]
            if current_anim_frames and self.current_frame_idx_in_animation < len(current_anim_frames):
                image_to_draw_final = current_anim_frames[self.current_frame_idx_in_animation]
        
        if image_to_draw_final:
            screen.blit(image_to_draw_final, self.rect.topleft)
        else: 
            # Fallback se non c'è spritesheet/animazione valida, disegna un cerchio
            # print(f"DRAW ({self.name}): Fallback to circle.") # Debug
            fallback_color = getattr(self, 'color', (128,128,128)) # Usa il colore definito in main
            # Il raggio originale era per il cerchio, ora usiamo le dimensioni del frame se disponibili
            # o un raggio di fallback se frame_width/height sono 0
            fb_radius = self.frame_width // 2 if self.frame_width > 15 else (15) 
            pygame.draw.circle(screen, fallback_color, (int(self.x), int(self.y)), fb_radius)

        if font:
            y_offset_current = self.radius + 10
            try: # Nome
                name_surf = font.render(self.name, True, text_color)
                name_rect = name_surf.get_rect(center=(int(self.x), int(self.y - y_offset_current)))
                screen.blit(name_surf, name_rect)
                y_offset_current = name_rect.top - 3 # Spazio per lo stato sopra il nome
            except Exception: pass
            
        status_text_to_draw = None 
        status_text_color = text_color # Colore di default per lo stato

        if self.current_action == "phoning": status_text_to_draw = "Telefona..."
        elif self.current_action == "resting_on_bed": status_text_to_draw = "Zzz..."
        elif self.current_action == "seeking_partner": status_text_to_draw = "Cerca Partner <3"
        elif self.current_action == "fiki_fiki_action": status_text_to_draw = "<3 Fiki Fiki <3" 
        elif self.current_action == "flirting_action": status_text_to_draw = "<3 Flirt <3" 
        elif self.current_action == "wandering": status_text_to_draw = "Gironzola..."
        elif self.current_action == "seeking_toilet": status_text_to_draw = "Va al WC..." # NUOVO
        elif self.current_action == "using_toilet": status_text_to_draw = "Usa il WC..." # NUOVO
        elif "seeking_" in self.current_action:
            action_display = self.current_action.replace("seeking_", "Va a ").replace("_", " ")
            status_text_to_draw = action_display + "..."
        
        # NUOVO: Visualizza stato gravidanza
        if self.is_pregnant and font:
            preg_days_total = getattr(game_config, 'PREGNANCY_TERM_GAME_DAYS', 24)
            preg_text = f"Incinta ({int(self.pregnancy_progress_days)}/{preg_days_total}g)"
            try:
                preg_surf = font.render(preg_text, True, text_color)
                y_pos_preg = int(self.y + self.radius + 5) # Sotto il personaggio
                if status_text_to_draw: y_pos_preg += 15 # Se c'è già uno stato, mettilo più in basso
                preg_rect = preg_surf.get_rect(centerx=int(self.x), top=y_pos_preg)
                screen.blit(preg_surf, preg_rect)
            except Exception: pass
            
            if status_text_to_draw:
                try:
                    status_surf = font.render(status_text_to_draw, True, text_color)
                    status_rect = status_surf.get_rect(center=(int(self.x), int(self.y - y_offset_current)))
                    screen.blit(status_surf, status_rect)
                except Exception: pass
            
    def eat(self, amount): self.hunger.satisfy(amount) # L'oggetto Hunger gestisce la logica (False per high_is_good)
    def rest(self, rec_rate, hours): self.energy.recover(rec_rate, hours) # Energy ha un metodo specifico
    def socialize_over_time(self, rate, hours): self.social.satisfy(rate * hours)
    def socialize(self, points): self.social.satisfy(points)
    def use_toilet(self, relief_amount): # NUOVO METODO
        """Diminuisce il valore del bisogno bladder."""
        if hasattr(self, 'bladder') and hasattr(self.bladder, 'satisfy'):
            self.bladder.satisfy(relief_amount) # Il metodo satisfy in BaseNeed con high_is_good=False diminuisce il valore
            print(f"CHARACTER ({self.name}): Usato WC. Vescica: {self.bladder.get_value():.0f}")
        else:
            print(f"CHARACTER_ERROR ({self.name}): Metodo use_toilet chiamato ma self.bladder o self.bladder.satisfy non trovati.")
    def have_fun(self, points): self.fun.satisfy(points)
    def get_clean(self, points): self.hygiene.satisfy(points)
    def satisfy_intimacy_drive(self, amount): self.intimacy.satisfy(amount) # L'oggetto Intimacy gestisce la logica
        # NUOVO: Metodo per iniziare la gravidanza
    def become_pregnant(self):
        if self.gender == "female" and not self.is_pregnant: # Solo femmine e non già incinte
            self.is_pregnant = True
            self.pregnancy_progress_days = 0.0
            print(f"CONGRATULAZIONI! {self.name} è incinta!")
            return True
        return False
