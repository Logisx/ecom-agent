from langchain_google_genai import ChatGoogleGenerativeAI
import os
import typing as _t
from dotenv import load_dotenv
from src.config.config_loader import ConfigLoader


def _create_llm() -> ChatGoogleGenerativeAI:
    # Ensure .env is loaded for import-time configuration
    load_dotenv()
    api_key: _t.Optional[str] = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GOOGLE_API_KEY is not set. Set your Gemini API key to avoid using OAuth ADC with insufficient scopes."
        )

    config = ConfigLoader().get_config()
    agent_config = config.get("agent", {})
    model_name = agent_config.get("llm_model", "gemini-2.5-flash")
    temperature = agent_config.get("temperature", 0.3)

    return ChatGoogleGenerativeAI(
        model=model_name,
        temperature=temperature,
        api_key=api_key,
    )


_llm = _create_llm()

def get_llm() -> ChatGoogleGenerativeAI:

    return _llm