import logging
from typing import Any

from src.graph.nodes.base_node import BaseNode
from src.graph.state import AgentState
from langchain_core.messages import SystemMessage
from src.graph.tools.python_tool import python_repl_tool

logger = logging.getLogger(__name__)

class AnalyzingNode(BaseNode):
    """
    Node responsible for analyzing data retrieved by the Data Retrieval Node.

    Attributes:
        llm_with_tools: The LLM instance bound with tools for execution.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialize the AnalyzingNode with tools bound to the LLM.
        """
        super().__init__(*args, **kwargs)
        logger.info("Initializing AnalyzingNode with Python REPL Tool.")
        self.llm_with_tools = self.llm.bind_tools([
            python_repl_tool,
        ])

    def __call__(self, state: AgentState) -> AgentState:
        """
        Analyze data and provide insights based on the agent's state.

        Args:
            state (AgentState): The current state of the agent.

        Returns:
            AgentState: The updated state of the agent with insights.
        """
        logger.info("AnalyzingNode called.")

        try:
            messages = state.get("messages", [])
            system_prompt = self._load_prompt("analyzing.md")

            logger.info("Loaded system prompt for AnalyzingNode.")
            messages = [SystemMessage(content=system_prompt)] + list(messages)

            logger.debug(f"Messages before invoking LLM: {messages}")
            response = self.llm_with_tools.invoke(messages)

            logger.info("AnalyzingNode successfully finishing.")
            return {"messages": [response]}
        except Exception as e:
            logger.error(f"Error in AnalyzingNode: {e}", exc_info=True)
            raise
