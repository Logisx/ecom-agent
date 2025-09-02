import os
import sys
import logging

logger = logging.getLogger(__name__)

class EnvConfig:
    """
    Configuration loader for environment variables.

    Attributes:
        google_api_key (str): The Google API key loaded from the environment.
    """

    def __init__(self) -> None:
        """
        Initialize the EnvConfig and load the Google API key.

        Raises:
            SystemExit: If the GOOGLE_API_KEY environment variable is not set.
        """
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        if not self.google_api_key:
            logger.error("GOOGLE_API_KEY environment variable is not set.")
            sys.exit("ERROR: GOOGLE_API_KEY environment variable is required.")
        logger.info("GOOGLE_API_KEY loaded successfully.")
