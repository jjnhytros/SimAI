# game/src/managers/character_manager.py
import logging
import random
from typing import List, Optional, TYPE_CHECKING

from game import config
from game.src.entities.character import Character

if TYPE_CHECKING:
    from game.src.modules.game_state_module import GameState
    from game.src.managers.asset_manager import SpriteSheetManager
    from pygame.font import Font # Per il tipo di font

logger = logging.getLogger(__name__)

class CharacterManager:
    def __init__(self, game_state: 'GameState', 
                 sprite_sheet_manager: 'SpriteSheetManager', 
                 main_font: 'Font'):
        self.game_state = game_state # Riferimento per accedere a all_npc_characters_list, ecc.
        self.sprite_sheet_manager = sprite_sheet_manager
        self.main_font = main_font

    def create_initial_npcs(self) -> List['Character']:
        """Crea gli NPC iniziali per una nuova partita."""
        npcs_to_create: List[Character] = []
        num_npcs_to_create = getattr(config, 'INITIAL_NUM_NPCS', 2)

        available_male_names = list(getattr(config, 'NPC_NAME_LIST_MALE', ["MaleNPC"]))
        available_female_names = list(getattr(config, 'NPC_NAME_LIST_FEMALE', ["FemaleNPC"]))
        random.shuffle(available_male_names)
        random.shuffle(available_female_names)

        # Considera di avere una lista di spawn point camminabili per evitare posizionamenti errati
        # spawn_points = getattr(config, 'NPC_INITIAL_SPAWN_POINTS_WORLD', 
        #                        [(config.SCREEN_WIDTH / 2, config.SCREEN_HEIGHT / 2)]) 
        world_px_w = getattr(config, 'WORLD_TILE_WIDTH', 100) * getattr(config, 'TILE_SIZE', 32)
        world_px_h = getattr(config, 'WORLD_TILE_HEIGHT', 80) * getattr(config, 'TILE_SIZE', 32)


        for i in range(num_npcs_to_create):
            gender = random.choice(["male", "female"])
            name, spritesheet_key, sleep_spritesheet_key = self._get_random_npc_details(gender, i, available_male_names, available_female_names)

            # Semplice posizionamento casuale, da migliorare con spawn point o verifica walkable
            initial_x = random.uniform(100, world_px_w - 100) 
            initial_y = random.uniform(100, world_px_h - 100 - getattr(config, 'PANEL_UI_HEIGHT', 150))

            try:
                npc = Character(
                    name=name, gender=gender, x=initial_x, y=initial_y,
                    game_state=self.game_state,
                    sprite_sheet_manager=self.sprite_sheet_manager,
                    font=self.main_font,
                    spritesheet_filename=spritesheet_key,
                    sleep_spritesheet_filename=sleep_spritesheet_key
                )
                npc.randomize_needs()
                npcs_to_create.append(npc)
                logger.info(f"CharacterManager: NPC '{name}' ({gender}) creato.")
            except Exception as e:
                logger.exception(f"CharacterManager: Errore creazione NPC {name}: {e}")
        return npcs_to_create

    def _get_random_npc_details(self, gender: str, index: int, male_names: list, female_names: list) -> tuple[str, str, str]:
        """Helper per ottenere nome e spritesheet casuali."""
        name, spritesheet_key, sleep_key = "", "", ""
        if gender == "male":
            name = male_names.pop(0) if male_names else f"MaleNPC{index}"
            spritesheet_key = random.choice(getattr(config, 'NPC_MALE_SPRITESHEET_KEYS', ["male_char"]))
            sleep_key = random.choice(getattr(config, 'NPC_MALE_SLEEP_SPRITESHEET_KEYS', ["male_sleep"]))
        else:
            name = female_names.pop(0) if female_names else f"FemaleNPC{index}"
            spritesheet_key = random.choice(getattr(config, 'NPC_FEMALE_SPRITESHEET_KEYS', ["female_char"]))
            sleep_key = random.choice(getattr(config, 'NPC_FEMALE_SLEEP_SPRITESHEET_KEYS', ["female_sleep"]))
        return name, spritesheet_key, sleep_key

    def spawn_newborn_npc(self, parent1: 'Character', parent2: Optional['Character'] = None) -> Optional['Character']:
        """Crea un nuovo NPC neonato."""
        logger.info(f"Tentativo di generare un neonato per {parent1.name}.")
        gender = random.choice(["male", "female"])
        # Il nome potrebbe essere generato o preso da una lista di nomi per bambini
        # Cognome potrebbe essere quello di parent1 o una combinazione
        child_name_prefix = "Baby"
        child_name_suffix = str(random.randint(100,999)) # Per unicità temporanea
        child_name = f"{child_name_prefix}{parent1.name.split(' ')[-1] if ' ' in parent1.name else parent1.name[:3]}{child_name_suffix}"


        # Posizione iniziale vicino al genitore (o in una culla se implementata)
        initial_x = parent1.x + random.uniform(-config.TILE_SIZE, config.TILE_SIZE)
        initial_y = parent1.y + random.uniform(-config.TILE_SIZE, config.TILE_SIZE)

        spritesheet_key = "baby_bundle" # Chiave per lo spritesheet del neonato
        sleep_spritesheet_key = "baby_bundle" # O uno specifico se lo hai

        try:
            newborn = Character(
                name=child_name, gender=gender, x=initial_x, y=initial_y,
                game_state=self.game_state,
                sprite_sheet_manager=self.sprite_sheet_manager,
                font=self.main_font,
                spritesheet_filename=spritesheet_key,
                sleep_spritesheet_filename=sleep_spritesheet_key,
                is_bundle=True # I neonati sono bundle
            )
            newborn.age_in_total_game_days = 0 # Appena nato
            newborn.randomize_needs() # I neonati avranno profili di bisogno diversi

            # Aggiungi alla lista globale degli NPC in game_state
            self.game_state.all_npc_characters_list.append(newborn)

            # TODO: Imposta relazioni familiari (parent1, parent2 -> newborn)
            # Questo richiederà un sistema di relazioni.

            logger.info(f"CharacterManager: Neonato '{newborn.name}' ({gender}) creato per {parent1.name}.")
            return newborn
        except Exception as e:
            logger.exception(f"CharacterManager: Errore creazione neonato: {e}")
            return None