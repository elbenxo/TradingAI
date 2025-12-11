"""Configuration management for TradingAI."""

import os
import yaml
from pathlib import Path
from typing import Any, Dict
from dotenv import load_dotenv


class Config:
    """Configuration manager for TradingAI application."""

    def __init__(self, config_path: str = None):
        """
        Initialize configuration manager.

        Args:
            config_path: Path to config.yaml file. Defaults to project root.
        """
        # Load environment variables
        load_dotenv()

        # Set config path
        if config_path is None:
            project_root = Path(__file__).parent.parent.parent.parent
            config_path = project_root / "config.yaml"

        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = {}
        self._load_config()

    def _load_config(self):
        """Load configuration from YAML file."""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                self._config = yaml.safe_load(f) or {}
        else:
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.

        Args:
            key: Dot-separated configuration key (e.g., 'app.name')
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self._config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default

        return value

    def get_env(self, key: str, default: str = None) -> str:
        """
        Get environment variable.

        Args:
            key: Environment variable name
            default: Default value if not found

        Returns:
            Environment variable value or default
        """
        return os.getenv(key, default)

    @property
    def app_name(self) -> str:
        """Get application name."""
        return self.get('app.name', 'TradingAI')

    @property
    def app_version(self) -> str:
        """Get application version."""
        return self.get('app.version', '0.1.0')

    @property
    def log_level(self) -> str:
        """Get logging level."""
        return self.get_env('LOG_LEVEL', self.get('app.log_level', 'INFO'))

    @property
    def environment(self) -> str:
        """Get environment (development/production)."""
        return self.get_env('ENVIRONMENT', self.get('app.environment', 'development'))


# Global configuration instance
config = Config()
