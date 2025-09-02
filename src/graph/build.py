import logging
from typing import Literal

from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode, tools_condition

from src.graph.state import AgentState
from src.graph.nodes.data_retrieval_node import DataRetrievalNode
from src.graph.nodes.analyzing_node import AnalyzingNode
from src.graph.nodes.summarizing_node import SummarizingNode
from src.graph.tools.bigquery_tool import query_bigquery_tool, describe_bigquery_table_schema_tool
from src.graph.tools.python_tool import python_repl_tool

def call_tools_condition(state: AgentState) -> Literal["tools", "finish", "__end__"]:
    """
    Custom routing condition for LangGraph to handle tool calls differently
    on the very first LLM invocation.

    Behavior:
        - On the first turn (state["first_turn"] is True):
            * If no tool calls are returned -> route to "finish".
            * If tool calls are returned   -> route to "tools".
            * Any other unexpected case    -> route to "finish".
          After evaluation, sets state["first_turn"] = False.
        
        - On subsequent turns:
            * Falls back to the default `tools_condition`, which checks
              for tool calls and routes accordingly.

    Args:
        state (AgentState): Current agent state, must include "messages" 
                            and optionally "first_turn" (bool).
    
    Returns:
        str: Routing key ("tools", "finish", or "__end__") for the graph.
    """
    last_msg = state["messages"][-1]

    if state.get("first_turn", True):   
        state["first_turn"] = False
        if hasattr(last_msg, "tool_calls") and not last_msg.tool_calls:
            return "finish"
        if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
            return "tools"
        return "finish"

    return tools_condition(state)


def build_graph() -> StateGraph:
    """
    Build and compile the state graph for the agent workflow.

    Returns:
        StateGraph: The compiled state graph.
    """
    logging.info("Building the state graph.")

    workflow = StateGraph(AgentState)

    workflow.add_node("data_retrieval", DataRetrievalNode())
    workflow.add_node("analyzing", AnalyzingNode())
    workflow.add_node("summarizing", SummarizingNode())

    data_tools = [query_bigquery_tool, describe_bigquery_table_schema_tool]
    analysis_tools = [python_repl_tool]

    data_tool_node = ToolNode(tools=data_tools)
    workflow.add_node("data_tools", data_tool_node)

    analysis_tool_node = ToolNode(tools=analysis_tools)
    workflow.add_node("analysis_tools", analysis_tool_node)

    workflow.add_conditional_edges(
        "data_retrieval", 
        call_tools_condition,
        {"tools": "data_tools", "finish": "__end__", "__end__": "analyzing"}
    )

    workflow.add_edge("data_tools", "data_retrieval")

    workflow.add_conditional_edges(
        "analyzing", tools_condition, {"tools": "analysis_tools", "__end__": "summarizing"}
    )
    workflow.add_edge("analysis_tools", "analyzing")

    workflow.set_entry_point("data_retrieval")

    memory = MemorySaver()
    graph = workflow.compile(checkpointer=memory)

    try:
        graph.get_graph().draw_mermaid_png(output_file_path="graph.png")
        logging.getLogger(__name__).info("Graph plotted to graph.png")
    except Exception as e:
        logging.getLogger(__name__).error(f"Failed to plot graph: {e}")

    logging.getLogger(__name__).info("Graph compiled successfully.")
    return graph