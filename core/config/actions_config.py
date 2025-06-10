# core/config/actions_config.py
"""
Configurazioni di default per le azioni degli NPC.
"""

from core.enums import (
    FunActivityType, ObjectType, SkillType, SocialInteractionType,
    RelationshipType, NeedType,
)

TRAVEL_ACTION_DEFAULT_DURATION_TICKS = 60

# --- SleepAction ---
SLEEP_ACTION_DEFAULT_HOURS = 7.0
SLEEP_HOURS_CHILD_TEEN = 9.0
SLEEP_HOURS_ELDERLY = 8.0
SLEEP_ACTION_ENERGY_GAIN_PER_HOUR = 15.0
ENERGY_THRESHOLD_TO_CONSIDER_SLEEP = 40.0 # Soglia del bisogno ENERGY per considerare di dormire
NEED_VALUE_ON_WAKE_HUNGER = 70.0
NEED_VALUE_ON_WAKE_THIRST = 75.0
NEED_VALUE_ON_WAKE_BLADDER = 80.0

# --- EatAction ---
EAT_ACTION_DEFAULT_DURATION_HOURS = 0.5 
EAT_ACTION_DEFAULT_HUNGER_GAIN = 75.0
# EAT_ACTION_DEFAULT_DURATION_TICKS = ... (se preferisci definirlo direttamente in tick)

# --- DrinkAction ---
DRINK_DEFAULT_DURATION_HOURS = 0.2
DRINK_DEFAULT_THIRST_GAIN = 40.0
DRINK_DEFAULT_BLADDER_EFFECT = -10.0 # Negativo significa che riempie la vescica

DRINK_WATER_THIRST_GAIN = 60.0
DRINK_JUICE_THIRST_GAIN = 45.0
DRINK_JUICE_FUN_GAIN = 10.0

# --- UseBathroomAction ---
USEBATHROOM_TOILET_DURATION_TICKS = 18
USEBATHROOM_TOILET_DURATION_HOURS = 0.15
USEBATHROOM_TOILET_BLADDER_RELIEF = 100.0
USEBATHROOM_TOILET_HYGIENE_GAIN = 15.0
USEBATHROOM_SHOWER_DURATION_TICKS = 48 # circa 24 min
USEBATHROOM_SHOWER_HYGIENE_GAIN = 80.0

# --- EngageIntimacyAction ---
INTIMACY_ACTION_DEFAULT_DURATION_HOURS = 1.0
INTIMACY_ACTION_DEFAULT_INITIATOR_GAIN = 60.0
INTIMACY_ACTION_DEFAULT_TARGET_GAIN = 60.0
INTIMACY_ACTION_DEFAULT_REL_GAIN = 15
INTIMACY_REL_GAIN_BONUS_PARTNER = 5
INTIMACY_ACTION_INITIATOR_DESIRE_THRESHOLD = 50.0
INTIMACY_ACTION_MIN_REL_SCORE = 30

# --- HaveFunAction ---
# Default per attività non configurate specificamente
HAVEFUN_DEFAULT_FUN_GAIN = 25.0
HAVEFUN_DEFAULT_DURATION_HOURS = 1.0
HAVEFUN_DEFAULT_COGNITIVE_EFFORT = 0.4 # Default per lo sforzo cognitivo

