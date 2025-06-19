# core/config/actions_config.py
"""
Configurazioni di default per le azioni degli NPC.
"""

from core.enums import (
    FunActivityType, ObjectType, SkillType, SocialInteractionType,
    RelationshipType, NeedType, Interest
)
from core.enums.trait_types import TraitType

TRAVEL_ACTION_DEFAULT_DURATION_TICKS = 60

# Mappa un'attività di divertimento all'interesse corrispondente
ACTIVITY_TO_INTEREST_MAP: dict[FunActivityType, Interest] = {
    # Creative & Craft Activities
    FunActivityType.PAINT: Interest.VISUAL_ARTS,
    FunActivityType.PLAY_GUITAR: Interest.MUSIC_PLAYING,
    FunActivityType.PLAY_PIANO: Interest.MUSIC_PLAYING,
    FunActivityType.PLAY_VIOLIN: Interest.MUSIC_PLAYING,
    FunActivityType.SING: Interest.MUSIC_PLAYING,
    FunActivityType.WRITE_BOOK_FOR_FUN: Interest.WRITING,
    FunActivityType.DJ_MIXING: Interest.MUSIC_PLAYING,
    FunActivityType.PHOTOGRAPHY: Interest.VISUAL_ARTS,
    FunActivityType.KNITTING: Interest.KNITTING,
    FunActivityType.POTTERY: Interest.POTTERY,
    FunActivityType.WOODWORKING: Interest.WOODWORKING,
    FunActivityType.DIGITAL_ART: Interest.VISUAL_ARTS,
    FunActivityType.SCULPTING: Interest.VISUAL_ARTS,
    FunActivityType.PHOTO_EDITING: Interest.VISUAL_ARTS,
    FunActivityType.CALLIGRAPHY: Interest.VISUAL_ARTS,
    FunActivityType.JEWELRY_MAKING: Interest.JEWELRY_MAKING,
    FunActivityType.UPHOLSTERY: Interest.CRAFTING,
    FunActivityType.GAME_DESIGN: Interest.VISUAL_ARTS,
    FunActivityType.COMIC_DRAWING: Interest.VISUAL_ARTS,
    FunActivityType.COSTUME_DESIGN: Interest.FASHION,
    FunActivityType.GRAFFITI_ART: Interest.GRAFFITI,
    FunActivityType.ANIMATION: Interest.ANIMATION,
    FunActivityType.LEATHERWORKING: Interest.LEATHERWORKING,
    FunActivityType.MODEL_BUILDING: Interest.MODEL_BUILDING,
    FunActivityType.STENCIL_ART: Interest.VISUAL_ARTS,
    FunActivityType.SONGWRITING: Interest.WRITING,
    FunActivityType.POETRY: Interest.POETRY,
    FunActivityType.FURNITURE_RESTORATION: Interest.CRAFTING,
    FunActivityType.BEADWORK: Interest.CRAFTING,
    FunActivityType.ORIGAMI: Interest.ORIGAMI,
    FunActivityType.BOTANICAL_ILLUSTRATION: Interest.VISUAL_ARTS,
    FunActivityType.CERAMIC_GLAZING: Interest.POTTERY,
    FunActivityType.PUPPET_MAKING: Interest.CRAFTING,
    FunActivityType.GLASS_ETCHING: Interest.VISUAL_ARTS,
    FunActivityType.TEXTILE_DESIGN: Interest.TEXTILE_ART,
    FunActivityType.COSPLAY_CRAFTING: Interest.CRAFTING,
    
    # Intellectual/Quiet Activities
    FunActivityType.READ_BOOK_FOR_FUN: Interest.READING,
    FunActivityType.PRACTICE_PUBLIC_SPEAKING: Interest.THEATER_ACTING,
    FunActivityType.BROWSE_SOCIAL_MEDIA: Interest.SOCIAL_MEDIA,
    FunActivityType.VISIT_MUSEUM: Interest.MUSEUM_VISITING,
    FunActivityType.DRINK_COFFEE: Interest.SOCIALIZING,
    FunActivityType.PLAY_CHESS: Interest.BOARD_GAMES,
    FunActivityType.DO_CROSSWORD_PUZZLE: Interest.BOARD_GAMES,
    FunActivityType.RESEARCH_INTEREST_ONLINE: Interest.SCIENCE,
    FunActivityType.DAYDREAM: Interest.MINDFULNESS,
    FunActivityType.WATCH_CLOUDS: Interest.MINDFULNESS,
    FunActivityType.PEOPLE_WATCH: Interest.GOSSIP,
    FunActivityType.MEDITATE: Interest.MEDITATION,
    FunActivityType.STUDY_PHILOSOPHY: Interest.PHILOSOPHY_DEBATE,
    FunActivityType.LEARN_LANGUAGE: Interest.LINGUISTICS,
    FunActivityType.ASTRONOMY_OBSERVATION: Interest.ASTRONOMY,
    FunActivityType.JOURNALING: Interest.JOURNALING,
    FunActivityType.SUDOKU: Interest.BOARD_GAMES,
    FunActivityType.TAROT_READING: Interest.TAROT,
    FunActivityType.BIRD_WATCHING: Interest.BIRD_WATCHING,
    FunActivityType.GENEALOGY_RESEARCH: Interest.GENEALOGY,
    FunActivityType.PUZZLE_SOLVING: Interest.BOARD_GAMES,
    FunActivityType.ASTROLOGY_STUDY: Interest.ASTROLOGY,
    FunActivityType.MINDFULNESS_PRACTICE: Interest.MINDFULNESS,
    FunActivityType.STARGAZING: Interest.STARGAZING,
    FunActivityType.CHEMISTRY_EXPERIMENTS: Interest.CHEMISTRY,
    FunActivityType.BOTANY_STUDY: Interest.BIOLOGY,
    FunActivityType.HISTORY_DOCUMENTARY: Interest.HISTORY,
    FunActivityType.MAP_STUDY: Interest.HISTORY,
    FunActivityType.MEMORY_TRAINING: Interest.COMPUTER_SCIENCE,
    FunActivityType.PHILOSOPHICAL_DEBATE: Interest.PHILOSOPHY_DEBATE,
    FunActivityType.ECONOMICS_ANALYSIS: Interest.ECONOMICS,
    FunActivityType.PSYCHOLOGY_STUDY: Interest.PSYCHOLOGY,
    FunActivityType.ARCHITECTURE_STUDY: Interest.ARCHITECTURE,
    FunActivityType.CRYPTOGRAPHY: Interest.CRYPTOGRAPHY,
    FunActivityType.STRATEGY_GAME_SOLO: Interest.BOARD_GAMES,
    FunActivityType.MYTHOLOGY_STUDY: Interest.LITERATURE,
    FunActivityType.POETRY_ANALYSIS: Interest.POETRY,
    FunActivityType.AI_PROGRAMMING: Interest.ARTIFICIAL_INTELLIGENCE,
    
    # Outdoor/Physical Activities
    FunActivityType.DANCE: Interest.DANCE,
    FunActivityType.GO_FOR_A_JOG: Interest.RUNNING,
    FunActivityType.JOG_IN_PLACE: Interest.RUNNING,
    FunActivityType.GO_HIKING: Interest.HIKING,
    FunActivityType.SWIMMING: Interest.SWIMMING,
    FunActivityType.GARDENING: Interest.GARDENING,
    FunActivityType.FISHING: Interest.FISHING,
    FunActivityType.PLAY_SPORTS_CASUAL: Interest.SPORTS_PRACTICING,
    FunActivityType.EXPLORE_NEIGHBORHOOD: Interest.URBAN_EXPLORATION,
    FunActivityType.ROCK_CLIMBING: Interest.ROCK_CLIMBING,
    FunActivityType.MOUNTAIN_BIKING: Interest.MOUNTAIN_BIKING,
    FunActivityType.SURFING: Interest.SURFING,
    FunActivityType.KAYAKING: Interest.KAYAKING,
    FunActivityType.ARCHERY: Interest.SPORTS_PRACTICING,
    FunActivityType.PARKOUR: Interest.PARKOUR,
    FunActivityType.SKATEBOARDING: Interest.SKATING,
    FunActivityType.BEACH_VOLLEYBALL: Interest.SPORTS_PRACTICING,
    FunActivityType.DISC_GOLF: Interest.SPORTS_PRACTICING,
    FunActivityType.ORIENTEERING: Interest.SPORTS_PRACTICING,
    FunActivityType.GEOCACHING: Interest.GEOCACHING,
    FunActivityType.TREE_CLIMBING: Interest.CLIMBING,
    FunActivityType.SNOWSHOEING: Interest.SPORTS_PRACTICING,
    FunActivityType.STARGAZING_HIKE: Interest.STARGAZING,
    FunActivityType.BIRDING: Interest.BIRD_WATCHING,
    FunActivityType.FOREST_BATHING: Interest.NATURE_AND_OUTDOORS,
    FunActivityType.NATURE_PHOTOGRAPHY: Interest.VISUAL_ARTS,
    FunActivityType.BOTANICAL_FORAGING: Interest.FORAGING,
    FunActivityType.ROCK_HUNTING: Interest.COLLECTING,
    FunActivityType.WATERFALL_EXPLORATION: Interest.HIKING,
    FunActivityType.CAVING: Interest.CAVING,
    FunActivityType.STANDUP_PADDLEBOARD: Interest.SPORTS_PRACTICING,
    FunActivityType.ICE_SKATING: Interest.SKATING,
    FunActivityType.SNOWBALL_FIGHT: Interest.SPORTS_PRACTICING,
    FunActivityType.FRISBEE_GOLF: Interest.SPORTS_PRACTICING,
    FunActivityType.CANYONING: Interest.SPORTS_PRACTICING,
    FunActivityType.URBAN_EXPLORATION: Interest.URBAN_EXPLORATION,
    FunActivityType.STONE_SKIPPING: Interest.NATURE_AND_OUTDOORS,
    FunActivityType.SUNRISE_YOGA: Interest.YOGA,
    
    # Domestic/Media Activities
    FunActivityType.WATCH_TV: Interest.FILM_TV_THEATER,
    FunActivityType.COOKING_SHOW: Interest.COOKING_AND_FOOD,
    FunActivityType.PODCAST_LISTENING: Interest.FILM_TV_THEATER,
    FunActivityType.VIRTUAL_TOUR: Interest.TRAVEL,
    FunActivityType.HOME_BAKING: Interest.BAKING,
    FunActivityType.AQUARIUM_WATCHING: Interest.ANIMALS,
    FunActivityType.HOME_BREWING: Interest.BREWING,
    FunActivityType.PUZZLE_ASSEMBLY: Interest.CRAFTING,
    FunActivityType.MODEL_TRAIN_SETUP: Interest.MODEL_BUILDING,
    FunActivityType.HOME_DECORATING: Interest.INTERIOR_DESIGN,
    FunActivityType.CANDLE_MAKING: Interest.CANDLE_MAKING,
    FunActivityType.SOAP_CRAFTING: Interest.SOAP_MAKING,
    FunActivityType.INDOOR_GARDENING: Interest.GARDENING,
    FunActivityType.TERRARIUM_BUILDING: Interest.GARDENING,
    FunActivityType.HOME_WINE_TASTING: Interest.WINE_TASTING,
    FunActivityType.VIRTUAL_CONCERT: Interest.MUSIC_LISTENING,
    FunActivityType.FAMILY_HISTORY_ALBUM: Interest.GENEALOGY,
    FunActivityType.HOME_SPA: Interest.FITNESS_AND_WELLNESS,
    FunActivityType.AUDIOBOOK_LISTENING: Interest.AUDIOBOOK_LISTENING,
    FunActivityType.INDOOR_PICNIC: Interest.SOCIALIZING,
    FunActivityType.CHEESE_TASTING: Interest.COOKING_AND_FOOD,
    FunActivityType.HOME_IMPROVEMENT: Interest.HOME_IMPROVEMENT,
    FunActivityType.INDOOR_CAMPING: Interest.CAMPING,
    FunActivityType.TEA_CEREMONY: Interest.TEA_CEREMONY,
    FunActivityType.HOME_KARAOKE: Interest.MUSIC_PLAYING,
    FunActivityType.BATH_BOOK_READING: Interest.READING,
    FunActivityType.HOME_ESCAPE_ROOM: Interest.GAMING,
    FunActivityType.BALLOON_ART: Interest.VISUAL_ARTS,
    FunActivityType.VIRTUAL_TRAVEL: Interest.TRAVEL,
    
    # Social/City Activities
    FunActivityType.GO_TO_BAR: Interest.SOCIALIZING,
    FunActivityType.COMEDY_CLUB: Interest.COMEDY,
    FunActivityType.ART_GALLERY_TOUR: Interest.VISUAL_ARTS,
    FunActivityType.THEATER_PERFORMANCE: Interest.FILM_TV_THEATER,
    FunActivityType.KARAOKE_NIGHT: Interest.MUSIC_PLAYING,
    FunActivityType.FOOD_TRUCK_FESTIVAL: Interest.COOKING_AND_FOOD,
    FunActivityType.STREET_PERFORMANCE: Interest.PERFORMANCE_ART,
    FunActivityType.PUB_QUIZ: Interest.SOCIALIZING,
    FunActivityType.DANCE_CLUB: Interest.DANCE,
    FunActivityType.BOARD_GAME_CAFE: Interest.BOARD_GAMES,
    FunActivityType.FARMERS_MARKET: Interest.COOKING_AND_FOOD,
    FunActivityType.POETRY_SLAM: Interest.POETRY,
    FunActivityType.CITY_PHOTO_WALK: Interest.VISUAL_ARTS,
    FunActivityType.ARCADE_NIGHT: Interest.GAMING,
    FunActivityType.LIVE_MUSIC_VENUE: Interest.MUSIC_LISTENING,
    FunActivityType.SPEED_DATING: Interest.DATING,
    FunActivityType.THEME_PARK: Interest.SOCIALIZING,
    FunActivityType.STREET_FOOD_TOUR: Interest.COOKING_AND_FOOD,
    FunActivityType.CITY_SCAVENGER_HUNT: Interest.URBAN_EXPLORATION,
    FunActivityType.FESTIVAL_ATTENDANCE: Interest.SOCIALIZING,
    FunActivityType.IMPROV_WORKSHOP: Interest.THEATER_ACTING,
    FunActivityType.MURDER_MYSTERY_DINNER: Interest.SOCIALIZING,
    FunActivityType.ESCAPE_ROOM_CHALLENGE: Interest.GAMING,
    FunActivityType.CITY_BIKE_TOUR: Interest.CYCLING,
    FunActivityType.STREET_ART_TOUR: Interest.VISUAL_ARTS,
    FunActivityType.FOOD_COURT_SAMPLING: Interest.COOKING_AND_FOOD,
    FunActivityType.NIGHT_MARKET: Interest.COOKING_AND_FOOD,
    FunActivityType.ROOFTOP_BAR: Interest.SOCIALIZING,
    FunActivityType.BOAT_PARTY: Interest.SOCIALIZING,
    FunActivityType.LISTEN_TO_LIVE_JAZZ: Interest.MUSIC_LISTENING,
    FunActivityType.PERFORM_JAZZ: Interest.MUSIC_PLAYING,
    FunActivityType.PERFORM_ON_STREET: Interest.PERFORMANCE_ART,
    FunActivityType.JUMP_ON_BENCH: Interest.SPORTS_PRACTICING,
    
    # Romantic/Sensual Activities
    FunActivityType.SUNSET_PICNIC: Interest.NATURE_AND_OUTDOORS,
    FunActivityType.COUPLES_MASSAGE: Interest.FITNESS_AND_WELLNESS,
    FunActivityType.CANDLELIGHT_DINNER: Interest.COOKING_AND_FOOD,
    FunActivityType.STARGAZING_DATE: Interest.STARGAZING,
    FunActivityType.SENSUAL_DANCE: Interest.DANCE,
    FunActivityType.LOVE_LETTER_WRITING: Interest.WRITING,
    FunActivityType.HOT_SPRINGS_VISIT: Interest.NATURE_AND_OUTDOORS,
    FunActivityType.TANGO_LESSONS: Interest.DANCE,
    FunActivityType.CHOCOLATE_TASTING: Interest.COOKING_AND_FOOD,
    FunActivityType.PRIVATE_WINE_CELLAR: Interest.WINE_TASTING,
    FunActivityType.COUPLES_ART_CLASS: Interest.VISUAL_ARTS,
    FunActivityType.MOONLIGHT_SWIM: Interest.SWIMMING,
    FunActivityType.AROMATHERAPY_SESSION: Interest.FITNESS_AND_WELLNESS,
    FunActivityType.DOUBLE_MASSAGE: Interest.FITNESS_AND_WELLNESS,
    FunActivityType.PRIVATE_DANCE: Interest.DANCE,
    FunActivityType.KISSING_CONTEST: Interest.DATING,
    FunActivityType.ROLEPLAYING_GAME: Interest.GAMING,
    FunActivityType.SILK_ROBES_EVENING: Interest.FASHION,
    FunActivityType.EROTIC_STORYTELLING: Interest.PERFORMANCE_ART,
    FunActivityType.SCENT_CREATION: Interest.PERFUMERY,
    FunActivityType.FANTASY_ROLEPLAY: Interest.GAMING,
    FunActivityType.MASSAGE_OIL_MAKING: Interest.SOAP_MAKING,
    FunActivityType.INTIMATE_GAME_NIGHT: Interest.GAMING,
    FunActivityType.SENSUAL_FEEDING: Interest.DATING,
    FunActivityType.TANTRIC_BREATHWORK: Interest.MEDITATION,
    FunActivityType.LINGERIE_SHOPPING: Interest.FASHION,
    FunActivityType.LOVE_POETRY_READING: Interest.POETRY,
    FunActivityType.COUPLES_YOGA: Interest.YOGA,
    FunActivityType.SENSUAL_COOKING: Interest.COOKING_AND_FOOD,
    FunActivityType.AFTERGLOW_CUDDLING: Interest.DATING,
    FunActivityType.PRIVATE_CONCERT: Interest.MUSIC_LISTENING,
    FunActivityType.EROTIC_PHOTOGRAPHY: Interest.VISUAL_ARTS,
}

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
INTIMACY_ACTION_CONFIG = {
    # La chiave è il bisogno che questa azione soddisfa
    NeedType.INTIMACY: {
        # Non serve action_class_path qui perché il discoverer per l'intimità
        # saprà già quale classe usare (EngageIntimacyAction).
        "duration_hours": 1.5,
        "initiator_intimacy_gain": 60.0,
        "target_intimacy_gain": 50.0,
        "relationship_score_gain": 8,
        # Regole di validazione
        "required_relationship_types": {RelationshipType.ROMANTIC_PARTNER, RelationshipType.SPOUSE},
        "min_rel_score": 30,
        "initiator_desire_threshold": 50.0, # L'NPC deve avere il bisogno sotto questa soglia per iniziare
    }
}

