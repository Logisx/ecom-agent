from typing import Any, List

from src.graph.nodes.base_node import BaseNode
from src.graph.state import AgentState
import pandas as pd
from src.graph.tools.bigquery import (
    query_bigquery_tool,
    describe_bigquery_table_schema_tool,
)

import logging
from langchain_core.messages import ToolMessage
from langchain_core.messages import SystemMessage
logger = logging.getLogger(__name__)


class AnalyzeNode(BaseNode):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.llm_with_tools = self.llm.bind_tools([
            query_bigquery_tool,
            describe_bigquery_table_schema_tool,
        ])

    def __call__(self, state: AgentState) -> AgentState:
        logger.info("AnalyzeNode called")

        messages = state.get("messages", [])
        system_prompt = self._load_prompt("analyze.md")

        messages = [SystemMessage(content=system_prompt)] + list(messages)

        print("MESSAGES:", state.get("messages"))

        response = self.llm_with_tools.invoke(messages)
        
        return {"messages": [response]}