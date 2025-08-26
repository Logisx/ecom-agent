from typing import TypedDict, Annotated, Optional, Dict, Any
from langgraph.graph.message import add_messages
import pandas as pd


class AgentState(TypedDict, total=False):
    # Conversation and inputs
    messages: Annotated[list[dict], add_messages]
    question: str
    dataset_id: str
    project_id: Optional[str]
    model_name: str
    api_key: Optional[str]

    # Intermediate and outputs
    sql: Optional[str]
    df_preview: Optional[pd.DataFrame]
    summary: Optional[str]
    extra: Dict[str, Any]



    #sql: Optional[str]
    #analysis_plan: Optional[str]
    #dry_run_ok: bool
    #error: Optional[str]
    #result_rows: Optional[List[Dict[str, Any]]]


