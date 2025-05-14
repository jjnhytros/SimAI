# simai/game/src/entities/character.py
# MODIFIED: Made debug/warning prints conditional. Removed FallbackConfig/GameUtilsFallback.
# MODIFIED: to_dict and from_data handle spritesheet_filename and sleep_spritesheet_filename.
# MODIFIED: Fixed randomize_needs to pass min/max percentages.

import pygame
import math 
import random 
import uuid 
import os 
import sys 

try:
    from game import config as game_config 
    from game import game_utils 
except ImportError as e:
    # Questa è un'importazione critica. Se fallisce, il modulo Character non può funzionare.
    print(f"CRITICAL ERROR (Character): Could not import 'game.config' or 'game.game_utils': {e}")
    print("Ensure these modules are accessible. The application will now exit.")
    sys.exit() # Esce se i moduli critici non sono trovati

# Leggi il flag di debug una volta, dopo aver importato (o tentato di importare) config
DEBUG_VERBOSE = getattr(game_config, 'DEBUG_AI_ACTIVE', False) # Usa lo stesso flag o uno dedicato

try:
    from game.src.modules.needs.hunger import Hunger
    from game.src.modules.needs.energy import Energy
    from game.src.modules.needs.social import Social
    from game.src.modules.needs.bladder import Bladder
    from game.src.modules.needs.fun import Fun
    from game.src.modules.needs.hygiene import Hygiene
    from game.src.modules.needs.intimacy import Intimacy 
except ImportError as e_needs:
    if DEBUG_VERBOSE: print(f"CRITICAL ERROR (Character): Could not import Need modules: {e_needs}")
    sys.exit()

def _character_grid_to_world_center(grid_x: int, grid_y: int, tile_size_ref: int) -> tuple:
    world_x = grid_x * tile_size_ref + tile_size_ref / 2.0
    world_y = grid_y * tile_size_ref + tile_size_ref / 2.0
    return world_x, world_y

