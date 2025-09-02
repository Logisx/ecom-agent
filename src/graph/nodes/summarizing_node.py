import logging
from typing import Any

from src.graph.nodes.base_node import BaseNode
from src.graph.state import AgentState
from langchain_core.messages import SystemMessage

logger = logging.getLogger(__name__)

class SummarizingNode(BaseNode):
    """
    Node responsible for summarizing insights and providing concise answers.

    Attributes:
        llm: The LLM instance used for summarization.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialize the SummarizingNode.
        """
        super().__init__(*args, **kwargs)
        logger.info("Initializing SummarizingNode.")

    def __call__(self, state: AgentState) -> AgentState:
        """
        Summarize insights and provide a concise answer.

        Args:
            state (AgentState): The current state of the agent.

        Returns:
            AgentState: The updated state of the agent with the summary.
        """
        logger.info("SummarizingNode called.")

        try:
            messages = state.get("messages", [])
            system_prompt = self._load_prompt("summarizing.md")

            logger.info("Loaded system prompt for SummarizingNode.")
            messages = [SystemMessage(content=system_prompt)] + list(messages)

            logger.debug(f"Messages before invoking LLM: {messages}")
            response = self.llm.invoke(messages)

            logger.info("SummarizingNode successfully finished.")
            return {"messages": [response]}
        except Exception as e:
            logger.error(f"Error in SummarizingNode: {e}", exc_info=True)
            raise