# Mappa di configurazione per ogni attività di divertimento
HAVEFUN_ACTIVITY_CONFIGS = {
    # ================= CATEGORIA 1: CREATIVE (30 attività) =================
    FunActivityType.PAINT: {"fun_gain": 45.0, "duration_hours": 2.0, "required_object_types": (ObjectType.EASEL,), "skill_to_practice": SkillType.PAINTING, "skill_xp_gain": 60.0, "cognitive_effort": 0.8},
    FunActivityType.PLAY_GUITAR: {"fun_gain": 40.0, "duration_hours": 1.0, "required_object_types": (ObjectType.GUITAR,), "skill_to_practice": SkillType.GUITAR, "skill_xp_gain": 50.0, "cognitive_effort": 0.7},
    FunActivityType.DIGITAL_ART: {"fun_gain": 50.0, "duration_hours": 2.5, "required_object_types": (ObjectType.TABLET, ObjectType.DIGITAL_PEN), "skill_to_practice": SkillType.DIGITAL_ART, "skill_xp_gain": 70.0, "cognitive_effort": 0.9},
    FunActivityType.SCULPTING: {"fun_gain": 35.0, "duration_hours": 3.0, "required_object_types": (ObjectType.SCULPTING_TOOLS,), "skill_to_practice": SkillType.SCULPTING, "skill_xp_gain": 55.0, "cognitive_effort": 0.8},
    FunActivityType.PHOTO_EDITING: {"fun_gain": 30.0, "duration_hours": 1.5, "required_object_types": (ObjectType.COMPUTER,), "skill_to_practice": SkillType.PHOTOGRAPHY, "skill_xp_gain": 40.0, "cognitive_effort": 0.7},
    FunActivityType.CALLIGRAPHY: {"fun_gain": 25.0, "duration_hours": 1.0, "skill_to_practice": SkillType.CALLIGRAPHY, "skill_xp_gain": 35.0, "cognitive_effort": 0.6},
    FunActivityType.JEWELRY_MAKING: {"fun_gain": 40.0, "duration_hours": 2.0, "required_object_types": (ObjectType.JEWELRY_TOOLS,), "skill_to_practice": SkillType.JEWELRY_MAKING, "skill_xp_gain": 45.0, "cognitive_effort": 0.7},
    FunActivityType.UPHOLSTERY: {"fun_gain": 30.0, "duration_hours": 3.0, "skill_to_practice": SkillType.HANDINESS, "skill_xp_gain": 50.0, "cognitive_effort": 0.8},
    FunActivityType.GAME_DESIGN: {"fun_gain": 60.0, "duration_hours": 3.0, "required_object_types": (ObjectType.COMPUTER,), "skill_to_practice": SkillType.GAME_DESIGN, "skill_xp_gain": 75.0, "cognitive_effort": 0.95},
    FunActivityType.COMIC_DRAWING: {"fun_gain": 45.0, "duration_hours": 2.0, "skill_to_practice": SkillType.COMIC_ART, "skill_xp_gain": 60.0, "cognitive_effort": 0.8},
    FunActivityType.COSTUME_DESIGN: {"fun_gain": 35.0, "duration_hours": 2.5, "skill_to_practice": SkillType.COSTUME_DESIGN, "skill_xp_gain": 40.0, "cognitive_effort": 0.7},
    FunActivityType.GRAFFITI_ART: {"fun_gain": 55.0, "duration_hours": 2.0, "is_outdoors": True, "skill_to_practice": SkillType.STREET_ART, "skill_xp_gain": 65.0, "cognitive_effort": 0.75},
    FunActivityType.ANIMATION: {"fun_gain": 50.0, "duration_hours": 3.5, "required_object_types": (ObjectType.COMPUTER,), "skill_to_practice": SkillType.ANIMATION, "skill_xp_gain": 80.0, "cognitive_effort": 0.9},
    FunActivityType.LEATHERWORKING: {"fun_gain": 40.0, "duration_hours": 3.0, "skill_to_practice": SkillType.LEATHERWORKING, "skill_xp_gain": 45.0, "cognitive_effort": 0.7},
    FunActivityType.MODEL_BUILDING: {"fun_gain": 30.0, "duration_hours": 2.5, "skill_to_practice": SkillType.HANDINESS, "skill_xp_gain": 35.0, "cognitive_effort": 0.65},
    FunActivityType.STENCIL_ART: {"fun_gain": 25.0, "duration_hours": 1.5, "skill_to_practice": SkillType.STREET_ART, "skill_xp_gain": 30.0, "cognitive_effort": 0.5},
    FunActivityType.SONGWRITING: {"fun_gain": 45.0, "duration_hours": 2.0, "skill_to_practice": SkillType.SONGWRITING, "skill_xp_gain": 55.0, "cognitive_effort": 0.8},
    FunActivityType.POETRY: {"fun_gain": 35.0, "duration_hours": 1.0, "skill_to_practice": SkillType.POETRY, "skill_xp_gain": 40.0, "cognitive_effort": 0.7},
    FunActivityType.FURNITURE_RESTORATION: {"fun_gain": 30.0, "duration_hours": 4.0, "skill_to_practice": SkillType.HANDINESS, "skill_xp_gain": 50.0, "cognitive_effort": 0.75},
    FunActivityType.BEADWORK: {"fun_gain": 20.0, "duration_hours": 1.5, "skill_to_practice": SkillType.CRAFTING, "skill_xp_gain": 25.0, "cognitive_effort": 0.4},
    FunActivityType.ORIGAMI: {"fun_gain": 15.0, "duration_hours": 1.0, "skill_to_practice": SkillType.PAPER_CRAFT, "skill_xp_gain": 20.0, "cognitive_effort": 0.3},
    FunActivityType.BOTANICAL_ILLUSTRATION: {"fun_gain": 40.0, "duration_hours": 2.0, "skill_to_practice": SkillType.BOTANICAL_ART, "skill_xp_gain": 45.0, "cognitive_effort": 0.6},
    FunActivityType.CERAMIC_GLAZING: {"fun_gain": 30.0, "duration_hours": 1.5, "required_object_types": (ObjectType.KILN,), "skill_to_practice": SkillType.POTTERY, "skill_xp_gain": 35.0, "cognitive_effort": 0.5},
    FunActivityType.PUPPET_MAKING: {"fun_gain": 35.0, "duration_hours": 2.5, "skill_to_practice": SkillType.PUPPETRY, "skill_xp_gain": 40.0, "cognitive_effort": 0.6},
    FunActivityType.GLASS_ETCHING: {"fun_gain": 25.0, "duration_hours": 1.5, "skill_to_practice": SkillType.GLASS_ART, "skill_xp_gain": 30.0, "cognitive_effort": 0.55},
    FunActivityType.TEXTILE_DESIGN: {"fun_gain": 40.0, "duration_hours": 2.0, "skill_to_practice": SkillType.TEXTILE_ART, "skill_xp_gain": 45.0, "cognitive_effort": 0.65},
    FunActivityType.COSPLAY_CRAFTING: {"fun_gain": 55.0, "duration_hours": 4.0, "skill_to_practice": SkillType.COSTUME_DESIGN, "skill_xp_gain": 60.0, "cognitive_effort": 0.8},
    
    # ================= CATEGORIA 2: INTELLETTUALI E TRANQUILLE (30 attività) =================
    FunActivityType.READ_BOOK_FOR_FUN: {"fun_gain": 35.0, "duration_hours": 1.5, "required_object_types": (ObjectType.BOOKSHELF, ObjectType.BOOK), "cognitive_effort": 0.2},
    FunActivityType.STUDY_PHILOSOPHY: {"fun_gain": 30.0, "duration_hours": 2.0, "skill_to_practice": SkillType.PHILOSOPHY, "skill_xp_gain": 50.0, "cognitive_effort": 0.85},
    FunActivityType.LEARN_LANGUAGE: {"fun_gain": 40.0, "duration_hours": 1.5, "skill_to_practice": SkillType.LINGUISTICS, "skill_xp_gain": 45.0, "cognitive_effort": 0.75},
    FunActivityType.ASTRONOMY_OBSERVATION: {"fun_gain": 60.0, "duration_hours": 2.0, "is_outdoors": True, "required_object_types": (ObjectType.TELESCOPE,), "skill_to_practice": SkillType.ASTRONOMY, "skill_xp_gain": 65.0, "cognitive_effort": 0.7},
    FunActivityType.JOURNALING: {"fun_gain": 25.0, "duration_hours": 1.0, "skill_to_practice": SkillType.WRITING, "skill_xp_gain": 30.0, "cognitive_effort": 0.4},
    FunActivityType.MEDITATE: {"fun_gain": 20.0, "duration_hours": 0.5, "skill_to_practice": SkillType.WELLNESS, "skill_xp_gain": 25.0, "cognitive_effort": 0.2},
    FunActivityType.SUDOKU: {"fun_gain": 15.0, "duration_hours": 0.75, "skill_to_practice": SkillType.LOGIC, "skill_xp_gain": 20.0, "cognitive_effort": 0.6},
    FunActivityType.TAROT_READING: {"fun_gain": 30.0, "duration_hours": 1.0, "skill_to_practice": SkillType.INTUITION, "skill_xp_gain": 25.0, "cognitive_effort": 0.5},
    FunActivityType.BIRD_WATCHING: {"fun_gain": 35.0, "duration_hours": 2.0, "is_outdoors": True, "skill_to_practice": SkillType.ORNITHOLOGY, "skill_xp_gain": 30.0, "cognitive_effort": 0.3},
    FunActivityType.GENEALOGY_RESEARCH: {"fun_gain": 40.0, "duration_hours": 3.0, "required_object_types": (ObjectType.COMPUTER,), "skill_to_practice": SkillType.RESEARCH, "skill_xp_gain": 50.0, "cognitive_effort": 0.8},
    FunActivityType.PUZZLE_SOLVING: {"fun_gain": 25.0, "duration_hours": 1.5, "skill_to_practice": SkillType.PROBLEM_SOLVING, "skill_xp_gain": 35.0, "cognitive_effort": 0.65},
    FunActivityType.ASTROLOGY_STUDY: {"fun_gain": 30.0, "duration_hours": 1.0, "skill_to_practice": SkillType.ASTROLOGY, "skill_xp_gain": 25.0, "cognitive_effort": 0.55},
    FunActivityType.MINDFULNESS_PRACTICE: {"fun_gain": 20.0, "duration_hours": 0.5, "skill_to_practice": SkillType.WELLNESS, "skill_xp_gain": 30.0, "cognitive_effort": 0.15},
    FunActivityType.STARGAZING: {"fun_gain": 45.0, "duration_hours": 1.5, "is_outdoors": True, "cognitive_effort": 0.2},
    FunActivityType.CHEMISTRY_EXPERIMENTS: {"fun_gain": 55.0, "duration_hours": 2.5, "required_object_types": (ObjectType.CHEMISTRY_SET,), "skill_to_practice": SkillType.CHEMISTRY, "skill_xp_gain": 70.0, "cognitive_effort": 0.9},
    FunActivityType.BOTANY_STUDY: {"fun_gain": 35.0, "duration_hours": 2.0, "skill_to_practice": SkillType.BOTANY, "skill_xp_gain": 40.0, "cognitive_effort": 0.7},
    FunActivityType.HISTORY_DOCUMENTARY: {"fun_gain": 30.0, "duration_hours": 2.0, "required_object_types": (ObjectType.TV,), "skill_to_practice": SkillType.HISTORY, "skill_xp_gain": 35.0, "cognitive_effort": 0.4},
    FunActivityType.MAP_STUDY: {"fun_gain": 20.0, "duration_hours": 1.0, "skill_to_practice": SkillType.GEOGRAPHY, "skill_xp_gain": 25.0, "cognitive_effort": 0.5},
    FunActivityType.MEMORY_TRAINING: {"fun_gain": 15.0, "duration_hours": 0.5, "skill_to_practice": SkillType.MEMORY, "skill_xp_gain": 30.0, "cognitive_effort": 0.6},
    FunActivityType.PHILOSOPHICAL_DEBATE: {"fun_gain": 40.0, "duration_hours": 1.5, "skill_to_practice": SkillType.DEBATE, "skill_xp_gain": 45.0, "cognitive_effort": 0.85},
    FunActivityType.ECONOMICS_ANALYSIS: {"fun_gain": 25.0, "duration_hours": 2.0, "skill_to_practice": SkillType.ECONOMICS, "skill_xp_gain": 50.0, "cognitive_effort": 0.9},
    FunActivityType.PSYCHOLOGY_STUDY: {"fun_gain": 30.0, "duration_hours": 1.5, "skill_to_practice": SkillType.PSYCHOLOGY, "skill_xp_gain": 35.0, "cognitive_effort": 0.75},
    FunActivityType.ARCHITECTURE_STUDY: {"fun_gain": 35.0, "duration_hours": 2.0, "skill_to_practice": SkillType.ARCHITECTURE, "skill_xp_gain": 40.0, "cognitive_effort": 0.7},
    FunActivityType.CRYPTOGRAPHY: {"fun_gain": 50.0, "duration_hours": 2.5, "skill_to_practice": SkillType.CRYPTOGRAPHY, "skill_xp_gain": 65.0, "cognitive_effort": 0.95},
    FunActivityType.STRATEGY_GAME_SOLO: {"fun_gain": 40.0, "duration_hours": 1.5, "skill_to_practice": SkillType.STRATEGY, "skill_xp_gain": 45.0, "cognitive_effort": 0.8},
    FunActivityType.MYTHOLOGY_STUDY: {"fun_gain": 30.0, "duration_hours": 1.0, "skill_to_practice": SkillType.MYTHOLOGY, "skill_xp_gain": 25.0, "cognitive_effort": 0.5},
    FunActivityType.POETRY_ANALYSIS: {"fun_gain": 25.0, "duration_hours": 1.0, "skill_to_practice": SkillType.LITERATURE, "skill_xp_gain": 30.0, "cognitive_effort": 0.6},
    FunActivityType.AI_PROGRAMMING: {"fun_gain": 60.0, "duration_hours": 3.0, "required_object_types": (ObjectType.COMPUTER,), "skill_to_practice": SkillType.AI_PROGRAMMING, "skill_xp_gain": 80.0, "cognitive_effort": 0.95},
    
    # ================= CATEGORIA 3: FISICHE E ALL'APERTO (30 attività) =================
    FunActivityType.GO_FOR_A_JOG: {"fun_gain": 40.0, "duration_hours": 1.0, "is_outdoors": True, "skill_to_practice": SkillType.FITNESS, "skill_xp_gain": 40.0, "cognitive_effort": 0.6},
    FunActivityType.ROCK_CLIMBING: {"fun_gain": 65.0, "duration_hours": 3.0, "is_outdoors": True, "skill_to_practice": SkillType.ROCK_CLIMBING, "skill_xp_gain": 70.0, "cognitive_effort": 0.8},
    FunActivityType.MOUNTAIN_BIKING: {"fun_gain": 60.0, "duration_hours": 2.5, "is_outdoors": True, "skill_to_practice": SkillType.CYCLING, "skill_xp_gain": 55.0, "cognitive_effort": 0.75},
    FunActivityType.SURFING: {"fun_gain": 70.0, "duration_hours": 3.0, "is_outdoors": True, "skill_to_practice": SkillType.SURFING, "skill_xp_gain": 65.0, "cognitive_effort": 0.85},
    FunActivityType.KAYAKING: {"fun_gain": 55.0, "duration_hours": 2.5, "is_outdoors": True, "skill_to_practice": SkillType.KAYAKING, "skill_xp_gain": 50.0, "cognitive_effort": 0.7},
    FunActivityType.ARCHERY: {"fun_gain": 45.0, "duration_hours": 1.5, "is_outdoors": True, "skill_to_practice": SkillType.ARCHERY, "skill_xp_gain": 40.0, "cognitive_effort": 0.65},
    FunActivityType.PARKOUR: {"fun_gain": 65.0, "duration_hours": 2.0, "is_outdoors": True, "skill_to_practice": SkillType.PARKOUR, "skill_xp_gain": 60.0, "cognitive_effort": 0.8},
    FunActivityType.SKATEBOARDING: {"fun_gain": 50.0, "duration_hours": 2.0, "is_outdoors": True, "skill_to_practice": SkillType.SKATEBOARDING, "skill_xp_gain": 45.0, "cognitive_effort": 0.7},
    FunActivityType.BEACH_VOLLEYBALL: {"fun_gain": 55.0, "duration_hours": 1.5, "is_outdoors": True, "skill_to_practice": SkillType.VOLLEYBALL, "skill_xp_gain": 40.0, "cognitive_effort": 0.6},
    FunActivityType.DISC_GOLF: {"fun_gain": 40.0, "duration_hours": 2.0, "is_outdoors": True, "skill_to_practice": SkillType.FRISBEE, "skill_xp_gain": 35.0, "cognitive_effort": 0.5},
    FunActivityType.ORIENTEERING: {"fun_gain": 50.0, "duration_hours": 3.0, "is_outdoors": True, "skill_to_practice": SkillType.NAVIGATION, "skill_xp_gain": 55.0, "cognitive_effort": 0.75},
    FunActivityType.GEOCACHING: {"fun_gain": 45.0, "duration_hours": 2.5, "is_outdoors": True, "skill_to_practice": SkillType.GEOCACHING, "skill_xp_gain": 40.0, "cognitive_effort": 0.6},
    FunActivityType.TREE_CLIMBING: {"fun_gain": 35.0, "duration_hours": 1.5, "is_outdoors": True, "skill_to_practice": SkillType.CLIMBING, "skill_xp_gain": 30.0, "cognitive_effort": 0.55},
    FunActivityType.SNOWSHOEING: {"fun_gain": 50.0, "duration_hours": 2.0, "is_outdoors": True, "skill_to_practice": SkillType.WINTER_SPORTS, "skill_xp_gain": 45.0, "cognitive_effort": 0.65},
    FunActivityType.STARGAZING_HIKE: {"fun_gain": 60.0, "duration_hours": 4.0, "is_outdoors": True, "skill_to_practice": SkillType.ASTRONOMY, "skill_xp_gain": 50.0, "cognitive_effort": 0.4},
    FunActivityType.BIRDING: {"fun_gain": 30.0, "duration_hours": 2.0, "is_outdoors": True, "skill_to_practice": SkillType.ORNITHOLOGY, "skill_xp_gain": 35.0, "cognitive_effort": 0.3},
    FunActivityType.FOREST_BATHING: {"fun_gain": 25.0, "duration_hours": 1.5, "is_outdoors": True, "skill_to_practice": SkillType.WELLNESS, "skill_xp_gain": 20.0, "cognitive_effort": 0.1},
    FunActivityType.NATURE_PHOTOGRAPHY: {"fun_gain": 40.0, "duration_hours": 2.5, "is_outdoors": True, "skill_to_practice": SkillType.PHOTOGRAPHY, "skill_xp_gain": 45.0, "cognitive_effort": 0.5},
    FunActivityType.BOTANICAL_FORAGING: {"fun_gain": 35.0, "duration_hours": 2.0, "is_outdoors": True, "skill_to_practice": SkillType.FORAGING, "skill_xp_gain": 30.0, "cognitive_effort": 0.4},
    FunActivityType.ROCK_HUNTING: {"fun_gain": 30.0, "duration_hours": 3.0, "is_outdoors": True, "skill_to_practice": SkillType.GEOLOGY, "skill_xp_gain": 35.0, "cognitive_effort": 0.45},
    FunActivityType.WATERFALL_EXPLORATION: {"fun_gain": 55.0, "duration_hours": 4.0, "is_outdoors": True, "skill_to_practice": SkillType.EXPLORATION, "skill_xp_gain": 40.0, "cognitive_effort": 0.6},
    FunActivityType.CAVING: {"fun_gain": 70.0, "duration_hours": 5.0, "is_outdoors": True, "skill_to_practice": SkillType.SPELEOLOGY, "skill_xp_gain": 60.0, "cognitive_effort": 0.85},
    FunActivityType.STANDUP_PADDLEBOARD: {"fun_gain": 45.0, "duration_hours": 2.0, "is_outdoors": True, "skill_to_practice": SkillType.PADDLEBOARDING, "skill_xp_gain": 40.0, "cognitive_effort": 0.65},
    FunActivityType.ICE_SKATING: {"fun_gain": 40.0, "duration_hours": 1.5, "is_outdoors": True, "skill_to_practice": SkillType.ICE_SKATING, "skill_xp_gain": 35.0, "cognitive_effort": 0.6},
    FunActivityType.SNOWBALL_FIGHT: {"fun_gain": 50.0, "duration_hours": 1.0, "is_outdoors": True, "skill_to_practice": SkillType.WINTER_SPORTS, "skill_xp_gain": 25.0, "cognitive_effort": 0.4},
    FunActivityType.FRISBEE_GOLF: {"fun_gain": 35.0, "duration_hours": 1.5, "is_outdoors": True, "skill_to_practice": SkillType.FRISBEE, "skill_xp_gain": 30.0, "cognitive_effort": 0.5},
    FunActivityType.CANYONING: {"fun_gain": 75.0, "duration_hours": 6.0, "is_outdoors": True, "skill_to_practice": SkillType.CANYONING, "skill_xp_gain": 70.0, "cognitive_effort": 0.9},
    FunActivityType.URBAN_EXPLORATION: {"fun_gain": 45.0, "duration_hours": 3.0, "is_outdoors": True, "skill_to_practice": SkillType.URBAN_EXPLORATION, "skill_xp_gain": 40.0, "cognitive_effort": 0.7},
    FunActivityType.STONE_SKIPPING: {"fun_gain": 20.0, "duration_hours": 0.5, "is_outdoors": True, "skill_to_practice": SkillType.SKIPPING, "skill_xp_gain": 15.0, "cognitive_effort": 0.3},
    FunActivityType.SUNRISE_YOGA: {"fun_gain": 30.0, "duration_hours": 1.0, "is_outdoors": True, "skill_to_practice": SkillType.YOGA, "skill_xp_gain": 35.0, "cognitive_effort": 0.2},
    
    # ================= CATEGORIA 4: DOMESTICHE E MEDIA (30 attività) =================
    FunActivityType.WATCH_TV: {"fun_gain": 30.0, "duration_hours": 2.0, "required_object_types": (ObjectType.TV,), "cognitive_effort": 0.1},
    FunActivityType.COOKING_SHOW: {"fun_gain": 40.0, "duration_hours": 1.0, "required_object_types": (ObjectType.TV,), "skill_to_practice": SkillType.COOKING, "skill_xp_gain": 25.0, "cognitive_effort": 0.3},
    FunActivityType.PODCAST_LISTENING: {"fun_gain": 25.0, "duration_hours": 1.5, "cognitive_effort": 0.2},
    FunActivityType.VIRTUAL_TOUR: {"fun_gain": 35.0, "duration_hours": 1.0, "required_object_types": (ObjectType.VR_HEADSET,), "cognitive_effort": 0.4},
    FunActivityType.HOME_BAKING: {"fun_gain": 45.0, "duration_hours": 2.0, "skill_to_practice": SkillType.BAKING, "skill_xp_gain": 50.0, "cognitive_effort": 0.6},
    FunActivityType.AQUARIUM_WATCHING: {"fun_gain": 20.0, "duration_hours": 0.5, "required_object_types": (ObjectType.AQUARIUM,), "cognitive_effort": 0.1},
    FunActivityType.HOME_BREWING: {"fun_gain": 50.0, "duration_hours": 4.0, "skill_to_practice": SkillType.BREWING, "skill_xp_gain": 55.0, "cognitive_effort": 0.7},
    FunActivityType.PUZZLE_ASSEMBLY: {"fun_gain": 30.0, "duration_hours": 2.5, "skill_to_practice": SkillType.PATIENCE, "skill_xp_gain": 35.0, "cognitive_effort": 0.5},
    FunActivityType.MODEL_TRAIN_SETUP: {"fun_gain": 40.0, "duration_hours": 3.0, "skill_to_practice": SkillType.MODEL_BUILDING, "skill_xp_gain": 45.0, "cognitive_effort": 0.6},
    FunActivityType.HOME_DECORATING: {"fun_gain": 35.0, "duration_hours": 2.0, "skill_to_practice": SkillType.INTERIOR_DESIGN, "skill_xp_gain": 40.0, "cognitive_effort": 0.55},
    FunActivityType.CANDLE_MAKING: {"fun_gain": 30.0, "duration_hours": 1.5, "skill_to_practice": SkillType.CANDLE_MAKING, "skill_xp_gain": 25.0, "cognitive_effort": 0.4},
    FunActivityType.SOAP_CRAFTING: {"fun_gain": 25.0, "duration_hours": 2.0, "skill_to_practice": SkillType.SOAP_MAKING, "skill_xp_gain": 30.0, "cognitive_effort": 0.45},
    FunActivityType.INDOOR_GARDENING: {"fun_gain": 30.0, "duration_hours": 1.0, "skill_to_practice": SkillType.GARDENING, "skill_xp_gain": 20.0, "cognitive_effort": 0.3},
    FunActivityType.TERRARIUM_BUILDING: {"fun_gain": 35.0, "duration_hours": 2.0, "skill_to_practice": SkillType.TERRARIUM_DESIGN, "skill_xp_gain": 30.0, "cognitive_effort": 0.5},
    FunActivityType.HOME_WINE_TASTING: {"fun_gain": 40.0, "duration_hours": 1.0, "skill_to_practice": SkillType.WINE_APPRECIATION, "skill_xp_gain": 35.0, "cognitive_effort": 0.4},
    FunActivityType.VIRTUAL_CONCERT: {"fun_gain": 50.0, "duration_hours": 2.0, "required_object_types": (ObjectType.VR_HEADSET,), "cognitive_effort": 0.3},
    FunActivityType.FAMILY_HISTORY_ALBUM: {"fun_gain": 30.0, "duration_hours": 2.5, "skill_to_practice": SkillType.GENEALOGY, "skill_xp_gain": 25.0, "cognitive_effort": 0.4},
    FunActivityType.HOME_SPA: {"fun_gain": 35.0, "duration_hours": 1.5, "skill_to_practice": SkillType.WELLNESS, "skill_xp_gain": 20.0, "cognitive_effort": 0.1},
    FunActivityType.AUDIOBOOK_LISTENING: {"fun_gain": 25.0, "duration_hours": 2.0, "cognitive_effort": 0.2},
    FunActivityType.INDOOR_PICNIC: {"fun_gain": 40.0, "duration_hours": 1.5, "cognitive_effort": 0.3},
    FunActivityType.CHEESE_TASTING: {"fun_gain": 30.0, "duration_hours": 1.0, "skill_to_practice": SkillType.CULINARY_ARTS, "skill_xp_gain": 25.0, "cognitive_effort": 0.35},
    FunActivityType.HOME_IMPROVEMENT: {"fun_gain": 45.0, "duration_hours": 3.0, "skill_to_practice": SkillType.HANDINESS, "skill_xp_gain": 50.0, "cognitive_effort": 0.7},
    FunActivityType.INDOOR_CAMPING: {"fun_gain": 35.0, "duration_hours": 3.0, "cognitive_effort": 0.4},
    FunActivityType.TEA_CEREMONY: {"fun_gain": 30.0, "duration_hours": 1.0, "skill_to_practice": SkillType.TEA_APPRECIATION, "skill_xp_gain": 20.0, "cognitive_effort": 0.25},
    FunActivityType.HOME_KARAOKE: {"fun_gain": 55.0, "duration_hours": 1.5, "required_object_types": (ObjectType.KARAOKE_MACHINE,), "skill_to_practice": SkillType.SINGING, "skill_xp_gain": 30.0, "cognitive_effort": 0.5},
    FunActivityType.BATH_BOOK_READING: {"fun_gain": 20.0, "duration_hours": 1.0, "cognitive_effort": 0.15},
    FunActivityType.HOME_ESCAPE_ROOM: {"fun_gain": 60.0, "duration_hours": 2.0, "skill_to_practice": SkillType.PROBLEM_SOLVING, "skill_xp_gain": 45.0, "cognitive_effort": 0.85},
    FunActivityType.BALLOON_ART: {"fun_gain": 25.0, "duration_hours": 1.0, "skill_to_practice": SkillType.BALLOON_TWISTING, "skill_xp_gain": 20.0, "cognitive_effort": 0.35},
    FunActivityType.VIRTUAL_TRAVEL: {"fun_gain": 40.0, "duration_hours": 1.5, "required_object_types": (ObjectType.VR_HEADSET,), "cognitive_effort": 0.3},
    
    # ================= CATEGORIA 5: SOCIALI E IN CITTÀ (30 attività) =================
    FunActivityType.GO_TO_BAR: {"fun_gain": 35.0, "duration_hours": 2.0, "is_noisy": True, "cognitive_effort": 0.4},
    FunActivityType.COMEDY_CLUB: {"fun_gain": 60.0, "duration_hours": 2.0, "is_noisy": True, "skill_to_practice": SkillType.COMEDY_APPRECIATION, "skill_xp_gain": 25.0, "cognitive_effort": 0.3},
    FunActivityType.ART_GALLERY_TOUR: {"fun_gain": 40.0, "duration_hours": 2.5, "skill_to_practice": SkillType.ART_APPRECIATION, "skill_xp_gain": 35.0, "cognitive_effort": 0.4},
    FunActivityType.THEATER_PERFORMANCE: {"fun_gain": 50.0, "duration_hours": 3.0, "skill_to_practice": SkillType.THEATER_APPRECIATION, "skill_xp_gain": 30.0, "cognitive_effort": 0.3},
    FunActivityType.KARAOKE_NIGHT: {"fun_gain": 65.0, "duration_hours": 2.0, "is_noisy": True, "skill_to_practice": SkillType.SINGING, "skill_xp_gain": 40.0, "cognitive_effort": 0.5},
    FunActivityType.FOOD_TRUCK_FESTIVAL: {"fun_gain": 55.0, "duration_hours": 3.0, "is_noisy": True, "skill_to_practice": SkillType.CULINARY_EXPLORATION, "skill_xp_gain": 30.0, "cognitive_effort": 0.4},
    FunActivityType.STREET_PERFORMANCE: {"fun_gain": 45.0, "duration_hours": 1.5, "skill_to_practice": SkillType.PERFORMANCE_ART, "skill_xp_gain": 35.0, "cognitive_effort": 0.6},
    FunActivityType.PUB_QUIZ: {"fun_gain": 50.0, "duration_hours": 2.0, "is_noisy": True, "skill_to_practice": SkillType.TRIVIA, "skill_xp_gain": 45.0, "cognitive_effort": 0.7},
    FunActivityType.DANCE_CLUB: {"fun_gain": 70.0, "duration_hours": 3.0, "is_noisy": True, "skill_to_practice": SkillType.DANCING, "skill_xp_gain": 50.0, "cognitive_effort": 0.6},
    FunActivityType.BOARD_GAME_CAFE: {"fun_gain": 45.0, "duration_hours": 2.5, "skill_to_practice": SkillType.STRATEGY, "skill_xp_gain": 40.0, "cognitive_effort": 0.65},
    FunActivityType.FARMERS_MARKET: {"fun_gain": 30.0, "duration_hours": 1.5, "skill_to_practice": SkillType.CULINARY_EXPLORATION, "skill_xp_gain": 25.0, "cognitive_effort": 0.3},
    FunActivityType.POETRY_SLAM: {"fun_gain": 40.0, "duration_hours": 2.0, "skill_to_practice": SkillType.POETRY, "skill_xp_gain": 35.0, "cognitive_effort": 0.5},
    FunActivityType.CITY_PHOTO_WALK: {"fun_gain": 35.0, "duration_hours": 2.0, "skill_to_practice": SkillType.PHOTOGRAPHY, "skill_xp_gain": 30.0, "cognitive_effort": 0.4},
    FunActivityType.ARCADE_NIGHT: {"fun_gain": 55.0, "duration_hours": 2.0, "is_noisy": True, "skill_to_practice": SkillType.ARCADE_GAMING, "skill_xp_gain": 25.0, "cognitive_effort": 0.5},
    FunActivityType.LIVE_MUSIC_VENUE: {"fun_gain": 60.0, "duration_hours": 2.5, "is_noisy": True, "skill_to_practice": SkillType.MUSIC_APPRECIATION, "skill_xp_gain": 30.0, "cognitive_effort": 0.4},
    FunActivityType.SPEED_DATING: {"fun_gain": 45.0, "duration_hours": 1.5, "skill_to_practice": SkillType.SOCIALIZING, "skill_xp_gain": 40.0, "cognitive_effort": 0.7},
    FunActivityType.THEME_PARK: {"fun_gain": 80.0, "duration_hours": 6.0, "is_noisy": True, "cognitive_effort": 0.6},
    FunActivityType.STREET_FOOD_TOUR: {"fun_gain": 50.0, "duration_hours": 3.0, "skill_to_practice": SkillType.CULINARY_EXPLORATION, "skill_xp_gain": 35.0, "cognitive_effort": 0.4},
    FunActivityType.CITY_SCAVENGER_HUNT: {"fun_gain": 65.0, "duration_hours": 3.5, "skill_to_practice": SkillType.ORIENTEERING, "skill_xp_gain": 45.0, "cognitive_effort": 0.75},
    FunActivityType.FESTIVAL_ATTENDANCE: {"fun_gain": 70.0, "duration_hours": 4.0, "is_noisy": True, "cognitive_effort": 0.5},
    FunActivityType.IMPROV_WORKSHOP: {"fun_gain": 55.0, "duration_hours": 2.0, "skill_to_practice": SkillType.IMPROVISATION, "skill_xp_gain": 50.0, "cognitive_effort": 0.8},
    FunActivityType.MURDER_MYSTERY_DINNER: {"fun_gain": 60.0, "duration_hours": 3.0, "skill_to_practice": SkillType.DEDUCTION, "skill_xp_gain": 45.0, "cognitive_effort": 0.85},
    FunActivityType.ESCAPE_ROOM_CHALLENGE: {"fun_gain": 75.0, "duration_hours": 1.5, "skill_to_practice": SkillType.PROBLEM_SOLVING, "skill_xp_gain": 60.0, "cognitive_effort": 0.9},
    FunActivityType.CITY_BIKE_TOUR: {"fun_gain": 45.0, "duration_hours": 2.0, "skill_to_practice": SkillType.CYCLING, "skill_xp_gain": 40.0, "cognitive_effort": 0.6},
    FunActivityType.STREET_ART_TOUR: {"fun_gain": 40.0, "duration_hours": 2.5, "skill_to_practice": SkillType.ART_APPRECIATION, "skill_xp_gain": 35.0, "cognitive_effort": 0.45},
    FunActivityType.FOOD_COURT_SAMPLING: {"fun_gain": 50.0, "duration_hours": 1.5, "skill_to_practice": SkillType.CULINARY_EXPLORATION, "skill_xp_gain": 30.0, "cognitive_effort": 0.35},
    FunActivityType.NIGHT_MARKET: {"fun_gain": 45.0, "duration_hours": 2.0, "cognitive_effort": 0.4},
    FunActivityType.ROOFTOP_BAR: {"fun_gain": 40.0, "duration_hours": 2.0, "skill_to_practice": SkillType.SOCIALIZING, "skill_xp_gain": 25.0, "cognitive_effort": 0.3},
    FunActivityType.BOAT_PARTY: {"fun_gain": 75.0, "duration_hours": 4.0, "is_noisy": True, "cognitive_effort": 0.5},
    FunActivityType.VISIT_MUSEUM: {"duration_hours": 2.0,"fun_gain": 45.0,"skill_to_practice": SkillType.HISTORY,"skill_xp_gain": 20.0,"cognitive_effort": 0.3,},
    FunActivityType.DRINK_COFFEE: {"duration_hours": 0.5,"fun_gain": 15.0,"required_object_types": (ObjectType.COFFEE_MACHINE,),"cognitive_effort": 0.1},
    FunActivityType.LISTEN_TO_LIVE_JAZZ: {"duration_hours": 2.5,"fun_gain": 50.0,"is_noisy": True,"cognitive_effort": 0.1,},
    FunActivityType.PERFORM_JAZZ: {"duration_hours": 2.0,"fun_gain": 30.0,
        # Potrebbe anche dare un piccolo guadagno economico
        # "money_gain": 50.0,
        "required_object_types": (ObjectType.STAGE, ObjectType.MICROPHONE, ObjectType.PIANO),"skill_to_practice": SkillType.PIANO,"skill_xp_gain": 75.0,"is_noisy": True,"cognitive_effort": 0.8},
    FunActivityType.PERFORM_ON_STREET: {
        "duration_hours": 3.0,
        "fun_gain": 25.0, # È un po' un lavoro, quindi non è super divertente
        "money_gain": 75.0, # Guadagno base in Athel
        # Non richiede un oggetto, ma un tipo di location (gestito dall'IA)
        "is_outdoors": True,
        "is_noisy": True,
        "cognitive_effort": 0.6,
        "skill_to_practice": SkillType.GUITAR, # O un'altra skill musicale
        "skill_xp_gain": 60.0,
    },
    FunActivityType.JUMP_ON_BENCH: {
        "duration_hours": 0.1,
        "fun_gain": 20.0, # Molto divertente!
        "required_object_types": (ObjectType.BENCH,),
        "cognitive_effort": 0.1,
    },

    
    # ================= CATEGORIA 6: ROMANTICHE E SENSUALI (30 attività) =================
    FunActivityType.SUNSET_PICNIC: {"fun_gain": 65.0, "duration_hours": 2.0, "is_outdoors": True, "skill_to_practice": SkillType.ROMANCE_PLANNING, "skill_xp_gain": 40.0, "cognitive_effort": 0.4},
    FunActivityType.COUPLES_MASSAGE: {"fun_gain": 70.0, "duration_hours": 1.5, "skill_to_practice": SkillType.EROTIC_MASSAGE, "skill_xp_gain": 45.0, "cognitive_effort": 0.3},
    FunActivityType.CANDLELIGHT_DINNER: {"fun_gain": 60.0, "duration_hours": 2.5, "skill_to_practice": SkillType.ROMANCE_PLANNING, "skill_xp_gain": 35.0, "cognitive_effort": 0.5},
    FunActivityType.STARGAZING_DATE: {"fun_gain": 55.0, "duration_hours": 2.0, "is_outdoors": True, "skill_to_practice": SkillType.ROMANCE_PLANNING, "skill_xp_gain": 30.0, "cognitive_effort": 0.2},
    FunActivityType.SENSUAL_DANCE: {"fun_gain": 75.0, "duration_hours": 1.0, "skill_to_practice": SkillType.SENSUAL_DANCING, "skill_xp_gain": 50.0, "cognitive_effort": 0.6},
    FunActivityType.LOVE_LETTER_WRITING: {"fun_gain": 45.0, "duration_hours": 1.0, "skill_to_practice": SkillType.ROMANTIC_WRITING, "skill_xp_gain": 40.0, "cognitive_effort": 0.7},
    FunActivityType.HOT_SPRINGS_VISIT: {"fun_gain": 80.0, "duration_hours": 3.0, "skill_to_practice": SkillType.SENSUAL_RELAXATION, "skill_xp_gain": 35.0, "cognitive_effort": 0.1},
    FunActivityType.TANGO_LESSONS: {"fun_gain": 60.0, "duration_hours": 1.5, "skill_to_practice": SkillType.TANGO, "skill_xp_gain": 55.0, "cognitive_effort": 0.7},
    FunActivityType.CHOCOLATE_TASTING: {"fun_gain": 50.0, "duration_hours": 1.0, "skill_to_practice": SkillType.SENSUAL_TASTING, "skill_xp_gain": 30.0, "cognitive_effort": 0.4},
    FunActivityType.PRIVATE_WINE_CELLAR: {"fun_gain": 55.0, "duration_hours": 2.0, "skill_to_practice": SkillType.WINE_APPRECIATION, "skill_xp_gain": 40.0, "cognitive_effort": 0.45},
    FunActivityType.COUPLES_ART_CLASS: {"fun_gain": 65.0, "duration_hours": 2.5, "skill_to_practice": SkillType.ARTISTIC_EXPRESSION, "skill_xp_gain": 45.0, "cognitive_effort": 0.6},
    FunActivityType.MOONLIGHT_SWIM: {"fun_gain": 70.0, "duration_hours": 1.5, "is_outdoors": True, "skill_to_practice": SkillType.SENSUAL_SWIMMING, "skill_xp_gain": 35.0, "cognitive_effort": 0.5},
    FunActivityType.AROMATHERAPY_SESSION: {"fun_gain": 40.0, "duration_hours": 1.0, "skill_to_practice": SkillType.SENSUAL_RELAXATION, "skill_xp_gain": 30.0, "cognitive_effort": 0.2},
    FunActivityType.DOUBLE_MASSAGE: {"fun_gain": 75.0, "duration_hours": 1.5, "skill_to_practice": SkillType.MASSAGE_THERAPY, "skill_xp_gain": 40.0, "cognitive_effort": 0.3},
    FunActivityType.PRIVATE_DANCE: {"fun_gain": 85.0, "duration_hours": 0.5, "skill_to_practice": SkillType.SEDUCTIVE_DANCE, "skill_xp_gain": 55.0, "cognitive_effort": 0.65},
    FunActivityType.KISSING_CONTEST: {"fun_gain": 60.0, "duration_hours": 0.5, "skill_to_practice": SkillType.KISSING_TECHNIQUE, "skill_xp_gain": 45.0, "cognitive_effort": 0.4},
    FunActivityType.ROLEPLAYING_GAME: {"fun_gain": 65.0, "duration_hours": 2.0, "skill_to_practice": SkillType.IMPROVISATION, "skill_xp_gain": 50.0, "cognitive_effort": 0.8},
    FunActivityType.SILK_ROBES_EVENING: {"fun_gain": 55.0, "duration_hours": 2.0, "skill_to_practice": SkillType.SENSUAL_RELAXATION, "skill_xp_gain": 35.0, "cognitive_effort": 0.25},
    FunActivityType.EROTIC_STORYTELLING: {"fun_gain": 70.0, "duration_hours": 1.0, "skill_to_practice": SkillType.EROTIC_STORYTELLING, "skill_xp_gain": 60.0, "cognitive_effort": 0.75},
    FunActivityType.COUPLES_YOGA: {"fun_gain": 50.0, "duration_hours": 1.5, "skill_to_practice": SkillType.TANTRIC_YOGA, "skill_xp_gain": 40.0, "cognitive_effort": 0.6},
    FunActivityType.SENSUAL_COOKING: {"fun_gain": 60.0, "duration_hours": 2.0, "skill_to_practice": SkillType.SENSUAL_COOKING, "skill_xp_gain": 45.0, "cognitive_effort": 0.55},
    FunActivityType.AFTERGLOW_CUDDLING: {"fun_gain": 45.0, "duration_hours": 1.0, "skill_to_practice": SkillType.INTIMACY, "skill_xp_gain": 30.0, "cognitive_effort": 0.1},
    FunActivityType.PRIVATE_CONCERT: {"fun_gain": 65.0, "duration_hours": 1.5, "skill_to_practice": SkillType.MUSIC_PERFORMANCE, "skill_xp_gain": 50.0, "cognitive_effort": 0.5},
    FunActivityType.EROTIC_PHOTOGRAPHY: {"fun_gain": 75.0, "duration_hours": 2.0, "skill_to_practice": SkillType.EROTIC_PHOTOGRAPHY, "skill_xp_gain": 55.0, "cognitive_effort": 0.7},
    FunActivityType.SCENT_CREATION: {"fun_gain": 40.0, "duration_hours": 1.5, "skill_to_practice": SkillType.PERFUME_CRAFTING, "skill_xp_gain": 35.0, "cognitive_effort": 0.45},
    FunActivityType.FANTASY_ROLEPLAY: {"fun_gain": 80.0, "duration_hours": 2.5, "skill_to_practice": SkillType.IMAGINATION, "skill_xp_gain": 60.0, "cognitive_effort": 0.85},
    FunActivityType.MASSAGE_OIL_MAKING: {"fun_gain": 35.0, "duration_hours": 1.0, "skill_to_practice": SkillType.AROMATHERAPY, "skill_xp_gain": 25.0, "cognitive_effort": 0.4},
    FunActivityType.INTIMATE_GAME_NIGHT: {"fun_gain": 70.0, "duration_hours": 2.0, "skill_to_practice": SkillType.INTIMACY, "skill_xp_gain": 45.0, "cognitive_effort": 0.65},
    FunActivityType.SENSUAL_FEEDING: {"fun_gain": 55.0, "duration_hours": 1.0, "skill_to_practice": SkillType.SENSUAL_FEEDING, "skill_xp_gain": 40.0, "cognitive_effort": 0.5},
    FunActivityType.TANTRIC_BREATHWORK: {"fun_gain": 45.0, "duration_hours": 1.0, "skill_to_practice": SkillType.TANTRIC_PRACTICES, "skill_xp_gain": 35.0, "cognitive_effort": 0.6},
    FunActivityType.LINGERIE_SHOPPING: {"fun_gain": 50.0, "duration_hours": 1.5, "skill_to_practice": SkillType.LINGERIE_SELECTION, "skill_xp_gain": 30.0, "cognitive_effort": 0.3},
    FunActivityType.LOVE_POETRY_READING: {"fun_gain": 40.0, "duration_hours": 1.0, "skill_to_practice": SkillType.ROMANTIC_EXPRESSION, "skill_xp_gain": 25.0, "cognitive_effort": 0.4},
    }

