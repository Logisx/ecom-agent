from langchain_google_genai import ChatGoogleGenerativeAI
import os
from typing import Optional
from src.config.app_config_loader import AppConfigLoader
from langchain_core.runnables import Runnable
from src.config.env_config import EnvConfig

_llm: Optional[Runnable] = None

def _create_llm() -> Runnable:
    api_key: Optional[str] = EnvConfig().google_api_key

    config = AppConfigLoader().get_config()
    agent_config = config.get("agent", {})
    model_name = agent_config.get("llm_model", "gemini-2.5-pro")
    fallback_model_name = agent_config.get("fallback_llm_model", "gemini-2.0-flash")
    temperature = agent_config.get("temperature", 0.3)

    # Primary LLM
    primary_llm = ChatGoogleGenerativeAI(
        model=model_name,
        temperature=temperature,
        api_key=api_key,
    )

    # Fallback LLM
    fallback_llm = ChatGoogleGenerativeAI(
        model=fallback_model_name,
        temperature=temperature,
        api_key=api_key,
    )

    # Chain them together with fallbacks
    return primary_llm.with_fallbacks([fallback_llm])


def get_llm() -> Runnable:
    global _llm
    if _llm is None:
        _llm = _create_llm()  # runs after load_dotenv()
    return _llm