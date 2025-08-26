from src.graph.build import build_graph
from typing import Optional
import logging

from src.graph.state import AgentState
logger = logging.getLogger(__name__)


def run_chat_once_graph(
    *,
    model_name: str,
    project_id: Optional[str],
    dataset_id: str,
    question: str,
) -> str:

    logger.info("agent.py started")
    graph = build_graph()
    logger.info("agent.py graph built")
    final_state: AgentState = graph.invoke(
        AgentState(
            question=question,
            dataset_id=dataset_id,
            project_id=project_id,
            model_name=model_name,
        )
    )
    logger.info("agent.py recieved final state")
    # AgentState is a TypedDict; graph returns a dict-like state
    return final_state.get("summary") or "No summary produced."


