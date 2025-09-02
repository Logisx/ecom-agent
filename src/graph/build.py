import logging

from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode, tools_condition

from src.graph.state import AgentState
from src.graph.nodes.analyze import AnalyzeNode
from src.graph.tools.bigquery import query_bigquery_tool, describe_bigquery_table_schema_tool

def build_graph() -> StateGraph:
    """
    Build and compile the state graph for the agent workflow.

    Returns:
        StateGraph: The compiled state graph.
    """
    logging.info("Building the state graph.")

    workflow = StateGraph(AgentState)

    workflow.add_node("analyze", AnalyzeNode())
    tools = [query_bigquery_tool, describe_bigquery_table_schema_tool]
    tool_node = ToolNode(tools=tools)
    workflow.add_node("tools", tool_node)

    workflow.add_conditional_edges(
        "analyze", tools_condition, {"tools": "tools", "__end__": "__end__"}
    )

    workflow.add_edge("tools", "analyze")

    workflow.set_entry_point("analyze")

    memory = MemorySaver()
    graph = workflow.compile(checkpointer=memory)

    try:
        graph.get_graph().draw_mermaid_png(output_file_path="graph.png")
        logging.getLogger(__name__).info("Graph plotted to graph.png")
    except Exception as e:
        logging.getLogger(__name__).error(f"Failed to plot graph: {e}")

    logging.getLogger(__name__).info("Graph compiled successfully.")
    return graph