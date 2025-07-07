import yaml
import os

from reddit_saas_finder.src.data.database import DB_PATH

CONFIG_PATH = "reddit_saas_finder/config/default.yaml"

class ConfigManager:
    """Manages configuration for the application."""

    def __init__(self, config_path=CONFIG_PATH):
        self.config = self._load_config(config_path)

    def _load_config(self, config_path):
        """Loads the YAML configuration file."""
        try:
            with open(config_path, "r") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Error: Configuration file not found at {config_path}")
            raise
        except yaml.YAMLError as e:
            print(f"Error parsing YAML file: {e}")
            raise

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
        return self.config.get('data_collection', {}) 