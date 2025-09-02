import logging
from typing import Optional

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import Runnable

from src.config.app_config_loader import AppConfigLoader
from src.config.env_config import EnvConfig

logger = logging.getLogger(__name__)

_llm: Optional[Runnable] = None

def _create_llm() -> Runnable:
    """
    Create and configure the primary and fallback LLMs.

    Returns:
        Runnable: A runnable LLM instance with fallbacks.
    """
    logger.info("Creating LLM instance.")
    try:
        api_key: Optional[str] = EnvConfig().google_api_key

        if not api_key:
            logger.error("Google API key is missing in the environment configuration.")
            raise ValueError("Google API key is required to initialize the LLM.")

        config = AppConfigLoader().get_config()
        agent_config = config.get("agent", {})
        model_name = agent_config.get("llm_model", "gemini-2.5-pro")
        fallback_model_name = agent_config.get("fallback_llm_model", "gemini-2.0-flash")
        temperature = agent_config.get("temperature", 0.3)

        primary_llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            api_key=api_key,
        )

        fallback_llm = ChatGoogleGenerativeAI(
            model=fallback_model_name,
            temperature=temperature,
            api_key=api_key,
        )

        logger.info("LLM instance created successfully.")

        return primary_llm.with_fallbacks([fallback_llm])

    except Exception as e:
        logger.error(f"Failed to create LLM instance: {e}", exc_info=True)
        raise

def get_llm() -> Runnable:
    """
    Retrieve the shared LLM instance, creating it if necessary.

    Returns:
        Runnable: The shared LLM instance.
    """
    global _llm
    if _llm is None:
        logger.info("Initializing shared LLM instance.")
        _llm = _create_llm() 
    return _llm