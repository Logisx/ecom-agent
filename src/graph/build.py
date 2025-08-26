from langgraph.graph import StateGraph, START, END
import logging
from src.graph.state import AgentState
from src.graph.nodes import plan, sql_generate, dry_run, execute, repair_sql, route, summarize


from src.graph.nodes import plan_sql, run_sql

def build_graph() -> StateGraph:

    builder = StateGraph(AgentState)
    #builder.add_node("intent", route.node)
    #builder.add_node("route", route.node)
    #builder.add_node("plan", plan.node)
    builder.add_node("plan_sql", plan_sql.node)
    #builder.add_node("sql_generate", sql_generate.node)
    #builder.add_node("dry_run", dry_run.node)
    #builder.add_node("execute", execute.node)
    builder.add_node("run_sql", run_sql.node)
    #builder.add_node("repair_sql", repair_sql.node)
    builder.add_node("summarize", summarize.node)

    builder.set_entry_point("plan_sql")
    builder.add_edge("plan_sql", "run_sql")
    builder.add_edge("run_sql", "summarize")
    builder.add_edge("summarize", END)

    """
    builder.add_edge(START, "intent")
    builder.add_edge("intent", "plan") 
    builder.add_edge("plan", "sql_generate")
    builder.add_edge("sql_generate", "dry_run")

    def on_dry_run(state):
        return "execute" if state["dry_run_ok"] else "repair_sql"

    builder.add_conditional_edges("dry_run", on_dry_run, {"execute": "execute", "repair_sql": "repair_sql"})
    builder.add_edge("execute", "summarize")
    builder.add_edge("repair_sql", "sql_generate")
    builder.add_edge("summarize", END)
    """

    graph = builder.compile()

    logging.getLogger(__name__).info("graph: compiled")

    return graph