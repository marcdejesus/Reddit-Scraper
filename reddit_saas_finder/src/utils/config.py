import yaml
import os
from dotenv import load_dotenv
from rich.console import Console
from rich.syntax import Syntax

from reddit_saas_finder.src.data.database import DB_PATH

CONFIG_PATH = "reddit_saas_finder/config/default.yaml"
SUBREDDITS_PATH = "reddit_saas_finder/config/subreddits.yaml"

console = Console()

class ConfigManager:
    """Manages configuration for the application."""

    def __init__(self, config_path=CONFIG_PATH):
        load_dotenv(dotenv_path=".env.local")
        self.config = self._load_config(config_path)
        self.subreddits_config = self._load_config(SUBREDDITS_PATH)

    def _load_config(self, config_path):
        """Loads a YAML configuration file and substitutes environment variables."""
        try:
            with open(config_path, "r") as f:
                raw_config = f.read()
                expanded_config = os.path.expandvars(raw_config)
                return yaml.safe_load(expanded_config)
        except FileNotFoundError:
            console.print(f"[bold red]Error: Configuration file not found at {config_path}[/bold red]")
            return None # Return None instead of raising to allow graceful failure
        except yaml.YAMLError as e:
            console.print(f"[bold red]Error parsing YAML file {config_path}: {e}[/bold red]")
            return None

    def get_reddit_credentials(self):
        """Returns Reddit API credentials."""
        if self.config and 'reddit' in self.config:
            return (
                self.config['reddit'].get('client_id'),
                self.config['reddit'].get('client_secret'),
                self.config['reddit'].get('user_agent')
            )
        return None, None, None

    def get_database_path(self):
        """Returns the path to the SQLite database."""
        return DB_PATH
        
    def get_data_collection_config(self):
        """Returns the data collection configuration."""
        return self.config.get('data_collection', {}) if self.config else {}

    def get_nlp_config(self):
        """Returns the NLP configuration."""
        return self.config.get('nlp', {}) if self.config else {}

    def get_scoring_config(self):
        """Returns the scoring configuration."""
        return self.config.get('scoring', {}) if self.config else {}

    def load_subreddits(self):
        """Loads primary and secondary subreddits from subreddits.yaml."""
        if self.subreddits_config and 'subreddits' in self.subreddits_config:
            return (
                self.subreddits_config['subreddits'].get('primary', []),
                self.subreddits_config['subreddits'].get('secondary', [])
            )
        return [], []
    
    def get_raw_config_text(self):
        """Returns the raw text content of the config files."""
        raw_main = ""
        raw_subreddits = ""
        try:
            with open(CONFIG_PATH, 'r') as f:
                raw_main = f.read()
        except FileNotFoundError:
            pass # Handled in _load_config

        try:
            with open(SUBREDDITS_PATH, 'r') as f:
                raw_subreddits = f.read()
        except FileNotFoundError:
            pass
        
        return raw_main, raw_subreddits 