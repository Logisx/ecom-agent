from abc import abstractmethod, ABC

from src.services.llm import get_llm
from src.graph.state import AgentState


class BaseNode(ABC):
    def __init__(self):
        self.llm = get_llm()

    @abstractmethod
    def __call__(self, state: AgentState) -> AgentState:
        pass
