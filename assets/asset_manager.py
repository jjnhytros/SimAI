# core/graphics/asset_manager.py
import pygame
import os
from typing import Dict, Optional, Tuple

from pygame.surface import Surface

class AssetManager:
    def __init__(self):
        self.spritesheets: Dict[str, Surface] = {}
        print("  [AssetManager] Creato.")

    def load_assets(self, tile_size: Tuple[int, int]):
        print("\n--- [AssetManager] Inizio Caricamento Assets ---")
        
        # Definiamo le cartelle da scansionare con percorsi relativi semplici
        asset_folders = [
            "assets/graphics/objects",
            "assets/graphics/tiles"
        ]

        # Controlliamo la cartella di lavoro corrente per essere sicuri
        print(f"  [AssetManager] Cartella di lavoro corrente: '{os.getcwd()}'")

        for folder in asset_folders:
            # Controlliamo se la cartella esiste partendo dalla cartella di lavoro
            if not os.path.isdir(folder):
                print(f"  [AssetManager] ATTENZIONE: La cartella '{folder}' non è stata trovata.")
                continue

            print(f"  [AssetManager] Scansione di: '{folder}'")
            for filename in os.listdir(folder):
                if filename.lower().endswith((".png", ".jpg")):
                    name = os.path.splitext(filename)[0]
                    full_path = os.path.join(folder, filename)
                    try:
                        image = pygame.image.load(full_path).convert_alpha()
                        self.spritesheets[name] = image
                        print(f"    -> Caricato con successo '{full_path}' con chiave '{name}'")
                    except pygame.error as e:
                        print(f"    -> ERRORE PYGAME: Impossibile caricare '{full_path}'. {e}")
        
        print("--- [AssetManager] Caricamento Completato ---\n")

    def get_spritesheet(self, name: str) -> Optional[Surface]:
        return self.spritesheets.get(name)

    # Nota: la gestione delle tile è ora inclusa nel caricamento generale degli spritesheet
    # quindi questo metodo non è strettamente necessario se non vuoi una logica separata.
    def get_tile(self, name: str) -> Optional[Surface]:
        return self.spritesheets.get(name) # Cerca tra tutti gli spritesheet caricati
