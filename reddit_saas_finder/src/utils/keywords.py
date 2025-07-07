"""Manages custom keywords for NLP processing."""
import yaml
from rich.console import Console
import os

KEYWORDS_PATH = "reddit_saas_finder/config/keywords.yaml"
console = Console()

class KeywordManager:
    """
    Manages custom pain point keywords stored in a YAML configuration file.

    This class handles loading, saving, adding, removing, and exporting
    custom keywords used by the NLP pain point detectors.
    """
    def __init__(self, keywords_path=KEYWORDS_PATH):
        """Initializes the KeywordManager.

        Args:
            keywords_path (str, optional): The path to the keywords YAML file.
                Defaults to KEYWORDS_PATH.
        """
        self.keywords_path = keywords_path
        self.keywords = self._load_keywords()

    def _load_keywords(self):
        """
        Loads keywords from the YAML file.

        If the file doesn't exist, it creates a default one.

        Returns:
            dict: The loaded keywords.
        """
        if not os.path.exists(self.keywords_path):
            self._create_default_keywords_file()
        try:
            with open(self.keywords_path, 'r') as f:
                return yaml.safe_load(f) or {'pain_point_keywords': []}
        except yaml.YAMLError as e:
            console.print(f"[bold red]Error parsing keywords file: {e}[/bold red]")
            return {'pain_point_keywords': []}

    def _save_keywords(self):
        """Saves the current keywords dictionary back to the YAML file."""
        try:
            with open(self.keywords_path, 'w') as f:
                yaml.dump(self.keywords, f, default_flow_style=False)
            console.print(f"[green]Keywords saved to {self.keywords_path}[/green]")
        except IOError as e:
            console.print(f"[bold red]Error saving keywords file: {e}[/bold red]")

    def _create_default_keywords_file(self):
        """Creates a default `keywords.yaml` file with a few example keywords."""
        default_keywords = {
            'pain_point_keywords': [
                "frustrating", "difficult", "impossible", "waste of time", "inefficient"
            ]
        }
        try:
            os.makedirs(os.path.dirname(self.keywords_path), exist_ok=True)
            with open(self.keywords_path, 'w') as f:
                yaml.dump(default_keywords, f)
            console.print(f"Created default keywords file at {self.keywords_path}")
        except IOError as e:
            console.print(f"[bold red]Could not create default keywords file: {e}[/bold red]")
    
    def add_pain_point_keyword(self, keyword: str, category: str = None):
        """
        Adds a new keyword to the list of pain point keywords.

        Args:
            keyword (str): The keyword to add.
            category (str, optional): The category to associate with the keyword.
                This is not yet fully implemented. Defaults to None.
        """
        if 'pain_point_keywords' not in self.keywords:
            self.keywords['pain_point_keywords'] = []
            
        if keyword not in self.keywords['pain_point_keywords']:
            self.keywords['pain_point_keywords'].append(keyword)
            self._save_keywords()
            console.print(f"Added keyword: '[bold cyan]{keyword}[/bold cyan]'")
        else:
            console.print(f"Keyword '[bold cyan]{keyword}[/bold cyan]' already exists.")

    def remove_keyword(self, keyword: str):
        """
        Removes a keyword from the list of pain point keywords.

        Args:
            keyword (str): The keyword to remove.
        """
        if keyword in self.keywords.get('pain_point_keywords', []):
            self.keywords['pain_point_keywords'].remove(keyword)
            self._save_keywords()
            console.print(f"Removed keyword: '[bold cyan]{keyword}[/bold cyan]'")
        else:
            console.print(f"Keyword '[bold red]{keyword}[/bold red]' not found.")

    def export_keywords(self, file_path: str, format: str = 'yaml'):
        """
        Exports the current keywords to a specified file.

        Args:
            file_path (str): The path to the file where keywords will be saved.
            format (str, optional): The export format. Currently only 'yaml'
                is supported. Defaults to 'yaml'.
        """
        if format.lower() != 'yaml':
            console.print("[bold red]Only YAML export is currently supported.[/bold red]")
            return

        try:
            with open(file_path, 'w') as f:
                yaml.dump(self.keywords, f, default_flow_style=False)
            console.print(f"[green]Keywords exported successfully to {file_path}[/green]")
        except IOError as e:
            console.print(f"[bold red]Error exporting keywords to {file_path}: {e}[/bold red]")

    def get_pain_point_keywords(self):
        """
        Returns the list of all configured pain point keywords.

        Returns:
            list: A list of keyword strings.
        """
        return self.keywords.get('pain_point_keywords', []) 