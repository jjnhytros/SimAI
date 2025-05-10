# simai/game/game_utils.py
import pygame
import os
import math
from game import config

def interpolate_color(color1, color2, factor):
    factor = max(0.0, min(1.0, factor))
    r = int(color1[0] * (1 - factor) + color2[0] * factor)
    g = int(color1[1] * (1 - factor) + color2[1] * factor)
    b = int(color1[2] * (1 - factor) + color2[2] * factor)
    return (max(0,min(255,r)), max(0,min(255,g)), max(0,min(255,b)))

def get_sky_color_and_period_info(precise_hour_in_day):
    hour_for_color = precise_hour_in_day % config.GAME_HOURS_IN_DAY
    prev_kf_hour, prev_kf_color = config.SKY_KEYFRAMES[0] 
    sky_color = prev_kf_color 
    for i in range(len(config.SKY_KEYFRAMES) - 1):
        h1, c1 = config.SKY_KEYFRAMES[i]
        h2, c2 = config.SKY_KEYFRAMES[i+1]
        if h1 <= hour_for_color < h2:
            segment_duration = h2 - h1
            if segment_duration <= 0:
                sky_color = c1
            else:
                time_into_segment = hour_for_color - h1
                factor = time_into_segment / segment_duration
                sky_color = interpolate_color(c1, c2, factor)
            break 
    else: 
        sky_color = config.SKY_KEYFRAMES[-1][1]

    hour_int = int(precise_hour_in_day) % config.GAME_HOURS_IN_DAY
    period_name = ""
    if 0 <= hour_int < 7: 
        period_name = "Notte"
    elif 7 <= hour_int < 14: 
        period_name = "Mattino"
    elif 14 <= hour_int < 21: 
        period_name = "Mezzogiorno"
    else: 
        period_name = "Sera" 
    
    brightness = (sky_color[0]*0.299 + sky_color[1]*0.587 + sky_color[2]*0.114)
    ui_text_color = config.TEXT_COLOR_DARK if brightness > 150 else config.TEXT_COLOR_LIGHT
    return sky_color, period_name, ui_text_color

def world_to_grid(world_x, world_y):
    grid_x = int(world_x // config.TILE_SIZE)
    grid_y = int(world_y // config.TILE_SIZE)
    grid_x = max(0, min(config.GRID_WIDTH - 1, grid_x))
    grid_y = max(0, min(config.GRID_HEIGHT - 1, grid_y))
    return grid_x, grid_y

def grid_to_world_center(grid_x, grid_y): # Rinomina in modo generico
    world_x = grid_x * config.TILE_SIZE + config.TILE_SIZE / 2
    world_y = grid_y * config.TILE_SIZE + config.TILE_SIZE / 2
    return world_x, world_y

def load_image(filename, size=None, base_path="."):
    """Carica un'immagine PNG e opzionalmente la ridimensiona."""
    try:
        full_path = os.path.join(base_path, filename)
        
        # DEBUG PRINT: Percorso completo tentato
        print(f"LOAD_IMAGE DEBUG: Tentativo di caricare: '{full_path}'")

        if not os.path.exists(full_path):
            print(f"LOAD_IMAGE ATTENZIONE: Immagine NON TROVATA in '{full_path}'")
            return None
        
        image = pygame.image.load(full_path)
        
        # Applica convert o convert_alpha per ottimizzazione
        if image.get_alpha():
            image = image.convert_alpha()
        else:
            image = image.convert()

        if size: # Ridimensiona SOLO se una 'size' è specificata
            image = pygame.transform.smoothscale(image, size)
        
        print(f"LOAD_IMAGE INFO: Immagine '{full_path}' caricata con successo.")
        return image
    except pygame.error as e: # Errore specifico di Pygame (es. file non trovato da Pygame, formato non supportato)
        print(f"LOAD_IMAGE ERRORE Pygame caricando '{filename}' da '{base_path}': {e}")
        return None
    except Exception as e: # Altri errori generici
        print(f"LOAD_IMAGE ERRORE generico caricando '{filename}': {e}")
        return None
