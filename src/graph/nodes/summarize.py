from typing import Dict, Any
import logging
import os

logger = logging.getLogger(__name__)


from src.services.llm import get_llm
from src.graph.state import AgentState

SYSTEM_PROMPT = (
    "You are a data analysis assistant for the thelook_ecommerce dataset. "
    "When asked a question, produce BigQuery Standard SQL that uses fully-qualified, backticked table names, "
    "then summarize key findings in plain English. Focus on actionable insights.\n\n"
    "Tables and columns:\n"
    "- orders(order_id, user_id, status, gender, created_at, returned_at, shipped_at, delivered_at, num_of_item)\n"
    "- order_items(id, order_id, user_id, product_id, inventory_item_id, status, created_at, shipped_at, delivered_at, returned_at, sale_price)\n"
    "- products(id, cost, category, name, brand, retail_price, department, sku, distribution_center_id)\n"
    "- users(id, first_name, last_name, email, age, gender, state, street_address, postal_code, city, country, latitude, longitude, traffic_source, created_at, user_geom)\n"
)

def node(state: AgentState) -> AgentState:
    # Don't hard-assert here; get_llm() will read env and raise if missing
    llm = get_llm()
    df_preview = state.get("df_preview")  # type: ignore[index]
    preview = "" if df_preview is None else df_preview.to_string(index=False)
    question = state.get("question", "")  # type: ignore[index]
    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"Question: {question}\n"
        "Here is a small preview of query results (first rows):\n"
        f"{preview}\n\n"
        "Provide a concise, actionable insight summary (3-6 sentences)."
    )
    msg = llm.invoke(prompt)
    state["summary"] = msg.content if isinstance(msg.content, str) else str(msg.content)  # type: ignore[index]
    return state

"""
def node(state: Dict[str, Any]) -> Dict[str, Any]:
    rows = state.get("result_rows") or []
    sql = state.get("sql") or ""
    insight = f"Fetched {len(rows)} rows. Example SQL executed:\n\n{sql[:400]}\n\nSample row: {rows[0] if rows else '{}'}"
    state.setdefault("messages", []).append({"role": "assistant", "content": insight})
    logger.info("summarize.node: message_appended", extra={"rows": len(rows)})
    return state

"""