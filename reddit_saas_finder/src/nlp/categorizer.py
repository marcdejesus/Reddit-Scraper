"""Categorizes text into predefined categories."""
from utils.config import ConfigManager
import yaml
from rich.console import Console

class Categorizer:
    """
    Classifies text into predefined categories based on keywords.

    This class uses a dictionary of categories and their associated keywords,
    loaded from the configuration, to determine the most appropriate category
    for a given piece of text.
    """
    def __init__(self):
        """Initializes the Categorizer.

        Loads the category-keyword mappings from the application configuration.
        """
        config_manager = ConfigManager()
        self.categories = config_manager.config.get('categories', {})

    def classify_problem_category(self, text: str):
        """
        Classifies the given text into one of the predefined categories.

        It performs a case-insensitive search for keywords in the text.
        The first category with a matching keyword is returned.

        Args:
            text (str): The text to be classified.

        Returns:
            str: The name of the matched category, or 'other' if no keywords
                 from any category are found.
        """
        text_lower = text.lower()
        for category, keywords in self.categories.items():
            if any(keyword in text_lower for keyword in keywords):
                return category
        return 'other' 