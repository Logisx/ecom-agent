import logging
from typing import Optional

from src.graph.build import build_graph
from src.graph.state import AgentState

logger = logging.getLogger(__name__)

_graph = None


def get_graph():
    global _graph
    if _graph is None:
        logger.info("runner: building graph (singleton)")
        _graph = build_graph()
    return _graph


def run_chat_once(
    *,
    question: str,
) -> str:
    graph = get_graph()
    logger.info("runner: invoking graph")
    initial_state: AgentState = {
        "messages": [],
        "question": question,
    }

    events = graph.stream(
        initial_state,
        config={
            "configurable": {
                "thread_id": "cli",
            }
        },
        stream_mode="values"
    )

    for event in events:
        try:
            if event.get("messages") and len(event["messages"]) > 0:
                event["messages"][-1].pretty_print()
        except Exception as e:
            logger.error(e)
            pass
        final_state = event

    logger.info("runner: received final state")
    return final_state.get("summary") or "No summary produced."


