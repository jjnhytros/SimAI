# core/AI/__init__.py
"""
Package per i sistemi di Intelligenza Artificiale di SimAI.
"""
from .ai_decision_maker import AIDecisionMaker
from .ai_coordinator import AICoordinator  # <-- NUOVA RIGA per esportare AICoordinator
from .decision_system import DecisionSystem
from .needs_processor import NeedsProcessor
from .action_executor import ActionExecutor
from .social_manager import SocialManager
# from .memory_system import MemorySystem # Se definito
# from .learning_system import LearningSystem # Se definito