# --- HaveFunAction ---
# Default per attività non configurate specificamente
HAVEFUN_DEFAULT_FUN_GAIN = 25.0
HAVEFUN_DEFAULT_DURATION_HOURS = 1.0
HAVEFUN_DEFAULT_COGNITIVE_EFFORT = 0.4 # Default per lo sforzo cognitivo

# Mappa di configurazione per ogni attività di divertimento
HAVEFUN_ACTIVITY_CONFIGS = {
    # ================= CATEGORIA 0: Generali =================
    SocialInteractionType.TALK: {
        "duration_ticks": 20,
        "initiator_social_gain": 10.0,
        "target_social_gain": 10.0,
        "rel_change": 1, # Una chiacchierata base migliora leggermente la relazione
    },

    SocialInteractionType.TELL_JOKE: {
        "duration_ticks": 15,
        "initiator_social_gain": 5.0, # Meno guadagno sociale, più divertimento
        "target_fun_gain": 20.0, # L'obiettivo principale è far divertire l'altro
        "rel_change_success": 3, # Una buona battuta rafforza molto il legame
        "rel_change_fail": -2,   # Una pessima battuta lo danneggia
        "success_chance": 0.75,  # 75% di probabilità che la battuta riesca
        # In futuro, la skill CHARISMA o COMEDY potrebbe influenzare questa probabilità
    },

    SocialInteractionType.COMPLIMENT: {
        "duration_ticks": 10,
        "initiator_social_gain": 2.0,
        "target_social_gain": 15.0, # Il complimento fa sentire bene chi lo riceve
        "rel_change_success": 2,
        "rel_change_fail": -4, # Un complimento goffo o mal percepito è molto dannoso
        "success_chance": 0.85,
        # In futuro, un tratto come SHY potrebbe abbassare la probabilità di successo
    },
    FunActivityType.MEDITATE: {
        "duration_hours": 1.0,
        "fun_gain": 5.0, # Non è super divertente, ma rilassante
        "effects_on_needs": {
            NeedType.STRESS: -30.0 # Riduce lo stress
        }
        # Non richiede oggetti
    },
    FunActivityType.DANCE: {
        "duration_hours": 2.0,
        "fun_gain": 80.0,
        "skill_to_practice": SkillType.DANCING,
        "skill_xp_gain": 40.0,
        "personality_modifiers": {
            TraitType.PARTY_ANIMAL: 2.5, # Un animale da festa ama ballare (+150% score)
            TraitType.SOCIAL: 1.5,
            TraitType.LONER: 0.3,       # Un solitario odia ballare (-70% score)
            TraitType.SHY: 0.5,
        }
    },
    FunActivityType.READ_BOOK_FOR_FUN: {
        "duration_hours": 1.5,
        "fun_gain": 60.0,
        "required_object_types": (ObjectType.BOOKSHELF,),
        "personality_modifiers": {
            TraitType.BOOKWORM: 2.0,
            TraitType.ACTIVE: 0.8,
            TraitType.PARTY_ANIMAL: 0.5,
        }
    },
}
    
