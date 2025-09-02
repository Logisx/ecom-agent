import os
import yaml
import argparse
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class AppConfigLoader:
    """
    Singleton class for loading and managing application configuration.

    Attributes:
        _instance: The singleton instance of the class.
        _config: The loaded configuration dictionary.
    """
    _instance = None
    _config: Optional[Dict[str, Any]] = None

    def __new__(cls) -> "AppConfigLoader":
        """
        Ensure a single instance of AppConfigLoader is created.

        Returns:
            AppConfigLoader: The singleton instance.
        """
        if cls._instance is None:
            cls._instance = super(AppConfigLoader, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """
        Initialize the AppConfigLoader and load the configuration if not already loaded.
        """
        if self._config is None:
            logger.info("Loading application configuration.")
            self._load_config()

    def _load_config(self) -> None:
        """
        Load the configuration from the YAML file.
        """
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "config",
            "app-config.yaml",
        )
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                self._config = yaml.safe_load(f)
                logger.info("Configuration loaded successfully from config.yaml.")
        except FileNotFoundError:
            logger.warning(f"Configuration file not found at {config_path}. Using default empty configuration.")
            self._config = {}
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}", exc_info=True)
            self._config = {}

    def get_config(self) -> Dict[str, Any]:
        """
        Get a copy of the loaded configuration.

        Returns:
            Dict[str, Any]: A copy of the configuration dictionary.
        """
        logger.debug("Fetching a copy of the application configuration.")
        return self._config.copy() if self._config else {}

    def merge_with_args(self, args: argparse.Namespace) -> Dict[str, Any]:
        """
        Merge argparse arguments with the base YAML configuration.
        CLI arguments take precedence over YAML values.

        Args:
            args (argparse.Namespace): Parsed command-line arguments.

        Returns:
            Dict[str, Any]: The merged configuration dictionary.
        """
        logger.info("Merging command-line arguments with application configuration.")
        config = self.get_config()

        bq_config = config.setdefault("bigquery", {})
        if getattr(args, "project", None) is not None:
            bq_config["project_id"] = args.project
        if getattr(args, "dataset", None) is not None:
            bq_config["dataset_id"] = args.dataset

        agent_config = config.setdefault("agent", {})
        if getattr(args, "model", None) is not None:
            agent_config["llm_model"] = args.model

        log_config = config.setdefault("logging", {})
        if getattr(args, "verbose", False):
            log_config["level"] = "DEBUG"

        logger.info("Configuration merged successfully.")
        return config
