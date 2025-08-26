from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

def node(state: Dict[str, Any]) -> Dict[str, Any]:
    # Stub: if SQL failed, just append LIMIT to be safe; real impl would use LLM
    sql = (state.get("sql") or "").strip()
    logger.debug("repair_sql.node: start", extra={"sql_preview": sql[:120], "error": state.get("error")})
    if not sql.lower().endswith("limit 100"):
        sql = sql.rstrip(";") + "\nLIMIT 100"
    state["sql"] = sql
    logger.info("repair_sql.node: adjusted_sql")
    logger.debug("repair_sql.node: end")
    return state

