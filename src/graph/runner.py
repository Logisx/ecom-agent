import logging
from typing import Optional

from src.graph.build import build_graph
from src.graph.state import AgentState

logger = logging.getLogger(__name__)


def run_chat_once(
    *,
    model_name: str,
    project_id: Optional[str],
    dataset_id: str,
    question: str,
) -> str:
    logger.info("runner: building graph")
    graph = build_graph()
    logger.info("runner: invoking graph")
    initial_state: AgentState = {
        "messages": [],
        "question": question,
        "dataset_id": dataset_id,
        "project_id": project_id,
        "model_name": model_name,
    }
    final_state: AgentState = graph.invoke(initial_state)
    logger.info("runner: received final state")
    return final_state.get("summary") or "No summary produced."


