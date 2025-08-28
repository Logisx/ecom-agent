from typing import TypedDict, Annotated, Optional, Dict, Any, List
from langgraph.graph.message import add_messages
import pandas as pd


class AgentState(TypedDict, total=False):
    # Conversation and inputs
    messages: Annotated[list[dict], add_messages]
    question: str
    dataset_id: str
    project_id: Optional[str]
    model_name: str
    summary: Optional[str]
