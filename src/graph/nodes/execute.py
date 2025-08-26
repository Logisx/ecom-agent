from typing import Dict, Any
from src.services.big_query_runner import BigQueryRunner
import logging

logger = logging.getLogger(__name__)

_runner: BigQueryRunner | None = None

def _get_runner() -> BigQueryRunner:
    global _runner
    if _runner is None:
        _runner = BigQueryRunner()
    return _runner

def node(state: Dict[str, Any]) -> Dict[str, Any]:
    sql = state.get("sql") or ""
    logger.debug("execute.node: start", extra={"sql_preview": sql[:120]})
    df = _get_runner().execute_query(sql)
    state["result_rows"] = df.to_dict(orient="records")[:100]
    logger.info("execute.node: rows_fetched", extra={"row_count": len(state["result_rows"])})
    logger.debug("execute.node: end")
    return state