# --- SocializeAction ---
# Default per interazioni non definite specificamente
SOCIALIZE_DEFAULT_DURATION_TICKS = 40
SOCIALIZE_DEFAULT_INITIATOR_GAIN = 10.0
SOCIALIZE_DEFAULT_TARGET_GAIN = 10.0
SOCIALIZE_DEFAULT_REL_CHANGE = 1

# Mappa di configurazione per ogni tipo di interazione sociale
SOCIALIZE_INTERACTION_CONFIGS = {
    # --- Interazioni Amichevoli / Neutre ---
    SocialInteractionType.CHAT_CASUAL: {
        "duration_ticks": 40, "initiator_gain": 15.0, "target_gain": 15.0, "rel_change": 2,
    },
    SocialInteractionType.DEEP_CONVERSATION: {
        "duration_ticks": 120, "initiator_gain": 30.0, "target_gain": 30.0, "rel_change": 8,
        "new_rel_type_on_success": RelationshipType.FRIEND_CLOSE, "min_rel_score_req": 30
    },
    SocialInteractionType.ASK_ABOUT_DAY: {
        "duration_ticks": 20, "initiator_gain": 12.0, "target_gain": 12.0, "rel_change": 2,
    },
    SocialInteractionType.SHARE_INTEREST: {
        "duration_ticks": 60, "initiator_gain": 20.0, "target_gain": 20.0, "rel_change": 4,
    },
    SocialInteractionType.TELL_JOKE: {
        "duration_ticks": 15, "initiator_gain": 10.0, "target_gain": 15.0, "rel_change": 2,
        "effects_on_target": {NeedType.FUN: 10.0}
    },
    SocialInteractionType.TELL_STORY: {
        "duration_ticks": 70, "initiator_gain": 18.0, "target_gain": 18.0, "rel_change": 3,
    },
    SocialInteractionType.COMPLIMENT: {
        "duration_ticks": 10, "initiator_gain": 5.0, "target_gain": 15.0, "rel_change": 4,
    },
    SocialInteractionType.OFFER_COMFORT: {
        "duration_ticks": 50, "initiator_gain": 10.0, "target_gain": 25.0, "rel_change": 6,
    },
    SocialInteractionType.GIVE_ADVICE: {
        "duration_ticks": 40, "initiator_gain": 8.0, "target_gain": 8.0, "rel_change": 2,
    },
    SocialInteractionType.SHARE_SECRET: {
        "duration_ticks": 50, "initiator_gain": 25.0, "target_gain": 25.0, "rel_change": 10,
        "new_rel_type_on_success": RelationshipType.FRIEND_CLOSE, "min_rel_score_req": 40
    },

    # --- Interazioni Romantiche ---
    SocialInteractionType.FLIRT: {
        "duration_ticks": 30, "initiator_gain": 15.0, "target_gain": 5.0, "rel_change": 3,
        "new_rel_type_on_success": RelationshipType.CRUSH, "min_rel_score_req": -10
    },
    SocialInteractionType.COMPLIMENT_APPEARANCE: {
        "duration_ticks": 10, "initiator_gain": 5.0, "target_gain": 20.0, "rel_change": 5,
        "min_rel_score_req": 0
    },
    SocialInteractionType.CONFESS_ATTRACTION: {
        "duration_ticks": 60, "initiator_gain": 10.0, "target_gain": 10.0, "rel_change": 15,
        "new_rel_type_on_success": RelationshipType.ROMANTIC_PARTNER, "min_rel_score_req": 35
    },
    SocialInteractionType.PROPOSE_DATE: {
        "duration_ticks": 25, "initiator_gain": 5.0, "target_gain": 5.0, "rel_change": 5,
        "min_rel_score_req": 20
    },
    SocialInteractionType.PROPOSE_INTIMACY: {
        "duration_ticks": 20, "initiator_gain": 5.0, "target_gain": 0.0, "rel_change": 1,
        "min_rel_score_req": 40
    },
    SocialInteractionType.PROPOSE_MARRIAGE: {
        "duration_ticks": 80, "initiator_gain": 10.0, "target_gain": 10.0, "rel_change": 20,
        "new_rel_type_on_success": RelationshipType.SPOUSE, "min_rel_score_req": 80
    },
    SocialInteractionType.KISS: {
        "duration_ticks": 10,"initiator_social_gain": 5.0,"target_social_gain": 5.0,"rel_change": 4,
        # Prerequisito FONDAMENTALE: Deve esserci un forte sentimento
        "min_rel_score_req": 50,"required_rel_types": (RelationshipType.ROMANTIC_PARTNER, RelationshipType.SPOUSE, RelationshipType.CRUSH)
},


    # --- Interazioni Negative / Conflittuali ---
    SocialInteractionType.ARGUE: {
        "duration_ticks": 50, "initiator_gain": -20.0, "target_gain": -20.0, "rel_change": -8,
        "new_rel_type_on_success": RelationshipType.ENEMY_DISLIKED
    },
    SocialInteractionType.INSULT: {
        "duration_ticks": 10, "initiator_gain": -5.0, "target_gain": -30.0, "rel_change": -15,
        "new_rel_type_on_success": RelationshipType.ENEMY_DISLIKED
    },
    SocialInteractionType.CRITICIZE: {
        "duration_ticks": 20, "initiator_gain": -10.0, "target_gain": -20.0, "rel_change": -5,
    },
    SocialInteractionType.YELL_AT: {
        "duration_ticks": 30, "initiator_gain": -25.0, "target_gain": -40.0, "rel_change": -20,
        "new_rel_type_on_success": RelationshipType.ENEMY_RIVAL
    },
    SocialInteractionType.GOSSIP_ABOUT_ANOTHER_NPC: {
        "duration_ticks": 50, "initiator_gain": 10.0, "target_gain": 10.0, "rel_change": 3,
    },
    
    # ... Puoi aggiungere le altre categorie (Familiari, Contestuali) qui ...
}
