import logging
from abc import abstractmethod, ABC
from pathlib import Path

from src.services.llm import get_llm
from src.graph.state import AgentState

logger = logging.getLogger(__name__)


class BaseNode(ABC):
    """
    Abstract base class for nodes in the agent's state graph.

    Attributes:
        llm: The language model instance used by the node.
    """

    def __init__(self) -> None:
        """
        Initialize the BaseNode with an LLM instance.
        """
        logger.info("Initializing BaseNode with LLM instance.")
        self.llm = get_llm()

    def _load_prompt(self, template_name: str) -> str:
        """
        Load a prompt template by name.

        Args:
            template_name (str): The name of the template file to load.

        Returns:
            str: The content of the template file.

        Raises:
            FileNotFoundError: If the template file cannot be found.
            Exception: For other errors during file loading.
        """
        import importlib.resources as pkg_resources

        try:
            from src.graph import prompts as prompts_pkg

            logger.info(f"Attempting to load prompt template: {template_name}")
            with pkg_resources.files(prompts_pkg).joinpath(template_name).open(
                "r", encoding="utf-8"
            ) as f:
                logger.info(f"Successfully loaded prompt template: {template_name}")
                return f.read()
        except FileNotFoundError as e:
            logger.error(f"Prompt template not found: {template_name}")
            raise e
        except Exception as e:
            logger.warning(f"Failed to load prompt template via pkg_resources: {e}")
            here = Path(__file__).resolve().parents[1] / "prompts" / template_name
            try:
                logger.info(
                    f"Attempting to load prompt template from fallback path: {here}"
                )
                return here.read_text(encoding="utf-8")
            except Exception as fallback_error:
                logger.error(
                    f"Failed to load prompt template from fallback path: {fallback_error}"
                )
                raise fallback_error

    @abstractmethod
    def __call__(self, state: AgentState) -> AgentState:
        """
        Abstract method to process the agent's state.

        Args:
            state (AgentState): The current state of the agent.

        Returns:
            AgentState: The updated state of the agent.
        """
        pass
