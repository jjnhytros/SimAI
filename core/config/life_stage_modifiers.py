# simai/core/config/life_stage_modifiers.py
from enum import Enum
from typing import Dict, List, Callable, Any
from core.enums.life_stages import LifeStage
from core.enums.lifestyles import LifeStyle
from core.enums.moodlet_types import MoodletType
from core.enums.trait_types import TraitType

class LifeStageEffectType(Enum):
    METABOLIC_RATE = "metabolic_rate"
    SOCIAL_NEED_MODIFIER = "social_need_modifier"
    ENERGY_DECAY_MODIFIER = "energy_decay_modifier"
    SLEEP_REQUIREMENT = "sleep_requirement"
    LEARNING_EFFICIENCY = "learning_efficiency"

class LifeStageEffectSystem:
    # Modificatori base per ogni stadio di vita
    BASE_EFFECTS = {
        # Fase Infantile
        LifeStage.NEWBORN:    { LifeStageEffectType.METABOLIC_RATE: 2.0, LifeStageEffectType.SOCIAL_NEED_MODIFIER: 1.5, LifeStageEffectType.ENERGY_DECAY_MODIFIER: 0.5, LifeStageEffectType.SLEEP_REQUIREMENT: 16, LifeStageEffectType.LEARNING_EFFICIENCY: 0.1 },
        LifeStage.INFANT:     { LifeStageEffectType.METABOLIC_RATE: 1.9, LifeStageEffectType.SOCIAL_NEED_MODIFIER: 1.8, LifeStageEffectType.ENERGY_DECAY_MODIFIER: 0.7, LifeStageEffectType.SLEEP_REQUIREMENT: 14, LifeStageEffectType.LEARNING_EFFICIENCY: 0.2 },
        LifeStage.TODDLER:    { LifeStageEffectType.METABOLIC_RATE: 1.8, LifeStageEffectType.SOCIAL_NEED_MODIFIER: 2.0, LifeStageEffectType.ENERGY_DECAY_MODIFIER: 0.8, LifeStageEffectType.SLEEP_REQUIREMENT: 12, LifeStageEffectType.LEARNING_EFFICIENCY: 0.5 },
        
        # Fase Fanciullezza
        LifeStage.PRESCHOOLER:{ LifeStageEffectType.METABOLIC_RATE: 1.7, LifeStageEffectType.SOCIAL_NEED_MODIFIER: 1.8, LifeStageEffectType.ENERGY_DECAY_MODIFIER: 0.9, LifeStageEffectType.SLEEP_REQUIREMENT: 11, LifeStageEffectType.LEARNING_EFFICIENCY: 1.0 },
        LifeStage.CHILD:      { LifeStageEffectType.METABOLIC_RATE: 1.6, LifeStageEffectType.SOCIAL_NEED_MODIFIER: 1.6, LifeStageEffectType.ENERGY_DECAY_MODIFIER: 1.0, LifeStageEffectType.SLEEP_REQUIREMENT: 10, LifeStageEffectType.LEARNING_EFFICIENCY: 1.2 },
        LifeStage.PRE_TEEN:   { LifeStageEffectType.METABOLIC_RATE: 1.5, LifeStageEffectType.SOCIAL_NEED_MODIFIER: 1.7, LifeStageEffectType.ENERGY_DECAY_MODIFIER: 1.0, LifeStageEffectType.SLEEP_REQUIREMENT: 9,  LifeStageEffectType.LEARNING_EFFICIENCY: 1.3 },

        # Fase Adolescenza
        LifeStage.EARLY_ADOLESCENCE: { LifeStageEffectType.METABOLIC_RATE: 1.6, LifeStageEffectType.SOCIAL_NEED_MODIFIER: 1.8, LifeStageEffectType.ENERGY_DECAY_MODIFIER: 1.1, LifeStageEffectType.SLEEP_REQUIREMENT: 9, LifeStageEffectType.LEARNING_EFFICIENCY: 1.4 },
        LifeStage.MID_ADOLESCENCE:   { LifeStageEffectType.METABOLIC_RATE: 1.4, LifeStageEffectType.SOCIAL_NEED_MODIFIER: 2.0, LifeStageEffectType.ENERGY_DECAY_MODIFIER: 1.1, LifeStageEffectType.SLEEP_REQUIREMENT: 8, LifeStageEffectType.LEARNING_EFFICIENCY: 1.3 },
        LifeStage.LATE_ADOLESCENCE:  { LifeStageEffectType.METABOLIC_RATE: 1.2, LifeStageEffectType.SOCIAL_NEED_MODIFIER: 1.5, LifeStageEffectType.ENERGY_DECAY_MODIFIER: 1.0, LifeStageEffectType.SLEEP_REQUIREMENT: 8, LifeStageEffectType.LEARNING_EFFICIENCY: 1.2 },

        # Fase Adulta
        LifeStage.YOUNG_ADULT:  { LifeStageEffectType.METABOLIC_RATE: 1.1, LifeStageEffectType.SOCIAL_NEED_MODIFIER: 1.2, LifeStageEffectType.ENERGY_DECAY_MODIFIER: 1.0, LifeStageEffectType.SLEEP_REQUIREMENT: 7, LifeStageEffectType.LEARNING_EFFICIENCY: 1.1 },
        LifeStage.ADULT:        { LifeStageEffectType.METABOLIC_RATE: 1.0, LifeStageEffectType.SOCIAL_NEED_MODIFIER: 1.0, LifeStageEffectType.ENERGY_DECAY_MODIFIER: 1.0, LifeStageEffectType.SLEEP_REQUIREMENT: 7, LifeStageEffectType.LEARNING_EFFICIENCY: 1.0 },
        LifeStage.MIDDLE_AGED:  { LifeStageEffectType.METABOLIC_RATE: 0.9, LifeStageEffectType.SOCIAL_NEED_MODIFIER: 0.9, LifeStageEffectType.ENERGY_DECAY_MODIFIER: 1.1, LifeStageEffectType.SLEEP_REQUIREMENT: 7, LifeStageEffectType.LEARNING_EFFICIENCY: 0.9 },

        # Fase Anziana
        LifeStage.MATURE_ADULT: { LifeStageEffectType.METABOLIC_RATE: 0.8, LifeStageEffectType.SOCIAL_NEED_MODIFIER: 0.8, LifeStageEffectType.ENERGY_DECAY_MODIFIER: 1.2, LifeStageEffectType.SLEEP_REQUIREMENT: 8, LifeStageEffectType.LEARNING_EFFICIENCY: 0.8 },
        LifeStage.SENIOR:       { LifeStageEffectType.METABOLIC_RATE: 0.7, LifeStageEffectType.SOCIAL_NEED_MODIFIER: 0.7, LifeStageEffectType.ENERGY_DECAY_MODIFIER: 1.3, LifeStageEffectType.SLEEP_REQUIREMENT: 8, LifeStageEffectType.LEARNING_EFFICIENCY: 0.7 },
        LifeStage.ELDERLY:      { LifeStageEffectType.METABOLIC_RATE: 0.6, LifeStageEffectType.SOCIAL_NEED_MODIFIER: 0.6, LifeStageEffectType.ENERGY_DECAY_MODIFIER: 1.4, LifeStageEffectType.SLEEP_REQUIREMENT: 9, LifeStageEffectType.LEARNING_EFFICIENCY: 0.5 },
    }

    # Mappa dei modificatori dinamici
    DYNAMIC_MODIFIERS = {
        # Modificatori basati sui tratti
        TraitType.ACTIVE: {
            LifeStageEffectType.METABOLIC_RATE: 1.15,
            LifeStageEffectType.ENERGY_DECAY_MODIFIER: 1.1
        },
        TraitType.LAZY: {
            LifeStageEffectType.METABOLIC_RATE: 0.9,
            LifeStageEffectType.ENERGY_DECAY_MODIFIER: 0.8
        },
        TraitType.SOCIAL: {
            LifeStageEffectType.SOCIAL_NEED_MODIFIER: 1.3
        },
        TraitType.LONER: {
            LifeStageEffectType.SOCIAL_NEED_MODIFIER: 0.7
        },
        TraitType.BOOKWORM: {
            LifeStageEffectType.LEARNING_EFFICIENCY: 1.25
        },
        
        # Modificatori basati sull'umore
        MoodletType.DEPRESSED: {
            LifeStageEffectType.METABOLIC_RATE: 0.85,
            LifeStageEffectType.ENERGY_DECAY_MODIFIER: 1.2
        },
        MoodletType.ENERGETIC: {
            LifeStageEffectType.METABOLIC_RATE: 1.1,
            LifeStageEffectType.ENERGY_DECAY_MODIFIER: 0.9
        },
        MoodletType.STRESSED: {
            LifeStageEffectType.SLEEP_REQUIREMENT: 1.2,
            LifeStageEffectType.LEARNING_EFFICIENCY: 0.8
        },
        
        # Modificatori basati sullo stile di vita
        LifeStyle.ATHLETE: {
            LifeStageEffectType.METABOLIC_RATE: 1.2,
            LifeStageEffectType.ENERGY_DECAY_MODIFIER: 0.85
        },
        LifeStyle.SEDENTARY: {
            LifeStageEffectType.METABOLIC_RATE: 0.9,
            LifeStageEffectType.ENERGY_DECAY_MODIFIER: 1.15
        },
        LifeStyle.INTELLECTUAL: {
            LifeStageEffectType.LEARNING_EFFICIENCY: 1.3
        }
    }

    # Modificatori cumulativi per malattie/condizioni
    HEALTH_MODIFIERS = {
        "DIABETES": {
            LifeStageEffectType.METABOLIC_RATE: 0.8,
            LifeStageEffectType.ENERGY_DECAY_MODIFIER: 1.3
        },
        "HYPERTHYROIDISM": {
            LifeStageEffectType.METABOLIC_RATE: 1.4
        },
        "DEPRESSION": {
            LifeStageEffectType.ENERGY_DECAY_MODIFIER: 1.4
        }
    }

    @classmethod
    def get_effect(cls, npc, effect_type: LifeStageEffectType) -> float:
        """Calcola un effetto composito basato su vari fattori"""
        # Ottieni l'effetto base per lo stadio di vita
        base_value = cls.BASE_EFFECTS.get(npc.life_stage, {}).get(effect_type, 1.0)
        
        # Applica modificatori cumulativi
        total_modifier = 1.0
        
        # 1. Modificatori dai tratti
        for trait in npc.traits:
            if trait in cls.DYNAMIC_MODIFIERS and effect_type in cls.DYNAMIC_MODIFIERS[trait]:
                total_modifier *= cls.DYNAMIC_MODIFIERS[trait][effect_type]
        
        # 2. Modificatori dall'umore
        if npc.moodlet_manager:
            for moodlet_type in npc.moodlet_manager.active_moodlets.keys():
                if moodlet_type in cls.DYNAMIC_MODIFIERS and effect_type in cls.DYNAMIC_MODIFIERS[moodlet_type]:
                    total_modifier *= cls.DYNAMIC_MODIFIERS[moodlet_type][effect_type]
        
        # 3. Modificatori dallo stile di vita
        if npc.lifestyle in cls.DYNAMIC_MODIFIERS and effect_type in cls.DYNAMIC_MODIFIERS[npc.lifestyle]:
            total_modifier *= cls.DYNAMIC_MODIFIERS[npc.lifestyle][effect_type]
        
        # 4. Modificatori dalla salute
        for condition in npc.health_conditions:
            if condition in cls.HEALTH_MODIFIERS and effect_type in cls.HEALTH_MODIFIERS[condition]:
                total_modifier *= cls.HEALTH_MODIFIERS[condition][effect_type]
        
        return base_value * total_modifier

    @classmethod
    def apply_dynamic_effects(cls, npc):
        """Applica tutti gli effetti dinamici a un NPC"""
        npc.metabolic_rate = cls.get_effect(npc, LifeStageEffectType.METABOLIC_RATE)
        npc.social_need_modifier = cls.get_effect(npc, LifeStageEffectType.SOCIAL_NEED_MODIFIER)
        npc.energy_decay_modifier = cls.get_effect(npc, LifeStageEffectType.ENERGY_DECAY_MODIFIER)
        npc.sleep_requirement = cls.get_effect(npc, LifeStageEffectType.SLEEP_REQUIREMENT)
        npc.learning_efficiency = cls.get_effect(npc, LifeStageEffectType.LEARNING_EFFICIENCY)