# game/src/entities/character.py
import pygame
import math
import random
import uuid
import os
import sys
import logging
from collections import deque # Per current_path
from typing import TYPE_CHECKING, Optional, List, Dict, Any

# Importa dal package 'game'
try:
    from game import config
    from game.src.utils import game as game_utils
except ImportError as e:
    print(f"CRITICAL ERROR (Character): Could not import 'game.config' or 'game.src.utils.game': {e}")
    sys.exit()

# Importa i componenti
try:
    from .components.needs_component import NeedsComponent
    from .components.finance_component import FinanceComponent
    from .components.mood_component import MoodComponent
    from .components.aspiration_component import AspirationComponent
    from .components.career_component import CareerComponent
    from .components.skill_component import SkillComponent
    from .components.relationship_component import RelationshipComponent, Relationship # Importa anche Relationship per type hints
    from .components.inventory_component import InventoryComponent, Item # Importa Item per type hints
    from .components.status_component import StatusComponent
except ImportError as e_comp:
    print(f"ERROR (Character): Could not import Character components: {e_comp}. Placeholder classes will be used.")
    class PlaceholderComponent:
        def __init__(self, *args, **kwargs): pass
        def update(self, *args, **kwargs): pass
        def to_dict(self): return {}
        @classmethod
        def from_dict(cls, data, *args, **kwargs): return cls()
    NeedsComponent = FinanceComponent = MoodComponent = AspirationComponent = CareerComponent = \
    SkillComponent = RelationshipComponent = InventoryComponent = StatusComponent = PlaceholderComponent
    class Item: pass # Placeholder per Item se l'import fallisce
    class Relationship: pass # Placeholder


# Forward declaration per Camera e altri manager
if TYPE_CHECKING:
    from game.src.utils.camera import Camera
    from game.src.managers.asset_manager import SpriteSheetManager
    from game.src.modules.game_state_module import GameState

logger = logging.getLogger(__name__)
DEBUG_VERBOSE = getattr(config, 'DEBUG_AI_ACTIVE', False)


