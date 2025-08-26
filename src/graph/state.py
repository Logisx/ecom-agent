from typing import TypedDict, Annotated, Optional, List, Dict, Any
from langgraph.graph.message import add_messages
from dataclasses import dataclass, field

import pandas as pd

@dataclass
class AgentState(TypedDict):
    messages: Annotated[list[dict], add_messages]
    question: str
    dataset_id: str
    project_id: Optional[str] = None
    model_name: str = "gemini-2.0-flash-lite"
    api_key: Optional[str] = None

    sql: Optional[str] = None
    df_preview: Optional[pd.DataFrame] = None
    summary: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)



    #sql: Optional[str]
    #analysis_plan: Optional[str]
    #dry_run_ok: bool
    #error: Optional[str]
    #result_rows: Optional[List[Dict[str, Any]]]


