import logging
from typing import Optional

from src.graph.build import build_graph
from src.graph.state import AgentState

from typing import Dict, Any

from langchain_core.messages import HumanMessage
from langgraph.errors import GraphRecursionError

logger = logging.getLogger(__name__)

_graph = None


def get_graph():
    global _graph
    if _graph is None:
        logger.info("runner: building graph (singleton)")
        _graph = build_graph()
    return _graph


def run_chat_once(question: str, bq_config: Dict[str, Any], agent_config: Dict[str, Any] ) -> str:
    graph = get_graph()
    logger.info("runner: invoking graph")
    initial_state: AgentState = {
        "messages": [HumanMessage(content=question)],
        "question": question,
    }

    max_iterations = agent_config.get("max_iterations", 5)
    recursion_limit = 2 * max_iterations + 1
    
    try:
        events = graph.stream(
            initial_state,
            config={
                "configurable": {
                    "thread_id": "1",
                },
                "recursion_limit": recursion_limit,
            },
            stream_mode="values"
            )
        print("EVENTS:", events)

        for event in events:
            try:
                if event.get("messages") and len(event["messages"]) > 0:
                    event["messages"][-1].pretty_print()
            except Exception as e:
                logger.error(e)
                pass
            final_state = event
    except GraphRecursionError:
        logger.warning("Agent stopped due to reaching the recursion limit.")
        return "Agent stopped: maximum iterations reached."

    logger.info("runner: received final state")
    return "Finished" #final_state["messages"][-1] if final_state.get("messages") else "No summary produced."


