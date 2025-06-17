# core/AI/__init__.py
"""
Package per i sistemi di Intelligenza Artificiale di SimAI.
"""
from .action_executor import ActionExecutor
from .ai_coordinator import AICoordinator
from .ai_decision_maker import AIDecisionMaker
from .claire.claire_system import ClaireSystem
from .consequence_analyzer import ConsequenceAnalyzer
from .decision_system import DecisionSystem
from .needs_processor import NeedsProcessor
from .social_manager import SocialManager
from .thought import Thought

__all__ = [
    'AICoordinator',
    'AIDecisionMaker',
    'ActionExecutor',
    'ClaireSystem',
    'ConsequenceAnalyzer',
    'DecisionSystem',
    'NeedsProcessor',
    'SocialManager',
    'Thought',
]