class Character:
    def __init__(self, name: str, gender: str, x: float, y: float,
                 game_state: 'GameState',
                 sprite_sheet_manager: Optional['SpriteSheetManager'],
                 font: Optional[pygame.font.Font],
                 color: tuple = (255,0,0), radius: int = 15, speed: float = 200,
                 spritesheet_filename: Optional[str] = None,
                 sleep_spritesheet_filename: Optional[str] = None,
                 is_bundle: bool = False, existing_uuid: Optional[str] = None,
                 initial_action: str = "idle",
                 household_id: Optional[str] = None): # Aggiunto household_id

        self.uuid: str = existing_uuid if existing_uuid else str(uuid.uuid4())
        self.name: str = name
        self.gender: str = gender
        self.game_state_ref: 'GameState' = game_state
        self.sprite_sheet_manager_ref: Optional['SpriteSheetManager'] = sprite_sheet_manager
        self.font_ref: Optional[pygame.font.Font] = font

        self.x: float = float(x); self.y: float = float(y)
        self.fallback_color: tuple = color; self.fallback_radius: int = radius
        self.speed: float = float(speed); self.is_bundle: bool = is_bundle

        self.spritesheet_filename_ref: Optional[str] = spritesheet_filename
        self.sleep_spritesheet_filename_ref: Optional[str] = sleep_spritesheet_filename
        self.spritesheet_image: Optional[pygame.Surface] = None
        self.sleep_spritesheet_image: Optional[pygame.Surface] = None
        
        frame_dims = {'width': 64, 'height': 64}
        if self.is_bundle:
            frame_dims['width'] = getattr(config, 'BUNDLE_FRAME_WIDTH', 32)
            frame_dims['height'] = getattr(config, 'BUNDLE_FRAME_HEIGHT', 32)
        else:
            frame_dims['width'] = getattr(config, 'SPRITE_FRAME_WIDTH', 64)
            frame_dims['height'] = getattr(config, 'SPRITE_FRAME_HEIGHT', 64)
        self.frame_width: int = frame_dims['width']
        self.frame_height: int = frame_dims['height']
        self.sleep_frame_width: int = getattr(config, 'SLEEP_SPRITE_FRAME_WIDTH', 64)
        self.sleep_frame_height: int = getattr(config, 'SLEEP_SPRITE_FRAME_HEIGHT', 64)

        self.current_action: str = initial_action
        self.current_facing_direction: str = "down"

        self.animations: Dict[str, List[pygame.Surface]] = {}
        self.current_animation_key: str = "idle_down"
        self.current_frame_idx_in_animation: int = 0
        self.animation_timer: float = 0.0
        self.animation_speed: float = getattr(config, 'DEFAULT_ANIMATION_SPEED', 0.15)
        self._load_character_sprites()

        initial_rect_w, initial_rect_h = self.frame_width, self.frame_height
        if initial_action == "resting_on_bed" and self.sleep_spritesheet_image:
            initial_rect_w, initial_rect_h = self.sleep_frame_width, self.sleep_frame_height
        self.rect = pygame.Rect(0, 0, max(1, initial_rect_w), max(1, initial_rect_h))
        self.rect.center = (int(self.x), int(self.y))

        self.target_destination: Optional[Tuple[float, float]] = None
        self.current_path: Optional[deque] = None
        self.current_path_index: int = 0
        self.target_partner: Optional['Character'] = None
        self.time_in_current_action: float = 0.0
        self.is_interacting: bool = False
        self.current_action_before_movement: Optional[str] = None
        self.previous_action_was_movement_to_target: bool = False
        
        self.is_on_bed: bool = (initial_action == "resting_on_bed")
        self.bed_object_id: Optional[str] = None
        self.bed_slot_index: int = -1
        self.target_bed_slot_id: Optional[int] = None
        
        # --- Componenti ---
        self.needs = NeedsComponent(character_owner=self)
        self.finances = FinanceComponent(character_owner=self, initial_money=random.uniform(
            getattr(config, 'NPC_INITIAL_MONEY_MIN', 500),
            getattr(config, 'NPC_INITIAL_MONEY_MAX', 2000)
        ))
        self.mood = MoodComponent(character_owner=self) # Rinominato da self.emotions
        self.aspirations = AspirationComponent(character_owner=self)
        self.career = CareerComponent(character_owner=self)
        self.skills = SkillComponent(character_owner=self)
        self.relationships = RelationshipComponent(character_owner=self, owner_uuid=self.uuid)
        self.inventory = InventoryComponent(character_owner=self, capacity=getattr(config, 'NPC_PERSONAL_INVENTORY_CAPACITY', 10))
        self.status = StatusComponent(character_owner=self, initial_age_days=random.uniform(
            getattr(config,'NPC_INITIAL_AGE_YEARS_MIN',20) * getattr(config,'GAME_DAYS_PER_YEAR',432),
            getattr(config,'NPC_INITIAL_AGE_YEARS_MAX',40) * getattr(config,'GAME_DAYS_PER_YEAR',432)
        ))
        
        self.pending_intimacy_requester: Optional['Character'] = None
        self.household_id: Optional[str] = household_id # ID della famiglia/casa a cui appartiene

        # Per il salvataggio/caricamento di relazioni che coinvolgono NPC non ancora istanziati
        self.target_partner_uuid_to_resolve: Optional[str] = None
        self.pending_intimacy_requester_uuid_to_resolve: Optional[str] = None


        if DEBUG_VERBOSE:
            logger.debug(f"Character ({self.name} - {self.uuid}) initialized. Pos: ({self.x:.0f},{self.y:.0f}), Action: {self.current_action}")

    # --- Metodi di Caricamento Sprite e Animazioni (come prima) ---
    def _load_character_sprites(self):
        if self.sprite_sheet_manager_ref:
            if self.spritesheet_filename_ref:
                self.spritesheet_image = self.sprite_sheet_manager_ref.get_sheet(self.spritesheet_filename_ref)
                if self.spritesheet_image:
                    if self.is_bundle: self._load_bundle_animations()
                    else: self._load_standard_animations()
                elif DEBUG_VERBOSE: 
                    logger.warning(f"Standard spritesheet '{self.spritesheet_filename_ref}' (key) non trovato per {self.name}")
            if self.sleep_spritesheet_filename_ref:
                self.sleep_spritesheet_image = self.sprite_sheet_manager_ref.get_sheet(self.sleep_spritesheet_filename_ref)
                if self.sleep_spritesheet_image: self._load_sleep_animations()
                elif DEBUG_VERBOSE: 
                    logger.warning(f"Sleep spritesheet '{self.sleep_spritesheet_filename_ref}' (key) non trovato per {self.name}")
        elif DEBUG_VERBOSE: logger.warning(f"SpriteSheetManager non fornito a {self.name}. Sprites non caricati.")
        self._set_initial_animation_key()

    def _get_sprite_from_sheet(self, source_spritesheet: Optional[pygame.Surface], x_on_sheet: int, y_on_sheet: int, width: int, height: int) -> Optional[pygame.Surface]:
        if not source_spritesheet or width <= 0 or height <= 0: return None
        if x_on_sheet + width > source_spritesheet.get_width() or y_on_sheet + height > source_spritesheet.get_height():
            logger.warning(f"Tentativo di estrarre sprite ({x_on_sheet},{y_on_sheet} {width}x{height}) fuori dai limiti dello sheet ({source_spritesheet.get_size()}).")
            return None
        sprite_surface = pygame.Surface((width, height), pygame.SRCALPHA); sprite_surface.blit(source_spritesheet, (0, 0), (x_on_sheet, y_on_sheet, width, height))
        return sprite_surface

    def _load_animation_frames(self, sheet_to_use_surf: Optional[pygame.Surface], sheet_row_idx: int, num_frms: int, frm_w: int, frm_h: int) -> List[pygame.Surface]:
        frames = []
        if not sheet_to_use_surf or frm_w <= 0 or frm_h <= 0 or num_frms <= 0: return frames
        y_pos_sheet = sheet_row_idx * frm_h
        if y_pos_sheet + frm_h > sheet_to_use_surf.get_height():
            logger.warning(f"Riga animazione {sheet_row_idx} ({y_pos_sheet}) fuori dai limiti per sheet {sheet_to_use_surf.get_height()}H e frame_h {frm_h}")
            return frames
        for i in range(num_frms):
            x_pos_sheet = i * frm_w
            if x_pos_sheet + frm_w > sheet_to_use_surf.get_width():
                logger.warning(f"Frame animazione {i} (col {x_pos_sheet}) fuori dai limiti per sheet {sheet_to_use_surf.get_width()}W e frame_w {frm_w}")
                break 
            sprite = self._get_sprite_from_sheet(sheet_to_use_surf, x_pos_sheet, y_pos_sheet, frm_w, frm_h)
            if sprite: frames.append(sprite)
            else: logger.error(f"Fallito il caricamento del frame {i} per riga {sheet_row_idx} da sheet.")
        return frames

    def _load_standard_animations(self):
        if not self.spritesheet_image: return
        wc = getattr(config, 'SPRITE_WALK_ANIM_FRAMES', 4); ic = getattr(config, 'SPRITE_IDLE_ANIM_FRAMES', 1)
        anim_defs = {
            "walk_up": (getattr(config,'ANIM_ROW_WALK_UP',8), wc), "walk_left": (getattr(config,'ANIM_ROW_WALK_LEFT',9), wc),
            "walk_down": (getattr(config,'ANIM_ROW_WALK_DOWN',10), wc), "walk_right": (getattr(config,'ANIM_ROW_WALK_RIGHT',11), wc),
            "idle_up": (getattr(config,'ANIM_ROW_IDLE_UP',0), ic), "idle_left": (getattr(config,'ANIM_ROW_IDLE_LEFT',1), ic),
            "idle_down": (getattr(config,'ANIM_ROW_IDLE_DOWN',2), ic), "idle_right": (getattr(config,'ANIM_ROW_IDLE_RIGHT',3), ic),
        }
        for anim_name, (row, num_frames) in anim_defs.items():
            self.animations[anim_name] = self._load_animation_frames(self.spritesheet_image, row, num_frames, self.frame_width, self.frame_height)
            if not self.animations[anim_name] and DEBUG_VERBOSE: logger.warning(f"Animazione standard '{anim_name}' per {self.name} non caricata/vuota.")

    def _load_bundle_animations(self):
        if not self.spritesheet_image: return
        br = getattr(config, 'BUNDLE_ANIM_ROW', 0); nbf = getattr(config, 'BUNDLE_ANIM_FRAMES', 1)
        self.animations["idle_bundle"] = self._load_animation_frames(self.spritesheet_image, br, nbf, self.frame_width, self.frame_height)
        if not self.animations["idle_bundle"] and DEBUG_VERBOSE: logger.warning(f"Animazione bundle 'idle_bundle' per {self.name} non caricata/vuota.")

    def _load_sleep_animations(self):
        if not self.sleep_spritesheet_image: return
        nsf = getattr(config, 'NUM_SLEEP_ANIM_FRAMES', 1)
        anim_defs_sleep = {
            "sleep_on_back": getattr(config, 'ANIM_ROW_SLEEP_ON_BACK', 0),
            "sleep_side_left": getattr(config, 'ANIM_ROW_SLEEP_SIDE_LEFT', 1),
            "sleep_side_right": getattr(config, 'ANIM_ROW_SLEEP_SIDE_RIGHT', 2),
        }
        for anim_name, row in anim_defs_sleep.items():
            self.animations[anim_name] = self._load_animation_frames(self.sleep_spritesheet_image, row, nsf, self.sleep_frame_width, self.sleep_frame_height)
            if not self.animations.get(anim_name) and DEBUG_VERBOSE: logger.warning(f"Animazione sonno '{anim_name}' per {self.name} non caricata/vuota.")

    def _set_initial_animation_key(self):
        if self.is_bundle: initial_key = "idle_bundle"
        elif self.current_action == "resting_on_bed": initial_key = "sleep_on_back" 
        else: initial_key = "idle_" + self.current_facing_direction
        
        if initial_key in self.animations and self.animations[initial_key]:
            self.current_animation_key = initial_key
        elif self.animations:
            try: fallback_key = next(iter(self.animations)); self.current_animation_key = fallback_key
            except StopIteration: logger.error(f"Nessuna animazione caricata per {self.name}.")
            else: logger.warning(f"Animazione iniziale '{initial_key}' per {self.name} non trovata. Uso fallback: '{self.current_animation_key}'.")
        else: logger.error(f"Nessuna animazione caricata per {self.name}.")
        self.current_frame_idx_in_animation = 0; self.animation_timer = 0.0
    # --- Metodi di Utilità e Accesso ai Componenti ---
    def randomize_needs(self):
        if hasattr(self, 'needs') and self.needs: self.needs.randomize_all_needs()
        elif DEBUG_VERBOSE: logger.warning(f"Character ({self.name}): Tentativo di randomizzare bisogni, ma NeedsComponent non inizializzato.")

    def get_formatted_age_string(self) -> str:
        return self.status.get_formatted_age_string() if hasattr(self, 'status') and self.status else "Età N/D"

    # --- Metodo di Aggiornamento Principale ---
    def update(self, dt_real: float, world_width_pixels: int, world_height_pixels: int, 
               game_hours_advanced: float, current_time_speed_index: int, 
               tile_size: int, period_name: str):
        
        is_moving_this_frame: bool = False
        can_move_now = (self.current_action == "moving_to_target") and (current_time_speed_index > 0)

        if can_move_now:
            dx, dy = 0.0, 0.0
            if self.current_path and self.target_destination is None:
                if self.current_path_index < len(self.current_path):
                    target_node_obj = self.current_path[self.current_path_index]
                    if hasattr(target_node_obj, 'position') and isinstance(target_node_obj.position, tuple) and len(target_node_obj.position) == 2:
                        self.target_destination = game_utils.grid_to_world_center(target_node_obj.position[0], target_node_obj.position[1])
                    else: 
                        logger.error(f"Nodo A* malformato per {self.name}. Annullamento path."); self.current_path = None; self.current_action = "idle"; self.previous_action_was_movement_to_target = False
                else: self.current_path = None; self.target_destination = None 

            if self.target_destination:
                target_x, target_y = self.target_destination
                dist_x, dist_y = target_x - self.x, target_y - self.y
                distance_to_target = math.sqrt(dist_x**2 + dist_y**2)
                reach_threshold = getattr(config, 'NPC_TARGET_REACH_THRESHOLD', tile_size / 2.5)
                
                if distance_to_target > reach_threshold:
                    angle = math.atan2(dist_y, dist_x)
                    move_mult = getattr(config, 'NPC_MOVEMENT_SPEED_MULTIPLIERS', {}).get(current_time_speed_index, 1.0)
                    move_dist = (self.speed * move_mult) * dt_real
                    
                    if distance_to_target <= move_dist: dx, dy = dist_x, dist_y
                    else: dx, dy = math.cos(angle) * move_dist, math.sin(angle) * move_dist
                    
                    self.x += dx; self.y += dy; is_moving_this_frame = True
                else: 
                    self.x, self.y = target_x, target_y; self.target_destination = None
                    if self.current_path: self.current_path_index += 1
                    if self.current_path and self.current_path_index >= len(self.current_path): self.current_path = None
            
            if is_moving_this_frame:
                if abs(dx) > abs(dy) * 0.7: self.current_facing_direction = "right" if dx > 0 else "left"
                elif abs(dy) > abs(dx) * 0.7: self.current_facing_direction = "down" if dy > 0 else "up"
            
            # Clamp e aggiornamento rect (usa le dimensioni del frame corretto)
            active_w = self.sleep_frame_width if self.is_on_bed else self.frame_width
            active_h = self.sleep_frame_height if self.is_on_bed else self.frame_height
            half_w, half_h = active_w / 2, active_h / 2
            self.x = max(half_w, min(self.x, world_width_pixels - half_w))
            self.y = max(half_h, min(self.y, world_height_pixels - half_h))
            self.rect.size = (max(1,active_w), max(1,active_h)) # Evita size 0
            self.rect.center = (int(self.x), int(self.y))
        
        # Aggiornamento Componenti
        if hasattr(self, 'status') and self.status: self.status.update(game_hours_advanced)
        if hasattr(self, 'needs') and self.needs:
            is_resting = (self.current_action == "resting_on_bed" or self.current_action == "cuddling_in_bed" or self.current_action == "waiting_in_bed_for_partner")
            self.needs.update(game_hours_advanced, period_name, self.current_action, is_resting)
        if hasattr(self, 'mood') and self.mood: self.mood.update(dt_real, self)
        if hasattr(self, 'career') and self.career: self.career.update(game_hours_advanced, self.game_state_ref) # Passa game_state
        if hasattr(self, 'aspirations') and self.aspirations: self.aspirations.update(self)
        if hasattr(self, 'skills') and self.skills: self.skills.update(game_hours_advanced, self.current_action, self)
        if hasattr(self, 'relationships') and self.relationships: self.relationships.update(game_hours_advanced, self.game_state_ref)
        if hasattr(self, 'inventory') and self.inventory: self.inventory.update(game_hours_advanced, self.game_state_ref)
        
        # Logica specifica di recupero Energia (potrebbe essere duplicata se Energy.update la gestisce)
        if game_hours_advanced > 0 and self.current_action == "resting_on_bed" and hasattr(self, 'needs') and self.needs and hasattr(self.needs, 'energy'):
            self.needs.energy.recover(getattr(config, 'ENERGY_RECOVERY_RATE_PER_HOUR', 15.0), game_hours_advanced)
        
        # Aggiornamento Animazione
        new_anim_key = self.current_animation_key
        current_render_fw, current_render_fh = self.frame_width, self.frame_height

        if self.is_bundle: new_anim_key = "idle_bundle"
        elif self.is_on_bed: # Usa is_on_bed che è più affidabile di current_action per lo sprite a letto
            sleep_anim_map = {"left": "sleep_side_left", "right": "sleep_side_right", "up": "sleep_on_back", "down": "sleep_on_back"}
            potential_sleep_key = sleep_anim_map.get(self.current_facing_direction, "sleep_on_back")
            if potential_sleep_key in self.animations and self.animations[potential_sleep_key]: new_anim_key = potential_sleep_key
            elif "sleep_on_back" in self.animations and self.animations["sleep_on_back"]: new_anim_key = "sleep_on_back"
            else: new_anim_key = "idle_" + self.current_facing_direction # Fallback se mancano animazioni sonno
            current_render_fw, current_render_fh = self.sleep_frame_width, self.sleep_frame_height
        elif self.current_action == "moving_to_target" and is_moving_this_frame:
            new_anim_key = "walk_" + self.current_facing_direction
        else: new_anim_key = "idle_" + self.current_facing_direction
        
        if new_anim_key and new_anim_key != self.current_animation_key:
            if new_anim_key in self.animations and self.animations[new_anim_key]:
                self.current_animation_key = new_anim_key
                self.current_frame_idx_in_animation = 0; self.animation_timer = 0.0
            elif DEBUG_VERBOSE: logger.warning(f"CHARACTER ({self.name}): Tentativo animazione '{new_anim_key}' non trovata.")

        self.animation_timer += dt_real
        if self.current_animation_key in self.animations:
            anim_frames = self.animations[self.current_animation_key]
            if anim_frames and self.animation_timer >= self.animation_speed:
                self.animation_timer = 0.0
                self.current_frame_idx_in_animation = (self.current_frame_idx_in_animation + 1) % len(anim_frames)
        
        self.rect.size = (max(1,current_render_fw), max(1,current_render_fh))
        self.rect.center = (int(self.x), int(self.y))

    # --- Metodo di Disegno ---
    def draw(self, screen: pygame.Surface, camera: Optional['Camera'] = None, font: Optional[pygame.font.Font] = None, text_color: tuple = (255,255,255)):
        active_frame_w, active_frame_h = self.frame_width, self.frame_height
        current_anim_key_to_use = self.current_animation_key

        # Se è a letto, usa dimensioni e animazioni del sonno
        if self.is_on_bed: # Usa il flag is_on_bed
            if self.sleep_spritesheet_image:
                active_frame_w, active_frame_h = self.sleep_frame_width, self.sleep_frame_height
                # L'animazione del sonno (es. "sleep_on_back") dovrebbe essere già in current_animation_key dall'update
            else: logger.warning(f"Nessuno sleep_spritesheet_image per {self.name} mentre is_on_bed=True.")

        world_topleft_x = self.x - active_frame_w / 2
        world_topleft_y = self.y - active_frame_h / 2
        draw_topleft_x_on_screen, draw_topleft_y_on_screen = int(world_topleft_x), int(world_topleft_y)

        if camera:
            world_render_rect = pygame.Rect(world_topleft_x, world_topleft_y, active_frame_w, active_frame_h)
            screen_render_rect = camera.apply_to_rect(world_render_rect)
            draw_topleft_x_on_screen, draw_topleft_y_on_screen = int(screen_render_rect.left), int(screen_render_rect.top)

        image_to_render = None
        if current_anim_key_to_use in self.animations:
            anim_frames = self.animations[current_anim_key_to_use]
            if anim_frames and 0 <= self.current_frame_idx_in_animation < len(anim_frames):
                image_to_render = anim_frames[self.current_frame_idx_in_animation]
        
        if image_to_render:
            screen.blit(image_to_render, (draw_topleft_x_on_screen, draw_topleft_y_on_screen))
        elif self.fallback_radius > 0:
            center_x_on_screen = draw_topleft_x_on_screen + active_frame_w // 2
            center_y_on_screen = draw_topleft_y_on_screen + active_frame_h // 2
            pygame.draw.circle(screen, self.fallback_color, (center_x_on_screen, center_y_on_screen), self.fallback_radius)

        if font and self.font_ref:
            actual_font = font # Usa il font passato (debug) se disponibile, altrimenti self.font_ref (main_font)
            text_anchor_y = draw_topleft_y_on_screen - 5
            center_x = draw_topleft_x_on_screen + active_frame_w / 2
            status_txt, status_col = None, text_color
            
            if self.current_action == "resting_on_bed": status_txt = "Zzz..."
            # ... (altri testi di stato come prima) ...
            elif self.current_action == "moving_to_target" and self.current_action_before_movement:
                status_txt = f"Verso: {self.current_action_before_movement.replace('seeking_', '').replace('_', ' ').capitalize()}"

            if status_txt and not (self.is_on_bed and status_txt == "Zzz..."): # Evita doppio Zzz se è a letto e animazione è già sonno
                try:
                    s_srf = actual_font.render(status_txt, True, status_col)
                    s_rct = s_srf.get_rect(centerx=int(center_x), bottom=text_anchor_y)
                    screen.blit(s_srf, s_rct); text_anchor_y = s_rct.top - 2
                except Exception as e: logger.error(f"Errore render status txt per {self.name}: {e}")
            try:
                n_srf = actual_font.render(self.name, True, text_color)
                n_rct = n_srf.get_rect(centerx=int(center_x), bottom=text_anchor_y)
                screen.blit(n_srf, n_rct)
            except Exception as e: logger.error(f"Errore render nome txt per {self.name}: {e}")
            
            if self.is_pregnant: # Usa la proprietà
                try:
                    preg_term = getattr(config, 'PREGNANCY_TERM_GAME_DAYS', 24)
                    preg_txt = f"Incinta ({int(self.pregnancy_progress_days)}/{preg_term}gg)"
                    p_srf = actual_font.render(preg_txt, True, text_color)
                    p_rct = p_srf.get_rect(centerx=int(center_x), top=draw_topleft_y_on_screen + active_frame_h + 2)
                    screen.blit(p_srf, p_rct)
                except Exception as e: logger.error(f"Errore render preg txt per {self.name}: {e}")

    # --- Metodi Wrapper per Componenti (come prima, ma con controlli hasattr) ---
    def get_money(self) -> float: return self.finances.get_balance() if hasattr(self, 'finances') and self.finances else 0.0
    def add_money(self, amount: float, desc: str ="Income"):  _ = self.finances.add_money(amount, desc) if hasattr(self, 'finances') and self.finances else None
    def spend_money(self, amount: float, desc: str="Expense") -> bool: return self.finances.spend_money(amount, desc) if hasattr(self, 'finances') and self.finances else False
    def get_need_value(self, need_name: str) -> float: return self.needs.get_value(need_name) if hasattr(self, 'needs') and self.needs else 0.0
    def satisfy_need(self, need_name: str, amount: float): _ = self.needs.satisfy(need_name, amount) if hasattr(self, 'needs') and self.needs else None
    def become_pregnant(self) -> bool: return self.status.set_pregnant() if hasattr(self, 'status') and self.status else False
    @property
    def is_pregnant(self) -> bool: return self.status.is_pregnant if hasattr(self, 'status') and self.status else False
    @property
    def pregnancy_progress_days(self) -> float: return self.status.pregnancy_progress_days if hasattr(self, 'status') and self.status else 0.0
    
    # --- Metodi di Interazione con Inventario Domestico (se household_id è impostato) ---
    def get_household_inventory(self) -> Optional['InventoryComponent']:
        if self.household_id and self.game_state_ref and \
           hasattr(self.game_state_ref, 'household_inventories') and \
           self.household_id in self.game_state_ref.household_inventories:
            return self.game_state_ref.household_inventories[self.household_id]
        return None

    def add_item_to_household_inventory(self, item_to_add: Item, quantity: int = 1) -> bool:
        hh_inv = self.get_household_inventory()
        if hh_inv: return hh_inv.add_item_instance(item_to_add, quantity) # Usa add_item_instance
        logger.warning(f"{self.name} non ha un inventario domestico per aggiungere {item_to_add.name}.")
        return False

    def remove_item_from_household_inventory(self, item_id_to_remove: str, quantity: int = 1) -> int:
        hh_inv = self.get_household_inventory()
        if hh_inv: return hh_inv.remove_item_by_id(item_id_to_remove, quantity) # Usa remove_item_by_id
        logger.warning(f"{self.name} non ha un inventario domestico per rimuovere {item_id_to_remove}.")
        return 0

    def household_has_item(self, item_id: str, quantity: int = 1) -> bool:
        hh_inv = self.get_household_inventory()
        return hh_inv.has_item_id(item_id, quantity) if hh_inv else False # Usa has_item_id


    def to_dict(self) -> Dict[str, Any]:
        return {
            "uuid": self.uuid, "name": self.name, "gender": self.gender, "x": self.x, "y": self.y,
            "fallback_color": list(self.fallback_color), "fallback_radius": self.fallback_radius, "speed": self.speed,
            "spritesheet_filename_ref": self.spritesheet_filename_ref,
            "sleep_spritesheet_filename_ref": self.sleep_spritesheet_filename_ref,
            "is_bundle": self.is_bundle, "current_action": self.current_action,
            "current_action_before_movement": self.current_action_before_movement,
            "previous_action_was_movement_to_target": self.previous_action_was_movement_to_target,
            "target_destination": list(self.target_destination) if self.target_destination else None,
            "target_partner_uuid": self.target_partner.uuid if self.target_partner else None,
            "time_in_current_action": self.time_in_current_action,
            "is_on_bed": self.is_on_bed, "bed_object_id": self.bed_object_id, 
            "bed_slot_index": self.bed_slot_index, "target_bed_slot_id": self.target_bed_slot_id,
            "is_interacting": self.is_interacting,
            "current_facing_direction": self.current_facing_direction,
            "current_animation_key": self.current_animation_key,
            "pending_intimacy_requester_uuid": self.pending_intimacy_requester.uuid if self.pending_intimacy_requester else None,
            "household_id": self.household_id, # Salva household_id
            
            "needs_data": self.needs.to_dict() if hasattr(self, 'needs') and self.needs else None,
            "finance_data": self.finances.to_dict() if hasattr(self, 'finances') and self.finances else None,
            "mood_data": self.mood.to_dict() if hasattr(self, 'mood') and self.mood else None, # Rinominato
            "aspiration_data": self.aspirations.to_dict() if hasattr(self, 'aspirations') and self.aspirations else None,
            "career_data": self.career.to_dict() if hasattr(self, 'career') and self.career else None,
            "skill_data": self.skills.to_dict() if hasattr(self, 'skills') and self.skills else None,
            "relationship_data": self.relationships.to_dict() if hasattr(self, 'relationships') and self.relationships else None,
            "inventory_data": self.inventory.to_dict() if hasattr(self, 'inventory') and self.inventory else None,
            "status_data": self.status.to_dict() if hasattr(self, 'status') and self.status else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], 
                  sprite_sheet_manager_param: 'SpriteSheetManager', 
                  font_param: pygame.font.Font, 
                  game_state_param: 'GameState') -> 'Character':
        
        character = cls( # Chiamata a __init__ con i dati base
            name=data.get("name", "Loaded NPC"), gender=data.get("gender", "male"),
            x=float(data.get("x", config.SCREEN_WIDTH / 2)), y=float(data.get("y", config.SCREEN_HEIGHT / 2)),
            game_state=game_state_param, sprite_sheet_manager=sprite_sheet_manager_param, font=font_param,
            color=tuple(data.get("fallback_color", [255,0,0])), radius=int(data.get("fallback_radius", 15)),
            speed=float(data.get("speed", 200)),
            spritesheet_filename=data.get("spritesheet_filename_ref"),
            sleep_spritesheet_filename=data.get("sleep_spritesheet_filename_ref"),
            is_bundle=data.get("is_bundle", False), existing_uuid=data.get("uuid"),
            initial_action=data.get("current_action", "idle"),
            household_id=data.get("household_id") # Carica household_id
        )
        
        character.current_action_before_movement = data.get("current_action_before_movement")
        character.previous_action_was_movement_to_target = data.get("previous_action_was_movement_to_target", False)
        td = data.get("target_destination"); character.target_destination = tuple(td) if td else None
        character.time_in_current_action = float(data.get("time_in_current_action", 0.0))
        character.is_on_bed = data.get("is_on_bed", False)
        character.bed_object_id = data.get("bed_object_id")
        character.bed_slot_index = data.get("bed_slot_index", -1)
        character.target_bed_slot_id = data.get("target_bed_slot_id")
        character.is_interacting = data.get("is_interacting", False)
        character.current_facing_direction = data.get("current_facing_direction", "down")
        saved_anim_key = data.get("current_animation_key")
        if saved_anim_key and saved_anim_key in character.animations and character.animations[saved_anim_key]:
            character.current_animation_key = saved_anim_key
        
        # Carica componenti (con controlli hasattr per robustezza)
        component_map = {
            "needs": (NeedsComponent, "needs_data"), "finances": (FinanceComponent, "finance_data"),
            "mood": (MoodComponent, "mood_data"), "aspirations": (AspirationComponent, "aspiration_data"),
            "career": (CareerComponent, "career_data"), "skills": (SkillComponent, "skill_data"),
            "relationships": (RelationshipComponent, "relationship_data"), 
            "inventory": (InventoryComponent, "inventory_data"), "status": (StatusComponent, "status_data")
        }
        for attr_name, (comp_class, data_key) in component_map.items():
            if hasattr(character, attr_name) and getattr(character, attr_name) and data.get(data_key):
                # Alcuni componenti potrebbero aver bisogno di 'character_owner' o 'owner_uuid' in from_dict
                if attr_name in ["needs", "finances", "mood", "aspirations", "career", "skills", "inventory", "status"]:
                     setattr(character, attr_name, comp_class.from_dict(data[data_key], character))
                elif attr_name == "relationships":
                     setattr(character, attr_name, comp_class.from_dict(data[data_key], character, character.uuid))
            elif DEBUG_VERBOSE:
                logger.debug(f"Dati per il componente '{attr_name}' non trovati o componente non inizializzato per {character.name}.")

        character.target_partner_uuid_to_resolve = data.get("target_partner_uuid")
        character.pending_intimacy_requester_uuid_to_resolve = data.get("pending_intimacy_requester_uuid")
        
        character._set_initial_animation_key()
        if character.current_action == "resting_on_bed" or character.is_on_bed: # Controlla anche is_on_bed
            character.rect.size = (character.sleep_frame_width, character.sleep_frame_height)
        else:
            character.rect.size = (character.frame_width, character.frame_height)
        character.rect.center = (int(character.x), int(character.y))
        return character