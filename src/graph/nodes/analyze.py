from typing import Any, List

from src.graph.nodes.base_node import BaseNode
from src.graph.state import AgentState
import pandas as pd
from src.graph.tools.bigquery import (
    query_bigquery_tool,
    describe_bigquery_table_schema_tool,
)

import logging

logger = logging.getLogger(__name__)


class AnalyzeNode(BaseNode):
    def __call__(self, state: AgentState) -> AgentState:
        logger.info("AnalyzeNode called")

        question = state.get("question", "") 
        
        # Get the last message to use as a preview if it's a tool output
        last_message = state["messages"][-1] if state.get("messages") else None
        preview = ""
        if last_message and hasattr(last_message, 'content') and not hasattr(last_message, 'tool_calls'):
             # content from a ToolMessage is often a string representation of the data
             preview = str(last_message.content)

        prompt_template = self._load_prompt("analyze.md")
        prompt = (
            prompt_template
            .replace("{question}", question)
            .replace("{preview}", preview)
            .replace("{dataset_id}", str(state.get("dataset_id", "")))
            .replace("{project_id}", str(state.get("project_id", "")))
        )

        # Bind tools so the model can emit structured tool calls
        llm_with_tools = self.llm.bind_tools([
            query_bigquery_tool,
            describe_bigquery_table_schema_tool,
        ])
        msg = llm_with_tools.invoke(prompt)
        
        return {"messages": [msg]}