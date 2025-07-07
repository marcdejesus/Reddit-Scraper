import yaml
import os
from dotenv import load_dotenv
from rich.console import Console
from rich.syntax import Syntax

from data.database import DB_PATH

CONFIG_PATH = "reddit_saas_finder/config/default.yaml"
SUBREDDITS_PATH = "reddit_saas_finder/config/subreddits.yaml"

console = Console()

class ConfigManager:
    """
    Manages loading and accessing configuration from YAML files and environment variables.

    This class handles reading the main configuration (`default.yaml`), subreddit
    lists (`subreddits.yaml`), and substituting environment variables for secrets.
    """

    def __init__(self, config_path=CONFIG_PATH):
        """Initializes the ConfigManager.

        Loads the main config and subreddit config files. It also loads environment
        variables from a `.env.local` file if it exists.

        Args:
            config_path (str, optional): The path to the main configuration file.
                Defaults to CONFIG_PATH.
        """
        load_dotenv(dotenv_path=".env.local")
        self.config = self._load_config(config_path)
        self.subreddits_config = self._load_config(SUBREDDITS_PATH)

    def _load_config(self, config_path):
        """
        Loads a single YAML configuration file and substitutes environment variables.

        Args:
            config_path (str): The path to the YAML file.

        Returns:
            dict or None: The loaded configuration as a dictionary, or None if
                          an error occurred.
        """
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

        This is useful for displaying the original configuration to the user.

        Returns:
            tuple: A tuple containing the raw string content of (main_config, subreddit_config).
        """
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