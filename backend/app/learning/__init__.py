"""
Learning Module
Provides continuous learning from design, simulation, and manufacturing outcomes.
"""
from app.learning.feedback_engine import FeedbackEngine
from app.learning.experience_store import ExperienceStore
from app.learning.lesson_extractor import LessonExtractor
from app.learning.improvement_engine import ImprovementEngine

__all__ = [
    "FeedbackEngine",
    "ExperienceStore",
    "LessonExtractor",
    "ImprovementEngine",
]
