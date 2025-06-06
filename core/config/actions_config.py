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
USEBATHROOM_TOILET_DURATION_HOURS = 0.15
USEBATHROOM_TOILET_BLADDER_RELIEF = 100.0
USEBATHROOM_TOILET_HYGIENE_GAIN = 15.0
USEBATHROOM_SHOWER_DURATION_HOURS = 0.4
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
HAVEFUN_DEFAULT_FUN_GAIN = 25.0
HAVEFUN_DEFAULT_DURATION_HOURS = 1.0

HAVEFUN_ACTIVITY_CONFIGS = {
    FunActivityType.WATCH_TV: {
        "fun_gain": 30.0, "duration_hours": 2.0,
        "required_object_types": (ObjectType.TV,),
    },
    FunActivityType.READ_BOOK_FOR_FUN: {
        "fun_gain": 35.0, "duration_hours": 1.5,
        "required_object_types": (ObjectType.BOOKSHELF, ObjectType.BOOK),
    },
    FunActivityType.DAYDREAM: {
        "fun_gain": 15.0, "duration_hours": 0.5,
    },
    FunActivityType.PLAY_GUITAR: {
        "fun_gain": 40.0, "duration_hours": 1.0,
        "required_object_types": (ObjectType.GUITAR,),
        "skill_to_practice": SkillType.GUITAR,
        "skill_xp_gain": 50.0,
    },
    # ... definisci una entry per ogni FunActivityType ...
}

# --- SocializeAction ---
SOCIALIZE_DEFAULT_DURATION_TICKS = 40 # Usiamo tick qui perché le interazioni possono essere brevi
SOCIALIZE_DEFAULT_INITIATOR_GAIN = 10.0
SOCIALIZE_DEFAULT_TARGET_GAIN = 10.0
SOCIALIZE_DEFAULT_REL_CHANGE = 1

SOCIALIZE_INTERACTION_CONFIGS = {
    SocialInteractionType.CHAT_CASUAL: {
        "duration_ticks": 40, "initiator_gain": 15.0, "target_gain": 15.0, "rel_change": 2,
    },
    SocialInteractionType.DEEP_CONVERSATION: {
        "duration_ticks": 120, "initiator_gain": 30.0, "target_gain": 30.0, "rel_change": 5,
        "new_rel_type_on_success": RelationshipType.FRIEND_REGULAR, "min_rel_score_req": 15
    },
    SocialInteractionType.TELL_JOKE: {
        "duration_ticks": 15, "initiator_gain": 10.0, "target_gain": 15.0, "rel_change": 2,
        "effects_on_target": {NeedType.FUN: 10.0}
    },
    SocialInteractionType.FLIRT: {
        "duration_ticks": 30, "initiator_gain": 15.0, "target_gain": 5.0, "rel_change": 3,
        "new_rel_type_on_success": RelationshipType.CRUSH, "min_rel_score_req": -10
    },
    SocialInteractionType.ARGUE: {
        "duration_ticks": 50, "initiator_gain": -20.0, "target_gain": -20.0, "rel_change": -8,
        "new_rel_type_on_success": RelationshipType.ENEMY_DISLIKED
    },
    # ... definisci una entry per ogni SocialInteractionType ...
}
