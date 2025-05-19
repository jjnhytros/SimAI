# /home/nhytros/work/clair/simai/game/src/managers/asset_manager.py
import pygame
import os
from typing import Dict, Tuple, Optional, List # Aggiunti i type hints
import logging

# Importa config per accedere ai percorsi degli asset e alle dimensioni di default.
# Dato che asset_manager.py è in game/src/managers/, e config.py è in game/,
# l'import corretto quando si esegue con 'python -m game.main' da 'simai/' è:
from game import config # Cercherà simai/game/config.py

logger = logging.getLogger(__name__)

class SpriteSheetManager:
    def __init__(self):
        self.sprite_sheets: dict[str, pygame.Surface] = {}
        self.frame_dimensions: dict[str, tuple[int, int]] = {}
        self.animation_configs: dict[str, dict] = {}

        if getattr(config, 'DEBUG_AI_ACTIVE', False):
            print("ASSET_MANAGER: SpriteSheetManager initialized.")

    def load_sheet(self, key: str, image_path_relative_to_config_image_path: str, frame_width: int, frame_height: int,
                   animation_config: Optional[dict] = None):
        """
        Carica uno sprite sheet da un file immagine.
        image_path_relative_to_config_image_path: Il percorso RELATIVO a config.IMAGE_PATH.
        """
        # COSTRUISCI IL PERCORSO COMPLETO USANDO config.IMAGE_PATH COME BASE
        full_image_path = os.path.join(config.IMAGE_PATH, image_path_relative_to_config_image_path)

        if not os.path.exists(full_image_path):
            print(f"ERRORE ASSET_MANAGER: Immagine non trovata per lo sprite sheet '{key}' al percorso: {full_image_path}")
            return False

        try:
            sheet_surface = pygame.image.load(full_image_path).convert_alpha()
            self.sprite_sheets[key] = sheet_surface
            self.frame_dimensions[key] = (frame_width, frame_height)
            if animation_config:
                self.animation_configs[key] = animation_config
            if getattr(config, 'DEBUG_AI_ACTIVE', False):
                print(f"ASSET_MANAGER: Sprite sheet '{key}' caricato da '{full_image_path}' con frame ({frame_width}x{frame_height}).")
            return True
        except pygame.error as e:
            print(f"ERRORE ASSET_MANAGER: Impossibile caricare lo sprite sheet '{key}' da '{full_image_path}': {e}")
            return False

    def get_sprite(self, sheet_key: str, frame_x_index: int, frame_y_index: int) -> Optional[pygame.Surface]:
        """
        Estrae un singolo sprite (frame) da uno sprite sheet caricato, date le coordinate dell'indice del frame.
        frame_x_index: Indice X del frame (partendo da 0).
        frame_y_index: Indice Y del frame (partendo da 0).
        """
        if sheet_key not in self.sprite_sheets:
            if getattr(config, 'DEBUG_AI_ACTIVE', False):
                print(f"ERRORE ASSET_MANAGER: Sprite sheet '{sheet_key}' non trovato per get_sprite.")
            return None

        sheet = self.sprite_sheets[sheet_key]
        frame_width, frame_height = self.frame_dimensions[sheet_key]

        x = frame_x_index * frame_width
        y = frame_y_index * frame_height

        # Verifica che le coordinate del frame siano all'interno dello sheet
        if x + frame_width > sheet.get_width() or y + frame_height > sheet.get_height():
            if getattr(config, 'DEBUG_AI_ACTIVE', False):
                print(f"ERRORE ASSET_MANAGER: Coordinate frame ({frame_x_index}, {frame_y_index}) fuori dai limiti per lo sheet '{sheet_key}'.")
            return None

        sprite_surface = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
        sprite_surface.blit(sheet, (0, 0), (x, y, frame_width, frame_height))
        return sprite_surface

    def get_sprite_by_pixel_rect(self, sheet_key: str, rect_on_sheet: pygame.Rect) -> Optional[pygame.Surface]:
        """
        Estrae un singolo sprite (Surface) da uno sprite sheet caricato,
        data una specifica pygame.Rect che definisce l'area in pixel sullo sheet.
        """
        if sheet_key not in self.sprite_sheets:
            logger.error(f"Sprite sheet '{sheet_key}' non trovato per get_sprite_by_pixel_rect.")
            return None

        sheet = self.sprite_sheets[sheet_key]

        if rect_on_sheet.left < 0 or rect_on_sheet.top < 0 or \
           rect_on_sheet.right > sheet.get_width() or \
           rect_on_sheet.bottom > sheet.get_height() or \
           rect_on_sheet.width <= 0 or rect_on_sheet.height <= 0:
            logger.error(f"Rettangolo {rect_on_sheet} fuori dai limiti o non valido per sheet '{sheet_key}' (size: {sheet.get_size()}).")
            return None

        try:
            sprite_surface = pygame.Surface(rect_on_sheet.size, pygame.SRCALPHA)
            sprite_surface.blit(sheet, (0, 0), rect_on_sheet)
            if getattr(config, 'DEBUG_AI_ACTIVE', False):
                 logger.debug(f"Estratto sprite da '{sheet_key}' usando rect {rect_on_sheet}.")
            return sprite_surface
        except Exception as e:
            logger.error(f"Errore durante blit per get_sprite_by_pixel_rect da '{sheet_key}': {e}")
            return None


    def get_animation_frames(self, sheet_key: str, animation_name: str) -> List[pygame.Surface]:
        """
        Restituisce una lista di Surface per un'animazione specifica,
        basandosi su animation_configs.
        """
        frames = []
        if sheet_key not in self.animation_configs or animation_name not in self.animation_configs[sheet_key]:
            if getattr(config, 'DEBUG_AI_ACTIVE', False):
                print(f"ERRORE ASSET_MANAGER: Configurazione animazione '{animation_name}' non trovata per sheet '{sheet_key}'.")
            # Fallback: prova a restituire il primo frame se esiste (0,0)
            sprite = self.get_sprite(sheet_key, 0, 0)
            return [sprite] if sprite else []


        anim_info = self.animation_configs[sheet_key][animation_name]
        row = anim_info.get("row")
        num_frames = anim_info.get("frames", 1) # Default a 1 frame se non specificato
        start_col = anim_info.get("start_col", 0) # Colonna iniziale, default 0

        if row is None: # Se 'row' non è specificato, potrebbe essere un'animazione orizzontale da una singola riga (row 0)
            # Questo è un caso comune per animazioni semplici o sprite singoli
            # O potresti avere una convenzione diversa, es. una lista di coordinate [(x,y), (x,y)...]
            if getattr(config, 'DEBUG_AI_ACTIVE', False) and num_frames > 1: # Solo se ci si aspetta più frame
                print(f"WARN ASSET_MANAGER: 'row' non specificata per animazione '{animation_name}' sheet '{sheet_key}'. Assumo riga 0.")
            row = 0 # Fallback a riga 0

        for i in range(num_frames):
            frame_x_idx = start_col + i
            sprite = self.get_sprite(sheet_key, frame_x_idx, row)
            if sprite:
                frames.append(sprite)
            else:
                if getattr(config, 'DEBUG_AI_ACTIVE', False):
                    print(f"ERRORE ASSET_MANAGER: Frame mancante ({frame_x_idx}, {row}) per animazione '{animation_name}' sheet '{sheet_key}'.")
        return frames

    def get_sheet(self, sheet_key: str) -> Optional[pygame.Surface]:
        """Restituisce l'intera Surface dello sprite sheet."""
        return self.sprite_sheets.get(sheet_key)

    def get_frame_dimensions(self, sheet_key: str) -> Optional[Tuple[int, int]]:
        """Restituisce le dimensioni (width, height) dei frame per uno sheet specifico."""
        return self.frame_dimensions.get(sheet_key)

# Potresti aggiungere altre classi manager qui (SoundManager, FontManager) o tenerle separate.
