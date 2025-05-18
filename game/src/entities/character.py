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
    from collections import deque
    from game import config
    from game.src.utils import game 
except ImportError as e:
    # Questa è un'importazione critica. Se fallisce, il modulo Character non può funzionare.
    print(f"CRITICAL ERROR (Character): Could not import 'game.config' or 'game.game_utils': {e}")
    print("Ensure these modules are accessible. The application will now exit.")
    sys.exit() # Esce se i moduli critici non sono trovati

# Leggi il flag di debug una volta, dopo aver importato (o tentato di importare) config
DEBUG_VERBOSE = getattr(config, 'DEBUG_AI_ACTIVE', False) # Usa lo stesso flag o uno dedicato

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

from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from game.src.managers.asset_manager import SpriteSheetManager
    from game.src.modules.game_state_module import GameState
    # from pygame.font import Font # Se vuoi tipizzare font

def _character_grid_to_world_center(grid_x: int, grid_y: int, tile_size_ref: int) -> tuple:
    world_x = grid_x * tile_size_ref + tile_size_ref / 2.0
    world_y = grid_y * tile_size_ref + tile_size_ref / 2.0
    return world_x, world_y

class Character:
    def __init__(self, name: str, gender: str, x: float, y: float,
                 game_state: 'GameState', # Aggiunto
                 sprite_sheet_manager: Optional['SpriteSheetManager'], # Aggiunto, reso opzionale se può essere None
                 font: Optional[pygame.font.Font], # Aggiunto, reso opzionale
                 color: tuple = (255,0,0), radius: int = 15, speed: float = 200,
                 spritesheet_filename: str = None, # Questo diventa la "chiave" o nome file principale
                 sleep_spritesheet_filename: str = None,
                 is_bundle: bool = False, existing_uuid: str = None,
                 sprite_key_override: str = None): # Aggiunto, anche se potremmo non usarlo direttamente se spritesheet_filename è la chiave

        self.uuid: str = existing_uuid if existing_uuid else str(uuid.uuid4())
        self.name: str = name
        self.gender: str = gender
        self.x: float = float(x)
        self.y: float = float(y)
        self.fallback_color: tuple = color
        self.fallback_radius: int = radius
        self.speed: float = float(speed)
        self.pending_intimacy_requester: Optional[Character] = None # O Optional[str] per l'UUID

        # Memorizza i manager e game_state
        self.game_state_ref: 'GameState' = game_state # Riferimento a game_state per i bisogni, ecc.
        self.sprite_sheet_manager_ref: Optional['SpriteSheetManager'] = sprite_sheet_manager # Riferimento al manager
        self.font_ref: Optional[pygame.font.Font] = font # Riferimento al font

        self.target_destination: tuple | None = None
        self.is_player: bool = False
        self.current_action: str = "idle"
        self.current_path: Optional[deque] = None # Modificato tipo per coerenza
        self.current_path_index: int = 0
        self.target_partner: Optional[Character] = None # Usare Character per type hint
        self.time_in_current_action: float = 0.0

        # Usa spritesheet_filename come riferimento principale per lo sheet del personaggio
        self.spritesheet_filename_ref: str | None = spritesheet_filename
        self.sleep_spritesheet_filename_ref: str | None = sleep_spritesheet_filename

        self.spritesheet_image: Optional[pygame.Surface] = None
        self.sleep_spritesheet_image: Optional[pygame.Surface] = None
        self.is_bundle: bool = is_bundle
        self.target_bed_slot_id: Optional[int] = None

        if self.is_bundle:
            self.frame_width: int = getattr(config, 'BUNDLE_FRAME_WIDTH', 32)
            self.frame_height: int = getattr(config, 'BUNDLE_FRAME_HEIGHT', 32)
        else:
            self.frame_width: int = getattr(config, 'SPRITE_FRAME_WIDTH', 64)
            self.frame_height: int = getattr(config, 'SPRITE_FRAME_HEIGHT', 64)

        self.sleep_frame_width: int = getattr(config, 'SLEEP_SPRITE_FRAME_WIDTH', 64)
        self.sleep_frame_height: int = getattr(config, 'SLEEP_SPRITE_FRAME_HEIGHT', 64)

        self.animations: dict = {}
        self.current_animation_key: str = "idle_down"
        self.current_frame_idx_in_animation: int = 0
        self.animation_timer: float = 0.0
        self.animation_speed: float = getattr(config, 'DEFAULT_ANIMATION_SPEED', 0.15)
        self.current_facing_direction: str = "down"


        # char_sprite_base_path = getattr(config, 'CHARACTER_SPRITE_PATH', os.path.join('assets', 'images', 'characters'))

        if self.sprite_sheet_manager_ref:
            if self.spritesheet_filename_ref: # Questo 'filename' è in realtà la chiave usata in AssetManager
                self.spritesheet_image = self.sprite_sheet_manager_ref.get_sheet(self.spritesheet_filename_ref)
                if self.spritesheet_image:
                    if self.is_bundle: self._load_bundle_animations()
                    else: self._load_standard_animations()
                elif DEBUG_VERBOSE: print(f"CHARACTER WARNING: Standard spritesheet '{self.spritesheet_filename_ref}' (key) not found in manager for {self.name}")

            if self.sleep_spritesheet_filename_ref: # Anche questa è una chiave
                self.sleep_spritesheet_image = self.sprite_sheet_manager_ref.get_sheet(self.sleep_spritesheet_filename_ref)
                if self.sleep_spritesheet_image:
                    self._load_sleep_animations()
                elif DEBUG_VERBOSE: print(f"CHARACTER WARNING: Sleep spritesheet '{self.sleep_spritesheet_filename_ref}' (key) not found in manager for {self.name}")
        else:
            if DEBUG_VERBOSE: print(f"CHARACTER WARNING: SpriteSheetManager not provided to {self.name}. Sprites will not be loaded.")

        self._set_initial_animation_key()

        current_render_fw = self.sleep_frame_width if self.current_action == "resting_on_bed" and self.sleep_spritesheet_image else self.frame_width
        current_render_fh = self.sleep_frame_height if self.current_action == "resting_on_bed" and self.sleep_spritesheet_image else self.frame_height
        rect_w = current_render_fw if (self.spritesheet_image or self.sleep_spritesheet_image) and current_render_fw > 0 else self.fallback_radius * 2
        rect_h = current_render_fh if (self.spritesheet_image or self.sleep_spritesheet_image) and current_render_fh > 0 else self.fallback_radius * 2
        self.rect = pygame.Rect(0, 0, rect_w, rect_h)
        self.rect.center = (int(self.x), int(self.y))

        # Passa self (character_owner) ai bisogni
        self.hunger = Hunger(self,getattr(config,'HUNGER_MAX_VALUE',100.),getattr(config,'HUNGER_INITIAL_MIN_PCT',0.),getattr(config,'HUNGER_INITIAL_MAX_PCT',0.6),getattr(config,'HUNGER_BASE_RATE',2.),getattr(config,'HUNGER_RATE_MULTIPLIERS',{}))
        self.energy = Energy(self,getattr(config,'ENERGY_MAX_VALUE',100.),getattr(config,'ENERGY_INITIAL_MIN_PCT',0.4),getattr(config,'ENERGY_INITIAL_MAX_PCT',1.),getattr(config,'ENERGY_BASE_DECAY_RATE',5.5),getattr(config,'ENERGY_DECAY_MULTIPLIERS',{}))
        self.social = Social(self,getattr(config,'SOCIAL_MAX_VALUE',100.),getattr(config,'SOCIAL_INITIAL_MIN_PCT',0.4),getattr(config,'SOCIAL_INITIAL_MAX_PCT',1.),getattr(config,'SOCIAL_BASE_DECAY_RATE',1.4),getattr(config,'SOCIAL_DECAY_MULTIPLIERS',{}))
        self.bladder = Bladder(self,getattr(config,'BLADDER_MAX_VALUE',100.),getattr(config,'BLADDER_INITIAL_MIN_PCT',0.),getattr(config,'BLADDER_INITIAL_MAX_PCT',0.65),getattr(config,'BLADDER_BASE_FILL_RATE',3.),getattr(config,'BLADDER_FILL_MULTIPLIERS',{}))
        self.fun = Fun(self,getattr(config,'FUN_MAX_VALUE',100.),getattr(config,'FUN_INITIAL_MIN_PCT',0.3),getattr(config,'FUN_INITIAL_MAX_PCT',1.),getattr(config,'FUN_BASE_DECAY_RATE',2.5),getattr(config,'FUN_DECAY_MULTIPLIERS',{}))
        self.hygiene = Hygiene(self,getattr(config,'HYGIENE_MAX_VALUE',100.),getattr(config,'HYGIENE_INITIAL_MIN_PCT',0.5),getattr(config,'HYGIENE_INITIAL_MAX_PCT',1.),getattr(config,'HYGIENE_BASE_DECAY_RATE',1.8),getattr(config,'HYGIENE_DECAY_MULTIPLIERS',{}))
        self.intimacy = Intimacy(self,getattr(config,'INTIMACY_MAX_VALUE',100.),getattr(config,'INTIMACY_INITIAL_MIN_PCT',0.),getattr(config,'INTIMACY_INITIAL_MAX_PCT',0.3),getattr(config,'INTIMACY_BASE_INCREASE_RATE',0.8),getattr(config,'INTIMACY_INCREASE_RATE_MULTIPLIERS',{}))

        self.age_in_total_game_days: float = random.uniform(getattr(config,'NPC_INITIAL_AGE_YEARS_MIN',20)*getattr(config,'GAME_DAYS_PER_YEAR',432), getattr(config,'NPC_INITIAL_AGE_YEARS_MAX',40)*getattr(config,'GAME_DAYS_PER_YEAR',432))
        self.is_pregnant: bool = False
        self.pregnancy_progress_days: float = 0.0
        # Inizializza PregnancyStatus (se non lo fai già nel metodo from_dict o altrove)
        # self.pregnancy_status = self.PregnancyStatus(self.game_state_ref) # Assicurati che PregnancyStatus sia definita

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
        wc = getattr(config, 'SPRITE_WALK_ANIM_FRAMES', 4); ic = getattr(config, 'SPRITE_IDLE_ANIM_FRAMES', 1)
        self.animations["walk_up"]=self._load_animation_frames(self.spritesheet_image,getattr(config,'ANIM_ROW_WALK_UP',8),wc,self.frame_width,self.frame_height)
        self.animations["walk_left"]=self._load_animation_frames(self.spritesheet_image,getattr(config,'ANIM_ROW_WALK_LEFT',9),wc,self.frame_width,self.frame_height)
        self.animations["walk_down"]=self._load_animation_frames(self.spritesheet_image,getattr(config,'ANIM_ROW_WALK_DOWN',10),wc,self.frame_width,self.frame_height)
        self.animations["walk_right"]=self._load_animation_frames(self.spritesheet_image,getattr(config,'ANIM_ROW_WALK_RIGHT',11),wc,self.frame_width,self.frame_height)
        self.animations["idle_up"]=self._load_animation_frames(self.spritesheet_image,getattr(config,'ANIM_ROW_IDLE_UP',22),ic,self.frame_width,self.frame_height)
        self.animations["idle_left"]=self._load_animation_frames(self.spritesheet_image,getattr(config,'ANIM_ROW_IDLE_LEFT',23),ic,self.frame_width,self.frame_height)
        self.animations["idle_down"]=self._load_animation_frames(self.spritesheet_image,getattr(config,'ANIM_ROW_IDLE_DOWN',24),ic,self.frame_width,self.frame_height)
        self.animations["idle_right"]=self._load_animation_frames(self.spritesheet_image,getattr(config,'ANIM_ROW_IDLE_RIGHT',25),ic,self.frame_width,self.frame_height)

    def _load_bundle_animations(self):
        if not self.spritesheet_image: return
        br = getattr(config, 'BUNDLE_ANIM_ROW', 4); nbf = getattr(config, 'BUNDLE_ANIM_FRAMES', 3)
        self.animations["idle_bundle"] = self._load_animation_frames(self.spritesheet_image, br, nbf, self.frame_width, self.frame_height)

    def _load_sleep_animations(self):
        if not self.sleep_spritesheet_image: return
        nsf = getattr(config, 'NUM_SLEEP_ANIM_FRAMES', 2) 
        self.animations["sleep_side_right"] = self._load_animation_frames(self.sleep_spritesheet_image, getattr(config, 'ANIM_ROW_SLEEP_SIDE_RIGHT',0), nsf, self.sleep_frame_width, self.sleep_frame_height)
        self.animations["sleep_on_back"] = self._load_animation_frames(self.sleep_spritesheet_image, getattr(config, 'ANIM_ROW_SLEEP_ON_BACK',1), nsf, self.sleep_frame_width, self.sleep_frame_height)
        self.animations["sleep_side_left"] = self._load_animation_frames(self.sleep_spritesheet_image, getattr(config, 'ANIM_ROW_SLEEP_SIDE_LEFT',2), nsf, self.sleep_frame_width, self.sleep_frame_height)

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
        debug_active = getattr(config, 'DEBUG_MODE_ACTIVE', False) # Questo è il flag specifico per la logica di randomizzazione, non DEBUG_VERBOSE generale
        for need_name_key, config_details_tuple in needs_config_map.items():
            need_object_instance = config_details_tuple[0]
            default_min_pct = getattr(config, config_details_tuple[1], 0.0)
            default_max_pct = getattr(config, config_details_tuple[2], 1.0)
            current_min_pct_to_use = default_min_pct
            current_max_pct_to_use = default_max_pct
            if debug_active and len(config_details_tuple) > 4:
                debug_min_attr_name = config_details_tuple[3]
                debug_max_attr_name = config_details_tuple[4]
                if hasattr(config, debug_min_attr_name):
                    current_min_pct_to_use = getattr(config, debug_min_attr_name)
                if hasattr(config, debug_max_attr_name):
                    current_max_pct_to_use = getattr(config, debug_max_attr_name)
            if current_min_pct_to_use >= current_max_pct_to_use:
                if DEBUG_VERBOSE: print(f"CHARACTER DEBUG Warning (randomize_needs for {self.name}.{need_name_key}): min_pct {current_min_pct_to_use} >= max_pct {current_max_pct_to_use}. Defaulting to 0.0-1.0 range.")
                current_min_pct_to_use = 0.0
                current_max_pct_to_use = 1.0
            need_object_instance.randomize_value(current_min_pct_to_use, current_max_pct_to_use)
        if DEBUG_VERBOSE: print(f"CHARACTER DEBUG: Needs randomized for {self.name} (Debug Active: {debug_active})")

    def get_formatted_age_string(self) -> str:
        years = int(self.age_in_total_game_days / getattr(config, 'GAME_DAYS_PER_YEAR', 432))
        days_into_year = int(self.age_in_total_game_days % getattr(config, 'GAME_DAYS_PER_YEAR', 432))
        months = int(days_into_year / getattr(config, 'DAYS_PER_MONTH', 24))
        days = int(days_into_year % getattr(config, 'DAYS_PER_MONTH', 24))
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
                    movement_multiplier = getattr(config, 'NPC_MOVEMENT_SPEED_MULTIPLIERS', {}).get(current_time_speed_index, 1.0)
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

        ghid = getattr(config,'GAME_HOURS_IN_DAY',28)
        if game_hours_advanced > 0 and ghid > 0 : self.age_in_total_game_days += game_hours_advanced / ghid
        if self.is_pregnant and game_hours_advanced > 0 and ghid > 0:
            days_advanced_this_frame = game_hours_advanced / ghid; self.pregnancy_progress_days += days_advanced_this_frame
            preg_term = getattr(config, 'PREGNANCY_TERM_GAME_DAYS', 24)
            if self.pregnancy_progress_days >= preg_term:
                if DEBUG_VERBOSE: print(f"CHARACTER EVENT: {self.name} has given birth! (Newborn NPC placeholder)")
                self.is_pregnant = False; self.pregnancy_progress_days = 0.0

        if game_hours_advanced > 0:
            if self.current_action == "resting_on_bed": self.rest(getattr(config, 'ENERGY_RECOVERY_RATE_PER_HOUR', 15.0), game_hours_advanced)
            if self.current_action == "phoning": self.socialize_over_time(getattr(config, 'SOCIAL_RECOVERY_RATE_PER_HOUR_PHONE', 40.0), game_hours_advanced)
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
            elif self.current_action == "romantic_interaction_action": status_txt_val = "<3 Romantic <3"; status_txt_col = getattr(config, 'HEART_COLOR_ROMANTIC', config.RED)
            elif self.current_action == "affectionate_interaction_action": status_txt_val = "<3 Affectionate <3"; status_txt_col = getattr(config, 'HEART_COLOR_AFFECTIONATE', (255,105,180))
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
                preg_term_val = getattr(config, 'PREGNANCY_TERM_GAME_DAYS', 24); preg_txt_val = f"Pregnant ({int(self.pregnancy_progress_days)}/{preg_term_val}d)"
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

    def to_dict(self):
        """Converte lo stato completo dell'NPC in un dizionario serializzabile."""
        rect_data = [self.rect.x, self.rect.y, self.rect.width, self.rect.height] if self.rect else None
        needs_data = {name: need.to_dict() for name, need in self.needs.items()}
        path_data = list(self.path) if self.path else None

        needs_data_to_save = {
            "hunger": self.hunger.to_dict(),
            "energy": self.energy.to_dict(),
            "social": self.social.to_dict(),
            "bladder": self.bladder.to_dict(),
            "fun": self.fun.to_dict(),
            "hygiene": self.hygiene.to_dict(),
            "intimacy": self.intimacy.to_dict()
        }

        return {
            "uuid": self.uuid, # Coerenza con from_dict
            "name": self.name,
            "age_in_total_game_days": self.age_in_total_game_days, # Coerenza con from_dict
            "gender": self.gender,
            "x": self.x, # Salva le coordinate dirette
            "y": self.y,
            "fallback_color": list(self.fallback_color),
            "fallback_radius": self.fallback_radius,
            "speed": self.speed,
            "spritesheet_filename_ref": self.spritesheet_filename_ref,
            "sleep_spritesheet_filename_ref": self.sleep_spritesheet_filename_ref,
            "is_bundle": self.is_bundle,
            "current_action": self.current_action, # Coerenza con from_dict
            # "current_path": [node.to_tuple() for node in self.current_path] if self.current_path else None, # Se i nodi hanno to_tuple()
            "current_path": None, # Ricalcolare il path è spesso più sicuro
            "current_path_index": self.current_path_index,
            "target_destination": list(self.target_destination) if self.target_destination else None,
            "target_partner_uuid": self.target_partner.uuid if self.target_partner else None, # Salva UUID
            "target_bed_slot_id": self.target_bed_slot_id,
            "time_in_current_action": self.time_in_current_action,
            "is_pregnant": self.is_pregnant,
            "pregnancy_progress_days": self.pregnancy_progress_days,
            # "pregnancy_status": self.pregnancy_status.to_dict(), # Se PregnancyStatus ha to_dict
            "needs_data": needs_data_to_save # Chiave corretta
        }

    @classmethod
    def from_dict(cls, data, sprite_sheet_manager_param, font_param, game_state_param):
        char_id = data.get("uuid", f"npc_{uuid.uuid4()}") # Coerenza con __init__
        name = data.get("name", "Loaded NPC")
        age_days = data.get("age_in_total_game_days", 20 * getattr(config, 'GAME_DAYS_PER_YEAR', 432))
        gender = data.get("gender", random.choice(["male", "female"]))

        rect_data = data.get("rect") # 'rect' è una lista [x, y, w, h]
        initial_x = rect_data[0] + rect_data[2]/2 if rect_data else config.SCREEN_WIDTH / 2 # Centro x
        initial_y = rect_data[1] + rect_data[3]/2 if rect_data else config.SCREEN_HEIGHT / 2 # Centro y

        # Recupera i nomi dei file degli spritesheet dal salvataggio
        spritesheet_fn = data.get("spritesheet_filename_ref") # Coerente con to_dict
        sleep_spritesheet_fn = data.get("sleep_spritesheet_filename_ref") # Coerente con to_dict
        is_bundle_loaded = data.get("is_bundle", False)


        character = cls(
            name=name,
            gender=gender,
            x=initial_x,
            y=initial_y,
            game_state=game_state_param, # Passa game_state
            sprite_sheet_manager=sprite_sheet_manager_param, # Passa il manager
            font=font_param, # Passa il font
            spritesheet_filename=spritesheet_fn, # Passa la chiave/nome file
            sleep_spritesheet_filename=sleep_spritesheet_fn, # Passa la chiave/nome file
            is_bundle=is_bundle_loaded,
            existing_uuid=char_id,
            # sprite_key_override non è più necessario se spritesheet_filename è la chiave principale
            # Se lo vuoi mantenere, aggiungilo alla firma di __init__
            color=tuple(data.get("fallback_color", (255,0,0))), # Usa fallback_color
            radius=data.get("fallback_radius", 15),
            speed=data.get("speed", config.CHARACTER_SPEED)
        )

        # Popola attributi che __init__ potrebbe non coprire dal dizionario 'data'
        # (molti di questi ora sono gestiti da __init__ o sono impostati ai default lì)

        character.current_action = data.get("current_action", "idle") # Coerenza con Character.current_action
        # current_animation_key e current_frame_idx_in_animation sono gestiti da _set_initial_animation_key e update

        path_data_raw = data.get("current_path") # current_path è salvato come lista di tuple (x,y)
        if path_data_raw:
            # Se AStarNode ha un metodo from_tuple o simile per la ricostruzione, usalo
            # Altrimenti, se salvi solo tuple (x,y), la conversione a Node potrebbe essere complessa qui
            # Per ora, assumiamo che AStarNode possa essere ricreato se necessario o che il path sia solo di tuple
            # Questo path è di nodi griglia, non world coords.
            # La ricostruzione dei Node objects da semplici tuple (x,y) è problematica qui.
            # È meglio che il path venga ricalcolato se necessario, o che i nodi siano serializzabili.
            # Per ora, resettiamo il path, l'IA lo ricalcolerà.
            character.current_path = None #deque([AStarNode.from_tuple(p_tuple) for p_tuple in path_data_raw])
            character.current_path_index = data.get("current_path_index", 0)
        else:
            character.current_path = None

        character.target_destination = tuple(data.get("target_destination")) if data.get("target_destination") else None

        # Bisogni: __init__ già li inizializza e li randomizza.
        # from_dict dovrebbe SOVRASCRIVERE i valori dei bisogni con quelli salvati.
        needs_data_loaded = data.get("needs_data", {}) # Assumendo che 'needs_data' sia la chiave corretta
        for need_name_key, need_saved_data in needs_data_loaded.items():
            if hasattr(character, need_name_key.lower()): # es. character.hunger
                need_object_to_update = getattr(character, need_name_key.lower())
                # Assumiamo che BaseNeed e le sue sottoclassi abbiano un metodo per impostare lo stato da un dizionario,
                # o almeno un set_value.
                if hasattr(need_object_to_update, 'set_value') and 'current_value' in need_saved_data:
                    need_object_to_update.set_value(need_saved_data['current_value'])
                    if hasattr(need_object_to_update, 'last_updated_total_seconds') and 'last_updated_total_seconds' in need_saved_data:
                         need_object_to_update.last_updated_total_seconds = need_saved_data['last_updated_total_seconds']
                # Oppure un metodo from_dict più completo nel BaseNeed:
                # need_object_to_update.from_data(need_saved_data) # Se BaseNeed.from_data è adatto
            elif DEBUG_VERBOSE:
                print(f"CHARACTER from_dict WARNING: Need '{need_name_key}' from save data not found as attribute on character '{character.name}'.")


        character.is_pregnant = data.get("is_pregnant", False)
        character.pregnancy_progress_days = data.get("pregnancy_progress_days", 0.0)
        # pregnancy_status (se hai una sottoclasse e un metodo from_dict per essa)

        character.target_partner_uuid = data.get("target_partner_uuid") # Salva UUID, ricostruisci il riferimento dopo
        character.target_bed_slot_id = data.get("target_bed_slot_id")
        # ... (altri attributi)

        return character

    # === Sottoclasse Need ===
    class Need:
        def __init__(self, name, game_state, max_value=100, decay_rate_per_hour=5, low_threshold=30, critical_threshold=10, period_multipliers=None):
            # ... (codice __init__ esistente di Need) ...
            # Assicurati che tutti questi attributi siano definiti qui
            self.name = name
            self.game_state = game_state 
            self.max_value = max_value
            self.current_value = max_value
            self.decay_rate_per_hour = decay_rate_per_hour
            self.low_threshold = low_threshold
            self.critical_threshold = critical_threshold
            
            self.period_multipliers = period_multipliers if period_multipliers is not None else {
                "Alba": 1.0, "Mattina": 1.0, "Mezzogiorno": 1.0,
                "Pomeriggio": 1.0, "Tramonto": 1.0, "Sera": 1.0,
                "Notte": 0.5, "Tarda Notte": 0.5 # Esempio: il decadimento dei bisogni rallenta di notte
            }
            
            # Aggiunto per tracciare l'ultimo aggiornamento basato sul tempo di gioco globale
            self.last_updated_total_seconds = self.game_state.game_time_handler.total_game_seconds_elapsed if self.game_state and hasattr(self.game_state, 'game_time_handler') else 0
            
            # Testo e colore per la UI (verranno aggiornati)
            self.text_color = (0, 0, 0) # Default black
            self.font = pygame.font.Font(config.FONT_NAME, 12) # Usa un font specifico per i bisogni
            self.update_text_color()

        def update(self, total_game_seconds_elapsed, current_period_name):
            if self.game_state is None or not hasattr(self.game_state, 'game_time_handler'):
                # print(f"Attenzione: game_state o game_time_handler non disponibile per il bisogno {self.name}")
                return

            time_delta_seconds = total_game_seconds_elapsed - self.last_updated_total_seconds

            if time_delta_seconds >= config.NEED_UPDATE_INTERVAL_SECONDS: # Aggiorna solo se è passato abbastanza tempo
                hours_passed = time_delta_seconds / 3600.0
                
                period_multiplier = self.period_multipliers.get(current_period_name, 1.0)
                decay_amount = self.decay_rate_per_hour * hours_passed * period_multiplier
                
                self.current_value -= decay_amount
                self.current_value = max(0, min(self.current_value, self.max_value))
                self.last_updated_total_seconds = total_game_seconds_elapsed
                self.update_text_color()

        def update_text_color(self):
            if self.current_value <= self.critical_threshold:
                self.text_color = (255, 0, 0)  # Rosso
            elif self.current_value <= self.low_threshold:
                self.text_color = (255, 165, 0)  # Arancione
            else:
                self.text_color = (0, 128, 0)  # Verde scuro (più leggibile del verde brillante)
        
        def get_display_text(self):
            return f"{self.name}: {int(self.current_value)}/{self.max_value}"

        def render_text(self):
            return self.font.render(self.get_display_text(), True, self.text_color)

        def to_dict(self):
            return {
                "name": self.name,
                "current_value": self.current_value,
                "max_value": self.max_value,
                "decay_rate_per_hour": self.decay_rate_per_hour,
                "low_threshold": self.low_threshold,
                "critical_threshold": self.critical_threshold,
                "last_updated_total_seconds": self.last_updated_total_seconds,
                "period_multipliers": self.period_multipliers,
            }

        @classmethod
        def from_dict(cls, data, game_state): 
            if game_state is None:
                # Questo è un problema, perché game_state è necessario per __init__
                # Potremmo dover sollevare un errore o avere un game_state di fallback/globale
                # per ora, stampiamo un avviso e cerchiamo di procedere con cautela.
                print(f"ATTENZIONE: game_state non fornito a Need.from_dict per il bisogno {data.get('name')}. Alcune funzionalità potrebbero non essere corrette.")
            
            # Crea l'istanza di Need, passando game_state
            need = cls(
                name=data.get("name", "UnknownNeed"),
                game_state=game_state, 
                max_value=data.get("max_value", 100),
                decay_rate_per_hour=data.get("decay_rate_per_hour", 5),
                low_threshold=data.get("low_threshold", 30),
                critical_threshold=data.get("critical_threshold", 10),
                period_multipliers=data.get("period_multipliers")
            )
            # Imposta i valori caricati
            need.current_value = data.get("current_value", need.max_value)
            need.last_updated_total_seconds = data.get("last_updated_total_seconds", 
                                                       game_state.game_time_handler.total_game_seconds_elapsed if game_state and hasattr(game_state, 'game_time_handler') else 0)
            need.update_text_color() # Aggiorna il colore del testo in base al valore caricato
            return need

    # === Sottoclasse PregnancyStatus ===
    class PregnancyStatus:
        def __init__(self, game_state):
            # ... (codice __init__ esistente di PregnancyStatus) ...
            self.game_state = game_state # Assicurati che game_state sia memorizzato
            self.current_status = "not_pregnant"  # "not_pregnant", "early_stage", "mid_stage", "late_stage", "postpartum_cooldown"
            self.not_pregnant_timer = 0  # Timer per il cooldown post-parto in secondi di gioco

        # ... (metodo update esistente di PregnancyStatus) ...
        def update(self, actual_dt):
            if self.current_status == "postpartum_cooldown":
                self.not_pregnant_timer -= actual_dt
                if self.not_pregnant_timer <= 0:
                    self.current_status = "not_pregnant"
                    self.not_pregnant_timer = 0
                    # print(f"NPC {self.owner.name} cooldown post-parto terminato.") # self.owner non è definito qui
        
        def start_pregnancy(self):
            if self.current_status == "not_pregnant":
                self.current_status = "early_stage" # O come gestisci gli stadi
                # Qui potresti inizializzare days_into_pregnancy sull'NPC proprietario
                # print(f"NPC {self.owner.name} ha iniziato una gravidanza.") # self.owner non definito
                return True
            return False

        def reset_pregnancy(self):
            # Chiamato dopo il parto per iniziare il cooldown
            self.current_status = "postpartum_cooldown"
            if self.game_state and hasattr(self.game_state, 'config_constants'):
                cooldown_seconds = self.game_state.config_constants.get('NPC_POST_PREGNANCY_COOLDOWN_SECONDS', config.NPC_POST_PREGNANCY_COOLDOWN_SECONDS)
            else: # Fallback se config_constants non è in game_state
                cooldown_seconds = config.NPC_POST_PREGNANCY_COOLDOWN_SECONDS
            self.not_pregnant_timer = cooldown_seconds
            print(f"NPC {self.owner.name} in cooldown post-parto per {cooldown_seconds} secondi.") # self.owner non definito


        def to_dict(self):
            return {
                "current_status": self.current_status,
                "not_pregnant_timer": self.not_pregnant_timer
            }

        @classmethod
        def from_dict(cls, data, game_state):
            if game_state is None:
                # Come per Need, game_state è importante.
                print(f"ATTENZIONE: game_state non fornito a PregnancyStatus.from_dict. Cooldown potrebbe non funzionare correttamente.")
            
            status_obj = cls(game_state) 
            status_obj.current_status = data.get("current_status", "not_pregnant")
            status_obj.not_pregnant_timer = data.get("not_pregnant_timer", 0)
            return status_obj
