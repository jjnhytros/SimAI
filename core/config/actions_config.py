# core/config/actions_config.py
"""
Configurazioni di default per le azioni degli NPC.
"""

from core.enums import (
    FunActivityType, ObjectType, SkillType, SocialInteractionType,
    RelationshipType, NeedType,
)

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
    # Creative
    FunActivityType.PAINT: {"fun_gain": 45.0, "duration_hours": 2.0, "required_object_types": (ObjectType.EASEL,), "skill_to_practice": SkillType.PAINTING, "skill_xp_gain": 60.0, "cognitive_effort": 0.8},
    FunActivityType.PLAY_GUITAR: {"fun_gain": 40.0, "duration_hours": 1.0, "required_object_types": (ObjectType.GUITAR,), "skill_to_practice": SkillType.GUITAR, "skill_xp_gain": 50.0, "cognitive_effort": 0.7},
    FunActivityType.PLAY_PIANO: {"fun_gain": 40.0, "duration_hours": 1.0, "required_object_types": (ObjectType.PIANO,), "skill_to_practice": SkillType.PIANO, "skill_xp_gain": 50.0, "cognitive_effort": 0.7},
    FunActivityType.PLAY_VIOLIN: {"fun_gain": 40.0, "duration_hours": 1.0, "required_object_types": (ObjectType.VIOLIN,), "skill_to_practice": SkillType.VIOLIN, "skill_xp_gain": 55.0, "cognitive_effort": 0.8},
    FunActivityType.SING: {"fun_gain": 25.0, "duration_hours": 0.5, "skill_to_practice": SkillType.SINGING, "skill_xp_gain": 30.0, "cognitive_effort": 0.5},
    FunActivityType.WRITE_BOOK_FOR_FUN: {"fun_gain": 35.0, "duration_hours": 2.5, "required_object_types": (ObjectType.COMPUTER, ObjectType.LAPTOP), "skill_to_practice": SkillType.WRITING_CREATIVE, "skill_xp_gain": 70.0, "cognitive_effort": 0.9},
    FunActivityType.DJ_MIXING: {"fun_gain": 40.0, "duration_hours": 2.0, "required_object_types": (ObjectType.DJ_TURNTABLE,), "skill_to_practice": SkillType.DJ_MIXING, "skill_xp_gain": 45.0, "cognitive_effort": 0.6},
    FunActivityType.PHOTOGRAPHY: {"fun_gain": 30.0, "duration_hours": 2.0, "is_outdoors": True, "skill_to_practice": SkillType.PHOTOGRAPHY, "skill_xp_gain": 35.0, "cognitive_effort": 0.5},
    FunActivityType.KNITTING: {"fun_gain": 25.0, "duration_hours": 1.5, "skill_to_practice": SkillType.KNITTING, "skill_xp_gain": 20.0, "cognitive_effort": 0.3},
    FunActivityType.POTTERY: {"fun_gain": 35.0, "duration_hours": 2.0, "required_object_types": (ObjectType.POTTERY_WHEEL,), "skill_to_practice": SkillType.POTTERY, "skill_xp_gain": 40.0, "cognitive_effort": 0.6},
    FunActivityType.WOODWORKING: {"fun_gain": 30.0, "duration_hours": 3.0, "required_object_types": (ObjectType.WORKBENCH,), "skill_to_practice": SkillType.WOODWORKING, "skill_xp_gain": 40.0, "cognitive_effort": 0.7},

    # Intellettuali / tranquille
    FunActivityType.READ_BOOK_FOR_FUN: {"fun_gain": 35.0, "duration_hours": 1.5, "required_object_types": (ObjectType.BOOKSHELF, ObjectType.BOOK), "cognitive_effort": 0.2},
    FunActivityType.PLAY_CHESS: {"fun_gain": 30.0, "duration_hours": 1.0, "required_object_types": (ObjectType.CHESS_TABLE,), "skill_to_practice": SkillType.LOGIC, "skill_xp_gain": 50.0, "cognitive_effort": 0.8},
    FunActivityType.DO_CROSSWORD_PUZZLE: {"fun_gain": 20.0, "duration_hours": 1.0, "cognitive_effort": 0.5},
    FunActivityType.RESEARCH_INTEREST_ONLINE: {"fun_gain": 25.0, "duration_hours": 1.0, "required_object_types": (ObjectType.COMPUTER, ObjectType.LAPTOP), "skill_to_practice": SkillType.RESEARCH_DEBATE, "skill_xp_gain": 30.0, "cognitive_effort": 0.6},
    FunActivityType.DAYDREAM: {"fun_gain": 15.0, "duration_hours": 0.5, "cognitive_effort": 0.1},
    FunActivityType.WATCH_CLOUDS: {"fun_gain": 15.0, "duration_hours": 0.75, "is_outdoors": True, "cognitive_effort": 0.1},
    FunActivityType.PEOPLE_WATCH: {"fun_gain": 20.0, "duration_hours": 1.0, "cognitive_effort": 0.2},
    FunActivityType.MEDITATE: {"fun_gain": 10.0, "duration_hours": 0.5, "skill_to_practice": SkillType.WELLNESS, "skill_xp_gain": 25.0, "cognitive_effort": 0.2},

    # All'aperto / Fisiche
    FunActivityType.GO_FOR_A_JOG: {"fun_gain": 40.0, "duration_hours": 1.0, "is_outdoors": True, "skill_to_practice": SkillType.FITNESS, "skill_xp_gain": 40.0, "cognitive_effort": 0.6},
    FunActivityType.JOG_IN_PLACE: {"fun_gain": 25.0, "duration_hours": 0.5, "skill_to_practice": SkillType.FITNESS, "skill_xp_gain": 20.0, "cognitive_effort": 0.5},
    FunActivityType.GO_HIKING: {"fun_gain": 50.0, "duration_hours": 3.0, "is_outdoors": True, "skill_to_practice": SkillType.FITNESS, "skill_xp_gain": 50.0, "cognitive_effort": 0.6},
    FunActivityType.SWIMMING: {"fun_gain": 40.0, "duration_hours": 1.0, "is_outdoors": True, "skill_to_practice": SkillType.FITNESS, "skill_xp_gain": 45.0, "cognitive_effort": 0.7},
    FunActivityType.GARDENING: {"fun_gain": 30.0, "duration_hours": 2.0, "is_outdoors": True, "skill_to_practice": SkillType.GARDENING, "skill_xp_gain": 30.0, "cognitive_effort": 0.4},
    FunActivityType.FISHING: {"fun_gain": 25.0, "duration_hours": 2.5, "is_outdoors": True, "skill_to_practice": SkillType.FISHING, "skill_xp_gain": 25.0, "cognitive_effort": 0.3},
    FunActivityType.PLAY_SPORTS_CASUAL: {"fun_gain": 45.0, "duration_hours": 1.5, "is_outdoors": True, "skill_to_practice": SkillType.FITNESS, "skill_xp_gain": 35.0, "cognitive_effort": 0.7},
    FunActivityType.EXPLORE_NEIGHBORHOOD: {"fun_gain": 30.0, "duration_hours": 2.0, "is_outdoors": True, "cognitive_effort": 0.4},

    # Domestiche / Media
    FunActivityType.WATCH_TV: {"fun_gain": 30.0, "duration_hours": 2.0, "required_object_types": (ObjectType.TV,), "cognitive_effort": 0.1},
    FunActivityType.WATCH_MOVIE_AT_HOME: {"fun_gain": 40.0, "duration_hours": 2.5, "required_object_types": (ObjectType.TV,), "cognitive_effort": 0.1},
    FunActivityType.PLAY_VIDEO_GAMES: {"fun_gain": 45.0, "duration_hours": 2.0, "required_object_types": (ObjectType.COMPUTER, ObjectType.LAPTOP, ObjectType.GAME_CONSOLE), "skill_to_practice": SkillType.GAMING, "skill_xp_gain": 20.0, "cognitive_effort": 0.6},
    FunActivityType.LISTEN_TO_MUSIC: {"fun_gain": 20.0, "duration_hours": 1.0, "required_object_types": (ObjectType.STEREO, ObjectType.COMPUTER), "cognitive_effort": 0.1},
    FunActivityType.BROWSE_SOCIAL_MEDIA: {"fun_gain": 25.0, "duration_hours": 1.0, "required_object_types": (ObjectType.COMPUTER, ObjectType.LAPTOP, ObjectType.PHONE), "skill_to_practice": SkillType.SOCIAL_MEDIA, "skill_xp_gain": 10.0, "cognitive_effort": 0.3},

    # Sociali / in Città
    FunActivityType.GO_TO_BAR: {"fun_gain": 35.0, "duration_hours": 2.0, "is_noisy": True, "cognitive_effort": 0.4},
    FunActivityType.DANCE: {"fun_gain": 30.0, "duration_hours": 1.5, "skill_to_practice": SkillType.DANCING, "skill_xp_gain": 25.0, "cognitive_effort": 0.5},
    FunActivityType.PLAY_BOARD_GAMES: {"fun_gain": 35.0, "duration_hours": 2.0, "skill_to_practice": SkillType.LOGIC, "skill_xp_gain": 15.0, "cognitive_effort": 0.6},
    FunActivityType.WINDOW_SHOPPING: {"fun_gain": 15.0, "duration_hours": 1.0, "is_outdoors": True, "cognitive_effort": 0.2},
    FunActivityType.WATCH_MOVIE_AT_CINEMA: {"fun_gain": 50.0, "duration_hours": 3.0, "cognitive_effort": 0.1},
    FunActivityType.TELL_STORIES: {"fun_gain": 20.0, "duration_hours": 0.5, "skill_to_practice": SkillType.CHARISMA, "skill_xp_gain": 10.0, "cognitive_effort": 0.4},
    FunActivityType.PRACTICE_PUBLIC_SPEAKING: {"fun_gain": 5.0, "duration_hours": 0.75, "skill_to_practice": SkillType.CHARISMA, "skill_xp_gain": 30.0, "cognitive_effort": 0.9},
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
