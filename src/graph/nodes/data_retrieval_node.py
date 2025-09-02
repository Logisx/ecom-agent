import logging
from typing import Any

from src.graph.nodes.base_node import BaseNode
from src.graph.state import AgentState
from src.graph.tools.bigquery_tool import (
    query_bigquery_tool,
    describe_bigquery_table_schema_tool,
)
from langchain_core.messages import SystemMessage

logger = logging.getLogger(__name__)

class DataRetrievalNode(BaseNode):
    """
    Node responsible for retrieving data from BigQuery using SQL tools.

    Attributes:
        llm_with_tools: The LLM instance bound with tools for execution.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialize the DataRetrievalNode with tools bound to the LLM.
        """
        super().__init__(*args, **kwargs)
        logger.info("Initializing DataRetrievalNode with tools.")
        self.llm_with_tools = self.llm.bind_tools([
            query_bigquery_tool,
            describe_bigquery_table_schema_tool,
        ])

    def __call__(self, state: AgentState) -> AgentState:
        """
        Retrieve data from BigQuery based on the agent's state.

        Args:
            state (AgentState): The current state of the agent.

        Returns:
            AgentState: The updated state of the agent with retrieved data.
        """
        logger.info("DataRetrievalNode called.")

        try:
            messages = state.get("messages", [])
            system_prompt = self._load_prompt("data_retrieval.md")

            logger.info("Loaded system prompt for DataRetrievalNode.")
            messages = [SystemMessage(content=system_prompt)] + list(messages)

            logger.debug(f"Messages before invoking LLM: {messages}")
            response = self.llm_with_tools.invoke(messages)

            logger.info("DataRetrievalNode successfully finished.")
            return {"messages": [response]}
        except Exception as e:
            logger.error(f"Error in DataRetrievalNode: {e}", exc_info=True)
            raise
