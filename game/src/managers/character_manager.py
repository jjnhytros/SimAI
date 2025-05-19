# game/src/managers/character_manager.py
import logging
import random
from typing import Optional, Tuple, List, Dict, Any, TYPE_CHECKING


from game import config
from game.src.entities.character import Character

if TYPE_CHECKING:
    from game.src.modules.game_state_module import GameState
    from game.src.managers.asset_manager import SpriteSheetManager
    from pygame.font import Font # Per il tipo di font

logger = logging.getLogger(__name__)

class CharacterManager:
    def __init__(self, game_state, sprite_sheet_manager, font):
        self.game_state = game_state
        self.sprite_sheet_manager = sprite_sheet_manager
        self.font = font
        self.characters: List[Character] = [] 
        logger.info("CharacterManager initialized.")

    def add_character(self, character: Character):
        if character not in self.characters:
            self.characters.append(character)
            if self.game_state and hasattr(self.game_state, 'all_npc_characters_list') and \
               character not in self.game_state.all_npc_characters_list:
                self.game_state.all_npc_characters_list.append(character)
            logger.info(f"CharacterManager: Aggiunto {character.full_name if hasattr(character, 'full_name') else character.name} (ID: {character.id}). Totale gestiti: {len(self.characters)}")
        else:
            logger.warning(f"CharacterManager: Tentativo di aggiungere personaggio duplicato: {character.full_name if hasattr(character, 'full_name') else character.name}")

    def get_all_characters(self) -> List[Character]:
        return self.characters

    def get_character_by_id(self, char_id: str) -> Optional[Character]:
        for char in self.characters:
            if char.id == char_id:
                return char
        return None

    def spawn_random_npc(self, gender: str, position: Tuple[int, int], 
                          first_name_override: Optional[str] = None,
                          last_name_override: Optional[str] = None,
                          age_years_override: Optional[int] = None) -> Optional[Character]:
        
        if not self.game_state: 
            logger.error("CharacterManager: GameState non disponibile per spawn_random_npc.")
            return None
        if not self.sprite_sheet_manager: # Ora Character.__init__ lo prende
            logger.error("CharacterManager: SpriteSheetManager non disponibile per spawn_random_npc.")
            return None
        if not self.font: # Ora Character.__init__ lo prende
            logger.error("CharacterManager: Font non disponibile per spawn_random_npc.")
            return None

        first_name = first_name_override
        last_name = last_name_override

        if not first_name:
            name_list_male = getattr(config, 'NPC_NAME_LIST_MALE', ["DebugM_CM"])
            name_list_female = getattr(config, 'NPC_NAME_LIST_FEMALE', ["DebugF_CM"])
            if gender.lower() == "male":
                first_name = random.choice(name_list_male) if name_list_male else "RandomMale"
            else: # Female
                first_name = random.choice(name_list_female) if name_list_female else "RandomFemale"
        
        if not last_name:
            surnames = getattr(config, 'NPC_NAME_LIST_LAST', ["DebugLast_CM"]) 
            last_name = random.choice(surnames) if surnames else "Surname"

        # Il parametro 'name' di Character.__init__ sarà il nome completo
        character_full_name = f"{first_name} {last_name}"

        age_in_years = age_years_override if age_years_override is not None else \
                       random.randint(getattr(config, 'NPC_INITIAL_AGE_YEARS_MIN', 18), 
                                      getattr(config, 'NPC_INITIAL_AGE_YEARS_MAX', 35))
        
        # Determina la chiave dello spritesheet da passare a Character.__init__
        sheet_key_for_character = ""
        sleep_sheet_key_for_character = "" # Aggiunto per lo spritesheet del sonno

        if gender.lower() == "male":
            sprite_keys_male = getattr(config, 'NPC_MALE_SPRITESHEET_KEYS', ["male_char"])
            sheet_key_for_character = random.choice(sprite_keys_male) if sprite_keys_male else "male_char"
            
            sleep_sprite_keys_male = getattr(config, 'NPC_MALE_SLEEP_SPRITESHEET_KEYS', ["male_sleep"]) # Da config
            sleep_sheet_key_for_character = random.choice(sleep_sprite_keys_male) if sleep_sprite_keys_male else "male_sleep"

        else: # Female
            sprite_keys_female = getattr(config, 'NPC_FEMALE_SPRITESHEET_KEYS', ["female_char"])
            sheet_key_for_character = random.choice(sprite_keys_female) if sprite_keys_female else "female_char"

            sleep_sprite_keys_female = getattr(config, 'NPC_FEMALE_SLEEP_SPRITESHEET_KEYS', ["female_sleep"]) # Da config
            sleep_sheet_key_for_character = random.choice(sleep_sprite_keys_female) if sleep_sprite_keys_female else "female_sleep"
        
        try:
            new_npc = Character(
                name=character_full_name, # Passa il nome completo
                gender=gender,
                x=float(position[0]), # Assicurati che x e y siano float
                y=float(position[1]),
                game_state=self.game_state, # Passa l'oggetto GameState completo
                sprite_sheet_manager=self.sprite_sheet_manager, # Passa il manager
                font=self.font, # Passa il font
                spritesheet_filename=sheet_key_for_character, # Nome chiave dello sheet principale
                sleep_spritesheet_filename=sleep_sheet_key_for_character, # Nome chiave sheet sonno
            )
            
            # Imposta l'età nello StatusComponent *dopo* la creazione, se necessario
            if hasattr(new_npc, 'status') and new_npc.status and hasattr(new_npc.status, 'set_age_years'):
                new_npc.status.set_age_years(age_in_years)
            elif hasattr(new_npc, 'status') and new_npc.status: # Se non c'è set_age_years, ma un modo per impostare i giorni
                age_in_days = age_in_years * getattr(config, 'GAME_DAYS_PER_YEAR', 432)
                new_npc.status.current_age_days = age_in_days # Imposta direttamente se possibile/necessario
            
            # Inizializzazione dei componenti (l'__init__ di Character già lo fa,
            # ma se vuoi randomizzare i bisogni o altro post-creazione, fallo qui)
            # Esempio: new_npc.randomize_needs() se hai quel metodo.
            # if hasattr(new_npc, 'needs') and new_npc.needs:
            #     new_npc.needs.initialize_needs_randomly(debug_mode=getattr(config, 'DEBUG_MODE_ACTIVE', False))


            self.add_character(new_npc) 
            logger.info(f"CharacterManager: NPC Casuale '{new_npc.name}' (ID: {new_npc.id}) spawnato.") # Usa new_npc.name
            return new_npc
        except Exception as e:
            logger.error(f"CharacterManager: Errore durante spawn_random_npc per {character_full_name}: {e}", exc_info=True)
            return None

    def create_initial_npcs(self) -> List[Character]:
        logger.info(f"CharacterManager: Creazione di {getattr(config, 'INITIAL_NUM_NPCS', 2)} NPC iniziali.")
        created_npcs = []
        num_npcs = getattr(config, 'INITIAL_NUM_NPCS', 2)
        
        for i in range(num_npcs):
            gender = random.choice(["Male", "Female"])
            tile_size = getattr(config, 'TILE_SIZE', 32)
            world_w_tiles = getattr(config, 'WORLD_TILE_WIDTH', 32)
            world_h_tiles = getattr(config, 'WORLD_TILE_HEIGHT', 24)
            spawn_x = random.randint(2, world_w_tiles - 3) * tile_size
            spawn_y = random.randint(2, world_h_tiles - 3) * tile_size
            
            npc = self.spawn_random_npc(gender=gender, position=(spawn_x, spawn_y)) # Ora chiama la versione aggiornata
            if npc:
                # add_character è già chiamato da spawn_random_npc
                pass 
            else:
                logger.warning(f"CharacterManager: Fallita creazione dell'NPC iniziale numero {i+1}.")
        
        # Restituisce la lista aggiornata da self.characters, che è la fonte di verità
        logger.info(f"CharacterManager: Creati {len(self.characters)} NPC iniziali totali (inclusi eventuali precedenti).")
        return self.get_all_characters()

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

    def create_character_from_data(self, char_data: Dict[str, Any], is_player: bool = False) -> Optional[Character]:
        if not self.game_state or not self.sprite_sheet_manager or not self.font:
            logger.error("CharacterManager: Dipendenze mancanti (GameState, SpriteSheetManager, Font) per create_character_from_data.")
            return None
        
        logger.info(f"Attempting to create character from UI data: {char_data}")
        first_name = char_data.get("first_name", "Player")
        last_name = char_data.get("last_name", "Sim")
        full_name = f"{first_name} {last_name}"
        gender = char_data.get("gender", "Male")
        age_in_years = char_data.get("age_years", getattr(config, 'NPC_INITIAL_AGE_YEARS_MIN', 18) )

        sheet_key = ""
        sleep_sheet_key = ""
        if gender.lower() == "male":
            sheet_key = random.choice(getattr(config, 'NPC_MALE_SPRITESHEET_KEYS', ["male_char"]))
            sleep_sheet_key = random.choice(getattr(config, 'NPC_MALE_SLEEP_SPRITESHEET_KEYS', ["male_sleep"]))
        else: 
            sheet_key = random.choice(getattr(config, 'NPC_FEMALE_SPRITESHEET_KEYS', ["female_char"]))
            sleep_sheet_key = random.choice(getattr(config, 'NPC_FEMALE_SLEEP_SPRITESHEET_KEYS', ["female_sleep"]))

        position = char_data.get("position", 
                                 (getattr(config,'SCREEN_WIDTH', 1024) // 4, 
                                  getattr(config,'SCREEN_HEIGHT', 768) // 2))

        try:
            new_char = Character(
                name=full_name,
                gender=gender,
                x=float(position[0]),
                y=float(position[1]),
                game_state=self.game_state,
                sprite_sheet_manager=self.sprite_sheet_manager,
                font=self.font,
                spritesheet_filename=sheet_key,
                sleep_spritesheet_filename=sleep_sheet_key,
            )
            
            if hasattr(new_char, 'status') and new_char.status and hasattr(new_char.status, 'set_age_years'):
                new_char.status.set_age_years(age_in_years)
            elif hasattr(new_char, 'status') and new_char.status:
                 age_in_days = age_in_years * getattr(config, 'GAME_DAYS_PER_YEAR', 432)
                 new_char.status.current_age_days = age_in_days
            
            if hasattr(new_char, 'needs') and new_char.needs:
                logger.info(f"Impostazione bisogni iniziali per il giocatore {new_char.name}")
                for need_name, need_obj in new_char.needs.all_needs.items():
                    # Imposta a un valore alto, es. 80% del massimo, o valori specifici per bisogno
                    need_obj.set_value(need_obj.max_value * 0.80) 


            self.add_character(new_char)
            logger.info(f"Character '{new_char.name}' created from UI data and added.")
            return new_char
        except Exception as e:
            logger.error(f"Error creating character from data for {full_name}: {e}", exc_info=True)
            return None
