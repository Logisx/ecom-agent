from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
import logging
from src.graph.state import AgentState

from langgraph.prebuilt import ToolNode, tools_condition
from src.graph.nodes.summarize import SummarizeNode
from src.graph.nodes.analyze import AnalyzeNode
from src.graph.tools.bigquery import query_bigquery_tool, describe_bigquery_table_schema_tool 

def build_graph() -> StateGraph:

    workflow = StateGraph(AgentState)

    workflow.add_node("analyze", AnalyzeNode())

    tools = [query_bigquery_tool, describe_bigquery_table_schema_tool]
    tool_node = ToolNode(tools=tools)
    workflow.add_node("tools", tool_node)



    workflow.add_conditional_edges("analyze", 
                                    tools_condition, 
                                    {"tools": "tools", "__end__": "__end__"})

    workflow.add_edge("tools", "analyze")

    workflow.set_entry_point("analyze")

    memory = MemorySaver()
    graph = workflow.compile(checkpointer=memory)

    try:
        graph.get_graph().draw_mermaid_png(output_file_path="graph.png")
        logging.getLogger(__name__).info("graph: plotted to graph.png")
    except Exception as e:
        logging.getLogger(__name__).error(f"Failed to plot graph: {e}")

    logging.getLogger(__name__).info("graph: compiled")

    return graph