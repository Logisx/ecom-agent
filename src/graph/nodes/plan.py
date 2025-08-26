from typing import Dict, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "plan.md"

def node(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.debug("plan.node: start")
    user_msg = ""
    for m in state.get("messages", []):
        if isinstance(m, dict):
            role = m.get("role") or m.get("type")
            content = m.get("content", "")
        else:
            role = getattr(m, "role", None) or getattr(m, "type", None)
            content = getattr(m, "content", "")
        if role in ("user", "human"):
            user_msg = content
    # very light heuristic plan without LLM for bootstrap
    plan = f"Plan to analyze: {user_msg}. Use orders, order_items, products, users. Generate safe SQL with LIMIT 100."
    state["analysis_plan"] = plan
    logger.info("plan.node: plan_created", extra={"has_user_msg": bool(user_msg)})
    logger.debug("plan.node: end")
    return state

