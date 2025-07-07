"""Categorizes text into predefined categories."""
from utils.config import ConfigManager
import yaml
from rich.console import Console

class Categorizer:
    """
    Classifies text into predefined categories based on keywords.
    """
    def __init__(self):
        config_manager = ConfigManager()
        self.categories = config_manager.config.get('categories', {})

    def classify_problem_category(self, text: str):
        """
        Classifies the given text into one of the predefined categories.
        """
        text_lower = text.lower()
        for category, keywords in self.categories.items():
            if any(keyword in text_lower for keyword in keywords):
                return category
        return 'other' 