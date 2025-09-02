import logging
from typing import Optional, Dict, Any

from langchain_core.messages import HumanMessage
from langgraph.errors import GraphRecursionError

from src.graph.build import build_graph
from src.graph.state import AgentState

logger = logging.getLogger(__name__)

_graph: Optional[Any] = None


def get_graph() -> Any:
    """
    Retrieve or build the state graph (singleton).

    Returns:
        Any: The state graph instance.
    """
    global _graph
    if _graph is None:
        logger.info("Building the state graph (singleton).")
        _graph = build_graph()
    return _graph


def run_chat_once(question: str, agent_config: Dict[str, Any]) -> str:
    """
    Run a single chat iteration with the agent.

    Args:
        question (str): The user's question.
        bq_config (Dict[str, Any]): BigQuery configuration.
        agent_config (Dict[str, Any]): Agent configuration.

    Returns:
        str: The agent's response or an error message.
    """
    logger.info("Invoking the state graph for chat.")
    graph = get_graph()

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
            stream_mode="values",
        )

        logger.info("Processing events from the graph.")

        for event in events:
            try:
                if event.get("messages") and len(event["messages"]) > 0:
                    print("\n")
                    event["messages"][-1].pretty_print()
                    print("\n================================================================================\n")
            except Exception as e:
                logger.error(f"Error processing event: {e}")
                continue

        logger.info("Received final event from the graph.")

        return (
            event["messages"][-1].content
            if event and event.get("messages")
            else "Unfortunately, agent was not able to produce a response."
        )

    except GraphRecursionError:
        logger.warning("Agent stopped due to reaching the recursion limit.")
        return "Agent stopped: maximum iterations reached."
    except Exception as e:
        logger.error(f"An error occurred during graph execution: {e}", exc_info=True)
        return f"Error: {e}"


