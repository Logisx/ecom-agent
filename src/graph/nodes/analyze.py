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

logger = logging.getLogger(__name__)


class AnalyzeNode(BaseNode):
    def __call__(self, state: AgentState) -> AgentState:
        logger.info("AnalyzeNode called")

        question = state.get("question", "") 
        
        # Get the last message to use as a preview if it's a tool output
        last_message = state["messages"][-1] if state.get("messages") else None

        print("MESSAGES:", state.get("messages"))
        print("LAST MESSAGE:", last_message)
        print("LAST MESSAGE TYPE:", type(last_message))
        preview = ""
        if isinstance(last_message, ToolMessage):
            preview = str(last_message.content)
            print("PREVIEW:", preview)

        prompt_template = self._load_prompt("analyze.md")
        prompt = (
            prompt_template
            .replace("{question}", question)
            .replace("{preview}", preview)
            .replace("{dataset_id}", str(state.get("dataset_id", "")))
            .replace("{project_id}", str(state.get("project_id", "")))
        )

        print("PROMPT:", prompt)

        # Bind tools so the model can emit structured tool calls
        llm_with_tools = self.llm.bind_tools([
            query_bigquery_tool,
            describe_bigquery_table_schema_tool,
        ])
        msg = llm_with_tools.invoke(prompt)
        
        return {"messages": [msg]}