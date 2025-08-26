from langchain_google_genai import ChatGoogleGenerativeAI
import os
import typing as _t
from dotenv import load_dotenv


def _create_llm() -> ChatGoogleGenerativeAI:
    # Ensure .env is loaded for import-time configuration
    load_dotenv()
    api_key: _t.Optional[str] = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GOOGLE_API_KEY is not set. Set your Gemini API key to avoid using OAuth ADC with insufficient scopes."
        )

    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-lite",
        temperature=0.3,
        api_key=api_key,
    )


_llm = _create_llm()

def get_llm() -> ChatGoogleGenerativeAI:

    return _llm