HAVEFUN_ACTIVITY_CONFIGS = {
    # ================= ATTIVITÀ CREATIVE =================
    FunActivityType.PAINT: {
        "fun_gain": 45.0,
        "duration_hours": 2.0,
        "required_object_types": (ObjectType.EASEL, ObjectType.PAINTBRUSH),
        "skill_to_practice": SkillType.PAINTING,
        "skill_xp_gain": 60.0,
        "cognitive_effort": 0.8
    },
    FunActivityType.PLAY_GUITAR: {
        "fun_gain": 50.0,
        "duration_hours": 1.5,
        "required_object_types": (ObjectType.GUITAR,),
        "skill_to_practice": SkillType.GUITAR,
        "skill_xp_gain": 70.0,
        "cognitive_effort": 0.7,
        "is_noisy": True
    },
    FunActivityType.PLAY_PIANO: {
        "fun_gain": 48.0,
        "duration_hours": 1.5,
        "required_object_types": (ObjectType.PIANO,),
        "skill_to_practice": SkillType.PIANO,
        "skill_xp_gain": 65.0,
        "cognitive_effort": 0.75,
        "is_noisy": True
    },
    FunActivityType.PLAY_VIOLIN: {
        "fun_gain": 46.0,
        "duration_hours": 1.2,
        "required_object_types": (ObjectType.VIOLIN,),
        "skill_to_practice": SkillType.VIOLIN,
        "skill_xp_gain": 62.0,
        "cognitive_effort": 0.8,
        "is_noisy": True
    },
    FunActivityType.SING: {
        "fun_gain": 42.0,
        "duration_hours": 1.0,
        "skill_to_practice": SkillType.SINGING,
        "skill_xp_gain": 55.0,
        "cognitive_effort": 0.6,
        "is_noisy": True
    },
    FunActivityType.WRITE_BOOK_FOR_FUN: {
        "fun_gain": 40.0,
        "duration_hours": 2.5,
        "required_object_types": (ObjectType.COMPUTER,),
        "skill_to_practice": SkillType.WRITING,
        "skill_xp_gain": 70.0,
        "cognitive_effort": 0.9
    },
    FunActivityType.DJ_MIXING: {
        "fun_gain": 65.0,
        "duration_hours": 2.0,
        "required_object_types": (ObjectType.DJ_SET,),
        "skill_to_practice": SkillType.DJING,
        "skill_xp_gain": 75.0,
        "cognitive_effort": 0.85,
        "is_noisy": True
    },
    FunActivityType.PHOTOGRAPHY: {
        "fun_gain": 55.0,
        "duration_hours": 1.8,
        "required_object_types": (ObjectType.CAMERA,),
        "skill_to_practice": SkillType.PHOTOGRAPHY,
        "skill_xp_gain": 68.0,
        "cognitive_effort": 0.75
    },
    FunActivityType.KNITTING: {
        "fun_gain": 35.0,
        "duration_hours": 1.5,
        "required_object_types": (ObjectType.KNITTING_NEEDLES,),
        "skill_to_practice": SkillType.KNITTING,
        "skill_xp_gain": 45.0,
        "cognitive_effort": 0.5
    },
    FunActivityType.POTTERY: {
        "fun_gain": 50.0,
        "duration_hours": 2.2,
        "required_object_types": (ObjectType.POTTERY_WHEEL,),
        "skill_to_practice": SkillType.POTTERY,
        "skill_xp_gain": 65.0,
        "cognitive_effort": 0.7
    },
    FunActivityType.WOODWORKING: {
        "fun_gain": 52.0,
        "duration_hours": 3.0,
        "required_object_types": (ObjectType.WOODWORKING_TOOLS,),
        "skill_to_practice": SkillType.WOODWORKING,
        "skill_xp_gain": 70.0,
        "cognitive_effort": 0.8,
        "is_noisy": True
    },
    FunActivityType.DIGITAL_ART: {
        "fun_gain": 58.0,
        "duration_hours": 2.0,
        "required_object_types": (ObjectType.TABLET,),
        "skill_to_practice": SkillType.DIGITAL_ART,
        "skill_xp_gain": 72.0,
        "cognitive_effort": 0.85
    },
    FunActivityType.SCULPTING: {
        "fun_gain": 50.0,
        "duration_hours": 2.5,
        "required_object_types": (ObjectType.SCULPTING_TOOLS,),
        "skill_to_practice": SkillType.SCULPTING,
        "skill_xp_gain": 65.0,
        "cognitive_effort": 0.8
    },
    FunActivityType.PHOTO_EDITING: {
        "fun_gain": 40.0,
        "duration_hours": 1.5,
        "required_object_types": (ObjectType.COMPUTER,),
        "skill_to_practice": SkillType.PHOTOGRAPHY,
        "skill_xp_gain": 55.0,
        "cognitive_effort": 0.7
    },
    FunActivityType.CALLIGRAPHY: {
        "fun_gain": 42.0,
        "duration_hours": 1.0,
        "skill_to_practice": SkillType.CALLIGRAPHY,
        "skill_xp_gain": 50.0,
        "cognitive_effort": 0.65
    },
    FunActivityType.JEWELRY_MAKING: {
        "fun_gain": 48.0,
        "duration_hours": 2.0,
        "required_object_types": (ObjectType.JEWELRY_TOOLS,),
        "skill_to_practice": SkillType.JEWELRY_MAKING,
        "skill_xp_gain": 60.0,
        "cognitive_effort": 0.75
    },
    FunActivityType.UPHOLSTERY: {
        "fun_gain": 45.0,
        "duration_hours": 2.5,
        "skill_to_practice": SkillType.HANDINESS,
        "skill_xp_gain": 58.0,
        "cognitive_effort": 0.7
    },
    FunActivityType.GAME_DESIGN: {
        "fun_gain": 65.0,
        "duration_hours": 3.0,
        "required_object_types": (ObjectType.COMPUTER,),
        "skill_to_practice": SkillType.GAME_DESIGN,
        "skill_xp_gain": 80.0,
        "cognitive_effort": 0.95
    },
    FunActivityType.COMIC_DRAWING: {
        "fun_gain": 55.0,
        "duration_hours": 2.0,
        "skill_to_practice": SkillType.DRAWING,
        "skill_xp_gain": 68.0,
        "cognitive_effort": 0.8
    },
    FunActivityType.COSTUME_DESIGN: {
        "fun_gain": 52.0,
        "duration_hours": 2.5,
        "required_object_types": (ObjectType.SEWING_MACHINE,),
        "skill_to_practice": SkillType.SEWING,
        "skill_xp_gain": 65.0,
        "cognitive_effort": 0.8
    },
    FunActivityType.GRAFFITI_ART: {
        "fun_gain": 60.0,
        "duration_hours": 1.5,
        "required_object_types": (ObjectType.SPRAY_PAINT,),
        "skill_to_practice": SkillType.STREET_ART,
        "skill_xp_gain": 70.0,
        "cognitive_effort": 0.75,
        "is_outdoors": True
    },
    FunActivityType.ANIMATION: {
        "fun_gain": 62.0,
        "duration_hours": 3.5,
        "required_object_types": (ObjectType.COMPUTER,),
        "skill_to_practice": SkillType.ANIMATION,
        "skill_xp_gain": 85.0,
        "cognitive_effort": 0.9
    },
    FunActivityType.LEATHERWORKING: {
        "fun_gain": 48.0,
        "duration_hours": 2.0,
        "required_object_types": (ObjectType.LEATHER_TOOLS,),
        "skill_to_practice": SkillType.LEATHERWORK,
        "skill_xp_gain": 62.0,
        "cognitive_effort": 0.75
    },
    FunActivityType.MODEL_BUILDING: {
        "fun_gain": 50.0,
        "duration_hours": 2.5,
        "skill_to_practice": SkillType.MODELING,
        "skill_xp_gain": 65.0,
        "cognitive_effort": 0.7
    },
    FunActivityType.STENCIL_ART: {
        "fun_gain": 42.0,
        "duration_hours": 1.2,
        "skill_to_practice": SkillType.DESIGN,
        "skill_xp_gain": 52.0,
        "cognitive_effort": 0.65
    },
    FunActivityType.SONGWRITING: {
        "fun_gain": 58.0,
        "duration_hours": 1.8,
        "skill_to_practice": SkillType.COMPOSITION,
        "skill_xp_gain": 72.0,
        "cognitive_effort": 0.85
    },
    FunActivityType.POETRY: {
        "fun_gain": 50.0,
        "duration_hours": 1.0,
        "skill_to_practice": SkillType.WRITING,
        "skill_xp_gain": 58.0,
        "cognitive_effort": 0.8
    },
    FunActivityType.FURNITURE_RESTORATION: {
        "fun_gain": 46.0,
        "duration_hours": 3.0,
        "required_object_types": (ObjectType.WOODWORKING_TOOLS,),
        "skill_to_practice": SkillType.RESTORATION,
        "skill_xp_gain": 62.0,
        "cognitive_effort": 0.75
    },
    FunActivityType.BEADWORK: {
        "fun_gain": 38.0,
        "duration_hours": 1.5,
        "skill_to_practice": SkillType.CRAFTING,
        "skill_xp_gain": 48.0,
        "cognitive_effort": 0.5
    },
    FunActivityType.ORIGAMI: {
        "fun_gain": 35.0,
        "duration_hours": 0.8,
        "skill_to_practice": SkillType.PAPER_CRAFT,
        "skill_xp_gain": 42.0,
        "cognitive_effort": 0.6
    },
    FunActivityType.BOTANICAL_ILLUSTRATION: {
        "fun_gain": 46.0,
        "duration_hours": 1.5,
        "skill_to_practice": SkillType.BOTANICAL_ART,
        "skill_xp_gain": 55.0,
        "cognitive_effort": 0.7
    },
    FunActivityType.CERAMIC_GLAZING: {
        "fun_gain": 44.0,
        "duration_hours": 1.2,
        "required_object_types": (ObjectType.POTTERY_TOOLS,),
        "skill_to_practice": SkillType.POTTERY,
        "skill_xp_gain": 52.0,
        "cognitive_effort": 0.6
    },
    FunActivityType.PUPPET_MAKING: {
        "fun_gain": 52.0,
        "duration_hours": 2.0,
        "skill_to_practice": SkillType.CRAFTING,
        "skill_xp_gain": 60.0,
        "cognitive_effort": 0.7
    },
    FunActivityType.GLASS_ETCHING: {
        "fun_gain": 48.0,
        "duration_hours": 1.8,
        "required_object_types": (ObjectType.GLASS_TOOLS,),
        "skill_to_practice": SkillType.GLASS_ART,
        "skill_xp_gain": 58.0,
        "cognitive_effort": 0.75
    },
    FunActivityType.TEXTILE_DESIGN: {
        "fun_gain": 52.0,
        "duration_hours": 2.0,
        "required_object_types": (ObjectType.SEWING_MACHINE,),
        "skill_to_practice": SkillType.TEXTILE_ART,
        "skill_xp_gain": 65.0,
        "cognitive_effort": 0.8
    },
    FunActivityType.COSPLAY_CRAFTING: {
        "fun_gain": 65.0,
        "duration_hours": 3.0,
        "skill_to_practice": SkillType.COSTUME_DESIGN,
        "skill_xp_gain": 75.0,
        "cognitive_effort": 0.85
    },

    # ================= ATTIVITÀ INTELLETTUALI =================
    FunActivityType.READ_BOOK_FOR_FUN: {
        "fun_gain": 40.0,
        "duration_hours": 1.5,
        "skill_to_practice": SkillType.READING,
        "skill_xp_gain": 45.0,
        "cognitive_effort": 0.6
    },
    FunActivityType.PRACTICE_PUBLIC_SPEAKING: {
        "fun_gain": 35.0,
        "duration_hours": 1.0,
        "skill_to_practice": SkillType.RHETORIC,
        "skill_xp_gain": 50.0,
        "cognitive_effort": 0.8
    },
    FunActivityType.BROWSE_SOCIAL_MEDIA: {
        "fun_gain": 25.0,
        "duration_hours": 0.5,
        "required_object_types": (ObjectType.SMARTPHONE,),
        "cognitive_effort": 0.3
    },
    FunActivityType.VISIT_MUSEUM: {
        "fun_gain": 45.0,
        "duration_hours": 2.0,
        "skill_to_practice": SkillType.ART_KNOWLEDGE,
        "skill_xp_gain": 40.0,
        "cognitive_effort": 0.5
    },
    FunActivityType.DRINK_COFFEE: {
        "fun_gain": 30.0,
        "duration_hours": 0.3,
        "cognitive_effort": 0.1,
        "effects_on_needs": {NeedType.ENERGY: 25.0}
    },
    FunActivityType.PLAY_CHESS: {
        "fun_gain": 42.0,
        "duration_hours": 1.0,
        "required_object_types": (ObjectType.CHESS_SET,),
        "skill_to_practice": SkillType.STRATEGY,
        "skill_xp_gain": 58.0,
        "cognitive_effort": 0.85
    },
    FunActivityType.DO_CROSSWORD_PUZZLE: {
        "fun_gain": 35.0,
        "duration_hours": 0.7,
        "skill_to_practice": SkillType.LOGIC,
        "skill_xp_gain": 42.0,
        "cognitive_effort": 0.75
    },
    FunActivityType.RESEARCH_INTEREST_ONLINE: {
        "fun_gain": 32.0,
        "duration_hours": 1.2,
        "required_object_types": (ObjectType.COMPUTER,),
        "skill_to_practice": SkillType.RESEARCH,
        "skill_xp_gain": 48.0,
        "cognitive_effort": 0.8
    },
    FunActivityType.DAYDREAM: {
        "fun_gain": 20.0,
        "duration_hours": 0.5,
        "cognitive_effort": 0.1
    },
    FunActivityType.WATCH_CLOUDS: {
        "fun_gain": 22.0,
        "duration_hours": 0.4,
        "cognitive_effort": 0.05,
        "is_outdoors": True
    },
    FunActivityType.PEOPLE_WATCH: {
        "fun_gain": 28.0,
        "duration_hours": 0.6,
        "skill_to_practice": SkillType.PSYCHOLOGY,
        "skill_xp_gain": 30.0,
        "cognitive_effort": 0.3
    },
    FunActivityType.MEDITATE: {
        "fun_gain": 35.0,
        "duration_hours": 0.5,
        "skill_to_practice": SkillType.MEDITATION,
        "skill_xp_gain": 40.0,
        "cognitive_effort": 0.15,
        "effects_on_needs": {NeedType.STRESS: -40.0}
    },
    FunActivityType.STUDY_PHILOSOPHY: {
        "fun_gain": 38.0,
        "duration_hours": 1.8,
        "skill_to_practice": SkillType.PHILOSOPHY,
        "skill_xp_gain": 55.0,
        "cognitive_effort": 0.9
    },
    FunActivityType.LEARN_LANGUAGE: {
        "fun_gain": 42.0,
        "duration_hours": 1.5,
        "skill_to_practice": SkillType.LINGUISTICS,
        "skill_xp_gain": 58.0,
        "cognitive_effort": 0.85
    },
    FunActivityType.ASTRONOMY_OBSERVATION: {
        "fun_gain": 50.0,
        "duration_hours": 1.5,
        "required_object_types": (ObjectType.TELESCOPE,),
        "skill_to_practice": SkillType.ASTRONOMY,
        "skill_xp_gain": 60.0,
        "cognitive_effort": 0.6,
        "is_outdoors": True
    },
    FunActivityType.JOURNALING: {
        "fun_gain": 32.0,
        "duration_hours": 0.8,
        "skill_to_practice": SkillType.WRITING,
        "skill_xp_gain": 40.0,
        "cognitive_effort": 0.5
    },
    FunActivityType.SUDOKU: {
        "fun_gain": 30.0,
        "duration_hours": 0.5,
        "skill_to_practice": SkillType.LOGIC,
        "skill_xp_gain": 35.0,
        "cognitive_effort": 0.7
    },
    FunActivityType.TAROT_READING: {
        "fun_gain": 35.0,
        "duration_hours": 0.7,
        "skill_to_practice": SkillType.INTUITION,
        "skill_xp_gain": 32.0,
        "cognitive_effort": 0.4
    },
    FunActivityType.BIRD_WATCHING: {
        "fun_gain": 45.0,
        "duration_hours": 1.5,
        "required_object_types": (ObjectType.BINOCULARS,),
        "skill_to_practice": SkillType.ORNITHOLOGY,
        "skill_xp_gain": 52.0,
        "cognitive_effort": 0.3,
        "is_outdoors": True
    },
    FunActivityType.GENEALOGY_RESEARCH: {
        "fun_gain": 40.0,
        "duration_hours": 2.5,
        "required_object_types": (ObjectType.COMPUTER,),
        "skill_to_practice": SkillType.RESEARCH,
        "skill_xp_gain": 55.0,
        "cognitive_effort": 0.8
    },
    FunActivityType.PUZZLE_SOLVING: {
        "fun_gain": 35.0,
        "duration_hours": 1.0,
        "skill_to_practice": SkillType.PROBLEM_SOLVING,
        "skill_xp_gain": 45.0,
        "cognitive_effort": 0.75
    },
    FunActivityType.ASTROLOGY_STUDY: {
        "fun_gain": 32.0,
        "duration_hours": 1.0,
        "skill_to_practice": SkillType.ASTROLOGY,
        "skill_xp_gain": 38.0,
        "cognitive_effort": 0.6
    },
    FunActivityType.MINDFULNESS_PRACTICE: {
        "fun_gain": 30.0,
        "duration_hours": 0.4,
        "skill_to_practice": SkillType.MEDITATION,
        "skill_xp_gain": 35.0,
        "cognitive_effort": 0.1,
        "effects_on_needs": {NeedType.STRESS: -30.0}
    },
    FunActivityType.STARGAZING: {
        "fun_gain": 48.0,
        "duration_hours": 1.2,
        "cognitive_effort": 0.2,
        "is_outdoors": True
    },
    FunActivityType.CHEMISTRY_EXPERIMENTS: {
        "fun_gain": 55.0,
        "duration_hours": 2.0,
        "required_object_types": (ObjectType.CHEMISTRY_SET,),
        "skill_to_practice": SkillType.CHEMISTRY,
        "skill_xp_gain": 70.0,
        "cognitive_effort": 0.9
    },
    FunActivityType.BOTANY_STUDY: {
        "fun_gain": 42.0,
        "duration_hours": 1.5,
        "skill_to_practice": SkillType.BOTANY,
        "skill_xp_gain": 55.0,
        "cognitive_effort": 0.7
    },
    FunActivityType.HISTORY_DOCUMENTARY: {
        "fun_gain": 38.0,
        "duration_hours": 1.2,
        "skill_to_practice": SkillType.HISTORY,
        "skill_xp_gain": 45.0,
        "cognitive_effort": 0.6
    },
    FunActivityType.MAP_STUDY: {
        "fun_gain": 33.0,
        "duration_hours": 0.8,
        "skill_to_practice": SkillType.GEOGRAPHY,
        "skill_xp_gain": 40.0,
        "cognitive_effort": 0.65
    },
    FunActivityType.MEMORY_TRAINING: {
        "fun_gain": 35.0,
        "duration_hours": 0.6,
        "skill_to_practice": SkillType.MEMORY,
        "skill_xp_gain": 42.0,
        "cognitive_effort": 0.75
    },
    FunActivityType.PHILOSOPHICAL_DEBATE: {
        "fun_gain": 50.0,
        "duration_hours": 1.5,
        "skill_to_practice": SkillType.RHETORIC,
        "skill_xp_gain": 60.0,
        "cognitive_effort": 0.85
    },
    FunActivityType.ECONOMICS_ANALYSIS: {
        "fun_gain": 43.0,
        "duration_hours": 2.0,
        "skill_to_practice": SkillType.ECONOMICS,
        "skill_xp_gain": 58.0,
        "cognitive_effort": 0.9
    },
    FunActivityType.PSYCHOLOGY_STUDY: {
        "fun_gain": 41.0,
        "duration_hours": 1.8,
        "skill_to_practice": SkillType.PSYCHOLOGY,
        "skill_xp_gain": 55.0,
        "cognitive_effort": 0.85
    },
    FunActivityType.ARCHITECTURE_STUDY: {
        "fun_gain": 39.0,
        "duration_hours": 1.5,
        "skill_to_practice": SkillType.ARCHITECTURE,
        "skill_xp_gain": 52.0,
        "cognitive_effort": 0.8
    },
    FunActivityType.CRYPTOGRAPHY: {
        "fun_gain": 53.0,
        "duration_hours": 2.2,
        "skill_to_practice": SkillType.CRYPTOGRAPHY,
        "skill_xp_gain": 68.0,
        "cognitive_effort": 0.95
    },
    FunActivityType.STRATEGY_GAME_SOLO: {
        "fun_gain": 47.0,
        "duration_hours": 1.2,
        "skill_to_practice": SkillType.STRATEGY,
        "skill_xp_gain": 58.0,
        "cognitive_effort": 0.88
    },
    FunActivityType.MYTHOLOGY_STUDY: {
        "fun_gain": 44.0,
        "duration_hours": 1.5,
        "skill_to_practice": SkillType.MYTHOLOGY,
        "skill_xp_gain": 50.0,
        "cognitive_effort": 0.7
    },
    FunActivityType.POETRY_ANALYSIS: {
        "fun_gain": 42.0,
        "duration_hours": 1.0,
        "skill_to_practice": SkillType.LITERATURE,
        "skill_xp_gain": 48.0,
        "cognitive_effort": 0.8
    },
    FunActivityType.AI_PROGRAMMING: {
        "fun_gain": 65.0,
        "duration_hours": 3.0,
        "required_object_types": (ObjectType.COMPUTER,),
        "skill_to_practice": SkillType.AI_DEVELOPMENT,
        "skill_xp_gain": 85.0,
        "cognitive_effort": 0.95,
        "effects_on_needs": {NeedType.STRESS: 30.0}
    },

    # ================= ATTIVITÀ FISICHE =================
    FunActivityType.DANCE: {
        "fun_gain": 60.0,
        "duration_hours": 1.2,
        "skill_to_practice": SkillType.DANCING,
        "skill_xp_gain": 65.0,
        "cognitive_effort": 0.4,
        "effects_on_needs": {NeedType.ENERGY: -35.0}
    },
    FunActivityType.GO_FOR_A_JOG: {
        "fun_gain": 45.0,
        "duration_hours": 0.8,
        "skill_to_practice": SkillType.RUNNING,
        "skill_xp_gain": 50.0,
        "cognitive_effort": 0.3,
        "is_outdoors": True,
        "effects_on_needs": {NeedType.HUNGER: -30.0, NeedType.ENERGY: -40.0}
    },
    FunActivityType.JOG_IN_PLACE: {
        "fun_gain": 35.0,
        "duration_hours": 0.5,
        "skill_to_practice": SkillType.RUNNING,
        "skill_xp_gain": 40.0,
        "cognitive_effort": 0.25,
        "effects_on_needs": {NeedType.ENERGY: -25.0}
    },
    FunActivityType.GO_HIKING: {
        "fun_gain": 70.0,
        "duration_hours": 3.0,
        "skill_to_practice": SkillType.HIKING,
        "skill_xp_gain": 60.0,
        "cognitive_effort": 0.4,
        "is_outdoors": True,
        "effects_on_needs": {NeedType.HUNGER: -50.0, NeedType.ENERGY: -60.0}
    },
    FunActivityType.SWIMMING: {
        "fun_gain": 55.0,
        "duration_hours": 1.0,
        "skill_to_practice": SkillType.SWIMMING,
        "skill_xp_gain": 62.0,
        "cognitive_effort": 0.35,
        "effects_on_needs": {NeedType.HYGIENE: 45.0, NeedType.ENERGY: -45.0}
    },
    FunActivityType.GARDENING: {
        "fun_gain": 50.0,
        "duration_hours": 2.0,
        "required_object_types": (ObjectType.GARDENING_TOOLS,),
        "skill_to_practice": SkillType.GARDENING,
        "skill_xp_gain": 55.0,
        "cognitive_effort": 0.5,
        "is_outdoors": True,
        "effects_on_needs": {NeedType.ENERGY: -45.0}
    },
    FunActivityType.FISHING: {
        "fun_gain": 47.0,
        "duration_hours": 2.5,
        "required_object_types": (ObjectType.FISHING_ROD,),
        "skill_to_practice": SkillType.FISHING,
        "skill_xp_gain": 58.0,
        "cognitive_effort": 0.3,
        "is_outdoors": True
    },
    FunActivityType.PLAY_SPORTS_CASUAL: {
        "fun_gain": 60.0,
        "duration_hours": 1.5,
        "skill_to_practice": SkillType.SPORTS,
        "skill_xp_gain": 52.0,
        "cognitive_effort": 0.45,
        "effects_on_needs": {NeedType.ENERGY: -50.0}
    },
    FunActivityType.EXPLORE_NEIGHBORHOOD: {
        "fun_gain": 42.0,
        "duration_hours": 1.2,
        "cognitive_effort": 0.2,
        "is_outdoors": True,
        "effects_on_needs": {NeedType.ENERGY: -30.0}
    },
    FunActivityType.ROCK_CLIMBING: {
        "fun_gain": 75.0,
        "duration_hours": 2.5,
        "required_object_types": (ObjectType.CLIMBING_GEAR,),
        "skill_to_practice": SkillType.CLIMBING,
        "skill_xp_gain": 80.0,
        "cognitive_effort": 0.6,
        "is_outdoors": True,
        "effects_on_needs": {NeedType.ENERGY: -70.0}
    },
    FunActivityType.MOUNTAIN_BIKING: {
        "fun_gain": 72.0,
        "duration_hours": 2.0,
        "required_object_types": (ObjectType.BICYCLE,),
        "skill_to_practice": SkillType.CYCLING,
        "skill_xp_gain": 77.0,
        "cognitive_effort": 0.55,
        "is_outdoors": True,
        "effects_on_needs": {NeedType.ENERGY: -65.0}
    },
    FunActivityType.SURFING: {
        "fun_gain": 80.0,
        "duration_hours": 2.0,
        "required_object_types": (ObjectType.SURFBOARD,),
        "skill_to_practice": SkillType.SURFING,
        "skill_xp_gain": 85.0,
        "cognitive_effort": 0.5,
        "is_outdoors": True,
        "effects_on_needs": {NeedType.HYGIENE: 50.0, NeedType.ENERGY: -75.0}
    },
    FunActivityType.KAYAKING: {
        "fun_gain": 67.0,
        "duration_hours": 1.8,
        "required_object_types": (ObjectType.KAYAK,),
        "skill_to_practice": SkillType.KAYAKING,
        "skill_xp_gain": 72.0,
        "cognitive_effort": 0.45,
        "is_outdoors": True,
        "effects_on_needs": {NeedType.ENERGY: -60.0}
    },
    FunActivityType.ARCHERY: {
        "fun_gain": 57.0,
        "duration_hours": 1.5,
        "required_object_types": (ObjectType.BOW,),
        "skill_to_practice": SkillType.ARCHERY,
        "skill_xp_gain": 65.0,
        "cognitive_effort": 0.6,
        "is_outdoors": True
    },
    FunActivityType.PARKOUR: {
        "fun_gain": 70.0,
        "duration_hours": 1.5,
        "skill_to_practice": SkillType.PARKOUR,
        "skill_xp_gain": 75.0,
        "cognitive_effort": 0.7,
        "is_outdoors": True,
        "effects_on_needs": {NeedType.ENERGY: -65.0}
    },
    FunActivityType.SKATEBOARDING: {
        "fun_gain": 62.0,
        "duration_hours": 1.2,
        "required_object_types": (ObjectType.SKATEBOARD,),
        "skill_to_practice": SkillType.SKATEBOARDING,
        "skill_xp_gain": 70.0,
        "cognitive_effort": 0.5,
        "is_outdoors": True,
        "effects_on_needs": {NeedType.ENERGY: -45.0}
    },
    FunActivityType.BEACH_VOLLEYBALL: {
        "fun_gain": 65.0,
        "duration_hours": 1.5,
        "skill_to_practice": SkillType.VOLLEYBALL,
        "skill_xp_gain": 60.0,
        "cognitive_effort": 0.4,
        "is_outdoors": True,
        "effects_on_needs": {NeedType.ENERGY: -55.0}
    },
    FunActivityType.DISC_GOLF: {
        "fun_gain": 52.0,
        "duration_hours": 1.8,
        "required_object_types": (ObjectType.FRISBEE,),
        "skill_to_practice": SkillType.DISC_SPORTS,
        "skill_xp_gain": 58.0,
        "cognitive_effort": 0.35,
        "is_outdoors": True
    },
    FunActivityType.ORIENTEERING: {
        "fun_gain": 60.0,
        "duration_hours": 2.0,
        "skill_to_practice": SkillType.NAVIGATION,
        "skill_xp_gain": 67.0,
        "cognitive_effort": 0.65,
        "is_outdoors": True
    },
    FunActivityType.GEOCACHING: {
        "fun_gain": 57.0,
        "duration_hours": 2.2,
        "required_object_types": (ObjectType.GPS_DEVICE,),
        "skill_to_practice": SkillType.GEOCACHING,
        "skill_xp_gain": 62.0,
        "cognitive_effort": 0.6,
        "is_outdoors": True
    },
    FunActivityType.TREE_CLIMBING: {
        "fun_gain": 50.0,
        "duration_hours": 1.0,
        "skill_to_practice": SkillType.CLIMBING,
        "skill_xp_gain": 55.0,
        "cognitive_effort": 0.5,
        "is_outdoors": True,
        "effects_on_needs": {NeedType.ENERGY: -40.0}
    },
    FunActivityType.SNOWSHOEING: {
        "fun_gain": 55.0,
        "duration_hours": 2.0,
        "required_object_types": (ObjectType.SNOWSHOES,),
        "skill_to_practice": SkillType.WINTER_SPORTS,
        "skill_xp_gain": 60.0,
        "cognitive_effort": 0.4,
        "is_outdoors": True,
        "effects_on_needs": {NeedType.ENERGY: -60.0}
    },
    FunActivityType.STARGAZING_HIKE: {
        "fun_gain": 65.0,
        "duration_hours": 2.5,
        "skill_to_practice": SkillType.HIKING,
        "skill_xp_gain": 50.0,
        "cognitive_effort": 0.3,
        "is_outdoors": True,
        "effects_on_needs": {NeedType.ENERGY: -70.0}
    },
    FunActivityType.BIRDING: {
        "fun_gain": 47.0,
        "duration_hours": 1.5,
        "required_object_types": (ObjectType.BINOCULARS,),
        "skill_to_practice": SkillType.ORNITHOLOGY,
        "skill_xp_gain": 55.0,
        "cognitive_effort": 0.3,
        "is_outdoors": True
    },
    FunActivityType.FOREST_BATHING: {
        "fun_gain": 42.0,
        "duration_hours": 1.0,
        "cognitive_effort": 0.1,
        "is_outdoors": True,
        "effects_on_needs": {NeedType.STRESS: -35.0}
    },
    FunActivityType.NATURE_PHOTOGRAPHY: {
        "fun_gain": 60.0,
        "duration_hours": 2.0,
        "required_object_types": (ObjectType.CAMERA,),
        "skill_to_practice": SkillType.PHOTOGRAPHY,
        "skill_xp_gain": 70.0,
        "cognitive_effort": 0.5,
        "is_outdoors": True
    },
    FunActivityType.BOTANICAL_FORAGING: {
        "fun_gain": 52.0,
        "duration_hours": 1.8,
        "skill_to_practice": SkillType.FORAGING,
        "skill_xp_gain": 58.0,
        "cognitive_effort": 0.4,
        "is_outdoors": True
    },
    FunActivityType.ROCK_HUNTING: {
        "fun_gain": 45.0,
        "duration_hours": 1.5,
        "skill_to_practice": SkillType.GEOLOGY,
        "skill_xp_gain": 50.0,
        "cognitive_effort": 0.35,
        "is_outdoors": True
    },
    FunActivityType.WATERFALL_EXPLORATION: {
        "fun_gain": 70.0,
        "duration_hours": 2.5,
        "skill_to_practice": SkillType.HIKING,
        "skill_xp_gain": 55.0,
        "cognitive_effort": 0.4,
        "is_outdoors": True,
        "effects_on_needs": {NeedType.ENERGY: -65.0}
    },
    FunActivityType.CAVING: {
        "fun_gain": 75.0,
        "duration_hours": 3.0,
        "required_object_types": (ObjectType.CAVING_GEAR,),
        "skill_to_practice": SkillType.SPELUNKING,
        "skill_xp_gain": 80.0,
        "cognitive_effort": 0.7,
        "is_outdoors": True
    },
    FunActivityType.STANDUP_PADDLEBOARD: {
        "fun_gain": 62.0,
        "duration_hours": 1.5,
        "required_object_types": (ObjectType.PADDLEBOARD,),
        "skill_to_practice": SkillType.PADDLEBOARDING,
        "skill_xp_gain": 70.0,
        "cognitive_effort": 0.45,
        "is_outdoors": True,
        "effects_on_needs": {NeedType.ENERGY: -55.0}
    },
    FunActivityType.ICE_SKATING: {
        "fun_gain": 57.0,
        "duration_hours": 1.2,
        "required_object_types": (ObjectType.ICE_SKATES,),
        "skill_to_practice": SkillType.SKATING,
        "skill_xp_gain": 65.0,
        "cognitive_effort": 0.5
    },
    FunActivityType.SNOWBALL_FIGHT: {
        "fun_gain": 60.0,
        "duration_hours": 0.8,
        "cognitive_effort": 0.3,
        "is_outdoors": True,
        "effects_on_needs": {NeedType.ENERGY: -35.0}
    },
    FunActivityType.FRISBEE_GOLF: {
        "fun_gain": 52.0,
        "duration_hours": 1.5,
        "required_object_types": (ObjectType.FRISBEE,),
        "skill_to_practice": SkillType.DISC_SPORTS,
        "skill_xp_gain": 55.0,
        "cognitive_effort": 0.35,
        "is_outdoors": True
    },
    FunActivityType.CANYONING: {
        "fun_gain": 80.0,
        "duration_hours": 3.5,
        "required_object_types": (ObjectType.CANYONING_GEAR,),
        "skill_to_practice": SkillType.CANYONING,
        "skill_xp_gain": 85.0,
        "cognitive_effort": 0.8,
        "is_outdoors": True,
        "effects_on_needs": {NeedType.ENERGY: -80.0}
    },
    FunActivityType.URBAN_EXPLORATION: {
        "fun_gain": 65.0,
        "duration_hours": 2.0,
        "skill_to_practice": SkillType.EXPLORATION,
        "skill_xp_gain": 60.0,
        "cognitive_effort": 0.5,
        "is_outdoors": True
    },
    FunActivityType.STONE_SKIPPING: {
        "fun_gain": 30.0,
        "duration_hours": 0.3,
        "cognitive_effort": 0.1,
        "is_outdoors": True
    },
    FunActivityType.SUNRISE_YOGA: {
        "fun_gain": 50.0,
        "duration_hours": 1.0,
        "skill_to_practice": SkillType.YOGA,
        "skill_xp_gain": 55.0,
        "cognitive_effort": 0.2,
        "is_outdoors": True,
        "effects_on_needs": {NeedType.STRESS: -45.0}
    },

    # ================= ATTIVITÀ DOMESTICHE =================
    FunActivityType.WATCH_TV: {
        "fun_gain": 35.0,
        "duration_hours": 1.0,
        "cognitive_effort": 0.1,
        "effects_on_needs": {NeedType.ENERGY: -20.0}
    },
    FunActivityType.COOKING_SHOW: {
        "fun_gain": 35.0,
        "duration_hours": 0.5,
        "skill_to_practice": SkillType.COOKING,
        "skill_xp_gain": 40.0,
        "cognitive_effort": 0.3
    },
    FunActivityType.PODCAST_LISTENING: {
        "fun_gain": 32.0,
        "duration_hours": 0.7,
        "cognitive_effort": 0.2
    },
    FunActivityType.VIRTUAL_TOUR: {
        "fun_gain": 40.0,
        "duration_hours": 1.0,
        "required_object_types": (ObjectType.COMPUTER,),
        "cognitive_effort": 0.25
    },
    FunActivityType.HOME_BAKING: {
        "fun_gain": 50.0,
        "duration_hours": 1.8,
        "required_object_types": (ObjectType.OVEN,),
        "skill_to_practice": SkillType.BAKING,
        "skill_xp_gain": 60.0,
        "cognitive_effort": 0.65,
        "effects_on_needs": {NeedType.HUNGER: -40.0}
    },
    FunActivityType.AQUARIUM_WATCHING: {
        "fun_gain": 25.0,
        "duration_hours": 0.4,
        "cognitive_effort": 0.05
    },
    FunActivityType.HOME_BREWING: {
        "fun_gain": 50.0,
        "duration_hours": 3.0,
        "required_object_types": (ObjectType.BREWING_KIT,),
        "skill_to_practice": SkillType.BREWING,
        "skill_xp_gain": 65.0,
        "cognitive_effort": 0.7
    },
    FunActivityType.PUZZLE_ASSEMBLY: {
        "fun_gain": 42.0,
        "duration_hours": 2.0,
        "skill_to_practice": SkillType.PATIENCE,
        "skill_xp_gain": 48.0,
        "cognitive_effort": 0.65
    },
    FunActivityType.MODEL_TRAIN_SETUP: {
        "fun_gain": 55.0,
        "duration_hours": 3.0,
        "required_object_types": (ObjectType.MODEL_TRAIN_SET,),
        "skill_to_practice": SkillType.MODELING,
        "skill_xp_gain": 70.0,
        "cognitive_effort": 0.75
    },
    FunActivityType.HOME_DECORATING: {
        "fun_gain": 47.0,
        "duration_hours": 2.0,
        "skill_to_practice": SkillType.INTERIOR_DESIGN,
        "skill_xp_gain": 60.0,
        "cognitive_effort": 0.7
    },
    FunActivityType.CANDLE_MAKING: {
        "fun_gain": 42.0,
        "duration_hours": 1.5,
        "required_object_types": (ObjectType.CANDLE_MAKING_KIT,),
        "skill_to_practice": SkillType.CANDLE_CRAFT,
        "skill_xp_gain": 50.0,
        "cognitive_effort": 0.6
    },
    FunActivityType.SOAP_CRAFTING: {
        "fun_gain": 44.0,
        "duration_hours": 1.8,
        "required_object_types": (ObjectType.SOAP_MAKING_KIT,),
        "skill_to_practice": SkillType.SOAP_CRAFT,
        "skill_xp_gain": 53.0,
        "cognitive_effort": 0.65
    },
    FunActivityType.INDOOR_GARDENING: {
        "fun_gain": 40.0,
        "duration_hours": 1.0,
        "skill_to_practice": SkillType.GARDENING,
        "skill_xp_gain": 45.0,
        "cognitive_effort": 0.4
    },
    FunActivityType.TERRARIUM_BUILDING: {
        "fun_gain": 49.0,
        "duration_hours": 1.5,
        "skill_to_practice": SkillType.GARDENING,
        "skill_xp_gain": 58.0,
        "cognitive_effort": 0.55
    },
    FunActivityType.HOME_WINE_TASTING: {
        "fun_gain": 38.0,
        "duration_hours": 0.7,
        "skill_to_practice": SkillType.WINE_KNOWLEDGE,
        "skill_xp_gain": 42.0,
        "cognitive_effort": 0.3
    },
    FunActivityType.VIRTUAL_CONCERT: {
        "fun_gain": 55.0,
        "duration_hours": 1.5,
        "required_object_types": (ObjectType.COMPUTER,),
        "cognitive_effort": 0.2
    },
    FunActivityType.FAMILY_HISTORY_ALBUM: {
        "fun_gain": 45.0,
        "duration_hours": 2.0,
        "skill_to_practice": SkillType.GENEALOGY,
        "skill_xp_gain": 50.0,
        "cognitive_effort": 0.5
    },
    FunActivityType.HOME_SPA: {
        "fun_gain": 50.0,
        "duration_hours": 1.2,
        "cognitive_effort": 0.15,
        "effects_on_needs": {NeedType.STRESS: -50.0, NeedType.HYGIENE: 60.0}
    },
    FunActivityType.AUDIOBOOK_LISTENING: {
        "fun_gain": 35.0,
        "duration_hours": 1.0,
        "cognitive_effort": 0.25
    },
    FunActivityType.INDOOR_PICNIC: {
        "fun_gain": 47.0,
        "duration_hours": 1.0,
        "cognitive_effort": 0.2,
        "effects_on_needs": {NeedType.HUNGER: -30.0}
    },
    FunActivityType.CHEESE_TASTING: {
        "fun_gain": 42.0,
        "duration_hours": 0.5,
        "skill_to_practice": SkillType.CULINARY_KNOWLEDGE,
        "skill_xp_gain": 45.0,
        "cognitive_effort": 0.3
    },
    FunActivityType.HOME_IMPROVEMENT: {
        "fun_gain": 53.0,
        "duration_hours": 2.5,
        "required_object_types": (ObjectType.TOOLBOX,),
        "skill_to_practice": SkillType.HANDINESS,
        "skill_xp_gain": 67.0,
        "cognitive_effort": 0.8,
        "effects_on_needs": {NeedType.ENERGY: -50.0}
    },
    FunActivityType.INDOOR_CAMPING: {
        "fun_gain": 60.0,
        "duration_hours": 3.0,
        "cognitive_effort": 0.3
    },
    FunActivityType.TEA_CEREMONY: {
        "fun_gain": 43.0,
        "duration_hours": 0.8,
        "skill_to_practice": SkillType.TEA_CEREMONY,
        "skill_xp_gain": 47.0,
        "cognitive_effort": 0.4,
        "effects_on_needs": {NeedType.STRESS: -25.0}
    },
    FunActivityType.HOME_KARAOKE: {
        "fun_gain": 65.0,
        "duration_hours": 1.0,
        "required_object_types": (ObjectType.KARAOKE_MACHINE,),
        "skill_to_practice": SkillType.SINGING,
        "skill_xp_gain": 50.0,
        "cognitive_effort": 0.3,
        "is_noisy": True
    },
    FunActivityType.BATH_BOOK_READING: {
        "fun_gain": 37.0,
        "duration_hours": 0.6,
        "skill_to_practice": SkillType.READING,
        "skill_xp_gain": 40.0,
        "cognitive_effort": 0.4,
        "effects_on_needs": {NeedType.HYGIENE: 40.0}
    },
    FunActivityType.HOME_ESCAPE_ROOM: {
        "fun_gain": 70.0,
        "duration_hours": 1.5,
        "skill_to_practice": SkillType.PROBLEM_SOLVING,
        "skill_xp_gain": 60.0,
        "cognitive_effort": 0.85
    },
    FunActivityType.BALLOON_ART: {
        "fun_gain": 45.0,
        "duration_hours": 0.7,
        "skill_to_practice": SkillType.BALLOON_TWISTING,
        "skill_xp_gain": 42.0,
        "cognitive_effort": 0.5
    },
    FunActivityType.VIRTUAL_TRAVEL: {
        "fun_gain": 40.0,
        "duration_hours": 1.2,
        "required_object_types": (ObjectType.VR_HEADSET,),
        "cognitive_effort": 0.3
    },

    # ================= ATTIVITÀ SOCIALI =================
    FunActivityType.GO_TO_BAR: {
        "fun_gain": 70.0,
        "duration_hours": 2.5,
        "cognitive_effort": 0.3,
        "effects_on_needs": {
            NeedType.HUNGER: -45.0,
            NeedType.THIRST: -60.0,
            NeedType.ENERGY: -35.0
        }
    },
    FunActivityType.COMEDY_CLUB: {
        "fun_gain": 75.0,
        "duration_hours": 1.5,
        "cognitive_effort": 0.2
    },
    FunActivityType.ART_GALLERY_TOUR: {
        "fun_gain": 60.0,
        "duration_hours": 2.0,
        "skill_to_practice": SkillType.ART_KNOWLEDGE,
        "skill_xp_gain": 50.0,
        "cognitive_effort": 0.4
    },
    FunActivityType.THEATER_PERFORMANCE: {
        "fun_gain": 80.0,
        "duration_hours": 2.5,
        "cognitive_effort": 0.3
    },
    FunActivityType.KARAOKE_NIGHT: {
        "fun_gain": 85.0,
        "duration_hours": 2.0,
        "skill_to_practice": SkillType.SINGING,
        "skill_xp_gain": 45.0,
        "cognitive_effort": 0.3,
        "is_noisy": True
    },
    FunActivityType.FOOD_TRUCK_FESTIVAL: {
        "fun_gain": 75.0,
        "duration_hours": 2.0,
        "cognitive_effort": 0.25,
        "effects_on_needs": {NeedType.HUNGER: -60.0}
    },
    FunActivityType.STREET_PERFORMANCE: {
        "fun_gain": 55.0,
        "duration_hours": 1.0,
        "cognitive_effort": 0.35,
        "is_outdoors": True
    },
    FunActivityType.PUB_QUIZ: {
        "fun_gain": 68.0,
        "duration_hours": 1.5,
        "skill_to_practice": SkillType.TRIVIA,
        "skill_xp_gain": 60.0,
        "cognitive_effort": 0.6
    },
    FunActivityType.DANCE_CLUB: {
        "fun_gain": 90.0,
        "duration_hours": 3.0,
        "skill_to_practice": SkillType.DANCING,
        "skill_xp_gain": 50.0,
        "cognitive_effort": 0.2,
        "is_noisy": True,
        "effects_on_needs": {NeedType.ENERGY: -70.0}
    },
    FunActivityType.BOARD_GAME_CAFE: {
        "fun_gain": 63.0,
        "duration_hours": 2.0,
        "skill_to_practice": SkillType.STRATEGY,
        "skill_xp_gain": 55.0,
        "cognitive_effort": 0.7,
        "effects_on_needs": {NeedType.HUNGER: -30.0}
    },
    FunActivityType.FARMERS_MARKET: {
        "fun_gain": 50.0,
        "duration_hours": 1.5,
        "cognitive_effort": 0.2,
        "is_outdoors": True
    },
    FunActivityType.POETRY_SLAM: {
        "fun_gain": 58.0,
        "duration_hours": 1.5,
        "skill_to_practice": SkillType.POETRY,
        "skill_xp_gain": 53.0,
        "cognitive_effort": 0.5
    },
    FunActivityType.CITY_PHOTO_WALK: {
        "fun_gain": 60.0,
        "duration_hours": 2.0,
        "required_object_types": (ObjectType.CAMERA,),
        "skill_to_practice": SkillType.PHOTOGRAPHY,
        "skill_xp_gain": 65.0,
        "cognitive_effort": 0.6,
        "is_outdoors": True
    },
    FunActivityType.ARCADE_NIGHT: {
        "fun_gain": 80.0,
        "duration_hours": 2.0,
        "skill_to_practice": SkillType.GAMING,
        "skill_xp_gain": 45.0,
        "cognitive_effort": 0.4
    },
    FunActivityType.LIVE_MUSIC_VENUE: {
        "fun_gain": 75.0,
        "duration_hours": 2.0,
        "cognitive_effort": 0.2,
        "is_noisy": True
    },
    FunActivityType.SPEED_DATING: {
        "fun_gain": 70.0,
        "duration_hours": 1.5,
        "cognitive_effort": 0.6
    },
    FunActivityType.THEME_PARK: {
        "fun_gain": 95.0,
        "duration_hours": 4.0,
        "cognitive_effort": 0.3,
        "is_outdoors": True,
        "effects_on_needs": {NeedType.ENERGY: -90.0}
    },
    FunActivityType.STREET_FOOD_TOUR: {
        "fun_gain": 82.0,
        "duration_hours": 2.5,
        "cognitive_effort": 0.25,
        "is_outdoors": True,
        "effects_on_needs": {NeedType.HUNGER: -70.0}
    },
    FunActivityType.CITY_SCAVENGER_HUNT: {
        "fun_gain": 85.0,
        "duration_hours": 3.0,
        "skill_to_practice": SkillType.PROBLEM_SOLVING,
        "skill_xp_gain": 70.0,
        "cognitive_effort": 0.8,
        "is_outdoors": True
    },
    FunActivityType.FESTIVAL_ATTENDANCE: {
        "fun_gain": 90.0,
        "duration_hours": 4.0,
        "cognitive_effort": 0.2,
        "is_outdoors": True
    },
    FunActivityType.IMPROV_WORKSHOP: {
        "fun_gain": 72.0,
        "duration_hours": 2.0,
        "skill_to_practice": SkillType.IMPROV,
        "skill_xp_gain": 75.0,
        "cognitive_effort": 0.75
    },
    FunActivityType.MURDER_MYSTERY_DINNER: {
        "fun_gain": 85.0,
        "duration_hours": 3.0,
        "skill_to_practice": SkillType.ROLEPLAYING,
        "skill_xp_gain": 65.0,
        "cognitive_effort": 0.7
    },
    FunActivityType.ESCAPE_ROOM_CHALLENGE: {
        "fun_gain": 88.0,
        "duration_hours": 1.5,
        "skill_to_practice": SkillType.PROBLEM_SOLVING,
        "skill_xp_gain": 80.0,
        "cognitive_effort": 0.9
    },
    FunActivityType.CITY_BIKE_TOUR: {
        "fun_gain": 70.0,
        "duration_hours": 2.0,
        "required_object_types": (ObjectType.BICYCLE,),
        "skill_to_practice": SkillType.CYCLING,
        "skill_xp_gain": 60.0,
        "cognitive_effort": 0.4,
        "is_outdoors": True,
        "effects_on_needs": {NeedType.ENERGY: -65.0}
    },
    FunActivityType.STREET_ART_TOUR: {
        "fun_gain": 60.0,
        "duration_hours": 1.8,
        "skill_to_practice": SkillType.ART_KNOWLEDGE,
        "skill_xp_gain": 55.0,
        "cognitive_effort": 0.35,
        "is_outdoors": True
    },
    FunActivityType.FOOD_COURT_SAMPLING: {
        "fun_gain": 65.0,
        "duration_hours": 1.5,
        "cognitive_effort": 0.2,
        "effects_on_needs": {NeedType.HUNGER: -55.0}
    },
    FunActivityType.NIGHT_MARKET: {
        "fun_gain": 72.0,
        "duration_hours": 2.0,
        "cognitive_effort": 0.25,
        "is_outdoors": True
    },
    FunActivityType.ROOFTOP_BAR: {
        "fun_gain": 75.0,
        "duration_hours": 2.0,
        "cognitive_effort": 0.2,
        "is_outdoors": True
    },
    FunActivityType.BOAT_PARTY: {
        "fun_gain": 95.0,
        "duration_hours": 4.0,
        "cognitive_effort": 0.15,
        "is_outdoors": True
    },
    FunActivityType.LISTEN_TO_LIVE_JAZZ: {
        "fun_gain": 70.0,
        "duration_hours": 2.0,
        "cognitive_effort": 0.2,
        "is_noisy": True
    },
    FunActivityType.PERFORM_JAZZ: {
        "fun_gain": 80.0,
        "duration_hours": 1.5,
        "required_object_types": (ObjectType.MUSICAL_INSTRUMENT,),
        "skill_to_practice": SkillType.MUSICIANSHIP,
        "skill_xp_gain": 70.0,
        "cognitive_effort": 0.6,
        "is_noisy": True
    },
    FunActivityType.PERFORM_ON_STREET: {
        "fun_gain": 60.0,
        "duration_hours": 1.0,
        "skill_to_practice": SkillType.PERFORMING,
        "skill_xp_gain": 65.0,
        "cognitive_effort": 0.5,
        "is_outdoors": True,
        "is_noisy": True
    }, # money_gain: 50.0},
    FunActivityType.JUMP_ON_BENCH: {
        "fun_gain": 35.0,
        "duration_hours": 0.1,
        "cognitive_effort": 0.05,
        "is_outdoors": True
    },

    # ================= ATTIVITÀ ROMANTICHE =================
    FunActivityType.SUNSET_PICNIC: {
        "fun_gain": 85.0,
        "duration_hours": 2.0,
        "cognitive_effort": 0.1,
        "is_outdoors": True,
        "effects_on_needs": {NeedType.HUNGER: -40.0}
    },
    FunActivityType.COUPLES_MASSAGE: {
        "fun_gain": 85.0,
        "duration_hours": 1.2,
        "skill_to_practice": SkillType.MASSAGE,
        "skill_xp_gain": 65.0,
        "cognitive_effort": 0.4,
        "effects_on_needs": {NeedType.STRESS: -50.0}
    },
    FunActivityType.CANDLELIGHT_DINNER: {
        "fun_gain": 90.0,
        "duration_hours": 1.5,
        "cognitive_effort": 0.2,
        "effects_on_needs": {NeedType.HUNGER: -60.0}
    },
    FunActivityType.STARGAZING_DATE: {
        "fun_gain": 75.0,
        "duration_hours": 1.5,
        "cognitive_effort": 0.15,
        "is_outdoors": True
    },
    FunActivityType.SENSUAL_DANCE: {
        "fun_gain": 95.0,
        "duration_hours": 1.0,
        "skill_to_practice": SkillType.DANCING,
        "skill_xp_gain": 70.0,
        "cognitive_effort": 0.4,
        "effects_on_needs": {NeedType.ENERGY: -40.0}
    },
    FunActivityType.LOVE_LETTER_WRITING: {
        "fun_gain": 70.0,
        "duration_hours": 0.8,
        "skill_to_practice": SkillType.WRITING,
        "skill_xp_gain": 50.0,
        "cognitive_effort": 0.6
    },
    FunActivityType.HOT_SPRINGS_VISIT: {
        "fun_gain": 88.0,
        "duration_hours": 2.0,
        "cognitive_effort": 0.1,
        "is_outdoors": True,
        "effects_on_needs": {NeedType.HYGIENE: 70.0}
    },
    FunActivityType.TANGO_LESSONS: {
        "fun_gain": 80.0,
        "duration_hours": 1.2,
        "skill_to_practice": SkillType.DANCING,
        "skill_xp_gain": 70.0,
        "cognitive_effort": 0.5
    },
    FunActivityType.CHOCOLATE_TASTING: {
        "fun_gain": 75.0,
        "duration_hours": 0.7,
        "cognitive_effort": 0.25
    },
    FunActivityType.PRIVATE_WINE_CELLAR: {
        "fun_gain": 78.0,
        "duration_hours": 1.5,
        "skill_to_practice": SkillType.WINE_KNOWLEDGE,
        "skill_xp_gain": 60.0,
        "cognitive_effort": 0.3
    },
    FunActivityType.COUPLES_ART_CLASS: {
        "fun_gain": 85.0,
        "duration_hours": 2.0,
        "skill_to_practice": SkillType.PAINTING,
        "skill_xp_gain": 55.0,
        "cognitive_effort": 0.6
    },
    FunActivityType.MOONLIGHT_SWIM: {
        "fun_gain": 92.0,
        "duration_hours": 1.0,
        "cognitive_effort": 0.2,
        "is_outdoors": True,
        "effects_on_needs": {NeedType.HYGIENE: 50.0}
    },
    FunActivityType.AROMATHERAPY_SESSION: {
        "fun_gain": 70.0,
        "duration_hours": 0.8,
        "cognitive_effort": 0.15,
        "effects_on_needs": {NeedType.STRESS: -45.0}
    },
    FunActivityType.DOUBLE_MASSAGE: {
        "fun_gain": 82.0,
        "duration_hours": 1.0,
        "skill_to_practice": SkillType.MASSAGE,
        "skill_xp_gain": 53.0,
        "cognitive_effort": 0.35,
        "effects_on_needs": {NeedType.STRESS: -55.0}
    },
    FunActivityType.PRIVATE_DANCE: {
        "fun_gain": 98.0,
        "duration_hours": 1.2,
        "skill_to_practice": SkillType.DANCING,
        "skill_xp_gain": 65.0,
        "cognitive_effort": 0.4
    },
    FunActivityType.KISSING_CONTEST: {
        "fun_gain": 80.0,
        "duration_hours": 0.5,
        "cognitive_effort": 0.1
    },
    FunActivityType.ROLEPLAYING_GAME: {
        "fun_gain": 75.0,
        "duration_hours": 2.5,
        "skill_to_practice": SkillType.ROLEPLAYING,
        "skill_xp_gain": 75.0,
        "cognitive_effort": 0.8
    },
    FunActivityType.SILK_ROBES_EVENING: {
        "fun_gain": 85.0,
        "duration_hours": 1.5,
        "cognitive_effort": 0.2
    },
    FunActivityType.EROTIC_STORYTELLING: {
        "fun_gain": 78.0,
        "duration_hours": 1.0,
        "skill_to_practice": SkillType.STORYTELLING,
        "skill_xp_gain": 60.0,
        "cognitive_effort": 0.6
    },
    FunActivityType.SCENT_CREATION: {
        "fun_gain": 67.0,
        "duration_hours": 1.2,
        "skill_to_practice": SkillType.PERFUMERY,
        "skill_xp_gain": 63.0,
        "cognitive_effort": 0.65
    },
    FunActivityType.FANTASY_ROLEPLAY: {
        "fun_gain": 90.0,
        "duration_hours": 2.0,
        "skill_to_practice": SkillType.ROLEPLAYING,
        "skill_xp_gain": 70.0,
        "cognitive_effort": 0.7
    },
    FunActivityType.MASSAGE_OIL_MAKING: {
        "fun_gain": 63.0,
        "duration_hours": 1.0,
        "skill_to_practice": SkillType.MASSAGE,
        "skill_xp_gain": 57.0,
        "cognitive_effort": 0.55
    },
    FunActivityType.INTIMATE_GAME_NIGHT: {
        "fun_gain": 82.0,
        "duration_hours": 1.8,
        "cognitive_effort": 0.4
    },
    FunActivityType.SENSUAL_FEEDING: {
        "fun_gain": 75.0,
        "duration_hours": 0.7,
        "cognitive_effort": 0.2
    },
    FunActivityType.TANTRIC_BREATHWORK: {
        "fun_gain": 65.0,
        "duration_hours": 0.8,
        "skill_to_practice": SkillType.MEDITATION,
        "skill_xp_gain": 50.0,
        "cognitive_effort": 0.3,
        "effects_on_needs": {NeedType.STRESS: -60.0}
    },
    FunActivityType.LINGERIE_SHOPPING: {
        "fun_gain": 70.0,
        "duration_hours": 1.5,
        "cognitive_effort": 0.25
    }, # money_gain: 120.0},
    FunActivityType.LOVE_POETRY_READING: {
        "fun_gain": 68.0,
        "duration_hours": 0.6,
        "skill_to_practice": SkillType.POETRY,
        "skill_xp_gain": 47.0,
        "cognitive_effort": 0.5
    },
    FunActivityType.COUPLES_YOGA: {
        "fun_gain": 73.0,
        "duration_hours": 1.0,
        "skill_to_practice": SkillType.YOGA,
        "skill_xp_gain": 55.0,
        "cognitive_effort": 0.35,
        "effects_on_needs": {NeedType.STRESS: -50.0}
    },
    FunActivityType.SENSUAL_COOKING: {
        "fun_gain": 80.0,
        "duration_hours": 1.5,
        "skill_to_practice": SkillType.COOKING,
        "skill_xp_gain": 60.0,
        "cognitive_effort": 0.6
    },
    FunActivityType.AFTERGLOW_CUDDLING: {
        "fun_gain": 60.0,
        "duration_hours": 0.5,
        "cognitive_effort": 0.05
    },
    FunActivityType.PRIVATE_CONCERT: {
        "fun_gain": 88.0,
        "duration_hours": 1.5,
        "cognitive_effort": 0.2,
        "is_noisy": True
    },
    FunActivityType.EROTIC_PHOTOGRAPHY: {
        "fun_gain": 75.0,
        "duration_hours": 1.2,
        "required_object_types": (ObjectType.CAMERA,),
        "skill_to_practice": SkillType.PHOTOGRAPHY,
        "skill_xp_gain": 65.0,
        "cognitive_effort": 0.6
    }
}

