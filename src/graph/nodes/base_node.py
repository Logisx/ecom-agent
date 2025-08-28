from abc import abstractmethod, ABC

from src.services.llm import get_llm
from src.graph.state import AgentState


class BaseNode(ABC):
    def __init__(self):
        self.llm = get_llm()

    def _load_prompt(self, template_name: str) -> str:
        import importlib.resources as pkg_resources
        from pathlib import Path
        try:
            # Try package resource loading
            from src.graph import prompts as prompts_pkg
            with pkg_resources.files(prompts_pkg).joinpath(template_name).open("r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            # Fallback to relative path
            here = Path(__file__).resolve().parents[1] / "prompts" / template_name
            return here.read_text(encoding="utf-8")

    @abstractmethod
    def __call__(self, state: AgentState) -> AgentState:
        pass