class Character:
    def __init__(self, name: str, gender: str, x: float, y: float, 
                 color: tuple = (255,0,0), radius: int = 15, speed: float = 200, 
                 spritesheet_filename: str = None, 
                 sleep_spritesheet_filename: str = None,
                 is_bundle: bool = False, existing_uuid: str = None):
        
        self.uuid: str = existing_uuid if existing_uuid else str(uuid.uuid4())
        self.name: str = name 
        self.gender: str = gender 
        self.x: float = float(x)    
        self.y: float = float(y)    
        self.fallback_color: tuple = color 
        self.fallback_radius: int = radius 
        self.speed: float = float(speed)
        
        self.target_destination: tuple | None = None 
        self.is_player: bool = False 
        self.current_action: str = "idle" 
        self.current_path: list | None = None 
        self.current_path_index: int = 0 
        self.target_partner: Character | None = None 
        self.time_in_current_action: float = 0.0

        self.spritesheet_filename_ref: str | None = spritesheet_filename
        self.sleep_spritesheet_filename_ref: str | None = sleep_spritesheet_filename

        self.spritesheet_image: pygame.Surface | None = None
        self.sleep_spritesheet_image: pygame.Surface | None = None
        self.is_bundle: bool = is_bundle
        self.target_bed_slot_id: int | None = None

        if self.is_bundle:
            self.frame_width: int = getattr(game_config, 'BUNDLE_FRAME_WIDTH', 32)
            self.frame_height: int = getattr(game_config, 'BUNDLE_FRAME_HEIGHT', 32)
        else:
            self.frame_width: int = getattr(game_config, 'SPRITE_FRAME_WIDTH', 64)
            self.frame_height: int = getattr(game_config, 'SPRITE_FRAME_HEIGHT', 64)
        
        self.sleep_frame_width: int = getattr(game_config, 'SLEEP_SPRITE_FRAME_WIDTH', 64)
        self.sleep_frame_height: int = getattr(game_config, 'SLEEP_SPRITE_FRAME_HEIGHT', 64)
        
        self.animations: dict = {} 
        self.current_animation_key: str = "idle_down" 
        self.current_frame_idx_in_animation: int = 0
        self.animation_timer: float = 0.0
        self.animation_speed: float = getattr(game_config, 'DEFAULT_ANIMATION_SPEED', 0.15)
        self.current_facing_direction: str = "down"

        char_sprite_base_path = getattr(game_config, 'CHARACTER_SPRITE_PATH', os.path.join('assets', 'images', 'characters'))

        if self.spritesheet_filename_ref:
            self.spritesheet_image = game_utils.load_image(self.spritesheet_filename_ref, base_path=char_sprite_base_path)
            if self.spritesheet_image:
                if self.is_bundle: self._load_bundle_animations()
                else: self._load_standard_animations()
            elif DEBUG_VERBOSE: print(f"CHARACTER WARNING: Standard spritesheet {self.spritesheet_filename_ref} not loaded for {self.name}")

        if self.sleep_spritesheet_filename_ref: 
            self.sleep_spritesheet_image = game_utils.load_image(self.sleep_spritesheet_filename_ref, base_path=char_sprite_base_path)
            if self.sleep_spritesheet_image:
                self._load_sleep_animations()
            elif DEBUG_VERBOSE: print(f"CHARACTER WARNING: Sleep spritesheet {self.sleep_spritesheet_filename_ref} not loaded for {self.name}")
        
        self._set_initial_animation_key()
        
        current_render_fw = self.sleep_frame_width if self.current_action == "resting_on_bed" and self.sleep_spritesheet_image else self.frame_width
        current_render_fh = self.sleep_frame_height if self.current_action == "resting_on_bed" and self.sleep_spritesheet_image else self.frame_height
        rect_w = current_render_fw if (self.spritesheet_image or self.sleep_spritesheet_image) and current_render_fw > 0 else self.fallback_radius * 2
        rect_h = current_render_fh if (self.spritesheet_image or self.sleep_spritesheet_image) and current_render_fh > 0 else self.fallback_radius * 2
        self.rect = pygame.Rect(0, 0, rect_w, rect_h)
        self.rect.center = (int(self.x), int(self.y))

        self.hunger = Hunger(self,getattr(game_config,'HUNGER_MAX_VALUE',100.),getattr(game_config,'HUNGER_INITIAL_MIN_PCT',0.),getattr(game_config,'HUNGER_INITIAL_MAX_PCT',0.6),getattr(game_config,'HUNGER_BASE_RATE',2.),getattr(game_config,'HUNGER_RATE_MULTIPLIERS',{}))
        self.energy = Energy(self,getattr(game_config,'ENERGY_MAX_VALUE',100.),getattr(game_config,'ENERGY_INITIAL_MIN_PCT',0.4),getattr(game_config,'ENERGY_INITIAL_MAX_PCT',1.),getattr(game_config,'ENERGY_BASE_DECAY_RATE',5.5),getattr(game_config,'ENERGY_DECAY_MULTIPLIERS',{}))
        self.social = Social(self,getattr(game_config,'SOCIAL_MAX_VALUE',100.),getattr(game_config,'SOCIAL_INITIAL_MIN_PCT',0.4),getattr(game_config,'SOCIAL_INITIAL_MAX_PCT',1.),getattr(game_config,'SOCIAL_BASE_DECAY_RATE',1.4),getattr(game_config,'SOCIAL_DECAY_MULTIPLIERS',{}))
        self.bladder = Bladder(self,getattr(game_config,'BLADDER_MAX_VALUE',100.),getattr(game_config,'BLADDER_INITIAL_MIN_PCT',0.),getattr(game_config,'BLADDER_INITIAL_MAX_PCT',0.65),getattr(game_config,'BLADDER_BASE_FILL_RATE',3.),getattr(game_config,'BLADDER_FILL_MULTIPLIERS',{}))
        self.fun = Fun(self,getattr(game_config,'FUN_MAX_VALUE',100.),getattr(game_config,'FUN_INITIAL_MIN_PCT',0.3),getattr(game_config,'FUN_INITIAL_MAX_PCT',1.),getattr(game_config,'FUN_BASE_DECAY_RATE',2.5),getattr(game_config,'FUN_DECAY_MULTIPLIERS',{}))
        self.hygiene = Hygiene(self,getattr(game_config,'HYGIENE_MAX_VALUE',100.),getattr(game_config,'HYGIENE_INITIAL_MIN_PCT',0.5),getattr(game_config,'HYGIENE_INITIAL_MAX_PCT',1.),getattr(game_config,'HYGIENE_BASE_DECAY_RATE',1.8),getattr(game_config,'HYGIENE_DECAY_MULTIPLIERS',{}))
        self.intimacy = Intimacy(self,getattr(game_config,'INTIMACY_MAX_VALUE',100.),getattr(game_config,'INTIMACY_INITIAL_MIN_PCT',0.),getattr(game_config,'INTIMACY_INITIAL_MAX_PCT',0.3),getattr(game_config,'INTIMACY_BASE_INCREASE_RATE',0.8),getattr(game_config,'INTIMACY_INCREASE_RATE_MULTIPLIERS',{}))

        self.age_in_total_game_days: float = random.uniform(getattr(game_config,'NPC_INITIAL_AGE_YEARS_MIN',20)*getattr(game_config,'GAME_DAYS_PER_YEAR',432), getattr(game_config,'NPC_INITIAL_AGE_YEARS_MAX',40)*getattr(game_config,'GAME_DAYS_PER_YEAR',432))
        self.is_pregnant: bool = False
        self.pregnancy_progress_days: float = 0.0

    def _get_sprite_from_sheet(self, source_spritesheet, x_on_sheet: int, y_on_sheet: int, width: int, height: int) -> pygame.Surface:
        if not source_spritesheet: surface = pygame.Surface((width,height),pygame.SRCALPHA); surface.fill((0,0,0,0)); return surface
        sprite_surface = pygame.Surface((width, height), pygame.SRCALPHA); sprite_surface.blit(source_spritesheet, (0,0), (x_on_sheet, y_on_sheet, width, height))
        return sprite_surface

    def _load_animation_frames(self, sheet_to_use_surf, sheet_row_idx: int, num_frms: int, frm_w: int, frm_h: int) -> list:
        frames = []
        if not sheet_to_use_surf or frm_w <= 0 or frm_h <= 0: return frames
        y_pos_sheet = sheet_row_idx * frm_h
        if y_pos_sheet + frm_h > sheet_to_use_surf.get_height(): return frames
        for i in range(num_frms):
            x_pos_sheet = i * frm_w
            if x_pos_sheet + frm_w > sheet_to_use_surf.get_width(): break
            frames.append(self._get_sprite_from_sheet(sheet_to_use_surf, x_pos_sheet, y_pos_sheet, frm_w, frm_h))
        return frames

    def _load_standard_animations(self):
        if not self.spritesheet_image: return
        wc = getattr(game_config, 'SPRITE_WALK_ANIM_FRAMES', 4); ic = getattr(game_config, 'SPRITE_IDLE_ANIM_FRAMES', 1)
        self.animations["walk_up"]=self._load_animation_frames(self.spritesheet_image,getattr(game_config,'ANIM_ROW_WALK_UP',8),wc,self.frame_width,self.frame_height)
        self.animations["walk_left"]=self._load_animation_frames(self.spritesheet_image,getattr(game_config,'ANIM_ROW_WALK_LEFT',9),wc,self.frame_width,self.frame_height)
        self.animations["walk_down"]=self._load_animation_frames(self.spritesheet_image,getattr(game_config,'ANIM_ROW_WALK_DOWN',10),wc,self.frame_width,self.frame_height)
        self.animations["walk_right"]=self._load_animation_frames(self.spritesheet_image,getattr(game_config,'ANIM_ROW_WALK_RIGHT',11),wc,self.frame_width,self.frame_height)
        self.animations["idle_up"]=self._load_animation_frames(self.spritesheet_image,getattr(game_config,'ANIM_ROW_IDLE_UP',22),ic,self.frame_width,self.frame_height)
        self.animations["idle_left"]=self._load_animation_frames(self.spritesheet_image,getattr(game_config,'ANIM_ROW_IDLE_LEFT',23),ic,self.frame_width,self.frame_height)
        self.animations["idle_down"]=self._load_animation_frames(self.spritesheet_image,getattr(game_config,'ANIM_ROW_IDLE_DOWN',24),ic,self.frame_width,self.frame_height)
        self.animations["idle_right"]=self._load_animation_frames(self.spritesheet_image,getattr(game_config,'ANIM_ROW_IDLE_RIGHT',25),ic,self.frame_width,self.frame_height)

    def _load_bundle_animations(self):
        if not self.spritesheet_image: return
        br = getattr(game_config, 'BUNDLE_ANIM_ROW', 4); nbf = getattr(game_config, 'BUNDLE_ANIM_FRAMES', 3)
        self.animations["idle_bundle"] = self._load_animation_frames(self.spritesheet_image, br, nbf, self.frame_width, self.frame_height)

    def _load_sleep_animations(self):
        if not self.sleep_spritesheet_image: return
        nsf = getattr(game_config, 'NUM_SLEEP_ANIM_FRAMES', 2) 
        self.animations["sleep_side_right"] = self._load_animation_frames(self.sleep_spritesheet_image, getattr(game_config, 'ANIM_ROW_SLEEP_SIDE_RIGHT',0), nsf, self.sleep_frame_width, self.sleep_frame_height)
        self.animations["sleep_on_back"] = self._load_animation_frames(self.sleep_spritesheet_image, getattr(game_config, 'ANIM_ROW_SLEEP_ON_BACK',1), nsf, self.sleep_frame_width, self.sleep_frame_height)
        self.animations["sleep_side_left"] = self._load_animation_frames(self.sleep_spritesheet_image, getattr(game_config, 'ANIM_ROW_SLEEP_SIDE_LEFT',2), nsf, self.sleep_frame_width, self.sleep_frame_height)

    def _set_initial_animation_key(self):
        initial_key = "idle_bundle" if self.is_bundle else "idle_" + self.current_facing_direction
        if initial_key in self.animations and self.animations[initial_key]:
            self.current_animation_key = initial_key
        elif self.animations: 
            self.current_animation_key = list(self.animations.keys())[0]
            if DEBUG_VERBOSE: print(f"CHARACTER WARNING ({self.name}): Initial animation '{initial_key}' not found or empty. Defaulting to '{self.current_animation_key}'.")
        else: 
            if DEBUG_VERBOSE: print(f"CHARACTER CRITICAL ({self.name}): No animations loaded. Spritesheet issue likely.")
            self.spritesheet_image = None 
            
    def randomize_needs(self):
        needs_config_map = {
            "hunger":   (self.hunger,   "HUNGER_INITIAL_MIN_PCT",   "HUNGER_INITIAL_MAX_PCT",   "DEBUG_HUNGER_INITIAL_MIN_PCT",   "DEBUG_HUNGER_INITIAL_MAX_PCT"),
            "energy":   (self.energy,   "ENERGY_INITIAL_MIN_PCT",   "ENERGY_INITIAL_MAX_PCT",   "DEBUG_ENERGY_INITIAL_MIN_PCT",   "DEBUG_ENERGY_INITIAL_MAX_PCT"),
            "social":   (self.social,   "SOCIAL_INITIAL_MIN_PCT",   "SOCIAL_INITIAL_MAX_PCT"),
            "bladder":  (self.bladder,  "BLADDER_INITIAL_MIN_PCT",  "BLADDER_INITIAL_MAX_PCT"),
            "fun":      (self.fun,      "FUN_INITIAL_MIN_PCT",      "FUN_INITIAL_MAX_PCT"),
            "hygiene":  (self.hygiene,  "HYGIENE_INITIAL_MIN_PCT",  "HYGIENE_INITIAL_MAX_PCT"),
            "intimacy": (self.intimacy, "INTIMACY_INITIAL_MIN_PCT", "INTIMACY_INITIAL_MAX_PCT")
        }
        debug_active = getattr(game_config, 'DEBUG_MODE_ACTIVE', False) # Questo è il flag specifico per la logica di randomizzazione, non DEBUG_VERBOSE generale
        for need_name_key, config_details_tuple in needs_config_map.items():
            need_object_instance = config_details_tuple[0]
            default_min_pct = getattr(game_config, config_details_tuple[1], 0.0)
            default_max_pct = getattr(game_config, config_details_tuple[2], 1.0)
            current_min_pct_to_use = default_min_pct
            current_max_pct_to_use = default_max_pct
            if debug_active and len(config_details_tuple) > 4:
                debug_min_attr_name = config_details_tuple[3]
                debug_max_attr_name = config_details_tuple[4]
                if hasattr(game_config, debug_min_attr_name):
                    current_min_pct_to_use = getattr(game_config, debug_min_attr_name)
                if hasattr(game_config, debug_max_attr_name):
                    current_max_pct_to_use = getattr(game_config, debug_max_attr_name)
            if current_min_pct_to_use >= current_max_pct_to_use:
                if DEBUG_VERBOSE: print(f"CHARACTER DEBUG Warning (randomize_needs for {self.name}.{need_name_key}): min_pct {current_min_pct_to_use} >= max_pct {current_max_pct_to_use}. Defaulting to 0.0-1.0 range.")
                current_min_pct_to_use = 0.0
                current_max_pct_to_use = 1.0
            need_object_instance.randomize_value(current_min_pct_to_use, current_max_pct_to_use)
        if DEBUG_VERBOSE: print(f"CHARACTER DEBUG: Needs randomized for {self.name} (Debug Active: {debug_active})")

    def get_formatted_age_string(self) -> str:
        years = int(self.age_in_total_game_days / getattr(game_config, 'GAME_DAYS_PER_YEAR', 432))
        days_into_year = int(self.age_in_total_game_days % getattr(game_config, 'GAME_DAYS_PER_YEAR', 432))
        months = int(days_into_year / getattr(game_config, 'DAYS_PER_MONTH', 24))
        days = int(days_into_year % getattr(game_config, 'DAYS_PER_MONTH', 24))
        return f"Age: {years}y, {months}m, {days}d"

    def update(self, dt_real: float, screen_width: int, screen_height: int, game_hours_advanced: float, 
               current_time_speed_index: int, is_char_externally_resting: bool, 
               tile_size: int, period_name: str):
        dx: float = 0.0; dy: float = 0.0; is_moving_this_frame: bool = False 
        is_in_blocking_action = self.current_action in ["phoning", "resting_on_bed", "romantic_interaction_action", "affectionate_interaction_action", "using_toilet"]
        can_move_now = current_time_speed_index > 0 and not is_char_externally_resting and not is_in_blocking_action

        if can_move_now:
            if self.current_action == "seeking_partner" and self.target_partner:
                self.target_destination = (self.target_partner.x, self.target_partner.y)
                self.current_path = None 
            elif self.current_path and self.target_destination is None: 
                if self.current_path_index < len(self.current_path):
                    target_node = self.current_path[self.current_path_index]
                    try:
                        target_world_x, target_world_y = _character_grid_to_world_center(target_node.x, target_node.y, tile_size)
                        self.target_destination = (target_world_x, target_world_y)
                    except AttributeError: self.current_path = None; self.target_destination = None 
                else: self.current_path = None; self.target_destination = None
            elif not self.current_path and self.current_action != "seeking_partner": self.target_destination = None

            if self.target_destination:
                target_x, target_y = self.target_destination; dist_x = target_x - self.x; dist_y = target_y - self.y
                distance_to_target = math.sqrt(dist_x**2 + dist_y**2)
                reach_threshold_for_node = tile_size / 2.0; stop_movement_threshold = self.fallback_radius * 0.25 
                if distance_to_target > stop_movement_threshold: 
                    angle = math.atan2(dist_y, dist_x)
                    movement_multiplier = getattr(game_config, 'NPC_MOVEMENT_SPEED_MULTIPLIERS', {}).get(current_time_speed_index, 1.0)
                    if current_time_speed_index == 0: movement_multiplier = 0.0 
                    effective_speed_this_frame = self.speed * movement_multiplier; move_this_frame_distance = effective_speed_this_frame * dt_real
                    if distance_to_target <= move_this_frame_distance: dx = dist_x; dy = dist_y
                    else: dx = math.cos(angle) * move_this_frame_distance; dy = math.sin(angle) * move_this_frame_distance
                if self.current_path and self.current_action != "seeking_partner": 
                    if distance_to_target <= reach_threshold_for_node:
                        self.current_path_index += 1
                        self.target_destination = None 
                        if self.current_path_index >= len(self.current_path): 
                            if DEBUG_VERBOSE: print(f"CHARACTER DEBUG ({self.name}): Reached end of A* path for {self.current_action}.")
                            self.current_path = None # A* path completato
                elif not self.current_path and self.current_action != "seeking_partner" and distance_to_target <= stop_movement_threshold : self.target_destination = None
            self.x += dx; self.y += dy
            if abs(dx) > 0.01 or abs(dy) > 0.01: is_moving_this_frame = True
            if is_moving_this_frame:
                if abs(dx) > abs(dy) * 0.8: self.current_facing_direction = "right" if dx > 0 else "left"
                elif abs(dy) > abs(dx) * 0.8: self.current_facing_direction = "down" if dy > 0 else "up"
            half_w = self.frame_width / 2 if self.frame_width > 0 else self.fallback_radius; half_h = self.frame_height / 2 if self.frame_height > 0 else self.fallback_radius
            self.x = max(half_w, min(self.x, screen_width - half_w)); self.y = max(half_h, min(self.y, screen_height - half_h))
            self.rect.center = (int(self.x), int(self.y)) 
        else: 
             if not is_in_blocking_action and self.current_action != "seeking_partner": self.target_destination = None 

        ghid = getattr(game_config,'GAME_HOURS_IN_DAY',28)
        if game_hours_advanced > 0 and ghid > 0 : self.age_in_total_game_days += game_hours_advanced / ghid
        if self.is_pregnant and game_hours_advanced > 0 and ghid > 0:
            days_advanced_this_frame = game_hours_advanced / ghid; self.pregnancy_progress_days += days_advanced_this_frame
            preg_term = getattr(game_config, 'PREGNANCY_TERM_GAME_DAYS', 24)
            if self.pregnancy_progress_days >= preg_term:
                if DEBUG_VERBOSE: print(f"CHARACTER EVENT: {self.name} has given birth! (Newborn NPC placeholder)")
                self.is_pregnant = False; self.pregnancy_progress_days = 0.0

        if game_hours_advanced > 0:
            if self.current_action == "resting_on_bed": self.rest(getattr(game_config, 'ENERGY_RECOVERY_RATE_PER_HOUR', 15.0), game_hours_advanced)
            if self.current_action == "phoning": self.socialize_over_time(getattr(game_config, 'SOCIAL_RECOVERY_RATE_PER_HOUR_PHONE', 40.0), game_hours_advanced)
            self.hunger.update(game_hours_advanced, period_name, self.current_action, is_char_externally_resting)
            self.energy.update(game_hours_advanced, period_name, self.current_action, is_char_externally_resting)
            self.social.update(game_hours_advanced, period_name, self.current_action, is_char_externally_resting)
            self.bladder.update(game_hours_advanced, period_name, self.current_action, is_char_externally_resting)
            self.fun.update(game_hours_advanced, period_name, self.current_action, is_char_externally_resting)
            self.hygiene.update(game_hours_advanced, period_name, self.current_action, is_char_externally_resting)
            self.intimacy.update(game_hours_advanced, period_name, self.current_action, is_char_externally_resting)
        
        if self.spritesheet_image or self.sleep_spritesheet_image:
            new_anim_key_selected = ""; current_render_fw_for_anim = self.frame_width; current_render_fh_for_anim = self.frame_height
            if self.is_bundle: new_anim_key_selected = "idle_bundle"
            elif self.current_action == "resting_on_bed":
                if "sleep_on_back" in self.animations and self.animations["sleep_on_back"]: new_anim_key_selected = "sleep_on_back" 
                else: new_anim_key_selected = "idle_" + self.current_facing_direction 
                current_render_fw_for_anim = self.sleep_frame_width; current_render_fh_for_anim = self.sleep_frame_height
            elif is_moving_this_frame: new_anim_key_selected = "walk_" + self.current_facing_direction
            else: new_anim_key_selected = "idle_" + self.current_facing_direction
            if new_anim_key_selected and new_anim_key_selected != self.current_animation_key:
                if new_anim_key_selected in self.animations and self.animations[new_anim_key_selected]:
                    self.current_animation_key = new_anim_key_selected
                    self.current_frame_idx_in_animation = 0; self.animation_timer = 0.0
            self.animation_timer += dt_real; active_animation_speed = self.animation_speed 
            if self.current_animation_key in self.animations:
                animation_frames_list = self.animations[self.current_animation_key]
                if animation_frames_list and self.animation_timer >= active_animation_speed:
                    self.animation_timer = 0.0
                    self.current_frame_idx_in_animation = (self.current_frame_idx_in_animation + 1) % len(animation_frames_list)
        self.rect.size = (current_render_fw_for_anim if current_render_fw_for_anim > 0 else self.fallback_radius*2, 
                          current_render_fh_for_anim if current_render_fh_for_anim > 0 else self.fallback_radius*2)
        self.rect.center = (int(self.x), int(self.y)) 

    def draw(self, screen: pygame.Surface, font: pygame.font.Font = None, text_color: tuple = (255,255,255)):
        active_frame_w = self.frame_width; active_frame_h = self.frame_height
        if self.current_action == "resting_on_bed" and self.sleep_spritesheet_image and \
           self.current_animation_key in ["sleep_side_right", "sleep_on_back", "sleep_side_left"]:
            active_frame_w = self.sleep_frame_width; active_frame_h = self.sleep_frame_height
        draw_topleft_x = int(self.x - active_frame_w / 2); draw_topleft_y = int(self.y - active_frame_h / 2)
        image_to_render = None; sheet_for_current_anim = self.spritesheet_image
        if self.current_action == "resting_on_bed" and self.sleep_spritesheet_image and self.current_animation_key.startswith("sleep_"):
            sheet_for_current_anim = self.sleep_spritesheet_image
        if sheet_for_current_anim and self.current_animation_key in self.animations:
            current_animation_frames_list = self.animations[self.current_animation_key]
            if current_animation_frames_list and self.current_frame_idx_in_animation < len(current_animation_frames_list):
                image_to_render = current_animation_frames_list[self.current_frame_idx_in_animation]
        if image_to_render: screen.blit(image_to_render, (draw_topleft_x, draw_topleft_y))
        else: pygame.draw.circle(screen, self.fallback_color, (int(self.x), int(self.y)), self.fallback_radius)
        if font: 
            text_anchor_y = self.rect.top - 5; status_txt_val = None; status_txt_col = text_color
            if self.current_action == "phoning": status_txt_val = "Phoning..."
            elif self.current_action == "resting_on_bed": status_txt_val = "Zzz..." 
            elif self.current_action == "seeking_partner": status_txt_val = "Seeking Partner <3"
            elif self.current_action == "romantic_interaction_action": status_txt_val = "<3 Romantic <3"; status_txt_col = getattr(game_config, 'HEART_COLOR_ROMANTIC', game_config.RED)
            elif self.current_action == "affectionate_interaction_action": status_txt_val = "<3 Affectionate <3"; status_txt_col = getattr(game_config, 'HEART_COLOR_AFFECTIONATE', (255,105,180))
            elif self.current_action == "wandering": status_txt_val = "Wandering..."
            elif self.current_action == "using_toilet": status_txt_val = "Using Toilet..."
            elif "seeking_" in self.current_action: status_txt_val = self.current_action.replace("seeking_", "Seeking ").replace("_", " ") + "..."
            if status_txt_val and self.current_action != "resting_on_bed": 
                try:
                    s_srf = font.render(status_txt_val, True, status_txt_col); s_rct = s_srf.get_rect(centerx=int(self.x), bottom=text_anchor_y)
                    screen.blit(s_srf, s_rct); text_anchor_y = s_rct.top - 2
                except: pass
            try: 
                n_srf = font.render(self.name, True, text_color); n_rct = n_srf.get_rect(centerx=int(self.x), bottom=text_anchor_y)
                screen.blit(n_srf, n_rct)
            except: pass
            if self.is_pregnant: 
                preg_term_val = getattr(game_config, 'PREGNANCY_TERM_GAME_DAYS', 24); preg_txt_val = f"Pregnant ({int(self.pregnancy_progress_days)}/{preg_term_val}d)"
                try:
                    p_srf = font.render(preg_txt_val, True, text_color); p_rct = p_srf.get_rect(centerx=int(self.x), top=self.rect.bottom + 2)
                    screen.blit(p_srf, p_rct)
                except: pass
            
    def eat(self, amount: float): self.hunger.satisfy(amount)
    def rest(self, recovery_rate_ph: float, hours_slept: float): self.energy.recover(recovery_rate_ph, hours_slept)
    def socialize_over_time(self, rate_ph: float, game_hrs_adv: float): self.social.satisfy(rate_ph * game_hrs_adv)
    def socialize(self, points: float): self.social.satisfy(points)
    def use_toilet(self, relief_amt: float): self.bladder.satisfy(relief_amt)
    def have_fun(self, fun_pts: float): self.fun.satisfy(fun_pts)
    def get_clean(self, hygiene_pts: float): self.hygiene.satisfy(hygiene_pts)
    def satisfy_intimacy_drive(self, amount_red: float): self.intimacy.satisfy(amount_red)
    
    def become_pregnant(self) -> bool:
        if self.gender == "female" and not self.is_pregnant:
            self.is_pregnant = True
            self.pregnancy_progress_days = 0.0
            if DEBUG_VERBOSE: print(f"CHARACTER EVENT: {self.name} has become pregnant!")
            return True
        return False

    def to_dict(self) -> dict:
        data = {
            "uuid": self.uuid, "name": self.name, "gender": self.gender,
            "x": self.x, "y": self.y, "current_action": self.current_action,
            "target_partner_uuid": self.target_partner.uuid if self.target_partner else None,
            "age_in_total_game_days": self.age_in_total_game_days,
            "is_pregnant": self.is_pregnant, 
            "pregnancy_progress_days": self.pregnancy_progress_days,
            "time_in_current_action": self.time_in_current_action,
            "spritesheet_filename": self.spritesheet_filename_ref,
            "sleep_spritesheet_filename": self.sleep_spritesheet_filename_ref,
            "needs": {
                "hunger": self.hunger.to_dict(), "energy": self.energy.to_dict(),
                "social": self.social.to_dict(), "bladder": self.bladder.to_dict(),
                "fun": self.fun.to_dict(), "hygiene": self.hygiene.to_dict(),
                "intimacy": self.intimacy.to_dict()
            }
        }
        return data

    @classmethod
    def from_data(cls, data: dict, fallback_color: tuple, fallback_radius: int, speed: float, is_bundle_load: bool = False):
        spritesheet_fn = data.get('spritesheet_filename')
        sleep_spritesheet_fn = data.get('sleep_spritesheet_filename')

        char = cls(name=data['name'], gender=data['gender'], x=data['x'], y=data['y'],
                   color=fallback_color, radius=fallback_radius, speed=speed,
                   spritesheet_filename=spritesheet_fn, 
                   sleep_spritesheet_filename=sleep_spritesheet_fn,
                   is_bundle=is_bundle_load, # Considerare se salvare/caricare is_bundle
                   existing_uuid=data.get('uuid'))

        char.current_action = data.get('current_action', "idle")
        char.age_in_total_game_days = data.get('age_in_total_game_days', 0)
        char.is_pregnant = data.get('is_pregnant', False)
        char.pregnancy_progress_days = data.get('pregnancy_progress_days', 0.0)
        char.time_in_current_action = data.get('time_in_current_action',0.0)
        
        if "needs" in data:
            needs_data = data["needs"]
            if "hunger" in needs_data: char.hunger.set_value(needs_data["hunger"].get("current_value", char.hunger.current_value))
            if "energy" in needs_data: char.energy.set_value(needs_data["energy"].get("current_value", char.energy.current_value))
            if "social" in needs_data: char.social.set_value(needs_data["social"].get("current_value", char.social.current_value))
            if "bladder" in needs_data: char.bladder.set_value(needs_data["bladder"].get("current_value", char.bladder.current_value))
            if "fun" in needs_data: char.fun.set_value(needs_data["fun"].get("current_value", char.fun.current_value))
            if "hygiene" in needs_data: char.hygiene.set_value(needs_data["hygiene"].get("current_value", char.hygiene.current_value))
            if "intimacy" in needs_data: char.intimacy.set_value(needs_data["intimacy"].get("current_value", char.intimacy.current_value))
        
        return char