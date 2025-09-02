import logging
from typing import Any 

from src.graph.nodes.base_node import BaseNode
from src.graph.state import AgentState
from src.graph.tools.bigquery import (
    query_bigquery_tool,
    describe_bigquery_table_schema_tool,
)
from langchain_core.messages import SystemMessage

logger = logging.getLogger(__name__)

class AnalyzeNode(BaseNode):
    """
    Node responsible for analyzing the agent's state and invoking tools.

    Attributes:
        llm_with_tools: The LLM instance bound with tools for execution.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialize the AnalyzeNode with tools bound to the LLM.
        """
        super().__init__(*args, **kwargs)
        logger.info("Initializing AnalyzeNode with tools.")
        self.llm_with_tools = self.llm.bind_tools([
            query_bigquery_tool,
            describe_bigquery_table_schema_tool,
        ])


    def __call__(self, state: AgentState) -> AgentState:
        """
        Process the agent's state by invoking the LLM with tools.

        Args:
            state (AgentState): The current state of the agent.

        Returns:
            AgentState: The updated state of the agent.
        """
        logger.info("AnalyzeNode called with state.")

        try:
            messages = state.get("messages", [])
            system_prompt = self._load_prompt("analyze.md")

            logger.info("Loaded system prompt for AnalyzeNode.")
            messages = [SystemMessage(content=system_prompt)] + list(messages)

            logger.debug(f"Messages before invoking LLM: {messages}")
            response = self.llm_with_tools.invoke(messages)

            logger.info("AnalyzeNode successfully processed the state.")
            return {"messages": [response]}
        except Exception as e:
            logger.error(f"Error in AnalyzeNode: {e}", exc_info=True)
            raise