import yaml
import os
from dotenv import load_dotenv
from rich.console import Console
from rich.syntax import Syntax
import importlib.resources

from data.database import DB_PATH

console = Console()

class ConfigManager:
    """
    Manages loading and accessing configuration from YAML files and environment variables.
    """

    def __init__(self):
        """Initializes the ConfigManager."""
        load_dotenv(dotenv_path=".env.local")
        self.config = self._load_config("default.yaml")
        self.subreddits_config = self._load_config("subreddits.yaml")

    def _load_config(self, filename):
        """
        Loads a single YAML configuration file from the package data.
        """
        try:
            with importlib.resources.files('config').joinpath(filename).open('r') as f:
                raw_config = f.read()
                expanded_config = os.path.expandvars(raw_config)
                return yaml.safe_load(expanded_config)
        except FileNotFoundError:
            console.print(f"[bold red]Error: Configuration file '{filename}' not found in package.[/bold red]")
            return None
        except yaml.YAMLError as e:
            console.print(f"[bold red]Error parsing YAML file {filename}: {e}[/bold red]")
            return None

    def get_reddit_credentials(self):
        """
        Retrieves the Reddit API credentials from the configuration.

        Returns:
            tuple: A tuple containing the client_id, client_secret, and user_agent.
                   Returns (None, None, None) if not found.
        """
        if self.config and 'reddit' in self.config:
            return (
                self.config['reddit'].get('client_id'),
                self.config['reddit'].get('client_secret'),
                self.config['reddit'].get('user_agent')
            )
        return None, None, None

    def get_database_path(self):
        """
        Returns the configured path to the SQLite database.

        Returns:
            str: The database file path.
        """
        return DB_PATH
        
    def get_data_collection_config(self):
        """
        Returns the 'data_collection' section of the configuration.

        Returns:
            dict: The data collection configuration dictionary, or an empty dict.
        """
        return self.config.get('data_collection', {}) if self.config else {}

    def get_nlp_config(self):
        """
        Returns the 'nlp' section of the configuration.

        Returns:
            dict: The NLP configuration dictionary, or an empty dict.
        """
        return self.config.get('nlp', {}) if self.config else {}

    def get_scoring_config(self):
        """
        Returns the 'scoring' section of the configuration.

        Returns:
            dict: The scoring configuration dictionary, or an empty dict.
        """
        return self.config.get('scoring', {}) if self.config else {}

    def load_subreddits(self):
        """
        Loads the lists of primary and secondary subreddits from the config.

        Returns:
            tuple: A tuple containing two lists: (primary_subreddits, secondary_subreddits).
        """
        if self.subreddits_config and 'subreddits' in self.subreddits_config:
            return (
                self.subreddits_config['subreddits'].get('primary', []),
                self.subreddits_config['subreddits'].get('secondary', [])
            )
        return [], []
    
    def get_raw_config_text(self):
        """
        Returns the raw text content of the main and subreddit config files.
        """
        raw_main = ""
        raw_subreddits = ""
        try:
            with importlib.resources.files('config').joinpath('default.yaml').open('r') as f:
                raw_main = f.read()
        except FileNotFoundError:
            pass 

        try:
            with importlib.resources.files('config').joinpath('subreddits.yaml').open('r') as f:
                raw_subreddits = f.read()
        except FileNotFoundError:
            pass
        
        return raw_main, raw_subreddits 