ACTIVITIES_WITHOUT_OBJECTS = {
    # Attività fisiche
    FunActivityType.DANCE,
    FunActivityType.JOG_IN_PLACE,
    FunActivityType.SING,
    FunActivityType.JUMP_ON_BENCH,
    
    # Attività intellettuali
    FunActivityType.DAYDREAM,
    FunActivityType.PRACTICE_PUBLIC_SPEAKING,
    FunActivityType.WATCH_CLOUDS,
    FunActivityType.MEDITATE,
    FunActivityType.PEOPLE_WATCH,
    FunActivityType.STUDY_PHILOSOPHY,
    FunActivityType.LEARN_LANGUAGE,
    FunActivityType.JOURNALING,
    FunActivityType.SUDOKU,
    FunActivityType.TAROT_READING,
    FunActivityType.MINDFULNESS_PRACTICE,
    FunActivityType.STARGAZING,
    FunActivityType.BOTANY_STUDY,
    FunActivityType.HISTORY_DOCUMENTARY,
    FunActivityType.MAP_STUDY,
    FunActivityType.MEMORY_TRAINING,
    FunActivityType.PHILOSOPHICAL_DEBATE,
    FunActivityType.ECONOMICS_ANALYSIS,
    FunActivityType.PSYCHOLOGY_STUDY,
    FunActivityType.ARCHITECTURE_STUDY,
    FunActivityType.CRYPTOGRAPHY,
    FunActivityType.STRATEGY_GAME_SOLO,
    FunActivityType.MYTHOLOGY_STUDY,
    FunActivityType.POETRY_ANALYSIS,
    FunActivityType.ASTROLOGY_STUDY,
    
    # Attività all'aperto
    FunActivityType.EXPLORE_NEIGHBORHOOD,
    FunActivityType.FOREST_BATHING,
    FunActivityType.BOTANICAL_FORAGING,
    FunActivityType.STONE_SKIPPING,
    FunActivityType.SNOWBALL_FIGHT,
    
    # Attività domestiche
    FunActivityType.WATCH_TV,
    FunActivityType.PODCAST_LISTENING,
    FunActivityType.AQUARIUM_WATCHING,
    FunActivityType.INDOOR_PICNIC,
    FunActivityType.INDOOR_CAMPING,
    FunActivityType.BATH_BOOK_READING,
    FunActivityType.DRINK_COFFEE,
    
    # Attività sociali
    FunActivityType.GO_TO_BAR,
    FunActivityType.COMEDY_CLUB,
    FunActivityType.THEATER_PERFORMANCE,
    FunActivityType.FOOD_TRUCK_FESTIVAL,
    FunActivityType.STREET_PERFORMANCE,
    FunActivityType.PUB_QUIZ,
    FunActivityType.DANCE_CLUB,
    FunActivityType.FARMERS_MARKET,
    FunActivityType.POETRY_SLAM,
    FunActivityType.ARCADE_NIGHT,
    FunActivityType.LIVE_MUSIC_VENUE,
    FunActivityType.SPEED_DATING,
    FunActivityType.THEME_PARK,
    FunActivityType.STREET_FOOD_TOUR,
    FunActivityType.FESTIVAL_ATTENDANCE,
    FunActivityType.IMPROV_WORKSHOP,
    FunActivityType.MURDER_MYSTERY_DINNER,
    FunActivityType.NIGHT_MARKET,
    FunActivityType.ROOFTOP_BAR,
    FunActivityType.BOAT_PARTY,
    FunActivityType.LISTEN_TO_LIVE_JAZZ,
    FunActivityType.PERFORM_ON_STREET,
    
    # Attività romantiche
    FunActivityType.SUNSET_PICNIC,
    FunActivityType.COUPLES_MASSAGE,
    FunActivityType.CANDLELIGHT_DINNER,
    FunActivityType.STARGAZING_DATE,
    FunActivityType.SENSUAL_DANCE,
    FunActivityType.LOVE_LETTER_WRITING,
    FunActivityType.HOT_SPRINGS_VISIT,
    FunActivityType.TANGO_LESSONS,
    FunActivityType.CHOCOLATE_TASTING,
    FunActivityType.PRIVATE_WINE_CELLAR,
    FunActivityType.COUPLES_ART_CLASS,
    FunActivityType.MOONLIGHT_SWIM,
    FunActivityType.AROMATHERAPY_SESSION,
    FunActivityType.DOUBLE_MASSAGE,
    FunActivityType.PRIVATE_DANCE,
    FunActivityType.KISSING_CONTEST,
    FunActivityType.ROLEPLAYING_GAME,
    FunActivityType.SILK_ROBES_EVENING,
    FunActivityType.EROTIC_STORYTELLING,
    FunActivityType.SCENT_CREATION,
    FunActivityType.FANTASY_ROLEPLAY,
    FunActivityType.MASSAGE_OIL_MAKING,
    FunActivityType.INTIMATE_GAME_NIGHT,
    FunActivityType.SENSUAL_FEEDING,
    FunActivityType.TANTRIC_BREATHWORK,
    FunActivityType.LINGERIE_SHOPPING,
    FunActivityType.LOVE_POETRY_READING,
    FunActivityType.COUPLES_YOGA,
    FunActivityType.SENSUAL_COOKING,
    FunActivityType.AFTERGLOW_CUDDLING,
    FunActivityType.PRIVATE_CONCERT,
    
    # Attività creative
    FunActivityType.CALLIGRAPHY,
    FunActivityType.SONGWRITING,
    FunActivityType.POETRY,
    FunActivityType.BEADWORK,
    FunActivityType.ORIGAMI,
    FunActivityType.BOTANICAL_ILLUSTRATION,
    FunActivityType.PUPPET_MAKING,
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

SIMPLE_NEED_ACTION_CONFIGS = {
    NeedType.HUNGER: {
        # Sostituisci la classe con il suo percorso come stringa
        "action_class_path": "core.modules.actions.hunger_actions.EatAction",
        "required_objects": (ObjectType.REFRIGERATOR,),
        "duration_hours": 0.75, # Cucinare richiede un po' più di tempo
        "hunger_gain": 75.0,
        # Non ci sono "guadagni" diretti, perché vengono dati da EatAction
    },
    NeedType.THIRST: {
        "action_class_path": "core.modules.actions.thirst_actions.DrinkAction",
        "required_objects": (ObjectType.SINK,),
        "duration_hours": 0.2,
        "thirst_gain": 60.0, # Parametro specifico per DrinkAction
    },
    NeedType.ENERGY: {
        "action_class_path": "core.modules.actions.energy_actions.SleepAction",
        "required_objects": (ObjectType.BED,),
        "duration_hours": 8.0,
        "energy_gain_per_hour": 12.5, # 100 punti in 8 ore
        "validation_threshold": 60.0, # L'NPC non andrà a dormire se ha più del 60% di energia
    },
    NeedType.BLADDER: {
        "action_class_path": "core.modules.actions.bathroom_actions.UseBathroomAction",
        "required_objects": (ObjectType.TOILET,),
        "duration_hours": 0.25,
        "bladder_gain": 100.0,
        "hygiene_gain": 15.0, # Esempio di effetto multiplo
    },
    NeedType.INTIMACY: {
        # Non serve 'action_class' qui, perché il discoverer la conosce già.
        "duration_hours": 1.5,
        "initiator_intimacy_gain": 60.0,
        "target_intimacy_gain": 50.0,
        "relationship_score_gain": 8,
        "required_relationship_types": {RelationshipType.ROMANTIC_PARTNER, RelationshipType.SPOUSE},
        "min_rel_score": 30,
        "initiator_desire_threshold": 50.0, # L'iniziatore deve avere bisogno < 50
    },
}
