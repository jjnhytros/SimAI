# core/graphics/asset_manager.py
import pygame
import os
from typing import Dict, Optional, Tuple
from pygame.surface import Surface
from core import settings

class AssetManager:
    """
    Gestisce il caricamento e l'accesso a tutte le risorse grafiche
    del gioco, come gli spritesheet.
    """
    def __init__(self):
        self.spritesheets: Dict[str, Surface] = {}
        if settings.DEBUG_MODE:
            print("  [AssetManager] Creato.")

    def load_assets(self, tile_size: Tuple[int, int]):
        """
        Scansiona le cartelle degli asset e carica tutte le immagini .png come spritesheet.
        """
        print("\n--- [AssetManager] Inizio Caricamento Assets ---")
        
        # Definiamo le cartelle da scansionare
        asset_folders = [
            "assets/graphics/objects",
            "assets/graphics/tiles",
            "assets/graphics/doors", # Aggiungiamo anche questa se la usi
        ]

        print(f"  [AssetManager] Cartella di lavoro corrente: '{os.getcwd()}'")

        for folder in asset_folders:
            # Controlla se la cartella esiste prima di provare a leggerla
            if not os.path.isdir(folder):
                # Questo non è un errore, ma un avviso se la cartella non esiste
                # print(f"  [AssetManager] Avviso: La cartella '{folder}' non è stata trovata.")
                continue

            print(f"  [AssetManager] Scansione di: '{folder}'")
            for filename in os.listdir(folder):
                if filename.lower().endswith(".png"):
                    # Il nome della risorsa è il nome del file senza estensione
                    name = os.path.splitext(filename)[0]
                    full_path = os.path.join(folder, filename)
                    
                    try:
                        image = pygame.image.load(full_path).convert_alpha()
                        self.spritesheets[name] = image
                        if settings.DEBUG_MODE:
                            print(f"    -> Caricato con successo '{full_path}' con chiave '{name}'")
                    except pygame.error as e:
                        print(f"    -> ERRORE PYGAME: Impossibile caricare '{full_path}'. {e}")
        
        print("--- [AssetManager] Caricamento Completato ---\n")

    def get_spritesheet(self, name: str) -> Optional[Surface]:
        """
        Restituisce una superficie spritesheet basandosi sul suo nome (il nome del file).
        """
        return self.spritesheets.get(name)