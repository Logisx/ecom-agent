from typing import TypedDict, Annotated, Optional, Dict, Any, List
from langgraph.graph.message import add_messages


class AgentState(TypedDict, total=False):
    """
    Represents the state of the agent during execution.

    Attributes:
        messages (list[dict]): List of messages exchanged in the conversation.
        question (str): The user's question.
        dataset_id (str): The dataset ID being queried.
        project_id (Optional[str]): The GCP project ID.
        model_name (str): The name of the model being used.
        summary (Optional[str]): A summary of the agent's response.
    """
    messages: Annotated[List[Dict[str, Any]], add_messages]
    question: str
    dataset_id: str
    project_id: Optional[str]
    model_name: str
    summary: Optional[str]
