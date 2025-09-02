import os
import yaml
import argparse
from typing import Dict, Any, Optional

class AppConfigLoader:
    _instance = None
    _config: Optional[Dict[str, Any]] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AppConfigLoader, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._config is None:
            self._load_config()

    def _load_config(self):
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "config",
            "config.yaml"
        )
        try:
            with open(config_path, "r") as f:
                self._config = yaml.safe_load(f)
        except FileNotFoundError:
            # Handle case where config file might be missing
            self._config = {}

    def get_config(self) -> Dict[str, Any]:
        """Returns a copy of the loaded configuration."""
        return self._config.copy() if self._config else {}

    def merge_with_args(self, args: argparse.Namespace) -> Dict[str, Any]:
        """
        Merges argparse arguments with the base YAML config.
        CLI arguments take precedence over YAML values.
        """
        config = self.get_config()
        
        # BigQuery settings
        bq_config = config.setdefault("bigquery", {})
        if getattr(args, "project", None) is not None:
            bq_config["project_id"] = args.project
        if getattr(args, "dataset", None) is not None:
            bq_config["dataset_id"] = args.dataset

        # Agent settings
        agent_config = config.setdefault("agent", {})
        if getattr(args, "model", None) is not None:
            agent_config["llm_model"] = args.model
        
        # Logging settings
        log_config = config.setdefault("logging", {})
        if getattr(args, "verbose", False):
            log_config["level"] = "DEBUG"

        return config      
    